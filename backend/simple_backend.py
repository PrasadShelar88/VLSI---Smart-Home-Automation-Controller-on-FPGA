from __future__ import annotations

import csv
import io
import json
import random
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8000
APP_TITLE = "VLSI Smart Home FPGA Backend"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "automation_logs.csv"

CSV_COLUMNS = [
    "timestamp",
    "mode",
    "motion",
    "dark",
    "temperature",
    "door_open",
    "security_mode",
    "manual_override",
    "manual_light",
    "manual_fan",
    "manual_socket",
    "overcurrent",
    "light_pwm",
    "fan_pwm",
    "socket_relay",
    "ac_relay",
    "alarm",
    "energy_saving",
    "state",
    "message",
]


def ensure_log_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=CSV_COLUMNS).writeheader()


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def bool_payload(payload: Dict[str, Any], key: str, default: bool = False) -> bool:
    value = payload.get(key, default)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def calculate_controller(payload: Dict[str, Any]) -> Dict[str, Any]:
    motion = bool_payload(payload, "motion", True)
    dark = bool_payload(payload, "dark", True)
    door_open = bool_payload(payload, "door_open", False)
    security_mode = bool_payload(payload, "security_mode", False)
    manual_override = bool_payload(payload, "manual_override", False)
    manual_light = bool_payload(payload, "manual_light", False)
    manual_fan = bool_payload(payload, "manual_fan", False)
    manual_socket = bool_payload(payload, "manual_socket", False)
    overcurrent = bool_payload(payload, "overcurrent", False)
    no_motion_timeout = bool_payload(payload, "no_motion_timeout", False)
    temperature = float(payload.get("temperature", 31.0))
    temp_threshold = float(payload.get("temp_threshold", 30.0))

    state = "AUTO"
    light_pwm = 0
    fan_pwm = 0
    socket_relay = False
    ac_relay = False
    alarm = False
    energy_saving = False
    messages: List[str] = []

    if overcurrent:
        state = "ALARM"
        alarm = True
        light_pwm = 255
        messages.append("Over-current detected: relay outputs forced OFF and alarm activated.")
    elif security_mode and door_open:
        state = "ALARM"
        alarm = True
        light_pwm = 255
        messages.append("Door opened in security mode: alarm activated.")
    elif manual_override:
        state = "MANUAL"
        light_pwm = 255 if manual_light else 0
        fan_pwm = 220 if manual_fan else 0
        socket_relay = manual_socket
        messages.append("Manual override has priority over sensor automation.")
    else:
        if motion and dark:
            light_pwm = 220
            messages.append("Motion detected and room is dark: light PWM enabled.")
        elif dark:
            light_pwm = 80
            messages.append("Room is dark but no motion: low night-light level selected.")
        else:
            light_pwm = 0
            messages.append("Enough ambient light: room light OFF.")

        if temperature >= temp_threshold + 5:
            fan_pwm = 255
            ac_relay = True
            messages.append("Temperature is very high: fan full speed and AC relay ON.")
        elif temperature >= temp_threshold:
            fan_pwm = 170
            messages.append("Temperature crossed threshold: fan PWM enabled.")
        else:
            fan_pwm = 0
            messages.append("Temperature normal: fan OFF.")

        socket_relay = motion

        if no_motion_timeout:
            light_pwm = 0
            fan_pwm = 0 if temperature < temp_threshold else fan_pwm
            socket_relay = False
            energy_saving = True
            state = "ENERGY_SAVE"
            messages.append("No-motion timeout: appliance outputs reduced for energy saving.")

    if alarm:
        socket_relay = False
        ac_relay = False

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "security" if security_mode else "normal",
        "motion": motion,
        "dark": dark,
        "temperature": round(temperature, 2),
        "door_open": door_open,
        "security_mode": security_mode,
        "manual_override": manual_override,
        "manual_light": manual_light,
        "manual_fan": manual_fan,
        "manual_socket": manual_socket,
        "overcurrent": overcurrent,
        "light_pwm": clamp(light_pwm, 0, 255),
        "fan_pwm": clamp(fan_pwm, 0, 255),
        "socket_relay": socket_relay,
        "ac_relay": ac_relay,
        "alarm": alarm,
        "energy_saving": energy_saving,
        "state": state,
        "message": " ".join(messages),
    }
    return result


def append_log(row: Dict[str, Any]) -> None:
    ensure_log_file()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=CSV_COLUMNS).writerow(row)


def read_logs() -> List[Dict[str, str]]:
    ensure_log_file()
    with LOG_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def make_pdf(lines: List[str]) -> bytes:
    escaped_lines = [
        line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:105]
        for line in lines
    ]
    commands = ["BT", "/F1 11 Tf", "45 790 Td"]
    for index, line in enumerate(escaped_lines):
        if index:
            commands.append("0 -16 Td")
        commands.append(f"({line}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(pdf.tell())
        pdf.write(f"{number} 0 obj\n".encode())
        pdf.write(obj)
        pdf.write(b"\nendobj\n")
    xref = pdf.tell()
    pdf.write(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode())
    pdf.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return pdf.getvalue()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: Any) -> None:
        self._send(status, json.dumps(data, indent=2).encode("utf-8"))

    def _body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def do_OPTIONS(self) -> None:
        self._send(HTTPStatus.NO_CONTENT, b"")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path in ("/", "/health"):
                self._json(200, {"status": "ok", "message": APP_TITLE})
            elif path == "/docs":
                html = """
                <html><head><title>VLSI Smart Home FPGA Backend</title></head>
                <body style="font-family:Arial;max-width:900px;margin:40px auto;line-height:1.5">
                <h1>VLSI Smart Home FPGA Backend</h1>
                <p>Backend is running at <b>http://127.0.0.1:8000</b></p>
                <h2>Main APIs</h2>
                <ul>
                  <li>GET /health</li>
                  <li>POST /api/controller/evaluate</li>
                  <li>POST /api/controller/simulate</li>
                  <li>GET /api/logs</li>
                  <li>GET /api/export/csv</li>
                  <li>GET /api/export/pdf</li>
                  <li>GET /api/source/rtl</li>
                  <li>GET /api/source/testbench</li>
                </ul>
                <h2>Sample Input</h2>
                <pre>{
  "motion": true,
  "dark": true,
  "temperature": 34,
  "door_open": false,
  "security_mode": false,
  "manual_override": false,
  "overcurrent": false
}</pre>
                </body></html>
                """
                self._send(200, html.encode("utf-8"), "text/html")
            elif path == "/api/logs":
                self._json(200, read_logs())
            elif path == "/api/export/csv":
                data = LOG_FILE.read_bytes() if LOG_FILE.exists() else b""
                self._send(200, data, "text/csv")
            elif path == "/api/export/pdf":
                logs = read_logs()
                lines = ["Smart Home Automation Controller on FPGA Report", ""]
                if logs:
                    for row in logs[-28:]:
                        lines.append(
                            f"{row['timestamp']} | {row['state']} | light={row['light_pwm']} fan={row['fan_pwm']} "
                            f"socket={row['socket_relay']} alarm={row['alarm']}"
                        )
                else:
                    lines.append("No logs available.")
                self._send(200, make_pdf(lines), "application/pdf")
            elif path == "/api/source/rtl":
                self._send(200, (BASE_DIR / "verilog" / "smart_home_controller.v").read_bytes(), "text/plain")
            elif path == "/api/source/testbench":
                self._send(200, (BASE_DIR / "verilog" / "tb_smart_home_controller.v").read_bytes(), "text/plain")
            else:
                self._json(404, {"detail": "Not Found"})
        except Exception as exc:
            self._json(500, {"detail": str(exc)})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/controller/evaluate":
                result = calculate_controller(self._body())
                append_log(result)
                self._json(200, result)
            elif path == "/api/controller/simulate":
                payload = self._body()
                count = clamp(int(payload.get("count", 10)), 1, 100)
                scenarios = []
                for _ in range(count):
                    scenario = {
                        "motion": random.choice([True, False]),
                        "dark": random.choice([True, False]),
                        "temperature": round(random.uniform(24, 40), 1),
                        "door_open": random.choice([True, False, False]),
                        "security_mode": random.choice([True, False]),
                        "manual_override": random.choice([True, False, False]),
                        "manual_light": random.choice([True, False]),
                        "manual_fan": random.choice([True, False]),
                        "manual_socket": random.choice([True, False]),
                        "overcurrent": random.choice([False, False, False, True]),
                        "no_motion_timeout": random.choice([False, False, True]),
                    }
                    result = calculate_controller(scenario)
                    append_log(result)
                    scenarios.append(result)
                self._json(200, scenarios)
            else:
                self._json(404, {"detail": "Not Found"})
        except Exception as exc:
            self._json(400, {"detail": str(exc)})

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/logs":
            if LOG_FILE.exists():
                LOG_FILE.unlink()
            ensure_log_file()
            self._json(200, {"message": "Logs cleared"})
        else:
            self._json(404, {"detail": "Not Found"})


def main() -> None:
    ensure_log_file()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("=" * 70)
    print(APP_TITLE)
    print(f"Backend running at http://{HOST}:{PORT}")
    print(f"Docs page: http://{HOST}:{PORT}/docs")
    print("Press CTRL + C to stop.")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBackend stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

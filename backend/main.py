from __future__ import annotations

import csv
import io
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field


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


class ControllerRequest(BaseModel):
    motion: bool = True
    dark: bool = True
    temperature: float = 34.0
    temp_threshold: float = 30.0
    door_open: bool = False
    security_mode: bool = False
    manual_override: bool = False
    manual_light: bool = False
    manual_fan: bool = False
    manual_socket: bool = False
    overcurrent: bool = False
    no_motion_timeout: bool = False


class ControllerResult(BaseModel):
    timestamp: str
    mode: str
    motion: bool
    dark: bool
    temperature: float
    door_open: bool
    security_mode: bool
    manual_override: bool
    manual_light: bool
    manual_fan: bool
    manual_socket: bool
    overcurrent: bool
    light_pwm: int
    fan_pwm: int
    socket_relay: bool
    ac_relay: bool
    alarm: bool
    energy_saving: bool
    state: str
    message: str


class SimulationRequest(BaseModel):
    count: int = Field(10, ge=1, le=100)


app = FastAPI(title=APP_TITLE, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_log_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=CSV_COLUMNS).writeheader()


def controller_logic(req: ControllerRequest) -> ControllerResult:
    state = "AUTO"
    light_pwm = 0
    fan_pwm = 0
    socket_relay = False
    ac_relay = False
    alarm = False
    energy_saving = False
    messages: List[str] = []

    if req.overcurrent:
        state = "ALARM"
        alarm = True
        light_pwm = 255
        messages.append("Over-current detected: relay outputs forced OFF and alarm activated.")
    elif req.security_mode and req.door_open:
        state = "ALARM"
        alarm = True
        light_pwm = 255
        messages.append("Door opened in security mode: alarm activated.")
    elif req.manual_override:
        state = "MANUAL"
        light_pwm = 255 if req.manual_light else 0
        fan_pwm = 220 if req.manual_fan else 0
        socket_relay = req.manual_socket
        messages.append("Manual override has priority over sensor automation.")
    else:
        if req.motion and req.dark:
            light_pwm = 220
            messages.append("Motion detected and room is dark: light PWM enabled.")
        elif req.dark:
            light_pwm = 80
            messages.append("Room is dark but no motion: low night-light level selected.")
        else:
            messages.append("Enough ambient light: room light OFF.")

        if req.temperature >= req.temp_threshold + 5:
            fan_pwm = 255
            ac_relay = True
            messages.append("Temperature is very high: fan full speed and AC relay ON.")
        elif req.temperature >= req.temp_threshold:
            fan_pwm = 170
            messages.append("Temperature crossed threshold: fan PWM enabled.")
        else:
            messages.append("Temperature normal: fan OFF.")

        socket_relay = req.motion

        if req.no_motion_timeout:
            light_pwm = 0
            socket_relay = False
            energy_saving = True
            state = "ENERGY_SAVE"
            messages.append("No-motion timeout: appliance outputs reduced for energy saving.")

    if alarm:
        socket_relay = False
        ac_relay = False

    return ControllerResult(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        mode="security" if req.security_mode else "normal",
        motion=req.motion,
        dark=req.dark,
        temperature=round(req.temperature, 2),
        door_open=req.door_open,
        security_mode=req.security_mode,
        manual_override=req.manual_override,
        manual_light=req.manual_light,
        manual_fan=req.manual_fan,
        manual_socket=req.manual_socket,
        overcurrent=req.overcurrent,
        light_pwm=max(0, min(255, light_pwm)),
        fan_pwm=max(0, min(255, fan_pwm)),
        socket_relay=socket_relay,
        ac_relay=ac_relay,
        alarm=alarm,
        energy_saving=energy_saving,
        state=state,
        message=" ".join(messages),
    )


def append_log(result: ControllerResult) -> None:
    ensure_log_file()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=CSV_COLUMNS).writerow(result.model_dump())


def read_logs() -> List[Dict[str, str]]:
    ensure_log_file()
    with LOG_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def make_pdf(lines: List[str]) -> bytes:
    escaped = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:105] for line in lines]
    commands = ["BT", "/F1 11 Tf", "45 790 Td"]
    for index, line in enumerate(escaped):
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
    pdf.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return pdf.getvalue()


@app.on_event("startup")
def startup_event() -> None:
    ensure_log_file()


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": APP_TITLE, "status": "running", "docs": "Open http://127.0.0.1:8000/docs"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "project": "Smart Home Automation Controller on FPGA"}


@app.post("/api/controller/evaluate", response_model=ControllerResult)
def evaluate(req: ControllerRequest) -> ControllerResult:
    result = controller_logic(req)
    append_log(result)
    return result


@app.post("/api/controller/simulate", response_model=List[ControllerResult])
def simulate(req: SimulationRequest) -> List[ControllerResult]:
    results = []
    for _ in range(req.count):
        item = ControllerRequest(
            motion=random.choice([True, False]),
            dark=random.choice([True, False]),
            temperature=round(random.uniform(24, 40), 1),
            door_open=random.choice([True, False, False]),
            security_mode=random.choice([True, False]),
            manual_override=random.choice([True, False, False]),
            manual_light=random.choice([True, False]),
            manual_fan=random.choice([True, False]),
            manual_socket=random.choice([True, False]),
            overcurrent=random.choice([False, False, False, True]),
            no_motion_timeout=random.choice([False, False, True]),
        )
        result = controller_logic(item)
        append_log(result)
        results.append(result)
    return results


@app.get("/api/logs")
def logs() -> List[Dict[str, str]]:
    return read_logs()


@app.delete("/api/logs")
def clear_logs() -> Dict[str, str]:
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    ensure_log_file()
    return {"message": "Logs cleared"}


@app.get("/api/export/csv")
def export_csv() -> FileResponse:
    ensure_log_file()
    return FileResponse(LOG_FILE, media_type="text/csv", filename="smart_home_fpga_logs.csv")


@app.get("/api/export/pdf")
def export_pdf() -> StreamingResponse:
    logs_data = read_logs()
    lines = ["Smart Home Automation Controller on FPGA Report", ""]
    if logs_data:
        for row in logs_data[-28:]:
            lines.append(
                f"{row['timestamp']} | {row['state']} | light={row['light_pwm']} fan={row['fan_pwm']} "
                f"socket={row['socket_relay']} alarm={row['alarm']}"
            )
    else:
        lines.append("No logs available.")
    return StreamingResponse(
        io.BytesIO(make_pdf(lines)),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=smart_home_fpga_report.pdf"},
    )


@app.get("/api/source/rtl")
def rtl_source() -> FileResponse:
    return FileResponse(BASE_DIR / "verilog" / "smart_home_controller.v", media_type="text/plain")


@app.get("/api/source/testbench")
def testbench_source() -> FileResponse:
    return FileResponse(BASE_DIR / "verilog" / "tb_smart_home_controller.v", media_type="text/plain")

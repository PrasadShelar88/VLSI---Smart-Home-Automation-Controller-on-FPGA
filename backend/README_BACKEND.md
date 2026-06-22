# VLSI Smart Home FPGA Backend

This backend is for the **Smart Home Automation Controller on FPGA** project. It gives you a virtual controller simulator, automation logs, CSV/PDF report export, and downloadable Verilog RTL/testbench source files.

This version is beginner-friendly. It can run with normal Python only, so you do not need pip install or internet.

## How to Run on Windows

1. Extract this zip file.
2. Open the extracted folder.
3. Double-click `run_backend.bat`.
4. Keep the backend window open.
5. Open this link in your browser:

```text
http://127.0.0.1:8000/docs
```

## API Features

- `GET /health` - Check backend status
- `POST /api/controller/evaluate` - Test one smart home input condition
- `POST /api/controller/simulate` - Generate virtual simulation readings
- `GET /api/logs` - View saved automation logs
- `DELETE /api/logs` - Clear saved logs
- `GET /api/export/csv` - Download CSV report
- `GET /api/export/pdf` - Download PDF report
- `GET /api/source/rtl` - Download Verilog RTL code
- `GET /api/source/testbench` - Download Verilog testbench code

## Sample JSON

Use this with `/api/controller/evaluate`:

```json
{
  "motion": true,
  "dark": true,
  "temperature": 34,
  "temp_threshold": 30,
  "door_open": false,
  "security_mode": false,
  "manual_override": false,
  "manual_light": false,
  "manual_fan": false,
  "manual_socket": false,
  "overcurrent": false,
  "no_motion_timeout": false
}
```

## Logic Priority

1. Over-current alarm
2. Security alarm
3. Manual override
4. Sensor automation
5. Energy saving timeout

## Stop Backend

Press `CTRL + C` in the backend window, then type `Y` if it asks for confirmation.

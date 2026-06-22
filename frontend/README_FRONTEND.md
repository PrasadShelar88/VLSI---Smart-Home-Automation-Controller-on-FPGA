# VLSI Smart Home FPGA Frontend

This is the frontend dashboard for the **Smart Home Automation Controller on FPGA** project.

## How to Run on Windows

1. Start the backend first.
2. Extract this frontend zip.
3. Open the extracted frontend folder.
4. Double-click `run_frontend.bat`.
5. Open this link in your browser:

```text
http://127.0.0.1:5500
```

## Backend URL

Use this backend URL in the dashboard:

```text
http://127.0.0.1:8000
```

## Features

- Backend connection test
- PIR motion, LDR dark-room, temperature, door, and security inputs
- Manual override controls for light, fan, and socket relay
- Output display for FSM state, light PWM, fan PWM, relays, alarm, and energy saving
- Virtual simulation generator
- Recent automation logs
- CSV and PDF report buttons
- RTL and testbench source buttons

## Stop Frontend

Press `CTRL + C` in the frontend window, then type `Y` if it asks for confirmation.

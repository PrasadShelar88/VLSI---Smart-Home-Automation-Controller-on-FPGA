
# Smart Home Automation Controller on FPGA

## Overview

This project is a **Smart Home Automation Controller designed using FPGA-based digital logic**. It simulates and controls home appliances such as lights, fan, socket relay, AC relay, and safety alarm using inputs from PIR motion sensor, LDR light sensor, temperature sensor, door sensor, security mode, manual override, and over-current fault detection.

The project includes a **virtual FPGA controller simulator**, **Verilog RTL**, **testbench**, logs, CSV/PDF report generation, and source-code access. It is designed as a beginner-friendly but industry-relevant VLSI course project.

This project demonstrates how FPGA logic can be used for deterministic, low-latency automation and safety control in smart homes, building automation, embedded controllers, and IoT-based systems.

---

## Project Objective

The main objective of this project is to design and implement a **parameterizable home automation controller on FPGA** that manages lighting, fan speed, relay sockets, security alarm, energy-saving logic, and manual control.

The system takes simulated sensor inputs and generates appliance control outputs based on priority-based control logic.

---

## Problem Statement

Traditional home automation systems often depend on microcontrollers or cloud-based control, which may introduce delay or reliability issues in safety-critical situations.

This project solves the problem by using FPGA-based control logic where multiple sensor inputs can be processed in parallel with predictable timing. The FPGA controller can respond quickly to motion, darkness, temperature, door status, security mode, and fault conditions.

---

## Features

- PIR motion sensor input simulation
- LDR dark-room detection
- Temperature-based fan control
- Door sensor and security mode alarm
- Manual override control
- Light PWM output
- Fan PWM output
- Socket relay control
- AC relay control
- Over-current fault alarm
- Energy-saving mode using no-motion timeout
- Priority-based automation logic
- FSM state display
- Backend API using FastAPI
- Frontend dashboard simulation
- Recent automation logs
- CSV report generation
- PDF report generation
- Verilog RTL source access
- Verilog testbench access

---

## VLSI / FPGA Concepts Used

- Verilog HDL
- RTL design
- Combinational logic
- Sequential logic
- Finite State Machine
- Priority logic
- Clock and reset handling
- Sensor input processing
- PWM output generation
- Relay output simulation
- Testbench verification
- Waveform-based debugging
- FPGA implementation planning

---

## System Architecture

```text
Sensor / Switch Inputs
        |
        v
FPGA Smart Home Controller
        |
        v
Control Logic / FSM / Priority Logic
        |
        v
Appliance Output Signals
        |
        v
Light PWM | Fan PWM | Socket Relay | AC Relay | Alarm
````

---

## Input Signals

| Input                 | Description                      |
| --------------------- | -------------------------------- |
| PIR Motion            | Detects human motion in the room |
| LDR Dark Input        | Detects whether the room is dark |
| Temperature           | Used to control fan speed        |
| Temperature Threshold | Limit above which fan turns ON   |
| Door Open             | Detects door status              |
| Security Mode         | Enables security alarm logic     |
| Over-current Fault    | Activates safety alarm           |
| No-motion Timeout     | Enables energy-saving mode       |
| Manual Override       | Allows user-controlled operation |
| Manual Light          | Manually turns light ON          |
| Manual Fan            | Manually turns fan ON            |
| Manual Socket Relay   | Manually controls socket relay   |

---

## Output Signals

| Output        | Description                            |
| ------------- | -------------------------------------- |
| Light PWM     | Controls light brightness              |
| Fan PWM       | Controls fan speed                     |
| Socket Relay  | Controls socket appliance              |
| AC Relay      | Controls AC output                     |
| Alarm         | Indicates security or fault alarm      |
| Energy Saving | Indicates no-motion energy-saving mode |
| FSM State     | Shows controller operating state       |

---

## Control Logic

| Condition                           | Output Behavior                       |
| ----------------------------------- | ------------------------------------- |
| Motion detected and room is dark    | Light PWM turns ON                    |
| Temperature greater than threshold  | Fan PWM turns ON                      |
| Door open while security mode is ON | Alarm turns ON                        |
| Over-current fault detected         | Alarm turns ON and outputs go safe    |
| Manual override enabled             | Manual inputs get priority            |
| No-motion timeout active            | Appliances turn OFF for energy saving |
| Normal sensor condition             | Controller stays in AUTO mode         |

---

## Priority Logic

The controller uses the following priority order:

```text
1. Over-current safety alarm
2. Security alarm
3. Manual override
4. Sensor-based automation
5. Energy-saving timeout
```

This means safety and security conditions are handled before normal automation.

---

## FSM States

| State       | Meaning                                |
| ----------- | -------------------------------------- |
| AUTO        | Sensor-based automation is active      |
| MANUAL      | Manual override is active              |
| SECURITY    | Security alarm condition is active     |
| FAULT       | Over-current or safety fault condition |
| ENERGY_SAVE | No-motion energy-saving mode           |

---

## Sample Output

Example simulation input:

```text
Temperature = 34°C
Temperature Threshold = 30°C
Motion Detected = ON
Room Dark = ON
Door Open = ON
Security Mode = OFF
Over-current Fault = OFF
Manual Override = OFF
```

Expected output:

```text
FSM State = AUTO
Light PWM = 220
Fan PWM = 170
Socket Relay = ON
AC Relay = OFF
Alarm = OFF
Energy Saving = OFF
```

Explanation:

```text
Motion detected and room is dark, so light PWM is enabled.
Temperature is above threshold, so fan PWM is enabled.
Security mode is OFF, so door open does not trigger alarm.
```

---

## Tech Stack

### Hardware / VLSI

* Verilog HDL
* FPGA-based control logic
* RTL design
* Testbench simulation

### Backend

* Python
* FastAPI
* Uvicorn
* CSV logging
* PDF report generation

### Frontend

* HTML
* CSS
* JavaScript
* Static frontend server

---

## Folder Structure

```text
Smart-Home-Automation-FPGA/
│
├── backend/
│   ├── main.py
│   ├── run_backend.bat
│   ├── requirements.txt
│   ├── data/
│   ├── rtl/
│   └── README.md
│
├── frontend/
│   ├── index.html
│   ├── assets/
│   │   ├── styles.css
│   │   └── app.js
│   └── run_frontend.bat
│
├── rtl/
│   └── smart_home_controller.v
│
├── tb/
│   └── smart_home_controller_tb.v
│
├── reports/
├── screenshots/
└── README.md
```

---

## How to Run Backend

Open PowerShell and run:

```powershell
cd "C:\Projects\VLSI\VLSI - Smart Home Automation Controller on FPGA\vlsi_smart_home_fpga_backend"
.\run_backend.bat
```

Backend will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## How to Run Frontend

Open another PowerShell window and run:

```powershell
cd "C:\Projects\VLSI\VLSI - Smart Home Automation Controller on FPGA\vlsi_smart_home_fpga_frontend"
py -3.10 -m http.server 5600 --bind 127.0.0.1
```

Open in browser:

```text
http://127.0.0.1:5600/index.html
```

---

## How to Use the Simulator

1. Start the backend.
2. Start the frontend.
3. Open the frontend dashboard in browser.
4. Enter temperature and threshold values.
5. Select sensor inputs such as motion, dark room, door open, and security mode.
6. Enable or disable manual override.
7. Click **Evaluate**.
8. Check FSM state, PWM outputs, relay status, alarm status, and logs.
9. Download CSV/PDF reports.
10. View RTL and testbench source code.

---

## Verilog RTL

The RTL module implements:

* Sensor input handling
* Manual override priority
* Security alarm condition
* Over-current fault condition
* PWM output assignment
* Relay output control
* Energy-saving state
* FSM-based output control

Main RTL file:

```text
rtl/smart_home_controller.v
```

---

## Testbench

The testbench verifies:

* Reset behavior
* Motion and dark-room condition
* Temperature-based fan control
* Door and security alarm
* Manual override condition
* Energy-saving timeout
* Over-current fault handling

Testbench file:

```text
tb/smart_home_controller_tb.v
```

---

## Simulation and Verification

The design can be simulated using:

* ModelSim
* Xilinx Vivado Simulator
* Icarus Verilog
* EDA Playground

Expected waveform checks:

* Light output turns ON when motion and darkness are active.
* Fan output turns ON when temperature exceeds threshold.
* Alarm turns ON during security breach or over-current fault.
* Manual override has higher priority than sensor automation.
* Energy-saving disables appliances during no-motion timeout.

---

## Applications

* Smart home automation
* Building automation
* Classroom energy control
* Security systems
* IoT-based appliance control
* Embedded automation systems
* Industrial control logic
* FPGA-based safety controllers

---

## Future Improvements

* Add real FPGA board implementation
* Add UART communication with ESP32
* Add MQTT or Blynk mobile control
* Add LCD or seven-segment display
* Add real PIR, LDR, and temperature sensors
* Add password-based security mode
* Add energy usage monitoring
* Add Wi-Fi dashboard integration
* Add formal verification for safety logic
* Add synthesis and utilization reports

---

## Learning Outcomes

Through this project, I learned:

* How FPGA can be used for real-time automation control
* How to design FSM-based control logic
* How to implement priority logic in digital systems
* How to use Verilog for RTL design
* How to write and understand testbench verification
* How to simulate sensor-based automation
* How PWM is used for light and fan control
* How safety and manual override logic is handled
* How to connect a frontend dashboard with a backend simulator
* How to document and present a VLSI project on GitHub

---

## Interview Questions and Answers

### 1. Explain your project.

This project is a Smart Home Automation Controller designed using FPGA logic. It takes inputs from simulated sensors such as PIR motion sensor, LDR light sensor, temperature sensor, door sensor, security mode, and manual switches. Based on these inputs, it controls outputs such as light PWM, fan PWM, socket relay, AC relay, and alarm. The design was verified using simulation, logs, reports, RTL code, and testbench.

### 2. Which VLSI concepts are used in this project?

This project uses Verilog RTL design, combinational logic, sequential logic, finite state machine, priority logic, PWM generation, clock/reset handling, testbench verification, and waveform analysis.

### 3. Why did you choose FPGA for smart home automation?

FPGA provides parallel processing, fast response time, deterministic behavior, and reconfigurable hardware. This makes it suitable for real-time control applications such as automation and safety systems.

### 4. What is the role of FSM in this project?

The FSM decides the operating state of the controller, such as AUTO, MANUAL, SECURITY, FAULT, and ENERGY_SAVE. It helps organize system behavior clearly and predictably.

### 5. What is manual override?

Manual override allows the user to directly control appliances even when automatic sensor logic is active. It is given higher priority than normal automation.

### 6. How does the alarm logic work?

The alarm turns ON when a security breach or over-current fault is detected. For example, if the door opens while security mode is active, the alarm output becomes ON.

### 7. How does energy saving work?

When no motion is detected for a timeout condition, the system turns OFF unnecessary appliances and enters energy-saving mode.

### 8. How did you verify the design?

The design was verified using a testbench and virtual simulation. Different input conditions were applied, and the output signals were checked using dashboard logs and waveform-style behavior.

### 9. What are the main outputs of the system?

The main outputs are light PWM, fan PWM, socket relay, AC relay, alarm signal, energy-saving status, and FSM state.

### 10. How can this project be improved?

The project can be improved by adding real FPGA hardware implementation, ESP32 UART communication, MQTT control, real sensors, LCD display, energy monitoring, mobile app control, and formal verification.

---

## Conclusion

This project demonstrates how digital design and FPGA logic can be applied to a real-world smart home automation problem. It combines Verilog RTL design, FSM control, priority-based decision making, PWM output control, safety alarm handling, simulation, backend API, frontend dashboard, and report generation.

The project is suitable for VLSI coursework, GitHub portfolio building, and interview preparation.

```

This README matches your uploaded project requirement, including the FPGA objective, RTL/testbench requirement, simulation proof, GitHub readiness, screenshots checklist, and interview preparation sections. :contentReference[oaicite:0]{index=0}
```

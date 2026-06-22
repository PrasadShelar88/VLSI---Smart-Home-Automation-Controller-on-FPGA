@echo off
cd /d "%~dp0"

echo Starting VLSI Smart Home FPGA backend...
echo Backend will run at http://127.0.0.1:8000
echo This beginner version does not need pip install or internet.

py -3.10 simple_backend.py
if errorlevel 1 py simple_backend.py
if errorlevel 1 python simple_backend.py

pause

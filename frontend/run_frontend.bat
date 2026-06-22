@echo off
cd /d "%~dp0"

echo Starting VLSI Smart Home FPGA frontend...
echo Frontend will run at http://127.0.0.1:5500
echo Keep this window open while using the dashboard.

py -3.10 -m http.server 5500
if errorlevel 1 py -m http.server 5500
if errorlevel 1 python -m http.server 5500

pause

@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (echo Run SETUP_WINDOWS.bat first & pause & exit /b 1)
start "DocMind" ".venv\Scripts\pythonw.exe" "desktop.py"

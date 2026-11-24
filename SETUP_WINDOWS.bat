@echo off
cd /d "%~dp0"
py -3.11 -m venv .venv || (echo Install Python 3.11 from python.org & pause & exit /b 1)
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (echo Installation failed. & pause & exit /b 1)
echo Setup finished. Double-click START_DOCMIND.bat
pause

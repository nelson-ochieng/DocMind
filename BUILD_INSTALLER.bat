@echo off
cd /d "%~dp0"
if not exist "dist\DocMind\DocMind.exe" (echo Run BUILD_WINDOWS.bat first & pause & exit /b 1)
"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" DocMind.iss
if errorlevel 1 (echo Install Inno Setup 6 or open DocMind.iss manually and compile. & pause & exit /b 1)
pause

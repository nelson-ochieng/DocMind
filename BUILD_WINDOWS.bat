@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Run SETUP_WINDOWS.bat first & pause & exit /b 1)
.venv\Scripts\python.exe -m pip install pyinstaller
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --collect-all matplotlib --collect-all fitz --collect-all pymupdf --collect-all pytesseract --name DocMind --collect-all chromadb --collect-all onnxruntime --collect-all tokenizers --collect-all posthog desktop.py
if errorlevel 1 (echo Build failed. & pause & exit /b 1)
echo Executable generated in dist\DocMind\DocMind.exe
pause

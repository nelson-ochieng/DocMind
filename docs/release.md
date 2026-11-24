# Windows build and release checklist

Source setup uses SETUP_WINDOWS.bat, then BUILD_WINDOWS.bat. Keep the complete dist/DocMind directory. Install Inno Setup 6 and compile DocMind.iss using BUILD_INSTALLER.bat or directly in Inno Setup. Ollama and models remain separate prerequisites. CI build workflow is manually triggered and does not publish binaries.

Before public binary distribution:
- [ ] License decision and full dependency inventory approved.
- [ ] CI passes on Windows and Linux.
- [ ] Build succeeds on Windows.
- [ ] Clean Windows 11 install and uninstall tested.
- [ ] Live Ollama tests with llama3.2:3b and optional qwen3:4b; check memory on 8 GB.
- [ ] PDF/DOCX/TXT ingestion, OCR, citations, fallback and reports tested.
- [ ] No reasoning leakage or invented quotes on synthetic regression fixtures.
- [ ] Check installer contents, malware scan, signing status and SHA-256.
- [ ] Publish release notes with limitations and label prerelease.

An executable build is not a GUI smoke test or accuracy benchmark. Never upload private documents or model weights.

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

## Download and test a private build
The manual Windows build workflow packages the installer, portable ZIP and SHA256SUMS.txt. Upload is enabled only when the repository is private; public repositories skip upload pending licensing clearance. Artifacts expire after seven days. No GitHub release is created.

After changing repository visibility to private (owner decision), run the Windows build workflow again and download DocMind-Windows-4.2.0-test from the successful run's Artifacts section. Extract the outer ZIP and verify the installer and portable ZIP with Get-FileHash -Algorithm SHA256 against SHA256SUMS.txt. Back up %LOCALAPPDATA%\\DocMind before installation. Keep Ollama running with llama3.2:3b and nomic-embed-text installed. Test launch, synthetic document ingestion, citations, exports, restart and uninstall. Extract the portable ZIP completely before launching DocMind.exe; keep its _internal directory. Builds are unsigned; verify provenance and scan locally. Do not bypass organizational security policy.

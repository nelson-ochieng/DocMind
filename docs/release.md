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

## Restricted artifact downloads

The manual [Windows build workflow](../.github/workflows/windows-build.yml) runs tests, compiles the application and installer, and packages three files:

| File | Purpose |
| --- | --- |
| DocMind-Setup.exe | Per-user Windows installer |
| DocMind-Portable.zip | Complete application directory |
| SHA256SUMS.txt | SHA-256 hashes of both packages |

Upload is restricted to private repositories and retention is seven days. Public repositories skip upload. No automatic release is created. Private repository readers can access artifacts; private access does not itself establish redistribution rights. Keep access limited to authorized testers and complete the dependency licensing review before wider distribution.

1. As repository owner, confirm private visibility in Settings. Do not change visibility without owner approval.
2. Open Actions > Windows build validation > Run workflow; select main.
3. Wait for a successful run and confirm the Retain restricted test artifacts step succeeded.
4. Download DocMind-Windows-4.2.0-test from Artifacts and extract the outer ZIP.
5. If no artifact appears, check repository visibility, upload step, retention expiry and run permissions. Re-run if expired.

## Verify downloads

Open PowerShell in the extracted directory:

```powershell
Get-Content .\SHA256SUMS.txt
Get-FileHash .\DocMind-Setup.exe -Algorithm SHA256
Get-FileHash .\DocMind-Portable.zip -Algorithm SHA256
```

Compare each complete hash with its corresponding manifest entry (case insensitive). Stop if either differs. Check the run's source commit and scan the files with Windows Security. Checksums detect corruption but do not authenticate an unsigned publisher. Do not bypass organizational security controls.

## Windows 11 smoke test

Use an authorized Windows 11 test machine, preferably a clean VM or separate test account. Record Windows version, RAM, commit SHA, workflow run URL, tester and date. Close DocMind and back up its existing data directory at `%LOCALAPPDATA%\DocMind` before testing. Use synthetic documents only.

### Setup

- Run DocMind-Setup.exe and confirm installation under `%LOCALAPPDATA%\Programs\DocMind` and creation of Start menu and desktop shortcuts.
- Launch from the shortcut without VS Code or a Python terminal.
- Install Ollama separately if needed. Verify models with `ollama list`; use `ollama pull llama3.2:3b` and `ollama pull nomic-embed-text` if missing. Model downloads require network access.
- Check Ollama connectivity with `Invoke-RestMethod http://127.0.0.1:11434/api/tags` in PowerShell.
- OCR may require a separately installed Tesseract executable. Record whether it is available.

### Test cases

Record PASS, FAIL or NOT RUN for each case; never count an unexecuted case as passed.

| ID | Action | Expected result |
| --- | --- | --- |
| W01 | Install as ordinary user | Installation completes without unexpected elevation |
| W02 | Launch from shortcut | Main window opens without crash |
| W03 | Connect to local Ollama | Installed models available; no paid API needed |
| W04 | Upload synthetic PDF, DOCX and TXT | Each supported document indexes successfully |
| W05 | Ask a question with a known answer | Answer matches the document and cites supporting text |
| W06 | Ask about a fact absent from the document | No invented evidence; uncertainty or fallback is explicit |
| W07 | Inspect citations | Referenced excerpts match the original document and page where applicable |
| W08 | Ask a methodology question | No raw reasoning leakage; no invented quotations |
| W09 | Export supported reports and diagrams | Files open and contain expected content |
| W10 | Restart application | Existing indexed documents and history remain accessible |
| W11 | Disconnect Ollama and ask a question | Failure is visible; application does not silently invent an answer |
| W12 | Test scanned PDF with OCR available | Text is extracted or a clear limitation is reported |
| W13 | Extract portable ZIP fully and launch DocMind.exe | Application opens with _internal directory intact |
| W14 | Observe Task Manager during indexing and answering on 8 GB RAM | Record peak memory, latency and any freezes or crashes |
| W15 | Uninstall using Windows Settings > Apps > Installed apps | Program and shortcuts removed; verify data handling separately |

Portable packaging does not imply isolated data storage: installed and portable versions may share the same user data directory. Test separately and retain backups. Do not delete user documents or data merely to test uninstall.

### Synthetic evidence fixture

Create a TXT document containing: "Project Cedar collected 24 samples in March 2025. The team used a calibrated temperature sensor. The report does not state a project budget." Ask how many samples were collected, which instrument was used, and what the budget was. Expect 24, a calibrated temperature sensor, and no invented budget. Repeat with PDF and DOCX versions, using separate test collections or removing duplicates as appropriate.

### Test report

Record the environment, build commit, workflow run, package hashes, model names, test IDs and results, actual behavior, reproduction steps and sanitized screenshots or logs. Do not include private documents, tokens or model weights in GitHub issues.

### Release gate

A successful build is not a successful smoke test. Resolve critical launch, data-loss, security and citation failures before release. Review packaging warnings, dependency licenses and unsigned installer status. Record outstanding limitations and keep public distribution disabled until approved. This guide defines tests; it does not claim they have been executed.

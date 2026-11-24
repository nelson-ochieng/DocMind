# DocMind 4.2.0 — Developer preview

Local desktop research assistant for PDF, DOCX and text documents. Ask questions, inspect cited evidence and export research notes using Ollama, Python, ChromaDB and Qt.

[![Tests](https://github.com/nelson-ochieng/DocMind/actions/workflows/tests.yml/badge.svg)](https://github.com/nelson-ochieng/DocMind/actions/workflows/tests.yml)

**Preview, not production-ready.** No paid AI API is required. Model and dependency downloads require internet. Local inference is the default; a custom Ollama endpoint may transmit document content.

## Quick start (Windows 11)
1. Back up %LOCALAPPDATA%\DocMind if upgrading.
2. Install [Python 3.11](https://www.python.org/downloads/) and [Ollama](https://ollama.com/download/windows).
3. Clone this repository or download its source ZIP and extract it.
4. Run SETUP_WINDOWS.bat. In PowerShell run:
   ```powershell
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   # Optional: ollama pull qwen3:4b
   ```
5. Start Ollama and double-click START_DOCMIND.bat.
6. Add a document, select it and ask a question. Re-index older documents after backing up.

## Capabilities
- Local document library, chat history, light and dark themes.
- Section-aware retrieval and structured JSON evidence extraction.
- Exact normalized quotation matching and clickable source references.
- PDF page viewer, best-effort English OCR with separately installed Tesseract.
- Manual chart, evidence-outline diagrams, Word/PDF/text report exports.

Quotes are not proof of relevance or entailment. Answers are extractive, not comprehensive synthesis; visual outlines do not establish causality. Full LaTeX and automatic charts are not implemented. Local data is not encrypted. Do not use as the sole basis for consequential decisions.

## Development
Install requirements-dev.txt and run `python -m pytest -q` with Python 3.11. Tests use synthetic evidence and mocked inference; they do not establish live model accuracy. Windows GUI, installer and live database integration require independent validation.

- [Architecture](docs/architecture.md)
- [Windows build and release checklist](docs/release.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Dependency licensing review](docs/licensing.md)
- [Changelog](CHANGELOG.md)

## License
Project license not yet selected. Public visibility is not an open-source license. Binary redistribution is on hold pending dependency and model license review.

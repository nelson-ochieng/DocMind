# Preliminary dependency licensing review

No final project license has been chosen. Review exact installed versions and transitive packages before distribution.

| Dependency | Preliminary status |
|---|---|
| PyMuPDF / MuPDF | AGPLv3 or commercial; major redistribution blocker |
| PySide6 / Qt | LGPL/GPL or commercial; check bundled modules and relinking/notice requirements |
| PyInstaller | GPL with bootloader exception; dependency obligations remain |
| ChromaDB, pypdf, python-docx, requests, reportlab, pytesseract, Pillow, psutil, matplotlib, pytest | Exact wheel licenses and transitive dependencies still require audit |
| Ollama, Tesseract, Inno Setup | Separate tools; review terms for any bundled components |
| Llama, Qwen, nomic models | Review exact model tags, upstream weights and model-specific terms; not bundled |

Primary references:
- https://pymupdf.io/licensing
- https://pypi.org/project/PySide6/
- https://www.pyinstaller.org/en/stable/license.html

AGPL-3.0 is a candidate if the owner wants copyleft and all combined dependencies permit it. MIT alone does not resolve PyMuPDF obligations. Alternatively evaluate replacing PyMuPDF or obtaining a commercial license. This is a preliminary engineering review, not legal advice.

Before release: inventory exact versions, review transitive license texts, collect notices and corresponding source as required, check model terms, and document the approved distribution method. No binary publication until resolved.

# Security policy

This is an experimental developer preview without a guaranteed support or patch schedule. Report suspected vulnerabilities privately through the repository Security tab if private reporting is enabled. Otherwise contact the repository owner privately; do not publish exploit details or sensitive files in issues.

Include affected version, minimal synthetic reproduction, impact and environment. Never attach confidential documents, credentials, database contents or unredacted logs.

## Known boundaries
- Local documents and chats are not encrypted by DocMind.
- Custom OLLAMA_URL endpoints can receive document content.
- PDF parsing, OCR and model outputs are untrusted.
- Prompt injection and incorrect quotations or contextual interpretations remain possible.
- Unsigned preview binaries must not be represented as verified installers.

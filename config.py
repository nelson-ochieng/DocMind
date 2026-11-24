"""DocMind local configuration; data is stored outside the installation directory."""
from pathlib import Path
import os
import sys

if os.name == 'nt':
    DATA_DIR = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'DocMind'
else:
    DATA_DIR = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))) / 'DocMind'
DOCUMENTS_DIR = DATA_DIR / 'documents'
DATABASE_DIR = DATA_DIR / 'database'
EXPORTS_DIR = DATA_DIR / 'exports'
CHROMA_COLLECTION = 'docmind'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 5
SIMILARITY_THRESHOLD = 0.45
LLM_MODEL = os.getenv('DOCMIND_LLM_MODEL', 'llama3.2:3b')
EMBEDDING_MODEL = os.getenv('DOCMIND_EMBEDDING_MODEL', 'nomic-embed-text')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434')
MAX_UPLOAD_MB = 25
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
for directory in (DOCUMENTS_DIR, DATABASE_DIR, EXPORTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

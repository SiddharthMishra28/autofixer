from __future__ import annotations

from pathlib import Path

from autofixer_agent.rag.chromadb_store import RagDocument
from autofixer_agent.rag.chunking import chunk_text

SUPPORTED_CODE_EXTENSIONS = {
    ".java": "java",
    ".feature": "cucumber",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".xml": "testng_or_config",
}


def ingest_code_directory(path: str) -> list[RagDocument]:
    root = Path(path)
    documents: list[RagDocument] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_CODE_EXTENSIONS:
            continue

        language = SUPPORTED_CODE_EXTENSIONS[file_path.suffix.lower()]
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for chunk in chunk_text(text):
            documents.append(
                RagDocument(
                    content=chunk,
                    metadata={
                        "source_type": "code",
                        "language": language,
                        "path": str(file_path),
                    },
                )
            )

    return documents

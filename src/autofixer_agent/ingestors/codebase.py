from __future__ import annotations

from pathlib import Path

from autofixer_agent.rag.chromadb_store import RagDocument
from autofixer_agent.rag.chunking import chunk_text

SUPPORTED_CODE_EXTENSIONS = {
    ".java": "java",
    ".feature": "karate_or_cucumber",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".xml": "testng_or_config",
}


def _framework_hint(file_path: Path, text: str) -> str:
    if file_path.suffix.lower() != ".feature":
        return ""
    lowered = text.lower()
    if "karate" in lowered or "match " in lowered or "def " in lowered:
        return "karate"
    return "cucumber"


def ingest_code_directory(path: str) -> list[RagDocument]:
    root = Path(path)
    documents: list[RagDocument] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_CODE_EXTENSIONS:
            continue

        language = SUPPORTED_CODE_EXTENSIONS[file_path.suffix.lower()]
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        framework = _framework_hint(file_path, text)
        for chunk in chunk_text(text):
            metadata = {
                "source_type": "code",
                "language": language,
                "path": str(file_path),
            }
            if framework:
                metadata["framework"] = framework
            documents.append(RagDocument(content=chunk, metadata=metadata))

    return documents

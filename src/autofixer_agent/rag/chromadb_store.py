from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import chromadb


@dataclass
class RagDocument:
    content: str
    metadata: dict


class ChromaRagStore:
    def __init__(self, persist_dir: str = ".chroma") -> None:
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)

    def add_documents(self, collection: str, documents: Iterable[RagDocument]) -> int:
        records = list(documents)
        if not records:
            return 0

        col = self.client.get_or_create_collection(collection)
        col.add(
            ids=[str(uuid4()) for _ in records],
            documents=[r.content for r in records],
            metadatas=[r.metadata for r in records],
        )
        return len(records)

    def query(self, collection: str, query: str, n_results: int = 5) -> dict:
        col = self.client.get_or_create_collection(collection)
        return col.query(query_texts=[query], n_results=n_results)

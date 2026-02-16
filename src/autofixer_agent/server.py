from __future__ import annotations

import os

import gitlab
from fastmcp import FastMCP

from autofixer_agent.ingestors.codebase import ingest_code_directory
from autofixer_agent.ingestors.excel import ingest_excel
from autofixer_agent.ingestors.text_docs import ingest_text_document
from autofixer_agent.rag.chromadb_store import ChromaRagStore

mcp = FastMCP("autofixer-maintenance-agent")
store = ChromaRagStore(persist_dir=os.getenv("CHROMA_PERSIST_DIR", ".chroma"))


@mcp.tool
def ingest_excel_to_rag(path: str, collection: str = "maintenance_knowledge") -> dict:
    """Read any Excel workbook, normalize cell-level content, and index it in ChromaDB."""
    docs = ingest_excel(path)
    count = store.add_documents(collection, docs)
    return {"indexed_documents": count, "collection": collection, "source": path}


@mcp.tool
def ingest_text_to_rag(path: str, collection: str = "maintenance_knowledge") -> dict:
    """Read a text-style document (txt/pdf/docx/json/html/etc) and index it in ChromaDB."""
    docs = ingest_text_document(path)
    count = store.add_documents(collection, docs)
    return {"indexed_documents": count, "collection": collection, "source": path}


@mcp.tool
def ingest_codebase_to_rag(path: str, collection: str = "maintenance_knowledge") -> dict:
    """Read Java/Cucumber/TestNG/Python/JS/TS repositories and index them in ChromaDB."""
    docs = ingest_code_directory(path)
    count = store.add_documents(collection, docs)
    return {"indexed_documents": count, "collection": collection, "source": path}


@mcp.tool
def query_rag(collection: str, query: str, n_results: int = 5) -> dict:
    """Query indexed RAG data from ChromaDB."""
    return store.query(collection=collection, query=query, n_results=n_results)


@mcp.tool
def gitlab_issue_and_mr_context(
    project_id: str,
    issue_iid: int | None = None,
    merge_request_iid: int | None = None,
    gitlab_url: str = "https://gitlab.com",
) -> dict:
    """Fetch issue and/or merge request context from GitLab for patch generation workflows."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise ValueError("Set GITLAB_TOKEN before using gitlab_issue_and_mr_context")

    gl = gitlab.Gitlab(url=gitlab_url, private_token=token)
    project = gl.projects.get(project_id)

    payload: dict = {"project": project.path_with_namespace}
    if issue_iid is not None:
        issue = project.issues.get(issue_iid)
        payload["issue"] = {
            "iid": issue.iid,
            "title": issue.title,
            "description": issue.description,
            "state": issue.state,
            "labels": issue.labels,
            "web_url": issue.web_url,
        }

    if merge_request_iid is not None:
        mr = project.mergerequests.get(merge_request_iid)
        changes = mr.changes()
        payload["merge_request"] = {
            "iid": mr.iid,
            "title": mr.title,
            "description": mr.description,
            "state": mr.state,
            "source_branch": mr.source_branch,
            "target_branch": mr.target_branch,
            "web_url": mr.web_url,
            "changes": changes.get("changes", []),
        }

    return payload


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

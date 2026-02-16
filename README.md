# Autofixer FastMCP Custom Agent

This repository provides a **FastMCP** server that exposes tools for:

1. Ingesting nearly any Excel workbook into a standard cell-level text representation and creating embeddings in ChromaDB.
2. Ingesting text documents (TXT/MD/JSON/HTML/PDF/DOCX, etc.) and creating embeddings in ChromaDB.
3. Fetching issue / merge request context from GitLab.
4. Ingesting code repositories (Java, Cucumber, TestNG XML, Python, JS/TS) into ChromaDB for RAG.

It is designed for maintenance scenarios where an agent fetches ticket + diff context, queries framework knowledge, and proposes patches.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run the MCP server

```bash
autofixer-mcp
```

## Exposed tools

- `ingest_excel_to_rag(path, collection)`
- `ingest_text_to_rag(path, collection)`
- `ingest_codebase_to_rag(path, collection)`
- `query_rag(collection, query, n_results)`
- `gitlab_issue_and_mr_context(project_id, issue_iid?, merge_request_iid?, gitlab_url?)`

## Suggested operating flow

1. Use `ingest_codebase_to_rag` on your automation framework repos.
2. Use `ingest_excel_to_rag` and `ingest_text_to_rag` for support docs, execution history, and SOPs.
3. Pull issue + MR diff context via `gitlab_issue_and_mr_context` (or the official GitLab MCP server).
4. Query `query_rag` for failing module patterns and known fixes.
5. Generate patch and tests in your Copilot agent prompt / custom instructions.

## VS Code / GitHub Copilot integration

- `.vscode/mcp.json` includes both this custom server and the GitLab MCP server.
- `.github/copilot-instructions.md` defines the expected maintenance-agent behavior.

For a complete setup guide, see `docs/setup_custom_agent.md`.

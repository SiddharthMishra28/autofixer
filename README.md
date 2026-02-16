# Autofixer FastMCP Custom Agent

A beginner-friendly **FastMCP** server that gives you MCP tools for:

1. Ingesting Excel files (including complex sheets with merged cells/formulas) into a RAG index.
2. Ingesting text documents (TXT/MD/JSON/HTML/PDF/DOCX) into the same RAG index.
3. Ingesting test automation codebases (Java, Cucumber, TestNG XML, Python, JS/TS).
4. Querying the indexed knowledge from ChromaDB.
5. Fetching issue + merge-request context from GitLab.

If you are new to MCP, RAG, or local Python setup, start here:

- **Beginner setup + usage guide:** [`docs/setup_custom_agent.md`](docs/setup_custom_agent.md)
- **Quick start (10 minutes):** [`docs/quickstart.md`](docs/quickstart.md)

---

## What this project solves

Maintenance work is usually hard because context is spread across:
- tickets,
- diffs,
- test framework code,
- runbooks and support docs,
- mapping sheets and reports.

This server standardizes all of that into searchable chunks in **ChromaDB**, so an AI coding agent can:
- fetch ticket/diff context,
- retrieve framework knowledge via RAG,
- suggest fixes and patches with better context.

---

## Repository layout

```text
.
├── src/autofixer_agent/
│   ├── server.py                     # FastMCP server + tools
│   ├── ingestors/
│   │   ├── excel.py                  # Excel to normalized text chunks
│   │   ├── text_docs.py              # Text/PDF/Docx/HTML parsing
│   │   └── codebase.py               # Code directory parsing
│   └── rag/
│       ├── chunking.py               # chunking strategy
│       └── chromadb_store.py         # Chroma wrapper
├── .vscode/mcp.json                  # MCP server config for VS Code
├── .github/copilot-instructions.md   # Copilot behavior guidance
├── docs/quickstart.md                # fast path for experienced users
└── docs/setup_custom_agent.md        # absolute beginner setup and usage
```

---

## Quick install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then run:

```bash
autofixer-mcp
```

---

## Available MCP tools

- `ingest_excel_to_rag(path, collection="maintenance_knowledge")`
- `ingest_text_to_rag(path, collection="maintenance_knowledge")`
- `ingest_codebase_to_rag(path, collection="maintenance_knowledge")`
- `query_rag(collection, query, n_results=5)`
- `gitlab_issue_and_mr_context(project_id, issue_iid=None, merge_request_iid=None, gitlab_url="https://gitlab.com")`

---

## Typical maintenance workflow

1. Ingest framework repositories with `ingest_codebase_to_rag`.
2. Ingest ops docs, runbooks, and sheets with `ingest_text_to_rag` + `ingest_excel_to_rag`.
3. Pull issue and MR context from GitLab using `gitlab_issue_and_mr_context`.
4. Ask `query_rag` for historical patterns and module-level context.
5. Use that context in your coding assistant (Copilot/custom agent) to generate safer patches.

---

## Important notes

- ChromaDB persistence defaults to `.chroma` in the workspace.
- `gitlab_issue_and_mr_context` requires `GITLAB_TOKEN`.
- `.vscode/mcp.json` also includes the official GitLab MCP server via `npx @gitlab-org/gitlab-mcp`.

For detailed troubleshooting and OS-specific setup, use the full beginner guide in `docs/setup_custom_agent.md`.

# Setup: Custom Maintenance Agent with FastMCP + GitLab MCP + Copilot

## 1) Start the custom FastMCP server

```bash
pip install -e .
autofixer-mcp
```

## 2) Configure MCP servers in VS Code

Copy `.vscode/mcp.json` into your workspace (already included in this repo). It registers:
- `autofixer-maintenance-agent` (custom FastMCP server)
- `gitlab` (official GitLab MCP server)

> Set `GITLAB_TOKEN` / `GITLAB_PAT` to a personal access token with API scope.

## 3) Bootstrap your RAG knowledge store

Use MCP calls from a chat client:

- `ingest_codebase_to_rag(path="/path/to/framework-repo")`
- `ingest_excel_to_rag(path="/path/to/test-mapping.xlsx")`
- `ingest_text_to_rag(path="/path/to/runbook.pdf")`

## 4) Configure Copilot custom agent behavior

Use `.github/copilot-instructions.md` (already included) to enforce this sequence:
1. Read ticket/MR context from GitLab tools.
2. Query RAG for framework and historical fixes.
3. Propose minimal patch + tests.
4. Explain root cause and impact.

## 5) Example maintenance prompt for Copilot Chat

```text
Act as Autofixer maintenance agent.
- Pull GitLab issue #123 and MR #456 context.
- Query RAG for classes/features related to LoginTest and flaky retry logic.
- Propose a patch limited to failing modules.
- Include tests and rollback considerations.
```

## 6) Recommended production hardening

- Add a stronger embedding model through Chroma embedding functions.
- Add PII filters before indexing business documents.
- Add collection versioning (`framework_v1`, `framework_v2`) for safer upgrades.
- Add RBAC and audit logs around ingestion and query tools.

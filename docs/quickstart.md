# Quickstart (10 minutes)

This is the shortest path if you already know Python and VS Code.

## 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) Export token (optional but needed for GitLab tool)

```bash
export GITLAB_TOKEN="<your_gitlab_pat>"
```

## 3) Run server

```bash
autofixer-mcp
```

## 4) Ingest data from MCP client

Use these tool calls:

```text
ingest_codebase_to_rag(path="/path/to/repo")
ingest_excel_to_rag(path="/path/to/data.xlsx")
ingest_text_to_rag(path="/path/to/runbook.pdf")
```

## 5) Query RAG

```text
query_rag(collection="maintenance_knowledge", query="Why is LoginTest flaky in retry flow?", n_results=5)
```

## 6) Get GitLab context

```text
gitlab_issue_and_mr_context(project_id="group/project", issue_iid=123, merge_request_iid=456)
```

For complete beginner instructions and troubleshooting, use `docs/setup_custom_agent.md`.

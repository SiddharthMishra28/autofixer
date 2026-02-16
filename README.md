# Autofixer FastMCP Custom Agent

A beginner-friendly **FastMCP** server with advanced **Karate automation maintenance** support.

## Core capabilities

1. Ingest Excel files (including complex sheets with merged cells/formulas) into RAG.
2. Ingest text docs (TXT/MD/JSON/HTML/PDF/DOCX) into RAG.
3. Ingest code repositories (Java, TestNG, Cucumber/Karate feature files, Python, JS/TS).
4. Query indexed knowledge from ChromaDB.
5. Fetch issue/MR context from GitLab.
6. Parse Karate scenarios/assertions into structured metadata.
7. Normalize Excel mapping sheets into canonical records for assertion maintenance.
8. Link mapping records to Karate assertions and generate patch suggestions.
9. Apply patches with branch safety controls + change budgets.
10. Run validation commands (Maven/Gradle/etc.) and collect logs.

## Start here

- **Beginner setup + usage guide:** [`docs/setup_custom_agent.md`](docs/setup_custom_agent.md)
- **Quick start (10 minutes):** [`docs/quickstart.md`](docs/quickstart.md)

## Available MCP tools

### Generic ingestion/query
- `ingest_excel_to_rag(path, collection="maintenance_knowledge")`
- `ingest_text_to_rag(path, collection="maintenance_knowledge")`
- `ingest_codebase_to_rag(path, collection="maintenance_knowledge")`
- `query_rag(collection, query, n_results=5)`
- `gitlab_issue_and_mr_context(project_id, issue_iid=None, merge_request_iid=None, gitlab_url="https://gitlab.com")`

### Karate-specific maintenance
- `ingest_karate_features_to_rag(path, collection="karate_features")`
- `normalize_excel_mapping_to_rag(path, collection="karate_mappings")`
- `suggest_karate_assertion_updates(karate_collection="karate_features", mapping_collection="karate_mappings", min_confidence=0.60)`
- `propose_karate_assertion_patches(karate_collection="karate_features", mapping_collection="karate_mappings", min_confidence=0.70, max_files=10, max_hunks=50)`
- `apply_karate_assertion_patches(repo_path, ..., dry_run=True, max_files=10, max_hunks=50, allow_protected_branch=False)`
- `run_karate_validation(command, repo_path, timeout_s=300)`

## Karate automatic maintenance flow

1. Index features with `ingest_karate_features_to_rag`.
2. Normalize + index mapping workbook with `normalize_excel_mapping_to_rag`.
3. Review link output from `suggest_karate_assertion_updates`.
4. Generate diff preview using `propose_karate_assertion_patches`.
5. Apply safely using `apply_karate_assertion_patches` in non-protected branch.
6. Validate by executing `run_karate_validation`.

## Safety controls built in

- Protected branch guard (`main`, `master`, `release`) on write flow.
- Change budget limits (`max_files`, `max_hunks`).
- Audit trail linking patch actions to mapping source sheet/cell.

## Quick install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
autofixer-mcp
```

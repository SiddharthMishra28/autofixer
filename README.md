# Autofixer FastMCP Custom Agent

A beginner-friendly **FastMCP** server for **Karate automation maintenance** with a reuse-first patching workflow.

This project helps you:
- ingest Karate `.feature` files, Excel mapping sheets, and docs into a RAG store,
- detect reusable assertions/utilities first,
- generate safer patch previews,
- apply changes with branch safety + change budgets,
- validate with Maven/Gradle commands,
- run everything via MCP (including VS Code MCP integration).

---

## 1) Who this is for (absolute beginners)

If you are new to MCP, Python virtual environments, or VS Code MCP setup, this README gives a complete copy/paste path.

If you prefer long-form details, also read:
- `docs/setup_custom_agent.md`
- `docs/quickstart.md`

---

## 2) What you can do with this agent

### Generic ingestion/query
- `ingest_excel_to_rag(path, collection="maintenance_knowledge")`
- `ingest_text_to_rag(path, collection="maintenance_knowledge")`
- `ingest_codebase_to_rag(path, collection="maintenance_knowledge")`
- `query_rag(collection, query, n_results=5)`
- `gitlab_issue_and_mr_context(project_id, issue_iid=None, merge_request_iid=None, gitlab_url="https://gitlab.com")`

### Karate-specific maintenance
- `ingest_karate_features_to_rag(path, collection="karate_features")`
- `normalize_excel_mapping_to_rag(path, collection="karate_mappings")`
- `analyze_karate_reuse_candidates(mapping_collection="karate_mappings", karate_collection="karate_features", top_k=5)`
- `suggest_karate_assertion_updates(..., min_confidence=0.60)`
- `propose_karate_assertion_patches(..., min_confidence=0.70, max_files=10, max_hunks=50)`
- `apply_karate_assertion_patches(..., dry_run=True, max_files=10, max_hunks=50, allow_protected_branch=False)`
- `run_karate_validation(command, repo_path, timeout_s=300)`

---

## 3) Install (copy/paste)

### 3.1 Prerequisites
- Python 3.10+
- VS Code (optional, for MCP UI)
- Node.js (optional, only if you want the GitLab MCP server in VS Code via `npx`)

### 3.2 Create and activate a virtual environment

#### macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Windows CMD
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3.3 Install package
```bash
pip install -e .
```

### 3.4 Start server
```bash
autofixer-mcp
```

---

## 4) VS Code MCP setup (beginner-friendly)

This repository already includes `.vscode/mcp.json` with both:
- `autofixer-maintenance-agent` (this custom server)
- `gitlab` (official GitLab MCP server)

### Steps
1. Open this repository folder in VS Code.
2. Ensure Python environment is active and package is installed (`pip install -e .`).
3. Ensure token env values are set in VS Code MCP input/env flow:
   - `GITLAB_TOKEN` (used by custom tool `gitlab_issue_and_mr_context`)
   - `GITLAB_PAT` (used by official GitLab MCP server)
4. Open your MCP-capable chat/tool panel and confirm servers appear.
5. Test with a simple call like:
   - `query_rag(collection="maintenance_knowledge", query="hello", n_results=1)`

If GitLab MCP server fails, verify `npx --version` from terminal.

---

## 5) Reuse-first Karate maintenance workflow (recommended)

This is the key behavior: **the agent checks existing assertions/utilities first, and only creates new script patterns if nothing fits**.

### Step A: Ingest Karate feature files
```text
ingest_karate_features_to_rag(path="/absolute/path/to/karate-repo")
```

### Step B: Normalize mapping workbook
```text
normalize_excel_mapping_to_rag(path="/absolute/path/to/assertion-mapping.xlsx")
```

### Step C: Reuse-first check
```text
analyze_karate_reuse_candidates(top_k=5)
```
Look for `reuse_found=true` and candidate expressions.

### Step D: Suggest updates
```text
suggest_karate_assertion_updates(min_confidence=0.70)
```
Review `strategy` in each suggestion:
- `reuse_existing` (preferred)
- `create_new` (fallback when reuse not possible)

### Step E: Patch preview
```text
propose_karate_assertion_patches(min_confidence=0.75, max_files=10, max_hunks=50)
```
Review unified diff and audit trail.

### Step F: Apply patch safely
```text
apply_karate_assertion_patches(
  repo_path="/absolute/path/to/karate-repo",
  dry_run=false,
  min_confidence=0.80,
  max_files=10,
  max_hunks=50,
  allow_protected_branch=false
)
```

### Step G: Validate
```text
run_karate_validation(command="mvn -Dtest=KarateRunner test", repo_path="/absolute/path/to/karate-repo")
```
(or use your Gradle command)

---

## 6) Safety controls included

- Protected branch write guard for `main`, `master`, `release`.
- Change budgets (`max_files`, `max_hunks`).
- Audit trail that links patch suggestions to mapping source (`sheet/cell`).

---

## 7) Typical troubleshooting

- **Command not found: `autofixer-mcp`**
  - Re-activate virtual env and run `pip install -e .`.
- **No reuse candidates**
  - Confirm `scenario_id` in Excel matches Karate scenario naming patterns.
  - Lower thresholds and re-run suggestions.
- **Protected branch error**
  - Switch to feature branch for apply step.
- **VS Code GitLab MCP not starting**
  - Install Node.js and verify `npx` is available.

---

## 8) Minimal “first run” checklist

- [ ] Server starts (`autofixer-mcp`)
- [ ] Karate features indexed
- [ ] Excel mapping normalized and indexed
- [ ] Reuse analysis returns candidates
- [ ] Patch preview generated
- [ ] Validation command executes

You are now ready to run automated Karate maintenance with reuse-first behavior in VS Code MCP workflows.

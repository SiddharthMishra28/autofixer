# Complete Beginner Guide: Karate Automatic Maintenance with FastMCP

This guide walks from zero setup to automatic Karate assertion maintenance.

## 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) Run MCP server

```bash
autofixer-mcp
```

## 3) Index your knowledge

### 3.1 Karate features (structured parsing)

```text
ingest_karate_features_to_rag(path="/absolute/path/to/karate-repo")
```

This extracts and stores:
- feature name
- scenario name
- tags
- step type (`Given/When/Then/And/*`)
- assertion expressions (`match`, `contains`, `==`)
- referenced payload keys

### 3.2 Excel mapping normalization

```text
normalize_excel_mapping_to_rag(path="/absolute/path/to/assertion-mapping.xlsx")
```

Expected columns (aliases are supported):
- scenario id
- json path
- expected value
- comparator (optional, default `==`)
- priority (optional)

Stored canonical record shape:
- `scenario_id`
- `json_path`
- `expected_value`
- `comparator`
- `priority`
- `source_sheet`
- `source_cell`

### 3.3 Additional context docs

```text
ingest_text_to_rag(path="/absolute/path/to/runbook.pdf")
ingest_excel_to_rag(path="/absolute/path/to/legacy-notes.xlsx")
ingest_codebase_to_rag(path="/absolute/path/to/automation-monorepo")
```

## 4) Check reuse candidates first (mandatory reuse-first policy)

```text
analyze_karate_reuse_candidates(top_k=5)
```

This checks existing Karate assertions first and lists reusable candidates for every mapping record.

## 5) Generate mapping ↔ assertion links

```text
suggest_karate_assertion_updates(min_confidence=0.70)
```

Returns suggestions with:
- target file/scenario
- suggested assertion expression
- confidence score
- traceability to mapping sheet/cell

## 6) Generate patch proposal (safe)

```text
propose_karate_assertion_patches(min_confidence=0.75, max_files=10, max_hunks=50)
```

Output includes:
- unified diff preview
- file/hunk counts
- audit trail for each proposed change

## 7) Apply patch

> Recommended: use feature branch only.

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

Safety controls:
- blocks writes on protected branches (`main/master/release`) unless explicitly overridden
- enforces change budgets

## 8) Run validation command

Maven example:

```text
run_karate_validation(command="mvn -Dtest=KarateRunner test", repo_path="/absolute/path/to/karate-repo")
```

Gradle example:

```text
run_karate_validation(command="./gradlew test --tests *Karate*", repo_path="/absolute/path/to/karate-repo")
```

## 9) Recommended operating model

1. Pull issue/MR via GitLab tool.
2. Re-index only changed modules or mapping sheets.
3. Run reuse-candidate analysis and confirm `reuse_found` where possible.
4. Generate suggestions and review `strategy` (`reuse_existing` preferred).
5. Review diff preview.
6. Apply patch with conservative confidence threshold.
7. Run validation and push PR.

## 10) Troubleshooting

- **No suggestions returned**: lower `min_confidence` to `0.6` and ensure mapping `scenario_id` aligns with scenario names.
- **Protected branch error**: switch to feature branch.
- **Too many changes**: increase `max_files`/`max_hunks` gradually after review.
- **Validation fails**: inspect returned stdout/stderr in `run_karate_validation` output.

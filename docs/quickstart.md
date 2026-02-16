# Quickstart (10 minutes)

## 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) Run server

```bash
autofixer-mcp
```

## 3) Index Karate + mapping knowledge

```text
ingest_karate_features_to_rag(path="/path/to/karate-repo")
normalize_excel_mapping_to_rag(path="/path/to/assertion-mapping.xlsx")
ingest_text_to_rag(path="/path/to/runbook.md")
```

## 4) Reuse-first analysis, then suggestions and patch preview

```text
analyze_karate_reuse_candidates(top_k=5)
suggest_karate_assertion_updates(min_confidence=0.7)
propose_karate_assertion_patches(min_confidence=0.75, max_files=20, max_hunks=80)
```

## 5) Apply patch and validate

```text
apply_karate_assertion_patches(repo_path="/path/to/karate-repo", dry_run=false)
run_karate_validation(command="mvn -Dtest=KarateRunner test", repo_path="/path/to/karate-repo")
```

For a full beginner walkthrough, troubleshooting and safety guidance, use `docs/setup_custom_agent.md`.

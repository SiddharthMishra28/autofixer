from __future__ import annotations

import json
import os
from dataclasses import asdict

import gitlab
from fastmcp import FastMCP

from autofixer_agent.ingestors.codebase import ingest_code_directory
from autofixer_agent.ingestors.excel import ingest_excel
from autofixer_agent.ingestors.text_docs import ingest_text_document
from autofixer_agent.karate.linking import link_mappings_to_assertions, suggestions_to_dict
from autofixer_agent.karate.mapping import MappingRecord, normalize_excel_mapping
from autofixer_agent.karate.parser import parse_karate_directory
from autofixer_agent.karate.patching import apply_suggestions
from autofixer_agent.karate.reuse import candidates_to_dict, find_reusable_assertions
from autofixer_agent.karate.safety import ensure_safe_branch
from autofixer_agent.karate.validation import run_validation_command
from autofixer_agent.rag.chromadb_store import ChromaRagStore, RagDocument

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
    """Read Java/Cucumber/Karate/TestNG/Python/JS/TS repositories and index them in ChromaDB."""
    docs = ingest_code_directory(path)
    count = store.add_documents(collection, docs)
    return {"indexed_documents": count, "collection": collection, "source": path}


@mcp.tool
def ingest_karate_features_to_rag(path: str, collection: str = "karate_features") -> dict:
    """Parse Karate .feature files and index structured scenario/assertion metadata for high-precision retrieval."""
    scenarios = parse_karate_directory(path)
    docs: list[RagDocument] = []
    for scenario in scenarios:
        payload = asdict(scenario)
        docs.append(
            RagDocument(
                content=json.dumps(payload, ensure_ascii=False),
                metadata={
                    "source_type": "karate_scenario",
                    "feature": scenario.feature_name,
                    "scenario": scenario.scenario_name,
                    "path": scenario.path,
                    "assertion_count": len(scenario.assertions),
                },
            )
        )

    count = store.add_documents(collection, docs)
    return {"indexed_documents": count, "collection": collection, "source": path}


@mcp.tool
def normalize_excel_mapping_to_rag(path: str, collection: str = "karate_mappings") -> dict:
    """Normalize mapping workbook into canonical JSON records and index them for retrieval/linking."""
    records = normalize_excel_mapping(path)
    docs = [
        RagDocument(
            content=json.dumps(asdict(record), ensure_ascii=False),
            metadata={
                "source_type": "karate_mapping",
                "scenario_id": record.scenario_id,
                "json_path": record.json_path,
                "source_sheet": record.source_sheet,
                "source_cell": record.source_cell,
            },
        )
        for record in records
    ]
    count = store.add_documents(collection, docs)
    return {
        "indexed_documents": count,
        "collection": collection,
        "source": path,
        "sample_records": [asdict(record) for record in records[:5]],
    }


def _mapping_from_store(collection: str) -> list[MappingRecord]:
    data = store.get_all(collection, where={"source_type": "karate_mapping"})
    records: list[MappingRecord] = []
    for doc in data.get("documents", []):
        payload = json.loads(doc)
        records.append(MappingRecord(**payload))
    return records


@mcp.tool
def analyze_karate_reuse_candidates(
    mapping_collection: str = "karate_mappings",
    karate_collection: str = "karate_features",
    top_k: int = 5,
) -> dict:
    """Check existing Karate assertions first and return reusable candidates for each mapping record."""
    karate_data = store.get_all(karate_collection, where={"source_type": "karate_scenario"})
    scenarios = []
    from autofixer_agent.karate.parser import KarateScenario, KarateAssertion

    for doc in karate_data.get("documents", []):
        payload = json.loads(doc)
        payload["assertions"] = [KarateAssertion(**item) for item in payload.get("assertions", [])]
        scenarios.append(KarateScenario(**payload))

    mappings = _mapping_from_store(mapping_collection)
    results = []
    for mapping in mappings:
        candidates = find_reusable_assertions(scenarios=scenarios, mapping=mapping, limit=top_k)
        results.append(
            {
                "scenario_id": mapping.scenario_id,
                "json_path": mapping.json_path,
                "source_sheet": mapping.source_sheet,
                "source_cell": mapping.source_cell,
                "reuse_found": bool(candidates),
                "candidates": candidates_to_dict(candidates),
            }
        )

    return {"mappings_checked": len(mappings), "results": results}


@mcp.tool
def suggest_karate_assertion_updates(
    karate_collection: str = "karate_features",
    mapping_collection: str = "karate_mappings",
    min_confidence: float = 0.60,
) -> dict:
    """Cross-link indexed mappings with indexed Karate scenarios and return assertion update suggestions with traceability."""
    karate_data = store.get_all(karate_collection, where={"source_type": "karate_scenario"})
    scenarios = []
    from autofixer_agent.karate.parser import KarateScenario, KarateAssertion

    for doc in karate_data.get("documents", []):
        payload = json.loads(doc)
        payload["assertions"] = [KarateAssertion(**item) for item in payload.get("assertions", [])]
        scenarios.append(KarateScenario(**payload))

    mappings = _mapping_from_store(mapping_collection)
    suggestions = link_mappings_to_assertions(scenarios=scenarios, mappings=mappings, min_confidence=min_confidence)
    return {"count": len(suggestions), "suggestions": suggestions_to_dict(suggestions)}


@mcp.tool
def propose_karate_assertion_patches(
    karate_collection: str = "karate_features",
    mapping_collection: str = "karate_mappings",
    min_confidence: float = 0.70,
    max_files: int = 10,
    max_hunks: int = 50,
) -> dict:
    """Build a unified diff patch proposal from mapping-to-assertion suggestions with budget and audit trail."""
    suggestions_payload = suggest_karate_assertion_updates(
        karate_collection=karate_collection,
        mapping_collection=mapping_collection,
        min_confidence=min_confidence,
    )
    from autofixer_agent.karate.linking import AssertionUpdateSuggestion

    suggestions = [AssertionUpdateSuggestion(**item) for item in suggestions_payload["suggestions"]]
    from autofixer_agent.karate.patching import propose_unified_diff

    proposal = propose_unified_diff(suggestions, max_files=max_files, max_hunks=max_hunks)
    proposal["suggestion_count"] = len(suggestions)
    return proposal


@mcp.tool
def apply_karate_assertion_patches(
    repo_path: str,
    karate_collection: str = "karate_features",
    mapping_collection: str = "karate_mappings",
    min_confidence: float = 0.75,
    dry_run: bool = True,
    max_files: int = 10,
    max_hunks: int = 50,
    allow_protected_branch: bool = False,
) -> dict:
    """Apply suggested Karate assertion updates with branch safety and change-budget controls."""
    safety = ensure_safe_branch(repo_path=repo_path, allow_protected=allow_protected_branch)

    suggestions_payload = suggest_karate_assertion_updates(
        karate_collection=karate_collection,
        mapping_collection=mapping_collection,
        min_confidence=min_confidence,
    )
    from autofixer_agent.karate.linking import AssertionUpdateSuggestion

    suggestions = [AssertionUpdateSuggestion(**item) for item in suggestions_payload["suggestions"]]
    result = apply_suggestions(
        suggestions=suggestions,
        dry_run=dry_run,
        max_files=max_files,
        max_hunks=max_hunks,
    )
    result["branch_safety"] = safety
    result["suggestion_count"] = len(suggestions)
    return result


@mcp.tool
def run_karate_validation(command: str, repo_path: str, timeout_s: int = 300) -> dict:
    """Run Karate framework validation command (Maven/Gradle/etc.) and return pass/fail with logs."""
    return run_validation_command(command=command, cwd=repo_path, timeout_s=timeout_s)


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

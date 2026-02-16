from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from autofixer_agent.karate.linking import AssertionUpdateSuggestion


@dataclass
class PatchResult:
    file_path: str
    applied: bool
    preview: str
    replacements: int
    audit: list[dict]


def _replace_in_scenario(lines: list[str], scenario_name: str, new_expression: str) -> tuple[list[str], int]:
    out = list(lines)
    in_scenario = False
    replacements = 0

    for i, line in enumerate(out):
        stripped = line.strip()
        if stripped.startswith(("Scenario:", "Scenario Outline:")):
            name = stripped.split(":", 1)[1].strip()
            in_scenario = name == scenario_name
            continue

        if in_scenario and "match " in stripped:
            prefix = line[: len(line) - len(line.lstrip())]
            out[i] = f"{prefix}* {new_expression}"
            replacements += 1
            break

    return out, replacements


def propose_unified_diff(
    suggestions: list[AssertionUpdateSuggestion],
    max_files: int = 10,
    max_hunks: int = 50,
) -> dict:
    files = sorted({s.file_path for s in suggestions})
    if len(files) > max_files:
        raise ValueError(f"Change budget exceeded: files={len(files)} > max_files={max_files}")

    grouped: dict[str, list[AssertionUpdateSuggestion]] = {}
    for suggestion in suggestions:
        grouped.setdefault(suggestion.file_path, []).append(suggestion)

    all_diffs: list[str] = []
    total_hunks = 0
    audit_trail: list[dict] = []

    for file_path, file_suggestions in grouped.items():
        original_lines = Path(file_path).read_text(encoding="utf-8", errors="ignore").splitlines()
        updated_lines = list(original_lines)
        file_replacements = 0

        for suggestion in file_suggestions:
            updated_lines, replacements = _replace_in_scenario(
                updated_lines,
                scenario_name=suggestion.scenario_name,
                new_expression=suggestion.suggested_expression,
            )
            file_replacements += replacements
            if replacements:
                audit_trail.append(
                    {
                        "file": suggestion.file_path,
                        "scenario": suggestion.scenario_name,
                        "json_path": suggestion.json_path,
                        "mapping_source": f"{suggestion.source_sheet}:{suggestion.source_cell}",
                        "confidence": suggestion.confidence,
                    }
                )

        diff_lines = list(
            difflib.unified_diff(
                original_lines,
                updated_lines,
                fromfile=file_path,
                tofile=file_path,
                lineterm="",
            )
        )
        if diff_lines:
            hunk_count = sum(1 for line in diff_lines if line.startswith("@@"))
            total_hunks += hunk_count
            if total_hunks > max_hunks:
                raise ValueError(f"Change budget exceeded: hunks={total_hunks} > max_hunks={max_hunks}")
            all_diffs.extend(diff_lines)

    return {
        "unified_diff": "\n".join(all_diffs),
        "hunks": total_hunks,
        "files": len(grouped),
        "audit_trail": audit_trail,
    }


def apply_suggestions(
    suggestions: list[AssertionUpdateSuggestion],
    dry_run: bool = True,
    max_files: int = 10,
    max_hunks: int = 50,
) -> dict:
    proposal = propose_unified_diff(suggestions, max_files=max_files, max_hunks=max_hunks)
    if dry_run:
        proposal["applied"] = False
        return proposal

    grouped: dict[str, list[AssertionUpdateSuggestion]] = {}
    for suggestion in suggestions:
        grouped.setdefault(suggestion.file_path, []).append(suggestion)

    for file_path, file_suggestions in grouped.items():
        original_lines = Path(file_path).read_text(encoding="utf-8", errors="ignore").splitlines()
        updated_lines = list(original_lines)
        for suggestion in file_suggestions:
            updated_lines, _ = _replace_in_scenario(
                updated_lines,
                scenario_name=suggestion.scenario_name,
                new_expression=suggestion.suggested_expression,
            )
        Path(file_path).write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    proposal["applied"] = True
    return proposal

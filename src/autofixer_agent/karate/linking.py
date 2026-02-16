from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from autofixer_agent.karate.mapping import MappingRecord
from autofixer_agent.karate.parser import KarateScenario


@dataclass
class AssertionUpdateSuggestion:
    file_path: str
    scenario_name: str
    scenario_id: str
    json_path: str
    suggested_expression: str
    confidence: float
    reason: str
    source_sheet: str
    source_cell: str


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _base_score(scenario: KarateScenario, mapping: MappingRecord) -> float:
    scenario_norm = _normalize(scenario.scenario_name)
    id_norm = _normalize(mapping.scenario_id)
    if id_norm and id_norm in scenario_norm:
        return 0.95

    if mapping.json_path in " ".join(step["text"] for step in scenario.steps):
        return 0.80

    return 0.55


def link_mappings_to_assertions(
    scenarios: list[KarateScenario],
    mappings: list[MappingRecord],
    min_confidence: float = 0.60,
) -> list[AssertionUpdateSuggestion]:
    suggestions: list[AssertionUpdateSuggestion] = []

    for scenario in scenarios:
        for mapping in mappings:
            score = _base_score(scenario, mapping)
            if score < min_confidence:
                continue

            comparator = mapping.comparator.strip() or "=="
            expression = f"match response.{mapping.json_path} {comparator} {mapping.expected_value}"
            reason = "matched by scenario id" if score >= 0.9 else "matched by json path proximity"

            suggestions.append(
                AssertionUpdateSuggestion(
                    file_path=scenario.path,
                    scenario_name=scenario.scenario_name,
                    scenario_id=mapping.scenario_id,
                    json_path=mapping.json_path,
                    suggested_expression=expression,
                    confidence=score,
                    reason=reason,
                    source_sheet=mapping.source_sheet,
                    source_cell=mapping.source_cell,
                )
            )

    unique: list[AssertionUpdateSuggestion] = []
    seen = set()
    for suggestion in suggestions:
        key = (suggestion.file_path, suggestion.scenario_name, suggestion.json_path, suggestion.suggested_expression)
        if key in seen:
            continue
        seen.add(key)
        unique.append(suggestion)

    return sorted(unique, key=lambda item: item.confidence, reverse=True)


def suggestions_to_dict(suggestions: list[AssertionUpdateSuggestion]) -> list[dict]:
    return [asdict(suggestion) for suggestion in suggestions]

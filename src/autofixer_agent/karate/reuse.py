from __future__ import annotations

from dataclasses import dataclass, asdict

from autofixer_agent.karate.mapping import MappingRecord
from autofixer_agent.karate.parser import KarateScenario


@dataclass
class ReuseCandidate:
    scenario_name: str
    file_path: str
    expression: str
    comparator: str
    json_path: str
    confidence: float


def find_reusable_assertions(
    scenarios: list[KarateScenario],
    mapping: MappingRecord,
    limit: int = 5,
) -> list[ReuseCandidate]:
    candidates: list[ReuseCandidate] = []

    for scenario in scenarios:
        for assertion in scenario.assertions:
            path_match = any(mapping.json_path in item or item in mapping.json_path for item in assertion.json_paths)
            if not path_match:
                continue

            comparator_match = not mapping.comparator or mapping.comparator == assertion.comparator
            score = 0.8 if comparator_match else 0.65
            candidates.append(
                ReuseCandidate(
                    scenario_name=scenario.scenario_name,
                    file_path=scenario.path,
                    expression=assertion.expression,
                    comparator=assertion.comparator,
                    json_path=mapping.json_path,
                    confidence=score,
                )
            )

    candidates.sort(key=lambda item: item.confidence, reverse=True)
    return candidates[:limit]


def candidates_to_dict(candidates: list[ReuseCandidate]) -> list[dict]:
    return [asdict(candidate) for candidate in candidates]

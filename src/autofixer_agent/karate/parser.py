from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

STEP_PREFIXES = ("Given", "When", "Then", "And", "But", "*")
ASSERTION_KEYWORDS = ("match", "contains", "==")


@dataclass
class KarateAssertion:
    step_type: str
    expression: str
    json_paths: list[str] = field(default_factory=list)
    comparator: str = ""


@dataclass
class KarateScenario:
    feature_name: str
    scenario_name: str
    tags: list[str]
    steps: list[dict]
    assertions: list[KarateAssertion]
    path: str


def _extract_json_paths(text: str) -> list[str]:
    patterns = [
        r"\$\.[A-Za-z0-9_\[\]\.\*]+",
        r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_\[\]]+)+",
    ]
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text))
    unique = []
    for item in matches:
        if item not in unique:
            unique.append(item)
    return unique


def _comparator(text: str) -> str:
    if " contains " in text:
        return "contains"
    if "==" in text:
        return "=="
    if " match " in text:
        return "match"
    return ""


def parse_karate_feature(path: str) -> list[KarateScenario]:
    file_path = Path(path)
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    feature_name = file_path.stem
    pending_tags: list[str] = []
    scenarios: list[KarateScenario] = []
    current: KarateScenario | None = None

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("Feature:"):
            feature_name = stripped.replace("Feature:", "", 1).strip() or feature_name
            continue

        if stripped.startswith("@"):
            pending_tags.extend(tag for tag in stripped.split() if tag.startswith("@"))
            continue

        if stripped.startswith(("Scenario:", "Scenario Outline:")):
            scenario_name = stripped.split(":", 1)[1].strip()
            current = KarateScenario(
                feature_name=feature_name,
                scenario_name=scenario_name,
                tags=pending_tags,
                steps=[],
                assertions=[],
                path=str(file_path),
            )
            scenarios.append(current)
            pending_tags = []
            continue

        if current is None:
            continue

        step_type = ""
        expression = stripped
        for prefix in STEP_PREFIXES:
            if stripped == prefix or stripped.startswith(prefix + " "):
                step_type = prefix
                expression = stripped[len(prefix) :].strip()
                break

        step_record = {"line": idx, "step_type": step_type or "raw", "text": expression}
        current.steps.append(step_record)

        if any(keyword in expression for keyword in ASSERTION_KEYWORDS):
            current.assertions.append(
                KarateAssertion(
                    step_type=step_type or "raw",
                    expression=expression,
                    json_paths=_extract_json_paths(expression),
                    comparator=_comparator(expression),
                )
            )

    return scenarios


def parse_karate_directory(path: str) -> list[KarateScenario]:
    root = Path(path)
    scenarios: list[KarateScenario] = []
    for file_path in root.rglob("*.feature"):
        scenarios.extend(parse_karate_feature(str(file_path)))
    return scenarios

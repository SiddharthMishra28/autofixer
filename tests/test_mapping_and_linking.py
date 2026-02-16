from pathlib import Path

import pytest

pytest.importorskip("openpyxl")
from openpyxl import Workbook

from autofixer_agent.karate.linking import link_mappings_to_assertions
from autofixer_agent.karate.mapping import normalize_excel_mapping
from autofixer_agent.karate.parser import parse_karate_feature


def _create_mapping_xlsx(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Mappings"
    ws.append(["scenario_id", "json_path", "expected_value", "comparator", "priority"])
    ws.append(["SCN-101", "user.role", "'manager'", "==", "high"])
    wb.save(path)


def test_mapping_normalization_and_linking(tmp_path):
    mapping_path = tmp_path / "mapping.xlsx"
    _create_mapping_xlsx(mapping_path)

    mappings = normalize_excel_mapping(str(mapping_path))
    assert len(mappings) == 1
    assert mappings[0].scenario_id == "SCN-101"

    scenarios = parse_karate_feature("tests/fixtures/karate/sample.feature")
    suggestions = link_mappings_to_assertions(scenarios, mappings, min_confidence=0.6)

    assert suggestions
    assert suggestions[0].scenario_id == "SCN-101"
    assert "user.role" in suggestions[0].suggested_expression

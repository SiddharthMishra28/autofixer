from pathlib import Path

from autofixer_agent.karate.linking import AssertionUpdateSuggestion
from autofixer_agent.karate.patching import apply_suggestions


FEATURE_TEXT = """Feature: Demo

Scenario: SCN-101 successful login
  * match response.user.role == 'admin'
"""


def test_apply_suggestions_dry_run(tmp_path):
    feature = tmp_path / "demo.feature"
    feature.write_text(FEATURE_TEXT, encoding="utf-8")

    suggestions = [
        AssertionUpdateSuggestion(
            file_path=str(feature),
            scenario_name="SCN-101 successful login",
            scenario_id="SCN-101",
            json_path="user.role",
            suggested_expression="match response.user.role == 'manager'",
            confidence=0.95,
            reason="matched by scenario id",
            source_sheet="Mappings",
            source_cell="A2",
        )
    ]

    result = apply_suggestions(suggestions, dry_run=True)
    assert result["applied"] is False
    assert "manager" in result["unified_diff"]
    assert "Mappings:A2" in str(result["audit_trail"])

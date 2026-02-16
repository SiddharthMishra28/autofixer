from autofixer_agent.karate.parser import parse_karate_feature


def test_parse_karate_feature_extracts_scenarios_and_assertions():
    scenarios = parse_karate_feature("tests/fixtures/karate/sample.feature")
    assert len(scenarios) == 3

    primary = scenarios[0]
    assert primary.feature_name == "Login API validations"
    assert primary.scenario_name == "SCN-101 successful login"
    assert "@login" in primary.tags
    assert len(primary.assertions) >= 2
    assert any("response.user.id" in assertion.expression for assertion in primary.assertions)

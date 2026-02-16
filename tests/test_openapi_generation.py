from autofixer_agent.karate.openapi import generate_karate_feature_from_openapi, parse_openapi_operations


def test_parse_openapi_operations_from_json_fixture():
    operations = parse_openapi_operations("tests/fixtures/openapi/petstore.json")
    assert len(operations) == 3
    assert any(op.operation_id == "listPets" and op.expected_status == 200 for op in operations)
    assert any(op.operation_id == "createPet" and op.expected_status == 201 for op in operations)


def test_generate_karate_feature_from_openapi_json():
    generated = generate_karate_feature_from_openapi(
        openapi_path="tests/fixtures/openapi/petstore.json",
        feature_name="Generated Pet API",
        tags="@generated @openapi",
    )
    assert "Feature: Generated Pet API" in generated
    assert "Scenario: listPets - List pets" in generated
    assert "When method get" in generated
    assert "Then status 201" in generated
    assert "Scenario: get_pets_petId - Get pet by id" in generated

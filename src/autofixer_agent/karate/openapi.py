from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

HTTP_METHODS = ["get", "post", "put", "patch", "delete", "head", "options"]


@dataclass
class OpenApiOperation:
    method: str
    path: str
    operation_id: str
    summary: str
    expected_status: int


def _load_openapi(path: str) -> dict:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".json":
        return json.loads(text)

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise ValueError("PyYAML is required for YAML OpenAPI parsing. Install pyyaml>=6.0") from exc
        return yaml.safe_load(text)

    raise ValueError(f"Unsupported OpenAPI extension: {suffix}")


def _best_status_code(operation: dict) -> int:
    responses = operation.get("responses", {}) or {}
    numeric_codes = []
    for key in responses.keys():
        if str(key).isdigit():
            numeric_codes.append(int(key))
    if numeric_codes:
        return sorted(numeric_codes)[0]
    return 200


def parse_openapi_operations(path: str) -> list[OpenApiOperation]:
    spec = _load_openapi(path)
    paths = spec.get("paths", {}) or {}

    operations: list[OpenApiOperation] = []
    for route, route_info in paths.items():
        if not isinstance(route_info, dict):
            continue
        for method in HTTP_METHODS:
            op = route_info.get(method)
            if not isinstance(op, dict):
                continue
            operation_id = op.get("operationId") or f"{method}_{route.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"
            summary = op.get("summary") or op.get("description") or operation_id
            operations.append(
                OpenApiOperation(
                    method=method.upper(),
                    path=route,
                    operation_id=operation_id,
                    summary=summary,
                    expected_status=_best_status_code(op),
                )
            )

    return operations


def generate_karate_feature_from_openapi(
    openapi_path: str,
    feature_name: str = "Generated API Tests",
    tags: str = "@generated @openapi",
    base_url_variable: str = "baseUrl",
) -> str:
    operations = parse_openapi_operations(openapi_path)
    tag_line = tags.strip()

    lines: list[str] = [f"Feature: {feature_name}", "", "Background:", f"  * url {base_url_variable}", ""]

    for op in operations:
        if tag_line:
            lines.append(tag_line)
        lines.extend(
            [
                f"Scenario: {op.operation_id} - {op.summary}",
                f"  Given path '{op.path.lstrip('/')}'",
                f"  When method {op.method.lower()}",
                f"  Then status {op.expected_status}",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def write_generated_karate_feature(content: str, output_dir: str, file_name: str = "generated_openapi.feature") -> str:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / file_name
    target.write_text(content, encoding="utf-8")
    return str(target)

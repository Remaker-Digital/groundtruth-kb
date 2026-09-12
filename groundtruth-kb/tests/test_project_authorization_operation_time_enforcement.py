from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from groundtruth_kb.governance.project_authorization_operation_time import (
    TaxonomyError,
    load_operation_taxonomy,
)

NOW = datetime(2026, 7, 13, tzinfo=UTC)


def _taxonomy_with_suffix(tmp_path: Path, suffix: str):
    current = load_operation_taxonomy()
    target = tmp_path / "config/governance/project-authorization-operation-taxonomy.toml"
    target.parent.mkdir(parents=True)
    target.write_text(Path(current.source_path).read_text(encoding="utf-8") + suffix, encoding="utf-8")
    return load_operation_taxonomy(tmp_path)


def _authorization(
    *,
    allowed: list[str] | None = None,
    forbidden: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": "PAUTH-FIXTURE",
        "version": 3,
        "project_id": "PROJECT-FIXTURE",
        "status": "active",
        "owner_decision_deliberation_id": "DELIB-FIXTURE",
        "expires_at": "2026-08-01T00:00:00Z",
        "supersedes": None,
        "superseded_by": None,
        "allowed_mutation_classes": allowed or ["source", "test_addition"],
        "forbidden_operations": forbidden or [],
        "included_work_item_ids": ["WI-FIXTURE"],
        "excluded_work_item_ids": [],
        "included_spec_ids": ["SPEC-FIXTURE"],
        "excluded_spec_ids": [],
    }


@pytest.mark.parametrize(
    "suffix",
    [
        '\n[[path_rule]]\npattern = ".other/**"\nmutation_class = "unknown"\n',
        '\n[[path_rule]]\npattern = ".githooks/**"\nmutation_class = "source"\n',
        '\n[[path_rule]]\npattern = "../.other/**"\nmutation_class = "source"\n',
    ],
)
def test_path_rule_loader_rejects_unknown_duplicate_or_non_root_rule(tmp_path: Path, suffix: str) -> None:
    with pytest.raises(TaxonomyError):
        _taxonomy_with_suffix(tmp_path, suffix)

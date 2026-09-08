from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import groundtruth_kb.postgres_kernel as kernel
import pytest
from groundtruth_kb.postgres_kernel import (
    CURRENT_FORMAT,
    MIGRATION_TABLES,
    TABLE_SPECS,
    PostgresKernelError,
)

TimestampCaller = Callable[[object], object]


@pytest.fixture(autouse=True)
def _forbid_database_connections(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("database connection attempted in database-free timestamp selector")

    monkeypatch.setattr(kernel.psycopg, "connect", forbidden)
    monkeypatch.setattr(kernel.sqlite3, "connect", forbidden)


def _test_plan_row(changed_at: object) -> dict[str, object]:
    values: dict[str, object] = {
        "id": "PLAN-TIMESTAMP",
        "version": 1,
        "title": "Timestamp fixture",
        "description": None,
        "status": "active",
        "changed_by": "test",
        "changed_at": changed_at,
        "change_reason": "WI-7749 deterministic fixture",
    }
    return {column: values.get(column) for column in TABLE_SPECS["test_plans"].columns}


def _through_manifest(value: object) -> object:
    tables = {table_name: [] for table_name in MIGRATION_TABLES}
    tables["test_plans"] = [_test_plan_row(value)]
    manifest = {
        "format": CURRENT_FORMAT,
        "schema_version": 1,
        "tables": tables,
    }
    return kernel.normalize_manifest(manifest)["tables"]["test_plans"][0]["changed_at"]


def _zero_transform_plan() -> dict[str, Any]:
    return {
        "project_dependencies": {
            "affected_gate_from": "authorization",
            "affected_gate_to": "readiness",
            "expected_active_after": 0,
            "expected_gate_transition_count": 0,
            "expected_retired_after": 0,
            "expected_source_count": 0,
            "preserve_dependency_ids": [],
            "retire_dependency_ids": [],
        },
        "projects": {
            "expected_programs": 0,
            "expected_authorized": 0,
            "expected_not_authorized": 0,
            "expected_total": 0,
        },
    }


def _through_transform(value: object) -> object:
    source_rows = {table_name: [] for table_name in MIGRATION_TABLES}
    source_rows["test_plans"] = [_test_plan_row(value)]
    return kernel._transform_source_rows(source_rows, _zero_transform_plan())["test_plans"][0]["changed_at"]


@pytest.fixture(params=[_through_manifest, _through_transform], ids=["manifest", "sqlite-transform"])
def timestamp_caller(request: pytest.FixtureRequest) -> TimestampCaller:
    return request.param


@pytest.mark.parametrize(
    "source",
    [
        "2026-03-13T01:54:31",
        "2026-03-13 01:54:31",
        "2026-03-13T01:54:31.123456",
        "2000-02-29",
        "2026-03-11",
        "",
    ],
)
def test_ambiguous_times_require_source_reconciliation_through_both_callers(
    timestamp_caller: TimestampCaller,
    source: str,
) -> None:
    with pytest.raises(PostgresKernelError) as error:
        timestamp_caller(source)
    assert error.value.code == "invalid_timestamp"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("2026-03-13T01:54:31Z", "2026-03-13T01:54:31+00:00"),
        ("2026-03-13 01:54:31+00:00", "2026-03-13T01:54:31+00:00"),
        ("2026-03-13T01:54:31.123456+00:00", "2026-03-13T01:54:31.123456+00:00"),
        ("2026-03-13T01:54:31+05:30", "2026-03-12T20:24:31+00:00"),
        (datetime(2026, 3, 13, 1, 54, 31, tzinfo=UTC), "2026-03-13T01:54:31+00:00"),
        (
            datetime(2026, 3, 13, 1, 54, 31, tzinfo=timezone(timedelta(hours=5, minutes=30))),
            "2026-03-12T20:24:31+00:00",
        ),
    ],
)
def test_preimage_accepted_values_keep_exact_canonical_output(
    timestamp_caller: TimestampCaller,
    source: object,
    expected: object,
) -> None:
    assert timestamp_caller(source) == expected


def test_private_timestamp_none_remains_none() -> None:
    assert kernel._canonical_timestamp(None, label="fixture.changed_at") is None


@pytest.mark.parametrize("source", ["\x00", "2026-03-13T01:54:31\x00", "\ud800"])
def test_text_validation_errors_remain_invalid_text(
    timestamp_caller: TimestampCaller,
    source: object,
) -> None:
    with pytest.raises(PostgresKernelError) as error:
        timestamp_caller(source)
    assert error.value.code == "invalid_text"


@pytest.mark.parametrize(
    "source",
    [
        "garbage",
        " ",
        "2026-02-29",
        "2026-13-01",
        "2026-03-13T01:54",
        1,
        object(),
        "0001-01-01T00:00:00+14:00",
        "9999-12-31T23:59:59-14:00",
    ],
)
def test_timestamp_and_type_errors_remain_invalid_timestamp(
    timestamp_caller: TimestampCaller,
    source: object,
) -> None:
    with pytest.raises(PostgresKernelError) as error:
        timestamp_caller(source)
    assert error.value.code == "invalid_timestamp"

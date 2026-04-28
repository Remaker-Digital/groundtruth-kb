"""Tests for scripts/collect_phase_a_metrics.py (Tier A #6).

The collector honors the scanner-safe-writer schema v1 stable-interface
contract: it indexes on ``pattern_name`` and NEVER on
``pattern_description``. Tests pin this contract plus per-hit counting
semantics, forward-compat behavior, and output format determinism.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Reuse the script as a module by path-import (scripts/ is not a package).
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "collect_phase_a_metrics.py"

sys.path.insert(0, str(_SCRIPT_PATH.parent))
import collect_phase_a_metrics as cpm  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "phase_a_metrics"


def _collect(fixture_name: str) -> dict[str, object]:
    return cpm.collect_metrics(FIXTURES / fixture_name, warn_stream=None)


def test_empty_log_returns_zero_metrics(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.log"
    report = cpm.collect_metrics(missing, warn_stream=None)

    assert report["total_deny_events"] == 0
    assert report["by_pattern_name"] == {}
    assert report["by_catalog_source"] == {}
    assert report["by_session_id"] == {}
    assert report["unique_file_paths"] == []
    assert report["by_date"] == {}
    fc = report["forward_compat"]
    assert fc == {
        "unknown_schema_versions": 0,
        "malformed_lines": 0,
        "lines_skipped_wrong_event": 0,
        "lines_skipped_wrong_hook": 0,
    }


def test_empty_file_returns_zero_metrics() -> None:
    report = _collect("empty.log")
    assert report["total_deny_events"] == 0
    assert report["by_pattern_name"] == {}


def test_canonical_only_fixture() -> None:
    report = _collect("canonical_only.log")
    assert report["total_deny_events"] == 3
    assert report["by_catalog_source"] == {"canonical": 3}
    assert report["by_pattern_name"] == {
        "aws_access_key_id": 2,
        "anthropic_api_key": 1,
    }
    assert report["by_session_id"] == {"S298": 2, "S299": 1}


def test_fallback_only_fixture() -> None:
    report = _collect("fallback_only.log")
    assert report["total_deny_events"] == 2
    assert report["by_catalog_source"] == {"fallback": 2}
    assert report["by_pattern_name"] == {"generic_api_key": 2}


def test_mixed_catalogs_fixture() -> None:
    report = _collect("mixed_catalogs.log")
    assert report["total_deny_events"] == 5
    assert report["by_catalog_source"] == {"canonical": 4, "fallback": 1}
    sum_catalogs = sum(report["by_catalog_source"].values())  # type: ignore[attr-defined]
    assert sum_catalogs == report["total_deny_events"]


def test_multi_hit_record_counts_each_hit() -> None:
    """Pin per-hit counting semantics (binding condition 2, Codex GO -002).

    The ``mixed_catalogs.log`` fixture contains one record (``mixed-005``)
    with two hits (``aws_access_key_id`` + ``anthropic_api_key``). That
    record increments ``total_deny_events`` by 1 but increments
    ``by_pattern_name`` entries by 1 each (hit count).
    """
    report = _collect("mixed_catalogs.log")
    # 5 records total; sum of per-pattern counts is 6 because mixed-005
    # has 2 hits.
    pattern_counts: dict[str, int] = report["by_pattern_name"]  # type: ignore[assignment]
    assert sum(pattern_counts.values()) == 6
    assert report["total_deny_events"] == 5
    assert pattern_counts["aws_access_key_id"] == 3
    assert pattern_counts["anthropic_api_key"] == 2
    assert pattern_counts["generic_api_key"] == 1


def test_malformed_lines_counted_in_forward_compat() -> None:
    report = _collect("malformed_lines.log")
    fc: dict[str, int] = report["forward_compat"]  # type: ignore[assignment]
    assert report["total_deny_events"] == 2
    assert fc["malformed_lines"] == 2
    assert fc["unknown_schema_versions"] == 0


def test_unknown_schema_version_skipped_and_counted() -> None:
    report = _collect("unknown_schema_version.log")
    fc: dict[str, int] = report["forward_compat"]  # type: ignore[assignment]
    assert report["total_deny_events"] == 1
    assert fc["unknown_schema_versions"] == 2
    assert report["by_pattern_name"] == {"aws_access_key_id": 1}


def test_unknown_schema_version_emits_stderr_warning() -> None:
    """Binding condition 3 (Codex GO -002): warn-and-skip must surface on stderr."""
    buf = io.StringIO()
    report = cpm.collect_metrics(
        FIXTURES / "unknown_schema_version.log",
        warn_stream=buf,
    )
    fc: dict[str, int] = report["forward_compat"]  # type: ignore[assignment]
    assert fc["unknown_schema_versions"] == 2

    warnings = buf.getvalue()
    assert "warning" in warnings.lower()
    assert "schema_version" in warnings
    # One warning line per distinct unknown version (2: `2` and `None`)
    assert warnings.count("\n") == 2


def test_wrong_event_counted_in_forward_compat() -> None:
    report = _collect("wrong_event.log")
    fc: dict[str, int] = report["forward_compat"]  # type: ignore[assignment]
    assert report["total_deny_events"] == 1
    assert fc["lines_skipped_wrong_event"] == 1
    assert fc["lines_skipped_wrong_hook"] == 1


def test_pattern_names_indexed_not_descriptions() -> None:
    """G5 stable-interface contract: group-by key is ``pattern_name``.

    ``pattern_name_stability.log`` contains two records with the same
    ``pattern_name`` (``aws_access_key_id``) but different
    ``pattern_description`` strings (canonical vs. fallback phrasing).
    The collector must collapse both records into a single bucket keyed on
    ``pattern_name`` with count 2. If a future change tries to group by
    ``pattern_description``, this test fails.
    """
    report = _collect("pattern_name_stability.log")
    assert report["total_deny_events"] == 2
    assert report["by_pattern_name"] == {"aws_access_key_id": 2}
    # pattern_description must not appear anywhere in the stable report.
    report_json = json.dumps(report)
    assert "canonical phrasing" not in report_json
    assert "fallback wording" not in report_json
    assert "pattern_description" not in report_json


def test_markdown_output_excludes_pattern_description() -> None:
    """G5 output contract: Markdown rendering is keyed on stable fields only."""
    report = _collect("pattern_name_stability.log")
    markdown = cpm.format_markdown(report)
    assert "pattern_description" not in markdown
    assert "canonical phrasing" not in markdown
    assert "fallback wording" not in markdown
    assert "| aws_access_key_id | 2 |" in markdown


def test_by_date_groups_utc_date_from_timestamp() -> None:
    report = _collect("mixed_catalogs.log")
    # 4 records on 2026-04-16, 1 record on 2026-04-17 (see fixture).
    assert report["by_date"] == {"2026-04-16": 4, "2026-04-17": 1}


def test_unique_file_paths_deduplicates(tmp_path: Path) -> None:
    """Binding condition 2 (Codex GO -002): deduplication is required, not optional."""
    log = tmp_path / "dup.log"
    record_template = {
        "schema_version": 1,
        "hook": "scanner-safe-writer",
        "event": "deny",
        "file_path": "bridge/same-file-001.md",
        "catalog_source": "canonical",
        "hits": [
            {
                "pattern_name": "aws_access_key_id",
                "pattern_description": "AWS access key ID",
                "span": [0, 20],
            }
        ],
        "session_id": "S298",
    }
    lines: list[str] = []
    for timestamp in (
        "2026-04-16T10:00:00Z",
        "2026-04-16T10:05:00Z",
        "2026-04-16T10:10:00Z",
    ):
        rec = {**record_template, "timestamp_utc": timestamp}
        lines.append(json.dumps(rec))
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = cpm.collect_metrics(log, warn_stream=None)
    assert report["total_deny_events"] == 3
    assert report["unique_file_paths"] == ["bridge/same-file-001.md"]


def test_session_id_null_folded_to_unknown(tmp_path: Path) -> None:
    """Binding condition 2 (Codex GO -002): null-session folding is required."""
    log = tmp_path / "null-session.log"
    record = {
        "schema_version": 1,
        "timestamp_utc": "2026-04-16T11:00:00Z",
        "hook": "scanner-safe-writer",
        "event": "deny",
        "file_path": "bridge/no-session-001.md",
        "catalog_source": "canonical",
        "hits": [
            {
                "pattern_name": "aws_access_key_id",
                "pattern_description": "AWS access key ID",
                "span": [0, 20],
            }
        ],
        "session_id": None,
    }
    log.write_text(json.dumps(record) + "\n", encoding="utf-8")

    report = cpm.collect_metrics(log, warn_stream=None)
    assert report["by_session_id"] == {"(unknown)": 1}


def test_json_stdout_excludes_pattern_description() -> None:
    """G5 output contract: stable JSON output never emits pattern_description."""
    report = _collect("canonical_only.log")
    report_json = json.dumps(report)
    assert "pattern_description" not in report_json
    assert "AWS access key ID" not in report_json
    assert "Anthropic API key" not in report_json


def test_pattern_name_ordering_is_deterministic() -> None:
    """by_pattern_name is sorted by descending count then ascending name."""
    report = _collect("mixed_catalogs.log")
    ordered_keys = list(report["by_pattern_name"].keys())  # type: ignore[arg-type]
    assert ordered_keys == ["aws_access_key_id", "anthropic_api_key", "generic_api_key"]


def test_cli_json_output_parses() -> None:
    """CLI smoke: `--format json` stdout is valid JSON matching the report shape."""
    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--log-path",
            str(FIXTURES / "canonical_only.log"),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["schema_version"] == 1
    assert parsed["total_deny_events"] == 3
    assert parsed["by_catalog_source"] == {"canonical": 3}
    # stderr must be empty when no unknown schema versions are present
    assert result.stderr == ""


def test_cli_markdown_output_contains_headers() -> None:
    """CLI smoke: `--format markdown` emits deterministic table headers and rows."""
    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--log-path",
            str(FIXTURES / "canonical_only.log"),
            "--format",
            "markdown",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    out = result.stdout
    assert "# Phase A Scanner-Safe-Writer Metrics" in out
    assert "## By pattern name" in out
    assert "| aws_access_key_id | 2 |" in out
    assert "| anthropic_api_key | 1 |" in out
    assert "## By catalog source" in out
    assert "| canonical | 3 |" in out
    assert "## Forward-compat indicators" in out


def test_cli_unknown_schema_version_warns_on_stderr() -> None:
    """Binding condition 3 at the CLI boundary: warn on stderr for unknown versions."""
    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT_PATH),
            "--log-path",
            str(FIXTURES / "unknown_schema_version.log"),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["forward_compat"]["unknown_schema_versions"] == 2
    assert "warning" in result.stderr.lower()
    assert "schema_version" in result.stderr


@pytest.mark.parametrize(
    "fixture_name",
    [
        "canonical_only.log",
        "fallback_only.log",
        "mixed_catalogs.log",
        "malformed_lines.log",
        "unknown_schema_version.log",
        "wrong_event.log",
        "empty.log",
        "pattern_name_stability.log",
    ],
)
def test_fixture_exists_and_is_readable(fixture_name: str) -> None:
    """Defensive: every named fixture is present and UTF-8 decodable."""
    path = FIXTURES / fixture_name
    assert path.exists(), f"missing fixture: {fixture_name}"
    path.read_text(encoding="utf-8")

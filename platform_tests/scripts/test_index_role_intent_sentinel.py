"""Tests for scripts/check_index_role_intent_sentinel.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_index_role_intent_sentinel.py"


@pytest.fixture(scope="module")
def sentinel_module():
    spec = importlib.util.spec_from_file_location("check_index_role_intent_sentinel", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def _write_role_files(tmp_path: Path, roles: dict[str, list[str] | str | None]) -> None:
    state_dir = tmp_path / "harness-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    identities = {
        "schema_version": 1,
        "harnesses": {
            "codex": {"id": "A"},
            "claude": {"id": "B"},
            "antigravity": {"id": "C"},
        },
    }
    assignments = {
        "schema_version": 1,
        "harnesses": {
            harness_id: {
                "harness_type": harness_id.lower(),
                "role": role,
            }
            for harness_id, role in roles.items()
        },
    }
    (state_dir / "harness-identities.json").write_text(json.dumps(identities), encoding="utf-8")
    (state_dir / "role-assignments.json").write_text(json.dumps(assignments), encoding="utf-8")


def _write_index(tmp_path: Path, body: str) -> Path:
    index_path = tmp_path / "bridge" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(body, encoding="utf-8")
    return index_path


def _index_with_sentinel(
    sentinel_module,
    tmp_path: Path,
    *,
    roles: dict[str, list[str] | str | None] | None = None,
    updated_at: datetime | None = None,
) -> str:
    if roles is None:
        roles = {"A": ["prime-builder"], "C": ["loyal-opposition"]}
    _write_role_files(tmp_path, roles)
    state = sentinel_module.state_from_files(tmp_path)
    sentinel = sentinel_module.render_sentinel(state, updated_at=updated_at)
    return f"# Bridge Index\n\n<!-- header comment -->\n{sentinel}\nDocument: fixture\nGO: bridge/fixture-002.md\n"


def test_sentinel_parses_correctly(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(sentinel_module, tmp_path)

    parsed = sentinel_module.parse_sentinel(index_text)

    assert parsed.prime_harness_id == "A"
    assert parsed.loyal_harness_id == "C"
    assert parsed.topology == "multi_harness"


def test_freshness_check_fails_stale(sentinel_module, tmp_path: Path) -> None:
    old_timestamp = datetime.now(UTC) - timedelta(days=8)
    index_text = _index_with_sentinel(sentinel_module, tmp_path, updated_at=old_timestamp)
    state = sentinel_module.state_from_files(tmp_path)

    errors = sentinel_module.validate_sentinel(index_text, state, now=datetime.now(UTC))

    assert any("role-intent sentinel is stale" in error for error in errors)


def test_consistency_passes_multi_harness_singleton(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(
        sentinel_module,
        tmp_path,
        roles={"A": ["prime-builder"], "C": ["loyal-opposition"]},
    )
    state = sentinel_module.state_from_files(tmp_path)

    assert sentinel_module.validate_sentinel(index_text, state) == []


def test_consistency_passes_single_harness_role_set(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(
        sentinel_module,
        tmp_path,
        roles={"A": ["prime-builder", "loyal-opposition"], "C": []},
    )
    state = sentinel_module.state_from_files(tmp_path)

    assert state.topology == "single_harness"
    assert sentinel_module.validate_sentinel(index_text, state) == []


def test_identity_map_first_resolution(sentinel_module, tmp_path: Path) -> None:
    _write_role_files(tmp_path, {"A": ["prime-builder"], "C": ["loyal-opposition"]})
    role_doc = sentinel_module.load_json(tmp_path / "harness-state" / "role-assignments.json")
    role_doc["harnesses"]["A"]["harness_type"] = "wrong-name"
    (tmp_path / "harness-state" / "role-assignments.json").write_text(json.dumps(role_doc), encoding="utf-8")

    state = sentinel_module.state_from_files(tmp_path)
    sentinel = sentinel_module.render_sentinel(state)

    assert "Prime Builder harness:    A (Codex)" in sentinel


def test_consistency_fails_on_role_map_drift(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(
        sentinel_module,
        tmp_path,
        roles={"A": ["prime-builder"], "C": ["loyal-opposition"]},
    )
    _write_role_files(tmp_path, {"A": ["prime-builder"], "C": []})
    drifted_state = sentinel_module.state_from_files(tmp_path)

    errors = sentinel_module.validate_sentinel(index_text, drifted_state)

    assert "Loyal Opposition harness mismatch: sentinel=C durable=none" in errors
    assert "Topology mismatch: sentinel=multi_harness durable=prime_only" in errors


def test_sentinel_is_non_authoritative(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(
        sentinel_module,
        tmp_path,
        roles={"A": ["prime-builder"], "C": ["loyal-opposition"]},
    )
    _write_role_files(tmp_path, {"A": ["prime-builder"], "C": []})
    before = (tmp_path / "harness-state" / "role-assignments.json").read_text(encoding="utf-8")
    _write_index(tmp_path, index_text)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--project-root", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 1
    assert "Loyal Opposition harness mismatch" in result.stderr
    assert (tmp_path / "harness-state" / "role-assignments.json").read_text(encoding="utf-8") == before


def test_update_mode_rewrites_sentinel(sentinel_module, tmp_path: Path) -> None:
    _write_role_files(tmp_path, {"A": ["prime-builder"], "C": ["loyal-opposition"]})
    index_path = _write_index(
        tmp_path, "# Bridge Index\n\n<!-- header comment -->\nDocument: fixture\nGO: bridge/fixture-002.md\n"
    )
    state = sentinel_module.state_from_files(tmp_path)

    updated = sentinel_module.update_index(index_path, state)
    parsed = sentinel_module.parse_sentinel(updated)

    assert parsed.prime_harness_id == "A"
    assert parsed.loyal_harness_id == "C"
    assert "Document: fixture" in updated


def test_update_preserves_other_content(sentinel_module, tmp_path: Path) -> None:
    _write_role_files(tmp_path, {"A": ["prime-builder"], "C": ["loyal-opposition"]})
    original = (
        "# Bridge Index\n\n"
        "<!-- Prime inserts new document entries at the top of the list below. -->\n"
        "<!-- Statuses: NEW, REVISED, GO, NO-GO, VERIFIED -->\n"
        "Document: first\n"
        "NO-GO: bridge/first-002.md\n"
        "NEW: bridge/first-001.md\n"
    )
    index_path = _write_index(tmp_path, original)

    updated = sentinel_module.update_index(index_path, sentinel_module.state_from_files(tmp_path))

    assert "<!-- Prime inserts new document entries at the top of the list below. -->" in updated
    assert "<!-- Statuses: NEW, REVISED, GO, NO-GO, VERIFIED -->" in updated
    assert "Document: first\nNO-GO: bridge/first-002.md\nNEW: bridge/first-001.md" in updated


def test_sentinel_block_has_no_cached_counts(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(sentinel_module, tmp_path)
    sentinel_text = sentinel_module.extract_sentinel_text(index_text)

    assert sentinel_text is not None
    assert "active_prime_authorization_count" not in sentinel_text
    assert "active_lo_advisory_count" not in sentinel_text
    assert "Active Prime authorization count" not in sentinel_text
    assert "Active LO advisory count" not in sentinel_text


def test_counts_mode_emits_live_not_stored(sentinel_module, tmp_path: Path) -> None:
    index_text = _index_with_sentinel(sentinel_module, tmp_path)
    index_text += (
        "\nDocument: no-go-doc\nNO-GO: bridge/no-go-doc-002.md\nNEW: bridge/no-go-doc-001.md\n"
        "\nDocument: new-doc\nNEW: bridge/new-doc-001.md\n"
        "\nDocument: revised-doc\nREVISED: bridge/revised-doc-002.md\nNEW: bridge/revised-doc-001.md\n"
        "\nDocument: advisory-doc\nADVISORY: bridge/advisory-doc-001.md\n"
    )

    output = sentinel_module.counts_output(index_text)
    sentinel_text = sentinel_module.extract_sentinel_text(index_text)

    assert output == "active_prime_authorization_count=2\nactive_lo_advisory_count=3\n"
    assert sentinel_text is not None
    assert "active_prime_authorization_count" not in sentinel_text
    assert "active_lo_advisory_count" not in sentinel_text

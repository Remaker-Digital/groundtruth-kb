"""Tests for the WI-5951 authorization-scan prefilter.

Per ``bridge/gtkb-wi5951-authorization-scan-prefilter-001.md`` (Loyal
Opposition GO at ``-002.md``). Covers the single behavioural change in
``scripts/implementation_authorization.py::_named_packets_authorizing_targets``:
the cheap ``target_path_globs`` filter now runs BEFORE the expensive
``load_named_packet`` integrity validation.

The change is a reordering, not a relaxation. These tests pin both halves of
that claim:

- the returned match set is unchanged (T1, T3),
- no packet reaches the result without full validation (T2, T4),
- corrupt input is still skipped rather than raised (T5).

``load_named_packet`` is monkeypatched throughout so a test can observe exactly
which packets were validated. That is the only way to assert T4 — the defect
is invisible in the return value and only shows up in the work performed.

Uses isolated ``tmp_path`` project roots; the only dependency on the live repo
is the script import path.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    """Load implementation_authorization.py as a module without executing main().

    Registers in sys.modules before exec_module so the @dataclass(frozen=True)
    decorator can resolve cls.__module__ on Python 3.12+.
    """
    spec = importlib.util.spec_from_file_location("implementation_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["implementation_authorization"] = module
    spec.loader.exec_module(module)
    return module


def _by_bridge_dir(auth_module, project_root: Path) -> Path:
    path = project_root / auth_module.BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_packet(auth_module, project_root: Path, bridge_id: str, globs: list[str]) -> Path:
    """Write a named packet carrying only the fields the prefilter reads."""
    path = _by_bridge_dir(auth_module, project_root) / f"{bridge_id}.json"
    path.write_text(
        json.dumps({"bridge_id": bridge_id, "target_path_globs": globs}),
        encoding="utf-8",
    )
    return path


def _install_recording_loader(
    auth_module,
    monkeypatch: pytest.MonkeyPatch,
    *,
    invalid: set[str] | None = None,
) -> list[str]:
    """Replace ``load_named_packet`` with a recorder over on-disk packet JSON.

    Returns the list that accumulates every ``bridge_id`` submitted to full
    validation. Bridge ids in ``invalid`` raise ``AuthorizationError``, standing
    in for expiry, hash-mismatch, or GO-drift failures.
    """
    validated: list[str] = []
    rejected = invalid or set()

    def _fake_load_named_packet(project_root: Path, bridge_id: str) -> dict[str, Any]:
        validated.append(bridge_id)
        if bridge_id in rejected:
            raise auth_module.AuthorizationError(f"Named packet for bridge {bridge_id!r} failed validation")
        path = project_root / auth_module.BY_BRIDGE_DIRECTORY_RELATIVE_PATH / f"{bridge_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    monkeypatch.setattr(auth_module, "load_named_packet", _fake_load_named_packet)
    return validated


def _reference_validate_then_filter(
    auth_module, project_root: Path, normalized_targets: list[str]
) -> list[dict[str, Any]]:
    """The pre-WI-5951 implementation, kept as the T1 equality oracle.

    Deliberately mirrors the original body: validate every packet, then apply
    the cheap filter to whatever survived.
    """
    by_bridge_dir = project_root / auth_module.BY_BRIDGE_DIRECTORY_RELATIVE_PATH
    if not by_bridge_dir.is_dir():
        return []
    matches: list[dict[str, Any]] = []
    for path in sorted(by_bridge_dir.glob("*.json")):
        try:
            packet = auth_module.load_named_packet(project_root, path.stem)
        except auth_module.AuthorizationError:
            continue
        if not auth_module._unauthorized_targets(packet, normalized_targets):
            matches.append(packet)
    return matches


def _ids(packets: list[dict[str, Any]]) -> list[str]:
    return [str(packet.get("bridge_id")) for packet in packets]


# --------------------------------------------------------------------------
# T1 - the returned match set is identical before and after the change
# --------------------------------------------------------------------------


def test_t1_match_set_identical_to_validate_then_filter(auth_module, tmp_path, monkeypatch):
    """Authorization-gate semantics: reordering must not change the result."""
    targets = ["scripts/alpha.py", "scripts/beta.py"]
    _write_packet(auth_module, tmp_path, "exact-both", ["scripts/alpha.py", "scripts/beta.py"])
    _write_packet(auth_module, tmp_path, "glob-covers-both", ["scripts/*.py"])
    _write_packet(auth_module, tmp_path, "covers-one-only", ["scripts/alpha.py"])
    _write_packet(auth_module, tmp_path, "covers-neither", ["docs/**"])
    _write_packet(auth_module, tmp_path, "empty-globs", [])
    _write_packet(auth_module, tmp_path, "expired-but-covering", ["scripts/**"])

    invalid = {"expired-but-covering"}

    _install_recording_loader(auth_module, monkeypatch, invalid=invalid)
    expected = _reference_validate_then_filter(auth_module, tmp_path, targets)

    _install_recording_loader(auth_module, monkeypatch, invalid=invalid)
    actual = auth_module._named_packets_authorizing_targets(tmp_path, targets)

    assert _ids(actual) == _ids(expected)
    assert _ids(actual) == ["exact-both", "glob-covers-both"]


# --------------------------------------------------------------------------
# T2 - no relaxation: an authorizing packet that fails validation is rejected
# --------------------------------------------------------------------------


def test_t2_authorizing_packet_failing_validation_is_never_returned(auth_module, tmp_path, monkeypatch):
    """A packet may authorize the targets and still be invalid; it must not pass."""
    targets = ["scripts/alpha.py"]
    _write_packet(auth_module, tmp_path, "drifted", ["scripts/alpha.py"])

    validated = _install_recording_loader(auth_module, monkeypatch, invalid={"drifted"})
    result = auth_module._named_packets_authorizing_targets(tmp_path, targets)

    assert result == []
    # It survived the prefilter, so validation must still have been attempted:
    # the prefilter must not become an alternative route into the match set.
    assert validated == ["drifted"]


# --------------------------------------------------------------------------
# T3 - no over-rejection: a valid authorizing packet is still returned
# --------------------------------------------------------------------------


def test_t3_valid_authorizing_packet_is_returned(auth_module, tmp_path, monkeypatch):
    targets = ["scripts/alpha.py"]
    _write_packet(auth_module, tmp_path, "valid", ["scripts/**"])

    validated = _install_recording_loader(auth_module, monkeypatch)
    result = auth_module._named_packets_authorizing_targets(tmp_path, targets)

    assert _ids(result) == ["valid"]
    assert validated == ["valid"]


# --------------------------------------------------------------------------
# T4 - the defect itself: non-authorizing packets are never validated
# --------------------------------------------------------------------------


def test_t4_non_authorizing_packets_skip_full_validation(auth_module, tmp_path, monkeypatch):
    """WI-5951: validation is the expensive step and must not run on discards."""
    targets = ["scripts/alpha.py"]
    _write_packet(auth_module, tmp_path, "aaa-irrelevant", ["docs/**"])
    _write_packet(auth_module, tmp_path, "bbb-relevant", ["scripts/alpha.py"])
    for index in range(25):
        _write_packet(auth_module, tmp_path, f"noise-{index:03d}", [f"other/{index}/**"])

    validated = _install_recording_loader(auth_module, monkeypatch)
    result = auth_module._named_packets_authorizing_targets(tmp_path, targets)

    assert _ids(result) == ["bbb-relevant"]
    assert validated == ["bbb-relevant"], (
        "full validation ran for packets the target filter discards; the WI-5951 prefilter is not in effect"
    )


def test_t4b_no_validation_at_all_when_nothing_authorizes(auth_module, tmp_path, monkeypatch):
    targets = ["scripts/alpha.py"]
    for index in range(10):
        _write_packet(auth_module, tmp_path, f"noise-{index:03d}", ["docs/**"])

    validated = _install_recording_loader(auth_module, monkeypatch)
    result = auth_module._named_packets_authorizing_targets(tmp_path, targets)

    assert result == []
    assert validated == []


# --------------------------------------------------------------------------
# T5 - corrupt-input parity: skipped, not raised
# --------------------------------------------------------------------------


def test_t5_corrupt_packet_json_is_skipped_without_raising(auth_module, tmp_path, monkeypatch):
    targets = ["scripts/alpha.py"]
    corrupt = _by_bridge_dir(auth_module, tmp_path) / "corrupt.json"
    corrupt.write_text("{not valid json", encoding="utf-8")
    _write_packet(auth_module, tmp_path, "valid", ["scripts/alpha.py"])

    validated = _install_recording_loader(auth_module, monkeypatch)
    result = auth_module._named_packets_authorizing_targets(tmp_path, targets)

    assert _ids(result) == ["valid"]
    assert "corrupt" not in validated


def test_t5b_missing_by_bridge_directory_returns_empty(auth_module, tmp_path):
    assert auth_module._named_packets_authorizing_targets(tmp_path, ["scripts/alpha.py"]) == []

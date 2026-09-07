"""Focused tests for the modernization hard-invariant registry checker (WI-5152)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = PROJECT_ROOT / "scripts"
REGISTRY_PATH = PROJECT_ROOT / "config" / "governance" / "modernization-hard-invariants.toml"

CHECKER = SCRIPTS / "check_modernization_invariant_registry.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("mod_hard_inv", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mod_hard_inv"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def checker():
    return _load_checker()


class FakeProvider:
    """Deterministic in-memory carrier-version provider (no subprocess)."""

    def __init__(self, versions=None):
        self.versions = versions or {
            "ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001": (1, "specified"),
            "REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001": (2, "specified"),
            "DCL-GIT-BRANCH-BINDING-PROMOTION-001": (3, "specified"),
            "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001": (1, "specified"),
        }

    def resolve(self, spec_id):
        return self.versions.get(spec_id, (None, None))


def _load_toml():
    import tomllib

    with REGISTRY_PATH.open("rb") as fh:
        return tomllib.load(fh)


def test_registry_has_exactly_28_entries():
    data = _load_toml()
    assert len(data["entries"]) == 28
    assert data["registry_id"] == "modernization-hard-invariants-wi5158-gate-1.25"


def test_entry_applicability_split_is_exact():
    data = _load_toml()
    counts = {"MUST_APPLY": 0, "DEFERRED_TO": 0, "CONDITIONAL": 0}
    for e in data["entries"]:
        counts[e["applicability"]] += 1
    assert counts == {"MUST_APPLY": 23, "DEFERRED_TO": 4, "CONDITIONAL": 1}


def test_registry_ids_are_unique():
    data = _load_toml()
    ids = [e["id"] for e in data["entries"]]
    assert len(ids) == len(set(ids))


def test_deferred_targets_match_expected(checker):
    expected = {
        "GIT-ADR-A5": "WI-5159",
        "GIT-REQ-A5": "WI-5159",
        "GIT-REQ-A7": "WI-5160",
        "BRANCH-BIND-A6": "WI-5159",
    }
    data = _load_toml()
    deferred = {e["id"]: e.get("deferred_to") for e in data["entries"] if e["applicability"] == "DEFERRED_TO"}
    assert deferred == expected


def test_checker_returns_pass_with_expected_counts(checker):
    payload = checker.evaluate(provider=FakeProvider(), terminal_evaluator=True)
    assert payload["status"] == "PASS"
    assert payload["entry_count"] == 28
    assert payload["must_apply"] == 23
    assert payload["deferred_to"] == 4
    assert payload["conditional"] == 1
    assert payload["fail_closed"] is True


def test_checker_fails_closed_on_count_mismatch(checker):
    data = _load_toml()
    bad = dict(data)
    bad["entries"] = data["entries"][:-1]
    payload = checker.evaluate(registry=bad, provider=FakeProvider(), terminal_evaluator=True)
    assert payload["status"] == "FAIL"
    assert any(f["reason"] == "registry-count-mismatch" for f in payload["findings"])


def test_checker_fails_closed_on_duplicate(checker):
    data = _load_toml()
    dup = dict(data)
    entries = [dict(e) for e in data["entries"]]
    entries.append(dict(entries[0]))
    dup["entries"] = entries
    payload = checker.evaluate(registry=dup, provider=FakeProvider(), terminal_evaluator=True)
    assert payload["status"] == "FAIL"
    assert any(f["reason"] == "duplicate-entry" for f in payload["findings"])


def test_checker_fails_closed_on_unsupported_applicability(checker):
    data = _load_toml()
    bad = dict(data)
    entries = [dict(e) for e in data["entries"]]
    entries[0]["applicability"] = "BOGUS"
    bad["entries"] = entries
    payload = checker.evaluate(registry=bad, provider=FakeProvider(), terminal_evaluator=True)
    assert payload["status"] == "FAIL"
    assert any(f["reason"] == "unsupported-applicability" for f in payload["findings"])


def test_checker_fails_closed_on_missing_deferred(checker):
    data = _load_toml()
    bad = dict(data)
    entries = [dict(e) for e in data["entries"]]
    for e in entries:
        if e["id"] == "BRANCH-BIND-A6":
            e.pop("deferred_to", None)
    bad["entries"] = entries
    payload = checker.evaluate(registry=bad, provider=FakeProvider(), terminal_evaluator=True)
    assert payload["status"] == "FAIL"
    assert any(f["reason"] == "missing-deferred-target" for f in payload["findings"])


def test_checker_fails_closed_on_stale_carrier(checker):
    data = _load_toml()
    stale = FakeProvider({"DCL-GIT-BRANCH-BINDING-PROMOTION-001": (2, "specified")})
    payload = checker.evaluate(registry=data, provider=stale, terminal_evaluator=True)
    assert payload["status"] == "FAIL"
    assert any(f["reason"] == "stale-carrier-version" for f in payload["findings"])


def test_checker_fails_closed_on_missing_evaluator(checker):
    payload = checker.evaluate(provider=FakeProvider(), terminal_evaluator=False)
    assert payload["status"] == "FAIL"
    assert any(f["reason"] == "missing-wi5153-evaluator" for f in payload["findings"])


def test_checker_is_deterministic(checker):
    p1 = checker.evaluate(provider=FakeProvider(), terminal_evaluator=True)
    p2 = checker.evaluate(provider=FakeProvider(), terminal_evaluator=True)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)


def test_conditional_a4_declared(checker):
    data = _load_toml()
    a4 = next(e for e in data["entries"] if e["id"] == "A4")
    assert a4["applicability"] == "CONDITIONAL"
    assert "NOT_APPLICABLE" in a4.get("conditional_note", "")

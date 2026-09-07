"""Write-time out-of-role bridge status guard (WI-5967 C1).

Per ``bridge/gtkb-wi5967-verdict-role-transition-guard-and-correction-001.md``
(Loyal Opposition GO at ``-002.md``).

`.claude/rules/file-bridge-protocol.md` section Statuses binds each status to an
author role. That binding was enforced only at READ time by
``bridge_lifecycle_resolver``, so an out-of-role verdict reached disk and failed
later at an unrelated caller, wedging its thread. The motivating instance is
``bridge/gtkb-dispatcher-next-foundation-spike-013.md`` -- a Prime-authored
``VERIFIED`` on the P0 Dispatcher Next foundation thread.

These tests pin both directions. Over-blocking would stall the bridge entirely,
so every deny case is paired with an allow case.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"


def _load(path: Path, name: str):
    for extra in (REPO_ROOT, REPO_ROOT / "scripts", REPO_ROOT / "groundtruth-kb" / "src"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate():
    return _load(ACTIVE_HOOK, "_wi5967_active_gate")


def _body(status: str, identity: str) -> str:
    return (
        f"{status}\n\n"
        f"author_identity: {identity}\n"
        "author_harness_id: G\n"
        "author_session_context_id: G-2026-08-06T00-00-00Z\n\n"
        "bridge_kind: lo_verdict\n"
        "Document: fixture\n"
        "Version: 013\n"
    )


def _deny(gate, status: str, identity: str) -> str | None:
    return gate._verdict_role_deny("bridge/fixture-013.md", _body(status, identity), REPO_ROOT)


# --------------------------------------------------------------------------
# T1 - the exact v013 defect: a Prime-authored VERIFIED is refused
# --------------------------------------------------------------------------


def test_t1_prime_authored_verified_is_denied(gate):
    reason = _deny(gate, "VERIFIED", "prime-builder/goose/G")
    assert reason is not None
    assert "VERIFIED" in reason
    assert "prime-builder" in reason
    # The reason must name the rule, not merely refuse, so the author can act on it.
    assert "file-bridge-protocol" in reason


@pytest.mark.parametrize("status", ["GO", "NO-GO", "VERIFIED"])
def test_t1b_all_lo_statuses_denied_under_prime_role(gate, status):
    assert _deny(gate, status, "prime-builder/claude/B") is not None


# --------------------------------------------------------------------------
# T2 - the mirror direction: Prime statuses authored under LO are refused
# --------------------------------------------------------------------------


@pytest.mark.parametrize("status", ["NEW", "REVISED", "NO-ACTION"])
def test_t2_prime_statuses_denied_under_lo_role(gate, status):
    assert _deny(gate, status, "loyal-opposition/goose/G") is not None


# --------------------------------------------------------------------------
# T3 / T5 - no over-blocking: correctly-authored statuses are allowed
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "identity"),
    [
        ("VERIFIED", "loyal-opposition/goose/G"),
        ("GO", "loyal-opposition/goose/G"),
        ("NO-GO", "loyal-opposition/cursor/E"),
        ("NEW", "prime-builder/claude/B"),
        ("REVISED", "prime-builder/claude/B"),
        ("NO-ACTION", "prime-builder/codex/A"),
    ],
)
def test_t3_correctly_authored_statuses_are_allowed(gate, status, identity):
    assert _deny(gate, status, identity) is None


def test_t3b_non_status_first_line_is_ignored(gate):
    """The guard must not fire on content that is not a bridge status write."""
    content = "# Some heading\n\nauthor_identity: prime-builder/claude/B\n"
    assert gate._verdict_role_deny("bridge/fixture-013.md", content, REPO_ROOT) is None


# --------------------------------------------------------------------------
# T6 - fail-soft contract inherited from the sibling self-review guard
# --------------------------------------------------------------------------


def test_t6_unparseable_author_identity_allows(gate):
    """An identity the resolver cannot parse is its legacy/malformed concern.

    ``bridge/gtkb-dispatcher-next-foundation-spike-002.md`` carries
    ``author_identity: OpenRouter F``, which parses to no role. The guard must
    not invent a verdict for it.
    """
    assert _deny(gate, "VERIFIED", "OpenRouter F") is None


def test_t6b_missing_author_identity_allows(gate):
    content = "VERIFIED\n\nbridge_kind: lo_verdict\nDocument: fixture\n"
    assert gate._verdict_role_deny("bridge/fixture-013.md", content, REPO_ROOT) is None


def test_t6c_resolver_import_failure_allows(gate, monkeypatch):
    """Infrastructure failure must allow, never deny -- the resolver backstops."""
    import builtins

    real_import = builtins.__import__

    def _boom(name, *args, **kwargs):
        if "bridge_lifecycle_resolver" in name:
            raise ImportError("simulated infrastructure failure")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    assert _deny(gate, "VERIFIED", "prime-builder/goose/G") is None


# --------------------------------------------------------------------------
# T7 - template parity
# --------------------------------------------------------------------------


def test_t7_template_carries_the_identical_guard():
    active = ACTIVE_HOOK.read_text(encoding="utf-8")
    template = TEMPLATE_HOOK.read_text(encoding="utf-8")
    start = active.index("def _verdict_role_deny(")
    end = active.index("def _no_action_prior_verdict_deny(")
    guard = active[start:end]
    assert guard in template, "template hook is missing the byte-identical WI-5967 guard"
    assert "role_deny = _verdict_role_deny(" in template, "template hook does not dispatch the guard"


def test_t7b_template_guard_behaves_identically():
    template_gate = _load(TEMPLATE_HOOK, "_wi5967_template_gate")
    assert (
        template_gate._verdict_role_deny("bridge/fixture-013.md", _body("VERIFIED", "prime-builder/goose/G"), REPO_ROOT)
        is not None
    )
    assert (
        template_gate._verdict_role_deny(
            "bridge/fixture-013.md", _body("VERIFIED", "loyal-opposition/goose/G"), REPO_ROOT
        )
        is None
    )


# --------------------------------------------------------------------------
# Single source of truth: the guard must not carry its own role table
# --------------------------------------------------------------------------


def test_guard_defers_to_the_resolver_predicate(gate):
    """A duplicated table would drift; the guard must import the resolver's."""
    from scripts.bridge_lifecycle_resolver import author_role_is_valid_for_status

    assert author_role_is_valid_for_status("VERIFIED", "loyal-opposition") is True
    assert author_role_is_valid_for_status("VERIFIED", "prime-builder") is False
    assert author_role_is_valid_for_status("NEW", "prime-builder") is True
    assert author_role_is_valid_for_status("NEW", "loyal-opposition") is False

# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the Codex SessionStart hook dispatcher.

Authority: bridge/gtkb-canonical-init-keyword-syntax-001-005.md IP-8 surface 4
(Codex GO at -008). Mirror of
``platform_tests/scripts/test_claude_session_start_dispatcher.py`` for the
Codex side, focused on IP-4 ``StartupDecision`` enum-path coverage.

Specs:

- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause — set-membership
  check, mismatch -> STRICT_DROP with audit log.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — receiver enforcement must apply
  symmetrically to both Claude and Codex.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"


def _load_codex_hook(name_suffix: str) -> ModuleType:
    """Load Codex hook with unique sys.modules key for test isolation."""
    name = f"codex_session_start_dispatch_test_{name_suffix}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, DISPATCHER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_harness_state(
    project_root: Path,
    *,
    claude_role: str | list[str] = "prime-builder",
    codex_role: str | list[str] = "loyal-opposition",
) -> None:
    """Seed the harness registry projection with the requested role assignments.

    WI-3342 IP-4: the SessionStart dispatcher's ``_resolve_own_role_set``
    resolves identity + role in a single lookup against the DB-backed registry
    projection ``harness-state/harness-registry.json`` (migrated from the
    two-step ``harness-identities.json`` -> ``role-assignments.json`` chain).
    The projection's ``harnesses`` field is a LIST of unified records; each
    record carries ``id``, ``harness_name``, and ``role``. ``claude_role`` /
    ``codex_role`` accept the scalar or list wire form; both are normalized to
    the role-set list form here.
    """

    def _role_list(value: str | list[str]) -> list[str]:
        return list(value) if isinstance(value, list) else [value]

    harness_state = project_root / "harness-state"
    harness_state.mkdir(parents=True, exist_ok=True)
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": _role_list(codex_role),
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "role": _role_list(claude_role),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


# ──────────────────────────────────────────────────────────────────────────
# StartupDecision enum existence + values
# ──────────────────────────────────────────────────────────────────────────


def test_startup_decision_enum_has_five_distinct_values() -> None:
    """IP-4 enum cleanup — five mutually-exclusive decision values."""
    hook = _load_codex_hook("enum_values")
    values = {d.value for d in hook.StartupDecision}
    expected = {
        "normal_startup",
        "dispatch_authorized",
        "spoof_fallback",
        "legacy_fallback",
        "strict_drop",
    }
    assert values == expected, (
        f"StartupDecision values drifted: got {values!r}, expected {expected!r}"
    )


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-codex-receiver-decisions — five enum paths
# ──────────────────────────────────────────────────────────────────────────


def test_normal_startup_when_no_env_no_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No env-var, no keyword -> NORMAL_STARTUP."""
    _write_harness_state(tmp_path)
    hook = _load_codex_hook("normal_startup")
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    monkeypatch.delenv("GTKB_BRIDGE_DISPATCH_KEYWORD", raising=False)
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.NORMAL_STARTUP


def test_dispatch_authorized_when_env_and_matching_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env-var + keyword + mode-in-role-set -> DISPATCH_AUTHORIZED."""
    # Codex hosts loyal-opposition; mode 'lo' must be authorized.
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    hook = _load_codex_hook("dispatch_auth")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-codex-auth")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.DISPATCH_AUTHORIZED


def test_dispatch_authorized_when_role_record_is_multi_role_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Single-harness role-set schema: Codex can authorize either role mode."""
    _write_harness_state(
        tmp_path,
        claude_role="loyal-opposition",
        codex_role=["loyal-opposition", "prime-builder"],
    )
    hook = _load_codex_hook("dispatch_auth_role_set")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-codex-auth-role-set")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb pb")
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.DISPATCH_AUTHORIZED


def test_spoof_fallback_when_keyword_without_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """keyword present, env-var absent -> SPOOF_FALLBACK.

    Defends against an owner-typed keyword without the trigger's
    accompanying env var.
    """
    _write_harness_state(tmp_path)
    hook = _load_codex_hook("spoof_fallback")
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.SPOOF_FALLBACK


def test_legacy_fallback_when_env_without_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env-var present, keyword absent -> LEGACY_FALLBACK.

    Preserves backward compat with older trigger versions that did not
    set the canonical keyword env var alongside the run-id env var.
    """
    _write_harness_state(tmp_path)
    hook = _load_codex_hook("legacy_fallback")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-codex-legacy")
    monkeypatch.delenv("GTKB_BRIDGE_DISPATCH_KEYWORD", raising=False)
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.LEGACY_FALLBACK


def test_strict_drop_when_mode_not_in_own_role_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env-var + keyword + mode-NOT-in-role-set -> STRICT_DROP + audit log.

    Codex has durable role 'loyal-opposition' ({'lo'}); a dispatch with
    keyword 'pb' must be silently dropped.
    """
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    hook = _load_codex_hook("strict_drop")
    failures_path = tmp_path / "dispatch-failures.jsonl"
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-codex-misdirect")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb pb")
    decision, _reason = hook._bridge_dispatch_keyword_check(
        project_root=tmp_path, failures_path=failures_path
    )
    assert decision == hook.StartupDecision.STRICT_DROP

    # Audit log entry written with structured fields.
    assert failures_path.is_file()
    lines = [l for l in failures_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines
    record = json.loads(lines[-1])
    assert record["kind"] == "misdirected_dispatch_strict_drop"
    assert record["observed_keyword_mode"] == "pb"
    assert record["expected_role_set"] == ["lo"]
    assert record["own_harness_name"] == "codex"
    assert record["own_harness_id"] == "A"


# ──────────────────────────────────────────────────────────────────────────
# Fail-closed behavior on unreadable role records
# ──────────────────────────────────────────────────────────────────────────


def test_strict_drop_on_unreadable_role_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If own durable role is unreadable, treat dispatch as misdirected.

    Fail-closed semantic: cannot prove the keyword matches our role -> drop.
    """
    # Intentionally do NOT write harness-state files. _resolve_own_role_set
    # will raise FileNotFoundError; the keyword check must STRICT_DROP.
    hook = _load_codex_hook("unreadable_role")
    failures_path = tmp_path / "dispatch-failures.jsonl"
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-codex-unreadable")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, reason = hook._bridge_dispatch_keyword_check(
        project_root=tmp_path, failures_path=failures_path
    )
    assert decision == hook.StartupDecision.STRICT_DROP
    assert "could not resolve own role set" in reason


# ──────────────────────────────────────────────────────────────────────────
# Envelope shape parity with the Claude dispatcher
# ──────────────────────────────────────────────────────────────────────────


def test_codex_hook_has_envelope_parity_constants() -> None:
    """The Codex hook must expose the same IP-4 constants the Claude hook
    exposes (regex, env var names, decision enum).

    Shape parity invariant per ``SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001``
    (parallel/precedent) and DCL-CROSS-HARNESS-ENFORCEMENT-001.
    """
    hook = _load_codex_hook("envelope_parity")
    # Regex compiled with the canonical pattern.
    assert hook._CANONICAL_KEYWORD_RE.pattern == r"^::init gtkb (pb|lo)$"
    # Env var name constants.
    assert hook._BRIDGE_DISPATCH_RUN_ID_ENV == "GTKB_BRIDGE_POLLER_RUN_ID"
    assert hook._BRIDGE_DISPATCH_KEYWORD_ENV == "GTKB_BRIDGE_DISPATCH_KEYWORD"
    # Label mapping.
    assert hook._LABEL_TO_CANONICAL_MODE == {
        "prime-builder": "pb",
        "acting-prime-builder": "pb",
        "loyal-opposition": "lo",
    }
    # Dispatch-failures path is under .gtkb-state/bridge-poller/.
    failures_path = str(hook.DISPATCH_FAILURES_PATH).replace("\\", "/")
    assert ".gtkb-state/bridge-poller/dispatch-failures.jsonl" in failures_path


# ──────────────────────────────────────────────────────────────────────────
# Startup-disclosure relay cache tests
#
# Authority: bridge/gtkb-startup-relay-truncation-fix-refile-003.md (Codex GO
# at -004); DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Required Behavior 5.
# ──────────────────────────────────────────────────────────────────────────


def test_startup_relay_cache_written_with_consistent_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """T4 -- the dispatcher writes a harness-scoped relay cache + consistent metadata."""
    import hashlib

    module = _load_codex_hook("relay_cache_write")
    monkeypatch.setattr(module, "OUT_DIR", tmp_path)
    body = "# GroundTruth-KB Fresh Session Startup\n\nrelay body line one\nrelay body line two"
    module._write_startup_relay_cache(
        "# GroundTruth-KB Programmatic Startup Payload\n\n## User-Visible Startup Message\n\n" + body
    )

    cache = tmp_path / "last-user-visible-startup.md"
    meta_path = tmp_path / "last-user-visible-startup.meta.json"
    assert cache.is_file() and meta_path.is_file()
    cached = cache.read_text(encoding="utf-8")
    assert cached == body, "cache holds the extracted user-visible startup message"
    assert "Programmatic Startup Payload" not in cached
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    encoded = cached.encode("utf-8")
    assert meta["sha256"] == hashlib.sha256(encoded).hexdigest()
    assert meta["byte_length"] == len(encoded)
    assert meta["harness_name"] == "codex"


def test_startup_relay_cache_not_written_by_bridge_dispatch_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """T4 -- bridge auto-dispatch payloads must not populate the interactive relay cache.

    DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Required Behavior 5: the
    interactive startup-disclosure cache is isolated from bridge auto-dispatch
    SessionStart payloads.
    """
    module = _load_codex_hook("relay_cache_isolation")
    monkeypatch.setattr(module, "OUT_DIR", tmp_path)
    monkeypatch.setattr(module, "_bridge_auto_dispatch_context", lambda: "bridge auto-dispatch test context")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-relay-isolation")
    monkeypatch.delenv("GTKB_BRIDGE_DISPATCH_KEYWORD", raising=False)

    rc = module.main()
    capsys.readouterr()
    assert rc == 0
    assert not (tmp_path / "last-user-visible-startup.md").exists(), (
        "bridge auto-dispatch path must not populate the interactive relay cache"
    )

"""Tests for the Claude SessionStart hook dispatcher.

Authority: bridge/gtkb-claude-session-start-parity-001.md (Codex GO at -002).
IP-4 extension authority: bridge/gtkb-canonical-init-keyword-syntax-001-005.md
(Codex GO at -008) — adds StartupDecision enum-path coverage per IP-8 surface 4.

Verifies:
- Dispatcher emits a properly-shaped SessionStart `hookSpecificOutput` envelope
  (`GOV-SESSION-SELF-INITIALIZATION-001`).
- Payload includes the canonical role/governance disclosure
  (`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`).
- Payload includes token-budget content
  (`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`).
- Envelope shape matches the Codex dispatcher
  (`SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` parallel/precedent).
- Diagnostic files land under `.claude/hooks/`
  (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`).
- `.claude/settings.json` SessionStart timeout matches `.codex/hooks.json`.
- Canonical service `--emit-report --fast-hook --harness-name claude` no
  longer prints the `scripts.check_harness_parity` import error
  (Change 3 — harness-parity import repair).
- Dispatcher fails soft and emits a degraded-banner fallback when the
  startup service is unreachable.
- IP-4 StartupDecision enum has five distinct paths covering every
  combination of env-var, keyword, and own-role-set membership
  (`DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` receiver clause).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = PROJECT_ROOT / ".claude" / "hooks" / "session_start_dispatch.py"
DIAG_JSON = PROJECT_ROOT / ".claude" / "hooks" / "last-session-start.json"
DIAG_ERR = PROJECT_ROOT / ".claude" / "hooks" / "last-session-start.err"
CLAUDE_SETTINGS = PROJECT_ROOT / ".claude" / "settings.json"
CODEX_HOOKS = PROJECT_ROOT / ".codex" / "hooks.json"
STARTUP_SERVICE = PROJECT_ROOT / "scripts" / "session_self_initialization.py"


_BRIDGE_DISPATCH_ENV_VARS = frozenset(
    {"GTKB_BRIDGE_POLLER_RUN_ID", "GTKB_BRIDGE_DISPATCH_KEYWORD"}
)


def _run_dispatcher(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Invoke the SessionStart dispatcher in a hermetic env by default.

    Per Slice 4 NO-GO -018 F1 and IP-4 of
    bridge/gtkb-canonical-init-keyword-syntax-001 (NO-GO at -010 F1): when
    `env` is None, the default environment strips BOTH bridge-dispatch markers
    (``GTKB_BRIDGE_POLLER_RUN_ID`` and ``GTKB_BRIDGE_DISPATCH_KEYWORD``) from
    the inherited process env so normal-startup tests stay deterministic in
    bridge auto-dispatched review sessions (where the trigger sets both
    markers for its child harness). Tests that intentionally exercise the
    bridge auto-dispatch branch must pass an explicit `env` containing the
    relevant marker(s) themselves; inheriting the parent shell's markers is
    a hermeticity defect that Codex's NO-GO at -010 surfaced.
    """
    if env is None:
        env = {
            k: v for k, v in os.environ.items() if k not in _BRIDGE_DISPATCH_ENV_VARS
        }
    return subprocess.run(
        [sys.executable, str(DISPATCHER)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
        env=env,
    )


def test_dispatcher_emits_session_start_envelope() -> None:
    """`hookSpecificOutput.hookEventName == 'SessionStart'` per Claude Code contract.

    Spec: GOV-SESSION-SELF-INITIALIZATION-001.
    """
    result = _run_dispatcher()
    assert result.returncode == 0, f"dispatcher non-zero exit: {result.stderr}"
    payload = json.loads(result.stdout)
    assert "hookSpecificOutput" in payload
    hook_output = payload["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "SessionStart"
    assert isinstance(hook_output["additionalContext"], str)
    assert len(hook_output["additionalContext"]) > 100


def test_envelope_contains_governance_disclosure() -> None:
    """Role / governance / bridge / poller / role-mapping disclosure present.

    Spec: PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001.
    """
    result = _run_dispatcher()
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Programmatic Startup Payload" in ctx
    assert "Role being assumed:" in ctx
    assert "Role mapping source:" in ctx
    assert "harness-state/role-assignments.json" in ctx


def test_envelope_contains_token_budget_content() -> None:
    """Startup payload exposes token-budget context per DCL.

    Spec: DCL-SESSION-STARTUP-TOKEN-BUDGET-001.
    """
    result = _run_dispatcher()
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Token measurement status:" in ctx
    assert "reducing startup token consumption" in ctx.lower() or "token consumption" in ctx.lower()


def test_bridge_auto_dispatch_context_bypasses_interactive_startup() -> None:
    """Bridge poller dispatch sessions must process the initial prompt.

    The verified smart poller (and now the cross-harness event-driven trigger)
    launches headless harnesses with ``GTKB_BRIDGE_POLLER_RUN_ID`` in the
    environment. In that mode the SessionStart hook must not emit interactive
    fresh-session semantics that cause Codex/Claude to discard the auto-dispatch
    prompt as a startup stimulus.

    Per IP-4 of bridge/gtkb-canonical-init-keyword-syntax-001 (Codex GO at -008):
    this test pins the LEGACY_FALLBACK enum path -- env-var present, canonical
    keyword absent. The hermetic env explicitly strips
    ``GTKB_BRIDGE_DISPATCH_KEYWORD`` from any inherited parent state so the test
    is deterministic in bridge auto-dispatched review sessions where the
    parent's keyword env var would otherwise leak in (per Codex NO-GO at -010 F1).
    The DISPATCH_AUTHORIZED canonical-keyword-matching path is covered by
    ``test_dispatch_authorized_when_env_and_matching_keyword``.
    """
    env = {k: v for k, v in os.environ.items() if k not in _BRIDGE_DISPATCH_ENV_VARS}
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = "test-run-001"
    # Explicitly do NOT set GTKB_BRIDGE_DISPATCH_KEYWORD: this test asserts
    # the LEGACY_FALLBACK path (env-var-only legacy dispatch behavior).

    result = _run_dispatcher(env=env)
    assert result.returncode == 0, f"dispatcher non-zero exit: {result.stderr}"
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Bridge Auto-Dispatch Session" in ctx
    assert "test-run-001" in ctx
    assert "Programmatic Startup Payload" not in ctx
    assert "discarded owner session-start stimulus" in ctx
    assert "active bridge auto-dispatch task" in ctx
    assert "bridge/INDEX.md" in ctx


def test_envelope_shape_parity_with_codex() -> None:
    """Claude dispatcher emits same envelope keys as the Codex dispatcher.

    Both dispatchers must produce `hookSpecificOutput` with exactly the
    `hookEventName` and `additionalContext` keys at minimum.

    Spec: SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001 (parallel/precedent).
    """
    result = _run_dispatcher()
    payload = json.loads(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    required_keys = {"hookEventName", "additionalContext"}
    assert required_keys.issubset(hook_output.keys())


def test_diagnostic_files_land_in_claude_hooks_dir() -> None:
    """Diagnostic files must resolve under E:\\GT-KB\\.claude\\hooks\\.

    Spec: ADR-ISOLATION-APPLICATION-PLACEMENT-001.
    """
    _run_dispatcher()
    assert DIAG_JSON.is_file(), f"missing {DIAG_JSON}"
    assert DIAG_ERR.is_file(), f"missing {DIAG_ERR}"
    # Both files must be under the project root
    assert PROJECT_ROOT in DIAG_JSON.resolve().parents
    assert PROJECT_ROOT in DIAG_ERR.resolve().parents
    # Diagnostic JSON must contain the canonical hookSpecificOutput envelope
    content = DIAG_JSON.read_text(encoding="utf-8")
    assert "hookSpecificOutput" in content


def test_session_start_timeout_alignment() -> None:
    """`.claude/settings.json` SessionStart timeout matches `.codex/hooks.json`.

    Both must be 60 s (Codex's existing value); this prevents Claude-side
    truncation under load.
    """
    claude = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))
    codex = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))

    def _session_start_timeout(settings: dict) -> int:
        for entry in settings.get("hooks", {}).get("SessionStart", []):
            for hook in entry.get("hooks", []):
                if "timeout" in hook:
                    return int(hook["timeout"])
        return -1

    claude_timeout = _session_start_timeout(claude)
    codex_timeout = _session_start_timeout(codex)
    assert claude_timeout > 0, "Claude settings has no SessionStart timeout"
    assert codex_timeout > 0, "Codex hooks has no SessionStart timeout"
    assert claude_timeout == codex_timeout, f"Claude SessionStart timeout {claude_timeout}s != Codex {codex_timeout}s"


def test_harness_parity_import_repaired() -> None:
    """The canonical service no longer prints the import error.

    Change 3 — repairs `No module named 'scripts.check_harness_parity'`
    by ensuring project root is on sys.path before sibling imports.
    """
    result = subprocess.run(
        [
            sys.executable,
            str(STARTUP_SERVICE),
            "--emit-report",
            "--fast-hook",
            "--harness-name",
            "claude",
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert "No module named 'scripts.check_harness_parity'" not in result.stdout
    assert "Harness parity:" in result.stdout
    # Should NOT be "unavailable" anymore
    assert "Harness parity: unavailable" not in result.stdout


def test_dispatcher_fallback_on_broken_startup_service(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """If the startup service path is unreachable, dispatcher emits a fallback.

    Validates fail-soft behavior — dispatcher must always emit a valid
    SessionStart envelope, even when the canonical service is broken.

    Per Slice 4 NO-GO -018 F1: this test calls ``module.main()`` in-process
    so it inherits the test process env. In bridge auto-dispatched review
    sessions ``GTKB_BRIDGE_POLLER_RUN_ID`` is set, which would route the
    dispatcher into ``_bridge_auto_dispatch_context()`` before reaching the
    fallback path under test. ``monkeypatch.delenv`` makes this test
    hermetic regardless of inherited env.
    """
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "session_start_dispatch_test_fallback",
        DISPATCHER,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Point STARTUP_SERVICE at a path that does not exist; subprocess.run
    # will raise FileNotFoundError, which the dispatcher catches and routes
    # through `_fallback_context`.
    module.STARTUP_SERVICE = tmp_path / "does_not_exist.py"

    rc = module.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out, "dispatcher emitted no stdout on broken-service path"
    payload = json.loads(captured.out)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "Startup Service Degraded" in ctx
    assert "Dashboard" in ctx


# ──────────────────────────────────────────────────────────────────────────
# IP-4 StartupDecision enum-path tests
#
# Authority: bridge/gtkb-canonical-init-keyword-syntax-001-005.md IP-8 surface 4
# (Codex GO at -008). T-CIK-claude-receiver-decisions in the spec-derived test
# plan. Each enum value MUST be reached for the matching env/keyword/role
# combination per the IP-4 behavior table.
# ──────────────────────────────────────────────────────────────────────────


def _load_claude_hook_isolated(name_suffix: str) -> ModuleType:
    """Load Claude hook with unique sys.modules key for IP-4 enum-path tests."""
    name = f"claude_session_start_dispatch_ip4_{name_suffix}"
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


def test_startup_decision_enum_has_five_distinct_values() -> None:
    """IP-4 enum cleanup — five mutually-exclusive decision values."""
    hook = _load_claude_hook_isolated("enum_values")
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


def test_normal_startup_when_no_env_no_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No env-var, no keyword -> NORMAL_STARTUP (Claude side)."""
    _write_harness_state(tmp_path)
    hook = _load_claude_hook_isolated("normal_startup")
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    monkeypatch.delenv("GTKB_BRIDGE_DISPATCH_KEYWORD", raising=False)
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.NORMAL_STARTUP


def test_dispatch_authorized_when_env_and_matching_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env-var + keyword + mode-in-role-set -> DISPATCH_AUTHORIZED (Claude side).

    Claude hosts prime-builder; mode 'pb' must be authorized.
    """
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    hook = _load_claude_hook_isolated("dispatch_auth")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-claude-auth")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb pb")
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.DISPATCH_AUTHORIZED


def test_dispatch_authorized_when_role_record_is_multi_role_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Single-harness role-set schema: Claude can authorize either role mode."""
    _write_harness_state(
        tmp_path,
        claude_role=["loyal-opposition", "prime-builder"],
        codex_role="loyal-opposition",
    )
    hook = _load_claude_hook_isolated("dispatch_auth_role_set")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-claude-auth-role-set")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.DISPATCH_AUTHORIZED


def test_spoof_fallback_when_keyword_without_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """keyword present, env-var absent -> SPOOF_FALLBACK (Claude side).

    Defends against an owner-typed keyword without the trigger's
    accompanying env var.
    """
    _write_harness_state(tmp_path)
    hook = _load_claude_hook_isolated("spoof_fallback")
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb pb")
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.SPOOF_FALLBACK


def test_legacy_fallback_when_env_without_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env-var present, keyword absent -> LEGACY_FALLBACK (Claude side).

    Preserves backward compat with older trigger versions that did not
    set the canonical keyword env var alongside the run-id env var.
    """
    _write_harness_state(tmp_path)
    hook = _load_claude_hook_isolated("legacy_fallback")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-claude-legacy")
    monkeypatch.delenv("GTKB_BRIDGE_DISPATCH_KEYWORD", raising=False)
    decision, _reason = hook._bridge_dispatch_keyword_check(project_root=tmp_path)
    assert decision == hook.StartupDecision.LEGACY_FALLBACK


def test_strict_drop_when_mode_not_in_own_role_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """env-var + keyword + mode-NOT-in-role-set -> STRICT_DROP + audit log
    (Claude side).

    Claude has durable role 'prime-builder' ({'pb'}); a dispatch with
    keyword 'lo' must be silently dropped with an audit log entry.
    """
    _write_harness_state(tmp_path, claude_role="prime-builder", codex_role="loyal-opposition")
    hook = _load_claude_hook_isolated("strict_drop")
    failures_path = tmp_path / "dispatch-failures.jsonl"
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-claude-misdirect")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb lo")
    decision, _reason = hook._bridge_dispatch_keyword_check(
        project_root=tmp_path, failures_path=failures_path
    )
    assert decision == hook.StartupDecision.STRICT_DROP

    # Audit log written with structured fields.
    assert failures_path.is_file()
    lines = [l for l in failures_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines
    record = json.loads(lines[-1])
    assert record["kind"] == "misdirected_dispatch_strict_drop"
    assert record["observed_keyword_mode"] == "lo"
    assert record["expected_role_set"] == ["pb"]
    assert record["own_harness_name"] == "claude"
    assert record["own_harness_id"] == "B"


def test_strict_drop_on_unreadable_role_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If own durable role is unreadable, treat dispatch as misdirected
    (Claude side).

    Fail-closed semantic: cannot prove keyword matches our role -> drop.
    """
    # Intentionally do NOT write harness-state files.
    hook = _load_claude_hook_isolated("unreadable_role")
    failures_path = tmp_path / "dispatch-failures.jsonl"
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-run-claude-unreadable")
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", "::init gtkb pb")
    decision, reason = hook._bridge_dispatch_keyword_check(
        project_root=tmp_path, failures_path=failures_path
    )
    assert decision == hook.StartupDecision.STRICT_DROP
    assert "could not resolve own role set" in reason


def test_claude_hook_has_envelope_parity_constants() -> None:
    """The Claude hook must expose the same IP-4 constants the Codex hook
    exposes (regex, env var names, decision enum, dispatch-failures path).
    """
    hook = _load_claude_hook_isolated("envelope_parity")
    assert hook._CANONICAL_KEYWORD_RE.pattern == r"^::init gtkb (pb|lo)$"
    assert hook._BRIDGE_DISPATCH_RUN_ID_ENV == "GTKB_BRIDGE_POLLER_RUN_ID"
    assert hook._BRIDGE_DISPATCH_KEYWORD_ENV == "GTKB_BRIDGE_DISPATCH_KEYWORD"
    assert hook._LABEL_TO_CANONICAL_MODE == {
        "prime-builder": "pb",
        "acting-prime-builder": "pb",
        "loyal-opposition": "lo",
    }
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

    module = _load_claude_hook_isolated("relay_cache_write")
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
    assert meta["harness_name"] == "claude"


def test_startup_relay_cache_not_written_by_bridge_dispatch_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """T4 -- bridge auto-dispatch payloads must not populate the interactive relay cache.

    DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Required Behavior 5: the
    interactive startup-disclosure cache is isolated from bridge auto-dispatch
    SessionStart payloads.
    """
    module = _load_claude_hook_isolated("relay_cache_isolation")
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

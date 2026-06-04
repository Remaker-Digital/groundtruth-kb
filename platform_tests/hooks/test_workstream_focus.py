"""Regression tests for GT-KB workstream focus / work-subject hooks."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "workstream_focus.py"
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "workstream-focus.py"

_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

# WI-3342 IP-6 — registry-backed role reader/writer fixtures.
#
# scripts/workstream_focus.py resolves the harness role map through
# scripts.harness_roles.load_role_assignments, migrated to read the DB-backed
# registry projection (harness-state/harness-registry.json). The role-toggle
# path (handle_role_command -> set_next_session_role -> set_harness_role)
# persists to the DB ``harnesses`` table and regenerates the projection. Tests
# that exercise role reads/writes therefore seed an ISOLATED groundtruth.db +
# projection under tmp_path; they MUST NOT pass the real REPO_ROOT (that would
# mutate the real registry — the IP-2 smoke-test pollution this WI-3342 thread
# exists to remediate).


def _seed_registry(root: Path, harnesses: dict[str, tuple[str, list[str]]]) -> None:
    """Seed a groundtruth.db ``harnesses`` table + generated projection.

    ``harnesses`` maps each durable harness id to ``(harness_name, role_set)``.
    """
    from groundtruth_kb.db import KnowledgeDB
    from groundtruth_kb.harness_projection import generate_harness_projection

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_id, (harness_name, role_set) in harnesses.items():
        db.insert_harness(
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_name,
            role=list(role_set),
            changed_by="test",
            change_reason="WI-3342 IP-6 workstream_focus fixture",
            status="active",
        )
    generate_harness_projection(db, root)


def _copy_parity_registry(root: Path) -> None:
    """Copy the harness-capability-registry.toml into an isolated project root.

    The role-toggle path renders a harness-parity message via
    scripts.check_harness_parity.check_harness_parity, which reads
    ``<root>/config/agent-control/harness-capability-registry.toml``. Copying
    the canonical registry lets the parity check resolve against an isolated
    tmp_path root.
    """
    src = REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
    dst = root / "config" / "agent-control" / "harness-capability-registry.toml"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def _projection_role(root: Path, harness_id: str) -> object:
    """Return the raw ``role`` field for ``harness_id`` in the registry projection."""
    projection = json.loads((root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    for record in projection.get("harnesses", []):
        if isinstance(record, dict) and record.get("id") == harness_id:
            return record.get("role")
    raise KeyError(harness_id)


def _load_module():
    spec = importlib.util.spec_from_file_location("workstream_focus", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["workstream_focus"] = module
    spec.loader.exec_module(module)
    return module


def _run_hook(payload: dict, state_path: Path, *, guard_path: Path | None = None) -> dict:
    env = {
        **dict(os.environ),
        "GTKB_WORKSTREAM_FOCUS_STATE": str(state_path),
        "CLAUDE_PROJECT_DIR": str(REPO_ROOT),
    }
    effective_guard_path = guard_path or (state_path.parent / "lifecycle-guard.json")
    env["GTKB_LIFECYCLE_GUARD_PATH"] = str(effective_guard_path)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        cwd=REPO_ROOT,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
    )
    return json.loads(result.stdout)


def _isolate_state(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    canonical = tmp_path / "work-subject.json"
    legacy = tmp_path / ".workstream-focus-state.json"
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(canonical))
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_LEGACY_STATE", str(legacy))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))
    monkeypatch.delenv("GTKB_PRODUCT_ROOT", raising=False)
    return canonical, legacy


def _write_role_map(path: Path, roles: dict[str, tuple[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    harness_id: {"harness_type": harness_type, "role": role}
                    for harness_id, (harness_type, role) in roles.items()
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_registry_projection(root: Path, harnesses: dict[str, tuple[str, str | list[str]]]) -> None:
    """Seed the registry projection file directly under ``root``.

    ``harnesses`` maps each durable harness id to ``(harness_name, role)``.
    Pure-reader code paths (``detect_counterpart_state``) resolve identity +
    role from this projection (``harness-state/harness-registry.json``), so a
    file-level seed is sufficient — no DB fixture needed.
    """
    records = []
    for harness_id, (harness_name, role) in harnesses.items():
        role_list = list(role) if isinstance(role, list) else [role]
        records.append(
            {
                "id": harness_id,
                "harness_name": harness_name,
                "harness_type": harness_name,
                "status": "active",
                "role": role_list,
            }
        )
    registry = root / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": records,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_default_work_subject_is_gtkb_and_startup_lines_explain_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    state = module.load_state(REPO_ROOT)
    lines = module.render_startup_focus_lines(module.startup_focus_snapshot(REPO_ROOT))

    assert state["default_focus"] == module.FOCUS_GTKB_INFRASTRUCTURE
    assert state["current_focus"] == module.FOCUS_GTKB_INFRASTRUCTURE
    assert state["current_subject"] == module.SUBJECT_GTKB
    assert state["schema_version"] == module.SCHEMA_VERSION
    assert state["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert "Default work subject: GT-KB Infrastructure Focus" in lines
    assert "Current work subject: GT-KB Infrastructure Focus" in lines
    assert "GT-KB is the default work subject" in lines
    assert "`work subject application`" in lines
    assert "`work subject GT-KB`" in lines
    assert "`application mode`" in lines
    assert "`GT-KB mode`" in lines
    assert ".claude/session/work-subject.json" in lines


def test_canonical_state_file_written_under_claude_session(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)

    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT, updated_by="owner_prompt")

    assert canonical.exists()
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["schema_version"] == module.SCHEMA_VERSION
    assert data["current_subject"] == module.SUBJECT_GTKB
    assert data["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert data["source"] == "standalone owner command"
    assert data["updated_by"] == "owner_prompt"
    assert data["updated_at"]
    assert data["project_root"]
    # gtkb_root may be None; key must exist.
    assert "gtkb_root" in data


def test_legacy_state_migrates_on_load_when_canonical_absent(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _, legacy = _isolate_state(monkeypatch, tmp_path)

    legacy.write_text(
        json.dumps(
            {
                "default_focus": "application",
                "current_focus": "gtkb_infrastructure",
                "application_label": "Agent Red",
                "updated_at": "2026-04-01T00:00:00Z",
                "updated_by": "owner_prompt",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    state = module.load_state(REPO_ROOT)
    assert state["current_subject"] == module.SUBJECT_GTKB
    assert state["current_focus"] == module.FOCUS_GTKB_INFRASTRUCTURE
    assert state["source"] == "legacy workstream alias"


def test_work_subject_application_command_sets_canonical_state(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    # Seed GT-KB so the command flips state.
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_user_prompt("work subject application", REPO_ROOT)

    assert "Current work subject set to Application Focus" in response["systemMessage"]
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["current_subject"] == module.SUBJECT_APPLICATION


def test_work_subject_gtkb_command_sets_canonical_state(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)

    response = module.handle_user_prompt("work subject GT-KB", REPO_ROOT)

    assert "Current work subject set to GT-KB Infrastructure Focus" in response["systemMessage"]
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["current_subject"] == module.SUBJECT_GTKB


def test_legacy_aliases_still_recognized(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    # Application-side legacy alias
    module.handle_user_prompt("application mode", REPO_ROOT)
    assert module.load_state(REPO_ROOT)["current_subject"] == module.SUBJECT_APPLICATION

    # GT-KB-side legacy alias
    module.handle_user_prompt("GT-KB mode", REPO_ROOT)
    assert module.load_state(REPO_ROOT)["current_subject"] == module.SUBJECT_GTKB


def test_hook_payload_accepts_claude_prompt_field_for_user_promptsubmit(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "work subject application",
        },
        REPO_ROOT,
    )

    assert "Current work subject set to Application Focus" in response["systemMessage"]
    assert json.loads(canonical.read_text(encoding="utf-8"))["current_subject"] == module.SUBJECT_APPLICATION


def test_hook_payload_accepts_claude_prompt_field_for_startup_gate(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "::init gtkb pb",
        },
        REPO_ROOT,
    )

    assert "(init-keyword match)" in response["systemMessage"]
    assert "first owner message of a fresh session is never actionable" not in response["systemMessage"]
    assert response["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["startup_prompt_discarded"] is True
    assert guard_state["startup_response_pending"] is True
    assert guard_state["startup_prompt_preview"] == "::init gtkb pb"


def test_startup_gate_no_match_passes_prompt_through(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "work subject application",
        },
        REPO_ROOT,
    )

    assert "GTKB STARTUP INPUT GATE" not in response["systemMessage"]
    assert "Current work subject set to Application Focus" in response["systemMessage"]
    assert json.loads(canonical.read_text(encoding="utf-8"))["current_subject"] == module.SUBJECT_APPLICATION
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["startup_prompt_discarded"] is False
    assert guard_state["startup_response_pending"] is False
    assert guard_state["startup_gate_no_match_passed_through"] is True


def test_sessionstart_plus_dispatch_prompt_without_marker_processes_bridge_task(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    dispatch_prompt = """::init gtkb pb

Single-harness bridge dispatcher notification (Slice 2 scheduled task).

This is an automated bridge dispatch from the single-harness dispatcher, not a fresh-session owner stimulus; do not wait for another owner message before processing the selected entries.

Read bridge/INDEX.md directly before acting.
"""

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": dispatch_prompt,
        },
        REPO_ROOT,
    )

    assert "GTKB STARTUP INPUT GATE" not in response["systemMessage"]
    assert "hookSpecificOutput" not in response
    assert "additionalContext" not in json.dumps(response)
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["startup_prompt_discarded"] is False
    assert guard_state["startup_response_pending"] is False
    assert guard_state["startup_gate_no_match_passed_through"] is True
    assert guard_state["startup_prompt_preview"].startswith("::init gtkb pb Single-harness bridge dispatcher")


def test_startup_gate_init_keyword_sets_app_scope(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "init agent_red",
        },
        REPO_ROOT,
    )

    assert "(init-keyword match)" in response["systemMessage"]
    state = json.loads(canonical.read_text(encoding="utf-8"))
    assert state["current_subject"] == module.SUBJECT_APPLICATION
    assert state["application_id"] == "agent_red"
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["current_subject"] == module.SUBJECT_APPLICATION
    assert guard_state["startup_init_app_scope"] == "agent_red"


def _write_startup_gate_guard(tmp_path: Path) -> None:
    """Write a lifecycle guard primed for the init-keyword startup-disclosure gate."""
    (tmp_path / "guard.json").write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _write_relay_cache(
    diagnostics: Path,
    body: str,
    *,
    sha: str | None = None,
    byte_length: int | None = None,
) -> None:
    """Write a harness-scoped startup-disclosure relay cache file + metadata sidecar."""
    diagnostics.mkdir(parents=True, exist_ok=True)
    encoded = body.encode("utf-8")
    diagnostics.joinpath("last-user-visible-startup.md").write_text(body, encoding="utf-8", newline="\n")
    from datetime import datetime

    now_str = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "harness_name": "codex",
        "harness_id": "A",
        "generated_at": now_str,
        "byte_length": byte_length if byte_length is not None else len(encoded),
        "sha256": sha if sha is not None else hashlib.sha256(encoded).hexdigest(),
    }
    diagnostics.joinpath("last-user-visible-startup.meta.json").write_text(
        json.dumps(meta), encoding="utf-8", newline="\n"
    )


def test_startup_gate_emits_bounded_pointer_not_inlined_disclosure(tmp_path, monkeypatch) -> None:
    """T1 -- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001: relay additionalContext is a bounded pointer."""
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    _write_startup_gate_guard(tmp_path)
    disclosure = "# GroundTruth-KB Fresh Session Startup\n\n## Startup Disclosure\n\n" + (
        "disclosure body line\n" * 400
    )
    _write_relay_cache(tmp_path / ".codex" / "gtkb-hooks", disclosure)

    response = module.handle_hook_payload(
        {"hook_event_name": "UserPromptSubmit", "prompt": "init gtkb"},
        tmp_path,
    )
    context = response["hookSpecificOutput"]["additionalContext"]
    encoded_disclosure = disclosure.encode("utf-8")

    assert len(context.encode("utf-8")) < 4096, "relay additionalContext must stay bounded"
    assert ".codex/gtkb-hooks/last-user-visible-startup.md" in context
    assert str(len(encoded_disclosure)) in context
    assert hashlib.sha256(encoded_disclosure).hexdigest() in context
    assert "disclosure body line" not in context, "full disclosure body must not be inlined"
    assert "## Cached User-Visible Startup Message" not in context


def test_startup_gate_message_authorizes_one_read_only_read(tmp_path, monkeypatch) -> None:
    """T2 -- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001: gate wording permits the recovery read."""
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    _write_startup_gate_guard(tmp_path)
    _write_relay_cache(
        tmp_path / ".codex" / "gtkb-hooks", "# GroundTruth-KB Fresh Session Startup\n\n## Startup Disclosure\n\nbody"
    )

    response = module.handle_hook_payload(
        {"hook_event_name": "UserPromptSubmit", "prompt": "init gtkb"},
        tmp_path,
    )
    lowered = response["hookSpecificOutput"]["additionalContext"].lower()

    assert "read-only" in lowered
    assert "verbatim" in lowered
    assert "acknowledgement" in lowered
    assert "do not use tools" not in lowered, "the contradictory blanket tool prohibition must be gone"


def test_startup_gate_does_not_consult_shared_dashboard_report(tmp_path, monkeypatch) -> None:
    """T3 -- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 Finding 3: no shared-report fallback."""
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    _write_startup_gate_guard(tmp_path)
    shared = tmp_path / "docs" / "gtkb-dashboard"
    shared.mkdir(parents=True)
    shared.joinpath("session-startup-report.md").write_text(
        "WRONG-ROLE shared dashboard report content", encoding="utf-8"
    )

    response = module.handle_hook_payload(
        {"hook_event_name": "UserPromptSubmit", "prompt": "init gtkb"},
        tmp_path,
    )
    context = response["hookSpecificOutput"]["additionalContext"]

    assert "WRONG-ROLE shared dashboard report content" not in context
    assert "session-startup-report.md" not in context
    assert "STARTUP RELAY FAILURE" in context, "absent harness-scoped cache must fail visibly"


def test_startup_gate_fails_visibly_on_inconsistent_cache(tmp_path, monkeypatch) -> None:
    """T5 -- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001: a bad cache fails visibly, not silently."""
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    _write_startup_gate_guard(tmp_path)
    _write_relay_cache(
        tmp_path / ".codex" / "gtkb-hooks",
        "# Fresh Session Startup\n\nbody",
        sha="0" * 64,
    )

    response = module.handle_hook_payload(
        {"hook_event_name": "UserPromptSubmit", "prompt": "init gtkb"},
        tmp_path,
    )
    context = response["hookSpecificOutput"]["additionalContext"]

    assert "STARTUP RELAY FAILURE" in context
    assert "do not treat startup as satisfied" in context.lower()


def test_user_promptsubmit_clears_stale_startup_gate_after_startup_stop(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "first_wrapup_suppressed": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
                "suppress_next_wrapup": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.handle_hook_payload(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "work subject application",
        },
        REPO_ROOT,
    )

    assert "first owner message of a fresh session is never actionable" not in response["systemMessage"]
    assert "Current work subject set to Application Focus" in response["systemMessage"]
    assert json.loads(canonical.read_text(encoding="utf-8"))["current_subject"] == module.SUBJECT_APPLICATION
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["stale_startup_gate_cleared"] is True
    assert guard_state["stale_startup_gate_reason"] == "startup_stop_already_suppressed"
    assert guard_state["startup_prompt_preview"] == "work subject application"


def test_prompt_hook_accepts_bom_prefixed_stdin_from_windows_pipeline(tmp_path) -> None:
    state_path = tmp_path / "focus.json"
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    env = {
        **dict(os.environ),
        "GTKB_WORKSTREAM_FOCUS_STATE": str(state_path),
        "GTKB_LIFECYCLE_GUARD_PATH": str(guard_path),
        "CLAUDE_PROJECT_DIR": str(REPO_ROOT),
    }

    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        cwd=REPO_ROOT,
        env=env,
        input=("\ufeff" + json.dumps({"prompt": "::init gtkb pb", "hook_event_name": "UserPromptSubmit"})).encode(
            "utf-8"
        ),
        capture_output=True,
        timeout=10,
        check=True,
    )

    response = json.loads(result.stdout.decode("utf-8"))
    assert "(init-keyword match)" in response["systemMessage"]
    assert "first owner message of a fresh session is never actionable" not in response["systemMessage"]
    assert json.loads(guard_path.read_text(encoding="utf-8"))["startup_response_pending"] is True


@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN-3")
def test_prompt_hook_switches_focus_with_standalone_commands(tmp_path) -> None:
    state_path = tmp_path / "focus.json"

    response = _run_hook({"user_prompt": "GT-KB mode"}, state_path)
    assert "GT-KB Infrastructure Focus" in response["systemMessage"]
    assert json.loads(state_path.read_text(encoding="utf-8"))["current_focus"] == "gtkb_infrastructure"

    response = _run_hook({"user_prompt": "please application mode."}, state_path)
    assert "Application Focus" in response["systemMessage"]
    assert json.loads(state_path.read_text(encoding="utf-8"))["current_focus"] == "application"


def test_prompt_hook_toggles_next_session_role_with_simple_phrase(tmp_path, monkeypatch) -> None:
    module = _load_module()
    # WI-3342 IP-6: the role-toggle path persists to the DB-backed registry; an
    # isolated groundtruth.db + projection is seeded under tmp_path and tmp_path
    # is passed as project_root so the real registry is never mutated.
    _seed_registry(
        tmp_path,
        {"A": ("codex", ["loyal-opposition"]), "B": ("claude", ["prime-builder"])},
    )
    _copy_parity_registry(tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("switch mode next session", tmp_path)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    assert "Harness parity after role change:" in response["systemMessage"]
    # Role-set wire form per IP-8 of gtkb-single-harness-bridge-dispatcher-001:
    # WRITE always emits JSON list; singleton represents the multi-harness case.
    # WI-3342 IP-5: the post-write role surface is the registry projection.
    assert _projection_role(tmp_path, "A") == ["prime-builder"]
    assert _projection_role(tmp_path, "B") == ["loyal-opposition"]

    response = module.handle_user_prompt("please change mode next session.", tmp_path)

    assert "Next fresh-session operating mode set to Loyal Opposition" in response["systemMessage"]
    assert _projection_role(tmp_path, "A") == ["loyal-opposition"]


def test_prompt_hook_sets_explicit_next_session_role(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _seed_registry(
        tmp_path,
        {"A": ("codex", ["loyal-opposition"]), "B": ("claude", ["prime-builder"])},
    )
    _copy_parity_registry(tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("prime builder mode next session", tmp_path)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    assert _projection_role(tmp_path, "A") == ["prime-builder"]
    assert _projection_role(tmp_path, "B") == ["loyal-opposition"]


def test_prompt_hook_uses_harness_id_role_map_when_named(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _seed_registry(
        tmp_path,
        {"A": ("codex", ["loyal-opposition"]), "B": ("claude", ["prime-builder"])},
    )
    _copy_parity_registry(tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("switch mode next session", tmp_path)

    assert "Next fresh-session operating mode set to Prime Builder" in response["systemMessage"]
    # The message names the role-map file path the operating-role command
    # updates and the durable harness id it applies to.
    role_path_display = module.operating_role_path(tmp_path)
    try:
        expected_path = role_path_display.relative_to(tmp_path.resolve()).as_posix()
    except ValueError:
        expected_path = str(role_path_display)
    assert expected_path in response["systemMessage"]
    assert "harness `A`" in response["systemMessage"]
    assert _projection_role(tmp_path, "A") == ["prime-builder"]


def test_prompt_hook_toggles_dashboard_auto_launch(tmp_path, monkeypatch) -> None:
    module = _load_module()
    preferences_path = tmp_path / "session-startup-preferences.json"
    monkeypatch.setenv("GTKB_STARTUP_PREFERENCES_PATH", str(preferences_path))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "guard.json"))

    response = module.handle_user_prompt("enable dashboard", REPO_ROOT)

    assert "Dashboard auto-launch is enabled" in response["systemMessage"]
    assert json.loads(preferences_path.read_text(encoding="utf-8"))["open_dashboard_on_session_start"] is True

    response = module.handle_user_prompt("disable dashboard", REPO_ROOT)

    assert "Dashboard auto-launch is disabled" in response["systemMessage"]
    assert json.loads(preferences_path.read_text(encoding="utf-8"))["open_dashboard_on_session_start"] is False


@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN-3")
def test_prompt_hook_discards_first_fresh_session_message_when_startup_gate_is_armed(tmp_path) -> None:
    state_path = tmp_path / "focus.json"
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": True,
                "startup_guard_id": "test-guard",
                "startup_response_pending": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = _run_hook({"user_prompt": "Please resume."}, state_path, guard_path=guard_path)

    assert "first owner message of a fresh session is never actionable" in response["systemMessage"]
    assert response["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert (
        "startup disclosure already generated for this session" in response["hookSpecificOutput"]["additionalContext"]
    )

    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["discard_next_user_prompt"] is False
    assert guard_state["startup_prompt_discarded"] is True
    assert guard_state["startup_response_pending"] is True
    assert guard_state["startup_prompt_preview"] == "Please resume."


@pytest.mark.skip(reason="workstream-focus.py intentionally retired S304/S305; see REVISED-5 BN-3")
def test_startup_response_pending_clears_on_next_owner_prompt_and_allows_normal_processing(tmp_path) -> None:
    state_path = tmp_path / "focus.json"
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": False,
                "startup_guard_id": "test-guard",
                "startup_prompt_discarded": True,
                "startup_response_pending": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = _run_hook({"user_prompt": "GT-KB mode"}, state_path, guard_path=guard_path)

    assert "GT-KB Infrastructure Focus" in response["systemMessage"]
    assert json.loads(state_path.read_text(encoding="utf-8"))["current_focus"] == "gtkb_infrastructure"
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["startup_response_pending"] is False
    assert guard_state["startup_input_gate_cleared_at"]


def test_classify_root_4_categories(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    gtkb_dir = tmp_path / "groundtruth-kb"
    (gtkb_dir / "src" / "groundtruth_kb").mkdir(parents=True)
    monkeypatch.setenv("GTKB_PRODUCT_ROOT", str(gtkb_dir))

    gtkb_target = gtkb_dir / "src" / "groundtruth_kb" / "foo.py"
    assert module.classify_root(str(gtkb_target), REPO_ROOT) == module.ROOT_GTKB_PRODUCT
    assert module.classify_root("src/example.py", REPO_ROOT) == module.ROOT_APPLICATION_PRODUCT
    assert module.classify_root(".claude/rules/new-rule.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    assert (
        module.classify_root("bridge/some-proposal-001.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    )
    assert module.classify_root("AGENTS.md", REPO_ROOT) == module.ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE
    assert module.classify_root("README.md", REPO_ROOT) == module.ROOT_NEUTRAL


def test_application_subject_blocks_gtkb_product_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

    gtkb_dir = tmp_path / "groundtruth-kb"
    (gtkb_dir / "src" / "groundtruth_kb").mkdir(parents=True)
    monkeypatch.setenv("GTKB_PRODUCT_ROOT", str(gtkb_dir))

    gtkb_target = gtkb_dir / "src" / "groundtruth_kb" / "foo.py"
    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": str(gtkb_target)}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "Current work subject is application" in response["reason"]
    assert "work subject GT-KB" in response["reason"]
    assert "GT-KB product artifacts" in response["reason"]


def test_application_subject_allows_current_repo_bridge_or_governance_write(tmp_path, monkeypatch) -> None:
    """Phase 7 relaxation: current-repo bridge/governance paths are NOT blocked under application subject."""

    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response == {}


def test_application_subject_allows_application_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response == {}


def test_gtkb_subject_blocks_application_product_write(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "Current work subject is GT-KB" in response["reason"]
    assert "work subject application" in response["reason"]
    assert "application product artifacts" in response["reason"]


def test_gtkb_subject_allows_current_repo_bridge_or_governance_write(tmp_path, monkeypatch) -> None:
    """Phase 7: current-repo bridge/governance is allowed in BOTH subjects."""

    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_GTKB_INFRASTRUCTURE, REPO_ROOT)

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response == {}


def test_startup_response_pending_blocks_tool_use_until_next_owner_prompt(tmp_path, monkeypatch) -> None:
    module = _load_module()
    guard_path = tmp_path / "guard.json"
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(guard_path))
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": False,
                "startup_prompt_discarded": True,
                "startup_response_pending": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": "src/example.py"}},
        REPO_ROOT,
    )

    assert response["decision"] == "block"
    assert "GTKB-STARTUP-INPUT-GATE" in response["reason"]
    assert "startup disclosure has been emitted" in response["reason"]
    assert "init-keyword contract" in response["reason"]
    assert "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001" in response["reason"]
    assert "first owner message of this fresh session was discarded" not in response["reason"]


def test_stale_startup_response_pending_does_not_block_later_tool_use(tmp_path, monkeypatch) -> None:
    module = _load_module()
    guard_path = tmp_path / "guard.json"
    monkeypatch.setenv("GTKB_WORKSTREAM_FOCUS_STATE", str(tmp_path / "focus.json"))
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(guard_path))
    guard_path.write_text(
        json.dumps(
            {
                "discard_next_user_prompt": False,
                "startup_prompt_discarded": True,
                "startup_prompt_discarded_at": "2026-01-01T00:00:00Z",
                "startup_response_pending": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = module.guard_tool_use(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rules/new-rule.md"}},
        REPO_ROOT,
    )

    assert response == {}
    guard_state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert guard_state["startup_response_pending"] is False
    assert guard_state["stale_startup_response_pending_cleared"] is True


def test_bash_guard_only_blocks_mutating_gtkb_product_commands(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT)

    gtkb_dir = tmp_path / "groundtruth-kb"
    (gtkb_dir / "src" / "groundtruth_kb").mkdir(parents=True)
    monkeypatch.setenv("GTKB_PRODUCT_ROOT", str(gtkb_dir))

    # Read commands touching bridge/governance surfaces should not block.
    read_response = module.guard_tool_use(
        {"tool_name": "Bash", "tool_input": {"command": "Get-Content .claude/rules/prime-builder-role.md"}},
        REPO_ROOT,
    )
    assert read_response == {}

    # Mutations to bridge/governance are NOT blocked (Phase 7 relaxation).
    governance_write_response = module.guard_tool_use(
        {
            "tool_name": "Bash",
            "tool_input": {"command": "Set-Content .claude/rules/new-rule.md 'text'"},
        },
        REPO_ROOT,
    )
    assert governance_write_response == {}

    # Mutations to GT-KB product paths ARE blocked under application subject.
    gtkb_target = (gtkb_dir / "src" / "groundtruth_kb" / "foo.py").as_posix()
    gtkb_write_response = module.guard_tool_use(
        {
            "tool_name": "Bash",
            "tool_input": {"command": f"Set-Content {gtkb_target} 'text'"},
        },
        REPO_ROOT,
    )
    assert gtkb_write_response["decision"] == "block"
    assert "work subject GT-KB" in gtkb_write_response["reason"]


# ---- GTKB-ISOLATION-015 Slice 1 §A / §C / §E regression coverage ----------


def test_startup_focus_lines_include_role_slot_topology_mode_init_keyword_and_bridge_authority(
    tmp_path, monkeypatch
) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)

    snapshot = module.startup_focus_snapshot(REPO_ROOT)
    lines = module.render_startup_focus_lines(snapshot)

    assert snapshot["role_slot"] == module.ROLE_SLOT_DEFAULT
    assert snapshot["topology_mode"] == module.TOPOLOGY_MODE_DEFAULT
    assert "Bridge role slot:" in lines
    assert module.ROLE_SLOT_DEFAULT in lines
    assert "Harness topology:" in lines
    assert module.TOPOLOGY_MODE_SINGLE in lines
    assert "First owner message" in lines
    assert "init-keyword matcher" in lines
    assert "bridge/INDEX.md" in lines
    assert "canonical handoff/review" in lines


def test_save_state_persists_topology_mode_default(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)

    # WI-3342 IP-4: save_state derives topology_mode from the registry
    # projection via load_role_assignments. With no registry under the
    # (isolated) tmp_path project root, derivation finds no harnesses and
    # save_state keeps the canonical default topology mode.
    module.save_state(module.FOCUS_APPLICATION, tmp_path, updated_by="owner_prompt")
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert data["topology_mode"] == module.TOPOLOGY_MODE_SINGLE


def test_overlay_startup_note_absent_is_informational(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    note = module.overlay_startup_note({"overlay_present": False})
    assert note["level"] == "info"
    assert any("No session overlay active" in line for line in note["lines"])
    assert not any(line.startswith("WARNING") for line in note["lines"])


def test_overlay_startup_note_stale_is_warning(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    note = module.overlay_startup_note({"overlay_present": True, "is_stale": True})
    assert note["level"] == "warning"
    assert any("stale" in line for line in note["lines"])
    assert any(line.startswith("WARNING") for line in note["lines"])


def test_overlay_startup_note_root_mismatch_is_warning() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "root_mismatch": True})
    assert note["level"] == "warning"
    assert any("different project root" in line for line in note["lines"])


def test_overlay_startup_note_subject_mismatch_is_warning() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "subject_mismatch": True})
    assert note["level"] == "warning"
    assert any("work subject differs" in line for line in note["lines"])


def test_overlay_startup_note_projection_diff_is_warning() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "projection_diff": True})
    assert note["level"] == "warning"
    assert any("projection differs" in line for line in note["lines"])


def test_overlay_startup_note_never_canonical_phrasing() -> None:
    module = _load_module()
    note = module.overlay_startup_note({"overlay_present": True, "is_stale": True})
    joined = " ".join(note["lines"])
    assert "never canonical" in joined
    assert "Deliberation Archive" in joined


def test_detect_counterpart_state_no_counterpart_files_no_warning(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    result = module.detect_counterpart_state()
    assert result["warnings"] == []
    assert result["counterpart_present"] is False


# WI-3342 IP-6 — KNOWN PRODUCTION REGRESSION (reported, not fixed here).
#
# The two tests below are written correctly against the migrated registry
# projection, but they expose a genuine production defect introduced by the
# WI-3342 IP-3 migration of ``scripts/harness_roles.py::load_role_assignments``:
#
#   * Pre-migration, ``load_role_assignments`` returned each harness record as
#     a FULL dict (``dict(raw_record)``), preserving ``harness_type``.
#   * Post-migration, it returns a MINIMAL ``{"role": [...]}`` record
#     (harness_roles.py lines ~248-252) — ``harness_type`` is dropped.
#   * ``detect_counterpart_state`` (scripts/workstream_focus.py line ~909)
#     still keys ``per_harness_role_sets`` by ``record.get("harness_type")``,
#     which is now always ``None`` -> the map is keyed by harness ID (A/B).
#   * ``counterpart_present`` (line ~912-914) tests membership against
#     ``DEFAULT_HARNESS_IDS`` KEYS (harness names ``codex``/``claude``), which
#     never match the ID-keyed map -> ``counterpart_present`` is always False
#     and ``same_role_slot`` never fires.
#
# Net effect: counterpart role-collision warnings silently never fire. This is
# a production fix (workstream_focus.py should resolve harness names from the
# registry projection, e.g. via load_harness_projection / harness_name, rather
# than relying on the now-stripped harness_type), out of scope for this
# test-only WI-3342 IP-6 work item. xfail keeps the correct test in place and
# will xpass — flagging the marker for removal — once production is fixed.
_COUNTERPART_HARNESS_TYPE_REGRESSION = (
    "WI-3342 IP-3 production regression: load_role_assignments no longer "
    "returns harness_type, so detect_counterpart_state keys per_harness_role_sets "
    "by harness ID and counterpart_present (compared vs harness names) is always "
    "False. Production fix required in scripts/workstream_focus.py; out of scope "
    "for the test-only WI-3342 IP-6 work item."
)


@pytest.mark.xfail(reason=_COUNTERPART_HARNESS_TYPE_REGRESSION, strict=True)
def test_detect_counterpart_state_same_role_warns(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    # WI-3342 IP-4: detect_counterpart_state resolves the role map from the
    # registry projection; seed it under tmp_path and pass tmp_path as the
    # project root so the read is isolated from the real harness-state.
    _write_registry_projection(
        tmp_path,
        {"A": ("codex", "prime-builder"), "B": ("claude", "prime-builder")},
    )
    result = module.detect_counterpart_state(tmp_path)
    assert result["same_role_slot"] is True
    assert result["counterpart_present"] is True
    assert any("prime-builder" in msg and "collide" in msg for msg in result["warnings"])


@pytest.mark.xfail(reason=_COUNTERPART_HARNESS_TYPE_REGRESSION, strict=True)
def test_detect_counterpart_state_different_role_warns(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    # WI-3342 IP-4: role map resolved from the registry projection.
    _write_registry_projection(
        tmp_path,
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    result = module.detect_counterpart_state(tmp_path)
    assert result["same_role_slot"] is False
    assert result["counterpart_present"] is True
    assert any("prime-builder" in msg and "loyal-opposition" in msg for msg in result["warnings"])


def test_detect_counterpart_state_subject_mismatch_warns(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_guard.parent.mkdir(parents=True, exist_ok=True)
    claude_guard.parent.mkdir(parents=True, exist_ok=True)
    codex_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_GTKB_INFRASTRUCTURE}) + "\n",
        encoding="utf-8",
    )
    claude_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_APPLICATION}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = module.detect_counterpart_state()
    assert result["subject_mismatch"] is True
    assert any(
        module.FOCUS_GTKB_INFRASTRUCTURE in msg and module.FOCUS_APPLICATION in msg for msg in result["warnings"]
    )


def test_detect_counterpart_state_subject_mismatch_symmetric_from_codex_side(tmp_path, monkeypatch) -> None:
    """Symmetric §E regression (bridge -014 P1).

    Reproduces the live asymmetry Codex demonstrated: Codex on
    gtkb_infrastructure, Claude on application, shared canonical set to
    application. Before -014's fix, detect_counterpart_state() with
    GTKB_HARNESS_NAME=codex read our_subject from the shared canonical
    (application), compared against counterpart Claude guard (application),
    and returned subject_mismatch=False — silently missing the split.

    After the fix, our_subject is read from our own harness guard first, so
    Codex sees our_subject=gtkb_infrastructure and correctly warns.
    """
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "prime-builder"), "B": ("claude", "loyal-opposition")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_guard.parent.mkdir(parents=True, exist_ok=True)
    claude_guard.parent.mkdir(parents=True, exist_ok=True)
    # Codex harness's own guard says gtkb_infrastructure.
    codex_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_GTKB_INFRASTRUCTURE}) + "\n",
        encoding="utf-8",
    )
    # Claude's guard says application — matches shared canonical.
    claude_guard.write_text(
        json.dumps({"current_subject": module.FOCUS_APPLICATION}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    # Shared canonical is application (what Claude last wrote). If the old
    # implementation read our_subject from this file, it would compare
    # application (ours) against application (claude's guard) and miss.
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = module.detect_counterpart_state()
    assert result["subject_mismatch"] is True, (
        "Codex-side must detect subject divergence against Claude's guard; "
        "pre-fix behavior silently missed this because our_subject came from "
        "the shared canonical instead of codex's own guard."
    )
    assert any(
        module.FOCUS_GTKB_INFRASTRUCTURE in msg and module.FOCUS_APPLICATION in msg for msg in result["warnings"]
    )


def test_detect_counterpart_state_subject_match_no_warning(tmp_path, monkeypatch) -> None:
    module = _load_module()
    canonical, _ = _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"A": ("codex", "loyal-opposition"), "B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    codex_guard = tmp_path / ".codex" / "session-lifecycle-guard.json"
    claude_guard = tmp_path / ".claude" / "session-lifecycle-guard.json"
    codex_guard.parent.mkdir(parents=True, exist_ok=True)
    claude_guard.parent.mkdir(parents=True, exist_ok=True)
    for guard in (codex_guard, claude_guard):
        guard.write_text(
            json.dumps({"current_subject": module.FOCUS_APPLICATION}) + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(
        module,
        "HARNESS_LIFECYCLE_GUARDS",
        {"codex": codex_guard, "claude": claude_guard},
    )
    module.save_state(module.FOCUS_APPLICATION, REPO_ROOT, updated_by="owner_prompt")

    result = module.detect_counterpart_state()
    assert result["subject_mismatch"] is False
    assert not any("work subject" in msg for msg in result["warnings"])


def test_detect_counterpart_state_missing_counterpart_no_crash(tmp_path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))
    result = module.detect_counterpart_state()
    assert result["counterpart_present"] is False
    assert result["warnings"] == []


def test_render_active_work_subject_combines_focus_overlay_and_counterpart(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _isolate_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    role_map = _write_role_map(
        tmp_path / "role-assignments.json",
        {"B": ("claude", "prime-builder")},
    )
    monkeypatch.setenv("GTKB_ROLE_ASSIGNMENTS_PATH", str(role_map))

    rendered = module.render_active_work_subject(
        REPO_ROOT,
        overlay_status={"overlay_present": False},
    )
    assert "Active Work Subject" not in rendered  # heading is rendered by caller
    assert "Bridge role slot:" in rendered
    assert "No session overlay active" in rendered


def test_assert_readiness_subject_scope_hard_rejects_unlabeled_combined_green() -> None:
    module = _load_module()
    with pytest.raises(module.SubjectScopeError, match="combined application \\+ GT-KB"):
        module.assert_readiness_subject_scope(application_green=True, gtkb_green=True, dual_scope_declared=False)


def test_assert_readiness_subject_scope_permits_dual_scope_declaration() -> None:
    module = _load_module()
    module.assert_readiness_subject_scope(application_green=True, gtkb_green=True, dual_scope_declared=True)


def test_harness_state_records_for_project_returns_sandbox_relative_paths(tmp_path) -> None:
    module = _load_module()
    sandbox = tmp_path / "sandbox"
    role_assignment_path, lifecycle_guards = module._harness_state_records_for_project(sandbox)

    assert role_assignment_path == sandbox / "harness-state" / "role-assignments.json"
    assert lifecycle_guards["codex"] == sandbox / "harness-state" / "codex" / "session-lifecycle-guard.json"
    assert lifecycle_guards["claude"] == sandbox / "harness-state" / "claude" / "session-lifecycle-guard.json"
    assert role_assignment_path != module.PROJECT_ROOT / "harness-state" / "role-assignments.json"
    assert lifecycle_guards["codex"] != module.HARNESS_LIFECYCLE_GUARDS["codex"]


def test_detect_counterpart_state_uses_project_root_paths_when_provided(tmp_path, monkeypatch) -> None:
    """Per bridge/harness-state-preferences-path-cli-2026-04-28-005.md class-level fix.

    When detect_counterpart_state is called with a sandbox project_root, it
    must read the sandbox role-assignment map, not the canonical map.
    """
    module = _load_module()
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    recorded_paths: list[Path] = []

    def _fake_load(project_root: Path, assignment_path: Path | None = None) -> dict:
        recorded_paths.append(assignment_path or project_root / "harness-state" / "role-assignments.json")
        return {"harnesses": {}}

    monkeypatch.setattr(module, "load_role_assignments", _fake_load)
    monkeypatch.setattr(module, "_read_counterpart_subject", lambda _path: None)

    module.detect_counterpart_state(sandbox)

    assert recorded_paths, "expected detect_counterpart_state to load role assignments"
    canonical_root = module.PROJECT_ROOT
    for path in recorded_paths:
        assert sandbox in path.parents, (
            f"role assignment path {path!r} should be under sandbox {sandbox!r} but is not — class-level fix regressed"
        )
        assert canonical_root not in path.parents, (
            f"role assignment path {path!r} should NOT be under canonical "
            f"PROJECT_ROOT {canonical_root!r} — class-level fix regressed"
        )


def test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted(tmp_path, monkeypatch) -> None:
    module = _load_module()
    recorded_paths: list[Path] = []

    def _fake_load(project_root: Path, assignment_path: Path | None = None) -> dict:
        recorded_paths.append(assignment_path or project_root / "harness-state" / "role-assignments.json")
        return {"harnesses": {}}

    monkeypatch.setattr(module, "load_role_assignments", _fake_load)
    monkeypatch.setattr(module, "_read_counterpart_subject", lambda _path: None)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(module.PROJECT_ROOT))

    module.detect_counterpart_state()  # no project_root arg

    assert recorded_paths, "expected detect_counterpart_state to load role assignments"
    assert recorded_paths == [module.PROJECT_ROOT / "harness-state" / "role-assignments.json"]


def test_assert_readiness_subject_scope_permits_single_green() -> None:
    module = _load_module()
    module.assert_readiness_subject_scope(application_green=True, gtkb_green=False, dual_scope_declared=False)
    module.assert_readiness_subject_scope(application_green=False, gtkb_green=True, dual_scope_declared=False)

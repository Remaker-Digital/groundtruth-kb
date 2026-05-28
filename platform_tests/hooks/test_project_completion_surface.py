"""Tests for the project-completion-surface UserPromptSubmit hook, exercising
BOTH the Claude and Codex parity hook files.

W1 of GTKB-GOVERNANCE-CORRECTION-S358 (WI-3365): under
GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 the hook is the automatic-
transition trigger. On each UserPromptSubmit it auto-completes every project
authorization whose membership-linked work items are all VERIFIED, retires the
project when sole-active, and emits a notification - with no AskUserQuestion
instruction. Uses isolated tmp_path project roots; the hook resolves its root
from GTKB_PROJECT_ROOT.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOK = REPO_ROOT / ".claude" / "hooks" / "project-completion-surface.py"
CODEX_HOOK = REPO_ROOT / ".codex" / "gtkb-hooks" / "project-completion-surface.py"


def _seed(project_root: Path, authorizations: dict[str, dict[str, bool]]) -> None:
    """Seed a project root. ``authorizations`` maps authorization id ->
    {work_item_id: bridge-thread-is-VERIFIED}.

    GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 gates completion on the
    project's active project-to-work-item membership links; every seeded work
    item is linked to PROJECT-X via ``link_project_work_item()``.
    """
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    wi_verified: dict[str, bool] = {}
    for wi_map in authorizations.values():
        wi_verified.update(wi_map)
    index_lines = ["# Bridge Index", ""]
    for index, (wi, verified) in enumerate(sorted(wi_verified.items())):
        slug = f"gtkb-thread-{index}"
        top_status = "VERIFIED" if verified else "GO"
        (bridge / f"{slug}-001.md").write_text(f"# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8")
        index_lines += [f"Document: {slug}", f"{top_status}: bridge/{slug}-001.md", ""]
    (bridge / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED",
            "owner_conversation",
            "Owner approved",
            "Owner approved the seed authorizations.",
            "{}",
            "test",
            "seed",
            outcome="owner_decision",
        )
        db.insert_project("Surface Project", "test", "seed", id="PROJECT-X", status="active")
        db.insert_spec(
            id="SPEC-SEED",
            title="Seed spec",
            status="verified",
            changed_by="test",
            change_reason="seed",
        )
        for wi in wi_verified:
            db.insert_work_item(wi, f"Work item {wi}", "new", "backlog", "open", "test", "seed")
            db.link_project_work_item("PROJECT-X", wi, "test", "seed")
        for auth_id, wi_map in authorizations.items():
            db.insert_project_authorization(
                "PROJECT-X",
                f"Authorization {auth_id}",
                "DELIB-SEED",
                "Bounded scope.",
                "test",
                "seed",
                id=auth_id,
                status="active",
                included_work_item_ids=list(wi_map),
                included_spec_ids=["SPEC-SEED"],
            )
    finally:
        db.close()


def _load_hook(hook_path: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Load a hook file fresh with PROJECT_ROOT bound to ``project_root``."""
    monkeypatch.setenv("GTKB_PROJECT_ROOT", str(project_root))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    mod_name = f"_pcs_hook_{abs(hash((str(hook_path), str(project_root)))) & 0xFFFFFF}"
    spec = importlib.util.spec_from_file_location(mod_name, hook_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def _authorization_status(project_root: Path, authorization_id: str) -> str:
    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        return str(db.get_project_authorization(authorization_id)["status"])
    finally:
        db.close()


def _project_status(project_root: Path, project_id: str) -> str:
    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        return str(db.get_project(project_id)["status"])
    finally:
        db.close()


def test_claude_hook_auto_completes_and_retires(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    output = hook._user_prompt_handler()
    assert "PAUTH-X" in output
    assert "Auto-Completed" in output
    assert _authorization_status(tmp_path, "PAUTH-X") == "completed"
    assert _project_status(tmp_path, "PROJECT-X") == "retired"


def test_codex_hook_auto_completes_and_retires(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}})
    hook = _load_hook(CODEX_HOOK, tmp_path, monkeypatch)
    output = hook._user_prompt_handler()
    assert "PAUTH-X" in output
    assert "Auto-Completed" in output
    assert _authorization_status(tmp_path, "PAUTH-X") == "completed"
    assert _project_status(tmp_path, "PROJECT-X") == "retired"


def test_hook_notification_omits_owner_confirmation_language(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    output = hook._user_prompt_handler()
    assert output != ""
    assert "AskUserQuestion" not in output
    assert "Do NOT auto-transition" not in output
    assert "no action is required" in output


def test_hook_silent_when_no_completion_ready_authorization(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": False}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    assert hook._user_prompt_handler() == ""
    assert _authorization_status(tmp_path, "PAUTH-X") == "active"

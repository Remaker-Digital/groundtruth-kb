"""Tests for the project-completion-surface UserPromptSubmit hook (IP-2 of
WI-3316), exercising BOTH the Claude and Codex parity hook files.

Bridge thread gtkb-project-verified-completion-auq-trigger. Uses isolated
tmp_path project roots; the hook resolves its root from GTKB_PROJECT_ROOT.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_PATH = REPO_ROOT / "scripts" / "project_verified_completion_scanner.py"
CLAUDE_HOOK = REPO_ROOT / ".claude" / "hooks" / "project-completion-surface.py"
CODEX_HOOK = REPO_ROOT / ".codex" / "gtkb-hooks" / "project-completion-surface.py"


def _seed(project_root: Path, authorizations: dict[str, dict[str, bool]]) -> None:
    """Seed a project root. ``authorizations`` maps authorization id ->
    {work_item_id: bridge-thread-is-VERIFIED}."""
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    # one bridge thread per distinct WI
    wi_verified: dict[str, bool] = {}
    for wi_map in authorizations.values():
        wi_verified.update(wi_map)
    index_lines = ["# Bridge Index", ""]
    for index, (wi, verified) in enumerate(sorted(wi_verified.items())):
        slug = f"gtkb-thread-{index}"
        top_status = "VERIFIED" if verified else "GO"
        (bridge / f"{slug}-001.md").write_text(
            f"# Proposal {slug}\n\nWork Item: {wi}\n", encoding="utf-8"
        )
        index_lines += [f"Document: {slug}", f"{top_status}: bridge/{slug}-001.md", ""]
    (bridge / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    # the hook imports the scanner from <root>/scripts/
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCANNER_PATH, scripts_dir / SCANNER_PATH.name)

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED", "owner_conversation", "Owner approved",
            "Owner approved the seed authorizations.", "{}", "test", "seed",
            outcome="owner_decision",
        )
        db.insert_project("Surface Project", "test", "seed", id="PROJECT-X", status="active")
        db.insert_spec(
            id="SPEC-SEED", title="Seed spec", status="verified",
            changed_by="test", change_reason="seed",
        )
        for wi in wi_verified:
            db.insert_work_item(wi, f"Work item {wi}", "new", "backlog", "open", "test", "seed")
        for auth_id, wi_map in authorizations.items():
            db.insert_project_authorization(
                "PROJECT-X", f"Authorization {auth_id}", "DELIB-SEED",
                "Bounded scope.", "test", "seed", id=auth_id, status="active",
                included_work_item_ids=list(wi_map), included_spec_ids=["SPEC-SEED"],
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


def _payload(session_id: str = "session-1") -> str:
    return json.dumps({"session_id": session_id, "prompt": "continue work"})


def test_hook_surfaces_one_authorization_per_prompt(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}, "PAUTH-Y": {"WI-8002": True}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    output = hook._user_prompt_handler(_payload())
    assert "PAUTH-X" in output  # oldest (project/id-sorted) first
    assert "PAUTH-Y" not in output


def test_hook_does_not_resurface_same_authorization_same_session(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    first = hook._user_prompt_handler(_payload("session-1"))
    second = hook._user_prompt_handler(_payload("session-1"))
    assert "PAUTH-X" in first
    assert second == ""


def test_claude_hook_surfaces_completion_ready_authorization(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    output = hook._user_prompt_handler(_payload())
    assert "PAUTH-X" in output
    assert "AskUserQuestion" in output


def test_codex_hook_surfaces_completion_ready_authorization(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": True}})
    hook = _load_hook(CODEX_HOOK, tmp_path, monkeypatch)
    output = hook._user_prompt_handler(_payload())
    assert "PAUTH-X" in output
    assert "AskUserQuestion" in output


def test_hook_silent_when_no_completion_ready_authorization(tmp_path, monkeypatch):
    _seed(tmp_path, {"PAUTH-X": {"WI-8001": False}})
    hook = _load_hook(CLAUDE_HOOK, tmp_path, monkeypatch)
    assert hook._user_prompt_handler(_payload()) == ""

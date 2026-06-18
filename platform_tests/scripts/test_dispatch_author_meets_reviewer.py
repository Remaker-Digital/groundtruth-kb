from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cross_harness_bridge_trigger as cht  # noqa: E402


def _write_project(root: Path) -> Path:
    (root / "groundtruth.toml").write_text('[project]\nproject_name = "test"\n', encoding="utf-8")
    (root / "bridge").mkdir(exist_ok=True)
    harness_state = root / "harness-state"
    harness_state.mkdir(exist_ok=True)

    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "claude": {"id": "B"},
                    "codex": {"id": "A"},
                    "ollama": {"id": "D"},
                },
            }
        ),
        encoding="utf-8",
    )

    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["prime-builder"],
                        "invocation_surfaces": {"headless": {"argv": ["codex"]}},
                    },
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["loyal-opposition"],
                        "invocation_surfaces": {"headless": {"argv": ["ollama"]}},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root


def test_should_refuse_self_review_returns_true_when_author_session_matches_reviewer_session(tmp_path: Path) -> None:
    root = _write_project(tmp_path)
    bridge_id = "test-doc"
    (root / "bridge" / f"gtkb-{bridge_id}-001.md").write_text(
        "author_harness_id: D\nauthor_session_context_id: session-D\n# content\n",
        encoding="utf-8",
    )
    res = cht._should_refuse_self_review(bridge_id, "session-D", root)
    assert res is True


def test_should_refuse_self_review_returns_false_when_same_harness_different_session(tmp_path: Path) -> None:
    root = _write_project(tmp_path)
    bridge_id = "test-doc"
    (root / "bridge" / f"gtkb-{bridge_id}-001.md").write_text(
        "author_harness_id: D\nauthor_session_context_id: author-session\n# content\n",
        encoding="utf-8",
    )
    res = cht._should_refuse_self_review(bridge_id, "reviewer-session", root)
    assert res is False


def test_should_refuse_self_review_fails_closed_when_author_session_metadata_missing(tmp_path: Path) -> None:
    root = _write_project(tmp_path)
    bridge_id = "test-doc"
    (root / "bridge" / f"gtkb-{bridge_id}-001.md").write_text("# content\n", encoding="utf-8")
    res = cht._should_refuse_self_review(bridge_id, "reviewer-session", root)
    assert res is True


def test_dispatch_emits_author_meets_reviewer_refused_diagnostic_record_on_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    root = _write_project(tmp_path)
    state_dir = tmp_path / "state"

    bridge_id = "test-self-review"
    (root / "bridge" / f"gtkb-{bridge_id}-001.md").write_text(
        "NEW\n\nauthor_harness_id: D\nauthor_session_context_id: dispatch-session-1\n# content\n",
        encoding="utf-8",
    )
    (root / "bridge" / "INDEX.md").write_text(
        f"Document: {bridge_id}\nNEW: bridge/gtkb-{bridge_id}-001.md\n", encoding="utf-8"
    )

    monkeypatch.setattr(cht, "_is_cross_harness_trigger_active_substrate", lambda root: True)
    monkeypatch.setattr(cht, "_is_single_harness_topology", lambda root: False)
    monkeypatch.setattr(cht, "_evaluate_ollama_dispatch_readiness", lambda root: {"ready": True})
    monkeypatch.setattr(cht, "_new_dispatch_id", lambda recipient_key: "dispatch-session-1")

    summary = cht.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    assert summary["results"]["loyal-opposition"]["reason"] == "author_meets_reviewer_refused"

    # Verify dispatch state file was written with last_result
    state_file = state_dir / "dispatch-state.json"
    assert state_file.is_file()
    state_data = json.loads(state_file.read_text(encoding="utf-8"))
    assert state_data["recipients"]["loyal-opposition"]["last_result"] == "author_meets_reviewer_refused"

    # Verify trigger-diagnostic.jsonl has a record
    diag_file = state_dir / "trigger-diagnostic.jsonl"
    assert diag_file.is_file()
    diag_lines = diag_file.read_text(encoding="utf-8").splitlines()
    assert len(diag_lines) > 0
    lo_diags = [json.loads(line) for line in diag_lines if json.loads(line).get("recipient") == "loyal-opposition"]
    assert len(lo_diags) > 0
    lo_diag = lo_diags[-1]
    assert lo_diag["last_result"] == "author_meets_reviewer_refused"
    assert lo_diag["classification"] == "author_meets_reviewer_refused"


def test_dispatch_fails_closed_when_author_session_metadata_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    root = _write_project(tmp_path)
    state_dir = tmp_path / "state"

    bridge_id = "test-missing-session"
    (root / "bridge" / f"gtkb-{bridge_id}-001.md").write_text(
        "NEW\n\nauthor_harness_id: D\n# content\n",
        encoding="utf-8",
    )
    (root / "bridge" / "INDEX.md").write_text(
        f"Document: {bridge_id}\nNEW: bridge/gtkb-{bridge_id}-001.md\n", encoding="utf-8"
    )

    monkeypatch.setattr(cht, "_is_cross_harness_trigger_active_substrate", lambda root: True)
    monkeypatch.setattr(cht, "_is_single_harness_topology", lambda root: False)
    monkeypatch.setattr(cht, "_evaluate_ollama_dispatch_readiness", lambda root: {"ready": True})

    summary = cht.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    assert summary["results"]["loyal-opposition"]["reason"] == "author_session_context_missing"

    state_file = state_dir / "dispatch-state.json"
    state_data = json.loads(state_file.read_text(encoding="utf-8"))
    assert state_data["recipients"]["loyal-opposition"]["last_result"] == "author_session_context_missing"

    diag_file = state_dir / "trigger-diagnostic.jsonl"
    lo_diags = [json.loads(line) for line in diag_file.read_text(encoding="utf-8").splitlines()]
    lo_diag = [record for record in lo_diags if record.get("recipient") == "loyal-opposition"][-1]
    assert lo_diag["last_result"] == "author_session_context_missing"
    assert lo_diag["classification"] == "author_meets_reviewer_refused"

"""Tests for Wave 2 Slice 4 _path_rewrite.py.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-003.md`` (REVISED-1)
and ``-004`` (Codex GO with 5 implementation conditions).

Mocking strategy: ``subprocess.run`` is monkeypatched in 16 tests to
return synthetic classification JSON without walking ``LEGACY_ROOT``. One
live-subprocess smoke test (``test_subprocess_smoke_invokes_classify_tree
_against_tmp_dir``) runs the real ``classify-tree`` against a tiny tmp
tree to catch entrypoint regressions (per Codex GO -004 condition 3:
"Keep live subprocess testing constrained to a tiny temp tree; do not
run live classify-tree against LEGACY_ROOT in unit tests").
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _path_rewrite  # noqa: E402
from rehearse._common import LEGACY_ROOT  # noqa: E402


_VALID_FILTER_TEMPLATE = (
    "git filter-repo --path <agent-red-paths-from-_path_rewrite> "
    "--path-rename <each-source>:applications/Agent_Red/<each-target>"
)


def _build_manifest(legacy_root: Path, app_name: str = "Agent_Red") -> dict[str, Any]:
    """Return a minimal valid Wave 2 manifest dict (already loaded shape).

    ``app_name`` lets F2 fixture tests prove the rewrite target derives
    from manifest rather than a hard-coded ``Agent_Red`` constant.
    """
    return {
        "target_root": str((legacy_root / "applications" / app_name).as_posix()),
        "legacy_root": str(legacy_root.as_posix()),
        "applications_namespace": str((legacy_root / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "git_filter_command_template": _VALID_FILTER_TEMPLATE,
        "excluded_paths": [],
    }


def _synth_classification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compose the classification JSON shape returned by gt project classify-tree."""
    return {
        "generated": "2026-04-27T02:00:00+00:00",
        "gt_kb_version": "0.6.1-test",
        "gt_kb_head": "abc1234",
        "target_tree": "synthetic",
        "target_head": "def5678",
        "total_paths_classified": len(rows),
        "owner_decision_pending_rows": sum(
            1 for r in rows if r.get("owner_decision_pending")
        ),
        "rows": rows,
    }


def _mock_classify_tree_writes(
    monkeypatch: pytest.MonkeyPatch,
    rows: list[dict[str, Any]] | None = None,
    *,
    returncode: int = 0,
    write_file: bool = True,
    file_content: str | None = None,
) -> dict[str, Any]:
    """Patch subprocess.run so classify-tree's --output writes synthetic JSON.

    Captures the argv used for later assertions. Returns a dict with a
    ``cmd`` key updated by the mock when subprocess.run is called.
    """
    captured: dict[str, Any] = {"cmd": None}
    payload = _synth_classification(rows or [])

    def _fake_run(cmd: list[str], *args: Any, **kwargs: Any) -> Any:
        captured["cmd"] = list(cmd)
        if write_file and "--output" in cmd:
            output_idx = cmd.index("--output") + 1
            output_path = Path(cmd[output_idx])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                file_content if file_content is not None else json.dumps(payload),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(
            args=cmd, returncode=returncode, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)
    return captured


# ----- T1: dry-run -----


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    """Dry-run returns status='skipped' without invoking subprocess."""
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=True)
    assert result["status"] == "skipped"
    assert result["metrics"] == {"reason": "dry_run"}
    assert result["output_files"] == []


# ----- T2-T4: F1 entrypoint regression guards -----


def test_build_classify_tree_command_uses_callable_entrypoint(tmp_path: Path) -> None:
    """F1 regression guard: argv must use callable entrypoint, NOT -m form.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-002.md`` F1 NO-GO:
    ``python -m groundtruth_kb.cli`` is a no-op in this checkout.
    """
    cmd = _path_rewrite._build_classify_tree_command(
        tmp_path, tmp_path / "out.json"
    )
    assert cmd[0] == sys.executable
    assert cmd[1] == "-c"
    assert cmd[2] == "from groundtruth_kb.cli import main; main()"
    # Regression guards: -m and groundtruth_kb.cli MUST NOT appear.
    assert "-m" not in cmd, f"argv must not use -m form: {cmd}"
    assert "groundtruth_kb.cli" not in cmd, (
        f"argv must use callable form, not module path: {cmd}"
    )


def test_build_classify_tree_command_includes_required_flags(tmp_path: Path) -> None:
    """F1: argv contains --dir, --max-depth, --format json, --output."""
    output_path = tmp_path / "classification.json"
    cmd = _path_rewrite._build_classify_tree_command(tmp_path, output_path)
    assert "project" in cmd
    assert "classify-tree" in cmd
    assert "--dir" in cmd
    dir_idx = cmd.index("--dir")
    assert cmd[dir_idx + 1] == str(tmp_path)
    assert "--max-depth" in cmd
    assert "--format" in cmd
    fmt_idx = cmd.index("--format")
    assert cmd[fmt_idx + 1] == "json"
    assert "--output" in cmd
    out_idx = cmd.index("--output")
    assert cmd[out_idx + 1] == str(output_path)


def test_subprocess_smoke_invokes_classify_tree_against_tmp_dir(
    tmp_path: Path,
) -> None:
    """F1 live smoke: real subprocess against tmp tree must produce JSON.

    Per Codex GO -004 condition 3: live subprocess testing must stay
    constrained to a tiny temp tree, never LEGACY_ROOT. Catches "subprocess
    exits 0 but writes nothing" the same way Codex's F1 smoke detected the
    original ``-m`` no-op regression.
    """
    fixture_tree = tmp_path / "fixture"
    fixture_tree.mkdir()
    (fixture_tree / "alpha.py").write_text("print('alpha')\n", encoding="utf-8")
    (fixture_tree / "beta.md").write_text("# beta\n", encoding="utf-8")

    output_path = tmp_path / "smoke-classification.json"
    cmd = _path_rewrite._build_classify_tree_command(fixture_tree, output_path)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, (
        f"classify-tree exited {result.returncode}; stderr={result.stderr!r}"
    )
    assert output_path.exists(), (
        "classify-tree exited 0 but did not write classification.json — "
        "entrypoint regression (slice4-002 F1)."
    )
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "rows" in data
    assert isinstance(data["rows"], list)


# ----- T5: subprocess invoked correctly via mock -----


def test_run_invokes_classify_tree_subprocess(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mocked subprocess called with the _build_classify_tree_command shape."""
    captured = _mock_classify_tree_writes(monkeypatch, rows=[])
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert captured["cmd"] is not None
    assert captured["cmd"][0] == sys.executable
    assert captured["cmd"][1] == "-c"
    assert "classify-tree" in captured["cmd"]
    assert result["status"] == "ok"


# ----- T6: happy path adopter-owned -----


def test_run_produces_rewrites_for_adopter_owned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Adopter-owned rows produce path-rewrite entries."""
    rows = [
        {
            "path": "src/foo.py",
            "ownership": "adopter-owned",
            "record_id": "src.foo",
            "owner_decision_pending": False,
            "notes": "",
        }
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert result["status"] == "ok"
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(pr["rewrites"]) == 1
    assert pr["rewrites"][0]["source"] == "src/foo.py"
    assert pr["rewrites"][0]["target"] == "applications/Agent_Red/src/foo.py"


# ----- T7-T9: bucket partitioning -----


def test_run_skips_gt_kb_managed_in_rewrites(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """gt-kb-managed rows go to keep_at_root, not rewrites."""
    rows = [
        {
            "path": ".claude/hooks/foo.py",
            "ownership": "gt-kb-managed",
            "record_id": "hook.foo",
            "owner_decision_pending": False,
            "notes": "",
        },
        {
            "path": "groundtruth.toml",
            "ownership": "gt-kb-scaffolded",
            "record_id": "config.gt",
            "owner_decision_pending": False,
            "notes": "",
        },
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert pr["rewrites"] == []
    assert len(pr["keep_at_root"]) == 2
    assert {r["path"] for r in pr["keep_at_root"]} == {
        ".claude/hooks/foo.py",
        "groundtruth.toml",
    }
    assert result["status"] == "ok"


def test_run_emits_shared_structured_to_shared_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """shared-structured rows go to shared_paths bucket."""
    rows = [
        {
            "path": "memory/MEMORY.md",
            "ownership": "shared-structured",
            "record_id": "memory.shared",
            "owner_decision_pending": False,
            "notes": "",
        }
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(pr["shared_paths"]) == 1
    assert pr["shared_paths"][0]["path"] == "memory/MEMORY.md"
    assert pr["rewrites"] == []


def test_run_emits_legacy_exception_to_warnings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """legacy-exception rows go to legacy_exceptions list + warning string."""
    rows = [
        {
            "path": "groundtruth.db",
            "ownership": "legacy-exception",
            "record_id": "db.root",
            "owner_decision_pending": False,
            "notes": "explicit unresolved adoption debt",
        }
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert result["status"] == "ok"
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(pr["legacy_exceptions"]) == 1
    assert pr["legacy_exceptions"][0]["path"] == "groundtruth.db"
    assert any("legacy_exceptions_present" in w for w in result["warnings"])


def test_run_emits_unresolved_paths_when_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """owner_decision_pending=True diverts to unresolved_paths regardless of ownership."""
    rows = [
        {
            "path": "requirements-local.txt",
            "ownership": "legacy-exception",
            "record_id": "deps.local",
            "owner_decision_pending": True,
            "notes": "owner adoption cadence pending",
        },
        {
            "path": "src/bar.py",
            "ownership": "adopter-owned",
            "record_id": "src.bar",
            "owner_decision_pending": True,
            "notes": "split decision pending",
        },
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    # Both rows route to unresolved regardless of their ownership label.
    assert len(pr["unresolved_paths"]) == 2
    assert pr["rewrites"] == []
    assert pr["legacy_exceptions"] == []
    assert any("unresolved_paths_present" in w for w in result["warnings"])


# ----- T11-T12: artifact files -----


def test_run_writes_path_rewrite_json_with_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Main artifact path_rewrite.json is written with schema_version=1 and summary."""
    rows = [
        {
            "path": "src/a.py",
            "ownership": "adopter-owned",
            "record_id": "a",
            "owner_decision_pending": False,
            "notes": "",
        },
        {
            "path": "src/b.py",
            "ownership": "adopter-owned",
            "record_id": "b",
            "owner_decision_pending": False,
            "notes": "",
        },
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    pr_path = tmp_path / "out" / "path_rewrite" / "path_rewrite.json"
    assert pr_path.exists()
    pr = json.loads(pr_path.read_text(encoding="utf-8"))
    assert pr["schema_version"] == 1
    assert pr["summary"]["rewrites_count"] == 2
    assert pr["summary"]["total_classified"] == 2
    assert pr["target_namespace"] == "applications/Agent_Red"
    assert "generated_at" in pr


def test_run_writes_git_filter_args_file_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """git_filter_args.txt: one line per rewrite with --path / --path-rename."""
    rows = [
        {
            "path": "src/a.py",
            "ownership": "adopter-owned",
            "record_id": "a",
            "owner_decision_pending": False,
            "notes": "",
        },
        {
            "path": "src/b.py",
            "ownership": "adopter-owned",
            "record_id": "b",
            "owner_decision_pending": False,
            "notes": "",
        },
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    args_path = tmp_path / "out" / "path_rewrite" / "git_filter_args.txt"
    assert args_path.exists()
    lines = args_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert (
        lines[0]
        == "--path src/a.py --path-rename src/a.py:applications/Agent_Red/src/a.py"
    )
    assert (
        lines[1]
        == "--path src/b.py --path-rename src/b.py:applications/Agent_Red/src/b.py"
    )


# ----- T13: target path format -----


def test_run_target_path_format_correct(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Source ``src/foo.py`` becomes ``applications/Agent_Red/src/foo.py``."""
    rows = [
        {
            "path": "src/foo.py",
            "ownership": "adopter-owned",
            "record_id": "src.foo",
            "owner_decision_pending": False,
            "notes": "",
        }
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert pr["rewrites"][0]["target"] == "applications/Agent_Red/src/foo.py"
    assert "/" in pr["rewrites"][0]["target"]
    assert "\\" not in pr["rewrites"][0]["target"]


# ----- T14-T15: F2 non-hardcoding -----


def test_derive_target_namespace_returns_forward_slashed_relative_path(
    tmp_path: Path,
) -> None:
    """F2 unit: namespace = target_root.relative_to(legacy_root), forward slashes."""
    manifest = _build_manifest(tmp_path)
    ns = _path_rewrite._derive_target_namespace(manifest)
    assert ns == "applications/Agent_Red"
    assert "\\" not in ns


def test_run_target_namespace_derived_from_manifest_not_hardcoded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F2 fixture: a non-Agent_Red manifest produces non-Agent_Red rewrite targets."""
    rows = [
        {
            "path": "src/foo.py",
            "ownership": "adopter-owned",
            "record_id": "src.foo",
            "owner_decision_pending": False,
            "notes": "",
        }
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path, app_name="Different_App")
    _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert pr["target_namespace"] == "applications/Different_App"
    assert pr["rewrites"][0]["target"] == "applications/Different_App/src/foo.py"
    assert "Agent_Red" not in pr["rewrites"][0]["target"]
    assert "Agent_Red" not in pr["target_namespace"]


# ----- T16-T18: error paths -----


def test_run_returns_error_when_classify_tree_subprocess_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Non-zero subprocess exit → status='error', warning includes stderr."""
    _mock_classify_tree_writes(
        monkeypatch, rows=[], returncode=1, write_file=False
    )
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert result["status"] == "error"
    assert any("classify_tree_nonzero_exit" in w for w in result["warnings"])


def test_run_returns_error_when_subprocess_zero_exit_but_no_file_produced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Per GO -004 condition 2: zero-exit without classification.json → error.

    This is the production analog of Codex's F1 smoke test: the entrypoint
    regression class where subprocess exits 0 but writes nothing must be
    visible at runtime, not silently treated as an empty rewrite.
    """
    _mock_classify_tree_writes(
        monkeypatch, rows=[], returncode=0, write_file=False
    )
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert result["status"] == "error"
    assert any(
        "classify_tree_zero_exit_but_no_classification_file" in w
        for w in result["warnings"]
    )


def test_run_returns_error_when_classification_malformed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Malformed JSON from classify-tree → status='error'."""
    _mock_classify_tree_writes(
        monkeypatch, file_content="this is not json {{{"
    )
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert result["status"] == "error"
    assert any("classification_json_unreadable" in w for w in result["warnings"])


def test_run_unknown_ownership_emits_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown ownership label → warning string + skip (not error)."""
    rows = [
        {
            "path": "weird/path.txt",
            "ownership": "future-ownership-label",
            "record_id": "future",
            "owner_decision_pending": False,
            "notes": "",
        }
    ]
    _mock_classify_tree_writes(monkeypatch, rows=rows)
    manifest = _build_manifest(tmp_path)
    result = _path_rewrite.run(manifest, tmp_path / "out", dry_run=False)
    assert result["status"] == "ok"
    assert any("unknown_ownership_labels" in w for w in result["warnings"])
    pr = json.loads(
        (tmp_path / "out" / "path_rewrite" / "path_rewrite.json").read_text(
            encoding="utf-8"
        )
    )
    assert pr["summary"]["unknown_ownership_count"] == 1
    assert pr["rewrites"] == []

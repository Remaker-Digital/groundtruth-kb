"""Tests for scripts/check_commit_scope_bundling.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "check_commit_scope_bundling.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_commit_scope_bundling", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


checker = _load_checker()


def _write_project(root: Path, packets: list[dict[str, str]] | None = None) -> Path:
    config_path = root / "config" / "governance" / "narrative-artifact-approval.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        """
[[protected_artifacts]]
patterns = ["docs/*.md", ".claude/rules/*.md", "independent-progress-assessments/**/*.md"]

[[exemptions]]
patterns = ["docs/exempt.md"]
""".lstrip(),
        encoding="utf-8",
    )

    packet_dir = root / ".groundtruth" / "formal-artifact-approvals"
    packet_dir.mkdir(parents=True)
    for index, packet in enumerate(packets or [], start=1):
        (packet_dir / f"packet-{index}.json").write_text(json.dumps(packet), encoding="utf-8")
    return root


def _packet(path: str, source_ref: str, *, change_reason: str = "", artifact_id: str = "") -> dict[str, str]:
    return {
        "target_path": path,
        "source_ref": source_ref,
        "change_reason": change_reason,
        "artifact_id": artifact_id,
    }


def test_single_approval_scope_passes(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet(
                "docs/a.md",
                "bridge/gtkb-scope-alpha-001.md",
                change_reason="DELIB-S001 and GOV-SCOPE-001",
            )
        ],
    )

    result = checker.evaluate(root, paths=["docs/a.md"])

    assert result["status"] == "pass"
    assert len(result["scopes"]) == 1
    assert result["findings"] == []


def test_multiple_paths_same_scope_pass(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001"),
            _packet(".claude/rules/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001"),
        ],
    )

    result = checker.evaluate(root, paths=["docs/a.md", ".claude/rules/a.md"])

    assert result["status"] == "pass"
    scope = next(iter(result["scopes"].values()))
    assert scope["paths"] == [".claude/rules/a.md", "docs/a.md"]


def test_different_source_refs_warn(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001"),
            _packet("docs/b.md", "bridge/gtkb-scope-beta-001.md", change_reason="DELIB-S001 GOV-SCOPE-001"),
        ],
    )

    result = checker.evaluate(root, paths=["docs/a.md", "docs/b.md"])

    assert result["status"] == "warn"
    assert result["findings"][0]["kind"] == "multi_scope_bundle"


def test_different_deliberations_warn(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001"),
            _packet("docs/b.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S002 GOV-SCOPE-001"),
        ],
    )

    result = checker.evaluate(root, paths=["docs/a.md", "docs/b.md"])

    assert result["status"] == "warn"
    assert len(result["scopes"]) == 2


def test_different_bridge_slugs_warn(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", artifact_id="gtkb-scope-alpha-003"),
            _packet("docs/b.md", "bridge/gtkb-scope-beta-001.md", artifact_id="gtkb-scope-beta-009"),
        ],
    )

    result = checker.evaluate(root, paths=["docs/a.md", "docs/b.md"])

    assert result["status"] == "warn"
    assert sorted(scope["bridge_slug"] for scope in result["scopes"].values()) == [
        "gtkb-scope-alpha",
        "gtkb-scope-beta",
    ]


def test_unscoped_protected_path_warns(tmp_path: Path) -> None:
    root = _write_project(tmp_path)

    result = checker.evaluate(root, paths=["docs/a.md"])

    assert result["status"] == "warn"
    assert result["findings"] == [{"kind": "unscoped_protected_paths", "paths": ["docs/a.md"]}]


def test_unprotected_paths_are_skipped(tmp_path: Path) -> None:
    root = _write_project(tmp_path)

    result = checker.evaluate(root, paths=["src/app.py", "docs/exempt.md"])

    assert result["status"] == "pass"
    assert result["skipped_unprotected"] == ["docs/exempt.md", "src/app.py"]


def test_evaluate_output_is_deterministic(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/b.md", "bridge/gtkb-scope-beta-001.md", change_reason="DELIB-S002 GOV-SCOPE-002"),
            _packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001"),
        ],
    )

    first = checker.evaluate(root, paths=["docs/b.md", "docs/a.md", "docs/a.md"])
    second = checker.evaluate(root, paths=["docs/a.md", "docs/b.md"])

    assert first == second


def test_main_returns_zero_for_warn_mode(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md"),
            _packet("docs/b.md", "bridge/gtkb-scope-beta-001.md"),
        ],
    )

    code = checker.main(["--paths", "docs/a.md", "docs/b.md"], repository_root=root)

    captured = capsys.readouterr()
    assert code == 0
    assert "WARN commit-scope bundling detected" in captured.err


def test_missing_config_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = checker.main(["--paths", "docs/a.md"], repository_root=tmp_path)

    captured = capsys.readouterr()
    assert code == 2
    assert "narrative-artifact-approval config not found" in captured.err


def test_staged_paths_use_acm_diff_filter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(args, *, cwd, capture_output, text, check):
        assert args == ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
        assert cwd == tmp_path
        assert capture_output is True
        assert text is True
        assert check is True
        return SimpleNamespace(stdout="docs/a.md\ndocs/a.md\nD-only.md\n")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)

    assert checker._staged_paths(tmp_path) == ["D-only.md", "docs/a.md"]


def test_packets_without_structured_ids_share_none_scope(tmp_path: Path) -> None:
    root = _write_project(
        tmp_path,
        [
            _packet("docs/a.md", "manual-owner-approval"),
            _packet("docs/b.md", "manual-owner-approval"),
        ],
    )

    result = checker.evaluate(root, paths=["docs/a.md", "docs/b.md"])

    assert result["status"] == "pass"
    scope = next(iter(result["scopes"].values()))
    assert scope["deliberation_id"] is None
    assert scope["spec_id"] is None
    assert scope["bridge_slug"] is None


def test_paths_mode_does_not_read_staged_git_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _write_project(
        tmp_path,
        [_packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001")],
    )

    monkeypatch.setattr(checker, "_staged_paths", lambda _root: pytest.fail("staged paths should not be read"))

    result = checker.evaluate(root, paths=["docs/a.md"])

    assert result["status"] == "pass"


def test_json_output_shape(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _write_project(
        tmp_path,
        [_packet("docs/a.md", "bridge/gtkb-scope-alpha-001.md", change_reason="DELIB-S001 GOV-SCOPE-001")],
    )

    code = checker.main(["--paths", "docs/a.md", "--json"], repository_root=root)

    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "pass"
    assert set(payload) == {"findings", "scopes", "skipped_unprotected", "status", "unscoped_protected"}


def test_main_refuses_project_root_outside_repo_before_loading_config(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture_root = _write_project(tmp_path / "fixture")
    outside_root = Path("C:/tmp/gtkb-commit-scope-bundling-outside-repo")

    code = checker.main(
        ["--paths", "docs/a.md", "--project-root", str(outside_root)],
        repository_root=fixture_root,
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "outside repository root" in captured.err
    assert "narrative-artifact-approval config not found" not in captured.err

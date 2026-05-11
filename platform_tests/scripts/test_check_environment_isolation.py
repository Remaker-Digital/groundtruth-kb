"""Tests for the Phase 3 environment-boundary checker.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "check_environment_isolation.py"
)


def _load_checker_module():
    spec = importlib.util.spec_from_file_location(
        "check_environment_isolation", SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_environment_isolation"] = module
    spec.loader.exec_module(module)
    return module


CLEAN_DOCKERIGNORE = "\n".join(
    (
        ".codex/",
        ".groundtruth/",
        "bridge/",
        "independent-progress-assessments/",
        "groundtruth.db",
        ".groundtruth-chroma/",
        ".env",
    )
)

CLEAN_DOCKERFILE = "\n".join(
    (
        "FROM python:3.12-slim",
        "WORKDIR /app",
        "COPY requirements.txt ./",
        "COPY src/ ./src/",
    )
)

CLEAN_COMPOSE = "\n".join(
    (
        "services:",
        "  api:",
        "    volumes:",
        "      - ./src:/app/src:ro",
        "      - nats-data:/data",
        '    ports:',
        '      - "8080:8000"',
        "volumes:",
        "  nats-data:",
        "    driver: local",
    )
)

CLEAN_REQUIREMENTS_LOCAL = (
    "-r requirements-test.txt\n"
    "groundtruth-kb[web] @ git+https://example.com/g.git@v1\n"
)

CLEAN_REQUIREMENTS_TEST = (
    "-r requirements.txt\n"
    "groundtruth-kb[search] @ git+https://example.com/g.git@v1\n"
)


def _write_clean_tree(root: Path) -> None:
    (root / ".dockerignore").write_text(CLEAN_DOCKERIGNORE, encoding="utf-8")
    (root / "Dockerfile").write_text(CLEAN_DOCKERFILE, encoding="utf-8")
    (root / "docker-compose.yml").write_text(CLEAN_COMPOSE, encoding="utf-8")
    (root / "requirements.txt").write_text("", encoding="utf-8")
    (root / "requirements-test.txt").write_text(
        CLEAN_REQUIREMENTS_TEST, encoding="utf-8"
    )
    (root / "requirements-local.txt").write_text(
        CLEAN_REQUIREMENTS_LOCAL, encoding="utf-8"
    )


def test_clean_tree_produces_no_findings(tmp_path):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)

    report = mod.build_report(tmp_path)

    assert report.findings == []
    assert report.default_gtkb_dependency_mode == "released_package"
    assert report.has_errors is False


def test_missing_dockerignore_rule_is_reported(tmp_path):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)
    (tmp_path / ".dockerignore").write_text(
        "\n".join(
            (
                ".codex/",
                "bridge/",
                "independent-progress-assessments/",
                "groundtruth.db",
                ".groundtruth-chroma/",
            )
        ),
        encoding="utf-8",
    )

    findings = mod.check_dockerignore(tmp_path)

    codes = [f.code for f in findings]
    messages = " ".join(f.message for f in findings)
    assert codes == ["DOCKERIGNORE_MISSING_RULE"]
    assert ".groundtruth" in messages


def test_missing_dockerignore_file_is_reported(tmp_path):
    mod = _load_checker_module()

    findings = mod.check_dockerignore(tmp_path)

    assert [f.code for f in findings] == ["DOCKERIGNORE_MISSING_FILE"]
    assert findings[0].severity == "error"


def test_forbidden_dockerfile_copy_is_reported(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.12-slim\n"
        "COPY src/ ./src/\n"
        "COPY bridge/ ./bridge/\n"
        "COPY .codex ./agent-config/\n",
        encoding="utf-8",
    )

    findings = mod.check_dockerfile(tmp_path)

    codes = [f.code for f in findings]
    paths = [f.path for f in findings]
    assert codes == ["DOCKERFILE_FORBIDDEN_COPY", "DOCKERFILE_FORBIDDEN_COPY"]
    assert "Dockerfile:3" in paths and "Dockerfile:4" in paths


def test_dockerfile_allows_approved_copy_sources(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "Dockerfile").write_text(CLEAN_DOCKERFILE, encoding="utf-8")

    assert mod.check_dockerfile(tmp_path) == []


def test_compose_rejects_host_bind_escaping_repo(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n"
        "  api:\n"
        "    volumes:\n"
        "      - ../other-repo/src:/app/src:ro\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_HOST_BIND_OUT_OF_APP"]


def test_compose_rejects_absolute_host_bind(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n"
        "  api:\n"
        "    volumes:\n"
        "      - /etc/agentred:/app/etc:ro\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_HOST_BIND_OUT_OF_APP"]


def test_compose_requires_source_bind_read_only(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  api:\n    volumes:\n      - ./src:/app/src\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_SOURCE_BIND_NOT_READONLY"]


def test_compose_requires_any_repo_local_bind_read_only(tmp_path):
    """Repo-local binds outside the legacy src/app/scripts prefixes must also
    be read-only. Regression guard for Phase 3 NO-GO -004 F1."""
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  api:\n    volumes:\n      - ./config:/app/config\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_SOURCE_BIND_NOT_READONLY"]


def test_compose_accepts_repo_local_bind_with_read_only_opt(tmp_path):
    """A `:ro` option satisfies the policy regardless of the path prefix."""
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  api:\n    volumes:\n      - ./config:/app/config:ro\n",
        encoding="utf-8",
    )

    assert mod.check_compose(tmp_path) == []


def test_compose_rejects_windows_drive_letter_bind(tmp_path):
    """Windows drive-letter absolute host binds are out-of-app and must be
    rejected even if `:ro` is present. Regression guard for Phase 3 NO-GO
    -006 F1."""
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  api:\n    volumes:\n      - C:/temp/config:/app/config:ro\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_HOST_BIND_OUT_OF_APP"]


def test_compose_rejects_windows_drive_letter_bind_without_ro(tmp_path):
    """Windows drive-letter absolute host binds are rejected regardless of
    the :ro option (out-of-app is a higher-severity policy)."""
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  api:\n    volumes:\n      - D:/data:/app/data\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_HOST_BIND_OUT_OF_APP"]


def test_compose_rejects_windows_drive_letter_bind_with_backslash(tmp_path):
    """Windows backslash-separator drive-letter paths are also rejected."""
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(
        "services:\n  api:\n    volumes:\n      - C:\\temp\\config:/app/config:ro\n",
        encoding="utf-8",
    )

    findings = mod.check_compose(tmp_path)

    assert [f.code for f in findings] == ["COMPOSE_HOST_BIND_OUT_OF_APP"]


def test_compose_ignores_port_mappings_and_named_volumes(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "docker-compose.yml").write_text(CLEAN_COMPOSE, encoding="utf-8")

    assert mod.check_compose(tmp_path) == []


def test_detect_gtkb_mode_released(tmp_path):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)

    mode, findings = mod.detect_gtkb_mode(tmp_path)

    assert mode == "released_package"
    assert findings == []


def test_detect_gtkb_mode_editable_sibling_is_reported(tmp_path):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)
    (tmp_path / "requirements-local.txt").write_text(
        "-e ../groundtruth-kb[web]\n", encoding="utf-8"
    )

    mode, findings = mod.detect_gtkb_mode(tmp_path)

    assert mode == "editable_local"
    assert [f.code for f in findings] == ["REQUIREMENTS_EDITABLE_GTKB_SIBLING"]
    assert findings[0].severity == "error"


def test_detect_gtkb_mode_missing(tmp_path):
    mod = _load_checker_module()

    mode, findings = mod.detect_gtkb_mode(tmp_path)

    assert mode == "missing"
    assert findings == []


def test_detect_gtkb_mode_ignores_commented_editable_line(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "requirements-local.txt").write_text(
        "# -e ../groundtruth-kb[web]\n"
        "groundtruth-kb[web] @ git+https://example.com/g.git@v1\n",
        encoding="utf-8",
    )

    mode, findings = mod.detect_gtkb_mode(tmp_path)

    assert mode == "released_package"
    assert findings == []


def test_build_report_populates_probe_fields(tmp_path, monkeypatch):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)

    def fake_git(args, *, root):
        mapping = {
            ("rev-parse", "--show-toplevel"): str(tmp_path),
            ("config", "--get", "remote.origin.url"): "git@example.com:a.git",
            ("rev-parse", "--abbrev-ref", "HEAD"): "develop",
        }
        return mapping.get(tuple(args))

    monkeypatch.setattr(mod, "_git", fake_git)

    report = mod.build_report(tmp_path)

    assert report.repo_root == str(tmp_path)
    assert report.git_remote == "git@example.com:a.git"
    assert report.git_branch == "develop"


def test_build_report_degrades_when_git_unavailable(tmp_path, monkeypatch):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)
    monkeypatch.setattr(mod, "_git", lambda *_a, **_k: None)

    report = mod.build_report(tmp_path)

    assert report.repo_root is None
    assert report.git_remote is None
    assert report.git_branch is None
    assert report.has_errors is False


def test_json_output_shape(tmp_path, monkeypatch, capsys):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)
    monkeypatch.setattr(mod, "_git", lambda *_a, **_k: None)

    exit_code = mod.main(["--json", "--root", str(tmp_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert set(payload.keys()) == {
        "cwd",
        "repo_root",
        "git_remote",
        "git_branch",
        "default_gtkb_dependency_mode",
        "findings",
    }
    assert payload["findings"] == []
    assert payload["default_gtkb_dependency_mode"] == "released_package"


def test_main_exits_nonzero_on_error_finding(tmp_path, monkeypatch, capsys):
    mod = _load_checker_module()
    (tmp_path / ".dockerignore").write_text("", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    monkeypatch.setattr(mod, "_git", lambda *_a, **_k: None)

    exit_code = mod.main(["--root", str(tmp_path)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "DOCKERIGNORE_MISSING_RULE" in captured.out


def test_git_probe_handles_missing_git_binary(monkeypatch, tmp_path):
    mod = _load_checker_module()

    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert mod._git(["rev-parse", "--show-toplevel"], root=tmp_path) is None


def test_repository_passes_its_own_checker():
    """Sanity check: the Agent Red repo itself must satisfy the first-slice policy."""
    mod = _load_checker_module()
    repo_root = Path(__file__).resolve().parents[2]

    report = mod.build_report(repo_root)

    error_findings = [f for f in report.findings if f.severity == "error"]
    assert error_findings == [], (
        "Environment-isolation errors detected in the live repository: "
        + "; ".join(f"{f.code} {f.path}: {f.message}" for f in error_findings)
    )


def test_script_runs_as_cli(tmp_path, monkeypatch):
    _write_clean_tree(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["findings"] == []


def test_repeated_probe_is_deterministic(tmp_path, monkeypatch):
    mod = _load_checker_module()
    _write_clean_tree(tmp_path)
    monkeypatch.setattr(mod, "_git", lambda *_a, **_k: None)

    first = mod.build_report(tmp_path).to_dict()
    second = mod.build_report(tmp_path).to_dict()

    assert first == second


def test_editable_line_without_other_gtkb_still_marks_editable(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "requirements-local.txt").write_text(
        "-e ../groundtruth-kb[web]\n", encoding="utf-8"
    )

    mode, findings = mod.detect_gtkb_mode(tmp_path)

    assert mode == "editable_local"
    assert [f.code for f in findings] == ["REQUIREMENTS_EDITABLE_GTKB_SIBLING"]


def test_forbidden_copy_matches_unprefixed_segment(tmp_path):
    mod = _load_checker_module()
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.12-slim\nCOPY groundtruth.db /app/groundtruth.db\n",
        encoding="utf-8",
    )

    findings = mod.check_dockerfile(tmp_path)

    assert [f.code for f in findings] == ["DOCKERFILE_FORBIDDEN_COPY"]


def test_dockerignore_accepts_unslashed_entries(tmp_path):
    mod = _load_checker_module()
    (tmp_path / ".dockerignore").write_text(
        "\n".join(
            (
                ".codex",
                ".groundtruth",
                "bridge",
                "independent-progress-assessments",
                "groundtruth.db",
                ".groundtruth-chroma",
            )
        ),
        encoding="utf-8",
    )

    assert mod.check_dockerignore(tmp_path) == []


def test_dockerignore_ignores_comments_and_negations(tmp_path):
    mod = _load_checker_module()
    (tmp_path / ".dockerignore").write_text(
        "# leading comment\n"
        "!keepme\n"
        ".codex/\n"
        ".groundtruth/\n"
        "bridge/\n"
        "independent-progress-assessments/\n"
        "groundtruth.db\n"
        ".groundtruth-chroma/\n",
        encoding="utf-8",
    )

    assert mod.check_dockerignore(tmp_path) == []


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("src", "src"),
        ("./src", "src"),
        ("./src/", "src"),
        ("src/sub/file.py", "src"),
        ("./.codex/inner", ".codex"),
    ],
)
def test_first_path_segment_strips_prefixes(raw, expected):
    mod = _load_checker_module()

    assert mod._first_path_segment(raw) == expected

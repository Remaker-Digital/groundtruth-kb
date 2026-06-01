"""No-hook subprocess tests for ``gt bridge index`` serialized mutations."""

from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
WRITER_SOURCE = PROJECT_ROOT / "scripts" / "bridge_index_writer.py"


def _prepare_project(tmp_path: Path, index_text: str) -> Path:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "groundtruth.toml").write_text(
        f'[groundtruth]\ndb_path = "{(project_root / "groundtruth.db").as_posix()}"\n'
        f'project_root = "{project_root.as_posix()}"\n',
        encoding="utf-8",
    )
    bridge = project_root / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text(index_text, encoding="utf-8")
    scripts = project_root / "scripts"
    scripts.mkdir()
    (scripts / "bridge_index_writer.py").write_text(WRITER_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    return project_root


def _plain_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("CLAUDE") or key.startswith("CODEX"):
            env.pop(key, None)
    env["PYTHONPATH"] = str(PACKAGE_SRC)
    return env


def _run_gt(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb",
            "--config",
            str(project_root / "groundtruth.toml"),
            *args,
        ],
        cwd=project_root,
        env=_plain_env(),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_concurrent_add_document_preserves_every_document(tmp_path: Path) -> None:
    project_root = _prepare_project(tmp_path, "# Bridge Index\n\n")
    worker_count = 10

    def worker(i: int) -> subprocess.CompletedProcess[str]:
        slug = f"parallel-doc-{i}"
        return _run_gt(
            project_root,
            "bridge",
            "index",
            "add-document",
            slug,
            "--path",
            f"bridge/{slug}-001.md",
            "--json",
            "--timeout",
            "30",
        )

    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        results = list(pool.map(worker, range(worker_count)))

    assert all(result.returncode == 0 for result in results), [(r.returncode, r.stdout, r.stderr) for r in results]
    index_text = (project_root / "bridge" / "INDEX.md").read_text(encoding="utf-8")
    for i in range(worker_count):
        slug = f"parallel-doc-{i}"
        assert f"Document: {slug}\nNEW: bridge/{slug}-001.md" in index_text


def test_concurrent_set_status_preserves_every_status(tmp_path: Path) -> None:
    worker_count = 10
    index_text = "".join(
        f"Document: parallel-doc-{i}\nNEW: bridge/parallel-doc-{i}-001.md\n\n" for i in range(worker_count)
    )
    project_root = _prepare_project(tmp_path, index_text)

    def worker(i: int) -> subprocess.CompletedProcess[str]:
        slug = f"parallel-doc-{i}"
        return _run_gt(
            project_root,
            "bridge",
            "index",
            "set-status",
            slug,
            "GO",
            "--path",
            f"bridge/{slug}-002.md",
            "--json",
            "--timeout",
            "30",
        )

    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        results = list(pool.map(worker, range(worker_count)))

    assert all(result.returncode == 0 for result in results), [(r.returncode, r.stdout, r.stderr) for r in results]
    updated = (project_root / "bridge" / "INDEX.md").read_text(encoding="utf-8")
    for i in range(worker_count):
        slug = f"parallel-doc-{i}"
        assert f"Document: {slug}\nGO: bridge/{slug}-002.md\nNEW: bridge/{slug}-001.md" in updated

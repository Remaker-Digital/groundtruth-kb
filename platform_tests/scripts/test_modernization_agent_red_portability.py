"""Objective acceptance for Agent Red lifecycle isolation and portability.

This module exercises the checked-in Agent Red management surface through the
production slot, app-root, isolation, adopter-migration, and rollback services.
All Git-backed lifecycle work happens in a relocated throwaway application, so
the proof is reproducible in a dirty worktree without altering repository state.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import textwrap
import tomllib
import venv
import zipfile
from collections.abc import Iterator
from importlib import metadata
from pathlib import Path, PureWindowsPath

import pytest
from packaging.requirements import Requirement

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
AGENT_RED_ROOT = REPO_ROOT / "applications" / "Agent_Red"
PLATFORM_PRODUCT_ROOT = REPO_ROOT / "groundtruth-kb"
PRIOR_PACKAGE_FIXTURE = (
    REPO_ROOT / "platform_tests" / "fixtures" / "modernization" / "agent-red-prior-supported-package.json"
)

if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

_TEXT_SUFFIXES = frozenset({".json", ".md", ".ps1", ".py", ".sh", ".toml", ".yaml", ".yml"})
_OPERATIONAL_SUBTREES = (".claude", ".codex", "config", "scripts", "src")
_OPERATIONAL_ROOT_FILES = (
    ".dockerignore",
    ".gtkb-app-isolation.json",
    "application.toml",
    "CLAUDE-ARCHITECTURE.md",
    "CLAUDE-REFERENCE.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "package.json",
    "SECURITY.md",
    "shopify.app.toml",
)
_DERIVED_DIRS = frozenset(
    {".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__", "build", "dist", "node_modules"}
)
_WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z])(?P<path>[A-Za-z]:[\\/][^\s\"'<>|?*`,;)\]}]+)")
_POSIX_HOST_PATH = re.compile(r"(?<![A-Za-z0-9:/])(?P<path>/(?:home|mnt|opt|private|tmp|Users)/[^\s\"'<>`]+)")
_CANONICAL_WINDOWS_ROOT = PureWindowsPath("E:/GT-KB")
_PACKAGE_VERSION = re.compile(r'^__version__ = "(?P<version>[^"]+)"$', re.MULTILINE)
_BUILD_BACKEND_REQUIREMENT = "hatchling==1.29.0"
_OFFLINE_BUILD = textwrap.dedent(
    r"""
    import sys
    import tomllib
    from importlib import metadata
    from pathlib import Path

    project_root = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    build_site = Path(sys.argv[3]).resolve()
    sys.path.insert(0, str(build_site))
    build_system = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))["build-system"]
    required = "hatchling==1.29.0"
    assert build_system["build-backend"] == "hatchling.build"
    assert build_system["requires"] == [required]
    assert metadata.version("hatchling") == required.partition("==")[2]

    from hatchling.build import build_wheel

    output_dir.mkdir(parents=True, exist_ok=True)
    prior_cwd = Path.cwd()
    try:
        import os

        os.chdir(project_root)
        wheel_name = build_wheel(str(output_dir))
    finally:
        os.chdir(prior_cwd)
    print(wheel_name)
    """
).strip()
_AGENT_RED_OPERATIONAL_TESTS = (
    "tests/test_health.py::TestHealthEndpoint::test_health_returns_200_healthy",
    "tests/flows/test_flow_api_roundtrips.py::TestFlowWidgetConversation::test_widget_key_rejected_on_admin_endpoints",
)
_RUNTIME_PROBE = textwrap.dedent(
    r"""
    import importlib.util
    import json
    import os
    import sys
    from pathlib import Path

    source_root = os.path.normcase(os.path.abspath(os.environ["GTKB_SOURCE_ROOT"]))
    source_prefix = source_root + os.sep

    def under_source(value):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        normalized = os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(value))))
        return normalized == source_root or normalized.startswith(source_prefix)

    sys.path[:] = [entry for entry in sys.path if not entry or not under_source(entry)]

    def deny_source_host_reads(event, args):
        path = None
        if event == "open" and args:
            path = args[0]
        elif event in {"os.listdir", "os.scandir", "os.chdir"} and args:
            path = args[0]
        if path is not None and under_source(path):
            raise RuntimeError(f"source-host dependency denied: {path}")

    sys.addaudithook(deny_source_host_reads)

    host_root = Path(os.environ["GTKB_RELOCATED_HOST"]).resolve()
    app_root = host_root / "applications" / "Agent_Red"
    expected_install = Path(os.environ["GTKB_EXPECTED_INSTALL"]).resolve()
    expected_version = os.environ["GTKB_EXPECTED_VERSION"]
    phase = os.environ["GTKB_LIFECYCLE_PHASE"]
    evidence_path = Path(os.environ["GTKB_EVIDENCE_PATH"])
    expected_candidate_module = os.environ["GTKB_EXPECT_CANDIDATE_MODULE"] == "present"
    expected_isolation_findings = {
        item for item in os.environ["GTKB_EXPECT_ISOLATION_FINDINGS"].split("|") if item
    }

    sys.path.insert(0, str(app_root))

    import groundtruth_kb
    from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization
    from groundtruth_kb.isolation.validation import validate_self_completion_preflight
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks
    from src.app.factory import create_app

    package_origin = Path(groundtruth_kb.__file__).resolve()
    assert package_origin.is_relative_to(expected_install), (package_origin, expected_install)
    assert groundtruth_kb.__version__ == expected_version
    assert not any(entry and under_source(entry) for entry in sys.path)
    candidate_module_present = importlib.util.find_spec("groundtruth_kb.modernization") is not None
    assert candidate_module_present is expected_candidate_module

    validate_self_completion_preflight(host_root, "Agent_Red")
    minimization = validate_app_root_minimization(app_root, project_root=host_root, tracked_only=False)
    assert minimization.ok, minimization.first_error_message(limit=10)
    checks = run_isolation_checks(app_root, "dual-agent", product_root=package_origin.parent)
    unacceptable = {
        check.name: {"status": check.status, "message": check.message}
        for check in checks
        if check.status in {"error", "fail", "warning"}
    }
    assert set(unacceptable) == expected_isolation_findings, unacceptable

    app = create_app()
    app_origin = Path(sys.modules["src.app.factory"].__file__).resolve()
    assert app_origin.is_relative_to(app_root)
    assert app.title == "Agent Red Customer Experience"

    evidence_path.write_text(
        json.dumps(
            {
                "phase": phase,
                "package_version": groundtruth_kb.__version__,
                "package_origin": str(package_origin),
                "agent_red_origin": str(app_origin),
                "platform_consumption": "pass",
                "source_host_read_guard": "active",
                "candidate_module_present": candidate_module_present,
                "isolation_findings": sorted(unacceptable),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    import pytest

    raise SystemExit(pytest.main(["-q", "-p", "no:cacheprovider", *os.environ["GTKB_TEST_NODES"].split("|")]))
    """
).strip()

_MIGRATION_DRIVER = textwrap.dedent(
    r"""
    import hashlib
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path

    source_root = os.path.normcase(os.path.abspath(os.environ["GTKB_SOURCE_ROOT"]))
    source_prefix = source_root + os.sep

    def under_source(value):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        normalized = os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(value))))
        return normalized == source_root or normalized.startswith(source_prefix)

    sys.path[:] = [entry for entry in sys.path if not entry or not under_source(entry)]

    def deny_source_host_reads(event, args):
        path = None
        if event == "open" and args:
            path = args[0]
        elif event in {"os.listdir", "os.scandir", "os.chdir"} and args:
            path = args[0]
        if path is not None and under_source(path):
            raise RuntimeError(f"source-host dependency denied: {path}")

    sys.addaudithook(deny_source_host_reads)

    import groundtruth_kb
    from groundtruth_kb.project.rollback import (
        execute_rollback,
        find_latest_receipt,
        plan_rollback,
    )
    from groundtruth_kb.project.upgrade import execute_upgrade

    app_root = Path(os.environ["GTKB_AGENT_RED_ROOT"]).resolve()
    evidence_path = Path(os.environ["GTKB_EVIDENCE_PATH"])
    operation = os.environ["GTKB_MIGRATION_OPERATION"]
    package_origin = Path(groundtruth_kb.__file__).resolve()
    assert not package_origin.is_relative_to(Path(source_root))

    if operation == "upgrade":
        results = execute_upgrade(
            app_root,
            actions=[],
            accept_migration=True,
            product_root=package_origin.parent,
        )
        receipt = find_latest_receipt(app_root)
        assert receipt is not None
        receipt_path = (
            app_root
            / ".claude"
            / "upgrade-receipts"
            / "active"
            / f"{receipt['receipt_id']}.json"
        )
        raw_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        merge_commit = subprocess.run(
            ["git", "rev-parse", f"{receipt['merge_commit']}^{{commit}}"],
            cwd=app_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert merge_commit == receipt["merge_commit"]
        migration = raw_receipt.get("isolation_migration")
        assert isinstance(migration, dict)
        evidence = {
            "operation": operation,
            "package_origin": str(package_origin),
            "package_version": groundtruth_kb.__version__,
            "source_host_read_guard": "active",
            "receipt_id": receipt["receipt_id"],
            "receipt_mode": receipt["mode"],
            "receipt_path": str(receipt_path),
            "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
            "merge_commit": receipt["merge_commit"],
            "auto_fixed": migration.get("auto_fixed", []),
            "results": results,
        }
    elif operation == "rollback":
        receipt = find_latest_receipt(app_root)
        assert receipt is not None
        plan = plan_rollback(app_root, receipt_id=receipt["receipt_id"])
        result = execute_rollback(app_root, plan, commit=True)
        durable_receipt = find_latest_receipt(app_root)
        assert durable_receipt is not None
        assert durable_receipt["receipt_id"] == receipt["receipt_id"]
        receipt_path = (
            app_root
            / ".claude"
            / "upgrade-receipts"
            / "active"
            / f"{receipt['receipt_id']}.json"
        )
        evidence = {
            "operation": operation,
            "package_origin": str(package_origin),
            "package_version": groundtruth_kb.__version__,
            "source_host_read_guard": "active",
            "receipt_id": result.receipt_id,
            "receipt_mode": durable_receipt["mode"],
            "receipt_path": str(receipt_path),
            "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
            "merge_commit": result.merge_commit,
            "rollback_commit": result.commit_sha,
            "files_reverted": [entry.path for entry in result.files_reverted],
        }
    else:
        raise AssertionError(f"unknown migration operation: {operation}")

    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    """
).strip()


def _validate_app_root(app_root: Path, project_root: Path):
    from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization

    return validate_app_root_minimization(app_root, project_root=project_root, tracked_only=False)


def _validate_slot(project_root: Path) -> None:
    from groundtruth_kb.isolation.validation import validate_self_completion_preflight

    validate_self_completion_preflight(project_root, "Agent_Red")


def _isolation_checks(app_root: Path, product_root: Path):
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    return run_isolation_checks(app_root, "dual-agent", product_root=product_root)


def _assert_isolation_clean(checks) -> None:
    by_name = {check.name: check for check in checks}
    unacceptable = {
        name: {"status": check.status, "message": check.message}
        for name, check in by_name.items()
        if check.status in {"error", "fail", "warning"}
    }

    assert not unacceptable, f"Agent Red isolation checks are not clean: {unacceptable}"
    assert by_name["isolation:adopter-root-placement"].status == "pass"
    assert by_name["isolation:no-writable-product-paths"].status == "pass"
    assert by_name["isolation:hooks-point-to-wrappers"].status == "pass"
    assert by_name["isolation:workstream-focus-hook-absent"].status == "pass"
    assert by_name["isolation:chroma-regeneratable"].status == "pass"


def _copy_ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in _DERIVED_DIRS or name.endswith((".pyc", ".pyo"))}


def _run_checked(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    assert result.returncode == 0, (
        f"command failed ({result.returncode}): {' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return result


def _copy_package_build_source(destination: Path) -> None:
    destination.mkdir(parents=True)
    for name in ("pyproject.toml", "README.md"):
        shutil.copy2(PLATFORM_PRODUCT_ROOT / name, destination / name)
    for name in ("src", "templates"):
        shutil.copytree(PLATFORM_PRODUCT_ROOT / name, destination / name, ignore=_copy_ignore)


def _load_prior_package_fixture() -> dict[str, object]:
    fixture = json.loads(PRIOR_PACKAGE_FIXTURE.read_text(encoding="utf-8"))
    assert fixture["schema_version"] == 2
    assert re.fullmatch(r"[0-9a-f]{40}", str(fixture["commit_sha"]))
    assert re.fullmatch(r"[0-9a-f]{40}", str(fixture["groundtruth_kb_tree_sha"]))
    assert fixture["candidate_only_module"] == "groundtruth_kb.modernization"
    wheel_name = str(fixture["wheel_file"])
    assert Path(wheel_name).name == wheel_name
    wheel = PRIOR_PACKAGE_FIXTURE.parent / wheel_name
    assert wheel.is_file(), f"in-repo predecessor wheel is missing: {wheel}"
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == str(fixture["wheel_sha256"])
    fixture["wheel_path"] = wheel
    return fixture


def _wheel_contains_module(wheel: Path, module: str) -> bool:
    module_root = module.replace(".", "/") + "/"
    with zipfile.ZipFile(wheel) as archive:
        return any(name.startswith(module_root) for name in archive.namelist())


def _build_wheel(source_root: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True)
    config = tomllib.loads((source_root / "pyproject.toml").read_text(encoding="utf-8"))
    requirement = config["build-system"]["requires"]
    assert requirement == [_BUILD_BACKEND_REQUIREMENT]
    assert metadata.version("hatchling") == "1.29.0"
    build_site = _materialize_build_backend(output_dir)
    environment = os.environ.copy()
    environment.update(
        {
            "PIP_NO_INDEX": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "UV_OFFLINE": "1",
        }
    )
    _run_checked(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            _OFFLINE_BUILD,
            str(source_root),
            str(output_dir),
            str(build_site),
        ],
        cwd=source_root,
        env=environment,
        timeout=180,
    )
    wheels = list(output_dir.glob("groundtruth_kb-*.whl"))
    assert len(wheels) == 1, f"expected one GT-KB wheel, found {wheels}"
    return wheels[0]


def _materialize_build_backend(output_dir: Path) -> Path:
    """Copy the declared backend closure into the only non-stdlib import path."""
    build_site = output_dir / "build-backend-site"
    build_site.mkdir(parents=True)
    pending = [Requirement(_BUILD_BACKEND_REQUIREMENT)]
    copied: set[str] = set()
    while pending:
        requirement = pending.pop()
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue
        key = requirement.name.lower().replace("_", "-")
        if key in copied:
            continue
        distribution = metadata.distribution(requirement.name)
        assert requirement.specifier.contains(distribution.version, prereleases=True), (
            f"declared build dependency mismatch: {requirement}, installed={distribution.version}"
        )
        for entry in distribution.files or ():
            relative = Path(str(entry))
            if ".." in relative.parts:
                continue
            source = Path(distribution.locate_file(entry))
            if not source.is_file():
                continue
            target = build_site / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        copied.add(key)
        pending.extend(Requirement(item) for item in distribution.requires or ())
    return build_site


def _venv_python(environment_root: Path) -> Path:
    relative = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    return environment_root / relative


def _install_wheel(python: Path, wheel: Path, *, replace_existing: bool = False) -> None:
    command = [
        str(python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-deps",
        "--no-index",
    ]
    if replace_existing:
        command.append("--force-reinstall")
    command.append(str(wheel))
    _run_checked(command, cwd=wheel.parent, timeout=180)


def _run_relocated_operation(
    python: Path,
    *,
    environment_root: Path,
    relocated_host: Path,
    expected_version: str,
    phase: str,
    expect_candidate_module: bool,
    expected_isolation_findings: tuple[str, ...] = (),
) -> dict[str, object]:
    probe = relocated_host / "portability-runtime-probe.py"
    evidence_path = relocated_host / f"portability-{phase}.json"
    probe.write_text(_RUNTIME_PROBE + "\n", encoding="utf-8")
    env = os.environ.copy()
    env.update(
        {
            "GTKB_SOURCE_ROOT": str(REPO_ROOT),
            "GTKB_RELOCATED_HOST": str(relocated_host),
            "GTKB_EXPECTED_INSTALL": str(environment_root),
            "GTKB_EXPECTED_VERSION": expected_version,
            "GTKB_LIFECYCLE_PHASE": phase,
            "GTKB_EVIDENCE_PATH": str(evidence_path),
            "GTKB_TEST_NODES": "|".join(_AGENT_RED_OPERATIONAL_TESTS),
            "GTKB_EXPECT_CANDIDATE_MODULE": "present" if expect_candidate_module else "absent",
            "GTKB_EXPECT_ISOLATION_FINDINGS": "|".join(expected_isolation_findings),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONPATH": "",
        }
    )
    _run_checked([str(python), str(probe)], cwd=relocated_host / "applications" / "Agent_Red", env=env)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["phase"] == phase
    assert evidence["package_version"] == expected_version
    assert Path(evidence["package_origin"]).resolve().is_relative_to(environment_root.resolve())
    assert (
        Path(evidence["agent_red_origin"])
        .resolve()
        .is_relative_to((relocated_host / "applications" / "Agent_Red").resolve())
    )
    assert evidence["platform_consumption"] == "pass"
    assert evidence["source_host_read_guard"] == "active"
    assert evidence["candidate_module_present"] is expect_candidate_module
    assert evidence["isolation_findings"] == sorted(expected_isolation_findings)
    return evidence


def _run_migration_operation(
    python: Path,
    *,
    environment_root: Path,
    relocated_host: Path,
    operation: str,
) -> dict[str, object]:
    driver = relocated_host / "portability-migration-driver.py"
    evidence_path = relocated_host / f"portability-{operation}-evidence.json"
    driver.write_text(_MIGRATION_DRIVER + "\n", encoding="utf-8")
    env = os.environ.copy()
    env.update(
        {
            "GTKB_SOURCE_ROOT": str(REPO_ROOT),
            "GTKB_AGENT_RED_ROOT": str(relocated_host / "applications" / "Agent_Red"),
            "GTKB_EVIDENCE_PATH": str(evidence_path),
            "GTKB_MIGRATION_OPERATION": operation,
            "PYTHONPATH": "",
        }
    )
    _run_checked(
        [str(python), str(driver)],
        cwd=relocated_host,
        env=env,
        timeout=180,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["operation"] == operation
    assert evidence["source_host_read_guard"] == "active"
    assert Path(str(evidence["package_origin"])).resolve().is_relative_to(environment_root.resolve())
    return evidence


def _register_relocated_root_files(app_root: Path, names: tuple[str, ...]) -> None:
    registry_path = app_root / ".gtkb-app-isolation.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    artifacts = registry["top_level_artifacts"]
    existing = {entry["name"] for entry in artifacts}
    for name in names:
        if name in existing:
            continue
        artifacts.append(
            {
                "name": name,
                "type": "DIR" if name == ".git" else "FILE",
                "bucket": "A",
                "purpose": "Portability fixture for the canonical GT-KB adopter migration and rollback lifecycle.",
            }
        )
    artifacts.sort(key=lambda entry: entry["name"])
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _prepare_pre_isolation_state(app_root: Path) -> dict[str, object]:
    """Create a realistic old-adopter state and return its exact rollback baseline."""

    _register_relocated_root_files(app_root, (".git", ".gitignore", "groundtruth.toml"))
    (app_root / ".gitignore").write_text("# pre-migration application ignore policy\n", encoding="utf-8")

    manifest = app_root / "groundtruth.toml"
    manifest.write_text(
        textwrap.dedent(
            """
            [groundtruth]
            db_path = "config/portability-state.sqlite3"

            [project]
            project_name = "Agent Red"
            owner = "Portability Test"
            profile = "dual-agent"
            copyright_notice = ""
            cloud_provider = "none"
            scaffold_version = "0.6.0"
            created_at = "2026-01-01T00:00:00Z"

            [service]
            endpoint = "groundtruth.db"
            """
        ).lstrip(),
        encoding="utf-8",
    )

    work_subject = app_root / ".claude" / "session" / "work-subject.json"
    work_subject.parent.mkdir(parents=True, exist_ok=True)
    work_subject.write_text(
        json.dumps(
            {
                "current_subject": "platform",
                "application_root": str(app_root.resolve()).replace("\\", "/"),
                "set_by": "pre-modernization-adopter",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    legacy_hook = app_root / ".claude" / "hooks" / "workstream-focus.py"
    legacy_hook.parent.mkdir(parents=True, exist_ok=True)
    legacy_hook.write_text("# retired pre-isolation application hook\n", encoding="utf-8")

    state_file = app_root / "config" / "portability-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps({"tenant": "agent-red", "lifecycle": "pre-migration"}, indent=2) + "\n",
        encoding="utf-8",
    )
    database = app_root / "config" / "portability-state.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE application_state (state_key TEXT PRIMARY KEY, state_value TEXT NOT NULL)")
        connection.execute(
            "INSERT INTO application_state (state_key, state_value) VALUES (?, ?)",
            ("tenant-lifecycle", "pre-migration"),
        )

    return _snapshot_application_state(app_root)


def _snapshot_application_state(app_root: Path) -> dict[str, object]:
    database = app_root / "config" / "portability-state.sqlite3"
    with sqlite3.connect(database) as connection:
        database_rows = connection.execute(
            "SELECT state_key, state_value FROM application_state ORDER BY state_key"
        ).fetchall()
    return {
        "database_bytes": database.read_bytes(),
        "database_rows": database_rows,
        "state_file": (app_root / "config" / "portability-state.json").read_bytes(),
        "manifest": (app_root / "groundtruth.toml").read_bytes(),
        "work_subject": (app_root / ".claude" / "session" / "work-subject.json").read_bytes(),
        "legacy_hook": (
            (app_root / ".claude" / "hooks" / "workstream-focus.py").read_bytes()
            if (app_root / ".claude" / "hooks" / "workstream-focus.py").exists()
            else None
        ),
        "gitignore": (app_root / ".gitignore").read_bytes(),
    }


def _initialize_relocated_application_repository(app_root: Path) -> None:
    _run_checked(["git", "init", "--initial-branch=main"], cwd=app_root)
    for key, value in (
        ("user.email", "portability@example.invalid"),
        ("user.name", "GT-KB Portability Test"),
        ("commit.gpgsign", "false"),
        ("core.autocrlf", "false"),
        ("core.hooksPath", ".git/no-hooks"),
    ):
        _run_checked(["git", "config", key, value], cwd=app_root)
    _run_checked(["git", "add", "-A"], cwd=app_root)
    _run_checked(["git", "commit", "-m", "pre-migration Agent Red snapshot"], cwd=app_root)


@pytest.fixture
def relocated_agent_red(tmp_path: Path) -> tuple[Path, Path]:
    """Copy the real application into a second GT-KB host without Git state."""

    relocated_host = tmp_path / "relocated-gtkb-host"
    relocated_app = relocated_host / "applications" / "Agent_Red"
    relocated_app.parent.mkdir(parents=True)
    shutil.copytree(AGENT_RED_ROOT, relocated_app, ignore=_copy_ignore)
    return relocated_host, relocated_app


def _iter_operational_files(app_root: Path) -> Iterator[Path]:
    for name in _OPERATIONAL_ROOT_FILES:
        path = app_root / name
        if path.is_file():
            yield path

    for subtree_name in _OPERATIONAL_SUBTREES:
        subtree = app_root / subtree_name
        if not subtree.is_dir():
            continue
        for path in subtree.rglob("*"):
            if path.is_file() and path.suffix.lower() in _TEXT_SUFFIXES:
                yield path


def _text_fragments(path: Path) -> Iterator[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".py":
        yield from enumerate(text.splitlines(), start=1)
        return

    tree = ast.parse(text, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield getattr(node, "lineno", 1), node.value


def _is_within_canonical_windows_root(candidate: str) -> bool:
    normalized = PureWindowsPath(candidate.replace("\\\\", "\\"))
    candidate_parts = tuple(part.casefold() for part in normalized.parts)
    root_parts = tuple(part.casefold() for part in _CANONICAL_WINDOWS_ROOT.parts)
    return candidate_parts[: len(root_parts)] == root_parts


def _external_path_findings(app_root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(set(_iter_operational_files(app_root))):
        relative = path.relative_to(app_root).as_posix()
        for line_number, fragment in _text_fragments(path):
            for match in _WINDOWS_ABSOLUTE_PATH.finditer(fragment):
                candidate = match.group("path").replace("\\\\", "\\")
                if not _is_within_canonical_windows_root(candidate):
                    findings.append(f"{relative}:{line_number}: external Windows path {candidate}")
            for match in _POSIX_HOST_PATH.finditer(fragment):
                findings.append(f"{relative}:{line_number}: external POSIX path {match.group('path')!r}")
    return findings


def _external_link_findings(app_root: Path) -> list[str]:
    findings: list[str] = []
    canonical_root = REPO_ROOT.resolve()
    for path in app_root.rglob("*"):
        is_junction = getattr(path, "is_junction", lambda: False)()
        if not path.is_symlink() and not is_junction:
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(canonical_root):
            findings.append(f"{path.relative_to(app_root).as_posix()} -> {resolved}")
    return findings


def test_live_agent_red_is_a_clean_independent_application_slot() -> None:
    """The live application is registered, bounded, and outside platform product source."""

    _validate_slot(REPO_ROOT)
    minimization = _validate_app_root(AGENT_RED_ROOT, REPO_ROOT)
    _assert_isolation_clean(_isolation_checks(AGENT_RED_ROOT, PLATFORM_PRODUCT_ROOT))

    assert minimization.ok, minimization.first_error_message(limit=10)
    assert len(minimization.actual_entries) == len(minimization.registry_entries) >= 1
    assert AGENT_RED_ROOT.parent == REPO_ROOT / "applications"
    assert not AGENT_RED_ROOT.resolve().is_relative_to(PLATFORM_PRODUCT_ROOT.resolve())

    registered_names = {entry["name"] for entry in minimization.registry_entries}
    assert registered_names.isdisjoint({"bridge", "groundtruth-kb", "groundtruth.db"})


@pytest.mark.timeout(300)
def test_agent_red_survives_relocation_and_has_an_independent_lifecycle(
    relocated_agent_red: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    """A relocated Agent Red runs through install, adopter migration, and rollback."""

    relocated_host, relocated_app = relocated_agent_red
    original_marker = (AGENT_RED_ROOT / "application.toml").read_bytes()
    relocated_marker = relocated_app / "application.toml"
    relocated_marker.write_bytes(original_marker + b"\n# independent relocated lifecycle\n")

    prior_fixture = _load_prior_package_fixture()
    candidate_source = tmp_path / "candidate-package"
    _copy_package_build_source(candidate_source)

    candidate_init = candidate_source / "src" / "groundtruth_kb" / "__init__.py"
    candidate_text = candidate_init.read_text(encoding="utf-8")
    version_match = _PACKAGE_VERSION.search(candidate_text)
    assert version_match is not None, "GT-KB package version declaration is missing"
    candidate_version = version_match.group("version")

    baseline_version = str(prior_fixture["package_version"])
    candidate_only_module = str(prior_fixture["candidate_only_module"])

    candidate_wheel = _build_wheel(candidate_source, tmp_path / "candidate-wheel")
    baseline_wheel = Path(prior_fixture["wheel_path"])
    assert _wheel_contains_module(candidate_wheel, candidate_only_module)
    assert not _wheel_contains_module(baseline_wheel, candidate_only_module), (
        "the frozen prior wheel contains candidate-only modernization code"
    )
    environment_root = tmp_path / "clean-gtkb-install"
    venv.EnvBuilder(with_pip=True, system_site_packages=True).create(environment_root)
    python = _venv_python(environment_root)

    _install_wheel(python, baseline_wheel)
    baseline_evidence = _run_relocated_operation(
        python,
        environment_root=environment_root,
        relocated_host=relocated_host,
        expected_version=baseline_version,
        phase="clean-install",
        expect_candidate_module=False,
    )

    _install_wheel(python, candidate_wheel, replace_existing=True)
    pre_migration_state = _prepare_pre_isolation_state(relocated_app)
    _initialize_relocated_application_repository(relocated_app)

    migration_evidence = _run_migration_operation(
        python,
        environment_root=environment_root,
        relocated_host=relocated_host,
        operation="upgrade",
    )
    assert migration_evidence["receipt_mode"] == "tracked"
    assert re.fullmatch(r"[0-9a-f]{40}", str(migration_evidence["merge_commit"]))
    assert re.fullmatch(r"[0-9a-f]{64}", str(migration_evidence["receipt_sha256"]))
    assert {(entry["check_name"], entry["file"], entry["outcome"]) for entry in migration_evidence["auto_fixed"]} == {
        ("isolation:service-endpoint", "groundtruth.toml", "fixed"),
        ("isolation:work-subject", ".claude/session/work-subject.json", "fixed"),
        (
            "isolation:workstream-focus-hook-absent",
            ".claude/hooks/workstream-focus.py",
            "fixed",
        ),
    }

    migrated_state = _snapshot_application_state(relocated_app)
    assert migrated_state["database_bytes"] == pre_migration_state["database_bytes"]
    assert migrated_state["database_rows"] == pre_migration_state["database_rows"]
    assert migrated_state["state_file"] == pre_migration_state["state_file"]
    assert migrated_state["manifest"] != pre_migration_state["manifest"]
    assert migrated_state["work_subject"] != pre_migration_state["work_subject"]
    assert json.loads(bytes(migrated_state["work_subject"]))["current_subject"] == "application"
    assert migrated_state["legacy_hook"] is None

    upgraded_evidence = _run_relocated_operation(
        python,
        environment_root=environment_root,
        relocated_host=relocated_host,
        expected_version=candidate_version,
        phase="adopter-migration",
        expect_candidate_module=True,
    )

    rollback_operation = _run_migration_operation(
        python,
        environment_root=environment_root,
        relocated_host=relocated_host,
        operation="rollback",
    )
    assert rollback_operation["receipt_id"] == migration_evidence["receipt_id"]
    assert rollback_operation["merge_commit"] == migration_evidence["merge_commit"]
    assert rollback_operation["receipt_sha256"] == migration_evidence["receipt_sha256"]
    assert re.fullmatch(r"[0-9a-f]{40}", str(rollback_operation["rollback_commit"]))
    assert {
        "groundtruth.toml",
        ".claude/session/work-subject.json",
        ".claude/hooks/workstream-focus.py",
    }.issubset(set(rollback_operation["files_reverted"]))

    rolled_back_state = _snapshot_application_state(relocated_app)
    assert rolled_back_state == pre_migration_state
    rollback_evidence = _run_relocated_operation(
        python,
        environment_root=environment_root,
        relocated_host=relocated_host,
        expected_version=candidate_version,
        phase="adopter-rollback",
        expect_candidate_module=True,
        expected_isolation_findings=(
            "isolation:service-endpoint",
            "isolation:work-subject",
            "isolation:workstream-focus-hook-absent",
        ),
    )

    assert baseline_evidence["candidate_module_present"] is False
    assert upgraded_evidence["candidate_module_present"] is True
    assert rollback_evidence["candidate_module_present"] is True
    assert rollback_evidence["package_version"] == candidate_version
    assert _run_checked(["git", "status", "--porcelain"], cwd=relocated_app).stdout.strip() == ""
    assert (AGENT_RED_ROOT / "application.toml").read_bytes() == original_marker
    assert relocated_marker.read_bytes() != original_marker
    assert relocated_app.resolve() != AGENT_RED_ROOT.resolve()


def test_agent_red_operational_surfaces_have_no_out_of_root_dependencies() -> None:
    """Live code/config has neither external filesystem links nor host-path literals."""

    assert _external_link_findings(AGENT_RED_ROOT) == []
    assert _external_path_findings(AGENT_RED_ROOT) == []


def test_external_path_scan_is_not_vacuous(tmp_path: Path) -> None:
    app_root = tmp_path / "Agent_Red"
    source = app_root / "src" / "configuration.py"
    source.parent.mkdir(parents=True)
    source.write_text('MODEL_PATH = r"C:\\external-models\\agent-red.bin"\n', encoding="utf-8")

    findings = _external_path_findings(app_root)

    assert len(findings) == 1
    assert "C:\\external-models\\agent-red.bin" in findings[0]

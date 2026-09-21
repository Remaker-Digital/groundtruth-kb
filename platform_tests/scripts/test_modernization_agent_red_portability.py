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
import socket
import subprocess
import sys
import textwrap
import threading
import time
import tomllib
import venv
import zipfile
from collections.abc import Iterator
from importlib import metadata
from pathlib import Path, PureWindowsPath

import pytest
import uvicorn
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from packaging.requirements import Requirement

from platform_tests.groundtruth_kb.native_fixtures import native as native

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_RED_ROOT = REPO_ROOT / "applications" / "Agent_Red"
PLATFORM_PRODUCT_ROOT = REPO_ROOT / "groundtruth-kb"
PRIOR_PACKAGE_FIXTURE = (
    REPO_ROOT / "platform_tests" / "fixtures" / "modernization" / "agent-red-prior-supported-package.json"
)


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
    {
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }
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
    allowed_fixture_roots = tuple(
        os.path.normcase(os.path.abspath(value))
        for value in (os.environ["GTKB_RELOCATED_HOST"], sys.prefix)
    )

    def under_root(value, root):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        normalized = os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(value))))
        return normalized == root or normalized.startswith(root + os.sep)

    def denied_source(value):
        return under_root(value, source_root) and not any(
            under_root(value, allowed_root) for allowed_root in allowed_fixture_roots
        )

    sys.path[:] = [entry for entry in sys.path if not entry or not denied_source(entry)]

    def deny_source_host_reads(event, args):
        path = None
        if event == "open" and args:
            path = args[0]
        elif event in {"os.listdir", "os.scandir", "os.chdir"} and args:
            path = args[0]
        if path is not None and denied_source(path):
            raise RuntimeError(f"source-host dependency denied: {path}")

    assert not denied_source(os.environ["GTKB_RELOCATED_HOST"])
    assert not denied_source(sys.prefix)
    assert denied_source(source_root)
    assert denied_source(os.path.join(source_root, "groundtruth-kb", "src"))
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
    exercise_agent_red_runtime = os.environ["GTKB_PROBE_AGENT_RED_RUNTIME"] == "1"

    sys.path.insert(0, str(app_root))

    import groundtruth_kb
    from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization
    from groundtruth_kb.isolation.validation import validate_self_completion_preflight
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    package_origin = Path(groundtruth_kb.__file__).resolve()
    assert package_origin.is_relative_to(expected_install), (package_origin, expected_install)
    assert groundtruth_kb.__version__ == expected_version
    assert not any(entry and denied_source(entry) for entry in sys.path)
    candidate_module_present = importlib.util.find_spec("groundtruth_kb.native_authority") is not None
    assert candidate_module_present is expected_candidate_module

    validate_self_completion_preflight(host_root, "Agent_Red")
    minimization = validate_app_root_minimization(app_root, project_root=host_root)
    assert minimization.ok, minimization.first_error_message(limit=10)
    checks = run_isolation_checks(app_root, "dual-agent", product_root=package_origin.parent)
    unacceptable = {
        check.name: {"status": check.status, "message": check.message}
        for check in checks
        if check.status in {"error", "fail", "warning"}
    }
    assert set(unacceptable) == expected_isolation_findings, unacceptable

    app_origin = None
    if exercise_agent_red_runtime:
        from src.app.factory import create_app

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
                "agent_red_origin": str(app_origin) if app_origin else None,
                "platform_consumption": "pass" if exercise_agent_red_runtime else "not_exercised",
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

    if not exercise_agent_red_runtime:
        raise SystemExit(0)

    import pytest

    raise SystemExit(
        pytest.main(
            [
                "-q",
                "-p",
                "no:cacheprovider",
                "-c",
                os.devnull,
                "--rootdir",
                str(app_root),
                "--confcutdir",
                str(app_root),
                *os.environ["GTKB_TEST_NODES"].split("|"),
            ]
        )
    )
    """
).strip()

_NATIVE_LIFECYCLE_DRIVER = textwrap.dedent(
    r"""
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path

    source_root = os.path.normcase(os.path.abspath(os.environ["GTKB_SOURCE_ROOT"]))
    allowed_fixture_roots = tuple(
        os.path.normcase(os.path.abspath(value))
        for value in (os.environ["GTKB_RELOCATED_HOST"], sys.prefix)
    )

    def under_root(value, root):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        normalized = os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(value))))
        return normalized == root or normalized.startswith(root + os.sep)

    def denied_source(value):
        return under_root(value, source_root) and not any(
            under_root(value, allowed_root) for allowed_root in allowed_fixture_roots
        )

    sys.path[:] = [entry for entry in sys.path if not entry or not denied_source(entry)]

    def deny_source_host_reads(event, args):
        path = None
        if event == "open" and args:
            path = args[0]
        elif event in {"os.listdir", "os.scandir", "os.chdir"} and args:
            path = args[0]
        if path is not None and denied_source(path):
            raise RuntimeError(f"source-host dependency denied: {path}")

    assert not denied_source(os.environ["GTKB_RELOCATED_HOST"])
    assert not denied_source(sys.prefix)
    assert denied_source(source_root)
    assert denied_source(os.path.join(source_root, "groundtruth-kb", "src"))
    sys.addaudithook(deny_source_host_reads)

    import groundtruth_kb
    from groundtruth_kb.project.application_upgrade import (
        UpgradeOptions,
        apply_upgrade,
        plan_upgrade,
        recover,
        recovery_plan,
    )

    host_root = Path(os.environ["GTKB_RELOCATED_HOST"]).resolve()
    app_root = host_root / "applications" / "Agent_Red"
    evidence_path = Path(os.environ["GTKB_EVIDENCE_PATH"])
    operation = os.environ["GTKB_LIFECYCLE_OPERATION"]
    package_origin = Path(groundtruth_kb.__file__).resolve()
    assert package_origin.is_relative_to(Path(sys.prefix).resolve())
    assert not denied_source(package_origin)
    options = UpgradeOptions(
        application="Agent_Red",
        project_id=os.environ["GTKB_PROJECT_ID"],
        gt_kb_root=host_root,
        authority_url=os.environ["GTKB_AUTHORITY_URL"],
    )

    def head():
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=app_root, check=True, capture_output=True, text=True
        ).stdout.strip()

    before = head()
    if operation == "preview":
        plan = plan_upgrade(options)
        evidence = {"plan": plan.to_json_dict(), "writes": sorted(plan.writes), "removes": sorted(plan.removes)}
    elif operation == "apply":
        plan = plan_upgrade(options)
        result = apply_upgrade(plan)
        evidence = {"plan": plan.to_json_dict(), "result": result}
    elif operation == "recover":
        plan = recovery_plan(options)
        result = recover(options)
        evidence = {"recovery_plan": plan, "result": result}
    else:
        raise AssertionError(f"unknown lifecycle operation: {operation}")
    evidence.update(
        {
            "operation": operation,
            "package_origin": str(package_origin),
            "package_version": groundtruth_kb.__version__,
            "source_host_read_guard": "active",
            "head_before": before,
            "head_after": head(),
            "receipts_dir_exists": (app_root / ".claude" / "upgrade-receipts").exists(),
        }
    )
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    """
).strip()


def _validate_app_root(app_root: Path, project_root: Path):
    from groundtruth_kb.isolation.app_root_minimization import (
        validate_app_root_minimization,
    )

    return validate_app_root_minimization(app_root, project_root=project_root)


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
    assert by_name["isolation:hook-settings-structure"].status == "pass"
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
    assert fixture["candidate_only_module"] == "groundtruth_kb.native_authority"
    wheel_name = str(fixture["wheel_file"])
    assert Path(wheel_name).name == wheel_name
    wheel = PRIOR_PACKAGE_FIXTURE.parent / wheel_name
    assert wheel.is_file(), f"in-repo predecessor wheel is missing: {wheel}"
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == str(fixture["wheel_sha256"])
    fixture["wheel_path"] = wheel
    return fixture


def _wheel_contains_module(wheel: Path, module: str) -> bool:
    module_root = module.replace(".", "/")
    with zipfile.ZipFile(wheel) as archive:
        return any(name in {module_root + ".py", module_root + "/__init__.py"} for name in archive.namelist())


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
    _materialize_distributions([_BUILD_BACKEND_REQUIREMENT], build_site)
    return build_site


def _materialize_distributions(requirements: list[str], site: Path) -> set[str]:
    """Copy the closure of the named distributions from this interpreter into ``site`` (offline, versions checked)."""
    pending = [Requirement(item) for item in requirements]
    copied: set[str] = set()
    while pending:
        requirement = pending.pop()
        # A dependency declared for an extra (``psycopg[binary]`` -> ``psycopg-binary; extra == "binary"``) is
        # part of the closure only when that extra was requested by the depending distribution.
        extras = getattr(requirement, "_requested_extras", set())
        if requirement.marker is not None and not (
            requirement.marker.evaluate() or any(requirement.marker.evaluate({"extra": extra}) for extra in extras)
        ):
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
            target = site / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        copied.add(key)
        for item in distribution.requires or ():
            child = Requirement(item)
            child._requested_extras = set(requirement.extras)  # type: ignore[attr-defined]
            pending.append(child)
    return copied


def _materialize_runtime_dependencies(source_root: Path, environment_root: Path) -> set[str]:
    """The clean environment receives the package's declared runtime dependency closure, never the host's path."""
    config = tomllib.loads((source_root / "pyproject.toml").read_text(encoding="utf-8"))
    site = environment_root / ("Lib/site-packages" if os.name == "nt" else "lib/site-packages")
    if os.name != "nt":
        site = next(environment_root.glob("lib/python*/site-packages"))
    return _materialize_distributions(list(config["project"]["dependencies"]), site)


def _venv_python(environment_root: Path) -> Path:
    relative = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    return environment_root / relative


def _install_wheel(python: Path, wheel: Path, *, replace_existing: bool = False) -> None:
    """Install the supplied wheel into this test environment, ignoring host metadata."""
    command = [
        str(python),
        "-I",
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-deps",
        "--no-index",
    ]
    if replace_existing:
        command.append("--force-reinstall")
    else:
        # An inherited/system distribution with the same version is not an
        # installation in this newly created environment. Leave that copy alone.
        command.append("--ignore-installed")
    command.append(str(wheel))
    env = {key: value for key, value in os.environ.items() if not key.startswith("PIP_")}
    env.pop("PYTHONPATH", None)
    env["PIP_CONFIG_FILE"] = os.devnull
    _run_checked(command, cwd=wheel.parent, env=env, timeout=180)


def _run_relocated_operation(
    python: Path,
    *,
    environment_root: Path,
    relocated_host: Path,
    expected_version: str,
    phase: str,
    expect_candidate_module: bool,
    expected_isolation_findings: tuple[str, ...] = (),
    agent_red_runtime: bool = True,
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
            "GTKB_PROBE_AGENT_RED_RUNTIME": "1" if agent_red_runtime else "0",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONPATH": "",
        }
    )
    _run_checked(
        [str(python), str(probe)],
        cwd=relocated_host / "applications" / "Agent_Red",
        env=env,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["phase"] == phase
    assert evidence["package_version"] == expected_version
    assert Path(evidence["package_origin"]).resolve().is_relative_to(environment_root.resolve())
    if agent_red_runtime:
        assert (
            Path(evidence["agent_red_origin"])
            .resolve()
            .is_relative_to((relocated_host / "applications" / "Agent_Red").resolve())
        )
        assert evidence["platform_consumption"] == "pass"
    else:
        assert evidence["agent_red_origin"] is None and evidence["platform_consumption"] == "not_exercised"
    assert evidence["source_host_read_guard"] == "active"
    assert evidence["candidate_module_present"] is expect_candidate_module
    assert evidence["isolation_findings"] == sorted(expected_isolation_findings)
    return evidence


def _run_lifecycle_operation(
    python: Path,
    *,
    environment_root: Path,
    relocated_host: Path,
    authority_url: str,
    project_id: str,
    operation: str,
) -> dict[str, object]:
    driver = relocated_host / "portability-lifecycle-driver.py"
    evidence_path = relocated_host / f"portability-{operation}-evidence.json"
    driver.write_text(_NATIVE_LIFECYCLE_DRIVER + "\n", encoding="utf-8")
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith(("PG", "GT_POSTGRES_", "GIT_"))
        and key not in {"GT_AUTHORITY_URL", "GT_PROJECT_ROOT"}
    }
    env.update(
        {
            "GTKB_SOURCE_ROOT": str(REPO_ROOT),
            "GTKB_RELOCATED_HOST": str(relocated_host),
            "GTKB_AUTHORITY_URL": authority_url,
            "GTKB_PROJECT_ID": project_id,
            "GTKB_EVIDENCE_PATH": str(evidence_path),
            "GTKB_LIFECYCLE_OPERATION": operation,
            "PYTHONPATH": "",
        }
    )
    _run_checked([str(python), str(driver)], cwd=relocated_host, env=env, timeout=180)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["operation"] == operation
    assert evidence["source_host_read_guard"] == "active"
    assert Path(str(evidence["package_origin"])).resolve().is_relative_to(environment_root.resolve())
    assert evidence["receipts_dir_exists"] is False
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
                "classification": "runtime_data" if name == ".git" else "authoritative_input",
                "purpose": "Portability fixture for the canonical GT-KB adopter migration and rollback lifecycle.",
            }
        )
    artifacts.sort(key=lambda entry: entry["name"])
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _stage_relocated_host(relocated_host: Path, authority_url: str) -> None:
    """Give the relocated host what the native upgrade reads: baseline, projector, catalog and its authority."""
    shutil.copytree(
        REPO_ROOT / ".harness-baseline-configuration",
        relocated_host / ".harness-baseline-configuration",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.lock"),
    )
    shutil.copytree(
        REPO_ROOT / "scripts/harness_projection",
        relocated_host / "scripts/harness_projection",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for script in sorted(REPO_ROOT.glob("scripts/*_hook_adapter.py")) + [
        REPO_ROOT / "scripts/implementation_start_gate.py"
    ]:
        if script.is_file():
            shutil.copyfile(script, relocated_host / "scripts" / script.name)
    shutil.copyfile(REPO_ROOT / "pyproject.toml", relocated_host / "pyproject.toml")
    (relocated_host / ".githooks").mkdir()
    shutil.copyfile(REPO_ROOT / ".githooks/reference-transaction", relocated_host / ".githooks/reference-transaction")
    (relocated_host / "applications" / "registry.toml").write_text(
        '[applications]\nAgent_Red={slot="Agent_Red"}\n', encoding="utf-8"
    )
    (relocated_host / "groundtruth.toml").write_text(
        f'[groundtruth]\nproject_root="{relocated_host.as_posix()}"\nauthority_url="{authority_url}"\n',
        encoding="utf-8",
    )


def _initialize_relocated_application(app_root: Path, authority_url: str) -> dict[str, bytes]:
    """The relocated application selects the relocated host's authority; its own files are the baseline to preserve."""
    _register_relocated_root_files(app_root, (".git", ".gitignore", "groundtruth.toml"))
    (app_root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    (app_root / "groundtruth.toml").write_text(
        f'[groundtruth]\nproject_root="{app_root.as_posix()}"\nauthority_url="{authority_url}"\n', encoding="utf-8"
    )
    state_file = app_root / "config" / "portability-state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps({"tenant": "agent-red", "lifecycle": "relocated"}, indent=2) + "\n", encoding="utf-8"
    )
    return _snapshot_application_state(app_root)


def _snapshot_application_state(app_root: Path) -> dict[str, bytes]:
    return {
        "marker": (app_root / "application.toml").read_bytes(),
        "state_file": (app_root / "config" / "portability-state.json").read_bytes(),
        "config": (app_root / "groundtruth.toml").read_bytes(),
        "factory": (app_root / "src" / "app" / "factory.py").read_bytes(),
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


@pytest.mark.timeout(600)
def test_agent_red_survives_relocation_and_has_an_independent_lifecycle(
    relocated_agent_red: tuple[Path, Path],
    native,
    tmp_path: Path,
) -> None:
    """A relocated Agent Red runs through clean install, native upgrade preview/apply, commit and recovery."""

    relocated_host, relocated_app = relocated_agent_red
    original_marker = (AGENT_RED_ROOT / "application.toml").read_bytes()
    relocated_marker = relocated_app / "application.toml"
    relocated_marker.write_bytes(original_marker + b"\n# independent relocated lifecycle\n")

    service, _client, _schema, _service_name = native
    project_id = "PROJECT-AGENT-RED"
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        authority_url = f"http://127.0.0.1:{port}"
        # The relocated host is the authority's project root: its catalog registers the relocated application.
        _stage_relocated_host(relocated_host, authority_url)
        baseline_state = _initialize_relocated_application(relocated_app, authority_url)
        _initialize_relocated_application_repository(relocated_app)
        app = create_authority_app(service, project_root=relocated_host)
        client = TestClient(app)
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        while not server.started and worker.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        try:
            response = client.put(
                f"/v1/projects/{project_id}",
                json={
                    "expected_version": 0,
                    "actor": "portability",
                    "reason": "Relocated reference adopter",
                    "kind": "project",
                    "fields": {"name": "Agent Red (relocated)", "repository_ref": "application:Agent_Red"},
                },
            )
            assert response.status_code == 200, response.text
            committed_head = _run_checked(["git", "rev-parse", "HEAD"], cwd=relocated_app).stdout.strip()

            candidate_source = tmp_path / "candidate-package"
            _copy_package_build_source(candidate_source)
            candidate_init = candidate_source / "src" / "groundtruth_kb" / "__init__.py"
            version_match = _PACKAGE_VERSION.search(candidate_init.read_text(encoding="utf-8"))
            assert version_match is not None, "GT-KB package version declaration is missing"
            candidate_version = version_match.group("version")
            candidate_wheel = _build_wheel(candidate_source, tmp_path / "candidate-wheel")
            environment_root = tmp_path / "clean-gtkb-install"
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment_root)
            python = _venv_python(environment_root)
            _install_wheel(python, candidate_wheel)
            _materialize_runtime_dependencies(candidate_source, environment_root)

            install_evidence = _run_relocated_operation(
                python,
                environment_root=environment_root,
                relocated_host=relocated_host,
                expected_version=candidate_version,
                phase="clean-install",
                expect_candidate_module=True,
                agent_red_runtime=False,
            )

            preview = _run_lifecycle_operation(
                python,
                environment_root=environment_root,
                relocated_host=relocated_host,
                authority_url=authority_url,
                project_id=project_id,
                operation="preview",
            )
            assert preview["plan"]["project_id"] == project_id
            assert preview["plan"]["repository_ref"] == "application:Agent_Red"
            assert preview["head_after"] == committed_head
            assert _snapshot_application_state(relocated_app) == baseline_state, "a preview changes nothing"

            applied = _run_lifecycle_operation(
                python,
                environment_root=environment_root,
                relocated_host=relocated_host,
                authority_url=authority_url,
                project_id=project_id,
                operation="apply",
            )
            assert applied["head_after"] == committed_head, "the native upgrade never commits"
            assert applied["result"]["commits"] == 0
            assert _snapshot_application_state(relocated_app) == baseline_state, "application-owned files are preserved"
            written = set(applied["result"]["written"])
            assert written == set(preview["writes"]) and written, (written, preview["writes"])
            assert all(not path.startswith(("src/", "tests/", "config/")) for path in written), written
            _run_checked(["git", "add", "-A"], cwd=relocated_app)
            _run_checked(
                ["git", "commit", "-qm", "relocated Agent Red at the current host baseline"], cwd=relocated_app
            )
            upgraded_head = _run_checked(["git", "rev-parse", "HEAD"], cwd=relocated_app).stdout.strip()
            assert upgraded_head != committed_head

            current = _run_lifecycle_operation(
                python,
                environment_root=environment_root,
                relocated_host=relocated_host,
                authority_url=authority_url,
                project_id=project_id,
                operation="preview",
            )
            assert current["plan"]["changes"] == 0, current["plan"]
            tracked = set(_run_checked(["git", "ls-files"], cwd=relocated_app).stdout.splitlines())
            committed_managed = sorted(written & tracked)
            assert committed_managed, (written, sorted(tracked)[:20])
            drifted = committed_managed[0]
            drifted_path = relocated_app / drifted
            committed_bytes = drifted_path.read_bytes()
            drifted_path.write_bytes(b"# local drift that recovery restores\n")
            recovered = _run_lifecycle_operation(
                python,
                environment_root=environment_root,
                relocated_host=relocated_host,
                authority_url=authority_url,
                project_id=project_id,
                operation="recover",
            )
            assert drifted in set(recovered["result"]["restore"]), recovered["result"]
            assert recovered["result"]["status"] == "restored"
            assert drifted_path.read_bytes() == committed_bytes
            assert recovered["head_after"] == upgraded_head
            assert _run_checked(["git", "status", "--porcelain"], cwd=relocated_app).stdout.strip() == ""

            upgraded_evidence = _run_relocated_operation(
                python,
                environment_root=environment_root,
                relocated_host=relocated_host,
                expected_version=candidate_version,
                phase="adopter-upgraded",
                expect_candidate_module=True,
                agent_red_runtime=False,
            )
        finally:
            server.should_exit = True
            worker.join(timeout=10)
    assert install_evidence["candidate_module_present"] is True
    assert upgraded_evidence["candidate_module_present"] is True
    assert upgraded_evidence["package_version"] == candidate_version
    assert (AGENT_RED_ROOT / "application.toml").read_bytes() == original_marker
    assert relocated_marker.read_bytes() != original_marker
    assert relocated_app.resolve() != AGENT_RED_ROOT.resolve()


def _agent_red_runtime_requirements() -> list[str]:
    """Agent Red's declared runtime requirements and the test runner its operational tests need."""
    requirements = []
    for line in (AGENT_RED_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line and not line.startswith("-"):
            requirements.append(line)
    return requirements + ["pytest>=8.0", "pytest-asyncio>=0.24.0", "pytest-timeout>=2.3.0", "httpx>=0.27.0"]


def _missing_distributions(requirements: list[str]) -> list[str]:
    missing = []
    for item in requirements:
        requirement = Requirement(item)
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue
        try:
            version = metadata.version(requirement.name)
        except metadata.PackageNotFoundError:
            missing.append(item)
            continue
        if not requirement.specifier.contains(version, prereleases=True):
            missing.append(f"{item} (installed {version})")
    return missing


@pytest.mark.timeout(600)
def test_relocated_agent_red_runtime_operates_on_the_installed_platform(
    relocated_agent_red: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    """Agent Red's own application factory and operational tests run in the relocated, clean installation.

    Agent Red's runtime closure is its own declaration (requirements.txt); this case materializes that closure
    from the running interpreter into the clean environment and is skipped, visibly, where the interpreter does not
    carry it. The GT-KB lifecycle case above does not depend on Agent Red's runtime.
    """
    requirements = _agent_red_runtime_requirements()
    missing = _missing_distributions(requirements)
    if missing:
        pytest.skip("Agent Red's declared runtime closure is not installed in this interpreter: " + ", ".join(missing))
    relocated_host, relocated_app = relocated_agent_red
    _stage_relocated_host(relocated_host, "http://127.0.0.1:9")
    _initialize_relocated_application(relocated_app, "http://127.0.0.1:9")
    _initialize_relocated_application_repository(relocated_app)
    candidate_source = tmp_path / "candidate-package"
    _copy_package_build_source(candidate_source)
    version_match = _PACKAGE_VERSION.search(
        (candidate_source / "src/groundtruth_kb/__init__.py").read_text(encoding="utf-8")
    )
    assert version_match is not None
    candidate_wheel = _build_wheel(candidate_source, tmp_path / "candidate-wheel")
    environment_root = tmp_path / "clean-gtkb-install"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment_root)
    python = _venv_python(environment_root)
    _install_wheel(python, candidate_wheel)
    _materialize_runtime_dependencies(candidate_source, environment_root)
    site = (
        environment_root / "Lib/site-packages"
        if os.name == "nt"
        else next(environment_root.glob("lib/python*/site-packages"))
    )
    _materialize_distributions(requirements, site)
    evidence = _run_relocated_operation(
        python,
        environment_root=environment_root,
        relocated_host=relocated_host,
        expected_version=version_match.group("version"),
        phase="agent-red-runtime",
        expect_candidate_module=True,
        agent_red_runtime=True,
    )
    assert evidence["platform_consumption"] == "pass"


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


@pytest.mark.parametrize("replace_existing", [False, True])
def test_portability_wheel_install_ignores_inherited_same_version_distribution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, replace_existing: bool
) -> None:
    """A real same-version distribution on PYTHONPATH must not satisfy local installation."""
    prior = _load_prior_package_fixture()
    wheel = Path(prior["wheel_path"])
    inherited = tmp_path / "inherited-package"
    inherited.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        for entry in archive.infolist():
            target = inherited / entry.filename
            assert target.resolve().is_relative_to(inherited.resolve())
        archive.extractall(inherited)
        expected_init = archive.read("groundtruth_kb/__init__.py")
    before = {
        p.relative_to(inherited).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in inherited.rglob("*")
        if p.is_file()
    }
    environment = tmp_path / "isolated-install"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment)
    python = _venv_python(environment)
    monkeypatch.setenv("PYTHONPATH", str(inherited))
    _install_wheel(python, wheel)
    relative_site = (
        Path("Lib/site-packages")
        if os.name == "nt"
        else Path(
            "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}",
            "site-packages",
        )
    )
    installed_init = environment / relative_site / "groundtruth_kb/__init__.py"
    assert installed_init.read_bytes() == expected_init
    if replace_existing:
        installed_init.write_bytes(expected_init + b"\n# altered disposable installation\n")
        _install_wheel(python, wheel, replace_existing=True)
        assert installed_init.read_bytes() == expected_init
    probe = _run_checked(
        [
            str(python),
            "-I",
            "-c",
            "import json, groundtruth_kb; from importlib.metadata import version; print(json.dumps({'origin':groundtruth_kb.__file__,'version':version('groundtruth-kb')}))",
        ],
        cwd=tmp_path,
    )
    observed = json.loads(probe.stdout)
    assert Path(observed["origin"]).resolve().is_relative_to(environment.resolve())
    assert observed["version"] == prior["package_version"]
    assert before == {
        p.relative_to(inherited).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in inherited.rglob("*")
        if p.is_file()
    }

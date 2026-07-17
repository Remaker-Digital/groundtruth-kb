"""Fresh-host worker acceptance for startup, context, authority, and discovery."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
import tomllib
import zipfile
from importlib import metadata
from pathlib import Path

import pytest
from packaging.requirements import Requirement

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb"
BUILD_PROJECT = REPO_ROOT / "groundtruth-kb"
BUILD_BACKEND_REQUIREMENT = "hatchling==1.29.0"

OFFLINE_BUILD = textwrap.dedent(
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

COPIED_CONFIGS = (
    "config/agent-control/activity-disposition-profiles.toml",
    "config/agent-control/activity-envelope-sharding.toml",
    "config/agent-control/command-surface.toml",
    "config/agent-control/system-interface-map.toml",
    "config/governance/canonical-terms-sync.toml",
    "config/governance/project-authorization-operation-taxonomy.toml",
    "config/registry/sot-artifacts.toml",
)

PROBE = r"""from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

HOST = Path(__file__).resolve().parent
COPIED_SRC = (HOST / "groundtruth-kb" / "src").resolve()
sys.path.insert(0, str(COPIED_SRC))

from groundtruth_kb.context.manifest import assemble_context_manifest, resolve_context_registry
from groundtruth_kb.governance.project_authorization_operation_time import (
    evaluate_envelope,
    load_operation_taxonomy,
)
from groundtruth_kb.project.sot_registry import default_registry_path, load_toml
from groundtruth_kb.session.envelope import (
    ensure_worker_session,
    open_topic,
    resolve_worker_role_provenance,
)

session_id = "fresh-worker-001"
ensure_worker_session(
    HOST,
    harness_name="codex",
    session_id=session_id,
    role="prime-builder",
    role_source="dispatcher_composition",
    dispatch_run_id="fresh-dispatch-001",
)
provenance = resolve_worker_role_provenance(
    HOST,
    current_session_id=session_id,
    harness_name="codex",
)
topic = open_topic(HOST, "build", harness_name="codex")
fixed = datetime(2026, 7, 13, tzinfo=UTC)
manifest = assemble_context_manifest(
    activity="build",
    role=str(provenance["role"]),
    generated_at=fixed,
    project_root=HOST,
)
registry_resolution = resolve_context_registry(project_root=HOST)
authorization = {
    "id": "PAUTH-FRESH-WORKER",
    "version": 1,
    "allowed_mutation_classes": ["source", "test"],
    "forbidden_operations": [],
    "included_work_item_ids": ["WI-FRESH-WORKER"],
    "excluded_work_item_ids": [],
    "included_spec_ids": ["SPEC-FRESH-WORKER"],
    "excluded_spec_ids": [],
}
authority = evaluate_envelope(
    authorization,
    requested_operation="protected_mutation",
    target_paths=["scripts/fresh_worker.py", "platform_tests/scripts/test_fresh_worker.py"],
    decision_time=fixed,
    taxonomy=load_operation_taxonomy(HOST),
)
services = load_toml(default_registry_path(HOST))
service_by_id = {service.id: service for service in services}
required_services = {"sot-registry-toml", "harness-registry", "membase-pauths"}
missing_services = sorted(required_services - set(service_by_id))
groundtruth_modules = {
    name: str(Path(module.__file__).resolve())
    for name, module in sys.modules.items()
    if name == "groundtruth_kb" or name.startswith("groundtruth_kb.")
    if getattr(module, "__file__", None)
}
outside_copy = {
    name: path
    for name, path in groundtruth_modules.items()
    if not Path(path).is_relative_to(COPIED_SRC)
}
host_state_absent = all(
    not path.exists()
    for path in (HOST / "groundtruth.db", HOST / ".gtkb-state", HOST / "memory")
)
result = {
    "startup": {
        "session_id": provenance["session_id"],
        "harness_id": provenance["harness_id"],
        "role": provenance["role"],
        "source": provenance["role_resolution_source"],
    },
    "context": {
        "activity": manifest["active_activity"],
        "role": manifest["role_bootstrap"]["role"],
        "items": len(manifest["items"]),
        "omissions": manifest["omissions"],
        "registry_origin": registry_resolution.origin,
    },
    "authority": authority.as_dict(),
    "discovery": {
        "registered_services": len(services),
        "missing_required": missing_services,
        "build_route": topic["route_target"],
        "mutation_routes": {
            service_id: service_by_id[service_id].mutation_api
            for service_id in sorted(required_services)
            if service_id in service_by_id
        },
    },
    "isolation": {
        "cwd_is_host": Path.cwd().resolve() == HOST,
        "host_state_absent": host_state_absent,
        "outside_copy": outside_copy,
    },
}
assert result["startup"] == {
    "session_id": session_id,
    "harness_id": "FRESH-A",
    "role": "prime-builder",
    "source": "dispatcher_composition",
}
assert result["context"]["activity"] == "build"
assert result["context"]["role"] == "prime-builder"
assert result["context"]["items"] == 14
assert result["context"]["omissions"] == []
assert result["context"]["registry_origin"] == "packaged_default"
assert result["authority"]["allowed"] is True
assert result["discovery"]["missing_required"] == []
assert result["discovery"]["build_route"] == "build-package-scaffold-service"
assert all(result["discovery"]["mutation_routes"].values())
assert result["isolation"] == {
    "cwd_is_host": True,
    "host_state_absent": True,
    "outside_copy": {},
}
print(json.dumps(result, sort_keys=True))
"""


def _copy_product_asset(host: Path, relative_path: str) -> None:
    source = REPO_ROOT / relative_path
    target = host / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


@pytest.fixture
def fresh_host(tmp_path: Path) -> Path:
    host = tmp_path / "fresh-gtkb-host"
    package_target = host / "groundtruth-kb" / "src" / "groundtruth_kb"
    shutil.copytree(
        PACKAGE_SRC,
        package_target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    for relative_path in COPIED_CONFIGS:
        _copy_product_asset(host, relative_path)

    harness_state = host / "harness-state"
    harness_state.mkdir(parents=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "fresh-host fixture",
                "harnesses": {"codex": {"id": "FRESH-A"}},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "fresh-host fixture",
                "harnesses": [
                    {
                        "id": "FRESH-A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (host / "fresh_worker_probe.py").write_text(PROBE, encoding="utf-8")
    return host


def _isolated_environment(host: Path) -> dict[str, str]:
    controlled_temp = host / "runtime-temp"
    controlled_home = host / "runtime-home"
    controlled_temp.mkdir()
    controlled_home.mkdir()
    environment = {
        "GTKB_PROJECT_ROOT": str(host),
        "HOME": str(controlled_home),
        "USERPROFILE": str(controlled_home),
        "TEMP": str(controlled_temp),
        "TMP": str(controlled_temp),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PIP_NO_INDEX": "1",
        "UV_OFFLINE": "1",
    }
    for name in ("PATH", "PATHEXT", "SYSTEMROOT", "WINDIR"):
        if value := os.environ.get(name):
            environment[name] = value
    return environment


def _build_wheel_offline(project_root: Path, output_dir: Path) -> Path:
    config = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    requirement = config["build-system"]["requires"]
    assert requirement == [BUILD_BACKEND_REQUIREMENT]
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
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            OFFLINE_BUILD,
            str(project_root),
            str(output_dir),
            str(build_site),
        ],
        cwd=project_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    wheels = list(output_dir.glob("groundtruth_kb-*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def _materialize_build_backend(output_dir: Path) -> Path:
    """Copy the declared backend closure into the only non-stdlib import path."""
    build_site = output_dir / "build-backend-site"
    build_site.mkdir(parents=True)
    pending = [Requirement(BUILD_BACKEND_REQUIREMENT)]
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


def _run_probe(host: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(host / "fresh_worker_probe.py")],
        cwd=host,
        env=_isolated_environment(host),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_fresh_worker_bootstraps_from_only_copied_product_assets(fresh_host: Path) -> None:
    result = _run_probe(fresh_host)

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["startup"]["harness_id"] == "FRESH-A"
    assert payload["context"]["items"] == 14
    assert payload["context"]["registry_origin"] == "packaged_default"
    assert payload["authority"]["reason_code"] == "allowed"
    assert payload["discovery"]["registered_services"] >= 3
    assert payload["isolation"]["outside_copy"] == {}


def test_project_context_override_cannot_fall_back_to_packaged_assets(fresh_host: Path) -> None:
    override = fresh_host / "config" / "registry" / "context-manifests.toml"
    override.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "config" / "registry" / "context-manifests.toml", override)
    missing = fresh_host / "config" / "governance" / "canonical-terms-sync.toml"
    missing.unlink()

    result = _run_probe(fresh_host)

    assert result.returncode != 0
    combined = f"{result.stdout}\n{result.stderr}"
    assert "source is missing" in combined
    assert "baseline.glossary" in combined
    assert "recovery=gt canonical-terms list" in combined
    assert str(REPO_ROOT / "config" / "governance" / "canonical-terms-sync.toml") not in combined


@pytest.fixture(scope="session")
def built_groundtruth_wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output_dir = tmp_path_factory.mktemp("groundtruth-wheel")
    return _build_wheel_offline(BUILD_PROJECT, output_dir)


def _venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def test_built_wheel_assembles_context_without_source_tree_or_root_config(
    built_groundtruth_wheel: Path,
    tmp_path: Path,
) -> None:
    expected_resources = {
        "groundtruth_kb/context/registries/v1/context-manifests.toml",
        "groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml",
        "groundtruth_kb/context/registries/v1/config/agent-control/activity-envelope-sharding.toml",
        "groundtruth_kb/context/registries/v1/config/governance/canonical-terms-sync.toml",
    }
    with zipfile.ZipFile(built_groundtruth_wheel) as wheel:
        wheel_entries = wheel.namelist()
        assert expected_resources <= set(wheel_entries)
        assert all(wheel_entries.count(resource) == 1 for resource in expected_resources)

    venv = tmp_path / "venv"
    create = subprocess.run(
        [sys.executable, "-m", "venv", "--system-site-packages", str(venv)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert create.returncode == 0, create.stderr or create.stdout
    python = _venv_python(venv)
    install = subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            str(built_groundtruth_wheel),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert install.returncode == 0, install.stderr or install.stdout

    host = tmp_path / "empty-project"
    host.mkdir()
    probe = r"""
import json
from datetime import UTC, datetime
from pathlib import Path
import groundtruth_kb
from groundtruth_kb.context.manifest import assemble_context_manifest, resolve_context_registry

host = Path.cwd()
resolution = resolve_context_registry(project_root=host)
manifest = assemble_context_manifest(
    activity="build",
    role="Prime Builder",
    generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    project_root=host,
)
print(json.dumps({
    "module": str(Path(groundtruth_kb.__file__).resolve()),
    "origin": resolution.origin,
    "registry_version": manifest["registry_version"],
    "items": len(manifest["items"]),
    "root_config_exists": (host / "config").exists(),
}, sort_keys=True))
"""
    environment = _isolated_environment(host)
    result = subprocess.run(
        [str(python), "-I", "-c", probe],
        cwd=host,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload == {
        "items": 14,
        "module": payload["module"],
        "origin": "packaged_default",
        "registry_version": 1,
        "root_config_exists": False,
    }
    module_path = Path(payload["module"]).resolve()
    assert module_path.is_relative_to(venv.resolve())
    assert not module_path.is_relative_to((BUILD_PROJECT / "src").resolve())


def test_fresh_worker_cannot_fall_back_to_host_authority_taxonomy(fresh_host: Path) -> None:
    missing = fresh_host / "config" / "governance" / "project-authorization-operation-taxonomy.toml"
    missing.unlink()

    result = _run_probe(fresh_host)

    assert result.returncode != 0
    combined = f"{result.stdout}\n{result.stderr}"
    assert "operation taxonomy" in combined.lower()
    assert str(missing) in combined
    assert str(REPO_ROOT / "config" / "governance" / "project-authorization-operation-taxonomy.toml") not in combined

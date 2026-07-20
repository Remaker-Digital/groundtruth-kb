from __future__ import annotations

import os
import tomllib
import zipfile
from email.parser import BytesParser
from email.policy import compat32
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "groundtruth-kb"
PYPROJECT = PACKAGE_ROOT / "pyproject.toml"
LOCKFILE = PACKAGE_ROOT / "uv.lock"
MCP_NAME = canonicalize_name("mcp")


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _mcp_requirements(values: list[str]) -> list[Requirement]:
    return [requirement for value in values if canonicalize_name((requirement := Requirement(value)).name) == MCP_NAME]


def _build_wheel(output_dir: Path) -> Path:
    build_system = _load_toml(PYPROJECT)["build-system"]
    assert build_system["build-backend"] == "hatchling.build"
    assert build_system["requires"] == ["hatchling==1.29.0"]
    assert metadata.version("hatchling") == "1.29.0"

    from hatchling.build import build_wheel

    output_dir.mkdir(parents=True)
    prior_cwd = Path.cwd()
    try:
        os.chdir(PACKAGE_ROOT)
        wheel_name = build_wheel(str(output_dir))
    finally:
        os.chdir(prior_cwd)
    return output_dir / wheel_name


def test_mcp_is_an_unconditional_base_dependency_with_bridge_compatibility_extra() -> None:
    project = _load_toml(PYPROJECT)["project"]

    base_mcp = _mcp_requirements(project["dependencies"])
    assert len(base_mcp) == 1
    assert str(base_mcp[0].specifier) == ">=1.0"
    assert base_mcp[0].marker is None

    optional = project["optional-dependencies"]
    assert optional["bridge"] == []
    assert all(not _mcp_requirements(dependencies) for dependencies in optional.values())


def test_lock_projects_mcp_as_a_direct_unconditional_dependency() -> None:
    packages = _load_toml(LOCKFILE)["package"]
    project = next(package for package in packages if package["name"] == "groundtruth-kb")

    direct_mcp = [dependency for dependency in project["dependencies"] if dependency["name"] == "mcp"]
    assert direct_mcp == [{"name": "mcp"}]
    assert "bridge" not in project.get("optional-dependencies", {})

    metadata_mcp = [requirement for requirement in project["metadata"]["requires-dist"] if requirement["name"] == "mcp"]
    assert metadata_mcp == [{"name": "mcp", "specifier": ">=1.0"}]
    assert "bridge" in project["metadata"]["provides-extras"]


def test_built_wheel_metadata_requires_mcp_without_an_extra_marker(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path / "wheel")
    assert wheel.is_file()

    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        wheel_metadata = BytesParser(policy=compat32).parsebytes(archive.read(metadata_name))

    wheel_mcp = _mcp_requirements(wheel_metadata.get_all("Requires-Dist", []))
    assert len(wheel_mcp) == 1
    assert str(wheel_mcp[0].specifier) == ">=1.0"
    assert wheel_mcp[0].marker is None
    assert "bridge" in wheel_metadata.get_all("Provides-Extra", [])

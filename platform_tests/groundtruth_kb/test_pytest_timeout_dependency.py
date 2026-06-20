from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROOT_PYPROJECT = ROOT / "pyproject.toml"
GTKB_PYPROJECT = ROOT / "groundtruth-kb" / "pyproject.toml"
GTKB_LOCKFILE = ROOT / "groundtruth-kb" / "uv.lock"


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _dependency_names(dependencies: list[str]) -> set[str]:
    names: set[str] = set()
    for dependency in dependencies:
        name = dependency.split(";", 1)[0].split("[", 1)[0].split(">", 1)[0].split("<", 1)[0].split("=", 1)[0]
        names.add(name.strip().lower().replace("_", "-"))
    return names


def test_root_timeout_addopt_has_managed_pytest_timeout_dependency() -> None:
    root_pytest = _load_toml(ROOT_PYPROJECT)["tool"]["pytest"]["ini_options"]
    addopts = root_pytest.get("addopts", "")
    assert "--timeout=30" in addopts

    dev_dependencies = _load_toml(GTKB_PYPROJECT)["project"]["optional-dependencies"]["dev"]
    assert "pytest-timeout" in _dependency_names(dev_dependencies)

    lock_packages = {package["name"] for package in _load_toml(GTKB_LOCKFILE)["package"]}
    assert "pytest-timeout" in lock_packages

    assert importlib.util.find_spec("pytest_timeout") is not None

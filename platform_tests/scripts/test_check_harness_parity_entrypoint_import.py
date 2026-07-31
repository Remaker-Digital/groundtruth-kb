from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_harness_parity.py"


def _write_shadow_scripts_package(root: Path) -> Path:
    site_root = root / "site-packages"
    package = site_root / "scripts"
    package.mkdir(parents=True)
    package.joinpath("__init__.py").write_text(
        "raise ImportError('external scripts package was imported')\n",
        encoding="utf-8",
    )
    return site_root


def _load_checker_module(name: str) -> ModuleType:
    for module_name in (
        name,
        "scripts",
        "harness_projection_reader",
        "generate_codex_skill_adapters",
        "generate_antigravity_skill_adapters",
        "generate_api_skill_adapters",
    ):
        sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_direct_entrypoint_ignores_conflicting_external_scripts_package(tmp_path: Path) -> None:
    shadow_root = _write_shadow_scripts_package(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(shadow_root) + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--all", "--markdown"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )

    combined_output = result.stdout + result.stderr
    assert "external scripts package was imported" not in combined_output
    assert "Traceback" not in combined_output
    assert "# Harness Parity Review" in result.stdout


def test_adapter_generator_modules_are_loaded_from_checker_siblings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    shadow_root = _write_shadow_scripts_package(tmp_path)
    monkeypatch.syspath_prepend(str(shadow_root))

    module = _load_checker_module("check_harness_parity_shadow_probe")

    assert (
        Path(module.codex_adapter_generator.__file__).resolve()
        == (REPO_ROOT / "scripts" / "generate_codex_skill_adapters.py").resolve()
    )
    assert (
        Path(module.antigravity_adapter_generator.__file__).resolve()
        == (REPO_ROOT / "scripts" / "generate_antigravity_skill_adapters.py").resolve()
    )
    assert (
        Path(module.api_adapter_generator.__file__).resolve()
        == (REPO_ROOT / "scripts" / "generate_api_skill_adapters.py").resolve()
    )


def test_sibling_loader_preserves_genuine_local_import_failures(tmp_path: Path) -> None:
    module = _load_checker_module("check_harness_parity_failure_probe")
    tmp_path.joinpath("broken_generator.py").write_text(
        "raise ImportError('genuine local generator failure')\n",
        encoding="utf-8",
    )
    original_script_dir = module.SCRIPT_DIR
    module.SCRIPT_DIR = tmp_path
    try:
        with pytest.raises(ImportError, match="genuine local generator failure"):
            module._load_sibling_script_module("broken_generator")
    finally:
        module.SCRIPT_DIR = original_script_dir
        sys.modules.pop("broken_generator", None)

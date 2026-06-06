from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

from scripts import generate_ollama_skill_adapters as gen

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / ".ollama" / "skills" / "MANIFEST.json"
REGISTRY_PATH = REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"


def source_sha(path: Path) -> str:
    text = gen._strip_generated_block(path.read_text(encoding="utf-8")).lstrip("\ufeff").rstrip() + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_manifest_matches_generated_adapter_files() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    assert manifest["generated_by"] == "scripts/generate_ollama_skill_adapters.py"
    assert manifest["adapter_contract"] == "compact pointer; read canonical source before applying skill"
    assert len(manifest["adapters"]) >= 30
    for adapter in manifest["adapters"]:
        adapter_path = REPO_ROOT / adapter["adapter_relative_path"]
        source_path = REPO_ROOT / adapter["source_relative_path"]
        assert adapter_path.is_file(), adapter["adapter_relative_path"]
        assert source_path.is_file(), adapter["source_relative_path"]
        assert adapter["source_sha256"] == source_sha(source_path)
        text = adapter_path.read_text(encoding="utf-8")
        assert "GTKB-OLLAMA-SKILL-ADAPTER" in text
        assert f"Canonical source: {adapter['source_relative_path']}" in text
        assert "Before applying this skill, read the canonical source file listed above." in text


def test_bridge_adapter_is_compact_pointer_not_full_skill_copy() -> None:
    adapter_text = (REPO_ROOT / ".ollama" / "skills" / "bridge" / "SKILL.md").read_text(encoding="utf-8")

    assert "# Ollama Skill Adapter: gtkb-bridge" in adapter_text
    assert "## Use Contract" in adapter_text
    assert "## Operations" not in adapter_text
    assert "The bridge is GroundTruth-KB's coordination mechanism" not in adapter_text


def test_generator_check_passes_for_repository() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/generate_ollama_skill_adapters.py", "--check"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Ollama skill adapters: PASS" in completed.stdout


def test_ollama_registry_declares_adapter_support() -> None:
    registry = tomllib.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    ollama = registry["harnesses"]["ollama"]

    assert ollama["skill_adapter_generation_supported"] is True
    assert ollama["skill_adapter_generator"] == "scripts/generate_ollama_skill_adapters.py"
    assert ollama["skill_adapter_manifest"] == ".ollama/skills/MANIFEST.json"
    assert ollama["skill_adapter_drift_check_supported"] is True
    assert ollama["phase_1_only"] is True

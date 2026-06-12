"""FAB-15 regression coverage for role narrative/spec reconciliation."""

from __future__ import annotations

import importlib.util
import sys
import tomllib
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_canonical_terms.py"

SAMPLE_GLOSSARY = """\
# Canonical Terminology

## Canonical Terms

### MemBase

**Definition:** The canonical store of specifications and governed knowledge.
"""


def _load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_canonical_terms_under_test", SYNC_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_sync_fixture(root: Path) -> None:
    (root / "groundtruth.toml").write_text('[project]\nname = "fixture"\n', encoding="utf-8")
    rules = root / ".claude" / "rules"
    rules.mkdir(parents=True)
    (rules / "canonical-terminology.md").write_text(SAMPLE_GLOSSARY, encoding="utf-8")
    config = root / "config" / "governance"
    config.mkdir(parents=True)
    (config / "canonical-terms-sync.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                'glossary_path = ".claude/rules/canonical-terminology.md"',
                'database_path = "groundtruth.db"',
                'changed_by = "test-sync"',
                'freshness_failure_operations = ["insert", "update", "retire"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    KnowledgeDB(str(root / "groundtruth.db")).close()


def test_sync_check_fails_before_apply_and_passes_after_apply(tmp_path: Path) -> None:
    """The sync wrapper exposes a deterministic freshness gate."""
    _write_sync_fixture(tmp_path)
    module = _load_sync_module()

    assert module.main(["--project-root", str(tmp_path), "--check", "--json"]) == 1
    assert module.main(["--project-root", str(tmp_path), "--apply", "--json"]) == 0
    assert module.main(["--project-root", str(tmp_path), "--check", "--json"]) == 0


def test_codex_interactive_config_uses_split_posture() -> None:
    """FAB-15: project config is interactive-safe; headless carve-out is documented."""
    text = (REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)

    assert data["approval_policy"] == "on-request"
    assert data["sandbox_workspace_write"]["network_access"] is False
    assert "DELIB-FAB15-REMEDIATION-20260610" in text
    assert "Headless bridge-dispatch" in text

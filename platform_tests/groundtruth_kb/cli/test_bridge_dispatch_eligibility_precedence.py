from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import generate_harness_projection  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path, KnowledgeDB]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    db.insert_harness(
        id="D",
        harness_name="ollama",
        harness_type="ollama",
        role=["loyal-opposition"],
        changed_by="test",
        change_reason="seed",
        status="active",
        reviewer_precedence=20,
        invocation_surfaces={
            "dispatch": {"can_receive_dispatch": True, "can_fire_events": True},
            "headless": {
                "argv": ["python", "scripts/ollama_harness.py"],
                "can_receive_dispatch": True,
            },
        },
    )
    generate_harness_projection(db, root)

    dispatcher_dir = root / "config" / "dispatcher"
    dispatcher_dir.mkdir(parents=True)
    (dispatcher_dir / "rules.toml").write_text(
        """
schema_version = 1
selection_order = ["quality", "cost", "availability", "harness_id"]

[harnesses.D]
description = "Ollama"
can_receive_dispatch = true
can_fire_events = false
dispatch_cost = 30
dispatch_quality = 80
dispatch_availability = 95
tags = ["loyal-opposition"]

[[rules]]
id = "bridge-loyal-opposition-default"
required_roles = ["loyal-opposition"]
statuses = ["NEW", "REVISED", "NO-ACTION"]
prefer = ["quality", "cost", "availability", "harness_id"]
""".lstrip(),
        encoding="utf-8",
    )
    return root, config, db


def _set_eligibility(config: Path, enabled: bool) -> object:
    option = "--can-receive-dispatch" if enabled else "--no-can-receive-dispatch"
    return CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "config", "set-eligibility", "D", option, "--json"],
    )


def _registry_record(root: Path) -> dict[str, object]:
    registry = json.loads((root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    return next(record for record in registry["harnesses"] if record["id"] == "D")


def test_cli_eligibility_transaction_overrides_stale_headless_metadata(tmp_path: Path) -> None:
    root, config, db = _project(tmp_path)

    disabled = _set_eligibility(config, False)

    assert disabled.exit_code == 0, disabled.output
    assert json.loads(disabled.output)["status"] == "applied"
    disabled_projection = _registry_record(root)
    disabled_row = db.get_harness("D")
    assert disabled_row is not None
    disabled_surfaces = json.loads(disabled_row["invocation_surfaces"])
    assert disabled_row["version"] == 2
    assert disabled_projection["can_receive_dispatch"] is False
    assert disabled_projection["can_fire_events"] is False
    assert disabled_surfaces["dispatch"]["can_receive_dispatch"] is False
    assert disabled_surfaces["dispatch"]["can_fire_events"] is True
    assert disabled_surfaces["headless"]["can_receive_dispatch"] is True

    enabled = _set_eligibility(config, True)

    assert enabled.exit_code == 0, enabled.output
    assert json.loads(enabled.output)["status"] == "applied"
    enabled_projection = _registry_record(root)
    enabled_row = db.get_harness("D")
    assert enabled_row is not None
    enabled_surfaces = json.loads(enabled_row["invocation_surfaces"])
    assert enabled_row["version"] == 3
    assert enabled_projection["can_receive_dispatch"] is True
    assert enabled_projection["can_fire_events"] is False
    assert enabled_surfaces["dispatch"]["can_receive_dispatch"] is True
    assert enabled_surfaces["dispatch"]["can_fire_events"] is True
    assert enabled_surfaces["headless"]["can_receive_dispatch"] is True

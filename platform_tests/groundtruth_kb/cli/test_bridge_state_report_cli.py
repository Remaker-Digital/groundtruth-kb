from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.registry_control_plane import (  # noqa: E402
    append_passive_observation,
    consume_bridge_publication_capability,
    load_registry_snapshot,
    mint_bridge_publication_capability,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection  # noqa: E402

from scripts.bridge_work_intent_registry import acquire  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")

    dispatcher_dir = root / "config" / "dispatcher"
    dispatcher_dir.mkdir(parents=True)
    (dispatcher_dir / "rules.toml").write_text(
        """
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]

[budget]
enabled = false

    [budget.harnesses.A]
    model = "dispatcher-only-model-a"

    [budget.harnesses.D]
    model = "dispatcher-only-model-d"

[harnesses.A]
max_items = 1

[harnesses.D]
max_items = 2

rules = []
""".lstrip(),
        encoding="utf-8",
    )

    harness_dir = root / "harness-state"
    harness_dir.mkdir()
    (harness_dir / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                        "can_fire_events": False,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": False,
                        "dispatch_cost": 60,
                        "dispatch_quality": 90,
                        "dispatch_availability": 90,
                        "dispatch_max_items": 1,
                        "reviewer_precedence": 20,
                        "invocation_surfaces": {
                            "headless": {
                                "argv": [
                                    "codex",
                                    "exec",
                                    "--model",
                                    "gpt-5.5",
                                    "-c",
                                    'approval_policy="never"',
                                    "-c",
                                    'model_reasoning_effort="xhigh"',
                                ]
                            }
                        },
                    },
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "can_fire_events": False,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": False,
                        "dispatch_cost": 25,
                        "dispatch_quality": 92,
                        "dispatch_availability": 95,
                        "dispatch_max_items": 2,
                        "reviewer_precedence": 10,
                        "invocation_surfaces": {
                            "headless": {
                                "argv": [
                                    "groundtruth-kb/.venv/Scripts/python.exe",
                                    "scripts/ollama_harness.py",
                                    "-p",
                                    "{{PROMPT}}",
                                    "--skill",
                                    "bridge-review",
                                    "--model",
                                    "deepseek-v4-pro-cloud",
                                ]
                            }
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    bridge_dir = root / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "alpha-001.md").write_text("NEW\n\n# Alpha proposal\n", encoding="utf-8")
    (bridge_dir / "alpha-002.md").write_text("GO\n\n# Alpha approved\n", encoding="utf-8")
    (bridge_dir / "alpha-child-003.md").write_text("REVISED\n\n# Prefix sibling\n", encoding="utf-8")
    (bridge_dir / "gamma-001.md").write_text("NEW\n\n# Gamma proposal\n", encoding="utf-8")
    (bridge_dir / "verdict-correction-001.md").write_text(
        "NO-ACTION\n\n# Correct the prior verdict\n", encoding="utf-8"
    )
    (bridge_dir / "closed-001.md").write_text("VERIFIED\n\n# Closed thread\n", encoding="utf-8")
    (bridge_dir / "alpha-draft.md").write_text("NO-GO\n\n# Non-canonical draft\n", encoding="utf-8")

    state_dir = root / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps({"schema_version": 1, "updated_at": "2026-07-04T00:00:00Z", "recipients": {}}),
        encoding="utf-8",
    )

    return root, config


def _enable_bridge_registry(root: Path) -> tuple[Path, Path, Path]:
    record = SoTArtifact(
        id="bridge-versioned-files",
        domain="bridge_protocol",
        lifecycle="active",
        storage_path="bridge/*-[0-9][0-9][0-9].md",
        authority_spec_id="GOV-FILE-BRIDGE-AUTHORITY-001",
        mutation_api="governed bridge publication",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="_check_file_bridge_setup",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode="glob",
    )
    payload = serialize_registry([record])
    canonical = root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        root
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    canonical.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    canonical.write_bytes(payload)
    packaged.write_bytes(payload)

    db_path = root / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    db.close()
    sync_projection([record], db_path, changed_by="test", change_reason="state-report fixture")
    append_passive_observation(
        target_paths=["bridge/alpha-001.md"],
        actor_session="test-session",
        changed_by="test",
        change_reason="establish current bridge aggregate",
        project_root=root,
        registry_path=canonical,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    return canonical, packaged, db_path


def test_bridge_state_report_json_omits_dispatcher_and_uses_registry_model_config(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["bridge"]["total_thread_count"] == 5
    threads = {row["slug"]: row for row in payload["bridge"]["threads"]}
    assert threads["alpha"]["latest_status"] == "GO"
    assert threads["alpha"]["latest_path"] == "bridge/alpha-002.md"
    assert "alpha-draft" not in threads
    assert [row["slug"] for row in payload["bridge"]["lo_actionable"]] == [
        "alpha-child",
        "gamma",
        "verdict-correction",
    ]
    assert {row["status"]: row["count"] for row in payload["bridge"]["status_mix"]} == {
        "GO": 1,
        "NEW": 1,
        "NO-ACTION": 1,
        "REVISED": 1,
        "VERIFIED": 1,
    }
    assert set(payload) == {"bridge", "registry_publication", "harnesses", "source_authority"}
    assert "dispatcher" not in payload
    assert "dispatcher" not in payload["source_authority"]
    assert payload["registry_publication"] == {
        "enabled": False,
        "aggregate_current": None,
        "stale_count": 0,
        "stale_record_ids": [],
    }

    harnesses = {row["id"]: row for row in payload["harnesses"]["rows"]}
    assert all(set(row) == {"id", "harness", "model_config", "active", "events"} for row in harnesses.values())
    assert harnesses["A"]["model_config"] == "gpt-5.5; reasoning=xhigh; approval_policy=never"
    assert harnesses["D"]["model_config"] == "deepseek-v4-pro-cloud; skill=bridge-review"
    assert harnesses["A"]["events"] == "no"
    assert harnesses["D"]["active"] == "yes"
    assert "dispatcher-only-model-a" not in result.output
    assert "dispatcher-only-model-d" not in result.output


def test_bridge_state_report_markdown_is_three_worker_facing_tables(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--markdown"])

    assert result.exit_code == 0, result.output
    assert "| Status | Count |" in result.output
    assert "| Aspect | Value |" in result.output
    assert "## REGISTRY PUBLICATION" in result.output
    assert "## DISPATCHER" not in result.output
    assert "| Enabled | no |" in result.output
    assert "| Aggregate current | (unavailable) |" in result.output
    assert "| ID | Harness | Model / Config | Active | Events |" in result.output
    assert "| LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION | 3: alpha-child" in result.output
    assert sum(1 for line in result.output.splitlines() if line.startswith("| ---")) == 3


def test_bridge_state_report_surfaces_current_and_stale_registry_aggregate(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    canonical, packaged, db_path = _enable_bridge_registry(root)

    current_result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])
    assert current_result.exit_code == 0, current_result.output
    current_payload = json.loads(current_result.output)
    assert current_payload["registry_publication"] == {
        "enabled": True,
        "aggregate_current": True,
        "stale_count": 0,
        "stale_record_ids": [],
    }

    bridge_before = current_payload["bridge"]
    (root / "bridge" / "alpha-001.md").write_text("NEW\n\n# Alpha proposal drift\n", encoding="utf-8")

    stale_result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])
    assert stale_result.exit_code == 0, stale_result.output
    stale_payload = json.loads(stale_result.output)
    assert stale_payload["registry_publication"] == {
        "enabled": True,
        "aggregate_current": False,
        "stale_count": 1,
        "stale_record_ids": ["bridge-versioned-files"],
    }
    assert stale_payload["bridge"] == bridge_before

    markdown = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--markdown"])
    assert markdown.exit_code == 0, markdown.output
    assert "| Aggregate current | no |" in markdown.output
    assert "| Stale count | 1 |" in markdown.output
    assert "| Stale record IDs | bridge-versioned-files |" in markdown.output
    assert "WARNING: The bridge publication aggregate is stale audit state." in markdown.output
    assert "Governed publication self-observes the aggregate" in markdown.output
    assert "this diagnostic does not mean publications are refused." in markdown.output
    assert "will refuse ALL publications" not in markdown.output
    assert "gt registry observe --artifact bridge-versioned-files" not in markdown.output

    slug = "stale-publication"
    session_id = "stale-publication-session"
    content = (
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n"
        "author_identity: prime-builder/codex\n"
        "author_harness_id: test\n"
        f"author_session_context_id: {session_id}\n"
        "author_model: fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: unit-test\n"
        "author_metadata_source: unit-test\n\n"
        "# Stale aggregate publication fixture\n\n"
        "bridge_kind: prime_proposal\n"
        f"Document: {slug}\n"
        "Version: 001\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-0001\n"
        'target_paths: ["scripts/example.py"]\n'
    ).encode()
    target = root / "bridge" / f"{slug}-001.md"
    assert acquire(slug, session_id, project_root=root)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:state-report-stale-fixture",
        project_root=root,
        registry_path=canonical,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    target.write_bytes(content)
    receipt = consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason="publish while aggregate audit state is stale",
        project_root=root,
        registry_path=canonical,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert receipt.capability_state == "consumed"
    snapshot = load_registry_snapshot(
        project_root=root,
        registry_path=canonical,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert registry_currentness(snapshot, project_root=root, db_path=db_path)["current"]


def test_bridge_state_report_disables_incomplete_registry_control_plane(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    canonical = root / "config" / "registry" / "sot-artifacts.toml"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("# incomplete fixture\n", encoding="utf-8")

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["registry_publication"] == {
        "enabled": False,
        "aggregate_current": None,
        "stale_count": 0,
        "stale_record_ids": [],
    }
    markdown = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--markdown"])
    assert markdown.exit_code == 0, markdown.output
    assert "self-observes" not in markdown.output
    assert "publications are refused" not in markdown.output


def test_bridge_state_report_is_read_only_for_state_inputs(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    canonical, packaged, db_path = _enable_bridge_registry(root)
    tracked = [
        root / "bridge" / "alpha-001.md",
        root / "bridge" / "alpha-002.md",
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
        canonical,
        packaged,
        db_path,
    ]
    before = {path: path.read_bytes() for path in tracked}

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])

    assert result.exit_code == 0, result.output
    assert {path: path.read_bytes() for path in tracked} == before

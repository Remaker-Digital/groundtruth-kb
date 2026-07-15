"""Specification-derived tests for WI-5266 resource identity and closure."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from groundtruth_kb.context.manifest import (
    DEFAULT_REGISTRY,
    PACKAGED_REGISTRY_ROOT,
    ContextManifestError,
    assemble_context_manifest,
    canonical_manifest_bytes,
    load_context_registry,
    resolve_context_registry,
    validate_manifest_resource_semantics,
)
from groundtruth_kb.context.resource_routing import (
    canonical_resource_contract,
    dispatch_resource_selection,
    render_resource_context,
    resolve_resource_selection,
)

FIXED_TIME = datetime(2026, 7, 15, tzinfo=UTC)
REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("Auto-process the Top Backlog items", ["backlog"]),
        (
            "Process P0/P1 backlog, beginning with all bridge/TAFE/harness-related items",
            ["backlog"],
        ),
        ("Process the bridge queue", ["bridge_queue"]),
        ("Review the review queue", ["bridge_queue"]),
        ("Continue bridge work for the TAFE harness", []),
        ("Investigate bridge-related harness behavior", []),
        ("A bridgeless build and backlogless fixture", []),
    ],
)
def test_literal_resource_terms_are_boundary_aware(prompt: str, expected: list[str]) -> None:
    selection = resolve_resource_selection(prompt)

    assert selection["selected_resources"] == expected
    assert selection["primary_resource"] == (expected[0] if len(expected) == 1 else None)


def test_explicit_multi_resource_request_has_no_silent_winner() -> None:
    selection = resolve_resource_selection("Compare the current backlog with the bridge queue")

    assert selection["selected_resources"] == ["backlog", "bridge_queue"]
    assert selection["primary_resource"] is None
    assert selection["read_routes"] == {
        "backlog": "gt backlog list",
        "bridge_queue": "gt bridge state-report",
    }


@pytest.mark.parametrize("dispatch_run_id", [None, "", "   "])
def test_blank_dispatch_provenance_cannot_default_the_bridge_queue(dispatch_run_id: str | None) -> None:
    assert dispatch_resource_selection(dispatch_run_id)["selected_resources"] == []


def test_work_item_ids_and_compact_context_follow_current_literal_selection() -> None:
    selection = resolve_resource_selection("Process backlog item wi-5266 before WI-5267")
    context = render_resource_context(selection)

    assert selection["work_item_ids"] == ["WI-5266", "WI-5267"]
    assert selection["selection_authority"] == "current_owner_literal"
    assert "`backlog` via `gt backlog list`" in context
    assert "distinct, non-alias resources" in context


def test_all_activity_manifests_carry_the_exact_contract() -> None:
    expected = canonical_resource_contract()
    manifests = [
        assemble_context_manifest(activity=activity, role="Prime Builder", generated_at=FIXED_TIME)
        for activity in ("ops", "deliberation", "build", "test", "spec", "project")
    ]

    for manifest in manifests:
        validate_manifest_resource_semantics(manifest)
        assert manifest["resource_contract"] == expected
    repeated = assemble_context_manifest(activity="build", role="Prime Builder", generated_at=FIXED_TIME)
    assert canonical_manifest_bytes(manifests[2]) == canonical_manifest_bytes(repeated)


def test_empty_host_receives_the_packaged_fallback_contract(tmp_path: Path) -> None:
    manifest = assemble_context_manifest(
        activity="build",
        role="Prime Builder",
        generated_at=FIXED_TIME,
        project_root=tmp_path,
    )

    validate_manifest_resource_semantics(manifest)
    assert manifest["resource_contract"] == canonical_resource_contract()
    assert not (tmp_path / "config").exists()


def test_registry_rejects_nonblank_swapped_resource_routes(tmp_path: Path) -> None:
    marker = "__BACKLOG_ROUTE__"
    text = DEFAULT_REGISTRY.read_text(encoding="utf-8")
    text = text.replace('read_route = "gt backlog list"', f'read_route = "{marker}"', 1)
    text = text.replace('read_route = "gt bridge state-report"', 'read_route = "gt backlog list"', 1)
    text = text.replace(f'read_route = "{marker}"', 'read_route = "gt bridge state-report"', 1)
    registry_path = tmp_path / "context-manifests.toml"
    registry_path.write_text(text, encoding="utf-8")

    with pytest.raises(ContextManifestError, match="must exactly preserve"):
        load_context_registry(registry_path)


def test_registry_rejects_project_descriptor_without_backlog_route(tmp_path: Path) -> None:
    text = DEFAULT_REGISTRY.read_text(encoding="utf-8").replace(
        'read_route = "gt projects list; gt backlog list"',
        'read_route = "gt projects list"',
        1,
    )
    registry_path = tmp_path / "context-manifests.toml"
    registry_path.write_text(text, encoding="utf-8")

    with pytest.raises(ContextManifestError, match="backlog and bridge routes cannot be swapped or aliased"):
        load_context_registry(registry_path)


def test_registry_and_manifest_are_closed_and_deterministic() -> None:
    registry = load_context_registry()
    first = assemble_context_manifest(activity="build", role="Prime Builder", generated_at=FIXED_TIME)
    second = assemble_context_manifest(activity="build", role="Prime Builder", generated_at=FIXED_TIME)

    assert registry.activities == ("ops", "deliberation", "build", "test", "spec", "project")
    assert canonical_manifest_bytes(first) == canonical_manifest_bytes(second)
    assert first["stack_order"] == [
        "native_hints",
        "session_baseline",
        "role_bootstrap",
        "activity_overlay",
    ]
    assert all(item["source_id"] and item["read_route"] for item in first["items"])


def test_empty_project_uses_self_contained_packaged_registry(tmp_path: Path) -> None:
    resolution = resolve_context_registry(project_root=tmp_path)

    assert resolution.origin == "packaged_default"
    assert resolution.registry_path == DEFAULT_REGISTRY
    assert resolution.source_root == PACKAGED_REGISTRY_ROOT
    assert not (tmp_path / "config").exists()

    manifest = assemble_context_manifest(
        activity="build",
        role="Prime Builder",
        generated_at=FIXED_TIME,
        project_root=tmp_path,
    )
    assert manifest["registry_version"] == 1
    assert len(manifest["items"]) == 14


def test_project_override_is_strict_and_removal_rolls_back_to_packaged_default(tmp_path: Path) -> None:
    shutil.copytree(PACKAGED_REGISTRY_ROOT / "config", tmp_path / "config")
    override = tmp_path / "config" / "registry" / "context-manifests.toml"
    override.write_text(
        DEFAULT_REGISTRY.read_text(encoding="utf-8").replace("[manifest]\nversion = 1", "[manifest]\nversion = 7", 1),
        encoding="utf-8",
    )

    resolution = resolve_context_registry(project_root=tmp_path)
    assert resolution.origin == "project_override"
    assert (
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            project_root=tmp_path,
        )["registry_version"]
        == 7
    )

    missing_source = tmp_path / "config" / "governance" / "canonical-terms-sync.toml"
    missing_source.unlink()
    with pytest.raises(ContextManifestError, match=r"baseline\.glossary: source is missing"):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            project_root=tmp_path,
        )

    override.unlink()
    rolled_back = resolve_context_registry(project_root=tmp_path)
    assert rolled_back.origin == "packaged_default"
    assert (
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            project_root=tmp_path,
        )["registry_version"]
        == 1
    )


def test_packaged_v1_snapshot_matches_source_checkout_registry_inputs() -> None:
    relative_paths = (
        Path("config/registry/context-manifests.toml"),
        Path("config/governance/canonical-terms-sync.toml"),
        Path("config/agent-control/activity-disposition-profiles.toml"),
        Path("config/agent-control/activity-envelope-sharding.toml"),
        Path("config/agent-control/command-surface.toml"),
        Path("config/registry/sot-artifacts.toml"),
        Path("config/agent-control/system-interface-map.toml"),
    )
    for relative_path in relative_paths:
        packaged_path = (
            DEFAULT_REGISTRY
            if relative_path.name == "context-manifests.toml"
            else PACKAGED_REGISTRY_ROOT / relative_path
        )
        assert packaged_path.read_bytes() == (REPO_ROOT / relative_path).read_bytes(), relative_path


def test_high_churn_state_is_live_query_only() -> None:
    manifest = assemble_context_manifest(activity="project", role="Prime Builder", generated_at=FIXED_TIME)
    high_churn = [item for item in manifest["items"] if item["churn_class"] in {"project_status", "work_item_status"}]

    assert high_churn
    assert all(item["content"] is None and item["disposition"] == "live-query-only" for item in high_churn)


@pytest.mark.parametrize("activity", ["", "unknown", "Build"])
def test_unknown_or_ambiguous_activity_fails_closed(activity: str) -> None:
    with pytest.raises(ContextManifestError, match="one-active activity"):
        assemble_context_manifest(activity=activity, role="Prime Builder", generated_at=FIXED_TIME)


def test_missing_role_fails_before_activity_assembly() -> None:
    with pytest.raises(ContextManifestError, match="role-bootstrap"):
        assemble_context_manifest(activity="build", role="", generated_at=FIXED_TIME)


def test_expired_embedded_context_exposes_recovery() -> None:
    with pytest.raises(ContextManifestError, match=r"expired.*recovery="):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            evaluated_at=FIXED_TIME + timedelta(seconds=121),
        )


def test_essential_context_cannot_be_discarded_for_budget() -> None:
    with pytest.raises(ContextManifestError, match="essential-context exceeds token-budget and must-not-discard"):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            hard_token_budget=1,
        )


def test_missing_embedded_source_fails_with_recovery(tmp_path: Path) -> None:
    registry = tmp_path / "context-manifests.toml"
    text = DEFAULT_REGISTRY.read_text(encoding="utf-8").replace(
        'source_path = "config/governance/canonical-terms-sync.toml"',
        'source_path = "config/governance/missing-context-source.toml"',
        1,
    )
    registry.write_text(text, encoding="utf-8")

    with pytest.raises(ContextManifestError, match=r"source is missing; recovery="):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            registry_path=registry,
        )


def test_conflicting_authority_route_fails_with_recovery(tmp_path: Path) -> None:
    registry = tmp_path / "context-manifests.toml"
    registry.write_text(
        DEFAULT_REGISTRY.read_text(encoding="utf-8")
        + """

[[items]]
id = "activity.glossary.conflict"
layer = "activity_overlay"
category = "glossary"
source_id = "activity-disposition-profiles"
source_path = "config/agent-control/activity-disposition-profiles.toml"
authority_class = "conflicting_authority"
lifecycle = "current"
churn_class = "low"
embedding = "embedded"
ttl_seconds = 120
read_route = "conflicting read route"
mutation_route = "managed skill lifecycle"
recovery_route = "gt skills"
applicability = ["*"]
projection = "profile.terminology"
token_cost = 1
priority = 1
essential = false
""",
        encoding="utf-8",
    )

    with pytest.raises(ContextManifestError, match=r"conflict.*recovery="):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=FIXED_TIME,
            registry_path=registry,
        )


def test_canonical_bytes_are_hash_seed_independent() -> None:
    code = """
import hashlib
from datetime import UTC, datetime
from groundtruth_kb.context.manifest import assemble_context_manifest, canonical_manifest_bytes
manifest = assemble_context_manifest(
    activity='build',
    role='Prime Builder',
    generated_at=datetime(2026, 7, 13, tzinfo=UTC),
)
print(hashlib.sha256(canonical_manifest_bytes(manifest)).hexdigest())
"""
    observed: list[str] = []
    for seed in ("1", "991"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        env["PYTHONPATH"] = str(PACKAGE_SRC)
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        observed.append(result.stdout.strip())

    assert observed[0] == observed[1]

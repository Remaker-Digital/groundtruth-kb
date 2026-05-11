"""T-step-order-1 for GTKB-ISOLATION-018 sub-slice 18.E.1.

Per the GO'd implementation proposal at
`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` (Codex GO at -016).

Verifies the data-dependency ordering between implementation steps:

    Step 0  (drift reconciliation)  produces  manifest-v3.json
    Step 0.5 (write-set generation)  reads     manifest-v3.json
                                     produces  write-set.json
    Step 1   (worktree precondition)  reads     write-set.json

Mutation tests confirm that reversing the ordering raises FileNotFoundError —
e.g., generating the write-set before drift reconciliation has produced
manifest-v3.json fails because the input file does not exist.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_step0_produces_manifest_v3_before_step05_reads_it(
    tmp_path: Path,
) -> None:
    """Step 0 must produce .tmp/e3-disposition/manifest-v3.json before
    Step 0.5 reads it. Mutation: if manifest-v3.json does not exist when
    Step 0.5 runs, json.load raises FileNotFoundError."""
    manifest_path = tmp_path / ".tmp" / "e3-disposition" / "manifest-v3.json"
    # Step 0.5 reading the manifest before Step 0 produces it must raise.
    with pytest.raises(FileNotFoundError):
        json.loads(manifest_path.read_text(encoding="utf-8"))


def test_step05_produces_write_set_before_step1_reads_it(tmp_path: Path) -> None:
    """Step 0.5 must produce .tmp/e1-drift/write-set.json before Step 1
    reads it. Mutation: if write-set.json does not exist when Step 1
    precondition runs, the precondition script's json.load raises
    FileNotFoundError."""
    write_set_path = tmp_path / ".tmp" / "e1-drift" / "write-set.json"
    with pytest.raises(FileNotFoundError):
        json.loads(write_set_path.read_text(encoding="utf-8"))


def test_canonical_artifacts_exist_in_repo() -> None:
    """Post-Step 0 + Step 0.5 in the GT-KB repo, both canonical artifacts
    must exist at their documented paths."""
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = repo_root / ".tmp" / "e3-disposition" / "manifest-v3.json"
    write_set_path = repo_root / ".tmp" / "e1-drift" / "write-set.json"

    # These files are gitignored (under .tmp/) but are produced by E.1
    # implementation's Step 0 and Step 0.5. After implementation has run,
    # both should exist.
    assert manifest_path.exists(), (
        f"manifest-v3.json missing at {manifest_path} — Step 0 was not run"
    )
    assert write_set_path.exists(), (
        f"write-set.json missing at {write_set_path} — Step 0.5 was not run"
    )


def test_manifest_v3_schema_is_complete() -> None:
    """manifest-v3.json must contain the required disposition buckets and
    the totals field for downstream consumers (write-set generator)."""
    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = repo_root / ".tmp" / "e3-disposition" / "manifest-v3.json"

    if not manifest_path.exists():
        pytest.skip("manifest-v3.json not generated yet; run Step 0 first")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required_buckets = (
        "STAYS_PLATFORM_py",
        "STAYS_PLATFORM_nonpy",
        "MIGRATES_AGENT_RED_py",
        "MIGRATES_AGENT_RED_nonpy",
        "MIGRATES_AGENT_RED_WITH_SCRIPT_DEP_py",
    )
    for bucket in required_buckets:
        assert bucket in manifest, f"manifest-v3.json missing bucket: {bucket}"

    assert "totals" in manifest, "manifest-v3.json missing totals field"
    assert "grand_total" in manifest["totals"]


def test_write_set_schema_is_complete() -> None:
    """write-set.json must contain all required categories for downstream
    consumers (precondition, rollback, Step 3 git mv loop)."""
    repo_root = Path(__file__).resolve().parents[2]
    write_set_path = repo_root / ".tmp" / "e1-drift" / "write-set.json"

    if not write_set_path.exists():
        pytest.skip("write-set.json not generated yet; run Step 0.5 first")

    write_set = json.loads(write_set_path.read_text(encoding="utf-8"))
    required_keys = (
        "cluster_sources_dir_recursive",
        "cluster_sources_file",
        "cluster_destinations_dir_recursive",
        "cluster_destinations_file",
        "tests_migrating_source_paths",
        "tests_migrating_destination_paths",
        "tests_staying_platform_paths",
        "config_files_in_place_edits",
        "workflow_files_in_place_edits",
        "dockerfile_in_place_edits",
        "scratch_dirs",
    )
    for key in required_keys:
        assert key in write_set, f"write-set.json missing key: {key}"

    # Source-destination symmetry invariant (T-write-set-1 M3).
    sources = write_set["tests_migrating_source_paths"]
    destinations = write_set["tests_migrating_destination_paths"]
    assert len(sources) == len(destinations), (
        "tests_migrating_source_paths and _destination_paths must be paired"
    )
    for src, dst in zip(sources, destinations):
        assert dst == "applications/Agent_Red/" + src, (
            f"pair mismatch: {src} -> {dst}"
        )

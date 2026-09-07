"""The SoT registry names the baseline as authority, not its own derivations (WI-7523).

Specs: `GOV-HARNESS-NEUTRAL-BASELINE-001`, `GOV-PLATFORM-SOT-REGISTRY-001`,
`DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.

The defect these pin: the source-of-truth registry registered 391 generated
projection paths as source-of-truth artifacts and contained **zero** records for
`.harness-baseline-configuration/`, the surface that
`GOV-HARNESS-NEUTRAL-BASELINE-001` makes the sole harness-configuration
authoring authority. The registry asserted the inverse of the governance.

The adjacent rule-projection policy re-point belongs to WI-6329, which owns the
policy, its validator, and their tests under a separate live GO. This module
therefore exercises only the registry half of WI-7523.

This module is the executable selector for `TEST-12468`, which carried a null
selector before this work.

**One assertion from the GO'd verification plan is deliberately absent.**
`no_active_agent_control` -- that no `[[artifacts]]` record declares
`lifecycle = "active"` with a `storage_path` rooted at `config/agent-control/` --
is carried by **WI-7735**, split off by owner decision on 2026-09-04. All 78 such
records are still active, and the governed write path (`gt registry amend`)
requires a `--pauth-id` against a `project_authorizations` table that no longer
exists. Editing the TOML directly is not a substitute: it diverges the MemBase
projection and makes `load_registry_snapshot` raise `RegistryProjectionMismatch`,
which `test_control_plane_loads_and_classifies` below would then catch. The
assertion is deferred rather than weakened, and it lands with WI-7735.
"""

from __future__ import annotations

import hashlib
import sys
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = PROJECT_ROOT / "config" / "registry" / "sot-artifacts.toml"
PACKAGED_REGISTRY = (
    PROJECT_ROOT
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
BASELINE_ROOT = ".harness-baseline-configuration/"

#: Record count measured by the reviewing role at GO time
#: (bridge/gtkb-wi7523-baseline-projection-authority-inversion-004.md). The
#: registry may grow; a drop below this floor means records were removed, which
#: the re-base never authorizes.
RECORD_COUNT_FLOOR = 1446

#: Every field `GOV-PLATFORM-SOT-REGISTRY-001` requires of a registry record.
REQUIRED_FIELDS = (
    "id",
    "domain",
    "lifecycle",
    "storage_path",
    "coverage_mode",
    "authority_spec_id",
    "mutation_api",
    "versioning_policy",
    "backup_policy",
    "restore_action",
)


def _artifacts() -> list[dict]:
    return tomllib.loads(REGISTRY.read_text(encoding="utf-8"))["artifacts"]


def test_baseline_registered_as_source_of_truth() -> None:
    """`GOV-HARNESS-NEUTRAL-BASELINE-001`: the authoring authority is registered.

    Zero baseline records was the whole defect. Asserting merely "greater than
    zero" is deliberate: the exact count tracks how many baseline surfaces have
    been declared so far, and pinning it would turn every later registration
    into a test failure.
    """
    baseline = [a for a in _artifacts() if str(a.get("storage_path", "")).startswith(BASELINE_ROOT)]
    assert baseline, (
        f"no [[artifacts]] record is rooted at {BASELINE_ROOT!r}; the registry does not name "
        "the canonical baseline as a source of truth"
    )


def test_schema_intact_for_every_record() -> None:
    """`GOV-PLATFORM-SOT-REGISTRY-001`: re-basing must not shed fields or records."""
    artifacts = _artifacts()
    assert len(artifacts) >= RECORD_COUNT_FLOOR, (
        f"record count {len(artifacts)} fell below the GO-time floor {RECORD_COUNT_FLOOR}; "
        "the re-base adds and reclassifies records, it never removes them"
    )
    incomplete = {
        str(a.get("id")): [f for f in REQUIRED_FIELDS if f not in a]
        for a in artifacts
        if any(f not in a for f in REQUIRED_FIELDS)
    }
    assert not incomplete, f"records missing required fields: {incomplete}"


def test_registry_copies_byte_identical() -> None:
    """`DCL-SOT-REGISTRY-PROJECTION-PARITY-001`: the packaged copy is not a fork.

    Byte equality rather than parsed equality, because a formatting-only
    divergence still means the two copies were edited separately, which is the
    failure mode this guards.
    """
    declared = REGISTRY.read_bytes()
    packaged = PACKAGED_REGISTRY.read_bytes()
    assert hashlib.sha256(declared).hexdigest() == hashlib.sha256(packaged).hexdigest(), (
        f"registry copies diverged: {REGISTRY.name} is {len(declared)} bytes, packaged copy is {len(packaged)} bytes"
    )


def test_control_plane_loads_and_classifies() -> None:
    """`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: the declaration and its projection agree.

    This is the assertion that makes a raw TOML edit detectable. The loader
    compares the declaration against the MemBase projection and raises
    `RegistryProjectionMismatch` when they diverge, so editing the file without
    going through the governed mutation API fails here rather than silently.
    """
    src = PROJECT_ROOT / "groundtruth-kb" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from groundtruth_kb.project.registry_control_plane import load_registry_snapshot
    except ImportError as exc:  # pragma: no cover - environment defect, not a registry defect
        pytest.skip(f"registry control plane unavailable: {exc}")

    snapshot = load_registry_snapshot(project_root=PROJECT_ROOT)
    assert snapshot.records, "control plane loaded an empty registry"

    sample = next(
        (r for r in snapshot.records if str(getattr(r, "storage_path", "")).startswith(BASELINE_ROOT)),
        None,
    )
    assert sample is not None, (
        "control plane is operative but classifies no baseline-rooted path, so the re-base "
        "is not visible through the loader consumers actually use"
    )

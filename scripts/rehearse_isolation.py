"""GTKB-ISOLATION-016 Phase 8 isolation rehearsal driver (Wave 1 skeleton).

Top-level driver that orchestrates 11 sub-scripts per the manifest. Wave 1
ships argparse, manifest load, the eleven-entry dispatch table, and hard
refusal conditions. Sub-script bodies (``scripts/rehearse/_inventory.py``
and the rest) land in Wave 2 after owner answers §3.3 (output location) and
§3.5 (git strategy).

Authority: ``bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md``
(REVISED-6) and ``-014`` (Codex GO). ADR backing:
``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` upstream commit
``affa5a0567a64f79bb4c5aae891889d4af50a72a``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rehearse._common import (  # noqa: E402
    LEGACY_ROOT,
    TARGET_ROOT_DEFAULT,
    ManifestError,
    TargetRootError,
    hash_set_walk,
    load_manifest,
    validate_target_root,
)


EXIT_OK = 0
EXIT_USAGE = 1
EXIT_REFUSE = 2

# Per `-013` §2.2: 11 sub-script lanes mapping 1:1 to Phase 8 plan
# Exit Criterion 1. Each entry: (phase-cli-name, module-path, function-name).
# Wave 1 ships the table with stub functions; Wave 2 implements bodies.
DISPATCH_TABLE: tuple[tuple[str, str, str], ...] = (
    ("inventory", "rehearse._inventory", "run"),
    ("rewrite", "rehearse._path_rewrite", "run"),
    ("ci", "rehearse._ci_inventory", "run"),
    ("membase", "rehearse._membase_export", "run"),
    ("chromadb", "rehearse._chromadb_regen", "run"),
    ("dashboard", "rehearse._dashboard_regen", "run"),
    ("bridge-split", "rehearse._bridge_split", "run"),
    ("backlog-split", "rehearse._backlog_split", "run"),
    ("release-readiness-split", "rehearse._release_readiness_split", "run"),
    ("production", "rehearse._production_effects", "run"),
    ("rollback", "rehearse._rollback", "run"),
)

PHASE_CHOICES: tuple[str, ...] = tuple(p[0] for p in DISPATCH_TABLE) + ("verify", "all")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=TARGET_ROOT_DEFAULT,
        help=f"Target child root (default: {TARGET_ROOT_DEFAULT})",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=LEGACY_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "rehearsal" / "manifest.toml",
        help="Path to rehearsal manifest.toml",
    )
    parser.add_argument(
        "--phase",
        choices=PHASE_CHOICES,
        default="all",
        help="Sub-script phase to run (or 'all' / 'verify')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Default true; --no-dry-run is explicitly forbidden in v1",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="no_dry_run",
        action="store_true",
        help="Forbidden in v1; presence triggers refusal",
    )
    parser.add_argument(
        "--accept-drift",
        action="store_true",
        help="Bypass pre-run hash-set drift check",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.no_dry_run:
        print("rehearse_isolation: --no-dry-run is forbidden in v1; refusing", file=sys.stderr)
        return EXIT_REFUSE

    try:
        validate_target_root(args.target_root)
    except TargetRootError as exc:
        print(f"rehearse_isolation: target-root refusal — {exc}", file=sys.stderr)
        return EXIT_REFUSE

    try:
        manifest = load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"rehearse_isolation: manifest error — {exc}", file=sys.stderr)
        return EXIT_USAGE

    # Per Codex `-016` finding: do NOT walk the legacy root in default
    # execution. The walk is expensive (>120s on live repo) and Wave 1's
    # role is to ship a safe skeleton, not exercise drift. Wave 3 will
    # introduce real drift comparison via an explicit `drift-check` phase.
    # The `--accept-drift` flag is preserved for forward compatibility.

    # Wave 1: dispatch is a stub. Sub-scripts file in Wave 2 after owner
    # decisions §3.3 / §3.5 surface.
    if args.phase == "verify":
        print("rehearse_isolation: Wave 3 verification matrix not yet implemented (Wave 1 skeleton)")
        return EXIT_OK

    selected = (
        DISPATCH_TABLE
        if args.phase == "all"
        else tuple(entry for entry in DISPATCH_TABLE if entry[0] == args.phase)
    )
    print(f"rehearse_isolation: Wave 1 skeleton — would dispatch {len(selected)} phase(s):")
    for cli_name, module_path, func_name in selected:
        print(f"  {cli_name:30s} -> {module_path}.{func_name}")
    print("Sub-script bodies land in Wave 2 after owner answers decisions §3.3 and §3.5.")
    print(f"Manifest target_root: {manifest.get('target_root')}")
    print(f"Manifest legacy_root: {manifest.get('legacy_root')}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

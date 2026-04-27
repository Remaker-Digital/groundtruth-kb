"""GTKB-ISOLATION-016 Phase 8 isolation rehearsal driver.

Wave 1 shipped argparse, manifest load, the eleven-entry dispatch table,
and hard refusal conditions. Slice 3 (Wave 2) wires the dispatch to
actually invoke implemented lanes (currently `_inventory.py`; Stages B-D
follow as separate bridges).

Authority: ``bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md``
(REVISED-6) and ``-014`` (Codex GO); Slice 3 wire-up at
``bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md`` REVISED-1 +
``-004`` (Codex GO). ADR backing:
``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` upstream commit
``affa5a0567a64f79bb4c5aae891889d4af50a72a``.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rehearse._common import (  # noqa: E402
    LEGACY_ROOT,
    TARGET_ROOT_DEFAULT,
    ManifestError,
    ManifestValidationError,
    TargetRootError,
    hash_set_walk,
    load_manifest,
    validate_sandbox_output_dir,
    validate_target_root,
)


EXIT_OK = 0
EXIT_USAGE = 1
EXIT_REFUSE = 2

# Per `-013` §2.2: 11 sub-script lanes mapping 1:1 to Phase 8 plan
# Exit Criterion 1. Each entry: (phase-cli-name, module-path, function-name).
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
        help="Default true; --no-dry-run is explicitly forbidden in v1. "
             "For Wave 2 real execution, use --execute (which takes "
             "precedence over --dry-run if both are passed).",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="no_dry_run",
        action="store_true",
        help="Forbidden in v1; presence triggers refusal. Use --execute instead.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Wave 2 explicit opt-in: actually invoke the lane (sets "
             "dry_run=False). Default is dry_run=True. Distinct from "
             "--no-dry-run which remains a Wave 1 hard refusal. If both "
             "--dry-run and --execute are passed, --execute takes precedence.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override output directory. Default: manifest.output_dir + ISO "
             "timestamp suffix. The override is validated with the same M2 "
             "sandbox-safety rules as manifest.output_dir.",
    )
    parser.add_argument(
        "--accept-drift",
        action="store_true",
        help="Bypass pre-run hash-set drift check",
    )
    return parser


def _resolve_output_dir(manifest: dict[str, Any], override: Path | None = None) -> Path:
    """Resolve the per-run output_dir.

    If ``override`` is provided, validate via :func:`validate_sandbox_output_dir`
    and return it verbatim. Otherwise append an ISO timestamp to
    ``manifest.output_dir`` (which has already been validated by
    ``load_manifest(wave=2)``).

    Per Slice 3 F2 fix: the override is subject to the same M2 sandbox
    rules as the manifest value, preventing operators from directing
    output back into LEGACY_ROOT or non-allowlisted paths.
    """
    if override is not None:
        validate_sandbox_output_dir(override)
        return override
    base = manifest["output_dir"]
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return Path(f"{base}-{timestamp}")


def _dispatch(
    phase_name: str,
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """Look up the lane in DISPATCH_TABLE and invoke its run().

    Returns the lane's standard result dict per Wave 2 -003 §4.1. Per
    Slice 3 F3 fix:

    - ``ModuleNotFoundError`` is treated as "lane not yet implemented"
      ONLY when the missing module exactly matches the lane module path.
      A ``ModuleNotFoundError`` for any OTHER module name (e.g., a
      dependency the lane imports) indicates the lane is broken →
      status="error".
    - ``AttributeError`` on the run() lookup means the module exists but
      doesn't expose ``run()`` → status="error" (lane structure defect).
    - Any other exception during import propagates (driver crashes
      visibly on truly unexpected lane states).
    """
    for cli_name, module_path, func_name in DISPATCH_TABLE:
        if cli_name == phase_name:
            try:
                mod = importlib.import_module(module_path)
            except ModuleNotFoundError as exc:
                if exc.name == module_path:
                    return {
                        "status": "skipped",
                        "output_files": [],
                        "metrics": {},
                        "warnings": [
                            f"lane {phase_name!r} not yet implemented "
                            f"({module_path} not on disk); future Wave 2 "
                            f"slice will land it"
                        ],
                    }
                return {
                    "status": "error",
                    "output_files": [],
                    "metrics": {},
                    "warnings": [
                        f"lane {phase_name!r} import failed: missing "
                        f"dependency {exc.name!r} (the lane module exists "
                        f"but cannot import). This is a lane defect, not a "
                        f"not-yet-implemented case."
                    ],
                }
            try:
                fn = getattr(mod, func_name)
            except AttributeError:
                return {
                    "status": "error",
                    "output_files": [],
                    "metrics": {},
                    "warnings": [
                        f"lane {phase_name!r} module exists but has no "
                        f"{func_name}() function — lane defect."
                    ],
                }
            return fn(manifest, output_dir, dry_run=dry_run)
    raise ValueError(f"unknown phase: {phase_name}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.no_dry_run:
        print(
            "rehearse_isolation: --no-dry-run is forbidden; "
            "use --execute for Wave 2 real-run",
            file=sys.stderr,
        )
        return EXIT_REFUSE

    # Per GO -004 implementation note: make the --dry-run / --execute
    # interaction visible. --execute takes precedence; print a notice if
    # both were passed (since --dry-run defaults True, this only fires
    # when the operator explicitly passes both flags — which is a sign
    # of confusion worth surfacing).
    dry_run = not args.execute
    if args.execute:
        # Note: argparse default for --dry-run is True, so we cannot
        # detect explicit --dry-run vs default True from args alone.
        # Emit a notice when --execute is set so the operator sees
        # which mode actually applies.
        print(
            "rehearse_isolation: --execute set; running with dry_run=False "
            "(--execute takes precedence over --dry-run if both passed)",
            file=sys.stderr,
        )

    try:
        validate_target_root(args.target_root)
    except TargetRootError as exc:
        print(f"rehearse_isolation: target-root refusal — {exc}", file=sys.stderr)
        return EXIT_REFUSE

    try:
        manifest = load_manifest(args.manifest, wave=2)
    except ManifestError as exc:
        print(f"rehearse_isolation: manifest error — {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        output_dir = _resolve_output_dir(manifest, args.output_dir)
    except ManifestValidationError as exc:
        print(
            f"rehearse_isolation: --output-dir override rejected — {exc}",
            file=sys.stderr,
        )
        return EXIT_USAGE

    if args.phase == "verify":
        print(
            "rehearse_isolation: Wave 3 verification matrix not yet "
            "implemented (Wave 2 driver-only)"
        )
        return EXIT_OK

    selected = (
        DISPATCH_TABLE
        if args.phase == "all"
        else tuple(entry for entry in DISPATCH_TABLE if entry[0] == args.phase)
    )

    print(f"rehearse_isolation: Wave 2 dispatch — {len(selected)} phase(s)")
    print(f"  output_dir: {output_dir}")
    print(f"  manifest:   {args.manifest}")
    print(f"  dry_run:    {dry_run}")

    results: dict[str, dict[str, Any]] = {}
    any_error = False
    for cli_name, _, _ in selected:
        print(f"  -> {cli_name} ...", end="", flush=True)
        result = _dispatch(cli_name, manifest, output_dir, dry_run=dry_run)
        results[cli_name] = result
        print(f" {result['status']}")
        if result["status"] == "error":
            any_error = True
            for w in result["warnings"]:
                print(f"     WARNING: {w}", file=sys.stderr)

    # Write run-summary.json when at least one lane succeeded. Skipped-only
    # runs don't need a summary (nothing happened); error runs still need
    # one for forensics.
    if any(r["status"] in ("ok", "error") for r in results.values()):
        summary_path = output_dir / "run-summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(
                {
                    "run_started_at": time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                    ),
                    "manifest_path": str(args.manifest),
                    "phase_requested": args.phase,
                    "dry_run": dry_run,
                    "results": results,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"  summary: {summary_path}")

    return EXIT_OK if not any_error else EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())

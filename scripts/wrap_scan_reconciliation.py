"""Report-only bridge/backlog reconciliation scanner for session wrap-up.

Per bridge/gtkb-bridge-reconciliation-wrap-scan-check-002.md (GO at -002, WI-4238).

This scanner makes the VERIFIED bridge-reconciliation detector a *routine*
session-wrap signal rather than an operator-demand-only check. It reuses the
detector unchanged through its supported public surface
(``scripts/bridge_reconciliation_audit.py::run_audit``) and emits one
informational, report-only finding per non-zero deviation class plus a single
roll-up finding. Zero deviations yield a single "clean" informational finding.

It composes with — and does not replace — the other ``wrap_scan_*`` scanners
(``wrap_scan_consistency``, ``wrap_scan_cross_artifact_drift``,
``wrap_scan_hygiene``) and the on-demand ``gt bridge reconcile audit`` CLI.
It is read-only and report-only: it never mutates bridge, MemBase, project, or
correction-packet state, and it never writes a canonical surface.

EXIT CODES:
    0  Always. Findings are informational/report-only by design.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wrap_io import _atomic_write_text  # noqa: E402
from bridge_reconciliation_audit import run_audit  # noqa: E402

SCANNER_ID = "wrap_scan_reconciliation"
SEVERITY_INFORMATIONAL = "informational"
EXIT_OK = 0

DEFAULT_OUTPUT_DIR = ".groundtruth/session/wrap-scan"
REPORT_STEM = "reconciliation-scan"


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _finding(check: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "check": check,
        "severity": SEVERITY_INFORMATIONAL,
        "report_only": True,
        "message": message,
        **details,
    }


def _counts_by_class(audit_result: dict[str, Any]) -> dict[str, int]:
    """Derive per-class deviation counts from a ``run_audit`` result.

    Depends only on documented public keys. Prefers the canonical
    ``counts_by_class`` key emitted by ``run_audit``; falls back to the
    legacy ``counts`` key, then to deriving counts from the ``issues`` list
    (keyed by each issue's ``class``). Non-positive entries are dropped so a
    deviation class only appears when it actually occurred.
    """
    raw: dict[str, Any] = {}
    for key in ("counts_by_class", "counts"):
        value = audit_result.get(key)
        if isinstance(value, dict):
            raw = value
            break
    if not raw:
        for issue in audit_result.get("issues", []) or []:
            if isinstance(issue, dict):
                deviation_class = issue.get("class")
                if deviation_class:
                    raw[str(deviation_class)] = raw.get(str(deviation_class), 0) + 1
    counts: dict[str, int] = {}
    for deviation_class, count in raw.items():
        try:
            numeric = int(count)
        except (TypeError, ValueError):
            continue
        if numeric > 0:
            counts[str(deviation_class)] = numeric
    return dict(sorted(counts.items()))


def build_reconciliation_findings(audit_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Pure transform: ``run_audit`` result -> wrap-scan finding list.

    Emits one informational finding per non-zero deviation class (sorted by
    class name) plus a single roll-up finding carrying the total and the
    per-class breakdown. When there are no deviations, returns a single
    "clean" informational finding (never an error; report-only by design).
    """
    counts = _counts_by_class(audit_result)
    if not counts:
        return [
            _finding(
                "reconciliation_clean",
                "No bridge/backlog reconciliation drift detected.",
                deviation_total=0,
                counts_by_class={},
            )
        ]
    findings: list[dict[str, Any]] = []
    for deviation_class, count in counts.items():
        findings.append(
            _finding(
                "reconciliation_deviation_class",
                f"{count} bridge/backlog reconciliation deviation(s) of class '{deviation_class}'.",
                deviation_class=deviation_class,
                count=count,
            )
        )
    total = sum(counts.values())
    findings.append(
        _finding(
            "reconciliation_rollup",
            f"{total} bridge/backlog reconciliation deviation(s) across {len(counts)} class(es).",
            deviation_total=total,
            class_count=len(counts),
            counts_by_class=dict(counts),
        )
    )
    return findings


def scan(
    project_root: Path,
    *,
    db_path: Path | None = None,
    bridge_index: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Run the VERIFIED reconciliation detector read-only and shape findings.

    ``generated_at`` may be injected for deterministic tests; otherwise the
    audit result's own ``generated_at`` is carried through.
    """
    audit_result = run_audit(
        project_root=project_root,
        db_path=db_path,
        bridge_index=bridge_index,
    )
    findings = build_reconciliation_findings(audit_result)
    counts = _counts_by_class(audit_result)
    resolved_generated_at = generated_at if generated_at is not None else audit_result.get("generated_at")
    return {
        "scanner_id": SCANNER_ID,
        "generated_at": resolved_generated_at,
        "report_only": True,
        "severity_model": SEVERITY_INFORMATIONAL,
        "finding_count": len(findings),
        "findings": findings,
        "counts_by_class": dict(counts),
    }


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Bridge Reconciliation Wrap Scan", ""]
    lines.append(f"Scanner: `{SCANNER_ID}`")
    lines.append("Severity model: report-only informational findings.")
    generated_at = report.get("generated_at")
    if generated_at:
        lines.append(f"generated_at: `{generated_at}`")
    lines.append("")
    counts = report.get("counts_by_class") or {}
    lines.append("## Counts By Class")
    if counts:
        lines.extend(f"- {key}: {value}" for key, value in counts.items())
    else:
        lines.append("- none: 0")
    lines.append("")
    findings = report.get("findings", [])
    lines.append(f"## Findings ({len(findings)})")
    for finding in findings:
        lines.append(f"- **{finding['check']}**: {finding['message']}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--db-path", type=Path, default=None)
    parser.add_argument("--bridge-index", type=Path, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=f"Directory for {REPORT_STEM}.json + .md (default: <root>/{DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Write the JSON report to stdout instead of report files.",
    )
    args = parser.parse_args(argv)

    project_root = (args.project_root or _project_root()).resolve()
    report = scan(project_root, db_path=args.db_path, bridge_index=args.bridge_index)
    payload = render_json(report)

    if args.stdout:
        sys.stdout.write(payload)
        return EXIT_OK

    output_dir = (args.output_dir or (project_root / DEFAULT_OUTPUT_DIR)).resolve()
    _atomic_write_text(output_dir / f"{REPORT_STEM}.json", payload)
    _atomic_write_text(output_dir / f"{REPORT_STEM}.md", render_markdown(report))
    sys.stdout.write(f"{SCANNER_ID}: wrote {REPORT_STEM}.json + {REPORT_STEM}.md to {output_dir}\n")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

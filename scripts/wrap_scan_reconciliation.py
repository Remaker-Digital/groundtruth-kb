"""Report-only bridge/backlog reconciliation scanner for session wrap-up.

During the file-bridge transition, this scanner reports message counts only.
Counts and related bridge references never establish work-item completion.
Use the ordinary backlog and project CLI for canonical work state, independent
review and complete-project commit results. This scanner does not mutate those
records or perform lifecycle reconciliation.

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


def _bridge_status_counts(project_root: Path, bridge_dir: Path | None = None) -> dict[str, int]:
    from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

    resolved_bridge_dir = bridge_dir or project_root / "bridge"
    counts: dict[str, int] = {}
    for doc in scan_expected_documents(project_root, resolved_bridge_dir).values():
        latest_path = Path(doc.files[-1])
        if not latest_path.is_absolute():
            latest_path = project_root / latest_path
        status = status_from_bridge_file(latest_path) or "UNKNOWN"
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def build_reconciliation_findings(status_counts: dict[str, int]) -> list[dict[str, Any]]:
    total = sum(status_counts.values())
    return [
        _finding(
            "bridge_status_rollup",
            f"{total} status-bearing bridge document(s) visible to the wrap scanner.",
            bridge_document_total=total,
            bridge_status_counts=dict(status_counts),
        )
    ]


def scan(
    project_root: Path,
    *,
    db_path: Path | None = None,
    bridge_dir: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Read bridge lifecycle status counts and shape report-only findings.

    ``generated_at`` may be injected for deterministic tests. ``db_path`` is
    retained for CLI compatibility but is not read by this lightweight scanner.
    """
    _ = db_path
    counts = _bridge_status_counts(project_root, bridge_dir)
    findings = build_reconciliation_findings(counts)
    return {
        "scanner_id": SCANNER_ID,
        "generated_at": generated_at,
        "report_only": True,
        "severity_model": SEVERITY_INFORMATIONAL,
        "finding_count": len(findings),
        "findings": findings,
        "bridge_status_counts": dict(counts),
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
    counts = report.get("bridge_status_counts") or {}
    lines.append("## Bridge Status Counts")
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
    parser.add_argument("--bridge-dir", type=Path, default=None)
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
    report = scan(project_root, db_path=args.db_path, bridge_dir=args.bridge_dir)
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

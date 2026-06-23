# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only validator for autonomous dispatch loop bridge evidence.

Reads the numbered bridge file chain for a given slug and confirms the
reference lifecycle phases (NEW proposal → GO → implementation report →
VERIFIED, with optional NO-GO/REVISED cycles in between). Emits structured
JSON suitable for benchmarks and a concise human-readable summary.

Authority: bridge/gtkb-wi4742-autonomous-dispatch-loop-health-001.md GO at -002.
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001,
       DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001.

Default reference case: gtkb-lo-harness-turn-budget-fix (WI-4734, session
019eec48-908b-7592-a0c6-4e25b7ca4df0), the proven autonomous loop from 2026-06-22.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REFERENCE_BRIDGE_ID = "gtkb-lo-harness-turn-budget-fix"
REFERENCE_WI = "WI-4734"
REFERENCE_SESSION_ID = "019eec48-908b-7592-a0c6-4e25b7ca4df0"

# Ordered lifecycle phases required for a "complete" autonomous loop
REQUIRED_LIFECYCLE_PHASES = ["proposal", "go", "implementation_report", "verified"]

_STATUS_TOKEN_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN)\s*$",
    re.IGNORECASE,
)

_WI_RE = re.compile(r"^\s*Work Item:\s*(WI-\d+)\s*$", re.MULTILINE)
_SESSION_RE = re.compile(r"author_session_context_id:\s*([0-9a-f\-]+)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Bridge-file reading
# ---------------------------------------------------------------------------


@dataclass
class BridgeVersion:
    path: Path
    number: int
    status: str
    raw_text: str
    work_items: list[str] = field(default_factory=list)
    session_ids: list[str] = field(default_factory=list)


def _read_bridge_versions(bridge_dir: Path, slug: str) -> list[BridgeVersion]:
    """Return bridge file versions in ascending numeric order."""
    pattern = re.compile(rf"^{re.escape(slug)}-(\d+)\.md$")
    results: list[BridgeVersion] = []
    for p in bridge_dir.iterdir():
        m = pattern.match(p.name)
        if not m:
            continue
        number = int(m.group(1))
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        status = _extract_status(text)
        work_items = _WI_RE.findall(text)
        session_ids = _SESSION_RE.findall(text)
        results.append(
            BridgeVersion(
                path=p,
                number=number,
                status=status,
                raw_text=text,
                work_items=work_items,
                session_ids=session_ids,
            )
        )
    results.sort(key=lambda v: v.number)
    return results


def _extract_status(text: str) -> str:
    """Return the canonical status token from the first non-blank line."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        m = _STATUS_TOKEN_RE.match(stripped)
        if m:
            return m.group(1).upper()
        return "UNKNOWN"
    return "EMPTY"


# ---------------------------------------------------------------------------
# Lifecycle classification
# ---------------------------------------------------------------------------


def _classify_version(version: BridgeVersion, prev_status: Optional[str]) -> str:
    """Map a version status to a semantic lifecycle phase."""
    s = version.status
    if s == "NEW":
        if prev_status is None:
            return "proposal"
        return "implementation_report"
    if s == "REVISED":
        return "revised_report"
    if s == "GO":
        return "go"
    if s == "NO-GO":
        return "no_go"
    if s == "VERIFIED":
        return "verified"
    if s == "ADVISORY":
        return "advisory"
    if s in ("DEFERRED", "WITHDRAWN"):
        return s.lower()
    return "unknown"


def _analyze_lifecycle(versions: list[BridgeVersion]) -> dict:
    """Return lifecycle classification and phase sequence."""
    phases: list[dict] = []
    prev_status: Optional[str] = None
    for v in versions:
        phase = _classify_version(v, prev_status)
        phases.append(
            {
                "version": v.number,
                "status": v.status,
                "phase": phase,
                "path": str(v.path),
                "work_items": v.work_items,
                "session_ids": v.session_ids,
            }
        )
        prev_status = v.status
    return {"versions": phases}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class HealthResult:
    slug: str
    complete: bool
    phases_present: list[str]
    phases_missing: list[str]
    wi_found: bool
    expected_wi: Optional[str]
    session_found: bool
    expected_session_id: Optional[str]
    version_count: int
    lifecycle: dict
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "complete": self.complete,
            "phases_present": self.phases_present,
            "phases_missing": self.phases_missing,
            "wi_found": self.wi_found,
            "expected_wi": self.expected_wi,
            "session_found": self.session_found,
            "expected_session_id": self.expected_session_id,
            "version_count": self.version_count,
            "lifecycle": self.lifecycle,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_loop(
    bridge_dir: Path,
    slug: str,
    *,
    expected_wi: Optional[str] = None,
    expected_session_id: Optional[str] = None,
) -> HealthResult:
    """Validate the autonomous loop evidence for a bridge slug."""
    errors: list[str] = []
    warnings: list[str] = []

    versions = _read_bridge_versions(bridge_dir, slug)
    if not versions:
        return HealthResult(
            slug=slug,
            complete=False,
            phases_present=[],
            phases_missing=list(REQUIRED_LIFECYCLE_PHASES),
            wi_found=False,
            expected_wi=expected_wi,
            session_found=False,
            expected_session_id=expected_session_id,
            version_count=0,
            lifecycle={"versions": []},
            errors=[f"No bridge files found for slug '{slug}' in {bridge_dir}"],
        )

    lifecycle = _analyze_lifecycle(versions)
    phases_seen: set[str] = {p["phase"] for p in lifecycle["versions"]}

    # Check required phases
    phases_present = [p for p in REQUIRED_LIFECYCLE_PHASES if p in phases_seen]
    phases_missing = [p for p in REQUIRED_LIFECYCLE_PHASES if p not in phases_seen]

    # Check WI
    all_wis: list[str] = []
    for v in versions:
        all_wis.extend(v.work_items)
    wi_found = expected_wi in all_wis if expected_wi else bool(all_wis)

    if expected_wi and not wi_found:
        errors.append(f"Expected Work Item {expected_wi} not found in any bridge file")

    # Check session
    all_sessions: list[str] = []
    for v in versions:
        all_sessions.extend(v.session_ids)
    session_found = expected_session_id in all_sessions if expected_session_id else bool(all_sessions)

    if expected_session_id and not session_found:
        warnings.append(
            f"Expected session id {expected_session_id} not found; found: " + (", ".join(set(all_sessions)) or "(none)")
        )

    complete = not phases_missing and wi_found and (not expected_session_id or session_found)

    return HealthResult(
        slug=slug,
        complete=complete,
        phases_present=phases_present,
        phases_missing=phases_missing,
        wi_found=wi_found,
        expected_wi=expected_wi,
        session_found=session_found,
        expected_session_id=expected_session_id,
        version_count=len(versions),
        lifecycle=lifecycle,
        errors=errors,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------


def _render_summary(result: HealthResult) -> str:
    lines: list[str] = []
    status_label = "COMPLETE" if result.complete else "INCOMPLETE"
    lines.append(f"Autonomous dispatch loop health — {result.slug} — {status_label}")
    lines.append(f"  Versions found  : {result.version_count}")
    lines.append(f"  Phases present  : {', '.join(result.phases_present) or '(none)'}")
    lines.append(f"  Phases missing  : {', '.join(result.phases_missing) or '(none)'}")
    if result.expected_wi:
        wi_ok = "YES" if result.wi_found else "NO"
        lines.append(f"  Work Item check : {result.expected_wi} found={wi_ok}")
    if result.expected_session_id:
        sess_ok = "YES" if result.session_found else "NO"
        lines.append(f"  Session check   : {result.expected_session_id[:12]}... found={sess_ok}")
    for err in result.errors:
        lines.append(f"  ERROR: {err}")
    for warn in result.warnings:
        lines.append(f"  WARN : {warn}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only validator for autonomous dispatch loop bridge evidence.")
    parser.add_argument(
        "--bridge-id",
        default=REFERENCE_BRIDGE_ID,
        help=f"Bridge slug to validate (default: {REFERENCE_BRIDGE_ID}).",
    )
    parser.add_argument(
        "--expected-wi",
        default=None,
        help="Expected Work Item ID in the bridge chain (e.g. WI-4734).",
    )
    parser.add_argument(
        "--expected-session-id",
        default=None,
        help="Expected author_session_context_id in the implementation report(s).",
    )
    parser.add_argument(
        "--bridge-dir",
        type=Path,
        default=None,
        help="Path to the bridge/ directory (default: auto-resolve from script location).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output instead of human-readable summary.",
    )
    parser.add_argument(
        "--reference",
        action="store_true",
        help=(
            "Validate the canonical reference autonomous loop "
            f"({REFERENCE_BRIDGE_ID}, {REFERENCE_WI}, session {REFERENCE_SESSION_ID})."
        ),
    )
    return parser


def _resolve_bridge_dir(explicit: Optional[Path]) -> Path:
    if explicit is not None:
        return explicit
    return Path(__file__).resolve().parents[1] / "bridge"


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_argparser()
    args = parser.parse_args(argv)

    slug = args.bridge_id
    expected_wi = args.expected_wi
    expected_session_id = args.expected_session_id

    if args.reference:
        slug = REFERENCE_BRIDGE_ID
        expected_wi = REFERENCE_WI
        expected_session_id = REFERENCE_SESSION_ID

    bridge_dir = _resolve_bridge_dir(args.bridge_dir)

    result = validate_loop(
        bridge_dir,
        slug,
        expected_wi=expected_wi,
        expected_session_id=expected_session_id,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_render_summary(result))

    return 0 if result.complete else 1


if __name__ == "__main__":
    sys.exit(main())

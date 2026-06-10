# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Migrate bridge proposal/verdict files to canonical bridge_kind values."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Resolve packages from groundtruth-kb/src/
for _parent in Path(__file__).resolve().parents:
    _gt_src = _parent / "groundtruth-kb" / "src"
    if _gt_src.is_dir():
        if str(_gt_src) not in sys.path:
            sys.path.insert(0, str(_gt_src))
        break

from groundtruth_kb.bridge.taxonomy import BridgeKind

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = PROJECT_ROOT / "bridge"
BACKUP_DIR = PROJECT_ROOT / ".gtkb-state" / "bridge-backup-taxonomy-migration"

# Matches: bridge_kind: <value>
BRIDGE_KIND_RE = re.compile(r"^(bridge_kind:\s*)([A-Za-z0-9_-]+)(.*)$", re.IGNORECASE | re.MULTILINE)

MAPPING = {
    # LO Verdicts
    "loyal_opposition_verdict": "lo_verdict",
    "verification_verdict": "lo_verdict",
    "review_verdict": "lo_verdict",
    "loyal_opposition_review": "lo_verdict",
    "loyal_opposition_verification": "lo_verdict",
    "review": "lo_verdict",
    "proposal_verdict": "lo_verdict",
    "proposal_review_verdict": "lo_verdict",
    "verification": "lo_verdict",
    "closure": "lo_verdict",
    "implementation_review": "lo_verdict",
    "supersession_closure_report": "lo_verdict",
    "supersession_closure": "lo_verdict",
    # Prime Proposals
    "implementation_proposal": "prime_proposal",
    "proposal": "prime_proposal",
    "prime_implementation_proposal": "prime_proposal",
    "implementation_slice": "prime_proposal",
    "scoping_proposal": "prime_proposal",
    # Prime Reports
    "implementation_report": "implementation_report",
    "post_implementation_report": "implementation_report",
    "prime_builder_post_implementation_report": "implementation_report",
    "prime_implementation_report": "implementation_report",
    "implementation": "implementation_report",
    "implementation_report_revision": "implementation_report",
    # Governance & Advisory
    "governance_review": "governance_advisory",
    "loyal_opposition_advisory": "governance_advisory",
    "advisory_report": "governance_advisory",
    "advisory": "governance_advisory",
    # Index Reconciliation
    "index_reconciliation": "index_reconciliation",
    # Operational State Change
    "operational_state_change": "operational_state_change",
}


def map_bridge_kind(old_val: str, first_line: str) -> str:
    old_val_lower = old_val.lower().strip()
    if old_val_lower in MAPPING:
        return MAPPING[old_val_lower]

    # Heuristic matching
    if any(x in old_val_lower for x in ("verdict", "review", "verification", "closure")):
        return "lo_verdict"
    if any(x in old_val_lower for x in ("proposal", "slice")):
        return "prime_proposal"
    if any(x in old_val_lower for x in ("report", "post_implementation")):
        return "implementation_report"
    if "advisory" in old_val_lower:
        return "governance_advisory"

    # First line fallback
    first_line_clean = first_line.strip().upper()
    if any(first_line_clean.startswith(x) for x in ("GO", "NO-GO", "VERIFIED", "WITHDRAWN")):
        return "lo_verdict"
    if first_line_clean == "ADVISORY":
        return "governance_advisory"

    return "prime_proposal"


def perform_backup() -> None:
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for p in BRIDGE_DIR.glob("*.md"):
        if p.is_file():
            shutil.copy2(p, BACKUP_DIR / p.name)
    print(f"Backup created at: {BACKUP_DIR.relative_to(PROJECT_ROOT)}")


def perform_rollback() -> None:
    if not BACKUP_DIR.is_dir():
        print(f"No backup directory found at {BACKUP_DIR.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        sys.exit(1)

    for p in BACKUP_DIR.glob("*.md"):
        if p.is_file():
            shutil.copy2(p, BRIDGE_DIR / p.name)
    print("Rollback completed successfully.")


def get_first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        if line.strip():
            return line
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollback", action="store_true", help="Restore files from backup.")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without modifying files.")
    args = parser.parse_args(argv)

    if args.rollback:
        perform_rollback()
        return 0

    if not args.dry_run:
        perform_backup()

    modified_count = 0
    total_count = 0

    allowed_kinds = {k.value for k in BridgeKind}

    for p in BRIDGE_DIR.glob("*.md"):
        if p.name.lower() == "index.md":
            continue
        if not re.search(r"-\d{3,}\.md$", p.name):
            continue

        total_count += 1
        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {p.name}: {e}", file=sys.stderr)
            continue

        match = BRIDGE_KIND_RE.search(content)
        if not match:
            continue

        old_val = match.group(2)
        if old_val.lower() in allowed_kinds:
            # Already canonical case/value
            continue

        first_line = get_first_nonblank_line(content)
        new_val = map_bridge_kind(old_val, first_line)

        # Replace in-place
        def repl(m: re.Match) -> str:
            return f"{m.group(1)}{new_val}{m.group(3)}"

        new_content = BRIDGE_KIND_RE.sub(repl, content)

        if new_content != content:
            modified_count += 1
            if args.dry_run:
                print(f"[DRY-RUN] {p.name}: bridge_kind: {old_val} -> {new_val}")
            else:
                try:
                    p.write_text(new_content, encoding="utf-8")
                    print(f"Migrated {p.name}: bridge_kind: {old_val} -> {new_val}")
                except Exception as e:
                    print(f"Error writing {p.name}: {e}", file=sys.stderr)

    print(f"Migration finished. Total files: {total_count}, Modified: {modified_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

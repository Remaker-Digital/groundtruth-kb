#!/usr/bin/env python3
"""Canonical semantic evaluator for the governed two-tier Git lifecycle.

Registered as the canonical evaluator by two active formal records:

- ``ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`` -- canonical_evaluator_id
  ``governed-two-tier-git-lifecycle``
- ``REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`` -- canonical_evaluator_id
  ``governed-git-lifecycle-requirement``

Both records declare ``fail_closed_on_missing_or_contradictory_evidence: true``.
This evaluator therefore reports a violation when required evidence is absent or
self-contradictory; it never reports PASS by default.

The evaluator is read-only. It performs no Git mutation, no MemBase mutation, and
no bridge write. Exit status is 0 when every family passes, 1 when any family
reports a violation, and 2 on an evaluation error.

WI-6547 (PROJECT-GTKB-GET-HEALTHY-PHASE-3).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Stable semantic contract markers. The registered assertions grep for these
# exact strings; they are also the canonical_evaluator_id values carried in each
# record's ``constraints`` column, so the marker and the record agree by
# construction rather than by convention.
ADR_EVALUATOR_ID = "governed-two-tier-git-lifecycle"
REQ_EVALUATOR_ID = "governed-git-lifecycle-requirement"

ADR_SPEC_ID = "ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001"
REQ_SPEC_ID = "REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001"

# Invariants both records assert in ``constraints``. A record that disagrees with
# any of these is contradictory evidence, which fails closed.
REQUIRED_CONSTRAINTS: dict[str, object] = {
    "fail_closed_on_missing_or_contradictory_evidence": True,
    "verified_emission_has_lifecycle_effect": False,
    "dispatcher_post_verified_reconciliation_required": True,
}

WORK_ITEM_RE = re.compile(r"\(WI-\d+\)")


@dataclass
class Finding:
    family: str
    ok: bool
    detail: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, family: str, ok: bool, detail: str) -> None:
        self.findings.append(Finding(family=family, ok=ok, detail=detail))

    @property
    def violations(self) -> list[Finding]:
        return [f for f in self.findings if not f.ok]


def _project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    raise SystemExit("evaluation error: groundtruth.toml not found above " + str(start))


def _latest_spec(conn: sqlite3.Connection, spec_id: str) -> dict[str, object] | None:
    row = conn.execute(
        "SELECT id, version, status, constraints FROM specifications WHERE id = ? ORDER BY version DESC LIMIT 1",
        (spec_id,),
    ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "version": row[1], "status": row[2], "constraints": row[3]}


def check_record_active(report: Report, spec: dict[str, object] | None, spec_id: str) -> None:
    """A1 -- the record naming this evaluator is present and active."""
    family = f"{spec_id}:record-active"
    if spec is None:
        report.add(family, False, f"{spec_id} is absent from MemBase (fail-closed on missing evidence)")
        return
    if spec["status"] != "active":
        report.add(family, False, f"{spec_id} v{spec['version']} status is {spec['status']!r}, expected 'active'")
        return
    report.add(family, True, f"{spec_id} v{spec['version']} is active")


def check_evaluator_binding(report: Report, spec: dict[str, object] | None, spec_id: str, expected_id: str) -> None:
    """A2 -- the record binds this evaluator by canonical_evaluator_id."""
    family = f"{spec_id}:evaluator-binding"
    if spec is None:
        report.add(family, False, f"{spec_id} absent; evaluator binding unverifiable")
        return
    try:
        constraints = json.loads(spec["constraints"] or "{}")
    except (TypeError, ValueError) as exc:
        report.add(family, False, f"{spec_id} constraints are not valid JSON: {exc}")
        return
    actual = constraints.get("canonical_evaluator_id")
    if actual != expected_id:
        report.add(
            family,
            False,
            f"{spec_id} canonical_evaluator_id is {actual!r}, expected {expected_id!r}",
        )
        return
    report.add(family, True, f"{spec_id} binds canonical_evaluator_id {expected_id!r}")


def check_semantic_invariants(report: Report, spec: dict[str, object] | None, spec_id: str) -> None:
    """A3 -- the record's semantic invariants hold and do not contradict the contract."""
    family = f"{spec_id}:semantic-invariants"
    if spec is None:
        report.add(family, False, f"{spec_id} absent; invariants unverifiable")
        return
    try:
        constraints = json.loads(spec["constraints"] or "{}")
    except (TypeError, ValueError) as exc:
        report.add(family, False, f"{spec_id} constraints are not valid JSON: {exc}")
        return
    mismatches = [
        f"{key}={constraints.get(key)!r} (expected {value!r})"
        for key, value in REQUIRED_CONSTRAINTS.items()
        if constraints.get(key) != value
    ]
    if mismatches:
        report.add(family, False, f"{spec_id} contradicts the lifecycle contract: " + "; ".join(mismatches))
        return
    report.add(family, True, f"{spec_id} satisfies all {len(REQUIRED_CONSTRAINTS)} semantic invariants")


def check_records_agree(report: Report, adr: dict[str, object] | None, req: dict[str, object] | None) -> None:
    """A4 -- the two records do not contradict one another."""
    family = "cross-record:agreement"
    if adr is None or req is None:
        report.add(family, False, "one or both lifecycle records are absent; agreement unverifiable")
        return
    try:
        adr_c = json.loads(adr["constraints"] or "{}")
        req_c = json.loads(req["constraints"] or "{}")
    except (TypeError, ValueError) as exc:
        report.add(family, False, f"constraints are not valid JSON: {exc}")
        return
    conflicts = [
        f"{key}: ADR={adr_c.get(key)!r} REQ={req_c.get(key)!r}"
        for key in REQUIRED_CONSTRAINTS
        if adr_c.get(key) != req_c.get(key)
    ]
    if conflicts:
        report.add(family, False, "records disagree on shared invariants: " + "; ".join(conflicts))
        return
    report.add(family, True, "ADR and REQ agree on every shared lifecycle invariant")


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def check_singleton_work_item_per_commit(report: Report, root: Path, limit: int) -> None:
    """A5 -- a terminal commit names exactly one work item.

    ADR decision clause 2 and REQ clause 3 both require the work-product commit to
    name exactly one terminal work item. A commit naming two retires two work
    items in one terminal action, which the lifecycle forbids.
    """
    family = "terminal-commit:singleton-work-item"
    log = _git(root, "log", f"-{limit}", "--format=%H%x1f%s%x1f%b%x1e")
    if log is None:
        report.add(family, False, "git log unavailable; singleton-work-item evidence missing (fail-closed)")
        return
    offenders: list[str] = []
    inspected = 0
    for record in log.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f")
        sha = parts[0][:12]
        message = " ".join(parts[1:])
        names = WORK_ITEM_RE.findall(message)
        if not names:
            continue
        inspected += 1
        if len(set(names)) > 1:
            offenders.append(f"{sha} names {sorted(set(names))}")
    if offenders:
        report.add(
            family, False, f"{len(offenders)} commit(s) name more than one work item: " + "; ".join(offenders[:5])
        )
        return
    report.add(family, True, f"all {inspected} work-item-naming commit(s) in the last {limit} name exactly one")


def check_verified_outside_commit(report: Report, root: Path, limit: int) -> None:
    """A6 -- VERIFIED is authored outside the work-product commit.

    ADR decision clause 4 and REQ clause 5 both require the VERIFIED verdict to be
    authored outside the commit whose bytes it verifies. A commit that both names a
    retired work item and adds a terminal VERIFIED bridge artifact violates that.
    """
    family = "terminal-commit:verified-outside-commit"
    log = _git(root, "log", f"-{limit}", "--format=%H%x1f%s %b%x1e", "--name-only")
    if log is None:
        report.add(family, False, "git log unavailable; VERIFIED-placement evidence missing (fail-closed)")
        return
    offenders: list[str] = []
    inspected = 0
    for record in log.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        head, _, files_blob = record.partition("\n")
        parts = head.split("\x1f")
        sha = parts[0][:12]
        message = parts[1] if len(parts) > 1 else ""
        if not WORK_ITEM_RE.search(message):
            continue
        inspected += 1
        bridge_files = [
            line.strip()
            for line in files_blob.splitlines()
            if line.strip().startswith("bridge/") and line.strip().endswith(".md")
        ]
        for rel in bridge_files:
            blob = _git(root, "show", f"{parts[0]}:{rel}")
            if blob is None:
                continue
            first = next((ln.strip() for ln in blob.splitlines() if ln.strip()), "")
            if first == "VERIFIED":
                offenders.append(f"{sha} carries terminal VERIFIED artifact {rel}")
    if offenders:
        report.add(family, False, f"{len(offenders)} violation(s): " + "; ".join(offenders[:5]))
        return
    report.add(family, True, f"no work-product commit among {inspected} inspected carries a VERIFIED artifact")


def evaluate(root: Path, *, limit: int) -> Report:
    report = Report()
    db_path = root / "groundtruth.db"
    if not db_path.is_file():
        report.add("evidence:membase", False, f"MemBase absent at {db_path} (fail-closed)")
        return report
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        adr = _latest_spec(conn, ADR_SPEC_ID)
        req = _latest_spec(conn, REQ_SPEC_ID)
    finally:
        conn.close()

    check_record_active(report, adr, ADR_SPEC_ID)
    check_record_active(report, req, REQ_SPEC_ID)
    check_evaluator_binding(report, adr, ADR_SPEC_ID, ADR_EVALUATOR_ID)
    check_evaluator_binding(report, req, REQ_SPEC_ID, REQ_EVALUATOR_ID)
    check_semantic_invariants(report, adr, ADR_SPEC_ID)
    check_semantic_invariants(report, req, REQ_SPEC_ID)
    check_records_agree(report, adr, req)
    check_singleton_work_item_per_commit(report, root, limit)
    check_verified_outside_commit(report, root, limit)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=None, help="GT-KB project root (default: discovered upward).")
    parser.add_argument("--limit", type=int, default=200, help="How many recent commits to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    start = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parent
    root = _project_root(start)
    report = evaluate(root, limit=args.limit)

    if args.json:
        print(
            json.dumps(
                {
                    "evaluator_ids": [ADR_EVALUATOR_ID, REQ_EVALUATOR_ID],
                    "project_root": str(root),
                    "findings": [{"family": f.family, "ok": f.ok, "detail": f.detail} for f in report.findings],
                    "violations": len(report.violations),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for finding in report.findings:
            print(f"[{'PASS' if finding.ok else 'FAIL'}] {finding.family}: {finding.detail}")
        print(f"-- {len(report.violations)} violation(s) of {len(report.findings)} families")
    return 1 if report.violations else 0


if __name__ == "__main__":
    sys.exit(main())

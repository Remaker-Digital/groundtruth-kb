"""Verify Slice 8.5 CI-green evidence in memory/release-readiness.md."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
READINESS_PATH = PROJECT_ROOT / "memory" / "release-readiness.md"

REPOSITORY = "Remaker-Digital/agent-red-customer-engagement"
BRANCH = "develop"
EVENT = "push"
HEAD_SHA = "98b7eab19812ed995d1e606d1d9854a7da803dab"
CONCLUSION = "success"
DELIB_ID = "DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE"

EXPECTED_HEADER = [
    "Workflow",
    "Repository",
    "Branch",
    "Event",
    "Head SHA",
    "Run ID",
    "URL",
    "Conclusion",
    "Authority",
]

REQUIRED_RUNS = {
    "Lint": "25296718957",
    "Release Candidate Gate": "25296719002",
    "SonarCloud": "25296718961",
    "Security Scan": "25296718958",
    "Python Tests": "25296718963",
}

TAG_GATE_PHRASES = [
    "v0.7.0-rc1 remains unauthorized",
    "canonical migration",
    "canonical CI",
]


def _strip_code(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == "`" and value[-1] == "`":
        return value[1:-1].strip()
    return value


def _split_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [_strip_code(cell) for cell in stripped.strip("|").split("|")]
    return [cell.strip() for cell in cells]


def _is_separator(cells: list[str]) -> bool:
    return all(cell and set(cell) <= {"-", ":", " "} for cell in cells)


def _evidence_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_evidence_table = False
    for line in text.splitlines():
        cells = _split_table_row(line)
        if cells is None:
            continue
        if cells == EXPECTED_HEADER:
            in_evidence_table = True
            continue
        if not in_evidence_table:
            continue
        if _is_separator(cells):
            continue
        if len(cells) != len(EXPECTED_HEADER):
            # Another markdown table began; the Slice 8.5 evidence table is over.
            if rows:
                break
            continue
        rows.append(dict(zip(EXPECTED_HEADER, cells, strict=True)))
    return rows


def verify_text(text: str) -> list[str]:
    """Return verification errors; an empty list means PASS."""
    errors: list[str] = []

    if "### Slice 8.5 CI-green evidence (transient exception)" not in text:
        errors.append("missing Slice 8.5 CI-green evidence section")

    b6_rows = [line for line in text.splitlines() if line.startswith("| B6")]
    if not b6_rows:
        errors.append("missing B6 blocker-outcome row")
    else:
        for row in b6_rows:
            if "DEFERRED to Slice 8.5" in row:
                errors.append("B6 blocker-outcome row still records deferred state")
            if "GREEN" not in row:
                errors.append("B6 blocker-outcome row does not record GREEN evidence")
            if DELIB_ID not in row:
                errors.append("B6 blocker-outcome row does not cite transient-exception DELIB")

    rows = _evidence_rows(text)
    if len(rows) != len(REQUIRED_RUNS):
        errors.append(f"expected {len(REQUIRED_RUNS)} Slice 8.5 evidence rows, found {len(rows)}")

    seen: dict[str, int] = {}
    for row in rows:
        workflow = row.get("Workflow", "")
        seen[workflow] = seen.get(workflow, 0) + 1
        if workflow not in REQUIRED_RUNS:
            errors.append(f"unexpected workflow evidence row: {workflow!r}")
            continue

        run_id = REQUIRED_RUNS[workflow]
        expected_url = f"https://github.com/{REPOSITORY}/actions/runs/{run_id}"
        expected_values = {
            "Repository": REPOSITORY,
            "Branch": BRANCH,
            "Event": EVENT,
            "Head SHA": HEAD_SHA,
            "Run ID": run_id,
            "URL": expected_url,
            "Conclusion": CONCLUSION,
        }
        for field, expected in expected_values.items():
            actual = row.get(field, "")
            if actual != expected:
                errors.append(f"{workflow}: expected {field}={expected!r}, got {actual!r}")
        if DELIB_ID not in row.get("Authority", ""):
            errors.append(f"{workflow}: missing full DELIB authority citation")

    for workflow in REQUIRED_RUNS:
        count = seen.get(workflow, 0)
        if count == 0:
            errors.append(f"missing workflow evidence row: {workflow}")
        elif count > 1:
            errors.append(f"duplicate workflow evidence rows for {workflow}: {count}")

    for phrase in TAG_GATE_PHRASES:
        if phrase not in text:
            errors.append(f"missing tag-gate phrase: {phrase!r}")

    return errors


def verify_file(path: Path = READINESS_PATH) -> list[str]:
    if not path.exists():
        return [f"missing release readiness file: {path}"]
    return verify_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    path = Path(args[0]) if args else READINESS_PATH
    errors = verify_file(path)
    if errors:
        print("FAIL Slice 8.5 CI-green evidence verification")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS Slice 8.5 CI-green evidence verification ({len(REQUIRED_RUNS)} workflows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

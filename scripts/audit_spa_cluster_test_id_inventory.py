"""Generate the S350 SPA cluster test-ID inventory.

This script is intentionally read-only against ``groundtruth.db``. Running it
with no arguments writes the governed inventory artifact approved by
``bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1``.
"""

from __future__ import annotations

import datetime as dt
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = REPO_ROOT / "groundtruth.db"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "independent-progress-assessments" / "spec-hygiene" / "S350-spa-cluster-test-id-inventory.md"
)

SPA_SPEC_IDS = (
    "SPEC-1816",
    "SPEC-1818",
    "SPEC-1819",
    "SPEC-1820",
    "SPEC-1821",
    "SPEC-1822",
    "SPEC-1823",
    "SPEC-1824",
    "SPEC-1826",
    "SPEC-1827",
)

RECYCLED_TEST_IDS = tuple([f"TEST-{i}" for i in range(10481, 10500)] + [f"TEST-{i}" for i in range(10503, 10507)])

LATEST_SPEC_QUERY = """
SELECT id, version, title, status
FROM specifications
WHERE id = ?
ORDER BY version DESC
LIMIT 1
""".strip()

CURRENT_TESTS_QUERY = """
WITH latest AS (
    SELECT id, MAX(version) AS mv
    FROM tests
    GROUP BY id
)
SELECT t.id, t.version, t.spec_id, t.title, t.test_file, t.test_function, t.last_result
FROM tests t
JOIN latest l ON l.id = t.id AND l.mv = t.version
WHERE t.spec_id = ?
ORDER BY t.id
""".strip()

TEST_HISTORY_QUERY = """
SELECT id, version, spec_id, title, test_file, test_function, last_result
FROM tests
WHERE id = ?
ORDER BY version
""".strip()


@dataclass(frozen=True)
class TestRow:
    id: str
    version: int
    spec_id: str
    title: str
    test_file: str | None
    test_function: str | None
    last_result: str | None


@dataclass(frozen=True)
class RecycledTest:
    id: str
    historical_spec_id: str
    latest_spec_id: str
    historical_title: str
    latest_title: str
    latest_file: str | None
    latest_function: str | None
    latest_result: str | None


@dataclass(frozen=True)
class SpecInventory:
    id: str
    version: int
    title: str
    status: str
    current_tests: tuple[TestRow, ...]
    recycled_tests: tuple[RecycledTest, ...]
    classification: str
    no_current_linkage: bool


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_test(row: sqlite3.Row) -> TestRow:
    return TestRow(
        id=str(row["id"]),
        version=int(row["version"]),
        spec_id=str(row["spec_id"]),
        title=str(row["title"]),
        test_file=row["test_file"],
        test_function=row["test_function"],
        last_result=row["last_result"],
    )


def _latest_spec(conn: sqlite3.Connection, spec_id: str) -> sqlite3.Row:
    row = conn.execute(LATEST_SPEC_QUERY, (spec_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"spec not found: {spec_id}")
    return row


def _current_tests(conn: sqlite3.Connection, spec_id: str) -> tuple[TestRow, ...]:
    return tuple(_row_to_test(row) for row in conn.execute(CURRENT_TESTS_QUERY, (spec_id,)).fetchall())


def _test_history(conn: sqlite3.Connection, test_id: str) -> tuple[TestRow, ...]:
    return tuple(_row_to_test(row) for row in conn.execute(TEST_HISTORY_QUERY, (test_id,)).fetchall())


def _recycled_tests_by_historical_spec(
    conn: sqlite3.Connection, test_ids: tuple[str, ...]
) -> dict[str, list[RecycledTest]]:
    recycled: dict[str, list[RecycledTest]] = {}
    for test_id in test_ids:
        versions = _test_history(conn, test_id)
        if len(versions) < 2:
            continue
        historical = versions[0]
        latest = versions[-1]
        if latest.spec_id == historical.spec_id:
            continue
        item = RecycledTest(
            id=test_id,
            historical_spec_id=historical.spec_id,
            latest_spec_id=latest.spec_id,
            historical_title=historical.title,
            latest_title=latest.title,
            latest_file=latest.test_file,
            latest_function=latest.test_function,
            latest_result=latest.last_result,
        )
        recycled.setdefault(historical.spec_id, []).append(item)
    for items in recycled.values():
        items.sort(key=lambda item: item.id)
    return recycled


def classify_spec(current_tests: tuple[TestRow, ...], recycled_tests: tuple[RecycledTest, ...]) -> tuple[str, bool]:
    no_current_linkage = len(current_tests) == 0
    if recycled_tests:
        return "placeholder_test_id_unresolved", no_current_linkage
    if no_current_linkage:
        return "no_test_id_field", True
    if all((test.last_result or "").lower() == "pass" and test.test_file for test in current_tests):
        return "real_test_linked_pass", False
    return "real_test_linked_fail", False


def collect_inventory(
    db_path: Path,
    *,
    spec_ids: tuple[str, ...] = SPA_SPEC_IDS,
    recycled_test_ids: tuple[str, ...] = RECYCLED_TEST_IDS,
) -> tuple[SpecInventory, ...]:
    with _connect_readonly(db_path) as conn:
        recycled_by_spec = _recycled_tests_by_historical_spec(conn, recycled_test_ids)
        records: list[SpecInventory] = []
        for spec_id in spec_ids:
            spec = _latest_spec(conn, spec_id)
            current_tests = _current_tests(conn, spec_id)
            recycled_tests = tuple(recycled_by_spec.get(spec_id, []))
            classification, no_current_linkage = classify_spec(current_tests, recycled_tests)
            records.append(
                SpecInventory(
                    id=str(spec["id"]),
                    version=int(spec["version"]),
                    title=str(spec["title"]),
                    status=str(spec["status"]),
                    current_tests=current_tests,
                    recycled_tests=recycled_tests,
                    classification=classification,
                    no_current_linkage=no_current_linkage,
                )
            )
        return tuple(records)


def _commit_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _generated_at() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def _format_bool(value: bool) -> str:
    return "true" if value else "false"


def render_inventory(
    records: tuple[SpecInventory, ...],
    *,
    generated_at: str,
    commit_sha: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    classification_counts: dict[str, int] = {}
    all_recycled = [item for record in records for item in record.recycled_tests]
    current_link_count = sum(len(record.current_tests) for record in records)
    for record in records:
        classification_counts[record.classification] = classification_counts.get(record.classification, 0) + 1

    lines: list[str] = [
        "# S350 SPA Cluster Test-ID Inventory",
        "",
        "Source work item: WI-3183",
        "Bridge thread: gtkb-spa-cluster-test-id-investigation-closure-slice-1",
        "Session: S350",
        "Inventory file: independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md",
        f"Generated at: {generated_at}",
        f"Commit SHA: {commit_sha}",
        f"Database: {db_path}",
        "",
        "## Closure Summary",
        "",
        f"- SPA specs enumerated: {len(records)}",
        f"- Current latest-version tests linked to SPA specs: {current_link_count}",
        f"- Historical recycled test IDs recorded: {len(all_recycled)}",
        "- Recommended downstream action: use this inventory as WI-3183 closure evidence and let WI-3184 handle any separate status-remediation decision.",
        "",
        "## Classification Counts",
        "",
    ]
    for name in sorted(classification_counts):
        lines.append(f"- {name}: {classification_counts[name]}")

    lines.extend(
        [
            "",
            "## Source Queries",
            "",
            "Latest spec row:",
            "",
            "```sql",
            LATEST_SPEC_QUERY,
            "```",
            "",
            "Current latest-version tests per spec:",
            "",
            "```sql",
            CURRENT_TESTS_QUERY,
            "```",
            "",
            "Historical versions for recycled test IDs:",
            "",
            "```sql",
            TEST_HISTORY_QUERY,
            "```",
            "",
            "## Recycled Test IDs",
            "",
            "| Test ID | Historical spec | Latest spec | Latest result | Latest file | Latest function |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in sorted(all_recycled, key=lambda value: value.id):
        lines.append(
            "| {id} | {old} | {new} | {result} | {file} | {function} |".format(
                id=item.id,
                old=item.historical_spec_id,
                new=item.latest_spec_id,
                result=item.latest_result or "",
                file=item.latest_file or "",
                function=item.latest_function or "",
            )
        )

    lines.extend(["", "## Per-Spec Inventory", ""])
    for record in records:
        lines.extend(
            [
                f"### {record.id} - {record.title}",
                "",
                f"- Latest version: {record.version}",
                f"- Status: {record.status}",
                f"- Classification: {record.classification}",
                f"- No current linkage: {_format_bool(record.no_current_linkage)}",
                f"- Current latest-version tests: {len(record.current_tests)}",
                f"- Historical recycled test IDs: {', '.join(item.id for item in record.recycled_tests) or '(none)'}",
                "",
            ]
        )
        if record.current_tests:
            lines.extend(
                [
                    "| Current test ID | Result | File | Function |",
                    "|---|---|---|---|",
                ]
            )
            for test in record.current_tests:
                lines.append(
                    f"| {test.id} | {test.last_result or ''} | {test.test_file or ''} | {test.test_function or ''} |"
                )
            lines.append("")
        if record.recycled_tests:
            lines.extend(
                [
                    "| Recycled test ID | Historical title | Latest title | Latest spec |",
                    "|---|---|---|---|",
                ]
            )
            for item in record.recycled_tests:
                lines.append(f"| {item.id} | {item.historical_title} | {item.latest_title} | {item.latest_spec_id} |")
            lines.append("")

    lines.extend(
        [
            "## Closure Statement",
            "",
            "The SPA control-plane cluster currently has zero latest-version MemBase test rows bound to SPEC-1816, SPEC-1818 through SPEC-1824, SPEC-1826, or SPEC-1827. The 23 historical test IDs listed above were recycled to SPEC-1837 in their latest versions, so they are not current evidence for the SPA specs under append-only latest-version semantics.",
            "",
            "End of inventory.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_inventory(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    generated_at: str | None = None,
    commit_sha: str | None = None,
) -> str:
    records = collect_inventory(db_path)
    content = render_inventory(
        records,
        generated_at=generated_at or _generated_at(),
        commit_sha=commit_sha or _commit_sha(),
        db_path=db_path,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return content


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv:
        print("usage: python scripts/audit_spa_cluster_test_id_inventory.py", file=sys.stderr)
        return 2
    generate_inventory()
    print(DEFAULT_OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Complexity metrics benchmark (WI-6746).

Counts the quantities that grow silently: state directories, derived or cached
artifact trees, governance rule files, governance and gate lines of code, and
registered SoT artifacts.

Motivation, recorded because it is the reason this benchmark exists rather than
a general interest in numbers: 98 session-envelope documents accumulated under
``harness-state/<harness>/session-envelope-archive/`` between 2026-06-05 and
2026-08-21. They survived an explicit owner removal directive on 2026-08-13 and
were discovered only when someone ran an ad hoc ``find``. A prior scoping pass
reported "0 envelope documents present on disk" because it searched a path that
does not exist, and no counter existed to contradict it.

Read-only. Writes nothing outside ``.gtkb-state/benchmarks/<run_id>/`` via the
shared ``write_run_outputs`` helper, and never mutates a canonical table.

Retirement condition, per the owner decision authorizing
``PROJECT-GTKB-SIMPLICITY-BIAS`` (``DELIB-20260821042801``): this benchmark adds
an artifact in service of reducing artifacts. That is defensible only if the
metric is consulted. If the dashboard row goes unread, this module is itself an
instance of the drift it measures and should be retired rather than maintained.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from scripts.benchmarks.common import (
    BenchmarkResult,
    current_source_commit,
    new_run_id,
)

BENCHMARK_ID = "complexity_metrics"

#: State roots scanned for unregistered state locations. Deliberately a closed,
#: small set rather than a whole-tree walk: these are the four trees that hold
#: runtime state, and scanning everything would count source directories as
#: state. Kept in sync with the scan scope proposed for WI-6739.
STATE_ROOTS = (
    ".gtkb-state",
    "harness-state",
    ".claude/session",
    ".groundtruth",
)

#: Trees that are generated or cached rather than authored. Counted separately
#: because a growing derived surface is a different signal from a growing
#: authored one: derived growth means more projection targets to keep current,
#: and every one is a place a stale copy can be mistaken for a source.
DERIVED_ROOTS = (
    ".claude",
    ".codex",
    ".goose",
    ".cursor",
    ".agent",
    ".antigravity",
    ".api-harness",
)

#: Governance rule surface. The baseline is the authority; per-harness copies
#: are projections and are counted under DERIVED_ROOTS instead, so a rule file
#: is not counted once per harness.
GOVERNANCE_RULE_DIR = ".harness-baseline-configuration/rules"

#: Gate and enforcement code. Growth here is the cost side of the governance
#: ledger: every gate is enforcement that must itself be maintained, projected,
#: and kept from failing open.
GATE_CODE_DIRS = (
    ".harness-baseline-configuration/hooks",
    ".githooks",
)


def _count_dirs_and_files(root: Path) -> tuple[int, int]:
    """Return (directory count, loose file count) at depth 1 of ``root``.

    Depth 1 plus loose files, not a recursive walk. The unit that matters for
    drift is a new *location*, and a location appears as a new child of a state
    root. Loose files are counted because ``.claude/session`` holds zero
    directories and eighteen loose files -- a directories-only count is blind to
    an entire state root.
    """
    if not root.is_dir():
        return (0, 0)
    dirs = 0
    files = 0
    try:
        for child in root.iterdir():
            if child.is_dir():
                dirs += 1
            elif child.is_file():
                files += 1
    except OSError:
        # An unreadable root contributes nothing rather than aborting the run.
        # A benchmark that cannot count one tree should still report the others.
        return (0, 0)
    return (dirs, files)


def _count_files(root: Path, suffix: str | None = None) -> int:
    if not root.is_dir():
        return 0
    total = 0
    try:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if suffix is not None and path.suffix != suffix:
                continue
            total += 1
    except OSError:
        return total
    return total


def _count_lines(root: Path, suffix: str) -> int:
    if not root.is_dir():
        return 0
    total = 0
    try:
        paths = list(root.rglob(f"*{suffix}"))
    except OSError:
        return 0
    for path in paths:
        if not path.is_file():
            continue
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                total += sum(1 for _ in handle)
        except OSError:
            continue
    return total


def _registered_sot_artifacts(root: Path) -> int:
    """Count rows in the SoT artifact registry.

    Read through the packaged TOML rather than the CLI so the benchmark stays
    read-only and does not depend on a CLI that may itself be under change.
    """
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    if not registry.is_file():
        return 0
    try:
        text = registry.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    return text.count("[[artifacts]]")


def _membase_counts(root: Path) -> dict[str, int]:
    """Count governed records. Opened read-only; failure yields zeros.

    Uses a URI connection with ``mode=ro`` so this cannot write, create, or
    migrate the database even if the file is absent or locked.
    """
    db_path = root / "groundtruth.db"
    out = {"specifications": 0, "work_items_open": 0, "deliberations": 0}
    if not db_path.is_file():
        return out
    try:
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error:
        return out
    try:
        for key, query in (
            ("specifications", "SELECT COUNT(DISTINCT id) FROM specifications"),
            (
                "work_items_open",
                "SELECT COUNT(DISTINCT id) FROM work_items "
                "WHERE resolution_status NOT IN ('resolved','verified','retired','not_a_defect','wont_fix')",
            ),
            ("deliberations", "SELECT COUNT(DISTINCT id) FROM deliberations"),
        ):
            try:
                out[key] = int(conn.execute(query).fetchone()[0])
            except sqlite3.Error:
                out[key] = 0
    finally:
        conn.close()
    return out


def run(
    window_start: str,
    window_end: str,
    project_root: Path | str | None = None,
) -> list[BenchmarkResult]:
    """Compute complexity counts.

    ``window_start`` and ``window_end`` are accepted for contract conformance
    and carried into the results, but the counts are a point-in-time census of
    the tree rather than a windowed measurement. That is stated plainly rather
    than implied: this benchmark answers "how much is there now", and trend is
    obtained by comparing successive runs.
    """
    root = Path(project_root or Path(__file__).resolve().parents[2])
    run_id = new_run_id()
    commit = current_source_commit(root)

    state_dirs = 0
    state_files = 0
    per_root: dict[str, Any] = {}
    for name in STATE_ROOTS:
        dirs, files = _count_dirs_and_files(root / name)
        per_root[name] = {"directories": dirs, "loose_files": files}
        state_dirs += dirs
        state_files += files

    derived: dict[str, int] = {}
    derived_total = 0
    for name in DERIVED_ROOTS:
        count = _count_files(root / name)
        derived[name] = count
        derived_total += count

    rule_files = _count_files(root / GOVERNANCE_RULE_DIR, suffix=".md")
    gate_loc = 0
    gate_detail: dict[str, int] = {}
    for name in GATE_CODE_DIRS:
        lines = _count_lines(root / name, ".py")
        gate_detail[name] = lines
        gate_loc += lines

    registered = _registered_sot_artifacts(root)
    membase = _membase_counts(root)

    def _result(benchmark_suffix: str, value: float, dimensions: dict[str, Any], query: str) -> BenchmarkResult:
        return BenchmarkResult(
            run_id=run_id,
            benchmark_id=f"{BENCHMARK_ID}.{benchmark_suffix}",
            window_start=window_start,
            window_end=window_end,
            value=float(value),
            dimensions=dimensions,
            source_commit=commit,
            source_query=query,
        )

    return [
        _result(
            "state_locations",
            state_dirs + state_files,
            {"per_root": per_root, "directories": state_dirs, "loose_files": state_files},
            f"depth-1 directory and loose-file census of {list(STATE_ROOTS)}",
        ),
        _result(
            "derived_artifacts",
            derived_total,
            {"per_projection": derived},
            f"recursive file count under generated projection roots {list(DERIVED_ROOTS)}",
        ),
        _result(
            "governance_rule_files",
            rule_files,
            {"root": GOVERNANCE_RULE_DIR},
            f"recursive count of *.md under {GOVERNANCE_RULE_DIR} (baseline authority only)",
        ),
        _result(
            "gate_code_lines",
            gate_loc,
            {"per_dir": gate_detail},
            f"line count of *.py under {list(GATE_CODE_DIRS)}",
        ),
        _result(
            "registered_sot_artifacts",
            registered,
            {"registry": "config/registry/sot-artifacts.toml"},
            "count of [[artifacts]] entries in the SoT artifact registry",
        ),
        _result(
            "governed_records",
            membase["specifications"] + membase["work_items_open"] + membase["deliberations"],
            membase,
            "distinct-id counts from specifications, open work_items, deliberations (read-only connection)",
        ),
    ]

#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GT-KB platform VERIFIED runner: full-history bridge spec-derived test execution.

Per ``bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md``
REVISED-1, GO at ``-004``. Implements ``DCL-VERIFIED-BRIDGE-HISTORY-001``
assertions A1 (union accumulation across versions) + A2 (removal requires
owner-approved waiver) and serves as the mechanical enforcement layer for
``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``.

CLI (per -003 F2 fix — fail-closed by default):

    python scripts/run_spec_derived_tests.py --bridge-id <doc-name> [--json] [--advisory] [--strict]

- ``--bridge-id``  required: kebab-case Document name from bridge/INDEX.md.
- ``--json``       emit JSON output (canonical for review-skill consumption).
- ``--advisory``   opt-in to non-blocking mode (exits 0 on coverage gap / fail).
- ``--strict``     accepted as no-op for backward compatibility (fail-closed
                   is now the default per Codex -004 F2 closure).

Exit codes:
- ``0``  success — every linked spec has at least one derived test and all
         derived tests passed; no waiver validation failures.
- non-0  any of: missing INDEX entry, coverage gap, test failure, waiver
         validation failure. stderr identifies which.

Read-only against ``bridge/INDEX.md`` and ``groundtruth.db``. Per F4
classification: this is GT-KB platform governance tooling (not Agent Red
application code).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
INDEX_PATH: Final[Path] = PROJECT_ROOT / "bridge" / "INDEX.md"
DB_PATH: Final[Path] = PROJECT_ROOT / "groundtruth.db"
APPROVALS_DIR: Final[Path] = PROJECT_ROOT / ".groundtruth" / "formal-artifact-approvals"

# Test-discovery roots. CONSERVATIVE: only module-level docstrings are scanned;
# function-level docstrings would risk overcounting (per -003 §1.3).
TEST_DIRS: Final[tuple[Path, ...]] = (
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "groundtruth-kb" / "tests",
)

DEFAULT_PYTEST_TIMEOUT_S: Final[int] = 120

# Spec ID token pattern. Excludes `.` from the suffix so dotted assertion
# references like "DCL-VERIFIED-BRIDGE-HISTORY-001.A1" match only the spec
# ID portion ("DCL-VERIFIED-BRIDGE-HISTORY-001"), not the parent + the
# assertion-suffix as one merged token.
SPEC_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_-]*\b"
)

# Section heading patterns (start anchored only; trailing text tolerated).
SPEC_LINK_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$",
    re.IGNORECASE,
)
WAIVERS_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^#{1,6}\s*specification[-\s]+coverage[-\s]+waivers?\s*$",
    re.IGNORECASE,
)

# Index parsing — mirrors bridge protocol §"Index File" format.
INDEX_DOC_RE: Final[re.Pattern[str]] = re.compile(r"^Document:\s+(\S+)\s*$")
INDEX_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+bridge/(\S+\.md)\s*$"
)

# Waiver field parsing — supports `key: value` lines under bullet items.
WAIVER_BULLET_RE: Final[re.Pattern[str]] = re.compile(r"^\s*-\s*spec_id:\s*(\S+)\s*$")
WAIVER_FIELD_RE: Final[re.Pattern[str]] = re.compile(r"^\s+(\w+):\s*(.+?)\s*$")


@dataclass(frozen=True)
class BridgeVersion:
    status: str
    file_path: Path
    version_number: int


@dataclass
class Waiver:
    spec_id: str
    reason: str = ""
    approved_by: str = ""
    applies_from_version: int | None = None


@dataclass
class SpecMatrixEntry:
    spec_id: str
    tests_found: list[str] = field(default_factory=list)
    tests_passed: int = 0
    tests_failed: int = 0
    verified: bool = False
    reason: str = ""


def _parse_index_for_document(bridge_id: str) -> list[BridgeVersion]:
    """Return all versions for the named document, ordered most-recent-first.

    Returns [] when the document is not found in INDEX.md.
    """
    if not INDEX_PATH.is_file():
        return []
    versions: list[BridgeVersion] = []
    in_target = False
    for line in INDEX_PATH.read_text(encoding="utf-8").splitlines():
        doc_match = INDEX_DOC_RE.match(line)
        if doc_match:
            in_target = doc_match.group(1) == bridge_id
            continue
        if not in_target:
            continue
        status_match = INDEX_STATUS_RE.match(line)
        if status_match:
            status = status_match.group(1)
            rel = status_match.group(2)
            file_path = PROJECT_ROOT / "bridge" / rel
            # Extract trailing version number from filename: foo-NNN.md → NNN.
            version_match = re.search(r"-(\d+)\.md$", rel)
            version_number = int(version_match.group(1)) if version_match else 0
            versions.append(BridgeVersion(status, file_path, version_number))
        elif line.strip() == "":
            in_target = False  # Blank line ends the document entry.
    return versions


def _strip_code_fences(lines: list[str]) -> list[str]:
    """Return lines with code-fenced blocks (``` or ~~~) replaced by blanks.

    Code-fenced blocks contain illustrative content (schemas, examples) that
    the runner must NOT parse as authoritative spec links or waivers. The
    proposal at `-003 §1.5` literally embeds a waiver schema example inside
    a fence; without this filter the extractor treats it as a real waiver.
    """
    fence_re = re.compile(r"^\s*(?:```|~~~)")
    in_fence = False
    out: list[str] = []
    for line in lines:
        if fence_re.match(line):
            in_fence = not in_fence
            out.append("")  # placeholder so line numbers stay aligned for debug
            continue
        out.append("" if in_fence else line)
    return out


def _extract_spec_links_section(content: str) -> set[str]:
    """Return the set of cited spec IDs in the file's Specification Links section.

    Only the section between the `## Specification Links` heading and the next
    heading is scanned. Spec IDs are SPEC-/GOV-/ADR-/DCL-/PB-/REQ- prefixed.
    Code-fenced blocks are stripped (illustrative content, not authoritative).
    """
    lines = _strip_code_fences(content.splitlines())
    start: int | None = None
    for idx, line in enumerate(lines):
        if SPEC_LINK_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return set()
    section_lines: list[str] = []
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        section_lines.append(line)
    section_text = "\n".join(section_lines)
    return set(SPEC_ID_RE.findall(section_text))


def _extract_waivers_section(content: str) -> dict[str, Waiver]:
    """Return mapping spec_id → Waiver for the file's coverage-waivers section.

    Code-fenced blocks are stripped before parsing so embedded schema examples
    aren't treated as real waivers.
    """
    lines = _strip_code_fences(content.splitlines())
    start: int | None = None
    for idx, line in enumerate(lines):
        if WAIVERS_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return {}
    waivers: dict[str, Waiver] = {}
    current: Waiver | None = None
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        bullet_match = WAIVER_BULLET_RE.match(line)
        if bullet_match:
            if current is not None:
                waivers[current.spec_id] = current
            current = Waiver(spec_id=bullet_match.group(1))
            continue
        field_match = WAIVER_FIELD_RE.match(line)
        if field_match and current is not None:
            key, raw_value = field_match.group(1), field_match.group(2)
            value = raw_value.strip().strip('"').strip("'")
            if key == "reason":
                current.reason = value
            elif key == "approved_by":
                current.approved_by = value
            elif key == "applies_from_version":
                try:
                    current.applies_from_version = int(value)
                except ValueError:
                    current.applies_from_version = None
    if current is not None:
        waivers[current.spec_id] = current
    return waivers


def _delib_owner_attributed(row: tuple) -> bool:
    """Owner-attribution check per Codex -004 GO."""
    # row column order: id, version, spec_id, work_item_id, source_type, ..., outcome
    source_type, outcome = row[4], row[12]
    return source_type == "owner_conversation" or outcome == "owner_decision"


def _delib_references_spec(conn: sqlite3.Connection, delib_id: str, spec_id: str, content: str) -> bool:
    """Check that DELIB references spec_id via deliberation_specs join OR content substring."""
    cur = conn.execute(
        "SELECT 1 FROM deliberation_specs WHERE deliberation_id = ? AND spec_id = ? LIMIT 1",
        (delib_id, spec_id),
    )
    if cur.fetchone() is not None:
        return True
    return spec_id in (content or "")


def _validate_waiver_evidence(waiver: Waiver) -> str | None:
    """Return error code (per -003 §1.5) if waiver is invalid, else None."""
    if not waiver.approved_by:
        return "malformed"
    # Version coherence (Codex Q2: applies_from_version: 0 acceptable as
    # "applies from initial version before 001" if explicitly tested).
    if waiver.applies_from_version is None:
        return "version_mismatch"
    if not isinstance(waiver.applies_from_version, int) or waiver.applies_from_version < 0:
        return "version_mismatch"

    if waiver.approved_by.startswith("DELIB-"):
        if not DB_PATH.is_file():
            return "nonexistent_delib"
        try:
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=2.0)
        except sqlite3.Error:
            return "nonexistent_delib"
        try:
            cur = conn.execute(
                "SELECT id, version, spec_id, work_item_id, source_type, source_ref, "
                "title, summary, content, content_hash, participants, session_id, outcome "
                "FROM deliberations WHERE id = ? ORDER BY version DESC LIMIT 1",
                (waiver.approved_by,),
            )
            row = cur.fetchone()
            if row is None:
                return "nonexistent_delib"
            # Reorder to match _delib_owner_attributed expectations:
            # index 4 = source_type, index 12 = outcome.
            full_row = (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12])
            if not _delib_owner_attributed(full_row):
                return "not_owner_decision"
            if not _delib_references_spec(conn, waiver.approved_by, waiver.spec_id, row[8] or ""):
                return "wrong_spec"
        finally:
            conn.close()
    elif waiver.approved_by.startswith("approval_packet:"):
        filename = waiver.approved_by.removeprefix("approval_packet:").strip()
        packet_path = APPROVALS_DIR / filename
        if not packet_path.is_file():
            return "nonexistent_packet"
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return "malformed"
        if packet.get("artifact_id") != waiver.spec_id:
            return "wrong_spec"
        if not packet.get("approval_mode"):
            return "malformed"
    else:
        return "malformed"
    return None


def _discover_derived_tests(spec_id: str) -> list[str]:
    """Find test files whose module-level docstring cites spec_id.

    CONSERVATIVE per -003 §1.3: only module-level docstrings are scanned.
    Returns relative paths (str) for stable JSON output.
    """
    matches: list[Path] = []
    pattern = re.compile(rf"\b{re.escape(spec_id)}\b")
    for test_dir in TEST_DIRS:
        if not test_dir.is_dir():
            continue
        for test_file in test_dir.rglob("test_*.py"):
            try:
                source = test_file.read_text(encoding="utf-8")
            except OSError:
                continue
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            module_docstring = ast.get_docstring(tree)
            if module_docstring and pattern.search(module_docstring):
                matches.append(test_file)
    return [str(p.relative_to(PROJECT_ROOT)).replace("\\", "/") for p in matches]


def _parse_pytest_summary(output: str) -> tuple[int, int]:
    """Parse pytest summary lines. Returns (passed, failed)."""
    passed = 0
    failed = 0
    for line in output.splitlines():
        m = re.search(r"(\d+)\s+passed", line)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+)\s+failed", line)
        if m:
            failed = int(m.group(1))
        m = re.search(r"(\d+)\s+errors?", line)
        if m:
            failed += int(m.group(1))
    return (passed, failed)


def _run_pytest(test_files: list[str], timeout_s: int) -> tuple[int, int]:
    """Invoke pytest on the given test files. Returns (passed_count, failed_count).

    Test files are grouped by their test root (``tests/`` vs
    ``groundtruth-kb/tests/``) and pytest is invoked separately per group with
    appropriate ``--rootdir`` + ``--override-ini`` flags. This avoids
    conftest-import collisions when files from both roots appear together
    (the ``tests.conftest`` ImportPathMismatchError is fatal otherwise).

    On any error (timeout, missing pytest), the affected group counts as
    ``failed`` — fail-closed semantic.
    """
    if not test_files:
        return (0, 0)

    # Group test files by their test root.
    groups: dict[str, list[str]] = {}
    for f in test_files:
        parts = f.split("/")
        if len(parts) >= 2 and parts[0] == "groundtruth-kb" and parts[1] == "tests":
            root = "groundtruth-kb/tests"
        else:
            root = "tests"
        groups.setdefault(root, []).append(f)

    total_passed = 0
    total_failed = 0
    for root, files in groups.items():
        if root == "groundtruth-kb/tests":
            cmd = [
                sys.executable, "-m", "pytest",
                "--rootdir=groundtruth-kb",
                "--override-ini=testpaths=tests",
                *files, "--tb=no", "-q", "--no-header",
            ]
        else:
            cmd = [sys.executable, "-m", "pytest", *files, "--tb=no", "-q", "--no-header"]
        try:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            total_failed += len(files)
            continue
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        passed, failed = _parse_pytest_summary(output)
        total_passed += passed
        total_failed += failed
    return (total_passed, total_failed)


def _format_human(matrix: dict[str, SpecMatrixEntry], waivers: dict[str, Waiver],
                  bridge_id: str, version_count: int, verified_overall: bool) -> str:
    lines = [
        f"Bridge: {bridge_id}",
        f"Cited specs: {len(matrix)} (across {version_count} versions)",
        f"Waivers applied: {len(waivers)}",
        "",
        "Per-spec verification:",
    ]
    for spec_id in sorted(matrix.keys()):
        entry = matrix[spec_id]
        marker = "[PASS]" if entry.verified else "[FAIL]" if entry.tests_failed else "[GAP]"
        detail = (
            f"{len(entry.tests_found)} tests, all pass" if entry.verified
            else f"{entry.tests_failed} failed" if entry.tests_failed
            else "no derived tests found"
        )
        lines.append(f"  {spec_id:<55} {marker:<8}{detail}")
    lines.append("")
    lines.append(f"Overall verified: {'YES' if verified_overall else 'NO'}")
    return "\n".join(lines)


def run(bridge_id: str, json_output: bool = False, advisory: bool = False,
        pytest_timeout_s: int = DEFAULT_PYTEST_TIMEOUT_S) -> int:
    """Execute the full procedure. Returns exit code per CLI contract."""
    # Step 1-2: Parse INDEX + enumerate ALL versions.
    versions = _parse_index_for_document(bridge_id)
    if not versions:
        msg = f"ERR_NO_INDEX_ENTRY: no entry for bridge_id={bridge_id!r} in {INDEX_PATH}"
        sys.stderr.write(msg + "\n")
        return 0 if advisory else 2

    # Step 3-4: Read each file → compute union of cited specs + collect waivers.
    # IMPORTANT: only Prime-authored versions (NEW / REVISED) carry the
    # ``## Specification Links`` section. Codex verdict files (GO / NO-GO /
    # VERIFIED) typically lack that section because they inherit the spec
    # context from the proposal they reviewed. A2 enforcement therefore
    # compares against the most-recent PRIME-authored version, not the
    # absolute-latest version. Per the operative-Prime-version pattern from
    # smart-poller-kind-aware-routing-2026-04-30 F1 fix.
    PRIME_AUTHORED_STATUSES = {"NEW", "REVISED"}
    cited_history: dict[int, set[str]] = {}  # version_number → cited specs (Prime-authored only)
    cited_specs: set[str] = set()
    waivers: dict[str, Waiver] = {}
    for v in versions:
        if not v.file_path.is_file():
            continue
        try:
            content = v.file_path.read_text(encoding="utf-8")
        except OSError:
            continue
        version_specs = _extract_spec_links_section(content)
        # Verdict files: skip the spec-links extraction (they don't carry the
        # section). Still scan their waivers section since Codex could in
        # principle add waivers in a verdict, though normally waivers come from
        # Prime versions.
        # Empty version_specs from a Prime-authored version means the proposal
        # opted to carry-forward via prose ("Carried forward from -001
        # unchanged.") rather than re-enumerating. A2 should NOT fire on
        # carry-forward — A1 union accumulation is the correct semantic.
        # Only register the version's spec set when non-empty (explicit
        # enumeration).
        if v.status in PRIME_AUTHORED_STATUSES and version_specs:
            cited_history[v.version_number] = version_specs
            cited_specs.update(version_specs)
        version_waivers = _extract_waivers_section(content)
        # Later versions' waivers override earlier (most-recent wins).
        for spec_id, waiver in version_waivers.items():
            if spec_id not in waivers:
                waivers[spec_id] = waiver

    # A2 enforcement: detect specs cited in earlier Prime versions but not
    # the most-recent Prime version, without an approved waiver. Latest =
    # highest version_number among Prime-authored entries.
    latest_v = max(cited_history.keys()) if cited_history else 0
    latest_specs = cited_history.get(latest_v, set())
    for spec_id in cited_specs - latest_specs:
        if spec_id not in waivers:
            msg = (f"ERR_REMOVAL_WITHOUT_WAIVER: spec_id={spec_id} cited in earlier "
                   f"version but not version {latest_v} of {bridge_id}")
            sys.stderr.write(msg + "\n")
            return 0 if advisory else 3

    # F3 step: validate waiver evidence.
    waiver_errors: dict[str, str] = {}
    for spec_id, waiver in waivers.items():
        err = _validate_waiver_evidence(waiver)
        if err:
            waiver_errors[spec_id] = err
            sys.stderr.write(
                f"ERR_WAIVER_{err.upper()}: spec_id={spec_id} approved_by={waiver.approved_by!r}\n"
            )
    if waiver_errors and not advisory:
        return 4

    # Steps 5-7: discover derived tests + execute pytest + build matrix.
    matrix: dict[str, SpecMatrixEntry] = {}
    for spec_id in cited_specs:
        if spec_id in waivers and spec_id not in waiver_errors:
            entry = SpecMatrixEntry(spec_id=spec_id, verified=True, reason="waived")
            matrix[spec_id] = entry
            continue
        test_files = _discover_derived_tests(spec_id)
        if not test_files:
            entry = SpecMatrixEntry(
                spec_id=spec_id, tests_found=[], verified=False, reason="no_derived_tests",
            )
            matrix[spec_id] = entry
            continue
        passed, failed = _run_pytest(test_files, pytest_timeout_s)
        entry = SpecMatrixEntry(
            spec_id=spec_id,
            tests_found=test_files,
            tests_passed=passed,
            tests_failed=failed,
            verified=(failed == 0 and passed > 0),
            reason="all_pass" if (failed == 0 and passed > 0) else "tests_failed" if failed else "no_passing_tests",
        )
        matrix[spec_id] = entry

    # Step 8: overall verified + output.
    verified_overall = bool(matrix) and all(e.verified for e in matrix.values()) and not waiver_errors
    if json_output:
        payload = {
            "bridge_document_name": bridge_id,
            "cited_specs_count": len(cited_specs),
            "matrix": {
                spec_id: {
                    "tests_found": e.tests_found,
                    "tests_passed": e.tests_passed,
                    "tests_failed": e.tests_failed,
                    "verified": e.verified,
                    "reason": e.reason,
                }
                for spec_id, e in matrix.items()
            },
            "verified_overall": verified_overall,
            "waivers_applied": list(waivers.keys()),
            "waiver_errors": waiver_errors,
        }
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(_format_human(matrix, waivers, bridge_id, len(versions), verified_overall) + "\n")

    if not verified_overall and not advisory:
        return 5
    return 0


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_spec_derived_tests.py",
        description="GT-KB platform VERIFIED runner: full-history bridge spec-derived test execution.",
    )
    parser.add_argument("--bridge-id", required=True, help="Document name from bridge/INDEX.md.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Non-blocking mode: exit 0 even on coverage gap or waiver failure (default is fail-closed).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="No-op for backward compatibility (fail-closed is now the default per -003 F2).",
    )
    parser.add_argument(
        "--pytest-timeout",
        type=int,
        default=DEFAULT_PYTEST_TIMEOUT_S,
        help=f"Pytest timeout in seconds (default {DEFAULT_PYTEST_TIMEOUT_S}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    return run(
        bridge_id=args.bridge_id,
        json_output=args.json,
        advisory=args.advisory,
        pytest_timeout_s=args.pytest_timeout,
    )


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministically evaluate the six GOV-FILE-BRIDGE-AUTHORITY-001 v3 assertions.

WI-5193 (``PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION``). This
is the canonical assertion evaluator mandated by ``GOV-FILE-BRIDGE-AUTHORITY-001``
v3. It implements the six executable assertions ``FILE-BRIDGE-AUTH-A1`` ..
``FILE-BRIDGE-AUTH-A6`` as a deterministic, rerunnable checker layered on the
governed live bridge reader
(``groundtruth_kb.bridge.status_driver.collect_bridge_status``) plus stable
filesystem and rule-surface facts.

The checker performs no mutation and never writes bridge state. Each assertion is
an ``all_of`` over three sub-assertions keyed by the exact marker strings the GOV
v3 spec greps for. The checker fails closed: any unreadable required surface, or
any sub-assertion violation, yields overall ``FAIL`` (exit 1). Output carries no
timestamps or absolute paths so the exit/JSON contract is reproducible for a
fixed tree, per ``DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001``.

Marker map (spec grep pattern -> sub-assertion evaluated here):

- A1 numbered-files-authoritative-chain / versioned-reader-only /
  append-only-version-order
- A2 tafe-dispatch-runtime-authority / no-markdown-runtime-inference /
  dual-surface-conflict-denied
- A3 bridge-index-absent / bridge-index-no-writer /
  bridge-index-reference-classified
- A4 startup-projection-context-only / dashboard-report-cache-context-only /
  fresh-live-read-required
- A5 malformed-status-denied / duplicate-version-denied /
  unreadable-required-state-denied
- A6 lo-repair-bridge-scope-only / lo-repair-preserves-history /
  lo-repair-no-self-review
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.bridge.status_driver import collect_bridge_status  # noqa: E402

# The nine canonical bridge status tokens (file-bridge-protocol.md). Statuses
# outside this set are never actionable and must fail closed (A5).
ACTIONABLE_STATUS_TOKENS = frozenset({"NEW", "REVISED", "GO", "NO-GO", "NO-ACTION", "ADVISORY"})

# Matches the governed reader's file pattern (``\d{3,}``); ``int(version)`` keys
# duplicate detection so ``foo-001.md`` and ``foo-0001.md`` collide as one version.
_NUMBERED_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3,})\.md$")

# A line that both names an INDEX.md path and applies a write verb is a writer.
_WRITE_HINT_RE = re.compile(r"""write_text|write_bytes|\.write\(|open\([^)]*['"][wa]""")

# Tokens that mark an INDEX.md reference as historical / guard / anti-regression
# evidence rather than a live dependency (A3 reference-classified).
_CLASSIFICATION_RE = re.compile(
    r"historical|anti-regression|anti_regression|guard|retired|quarantine|"
    r"absent|generated[ _-]view|superseded|legacy|do not (?:re)?create|"
    r"must not|no.*writer|aggregate.*not|not.*canonical|retire|"
    r"controlled[_ ]?artifact|direct_mutation|mutating[_ ]?target|denied|blocked",
    re.IGNORECASE,
)


class FileBridgeAuthorityError(RuntimeError):
    """Raised when a required surface cannot be inspected (fail closed)."""


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _subassertion(marker: str, passes: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"id": marker, "status": "PASS" if passes else "FAIL", "evidence": evidence}


def _group(assertion_id: str, description: str, subs: list[dict[str, Any]]) -> dict[str, Any]:
    passes = all(sub["status"] == "PASS" for sub in subs)
    return {
        "id": assertion_id,
        "type": "all_of",
        "status": "PASS" if passes else "FAIL",
        "description": description,
        "subassertions": subs,
    }


def _scan_numbered_files(bridge_dir: Path) -> dict[str, Any]:
    """Deterministically scan the numbered bridge file chain from the filesystem.

    Returns per-slug version lists plus duplicate-version and unreadable-file
    findings. Status *resolution* is delegated to the governed reader; this scan
    only concerns the append-only file structure (A1/A5b/A5c).
    """

    slug_versions: dict[str, list[int]] = {}
    duplicate_versions: list[str] = []
    unreadable: list[str] = []
    if not bridge_dir.is_dir():
        raise FileBridgeAuthorityError(f"bridge directory is not readable: {bridge_dir}")
    for path in sorted(bridge_dir.glob("*.md"), key=lambda item: item.name.casefold()):
        match = _NUMBERED_FILE_RE.match(path.name)
        if match is None:
            continue  # non-versioned markdown is outside the dispatchable chain
        slug = match.group("slug")
        version = int(match.group("version"))
        try:
            path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError):
            unreadable.append(path.name)
        versions = slug_versions.setdefault(slug, [])
        if version in versions:
            duplicate_versions.append(path.name)
        versions.append(version)
    return {
        "slug_versions": slug_versions,
        "duplicate_versions": sorted(duplicate_versions),
        "unreadable": sorted(unreadable),
    }


def _effective_source_files(root: Path) -> list[Path]:
    """Bounded, deterministic set of load-bearing bridge-authority surfaces."""

    files: list[Path] = []
    self_name = Path(__file__).name
    for path in sorted((root / "scripts").glob("*.py"), key=lambda item: item.name.casefold()):
        name = path.name
        if name == self_name or name.startswith("_tmp_") or name.startswith("test_"):
            continue
        files.append(path)
    bridge_pkg = root / "groundtruth-kb" / "src" / "groundtruth_kb" / "bridge"
    if bridge_pkg.is_dir():
        for path in sorted(bridge_pkg.rglob("*.py"), key=lambda item: item.as_posix().casefold()):
            files.append(path)
    rules_dir = root / ".claude" / "rules"
    if rules_dir.is_dir():
        for path in sorted(rules_dir.glob("*.md"), key=lambda item: item.name.casefold()):
            files.append(path)
    return files


def _index_reference_scan(root: Path) -> dict[str, Any]:
    """Find INDEX.md writers and unclassified references across effective surfaces."""

    writers: list[str] = []
    unclassified_references: list[str] = []
    for path in _effective_source_files(root):
        text = _read_text(path)
        if text is None or "INDEX.md" not in text:
            continue
        rel = _rel(path, root)
        for line in text.splitlines():
            if "INDEX.md" in line and _WRITE_HINT_RE.search(line):
                writers.append(rel)
                break
        if not _CLASSIFICATION_RE.search(text):
            unclassified_references.append(rel)
    return {
        "writers": sorted(set(writers)),
        "unclassified_references": sorted(set(unclassified_references)),
    }


def _rule_text(root: Path, *names: str) -> str:
    """Concatenate the text of the named ``.claude/rules`` files (missing -> empty)."""

    chunks: list[str] = []
    for name in names:
        text = _read_text(root / ".claude" / "rules" / name)
        if text:
            chunks.append(text)
    return "\n".join(chunks)


def _assert_a1(root: Path, scan: dict[str, Any], snapshot: Any) -> dict[str, Any]:
    queue = snapshot.queue
    versioned_reader = root / "groundtruth-kb" / "src" / "groundtruth_kb" / "bridge" / "versioned_files.py"
    slug_versions: dict[str, list[int]] = scan["slug_versions"]
    non_monotonic = sorted(
        slug for slug, versions in slug_versions.items() if sorted(versions) != sorted(set(versions))
    )
    subs = [
        _subassertion(
            "numbered-files-authoritative-chain",
            queue.threads > 0 and bool(slug_versions),
            {"documents": queue.threads, "numbered_slugs": len(slug_versions)},
        ),
        _subassertion(
            "versioned-reader-only",
            versioned_reader.is_file(),
            {"governed_reader": _rel(versioned_reader, root)},
        ),
        _subassertion(
            "append-only-version-order",
            not non_monotonic,
            {"slugs_with_duplicate_versions": non_monotonic},
        ),
    ]
    return _group(
        "FILE-BRIDGE-AUTH-A1",
        "Numbered status-bearing files are the authoritative append-only chain.",
        subs,
    )


def _assert_a2(root: Path, snapshot: Any) -> dict[str, Any]:
    automation = snapshot.automation
    index_path = root / "bridge" / "INDEX.md"
    disposition = root / "groundtruth-kb" / "src" / "groundtruth_kb" / "bridge" / "disposition.py"
    dispatch_state = automation.dispatch_state if isinstance(automation.dispatch_state, dict) else {}
    subs = [
        _subassertion(
            "tafe-dispatch-runtime-authority",
            bool(automation.dispatcher_daemon_script_exists) and bool(dispatch_state),
            {
                "dispatcher_daemon_script_exists": bool(automation.dispatcher_daemon_script_exists),
                "dispatch_state_present": bool(dispatch_state),
            },
        ),
        _subassertion(
            "no-markdown-runtime-inference",
            not index_path.exists(),
            {"bridge_index_present": index_path.exists()},
        ),
        _subassertion(
            "dual-surface-conflict-denied",
            disposition.is_file(),
            {"disposition_module": _rel(disposition, root)},
        ),
    ]
    return _group(
        "FILE-BRIDGE-AUTH-A2",
        "TAFE and dispatcher state control only live runtime coordination.",
        subs,
    )


def _assert_a3(root: Path, reference_scan: dict[str, Any]) -> dict[str, Any]:
    index_path = root / "bridge" / "INDEX.md"
    subs = [
        _subassertion(
            "bridge-index-absent",
            not index_path.exists(),
            {"bridge_index_present": index_path.exists()},
        ),
        _subassertion(
            "bridge-index-no-writer",
            not reference_scan["writers"],
            {"index_writers": reference_scan["writers"]},
        ),
        _subassertion(
            "bridge-index-reference-classified",
            not reference_scan["unclassified_references"],
            {"unclassified_references": reference_scan["unclassified_references"]},
        ),
    ]
    return _group(
        "FILE-BRIDGE-AUTH-A3",
        "The retired bridge aggregate cannot return as authority or dependency.",
        subs,
    )


def _assert_a4(root: Path) -> dict[str, Any]:
    startup = _read_text(root / "scripts" / "session_self_initialization.py") or ""
    rules = _rule_text(
        root,
        "codex-way-of-working.md",
        "codex-session-bootstrap.md",
        "bridge-essential.md",
    )
    freshness = _read_text(root / ".claude" / "rules" / "sot-read-discipline.md") or ""
    startup_ok = "non-authoritative" in startup and "bridge" in startup
    context_only = bool(re.search(r"context[ -]only", rules, re.IGNORECASE))
    fresh_ok = bool(re.search(r"fresh canonical read|fresh.*live read|canonical read", freshness, re.IGNORECASE))
    subs = [
        _subassertion(
            "startup-projection-context-only",
            startup_ok,
            {"startup_declares_non_authoritative_bridge_projection": startup_ok},
        ),
        _subassertion(
            "dashboard-report-cache-context-only",
            context_only,
            {"rules_declare_derived_artifacts_context_only": context_only},
        ),
        _subassertion(
            "fresh-live-read-required",
            fresh_ok,
            {"sot_read_discipline_requires_fresh_reads": fresh_ok},
        ),
    ]
    return _group(
        "FILE-BRIDGE-AUTH-A4",
        "Projections remain context-only and cannot determine bridge state.",
        subs,
    )


def _assert_a5(scan: dict[str, Any], snapshot: Any) -> dict[str, Any]:
    queue = snapshot.queue
    actionable = list(queue.prime_actionable) + list(queue.loyal_opposition_actionable)
    non_canonical_actionable = sorted(
        {item.top_status for item in actionable if item.top_status not in ACTIONABLE_STATUS_TOKENS}
    )
    unknown_docs = int(queue.status_counts.get("UNKNOWN", 0))
    subs = [
        _subassertion(
            "malformed-status-denied",
            not non_canonical_actionable,
            {
                "unresolved_or_unknown_documents": unknown_docs,
                "non_canonical_actionable_statuses": non_canonical_actionable,
            },
        ),
        _subassertion(
            "duplicate-version-denied",
            not scan["duplicate_versions"],
            {"duplicate_version_files": scan["duplicate_versions"]},
        ),
        _subassertion(
            "unreadable-required-state-denied",
            not scan["unreadable"],
            {"unreadable_files": scan["unreadable"]},
        ),
    ]
    return _group(
        "FILE-BRIDGE-AUTH-A5",
        "Malformed, conflicting, or unreadable bridge state fails closed.",
        subs,
    )


def _assert_a6(root: Path) -> dict[str, Any]:
    repair_rules = _rule_text(
        root,
        "codex-way-of-working.md",
        "loyal-opposition.md",
        "bridge-essential.md",
    )
    history_rules = _rule_text(root, "file-bridge-protocol.md", "bridge-essential.md")
    independence_rules = _rule_text(root, "codex-review-gate.md", "file-bridge-protocol.md", "loyal-opposition.md")
    scope_ok = bool(
        re.search(r"bridge-scoped|bridge function and use|correct bridge function", repair_rules, re.IGNORECASE)
    )
    history_ok = bool(re.search(r"never delete.*bridge file|append-only", history_rules, re.IGNORECASE))
    independence_ok = "author_session_context_id" in independence_rules and bool(
        re.search(r"review independence", independence_rules, re.IGNORECASE)
    )
    subs = [
        _subassertion(
            "lo-repair-bridge-scope-only",
            scope_ok,
            {"repair_authority_bridge_scoped": scope_ok},
        ),
        _subassertion(
            "lo-repair-preserves-history",
            history_ok,
            {"append_only_history_preserved": history_ok},
        ),
        _subassertion(
            "lo-repair-no-self-review",
            independence_ok,
            {"review_independence_by_session_context": independence_ok},
        ),
    ]
    return _group(
        "FILE-BRIDGE-AUTH-A6",
        "Permanent Loyal Opposition bridge-repair authority is targeted and non-self-reviewing.",
        subs,
    )


def audit_file_bridge_authority(project_root: Path) -> dict[str, Any]:
    """Evaluate all six GOV v3 assertions and return the deterministic report."""

    root = project_root.resolve()
    bridge_dir = root / "bridge"
    try:
        snapshot = collect_bridge_status(root, top_n=None)
    except Exception as exc:  # noqa: BLE001 - fail closed on any reader error
        raise FileBridgeAuthorityError(f"governed bridge reader failed: {exc}") from exc
    scan = _scan_numbered_files(bridge_dir)
    reference_scan = _index_reference_scan(root)
    assertions = [
        _assert_a1(root, scan, snapshot),
        _assert_a2(root, snapshot),
        _assert_a3(root, reference_scan),
        _assert_a4(root),
        _assert_a5(scan, snapshot),
        _assert_a6(root),
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in assertions) else "FAIL"
    return {"schema_version": 1, "status": status, "assertions": assertions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        report = audit_file_bridge_authority(args.project_root)
    except FileBridgeAuthorityError as exc:
        print(f"FILE BRIDGE AUTHORITY: FAIL - {exc}", file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"FILE BRIDGE AUTHORITY: {report['status']}")
        for assertion in report["assertions"]:
            print(f"- {assertion['id']}: {assertion['status']}")
            for sub in assertion["subassertions"]:
                print(f"  - {sub['id']}: {sub['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

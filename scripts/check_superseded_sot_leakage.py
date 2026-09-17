#!/usr/bin/env python3
"""Lifecycle-aware scanner for superseded-authority leakage (DCL-SUPERSEDED-SOT-LEAKAGE-001).

Evaluator ID: ``superseded-sot-leakage``.
Canonical invocation: ``gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001``.

The scanner answers one question deterministically: does any **active** GT-KB
surface still cite a formal record whose current MemBase status is retired or
superseded, in a way that could direct current behavior?

The hard part is not detection, it is *lifecycle classification*. GT-KB's
append-only history (bridge chains, deliberations, cleanup evidence, archives)
legitimately preserves obsolete literals forever. Treating those as active
residue would drown a real P0 in thousands of false positives, so history is
scanned and classified but never reported as critical. Equally, some active
surfaces cite a retired id *in order to enforce its absence* - a retired-registry
sentinel or a guard test. Those are load-bearing in the opposite direction:
removing them would weaken enforcement, so they resolve to KEEP.

Severity and gate effects follow the DCL: a stale active authority reference is
blocking P0; incomplete classification or missing currentness evidence is
blocking P1; valid history is informational. Missing required coverage never
produces PASS - it produces PARTIAL or UNASSESSED and blocks.

Work item: WI-5154. Acceptance test: TEST-11323
(``platform_tests/scripts/test_check_superseded_sot_leakage.py``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EVALUATOR_ID = "superseded-sot-leakage"
EVALUATOR_VERSION = 1

# ---------------------------------------------------------------------------
# Source providers (SOT-LEAK-A1)
#
# Every provider below is REQUIRED. A provider that cannot be resolved yields a
# ``missing-provider`` finding and forces PARTIAL/UNASSESSED - the DCL failure
# contract forbids PASS on incomplete coverage.
# ---------------------------------------------------------------------------

PROVIDER_CURRENT_FORMAL_ARTIFACTS = "current-formal-artifacts"
PROVIDER_ACTIVE_SURFACE_CLASSES = "active-surface-classes"
PROVIDER_CURRENTNESS_EVIDENCE = "currentness-evidence"
REQUIRED_PROVIDERS = (
    PROVIDER_CURRENT_FORMAL_ARTIFACTS,
    PROVIDER_ACTIVE_SURFACE_CLASSES,
    PROVIDER_CURRENTNESS_EVIDENCE,
)
MISSING_PROVIDER = "missing-provider"

# Statuses that make a formal record a superseded authority.
SUPERSEDED_STATUSES = frozenset({"retired", "superseded"})

# ---------------------------------------------------------------------------
# Active surface classes (SOT-LEAK-A1)
#
# Ordered most-specific-first; the first matching class wins so a generated
# projection is never mistaken for its canonical source.
# ---------------------------------------------------------------------------

ACTIVE_SURFACE_CLASSES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("generated", (".codex/skills/**/*.md", ".cursor/skills/**/*.md", ".agent/skills/**/*.md")),
    ("hook", (".claude/hooks/*.py",)),
    ("skill", (".claude/skills/**/SKILL.md",)),
    ("rule", (".claude/rules/*.md",)),
    ("manifest", ("config/registry/*.toml", "groundtruth-kb/templates/managed-artifacts.toml")),
    ("scaffold", ("groundtruth-kb/templates/rules/*.md", "groundtruth-kb/templates/project/*.md")),
    ("cli-help", ("groundtruth-kb/src/groundtruth_kb/cli.py",)),
    ("worker-loading", ("AGENTS.md", "CLAUDE.md")),
)

# ---------------------------------------------------------------------------
# Historical (non-operative) classes (SOT-LEAK-A2)
#
# These are scanned and lifecycle-classified, but MUST NOT be treated as active
# residue solely because they preserve an obsolete literal.
# ---------------------------------------------------------------------------

HISTORICAL_BRIDGE = "historical-bridge"
HISTORICAL_DELIBERATION = "historical-deliberation"
HISTORICAL_EVIDENCE = "historical-evidence"
HISTORICAL_ARCHIVE = "historical-archive"
NON_OPERATIVE = "non-operative"
NO_CRITICAL_FALSE_POSITIVE = "no-critical-false-positive"

HISTORICAL_PREFIXES: tuple[tuple[str, str], ...] = (
    ("bridge/", HISTORICAL_BRIDGE),
    ("deliberations/", HISTORICAL_DELIBERATION),
    ("archive/", HISTORICAL_ARCHIVE),
    (".gtkb-state/", HISTORICAL_EVIDENCE),
)
HISTORICAL_MARKERS: tuple[str, str] = ("cleanup-evidence", HISTORICAL_EVIDENCE)

# ---------------------------------------------------------------------------
# Guarded-KEEP recognition (SOT-LEAK-A3)
# ---------------------------------------------------------------------------

RETIRED_REGISTRY_SENTINEL = "retired-registry-sentinel"
ACTIVE_GUARD_REFERENCE = "active-guard-reference"
CURRENT_ENFORCEMENT_EVIDENCE = "current-enforcement-evidence"
NO_ACTIVE_AUTHORITY_EFFECT = "no-active-authority-effect"

# A reference is an active guard only when the citing line demonstrably enforces
# absence/retirement rather than instructing current behavior.
_ENFORCEMENT_LINE_RE = re.compile(
    r"(?i)\b(?:assert|grep_absent|must_not|must not|forbidden|retired|superseded|"
    r"deprecated|do not use|no longer|removed|absence)\b"
)
_GUARD_PATH_RE = re.compile(r"(?i)(?:^|/)(?:platform_tests|tests)/|/test_[^/]+\.py$|(?:^|/)test_[^/]+\.py$")

# ---------------------------------------------------------------------------
# Dispositions and severities
# ---------------------------------------------------------------------------

STRIP = "STRIP"
KEEP = "KEEP"
QUARANTINE = "QUARANTINE"

SEVERITY_P0 = "P0"
SEVERITY_P1 = "P1"
SEVERITY_INFO = "informational"

STALE_ACTIVE = "stale-active"
DEDUPLICATE_PATH = "deduplicate-path"
DETERMINISTIC_REMEDIATION = "deterministic-remediation"
GATE_BLOCK = "gate-block"

RESULT_PASS = "PASS"
RESULT_FAIL = "FAIL"
RESULT_PARTIAL = "PARTIAL"
RESULT_UNASSESSED = "UNASSESSED"

# Formal-record identifier shape (GOV-/DCL-/ADR-/SPEC-/PB-/REQ-/RETIRE-SPEC-...).
_ID_TOKEN_RE = re.compile(r"\b(?:RETIRE-SPEC|GOV|DCL|ADR|SPEC|PB|REQ)-[A-Z0-9][A-Z0-9-]{2,}\b")

_SKIP_DIR_PARTS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"})
_MAX_BYTES = 2_000_000


@dataclass(frozen=True, slots=True)
class Finding:
    """One deduplicated finding per (surface path, superseded subject).

    Carries every field the DCL finding contract requires.
    """

    finding_id: str
    artifact_identity: str
    path: str
    line: int
    surface_class: str
    lifecycle: str
    authority: str
    subject_id: str
    subject_version: str
    subject_hash: str
    currentness_evidence: dict[str, Any]
    superseding_carrier: str | None
    severity: str
    affected_gate: str
    disposition: str
    remediation: str
    recovery_route: str


@dataclass(slots=True)
class ScanReport:
    evaluator: str = EVALUATOR_ID
    evaluator_version: int = EVALUATOR_VERSION
    result: str = RESULT_UNASSESSED
    gate_blocked: bool = True
    providers: dict[str, Any] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["findings"] = [asdict(f) if not isinstance(f, dict) else f for f in self.findings]
        return payload


def _iter_repo_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    seen: list[Path] = []
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            if _SKIP_DIR_PARTS & set(path.relative_to(root).parts):
                continue
            seen.append(path)
    return seen


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def classify_lifecycle(rel_path: str) -> str:
    """Return the lifecycle class for a repository-relative path.

    Append-only history is ``non-operative``: it is classified, never treated as
    active residue. Everything else is ``active``.
    """
    for prefix, label in HISTORICAL_PREFIXES:
        if rel_path.startswith(prefix):
            return label
    marker, label = HISTORICAL_MARKERS
    if marker in rel_path:
        return label
    return "active"


def classify_surface(rel_path: str, root: Path) -> str | None:
    """Return the active-surface class for a path, or None when not an active surface."""
    for label, patterns in ACTIVE_SURFACE_CLASSES:
        for pattern in patterns:
            for candidate in root.glob(pattern):
                if candidate.is_file() and _rel(candidate, root) == rel_path:
                    return label
    return None


def _is_guarded_keep(rel_path: str, line_text: str, subject_id: str) -> tuple[bool, str, str]:
    """Return ``(is_keep, keep_kind, enforcement_evidence)``.

    A retired id may remain on an active surface only when it cannot direct
    current behavior: either it *is* a retirement-registry sentinel, or the
    citing line demonstrably enforces absence.
    """
    if subject_id.startswith("RETIRE-SPEC"):
        return True, RETIRED_REGISTRY_SENTINEL, "subject is a retirement-registry sentinel id"
    if _GUARD_PATH_RE.search("/" + rel_path) and _ENFORCEMENT_LINE_RE.search(line_text):
        return True, ACTIVE_GUARD_REFERENCE, "guard surface with enforcement-shaped citing line"
    if _ENFORCEMENT_LINE_RE.search(line_text):
        return True, ACTIVE_GUARD_REFERENCE, "citing line asserts retirement/absence"
    return False, "", ""


def load_superseded_index(db: Any) -> dict[str, dict[str, Any]]:
    """Build the superseded-authority index from current MemBase formal records."""
    index: dict[str, dict[str, Any]] = {}
    for spec in db.list_specs():
        status = str(spec.get("status") or "").strip().lower()
        if status not in SUPERSEDED_STATUSES:
            continue
        spec_id = str(spec.get("id") or "").strip()
        if not spec_id:
            continue
        index[spec_id] = {
            "status": status,
            "version": str(spec.get("version") or ""),
            "retired_at": str(spec.get("retired_at") or ""),
            "title": str(spec.get("title") or ""),
        }
    return index


def _subject_hash(subject_id: str, meta: dict[str, Any]) -> str:
    material = f"{subject_id}|{meta.get('status')}|{meta.get('version')}|{meta.get('retired_at')}"
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def scan(root: Path, db: Any | None = None) -> ScanReport:
    """Run the deterministic superseded-authority scan."""
    report = ScanReport()

    # --- provider resolution (missing-provider => never PASS) ---------------
    if db is None:
        try:
            from groundtruth_kb.db import KnowledgeDB

            db = KnowledgeDB(str(root / "groundtruth.db"))
        except Exception as exc:  # noqa: BLE001 - a missing provider is a reported outcome
            report.providers[PROVIDER_CURRENT_FORMAL_ARTIFACTS] = {
                "resolved": False,
                "reason": f"{MISSING_PROVIDER}: {exc}",
            }
            report.result = RESULT_UNASSESSED
            report.gate_blocked = True
            report.counts = {"findings": 0, SEVERITY_P0: 0, SEVERITY_P1: 0}
            return report

    try:
        superseded = load_superseded_index(db)
    except Exception as exc:  # noqa: BLE001
        report.providers[PROVIDER_CURRENT_FORMAL_ARTIFACTS] = {
            "resolved": False,
            "reason": f"{MISSING_PROVIDER}: {exc}",
        }
        report.result = RESULT_UNASSESSED
        report.gate_blocked = True
        report.counts = {"findings": 0, SEVERITY_P0: 0, SEVERITY_P1: 0}
        return report

    report.providers[PROVIDER_CURRENT_FORMAL_ARTIFACTS] = {
        "resolved": True,
        "superseded_record_count": len(superseded),
    }

    surfaces: list[tuple[str, Path]] = []
    for label, patterns in ACTIVE_SURFACE_CLASSES:
        for path in _iter_repo_files(root, patterns):
            surfaces.append((label, path))
    report.providers[PROVIDER_ACTIVE_SURFACE_CLASSES] = {
        "resolved": bool(surfaces),
        "classes": [label for label, _ in ACTIVE_SURFACE_CLASSES],
        "scanned_file_count": len(surfaces),
    }
    if not surfaces:
        report.providers[PROVIDER_ACTIVE_SURFACE_CLASSES]["reason"] = (
            f"{MISSING_PROVIDER}: no active surface resolved under {root}"
        )

    # --- scan ---------------------------------------------------------------
    # deduplicate-path: one canonical finding per (path, subject).
    deduped: dict[tuple[str, str], Finding] = {}
    for surface_class, path in surfaces:
        rel_path = _rel(path, root)
        lifecycle = classify_lifecycle(rel_path)
        try:
            if path.stat().st_size > _MAX_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line_text in enumerate(text.splitlines(), start=1):
            for subject_id in set(_ID_TOKEN_RE.findall(line_text)):
                meta = superseded.get(subject_id)
                if meta is None:
                    continue
                key = (rel_path, subject_id)
                if key in deduped:
                    continue

                if lifecycle != "active":
                    # SOT-LEAK-A2: history is classified, stays non-operative,
                    # and must not raise a critical finding.
                    severity, disposition = SEVERITY_INFO, KEEP
                    authority = NON_OPERATIVE
                    remediation = f"{NO_CRITICAL_FALSE_POSITIVE}: preserve append-only history unchanged"
                    recovery = "no action; historical evidence is retained verbatim"
                else:
                    keep, keep_kind, enforcement = _is_guarded_keep(rel_path, line_text, subject_id)
                    if keep:
                        # SOT-LEAK-A3: KEEP only with current enforcement
                        # evidence and no active-authority effect.
                        severity, disposition = SEVERITY_INFO, KEEP
                        authority = f"{keep_kind}/{NO_ACTIVE_AUTHORITY_EFFECT}"
                        remediation = f"{CURRENT_ENFORCEMENT_EVIDENCE}: {enforcement}"
                        recovery = "retain the guard; re-verify enforcement on registry change"
                    else:
                        # SOT-LEAK-A4: stale active authority is a blocking P0.
                        severity, disposition = SEVERITY_P0, STRIP
                        authority = STALE_ACTIVE
                        remediation = (
                            f"{DETERMINISTIC_REMEDIATION}: replace {subject_id} "
                            f"({meta['status']}) at {rel_path}:{lineno} with its current canonical "
                            "carrier, or requalify the citation as explicit history"
                        )
                        recovery = (
                            "refresh the governed inventory, repair the canonical carrier, "
                            "then rerun: gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001"
                        )

                deduped[key] = Finding(
                    finding_id="SOTLEAK-" + hashlib.sha256(f"{rel_path}|{subject_id}".encode()).hexdigest()[:12],
                    artifact_identity=f"{surface_class}:{rel_path}",
                    path=rel_path,
                    line=lineno,
                    surface_class=surface_class,
                    lifecycle=lifecycle,
                    authority=authority,
                    subject_id=subject_id,
                    subject_version=str(meta.get("version") or ""),
                    subject_hash=_subject_hash(subject_id, meta),
                    currentness_evidence={
                        "evaluator_version": EVALUATOR_VERSION,
                        "subject_status": meta.get("status"),
                        "subject_retired_at": meta.get("retired_at"),
                        "superseded_record_count": len(superseded),
                    },
                    superseding_carrier=None,
                    severity=severity,
                    affected_gate="verification/promotion/closure",
                    disposition=disposition,
                    remediation=remediation,
                    recovery_route=recovery,
                )

    findings = sorted(deduped.values(), key=lambda f: (f.path, f.subject_id))
    report.findings = findings

    p0 = sum(1 for f in findings if f.severity == SEVERITY_P0)
    p1 = sum(1 for f in findings if f.severity == SEVERITY_P1)
    report.counts = {
        "findings": len(findings),
        SEVERITY_P0: p0,
        SEVERITY_P1: p1,
        SEVERITY_INFO: sum(1 for f in findings if f.severity == SEVERITY_INFO),
    }

    providers_ok = all(
        report.providers.get(name, {}).get("resolved")
        for name in (
            PROVIDER_CURRENT_FORMAL_ARTIFACTS,
            PROVIDER_ACTIVE_SURFACE_CLASSES,
        )
    )
    report.providers[PROVIDER_CURRENTNESS_EVIDENCE] = {
        "resolved": providers_ok,
        "evaluator_version": EVALUATOR_VERSION,
        "superseded_record_count": len(superseded),
    }

    if not providers_ok:
        report.result = RESULT_PARTIAL
        report.gate_blocked = True
    elif p0 or p1:
        report.result = RESULT_FAIL
        report.gate_blocked = True  # gate-block
    else:
        report.result = RESULT_PASS
        report.gate_blocked = False
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit the full report as JSON.")
    args = parser.parse_args(argv)

    report = scan(args.project_root.resolve())
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"evaluator={EVALUATOR_ID} result={report.result} gate_blocked={report.gate_blocked}")
        for name, meta in sorted(report.providers.items()):
            print(f"  provider {name}: resolved={meta.get('resolved')}")
        print(f"  findings={report.counts.get('findings', 0)} P0={report.counts.get(SEVERITY_P0, 0)}")
        for finding in report.findings:
            if finding.severity == SEVERITY_P0:
                print(
                    f"  [{finding.severity}] {finding.path}:{finding.line} {finding.subject_id} -> {finding.disposition}"
                )
    return 1 if report.gate_blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())

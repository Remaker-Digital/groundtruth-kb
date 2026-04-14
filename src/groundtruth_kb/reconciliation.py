# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
GroundTruth KB — F8 Provenance Reconciliation.

Five detectors that inspect the knowledge database for provenance drift:

  - ``find_orphaned_assertions`` — assertion targets whose files no longer exist
  - ``find_stale_specs`` — specs unchanged across an N-snapshot window while
    their section continued to evolve (with a changed_at fallback path)
  - ``find_authority_conflicts`` — stated vs inferred specs with structural
    assertion-target overlap inside the same (section, scope)
  - ``find_duplicate_specs`` — specs with near-identical titles (token overlap)
  - ``find_expired_provisionals`` — provisional specs whose replacement
    (looked up via ``provisional_until``) has reached lifecycle
    ``status in {'implemented', 'verified'}``

All detectors return a :class:`ReconciliationReport` holding a category label
and a list of finding dicts.  Reports are deterministic: callers can pass them
directly to a CLI aggregator and expect the same output for the same KB.

Approved scope: bridge/gtkb-spec-pipeline-f8-003.md,
bridge/gtkb-phase4-implementation-007.md,
bridge/gtkb-phase4-implementation-009.md,
bridge/gtkb-phase4-implementation-010.md.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from groundtruth_kb.assertions import (
    AssertionTarget,
    _extract_assertion_targets,
    _safe_glob,
    _safe_resolve,
)

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB


# ---------------------------------------------------------------------------
# Report container
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReconciliationReport:
    """Container for the output of a single reconciliation detector.

    ``category`` is a short machine-readable label (``orphaned_assertions``,
    ``stale_specs``, ``authority_conflicts``, ``duplicate_specs``, or
    ``expired_provisionals``).  ``findings`` is a list of per-finding dicts
    whose exact shape is detector-specific but always includes a ``type``
    field echoing the category.
    """

    category: str
    findings: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_iso(ts: str | None) -> datetime | None:
    """Parse an ISO-8601 string into a timezone-aware UTC datetime.

    Returns None if the input is falsy or unparseable.  Handles trailing
    ``Z`` as UTC and naive strings as UTC.
    """
    if not ts or not isinstance(ts, str):
        return None
    try:
        raw = ts.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _iter_spec_targets(spec: dict[str, Any]) -> list[AssertionTarget]:
    """Extract typed assertion targets from a spec's parsed assertions list.

    Mirrors ``impact._targets_for_spec`` so F2 and F8 share the exact same
    extraction path.  Non-dict assertion children (plain text) are silently
    dropped by ``_extract_assertion_targets`` — this is the F8 "plain-text
    safety" guarantee.
    """
    assertions = spec.get("assertions_parsed") or spec.get("_assertions_parsed") or []
    targets: list[AssertionTarget] = []
    if not isinstance(assertions, list):
        return targets
    for a in assertions:
        targets.extend(_extract_assertion_targets(a))
    return targets


_TITLE_PUNCT_RE = re.compile(f"[{re.escape(string.punctuation)}]+")


def _tokenize_title(title: str | None) -> set[str]:
    """Lowercase, strip punctuation, split on whitespace, drop empties."""
    if not title:
        return set()
    cleaned = _TITLE_PUNCT_RE.sub(" ", title.lower())
    return {token for token in cleaned.split() if token}


# ---------------------------------------------------------------------------
# Detector 1: Orphaned assertion targets
# ---------------------------------------------------------------------------


def _target_file_exists(
    target: AssertionTarget,
    project_root: Path,
) -> bool:
    """Resolve an assertion target's file field and check for existence.

    Dispatch rules (must stay aligned with assertions.py handlers):

    - ``glob``                         → always glob resolution
    - ``grep``/``grep_absent``/``count`` with ``*`` in ``file_target``
                                       → glob resolution (any match = exists)
    - ``grep``/``grep_absent``/``count`` without ``*``
                                       → literal resolution
    - ``file_exists``/``json_path``    → literal resolution
                                         (note: ``*`` in the file string is
                                          treated as a literal character —
                                          these types are NOT glob-aware at
                                          execution time, so F8 must match
                                          that contract)

    Targets with a missing/empty ``file_target`` are treated as "exists"
    (nothing to check) and skipped by the caller.
    """
    if not target.file_target:
        return True  # nothing to resolve — caller treats as non-orphan

    use_glob = target.assertion_type == "glob" or (
        target.assertion_type in ("grep", "grep_absent", "count") and target.file_is_glob
    )

    if use_glob:
        matches = _safe_glob(target.file_target, project_root)
        if matches is None:
            # Unsafe pattern — not an orphan, it's a separate safety concern
            return True
        return len(matches) > 0

    resolved = _safe_resolve(target.file_target, project_root)
    if resolved is None:
        # Unsafe literal path — not reported as orphan
        return True
    return resolved.exists()


def find_orphaned_assertions(
    db: KnowledgeDB,
    *,
    project_root: Path | None = None,
) -> ReconciliationReport:
    """Find assertion targets whose backing files no longer exist.

    Iterates every current spec, extracts its typed assertion targets via
    the shared ``_extract_assertion_targets`` helper, and reports each
    target whose resolved path (glob or literal) yields zero matches.

    Composition (``all_of``/``any_of``) is flattened by the extractor, so
    mixed-child compositions produce per-child orphan findings — one finding
    per orphaned leaf target, not one finding per parent composition.

    Plain-text assertions are silently skipped (the extractor returns
    ``[]`` for non-dict assertions, and the detector only sees dict-derived
    targets).

    Args:
        db: Knowledge database.
        project_root: Root used to resolve relative paths.  Defaults to the
            database's configured project root or the current working
            directory if no configuration is available.
    """
    root = _resolve_project_root(db, project_root)
    findings: list[dict] = []

    for spec in db.list_specs():
        spec_id = spec.get("id")
        targets = _iter_spec_targets(spec)
        for target in targets:
            if not target.file_target:
                continue
            if _target_file_exists(target, root):
                continue
            findings.append(
                {
                    "type": "orphaned_assertion",
                    "spec_id": spec_id,
                    "assertion_type": target.assertion_type,
                    "file_target": target.file_target,
                    "match_target": target.match_target,
                    "file_is_glob": target.file_is_glob,
                }
            )

    return ReconciliationReport(category="orphaned_assertions", findings=findings)


def _resolve_project_root(
    db: KnowledgeDB,
    project_root: Path | None,
) -> Path:
    """Return a usable project_root for file resolution.

    Priority: explicit argument → ``db.project_root`` attribute → cwd.
    """
    if project_root is not None:
        return Path(project_root)
    attr = getattr(db, "project_root", None)
    if attr is not None:
        return Path(attr)
    return Path.cwd()


# ---------------------------------------------------------------------------
# Detector 2: Stale specs
# ---------------------------------------------------------------------------


def find_stale_specs(
    db: KnowledgeDB,
    *,
    staleness_threshold_sessions: int = 5,
    staleness_threshold_days: int = 90,
    section_activity_days: int = 30,
) -> ReconciliationReport:
    """Detect specs that have become stale inside an evolving section.

    Snapshot-backed primary path (per bridge/gtkb-phase4-implementation-007.md
    lines 108-159 and bridge/gtkb-phase4-implementation-009.md):

        1. ``all_post_change`` = snapshots with
           ``captured_at > spec.changed_at``
        2. If ``len(all_post_change) < N``, fall back to the ``changed_at``
           path for this spec.
        3. Sort descending by ``captured_at``; take the N most recent →
           ``S_N``.
        4. ``T_window_start = S_N[-1].captured_at``  — the oldest of those
           N snapshots, i.e. the earliest edge of the N-session evidence
           window.
        5. The spec is stale iff some OTHER spec in the same ``section``
           has ``changed_at > T_window_start`` — activity inside the
           evidence window, not before it.

    Fallback path (triggered when the spec has fewer than N post-change
    snapshots):

        - Spec is stale iff ``spec.changed_at`` is older than
          ``now - staleness_threshold_days`` AND another spec in the same
          section has ``changed_at`` within the last
          ``section_activity_days``.

    Specs with no ``section`` are never reported (no same-section signal
    to compare against).
    """
    now = datetime.now(UTC)
    stale_cutoff = now - timedelta(days=staleness_threshold_days)
    activity_cutoff = now - timedelta(days=section_activity_days)

    snapshots = db.get_snapshot_history(limit=1000)
    # Sorted descending by captured_at already (get_snapshot_history contract).
    parsed_snapshots = [(_parse_iso(s.get("captured_at")), s) for s in snapshots]
    parsed_snapshots = [(t, s) for t, s in parsed_snapshots if t is not None]

    findings: list[dict] = []
    all_specs = db.list_specs()

    # Pre-index by section for cheap same-section lookups.
    by_section: dict[str, list[dict[str, Any]]] = {}
    for s in all_specs:
        section = s.get("section")
        if not section:
            continue
        by_section.setdefault(section, []).append(s)

    for spec in all_specs:
        section = spec.get("section")
        if not section:
            continue
        spec_id = spec.get("id")
        spec_changed_at = _parse_iso(spec.get("changed_at"))
        if spec_changed_at is None:
            continue

        post_change = [(t, s) for (t, s) in parsed_snapshots if t > spec_changed_at]

        used_snapshot_path = False
        reason: str | None = None
        window_start: datetime | None = None

        if len(post_change) >= staleness_threshold_sessions:
            used_snapshot_path = True
            selected = post_change[:staleness_threshold_sessions]
            # Already sorted DESC by captured_at → selected[-1] is the
            # oldest of the N most recent → the evidence-window start.
            window_start = selected[-1][0]
            reason = "snapshot_window"

        if used_snapshot_path:
            assert window_start is not None
            others = [o for o in by_section.get(section, []) if o.get("id") != spec_id]
            has_activity = False
            for other in others:
                other_changed = _parse_iso(other.get("changed_at"))
                if other_changed is None:
                    continue
                if other_changed > window_start:
                    has_activity = True
                    break
            if has_activity:
                findings.append(
                    {
                        "type": "stale_spec",
                        "spec_id": spec_id,
                        "section": section,
                        "reason": reason,
                        "window_start": window_start.isoformat(),
                        "snapshots_observed": len(post_change),
                        "threshold_sessions": staleness_threshold_sessions,
                    }
                )
            continue

        # Fallback path — explicit bounded windows.
        if spec_changed_at >= stale_cutoff:
            continue
        others = [o for o in by_section.get(section, []) if o.get("id") != spec_id]
        has_recent_activity = False
        for other in others:
            other_changed = _parse_iso(other.get("changed_at"))
            if other_changed is None:
                continue
            if other_changed >= activity_cutoff:
                has_recent_activity = True
                break
        if has_recent_activity:
            findings.append(
                {
                    "type": "stale_spec",
                    "spec_id": spec_id,
                    "section": section,
                    "reason": "changed_at_fallback",
                    "changed_at": spec.get("changed_at"),
                    "threshold_days": staleness_threshold_days,
                    "section_activity_days": section_activity_days,
                }
            )

    return ReconciliationReport(category="stale_specs", findings=findings)


# ---------------------------------------------------------------------------
# Detector 3: Authority conflicts
# ---------------------------------------------------------------------------


def find_authority_conflicts(db: KnowledgeDB) -> ReconciliationReport:
    """Find stated-vs-inferred specs with overlapping assertion targets.

    A conflict is reported when a ``stated`` spec and an ``inferred`` spec
    share the SAME ``section`` AND the SAME ``scope`` AND have at least
    one ``file_target`` string in common after alias resolution and
    composition flattening.

    This is the F8-003 "structural overlap" rule: no semantic similarity,
    only ``file_target`` string identity.  Alias overlap (``target``,
    ``path``, etc.), composition overlap (``all_of``/``any_of`` children),
    and glob-string overlap (``*`` patterns) are all handled by the
    shared extractor producing identical ``file_target`` strings.
    """
    stated = db.list_specs(authority="stated")
    inferred = db.list_specs(authority="inferred")

    findings: list[dict] = []
    for inf in inferred:
        inf_section = inf.get("section")
        inf_scope = inf.get("scope")
        inf_targets = _iter_spec_targets(inf)
        inf_files = {t.file_target for t in inf_targets if t.file_target}
        if not inf_files:
            continue
        for st in stated:
            if st.get("section") != inf_section or st.get("scope") != inf_scope:
                continue
            st_targets = _iter_spec_targets(st)
            st_files = {t.file_target for t in st_targets if t.file_target}
            overlap = inf_files & st_files
            if not overlap:
                continue
            findings.append(
                {
                    "type": "authority_conflict",
                    "stated_spec": st.get("id"),
                    "inferred_spec": inf.get("id"),
                    "section": inf_section,
                    "scope": inf_scope,
                    "overlapping_targets": sorted(overlap),
                }
            )

    return ReconciliationReport(category="authority_conflicts", findings=findings)


# ---------------------------------------------------------------------------
# Detector 4: Duplicate specs (title token overlap)
# ---------------------------------------------------------------------------


def find_duplicate_specs(
    db: KnowledgeDB,
    *,
    title_token_overlap_threshold: float = 0.9,
) -> ReconciliationReport:
    """Find spec pairs whose titles share >= ``title_token_overlap_threshold``
    of their tokens.

    Tokenization is lowercase + punctuation-strip + whitespace-split.
    Overlap is defined as Jaccard-style:
    ``|tokens(a) ∩ tokens(b)| / |tokens(a) ∪ tokens(b)|``.  Each pair is
    reported once (``spec_a.id < spec_b.id`` order) to keep output
    deterministic and avoid duplicated reports.
    """
    specs = db.list_specs()
    tokens_by_spec: list[tuple[str, set[str]]] = []
    for spec in specs:
        spec_id = spec.get("id")
        if not spec_id:
            continue
        tokens = _tokenize_title(spec.get("title"))
        if not tokens:
            continue
        tokens_by_spec.append((spec_id, tokens))

    findings: list[dict] = []
    n = len(tokens_by_spec)
    for i in range(n):
        id_a, tok_a = tokens_by_spec[i]
        for j in range(i + 1, n):
            id_b, tok_b = tokens_by_spec[j]
            union = tok_a | tok_b
            if not union:
                continue
            overlap = len(tok_a & tok_b) / len(union)
            if overlap + 1e-9 >= title_token_overlap_threshold:
                # Canonicalize pair order by id
                first, second = (id_a, id_b) if id_a < id_b else (id_b, id_a)
                findings.append(
                    {
                        "type": "duplicate_spec",
                        "spec_a": first,
                        "spec_b": second,
                        "overlap": round(overlap, 4),
                    }
                )

    return ReconciliationReport(category="duplicate_specs", findings=findings)


# ---------------------------------------------------------------------------
# Detector 5: Expired provisionals
# ---------------------------------------------------------------------------


def find_expired_provisionals(db: KnowledgeDB) -> ReconciliationReport:
    """Find provisional specs whose replacement has shipped.

    Iterates :meth:`KnowledgeDB.get_provisional_specs` (which already
    filters on ``authority='provisional' AND provisional_until IS NOT NULL``),
    then checks each provisional's replacement spec's lifecycle ``status``.

    A provisional spec is 'expired' when:

        (a) the provisional spec itself satisfies
            ``authority == 'provisional'`` AND ``provisional_until IS NOT NULL``
            — this is exactly what ``get_provisional_specs`` returns, so
            callers do not need to re-filter;
        (b) the replacement spec, looked up by id from ``provisional_until``,
            has lifecycle ``status in {'implemented', 'verified'}``.

    Replacements still at lifecycle ``status='specified'`` or
    ``'deprecated'``, or replacements that are themselves provisional,
    do NOT trigger expiration.  The provisional remains load-bearing
    until its replacement has actually shipped.

    Note on field separation: ``provisional`` is an AUTHORITY value, not
    a STATUS value.  Do not filter on ``spec.status == 'provisional'`` —
    no spec ever has that status.  The current F1 schema keeps authority
    (source) and status (lifecycle) strictly orthogonal.

    Relies on existing F1 support:

        - ``db.get_provisional_specs()``       (groundtruth_kb/db.py:1048-1059)
        - ``specifications.authority='provisional'`` pairing with
          ``specifications.provisional_until``  (groundtruth_kb/db.py:515-527)
    """
    findings: list[dict] = []
    for provisional in db.get_provisional_specs():
        replacement_id = provisional.get("provisional_until")
        if not replacement_id:
            continue  # defensive; get_provisional_specs already filters this
        replacement = db.get_spec(replacement_id)
        if replacement is None:
            continue  # dangling replacement reference is a separate concern
        if replacement.get("status") in ("implemented", "verified"):
            findings.append(
                {
                    "type": "expired_provisional",
                    "spec_id": provisional["id"],
                    "replacement_spec_id": replacement_id,
                    "replacement_status": replacement["status"],
                }
            )

    return ReconciliationReport(
        category="expired_provisionals",
        findings=findings,
    )

# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
GroundTruth KB — F8 Provenance Reconciliation over the native authority.

Five read-only detectors inspect the current specification records of the
selected authority for provenance drift:

  - ``find_orphaned_assertions`` — assertion targets whose files no longer exist
  - ``find_stale_specs`` — specs unchanged for ``staleness_threshold_days``
    inside a section that changed within ``section_activity_days``
  - ``find_authority_conflicts`` — stated vs inferred specs with structural
    assertion-target overlap inside the same (section, scope)
  - ``find_duplicate_specs`` — specs with near-identical titles (token overlap)
  - ``find_expired_provisionals`` — provisional specs whose replacement
    (looked up via ``provisional_until``) carries ``implementation_verified_at``

Every detector reads through a :class:`SpecSource`: a read-only view of the
current specification records in the native record shape (``id``, ``title``,
``status``, ``section``, ``scope``, ``authority``, ``assertions`` as a JSON
list, ``provisional_until``, ``implementation_verified_at``, ``changed_at``).
:class:`NativeSpecSource` pages ``GET /v1/specifications`` of the configured
authority. Nothing here writes: findings are reports, not verdicts or gates.

All detectors return a :class:`ReconciliationReport` holding a category label
and a list of finding dicts.  Reports are deterministic: the same records give
the same output.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import re
import string
from collections.abc import Iterable, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

from groundtruth_kb.assertions import (
    AssertionTarget,
    _extract_assertion_targets,
    _safe_glob,
    _safe_resolve,
)
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.postgres_kernel import canonical_json_bytes

ACTIVE_STATUS = "active"
"""Native lifecycle status of a current, load-bearing specification."""

DETECTOR_CATEGORIES: tuple[str, ...] = (
    "orphaned_assertions",
    "stale_specs",
    "authority_conflicts",
    "duplicate_specs",
    "expired_provisionals",
)
"""Every detector category in the canonical run order."""


# ---------------------------------------------------------------------------
# Specification sources
# ---------------------------------------------------------------------------


class SpecSource(Protocol):
    """Read-only source of current specification records in the native shape."""

    def list_specs(self, *, status: str | None = None, authority: str | None = None) -> list[dict[str, Any]]:
        """Return the current records matching every given filter, in deterministic ID order."""
        ...


class NativeSpecSource:
    """Page ``GET /v1/specifications`` of the selected authority; never writes.

    Pages are read with ``limit``/``after`` until ``next_after`` is null.  The
    ``status`` filter is a native list filter and is passed through as a query
    parameter; the list route accepts no ``authority`` query field, so
    ``authority`` is applied client-side over the listed records.  Each
    distinct ``status`` listing is read once per instance, so one
    reconciliation run is one bounded read of current state.  A malformed
    page (wrong shape, missing or duplicate identities, a cursor that does not
    advance) is an ``invalid_response`` error, never a partial corpus.
    """

    page_size = 500

    def __init__(self, client: AuthorityClient) -> None:
        self.client = client
        self._listings: dict[str | None, list[dict[str, Any]]] = {}

    def list_specs(self, *, status: str | None = None, authority: str | None = None) -> list[dict[str, Any]]:
        records = self._listing(status)
        if authority is not None:
            return [record for record in records if record.get("authority") == authority]
        return list(records)

    def _listing(self, status: str | None) -> list[dict[str, Any]]:
        cached = self._listings.get(status)
        if cached is not None:
            return cached
        records: list[dict[str, Any]] = []
        identities: set[str] = set()
        cursors: set[str] = set()
        after: str | None = None
        while True:
            page = self.client.request(
                "GET",
                "/v1/specifications",
                query={"status": status, "after": after, "limit": self.page_size},
            )
            if not isinstance(page, dict) or not isinstance(page.get("records"), list) or "next_after" not in page:
                raise AuthorityClientError("invalid_response", "Expected a complete specification page")
            for record in page["records"]:
                if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                    raise AuthorityClientError("invalid_response", "Expected specification identities in the page")
                if record["id"] in identities:
                    raise AuthorityClientError("invalid_response", "Duplicate specification in the listed corpus")
                identities.add(record["id"])
                records.append(record)
            next_after = page["next_after"]
            if next_after is None:
                break
            if not isinstance(next_after, str) or not next_after or not page["records"] or next_after in cursors:
                raise AuthorityClientError("invalid_response", "Specification pagination did not advance")
            cursors.add(next_after)
            after = next_after
        self._listings[status] = records
        return records


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
    findings: list[dict[str, Any]] = field(default_factory=list)


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


def _is_timestamp(value: Any) -> bool:
    """True for a datetime or a parseable ISO-8601 string; null and junk are not timestamps."""
    if isinstance(value, datetime):
        return True
    return isinstance(value, str) and _parse_iso(value) is not None


def _spec_assertions(spec: dict[str, Any]) -> list[Any]:
    """Return the spec's assertion list.

    Native records carry ``assertions`` as a JSON list.  A JSON string (an
    older projection of the same field) is decoded; any other shape yields no
    assertions rather than a crash.
    """
    value = spec.get("assertions")
    if isinstance(value, str):
        with suppress(json.JSONDecodeError):
            value = json.loads(value)
    return value if isinstance(value, list) else []


def _iter_spec_targets(spec: dict[str, Any]) -> list[AssertionTarget]:
    """Extract typed assertion targets from a spec's assertions list.

    Mirrors ``impact._targets_for_spec`` so F2 and F8 share the exact same
    extraction path.  Non-dict assertion children (plain text) are silently
    dropped by ``_extract_assertion_targets`` — this is the F8 "plain-text
    safety" guarantee.
    """
    targets: list[AssertionTarget] = []
    for assertion in _spec_assertions(spec):
        targets.extend(_extract_assertion_targets(assertion))
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
    source: SpecSource,
    *,
    project_root: Path | None = None,
) -> ReconciliationReport:
    """Find assertion targets whose backing files no longer exist.

    Iterates every active spec, extracts its typed assertion targets via
    the shared ``_extract_assertion_targets`` helper, and reports each
    target whose resolved path (glob or literal) yields zero matches.

    Composition (``all_of``/``any_of``) is flattened by the extractor, so
    mixed-child compositions produce per-child orphan findings — one finding
    per orphaned leaf target, not one finding per parent composition.

    Plain-text assertions are silently skipped (the extractor returns
    ``[]`` for non-dict assertions, and the detector only sees dict-derived
    targets).

    Args:
        source: Current specification records.
        project_root: Root used to resolve relative paths.  Defaults to the
            current working directory.
    """
    root = Path(project_root) if project_root is not None else Path.cwd()
    findings: list[dict[str, Any]] = []

    for spec in source.list_specs(status=ACTIVE_STATUS):
        spec_id = spec.get("id")
        for target in _iter_spec_targets(spec):
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


# ---------------------------------------------------------------------------
# Detector 2: Stale specs
# ---------------------------------------------------------------------------


def find_stale_specs(
    source: SpecSource,
    *,
    staleness_threshold_days: int = 90,
    section_activity_days: int = 30,
    now: datetime | None = None,
) -> ReconciliationReport:
    """Detect active specs that stopped changing while their section kept evolving.

    A spec is stale iff its ``changed_at`` is older than
    ``now - staleness_threshold_days`` AND another active spec in the same
    ``section`` has ``changed_at`` within the last ``section_activity_days``.

    Specs with no ``section`` (no same-section signal to compare against) or
    no parseable ``changed_at`` are never reported.  ``now`` must be
    timezone-aware; it defaults to the current UTC time.

    The N-session snapshot evidence window of the SQLite era has no native
    record source (session snapshots are retired), so the ``changed_at``
    window is the only path and every finding carries ``reason: changed_at``.
    """
    current = now if now is not None else datetime.now(UTC)
    stale_cutoff = current - timedelta(days=staleness_threshold_days)
    activity_cutoff = current - timedelta(days=section_activity_days)

    dated: list[tuple[dict[str, Any], str, datetime]] = []
    by_section: dict[str, list[tuple[Any, datetime]]] = {}
    for spec in source.list_specs(status=ACTIVE_STATUS):
        section = spec.get("section")
        changed_at = _parse_iso(spec.get("changed_at"))
        if not section or changed_at is None:
            continue
        dated.append((spec, section, changed_at))
        by_section.setdefault(section, []).append((spec.get("id"), changed_at))

    findings: list[dict[str, Any]] = []
    for spec, section, changed_at in dated:
        if changed_at >= stale_cutoff:
            continue
        spec_id = spec.get("id")
        has_recent_activity = any(
            other_id != spec_id and other_changed >= activity_cutoff for other_id, other_changed in by_section[section]
        )
        if not has_recent_activity:
            continue
        findings.append(
            {
                "type": "stale_spec",
                "spec_id": spec_id,
                "section": section,
                "reason": "changed_at",
                "changed_at": spec.get("changed_at"),
                "threshold_days": staleness_threshold_days,
                "section_activity_days": section_activity_days,
            }
        )

    return ReconciliationReport(category="stale_specs", findings=findings)


# ---------------------------------------------------------------------------
# Detector 3: Authority conflicts
# ---------------------------------------------------------------------------


def find_authority_conflicts(source: SpecSource) -> ReconciliationReport:
    """Find stated-vs-inferred specs with overlapping assertion targets.

    A conflict is reported when an active ``stated`` spec and an active
    ``inferred`` spec share the SAME ``section`` AND the SAME ``scope`` AND
    have at least one ``file_target`` string in common after alias resolution
    and composition flattening.

    This is the F8-003 "structural overlap" rule: no semantic similarity,
    only ``file_target`` string identity.  Alias overlap (``target``,
    ``path``, etc.), composition overlap (``all_of``/``any_of`` children),
    and glob-string overlap (``*`` patterns) are all handled by the
    shared extractor producing identical ``file_target`` strings.
    """
    stated = source.list_specs(status=ACTIVE_STATUS, authority="stated")
    inferred = source.list_specs(status=ACTIVE_STATUS, authority="inferred")

    findings: list[dict[str, Any]] = []
    for inf in inferred:
        inf_section = inf.get("section")
        inf_scope = inf.get("scope")
        inf_files = {t.file_target for t in _iter_spec_targets(inf) if t.file_target}
        if not inf_files:
            continue
        for st in stated:
            if st.get("section") != inf_section or st.get("scope") != inf_scope:
                continue
            st_files = {t.file_target for t in _iter_spec_targets(st) if t.file_target}
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
    source: SpecSource,
    *,
    title_token_overlap_threshold: float = 0.9,
) -> ReconciliationReport:
    """Find active spec pairs whose titles share >= ``title_token_overlap_threshold``
    of their tokens.

    Tokenization is lowercase + punctuation-strip + whitespace-split.
    Overlap is defined as Jaccard-style:
    ``|tokens(a) ∩ tokens(b)| / |tokens(a) ∪ tokens(b)|``.  Each pair is
    reported once (``spec_a.id < spec_b.id`` order) to keep output
    deterministic and avoid duplicated reports.
    """
    tokens_by_spec: list[tuple[str, set[str]]] = []
    for spec in source.list_specs(status=ACTIVE_STATUS):
        spec_id = spec.get("id")
        if not spec_id:
            continue
        tokens = _tokenize_title(spec.get("title"))
        if not tokens:
            continue
        tokens_by_spec.append((spec_id, tokens))

    findings: list[dict[str, Any]] = []
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


def find_expired_provisionals(source: SpecSource) -> ReconciliationReport:
    """Find active provisional specs whose replacement has a verified implementation.

    A provisional spec is one with ``authority == 'provisional'`` and a
    ``provisional_until`` reference to its replacement.  It is 'expired' when
    the referenced replacement record exists and carries
    ``implementation_verified_at``: the native marker that the replacement's
    implementation was verified.  The SQLite lifecycle statuses
    ``implemented``/``verified`` do not exist natively (``status`` is
    ``active``, ``superseded`` or ``retired``), so the verification timestamp
    is the equivalent signal.  A replacement without it, or a dangling
    reference, does NOT expire the provisional: it remains load-bearing until
    its replacement has actually shipped.

    Note on field separation: ``provisional`` is an AUTHORITY value, not a
    STATUS value.  Do not filter on ``spec.status == 'provisional'`` — no
    spec ever has that status.  Authority (source) and status (lifecycle)
    stay strictly orthogonal.
    """
    by_id: dict[str, dict[str, Any]] = {
        spec["id"]: spec for spec in source.list_specs() if isinstance(spec.get("id"), str)
    }
    findings: list[dict[str, Any]] = []
    for provisional in source.list_specs(status=ACTIVE_STATUS, authority="provisional"):
        replacement_id = provisional.get("provisional_until")
        if not isinstance(replacement_id, str) or not replacement_id:
            continue
        replacement = by_id.get(replacement_id)
        if replacement is None:
            continue  # dangling replacement reference is a separate concern
        verified_at = replacement.get("implementation_verified_at")
        if not _is_timestamp(verified_at):
            continue
        findings.append(
            {
                "type": "expired_provisional",
                "spec_id": provisional.get("id"),
                "replacement_spec_id": replacement_id,
                "replacement_status": replacement.get("status"),
                "replacement_implementation_verified_at": (
                    verified_at.isoformat() if isinstance(verified_at, datetime) else verified_at
                ),
            }
        )

    return ReconciliationReport(
        category="expired_provisionals",
        findings=findings,
    )


# ---------------------------------------------------------------------------
# Composition (shared by the CLI and by tests)
# ---------------------------------------------------------------------------


def run_detectors(
    source: SpecSource,
    categories: Iterable[str],
    *,
    project_root: Path | None = None,
    staleness_threshold_days: int = 90,
    section_activity_days: int = 30,
) -> list[ReconciliationReport]:
    """Run the selected detectors in canonical order and return one report each.

    ``categories`` selects by :data:`DETECTOR_CATEGORIES` label; the order of
    the selection does not matter and unknown labels are a ``ValueError``.
    """
    selected = set(categories)
    unknown = sorted(selected - set(DETECTOR_CATEGORIES))
    if unknown:
        raise ValueError(f"Unknown reconciliation detector(s): {', '.join(unknown)}")
    reports: list[ReconciliationReport] = []
    for category in DETECTOR_CATEGORIES:
        if category not in selected:
            continue
        if category == "orphaned_assertions":
            reports.append(find_orphaned_assertions(source, project_root=project_root))
        elif category == "stale_specs":
            reports.append(
                find_stale_specs(
                    source,
                    staleness_threshold_days=staleness_threshold_days,
                    section_activity_days=section_activity_days,
                )
            )
        elif category == "authority_conflicts":
            reports.append(find_authority_conflicts(source))
        elif category == "duplicate_specs":
            reports.append(find_duplicate_specs(source))
        else:
            reports.append(find_expired_provisionals(source))
    return reports


def format_report_text(reports: Sequence[ReconciliationReport], *, per_report_limit: int = 50) -> str:
    """Render reports as the CLI's text output.

    One ``[category] N finding(s)`` block per report with up to
    ``per_report_limit`` canonical-JSON finding lines (the remainder is
    counted), then ``Total findings across N detector(s): M``.
    """
    lines: list[str] = []
    total = 0
    for report in reports:
        lines.append("")
        lines.append(f"[{report.category}] {len(report.findings)} finding(s)")
        total += len(report.findings)
        for finding in report.findings[:per_report_limit]:
            label = finding.get("spec_id") or finding.get("spec_a") or finding.get("inferred_spec") or "?"
            lines.append(f"  - {label}: {canonical_json_bytes(finding).decode('utf-8').strip()}")
        if len(report.findings) > per_report_limit:
            lines.append(f"  ... ({len(report.findings) - per_report_limit} more)")
    lines.append("")
    lines.append(f"Total findings across {len(reports)} detector(s): {total}")
    return "\n".join(lines) + "\n"

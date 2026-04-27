"""Wave 2 lane 9 (Stage B): release-readiness artifact split by subject.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice6-003.md`` (REVISED-1)
and ``-004`` (Codex GO with 6 implementation conditions).

Reads 5 explicit sources per Codex Slice 5 ``-002`` F1 prescription:

1. ``memory/release-readiness.md`` — live ledger; whole-file adopter
   classification with section headers extracted (not full content).
2. KB documents via ``KnowledgeDB.list_documents()``, filtered to
   release-keyword candidates; classified with a DOC-specific
   heuristic (per ``-004`` condition 3 — DOCs don't follow GTKB-/AR-
   prefix; cannot use the shared prefix helper).
3. Release-gate implementation surfaces (``scripts/release_candidate_gate.py``,
   workflow YAML, skill SKILL.md) — classified as **adopter** with
   ``mechanism_origin`` provenance metadata (per ``-004`` condition 1
   + isolation inventory: these are application release gates, not
   GT-KB product gates).
4. Specs + work items via ``KnowledgeDB.list_specs()`` + ``list_work_items()``,
   classified via ``_split_helper.classify_with_content_override()``
   (per ``-004`` condition 2 — GTKB-* + Agent Red content stays
   unclassified, not silent adopter).
5. Deliberations via ``KnowledgeDB.list_deliberations()`` —
   **uncapped inventory API**, NOT ``search_deliberations()`` which
   has a default cap of 5. Per Codex Slice 5 ``-002``: explicit
   regression guard test asserts ``search_deliberations`` is not
   called.

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001; Wave 2 GO at
``bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md``.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import (
    emit_result,
    partition_items,
)

# Release-gate implementation surfaces (per Codex `-004` condition 1:
# adopter classification with mechanism_origin metadata).
_RELEASE_GATE_SURFACES: tuple[tuple[str, str], ...] = (
    ("scripts/release_candidate_gate.py", "agent_red_local"),
    (".github/workflows/release-candidate-gate.yml", "agent_red_local"),
    (".claude/skills/release-candidate-gate/SKILL.md", "agent_red_local"),
)

# Documents whose ID is a release keyword candidate. Not a closed list;
# matched case-insensitively against the actual list_documents() output.
_RELEASE_DOC_KEYWORDS: tuple[str, ...] = (
    "release",
    "readiness",
)

# Known DOC IDs that are explicitly Agent-Red-local. Per Codex `-004`
# condition 3: DOC records don't follow GTKB-/AR- prefix; explicit
# allowlist anchors known cases. Test minimum: DOC-release-readiness-recovery.
_KNOWN_ADOPTER_DOC_IDS: frozenset[str] = frozenset(
    {
        "doc-release-readiness-recovery",
    }
)

_H2_HEADER = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)


def _extract_section_headers(markdown_text: str) -> list[str]:
    """Return the H2 section titles from the ledger.

    Whole-content extraction is intentionally avoided per Codex Slice 6
    ``-002`` non-blocking note: section headers give downstream
    consumers a quick sanity check without copying multi-KB content.
    """
    return [m.group("title").strip() for m in _H2_HEADER.finditer(markdown_text)]


def _classify_release_readiness_md(
    path: Path,
) -> dict[str, Any]:
    """Classify the live ledger as a whole-file adopter artifact."""
    if not path.exists():
        return {
            "path": str(path).replace("\\", "/"),
            "exists": False,
            "classification": "unclassified",
            "classification_signal": "release_readiness_md_missing",
        }
    text = path.read_text(encoding="utf-8")
    section_headers = _extract_section_headers(text)
    return {
        "path": str(path).replace("\\", "/"),
        "exists": True,
        "classification": "adopter",
        "classification_signal": "explicit_adopter_ledger",
        "size_bytes": len(text.encode("utf-8")),
        "section_count": len(section_headers),
        "section_headers": section_headers,
    }


def _classify_document(doc: dict[str, Any]) -> tuple[str, str]:
    """DOC-specific classifier per Codex Slice 6 ``-004`` GO condition 3.

    DOC IDs (e.g. ``DOC-release-readiness-recovery``,
    ``doc-release-management``, ``doc-release-plan-v1.57``) do NOT
    follow GTKB-/AR- prefix structure. Cannot use the shared prefix
    helper. Heuristic:

    1. Known adopter-doc ID allowlist (``_KNOWN_ADOPTER_DOC_IDS``)
       → adopter (signal: ``doc_id_known_adopter``).
    2. Title or content explicit Agent Red mention → adopter
       (signal: ``doc_title_agent_red`` or ``doc_content_agent_red``).
    3. ``release management`` / ``release plan`` generic title with no
       Agent Red mention → framework.
    4. Otherwise → unclassified (signal: ``doc_no_subject_signal``).
    """
    doc_id = (doc.get("id") or "").lower()
    title = (doc.get("title") or "").lower()
    # Cap content scan to first 5000 chars to avoid pathological docs.
    content = (doc.get("content") or "")[:5000].lower()

    if doc_id in _KNOWN_ADOPTER_DOC_IDS:
        return ("adopter", "doc_id_known_adopter")
    if "agent red" in title or "agent_red" in title:
        return ("adopter", "doc_title_agent_red")
    if "agent red" in content or "agent_red" in content:
        return ("adopter", "doc_content_agent_red")
    if "release management" in title or "release plan" in title:
        return ("framework", "doc_release_management_generic")
    return ("unclassified", "doc_no_subject_signal")


def _is_release_doc(doc: dict[str, Any]) -> bool:
    """Filter docs to release-keyword candidates."""
    blob = ((doc.get("id") or "") + " " + (doc.get("title") or "")).lower()
    return any(k in blob for k in _RELEASE_DOC_KEYWORDS)


def _classify_release_gate_surfaces(legacy_root: Path) -> list[dict[str, Any]]:
    """Return per-surface entries with adopter classification + mechanism_origin.

    Per Codex Slice 6 ``-004`` condition 1: these are application
    release gates per the isolation inventory, not GT-KB product
    gates. ``mechanism_origin`` separates ownership bucket from
    provenance.
    """
    entries: list[dict[str, Any]] = []
    for relpath, mechanism_origin in _RELEASE_GATE_SURFACES:
        full = legacy_root / relpath
        exists = full.exists()
        size = full.stat().st_size if (exists and full.is_file()) else None
        entries.append(
            {
                "path": relpath,
                "exists": exists,
                "classification": "adopter",
                "classification_signal": "application_release_gate_surface",
                "mechanism_origin": mechanism_origin,
                "size_bytes": size,
            }
        )
    return entries


_RELEASE_READINESS_KEYWORDS: tuple[str, ...] = (
    "release",
    "readiness",
    "deployment",
    "deploy",
    "blocker",
    "gate",
    "recovery",
    "regression",
    "production",
    "staging",
)

# Spec types relevant to release-readiness inventory (per Codex Slice 6
# `-006` F1 fix: don't blindly include all SPEC-* rows). Sourced from
# the live KB type set.
_RELEVANT_SPEC_TYPES: tuple[str, ...] = (
    "governance",
    "protected_behavior",
    "architecture_decision",
    "design_constraint",
    "requirement",
)

# Resolution-statuses considered "open / recently closed" for the WI
# filter per the original Slice 6 -001 §2.4 contract. The live KB also
# uses 'resolved' which is excluded so historical WIs don't flood the
# split.
_OPEN_RESOLUTION_STATUSES: frozenset[str | None] = frozenset({None, "", "open", "in_progress", "pending", "blocked"})

# Framework-content markers complement adopter markers per Codex Slice
# 6 ``-006`` F2 fix. Real KB IDs (SPEC-/GOV-/PB-/ADR-/DCL-/WI-/DELIB-)
# don't carry inherent subject signal; content is the only signal. Use
# explicit framework keywords as the symmetric counterpart to adopter
# markers so the classifier can detect framework-targeted records.
_FRAMEWORK_CONTENT_MARKERS: tuple[str, ...] = (
    "groundtruth-kb",
    "groundtruth_kb",
    "gt-kb framework",
    "framework upstream",
    "upstream package",
)


def _spec_content_blob(spec: dict[str, Any]) -> str:
    """Per Codex Slice 6 ``-006`` F2: include the actual KB fields
    (title, description, scope) — not the absent summary/content fields
    the original implementation read."""
    return (
        (spec.get("title") or "")
        + " "
        + (spec.get("description") or "")
        + " "
        + (spec.get("scope") or "")
        + " "
        + (spec.get("rationale") or "")
    )


def _wi_content_blob(wi: dict[str, Any]) -> str:
    return (wi.get("title") or "") + " " + (wi.get("description") or "") + " " + (wi.get("failure_description") or "")


def _delib_content_blob(delib: dict[str, Any]) -> str:
    """Per Codex Slice 6 ``-006`` F2: include the content field as well
    (deliberations have title + summary + content)."""
    return (delib.get("title") or "") + " " + (delib.get("summary") or "") + " " + (delib.get("content") or "")


def _is_release_readiness_relevant(text: str) -> bool:
    """True if the text mentions any release-readiness keyword."""
    blob = text.lower()
    return any(k in blob for k in _RELEASE_READINESS_KEYWORDS)


def _filtered_specs(kb: Any) -> list[dict[str, Any]]:
    """Per Codex Slice 6 ``-006`` F1: filter specs by relevant types
    AND release-readiness keyword match before classification."""
    specs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for spec_type in _RELEVANT_SPEC_TYPES:
        for spec in kb.list_specs(type=spec_type):
            spec_id = spec.get("id", "")
            if spec_id in seen_ids:
                continue
            if _is_release_readiness_relevant(_spec_content_blob(spec)):
                specs.append(spec)
                seen_ids.add(spec_id)
    return specs


def _filtered_work_items(kb: Any) -> list[dict[str, Any]]:
    """Per Codex Slice 6 ``-006`` F1: filter WIs to open/recently-closed
    AND release-readiness keyword match before classification."""
    return [
        w
        for w in kb.list_work_items()
        if w.get("resolution_status") in _OPEN_RESOLUTION_STATUSES
        and _is_release_readiness_relevant(_wi_content_blob(w))
    ]


def _filtered_deliberations(kb: Any) -> list[dict[str, Any]]:
    """Per Codex Slice 6 ``-006`` F1: filter deliberations to
    owner_decision outcomes OR release-readiness keyword matches.

    Uses the inventory ``list_deliberations()`` API; never
    ``search_deliberations()`` (which is capped) per Codex Slice 5
    ``-002``.
    """
    owner_decisions = kb.list_deliberations(outcome="owner_decision")
    seen_ids = {d.get("id", "") for d in owner_decisions}
    relevant_others = [
        d
        for d in kb.list_deliberations()
        if d.get("id") not in seen_ids and _is_release_readiness_relevant(_delib_content_blob(d))
    ]
    return owner_decisions + relevant_others


def _classify_release_readiness_artifact(
    record_id: str,
    content_blob: str,
) -> tuple[str, str]:
    """Real-ID-family classifier per Codex Slice 6 ``-006`` F2.

    Real KB IDs (SPEC-/GOV-/PB-/ADR-/DCL-/WI-/DELIB-) do NOT carry
    inherent subject signal; content is the only reliable indicator.
    GTKB-/AR- records still use the prefix-with-conflict-routing rule.

    Returns ``(classification, signal)``:

    - ``AR-*`` prefix → ``('adopter', 'ar_prefix')``
    - ``GTKB-*`` prefix + adopter content → ``('unclassified',
      'gtkb_prefix_with_adopter_content')``
    - ``GTKB-*`` prefix + no adopter content → ``('framework',
      'gtkb_prefix')``
    - Any other prefix + both adopter and framework content →
      ``('unclassified', 'mixed_content_signals')`` (conflict-preserving)
    - Any other prefix + only adopter content → ``('adopter',
      'artifact_content_agent_red')``
    - Any other prefix + only framework content → ``('framework',
      'artifact_content_framework')``
    - Any other prefix + neither → ``('unclassified',
      'artifact_no_subject_signal')``
    """
    blob = content_blob.lower()
    has_adopter = any(m in blob for m in ("agent red", "agent_red"))
    has_framework = any(m in blob for m in _FRAMEWORK_CONTENT_MARKERS)

    if record_id.startswith("AR-"):
        return ("adopter", "ar_prefix")
    if record_id.startswith("GTKB-"):
        if has_adopter:
            return ("unclassified", "gtkb_prefix_with_adopter_content")
        return ("framework", "gtkb_prefix")

    if has_adopter and has_framework:
        return ("unclassified", "mixed_content_signals")
    if has_adopter:
        return ("adopter", "artifact_content_agent_red")
    if has_framework:
        return ("framework", "artifact_content_framework")
    return ("unclassified", "artifact_no_subject_signal")


def _classify_spec(spec: dict[str, Any]) -> tuple[str, str]:
    return _classify_release_readiness_artifact(spec.get("id", ""), _spec_content_blob(spec))


def _classify_work_item(wi: dict[str, Any]) -> tuple[str, str]:
    return _classify_release_readiness_artifact(wi.get("id", ""), _wi_content_blob(wi))


def _classify_deliberation(delib: dict[str, Any]) -> tuple[str, str]:
    return _classify_release_readiness_artifact(delib.get("id", ""), _delib_content_blob(delib))


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    release_readiness_path: Path | None = None,
    kb: Any | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage B leaf lane. Per common contract Wave 2 -003 §4.1.

    ``release_readiness_path`` (default ``LEGACY_ROOT/memory/release-readiness.md``)
    and ``kb`` (default a fresh ``KnowledgeDB()`` instance; tests pass
    a duck-typed object exposing ``list_documents``, ``list_specs``,
    ``list_work_items``, ``list_deliberations``) are fixture-root
    parameter overrides per Codex Slice 5 ``-002`` non-blocking note 4.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    lane_dir = output_dir / "release_readiness_split"
    lane_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = (
        release_readiness_path
        if release_readiness_path is not None
        else LEGACY_ROOT / "memory" / "release-readiness.md"
    )

    if kb is None:
        try:
            import sys

            sys.path.insert(0, str(LEGACY_ROOT / "tools" / "knowledge-db"))
            from db import KnowledgeDB  # type: ignore[import-not-found]

            kb = KnowledgeDB()
        except Exception as exc:
            return emit_result(
                lane_dir,
                {
                    "status": "error",
                    "output_files": [],
                    "metrics": {},
                    "warnings": [f"kb_unavailable: {exc}"],
                },
            )

    warnings: list[str] = []

    ledger_record = _classify_release_readiness_md(ledger_path)
    if not ledger_record["exists"]:
        warnings.append(f"release_readiness_md_missing: {ledger_path}")

    try:
        all_documents = kb.list_documents()
    except Exception as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"list_documents_failed: {exc}"],
            },
        )
    release_docs = [d for d in all_documents if _is_release_doc(d)]
    document_records: list[dict[str, Any]] = []
    for doc in release_docs:
        classification, signal = _classify_document(doc)
        document_records.append(
            {
                "id": doc.get("id"),
                "title": doc.get("title"),
                "category": doc.get("category"),
                "status": doc.get("status"),
                "classification": classification,
                "classification_signal": signal,
            }
        )

    release_gate_surfaces = _classify_release_gate_surfaces(LEGACY_ROOT)

    try:
        # Per Codex Slice 6 -006 F1 fix: filter sources before
        # classification. Specs by type + release-keyword content;
        # work items by open status + release-keyword content;
        # deliberations by owner_decision outcome OR release-keyword
        # content. Replaces the prior whole-KB dump that produced
        # 5,150 artifacts with 5,139 unclassified.
        filtered_specs = _filtered_specs(kb)
        filtered_work_items = _filtered_work_items(kb)
        filtered_deliberations = _filtered_deliberations(kb)
    except Exception as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"kb_inventory_query_failed: {exc}"],
            },
        )

    spec_buckets = partition_items(filtered_specs, _classify_spec)
    wi_buckets = partition_items(filtered_work_items, _classify_work_item)
    delib_buckets = partition_items(filtered_deliberations, _classify_deliberation)

    framework_artifact_count = (
        len(spec_buckets["framework"]) + len(wi_buckets["framework"]) + len(delib_buckets["framework"])
    )
    adopter_artifact_count = (
        1  # ledger
        + sum(1 for d in document_records if d["classification"] == "adopter")
        + sum(1 for s in release_gate_surfaces if s["classification"] == "adopter")
        + len(spec_buckets["adopter"])
        + len(wi_buckets["adopter"])
        + len(delib_buckets["adopter"])
    )
    unclassified_artifact_count = (
        sum(1 for d in document_records if d["classification"] == "unclassified")
        + len(spec_buckets["unclassified"])
        + len(wi_buckets["unclassified"])
        + len(delib_buckets["unclassified"])
    )
    framework_doc_count = sum(1 for d in document_records if d["classification"] == "framework")

    if any(s["classification_signal"] == "gtkb_prefix_with_adopter_content" for s in spec_buckets["unclassified"]):
        warnings.append("specs_gtkb_prefix_with_adopter_content_conflicts: surface for Wave 3")
    if any(w["classification_signal"] == "gtkb_prefix_with_adopter_content" for w in wi_buckets["unclassified"]):
        warnings.append("work_items_gtkb_prefix_with_adopter_content_conflicts: surface for Wave 3")

    release_readiness_split_doc = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": {
            "framework_artifact_count": framework_artifact_count + framework_doc_count,
            "adopter_artifact_count": adopter_artifact_count,
            "unclassified_artifact_count": unclassified_artifact_count,
            "total_artifacts": (
                framework_artifact_count + framework_doc_count + adopter_artifact_count + unclassified_artifact_count
            ),
        },
        "memory_release_readiness_md": ledger_record,
        "documents": document_records,
        "release_gate_surfaces": release_gate_surfaces,
        "framework_specs": spec_buckets["framework"],
        "adopter_specs": spec_buckets["adopter"],
        "unclassified_specs": spec_buckets["unclassified"],
        "framework_work_items": wi_buckets["framework"],
        "adopter_work_items": wi_buckets["adopter"],
        "unclassified_work_items": wi_buckets["unclassified"],
        "framework_deliberations": delib_buckets["framework"],
        "adopter_deliberations": delib_buckets["adopter"],
        "unclassified_deliberations": delib_buckets["unclassified"],
    }

    artifact_path = lane_dir / "release_readiness_split.json"
    artifact_path.write_text(json.dumps(release_readiness_split_doc, indent=2), encoding="utf-8")

    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": [str(artifact_path)],
            "metrics": {
                "framework_artifact_count": release_readiness_split_doc["summary"]["framework_artifact_count"],
                "adopter_artifact_count": release_readiness_split_doc["summary"]["adopter_artifact_count"],
                "unclassified_artifact_count": release_readiness_split_doc["summary"]["unclassified_artifact_count"],
                "total_artifacts": release_readiness_split_doc["summary"]["total_artifacts"],
            },
            "warnings": warnings,
        },
    )

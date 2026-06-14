"""Bridge-thread second-write ingestion into the TAFE shadow store (WI-4508,
Slice C; governed by ``ADR-TAFE-SLICE-C-INGESTION-001``).

This module opens TAFE's first write surface. It materializes each canonical
bridge thread (parsed from a single ``bridge/INDEX.md`` snapshot via the VERIFIED
Slice A lossless parser, :func:`groundtruth_kb.tafe_index_sync.parse_bridge_index`)
into the existing append-only ``flow_instances`` + ``flow_artifacts`` tables as a
**non-authoritative SHADOW** store. The canonical ``bridge/INDEX.md`` remains the
authoritative workflow state per ``GOV-FILE-BRIDGE-AUTHORITY-001``; this module
writes nothing canonical, reads no file, and holds **no canonical-index path
literal** — it receives ``index_text`` as a string and the read-only
``gt flow ingest-bridge-index`` CLI owns the guarded canonical-index read.

The four ADR constraints implemented here:

* **D1** — every thread maps to the seeded ``implementation`` flow_definition;
  the latest version's kind is preserved in ``metadata.bridge_kind``; an
  advisory-latest thread ingests with ``status='advisory'`` and
  ``metadata.bridge_kind='advisory'`` (not skipped — full-shadow coverage).
* **D2** — deterministic identity: ``flow-bridge-<slug>`` instance id and one
  ``fa-bridge-<slug>-<NNN>`` ``bridge_version`` artifact per INDEX version line,
  with ``artifact_ref`` = the canonical ``bridge/<slug>-NNN.md`` reference and
  ``metadata.status_token`` = that version's status.
* **D3** — ``flow_instances.status`` is derived from the thread's LATEST
  version-line token, with the version chain disambiguating a latest ``NEW``:
  a prior ``GO`` in the chain marks a post-implementation report
  (``in_verification``); otherwise it is an initial proposal (``in_review``).
* **D4** — replay-safe idempotence: ``ingest_fingerprint = sha256`` over
  ``(slug, ordered (status, version) tuples)`` stored in
  ``metadata.ingest_fingerprint``; a new flow_instance version is appended only
  when the fingerprint changes; flow_artifacts are insert-if-absent. Re-ingesting
  an unchanged INDEX is a guaranteed no-op.

Slice C writes ``flow_instances`` + ``flow_artifacts`` **only**; no
``stage_instances`` and no ``flow_events`` rows (deferred to a later slice).

Specification links: ``ADR-TAFE-SLICE-C-INGESTION-001`` (D1–D4 + scope),
``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (runtime tables + ``implementation``
flow), ``GOV-FILE-BRIDGE-AUTHORITY-001`` (canonical INDEX preserved; shadow-only).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from groundtruth_kb.tafe_index_sync import DocumentBlock, IndexVersionLine, parse_bridge_index
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

__all__ = [
    "ArtifactResult",
    "IngestionResult",
    "ThreadResult",
    "compute_thread_fingerprint",
    "derive_bridge_kind",
    "derive_flow_status",
    "ingest_bridge_index",
]

#: The seeded flow_definition every bridge thread maps to (ADR D1).
FLOW_DEFINITION_ID = "implementation"

#: ``flow_instances.subject_type`` for shadow bridge threads (ADR D2).
SUBJECT_TYPE = "bridge_thread"

#: ``flow_artifacts.artifact_type`` for one-per-version-line shadow rows (ADR D2).
ARTIFACT_TYPE = "bridge_version"

#: ``flow_artifacts.relationship`` for version-history rows (ADR D2).
ARTIFACT_RELATIONSHIP = "version"

# ADR D3 status-token -> flow status, for every token whose mapping does not
# depend on the version chain. A latest ``NEW`` is resolved separately because
# its meaning (initial proposal vs. post-impl report) depends on a prior ``GO``.
_FLOW_STATUS_BY_TOKEN: dict[str, str] = {
    "REVISED": "in_review",
    "GO": "in_implementation",
    "NO-GO": "in_revision",
    "VERIFIED": "complete",
    "WITHDRAWN": "withdrawn",
    "ADVISORY": "advisory",
    "DEFERRED": "deferred",
}


@dataclass(frozen=True)
class ArtifactResult:
    """The plan/outcome for one ``fa-bridge-<slug>-<NNN>`` version artifact."""

    artifact_id: str
    artifact_ref: str
    status_token: str
    existed: bool


@dataclass(frozen=True)
class ThreadResult:
    """The plan/outcome for one bridge thread's shadow flow_instance."""

    slug: str
    flow_instance_id: str
    flow_status: str
    bridge_kind: str
    fingerprint: str
    instance_action: str  # "created" | "updated" | "unchanged"
    artifacts: tuple[ArtifactResult, ...]

    @property
    def artifacts_written(self) -> int:
        """Count of version artifacts this thread would create (absent before)."""
        return sum(1 for artifact in self.artifacts if not artifact.existed)

    @property
    def instance_written(self) -> bool:
        """True when this thread would append a new flow_instance version."""
        return self.instance_action in ("created", "updated")

    def as_dict(self) -> dict[str, Any]:
        """A JSON-serializable view of the thread result."""
        return {
            "slug": self.slug,
            "flow_instance_id": self.flow_instance_id,
            "flow_status": self.flow_status,
            "bridge_kind": self.bridge_kind,
            "fingerprint": self.fingerprint,
            "instance_action": self.instance_action,
            "instance_written": self.instance_written,
            "artifacts_written": self.artifacts_written,
            "artifacts": [
                {
                    "artifact_id": artifact.artifact_id,
                    "artifact_ref": artifact.artifact_ref,
                    "status_token": artifact.status_token,
                    "existed": artifact.existed,
                }
                for artifact in self.artifacts
            ],
        }


@dataclass
class IngestionResult:
    """Aggregate plan/outcome of a single bridge-index ingestion run."""

    applied: bool
    threads_total: int
    threads_skipped: list[str] = field(default_factory=list)
    results: list[ThreadResult] = field(default_factory=list)

    @property
    def instances_written(self) -> int:
        """Number of flow_instance versions created/updated this run."""
        return sum(1 for result in self.results if result.instance_written)

    @property
    def artifacts_written(self) -> int:
        """Number of flow_artifact rows created this run."""
        return sum(result.artifacts_written for result in self.results)

    def as_dict(self) -> dict[str, Any]:
        """A JSON-serializable view of the ingestion result."""
        return {
            "applied": self.applied,
            "threads_total": self.threads_total,
            "threads_skipped": list(self.threads_skipped),
            "instances_written": self.instances_written,
            "artifacts_written": self.artifacts_written,
            "results": [result.as_dict() for result in self.results],
        }


def _version_suffix(path: str) -> str:
    """Extract the zero-padded ``NNN`` token from a ``bridge/<slug>-NNN.md`` ref.

    Returns the exact suffix as written so the derived ``fa-bridge-<slug>-<NNN>``
    artifact id and the ``bridge/<slug>-NNN.md`` reference stay consistent with
    the canonical file naming.
    """
    stem = path.rsplit("/", 1)[-1]
    base = stem[:-3] if stem.endswith(".md") else stem
    return base.rsplit("-", 1)[-1]


def _latest_version_line(block: DocumentBlock) -> IndexVersionLine | None:
    """Return the highest-version version line (the thread's latest), or None."""
    if not block.version_lines:
        return None
    return max(block.version_lines, key=lambda line: line.version)


def _has_prior_go(block: DocumentBlock, latest: IndexVersionLine) -> bool:
    """True when a ``GO`` exists in the chain below the latest version line."""
    return any(line.status == "GO" and line.version < latest.version for line in block.version_lines)


def derive_flow_status(latest_token: str, *, has_prior_go: bool) -> str:
    """Map a thread's latest status token to ``flow_instances.status`` (ADR D3).

    A latest ``NEW`` resolves to ``in_verification`` when a prior ``GO`` exists in
    the chain (a post-implementation report awaiting verification) and to
    ``in_review`` otherwise (an initial proposal). Unknown/historical tokens are
    recorded as ``unknown`` rather than dropped.
    """
    if latest_token == "NEW":
        return "in_verification" if has_prior_go else "in_review"
    return _FLOW_STATUS_BY_TOKEN.get(latest_token, "unknown")


def derive_bridge_kind(latest_token: str, *, has_prior_go: bool) -> str:
    """Derive ``metadata.bridge_kind`` from the latest version line (ADR D1).

    The kind reflects the latest version file's authoring role: an LO verdict
    (``GO``/``NO-GO``/``VERIFIED``) is a ``verification_verdict``; a ``NEW`` after a
    ``GO`` is an ``implementation_report``; an initial/revised ``NEW``/``REVISED`` is
    an ``implementation_proposal``; an ``ADVISORY``-latest thread is ``advisory``.
    Terminal/parked/unknown tokens record ``unknown`` for full-shadow coverage.
    """
    if latest_token == "ADVISORY":
        return "advisory"
    if latest_token in ("GO", "NO-GO", "VERIFIED"):
        return "verification_verdict"
    if latest_token == "NEW":
        return "implementation_report" if has_prior_go else "implementation_proposal"
    if latest_token == "REVISED":
        return "implementation_proposal"
    return "unknown"


def compute_thread_fingerprint(slug: str, version_lines: tuple[IndexVersionLine, ...]) -> str:
    """Compute the replay-safe ingest fingerprint for a thread (ADR D4).

    The fingerprint is ``sha256`` over the slug plus the thread's
    ``(status, version)`` pairs ordered by version, so it is stable regardless of
    source line order and changes only on a real bridge-state change.
    """
    pairs = sorted((line.version, line.status) for line in version_lines)
    payload = json.dumps([slug, [[version, status] for version, status in pairs]], separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _stored_fingerprint(instance: dict[str, Any]) -> str | None:
    """Read the stored ``metadata.ingest_fingerprint`` from a current instance row."""
    metadata = instance.get("metadata_parsed")
    if not isinstance(metadata, dict):
        raw = instance.get("metadata")
        if isinstance(raw, str) and raw:
            try:
                metadata = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                metadata = None
    if isinstance(metadata, dict):
        value = metadata.get("ingest_fingerprint")
        return value if isinstance(value, str) else None
    return None


def _plan_thread(block: DocumentBlock, service: TypedArtifactFlowService) -> ThreadResult | None:
    """Build the read-only ingestion plan for one bridge-thread document block."""
    latest = _latest_version_line(block)
    if latest is None:
        return None

    slug = block.name
    has_prior_go = _has_prior_go(block, latest)
    flow_status = derive_flow_status(latest.status, has_prior_go=has_prior_go)
    bridge_kind = derive_bridge_kind(latest.status, has_prior_go=has_prior_go)
    fingerprint = compute_thread_fingerprint(slug, block.version_lines)

    flow_instance_id = f"flow-bridge-{slug}"
    existing_instance = service.get_flow_instance(flow_instance_id)
    if existing_instance is None:
        instance_action = "created"
    elif _stored_fingerprint(existing_instance) == fingerprint:
        instance_action = "unchanged"
    else:
        instance_action = "updated"

    artifacts: list[ArtifactResult] = []
    seen_ids: set[str] = set()
    for line in block.version_lines:
        suffix = _version_suffix(line.path)
        artifact_id = f"fa-bridge-{slug}-{suffix}"
        if artifact_id in seen_ids:
            continue
        seen_ids.add(artifact_id)
        existed = service.get_flow_artifact(artifact_id) is not None
        artifacts.append(
            ArtifactResult(
                artifact_id=artifact_id,
                artifact_ref=line.path,
                status_token=line.status,
                existed=existed,
            )
        )

    return ThreadResult(
        slug=slug,
        flow_instance_id=flow_instance_id,
        flow_status=flow_status,
        bridge_kind=bridge_kind,
        fingerprint=fingerprint,
        instance_action=instance_action,
        artifacts=tuple(artifacts),
    )


def _apply_thread(
    result: ThreadResult,
    service: TypedArtifactFlowService,
    *,
    changed_by: str,
    change_reason: str,
) -> None:
    """Apply one planned thread: append a flow_instance version + missing artifacts."""
    if result.instance_written:
        service.create_flow_instance(
            id=result.flow_instance_id,
            flow_definition_id=FLOW_DEFINITION_ID,
            subject_type=SUBJECT_TYPE,
            subject_id=result.slug,
            status=result.flow_status,
            metadata={
                "bridge_kind": result.bridge_kind,
                "ingest_fingerprint": result.fingerprint,
                "shadow": True,
                "source": "bridge_index_second_write",
            },
            changed_by=changed_by,
            change_reason=change_reason,
        )
    for artifact in result.artifacts:
        if artifact.existed:
            continue
        service.link_flow_artifact(
            id=artifact.artifact_id,
            flow_instance_id=result.flow_instance_id,
            artifact_type=ARTIFACT_TYPE,
            artifact_ref=artifact.artifact_ref,
            relationship=ARTIFACT_RELATIONSHIP,
            metadata={"status_token": artifact.status_token},
            changed_by=changed_by,
            change_reason=change_reason,
        )


def ingest_bridge_index(
    index_text: str,
    service: TypedArtifactFlowService,
    *,
    changed_by: str = "tafe-bridge-ingestion",
    change_reason: str = "TAFE Slice C bridge-thread second-write ingestion (shadow)",
    apply: bool = False,
) -> IngestionResult:
    """Ingest a canonical bridge-index snapshot into the TAFE shadow store.

    Parses ``index_text`` with the Slice A lossless parser, plans one
    ``flow-bridge-<slug>`` instance + per-version ``fa-bridge-<slug>-<NNN>``
    artifacts per thread (ADR D1/D2), derives ``flow_instances.status`` and
    ``metadata.bridge_kind`` (ADR D1/D3), and gates writes on the per-thread
    fingerprint (ADR D4). With ``apply=False`` (the default) it computes and
    returns the plan and writes nothing; with ``apply=True`` it performs the
    append-only writes. Threads with no version lines are skipped and reported.
    Never writes ``stage_instances`` or ``flow_events`` (Slice C scope).
    """
    parsed = parse_bridge_index(index_text)
    results: list[ThreadResult] = []
    skipped: list[str] = []

    for block in parsed.blocks:
        plan = _plan_thread(block, service)
        if plan is None:
            skipped.append(block.name)
            continue
        if apply:
            _apply_thread(plan, service, changed_by=changed_by, change_reason=change_reason)
        results.append(plan)

    return IngestionResult(
        applied=apply,
        threads_total=len(parsed.blocks),
        threads_skipped=skipped,
        results=results,
    )

"""TAFE Bridge-INDEX compatibility-view generator (WI-4507).

This module renders Typed Artifact-Flow Engine (TAFE) flow/stage state in the
visual shape of ``bridge/INDEX.md`` so operators can inspect how TAFE-tracked
workflows would look through the bridge view. The output is a **preview
artifact** only:

* It is **not** a substitute for ``bridge/INDEX.md``.
* It is **not** consumed by any agent's bridge scan.
* It does **not** participate in the workflow-state authority chain.

``bridge/INDEX.md`` remains the canonical workflow state per
``GOV-FILE-BRIDGE-AUTHORITY-001``; this module never writes it and exposes no
write surface at all. The first line of every rendered preview is a
load-bearing non-authoritative header (see ``NON_AUTHORITATIVE_HEADER``).

The renderer is a pure function: it performs no file I/O, no subprocess, no
MemBase mutation, and holds no reference to the canonical bridge index path. The
caller injects ``now`` so the rendered ``generated_at`` is deterministic.

Specification links: ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (renderable
parallel view), ``SPEC-TAFE-R7`` (MemBase canonical), ``SPEC-TAFE-R2`` /
``SPEC-TAFE-R4`` (stage-claim and required-role context surfaced read-only),
``GOV-FILE-BRIDGE-AUTHORITY-001`` (canonical INDEX preserved).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

NON_AUTHORITATIVE_HEADER = (
    "<!-- NON-AUTHORITATIVE: generated from TAFE state; "
    "the canonical bridge index remains authoritative per GOV-FILE-BRIDGE-AUTHORITY-001 -->"
)

__all__ = [
    "NON_AUTHORITATIVE_HEADER",
    "BridgeIndexPreview",
    "render_tafe_bridge_index_preview",
]


@dataclass(frozen=True)
class BridgeIndexPreview:
    """Immutable result of a TAFE compatibility-view render.

    ``authoritative`` is a fixed ``False`` constant: a preview is never a
    canonical workflow-state surface.
    """

    text: str
    flow_instance_count: int
    stage_instance_count: int
    generated_at: str
    authoritative: bool = False


def _coerce_now(now: str | datetime) -> datetime:
    """Coerce an injected timestamp to an aware UTC ``datetime``.

    Accepts a ``datetime`` (naive values are interpreted as UTC) or an ISO-8601
    string. The renderer is pure, so ``now`` is required and there is no
    wall-clock fallback.
    """

    if isinstance(now, datetime):
        return now if now.tzinfo is not None else now.replace(tzinfo=UTC)
    candidate = str(now).strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def render_tafe_bridge_index_preview(
    flow_instances: Sequence[Mapping[str, Any]],
    stage_instances: Sequence[Mapping[str, Any]],
    *,
    now: str | datetime,
) -> BridgeIndexPreview:
    """Render TAFE flow/stage state in the bridge-INDEX visual shape.

    One ``Document: <subject_id>`` block is emitted per flow instance, followed
    by one status line per joined stage instance ordered by descending
    ``stage_index``::

        <status>: <stage_id> (role=<required_role>, claim=<claim_status>)

    The first line of ``BridgeIndexPreview.text`` is always
    ``NON_AUTHORITATIVE_HEADER``. The function is pure and adds no policy logic;
    it only surfaces state the caller provides.
    """

    generated_at = _coerce_now(now).isoformat()

    stages_by_flow: dict[str, list[Mapping[str, Any]]] = {}
    for stage in stage_instances:
        stages_by_flow.setdefault(str(stage["flow_instance_id"]), []).append(stage)

    lines: list[str] = [NON_AUTHORITATIVE_HEADER]
    for flow in flow_instances:
        lines.append("")
        lines.append(f"Document: {flow['subject_id']}")
        joined = stages_by_flow.get(str(flow["id"]), [])
        ordered = sorted(joined, key=lambda stage: stage["stage_index"], reverse=True)
        for stage in ordered:
            lines.append(
                f"{stage['status']}: {stage['stage_id']} (role={stage['required_role']}, claim={stage['claim_status']})"
            )

    return BridgeIndexPreview(
        text="\n".join(lines),
        flow_instance_count=len(flow_instances),
        stage_instance_count=len(stage_instances),
        generated_at=generated_at,
    )

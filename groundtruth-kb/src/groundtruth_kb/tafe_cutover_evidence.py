"""Read-only TAFE cutover-evidence gathering (WI-4509, Phase-7 governed cutover).

WI-4509 collects the evidence the governed cutover (WI-4510, owner-AUQ-gated)
needs to decide whether the TAFE shadow store may become authoritative. With
Slice C (WI-4508) VERIFIED, the shadow is populated from ``bridge/INDEX.md`` via
:func:`groundtruth_kb.tafe_bridge_ingestion.ingest_bridge_index`
(``flow_instances`` + per-version ``flow_artifacts``). This module assesses that
shadow against the canonical INDEX across the four evidence categories WI-4509
names, and writes nothing:

* **parallel-run parity** — the deterministic INDEX→shadow *derivation* (the
  Slice C dry-run plan) reproduces one ``flow-bridge-<slug>`` instance per INDEX
  ``Document:`` block and one ``fa-bridge-<slug>-<NNN>`` artifact per INDEX
  version line, and the derived ``flow_status`` re-computes from the parsed INDEX
  (ADR D1/D2/D3). A block that derives no instance is a parity gap;
* **completeness** — the Slice B oracle's ``lost_blocks`` / ``extra_blocks`` diff
  between the canonical INDEX and the ``bridge/`` directory;
* **contention-zero (idempotence)** — re-planning over the current INDEX writes
  nothing (every thread ``unchanged``; ADR D4), i.e. the stored shadow's
  fingerprints are current;
* **compatibility-view fidelity** — the *stored* shadow rows reconstruct the
  INDEX latest-status: each thread's latest stored ``status_token`` and the
  stored instance ``status`` equal the INDEX latest version line's token and its
  derived flow status.

A fifth informational view, **flow completion rates**, tabulates the derived
``flow_status`` distribution the cutover proposal reports.

Read-only contract: the canonical ``bridge/INDEX.md`` remains the sole
authoritative workflow state per ``GOV-FILE-BRIDGE-AUTHORITY-001``. This module
receives ``index_text`` as a string (it holds **no canonical-index path
literal**), consumes the Slice C dry-run plan (``apply=False``) and the Slice B
oracle, reads the stored TAFE shadow tables, and performs no canonical write, no
shadow write, no MemBase mutation, and no subprocess. The read-only
``gt flow cutover-evidence`` CLI owns the guarded canonical-index read.

Specification links: ``ADR-TAFE-SLICE-C-INGESTION-001`` (the D1-D4 derivation this
evidence assesses), ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (the cutover is
the dual-write program's terminal step), ``GOV-FILE-BRIDGE-AUTHORITY-001``
(canonical INDEX preserved; read-only).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.tafe_bridge_ingestion import (
    derive_flow_status,
    ingest_bridge_index,
)
from groundtruth_kb.tafe_index_completeness import index_completeness_report
from groundtruth_kb.tafe_index_sync import DocumentBlock, IndexVersionLine, parse_bridge_index
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

__all__ = [
    "CompatibilityFidelitySection",
    "ContentionSection",
    "CutoverEvidenceReport",
    "ParitySection",
    "gather_cutover_evidence",
]

#: Trailing ``-NNN`` extractor for a ``bridge/<slug>-NNN.md`` artifact ref.
_VERSION_SUFFIX_RE = re.compile(r"-(\d+)\.md$")


def _latest_version_line(block: DocumentBlock) -> IndexVersionLine | None:
    """Return the highest-version version line (the thread's latest), or None."""
    if not block.version_lines:
        return None
    return max(block.version_lines, key=lambda line: line.version)


def _has_prior_go(block: DocumentBlock, latest: IndexVersionLine) -> bool:
    """True when a ``GO`` exists in the chain below the latest version line."""
    return any(line.status == "GO" and line.version < latest.version for line in block.version_lines)


def _distinct_version_suffixes(block: DocumentBlock) -> set[str]:
    """The distinct ``NNN`` suffixes for a block (one shadow artifact each)."""
    return {line.path.rsplit("/", 1)[-1].rsplit("-", 1)[-1].removesuffix(".md") for line in block.version_lines}


def _artifact_version(artifact: dict[str, Any]) -> int:
    """Extract the integer version from a stored artifact's ``artifact_ref``.

    Falls back to ``-1`` when the ref carries no recognizable ``-NNN.md`` suffix
    so a malformed stored row sorts below any well-formed one.
    """
    ref = artifact.get("artifact_ref") or ""
    match = _VERSION_SUFFIX_RE.search(str(ref))
    return int(match.group(1)) if match is not None else -1


def _artifact_status_token(artifact: dict[str, Any]) -> str | None:
    """Read the stored ``metadata.status_token`` from a flow-artifact row."""
    metadata = artifact.get("metadata_parsed")
    if isinstance(metadata, dict):
        token = metadata.get("status_token")
        return token if isinstance(token, str) else None
    return None


@dataclass(frozen=True)
class ParitySection:
    """Parallel-run parity of the INDEX->shadow derivation vs the parsed INDEX."""

    index_threads: int
    index_version_lines: int
    derived_instances: int
    derived_artifacts: int
    threads_skipped: tuple[str, ...]
    parity_mismatches: tuple[dict[str, Any], ...]

    @property
    def ok(self) -> bool:
        """True when the derivation has no skipped block and no structural gap."""
        return not self.parity_mismatches and not self.threads_skipped

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "index_threads": self.index_threads,
            "index_version_lines": self.index_version_lines,
            "derived_instances": self.derived_instances,
            "derived_artifacts": self.derived_artifacts,
            "threads_skipped": list(self.threads_skipped),
            "parity_mismatches": [dict(item) for item in self.parity_mismatches],
        }


@dataclass(frozen=True)
class ContentionSection:
    """Contention-zero idempotence: a re-plan over the current INDEX writes nothing."""

    action_distribution: dict[str, int]
    replan_instances_written: int
    replan_artifacts_written: int

    @property
    def contention_zero(self) -> bool:
        """True when re-planning the current INDEX would create/append nothing."""
        return self.replan_instances_written == 0 and self.replan_artifacts_written == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "contention_zero": self.contention_zero,
            "action_distribution": dict(self.action_distribution),
            "replan_instances_written": self.replan_instances_written,
            "replan_artifacts_written": self.replan_artifacts_written,
        }


@dataclass(frozen=True)
class CompatibilityFidelitySection:
    """Fidelity: the stored shadow reconstructs the INDEX latest-status."""

    threads_checked: int
    fidelity_mismatches: tuple[dict[str, Any], ...]

    @property
    def ok(self) -> bool:
        """True when every stored thread reconstructs its INDEX latest line."""
        return not self.fidelity_mismatches

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "threads_checked": self.threads_checked,
            "fidelity_mismatches": [dict(item) for item in self.fidelity_mismatches],
        }


@dataclass(frozen=True)
class CutoverEvidenceReport:
    """The full read-only cutover-evidence report for one ``index_text`` snapshot."""

    parity: ParitySection
    contention: ContentionSection
    fidelity: CompatibilityFidelitySection
    flow_completion: dict[str, int]
    lost_blocks: tuple[str, ...]
    extra_blocks: tuple[str, ...]
    present_count: int
    expected_count: int

    @property
    def ok(self) -> bool:
        """True only when every gating evidence category is clean for cutover.

        Cutover evidence is GO-shaped when the derivation is lossless (parity),
        the shadow is current (contention-zero), the shadow reconstructs the
        INDEX (fidelity), and the INDEX/disk views agree (no lost/extra blocks).
        ``flow_completion`` is informational and does not gate ``ok``.
        """
        return (
            self.parity.ok
            and self.contention.contention_zero
            and self.fidelity.ok
            and not self.lost_blocks
            and not self.extra_blocks
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "parity": self.parity.as_dict(),
            "contention": self.contention.as_dict(),
            "fidelity": self.fidelity.as_dict(),
            "flow_completion": dict(self.flow_completion),
            "completeness": {
                "lost_blocks": list(self.lost_blocks),
                "extra_blocks": list(self.extra_blocks),
                "present_count": self.present_count,
                "expected_count": self.expected_count,
            },
        }


def _gather_parity(parsed_blocks: tuple[DocumentBlock, ...], plan: Any) -> ParitySection:
    """Compare the dry-run plan's derivation against the independently-parsed INDEX."""
    plan_by_slug = {result.slug: result for result in plan.results}
    index_version_lines = sum(len(block.version_lines) for block in parsed_blocks)
    derived_artifacts = sum(len(result.artifacts) for result in plan.results)

    mismatches: list[dict[str, Any]] = []
    for block in parsed_blocks:
        latest = _latest_version_line(block)
        if latest is None:
            # A Document block with no version lines derives no shadow instance;
            # the plan reports it as skipped. It is a parity gap for cutover.
            mismatches.append({"slug": block.name, "kind": "no_version_lines"})
            continue
        result = plan_by_slug.get(block.name)
        if result is None:
            mismatches.append({"slug": block.name, "kind": "no_derived_instance"})
            continue
        expected_artifacts = len(_distinct_version_suffixes(block))
        if len(result.artifacts) != expected_artifacts:
            mismatches.append(
                {
                    "slug": block.name,
                    "kind": "artifact_count_mismatch",
                    "index_artifacts": expected_artifacts,
                    "derived_artifacts": len(result.artifacts),
                }
            )
        expected_status = derive_flow_status(latest.status, has_prior_go=_has_prior_go(block, latest))
        if result.flow_status != expected_status:
            mismatches.append(
                {
                    "slug": block.name,
                    "kind": "flow_status_mismatch",
                    "index_derived": expected_status,
                    "plan_derived": result.flow_status,
                }
            )

    return ParitySection(
        index_threads=len(parsed_blocks),
        index_version_lines=index_version_lines,
        derived_instances=len(plan.results),
        derived_artifacts=derived_artifacts,
        threads_skipped=tuple(plan.threads_skipped),
        parity_mismatches=tuple(mismatches),
    )


def _gather_fidelity(
    parsed_blocks: tuple[DocumentBlock, ...],
    service: TypedArtifactFlowService,
) -> CompatibilityFidelitySection:
    """Compare the stored shadow's latest-status reconstruction against the INDEX."""
    mismatches: list[dict[str, Any]] = []
    checked = 0
    for block in parsed_blocks:
        latest = _latest_version_line(block)
        if latest is None:
            continue
        checked += 1
        flow_instance_id = f"flow-bridge-{block.name}"
        instance = service.get_flow_instance(flow_instance_id)
        if instance is None:
            mismatches.append({"slug": block.name, "kind": "shadow_instance_missing"})
            continue

        expected_status = derive_flow_status(latest.status, has_prior_go=_has_prior_go(block, latest))
        if instance.get("status") != expected_status:
            mismatches.append(
                {
                    "slug": block.name,
                    "kind": "instance_status_mismatch",
                    "index_latest_status": expected_status,
                    "shadow_status": instance.get("status"),
                }
            )

        artifacts = service.list_flow_artifacts(flow_instance_id=flow_instance_id)
        if not artifacts:
            mismatches.append({"slug": block.name, "kind": "shadow_artifacts_missing"})
            continue
        latest_artifact = max(artifacts, key=_artifact_version)
        stored_token = _artifact_status_token(latest_artifact)
        if stored_token != latest.status:
            mismatches.append(
                {
                    "slug": block.name,
                    "kind": "latest_status_token_mismatch",
                    "index_latest_token": latest.status,
                    "shadow_latest_token": stored_token,
                }
            )

    return CompatibilityFidelitySection(threads_checked=checked, fidelity_mismatches=tuple(mismatches))


def gather_cutover_evidence(
    index_text: str,
    service: TypedArtifactFlowService,
    *,
    project_root: Path,
) -> CutoverEvidenceReport:
    """Assemble the read-only TAFE cutover-evidence report for an INDEX snapshot.

    Parses ``index_text`` (Slice A parser), computes the Slice C dry-run plan
    (``apply=False``; writes nothing), runs the Slice B completeness oracle over
    ``project_root``, and reads the stored TAFE shadow. Returns the four-category
    evidence report (plus the informational flow-completion distribution). The
    canonical INDEX is never written and no shadow/MemBase row is mutated; the
    function only reads ``service`` state.
    """
    parsed = parse_bridge_index(index_text)
    plan = ingest_bridge_index(index_text, service, apply=False)
    completeness = index_completeness_report(index_text, project_root)

    parity = _gather_parity(parsed.blocks, plan)
    contention = ContentionSection(
        action_distribution=dict(Counter(result.instance_action for result in plan.results)),
        replan_instances_written=plan.instances_written,
        replan_artifacts_written=plan.artifacts_written,
    )
    fidelity = _gather_fidelity(parsed.blocks, service)
    flow_completion = dict(Counter(result.flow_status for result in plan.results))

    return CutoverEvidenceReport(
        parity=parity,
        contention=contention,
        fidelity=fidelity,
        flow_completion=flow_completion,
        lost_blocks=completeness.lost_blocks,
        extra_blocks=completeness.extra_blocks,
        present_count=len(completeness.present_slugs),
        expected_count=len(completeness.expected_slugs),
    )

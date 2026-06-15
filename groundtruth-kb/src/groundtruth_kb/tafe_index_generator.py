"""Byte-faithful ``flow_artifacts`` -> ``bridge/INDEX.md`` generator (WI-4510,
Phase 1; governed by ``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001``).

This module is the prerequisite the authoritative-bridge-state cutover needs: a
generator that reconstructs the canonical ``bridge/INDEX.md`` *version-line
history* from the TAFE shadow store's ``flow_instances`` + ``flow_artifacts``
rows (the rows Slice C wrote per ``ADR-TAFE-SLICE-C-INGESTION-001``). It is the
authoritative complement of the explicitly non-authoritative WI-4507 preview
(:mod:`groundtruth_kb.tafe_index_preview`), which renders from ``stage_instances``
that are *not written for bridge threads* and is therefore unusable for cutover.

What "byte-faithful" means here (and why a *structural* contract, not a literal
byte contract, is the gating invariant): the shadow rows preserve only the
``(status_token, artifact_ref)`` of every INDEX version line — they do **not**
capture per-line terminators, intra-line whitespace, document-block insertion
order, or any header/footer prose. So a render of the shadow reproduces the
INDEX's *semantic* content (the ordered set of ``Document`` blocks and their
``<STATUS>: bridge/<slug>-NNN.md`` version lines) exactly, while differences in
line terminator (the live INDEX mixes ``\\n`` and ``\\r\\n``), document-block
ordering, or non-version footer prose are the **one-time, owner-visible reformat**
the flip would apply once — surfaced for the WI-4510 gate-2 decision, never
applied silently (per the ADR's phased rollout). :func:`verify_against_index`
draws exactly this line: a status-token / path / lost-thread / extra-thread
difference is a *semantic* divergence (gate-failing); a terminator / ordering /
footer difference is a *reformat-only* difference (informational).

Read-only / pure contract: this module performs **no file I/O, no subprocess, no
MemBase mutation**, and holds **no canonical-index path literal**. It receives
``flow_instances`` / ``flow_artifacts`` as injected sequences and ``index_text``
as a string. The canonical ``bridge/INDEX.md`` remains the authoritative
workflow state per ``GOV-FILE-BRIDGE-AUTHORITY-001`` for the entire Phase-0/1/2
scope of WI-4510; this module never writes it. The read-only
``gt flow regen-verify`` CLI owns the guarded canonical-index read.

Specification links: ``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`` (generator
contract + round-trip fidelity criterion + phased reversible rollout),
``ADR-TAFE-SLICE-C-INGESTION-001`` (the ``fa-bridge-<slug>-<NNN>`` /
``metadata.status_token`` / ``artifact_ref`` derivation reconstructed here),
``DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`` (terminal-archived threads are
legitimately absent; the generator reproduces INDEX as it is, never re-emitting
trimmed threads), ``GOV-FILE-BRIDGE-AUTHORITY-001`` (canonical INDEX preserved;
no write surface), ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` (the authoritative
generated view is the umbrella program's cutover deliverable).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from groundtruth_kb.tafe_bridge_ingestion import ARTIFACT_TYPE, SUBJECT_TYPE
from groundtruth_kb.tafe_index_sync import parse_bridge_index

__all__ = [
    "RegenVerifyResult",
    "render_index_from_flow_artifacts",
    "verify_against_index",
]

#: The canonical line terminator the generated INDEX uses. The live INDEX may
#: mix terminators; normalizing to ``\n`` is part of the one-time reformat.
_NEWLINE = "\n"

#: Trailing ``-NNN`` extractor for a ``bridge/<slug>-NNN.md`` artifact ref
#: (mirrors the ingestion/cutover-evidence version extractor).
_VERSION_SUFFIX_RE = re.compile(r"-(\d+)\.md$")


def _artifact_version(artifact: Mapping[str, Any]) -> int:
    """Extract the integer version from a stored artifact's ``artifact_ref``.

    Falls back to ``-1`` when the ref carries no recognizable ``-NNN.md`` suffix
    so a malformed stored row sorts below any well-formed one (matching the
    cutover-evidence convention).
    """
    ref = artifact.get("artifact_ref") or ""
    match = _VERSION_SUFFIX_RE.search(str(ref))
    return int(match.group(1)) if match is not None else -1


def _artifact_status_token(artifact: Mapping[str, Any]) -> str | None:
    """Read the stored ``metadata.status_token`` from a flow-artifact row."""
    metadata = artifact.get("metadata_parsed")
    if isinstance(metadata, dict):
        token = metadata.get("status_token")
        return token if isinstance(token, str) else None
    return None


def render_index_from_flow_artifacts(
    flow_instances: Sequence[Mapping[str, Any]],
    flow_artifacts: Sequence[Mapping[str, Any]],
    *,
    header: str = "",
) -> str:
    """Render canonical ``bridge/INDEX.md`` text from TAFE shadow rows.

    For each ``bridge_thread`` flow instance (in the order given by
    ``flow_instances`` — the caller owns document-block ordering), emits a
    ``Document: <subject_id>`` line followed by its ``bridge_version`` artifacts as
    ``<status_token>: <artifact_ref>`` version lines, newest-first by version, then
    a single blank separator line. ``header`` (e.g. the captured INDEX preamble) is
    prepended verbatim. The function is pure: it reads only the injected sequences,
    writes nothing, and runs no subprocess.

    Instances whose ``subject_type`` is not ``bridge_thread`` are ignored. An
    artifact is rendered only when it is a ``bridge_version`` row carrying both a
    ``status_token`` and an ``artifact_ref``; duplicate versions (same ``-NNN``)
    collapse to one line, matching the ingestion's per-version dedup.
    """
    artifacts_by_instance: dict[str, list[Mapping[str, Any]]] = {}
    for artifact in flow_artifacts:
        if artifact.get("artifact_type") != ARTIFACT_TYPE:
            continue
        instance_id = artifact.get("flow_instance_id")
        if instance_id is None:
            continue
        artifacts_by_instance.setdefault(str(instance_id), []).append(artifact)

    parts: list[str] = []
    if header:
        parts.append(header)

    for instance in flow_instances:
        if instance.get("subject_type") != SUBJECT_TYPE:
            continue
        slug = instance.get("subject_id")
        if not slug:
            continue
        instance_id = str(instance.get("id"))

        block: list[str] = [f"Document: {slug}{_NEWLINE}"]
        seen_versions: set[int] = set()
        for artifact in sorted(artifacts_by_instance.get(instance_id, []), key=_artifact_version, reverse=True):
            version = _artifact_version(artifact)
            if version in seen_versions:
                continue
            token = _artifact_status_token(artifact)
            ref = artifact.get("artifact_ref")
            if token is None or not ref:
                continue
            seen_versions.add(version)
            block.append(f"{token}: {ref}{_NEWLINE}")
        block.append(_NEWLINE)  # one blank separator line after each block
        parts.append("".join(block))

    return "".join(parts)


def _semantic_blocks(index_text: str) -> list[tuple[str, tuple[tuple[int, str, str], ...]]]:
    """Reduce INDEX text to its semantic content: ordered ``(name, version-lines)``.

    Only document blocks that carry at least one version line are included (a
    block with no version lines derives no shadow instance and is reported
    separately, mirroring the ingestion's skip semantics). Each block's version
    lines are normalized to a sorted tuple of ``(version, status, path)`` so the
    comparison is independent of source line ordering and whitespace.
    """
    parsed = parse_bridge_index(index_text)
    blocks: list[tuple[str, tuple[tuple[int, str, str], ...]]] = []
    for block in parsed.blocks:
        if not block.version_lines:
            continue
        version_lines = tuple(sorted((line.version, line.status, line.path) for line in block.version_lines))
        blocks.append((block.name, version_lines))
    return blocks


def _blocks_without_versions(index_text: str) -> tuple[str, ...]:
    """Document-block names in ``index_text`` that carry no version line."""
    parsed = parse_bridge_index(index_text)
    return tuple(block.name for block in parsed.blocks if not block.version_lines)


@dataclass(frozen=True)
class RegenVerifyResult:
    """The verdict of regenerating the INDEX from shadow rows and comparing it.

    ``semantic_equal`` is the gating contract: the generated and canonical INDEX
    carry the same set of document blocks with the same version lines (status
    token + path). ``byte_identical`` is the strict literal contract (achievable
    only when the canonical INDEX is already in canonical form). When
    ``semantic_equal`` holds but ``byte_identical`` does not, the residual
    differences (line terminators, document-block ordering, non-version footer
    prose) are the one-time owner-visible reformat surfaced for gate-2.
    """

    byte_identical: bool
    semantic_equal: bool
    index_document_count: int
    generated_document_count: int
    missing_in_generated: tuple[str, ...]
    extra_in_generated: tuple[str, ...]
    version_line_mismatches: tuple[dict[str, Any], ...]
    ordering_differs: bool
    index_blocks_without_versions: tuple[str, ...]
    # WI-4510 Refined-Option-B partition of ``extra_in_generated`` (shadow threads
    # absent from the live INDEX). The TAFE shadow is append-only, so it retains
    # threads the protocol legitimately trimmed from the INDEX. ``extra_archived``
    # are extras classified terminal-archived by the shared on-disk oracle
    # (``tafe_index_completeness._candidate_is_archived`` rules 1->2->3); these are
    # informational and DO NOT gate (mirroring ``IndexCompletenessReport.archived_blocks``).
    # ``extra_divergent`` are the remaining extras (phantoms / non-terminal shadow
    # rows that SHOULD NOT be in the shadow) and DO gate. ``extra_in_generated``
    # remains the FULL extra set for transparency (the shadow IS a superset).
    extra_archived_in_generated: tuple[str, ...] = ()
    extra_divergent_in_generated: tuple[str, ...] = ()

    @property
    def status(self) -> str:
        """Coarse verdict: ``divergent`` / ``byte_identical`` / ``reformat_only``."""
        if not self.semantic_equal:
            return "divergent"
        return "byte_identical" if self.byte_identical else "reformat_only"

    @property
    def ok(self) -> bool:
        """True when the generated INDEX is semantically equal to the canonical one.

        A ``reformat_only`` difference is OK (it is the documented one-time
        reformat); only a ``divergent`` result — a lost/extra thread or a changed
        status token / path — gates the result False.
        """
        return self.semantic_equal

    def as_dict(self) -> dict[str, Any]:
        """A JSON-serializable view of the verdict."""
        return {
            "ok": self.ok,
            "status": self.status,
            "byte_identical": self.byte_identical,
            "semantic_equal": self.semantic_equal,
            "index_document_count": self.index_document_count,
            "generated_document_count": self.generated_document_count,
            "missing_in_generated": list(self.missing_in_generated),
            "extra_in_generated": list(self.extra_in_generated),
            "extra_archived_in_generated": list(self.extra_archived_in_generated),
            "extra_divergent_in_generated": list(self.extra_divergent_in_generated),
            "version_line_mismatches": [dict(item) for item in self.version_line_mismatches],
            "ordering_differs": self.ordering_differs,
            "index_blocks_without_versions": list(self.index_blocks_without_versions),
        }


def verify_against_index(
    index_text: str,
    flow_instances: Sequence[Mapping[str, Any]],
    flow_artifacts: Sequence[Mapping[str, Any]],
    *,
    header: str = "",
    is_archived_extra: Callable[[str], bool] | None = None,
) -> RegenVerifyResult:
    """Regenerate the INDEX from shadow rows and compare it to the canonical text.

    Renders ``flow_instances`` / ``flow_artifacts`` via
    :func:`render_index_from_flow_artifacts`, then compares the regenerated text
    to ``index_text`` both literally (byte-identity) and structurally (same
    document blocks, same version lines). The structural comparison is the gating
    contract; the literal comparison surfaces the one-time reformat. Pure: no I/O,
    no subprocess, no mutation.

    WI-4510 Refined Option B -- extra-thread partition. The append-only TAFE shadow
    retains threads the bridge protocol legitimately trimmed from the live INDEX, so
    ``generated - index`` (``extra``) is expected to be non-empty in steady state.
    ``is_archived_extra`` is dependency-injected to keep this module pure (the CLI
    wires in ``tafe_index_completeness._candidate_is_archived``); for each extra it
    returns ``True`` => legitimate terminal-archived residue
    (``extra_archived_in_generated``, informational, ungated, mirroring
    ``IndexCompletenessReport.archived_blocks``); ``False`` => divergent
    (``extra_divergent_in_generated``: a phantom or non-terminal shadow row that
    gates). ``semantic_equal`` is therefore ``not missing and not extra_divergent and
    not mismatches``. When ``is_archived_extra is None`` the fail-safe fallback gates
    ALL extras (every extra is divergent) so no caller can silently weaken the gate.
    ``extra_in_generated`` always reports the full extra set for transparency.
    """
    generated_text = render_index_from_flow_artifacts(flow_instances, flow_artifacts, header=header)
    byte_identical = generated_text == index_text

    index_blocks = _semantic_blocks(index_text)
    generated_blocks = _semantic_blocks(generated_text)
    index_map = dict(index_blocks)
    generated_map = dict(generated_blocks)

    missing = tuple(sorted(set(index_map) - set(generated_map)))
    extra = tuple(sorted(set(generated_map) - set(index_map)))
    extra_archived = tuple(slug for slug in extra if is_archived_extra(slug)) if is_archived_extra is not None else ()
    archived_set = set(extra_archived)
    extra_divergent = tuple(slug for slug in extra if slug not in archived_set)

    mismatches: list[dict[str, Any]] = []
    for name in sorted(set(index_map) & set(generated_map)):
        if index_map[name] != generated_map[name]:
            mismatches.append(
                {
                    "slug": name,
                    "index_version_lines": [list(item) for item in index_map[name]],
                    "generated_version_lines": [list(item) for item in generated_map[name]],
                }
            )

    semantic_equal = not missing and not extra_divergent and not mismatches

    shared = set(index_map) & set(generated_map)
    index_order = [name for name, _ in index_blocks if name in shared]
    generated_order = [name for name, _ in generated_blocks if name in shared]
    ordering_differs = index_order != generated_order

    return RegenVerifyResult(
        byte_identical=byte_identical,
        semantic_equal=semantic_equal,
        index_document_count=len(index_blocks),
        generated_document_count=len(generated_blocks),
        missing_in_generated=missing,
        extra_in_generated=extra,
        version_line_mismatches=tuple(mismatches),
        ordering_differs=ordering_differs,
        index_blocks_without_versions=_blocks_without_versions(index_text),
        extra_archived_in_generated=extra_archived,
        extra_divergent_in_generated=extra_divergent,
    )

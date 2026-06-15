"""Spec-derived tests for the byte-faithful TAFE INDEX generator (WI-4510 Phase 1).

Each test derives from a clause of ``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`` (the
generator contract + round-trip fidelity criterion + phased reversible rollout) and
the Slice-C derivation it reconstructs (``ADR-TAFE-SLICE-C-INGESTION-001``):

* round-trip byte-fidelity — ingest a canonical INDEX, regenerate from the shadow
  rows in INDEX order, and reproduce the canonical text byte-for-byte;
* multi-version reconstruction — every ``fa-bridge-<slug>-<NNN>`` re-emits its
  version line, newest-first;
* token coverage — ADVISORY / DEFERRED / WITHDRAWN / NO-GO tokens round-trip;
* terminal-archived trimming — the generator reproduces the INDEX as it is and
  never re-emits a thread absent from it (``DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001``);
* document-block ordering — the caller owns ordering; the generator renders in the
  order given;
* reformat-vs-divergent — a terminator/ordering/footer difference is reformat-only
  (semantic_equal); a changed token / lost thread / extra thread is divergent;
* read-only contract — the generator performs no file/DB write and no subprocess
  (``GOV-FILE-BRIDGE-AUTHORITY-001``).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import ast
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_bridge_ingestion import ingest_bridge_index
from groundtruth_kb.tafe_index_generator import (
    render_index_from_flow_artifacts,
    verify_against_index,
)
from groundtruth_kb.tafe_index_sync import parse_bridge_index
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

_HEADER = "# Bridge INDEX\n\n"


def _index(*blocks: tuple[str, list[tuple[str, int]]]) -> str:
    """Build canonical ``bridge/INDEX.md`` text from (slug, [(status, version)])."""
    parts = [_HEADER]
    for slug, lines in blocks:
        parts.append(f"Document: {slug}\n")
        for status, version in lines:
            parts.append(f"{status}: bridge/{slug}-{version:03d}.md\n")
        parts.append("\n")
    return "".join(parts)


def _service(tmp_path: Path) -> tuple[KnowledgeDB, TypedArtifactFlowService]:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    service = TypedArtifactFlowService(db)
    service.seed_reviewed_task_flow_definitions(changed_by="test", change_reason="seed for generator test")
    return db, service


def _instances_in_index_order(service: TypedArtifactFlowService, index_text: str) -> list[dict]:
    """Return shadow instances ordered to match the INDEX document-block order.

    The generator is pure and renders in the order given; the round-trip byte
    contract is therefore expressed by supplying instances in INDEX order (the
    caller owns ordering, per the generator contract).
    """
    order = [block.name for block in parse_bridge_index(index_text).blocks]
    by_slug = {inst["subject_id"]: inst for inst in service.list_flow_instances()}
    return [by_slug[name] for name in order if name in by_slug]


# --- Round-trip byte-fidelity (ADR Phase-1 exit criterion) ---------------------


def test_roundtrip_is_byte_identical_in_index_order(tmp_path: Path) -> None:
    index_text = _index(
        ("alpha-thread", [("GO", 2), ("NEW", 1)]),
        ("beta-thread", [("VERIFIED", 3), ("NEW", 2), ("NEW", 1)]),
        ("gamma-thread", [("NO-GO", 1)]),
    )
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(index_text, service, apply=True)
        instances = _instances_in_index_order(service, index_text)
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        generated = render_index_from_flow_artifacts(
            instances, artifacts, header="".join(parse_bridge_index(index_text).preamble_raw)
        )
    finally:
        db.close()
    assert generated == index_text


def test_multi_version_thread_reconstructs_newest_first(tmp_path: Path) -> None:
    index_text = _index(("multi", [("VERIFIED", 4), ("NEW", 3), ("GO", 2), ("NEW", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(index_text, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        generated = render_index_from_flow_artifacts(instances, artifacts, header=_HEADER)
    finally:
        db.close()
    body = generated[len(_HEADER) :]
    assert body == (
        "Document: multi\n"
        "VERIFIED: bridge/multi-004.md\n"
        "NEW: bridge/multi-003.md\n"
        "GO: bridge/multi-002.md\n"
        "NEW: bridge/multi-001.md\n"
        "\n"
    )


def test_advisory_deferred_withdrawn_tokens_round_trip(tmp_path: Path) -> None:
    index_text = _index(
        ("adv", [("ADVISORY", 1)]),
        ("def", [("DEFERRED", 2), ("NEW", 1)]),
        ("wd", [("WITHDRAWN", 2), ("NEW", 1)]),
    )
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(index_text, service, apply=True)
        instances = _instances_in_index_order(service, index_text)
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        verdict = verify_against_index(
            index_text, instances, artifacts, header="".join(parse_bridge_index(index_text).preamble_raw)
        )
    finally:
        db.close()
    assert verdict.semantic_equal
    assert verdict.byte_identical
    assert verdict.status == "byte_identical"


# --- Terminal-archived trimming (DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001) ---


def test_generator_never_emits_a_thread_absent_from_index(tmp_path: Path) -> None:
    # The shadow is populated from one INDEX; the generated set must equal the
    # ingested set. A thread trimmed from INDEX (terminal-archived) is simply not
    # in the shadow and therefore not generated.
    index_text = _index(("present-one", [("GO", 1)]), ("present-two", [("NEW", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(index_text, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        generated = render_index_from_flow_artifacts(instances, artifacts, header=_HEADER)
    finally:
        db.close()
    generated_docs = {block.name for block in parse_bridge_index(generated).blocks}
    assert generated_docs == {"present-one", "present-two"}
    assert "terminal-archived-ghost" not in generated_docs


# --- Document-block ordering: the caller owns it -------------------------------


def test_generator_renders_in_the_order_given(tmp_path: Path) -> None:
    index_text = _index(("aaa", [("NEW", 1)]), ("bbb", [("NEW", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(index_text, service, apply=True)
        by_slug = {inst["subject_id"]: inst for inst in service.list_flow_instances()}
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        reversed_order = [by_slug["bbb"], by_slug["aaa"]]
        generated = render_index_from_flow_artifacts(reversed_order, artifacts, header=_HEADER)
    finally:
        db.close()
    docs = [block.name for block in parse_bridge_index(generated).blocks]
    assert docs == ["bbb", "aaa"]


# --- reformat-only vs divergent (the gating distinction) -----------------------


def test_mixed_terminators_and_footer_are_reformat_only(tmp_path: Path) -> None:
    canonical = _index(("alpha", [("GO", 2), ("NEW", 1)]), ("beta", [("NEW", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(canonical, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        # Construct a live-like variant: CRLF terminators + a trailing footer
        # comment (the kind that accumulates in the hand-maintained INDEX).
        live_like = canonical.replace("\n", "\r\n") + "<!-- footer note -->\r\n"
        verdict = verify_against_index(live_like, instances, artifacts, header="")
    finally:
        db.close()
    assert verdict.semantic_equal is True
    assert verdict.byte_identical is False
    assert verdict.status == "reformat_only"
    assert verdict.ok is True


def test_changed_status_token_is_divergent(tmp_path: Path) -> None:
    canonical = _index(("alpha", [("GO", 2), ("NEW", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(canonical, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        # The canonical INDEX now claims the latest is NO-GO, but the shadow has GO.
        diverged = _index(("alpha", [("NO-GO", 2), ("NEW", 1)]))
        verdict = verify_against_index(diverged, instances, artifacts, header=_HEADER)
    finally:
        db.close()
    assert verdict.semantic_equal is False
    assert verdict.status == "divergent"
    assert verdict.version_line_mismatches
    assert verdict.version_line_mismatches[0]["slug"] == "alpha"


def test_lost_and_extra_threads_are_divergent(tmp_path: Path) -> None:
    canonical = _index(("only-in-shadow", [("GO", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(canonical, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        # INDEX has a thread the shadow lacks (lost) and lacks one the shadow has (extra).
        index_with_other = _index(("only-in-index", [("NEW", 1)]))
        verdict = verify_against_index(index_with_other, instances, artifacts, header=_HEADER)
    finally:
        db.close()
    assert verdict.semantic_equal is False
    assert verdict.missing_in_generated == ("only-in-index",)
    assert verdict.extra_in_generated == ("only-in-shadow",)


def test_blocks_without_version_lines_are_reported_not_failed(tmp_path: Path) -> None:
    # A Document block with no version lines derives no shadow instance; it must
    # be reported informationally, not treated as a lost thread.
    index_text = _HEADER + "Document: empty-block\n\nDocument: real\nNEW: bridge/real-001.md\n\n"
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(index_text, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
        verdict = verify_against_index(index_text, instances, artifacts, header=_HEADER)
    finally:
        db.close()
    assert "empty-block" in verdict.index_blocks_without_versions
    assert "empty-block" not in verdict.missing_in_generated
    assert verdict.semantic_equal is True


# --- WI-4510 Refined Option B: extra-thread partition --------------------------
# The append-only shadow retains threads the protocol trimmed from the live INDEX,
# so ``generated - index`` is non-empty in steady state. ``is_archived_extra``
# (dependency-injected; the CLI wires in tafe_index_completeness._candidate_is_archived)
# partitions extras into legitimate terminal-archived residue (ungated) vs phantom /
# non-terminal shadow rows (gating). Derives from
# DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001 + ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001.


def _shadow_with_extra(tmp_path: Path) -> tuple[list[dict], list[dict], str]:
    """Seed a shadow with 'kept' + 'extra-thread'; return (instances, artifacts, index-without-extra).

    Verifying the seeded shadow against an INDEX that omits 'extra-thread' makes
    'extra-thread' an ``extra_in_generated`` (in shadow, absent from the live INDEX).
    """
    seed_index = _index(("kept", [("NEW", 1)]), ("extra-thread", [("GO", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(seed_index, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
    finally:
        db.close()
    index_without_extra = _index(("kept", [("NEW", 1)]))
    return instances, artifacts, index_without_extra


def test_verify_terminal_archived_extra_is_non_gating(tmp_path: Path) -> None:
    instances, artifacts, index_text = _shadow_with_extra(tmp_path)
    verdict = verify_against_index(
        index_text, instances, artifacts, header=_HEADER, is_archived_extra=lambda slug: slug == "extra-thread"
    )
    assert verdict.ok is True
    assert verdict.status in {"byte_identical", "reformat_only"}
    assert verdict.extra_archived_in_generated == ("extra-thread",)
    assert verdict.extra_divergent_in_generated == ()
    # full-set transparency: the shadow IS a superset, so the extra still appears here.
    assert "extra-thread" in verdict.extra_in_generated


def test_verify_phantom_extra_gates(tmp_path: Path) -> None:
    # The central must-still-gate case: an extra the oracle does NOT classify archived
    # (a phantom / non-terminal shadow row) gates. Proves refined-B is not naive-B.
    instances, artifacts, index_text = _shadow_with_extra(tmp_path)
    verdict = verify_against_index(
        index_text, instances, artifacts, header=_HEADER, is_archived_extra=lambda slug: False
    )
    assert verdict.ok is False
    assert verdict.status == "divergent"
    assert verdict.extra_divergent_in_generated == ("extra-thread",)
    assert verdict.extra_archived_in_generated == ()


def test_verify_extra_partition_default_gates_all(tmp_path: Path) -> None:
    # Fail-safe fallback: with no classifier, every extra gates (no silent weakening).
    instances, artifacts, index_text = _shadow_with_extra(tmp_path)
    verdict = verify_against_index(index_text, instances, artifacts, header=_HEADER)
    assert verdict.ok is False
    assert verdict.extra_divergent_in_generated == ("extra-thread",)
    assert verdict.extra_archived_in_generated == ()


def test_verify_version_mismatch_still_gates_with_archived_extra_present(tmp_path: Path) -> None:
    # A genuine in-present-set mismatch still gates even while an archived extra is tolerated.
    seed_index = _index(("kept", [("GO", 2), ("NEW", 1)]), ("extra-thread", [("GO", 1)]))
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(seed_index, service, apply=True)
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type="bridge_version")
    finally:
        db.close()
    index_text = _index(("kept", [("NO-GO", 2), ("NEW", 1)]))  # changed token; extra-thread absent
    verdict = verify_against_index(
        index_text, instances, artifacts, header=_HEADER, is_archived_extra=lambda slug: slug == "extra-thread"
    )
    assert verdict.ok is False
    assert verdict.version_line_mismatches
    assert verdict.extra_archived_in_generated == ("extra-thread",)
    assert verdict.extra_divergent_in_generated == ()


def test_verify_missing_thread_still_gates_with_partition(tmp_path: Path) -> None:
    # The partition only touches extras; the lost-thread (missing) direction still gates,
    # even with a tolerate-everything classifier.
    instances, artifacts, _ = _shadow_with_extra(tmp_path)
    index_text = _index(("kept", [("NEW", 1)]), ("only-in-index", [("NEW", 1)]))
    verdict = verify_against_index(
        index_text, instances, artifacts, header=_HEADER, is_archived_extra=lambda slug: True
    )
    assert verdict.ok is False
    assert verdict.missing_in_generated == ("only-in-index",)


# --- Read-only contract (GOV-FILE-BRIDGE-AUTHORITY-001) ------------------------


def test_generator_module_performs_no_write_or_subprocess() -> None:
    """AST assertion: the generator imports/calls no write, mutation, or subprocess.

    The byte-faithful generator must be a pure function of injected rows so it can
    never write the canonical INDEX or mutate the shadow during a Phase-0/1/2
    verification cycle.
    """
    import groundtruth_kb.tafe_index_generator as generator_module

    source = Path(generator_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_imports = {"subprocess", "shutil", "os", "pathlib"}
    forbidden_call_names = {"open"}
    forbidden_attr_calls = {
        "write_text",
        "write_bytes",
        "mkdir",
        "unlink",
        "remove",
        "system",
        "popen",
        "run",
        "create_flow_instance",
        "link_flow_artifact",
        "insert_flow_instance",
        "insert_flow_artifact",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in forbidden_imports, f"forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root not in forbidden_imports, f"forbidden import-from: {node.module}"
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                assert func.id not in forbidden_call_names, f"forbidden call: {func.id}"
            elif isinstance(func, ast.Attribute):
                assert func.attr not in forbidden_attr_calls, f"forbidden attribute call: {func.attr}"

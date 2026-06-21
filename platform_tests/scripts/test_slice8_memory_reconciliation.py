# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slice 8 (WI-4346/WI-4347) verification guard.

Pins the MEMORY.md + topic-file reconciliation of
``PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION`` so it cannot silently regress:

- WI-4347 (retire): the 51 classifier RETIRE-bucket ephemera files are absent.
- WI-4347 (preserve) + GOV-08: the PRESERVE anchors still exist.
- WI-4346: ``memory/MEMORY.md`` is an index-only operational notepad
  (index headings present, bulky session-state log removed, under an
  index-size threshold) per GOV-SOURCE-OF-TRUTH-FRESHNESS-001 +
  GOV-STANDING-BACKLOG-001 (no backlog/content store in MEMORY.md).

Source: ``bridge/gtkb-platform-sot-consolidation-slice-8-memory-reconciliation-001.md``
(GO at ``-002``); owner authorization ``DELIB-20265460``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEMORY = ROOT / "memory" / "MEMORY.md"

# WI-4347 RETIRE bucket — the 51 clear-ephemera files deleted by Slice 8.
RETIRED = [
    "memory/SESSION-HANDOFF-2026-06-19-production-readiness-roadmap.md",
    "memory/canonical-terminology-md-new-section.md",
    "memory/canonical-terminology-md-rewrite-preview.md",
    "memory/codex-review-gate-md-rewrite-preview.md",
    "memory/dispatched-2026-06-11-fab01-step4-5-completed.md",
    "memory/dispatched-2026-06-11-fab04-fab01-stand-down.md",
    "memory/dispatched-2026-06-11T20Z-fab01-fab03-stand-down.md",
    "memory/dispatched-2026-06-11T20Z-fab04-git-reclamation-executed.md",
    "memory/dispatched-789f0e-wi4522-author-metadata-owner-blocked.md",
    "memory/draft_bridge_gtkb_platform_sot_consolidation_umbrella_001.md",
    "memory/handoff-2026-06-11-pb-fab20-and-hooks-restoration.md",
    "memory/handoff-2026-06-11-pb-fab21-fable-program.md",
    "memory/handoff-2026-06-11-pb-fab21-hyg025-hyg028-done.md",
    "memory/handoff-2026-06-11-stage2-filed-stage3-gated.md",
    "memory/handoff-2026-06-11-stage3-collision-yielded.md",
    "memory/handoff-2026-06-11-stage3-proposal-filed.md",
    "memory/handoff-2026-06-11-wi4459-verified-wi4461-impl.md",
    "memory/handoff-2026-06-12-cheap-harness-program-and-fab05-verify.md",
    "memory/handoff-2026-06-12-cheap-harness-program-progress-and-wi4472-collision.md",
    "memory/handoff-2026-06-12-tafe-program-drive.md",
    "memory/handoff-2026-06-12-wi4472-awaiting-go.md",
    "memory/handoff-2026-06-12-wi4472-closed.md",
    "memory/handoff-2026-06-12-wi4472-proposal-filed.md",
    "memory/handoff-2026-06-13-S438-tafe-telemetry-stuckflow.md",
    "memory/handoff-2026-06-13-pb-implementation-loop.md",
    "memory/handoff-2026-06-13-s436-governance.md",
    "memory/handoff-2026-06-13-tafe-live-pilot-parked-draft.md",
    "memory/handoff-2026-06-13-tafe-swarm-drive-S437.md",
    "memory/handoff-2026-06-13-tafe-swarm-drive-S438.md",
    "memory/handoff-2026-06-14-S440-backlog-loop.md",
    "memory/handoff-2026-06-14-S445-repo-cleanup-push-merge.md",
    "memory/handoff-2026-06-14-interactive-pb-marker-block-advisory.md",
    "memory/handoff-2026-06-14-tafe-cutover-driver.md",
    "memory/keep-working-pb-2026-06-11-0608z-outcome.md",
    "memory/nogo-backlog-triage-2026-06-18.md",
    "memory/phase-1-glossary-backfill-draft.md",
    "memory/phase-2-template-pre-population-draft.md",
    "memory/phase-3-glossary-expansion-hook-draft.md",
    "memory/phase_2_worktree_audit_2026_05_11.md",
    "memory/recovery-2026-06-11-fab20-commit-collision.md",
    "memory/research_sot_consolidation_2026_06_04.md",
    "memory/s133-live-test-migration.md",
    "memory/session-wrap-2026-04-29.md",
    "memory/slice-4-smart-poller-retirement-continuation.md",
    "memory/sot_consolidation_owner_decisions_2026_06_04.md",
    "memory/spec_content_dcl_sot_registry_projection_parity_001.md",
    "memory/spec_content_dcl_sot_registry_record_schema_001.md",
    "memory/spec_content_gov_platform_sot_registry_001.md",
    "memory/topics/session_s231_summary.md",
    "memory/topics/session_s259.md",
    "memory/topics/session_s262_summary.md",
]

# WI-4347 PRESERVE anchors — representative durable files that MUST remain.
PRESERVE_ANCHORS = [
    "memory/MEMORY.md",
    "memory/CLAUDE_ARCHIVE.md",
    "memory/release-readiness.md",
    "memory/pending-owner-decisions.md",
    "memory/project_external_resource_registry.md",
    "memory/gt-cli-invocation-harness-b.md",
    "memory/feedback/feedback_bridge_protocol.md",
    "memory/feedback/feedback_production_deploy_approval.md",
    "memory/topics/reference_sarah_scenario.md",
    "memory/topics/canonical_vocabulary.md",
]

INDEX_HEADINGS = ["## Session Bootstrap", "## Quick Reference", "## Recent Sessions"]

# Index-only size ceiling. Pre-Slice-8 MEMORY.md was ~109 KB; the index is a
# few KB. The ceiling proves the bulky session-state log was removed while
# leaving generous headroom for the index to grow.
INDEX_SIZE_CEILING_BYTES = 12_000


def test_retired_ephemera_absent() -> None:
    """WI-4347: every RETIRE-bucket ephemera file is deleted."""
    assert len(RETIRED) == 51, f"expected 51 retire targets, got {len(RETIRED)}"
    still_present = [p for p in RETIRED if (ROOT / p).exists()]
    assert not still_present, f"retire-bucket files still present: {still_present}"


def test_preserved_files_present() -> None:
    """WI-4347 + GOV-08: durable PRESERVE anchors are retained."""
    missing = [p for p in PRESERVE_ANCHORS if not (ROOT / p).exists()]
    assert not missing, f"preserve-anchor files were removed: {missing}"


def test_memory_md_is_index_template() -> None:
    """WI-4346: MEMORY.md is an index, not a bulky content/backlog store."""
    assert MEMORY.exists(), "memory/MEMORY.md must exist"
    text = MEMORY.read_text(encoding="utf-8")
    for heading in INDEX_HEADINGS:
        assert heading in text, f"index heading missing: {heading}"
    # The pre-reconciliation bulky session log lived under '### Current Status'.
    assert "### Current Status" not in text, "MEMORY.md still carries the '### Current Status' bulky session-state log"
    size = len(text.encode("utf-8"))
    assert size <= INDEX_SIZE_CEILING_BYTES, (
        f"MEMORY.md is {size} bytes, exceeds index ceiling {INDEX_SIZE_CEILING_BYTES} (still a content store?)"
    )

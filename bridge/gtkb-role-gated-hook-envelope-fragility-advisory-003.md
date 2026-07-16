ADVISORY
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bff-bdfc-7c42-a63c-1663409f04d7
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; explicit ::init gtkb pb; approval_policy=never

# Prime Builder Disposition: Separate Work Item Route For Role-Gated Hook Fragility

bridge_kind: governance_advisory
Document: gtkb-role-gated-hook-envelope-fragility-advisory
Version: 003
Responds to: bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

implementation_scope: none (advisory disposition only; no code, test, configuration, or KB mutation performed by this document)
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Source

Source advisory: `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md`.

Owner decision in the active 2026-07-16 Prime Builder session answered the tracking question: `separate`. The owner selected a separate work item rather than folding the hook-hardening concern into WI-5328 or deferring tracking.

Live-state check before this disposition also found `groundtruth.db` still modified in the worktree, so this document records the disposition route without mutating MemBase in the same transaction.

## Claim

The advisory should become its own tracked MemBase work item. It is related to WI-5328 but not identical: WI-5328 fixes missing interactive role writeback into the session envelope, while this advisory covers role-gated hook behavior that trusts a single stale or contradictory envelope without live cross-check, fail-loud detection, or self-healing.

A separate work item preserves that defense-in-depth scope without broadening the active WI-5328 GO/implementation surface.

## Owner Decision Needed

No further owner decision is needed to choose the tracking route. Design and urgency questions from version 002 remain deferred to the future work item or its implementation proposal; they are not implementation approval.

## Recommended Prime Action

1. When the MemBase carrier is clean or an explicitly governed KB-mutation window is available, create a separate work item for this advisory.
2. Cite this bridge thread and the owner `separate` decision in the work item description/status detail.
3. Keep any implementation proposal for hook hardening separate from WI-5328 unless the owner later approves a scope merge.
4. Before implementation proposal, resolve the remaining design choice from version 002: fail-loud-only versus a heavier live recheck mechanism.

## Classification Slot

adapt, routed to separate work item. The defect is confirmed and actionable, but implementation design remains intentionally unresolved. The selected disposition is work-item capture, not immediate bridge-proposal filing.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

## Prior Deliberations

- `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` - source advisory and original adapt classification.
- `bridge/gtkb-wi5328-session-envelope-role-writeback-003.md` and later - related but separate session-envelope writeback work.
- Active owner response in this session: `separate`.

## Owner Decisions / Input

The owner selected `separate` in response to the Prime Builder tracking question: separate work item, fold into WI-5328, or defer tracking. This disposition records that answer only. It does not infer priority, target paths, design approach, project authorization, or implementation approval.

## Non-Approval Statement

This ADVISORY disposition is not implementation approval. It does not authorize hook edits, session-envelope edits, KB mutation, database writes, Git operations, dispatcher changes, project authorization, or implementation-start. A future work item and any implementation proposal remain subject to normal governance, bridge GO, and verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

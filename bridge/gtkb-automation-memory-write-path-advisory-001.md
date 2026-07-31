ADVISORY
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6381-9939-7500-abd6-c73d192c8c35
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner-directed bridge ADVISORY filing

bridge_kind: governance_advisory
Document: gtkb-automation-memory-write-path-advisory
Version: 001
Author: Owner-directed Advisory Proposal by Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC
Mode: advisory proposal
Severity: P2
Priority: P2

# Automation Memory Write Path Advisory Proposal

## Source

- Owner direction in the active 2026-07-15 Prime Builder session to file this issue as a proper Advisory Proposal.
- Governed work item `WI-4681` and its latest VERIFIED bridge artifact, `bridge/gtkb-harness-local-scratchpad-boundary-008.md`.
- Current operating-contract rules governing harness-local scratchpads and project-relevant knowledge promotion.

## Claim

GT-KB has not yet established whether current automation runtimes require workers to read or append `$CODEX_HOME/automations/<automation_id>/memory.md`, or whether a product-owned API now handles that operation. If direct cache maintenance remains required, the absence of a deterministic sanctioned operation creates a serviceability risk: workers may spend tokens probing denied commands or reconstructing ad hoc append workarounds.

Current governance has since resolved part of the ambiguity:

- `WI-4681` and `bridge/gtkb-harness-local-scratchpad-boundary-008.md` are latest `VERIFIED`.
- The current operating contract classifies Codex automation memory, Claude auto-memory, Antigravity planning files, and the `MEMORY.md` hierarchy as non-authoritative scratch/notepad surfaces.
- Project-relevant information originating in those surfaces must be promoted into governed in-root artifacts before it becomes source evidence or a dependency.

The open question is narrow: if the automation runtime still requires its non-authoritative local cache to be updated, GT-KB should provide a deterministic, policy-explicit, low-token operation instead of recurring shell workarounds. This must not create a second authoritative memory system.

## Owner Decision Needed

No additional owner decision is needed to file this ADVISORY; the owner expressly requested this Advisory Proposal.

If current runtime discovery confirms that automation-memory writes are still required, a later owner disposition may choose among:

- retain the home-directory file as a sanctioned non-authoritative cache with a deterministic helper;
- replace the cache with a product-owned automation-memory API or equivalent runtime surface;
- retire the write requirement entirely.

An in-root mirror must not be introduced as an authority shortcut. Any project-relevant result must be promoted through the appropriate governed artifact lifecycle.

## Recommended Prime Action

Classify this advisory as `adapt`.

1. Re-check the current Codex automation contract and tool surface; do not assume the 2026-06-13 write requirement or blocked-command pattern remains unchanged.
2. If the requirement no longer exists or is fully owned by the automation product, record a no-op or withdrawal with evidence.
3. If the requirement remains, create a bounded work item for a deterministic helper or governed command that:
   - validates the automation identifier and resolved cache path;
   - supports read and append without arbitrary shell construction;
   - writes only the non-authoritative automation cache;
   - emits clear diagnostics and an auditable operation result;
   - never presents cache content as GT-KB source of truth;
   - directs project-relevant information into MemBase, the Deliberation Archive, bridge artifacts, specs, tests, or other governed in-root carriers.
4. Check overlap with current Codex app automation capabilities and harness-parity work before choosing a repo-owned `gt automation memory` command.
5. File a normal implementation proposal only after the ownership boundary, target paths, and verification contract are current.

## Classification Slot

Owner-directed governance advisory. Recommended disposition: `adapt` after current-state discovery; route to no-op if the automation product now provides the operation, otherwise to a small deterministic-service work item. This ADVISORY remains non-dispatchable and is not implementation approval.

## Prior Deliberations

- `DELIB-20260715-ADVISORY-PROPOSAL-PRIMARY-LO-INITIATION-MECHANISM`
- `DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY` - owner clarification that harness-local scratchpads and evolving auto-memory systems are non-authoritative.
- `DELIB-20260671` - platform source-of-truth consolidation direction.

## Related Governed Artifacts

- `WI-4681` - resolved harness-local scratchpad boundary work item.
- `bridge/gtkb-harness-local-scratchpad-boundary-008.md` - latest VERIFIED predecessor.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-0001` - three-tier memory architecture.

## Duplicate And Supersession Check

No bridge thread named `gtkb-automation-memory-write-path-advisory` existed before filing. The verified scratchpad-boundary thread settles authority classification but does not provide or reject the deterministic automation-cache operation recommended here. This proposal is therefore related, narrower follow-on guidance rather than a duplicate.

## Non-Approval Statement

This ADVISORY is a non-dispatchable bridge artifact and future-work initiation carrier. It is not a GO verdict, implementation proposal, project authorization, work-intent claim, implementation-start packet, or permission to mutate home-directory automation state, GT-KB source, hooks, configuration, or governed artifacts. Downstream implementation requires normal advisory disposition, requirement sufficiency, bridge proposal, independent Loyal Opposition GO, work-intent, implementation-start, report, and verification.

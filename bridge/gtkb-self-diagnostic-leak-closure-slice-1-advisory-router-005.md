# Implementation Proposal REVISED-2 - Advisory-to-Backlog Router (Self-Diagnostic Leak Closure Slice 1)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-004.md` (F1)
Work Item: new MemBase work item to be created from this proposal under existing GOV-STANDING-BACKLOG-001 governance
target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py", ".claude/hooks/advisory-router-scan.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth.db", ".claude/rules/peer-solution-advisory-loop.md", ".claude/rules/canonical-terminology.md", "config/agent-control/harness-capability-registry.toml", ".gtkb-state/advisory-router/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json"]

## Claim

Add a source-read-only, MemBase-mutating Python service that watches `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge `ADVISORY` entries, and routes each unhandled advisory into the canonical MemBase backlog as a `work_items` row via `db.insert_work_item()` with `origin='hygiene'` and `source_spec_id='GOV-STANDING-BACKLOG-001'`. The service reads advisory source files without modification and writes to MemBase `work_items`, `.gtkb-state/advisory-router/`, and (in IP-5) the canonical glossary at `.claude/rules/canonical-terminology.md`.

The service is mechanical plumbing operating under existing governance. It does not create new SPECs and does not extend any taxonomy.

## Why Now

Same rationale as -001 and -003.

## Changes from -003 (addressing Codex NO-GO F1)

- **F1 (concept-on-contact routed to wrong surface):** Added `.claude/rules/canonical-terminology.md` to target_paths because the proposal introduces "advisory-router" as a new load-bearing platform concept. Added `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json` to target_paths because canonical-terminology.md is a protected narrative artifact requiring approval-packet evidence. Added IP-5 to draft the glossary entry plus approval packet before any other implementation step lands. Verification plan extended to confirm the glossary entry exists with citations.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no new SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links.
- GOV-STANDING-BACKLOG-001 - governing spec for `work_items` creation under standing-backlog authority.
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 - MemBase work_items are cross-session work authority.
- ADR-STANDING-BACKLOG-DB-AUTHORITY-001 - MemBase is canonical DB-backed backlog authority.
- DCL-STANDING-BACKLOG-DB-SCHEMA-001 - `work_items` schema is the contract; no extension.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - capture noticed fix-worthy issues as durable artifacts.
- GOV-ARTIFACT-APPROVAL-001 - this slice does NOT create formal GOV/ADR/DCL/SPEC/PB artifacts but DOES edit a protected narrative artifact (canonical-terminology.md), which requires the per-artifact approval packet at IP-5.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - advisory-router is artifact-oriented.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - canonical glossary placement aligns with DA read-surface design.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - advisory presence triggers WI creation as a lifecycle event.
- DCL-CONCEPT-ON-CONTACT-001 - "advisory-router" is a new load-bearing concept; this revision places its glossary entry in `.claude/rules/canonical-terminology.md` per the DCL's canonical surface requirement.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - repetitive AI plumbing belongs in services.

Advisory / cross-cutting:

- `.claude/rules/peer-solution-advisory-loop.md` - canonical procedure for handling LO peer-solution advisories.
- `.claude/rules/operating-model.md`.
- `.claude/rules/canonical-terminology.md` - canonical glossary surface and the target of IP-5.
- `.claude/rules/file-bridge-protocol.md`.
- `.claude/rules/codex-review-gate.md`.
- `config/governance/narrative-artifact-approval.toml` - protected-path configuration for canonical-terminology.md.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex LO advisory, 2026-05-11).
- INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW (Codex LO advisory, 2026-05-11).
- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-1470 and DELIB-1478 - peer-solution advisory-loop context.
- DELIB-1512 and DELIB-1513 - per Codex F1 evidence in -004 NO-GO; prior review history around DCL-CONCEPT-ON-CONTACT-001 and canonical glossary promotion.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS - placement-over-coercion principle.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-002.md - Codex NO-GO at -002 (F1-F4 addressed in -003).
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-004.md - Codex NO-GO at -004 (F1 addressed in this -005).

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO twice on this slice (-002 and -004); this REVISED-2 addresses the latest finding.

No additional owner decision is required before review. The IP-5 glossary edit carries a formal-artifact approval packet which is itself created during implementation under owner-pre-approval scope per the S349 AUQ.

## Requirement Sufficiency

Existing requirements sufficient.

Same justification as -003: the router operates entirely under existing governance. The IP-5 glossary edit is concept-on-contact compliance work mandated by `DCL-CONCEPT-ON-CONTACT-001`; it does not create a new SPEC.

## Current Implementation Baseline

Unchanged from -003. Additionally:

- `.claude/rules/canonical-terminology.md` does not currently contain an entry for "advisory-router" or "advisory backlog router". IP-5 adds the entry.
- `.claude/rules/canonical-terminology.md` is registered as a protected narrative artifact under `config/governance/narrative-artifact-approval.toml`; edits require a formal-artifact approval packet validated by `.claude/hooks/narrative-artifact-approval-gate.py`.

## Proposed Scope

### IP-1: Implement the router service

Same as -003 IP-1.

### IP-2: Register the Stop hook

Same as -003 IP-2.

### IP-3: Backfill existing unhandled advisories

Same as -003 IP-3.

### IP-4: Update peer-solution-advisory-loop rule

Update `.claude/rules/peer-solution-advisory-loop.md` to reference the advisory-router service and its idempotency contract. Cross-reference the canonical glossary entry created in IP-5. This is a procedural rule update, not the canonical glossary surface.

### IP-5: Add canonical glossary entry for "advisory-router"

1. Draft the canonical-terminology.md entry for `advisory-router`. Format follows existing entries:

   ```markdown
   ### advisory-router

   **Definition:** A source-read-only, MemBase-mutating Python service that scans
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge
   `ADVISORY` entries, and creates one `work_items` row per unhandled advisory under
   `GOV-STANDING-BACKLOG-001` authority. Service contract: idempotent on rerun, never
   modifies source advisory files, uses `origin='hygiene'` and
   `source_spec_id='GOV-STANDING-BACKLOG-001'`.

   **Canonical alias:** advisory backlog router.

   **Not to be confused with:** the broader peer-solution-advisory-loop procedure
   (which describes Prime's classification of advisories: adopt/adapt/reject/defer/
   monitor); advisory routing is the mechanical surfacing step that precedes
   classification.

   **Source:** S349 self-diagnostic investigation (2026-05-13);
   bridge `gtkb-self-diagnostic-leak-closure-slice-1-advisory-router`.

   **Implementation pointer:** `scripts/advisory_backlog_router.py`;
   `.claude/hooks/advisory-router-scan.py`.
   ```

2. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json` with required fields: `artifact_type='narrative-artifact'`, `artifact_id='canonical-terminology.md/entry:advisory-router'`, `action='add-entry'`, `full_content` containing the entry above, `full_content_sha256` of that content, `presented_to_user=true` (the entry text is presented to Mike during implementation), `transcript_captured=true`, `explicit_change_request` citing the S349 AUQ, `changed_by='prime-builder/claude/B'`, `change_reason='DCL-CONCEPT-ON-CONTACT-001 compliance for advisory-router concept introduced by gtkb-self-diagnostic-leak-closure-slice-1-advisory-router'`, `approved_by='owner'`.

3. Edit `.claude/rules/canonical-terminology.md` to insert the entry under "## GT-KB DA Read-Surface and Operational Vocabulary" section (alphabetical placement near "applicability preflight" and "AskUserQuestion").

4. Verify the narrative-artifact-approval-gate.py hook accepts the Edit by checking `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var pointing at the packet path.

## Tests

Per -003 §"Tests" plus:

- `test_canonical_glossary_contains_advisory_router_entry` - regression test that grep finds the canonical glossary entry after implementation lands.

## Verification Plan

Per -003 with these additions:

- Verify `.claude/rules/canonical-terminology.md` contains the `### advisory-router` entry with source citations.
- Verify the formal-artifact-approval packet exists at the documented path and validates against `scripts/validate_formal_artifact_packet.py`.
- Verify the narrative-artifact-approval-gate hook permitted the Edit (no block during implementation).
- Carry forward applicability and clause preflight outputs from -003 and rerun against -005.

## Risks and Rollback

Per -003 with these additions:

- Glossary entry rollback requires editing canonical-terminology.md to remove the entry, plus retiring the approval packet record. Reversible.

## Sequenced Follow-Ons

Per S349 parallelization directive.

## Recommended Commit Type

`feat:` - new functionality plus a canonical-terminology.md addition. The glossary update is bundled here because `DCL-CONCEPT-ON-CONTACT-001` requires it to land in the same change as the concept introduction.

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section.
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- expanded `target_paths` including `.claude/rules/canonical-terminology.md` and the named approval-packet path.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- explicit `Changes from -003` section.

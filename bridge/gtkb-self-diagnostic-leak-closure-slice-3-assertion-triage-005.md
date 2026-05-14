# Implementation Proposal REVISED-2 - Assertion Signal/Noise Triage (Self-Diagnostic Leak Closure Slice 3)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-004.md` (F1 concept-on-contact, F2 work-item scope ambiguity)
Work Item: this proposal authorizes creation of one MemBase work_item for the slice (origin='hygiene', source_spec_id='SPEC-1662'); see IP-6
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py", ".claude/skills/assertion-triage/SKILL.md", ".codex/skills/assertion-triage/SKILL.md", "config/agent-control/harness-capability-registry.toml", ".codex/skills/MANIFEST.json", ".claude/rules/canonical-terminology.md", "groundtruth.db", ".gtkb-state/assertion-triage/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-assertion-category-entries.json"]

## Claim

Implement assertion signal/noise categorization that converts the 1,463 currently-failing GT-KB assertions into four owner-actionable categories (genuine_drift, chronic_noise, flaky, healthy) under existing SPEC-1662 (GOV-18: Assertion Quality Standard) and GOV-15 (test fix gate). Categorization is read-only inference over `assertion_runs` history; per-assertion retirement requires explicit one-at-a-time owner AUQ per `CODEX-WAY-OF-WORKING.md:127-130`.

The slice creates one MemBase `work_item` to track its own implementation (`origin='hygiene'`, `source_spec_id='SPEC-1662'`) - this is the only canonical state mutation in scope, and `groundtruth.db` is included in target_paths to authorize it. Categorization output (per-assertion category JSON) goes only to `.gtkb-state/assertion-triage/` and is non-authoritative.

## Why Now

Same rationale as -001 and -003.

## Changes from -003 (addressing Codex NO-GO F1, F2)

- **F1 (concept-on-contact routed to wrong surface):** Added `.claude/rules/canonical-terminology.md` to target_paths because the proposal introduces "assertion category", "genuine_drift", "chronic_noise", and "flaky" as new load-bearing platform concepts. Added `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-assertion-category-entries.json` to target_paths. Added IP-6 to draft glossary entries plus approval packet. Verification plan extended.
- **F2 (work-item creation scope ambiguity):** Clarified Work Item header to explicitly state one WI is created (with origin and source_spec_id). Added `groundtruth.db` to target_paths to authorize the WI insert. Updated Claim section to distinguish "categorization output is non-authoritative" (read-only against `assertion_runs`, writes only to `.gtkb-state/`) from "one tracking WI is created" (authoritative MemBase mutation with explicit scope).
- **Non-blocking update:** Citation now reads `SPEC-1662 (GOV-18: Assertion Quality Standard)` for machine retrievability (matching the Slice 2 REVISED-2 convention).

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no new SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - directly governs categorization as operationalizing meaningfulness over coverage.
- GOV-03 TEST-CLARITY - every test must produce unambiguous PASS/FAIL; chronic_noise category surfaces tests that have lost clarity.
- GOV-15 TEST-FIX-GATE - no fixing failed tests without owner approval; retirement workflow enforces per-call AUQ.
- GOV-STANDING-BACKLOG-001 - retirement candidates flow to standing backlog; the tracking WI created by this slice is a backlog item.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - categorization output is durable artifact.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - categorization is artifact-oriented.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - assertion state transitions are lifecycle events.
- DCL-CONCEPT-ON-CONTACT-001 - "assertion category", "genuine_drift", "chronic_noise", "flaky" are new load-bearing concepts; IP-6 places glossary entries in `.claude/rules/canonical-terminology.md` per the DCL's canonical surface.
- GOV-ARTIFACT-APPROVAL-001 - this slice does NOT create formal GOV/ADR/DCL/SPEC/PB artifacts but DOES edit a protected narrative artifact (canonical-terminology.md), which requires the per-artifact approval packet at IP-6. Retirement requires per-assertion AUQ with formal-artifact-approval packet at execution time.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.

Advisory / cross-cutting:

- `.claude/rules/operating-model.md` §1.
- `.claude/rules/canonical-terminology.md` - canonical glossary surface, target of IP-6.
- `config/governance/narrative-artifact-approval.toml` - protected-path config for canonical-terminology.md.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` §127-130 (one-at-a-time owner-action protocol).
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md`.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-0473 - prior pipeline hardening advisory.
- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-1512 and DELIB-1513 - per Codex F1 evidence in -002 NO-GO; prior review history around DCL-CONCEPT-ON-CONTACT-001 and canonical glossary promotion.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- Prior MEMORY.md handoff entries (S347, S348) - cite "224/1687 PASS and 1463 FAIL" verbatim.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md - Codex NO-GO at -002 (F1, F2, F3 addressed in -003).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-004.md - Codex NO-GO at -004 (F1, F2 addressed in this -005).

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO twice on this slice (-002, -004); this REVISED-2 addresses the latest findings.

No additional owner decision is required before review. Each retirement decision at execution time will be a separate AUQ.

## Requirement Sufficiency

Existing requirements sufficient.

Same justification as -003 with updated citation to SPEC-1662 (GOV-18: Assertion Quality Standard) for machine retrievability. The IP-6 glossary edits are concept-on-contact compliance work mandated by `DCL-CONCEPT-ON-CONTACT-001`. The MemBase WI insert at IP-7 is the standard tracking-WI for slice implementation under standing-backlog authority.

## Current Implementation Baseline

Unchanged from -003. Additionally:

- `.claude/rules/canonical-terminology.md` does not currently contain entries for "assertion category", "genuine_drift", "chronic_noise", or "flaky". IP-6 adds the entries.
- canonical-terminology.md is a protected narrative artifact; edits require a formal-artifact approval packet.

## Proposed Scope

### IP-1: Implement categorization script

Same as -003 IP-1.

### IP-2: Implement retirement workflow with one-at-a-time AUQ

Same as -003 IP-2.

### IP-3: Wire into assertion-check hook (advisory display only)

Same as -003 IP-3.

### IP-4: Tests

Same as -003 IP-4.

### IP-5: Add assertion-triage skill

Same as -003 IP-5, with the clarification that the skill describes HOW to run categorization; canonical vocabulary placement is IP-6 (not the skill).

### IP-6: Add canonical glossary entries for assertion-category concepts

1. Draft canonical-terminology.md entries for four concepts. Format follows existing entries:

   - `assertion category` - one of four classifications produced by `scripts/assertion_categorize.py` for currently-failing assertions: `genuine_drift`, `chronic_noise`, `flaky`, `healthy`. Categorization is deterministic inference over `assertion_runs` history; outputs are read-only at `.gtkb-state/assertion-triage/categories/<assertion_id>.json`. Source: S349 self-diagnostic. Implementation pointer: `scripts/assertion_categorize.py`. Not to be confused with: assertion (the GT-KB machine-verifiable check primitive itself).

   - `genuine_drift` - assertion category indicating: latest run FAIL, prior 5+ runs PASS, transition within configurable window (default 7 days). Drift detection per SPEC-1662 (GOV-18). Source: S349.

   - `chronic_noise` - assertion category indicating: latest 50+ consecutive runs all FAIL. Candidate for retirement-or-accept owner decision per GOV-15 (test fix gate). Source: S349.

   - `flaky` - assertion category indicating: latest 10 runs include both PASS and FAIL with at least one transition. Flag for repair, not retirement. Source: S349.

2. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-assertion-category-entries.json` with required fields, listing all four entries in `full_content` with a single combined `full_content_sha256`.

3. Edit `.claude/rules/canonical-terminology.md` to insert entries under "## GT-KB DA Read-Surface and Operational Vocabulary".

4. Verify the narrative-artifact-approval-gate hook accepts the Edit.

### IP-7: Create tracking work_item

1. After IP-1 through IP-6 land, insert one `work_items` row via `db.insert_work_item()`:
   - `origin='hygiene'`
   - `source_spec_id='SPEC-1662'`
   - `title='Implement assertion S/N triage (GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE Slice 3)'`
   - `related_bridge_threads='gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage'`
   - `changed_by='prime-builder/claude/B'`
   - `change_reason='S349 self-diagnostic LEAK 3 closure; slice authorized by owner AUQ + parallelization directive'`

This WI documents the slice's implementation lineage in the canonical backlog for cross-session traceability.

## Tests

Per -003 §"Tests" plus:

- `test_canonical_glossary_contains_assertion_category_entries` - regression test that grep finds each of the four canonical glossary entries.

## Verification Plan

Per -003 with these additions:

- Verify all four canonical glossary entries exist with source citations.
- Verify the formal-artifact approval packet exists and validates.
- Verify the narrative-artifact-approval-gate hook permitted the Edit.
- Verify the IP-7 tracking work_item exists in MemBase with origin='hygiene' and source_spec_id='SPEC-1662'.
- Verify SPEC-1662 citation resolves.
- Carry forward applicability and clause preflight outputs from -003.

## Risks and Rollback

Per -003 with these additions:

- Glossary rollback: edit canonical-terminology.md to remove the four entries.
- WI rollback: standard `db.update_work_item()` with `resolution_status='retired_by_rollback'`.

## Sequenced Follow-Ons

Per S349 parallelization directive.

## Recommended Commit Type

`feat:` - new functionality plus canonical-terminology.md additions bundled per `DCL-CONCEPT-ON-CONTACT-001`.

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section.
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- expanded `target_paths` including `.claude/rules/canonical-terminology.md`, `groundtruth.db`, and the named approval-packet path.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- explicit `Changes from -003` section.
- SPEC-1662 cited for machine retrievability.
- Work Item header consistent with `groundtruth.db` in target_paths.

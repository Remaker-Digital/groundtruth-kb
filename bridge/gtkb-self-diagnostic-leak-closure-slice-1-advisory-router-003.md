# Implementation Proposal REVISED-1 - Advisory-to-Backlog Router (Self-Diagnostic Leak Closure Slice 1)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-002.md` (F1, F2, F3, F4)
Work Item: new MemBase work item to be created from this proposal under existing GOV-STANDING-BACKLOG-001 governance
target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py", ".claude/hooks/advisory-router-scan.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth.db", ".claude/rules/peer-solution-advisory-loop.md", "config/agent-control/harness-capability-registry.toml", ".gtkb-state/advisory-router/**"]

## Claim

Add a source-read-only, MemBase-mutating Python service that watches `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge `ADVISORY` entries, and routes each unhandled advisory into the canonical MemBase backlog as a `work_items` row via `db.insert_work_item()` with `origin='hygiene'` and `source_spec_id='GOV-STANDING-BACKLOG-001'`. The service reads advisory source files without modification and writes only to MemBase `work_items` and `.gtkb-state/advisory-router/`.

The service is mechanical plumbing operating under existing governance. It does not create new SPECs, does not extend any taxonomy, and does not bypass the bridge protocol for subsequent implementation. It only converts "advisory exists on disk" into "MemBase work item exists" so the standing backlog reflects the actual work the platform has surfaced.

## Why Now

Same rationale as -001: S349 self-diagnostic surfaced three LO advisories from 2026-05-10 and 2026-05-11 sitting in the dropbox unhandled. Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, manually scanning each session is exactly the repetitive plumbing that belongs in a deterministic service.

## Changes from -001 (addressing Codex NO-GO F1-F4)

- **F1 (Requirement Sufficiency contradiction):** Removed SPEC creation from this slice. The router operates entirely under existing governance (`GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, `.claude/rules/peer-solution-advisory-loop.md`, `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE`). No new SPEC is required because the router's contract is fully described by these existing artifacts.
- **F2 (target_paths omits packet/state files):** Removed approval-packet writes from scope (no SPEC creation). Added `.gtkb-state/advisory-router/**` to target_paths for last-scan timestamp and audit logs.
- **F3 (work_items contract defect):** Changed `origin` to documented value `'hygiene'`. Set `source_spec_id='GOV-STANDING-BACKLOG-001'` (the governing spec for backlog management). Both fields conform to existing `KnowledgeDB.insert_work_item()` contract.
- **F4 (read-only claim was misleading):** Reworded claim to "source-read-only, MemBase-mutating" so the mutation boundary is explicit.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation; live `bridge/INDEX.md` remains canonical.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links and maps tests to them.
- GOV-STANDING-BACKLOG-001 - the governing spec for `work_items` creation; advisory routing produces canonical backlog rows under this authority.
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 - MemBase work_items are the cross-session work authority; advisory-router output flows here, not to markdown views.
- ADR-STANDING-BACKLOG-DB-AUTHORITY-001 - MemBase is the canonical DB-backed backlog/project authority.
- DCL-STANDING-BACKLOG-DB-SCHEMA-001 - `work_items` schema (origin, source_spec_id, related_*, changed_by, change_reason) is the contract this router writes against without extension.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - capture noticed fix-worthy issues as durable artifacts.
- GOV-ARTIFACT-APPROVAL-001 - this slice creates no formal GOV/ADR/DCL/SPEC/PB artifacts and so does not engage the formal-artifact-approval-packet workflow.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - advisory-router is artifact-oriented (writes durable work_items, reads durable advisories).
- ADR-DA-READ-SURFACE-PLACEMENT-001 - INSIGHTS reports remain a DA read surface; this slice adds a downstream consumer without changing placement.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - advisory presence triggers WI creation as a lifecycle event under existing taxonomy.
- DCL-CONCEPT-ON-CONTACT-001 - "advisory-router" is a new load-bearing concept; glossary entry added as part of IP-4 update to `.claude/rules/peer-solution-advisory-loop.md`.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - repetitive AI plumbing belongs in services.

Advisory / cross-cutting:

- `.claude/rules/peer-solution-advisory-loop.md` - canonical procedure for handling LO peer-solution advisories.
- `.claude/rules/operating-model.md` - operating model alignment baseline.
- `.claude/rules/canonical-terminology.md` - glossary maintenance baseline.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol authority.
- `.claude/rules/codex-review-gate.md` - implementation requires Codex GO.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC) - owner authorized work via AskUserQuestion "File both, sequenced" then "parallelize this work to the maximum extent possible".
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10) - one of the three unhandled advisories this slice routes.
- INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY (Codex LO advisory, 2026-05-11) - second unhandled advisory.
- INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW (Codex LO advisory, 2026-05-11) - third unhandled advisory.
- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE - per Codex F1 evidence in -002 NO-GO; supports routing future-work to MemBase rather than MEMORY.md.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT - per Codex F1 evidence in -002 NO-GO; confirms MemBase `work_items` as canonical backlog source of truth.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - per Codex F1 evidence in -002 NO-GO; supports moving repetitive AI plumbing into deterministic services.
- DELIB-1470 and DELIB-1478 - peer-solution advisory loop context per Codex F1 evidence in -002 NO-GO.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - recent owner authorization pattern consistent with this slice's owner-approval frame.
- DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS - placement-over-coercion principle; the router places consumption on existing path.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-002.md - Codex NO-GO at -002; this REVISED-1 addresses F1-F4.

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner asked Prime Builder to investigate GT-KB behavior for leaks/gaps/waste; investigation produced quantitative findings.
- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then authorized "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO on -001 with four findings; this REVISED-1 addresses them.

No additional owner decision is required before this revised proposal can be reviewed. The S349 AUQ remains the parent owner authorization.

## Requirement Sufficiency

Existing requirements sufficient.

The router operates entirely under existing governance:

- `GOV-STANDING-BACKLOG-001` governs `work_items` creation as the standing backlog authority.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` establishes MemBase as the canonical backlog substrate.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` provides the `work_items` schema fields (`origin`, `source_spec_id`, `related_*`, `changed_by`, `change_reason`) the router writes.
- `.claude/rules/peer-solution-advisory-loop.md` describes the advisory loop the router serves.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` authorizes routing of noticed fix-worthy issues to MemBase backlog.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` authorizes mechanical plumbing for repetitive AI work.

The router's behavior contract (read advisories, create one WI per unhandled advisory with `origin='hygiene'` and `source_spec_id='GOV-STANDING-BACKLOG-001'`, never modify source advisories, idempotent on rerun) is fully described by the bridge proposal itself plus these existing artifacts. No new SPEC is required.

## Current Implementation Baseline

Unchanged from -001 §"Current Implementation Baseline".

## Proposed Scope

### IP-1: Implement the router service

1. Create `scripts/advisory_backlog_router.py`:
   - CLI entry: `python scripts/advisory_backlog_router.py [--dry-run] [--source dropbox|bridge|both] [--since YYYY-MM-DD]`.
   - Scans configured sources, computes idempotency keys, queries existing `work_items` for `related_bridge_threads` and `related_deliberation_ids` matches to avoid duplicates, creates one new WI per unhandled advisory via `db.insert_work_item()` with:
     - `origin='hygiene'`
     - `source_spec_id='GOV-STANDING-BACKLOG-001'`
     - `title='Route LO advisory: <advisory_filename>'`
     - `description` containing first paragraph of advisory plus path
     - `related_deliberation_ids` populated with advisory filename anchor
     - `priority` derived from advisory severity header (P0/P1 → high, P2 → medium, P3/P4 or unset → low)
     - `changed_by='advisory-router-service@1.0'`
     - `change_reason` citing the source advisory path
   - Stores last-scan timestamp at `.gtkb-state/advisory-router/last-scan.json`.
   - Emits structured JSON output (`created`, `skipped_existing`, `errors`).

### IP-2: Register the Stop hook

1. Create `.claude/hooks/advisory-router-scan.py` as a thin wrapper invoking the router CLI in `--source both --since <last-scan>` mode on Prime Stop events.
2. Register in `.claude/settings.json` under `hooks.Stop`.
3. Add Codex parity registration in `.codex/hooks.json`.
4. Add capability registry entry in `config/agent-control/harness-capability-registry.toml`.

### IP-3: Backfill existing unhandled advisories

1. Run router in `--dry-run` mode against current dropbox state.
2. Owner reviews dry-run output via AskUserQuestion before applying.
3. Apply with `--source dropbox --since 2026-04-01`.

### IP-4: Update peer-solution-advisory-loop rule

1. Add a "Mechanical Surfacing" subsection to `.claude/rules/peer-solution-advisory-loop.md` documenting the advisory-router as the canonical surfacing mechanism.
2. Cross-reference the router's idempotency contract.
3. Add "advisory-router" glossary entry per `DCL-CONCEPT-ON-CONTACT-001`.

## Tests

`platform_tests/scripts/test_advisory_backlog_router.py` with the 8 tests previously specified in -001 §"Tests", with two additional assertions:

- `test_router_uses_hygiene_origin` - created WIs have `origin='hygiene'`.
- `test_router_sets_source_spec_id` - created WIs have `source_spec_id='GOV-STANDING-BACKLOG-001'`.

## Verification Plan

Per -001 §"Verification Plan" with these additions:

- Verify WI `origin` field is exactly `'hygiene'` in MemBase post-impl.
- Verify WI `source_spec_id` field is `'GOV-STANDING-BACKLOG-001'`.
- Verify `.gtkb-state/advisory-router/last-scan.json` exists and has valid ISO timestamp after first run.
- Carry forward applicability and clause preflight outputs from -001 (preflight_passed=true, 0 blocking gaps) and rerun against -003 in the post-impl report.

## Risks and Rollback

Per -001 §"Risks and Rollback". Additionally:

- `origin='hygiene'` may bleed into hygiene-specific dashboards/filters and conflate routed advisories with other hygiene work. Mitigation: `changed_by='advisory-router-service@1.0'` is a unique discriminator; dashboards filtering by `changed_by` get a clean view.
- Rollback now does not require retiring any new SPEC (none created); only WI retirement and code removal.

## Sequenced Follow-Ons

Per S349 parallelization directive, no longer waiting for any other slice.

## Recommended Commit Type

`feat:` - new functionality (router service, hook registration, rule update). Backfill commit is a separate `chore:`.

## Bridge-Compliance Self-Check

This proposal includes:

- non-empty `## Specification Links` section with cited governing specs (15 blocking + 4 advisory).
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- expanded `target_paths` including `.gtkb-state/advisory-router/**`.
- `## Requirement Sufficiency` subsection with exactly one operative state: "Existing requirements sufficient".
- `## Recommended Commit Type`.
- explicit `Changes from -001` section enumerating each NO-GO finding addressed.

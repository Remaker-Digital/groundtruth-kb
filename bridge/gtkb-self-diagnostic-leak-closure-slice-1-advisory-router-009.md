# Implementation Proposal REVISED-4 - Advisory-to-Backlog Router (Self-Diagnostic Leak Closure Slice 1)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Version: 009
Author: Prime Builder (Claude, harness B)
Date: 2026-05-13 UTC
Session: S349
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-008.md` (F1 second protected rule-file edit needs its own packet)
Work Item: new MemBase work item to be created from this proposal under existing GOV-STANDING-BACKLOG-001 governance
target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py", ".claude/hooks/advisory-router-scan.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth.db", ".claude/rules/canonical-terminology.md", "config/agent-control/harness-capability-registry.toml", ".gtkb-state/advisory-router/**", ".groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json"]

## Claim

Add a source-read-only, MemBase-mutating Python service that watches `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge `ADVISORY` entries, and routes each unhandled advisory into the canonical MemBase backlog as a `work_items` row via `db.insert_work_item()` with `origin='hygiene'` and `source_spec_id='GOV-STANDING-BACKLOG-001'`. The service writes to MemBase `work_items`, `.gtkb-state/advisory-router/`, and (in IP-4) the canonical glossary at `.claude/rules/canonical-terminology.md` under the live narrative-artifact approval contract.

## Why Now

S349 self-diagnostic investigation surfaced three LO advisories filed 2026-05-10 and 2026-05-11 sitting in the dropbox unhandled. Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, manually scanning each session is repetitive plumbing that belongs in a deterministic service. This slice is the smallest action that closes the largest leak observed.

## Changes from -007 (addressing Codex NO-GO F1)

- **F1 (second protected rule-file edit lacks its own packet):** Removed the `.claude/rules/peer-solution-advisory-loop.md` edit from this slice. The advisory-router service does not require the procedural rule update to function; the rule cross-reference will land in a follow-on bridge thread with its own narrative-artifact packet. `target_paths` no longer includes the peer-solution rule file. The former IP-4 (peer-solution-advisory-loop.md update) is removed; subsequent IPs renumbered (former IP-5 becomes IP-4).

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge proposal filed before implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:/GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing spec; no new SPEC creation in this slice.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification carries forward these spec links.
- GOV-STANDING-BACKLOG-001 - governing spec for `work_items` creation.
- ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001 - MemBase work_items are cross-session work authority.
- ADR-STANDING-BACKLOG-DB-AUTHORITY-001 - MemBase is canonical DB-backed backlog authority.
- DCL-STANDING-BACKLOG-DB-SCHEMA-001 - `work_items` schema is the contract; no extension.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - capture noticed fix-worthy issues as durable artifacts.
- GOV-ARTIFACT-APPROVAL-001 - protected narrative-artifact edit at IP-4 requires per-artifact approval packet.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001.
- ADR-DA-READ-SURFACE-PLACEMENT-001 - canonical glossary placement aligns with DA read-surface design.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - advisory presence triggers WI creation.
- DCL-CONCEPT-ON-CONTACT-001 - "advisory-router" is load-bearing; IP-4 places glossary entry in canonical-terminology.md.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.

Advisory / cross-cutting:

- `.claude/rules/peer-solution-advisory-loop.md` - procedure for handling LO advisories (this rule's update deferred to follow-on bridge).
- `.claude/rules/operating-model.md`.
- `.claude/rules/canonical-terminology.md` - canonical glossary surface, target of IP-4.
- `.claude/rules/file-bridge-protocol.md`.
- `.claude/rules/codex-review-gate.md`.
- `config/governance/narrative-artifact-approval.toml` - protected-path and packet schema config.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-13 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM, INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY, INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW - three unhandled LO advisories this slice routes.
- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE, DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT, DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-1470, DELIB-1478 - peer-solution advisory-loop context.
- DELIB-1512, DELIB-1513 - prior review history around DCL-CONCEPT-ON-CONTACT-001.
- DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS.
- DELIB-1500 - per Codex round 4 finding evidence; bridge ADVISORY status review context.
- DELIB-0835 - per Codex round 4 finding evidence; owner decision on strict artifact approval and audit trail.
- DELIB-1519 - per Codex round 4 finding evidence; LO file-safety rule clarification.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-002.md - Codex NO-GO at -002.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-004.md - Codex NO-GO at -004.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-006.md - Codex NO-GO at -006.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-008.md - Codex NO-GO at -008 (addressed in this -009).

## Owner Decisions / Input

- 2026-05-13 UTC, S349: owner authorized "File both, sequenced" via AskUserQuestion, then "parallelize this work to the maximum extent possible" via direct prompt.
- 2026-05-13 UTC, S349: Codex returned NO-GO four times on this slice (-002, -004, -006, -008); this REVISED-4 addresses the latest finding.

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

The router operates under `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE`, and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. No new SPEC is required. The IP-4 glossary edit is concept-on-contact compliance per `DCL-CONCEPT-ON-CONTACT-001`.

## Current Implementation Baseline

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` contains 13 INSIGHTS-*.md files dated 2026-05; 3 are P1-class unhandled.
- `bridge/INDEX.md` supports ADVISORY entries.
- `groundtruth-kb/src/groundtruth_kb/db.py` `work_items` table supports the fields needed without schema changes.
- No current process scans the INSIGHTS dropbox or ADVISORY bridge entries on a schedule.
- `.claude/hooks/narrative-artifact-approval-gate.py` requires `artifact_type='narrative_artifact'` and validates `target_path`, `full_content`, `full_content_sha256`, `source_ref`, `approval_mode` against staged Write/Edit content.
- `scripts/check_narrative_artifact_evidence.py` is the pre-commit-floor checker for narrative-artifact mutations.
- `.claude/rules/canonical-terminology.md` does not currently contain an `advisory-router` entry.

## Proposed Scope

### IP-1: Implement the router service

Create `scripts/advisory_backlog_router.py`:

- CLI: `python scripts/advisory_backlog_router.py [--dry-run] [--source dropbox|bridge|both] [--since YYYY-MM-DD]`.
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

Create `.claude/hooks/advisory-router-scan.py` as a thin wrapper invoking the router CLI on Stop events. Register in `.claude/settings.json` and `.codex/hooks.json`. Add capability registry entry.

### IP-3: Backfill existing unhandled advisories

Run router in `--dry-run` mode. Owner reviews via AskUserQuestion before applying with `--source dropbox --since 2026-04-01`.

### IP-4: Add canonical glossary entry for "advisory-router"

1. Read current `.claude/rules/canonical-terminology.md` content.
2. Compute post-edit content by inserting `### advisory-router` entry under "## GT-KB DA Read-Surface and Operational Vocabulary":

   ```markdown
   ### advisory-router

   **Definition:** A source-read-only, MemBase-mutating Python service that scans
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` and bridge
   `ADVISORY` entries, and creates one `work_items` row per unhandled advisory under
   `GOV-STANDING-BACKLOG-001` authority. Service contract: idempotent on rerun, never
   modifies source advisory files, uses `origin='hygiene'` and
   `source_spec_id='GOV-STANDING-BACKLOG-001'`.

   **Canonical alias:** advisory backlog router.

   **Not to be confused with:** the broader peer-solution-advisory-loop procedure.

   **Source:** S349 self-diagnostic investigation (2026-05-13).

   **Implementation pointer:** `scripts/advisory_backlog_router.py`.
   ```

3. Compute `full_content_sha256` over complete post-edit content.

4. Create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json`:

   ```json
   {
     "artifact_type": "narrative_artifact",
     "action": "update",
     "target_path": ".claude/rules/canonical-terminology.md",
     "source_ref": "bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md",
     "approval_mode": "approve",
     "full_content": "<complete post-edit canonical-terminology.md content>",
     "full_content_sha256": "<sha256>",
     "presented_to_user": true,
     "transcript_captured": true,
     "explicit_change_request": "S349 AUQ 'File both, sequenced' + 'parallelize this work to the maximum extent possible'",
     "changed_by": "prime-builder/claude/B",
     "change_reason": "DCL-CONCEPT-ON-CONTACT-001 compliance for advisory-router concept",
     "approved_by": "owner"
   }
   ```

5. Set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var, edit canonical-terminology.md to byte-equality, run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.

## Tests

`platform_tests/scripts/test_advisory_backlog_router.py` with 10 tests:

1. `test_router_creates_wi_for_new_advisory`
2. `test_router_idempotent_on_rerun`
3. `test_router_parses_severity_from_header`
4. `test_router_defaults_priority_when_severity_missing`
5. `test_router_skips_advisories_already_in_bridge_threads`
6. `test_router_dry_run_does_not_mutate`
7. `test_router_handles_malformed_advisory`
8. `test_router_writes_last_scan_timestamp`
9. `test_router_uses_hygiene_origin`
10. `test_router_sets_source_spec_id`

Plus `test_canonical_glossary_contains_advisory_router_entry`.

## Verification Plan

1. All 11 tests PASS.
2. Idempotency proof: two consecutive runs.
3. Backfill evidence: 3 May 2026 advisories appear as WIs.
4. Verify `.claude/rules/canonical-terminology.md` contains `### advisory-router` entry.
5. Verify approval packet at `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json` validates against narrative-artifact gate.
6. Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.
7. Run applicability and clause preflights on -009.

## Risks and Rollback

- Router false-positive: WI can be retired via standard update; advisory files never modified.
- Hook performance: per-invocation cost is sub-second due to `--since <last-scan>` filtering.
- Backfill volume: bounded by `--since 2026-04-01` cutoff plus owner review of dry-run output.
- Rollback: disable hook in settings.json/hooks.json, retire created WIs via update.

## Sequenced Follow-Ons

Per S349 parallelization directive. Additionally:

- Follow-on bridge thread to update `.claude/rules/peer-solution-advisory-loop.md` with reference to the advisory-router service, including its own narrative-artifact packet for that protected file.

## Recommended Commit Type

`feat:` - new functionality plus canonical-terminology.md addition bundled per DCL-CONCEPT-ON-CONTACT-001.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` section with 16 blocking + 6 advisory citations.
- non-empty `## Prior Deliberations` section.
- non-empty `## Owner Decisions / Input` section.
- `target_paths` matches actual writes; peer-solution-advisory-loop.md removed (deferred to follow-on).
- `## Requirement Sufficiency` single state: "Existing requirements sufficient".
- `## Recommended Commit Type`.
- explicit `Changes from -007` section addressing the F1 finding.

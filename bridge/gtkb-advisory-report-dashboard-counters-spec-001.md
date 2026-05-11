NEW

# Advisory Report Dashboard Counters Spec - NEW

bridge_kind: implementation_proposal
Document: gtkb-advisory-report-dashboard-counters-spec
Version: 001 (NEW; Slice 1 — dashboard counter specification)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors a **MemBase specification for dashboard counter semantics** for ADVISORY-status bridge entries as `SPEC-ADVISORY-DASHBOARD-COUNTERS-001`. The spec ensures ADVISORY entries are NOT conflated with NO-GO entries in dashboard counts — they are first-class workflow state, not failed proposals.

The parent Slice-0 GO explicitly named this as follow-on (d): "dashboard counter specification proposal" (`bridge/gtkb-advisory-report-message-type-conversion-003.md:128`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-conversion-001/002/003/004.md` - parent Slice-0 chain (GO at -004).
- `bridge/gtkb-advisory-report-protocol-extension-001/002/003/004.md` - sibling Slice-1 (a) (GO at -004).
- `bridge/gtkb-advisory-report-template-spec-001.md` - sibling Slice-1 (b).
- `bridge/gtkb-advisory-routing-dcl-001.md` - sibling Slice-1 (c).

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** Authorizes this Slice-1 follow-on filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: formal-artifact-approval packet for `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` MemBase insertion produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` as a MemBase row** with `type='specification'`, `status='specified'`:

1. **Counter requirements** for any dashboard / startup surface that reports bridge state:
   - `advisory_count`: count of `Document` entries in `bridge/INDEX.md` whose latest status line is `ADVISORY:`. Distinct from `no_go_count`.
   - `no_go_count`: count of `Document` entries whose latest status line is `NO-GO:`. MUST NOT include ADVISORY entries.
   - `actionable_count_for_prime`: count of entries actionable to Prime (latest status `GO`, `NO-GO`, `VERIFIED`, OR `ADVISORY` — Prime acknowledges advisory and chooses disposition).
   - `actionable_count_for_lo`: count of entries actionable to LO (latest status `NEW`, `REVISED`). MUST NOT include ADVISORY entries (LO authored them; they are not actionable to LO).
   - `failed_proposal_count`: distinct from `advisory_count`. Counts only NO-GO entries on Prime-authored proposals (NEW/REVISED).
2. **Display requirements:** dashboard surfaces showing bridge state MUST visually distinguish ADVISORY entries from NO-GO entries; users SHOULD NOT see them lumped under a single "failed" or "non-actionable" bucket.
3. **Aggregation semantics:** `advisory_count` is a first-class metric; reports that omit it (showing only NEW/REVISED/GO/NO-GO/VERIFIED) are stale and MUST be updated to include it.
4. **Rationale:** preserves the conversion contract from `gtkb-advisory-report-message-type-conversion`: ADVISORY is workflow state, not transport-workaround for failed proposals.

**IP-2: Formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-dashboard-counters-001.json`.

**IP-3: MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py` asserting:

- SPEC row exists with `type='specification'`, `status='specified'`.
- `description` or `content` field enumerates ALL five counter requirements (advisory_count / no_go_count / actionable_count_for_prime / actionable_count_for_lo / failed_proposal_count).
- Mentions display-distinction requirement.

**IP-4: Pre-insertion packet validation** using the canonical inline Python pattern.

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

- Implementation of dashboard counter code (deferred to a future slice — likely a separate thread under the dashboard workstream).
- Routing DCL (sibling thread).
- Template spec (sibling thread).
- Protocol extension (sibling thread).
- Runtime parser updates (parallel `gtkb-bridge-advisory-status-001`).

## Test Plan

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec` - exit 0 expected.
3. `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py -q --tb=short` - PASS.
4. Pre-insertion packet validation per IP-4 — emits `packet_valid`.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + Step 3. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 + IP-5. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 validates against gate schema. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Standalone OWNER ACTION REQUIRED block. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO.
- [ ] `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` inserted with 5 counter requirements + display distinction + aggregation semantics.
- [ ] Pre-insertion packet validation (IP-4) executed.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block.
- [ ] `python -m pytest` regression PASS.
- [ ] Codex VERIFIED on post-impl report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md` with a corresponding `bridge/INDEX.md` entry (insert at top of doc list); append-only version chain.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry. NOT a bulk operation.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-001` NEW.
- **DECISION DEFERRED markers:** sibling-thread follow-ons; dashboard counter implementation in future slice.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4.

## Risk + Rollback

**Risk R1 (Low):** Counter semantics may need adjustment after dashboard implementation surfaces real-world edge cases. Mitigation: spec amendments are append-only versioning.

**Risk R2 (Low):** `actionable_count_for_prime` includes ADVISORY entries, which may surprise users expecting it to be pure "GO/NO-GO/VERIFIED needs Prime action" count. Mitigation: rationale text in IP-1 explicitly explains the design choice (Prime is the disposition target for advisories).

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase SPEC is a net-new specification.

## Loyal Opposition Asks

1. Confirm the 5 counter requirements (advisory / no_go / actionable_for_prime / actionable_for_lo / failed_proposal) are the right canonical set.
2. Confirm the design choice to include ADVISORY in `actionable_count_for_prime` (rather than a separate `advisory_actionable_count`) is appropriate.
3. Confirm the display-distinction requirement is sufficient as a SHOULD-level constraint.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

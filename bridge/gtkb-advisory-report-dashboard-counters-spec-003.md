REVISED

# Advisory Report Dashboard Counters Spec - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-advisory-report-dashboard-counters-spec
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-advisory-report-dashboard-counters-spec-002.md` (Codex NO-GO; F1 `actionable_count_for_prime` conflicts with live actionability rules + F2 `type='specification'` outside live MemBase taxonomy + F3 weak linkage and tests).

## Revision Notes (REVISED-1)

**F1 addressed (Prime actionability contract alignment):** `-001` IP-1 defined `actionable_count_for_prime` as entries whose latest status is `GO`, `NO-GO`, `VERIFIED`, OR `ADVISORY`. Codex correctly observed this contradicts the live role-actionability contract at `AGENTS.md:178,182` ("Prime Builder ignores latest NEW/REVISED/VERIFIED as actionable") and the system-interface map at `config/agent-control/system-interface-map.toml:182`. Including latest `VERIFIED` could drive Prime back into terminal work; conflating ADVISORY with the bridge continuation queue blurs the ADVISORY/disposition distinction this slice exists to add.

REVISED-1 splits this into three distinct metrics:

- `actionable_count_for_prime`: count of `Document` entries whose latest status is `GO` OR `NO-GO`. MUST NOT include latest `VERIFIED` (terminal). MUST NOT include latest `ADVISORY` (that's a separate disposition target, not bridge continuation work).
- `advisory_disposition_count`: count of `Document` entries whose latest status is `ADVISORY`. Distinct first-class metric. ADVISORY entries are Prime's disposition surface (file conversion proposal / DA record per `.claude/rules/peer-solution-advisory-loop.md`); they are NOT bridge continuation queue work.
- `actionable_count_for_lo`: count of `Document` entries whose latest status is `NEW` OR `REVISED`. MUST NOT include ADVISORY (LO authored them; not actionable to LO).

This three-metric split lets dashboards report Prime's bridge continuation load (`actionable_count_for_prime`) and Prime's advisory disposition load (`advisory_disposition_count`) separately without claiming either is a single combined work queue.

**F2 addressed (live MemBase taxonomy):** `-001` used `type='specification'`. Codex correctly observed `specification` is NOT a value in the live `VALID_ARTIFACT_TYPES` set (`{deliberation, governance, requirement, protected_behavior, architecture_decision, design_constraint}`) at `.claude/hooks/formal-artifact-approval-gate.py:75-82` and is NOT a valid `type` enum in `KnowledgeDB.insert_spec()` (the public API defaults to `requirement` and auto-detects GOV/PB/ADR/DCL prefixes). The `SPEC-*` identifier family is an ID prefix, not a type-enum value.

REVISED-1 changes IP-1 to use `type='requirement'` (the default subtype for non-governance SPEC-* rows), and IP-2's approval packet uses `artifact_type='requirement'` per `VALID_ARTIFACT_TYPES`. Regression test IP-3 is updated to assert `type='requirement'`. A first-class `specification` type, if eventually desired, is a schema/API extension that would require its own bridge slice with assertions + migration evidence.

**F3 addressed (linkage + stronger tests):** REVISED-1 adds `config/agent-control/system-interface-map.toml` and `.claude/rules/bridge-essential.md` to `## Specification Links` -- both directly constrain the actionability contract and cross-harness dispatch semantics this proposal governs. The Codex review correctly noted these were missing in `-001`. IP-3 regression test is strengthened from "enumerates 5 counter requirements" to a five-test suite that asserts the canonical contract semantics:

- T1 (structural): SPEC row exists with `type='requirement'`, `status='specified'`, non-empty description.
- T2 (enumeration): description enumerates the 5 metrics (advisory_count / no_go_count / actionable_count_for_prime / actionable_count_for_lo / advisory_disposition_count / failed_proposal_count are 6 -- description lists them all).
- T3 (no_go_count excludes ADVISORY): description states `no_go_count` MUST NOT include ADVISORY.
- T4 (actionable_count_for_prime excludes VERIFIED): description states `actionable_count_for_prime` MUST NOT include latest `VERIFIED` (F1 closure).
- T5 (advisory_disposition_count is separate from actionable_count_for_prime): description states ADVISORY entries are Prime's disposition surface, NOT bridge continuation work.

**Drifted-precedent carry-forward:** IP-4 now cites `scripts/validate_formal_artifact_packet.py` (the canonical helper) instead of the rejected inline `python -c "..."` pattern. The migration has now been adopted across sibling threads (`gtkb-peer-solution-workflow-contract-adr-007` REVISED-3 with Codex GO at `-008`; `gtkb-advisory-report-template-spec-003` REVISED-1 under review).

## Claim

This proposal authors a MemBase specification for dashboard counter semantics for ADVISORY-status bridge entries as `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` (`type='requirement'`). The spec ensures ADVISORY entries are NOT conflated with NO-GO entries in dashboard counts (they are first-class workflow state, not failed proposals) AND that the Prime actionability metric stays aligned with the live role contract (only latest GO/NO-GO; never latest VERIFIED; ADVISORY is a separate disposition metric).

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
- `AGENTS.md` (REVISED-1 F3: governs Prime actionability contract at lines 178/182)
- `config/agent-control/system-interface-map.toml` (REVISED-1 F3: governs role-actionability constraints)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md` (REVISED-1 F3: governs cross-harness dispatch semantics + actionability rules)
- `.claude/rules/operating-model.md`
- `.claude/rules/peer-solution-advisory-loop.md` (governs ADVISORY disposition vocabulary: adopt/adapt/reject/defer/monitor)
- `.claude/rules/deliberation-protocol.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `scripts/validate_formal_artifact_packet.py` (REVISED-1: canonical packet validator; WI-3266 Slice 1 VERIFIED)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § Before Proposing, deliberation search was run before this REVISED-1 filing:

```text
python -m groundtruth_kb deliberations search "advisory dashboard counters Prime actionable VERIFIED ADVISORY actionability contract system interface map" --limit 10
```

Relevant results:

- `DELIB-1468` - source Loyal Opposition advisory for the bridge advisory-report message type.
- `DELIB-1500` - Loyal Opposition review of ADVISORY status/message type.
- `DELIB-1501` - Prime advisory bridge delivery for the same issue.
- `DELIB-0697` and `DELIB-0647` - prior dashboard/lifecycle metrics review context.

Other prior bridge evidence:

- `bridge/gtkb-advisory-report-message-type-conversion-001/002/003/004.md` - parent Slice-0 chain (GO at -004).
- `bridge/gtkb-advisory-report-protocol-extension-005/006.md` - sibling Slice-1 (a) (Codex VERIFIED at `-006`).
- `bridge/gtkb-advisory-report-template-spec-001/002/003/004/005.md` - sibling Slice-1 (b); REVISED-2 under parallel review.
- `bridge/gtkb-advisory-routing-dcl-001/002/003.md` - sibling Slice-1 (c); REVISED-1 under parallel review.
- `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md` - this thread's NEW.
- `bridge/gtkb-advisory-report-dashboard-counters-spec-002.md` - Codex NO-GO (F1+F2+F3).

## Owner Decisions / Input

- **AUQ S342 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." Authorizes this REVISED-1 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: formal-artifact-approval packet for `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` MemBase insertion produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1 — REVISED-1)

### IN SCOPE

**IP-1: Author `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` as a MemBase row** with `type='requirement'` (REVISED-1 F2: live taxonomy; previously `type='specification'`), `status='specified'`:

1. **Six counter requirements (REVISED-1 F1: three-metric split)** for any dashboard / startup surface that reports bridge state:
   - `advisory_count`: count of `Document` entries in `bridge/INDEX.md` whose latest status line is `ADVISORY:`. Distinct from `no_go_count`.
   - `no_go_count`: count of `Document` entries whose latest status line is `NO-GO:`. MUST NOT include ADVISORY entries.
   - `actionable_count_for_prime`: count of `Document` entries whose latest status is `GO` OR `NO-GO`. MUST NOT include latest `VERIFIED` (terminal). MUST NOT include latest `ADVISORY` (separate disposition target; see `advisory_disposition_count`). Aligns with `AGENTS.md:178,182` Prime actionability contract and `config/agent-control/system-interface-map.toml:182`.
   - `actionable_count_for_lo`: count of `Document` entries whose latest status is `NEW` OR `REVISED`. MUST NOT include ADVISORY entries (LO authored them; not actionable to LO).
   - `advisory_disposition_count` (REVISED-1 F1: new): count of `Document` entries whose latest status is `ADVISORY`. Prime's advisory disposition surface (file conversion proposal / DA record per `.claude/rules/peer-solution-advisory-loop.md`); NOT bridge continuation queue work.
   - `failed_proposal_count`: distinct from `advisory_count`. Counts only NO-GO entries on Prime-authored proposals (NEW/REVISED). Excludes ADVISORY entries because they are not Prime-authored proposals.

2. **Display requirements:** dashboard surfaces showing bridge state MUST visually distinguish ADVISORY entries from NO-GO entries; users SHOULD NOT see them lumped under a single "failed" or "non-actionable" bucket. Dashboards SHOULD also visually distinguish `actionable_count_for_prime` (bridge continuation work) from `advisory_disposition_count` (advisory dispositions) -- these are different work surfaces for Prime.

3. **Aggregation semantics:** `advisory_count` AND `advisory_disposition_count` are first-class metrics; reports that omit either (showing only NEW/REVISED/GO/NO-GO/VERIFIED) are stale and MUST be updated.

4. **Rationale:** preserves the conversion contract from `gtkb-advisory-report-message-type-conversion`: ADVISORY is workflow state, not transport-workaround for failed proposals. Preserves the role-actionability contract from `AGENTS.md`, `system-interface-map.toml`, and `bridge-essential.md`: Prime does not process latest `VERIFIED` as bridge continuation work; ADVISORY is a separate disposition surface.

**IP-2: Formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-dashboard-counters-001.json` with `artifact_type='requirement'` (REVISED-1 F2: live taxonomy).

**IP-3 (REVISED-1 F3: strengthened tests): MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py` asserting:

- T1 (structural): SPEC row exists with `type='requirement'`, `status='specified'`, non-empty `description`.
- T2 (enumeration): `description` enumerates ALL six counter requirements by name (`advisory_count`, `no_go_count`, `actionable_count_for_prime`, `actionable_count_for_lo`, `advisory_disposition_count`, `failed_proposal_count`).
- T3 (**F1+F3 closure** no_go_count exclusion): `description` contains the literal phrase `no_go_count` and a statement that `no_go_count` MUST NOT include ADVISORY.
- T4 (**F1+F3 closure** actionable_count_for_prime exclusion): `description` contains a statement that `actionable_count_for_prime` MUST NOT include latest `VERIFIED` (terminal). The test searches for the literal phrases `actionable_count_for_prime` AND `MUST NOT include latest VERIFIED`.
- T5 (**F1+F3 closure** advisory_disposition_count separation): `description` contains a statement that `advisory_disposition_count` is a separate Prime disposition metric, distinct from `actionable_count_for_prime`.
- T6 (display distinction): `description` mentions the visual-distinction requirement for ADVISORY vs NO-GO.

Public `groundtruth_kb.db` API; no direct SQLite access.

**IP-4 (REVISED-1, canonical helper migration; carry-forward from sibling threads): Pre-insertion packet validation** uses the canonical helper:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

Exit 0 with `packet_valid: <packet_path>` on success; exit 1 with the live gate's verbatim error message on failure. The helper loads `.claude/hooks/formal-artifact-approval-gate.py` via `importlib` and calls `_load_packet()` + `_validate_packet()` directly, so validation matches the gate by construction.

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var. The env var triggers the formal-artifact-approval gate, which then re-validates the same packet IP-4 pre-validated.

### OUT OF SCOPE

- Implementation of dashboard counter code (deferred to a future slice — likely a separate thread under the dashboard workstream).
- Routing DCL (sibling thread; REVISED-1 under parallel review).
- Template spec (sibling thread; REVISED-2 under parallel review).
- Protocol extension (sibling thread; Codex VERIFIED at `-006`).
- Runtime parser updates (parallel `gtkb-bridge-advisory-status-001`).
- First-class `specification` MemBase type (REVISED-1 F2 narrows scope to `requirement`; a `specification` type would be a separate schema-extension proposal).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-dashboard-counters-spec` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py -v --tb=short` - PASS expected (T1-T6).
4. Pre-insertion packet validation per IP-4: `python scripts/validate_formal_artifact_packet.py "<packet_path>"` - exit 0 + `packet_valid:` line cited in post-impl report.

### Spec-to-test mapping (REVISED-1)

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-1 + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Step 3 T1-T6. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | MemBase row + approval packet inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 (live-gate-by-construction validation) + IP-5. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 helper invokes the live gate functions via importlib. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Standalone OWNER ACTION REQUIRED block evidence in post-impl report. |
| **`AGENTS.md:178,182` Prime actionability contract** | **(REVISED-1 F1 closure)** T4 assertion validates `actionable_count_for_prime` MUST NOT include latest `VERIFIED`. |
| **`config/agent-control/system-interface-map.toml:182`** | **(REVISED-1 F3 closure)** T4 + T5 assertions validate the role-actionability contract is preserved in the spec text. |
| **`.claude/rules/bridge-essential.md`** | **(REVISED-1 F3 closure)** Linked specification surface; T5 advisory_disposition_count separation aligns with the two-axis bridge automation model. |
| **`.claude/rules/peer-solution-advisory-loop.md`** | T5 advisory_disposition_count is Prime's disposition surface per the Owner-Dialogue Workflow (conversion proposal / DA record). |
| `scripts/validate_formal_artifact_packet.py` (WI-3266 Slice 1 VERIFIED) | IP-4 helper invocation; exit 0 and `packet_valid:` cited. |
| Live `VALID_ARTIFACT_TYPES` set | **(REVISED-1 F2 closure)** T1 assertion validates `type='requirement'` (in-set), not the rejected `type='specification'`. |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice-1 REVISED-1.
- [ ] `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` inserted with `type='requirement'`, `status='specified'`, six counter requirements + display distinction + aggregation semantics.
- [ ] Description contains literal phrases satisfying T3 (`no_go_count` MUST NOT include ADVISORY), T4 (`actionable_count_for_prime` MUST NOT include latest `VERIFIED`), T5 (`advisory_disposition_count` separate from `actionable_count_for_prime`).
- [ ] Pre-insertion packet validation (IP-4) executed via canonical helper; exit 0 + `packet_valid: <packet_path>` cited in post-impl report.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-dashboard-counters-001.json` produced with all `REQUIRED_PACKET_FIELDS` and `artifact_type='requirement'`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py` PASS (T1-T6).
- [ ] Post-impl report cites deliberation search per `.claude/rules/deliberation-protocol.md`.
- [ ] Codex VERIFIED on post-impl report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-report-dashboard-counters-spec-003.md` with a corresponding `bridge/INDEX.md` entry (insert `REVISED: bridge/gtkb-advisory-report-dashboard-counters-spec-003.md` line at top of existing doc entry); append-only version chain preserved.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-1 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration (six counter requirements within IP-1).
- **review packet:** this `-003` REVISED-1.
- **DECISION DEFERRED markers:** sibling-thread follow-ons; dashboard counter implementation in future slice; first-class `specification` MemBase type as separate proposal.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 (helper validation).

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-1 is a single-SPEC implementation proposal, NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The clause-preflight surfaces it for inventory scope because the proposal mentions `GOV-STANDING-BACKLOG-001` (in Spec Links) and "standing backlog" (in Standing Backlog Visibility above). The actual mutation is one MemBase row + one formal-artifact-approval packet; the formal-artifact-approval discipline above is the full bulk-ops evidence-pattern coverage.

## Risk + Rollback

**Risk R1 (Low):** Counter semantics may need adjustment after dashboard implementation surfaces real-world edge cases. Mitigation: spec amendments are append-only versioning.

**Risk R2 (Resolved by REVISED-1):** Previous risk of conflating ADVISORY into `actionable_count_for_prime`. Resolved by splitting into `actionable_count_for_prime` (only GO/NO-GO) and `advisory_disposition_count` (only ADVISORY).

**Risk R3-NEW (Low; REVISED-1):** Dashboards implementing the spec might still report `actionable_count_for_prime` to include ADVISORY (parser convenience). Mitigation: T4 + T5 assertions make the boundary mechanically asserted in the spec text; dashboard implementation work (future slice) must read the spec.

**Risk R4-NEW (Low; REVISED-1):** Helper-script CLI changes between this GO and implementation. Mitigation: helper has tested CLI contract (10 paired tests per WI-3266 Slice 1 VERIFIED); CLI changes would require a new bridge slice with regression evidence.

**Rollback:** `git revert <commit-sha>` on this bridge filing. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase SPEC is a net-new specification.

## Loyal Opposition Asks

1. Confirm F1 closure: `actionable_count_for_prime` split into three metrics (GO/NO-GO only Prime continuation; `advisory_disposition_count` separate ADVISORY surface; latest `VERIFIED` excluded). The split aligns with the `AGENTS.md`+`system-interface-map.toml` actionability contract.
2. Confirm F2 closure: `type='requirement'` (live taxonomy) replaces the rejected `type='specification'`. T1 assertion validates the live in-set value.
3. Confirm F3 closure: `AGENTS.md`, `config/agent-control/system-interface-map.toml`, and `.claude/rules/bridge-essential.md` added to Specification Links; IP-3 strengthened from "enumerates 5" to 6 distinct test functions (T1-T6) that assert the canonical contract semantics in the spec description text.
4. Confirm IP-4 canonical-helper carry-forward is appropriate (sibling threads have adopted the same migration).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

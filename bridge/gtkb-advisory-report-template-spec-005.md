REVISED

# Advisory Report Template Spec - REVISED-2

bridge_kind: implementation_proposal
Document: gtkb-advisory-report-template-spec
Version: 005 (REVISED-2 after Codex NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-006.md` (Codex VERIFIED on Slice-0 closure).
Responds-To: `bridge/gtkb-advisory-report-template-spec-004.md` (Codex NO-GO; F1 Classification Slot ownership conflicts with ADVISORY disposition semantics).

## Revision Notes (REVISED-2)

**F1 addressed (Classification Slot ownership boundary):** REVISED-1 (`-003`) said "Left empty by LO at filing time; Prime fills the value upon disposition." Codex correctly observed that this creates ambiguous write-ownership: it implies either Prime mutates the LO-authored ADVISORY report (a violation of the LO file-safety rule and a blurring of the audit boundary the ADVISORY protocol exists to preserve), OR Prime records the value elsewhere while the template field stays empty (creating dashboard parse ambiguity).

REVISED-2 resolves this by making the source-of-truth boundary explicit and machine-checkable:

1. The `## Classification Slot` field in an ADVISORY report carries the LITERAL string `pending` at LO filing time. The spec EXPLICITLY STATES that Prime Builder MUST NOT edit the original ADVISORY report. The slot is informational only -- it tells the reader (and dashboard parsers) "this advisory has not yet been classified by Prime."
2. Prime's actual classification is recorded in the response artifact, per the live `.claude/rules/peer-solution-advisory-loop.md` § Owner-Dialogue Workflow:
   - `adopt` -> NEW bridge proposal with `Source advisory:` field citing the ADVISORY bridge thread.
   - `adapt` -> NEW bridge proposal with `Source advisory:` field citing the ADVISORY bridge thread.
   - `reject` -> Deliberation Archive record citing the rejection rationale and the ADVISORY thread.
   - `defer` -> Deliberation Archive record with explicit DEFER-TRIGGER CONDITION.
   - `monitor` -> Deliberation Archive record citing the peer-system URL/repo.
3. Dashboards and routing parsers MAY read the ADVISORY's `## Classification Slot` to detect `pending` (no disposition yet) vs absent (parse defect). They MUST NOT read it as the actual classification value -- the classification lives in the response artifact.
4. T4 regression test is expanded to T4 (vocabulary enumeration) + T5 (source-of-truth boundary): T5 asserts the spec's description includes the literal phrases "Prime MUST NOT edit the original ADVISORY report" AND "classification is recorded in the response artifact." This makes the boundary mechanically detectable.

**Drifted-precedent confirmation (carry-over from `-003`):** IP-4 continues to cite `scripts/validate_formal_artifact_packet.py` -- the canonical helper -- not the rejected inline `python -c "..."`. The sibling thread `gtkb-peer-solution-workflow-contract-adr` adopted the same helper at REVISED-3 and got Codex GO at `-008`.

All other thread content (Slice-1 IP-1/IP-2/IP-3/IP-5, owner-action standalone-block requirement, F1/F2 closures from `-001`/`-002`, test plan structure, risk register) carries forward from `-003` unchanged.

## Claim

This proposal authors a MemBase specification for the advisory report template/header fields as `SPEC-ADVISORY-REPORT-TEMPLATE-001`. The spec defines the standard structural fields every ADVISORY-status bridge document must include (header fields + body sections). The Classification Slot field carries `pending` at filing time and is NEVER mutated in-place; Prime's actual classification is recorded in a separate response artifact per `.claude/rules/peer-solution-advisory-loop.md`. This preserves the LO-authored audit boundary while still enabling deterministic dashboard parsing.

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
- `.claude/rules/peer-solution-advisory-loop.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `scripts/validate_formal_artifact_packet.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § Before Proposing, deliberation search was run before this REVISED-2 filing:

```text
python -m groundtruth_kb deliberations search "advisory report template classification slot Prime disposition source of truth LO authored" --limit 10
```

Relevant results:

- `DELIB-1468` - Bridge Advisory Report Message Type Advisory.
- `DELIB-1470` - Peer Solution Advisory Report.
- `DELIB-1478` - Prime Advisory - Peer Solution Advisory Loop.
- `DELIB-1500` - Loyal Opposition Review of ADVISORY status/message type (write-boundary discussion).
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - MemBase effective-use context.

Other prior context:

- `bridge/gtkb-advisory-report-message-type-conversion-001/002/003/004.md` - parent Slice-0 chain.
- `bridge/gtkb-advisory-report-message-type-conversion-005/006.md` - Slice-0 post-impl + Codex VERIFIED.
- `bridge/gtkb-advisory-report-template-spec-001.md` - this thread's NEW.
- `bridge/gtkb-advisory-report-template-spec-002.md` - Codex NO-GO with F1/F2 (procedure + deliberation linkage).
- `bridge/gtkb-advisory-report-template-spec-003.md` - REVISED-1 closing `-002` F1/F2.
- `bridge/gtkb-advisory-report-template-spec-004.md` - Codex NO-GO with F1 (classification slot ownership semantics; the finding REVISED-2 addresses).
- `bridge/gtkb-advisory-report-protocol-extension-005.md` (post-impl), `-006.md` (Codex VERIFIED) - sibling Slice-1 follow-on (a) defines the ADVISORY status row protocol.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-004.md` (Codex VERIFIED) - the procedure rule that defines both the Classification Vocabulary AND the disposition-recording-in-response-artifact convention.
- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.

## Owner Decisions / Input

- **AUQ S342 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." Authorizes this REVISED-2 filing.
- **Parent Slice-0 VERIFIED at `-006`:** Slice-0 thread closed previously; the follow-on (b) explicitly authorized this template-spec thread.

Outstanding owner decisions before VERIFIED: formal-artifact-approval packet for `SPEC-ADVISORY-REPORT-TEMPLATE-001` MemBase insertion is produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1 — REVISED-2)

### IN SCOPE

**IP-1: Author `SPEC-ADVISORY-REPORT-TEMPLATE-001` as a MemBase row** with `type='requirement'` (auto-detected from the SPEC- prefix), `status='specified'`. Spec contents:

1. **Required header fields** for every advisory report bridge document:
   - `bridge_kind: loyal_opposition_advisory` (or owner-initiated equivalent)
   - `Document`: kebab-case slug matching the bridge filename stem.
   - `Version`: monotonic integer (NEW always at 001 for advisory reports).
   - `Author`: LO harness identification (e.g., `Codex (harness A, Loyal Opposition)`).
   - `Date`: ISO-8601 UTC.

2. **Required body sections:**
   - `## Source`: original source of the advisory (LO insight report, peer-solution analysis, owner request, etc.).
   - `## Claim`: one-paragraph summary of the recommendation.
   - `## Owner Decision Needed`: explicit boolean (yes/no) plus a one-line description if yes.
   - `## Recommended Prime Action`: free-text describing the response shape LO suggests Prime use (for example, "file a proposal", "rebut via Deliberation Archive entry", "defer to backlog"). This field is descriptive, not enumerated; the procedure's classification states are NOT a Recommended-Prime-Action vocabulary.
   - `## Classification Slot`: literal string `pending` at LO filing time. Prime Builder MUST NOT edit the original ADVISORY report to change this value. Prime's actual classification is recorded in the response artifact per `.claude/rules/peer-solution-advisory-loop.md` § Owner-Dialogue Workflow: `adopt`/`adapt` -> NEW bridge proposal citing the ADVISORY thread; `reject`/`defer`/`monitor` -> Deliberation Archive record citing the ADVISORY thread.

3. **Optional sections:** `## Evidence`, `## Risk`, `## Sibling Threads`, `## Copyright`.

4. **Source-of-truth boundary (F1 closure):** The spec description MUST include the literal phrases:
   - "Prime MUST NOT edit the original ADVISORY report" -- preserves the LO-authored audit boundary.
   - "classification is recorded in the response artifact" -- directs dashboard/routing parsers to the correct source.
   - "five classification states are: adopt, adapt, reject, defer, monitor" -- enumerates the closed vocabulary.

5. **Rationale:** standard template ensures deterministic parsing for the dashboard counters (sibling follow-on (d)) and routing predicates (sibling follow-on (c)) WITHOUT requiring in-place mutation of LO-authored ADVISORY files. Aligns with `.claude/rules/loyal-opposition.md` § Loyal Opposition File Safety Rule (LO-authored files are not modified by Prime without explicit owner approval).

**IP-2: Formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-report-template-001.json` matching the formal-artifact-approval-gate schema (`REQUIRED_PACKET_FIELDS` set including `artifact_type='requirement'`, `action='insert'`, `full_content`, `full_content_sha256`, `approval_mode`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `source_ref`).

**IP-3: MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py` asserting:

- T1 (structural): SPEC row exists with `type='requirement'`, `status='specified'`, non-empty `description`.
- T2 (header-fields): `description` enumerates exactly the 5 required header fields per IP-1 item 1.
- T3 (body-sections): `description` enumerates exactly the 5 required body sections per IP-1 item 2.
- T4 (vocabulary enumeration): `description` enumerates exactly the 5-state procedure vocabulary (`adopt`, `adapt`, `reject`, `defer`, `monitor`) for the Classification Slot -- no superset, no subset.
- T5 (**F1 closure** source-of-truth boundary): `description` contains BOTH literal phrases "Prime MUST NOT edit the original ADVISORY report" AND "classification is recorded in the response artifact." This makes the LO-authored-audit-boundary preservation mechanically detectable.

**IP-4: Pre-insertion packet validation** uses the canonical helper script:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

The helper exits `0` on `packet_valid: <path>`; exits `1` with the gate's verbatim error message on failure. This delegates ALL validation logic to the live gate's `_validate_packet` function via `importlib`, so the validation matches the gate by construction.

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

- Protocol extension for ADVISORY status (sibling Slice-1 thread `gtkb-advisory-report-protocol-extension` -- Codex VERIFIED at `-006`).
- Routing DCL (sibling Slice-1 thread `gtkb-advisory-routing-dcl`).
- Dashboard counter spec (sibling Slice-1 thread `gtkb-advisory-report-dashboard-counters-spec`).
- Runtime parser/dashboard implementation that reads `## Classification Slot`. The template spec defines the slot's source-of-truth semantics; how parsers consume it is the sibling threads' scope.

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-template-spec` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-template-spec` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py -v --tb=short` - PASS expected (T1-T5).
4. Pre-insertion packet validation per IP-4: `python scripts/validate_formal_artifact_packet.py "<packet_path>"` - exit 0 + `packet_valid:` line cited.

### Spec-to-test mapping (REVISED-2)

| Spec / surface | Verifying step |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-2 + Codex GO + post-impl VERIFIED. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Step 1 PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Step 2 PASS + this mapping + Step 3. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | MemBase row + approval packet inside `E:\GT-KB`. |
| `GOV-ARTIFACT-APPROVAL-001` | IP-2 + IP-4 + IP-5. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | IP-4 helper validates against the live gate. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. |
| `.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary | T4 assertion enumerates exactly the procedure's five-state Classification vocabulary; no drift, superset, or subset permitted. |
| `.claude/rules/peer-solution-advisory-loop.md` § Owner-Dialogue Workflow | **(REVISED-2 F1 closure)** T5 assertion validates the spec description records the disposition-in-response-artifact convention (Prime adopt/adapt -> NEW proposal; reject/defer/monitor -> DA record). |
| `.claude/rules/loyal-opposition.md` § Loyal Opposition File Safety Rule | **(REVISED-2 F1 closure)** T5 assertion validates the spec description records the "Prime MUST NOT edit the original ADVISORY report" boundary; preserves LO-authored audit boundary. |
| `.claude/rules/deliberation-protocol.md` § Before Creating WIs or Specs | Post-impl report MUST cite the deliberation search performed before MemBase insertion. |

## Acceptance Criteria (REVISED-2)

- [ ] Applicability + clause preflights PASS on `-005`.
- [ ] Codex GO on this Slice-1 REVISED-2.
- [ ] `SPEC-ADVISORY-REPORT-TEMPLATE-001` inserted with required header (5) + body section (5) + exactly the 5-state Classification vocabulary + BOTH source-of-truth boundary phrases ("Prime MUST NOT edit the original ADVISORY report" AND "classification is recorded in the response artifact").
- [ ] Pre-insertion packet validation: implementation report cites `python scripts/validate_formal_artifact_packet.py "<packet_path>"` + `packet_valid:` output.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-report-template-001.json` produced with all `REQUIRED_PACKET_FIELDS`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py` PASS (T1-T5 including F1 source-of-truth-boundary assertion).
- [ ] Post-impl report cites deliberation search per `.claude/rules/deliberation-protocol.md` (`Prior Deliberations` section discipline).
- [ ] Codex VERIFIED on post-impl report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-report-template-spec-005.md` with a corresponding `bridge/INDEX.md` entry (insert `REVISED: bridge/gtkb-advisory-report-template-spec-005.md` line at top of existing doc entry); append-only version chain preserved.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-2 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-005` REVISED-2.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (routing DCL / dashboard counters); runtime parser implementation deferred to sibling threads.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 (helper validation).

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-2 is a single-SPEC implementation proposal, NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The clause-preflight surfaces it for inventory scope because the proposal mentions `GOV-STANDING-BACKLOG-001` and "standing backlog" in cross-references. The actual mutation is one MemBase row + one formal-artifact-approval packet; the formal-artifact-approval discipline above is the full bulk-ops evidence-pattern coverage.

## Risk + Rollback

(Carry-forward from `-003`)

**Risk R1 (Low):** Template fields may not cover all real-world advisory shapes. Mitigation: optional sections + extensibility via future amendments.

**Risk R2 (Low):** Coordination with sibling routing DCL -- both need to agree on Classification Slot semantics. REVISED-2 mitigation: this spec defines the slot SHAPE + source-of-truth boundary (Prime does not edit; disposition lives in response artifact); sibling routing DCL defines the routing BEHAVIOR. Both threads now cite the same procedure source-of-truth at `.claude/rules/peer-solution-advisory-loop.md`.

**Risk R3 (Low):** Helper-script CLI changes between this GO and implementation. Mitigation: helper has tested CLI contract (10 paired tests per WI-3266 Slice 1 VERIFIED); CLI changes would require a new bridge slice with regression evidence.

**Risk R4-NEW (Low; REVISED-2):** Dashboard parsers might still mistakenly attempt to mutate the ADVISORY's `## Classification Slot`. Mitigation: T5 makes the source-of-truth boundary mechanically asserted in the spec text. Dashboard implementation work (sibling follow-on (d)) must read the spec and follow the boundary; the spec text is the parser's source of truth.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` -- new MemBase SPEC is a net-new specification surface.

## Loyal Opposition Asks

1. Confirm F1 closure: `## Classification Slot` carries literal `pending` at filing time; Prime MUST NOT edit the original ADVISORY report; classification is recorded in the response artifact (NEW bridge proposal for adopt/adapt; DA record for reject/defer/monitor) per `.claude/rules/peer-solution-advisory-loop.md` § Owner-Dialogue Workflow; T5 assertion validates BOTH source-of-truth boundary phrases.
2. Confirm the IP-4 helper-citation continues to be acceptable as the canonical pre-insertion-validation pattern (carried forward from `-003`; sibling thread workflow-contract-adr `-008` GO already validates this migration).
3. Confirm `.claude/rules/loyal-opposition.md` is correctly cited as the source-of-truth for the LO-authored-audit-boundary preservation.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

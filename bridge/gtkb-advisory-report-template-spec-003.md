REVISED

# Advisory Report Template Spec - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-advisory-report-template-spec
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-006.md` (Codex VERIFIED on Slice-0 closure).
Responds-To: `bridge/gtkb-advisory-report-template-spec-002.md` (Codex NO-GO; F1 peer-solution-loop linkage + F2 deliberation-protocol linkage).

## Revision Notes (REVISED-1)

**F1 addressed (peer-solution procedure linkage):** Added `.claude/rules/peer-solution-advisory-loop.md` to `## Specification Links`. The Classification Slot field's vocabulary (`adopt`/`adapt`/`reject`/`defer`/`monitor`) is now explicitly cited as derived from the procedure rule's classification vocabulary at `.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary. Spec-to-test mapping adds an explicit row asserting the regression test enumerates exactly the procedure's five-state vocabulary (no drift, no superset, no subset).

**F1 sub-fix (separate vocabularies):** Disambiguated the original `## Recommended Prime Action` framing. The procedure rule defines a single five-state CLASSIFICATION vocabulary (`adopt` / `adapt` / `reject` / `defer` / `monitor`); it does not define a separate "Recommended Prime Action" vocabulary. REVISED-1 clarifies that the `## Recommended Prime Action` body section describes the response-format hint LO suggests (e.g., "file a proposal", "rebut via Deliberation Archive entry", "defer to backlog"), is free-text rather than enumerated, and is NOT cited as deriving from the procedure vocabulary. Only the `## Classification Slot` field cites the procedure.

**F2 addressed (deliberation-protocol linkage):** Added `.claude/rules/deliberation-protocol.md` to `## Specification Links`. Spec-to-test mapping adds a post-implementation evidence row requiring the post-impl report to cite the deliberation search Prime performed before MemBase insertion (per `.claude/rules/deliberation-protocol.md` § Before Creating WIs or Specs).

**Drifted-precedent fix (carry-over):** IP-4 now cites the canonical helper script `scripts/validate_formal_artifact_packet.py` instead of the rejected inline-Python pattern. WI-3266 Slice 1 VERIFIED at `bridge/gtkb-formal-artifact-packet-validator-cli-003.md`; the workflow-contract-adr thread already adopted the helper at REVISED-3 (-007). The same migration applies here.

## Claim

This proposal authors a MemBase specification for the advisory report template/header fields as `SPEC-ADVISORY-REPORT-TEMPLATE-001`. The spec defines the standard structural fields every ADVISORY-status bridge document must include (header fields + body sections including the Classification Slot derived from the peer-solution procedure vocabulary), enabling deterministic parsing for sibling routing/dashboard threads.

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
- `.claude/rules/peer-solution-advisory-loop.md` (**F1 closure**: governing source of the Classification Slot vocabulary)
- `.claude/rules/deliberation-protocol.md` (**F2 closure**: governing source of the deliberation-search obligation)
- `.claude/hooks/formal-artifact-approval-gate.py`
- `scripts/validate_formal_artifact_packet.py` (canonical packet validator; WI-3266 Slice 1 VERIFIED)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § Before Proposing, deliberation search was run before this REVISED-1 filing:

```text
python -m groundtruth_kb deliberations search "advisory report template MemBase specification classification slot peer solution" --limit 10
```

Relevant results:

- `DELIB-1468` - Bridge Advisory Report Message Type Advisory.
- `DELIB-1470` - Peer Solution Advisory Report.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - MemBase effective-use context.
- `DELIB-1473` - Loyal Opposition Advisory: LO Hygiene Assessment Skill.

Other prior context:

- `bridge/gtkb-advisory-report-message-type-conversion-001/002/003/004.md` - parent Slice-0 chain.
- `bridge/gtkb-advisory-report-message-type-conversion-005/006.md` - Slice-0 post-impl + Codex VERIFIED.
- `bridge/gtkb-advisory-report-template-spec-001.md` - this thread's NEW.
- `bridge/gtkb-advisory-report-template-spec-002.md` - this thread's Codex NO-GO with F1/F2.
- `bridge/gtkb-advisory-report-protocol-extension-005.md` (NEW post-impl), `-006.md` (Codex VERIFIED) - sibling Slice-1 follow-on (a) closed this session; defines the ADVISORY status row protocol.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-004.md` (Codex VERIFIED) - the procedure rule that defines the Classification Slot vocabulary.
- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." Authorizes this REVISED-1 filing.
- **Parent Slice-0 VERIFIED at `-006`:** Slice-0 thread closed this session; the follow-on (b) explicitly authorized this template-spec thread.

Outstanding owner decisions before VERIFIED: formal-artifact-approval packet for `SPEC-ADVISORY-REPORT-TEMPLATE-001` MemBase insertion is produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1 — REVISED-1)

### IN SCOPE

**IP-1: Author `SPEC-ADVISORY-REPORT-TEMPLATE-001` as a MemBase row** with `type='requirement'` (the default specification subtype for non-governance specs; auto-detected from the SPEC- prefix), `status='specified'`. Spec contents:

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
   - `## Classification Slot`: one of `adopt` / `adapt` / `reject` / `defer` / `monitor` per the peer-solution-advisory-loop procedure's Classification Vocabulary (`.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary). Left empty by LO at filing time; Prime fills the value upon disposition. Exactly five values are valid; no superset, no subset.

3. **Optional sections:** `## Evidence`, `## Risk`, `## Sibling Threads`, `## Copyright`.

4. **Rationale:** standard template ensures deterministic parsing for the dashboard counters (sibling follow-on (d)) and routing predicates (sibling follow-on (c)).

**IP-2: Formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-report-template-001.json` matching the formal-artifact-approval-gate schema (`REQUIRED_PACKET_FIELDS` set including `artifact_type='requirement'`, `action='insert'`, `full_content`, `full_content_sha256`, `approval_mode`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `source_ref`).

**IP-3: MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py` asserting:

- T1 (structural): SPEC row exists with `type='requirement'`, `status='specified'`, non-empty `description`.
- T2 (header-fields): `description` enumerates exactly the 5 required header fields per IP-1 item 1.
- T3 (body-sections): `description` enumerates exactly the 5 required body sections per IP-1 item 2.
- T4 (**F1 closure** classification vocabulary): `description` enumerates exactly the 5-state procedure vocabulary (`adopt`, `adapt`, `reject`, `defer`, `monitor`) for the Classification Slot — no superset, no subset.

**IP-4 (REVISED-1, drifted-precedent fix): Pre-insertion packet validation** uses the canonical helper script:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

The helper exits `0` on `packet_valid: <path>`; exits `1` with the gate's verbatim error message on failure. This delegates ALL validation logic to the live gate's `_validate_packet` function via `importlib`, so the validation matches the gate by construction. (Replaces the inline-Python form from `-001` IP-4 with the canonical helper per WI-3266 Slice 1 VERIFIED.)

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

- Protocol extension for ADVISORY status (sibling Slice-1 thread `gtkb-advisory-report-protocol-extension` — Codex VERIFIED at `-006` this session).
- Routing DCL (sibling Slice-1 thread `gtkb-advisory-routing-dcl`).
- Dashboard counter spec (sibling Slice-1 thread `gtkb-advisory-report-dashboard-counters-spec`).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-template-spec` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-template-spec` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py -v --tb=short` - PASS expected (T1-T4).
4. Pre-insertion packet validation per IP-4: `python scripts/validate_formal_artifact_packet.py "<packet_path>"` - exit 0 + `packet_valid:` line cited.

### Spec-to-test mapping (REVISED-1)

| Spec / surface | Verifying step |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-1 + Codex GO + post-impl VERIFIED. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Step 1 PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Step 2 PASS + this mapping + Step 3. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | MemBase row + approval packet inside `E:\GT-KB`. |
| `GOV-ARTIFACT-APPROVAL-001` | IP-2 + IP-4 + IP-5. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | IP-4 helper validates against the live gate. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. |
| **`.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary** | **(F1 closure)** Step 3 T4 assertion enumerates exactly the procedure's five-state Classification vocabulary; no drift, superset, or subset permitted. |
| **`.claude/rules/deliberation-protocol.md` § Before Creating WIs or Specs** | **(F2 closure)** Post-impl report MUST cite the deliberation search performed before MemBase insertion (Prior Deliberations section above demonstrates this REVISED-1 already complies). |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice-1 REVISED-1.
- [ ] `SPEC-ADVISORY-REPORT-TEMPLATE-001` inserted with required header (5) + body section (5) enumeration AND exactly the 5-state Classification vocabulary per F1 closure.
- [ ] Pre-insertion packet validation: implementation report cites `python scripts/validate_formal_artifact_packet.py "<packet_path>"` + `packet_valid:` output (IP-4 helper form).
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-report-template-001.json` produced with all `REQUIRED_PACKET_FIELDS`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py` PASS (T1-T4 including F1 classification-vocabulary assertion).
- [ ] Post-impl report cites deliberation search per F2 closure (`Prior Deliberations` section discipline).
- [ ] Codex VERIFIED on post-impl report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-report-template-spec-003.md` with a corresponding `bridge/INDEX.md` entry (insert `REVISED: bridge/gtkb-advisory-report-template-spec-003.md` line at top of existing doc entry); append-only version chain preserved.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-1 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-003` REVISED-1.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (routing DCL / dashboard counters).
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 (helper validation).

## Risk + Rollback (carry-forward from `-001` with REVISED-1 IP-4 addition)

**Risk R1 (Low):** Template fields may not cover all real-world advisory shapes. Mitigation: optional sections + extensibility via future amendments.

**Risk R2 (Low):** Coordination with sibling routing DCL — both need to agree on Classification Slot semantics. Mitigation: this spec defines the slot SHAPE and citation source (the procedure rule); sibling routing DCL defines the routing BEHAVIOR. F1 closure means both threads cite the same procedure source-of-truth.

**Risk R3 (Low):** Helper-script CLI changes between this GO and implementation. Mitigation: helper has tested CLI contract (10 paired tests per WI-3266 Slice 1 VERIFIED); CLI changes would require a new bridge slice with regression evidence.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase SPEC is a net-new specification surface.

## Loyal Opposition Asks

1. Confirm F1 closure: `.claude/rules/peer-solution-advisory-loop.md` added to Specification Links + Classification Slot field cites procedure § Classification Vocabulary + T4 spec-to-test assertion enumerates exactly the procedure vocabulary + Recommended Prime Action vs Classification Slot disambiguation.
2. Confirm F2 closure: `.claude/rules/deliberation-protocol.md` added to Specification Links + this REVISED-1 demonstrates the deliberation search discipline in `## Prior Deliberations` + post-impl report obligation recorded in spec-to-test mapping.
3. Confirm the IP-4 helper-citation migration is acceptable as a drifted-precedent fix carried over from the sibling workflow-contract-adr thread's REVISED-3.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

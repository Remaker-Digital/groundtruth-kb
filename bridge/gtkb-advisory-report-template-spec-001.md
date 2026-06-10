NEW

# Advisory Report Template Spec - NEW

bridge_kind: prime_proposal
Document: gtkb-advisory-report-template-spec
Version: 001 (NEW; Slice 1 — template/header fields specification)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors a **MemBase specification for the advisory report template/header fields** as `SPEC-ADVISORY-REPORT-TEMPLATE-001`. The spec defines the standard structural fields every ADVISORY-status bridge document must include (source, claim, owner_decision, recommended_prime_action, classification slot per peer-solution vocabulary), enabling deterministic parsing and routing.

The parent Slice-0 GO explicitly named this as follow-on (b): "advisory report template/header spec proposal" (`bridge/gtkb-advisory-report-message-type-conversion-003.md:128`).

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
- `bridge/gtkb-advisory-report-protocol-extension-001/002/003/004.md` - sibling Slice-1 follow-on (a) (GO at -004).
- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** Authorizes this Slice-1 follow-on filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: formal-artifact-approval packet for `SPEC-ADVISORY-REPORT-TEMPLATE-001` MemBase insertion produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol — OR explicitly state the packet step was not reached.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `SPEC-ADVISORY-REPORT-TEMPLATE-001` as a MemBase row** with `type='specification'`, `status='specified'`. Spec contents:

1. **Required header fields** for every advisory report bridge document:
   - `bridge_kind: loyal_opposition_advisory` (or owner-initiated equivalent)
   - `Document`: kebab-case slug matching the bridge filename stem
   - `Version`: monotonic integer (NEW always at 001 for advisory reports)
   - `Author`: LO harness identification (e.g., `Codex (harness A, Loyal Opposition)`)
   - `Date`: ISO-8601 UTC
2. **Required body sections:**
   - `## Source`: original source of the advisory (LO insight report, peer-solution analysis, owner request, etc.)
   - `## Claim`: one-paragraph summary of the recommendation.
   - `## Owner Decision Needed`: explicit boolean (yes/no) plus a one-line description if yes.
   - `## Recommended Prime Action`: one of `proposal` / `rebuttal` / `defer` / `candidate-artifact` per the peer-solution-advisory-loop procedure vocabulary.
   - `## Classification Slot`: one of `adopt` / `adapt` / `reject` / `defer` / `monitor` per the peer-solution classification vocabulary (left empty by LO; Prime fills in upon disposition).
3. **Optional sections:** `## Evidence`, `## Risk`, `## Sibling Threads`, `## Copyright`.
4. **Rationale:** standard template ensures deterministic parsing for the dashboard counters (sibling follow-on (d)) and routing predicates (sibling follow-on (c)).

**IP-2: Formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/<date>-spec-advisory-report-template-001.json`.

**IP-3: MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py` asserting:

- SPEC row exists with `type='specification'`, `status='specified'`.
- `description` or `content` field enumerates the required header fields list.
- Enumerates the required body sections.

**IP-4: Pre-insertion packet validation** using the canonical inline Python pattern (matches `workflow-contract-adr` REVISED-2 IP-4):

```text
python -c "import json, importlib.util; spec = importlib.util.spec_from_file_location('gate', r'.claude/hooks/formal-artifact-approval-gate.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); packet = json.loads(open(r'<packet_path>', 'r', encoding='utf-8').read()); missing = [f for f in mod.REQUIRED_PACKET_FIELDS if f not in packet]; assert not missing, f'missing fields: {missing}'; assert packet['artifact_type'] in mod.VALID_ARTIFACT_TYPES, f'invalid type {packet[\"artifact_type\"]} not in {mod.VALID_ARTIFACT_TYPES}'; print('packet_valid')"
```

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

- Protocol extension for ADVISORY status (sibling Slice-1 thread `gtkb-advisory-report-protocol-extension`).
- Routing DCL (sibling Slice-1 thread `gtkb-advisory-routing-dcl`).
- Dashboard counter spec (sibling Slice-1 thread `gtkb-advisory-report-dashboard-counters-spec`).

## Test Plan

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-template-spec` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-template-spec` - exit 0 expected.
3. `python -m pytest platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py -q --tb=short` - PASS.
4. Pre-insertion packet validation per IP-4 — emits `packet_valid`.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + Step 3. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 + IP-5. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 validates against gate schema. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Standalone OWNER ACTION REQUIRED block evidence in post-impl report. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO.
- [ ] `SPEC-ADVISORY-REPORT-TEMPLATE-001` inserted with required header + body section enumeration.
- [ ] Pre-insertion packet validation (IP-4) executed.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block.
- [ ] `python -m pytest` regression PASS.
- [ ] Codex VERIFIED on post-impl report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-report-template-spec-001.md` with a corresponding `bridge/INDEX.md` entry (insert at top of doc list); append-only version chain.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry. NOT a bulk operation.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-001` NEW.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (routing DCL / dashboard counters).
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4.

## Risk + Rollback

**Risk R1 (Low):** Template fields may not cover all real-world advisory shapes. Mitigation: optional sections + extensibility via future amendments.

**Risk R2 (Low):** Coordination with sibling routing DCL — both need to agree on classification slot semantics. Mitigation: this spec defines the slot SHAPE; sibling routing DCL defines the routing BEHAVIOR.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase SPEC is a net-new specification.

## Loyal Opposition Asks

1. Confirm the IP-1 required-fields enumeration (5 header + 5 body sections) is sufficient for deterministic advisory-report parsing.
2. Confirm the classification-slot vocabulary (adopt/adapt/reject/defer/monitor) aligns with sibling threads.
3. Confirm IP-4 inline Python validation pattern matches the canonical formal-artifact pattern.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

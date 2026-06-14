GO

Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 008
Date: 2026-06-13 UTC
Author: Loyal Opposition (Codex, harness A)
Author-Harness-ID: A
Review-Target: bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md
Bridge-Kind: implementation_review
Status: GO

# Loyal Opposition GO Verdict: WI-4534 Claim Role Eligibility Guard

## Claim

The revised implementation proposal in
`bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md` is approved to proceed
as the operative WI-4534 implementation plan.

This GO applies only to the three target paths listed in the revised proposal:

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_work_intent_role_eligibility.py`
- `platform_tests/scripts/test_go_impl_claim_timebox.py`

This GO does not approve GO-event dispatch routing, cutover/canonical
bridge-state-writer changes, or edits outside those three target paths.

## Evidence Reviewed

- Live bridge thread:
  `bridge/gtkb-wi4534-claim-role-eligibility-guard-001.md` through
  `bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md`.
- Live bridge authority:
  `bridge/INDEX.md`.
- Work item and project authorization:
  `python -m groundtruth_kb.cli backlog list --json`
  and the MemBase `project_authorizations` row for
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`.
- Owner approval evidence:
  `DELIB-20263200` and `DELIB-20263205`.
- Implementation authorization behavior:
  `scripts/implementation_authorization.py`, including packet creation from the
  approved proposal's target paths and target validation against the packet.
- Current test state:
  `platform_tests/scripts/test_work_intent_role_eligibility.py` and
  `platform_tests/scripts/test_go_impl_claim_timebox.py`.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4534-claim-role-eligibility-guard
```

Result:

- status: `PASS`
- operative bridge file:
  `bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md`
- applicability packet:
  `sha256:e08e69070ea1a4bced874ad54afa4dc87325fda4add9a43b8c9e44f7104d99a2`
- missing required specs: none
- missing advisory specs: none

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4534-claim-role-eligibility-guard
```

Result:

- status: `PASS`
- operative bridge file:
  `bridge\gtkb-wi4534-claim-role-eligibility-guard-007.md`
- must-apply clauses: 4
- may-apply clauses: 1
- blocking gaps: 0

## Verification Performed

Command:

```powershell
python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short
```

Result:

- `platform_tests/scripts/test_work_intent_role_eligibility.py`: 8 passed
- `platform_tests/scripts/test_go_impl_claim_timebox.py`: 6 failed, 2 passed

The six timebox failures are expected pre-implementation evidence for the
scope expansion approved in `DELIB-20263205`: those tests still use bare session
IDs without positive Prime Builder role evidence. The revised proposal is
specifically scoped to repair those tests while preserving strict F3.

Command:

```powershell
python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
```

Result: all checks passed.

Command:

```powershell
python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
```

Result: all checked files already formatted.

## Finding Disposition

### Prior NO-GO F1

Resolved. The revised proposal's `target_paths` now includes
`platform_tests/scripts/test_go_impl_claim_timebox.py`, which is the file
needed to repair the six strict F3 timebox tests affected by the new role
eligibility guard.

### Prior NO-GO F2

Resolved. `DELIB-20263205` records the owner decision approving Option A:
expand WI-4534 scope to update `test_go_impl_claim_timebox.py` while preserving
strict F3 behavior. This supplies the missing owner approval evidence for the
scope expansion beyond the original two target paths.

### Prior NO-GO F3

Resolved. The revised plan explicitly keeps strict F3 required and does not
weaken GO implementation claim timebox semantics. The required repair is to
make the six affected tests provide positive Prime Builder role evidence, not
to loosen the guard.

## Implementation Conditions

Prime Builder must start the implementation from this latest GO and confirm the
named implementation authorization packet includes exactly the three approved
target paths before editing:

```powershell
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4534-claim-role-eligibility-guard
```

If the generated packet does not include
`platform_tests/scripts/test_go_impl_claim_timebox.py`, stop and file a bridge
function issue instead of proceeding.

Prime Builder must not edit outside:

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_work_intent_role_eligibility.py`
- `platform_tests/scripts/test_go_impl_claim_timebox.py`

Prime Builder must preserve the forbidden-scope exclusions from the project
authorization: no GO-event dispatch routing, no cutover/canonical bridge state
writer changes, and no broader bridge workflow behavior changes.

The post-implementation report must cite `DELIB-20263205` and show that the
six repaired timebox tests now use Prime-eligible session evidence while the
strict F3 negative case still fails when role evidence is absent.

Required post-implementation verification:

```powershell
python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
```

## Residual Risk

The MemBase project authorization row remains the original active Slice A row
with `DELIB-20263200` as its owner decision reference. That row is not the
mechanical source for the named implementation authorization packet's target
paths; the packet is created from the approved bridge proposal. The risk is
therefore operational rather than blocking: Prime Builder must regenerate the
authorization packet after this GO and confirm the packet target list reflects
the revised proposal before making edits.

## Opportunity Radar

No new material deterministic-service or token-savings opportunity was found in
this review. The repeated preflight and targeted verification steps are already
served by existing bridge helper scripts and repo-native test commands.

## Owner Action Required

None.

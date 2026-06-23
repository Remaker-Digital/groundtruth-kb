REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-c239-7df0-8c15-537755d0eb70
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; resolved Prime Builder by owner init keyword ::init gtkb pb; durable role remains loyal-opposition for headless dispatch

# Defect-Fix Proposal - Auth-Gate Requirement Sufficiency Parser Surfaces

bridge_kind: prime_proposal
Document: gtkb-auth-gate-requirement-sufficiency-parser-surfaces
Version: 003
Date: 2026-06-23 UTC
Responds to: bridge/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3454

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
requirement_relaxation_in_scope: false

## Revision Claim

This REVISED proposal resolves the two findings from `bridge/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-002.md`.

Path choice is now settled by owner decision `DELIB-20265587`: use Path B. Path B means aligning the Write-time bridge-compliance gate to the existing implementation-start Requirement Sufficiency classifier without relaxing the Requirement Sufficiency contract. Path A and Path A+B are explicitly rejected for this WI revision.

The implementation remains the narrow de-duplication repair proposed in version 001: the bridge-compliance gate must surface at proposal filing time exactly the Requirement Sufficiency opener cases that `scripts/implementation_authorization.py` would reject at implementation-start time. No new requirement, parser-loosening, formal artifact mutation, or work-item mutation is in scope.

## First-Line Role Eligibility Check

- Session role source: owner transcript init keyword `::init gtkb pb`.
- Interactive resolved role: Prime Builder.
- Durable registry fallback for harness `A`: Loyal Opposition, used for headless dispatch routing only when no transcript-defined interactive role is present.
- Governing role rule: `.claude/rules/prime-builder-role.md` states that Prime Builder governance applies when the resolved session role comes from `::init gtkb pb`.
- Latest bridge status before this filing: `NO-GO` at `bridge/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-002.md`.
- Status authored here: `REVISED`.
- Prime Builder is authorized to author `REVISED` after latest `NO-GO`.
- Work-intent claim acquired for `gtkb-auth-gate-requirement-sufficiency-parser-surfaces` at `2026-06-23T02:32:54Z`, session `019ef217-c239-7df0-8c15-537755d0eb70`.

## Responds To NO-GO Findings

### P1 - The proposal says a required owner path decision is still missing

Response: Fixed. Owner decision `DELIB-20265587` selects Path B recommended.

The selected Path B scope is:

- Align the Write-time gate to the existing implementation-start Requirement Sufficiency classifier.
- Preserve the existing Requirement Sufficiency contract.
- Do not loosen parser acceptance.
- Do not introduce new or revised requirements.

The rejected alternatives are:

- Path A: loosen the parser to accept broader opener text.
- Path A+B: both loosen acceptance and move enforcement earlier.

### P2 - The live proposal is dispatchable while its body labels it a non-dispatchable draft

Response: Fixed. This filing is a live `REVISED` proposal. The metadata states `Version: 003` and does not describe the file as draft-only or non-dispatchable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge protocol's GO/VERIFIED discipline is undermined when a proposal can receive GO but fail the implementation-start Requirement Sufficiency parser; the filing-time gate must catch those rejects before LO review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal links every relevant governing specification and maps verification back to those links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable Project Authorization, Project, and Work Item metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the 2026-06-23 bounded project authorization supplies owner approval evidence for WI-3454 but does not bypass bridge GO or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH evidence is additive to the bridge protocol; implementation still requires LO GO and a fresh implementation-start packet.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests derived from this proposal's linked specs.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs the FAB-14 / HYG-046 Requirement Sufficiency classifier; Path B aligns the Write-time gate to this existing classifier.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain within the GT-KB project root and do not touch adopter application surfaces.
- `GOV-STANDING-BACKLOG-001` - WI-3454 is an open MemBase work item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the active hook and scaffold template hook must be updated in parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the accepted Requirement Sufficiency state remains a durable proposal property validated consistently across filing and activation gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision and work-item evidence are preserved as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the lifecycle trigger is moved earlier without changing the underlying lifecycle state.

## Owner Decisions / Input

- `DELIB-20265587` - owner selected Path B recommended for WI-3454: align the Write-time bridge-compliance gate to the existing implementation-start Requirement Sufficiency classifier without relaxing the Requirement Sufficiency contract.
- `DELIB-20265586` - owner authorized `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`, snapshot-bound to the 31 open project member work items, including `WI-3454`.
- `DELIB-20265457` - prior reliability-fixes batch authorization context cited by the version-001 proposal and version-002 NO-GO.
- No additional owner decision is required for Path B as scoped here.

## Prior Deliberations

- `bridge/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-001.md` - initial proposal selecting Path B but still declaring the owner path decision unresolved.
- `bridge/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-002.md` - LO NO-GO requiring owner path selection and removal of draft/non-dispatchable wording.
- `DELIB-20265587` - owner path selection for WI-3454.
- `DELIB-20265457` - owner decision authorizing the reliability-fixes proposal batch and non-fast-lane PAUTH context, without replacing per-WI bridge review.
- `DELIB-20265324` - prior Loyal Opposition GO for Requirement Sufficiency operative-precedence repair, adjacent parser/gate context.
- `DELIB-20261498` - project-completion scanner addressing-thread fix lineage identified as the origin incident.
- `DELIB-20261020` - sibling impl-auth and impl-start-gate parser hygiene verification context.
- `DELIB-2105` - reliability fast-lane authorization lineage.

## Requirement Sufficiency

Existing requirements sufficient. Path B preserves the existing Requirement Sufficiency contract and aligns the Write-time gate to the already-governing implementation-start classifier. No new or revised requirement/specification is introduced.

## Proposed Scope

Implement minimal, behavior-preserving de-duplication so the Write-time gate accepts or rejects the same Requirement Sufficiency opener states that the implementation-start parser accepts or rejects:

1. In `.claude/hooks/bridge-compliance-gate.py`, replace the private operative-state classification inside `_requirement_sufficiency_section_gap` so that after the existing presence/placeholder checks pass, the section body's operative state is derived from the same bounded classifier semantics used by `scripts/implementation_authorization.py` `requirement_sufficiency_state`.
2. Use an import-or-vendored-fallback pattern, matching the hook's existing approach for other shared helpers. The fallback must mirror the same bounded patterns and be pinned by tests.
3. Map classifier results to the existing gate descriptors:
   - `sufficient` or `gap` with exactly one operative state: accept.
   - `unrecognized`: reject at filing time using the existing no-operative-state descriptor.
   - dual-state assertions: reject with the existing multiple-operative-states descriptor.
4. Apply the byte-identical change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
5. Extend `platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py` with regression coverage proving the Write-time gate agrees with `requirement_sufficiency_state`.

Scope guard: this does not alter when the gate fires, does not modify `scripts/implementation_authorization.py`, does not relax parser acceptance, does not add Path A behavior, and does not mutate formal artifacts.

## Project Root Boundary

All implementation output paths and generated artifacts for this WI remain under the project root `E:\GT-KB`.

- Live bridge file: `E:\GT-KB\bridge\gtkb-auth-gate-requirement-sufficiency-parser-surfaces-003.md`.
- Active hook target: `E:\GT-KB\.claude\hooks\bridge-compliance-gate.py`.
- Scaffold template target: `E:\GT-KB\groundtruth-kb\templates\hooks\bridge-compliance-gate.py`.
- Test target: `E:\GT-KB\platform_tests\scripts\test_bridge_compliance_requirement_sufficiency.py`.
- No dependency, artifact, or verification evidence is read from or written outside `E:\GT-KB`.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` plus `SPEC-AUQ-POLICY-ENGINE-001` | `test_write_gate_agrees_with_impl_start_on_bounded_sufficiency` | For bounded sufficiency phrasings accepted by `requirement_sufficiency_state`, the Write gate returns no Requirement Sufficiency gap. |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_write_gate_denies_unrecognized_opener_caught_by_impl_start` | An opener classified as `unrecognized` by `requirement_sufficiency_state` is denied at filing time. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_write_gate_accepts_gap_state_unchanged` | The valid gap state remains accepted by the Write gate. |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_write_gate_rejects_dual_state_unchanged` | A section asserting both operative states remains denied with the multiple-state descriptor. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_template_and_active_hook_byte_identical` | The active and template hook copies remain byte-identical. |

Required commands after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q --tb=short
python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py
python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-auth-gate-requirement-sufficiency-parser-surfaces
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-auth-gate-requirement-sufficiency-parser-surfaces
```

## Acceptance Criteria

1. The Write-time bridge-compliance gate's Requirement Sufficiency operative-state decision is derived from the same bounded classifier semantics as implementation-start authorization.
2. The gate denies at filing time the opener states that implementation-start authorization would reject later.
3. Existing valid sufficient/gap states and dual-state rejection behavior remain unchanged.
4. `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical.
5. Focused pytest, ruff check, and ruff format check pass on the touched files.

## Pre-Filing Preflight Subsection

Candidate content file:

```text
.gtkb-state/bridge-revisions/drafts/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-003-complete.md
```

Applicability preflight command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-auth-gate-requirement-sufficiency-parser-surfaces --content-file .gtkb-state/bridge-revisions/drafts/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-003-complete.md --json
```

Applicability preflight result:

```text
preflight_passed: true
packet_hash: sha256:d102406ecdc710d956503ed072d39640032612f3959b73b2fa8b7371ed7cd359
missing_required_specs: []
missing_advisory_specs: []
```

Clause preflight command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-auth-gate-requirement-sufficiency-parser-surfaces --content-file .gtkb-state/bridge-revisions/drafts/gtkb-auth-gate-requirement-sufficiency-parser-surfaces-003-complete.md
```

Clause preflight result:

```text
must_apply: 3
may_apply: 2
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Risks / Rollback

- Risk: importing the implementation-start classifier from the hook could fail in a partial install. Mitigation: use an import-or-vendored-fallback pattern and pin fallback behavior with tests.
- Risk: aligning to the broader existing classifier could accept a phrase previously rejected by the narrower filing hook. Mitigation: this is the intended Path B convergence; it does not accept anything the implementation-start classifier rejects.
- Risk: active/template hook drift. Mitigation: edit both copies in lockstep and run the parity test.
- Rollback: revert the classifier-alignment changes in both hook copies and remove the added tests. No migration, schema change, or formal artifact mutation is involved.

## Fast-Lane Eligibility

The version-002 owner-decision blocker is resolved by `DELIB-20265587`. The selected Path B does not relax requirements and does not require new formal artifact scope. Implementation is still not authorized until LO records GO and Prime Builder creates an implementation-start packet.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py`

## Recommended Commit Type

fix

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

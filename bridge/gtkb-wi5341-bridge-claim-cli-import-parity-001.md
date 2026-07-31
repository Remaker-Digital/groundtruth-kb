NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; WI5341 governed proposal filing

# Implementation Proposal - Restore Bridge Claim CLI Import/API Parity For NO-ACTION Corrections

bridge_kind: prime_proposal
Document: gtkb-wi5341-bridge-claim-cli-import-parity
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5341-CLAIM-CLI-IMPORT-PARITY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5341
target_paths: ["scripts/bridge_claim_cli.py", "scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]
implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Proposal Claim

WI-5341 should restore the `claim-no-action` CLI/registry API contract as a
bounded successor to the WI-5249 stand-down, not as a hidden extension of
WI-5307. The command is currently exposed by `scripts/bridge_claim_cli.py`, and
the registry exports the compatibility token
`CLAIM_KIND_NO_ACTION_CORRECTION`, but explicit acquisition fails closed with
`Unsupported explicit claim kind: 'no_action_correction'`.

The proposed implementation makes `claim-no-action` usable again only for the
non-implementation Prime Builder correction path:

- latest bridge status must be `GO` or `NO-GO`;
- resolved acting role must be `prime-builder`;
- stored claim kind must be `no_action_correction`;
- implementation deadline and grace fields must remain null;
- the claim must not authorize `implementation_authorization.py begin`;
- ordinary `claim` behavior must remain unchanged, including latest `GO` as
  `go_implementation`, latest `NO-GO` as `draft`, and non-GO drafting as
  `draft`;
- WI-5279 `project_authorization_bootstrap` claims must remain intact;
- WI-5337 latest-status correction must remain intact;
- WI-5307's verified removal of nonterminal WI-5178 operation-time PAUTH helper
  behavior must remain intact.

This proposal does not authorize dispatcher mutation, TAFE mutation, database
schema mutation, release, deployment, push, credential lifecycle work,
destructive cleanup, or git history rewrite.

## Requirement Sufficiency

Existing requirements are sufficient. The active PAUTH authorizes one governed
proposal and, only after independent GO plus matching claim and
implementation-start authorization, source/test restoration of
`claim-no-action` constant/API parity across the four target files. No new
owner decision is required for this proposal. Implementation remains blocked
until Loyal Opposition returns an independent GO.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded fleet-defect repair proposals while preserving normal implementation gates.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5341-CLAIM-CLI-IMPORT-PARITY-20260716` - active bounded authorization for this proposal and subsequent exact four-file implementation after GO.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md` - terminal VERIFIED baseline disposition; active WI-5249 behavior was cleared there, while the inert compatibility token remained.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md` - terminal bridge-only stand-down; this proposal is the fresh successor required before any active `no_action_correction` implementation can be adopted.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - terminal VERIFIED bootstrap lifecycle behavior that WI-5341 must preserve.
- `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-003.md` - pending test-only recurrence guard; WI-5341 must not turn ordinary latest `NO-GO` into implementation authority.

## Owner Decisions / Input

- Owner goal: complete the black-box bridge, TAFE, and harness complex program and bring related work to terminal verified/closed state.
- Owner decision `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded defect-repair proposal filing for in-scope fleet defects.
- Active PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5341-CLAIM-CLI-IMPORT-PARITY-20260716` includes WI-5341, the exact four target paths, and mutation classes `bridge`, `metadata`, `source`, and `test`.
- No additional owner clarification is required before Loyal Opposition proposal review.

## Evidence Of Current Defect

`python scripts\bridge_claim_cli.py --help` now imports successfully and lists
`claim-no-action`, confirming WI-5341's original import failure has been
partially reduced to an API/semantic parity failure.

`python scripts\bridge_claim_cli.py claim-no-action gtkb-dispatcher-black-box-spec-foundation --ttl-seconds 60`
currently fails with:

```text
ERROR: Unsupported explicit claim kind: 'no_action_correction'
```

Focused test reproduction:

```text
python -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py -q --tb=short --timeout=300 -k "no_action or claim_cli"
```

Observed result: 7 selected, 1 passed, 6 failed.

Failure classes:

- explicit `no_action_correction` acquisition after latest `GO` and latest `NO-GO` is rejected as unsupported;
- `claim-no-action` CLI exits 3 with the same unsupported-kind error;
- stale test coverage still expects the removed WI-5178 `_validate_project_authorization_operation` helper.

The implementation must correct the first two failure classes and update stale
tests without resurrecting the removed WI-5178 helper behavior.

## Implementation Approach

1. Add a narrow registry validator for explicit
   `CLAIM_KIND_NO_ACTION_CORRECTION` acquisition.
2. Require latest status `GO` or `NO-GO` and resolved acting role
   `prime-builder`.
3. Persist a normal TTL claim with `claim_kind=no_action_correction`,
   `implementation_deadline=None`, `implementation_grace_expires_at=None`,
   no bootstrap metadata, and no GO-implementation extension cap.
4. Keep ordinary `claim` behavior unchanged.
5. Keep `CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP` behavior unchanged.
6. Keep `implementation_authorization.py begin` requiring a live
   `go_implementation` claim, so a `no_action_correction` claim cannot start
   implementation.
7. Repair tests to prove the supported contract and remove stale expectations
   that depend on the removed WI-5178 operation-time helper.

## Target Paths And Ownership

- `scripts/bridge_claim_cli.py` - existing command surface and user-facing help.
- `scripts/bridge_work_intent_registry.py` - explicit claim-kind registry behavior.
- `platform_tests/scripts/test_bridge_claim_cli.py` - CLI-level import and command coverage.
- `platform_tests/scripts/test_bridge_work_intent_registry.py` - registry semantics and implementation-start denial coverage.

Foreign dirty hunks in these files must remain excluded unless they are
required by this exact WI-5341 contract and included in the implementation
report as WI-5341-owned.

## Pre-Filing Preflight Subsection

- Applicability command: `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5341-bridge-claim-cli-import-parity-001.md --bridge-id gtkb-wi5341-bridge-claim-cli-import-parity --json`
- Applicability result: exit 0; `preflight_passed: true`; missing required specs `[]`; missing advisory specs `[]`; blocking errors `[]`.
- Clause command: `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5341-bridge-claim-cli-import-parity-001.md --bridge-id gtkb-wi5341-bridge-claim-cli-import-parity`
- Clause result: exit 0; clauses evaluated 5; must apply 3; evidence gaps in must-apply clauses 0; blocking gaps 0.

## Specification-Derived Verification Plan

| Governing requirement | Focused verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File this proposal as `NEW`, wait for independent LO `GO`, then implement only with an exact live claim and implementation-start packet. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Validate the four target paths against the active WI-5341 PAUTH before mutation and in the implementation report. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Add/repair tests proving latest `GO` and latest `NO-GO` allow only explicit `no_action_correction`, with no implementation deadline and no implementation-start authority. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify WI-5279 bootstrap claim tests still pass and bootstrap metadata remains unchanged. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Verify WI-5341 does not restore removed WI-5178 operation-time helper behavior or weaken implementation-start enforcement. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry focused pytest, Ruff check, Ruff format, applicability preflight, and clause preflight results into the implementation report. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run nonimpairment-focused checks over ordinary claim, no-action claim, bootstrap claim, and latest-status behavior. |

Planned commands:

```text
python -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py -q --tb=short --timeout=300 -k "no_action or claim_cli or bootstrap"
python -m pytest platform_tests\scripts\test_bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py -q --tb=short --timeout=300
python -m ruff check scripts\bridge_claim_cli.py scripts\bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_bridge_work_intent_registry.py
python -m ruff format --check scripts\bridge_claim_cli.py scripts\bridge_work_intent_registry.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_bridge_work_intent_registry.py
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5341-bridge-claim-cli-import-parity --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5341-bridge-claim-cli-import-parity
```

## Acceptance Criteria

1. `python scripts\bridge_claim_cli.py --help` succeeds and lists ordinary, bootstrap, no-action, extend, release, and status commands.
2. `claim-no-action` succeeds for a Prime Builder session when latest status is `GO`.
3. `claim-no-action` succeeds for a Prime Builder session when latest status is `NO-GO`.
4. `claim-no-action` rejects latest non-verdict statuses.
5. `claim-no-action` rejects non-Prime sessions.
6. Persisted `no_action_correction` claims have no implementation deadline, no implementation grace, and no GO-extension cap.
7. `implementation_authorization.py begin` rejects a `no_action_correction` claim because it is not a GO-implementation claim.
8. Ordinary latest `GO` claim behavior remains `go_implementation`.
9. Ordinary latest `NO-GO` claim behavior remains `draft`.
10. WI-5279 bootstrap claim behavior remains unchanged.
11. No dispatcher, TAFE, database schema, credential, release, deployment, push, cleanup, or git-history operation occurs.

## Risk And Rollback

Risk is moderate because `scripts/bridge_work_intent_registry.py` is a shared
claim gate and currently contains verified WI-5279 bootstrap behavior. The
main regression risks are accidentally re-authorizing implementation under a
NO-ACTION correction claim, reviving removed WI-5178 operation-time enforcement
helpers, or changing ordinary latest-status classification.

Rollback is removal of the WI-5341 source/test hunks. Bridge files remain
append-only, and any rollback would require its own governed bridge action if
the implementation reaches a verified state.

## Recommended Commit Type

`fix:`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

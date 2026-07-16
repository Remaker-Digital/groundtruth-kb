NEW

# Make DORA Track 2 Azure reconciliation tests self-contained

bridge_kind: prime_proposal
Document: gtkb-wi5287-dora-track2-azure-fixture-self-containment
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5287

target_paths: ["platform_tests/scripts/test_dora_001b_track2_ingest.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make the DORA Track 2 Azure-reconciliation tests explicitly provide the
application-owned configuration that production now correctly requires. The
exact RC module currently reports 6 failures and 12 passes because tests T8,
T9, T10, T11, T13, and T14 call `_reconcile_against_azure_revisions` without
`GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` or
`GTKB_DASHBOARD_AZURE_RESOURCE_GROUP`; production therefore skips before the
mocked subprocess behavior under test.

Add one test-local autouse fixture that uses `monkeypatch` to set a deterministic
JSON mapping for `production` and a non-secret test resource group. Preserve all
18 assertions, every mocked Azure result, production code, environment ownership,
and the no-live-Azure property. The fixture must not read `env.local`, ambient
credentials, external state, or a live Azure subscription.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the RC gate's executable DORA checks must run deterministically rather than depend on ambient application configuration.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must preserve application-owned Azure configuration and production fail-closed behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the protected test change requires independent GO, matching claim/start authority, a report, and independent VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Assurance project, active PAUTH, WI-5287, and one exact target are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing release, non-impairment, authority, and test obligations are linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must execute the focused module and the RC mixed regression batch.
- `GOV-STANDING-BACKLOG-001` - WI-5287 remains the durable owner until the exact repair is independently verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all test code and evidence remain under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the failure, proposal, test repair, execution evidence, and verdict remain linked artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5287 remains active until implementation, verification, and finalization evidence are complete.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the observed release failure and its disposition remain durably traceable.

## Prior Deliberations

- `DELIB-202666274` - authorizes all required modernization blocker work at project scope while retaining bridge, verification, and mechanical Git gates.

## Owner Decisions / Input

No new owner decision is required. The active Assurance project PAUTH version 3
allows test implementation and governed bridge work. Git staging/commit/push,
release, deployment, dispatcher/TAFE/harness mutation, credential lifecycle,
external-system mutation, and destructive cleanup remain excluded.

## Requirement Sufficiency

Existing requirements are sufficient. Production already implements the correct
application-owned configuration contract, and WI-5287 records the exact test
fixture omission. No production requirement or formal carrier must change.

## Proposed Scope

1. Add one autouse pytest fixture in `platform_tests/scripts/test_dora_001b_track2_ingest.py`.
2. Use `monkeypatch.setenv` to set `GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` to deterministic JSON containing only a `production` test mapping.
3. Set `GTKB_DASHBOARD_AZURE_RESOURCE_GROUP` to a non-secret test value.
4. Preserve all existing subprocess mocks and expected matched, drift, unknown, and confidence outcomes.
5. Do not edit production dashboard code, environment files, credentials, Azure configuration, or any second path.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5287 exact RC failure evidence on 2026-07-16","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"pytest monkeypatch fixture in the sole target module","before_behavior":"Six reconciliation tests skip before their mocked subprocess behavior because required application-owned settings are absent.","after_behavior":"The same tests provide deterministic test-owned settings and exercise their intended mocked reconciliation paths.","self_descriptive_naming":"Fixture and values identify test-only Azure reconciliation configuration.","obsolete_guidance_disposition":"No guidance or production ownership statement changes.","history_preservation":"Preserve every existing test and assertion; add only fixture setup.","baseline":{"command":"python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short","result":"6 failed, 12 passed"},"expected_result":{"focused":"18 passed","rc_batch":"advances beyond DORA without live Azure"},"rollback":{"instructions":"remove only the WI-5287 fixture hunk through a governed change","verification":"rerun the focused module and observe the recorded six-failure baseline"},"hard_invariants":["production remains application-owned","no live Azure call","no credential dependency","all existing assertions retained"],"fail_closed_conditions":["ambient configuration required","live Azure contacted","production code changed","second path changed"],"essential_context_preservation":"Keep environment-to-container-app ownership, resource-group ownership, mocked subprocess results, consistency classifications, and confidence upgrades explicit."}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Deterministic DORA fixture | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short` | 18 passed with both Azure variables initially absent from the invoking shell. |
| No live Azure or credentials | Review fixture plus existing `unittest.mock.patch("subprocess.run", ...)` sites; run focused module with no Azure credentials | Every reconciliation path remains mocked; no network or credential lookup occurs. |
| Test-only scope | `git diff -- platform_tests/scripts/test_dora_001b_track2_ingest.py` and `git diff --check -- platform_tests/scripts/test_dora_001b_track2_ingest.py` | Only the fixture/import hunk exists; diff check exits zero. |
| RC non-impairment | Run the exact mixed Python regression list from `scripts/release_candidate_gate.py` | DORA contributes 18 passes and the batch advances to independently owned blockers. |

## Acceptance Criteria

1. The focused module passes all 18 tests without ambient Azure variables.
2. T8/T9 still classify mocked CLI failure and missing CLI as `unknown`.
3. T10/T14 still classify exact mocked revision matches as `both_match`.
4. T11 still classifies mocked revision drift as `manifest_only`.
5. T13 still upgrades matching reconciliation confidence to `high`.
6. No production, credential, Azure, dispatcher, harness, database, or Git operation occurs.

## Risk / Rollback

Risk is low and confined to fixture overreach. An autouse fixture is appropriate
because all tests in this module exercise one application-specific DORA ingest
contract, but it must provide only non-secret deterministic values and must not
mask explicit missing-configuration tests elsewhere. Rollback is the exact
fixture hunk through a new governed change; no broad reset is permitted.

## Bridge Filing

File as the next append-only proposal for
`gtkb-wi5287-dora-track2-azure-fixture-self-containment` through the governed
Codex non-bypass helper. No manual routing or direct harness contact occurs.

## Recommended Commit Type

`test` - restores deterministic RC coverage without changing production behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

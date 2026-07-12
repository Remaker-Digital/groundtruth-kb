REVISED

# WI-5200..5202 - Revision: isolate H capability truth test from WI-5199 registration state

bridge_kind: prime_proposal
Document: gtkb-wi5200-5202-generous-harness-repair-narrow
Version: 005
Responds to: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-004.md (NO-GO)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; governed NO-GO revision

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5200
Related Work Items: WI-5201, WI-5202

target_paths: [".api-harness/routing.toml", "config/agent-control/harness-capability-registry.toml", "scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_lo_harness_turn_budget.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_check_harness_parity.py"]

implementation_scope: one self-contained parity-test correction; previously verified source/config substance unchanged
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

Prime accepts the isolated-worktree finding and selects remediation option (b):
rewrite only
`test_alibaba_managed_skill_adoption_review_is_truthfully_unsupported` as a
`tmp_path` fixture. The fixture will write a minimal harness projection that
registers `alibaba-cloud-studio` and a minimal capability registry containing
the truthful `unsupported` row, then call the checker against that fixture
root. This preserves the intended behavior assertion while removing the
test's accidental dependency on WI-5199's still-uncommitted generated registry.

The source/config repair affirmed by B remains unchanged. The revised test does
not weaken production parity logic, alter the expected state, or conceal a live
integration failure: WI-5199 separately owns the actual H registration and
genuine dispatcher proof.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION`
- `DELIB-202666172`
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-004.md`

## Owner Decisions / Input

Mike authorized WI-5200, WI-5201, WI-5202, generous recovery, and H reproof.
This revision stays inside the approved test target and responds directly to an
independent verification finding. No new owner decision is required. It avoids
the cross-thread co-finalization option and therefore does not override the
existing WI-5105-class hold noted by Loyal Opposition.

## Findings Addressed

### FINDING-1 - WI-owned isolated test failure

**Accepted.** The live-repository test currently reaches `_normalize_harness`
before the capability registry because clean HEAD does not yet contain H in the
generated projection. The revision will create the required projection and
registry as fixture inputs. Expected isolated result: the checker returns one
H row for `skill.managed-skill-adoption-review` with state `UNSUPPORTED`, not
`MISSING` and not a normalization error.

### FINDING-2 - foreign skill-governance-lifecycle projection failures

**Disclosed, not absorbed.** Clean HEAD lacks the untracked native skill file
while its registry declaration already exists. Those two live-repository tests
fail at pure HEAD and are not caused by this patch. This revision will report
the baseline separately and will not stage, edit, or claim the foreign skill
artifacts. Their existing governed skill-lifecycle carrier remains responsible
for committing the projection.

## Scope Changes

Only `platform_tests/scripts/test_check_harness_parity.py` changes relative to
the implementation report. All 16 approved target paths remain the complete
patch scope; no DB, generated harness registry, credential, deployment, or
foreign skill file enters this thread.

## Requirement Sufficiency

Existing requirements sufficient. The linked harness-onboarding and mandatory
verification requirements already demand truthful, isolated evidence. This
revision changes only the test setup needed to exercise those requirements from
a clean checkout; it introduces no new product or governance requirement.

## Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run the revised H fixture test alone | H normalizes from fixture projection and returns truthful `UNSUPPORTED`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Rebuild clean-HEAD isolated worktree, apply exact staged 16-path patch, run all 378 scoped tests | WI-owned suite passes; any pure-HEAD foreign baseline failures are separately demonstrated and not masked. |
| Shared runtime/dispatcher specs | Re-run all eight scoped test modules and Ruff | Blank recovery, generous limits, guards, parity, and dispatcher behavior remain green. |
| Finalization isolation | Compare staged config hunks and file set | Only approved 16 paths; unrelated routing/registry/skill state remains unstaged. |

## Pre-Filing Preflight Subsection

The canonical revision helper will run applicability and clause preflights on
this completed content before filing. Filing is prohibited if either reports a
blocking gap.

## Risk And Rollback

A fixture could become less representative than a live-repository integration
test. That is bounded here because the fixture asserts the exact production
projection schema and production checker behavior, while WI-5199 independently
retains the live-registration and genuine H-dispatch proof obligation. Rollback
is one test hunk; all affirmed source/config repairs remain untouched.

## Loyal Opposition Ask

Approve the one-test isolation correction, then independently rerun the clean
HEAD plus exact-patch rehearsal before VERIFIED.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

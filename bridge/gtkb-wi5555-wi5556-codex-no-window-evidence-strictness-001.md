NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; reasoning_effort=xhigh

# Defect-Fix Proposal - Tighten Codex no-window evidence semantics

bridge_kind: prime_proposal
Document: gtkb-wi5555-wi5556-codex-no-window-evidence-strictness
Version: 001 (NEW)
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5555
Work Item: WI-5556

target_paths: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "scripts/codex_no_window_smoke_probe.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

After WI-5389 reaches terminal VERIFIED/focused finalization, tighten the
shared schema-v3 Codex no-window evidence contract in one follow-up slice:

1. accept only exact integer `0` (excluding `bool`) and compatibility string
   `"0"` as successful child/wrapper return codes; and
2. reject any run whose captured output contains a
   `codex_models_manager::cache` ERROR diagnostic.

The smoke producer must fail the probe when the cache diagnostic appears, and
the package-canonical validator must independently fail closed with a stable
actionable reason even for previously written schema-v3 evidence. Both
production consumers already call the shared validator after WI-5389, so this
slice must not add new verifier/dispatcher validation forks.

## Defect / Reproduction

- WI-5555 records that Python set membership in `{0, "0"}` accepts JSON
  `false` and `0.0` because `False == 0` and `0.0 == 0`. The pending shared
  validator uses that comparison for command-step and wrapper return codes.
- WI-5556 records two fresh successful probes that emitted
  `codex_models_manager::cache` ERROR diagnostics, including an unknown
  reasoning-effort variant and a missing cache-schema field. The probe still
  reported PASS.
- `scripts/codex_no_window_smoke_probe.py` already stores per-run
  `stdout_preview` and `stderr_preview`, but its PASS expression currently
  considers only markers, effective permissions, sentinel lifecycle, wrapper
  status, and visible windows.
- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py`
  validates the same structural surfaces but currently neither enforces exact
  return-code types nor inspects captured output for model-cache ERROR lines.
- TEST-11613 and TEST-11614 are the exact intended linked tests. Their
  `source_test_id` linkage remains pending the already-governed WI-5326/WI-5483
  repair and must not be replaced by duplicate tests.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. No external cache, home-directory,
credential, provider, or harness state is a proposed target or evidence
dependency.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - dispatch readiness evidence must
  represent genuine functional compatibility, not merely process exit.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex readiness is consumed by the
  centralized dispatcher.
- `ADR-DISPATCHER-ARCHITECTURE-001` - producer and both consumers must share one
  validator contract rather than diverging.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - preserve Codex's headless/private
  desktop fallback and workspace permissions proof.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must not disable A,
  weaken dispatchability, or mutate dispatcher configuration.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO/verification and the
  append-only numbered chain remain mandatory.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization does
  not replace the implementation gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - mutation is limited to the six
  declared source/test paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - fresh claim and
  operation-time start validation are required after the dependency hold.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5389 terminal finalization and
  clean target ownership are hard predecessors.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  carries its governing specification set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires the
  mapped tests and observed command evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, and both
  work-item carriers are declared above.
- `GOV-WORK-TREE-HYGIENE-001` - foreign WI-5389 bytes must not be adopted or
  overwritten.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - both defects retain distinct WI/test
  traceability within one overlap-safe implementation slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation evidence remains
  linked across WIs, tests, bridge, source, and final commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - neither WI becomes complete before
  independent terminal verification and focused finalization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation and evidence
  remains in the GT-KB root.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - requires every
  discovered fleet defect to traverse the complete governed lifecycle without
  direct harness contact or dispatcher/runtime mutation.
- `DELIB-202666274` - confirms project-level authorization while preserving
  bridge, claim, implementation-start, independent verification, and
  mechanical-operation gates.
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-003.md` - current
  canonical WI-5389 implementation report whose pending candidate establishes
  the shared schema-v3 validator and owns overlapping target bytes.

## Owner Decisions / Input

- Active project-wide authorization
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` has no
  per-WI inclusion restriction and permits governed bridge/source/test work for
  active project members while preserving exact downstream gates.
- No new owner decision is required. The proposal does not authorize direct
  harness invocation, external cache mutation, credentials, dispatcher/TAFE
  mutation, staging, commit, push, deployment, release, or destructive cleanup.

## Requirement Sufficiency

Existing requirements sufficient.

WI-5555/TEST-11613 and WI-5556/TEST-11614 define the two exact defects and
expected outcomes. The cited harness-onboarding, centralized-dispatch,
single-validator, nonimpairment, project-ordering, and verification
specifications fully govern the bounded repair. No new or revised requirement
is needed before implementation.

## Proposed Scope

### Dependency Hold

Do not acquire an implementation claim, create an implementation-start packet,
or edit any target while WI-5389 is latest NEW or otherwise unfinalized. After
WI-5389 reaches independent VERIFIED and focused commit, require all six target
paths to match the finalized baseline before beginning.

### IP-1 - Exact Return-Code Semantics

Add one package-canonical helper that accepts only:

- exact `int` value `0`, with `bool` explicitly rejected; or
- exact string value `"0"`.

Use it for command-step and wrapper return-code checks. Preserve the existing
stable failure reasons for marker-chain and wrapper failures.

### IP-2 - Model-Cache Diagnostic Detection

Detect an ERROR line only when the captured line contains the
`codex_models_manager::cache` logger identity and an ERROR severity marker.
Do not reject unrelated prose containing words such as "cache" or "error".

The smoke producer must:

- mark the affected run and overall probe as failed;
- retain only the existing bounded/sanitized preview surface; and
- avoid reading, deleting, rewriting, or relocating any external cache.

The shared validator must independently scan the schema-v3 run previews and
return the stable reason
`codex_no_window_verification_model_cache_error`. Existing clean schema-v3
evidence remains structurally compatible; no schema-version bump is proposed.

### IP-3 - Consumer And Nonimpairment Coverage

Add focused tests proving both `scripts/verify_codex_dispatch.py` and
`scripts/dispatcher_runtime.py` surface the shared stable reason. Preserve all
current private-desktop, zero-visible-window, workspace create/read/remove
sentinel, marker-chain, wrapper, expiry, ACL, PB-only role, and max-items
requirements.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; DELIB-202666274; WI-5555; WI-5556; bridge/gtkb-wi5389-codex-no-window-schema-contract-003.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 plus the harness-onboarding, centralized-dispatch, project-ordering, bridge, and verification specifications cited in this proposal",
  "primary_route": "Independent review of this NEW proposal, terminal focused WI-5389 predecessor, exact claim and implementation-start validation, six-path implementation, mapped tests, NEW implementation report, independent VERIFIED, and focused finalization",
  "before_behavior": "Schema-v3 evidence accepts bool/float zero return codes and can report PASS while captured output contains codex_models_manager::cache ERROR diagnostics.",
  "after_behavior": "Only exact integer or compatibility string zero succeeds, model-cache ERROR output produces one stable fail-closed readiness reason, and clean schema-v3 evidence remains accepted through the existing producer and shared-consumer route.",
  "self_descriptive_naming": "WI-5555 names return-code typing, WI-5556 names model-cache schema errors, and the combined bridge slug names Codex no-window evidence strictness.",
  "obsolete_guidance_disposition": "No guidance is deleted; any prior assumption that process exit plus markers alone proves readiness is superseded by the stricter canonical validator behavior.",
  "history_preservation": "Both WIs, both tests, the WI-5389 predecessor chain, and this numbered bridge chain remain distinct and append-only.",
  "baseline": {
    "producer": "Schema-v3 probe captures bounded stdout/stderr previews but does not classify model-cache ERROR output.",
    "validator": "Shared WI-5389 candidate uses equality-based return-code membership and does not inspect cache diagnostics.",
    "dispatcher": "Codex A remains PB-only, max-items 1, and dispatchable only when current no-window evidence passes."
  },
  "expected_result": {
    "return_codes": "Exact int 0 excluding bool and exact string 0 are accepted; bools, floats, and nonzero values fail.",
    "cache_diagnostics": "Exact codex_models_manager::cache ERROR lines fail the producer and both consumers with a stable reason.",
    "clean_evidence": "Clean schema-v3 evidence retains existing private-desktop, workspace-sentinel, marker, wrapper, expiry, and ACL behavior."
  },
  "rollback": {
    "instructions": "Use a governed focused reversion of the six-path candidate after NO-GO or a later approved correction; do not disable Codex A or weaken readiness as rollback.",
    "verification": "Rerun the package and three platform modules, confirm the exact target diff, and confirm dispatcher/harness configuration is unchanged."
  },
  "hard_invariants": [
    "Codex A remains prime-builder only and max-items 1.",
    "No dispatcher, TAFE, harness eligibility, role, routing, lease, or runtime-state mutation.",
    "No external cache/home or credential read, write, delete, relocation, or dependency.",
    "No implementation before terminal focused WI-5389 and fresh exact GO/claim/start gates.",
    "No self-review, staging, commit, push, deployment, or release."
  ],
  "fail_closed_conditions": [
    "Missing or non-terminal WI-5389 predecessor.",
    "Dirty target bytes not attributable to the finalized WI-5389 baseline.",
    "Missing independent GO, matching claim, or implementation-start authorization.",
    "Malformed return-code type or detected model-cache ERROR diagnostic.",
    "Any proposal to restore dispatchability by weakening existing containment or sentinel checks."
  ],
  "essential_context_preservation": "The implementation report must retain both WI/test identities, the WI-5389 predecessor commit, exact six-path hashes, stable reason strings, full nonimpairment checks, and independent consumer verification."
}
```

## Specification-Derived Verification Plan

| Specification / obligation | Test / command |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Producer tests: cache ERROR causes probe FAIL; clean output remains PASS. Consumer tests: verifier and dispatcher return the stable cache-error reason. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Package tests prove one shared validator implements both exact return-code and cache diagnostic rules; source review confirms both consumers call it. |
| TEST-11613 | Parameterized JSON evidence rejects `false`, `true`, `0.0`, and nonzero values for step/wrapper return codes while accepting exact `0` and `"0"`. |
| TEST-11614 | Producer, package, verifier, and dispatcher tests cover both recorded cache error shapes and a clean control. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing schema-v3 no-window suites remain green; no dispatcher/harness configuration diff exists. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Pre-start scoped status/hashes show terminal WI-5389 baseline and clean exact targets; final diff contains only six declared paths plus append-only bridge artifacts. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run package tests and all three focused platform modules, Ruff check/format, and diff hygiene; report exact observed results. |

## Acceptance Criteria

1. Exact integer `0` and string `"0"` are the only successful return-code
   encodings; JSON booleans and floats fail closed.
2. Either recorded cache error shape makes the producer return FAIL and makes
   both production consumers report
   `codex_no_window_verification_model_cache_error`.
3. A clean two-run, three-command schema-v3 payload remains accepted without a
   schema bump.
4. Unrelated stderr warnings and prose do not trigger the cache classifier.
5. All existing private-desktop, workspace-sentinel, marker, wrapper,
   zero-visible-window, expiry, and ACL tests remain green.
6. No external cache/home path, credential, dispatcher/TAFE configuration,
   eligibility, role, lease, runtime state, live worker, staging, commit, push,
   deployment, or release mutation occurs.
7. Both WI-5555/TEST-11613 and WI-5556/TEST-11614 remain distinct canonical
   traceability carriers through one shared implementation report, independent
   VERIFIED verdict, and focused commit.

## Risks / Rollback

Risk is false-positive cache classification from ordinary text. Contain it with
the exact logger identity plus ERROR severity requirement and negative tests.
Risk is accidental adoption of pending WI-5389 bytes. Contain it with the hard
terminal/finalized/clean-target predecessor and fresh implementation-start
validation. Rollback is a focused governed reversion of the six-path candidate;
numbered bridge artifacts remain append-only. Do not roll back by weakening
Codex readiness or disabling A.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py`
- `groundtruth-kb/tests/test_codex_no_window_verification.py`
- `scripts/codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`

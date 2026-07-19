REVISED
::init gtkb lo
::open build


author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5555/WI-5556 Revised Codex No-Window Evidence Strictness

bridge_kind: prime_proposal
Document: gtkb-wi5555-wi5556-codex-no-window-evidence-strictness
Version: 003
Responds to: bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strictness-002.md
Revises: bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strictness-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5555
Work Item: WI-5556

target_paths: ["groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py", "groundtruth-kb/tests/test_codex_no_window_verification.py", "scripts/codex_no_window_smoke_probe.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Revision Claim

Version 002's sole blocking technical finding is accepted. The proposed
diagnostic anchor is widened from the `codex_models_manager::cache` submodule
to the complete `codex_models_manager::` logger namespace while retaining the
ERROR-severity requirement. This catches the canonical WI-5556 defect class
regardless of which model-manager submodule emits it without matching ordinary
prose containing words such as "cache" or "error".

The implementation and tests remain self-contained. They will use deterministic
literal input strings derived from the canonical WI-5556 problem statement and
this numbered review chain; no session-local, runtime-log, external-cache, home
directory, or other noncanonical artifact becomes a source, fixture, citation,
or dependency.

WI-5389 is now terminal VERIFIED at
`bridge/gtkb-wi5389-codex-no-window-schema-contract-004.md`, focused commit
`0bb45100ac922552aa4ec1c3879bc775e3e915a0`. The six WI-5555/WI-5556 targets
remain implementation-blocked until every target is clean at a fresh reviewed
preimage; one target is currently occupied by another workstream. No source,
test, dispatcher, TAFE, harness, runtime, Git, deployment, release, credential,
or project-state mutation occurred while preparing this revision.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  governed fleet-defect lifecycle while prohibiting direct dispatcher/runtime
  mutation.
- `DELIB-202666274` confirms project-level authorization while preserving
  bridge, claim, implementation-start, verification, and focused-finalization
  gates.
- `bridge/gtkb-wi5389-codex-no-window-schema-contract-004.md` is the terminal
  shared-validator predecessor, finalized at commit `0bb45100`.
- `bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strictness-002.md` is the
  independent NO-GO whose bounded namespace-scope finding this revision
  addresses.

## Owner Decisions / Input

- The active unrestricted project authorization
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` permits
  governed bridge/source/test work for active project members.
- The owner's canonical-artifact boundary requires every project dependency
  cited or used by a bridge artifact to be canonical. This revision therefore
  uses WI-5556 and the numbered bridge chain as authority and keeps test
  inputs self-contained.
- No new owner decision is required. Independent GO, exact claim,
  implementation-start, operation-time target authorization, clean preimages,
  independent VERIFIED, and focused finalization remain mandatory.

## Findings Addressed

### P1 - Namespace scope narrower than WI-5556

Accepted. IP-2, acceptance criterion 2, and TEST-11614 now cover any
ERROR-severity line whose logger identity begins with
`codex_models_manager::`. The match remains line-oriented and requires both
the exact namespace and ERROR severity. Negative controls cover unrelated
loggers, lower severities, and ordinary prose.

The suggested dependency on a historical local log is not adopted because it
would violate the owner-mandated canonicality boundary. Equivalent deterministic
literal lines exercise both `::cache` and `::manager` submodules, including a
manager-only control with no cache-submodule line.

### Non-Blocking WI-5389 Citation Staleness

Accepted. The predecessor citation now points to terminal VERIFIED v004 and
focused commit `0bb45100`.

## Requirement Sufficiency

Existing requirements remain sufficient. WI-5555/TEST-11613 defines exact
return-code typing. WI-5556/TEST-11614 requires readiness to fail on
`codex_models_manager` ERROR output without narrowing that obligation to one
submodule. The cited shared-validator, dispatcher, nonimpairment, bridge,
project-ordering, and verification specifications fully govern the corrected
slice.

## Scope Changes

- Widen IP-2's logger anchor from `codex_models_manager::cache` to
  `codex_models_manager::`.
- Add deterministic `::cache`, `::manager`, manager-only, unrelated-logger,
  lower-severity, and ordinary-prose controls.
- Refresh the WI-5389 predecessor citation to VERIFIED v004 and commit
  `0bb45100`.
- Preserve the six implementation targets, IP-1, IP-3, all specifications,
  project/PAUTH linkage, and every nonimpairment gate from v001.
- Do not begin implementation while any of the six targets is dirty or claimed.

## Corrected Proposed Scope

### IP-1 - Exact Return-Code Semantics

Add one package-canonical helper that accepts only exact `int` value `0`
excluding `bool`, or exact compatibility string `"0"`. Use it for command-step
and wrapper return-code checks. Preserve all other stable failure reasons.

### IP-2 - Model-Manager Diagnostic Detection

Detect a captured line only when it contains an ERROR severity marker and a
logger identity beginning with `codex_models_manager::`. The producer marks
the affected run and overall probe failed while retaining only its existing
bounded preview. The shared validator independently returns
`codex_no_window_verification_model_cache_error` for previously written
schema-v3 evidence containing the diagnostic.

Do not read, delete, rewrite, relocate, or depend on any external cache, home
directory, provider state, runtime log, or session-local artifact. Do not match
unrelated loggers, non-ERROR severities, or ordinary prose.

### IP-3 - Consumer And Nonimpairment Coverage

Prove both existing consumers surface the shared stable reason without adding
a new validation fork. Preserve private-desktop containment, zero visible
windows, workspace create/read/remove sentinel lifecycle, marker chain, wrapper,
expiry, ACL, PB-only role, and max-items requirements.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; DELIB-202666274; WI-5555; WI-5556; bridge/gtkb-wi5389-codex-no-window-schema-contract-004.md; bridge/gtkb-wi5555-wi5556-codex-no-window-evidence-strictness-002.md",
  "canonical_authority": "GOV-HARNESS-ONBOARDING-CONTRACT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; the linked bridge and project-authorization specifications",
  "primary_route": "Independent review of this REVISED proposal, exact claim and implementation-start validation after clean target ownership, six-path implementation, mapped tests, NEW report, independent VERIFIED, and focused finalization",
  "before_behavior": "Schema-v3 evidence accepts bool/float zero return codes and can report PASS while captured output contains an ERROR from the codex_models_manager namespace.",
  "after_behavior": "Only exact integer or compatibility string zero succeeds, any ERROR from the codex_models_manager namespace produces one stable fail-closed readiness reason, and clean schema-v3 evidence remains accepted.",
  "self_descriptive_naming": "is_success_return_code and codex_models_manager ERROR detection expose exact intent; the stable model-cache reason remains backward-compatible.",
  "obsolete_guidance_disposition": "The v001 cache-submodule-only anchor is superseded; no guidance or history is deleted.",
  "history_preservation": "Both WIs, both linked tests, WI-5389 terminal evidence, and this numbered bridge chain remain distinct and append-only.",
  "baseline": {
    "producer": "Schema-v3 probe captures bounded previews but does not classify codex_models_manager ERROR output.",
    "validator": "The shared validator uses equality-based return-code membership and does not inspect model-manager diagnostics.",
    "dispatcher": "Codex A remains PB-only, max-items 1, and dispatchable only when current no-window evidence passes."
  },
  "expected_result": {
    "return_codes": "Exact int 0 excluding bool and exact string 0 are accepted; bools, floats, and nonzero values fail.",
    "diagnostics": "ERROR lines from cache, manager, or another codex_models_manager submodule fail producer and both consumers with the stable reason.",
    "negative_controls": "Unrelated loggers, lower severities, and ordinary prose remain accepted.",
    "clean_evidence": "Clean schema-v3 evidence retains existing containment, sentinel, marker, wrapper, expiry, and ACL behavior."
  },
  "rollback": {
    "instructions": "Under separate authority, revert only the eventual six-path WI-5555/WI-5556 hunks; never disable Codex A or weaken readiness.",
    "verification": "Rerun the package and three platform modules, inspect exact target diffs, and confirm dispatcher/harness configuration remains unchanged."
  },
  "hard_invariants": [
    "Codex A remains prime-builder only and max-items 1.",
    "No dispatcher, TAFE, harness eligibility, role, routing, lease, or runtime-state mutation.",
    "No external cache, home, credential, runtime-log, or session-local artifact dependency.",
    "No implementation while any target is dirty, claimed, or outside the exact start packet.",
    "No self-review, staging, commit, push, deployment, or release before the applicable gates."
  ],
  "fail_closed_conditions": [
    "Dirty or claimed target bytes.",
    "Missing independent GO, matching claim, or schema-v3 implementation start.",
    "Malformed return-code type or detected codex_models_manager ERROR diagnostic.",
    "Any proposal to restore dispatchability by weakening containment, sentinel, or visible-window checks."
  ],
  "essential_context_preservation": "The implementation report must retain both WI/test identities, WI-5389 commit, exact six-path hashes, stable reasons, negative controls, nonimpairment checks, and independent consumer verification."
}
```

## Pre-Filing Preflight Subsection

Candidate-content preflights were executed against this completed revision
before insertion of this evidence subsection:

- Applicability packet:
  `sha256:da5bd58a258710cc425acfc70fcce7d6a75dc3c38d9201fdcb92a1e76d3969dc`
- Applicability result: `preflight_passed: true`
- Declared targets: all six `target_paths` above
- Missing required specifications: none
- Missing advisory specifications: none
- Blocking errors: none
- Mandatory clause result: exit code 0
- Clauses evaluated: 5 (`must_apply`: 3, `may_apply`: 2)
- Must-apply evidence gaps: 0
- Blocking clause gaps: 0

The governed revision helper must repeat both gates against the final filing
candidate and fail closed before publication if either result changes.

## Specification-Derived Verification Plan

| Specification / obligation | Test / command |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Producer tests prove any `codex_models_manager::` ERROR causes FAIL; both consumers return the stable reason; clean output remains PASS. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Package tests and source inspection prove the producer and both consumers use one shared classifier rather than independent forks. |
| TEST-11613 | Parameterized schema-v3 evidence rejects `false`, `true`, `0.0`, and nonzero step/wrapper codes while accepting exact `0` and `"0"`. |
| TEST-11614 | Self-contained inputs cover `::cache`, `::manager`, manager-only, an additional namespace submodule, unrelated logger, lower severity, and ordinary prose. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing schema-v3 suites remain green; exact-path diff confirms no dispatcher/harness configuration mutation. |
| `GOV-WORK-TREE-HYGIENE-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Before start, all six targets must be clean at terminal WI-5389-derived preimages and unclaimed; final diff remains six-path bounded. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run package, smoke-probe, verifier, and dispatcher focused modules plus Ruff, format, compile, diff, applicability, and clause gates. |

## Acceptance Criteria

1. Exact integer `0` and string `"0"` are the only successful return-code
   encodings; JSON booleans, floats, and nonzero values fail closed.
2. Any ERROR-severity line from the `codex_models_manager::` namespace,
   including a manager-only input with no cache-submodule line, makes the
   producer fail and both consumers report
   `codex_no_window_verification_model_cache_error`.
3. Clean two-run, three-command schema-v3 evidence remains accepted without a
   schema bump.
4. Unrelated logger identities, lower severities, warnings, and ordinary prose
   do not trigger the classifier.
5. Existing private-desktop, workspace-sentinel, marker, wrapper,
   zero-visible-window, expiry, and ACL tests remain green.
6. No noncanonical evidence dependency, external cache/home access,
   credential, dispatcher/TAFE configuration, eligibility, role, lease,
   runtime-state, live-worker, staging, commit, push, deployment, or release
   mutation occurs.
7. WI-5555/TEST-11613 and WI-5556/TEST-11614 remain distinct traceability
   carriers through one report, independent VERIFIED, and focused commit.

## Risk And Rollback

The widened namespace can overmatch only if unrelated text reproduces both the
exact logger namespace and ERROR severity. Line-oriented parsing and negative
controls bound that risk. The current dirty target creates a separate ownership
risk; implementation fails closed until all six exact paths are clean and
unclaimed under a fresh start packet.

Rollback requires separate authority and reverts only eventual attributable
six-path hunks. Numbered bridge, MemBase, PAUTH, claim, start, verdict, and
commit history remain append-only. Disabling A or weakening readiness is never
a rollback path.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/codex_no_window_verification.py`
- `groundtruth-kb/tests/test_codex_no_window_verification.py`
- `scripts/codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix(dispatch)`

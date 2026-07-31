NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# Implementation Proposal - Preserve Antigravity selected bridge prompts through CLI-compatible file transport

bridge_kind: prime_proposal
Document: gtkb-wi5217-antigravity-prompt-transport
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5217

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Genuine Antigravity C dispatch `2026-07-12T22-48-42Z-loyal-opposition-C-baf460` selected two actionable bridge documents and wrote the complete dispatcher assignment to its governed in-root stdin sidecar. The child argv then removed the prompt value but retained `agy --print`. Because `--print` is a value-taking CLI option, `agy` consumed the next token, `--print-timeout`, as its user prompt. C researched that unrelated flag, exited 0, and produced neither required verdict. The existing unit test explicitly expects the broken child argv shape.

Preserve the full assignment in the existing dispatch sidecar, but invoke Antigravity print mode with a short argv prompt that tells C to read and execute that exact in-root assignment file. This avoids a giant Windows argv payload, does not rely on unsupported stdin prompt parsing, and keeps the selected-document text authoritative and inspectable. Other harness prompt transports remain unchanged.

## Claim

Prime Builder proposes a bounded C-specific transport correction in dispatcher command composition and focused tests only. No harness registry, routing, model, role, lifecycle, worker lifetime, or runtime-state authority changes.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202666173` authorizes correction of every defect found during genuine six-harness proof; WI-5217 and TEST-11371 define the observed prompt-loss failure and exact expected outcome.

## In-Root Placement Evidence

Both target paths and the existing per-dispatch assignment sidecar are within `E:\GT-KB`. The sidecar is transport evidence only and does not become formal bridge authority.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected work must reach the chosen harness unchanged.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - eligibility remains controlled only through canonical transactions.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - C must perform genuine assigned-role work and produce governed evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - C requires equivalent actionable prompt delivery.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - successful process launch is not functional proof when the selected assignment is lost.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the 29,400-second worker lifetime and hidden process envelope remain intact.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the pointer assignment directs C back to authoritative selected bridge files and normal LO verdict rules.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - the dispatch/session context remains the author authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requirements are linked before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes mapped unit and genuine C checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, work item, PAUTH, and targets are declared.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live C failure has a durable defect lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dispatch, test, proposal, report, and verdict evidence remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - live misrouting triggers governed correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this is GT-KB dispatcher work.

## Prior Deliberations

- `DELIB-202666173` - complete six-harness governed proof and correct every discovered defect.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - cross-harness parity implementation authority.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` - verified requirement that every selected document advances independently.

## Owner Decisions / Input

- `DELIB-202666173` supplies owner authority for the discovered-defect correction.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712` forbids registry/routing edits, role/model changes, worker-lifetime reduction, direct runtime/lease mutation, and unrelated work.

## Proposed Scope

- Keep writing the complete dispatcher-composed assignment to the existing per-dispatch in-root prompt sidecar.
- For Antigravity stdin-configured targets only, retain `--print` with a short prompt value that names the exact sidecar and instructs C to read and execute its complete contents before acting.
- Do not pass the full rules-expanded assignment in argv and do not leave `--print` adjacent to `--print-timeout` without a value.
- Keep the sidecar path under the existing dispatch-run directory, correlated to dispatch ID, and passed as a project-relative or verified in-root path.
- Preserve `run_with_status`, hidden process containment, stdout/stderr/exit sidecars, selected-document leases, and the 29,400-second worker lifetime.
- Leave every non-C harness command and prompt transport byte-for-byte unchanged.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused command-composition test proves the assignment file contains selected documents and the short argv prompt names that file, never `--print-timeout`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | No config target changes; final eligibility is inspected through `gt bridge dispatch` only. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Fresh genuine C dispatch reads the assignment file and publishes a substantive canonical verdict. |
| Cross-harness parity carriers | Existing Claude, Codex, D, F, and H command-construction tests prove no transport regression. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Existing lifetime/hidden-launch tests continue to assert 29,400 seconds and no visible console. |
| Bridge/provenance carriers | Fresh C verdict metadata matches the dispatch/session envelope and selected document. |
| Verification/lifecycle carriers | Candidate/live applicability and clause preflights pass, focused dispatcher suites pass, and unrelated dirty paths remain excluded. |

## Acceptance Criteria

- C's `--print` option always has an intentional short prompt value; `--print-timeout` can never become the user prompt.
- The short prompt points to an existing in-root assignment file whose contents include every selected document and the canonical role/governance instructions.
- Full assignment text is not placed in child argv and no external file becomes a live dependency.
- Missing/unwritable assignment sidecars fail closed before launch; the pointer cannot escape the project root.
- Existing hidden-launch, status-wrapper, lease, per-document completion, and 29,400-second lifetime behavior remains green.
- A fresh C dispatch reads the real assignment and publishes a substantive canonical verdict or exposes another separately governed defect.
- Independent LO returns VERIFIED and creates a focused commit containing only these two source/test paths and this bridge chain.

## Risks / Rollback

Risk is that C treats the short pointer as the full task without opening the file. The pointer is explicit, the file is in-root and correlated to the dispatch ID, and the genuine proof must show actual selected-document review. Rollback reverts the two target paths; append-only evidence remains historical.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`

REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; governed bridge revision

bridge_kind: prime_proposal
Document: gtkb-wi5227-ollama-abrupt-exit-diagnostics
Version: 005
Responds to: bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-004.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5227
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
mutation_classes: ["source", "test", "bridge"]
linked_test: TEST-11381

# Dependency-Clearance Revision - WI-5227 Ollama D Abrupt-Exit Diagnostics

## Revision Claim

The sole blocking condition in version 004 has cleared. The peer thread
`gtkb-wi5255-bc-telemetry-worker-provenance` is terminal `VERIFIED` at version
008, so it no longer holds a nonterminal implementation report over the two
shared targets. Neither thread has a live work-intent claim.

Both exact WI-5227 targets are clean against current HEAD
`91dd60cfdfde221e81d8ae76074272809786829f`:

- `scripts/dispatcher_runtime.py` working and HEAD blob:
  `4dadd60f367c87f4094644f9186b8e28abd70cae`
- `platform_tests/scripts/test_dispatcher_runtime.py` working and HEAD blob:
  `4191b49bb5b50ae625a544043ae278d077b83930`

This revision therefore re-requests independent `GO` for the unchanged version
001 implementation plan. It adds no behavior, target, requirement, or
authorization. No source, test, dispatcher, TAFE, runtime, lease, Git, or
database mutation occurred while preparing this revision.

## Requirement Sufficiency

Existing requirements sufficient. WI-5227, TEST-11381, and the specifications
below already define the first-pass `0xFFFFFFFF` classification, bounded
diagnostics, no false verdict completion, exact-once exit/lease reconciliation,
allowance preservation, and independent verification requirements. The
version 004 NO-GO identified dependency ordering only, not a requirement or
design defect.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-202666274` preserves the active project-level authorization while
  retaining exact GO, claim, implementation-start, test, and verification
  gates.
- `DELIB-202666198` requires the observed abrupt-exit diagnostic regression to
  complete its governed defect lifecycle.
- `bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-001.md` is the unchanged
  substantive implementation proposal.
- `bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-004.md` is the independent
  dependency NO-GO and explicitly permits a fresh GO after WI-5255 becomes
  terminal.
- `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md` is the canonical
  terminal peer verdict that clears the shared-path hold.

## Owner Decisions / Input

No new owner decision is required. The active project authorization and
resumed fleet directive already cover WI-5227 through the normal bridge
lifecycle. This revision does not infer authority to bypass any mechanical
gate or alter dispatcher configuration.

## Findings Addressed

### F1 - Nonterminal WI-5255 shared-path ownership

Resolved. WI-5255 is latest `VERIFIED` at version 008. The implementation-start
peer-report rule excludes terminal `VERIFIED` threads from the nonterminal
shared-path hold. Both shared files are also clean and match their HEAD blobs.

## Scope Changes

None. The version 001 proposal remains operative:

1. Specialize the first reconciled no-verdict `4294967295` failure as
   `process_terminated_abruptly`.
2. Preserve the raw exit code and a bounded, honest diagnostic without
   inventing a provider cause.
3. Preserve shim telemetry, fatal-marker precedence, post-verdict
   reconciliation, retries, circuit breakers, routing, and all generous D
   allowances.
4. Add the focused TEST-11381 regression in the existing dispatcher test file.

No direct Ollama invocation, dispatcher/TAFE configuration change, runtime or
lease edit, credential action, unrelated mutation, push, deployment, or
release is in scope.

## Pre-Filing Preflight Subsection

Prime Builder evaluated this exact candidate through the mandatory
applicability and ADR/DCL clause preflights before filing. Filing is permitted
only when the applicability result reports `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, and
`blocking_errors: []`, and the clause result exits zero with no blocking gap.
The governed filing helper reruns both gates against the same candidate before
creating the numbered bridge file.

## Specification-Derived Verification Plan

| Requirement | Required evidence in the implementation report |
| --- | --- |
| WI-5227, TEST-11381, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused D-recipient fixture proves first-pass `process_terminated_abruptly`, nonempty bounded diagnostics, no verdict fields, exact-once processing, exact-once lease release, and stable second-pass no-op. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Full `platform_tests/scripts/test_dispatcher_runtime.py` suite passes, including fatal-marker and post-verdict reconciliation behavior. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Recipient state and failure record expose the specific reason/error type and raw exit code without an invented provider cause. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Fresh claim and implementation-start packet authorize exactly the two declared targets before editing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest plus Ruff check/format and candidate/live bridge preflights are recorded with observed results. |
| `GOV-WORK-TREE-HYGIENE-001` | Both targets remain clean at start or implementation stops and returns through the bridge; finalization includes only WI-5227 hunks and its numbered chain. |

Minimum commands remain those approved in version 001:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
python scripts/check_harness_parity.py --all --markdown
```

## Risk And Rollback

The shared targets are high-contention dispatcher files. Immediately before
claim/start, Prime Builder must re-read the latest WI-5255 status, exact Git
status, and both working/HEAD hashes. Any renewed nonterminal peer report or
dirty target stops implementation and requires another bridge disposition.

Behavioral risk remains bounded to diagnostic classification. Rollback removes
only the WI-5227 classification hunk and focused test. Append-only bridge and
MemBase evidence remain historical.

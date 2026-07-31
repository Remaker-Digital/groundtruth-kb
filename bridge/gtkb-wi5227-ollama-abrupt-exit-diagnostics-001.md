NEW

# Defect-Fix Proposal - Preserve actionable Ollama D abrupt-exit diagnostics

bridge_kind: prime_proposal
Document: gtkb-wi5227-ollama-abrupt-exit-diagnostics
Version: 001
Date: 2026-07-16 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-A-interactive-wi5227-20260716
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5227

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Claim

Correct the first-pass dispatcher classification for an Ollama D worker that
exits with Windows status `0xFFFFFFFF` before producing a governed verdict.
The canonical failure record and recipient state must say
`process_terminated_abruptly`, retain bounded non-sensitive diagnostic evidence,
and continue to reconcile the exit and document lease exactly once.

The retained incident is dispatch
`2026-07-14T01-35-27Z-loyal-opposition-D-f2292b`. Its canonical shim telemetry
records `exit_code=4294967295`, `exit_status=external_termination`, and
`stop_reason=external_termination`, but the dispatcher failure path still falls
through to `subprocess_execution_failed`. The later previous-launch detector
already knows the more specific `process_terminated_abruptly` classification;
the two canonical surfaces therefore disagree about the same exit signature.

## Defect / Reproduction

Read-only inspection established all of the following against HEAD
`42f6d02dfb4e91598247dce77c6b7506bee34732`:

1. WI-5227 and linked TEST-11381 are open and require actionable diagnostics,
   no false verdict completion, one exit reconciliation, and one lease release
   for an Ollama D `4294967295` exit.
2. The retained incident telemetry at
   `.gtkb-state/bridge-poller/dispatch-runs/2026-07-14T01-35-27Z-loyal-opposition-D-f2292b.telemetry.json`
   records the exact exit signature and external termination after 31 seconds.
3. `scripts/dispatcher_runtime.py::_process_pending_exit_codes_for_last_launch`
   gives an unresolved nonzero exit the generic reason and error type
   `subprocess_execution_failed`; no `4294967295` branch specializes that first
   failure record.
4. `_detect_previous_launch_failure` separately maps `4294967295` to
   `process_terminated_abruptly`. The specific classification therefore appears
   only on a later cycle, not when the exit is first reconciled.
5. Existing tests cover Prime work-intent release on abrupt termination and a
   generic shim `external_termination` envelope, but no test exercises the
   complete Loyal Opposition D failure-state, failure-log, verdict, telemetry,
   processing, and document-lease contract required by TEST-11381.

## Requirement Sufficiency

Existing requirements sufficient.

WI-5227, TEST-11381, and the linked dispatcher/harness specifications already
define the needed behavior. No new specification or requirement mutation is
required for this bounded repair.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`:

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Dirty-Tree Ownership Boundary

Both target files contain substantial pre-existing work owned by other active
threads and are quarantined, not adopted by this proposal:

| Path | HEAD blob | Filing-time working blob | Existing diff |
| --- | --- | --- | --- |
| `scripts/dispatcher_runtime.py` | `71bfa757be6404ecdb8b42444e8caf945d248097` | `f8b7ed91d78cb4da97dfa7f1ef6bc2137c230b46` | 76 insertions, 11 deletions |
| `platform_tests/scripts/test_dispatcher_runtime.py` | `2ca5e99a24dc355c236dc14dcc0c9e8b8ec67a57` | `b5ef52b95588ae6ad5fe0027985b6944c8428685` | 186 insertions, 16 deletions |

The implementation may add only the exact WI-5227 classification/diagnostic
hunk and its focused regression. Trusted worker-context/provenance work belongs
to WI-5255; session-envelope, work-intent, cap, finalization, and other current
dirty hunks remain foreign. If either filing-time blob changes before
implementation-start, Prime must re-audit ownership and update the evidence
before editing. Finalization must use an exact isolated include set and may not
stage or commit foreign bytes.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires functional, diagnosable governed harness execution and directly governs TEST-11381.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires the central dispatcher to reconcile worker outcomes and failures consistently.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires dispatcher status and failure evidence to be operationally truthful and actionable.
- `ADR-DISPATCHER-ARCHITECTURE-001` - keeps failure classification in the harness-agnostic dispatcher lifecycle rather than adding a D-only side channel.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct numbered bridge review and independent verdict authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite its complete governing specification set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent verification against tests derived from the linked specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires active PAUTH, project, work-item, and target-path metadata.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the defect, linked test, proposal, implementation report, and verdict as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the evidence-bearing lifecycle rather than treating a runtime observation as informal state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires implementation and verification artifacts for this accepted defect.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps dispatcher implementation and tests inside the GT-KB platform root.
- `GOV-STANDING-BACKLOG-001` - keeps WI-5227 visible until independently verified and finalized.
- `SPEC-AUQ-POLICY-ENGINE-001` - preserves the standing owner authorization boundary and does not infer new owner approval.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to use the governed helper path and self-enforce protected-file gates.

## Prior Deliberations

- `DELIB-202666198` - owner-resumed fleet goal and governed WI-5226 diagnostic-telemetry predecessor; it confirms that diagnostic-loss defects must follow the full bridge lifecycle.
- `DELIB-20266581` - prior dispatcher post-verdict exit reconciliation; it preserves successful verdict reconciliation while leaving no-verdict nonzero exits as failures.
- `DELIB-20265026` - prior Ollama provider-failure fallback and backoff review; this proposal does not weaken retry or fallback behavior.
- `bridge/gtkb-wi5226-openrouter-diagnostic-telemetry-004.md` - VERIFIED shared telemetry predecessor. It preserves worker-emitted bounded failure reasons but does not specialize a diagnostic-free `0xFFFFFFFF` first-pass dispatcher failure.
- `WI-5255` - related, nonterminal trusted worker-provenance work. This proposal excludes its hunks and does not depend on inferred verdict prose.

## Owner Decisions / Input

- `DELIB-202666274` underlies active project authorization `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`, which covers project source/test/bridge work while retaining exact GO, claim, implementation-start, testing, independent verification, and operation-specific Git gates.
- The owner-resumed fleet directive explicitly requires observer-created WI-5227 to be corrected through work item, linked test, PAUTH, bridge GO, implementation, testing, independent verification, and focused commit.
- The legacy project label contains `GOOSE`, but no Goose or harness G exists or is in scope. WI-5319 owns that naming cleanup. This proposal concerns only the registered Ollama D route and does not contact or configure any harness.

## Proposed Scope

1. In `_process_pending_exit_codes_for_last_launch`, when a worker has no more
   specific fatal marker or completed verdict and its exit code is
   `4294967295`, classify the first reconciled failure as
   `process_terminated_abruptly` in recipient state, `last_launch`, and the
   canonical dispatch-failure record.
2. Preserve bounded diagnostic evidence in the failure record: the exact exit
   signature, the inspected stdout/stderr paths when present, and an honest
   diagnostic that the process terminated before a governed verdict and no
   more specific worker-output marker was available. Do not invent a provider
   cause when the retained evidence proves only abrupt process termination.
3. Keep shim telemetry's established `external_termination` outcome and raw
   exit code. Do not change its schema or edit retained runtime evidence.
4. Add a focused Ollama D Loyal Opposition regression that exercises the
   observed exit signature and proves: specific first-pass classification,
   nonempty diagnostic evidence, no false verdict completion, one exit
   processing, one document-lease release, and stable second-pass no-op.
5. Preserve post-verdict nonzero reconciliation, fatal-marker precedence,
   retries, circuit-breaker semantics, launch caps, routing, and the full
   600-turn, 900-second operation, 3600-second model/session, 29400-second
   worker, and 29700-second lease allowances.

Out of scope: direct Ollama invocation, provider/model changes, eligibility or
ranking changes, dispatcher/TAFE configuration, runtime JSON or lease mutation,
credential work, source/test hunks owned by other threads, Git staging or
commit before independent VERIFIED finalization, push, deployment, and release.

## Specification-Derived Verification Plan

| Specification / requirement | Executed verification required before implementation report |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, WI-5227, TEST-11381 | A focused D-recipient regression creates a `4294967295` no-verdict exit and asserts `process_terminated_abruptly`, nonempty diagnostic evidence, no verdict fields, exact-once processing, exact-once document-lease release, and stable reprocessing. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Run the focused abrupt-exit test plus existing pending-exit, post-verdict, fatal-marker, ledger, and lease-reconciliation tests in `platform_tests/scripts/test_dispatcher_runtime.py`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Assert the recipient state and dispatch-failure JSONL expose the specific reason/error type on the first reconciliation, while shim telemetry retains `external_termination` and raw exit code. |
| Bridge and artifact governance specs | Run applicability and mandatory clause preflights on the filed implementation report; carry forward all linked specs and exact command/results evidence. |
| Python quality and ownership boundary | Run `ruff check` and `ruff format --check` on the two target files, plus exact diff/hunk review against the filing-time ownership boundary. |

Minimum command set:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
python scripts/check_harness_parity.py --all --markdown
```

## Acceptance Criteria

- A D Loyal Opposition `4294967295` exit with no governed verdict is classified
  as `process_terminated_abruptly` during the first exit reconciliation, not
  merely on a later previous-launch check.
- Canonical failure evidence contains the raw exit code and a nonempty bounded
  diagnostic without claiming an unproved provider cause.
- Canonical shim telemetry retains `exit_status=external_termination`,
  `stop_reason=external_termination`, and the raw exit code.
- No false GO, NO-GO, or VERIFIED completion is recorded.
- The exit is processed once, each document lease is released once, and a
  repeated reconciliation call does not duplicate either action or failure
  evidence.
- Existing fatal-marker and post-verdict reconciliation behavior remains green.
- The generous D allowances remain byte-for-byte unchanged.
- Only exact WI-5227 source/test hunks are adopted; all pre-existing dirty bytes
  remain quarantined and excluded from finalization.
- No harness, dispatcher/TAFE configuration, retained runtime state, credential,
  push, deployment, or release mutation occurs.

## Pre-Filing Preflight

The completed candidate was checked before filing through both mandatory
content-file preflights:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- Clause preflight: 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`,
  0 evidence gaps, 0 blocking gaps, exit code 0.

The content-derived packet hash is intentionally not self-embedded because
adding it would change the candidate content and invalidate that hash. The
helper output remains the filing-time packet evidence.

Commands:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5227-ollama-abrupt-exit-diagnostics --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5227-ollama-abrupt-exit-diagnostics-001.md
groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5227-ollama-abrupt-exit-diagnostics --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5227-ollama-abrupt-exit-diagnostics-001.md
```

## Risks / Rollback

Risk is moderate because both target files carry unrelated active work. The
primary control is exact-hunk ownership: implementation must stop and re-audit
if the filing-time blobs change, tests must exercise the integrated current
tree, and finalization must prove an isolated include set.

Behavioral risk is low and bounded to diagnostic classification. Fatal worker
markers remain more specific and keep precedence; successful post-verdict exits
remain reconciled; ordinary nonzero exits remain `subprocess_execution_failed`.

Rollback is removal of only the WI-5227 classification/diagnostic hunk and its
focused regression. Bridge and authorization evidence remains append-only.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`

REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-05T13-46-01Z-prime-builder-A-0e1a17
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex auto-dispatched prime-builder worker; ::init gtkb pb; resolved role prime-builder; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Serialize overlapping target_paths across implementation-start and dispatcher dispatch

bridge_kind: prime_proposal
Document: gtkb-wi4996-target-path-dispatch-serialization
Version: 003
Date: 2026-07-05 UTC
Responds to: bridge/gtkb-wi4996-target-path-dispatch-serialization-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4996

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Revise the WI-4996 proposal after Loyal Opposition NO-GO at `bridge/gtkb-wi4996-target-path-dispatch-serialization-002.md`.

The corrected design uses the implementation-start authorization path as the primary protection against overlapping source-file implementation and uses dispatcher-side target-path filtering as an optimization to avoid launching workers that would be blocked by that protection. This closes both cases identified by Loyal Opposition:

- same-batch dispatch of two GO threads that share target paths;
- cross-tick dispatch where a later GO thread overlaps a still in-flight work-intent claim or implementation authorization packet from an earlier tick.

The proposal remains source-only and keeps bridge, project authorization, owner-decision, and verification gates intact.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4996` that prevents parallel Prime implementation work from modifying the same source target path under separate bridge threads before the earlier thread is reported, verified, and committed or otherwise released.

## Requirement Sufficiency

Existing requirements are sufficient. The work item, the active project authorization, the bridge authority rules, and the implementation-start gate rules already require live GO authorization, work-intent ownership, target-path scoping, and spec-derived verification before protected implementation work.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

No Agent Red lifecycle-independent repository, archive checkout, or external path is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime files this revision as `REVISED`; Loyal Opposition remains the only authority for `GO`, `NO-GO`, and `VERIFIED`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the bridge, dispatcher, implementation-start, project-linkage, and verification specifications constraining the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward linked specs, map each to focused tests, and report exact command results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal includes project authorization, project, work item, and concrete `target_paths` metadata.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization cannot bypass the live bridge GO, work-intent claim, or implementation-start packet requirements.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher selection, dispatch state, worker launching, and suppression evidence are the central dispatch-service behavior under change.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher remains the coordination surface for headless workers and must fail closed around queue state and launch decisions.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex protected-file mutation enforcement must remain backed by the implementation-start gate and regression tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this coordination defect is preserved through bridge files, work-item linkage, and verification artifacts instead of transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix preserves artifact-first change control and evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation report and verification verdict must record lifecycle evidence for the changed dispatcher/gate behavior.
- `SPEC-AUQ-POLICY-ENGINE-001` - no new owner approval is requested in prose; carried owner evidence is listed in the owner-decision section.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains platform-side under `scripts/` and `platform_tests/`, not under an adopter application.
- `GOV-STANDING-BACKLOG-001` - WI-4996 is the recorded backlog/work-item response to the WI-4995 and WI-4992 shared-file contention.

## Prior Deliberations

- `bridge/gtkb-wi4995-document-lease-held-health-004.md` - parent NO-GO whose N1 documents the WI-4995 and WI-4992 shared-file entanglement. It states that two GO'd threads sharing a source file must not be implemented in parallel into one uncommitted working tree, and it records WI-4996 as the dispatcher-modernization follow-up.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directive governing the dispatcher-modernization program and the goal of making headless dispatch stable enough for autonomous bridge progress.
- `bridge/gtkb-wi4996-target-path-dispatch-serialization-002.md` - Loyal Opposition review of the first proposal. This revision directly addresses N1 through N5.
- Sibling bridge chains for `WI-4992` and `WI-4995` - adjacent implementation work whose shared target file created the motivating contention. The exact parent evidence is preserved in `bridge/gtkb-wi4995-document-lease-held-health-004.md`.

Semantic Deliberation Archive searches for "WI-4996 target_paths overlap serialization headless dispatch WI-4995 WI-4992", "DELIB-20260703 HEADLESS DISPATCH STABILITY GOAL dispatcher modernization", and "implementation authorization target paths overlap go implementation claim" returned no matching records in this session. Direct bridge prior art above governs the revision.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - carried owner directive for the dispatcher-modernization program.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4996`.

No new owner decision is required for this revision because Prime adopts the Loyal Opposition preferred design direction: implementation-start protection is primary, dispatcher suppression is an optimization, and no residual dispatcher-only interactive exposure is accepted.

## Revision Response To NO-GO Findings

### N1 - Prior Deliberations placeholder removed

The placeholder from `-001` is removed. This revision cites the parent WI-4995 NO-GO, the owner directive, the WI-4996 NO-GO, and the sibling WI-4992/WI-4995 chains. The DA semantic searches performed in this session are disclosed, and the direct bridge prior art is used as the operative provenance.

### N2 - Cross-tick and in-flight overlap covered

The scope now covers any later GO thread whose implementation target paths overlap:

- a currently selected earlier item in the same dispatcher batch;
- an active work-intent or `go_implementation` claim from a prior tick;
- a valid named implementation authorization packet held by another session; or
- a GO thread whose implementation remains unreported or whose post-implementation report has not reached `VERIFIED`.

The acceptance criteria require a later overlapping item to be suppressed and recorded even when it is the only item selected during a later tick.

### N3 - Implementation-start gate is the primary choke point

The implementation-start path is the primary guard. The implementation should make `implementation_authorization.py begin` fail closed when another active session has a live claim plus a valid named packet reserving overlapping target paths. `implementation_start_gate.py` remains the protected-mutation backstop, and dispatcher-side filtering prevents unnecessary worker launch before the backstop is reached.

### N4 - Glob overlap predicate defined

The overlap predicate is:

1. Normalize paths and patterns to repo-relative POSIX form.
2. Treat exact file matches as overlap.
3. Treat glob-vs-file overlap through `fnmatch` plus existing `/**` directory-prefix semantics.
4. Treat glob-vs-glob overlap conservatively by expanding against the finite union of declared concrete target paths already present in the compared packets/items; when both sides are broad globs and no finite concrete witness is available, fail closed as overlapping unless one pattern is provably disjoint by top-level path prefix.
5. Emit deterministic suppression metadata naming the suppressed document, the holder or earlier selected document, and the overlapping normalized path or pattern.

This avoids false negatives such as `scripts/*.py` versus `scripts/dispatcher_runtime.py`, while limiting false positives by using top-level prefix disjointness for patterns such as `scripts/**` versus `platform_tests/**`.

### N5 - Spec-to-test mapping made concrete

The verification plan below maps every linked specification to concrete tests, preflights, or command evidence. It does not defer most rows to the implementation report.

## Proposed Scope

- Add or complete begin-time target-path collision protection in `scripts/implementation_authorization.py` so `begin --bridge-id <later>` refuses to write a current or named authorization packet when another session's active work-intent claim plus valid named packet reserves overlapping target paths.
- Preserve the existing `scripts/implementation_start_gate.py` protected-mutation collision backstop, adding regression coverage where needed for exact-file and glob overlap behavior.
- Add dispatcher-side target-path serialization in `scripts/dispatcher_runtime.py` so Prime headless dispatch suppresses later GO items whose target paths overlap earlier selected items or live in-flight claims/packets.
- Route target-path overlap suppressions to `dispatch-suppressions.jsonl`, not `dispatch-failures.jsonl`, with a distinct reason such as `target_path_overlap_inflight` or `target_path_overlap_selected`.
- Preserve existing work-intent filtering, document leases, project-authorization packet creation, selected-batch signature semantics, provider-failure backoff, NO-GO revision dispatch, and Loyal Opposition NEW/REVISED dispatch behavior.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File this revision through `revise_bridge.py file`; confirm live bridge state shows `REVISED` at `bridge/gtkb-wi4996-target-path-dispatch-serialization-003.md` and no prior bridge file was edited. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4996-target-path-dispatch-serialization` after filing; require `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry this table forward and include observed pytest, ruff check, and ruff format results for changed Python files. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate and live bridge applicability preflights must accept the project authorization, project, work item, and `target_paths` metadata. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Add tests where `implementation_authorization.py begin` refuses a later overlapping bridge despite active project authorization, and where non-overlapping bridges still receive packets. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add dispatcher tests showing same-batch overlapping GO items launch only the oldest eligible item, disjoint GO items still fan out to the cap, and cross-tick in-flight overlaps are suppressed. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json --compact` or equivalent status command after implementation and show suppression evidence is visible without counting as provider failure. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused implementation-start gate tests proving Codex protected mutation remains blocked when a different active claim reserves the same exact or glob-matched path. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve the bridge audit chain and implementation report evidence; no state-only or chat-only closure. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Verify the fix produces durable bridge/report/test artifacts instead of relying on session memory. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Post-implementation report must list changed files, recommended commit type, and lifecycle evidence for suppression behavior. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Confirm no new owner decision is requested through prose and that carried owner evidence remains in the Owner Decisions / Input section. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm changed paths remain under `scripts/` and `platform_tests/`; no `applications/Agent_Red/` or external repository path is touched. |
| `GOV-STANDING-BACKLOG-001` | Confirm implementation report cites WI-4996 and preserves the dispatcher-modernization project linkage. |

Focused command set expected for implementation verification:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/dispatcher_runtime.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json --compact
```

## Acceptance Criteria

- `implementation_authorization.py begin --bridge-id <later>` refuses to create or overwrite authorization packets when another active session holds a work-intent claim plus valid named packet whose `target_path_globs` overlap the later bridge's target paths.
- The begin-time collision check allows non-overlapping bridges and ignores expired or invalid peer claims/packets.
- The protected-mutation gate continues to block an edit when another active claim plus valid named packet reserves the same exact path.
- The protected-mutation gate covers glob-vs-file overlap, including a peer packet with `scripts/*.py` and an attempted edit to `scripts/dispatcher_runtime.py`.
- A dispatcher batch with two GO bridge documents sharing a source target path launches only the oldest eligible document and records a target-path-overlap suppression for the later one.
- A dispatcher batch with GO documents whose `target_paths` are disjoint still fans out up to the effective max-items cap.
- A later dispatcher tick suppresses a GO document whose `target_paths` overlap an in-flight work-intent-held or packet-held thread, even when the later document is the only selected item for that tick.
- NO-GO revision dispatch and latest NEW/REVISED Loyal Opposition dispatch remain unchanged.
- Expected target-path overlap suppressions are routed to `dispatch-suppressions.jsonl` and surfaced in dispatch status/diagnostics without being treated as provider failures.

## Pre-Filing Preflight Subsection

Before live filing, Prime Builder performs candidate-content preflights through the governed revision helper:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4996-target-path-dispatch-serialization --content-file <candidate> --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4996-target-path-dispatch-serialization --content-file <candidate>
```

The helper refuses live filing unless both candidate preflights exit cleanly. After filing, Loyal Opposition can re-run the same preflights against the live `REVISED` file.

## Risks / Rollback

Risk is moderate because the change touches dispatcher worker selection and implementation-start authorization. The intended failure mode is conservative over-serialization rather than allowing two sessions to edit the same file under separate bridge threads.

Throughput risk is bounded by the defined overlap predicate and by preserving normal fan-out for disjoint target paths. False positives should appear as expected suppressions with explicit overlap evidence, allowing later tuning.

Rollback is a revert of source and test changes from the implementation commit. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

## Recommended Commit Type

`fix`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

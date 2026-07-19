REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder revision worker; transcript-defined Prime Builder role
author_metadata_source: explicit_interactive_session_metadata

# WI-5396 - Clean re-execution of session-envelope exact Git-root repair

bridge_kind: prime_proposal
Document: gtkb-wi5396-session-envelope-exact-git-root
Version: 005
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5396

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_fab13_retention_policy.py"]

implementation_scope: clean two-target revert and re-execution under fresh operation-time authority, plus correction of the stale live-PID provenance fixture in the already-approved test target
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This revision responds to every finding in
`bridge/gtkb-wi5396-session-envelope-exact-git-root-004.md`. It does not seek
a waiver and does not claim that reversing and reapplying a patch after an
ordering violation retroactively authorized the original writes. The current
two-target bytes are treated as unverified implementation residue.

The requested successor GO is limited to a fresh, path-bounded transaction:
after a new matching work-intent claim and implementation-start packet exist,
prove that the current two-target diff is exactly the disclosed WI-5396 diff,
restore both targets to the current committed baseline, prove that the two
targets are clean, and reapply the reviewed repair under the live packet. If
the pre-transaction diff or hashes do not match the disclosed WI-5396 residue,
the transaction fails closed without overwriting concurrent or unrelated work.

The revision also addresses the complete target-module failure rather than
waiving it. The current dispatcher runtime requires a live dispatch artifact
to carry both a live PID and matching `.create_time_epoch` provenance. The
existing target test creates `live.pid` and `live.stdout.log` but omits the
required provenance sidecar, so the runtime correctly classifies those
artifacts as unproven and prunes them. The test fixture will write the current
process create time using the runtime's existing provenance contract and will
assert that the PID, log, and provenance sidecar are all preserved. No change
to `scripts/dispatcher_runtime.py` is requested.

## NO-GO Finding Responses

### Finding 1 - Implementation-start ordering violation

Conceded. Version 003 disclosed that protected bytes were first written before
the claim/start packet. A later reverse/reapply does not cure that event. This
revision requests no exception. It requests a new independent GO and requires
the following order for the retry:

1. Confirm this version 005 proposal is the operative reviewed proposal and a
   fresh independent GO is latest.
2. Acquire a fresh `go_implementation` claim for this exact thread.
3. Obtain a fresh implementation-start packet covering exactly the two target
   paths.
4. Before mutation, capture the two path statuses, hashes, and binary diff and
   compare them to the version 003 reported residue. Any mismatch fails closed
   so unrelated bytes are preserved.
5. Under the active packet, restore only the two exact targets to committed
   `HEAD`, verify both paths are clean, and then reapply the reviewed WI-5396
   exact-root patch and the test-fixture correction.
6. Record packet issuance time, pre-restore evidence, clean-baseline evidence,
   post-write hashes, and target-scoped diff in the new implementation report.

This is a new lawful transaction. It makes no retroactive authorization claim.

### Finding 2 - Full target test module fails

Reproduced on 2026-07-17 with the exact full-module command: `1 failed, 7
passed`. The failure is
`test_dispatch_runs_prune_preserves_live_pid_artifacts`, where `live.pid` is
deleted. The cause is a stale test fixture, not environmental noise:

- `scripts/dispatcher_runtime.py` defines `PID_CREATE_TIME_SUFFIX` as
  `.create_time_epoch`.
- `_run_artifact_live()` requires `_pid_alive(pid)` and
  `_dispatch_pid_provenance_matches(...)`.
- The failing fixture creates a PID and log but no create-time sidecar.

The retry will update only the already-approved test target to create matching
current-process provenance through the runtime's public module surface, assert
the create time is available, write `live.create_time_epoch`, and assert that
all three live artifacts survive retention pruning. Missing or mismatched
provenance must continue to fail closed; no runtime safety rule is weakened.
The full eight-test module must pass before any implementation report is filed.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202666274` - project-scoped modernization authority that preserves
  independent GO, claim, start, verification, and exact Git gates.
- Owner directive, 2026-07-16 - correct the Git/console failure without
  impairing or disabling any harness.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-001.md` - original
  exact-root proposal and specification-derived verification plan.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-002.md` - original GO.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-003.md` - implementation
  report disclosing the ordering violation and the two-target residue.
- `bridge/gtkb-wi5396-session-envelope-exact-git-root-004.md` - controlling
  NO-GO requiring clean re-execution or a waiver and resolution of the full
  target-module failure. This revision selects clean re-execution, not waiver.
- `bridge/gtkb-wi4893-daemon-test-provenance-scope-amendment-003.md` - verified
  precedent for updating tests that expect live dispatch artifacts to provide
  matching PID create-time provenance.

The current deliberation search produced no more specific owner decision that
waives implementation-start ordering or the failing test, and this proposal
does not infer one.

## Owner Decisions / Input

No new owner decision or waiver is requested. Existing project authority is
sufficient to request independent review of this bounded retry. A fresh GO,
claim, and implementation-start packet remain mandatory before either target
is restored or edited.

## Requirement Sufficiency

Existing requirements sufficient. The linked session-envelope durability,
exact worktree evidence, dispatcher PID-provenance, nonimpairment,
implementation-authorization, and spec-derived verification requirements
already determine the required behavior. This revision corrects execution
ordering and a stale test fixture; it introduces no new product requirement
and requests no waiver or specification mutation.

## Proposed Scope

1. Revalidate operative PAUTH, latest GO, claim ownership, exact two-target
   packet scope, and no overlapping foreign claim.
2. Prove the current target bytes exactly match the disclosed WI-5396 residue;
   fail closed on any mismatch.
3. Under the active packet, restore only the two exact targets to committed
   `HEAD` and prove both are clean.
4. Reimplement the exact-root bounded Git probes in `envelope.py` under the
   active packet.
5. Reimplement the exact-root, mismatch, timeout, and bounded-output tests.
6. Correct the live-PID retention fixture in the same test target by writing a
   matching create-time provenance sidecar and asserting all live artifacts
   are retained.
7. Run the complete target module, focused session-envelope cases, unchanged
   frozen harness-parity coverage, Ruff, and target-scoped diff checks.
8. File a fresh implementation report only if every required command passes.

## Out Of Scope

- Any mutation to `scripts/dispatcher_runtime.py` or another source/test file.
- Any waiver, retroactive authorization claim, or weakening of PID provenance.
- Any broad restore, reset, clean, checkout, staging, commit, push, release,
  deployment, credential, dispatcher, TAFE, routing, or harness mutation.
- Any overwrite of bytes that differ from the disclosed WI-5396 residue.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Capture fresh GO, claim, and start packet before the first restore/write; compare packet time with transaction evidence. | Every retry mutation occurs after and within fresh authority; no retroactive claim is made. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare current two-target hashes/diff to the disclosed residue, restore only exact targets, and prove a clean two-target baseline before reapplication. | Concurrent or unrelated bytes cause fail-closed behavior; no unrelated path is touched. |
| `DCL-SESSION-ENVELOPE-DURABILITY-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run focused exact-root, nested-root, probe-failure, timeout, and output-bound tests. | Session close remains bounded and fail-soft while exact roots retain complete status evidence. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `DCL-DISPATCH-ENVELOPE-RULES-001` | Run `test_dispatch_runs_prune_preserves_live_pid_artifacts` with matching `.create_time_epoch` fixture evidence. | PID, stdout log, and provenance sidecar survive pruning only when PID and create time match. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete `platform_tests/scripts/test_fab13_retention_policy.py` module. | All 8 tests pass; no failure is waived or labeled noise. |
| `GOV-HARNESS-ROLE-PORTABILITY-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the unchanged frozen harness-parity test/module and inspect target-scoped diff. | Harness parity reaches assertions; no harness or routing surface changes. |

## Required Commands And Evidence

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab13_retention_policy.py -q --tb=short --timeout=300`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab13_retention_policy.py -q --tb=short --timeout=300 -k "session_envelope_git_status or dispatch_runs_prune_preserves_live_pid_artifacts"`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short --timeout=300`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py`
- `git diff --check -- groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_fab13_retention_policy.py`
- Path-scoped status, hashes, binary diff, packet timestamp, clean-baseline
  proof, and final two-target diff.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5396 versions 001-004; reproduced full target-module failure on 2026-07-17; WI-4893 verified PID-provenance test precedent","canonical_authority":"DCL-SESSION-ENVELOPE-DURABILITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001","primary_route":"fresh GO, claim, and implementation-start packet; exact two-target clean restore; reviewed reimplementation; complete target-module verification","before_behavior":"Current target bytes include an implementation first written before operation-time authority, and the target test module fails because its live-artifact fixture omits required PID create-time provenance.","after_behavior":"The two targets are restored and reimplemented only under fresh authority; exact-root session status remains bounded; the live-artifact fixture supplies matching provenance; the complete target module passes.","self_descriptive_naming":"Exact-root fields and live PID provenance sidecar names directly identify project ownership and process identity evidence.","obsolete_guidance_disposition":"The prior reverse/reapply cure claim is rejected; PID-only live-artifact fixtures are updated to the current provenance contract; no timeout or safety rule is weakened.","history_preservation":"Versions 003 and 004 preserve the ordering defect and NO-GO; version 005 requests a new transaction without rewriting prior evidence.","baseline":{"implementation_order":"first write preceded claim/start","target_module":"1 failed, 7 passed","failure":"live.pid pruned because live.create_time_epoch is absent","target_state":"two disclosed modified paths"},"expected_result":{"implementation_order":"all retry writes follow fresh GO, claim, and start","target_module":"8 passed","nested_root":"explicit unavailable without ancestor scan","exact_root":"bounded complete Git status evidence","live_artifacts":"pid, stdout log, and matching create-time sidecar retained"},"rollback":{"instructions":"Under a governed successor, restore only the two exact targets to the captured committed baseline.","verification":"two-target status/hash proof plus complete FAB-13 and frozen harness-parity modules"},"hard_invariants":["no waiver or retroactive authorization","no mutation before fresh claim/start","no overwrite when current residue hashes differ","no PID-provenance weakening","no harness, dispatcher, TAFE, routing, credential, release, or deployment mutation","no path outside the two exact targets is restored or edited"],"fail_closed_conditions":["latest status is not a fresh lawful GO","claim or start packet is absent, stale, or target-mismatched","current two-target residue differs from disclosed evidence","clean two-target baseline cannot be proven","complete target module is not 8 of 8 passing","frozen parity or static checks fail"],"essential_context_preservation":"Preserve the original ordering defect, exact target identities, nested-root containment purpose, process-provenance safety contract, complete-module failure evidence, and independent verification requirement."}
```

## Acceptance Criteria

1. Fresh GO, matching claim, and implementation-start packet exist before the
   first retry restore or write.
2. Pre-transaction bytes match the disclosed WI-5396 residue; otherwise the
   retry stops without mutation.
3. Both exact targets are restored to committed baseline and proven clean
   before the reviewed repair is reapplied.
4. Nested roots never scan or report an ancestor repository; exact roots
   retain bounded clean/dirty/count/truncation evidence.
5. The live-PID fixture supplies matching create-time provenance and proves
   all live artifacts survive pruning without weakening production logic.
6. The complete target test module passes 8 of 8 with no waiver.
7. Frozen harness parity, Ruff, format, and diff checks pass.
8. No path outside the two exact targets is restored or edited, and no Git
   finalization, release, deployment, or external mutation occurs.

## Risks / Rollback

The principal risk is overwriting bytes added after the version 003 report.
The mandatory pre-transaction hash/diff comparison makes any mismatch a
fail-closed condition. Rollback after a correctly entered retry is to restore
the two targets to the captured committed baseline through another governed
successor; no broad worktree operation is permitted.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `platform_tests/scripts/test_fab13_retention_policy.py`

## Recommended Commit Type

`fix`

## Pre-Filing Preflight Subsection

Before filing this revision, Prime Builder runs candidate applicability and
clause preflights against this completed content. Filing is permitted only when
`missing_required_specs: []`, `missing_advisory_specs: []`, and blocking clause
gaps are all empty. The live version is rechecked after helper filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

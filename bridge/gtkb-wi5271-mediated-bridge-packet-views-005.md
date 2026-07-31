REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5271 Mediated Bridge Packet Views - Foundation-Aware Revision

bridge_kind: prime_proposal
Document: gtkb-wi5271-mediated-bridge-packet-views
Version: 005
Responds to: bridge/gtkb-wi5271-mediated-bridge-packet-views-004.md
Revises: bridge/gtkb-wi5271-mediated-bridge-packet-views-001.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5271-MEDIATED-BRIDGE-VIEWS-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5271
Related Work Items: WI-5268, WI-5270, WI-5464
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_read_commands.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Revision Claim

Every version-004 blocking condition is accepted and re-evaluated against
current canonical state.

The foundation is no longer proposed or missing authority:

- `bridge/gtkb-dispatcher-black-box-spec-foundation-034.md` is independent
  `VERIFIED` and is committed at
  `6262862c8852d4d94530a4074a3047f921e7164e`;
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`,
  `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`, and
  `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` now exist in MemBase at version
  2, `status=specified`, with one executable assertion each;
- fresh assertion runs for those three records and
  `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` all report aggregate
  `PASS`;
- the active WI-5271 PAUTH cites the now-real records, permits only
  bridge/metadata/source/test work for WI-5271, and continues to forbid
  dispatcher mutation, destructive cleanup, Git push/history rewrite,
  release, deployment, credentials, and external-system mutation.

This revision does not treat the corrected foundation as immediate
source-mutation authority. WI-5270 is the named worker-context predecessor,
and its current version-004 `VERIFIED` artifact is untracked rather than
focused-finalized. The WI-5270 candidate also owns an untracked facade module,
an untracked focused test, and a dirty hunk in the shared
`groundtruth-kb/src/groundtruth_kb/cli.py` target. WI-5464 owns correction and
re-evaluation of that state. WI-5271 implementation must fail closed until
WI-5270 is independently reverified, commit-covered, and its exact shared-CLI
baseline is available for adoption.

This revision requests review of the corrected plan only. It performs no
source, test, dispatcher configuration/runtime, TAFE, harness-state, or Git
mutation.

## Findings Addressed

### F1 - Three governing foundation records were absent

Resolved. Fresh governed reads return version 2, `specified`, one assertion
each for:

- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`;
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`;
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`.

Fresh `gt assert --spec` execution passes for all three and for
`DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`.

### F2 - The foundation-first owner decision was omitted

Resolved. This revision explicitly carries
`DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` in Prior
Deliberations and derives the operation-time predecessor checks below from it.

### F3 - Foundation state needed a fresh filing-time check

Resolved for proposal review. The latest exact foundation artifact is v034
`VERIFIED`, its carrier commit is
`6262862c8852d4d94530a4074a3047f921e7164e`, the required records are version
2, and their assertions pass. The implementation-start path must repeat those
checks and stop on any drift.

### Corrected version-003 predecessor requirement

Not yet satisfied, and therefore retained as a hard implementation barrier.
WI-5270 has a candidate `VERIFIED` v004 but no carrier commit. Its exact
candidate paths remain dirty/untracked, including the shared CLI target.
Neither that artifact nor the shared hunk may be treated as terminal
predecessor evidence until WI-5464 correction, independent verification, and
focused finalization complete.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved version-2 foundation supplies canonical worker-safe packet,
ordinary-worker boundary, worker-context facade, and foundation-first
requirements. This proposal implements a read-only mediated view derived from
those records; it creates no new authority and requests no exception.

## Proposed Scope

1. Add a governed, read-only mediated bridge packet view for the worker's
   assigned bridge thread or work item.
2. Return the exact assigned proposal, verdict, implementation report,
   verification, governing specification links, project authorization,
   work-item metadata, target paths, role-authorized next actions, blockers,
   provenance, citations, and integrity evidence needed for ordinary work.
3. Exclude raw queue mechanics, raw bridge paths as worker dependencies,
   bridge-state internals, dispatcher configuration/runtime, TAFE internals,
   harness registry state, ranking/scheduling data, leases, process details,
   other-harness state, and unrelated queue content.
4. Fail to a safe blocker when required assigned content is unavailable; do
   not instruct an ordinary worker to inspect protected internals.
5. Compose with the terminal WI-5270 worker-context facade and preserve the
   existing operator-authorized `gt bridge show` and `gt bridge threads`
   surfaces without creating a competing ordinary-worker CLI contract.
6. Keep hard raw-surface enforcement in its separately governed later slice.
   This WI supplies the safe replacement path and does not mutate dispatcher
   configuration/runtime or TAFE/harness internals.

## Hard Implementation-Start Gates

1. Foundation v034 remains `VERIFIED` and commit
   `6262862c8852d4d94530a4074a3047f921e7164e` remains its durable carrier.
2. The five version-2 foundation records remain present with approved content
   and passing assertions, including the four records cited by this proposal.
3. WI-5270 reaches a fresh independent terminal `VERIFIED` state after WI-5464
   re-evaluation, and its exact focused finalization commit covers the facade,
   focused test, shared CLI hunk, and corrected terminal bridge evidence.
4. The shared CLI baseline produced by WI-5270 is clean and adopted explicitly;
   no whole-file overwrite or foreign-hunk absorption is permitted.
5. The active WI-5271 PAUTH remains current and unchanged in scope.
6. All three WI-5271 targets are clean and unclaimed, or every differing byte
   has a separately terminal, focused-finalized owner whose exact resulting
   hash is adopted by fresh independent review.
7. A fresh WI-5271 `GO`, exact same-session `go_implementation` claim,
   schema-v3 implementation-start packet, and per-target operation-time
   authorization all cover the same project, work item, thread, targets,
   mutation classes, and session.
8. Any dispatcher configuration/runtime, TAFE, harness registry/identity,
   credential, release, deployment, Git push/history rewrite, destructive
   cleanup, or unrelated worktree request fails closed.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`

## Owner Decisions / Input

No new owner decision is required. This revision carries forward the owner's
foundation-first, safe-packet, raw-bridge protection, and ordinary/ops/build
boundary decisions. The dispatcher-configuration troubleshooter hold remains
binding, and this proposal requests no configuration or runtime mutation.

## Specification-Derived Verification

| Requirement | Executable verification | Required result |
| --- | --- | --- |
| Worker-safe packet completeness | Focused read-command tests with proposal, verdict, report, verification, metadata, blockers, citations, and hashes | Full assigned content and required provenance are present. |
| Ordinary-worker black-box boundary | Negative tests for raw paths, raw state, config/runtime, TAFE/harness/ranking/lease/process fields, unrelated threads, and verbose/debug leakage | Protected internals and unrelated state are absent. |
| Safe incomplete-packet behavior | Missing/corrupt assignment and unknown slug/work-item tests | Safe blocker or governed mediated-fetch result; no raw-file instruction or traceback leakage. |
| Worker-context facade composition | Integration tests against the focused-finalized WI-5270 facade and shared CLI baseline | One coherent ordinary-worker route; no competing CLI behavior or foreign-hunk overwrite. |
| Read-only bridge authority | Before/after bridge and dispatcher-safe state hashes plus traversal/mutation negative tests | No bridge, TAFE, dispatcher, harness, or filesystem mutation. |
| Operator non-impairment | Existing `gt bridge show` and `gt bridge threads` focused regression tests | Authorized operator read surfaces remain compatible. |
| Foundation and operation-time authority | Fresh foundation/commit/spec/assertion, PAUTH, claim, schema-v3 start, exact target, and per-target authorization checks | Every authority layer agrees; drift blocks before mutation. |
| Cross-harness parity | Supported harness projections consume the same mediated packet schema and exclusion matrix | No provider-specific field leak or authority bypass. |
| Worktree hygiene | Exact target status/hashes before and after plus target-only diff/whitespace checks | Only WI-5271-owned hunks change. |
| Mandatory bridge gates | Candidate/live applicability and clause preflights | No missing specs, errors, or blocking gaps. |

Required focused commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_read_commands.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_read_commands.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_read_commands.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_read_commands.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_read_commands.py
```

## Acceptance Criteria

1. An ordinary worker can retrieve every assigned bridge-content class and its
   governing metadata without direct raw bridge or internal-state access.
2. Protected internals, unrelated work, path traversal, and hidden debug
   leakage are denied by executable tests.
3. Missing assigned content produces a safe blocker or governed mediated
   fetch, never a raw-file dependency.
4. The view composes with focused-finalized WI-5270 and preserves existing
   authorized operator read commands.
5. Foundation, predecessor, target ownership, and operation-time drift fail
   closed before mutation.
6. No dispatcher configuration/runtime, TAFE, harness registry/identity,
   credential, deployment, release, Git push/history, destructive cleanup, or
   unrelated worktree mutation occurs.

## Scope Changes

- Replaces absent foundation citations with live version-2 MemBase authority.
- Adds the omitted foundation-first owner decision and committed foundation
  evidence.
- Adds explicit WI-5270/WI-5464 predecessor and shared-target finalization
  barriers.
- Preserves the original three source/test targets and mediated-view behavior.

## Pre-Filing Preflight Subsection

Candidate applicability preflight:

- Command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5271-mediated-bridge-packet-views --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5271-mediated-bridge-packet-views-005.md --json`
- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- packet hash:
  `sha256:95913d0fb6886db20be1949583277478cbb123f3597679840acd7c01a1308ae8`

Mandatory clause preflight:

- Command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5271-mediated-bridge-packet-views --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5271-mediated-bridge-packet-views-005.md`
- clauses evaluated: 5
- `must_apply: 3`
- `may_apply: 2`
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0
- result: PASS (exit 0)

## Risk And Rollback

The main risks are leaking protected bridge/dispatcher internals, creating a
second worker CLI contract, and overwriting the shared CLI hunk owned by
WI-5270. Full positive/negative packet tests, explicit facade composition,
exact operation-time authorization, and the predecessor/clean-target gates
address those risks.

Rollback is a focused revert of WI-5271-owned hunks only. No whole-file
restore, foreign-hunk absorption, database replacement, bridge-history
rewrite, dispatcher/configuration rollback, or unrelated cleanup is
authorized.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_bridge_read_commands.py`

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

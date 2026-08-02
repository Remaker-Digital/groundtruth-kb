NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled and untouched
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5627-live-daemon-order-strict-recovery
Version: 001
Supersedes strict-invalid chain: bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md through bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-008.md
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5627

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

# Strict-Recovery Implementation Proposal — Restore the Pending WI-5627 Live-Daemon Order Repair

## Revision Claim

Version 008 correctly rejects the version-007 carrier-only `NO-ACTION` as a
closure mechanism. The current typed publication authority also proves the old
thread cannot accept a lawful successor: version 003 has no canonical
`Responds to:` link to version 002, so strict lifecycle resolution fails with
`WRONG_RESPONDS_TO_LINK`. Historical bridge files remain immutable.

This fresh strict-recovery proposal supersedes the malformed carrier and
restores the exact bounded repair approved in old version 006 against the
current clean target bytes. It does not claim that the old GO remains live, and
it requests a fresh independent Loyal Opposition review before any protected
source or test modification.

The defect is still present at current HEAD. The daemon acquires document
leases, verdict claims, and work-intent claims over `selected`, then executes:

```python
spawn_items = list(reversed(selected))
```

That reversal changes the provider-visible order after authority was acquired.
The correction remains one source-line behavior change plus a two-document
regression in the existing daemon test module:

```text
spawn_items == selected_documents == document_lease_slugs == verdict_claim_slugs
```

The first slug in that shared order must remain the primary bridge id in the
worker environment and launch/result telemetry.

No source or test mutation is authorized by this revision alone. Prime Builder
must obtain fresh `GO`, hold the exact work-intent claim, and pass the schema-v3
implementation-start gate for both declared targets before editing them.

## Current-State Evidence

- Both target paths are tracked and Git-clean.
- Current SHA-256 values:
  - `scripts/gtkb_dispatcher_daemon.py`: `e9a9dfb96d94d6623ace9110a861aa901dffc38864187c5d10b21bd3bfd2de1c`
  - `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`: `f68b9a8bee0a8ba72073fe39ae545cde1b8c89126bfde33b1f4db6c9fdb93c30`
- `scripts/gtkb_dispatcher_daemon.py:1467` still contains
  `spawn_items = list(reversed(selected))`; Git blame attributes the unchanged
  line to commit `20ebc30161`.
- `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q
  --tb=short -k wi5627 --timeout=600` passed `6` tests with `62` deselected in
  `0.72s`.
- Ruff format check passes for both targets; `git diff --check` passes.
- Full Ruff check has one pre-existing `I001` import-order finding at
  `scripts/gtkb_dispatcher_daemon.py:33`. It is unrelated to the order defect,
  predates this revision, and is explicitly excluded from the WI-5627 patch.

## Scope

The exact implementation scope is:

1. Replace only the reverse-order spawn preparation with an order-preserving
   copy of `selected`.
2. Add one focused two-document regression that records the exact sequence at
   selection, lease acquisition, verdict-claim acquisition, spawn, primary-id
   environment, and telemetry/result boundaries.
3. Assert ordered-list equality and first-item identity. A sorted or set-based
   comparison is insufficient.
4. Produce a new append-only canonical hunk patch under `bridge/hunks/` plus a
   self-contained preimage/postimage hash ledger in the implementation report.

Out of scope:

- dispatcher or TAFE configuration, activation, routing, ranking, eligibility,
  allowances, role maps, identities, provider selection, runtime state, lease
  files, live workers, or process control;
- the pre-existing Ruff import-order finding or any other opportunistic cleanup;
- MemBase, database, credential, deployment, release, push, history rewrite,
  destructive cleanup, or unrelated dirty-byte mutation; and
- reliance on `.gtkb-state`, harness scratch, or temporary reconstruction paths
  as canonical implementation evidence.

This proposal performs no KB or MemBase mutation, does not create or update any
specification, work item, test record, deliberation, project, authorization, or
other `groundtruth.db` row, and therefore does not include `groundtruth.db` in
`target_paths`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `TEST-11672`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-HARNESS-ISOLATION-001`

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizes bounded reliability
  implementation after the normal proposal, independent GO, exact claim,
  implementation-start, test, and independent verification gates.
- `DELIB-202666762` established the pre-launch LO verdict-claim lifecycle that
  WI-5627 applies to the live daemon.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires the canonical
  patch and hash-ledger evidence used by this revision.
- Old versions 005 and 006 contain the prior corrected proposal and independent
  GO; versions 007 and 008 establish that carrier `NO-ACTION` did not close it.
  The old chain is evidence only because its version-003 predecessor link is
  strict-invalid; this fresh thread is the sole requested execution path.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner decision is required. The active
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is version 1, status `active`,
has no expiry, covers active project members including WI-5627, and is derived
from `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

The owner's dispatcher/TAFE configuration hold remains binding. This proposal
does not authorize enabling, reconfiguring, or otherwise mutating either
runtime.

## Requirement Sufficiency

Existing requirements are sufficient. The centralized-dispatch architecture
already requires one authoritative selected batch, and TEST-11672 already
covers pre-launch claim lifecycle behavior. The missing regression makes the
ordered-sequence invariant executable without creating a new requirement.

## Specification-Derived Verification Plan

| Requirement | Command or evidence | Required result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Two-document fake-spawn regression | Exact selection order reaches spawn unchanged; first selected slug remains primary/correlation id. |
| `TEST-11672` | Ordered capture of selection, document leases, verdict claims, spawn items, environment, and telemetry/result fields | All ordered lists are equal; no set/sort normalization masks reversal. |
| Existing WI-5627 claim lifecycle | Focused `-k wi5627` suite and full daemon module with `--timeout=600` | Peer contention, owned-claim cleanup, incomplete exit, and authority-before-spawn remain passing. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh GO, exact claim, schema-v3 implementation-start, applicability and clause preflights | Every operation-time gate passes for exactly two targets. |
| `GOV-WORK-TREE-HYGIENE-001`; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Canonical hunk patch, pre/post hashes, forward/reverse applicability, `git diff --check` | Only the reviewed WI-5627 source/test delta is attributable and reproducible. |
| Python mechanical quality | Ruff format; Ruff check with the pre-existing source `I001` explicitly reported rather than silently absorbed; Python compilation | No new lint/format/compile defect; unrelated import cleanup remains excluded. |

Planned verification after fresh GO and implementation-start authorization:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short -k wi5627 --timeout=600
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short --timeout=600
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict -q --tb=short --timeout=600
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
git diff --check -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

## Risks and Rollback

The main behavioral risk is changing bundle ordering beyond the narrow spawn
reversal. The ordered multi-boundary regression constrains that risk. The main
repository risk is absorbing unrelated target-file evolution; clean preimages,
an exact canonical patch, hash reconstruction, and hunk-only attribution bound
that risk.

Rollback requires separate authority and reverses only the eventual v009
WI-5627 patch, followed by the same focused/full tests and mechanical gates.
No dispatcher or TAFE configuration rollback is relevant because neither is in
scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

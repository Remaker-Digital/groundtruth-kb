REVISED
::init gtkb lo
::open build

# WI-5627 Revision: Canonical Hunk Evidence and Live-Daemon Batch-Order Parity

bridge_kind: prime_proposal
Document: gtkb-wi5627-live-daemon-lo-verdict-claim-parity
Version: 005
Responds to: bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-004.md
Author: Prime Builder (Codex)
Date: 2026-07-19 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5627

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

Version 004 correctly rejected the version 003 forward-applicability evidence:
a canonical bridge report cannot depend on an ephemeral, noncanonical
reconstruction location. The next implementation report will use a new,
append-only canonical hunk patch and will carry the exact reconstruction inputs,
hashes, results, and procedure in the numbered bridge chain. It will not cite a
temporary path or any harness-local scratch surface.

This revision also incorporates a newly isolated WI-5627 defect in the same two
approved targets. The production daemon acquires document leases and LO verdict
claims in canonical `selected` order, but immediately before provider spawn it
reverses that list. The spawned worker therefore receives a different order
from the order recorded by the document leases and verdict claims. Runtime then
uses the reversed first item as the primary bridge id, worker environment
primary id, and telemetry correlation id. This mismatch explains observed
multi-document worker bundles whose primary/correlation metadata did not agree
with their governed lease and claim metadata.

The correction will preserve one canonical order throughout the launch
lifecycle:

```text
spawn_items == selected_documents == document_lease_slugs == verdict_claim_slugs
```

The first slug in that common sequence must also equal `primary_bridge_id`,
`GTKB_DISPATCH_PRIMARY_BRIDGE_ID`, and every launch/result telemetry bridge id
derived from the primary item.

No implementation is authorized by this revision alone. Both protected targets
remain untouched until a fresh independent GO, an exact implementation claim,
and a successful schema-v3 implementation-start authorization are live.

## Findings Addressed

### F1 - Canonical forward-applicability evidence

Accepted. The historical version 003 hunk patch remains immutable evidence for
that historical report. The revised implementation will create a distinct
versioned canonical hunk patch under `bridge/hunks/` after fresh GO. The next
report will contain:

- pre-implementation and post-implementation SHA-256 values for each exact
  target;
- canonical patch path, SHA-256, Git blob id, byte size, and numstat;
- an exact two-path header and marker scan;
- reverse applicability against the post-implementation target bytes;
- per-path reconstructed-preimage SHA-256 values that match the recorded
  pre-implementation hashes;
- forward applicability against those reconstructed preimages;
- post-forward SHA-256 values that match the recorded post-implementation
  hashes; and
- the complete deterministic reconstruction procedure, with only canonical
  patch/source inputs and the resulting hashes cited in the bridge report.

The reconstruction may execute in an ephemeral process, but no ephemeral path,
scratch item, or harness-local state will be cited or required as canonical
evidence. The canonical patch plus the report's exact hash ledger will be
self-contained and independently reproducible from the recorded target bytes.

### F2 - Spawn order diverges from governed selection, lease, and claim order

Accepted as an in-scope WI-5627 defect. The existing live-daemon implementation
creates `spawn_items` by reversing `selected`. The correction will remove that
reversal and preserve the selected batch order through provider launch,
primary-id derivation, worker environment, result recording, telemetry,
document leases, and verdict claims.

`TEST-11672` will gain a two-document regression that captures
`kwargs["items"]` at the fake spawn boundary and asserts the complete equality
contract. The regression will also assert that the first selected slug is the
primary bridge id exposed through the worker environment and telemetry/result
fields. A second assertion will ensure the test fails against the current
reversed behavior rather than merely comparing sorted sets.

## Scope

The implementation scope remains exactly:

- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

The runtime correction is limited to preserving canonical selected order at the
spawn boundary and keeping every derived primary/correlation field aligned.
The test correction is limited to the WI-5627 two-document ordering regression
and any narrowly necessary fixture capture.

Out of scope:

- dispatcher configuration, runtime JSON, lease files, routing, ranking,
  eligibility, allowances, roles, identities, provider configuration, or
  process control;
- direct harness or provider contact;
- MemBase or `groundtruth.db` mutation;
- credentials, deployment, release, push, or destructive cleanup;
- adoption of unrelated dirty source/test bytes; and
- whole-file staging or whole-file finalization of either commingled target.

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

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizes this bounded
  reliability repair while preserving proposal, independent review, exact
  claim, implementation-start, independent verification, and focused-commit
  gates.
- `DELIB-202666762` established the dispatcher-owned pre-launch LO
  verdict-claim lifecycle that WI-5627 applies to the production daemon path.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires canonical
  bridge evidence to avoid noncanonical scratch and session-state dependencies.
  This revision adopts that requirement explicitly.

The complete numbered WI-5627 chain and the linked MemBase work item and test
were reviewed. No owner decision or architecture record rejects preserving one
canonical document order across selection, leases, claims, spawn, environment,
and telemetry.

## Owner Decisions / Input

No new owner decision is required. The active fleet goal directs correction of
substantive dispatcher-produced defects through a work item, linked test,
project authorization, bridge GO, implementation, testing, independent
verification, and focused commit. The existing
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` authorizes proposal and,
following fresh GO and operation-time gates, bounded implementation of the two
declared targets.

The owner's dispatcher-configuration hold remains binding. This revision
neither requests nor authorizes any dispatcher configuration or runtime-state
mutation.

## Requirement Sufficiency

Existing requirements are sufficient. The central dispatcher specification and
architecture require the production daemon to preserve the authority and
correlation of its selected document batch. `TEST-11672` already requires exact
selected-batch claim acquisition before provider spawn; the two-document
ordering regression makes the previously implicit sequence invariant explicit.
No new product or governance requirement is needed.

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Exercise a two-document live-daemon selection through a fake spawn and inspect `kwargs["items"]`, result fields, environment, and telemetry capture. | Selection order reaches spawn unchanged; the first selected item remains the primary and correlation id. |
| `TEST-11672`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Assert `spawn_items == selected_documents == document_lease_slugs == verdict_claim_slugs` with exact ordered lists, not sets. | The regression fails against the current reversal and passes only when all four sequences are identical. |
| Existing WI-5627 claim-lifecycle acceptance | Re-run all focused WI-5627 tests, the complete daemon test module, and the WI-5400 incomplete-exit regression. | Authority-before-claim-before-spawn, neutral peer contention, owned-claim cleanup, and incomplete-exit behavior remain intact. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Require fresh GO, exact claim, schema-v3 start packet, target-path preflight, applicability preflight, clause preflight, and independent terminal verdict. | Every operation-time gate passes for exactly two protected targets. |
| `GOV-WORK-TREE-HYGIENE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Produce a new versioned canonical hunk patch and execute the self-contained hash-ledger reconstruction procedure described above. | Forward and reverse applicability pass without a canonical dependency on ephemeral state; foreign hunks remain excluded. |
| Python mechanical gates | Run Ruff lint and format check, Python compilation, and `git diff --check` for both targets. | All commands exit zero. |

Planned commands after fresh GO and implementation-start authorization:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short -k wi5627
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
git diff --check -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

## Pre-Filing Preflight

Candidate-content applicability and mandatory clause preflights will run
against these exact completed version 005 bytes before governed filing. The
filing helper must refuse missing required or advisory specifications,
blocking errors, clause gaps, stale latest status, or an existing version 005
path.

## Risk / Rollback

The main behavioral risk is changing bundle ordering beyond the narrow
live-daemon reversal. The regression therefore binds every governed sequence
and primary/correlation field to the original selected order. The main
worktree risk is adopting unrelated bytes from the heavily commingled target
files. A new append-only canonical hunk patch, exact hash ledger, forward and
reverse reconstruction checks, and hunk-only finalization are mandatory.

Rollback requires separate authority and reverses only the eventual revised
WI-5627 hunk patch, then reruns the focused and complete daemon tests plus all
mechanical gates. No dispatcher configuration rollback is required because
configuration is outside scope.

## Recommended Commit Type

`fix(dispatch):` preserve canonical selected-document order through the live
daemon claim and spawn lifecycle.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

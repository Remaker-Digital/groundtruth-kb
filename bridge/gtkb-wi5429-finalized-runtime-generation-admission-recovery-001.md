NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; strict-lifecycle replacement proposal
author_metadata_source: explicit_interactive_session_metadata

# WI-5429 — Finalized Runtime Generation Admission Strict Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5429-finalized-runtime-generation-admission-recovery
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718
Project Authorization Version: 1
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5429
target_paths: ["scripts/dispatcher_generation_admission.py", "scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_generation_admission.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

No KB mutation: this proposal does not mutate MemBase or `groundtruth.db`.
It authorizes no protected edit until independent `GO`, an exact claim, a
schema-v3 implementation-start packet, fresh operation-time PAUTH validation,
and exact target-preimage checks all pass.

## First-Line Role Eligibility Check

PASS. Harness A is active Prime Builder and may file this substantive `NEW`
replacement proposal. Prime does not author `GO`, `NO-GO`, or `VERIFIED`.

## Recovery Claim

This recovery proposal accepts the implementation and verification defects in version
008, corrects its stale approval conclusion, and proposes the smallest repair
that makes the already-committed five-path WI-5429 implementation reviewable.

The current implementation is not treated as verified. All five paths are
tracked and clean, but the generation materializer contains an incomplete
merge-shaped body: state variables are undefined, the manifest loop is
duplicated, and the function recomputes generation identity through a second
inline path after already calling the canonical helper. The focused admission
suite consequently fails before generation materialization completes.

## Replacement Relation And Historical Quarantine

This strict-valid thread supersedes the original
`gtkb-wi5429-finalized-runtime-generation-admission` versions 001–008 for all
future implementation and review authority. The original chain remains
append-only evidence and is not rewritten. Its version 004 declares decorated
metadata `Version: 004 (corrected verdict; responds to NO-ACTION 003)`, so the
typed publication writer rejects any candidate successor with
`WRONG_BRIDGE_VERSION_METADATA`. A direct v009 attempt created no file, and its
claim was released. This fresh thread preserves the current v008 NO-GO as
substantive review evidence while restoring a strict publication path.

## Requirement Sufficiency

Existing requirements sufficient. WI-5429, the active exact PAUTH, the
version-005 design, the version-008 reproduced failures, and the governing
specifications below define the intended admission boundary and the bounded
repair completely. No new or revised formal requirement is needed before
implementation; independent review and every implementation-start gate remain
mandatory.

## Project Authorization Reconciliation

`WI-5429` is an active member of
`PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`.
The project is active at version 15. Exact PAUTH
`PAUTH-DISPATCHER-BLACK-BOX-WI5429-FINALIZED-GENERATION-ADMISSION-V2-20260718`
is active, is owner-backed by
`DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST`, explicitly includes
WI-5429, and permits bridge, metadata, source, test, and governance-evidence
mutation subject to the downstream gates.

The work item's legacy `approval_state=unapproved` field does not override its
active project membership and active exact project authorization. This applies
the owner's current project-level inheritance direction in
`DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`. No additional
per-WI owner approval is requested or inferred.

## Exact Current Evidence

All five approved targets are tracked and clean at the following SHA-256
identities:

| Path | SHA-256 | Current role |
| --- | --- | --- |
| `scripts/dispatcher_generation_admission.py` | `a3b9efb3032534f43c4759f64cb22b685e19d3944b979a343e00ce4d55524415` | generation validation/materialization/admission implementation |
| `scripts/ensure_dispatcher_daemon.py` | `5f172ce9a0917532500632e91f37625975d5c4c140524428a27f3aede4b9c317` | supervisor integration |
| `scripts/gtkb_dispatcher_daemon.py` | `e9a9dfb96d94d6623ace9110a861aa901dffc38864187c5d10b21bd3bfd2de1c` | daemon integration |
| `platform_tests/scripts/test_dispatcher_generation_admission.py` | `71a2fae7a76939ab3c33cb370ef860535f8c81ac8b92215a8b19ada0bd4fa0e7` | focused admission coverage |
| `platform_tests/scripts/test_dispatcher_daemon_supervision.py` | `8b50f98738cb396ef2a012afa20d7070c512cd923935c834bc9a0644dfca4975` | focused supervisor coverage |

Fresh focused verification collected 51 tests: **40 passed, 11 failed** in
24.89 seconds. Every failure reaches
`materialize_generation()` and raises either undefined `errors` at line 419 or
undefined `digest` at line 447. Ruff reports 22 findings: the production
undefined-name defects plus test-file unused imports/locals and formatting
drift. Ruff format reports the production module and focused admission test
would be reformatted.

## Proposed Implementation

1. In `materialize_generation()`, initialize one local error accumulator before
   generation computation and return deterministic failure evidence when the
   canonical generation hash cannot be computed.
2. Retain `_compute_generation_hash()` as the single generation-identity
   implementation. Remove the duplicated manifest loop and the incomplete
   second inline digest path; build each manifest entry exactly once.
3. Preserve materialization from committed Git objects, in-root destination
   enforcement, per-file post-write hash verification, current-pointer
   atomics, dry-run behavior, idempotent same-generation behavior, and
   fail-closed handling for missing paths.
4. Remove only genuinely unused focused-test imports and assignments, then
   format the two touched Python files. Do not weaken assertions or exclude
   failing tests.
5. Treat the other three approved paths as reconciliation and regression
   evidence. Do not rewrite byte-identical files merely because they are in the
   authorized five-path scope.

## Non-Impairment And Runtime Boundary

- Do not start, stop, restart, reconfigure, reroute, or hand off a dispatcher,
  daemon, worker, or harness.
- Do not mutate TAFE, dispatcher configuration, runtime state, leases, claims,
  eligibility, generations under runtime state, or a current-generation
  pointer outside isolated tests.
- Do not disable a functional dispatch lane or make dirty working-tree bytes
  executable authority.
- TAFE remains deliberately disabled for repairs.
- Do not touch credentials, external systems, Git history/index/commit/push,
  deployment, release, or unrelated dirty files.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5429, DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST, and the exact active PAUTH",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001",
  "primary_route": "Admit one deterministic generation from committed Git objects through the established admission module; unattended recovery consumes only the governed current-generation pointer.",
  "before_behavior": "The committed materializer raises undefined-name errors, duplicates manifest entries, and cannot complete generation admission.",
  "after_behavior": "The canonical hash helper defines generation identity once, each committed object appears once in the manifest, materialization verifies bytes, and the focused admission and supervision suites pass.",
  "self_descriptive_naming": "The existing dispatcher_generation_admission module, generation identity, manifest, and current-generation terminology remain canonical.",
  "obsolete_guidance_disposition": "Version 007's stale no-action premise and version 008's per-WI approval conclusion remain append-only history but are not implementation authority.",
  "history_preservation": "The five committed target preimages, numbered bridge chain, project authorization, and deliberations remain preserved; no historical file is rewritten.",
  "baseline": {
    "production_sha256": "a3b9efb3032534f43c4759f64cb22b685e19d3944b979a343e00ce4d55524415",
    "focused_test_sha256": "71a2fae7a76939ab3c33cb370ef860535f8c81ac8b92215a8b19ada0bd4fa0e7",
    "focused_pytest": "40 passed, 11 failed",
    "ruff_findings": 22,
    "pauth_version": 1
  },
  "expected_result": {
    "identity": "One canonical helper-derived generation hash",
    "manifest": "One entry per declared runtime path",
    "verification": "51 focused tests plus Ruff check and format-check pass",
    "runtime": "No live dispatcher, TAFE, pointer, routing, or process mutation during repair"
  },
  "hard_invariants": [
    "Never execute arbitrary dirty working-tree runtime bytes.",
    "Never disable unattended hidden recovery or a functional dispatch lane.",
    "Never mutate live dispatcher configuration/runtime state or TAFE in this repair.",
    "Never weaken focused assertions or omit a failing admission case.",
    "Never mutate outside the independently GO-approved exact cohort."
  ],
  "rollback": {
    "instructions": "Restore only the exact reviewed source/test preimages before terminal finalization; preserve bridge and authorization history.",
    "test": "Rerun the focused admission/supervision suites, Ruff gates, exact hashes, scoped Git status, and runtime/TAFE non-mutation checks."
  },
  "fail_closed_conditions": [
    "Missing fresh GO, exact claim, schema-v3 start packet, or allowed operation-time PAUTH result.",
    "Any target preimage or ownership drift before implementation.",
    "Any focused test or Ruff gate remains red.",
    "Any live runtime, pointer, process, dispatcher configuration, or TAFE mutation is required.",
    "Any foreign dirty hunk overlaps an approved target."
  ],
  "essential_context_preservation": "The implementation report must retain the five-path committed provenance, exact before/after hashes, the project-level approval basis, all executed results, and the independent verification boundary."
}
```

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-CODE-QUALITY-BASELINE-001`

## Prior Deliberations

- `DELIB-20260718-DISPATCHER-HOLD-NARROW-WI5429-FIRST` — owner-backed bounded
  WI-5429 project authorization and sequence.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-level
  implementation approval controls; child work items do not require duplicate
  per-WI approval.
- `DELIB-202667066` — earlier review evidence for the original authorization
  and sequencing defects corrected by versions 005/006.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-005.md` — exact
  five-path revised proposal and spec-derived plan.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-006.md` —
  independent GO for that bounded implementation.
- `bridge/gtkb-wi5429-finalized-runtime-generation-admission-008.md` — current
  NO-GO and reproduced defect evidence.

## Specification-Derived Verification Plan

| Requirement | Command/evidence | Acceptance |
| --- | --- | --- |
| Committed-object admission and deterministic generation identity | `python -m pytest platform_tests/scripts/test_dispatcher_generation_admission.py -q --tb=short` | All focused admission tests pass, including missing path, deterministic/different hashes, dry-run, idempotence, in-root, and unfinalized-current detection. |
| Supervisor non-impairment | `python -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short` | All supervisor tests pass without starting or mutating a live daemon. |
| Combined contract | Run both focused files together | 51/51 pass with no timeout. |
| Code-quality baseline | `ruff check scripts/dispatcher_generation_admission.py platform_tests/scripts/test_dispatcher_generation_admission.py` and `ruff format --check` on both | Exit 0; no ignored or excluded findings. |
| Exact scope and foreign-byte preservation | Pre/post SHA-256 plus scoped Git status on all five paths | Only reviewed repair hunks appear; the three integration/evidence paths remain byte-identical unless separately justified before start. |
| Runtime/configuration non-mutation | Process/config/runtime-state and TAFE before/after observation | No live process, runtime pointer, dispatcher configuration, TAFE, routing, lease, or eligibility change. |

The implementation report must include exact commands, observed results,
post-edit hashes, a scoped diff, and explicit disposition of all five paths.
Independent Loyal Opposition verification remains mandatory.

## Timer, Concurrency, And SoT-Latency Review

No evidence in this focused reproduction establishes a too-short timer: the
51-test command completed in 24.89 seconds without a per-test timeout. No new
timer work item is created; broader timeout and concurrency centralization
remain with the existing WI-5804/WI-5806/WI-5807 and approved timer-program
carriers. No new concurrent execution failure was observed, so this recovery
does not duplicate the existing concurrency Advisory Reports. Implementation
must introduce no hard-coded cadence, retry, throttle, threshold, fan-out, or
concurrency value.

## Owner Decisions / Input

No new owner decision is required. The exact active project membership, exact
active PAUTH, its owner decision, and the owner's project-level inheritance
direction authorize the proposal cycle. This proposal does not activate the
implementation before independent GO and the remaining mandatory start gates.

## Pre-Filing Preflight

- Candidate applicability preflight: exit `0`; no missing required/advisory
  specifications, no blocking errors, and proposal-time PAUTH evaluation
  allowed both packet creation and implementation start for the exact cohort.
- Mandatory ADR/DCL clause preflight: exit `0`; zero evidence gaps and zero
  blocking gaps.
- Strict proposal-pattern lint: zero findings.
- The governed proposal helper must recheck role, claim, compliance, and
  numbered-file currentness against the final content.

## Rollback

The proposed code repair is reversible by restoring the exact five preimages
listed above. The bridge proposal itself is append-only review evidence. No
runtime-state rollback is expected because implementation and verification are
offline and must not mutate the live dispatcher or TAFE.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

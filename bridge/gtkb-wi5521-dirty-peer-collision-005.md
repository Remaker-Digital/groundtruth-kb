REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; integrated semantic-and-liveness revision
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5521-dirty-peer-collision
Version: 005
Responds to: bridge/gtkb-wi5521-dirty-peer-collision-004.md
Date: 2026-08-01 UTC

# WI-5521 — Integrated Dirty-Peer Collision and Peer-Scan Liveness Revision

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-V2-20260801
Project Authorization Version: 1
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5521
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

No source or test implementation has started. This revision authorizes no
protected edit until it receives independent `GO`, every predecessor below is
terminal, both exact targets and the canonical lifecycle dependency are clean,
an exact work-intent claim exists, and schema-v3 implementation-start plus
fresh operation-time PAUTH validation pass.

## First-Line Role Eligibility Check

PASS. Harness A is the active Prime Builder. Prime may file this `REVISED`
proposal and may not author `GO`, `NO-GO`, or `VERIFIED`.

## Revision Claim

This revision accepts both findings in version 004. Version 003 was not a valid
NO-ACTION correction and does not close the work. The revised design integrates
the accepted peer-scan liveness advisory into WI-5521 rather than creating a
duplicate carrier, while preserving the original structured-report and
terminal-but-uncommitted collision semantics.

The implementation remains intentionally dormant. This filing restores a
truthful review path; it does not revive version 002's narrower GO and does not
start source work.

## Requirement Sufficiency

Existing requirements are sufficient for proposal review. WI-5521 version 3,
the accepted advisory chain, the active project and PAUTH, and the governing
specifications below define the semantic, liveness, concurrency, and
verification boundary. WI-5806 remains the required configuration carrier for
the bounded deadline; this WI must consume that canonical value and must not
invent a local literal or independent environment read.

No new formal requirement is required. A later implementation is blocked until
WI-5382, WI-5454, WI-5806, and the foreign-owned lifecycle-resolver work are
terminal and released.

## Project Authorization Reconciliation

WI-5521 is an active member of the active black-box hardening project. Exact
PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-V2-20260801` is
active, owner-backed by
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`, permits bridge,
metadata, governance-evidence, source, and test work, and names the two exact
targets carried by this revision.

The work item's legacy `approval_state=unapproved` field is not a separate
implementation veto: under the owner's project-level approval direction, work
items inherit their parent project's approval. This revision does not expand
the two-file PAUTH cohort. It uses the existing lifecycle resolver as a
read-only semantic dependency and does not authorize mutation of
`scripts/bridge_lifecycle_resolver.py`.

## Exact Current Evidence

- In-root placement: the live revision will be filed under `E:/GT-KB/bridge`,
  both implementation targets are under the `E:/GT-KB` project root, and no
  generated artifact or live dependency may escape that root.
- `scripts/implementation_authorization.py` is tracked and clean at SHA-256
  `bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891`.
- `platform_tests/scripts/test_implementation_authorization.py` is tracked and
  clean at SHA-256
  `d59aca8a1c31fc0a3b3cbc6bebc8bc542735feda79bcbeb0eeb19ccff337e98f`.
- The focused current collision baseline is 2 passed, 161 deselected in 1.69
  seconds. Ruff check and Ruff format-check both pass for the exact cohort.
- The existing guard enumerates every named packet and calls the lifecycle
  resolver once per peer. Each resolver call enumerates the entire bridge
  directory, reproducing the advisory's packets-times-bridge-files shape.
- The existing report parser recognizes only `Files Changed` and `Implemented
  Paths`; terminal peers are excluded; unreadable peer chains fail soft.
- `scripts/bridge_lifecycle_resolver.py` is currently foreign-dirty and is not
  part of this authorization. Implementation must wait for that owner to
  terminalize and release it; WI-5521 must not absorb those hunks.

## Findings Addressed

### F1 — NO-ACTION was used as dormant-state closure

Accepted. Version 003 remains append-only history but is not treated as
closure. This version is a complete REVISED proposal, carries forward the
exact implementation boundary and verification plan, and explicitly records
that implementation has not started.

### F2 — The live work-item contract exceeds the old GO

Accepted. This design integrates one ephemeral per-evaluation bridge-history
index, stable snapshot detection, fail-closed malformed/duplicate/unreadable
handling, phase/cardinality diagnostics, a centrally configured deadline,
near-additive scale evidence, semantic equivalence, and concurrent
claim/release tests. A fresh independent GO is required.

## Proposed Implementation

1. At the start of one peer-collision evaluation, enumerate `bridge/` exactly
   once and construct an immutable in-memory index keyed by exact bridge id and
   version. The index records sorted relative path, size, and high-resolution
   modification identity and groups all exact numbered files without creating
   a persistent cache or alternate authority.
2. Resolve peer lifecycles from the indexed path groups through the canonical
   lifecycle resolver's existing parsing and transition semantics. The
   implementation may compose those existing semantics inside
   `implementation_authorization.py`; it must not copy or weaken the status,
   provenance, contiguity, duplicate, malformed-correction, or transition
   rules. If clean implementation cannot reuse those semantics without
   changing the resolver API, stop and return for a PAUTH-amended REVISED
   proposal rather than mutating the resolver outside this cohort.
3. Fingerprint the source directory again before returning an allow decision.
   Any added, removed, renamed, resized, or modified numbered bridge file makes
   the evaluation stale and denies implementation start with a stable
   `peer_bridge_snapshot_changed` diagnostic. A stale snapshot is never retried
   implicitly inside the authorization transaction.
4. Parse structured implementation-report `target_paths` and union them with
   the existing recognized heading evidence. Reject malformed or out-of-root
   structured paths fail closed. Preserve exact current-thread, bootstrap,
   clean-path, and non-overlap allowances.
5. Keep terminal VERIFIED or WITHDRAWN peers protective while their terminal
   verdict bytes are absent from or differ from HEAD. Once the exact terminal
   verdict is represented byte-for-byte in HEAD, historical report paths stop
   creating a permanent collision block.
6. Replace fail-soft unreadable/malformed/duplicate peer handling with an
   attributable fail-closed diagnostic. Preserve the exact canonical lifecycle
   decision code, peer id, phase, packet count, bridge-file count, candidate
   count, and elapsed duration without leaking file contents or credentials.
7. Consume the bounded evaluation deadline only through the centralized typed
   timer/concurrency configuration delivered by WI-5806. Missing, invalid, or
   exhausted configuration denies safely. Introduce no hard-coded timeout,
   retry, sleep, throttle, threshold, fan-out, or concurrency value and do not
   read `env.local` independently from this module.
8. Preserve append-only bridge history. The index is request-local and
   discarded after the evaluation; no bridge file, packet, claim, registry,
   runtime, dispatcher, or TAFE state is written by this read-side guard.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5521; PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-V2-20260801; accepted implementation-start peer-scan liveness advisory",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; canonical bridge lifecycle resolver",
  "primary_route": "One read-only implementation-start collision evaluation over one stable append-only bridge snapshot",
  "before_behavior": "The guard performs repeated full-directory lifecycle scans, ignores structured target_paths and terminal-but-uncommitted peers, and fails soft on unreadable peer chains.",
  "after_behavior": "One ephemeral stable snapshot preserves canonical lifecycle decisions, structured and heading evidence, terminal-byte semantics, fail-closed ambiguity handling, and a centrally configured liveness bound.",
  "self_descriptive_naming": "BridgeHistorySnapshot, snapshot-changed diagnostics, peer report paths, and phase/cardinality telemetry name the concepts they govern.",
  "obsolete_guidance_disposition": "Version 002's narrower GO and version 003's dormant-state closure premise remain history but provide no implementation authority.",
  "history_preservation": "All numbered bridge and packet evidence remains append-only; the index is ephemeral and non-authoritative.",
  "baseline": {
    "source_sha256": "bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891",
    "test_sha256": "d59aca8a1c31fc0a3b3cbc6bebc8bc542735feda79bcbeb0eeb19ccff337e98f",
    "focused_tests": "2 passed, 161 deselected",
    "current_complexity": "named_packets times bridge_files"
  },
  "expected_result": {
    "complexity": "One bridge enumeration plus one packet enumeration and linear indexed lifecycle work",
    "semantics": "Equivalent canonical decisions with stronger collision evidence and fail-closed ambiguity",
    "deadline": "Centralized by WI-5806 and relaxed-first/data-tuned",
    "runtime": "No dispatcher, TAFE, claim, packet, registry, or bridge-state mutation"
  },
  "hard_invariants": [
    "Never derive authority from a moving or ambiguous bridge snapshot.",
    "Never weaken canonical lifecycle, provenance, project, PAUTH, claim, or implementation-start gates.",
    "Never replace append-only history with a mutable cache.",
    "Never add a local timer or concurrency literal.",
    "Never mutate live dispatcher or TAFE state."
  ],
  "rollback": {
    "instructions": "Restore only the exact reviewed source and test preimages under separate implementation authority; preserve the numbered proposal and verdict history.",
    "verification": "Rerun semantic-equivalence, scale, snapshot-drift, collision, concurrency, Ruff, format, compile, and scoped-diff checks."
  },
  "fail_closed_conditions": [
    "Missing fresh GO, exact claim, schema-v3 start packet, or allowed operation-time PAUTH result.",
    "Any predecessor, target, imported resolver, or ownership state is non-terminal, dirty, or changed.",
    "Bridge snapshot movement, malformed lifecycle, duplicate version, unreadable evidence, or deadline exhaustion.",
    "Required implementation would modify a path outside this proposal's exact cohort."
  ],
  "essential_context_preservation": "The implementation report must retain exact before/after hashes, snapshot cardinalities, timings, canonical decision equivalence, all denial cases, configuration provenance, and runtime/TAFE non-mutation evidence."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Evidence

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — owner-backed
  project authorization basis.
- `DELIB-202667273` — independent GO for the original narrower design; retained
  as baseline evidence but superseded for future implementation authority.
- `bridge/gtkb-wi5521-dirty-peer-collision-004.md` — current independent NO-GO
  and exact requested revision.
- `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md` through
  `-005.md` — accepted O(packets × bridge-files) liveness evidence and required
  least-duplicate disposition into WI-5521.
- `DELIB-202667722` and `DELIB-202667748` — centralized timer/concurrency SoT,
  relaxed-first configuration, and ongoing evidence-driven tuning direction.

## Owner Decisions / Input

No new owner decision is required for this proposal cycle. The active project,
active exact PAUTH, accepted advisory disposition, and owner's project-level
inheritance and centralized-timer directions already decide integration rather
than a new WI. No source work starts from this statement.

## Specification-Derived Verification Plan

| Requirement | Verification | Acceptance |
| --- | --- | --- |
| Structured and heading report paths | Focused fixtures with structured-only, heading-only, both, malformed, duplicate, and out-of-root evidence | Exact normalized union; malformed/unsafe evidence denies rather than disappearing. |
| Terminal-byte collision semantics | Terminal VERIFIED and WITHDRAWN fixtures before and after exact verdict bytes are represented in HEAD | Dirty overlap blocks before atomic representation and stops blocking only after exact committed representation. |
| Canonical lifecycle equivalence | Table-driven comparison between indexed decisions and the canonical resolver over strict, legacy, correction, malformed, duplicate, unreadable, noncontiguous, and terminal chains | Identical decision or identical canonical diagnostic for every fixture. |
| Stable snapshot | Deterministically add, remove, rename, resize, and rewrite a numbered file between index and decision | Each movement denies with `peer_bridge_snapshot_changed`; no partial allow or hidden retry. |
| Near-additive scale | Synthetic fixtures varying packet and bridge-file cardinalities independently; instrument enumerations and parsed versions | Bridge directory enumerated once per evaluation; work grows with packets plus bridge files, not their product. |
| Concurrent claim/release | Barrier-controlled claim acquire/release while a collision evaluation reads its stable snapshot | No crash, mixed allow, state mutation, or weakened claim/PAUTH result; deterministic diagnostic on relevant movement. |
| Centralized deadline | Inject canonical timer configuration at relaxed, expired, missing, and invalid values | No local literal; valid relaxed value completes; missing/invalid/exhausted configuration denies with phase/cardinality telemetry. |
| Existing non-impairment | Run the complete implementation-authorization test file plus the current WI-5105 regression cases | Current-thread, bootstrap, clean-path, nonoverlap, packet integrity, project, PAUTH, and start gates remain green. |
| Code quality and exact scope | `python -m ruff check` and `python -m ruff format --check` on both targets, `python -m py_compile scripts/implementation_authorization.py`, `git diff --check`, exact hashes and scoped status | All exit 0; only the reviewed two-file cohort changes. |

The implementation report must include exact commands, observed durations,
packet and bridge-file cardinalities, enumeration counts, configuration source,
pre/post hashes, and explicit evidence that no dispatcher or TAFE state changed.
Independent Loyal Opposition verification remains mandatory.

## Timer, Concurrency, And SoT-Latency Disposition

The accepted advisory already provides evidence that repeated full-directory
scans exceeded a 90-second observation window at 507 packets and 14,086 bridge
files. WI-5521 owns removal of the multiplicative read pattern. WI-5806 owns
centralized timer, throttle, threshold, fan-out, and concurrency configuration;
this proposal adds no duplicate timer WI and no local constant. Broader
append-only SoT access and concurrent-writer evidence remains in the existing
Prime-prepared advisory bundle; no duplicate Advisory Report is created.

## Preconditions And Sequencing

- WI-5382 and WI-5454 must be terminal and focused-finalized.
- WI-5806 must provide the canonical configured evaluation deadline or the
  implementation must remain held.
- Foreign work on `scripts/bridge_lifecycle_resolver.py` must be terminal,
  released, and clean. WI-5521 may import its behavior but may not mutate it.
- Both declared targets must still match the exact preimages above.
- A fresh independent GO, exact claim, schema-v3 implementation-start packet,
  and allowed operation-time PAUTH result are mandatory.
- Any need for a third source or test path stops implementation and requires a
  PAUTH-amended REVISED proposal and another independent review.

## Risks And Rollback

The primary risks are lifecycle-semantic divergence, false authorization from
a mixed snapshot, permanent blocking from terminal history, and a new liveness
failure disguised as safety. The equivalence, stable-snapshot, cardinality,
deadline, and concurrency tests above are mandatory countermeasures.

Rollback restores only the two exact reviewed preimages. Bridge and advisory
history remains append-only. No runtime rollback is expected because this
guard is read-side and must not mutate dispatcher, TAFE, claim, packet,
registry, or bridge state.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

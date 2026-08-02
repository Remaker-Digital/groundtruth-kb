REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; review-only reconciliation; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current_interactive_session_context

bridge_kind: prime_proposal
Document: gtkb-wi5742-bound-protected-commit-evaluation
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5742-bound-protected-commit-evaluation-004.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5742
Related Work Items: WI-5715, WI-5806, WI-5825, WI-5839, WI-5858, WI-5869, WI-5881

target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", ".codex/skills/gtkb-verify/helpers/write_verdict.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/scripts/test_bridge_publication_finalization_atomicity.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]
implementation_scope: layer_c_transaction_reconciliation_and_completion
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_packet_evidence_in_scope: false

This proposal performs no KB mutation. This proposal creates no approval-packet evidence.

# REVISED Implementation Proposal — WI-5742 Layer C Atomic Finalization Reconciliation

## Revision Claim

Version 003's non-implementation premise was false. WI-5742 Layers A and B were
implemented in commit `45fedc3993130e1a23e38cfd3177d1663745678c` and independently
VERIFIED in the sibling thread
`gtkb-wi5742-emergency-bootstrap-implementation-report`. This revision preserves
that evidence, reopens the original thread truthfully, and retains the original
Layer C transaction-ordering and compensation scope under WI-5742.

Layer C is not yet implemented. The two exact Layer C nodes remain deliberately
skip-marked, and the current finalizer still calls `write_bridge_file` before it
creates the disposable Git index or runs the protected commit. The governed
writer still mints, materializes, and consumes publication authority before the
commit is durable. The missing structural correction is therefore real and is
not closed by the verified Layers A/B performance work.

This revision seeks independent review of a dependency-aware completion plan.
It starts no implementation, claims no protected target, changes no source or
test, and creates no new timer, retry, throttle, threshold, fan-out, or
per-harness concurrency value.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5742, its original proposal and
operative v004 findings, the twenty linked specifications below, the current
owner timer/concurrency decisions, TEST-11790, the two explicit Layer C test
nodes, and the accepted dependency interfaces named in this revision fully
specify the required outcome. No additional requirement, specification, owner
scope decision, timer value, or concurrency policy is needed for independent
review. Dependency convergence and a future GO/claim/start remain operation
gates, not missing requirements.

## Findings Addressed

### F1 — correct the false NO-ACTION premise and link the landed evidence

Accepted. Commit `45fedc3993130e1a23e38cfd3177d1663745678c` contains the seven
reported Layers A/B paths. The sibling implementation report v001 records the
implementation and its commands; sibling v002 independently records VERIFIED.
Those artifacts prove only the implemented Layers A/B cohort. They do not prove
Layer C, and this revision does not use them as a substitute for Layer C tests.

Prior versions remain immutable. Version 003 is retained as historical evidence
of the stale premise; version 004 is the operative NO-GO; this version is the
forward-only correction.

### F2 — preserve and complete Layer C under WI-5742

Accepted. The owner has not narrowed or split the original scope, and no scope
change is needed. Layer C remains a WI-5742 obligation. The future implementation
must remove the publish-before-commit ordering and replace old-aggregate-preimage
rollback assumptions with an exact, resumable, append-only recovery transaction.

This is not a duplicate of WI-5881 or WI-5825. WI-5742 owns the verified-finalizer
orchestration that must delay terminal visibility until commit eligibility is
established. WI-5881 owns the generic exact-generation durable reservation and
fence contract. WI-5825 owns capability/receipt recovery and backfill. Layer C
consumes those contracts after they are independently accepted; it does not
reimplement them locally.

## Current Evidence And Target Attribution

- Operative v004 is `NO-GO`, SHA-256
  `16AD3348A6C0301A5987FFF48485DD99DBEDBD5441F4BD5434F7225BD5798E6F`.
- Focused baseline:
  `python -m pytest platform_tests/scripts/test_protected_commit_evaluation_bound.py platform_tests/scripts/test_bridge_publication_finalization_atomicity.py -q`
  produced **39 passed, 2 skipped**. The skips are exactly
  `test_finalize_verified_near_bound_is_atomic` and
  `test_compensation_succeeds_after_sibling_aggregate_append`.
- `.claude/skills/gtkb-verify/helpers/write_verdict.py` and its generated Codex
  projection are byte-identical at SHA-256
  `FE441376957C64787FE5F1A8787CDBB50F79074BCDD6E8B23F5D182F221E76BD`.
- `scripts/gtkb_bridge_writer.py` is clean at SHA-256
  `9399A3878D99C0CB007C9A7E979F25C09B6EDFAC841CB75C6FB78D3C8472F2F4`.
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` and
  `groundtruth-kb/tests/test_registry_control_plane.py` are foreign-dirty under
  the current WI-5715 work. Their observed hashes are respectively
  `A063E0CB057FACFC86D077360B02EB9805A1EB516C7CE16CCED0B472D06C3006`
  and `FDA19AED075D4D397BF7A97556CB4395D6EA97324012DA08A8E39BE327349073`.
  WI-5742 may not edit, stage, overwrite, or attribute either file until that
  owner lands and a fresh clean/collision read succeeds, unless an independently
  reviewed exact hunk ledger is accepted.
- The atomicity and writer test files are clean at the observed hashes
  `6CAC74D6E8807FE51BE8A9D58AF69366AF5646A379E3BB5562ED54A50DCB8BF8`
  and `38A4BDEFF74BB9AA3F841C35F103DE3393945C36CBCA42925314D9605DA6D871`.

These are observation hashes, not implementation-start bindings. Fresh hashes,
ownership, claim, and schema-v3 start evidence are mandatory after dependencies
converge.

## Layer C Design

### C1 — prepare and bind exact candidate bytes before visibility

The finalizer first produces the complete normalized verdict bytes, author
envelope, candidate-evidence hash, predecessor binding, reviewed report set,
expected commit paths, and intended commit message without creating the live
numbered bridge file and without minting publication capability. The exact tuple
is persisted through the WI-5881 durable reservation interface before any
filesystem move or terminal publication.

The canonical `.claude` verify skill remains the authored source. The `.codex`
copy is regenerated by the managed-skill projection pipeline and parity-checked;
it is never hand-edited.

### C2 — evaluate the exact commit candidate before mint

Build the disposable Git index from HEAD and bind the intended verdict blob and
the reviewed implementation/report cohort into that index. Run the complete
Layers A/B protected-commit evaluation against that exact candidate generation.
The evaluation result is valid only for the bound HEAD, tree/index digest,
verdict digest, predecessor, target set, project authorization, implementation
start, claim/fence epoch, and reservation event head. Any drift invalidates the
result and returns to preparation with no live terminal file and no publication
capability.

The implementation must not use `--no-verify`, weaken a protected gate, trust a
shared mutable index, or accept an unbound preflight. The final commit path must
either execute the ordinary hooks against the exact prepared index or consume a
mechanically verified single-use gate result bound to the same tuple. If the
existing seven-target design cannot preserve that invariant, implementation
stops and returns to REVISED scope rather than silently adding a bypass or an
undeclared checker target.

### C3 — commit-before-terminal visibility with late mint

Only after exact-candidate authorization succeeds may the transaction enter its
short commit/publication phase. The durable reservation and exact candidate
allow the finalizer to make the reviewed Git generation durable before the
terminal numbered file becomes dispatcher-visible. The governed writer then
late-mints publication authority for the already-bound tuple, materializes the
exact stored bytes, consumes the WI-5825 receipt exactly once, and closes the
reservation/claim only after Git, physical file, capability, receipt, and event
readbacks converge.

No post-gate regeneration, renormalization, author replacement, candidate hash
restamp, path expansion, or predecessor refresh is permitted. The materialized
bytes must equal the committed/reserved bytes exactly.

### C4 — forward recovery after any residual partial phase

A process failure after the commit generation is durable must not attempt to
restore an obsolete aggregate preimage after unrelated append-only siblings have
advanced. Recovery reopens the exact WI-5881 reservation, validates the current
invoker/role/claim/start/fence separately from the immutable original author and
candidate bytes, observes the exact physical and Git state, and completes only
the missing publication/receipt/events.

Failures before durable commit leave no live terminal file and no minted or
consumed capability. Failures after durable commit preserve the reservation and
advance forward; they do not erase candidate bytes, unrelated aggregate history,
receipts, or incident evidence. A foreign or ambiguous state fails closed and is
reported as typed recovery-required evidence.

### C5 — claim and convergence ordering

The finalizer holds the exact work-intent claim through preparation, candidate
authorization, durable commit, materialization, capability/receipt consumption,
and final readback. Claim release is the last state transition. Release failure
after all other surfaces converge is represented as `release_pending` and is
idempotently repairable; it never authorizes duplicate publication.

The transaction uses WI-5881's published total phase/lock order. It introduces
no global leader and does not hold a work-intent SQLite transaction while
acquiring the control-plane registry lock, Git index lock, or filesystem move.

## Cross-Harness Disposition

No typed waiver is requested or used. The behavioral contract is common across
all harnesses even though only Claude and Codex have a materialized verify-skill
helper in this seven-target cohort.

| Harness | Disposition |
|---|---|
| Claude (B) | `.claude/skills/gtkb-verify/helpers/write_verdict.py` is the canonical authored helper. All Layer C behavior and tests originate here. |
| Codex (A) | `.codex/skills/gtkb-verify/helpers/write_verdict.py` is regenerated from the canonical Claude skill through the managed-skill projection pipeline; byte and behavior parity are mandatory. It is never hand-edited. |
| Cursor (E), Antigravity (C), Goose (G), Ollama (D), OpenRouter (F), Alibaba Cloud Studio (H) | These harnesses receive no harness-local helper edit in this proposal. Any invocation of finalization, governed writer, control-plane reservation, or receipt services consumes the same shared source contract and must pass the same role, claim/start, byte-binding, crash/recovery, timer-source, and exactly-once tests. No ambient harness fallback or vendor-specific branch is added. |

The implementation report must include the managed-skill generation command,
canonical/projection hashes, parity test results, and shared-service test evidence.

## Dependency And Implementation Hold

Independent review may proceed now. Protected implementation is held until all
of the following are freshly true:

1. WI-5715 has terminalized or supplies an independently accepted exact hunk
   ledger, and the two registry targets are collision-free for WI-5742.
2. WI-5839's centralized capability lifetime/mint-admission contract is landed
   and no production hard-coded timer or fallback remains in this transaction.
3. WI-5825 and its required WI-5812 ordering provide the exact receipt/recovery
   semantics consumed here.
4. WI-5881 provides the accepted exact-generation reservation, fencing, phase
   order, and forward-recovery interface.
5. Project/WI/PAUTH are current, a fresh exact `go_implementation` claim is
   acquired, and a schema-v3 implementation-start packet binds the final target
   set, hashes, reviewed GO, claim, and authorization.

Current WI-5715 is `NO-GO` v004. WI-5825 is `GO` v006 but is not treated as
implemented. WI-5839 and WI-5881 are `REVISED` v005 and await independent
review. Those states prohibit a WI-5742 implementation start today.

## Timer, Threshold, Throttle, Fan-Out, And Concurrency Contract

`DELIB-20260801-TIMER-CONCURRENCY-SOT-DIRECTION`,
`DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE`, and
`DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` supersede any design
assumption that a production literal or arbitrary short caller timer is an
acceptable default. WI-5806 is the program-level centralized timer/concurrency
carrier; WI-5839 owns capability lifetime; WI-5715 owns coherent read
scalability; WI-5858/WI-5869 retain observed contention/publication latency.

WI-5742 introduces no numeric production timeout, TTL, retry count, sleep,
polling interval, lock wait, throttle, threshold, fan-out, queue capacity, or
per-harness concurrency limit. Every such policy consumed by this transaction
must come from the governed typed timer/concurrency SoT, be inspectable with its
source and units, fail closed when absent or invalid, and emit measurement data
for later tuning. Test clocks or already-exhausted injected deadlines may be
used only as deterministic controls; they are not production policy fallbacks.

The 2026-08-01 publication recurrence that ran for 168.4 seconds before a fixed
registry-lock failure is already routed to WI-5869, WI-5881, and WI-5825. No
duplicate work item is created by this revision. Any newly observed timer or
concurrency control without an exact existing carrier must be filed as a new
project-linked WI before implementation proceeds.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — exact append-only status authority and
  convergent terminal publication.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — explicit PAUTH,
  project, WI, targets, requirements, and derived verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — both Layer C nodes must
  execute; skip markers cannot establish completion.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — later operations
  require current list-free project authority, claim, and start evidence.
- `GOV-ARTIFACT-APPROVAL-001` — formal artifact evidence is unchanged; this
  revision does not create an approval packet.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — terminal visibility, exact commit,
  index isolation, and recovery remain governed.
- `GOV-WORK-TREE-HYGIENE-001` — foreign registry bytes and index state are never
  absorbed or overwritten.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — candidate, reservation, HEAD/index,
  claim/start/PAUTH, capability, receipt, and physical readbacks are current at
  each CAS boundary.
- `GOV-ENV-LOCAL-AUTHORITY-001` — environment-backed policy values are resolved
  only through the governed typed configuration surface.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — authorization,
  byte binding, projection parity, and no-literal policy are mechanical gates.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — canonical skill ownership,
  generated Codex projection, shared-service semantics, and parity evidence are
  explicit and mechanically checked without a waiver.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — deterministic phase outcomes and
  typed recovery replace manual timing and cleanup.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — proposal, reservation, event, report,
  and verification evidence remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5715, WI-5806, WI-5825, WI-5839, WI-5858,
  WI-5869, WI-5881, and WI-5742 remain distinct governed carriers.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation and evidence
  paths stay inside the GT-KB root.

## Prior Deliberations

- `DELIB-202667740`, `DELIB-202667741`, and `DELIB-202667743` — the emergency
  Layers A/B authorization and operative GO history; evidence of the landed
  bounded cohort, not authority for new Layer C implementation.
- `DELIB-202667722` — earlier configuration-sourced timer discipline used by
  Layers A/B.
- `DELIB-20260801-TIMER-CONCURRENCY-SOT-DIRECTION` and
  `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` — current owner
  direction to remove hard-coded timer/concurrency policy and tune centrally
  from evidence.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` — highly parallel
  contention is expected; arbitrary short timers are not failure evidence.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — preserve
  useful parallel work without a program-wide leader.
- `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` — exact forward recovery and
  commit convergence discipline.
- `DELIB-202667721` and `DELIB-202667734` — Housekeeping Hardening project
  authority and its correction.

## Specification-Derived Verification Plan

| Requirement sources | Test node or check | Required result |
|---|---|---|
| WI-5742; `GOV-FILE-BRIDGE-AUTHORITY-001`; `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | `test_finalize_verified_near_bound_is_atomic` | Execute without skip; failed candidate evaluation leaves no live terminal file/capability, while a successful exact candidate converges commit, file, capability, receipt, reservation, and claim once. |
| WI-5742; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; artifact lifecycle specs | `test_compensation_succeeds_after_sibling_aggregate_append` | Execute without skip; an unrelated append after reservation/mint does not require restoring its old aggregate preimage and does not lose either append. |
| Project authorization and operation-time DCLs | exact PAUTH/claim/start drift matrix | Missing, expired, mismatched, or changed project/WI/PAUTH/GO/claim/start/fence yields zero terminal publication mutation. |
| Proposal-linkage DCLs; `GOV-ARTIFACT-APPROVAL-001` | bridge compliance and approval-evidence guards | Proposal linkage passes; no KB or approval-packet mutation is inferred. |
| `GOV-WORK-TREE-HYGIENE-001` | disposable-index and foreign-dirt tests | Shared index and foreign registry bytes remain unchanged; committed path set equals the reviewed cohort. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | crash injection at prepare, gate, commit, mint, file, receipt, and claim-release boundaries | Each boundary has one typed, idempotent forward outcome with no manual cleanup. |
| Timer/concurrency owner decisions; `GOV-ENV-LOCAL-AUTHORITY-001` | production-source AST/config-source assertion | No new hard-coded timeout, TTL, retry, sleep, throttle, threshold, fan-out, capacity, or per-harness concurrency literal/fallback exists. |
| Managed-skill, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, and cross-cutting enforcement specs | canonical/projection regeneration and byte/behavior-parity tests across shared service callers | `.codex` helper is generated from `.claude`; all applicable harnesses consume identical role, claim/start, reservation, receipt, timer-source, and recovery semantics without fallback. |
| `GOV-STANDING-BACKLOG-001` | dependency/current-head assertions | WI-5715, WI-5825, WI-5839, and WI-5881 are not falsely claimed complete and their owned behavior is not duplicated. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | target/root-boundary assertion | Every target, temp/reservation record, receipt, and test store stays in-root. |

The implementation report must carry all linked specifications forward, name
the exact test nodes and commands, record observed results, preserve pre/post
hashes and event identities, and disclose every skipped, flaky, or pre-existing
failure. A skipped Layer C node is a failed acceptance criterion.

## Acceptance Criteria

1. The original chain truthfully distinguishes verified Layers A/B from
   unimplemented Layer C without rewriting history.
2. Exact candidate bytes and all authority/evidence bindings are durable before
   terminal visibility and cannot be regenerated during recovery.
3. Full protected-commit authorization evaluates the exact intended candidate
   generation before publication capability minting.
4. No gate failure can leave a live terminal file, consumed capability, or
   ambiguous claim.
5. A durable commit followed by publication interruption is completed forward
   from the reservation; unrelated append-only aggregate movement is preserved.
6. Capability and receipt consumption are exactly once and bind the same author,
   candidate, predecessor, project, claim/start/fence, and commit generation.
7. Claim release occurs only after exact convergence; `release_pending` is
   resumable and never grants duplicate publication.
8. The two currently skipped Layer C tests execute and pass, with crash/race and
   zero-mutation negative coverage.
9. WI-5715/WI-5825/WI-5839/WI-5881 land or supply independently accepted exact
   interfaces before implementation; foreign bytes are not absorbed.
10. The verify skill projection is generated and byte/behavior-equivalent.
11. No production hard-coded timer, retry, throttle, threshold, fan-out,
    capacity, or per-harness concurrency literal or fallback is added.
12. No dispatcher/TAFE activation or mutation, credential action, external
    service action, deployment, release, push, history rewrite, lock deletion,
    broad cleanup, raw database bypass, or `--no-verify` path occurs.

## Risks And Rollback

- Cross-store partial phases are the primary risk. Durable exact-generation
  reservation/events plus strict lock order make them observable and resumable.
- Late failure after commit cannot be repaired by erasing unrelated aggregate
  history. Forward completion from committed bytes is the only accepted path.
- Additional exact candidate bytes increase exceptional recovery storage and
  read cost. Measure it and route meaningful latency to the existing SoT access
  advisory/carrier; do not hide it behind a local threshold.
- Dependency drift can invalidate the proposed interface. Reobserve and return
  to REVISED if any required API or target set changes.
- Before any durable reservation exists, rollback may revert only approved
  WI-5742 hunks after fresh foreign attribution. After reservation/commit,
  preserve bytes/events and recover or govern abort forward; never delete audit
  evidence.

## Owner Decisions / Input

No new owner decision is required for review. The owner has not narrowed or
split Layer C, so WI-5742 retains it. The active list-free Housekeeping Hardening
project authorization permits review under the parent-project approval model;
implementation remains separately gated by independent GO, dependencies, fresh
claim/start evidence, and exact target ownership.

## Candidate Pre-Filing Gates

Before live filing, reobserve v004 status/hash and v005 absence; confirm the
current Prime Builder role/session and no foreign draft claim; run candidate
applicability, clause, project-linkage, credential/pattern, and report-shape
checks; then publish only through the governed revision writer. After publication,
require exact live path/status/hash plus capability/receipt/pending-sidecar and
claim-release convergence. Timeout or lock contention is not proof of failure;
reobserve exact state before any retry.

## DISARM — Review-Only Boundary

This revision creates no implementation-start packet and authorizes no source,
test, configuration, database, Git/index, lock, capability-recovery, receipt,
or evidence-move mutation. Layer C implementation requires a future independent
GO and every hold condition above. TAFE remains deliberately disabled.

## Files Expected To Change After GO And Dependency Convergence

- `.claude/skills/gtkb-verify/helpers/write_verdict.py`
- `.codex/skills/gtkb-verify/helpers/write_verdict.py` (generated projection)
- `scripts/gtkb_bridge_writer.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `platform_tests/scripts/test_bridge_publication_finalization_atomicity.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

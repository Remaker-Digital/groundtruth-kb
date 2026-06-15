NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: prime-interactive-wi4510-cutover-readiness-2026-06-14
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style; 1M context

# WI-4510 — Governed cutover of bridge/INDEX.md authority to the TAFE generated view (decision + gated execution plan)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510
target_paths: []

## Summary

WI-4510 is the terminal, IRREVERSIBLE step of the TAFE Phase 6-7 cutover sequence: switching
`bridge/INDEX.md` workflow-state authority from the hand-maintained file to the TAFE-generated
view (MemBase flow records become canonical; `bridge/INDEX.md` becomes a read-only rendering).
Per its definition and `DELIB-20263195`, WI-4510's deliverable is "bridge proposal + Loyal
Opposition review + owner AUQ" — it RETAINS a closing owner AUQ and is not auto-promoted.

This is that bridge proposal. It is a **governance / decision proposal**: it presents the
now-green cutover-readiness evidence, records a material readiness finding, and proposes a
**gated execution plan** for the cutover. It proposes **no source changes** in this step
(`target_paths: []`); the cutover mechanism is correctly captured as a follow-on architecture
decision (ADR/DCL) and implemented only after this proposal is GO'd AND the owner approves the
closing AUQ.

The precursor reconciliation (WI-4546) that the owner HELD this cutover behind
(`DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614`) is now resolved + VERIFIED, and the
owner authorized beginning cutover readiness (`DELIB-20263410`, this session).

## Readiness Evidence

Read-only `gt flow cutover-evidence --json` (2026-06-14, `mutated: False`, INDEX byte-identical
before/after) reports `status: "ok"`, `ok: True`, and the summary "Evidence supports a cutover
proposal (WI-4510 owner-gated)":

- **Completeness:** `lost_blocks: 0`, `extra_blocks: 0`, `archived_blocks: 635` (the WI-4546
  terminal-archived oracle refinement — VERIFIED — reclassifies protocol-trimmed terminal
  threads as legitimately archived rather than lost).
- **Parity (dual-write):** `ok: True`, `parity_mismatches: 0`, derived 1956 == index 1956
  version-lines, 345/345 threads. The generated view is byte-faithful to the canonical INDEX.
- **Contention:** `contention_zero: True`, 0 replan artifacts/instances.
- **Fidelity:** `ok: True`, 0 fidelity_mismatches over 345 threads.

This is the clean re-ingest the owner's hold required. At hold time the same tool reported 634
lost_blocks, 1 extra_block, 14 fidelity_mismatches, and created/updated re-plan actions; all four
categories are now clean.

## Material Readiness Finding (mechanism gap)

A read-only investigation of the TAFE source establishes that the cutover **operation itself is
not yet implemented**:

1. There is no authority-transfer mechanism in code (no command/flag/state that flips
   `bridge/INDEX.md` from hand-maintained to a read-only rendering of the authoritative
   generated view). `gt flow cutover-evidence` is read-only and explicitly refuses to write the
   canonical INDEX (`GOV-FILE-BRIDGE-AUTHORITY-001` enforcement); `gt flow ingest-bridge-index`
   is the non-authoritative dual-write shadow ingest.
2. There is **no rollback path** in code. The cutover is currently framed as one-way and
   irreversible (`DELIB-20263195`).
3. The cutover PAUTH (`...-PHASE-6-7-CUTOVER-WI-4508-4509-4510`) ALLOWS `dual_write` and
   `authoritative_generated_view` but FORBIDS the `cutover` mutation class — confirming the
   irreversible flip is deliberately held behind a further gate beyond this proposal.

Consequence: WI-4510 is genuinely a design+governance step, not a rubber-stamp of a ready
operation. The cutover mechanism (authority transfer + a reversibility/contingency backstop) is
an architecture decision that must be captured as an ADR/DCL and implemented under a
cutover-execution authorization AFTER this proposal is GO'd and the owner approves the closing
AUQ. This proposal surfaces that, with two decisions flagged for the closing owner AUQ (see
§ Owner Decisions / Input).

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — the umbrella spec; the cutover is the dual-write
  program's terminal step (lossless + complete + faithful parallel view → authoritative view).
- `ADR-TAFE-SLICE-C-INGESTION-001` — the D1-D4 deterministic derivation the parity/fidelity
  evidence assesses; the cutover relies on this derivation being faithful (it is: parity 345/345).
- `SPEC-TAFE-R7` — MemBase is the canonical surface post-cutover; the requirement the cutover
  realizes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is the sole authoritative workflow state
  until cutover is complete; the cutover is precisely a governed transfer of that authority and
  must preserve the audit trail. The cutover mechanism must honor this gate's transition
  semantics (canonical INDEX preserved/rendered, not silently mutated).
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` — the WI-4546 completeness contract (terminal
  archived ≠ lost); the green completeness evidence depends on it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory cross-cutting: this
  proposal cites all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandatory cross-cutting: applies to the
  follow-on mechanism implementation (this governance proposal makes no code change); its
  verification plan derives tests from the cutover-mechanism ADR/DCL captured in Step 1.

## Prior Deliberations

- `DELIB-20263195` — owner AUQ 2026-06-13 authorizing the FULL TAFE cutover sequence
  (WI-4508 dual-write, WI-4509 evidence, WI-4510 governed cutover); WI-4510 RETAINS its closing
  owner AUQ and is IRREVERSIBLE / not auto-promoted.
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` — owner HELD WI-4510 pending a clean
  shadow re-ingest (then: 634 lost_blocks, 14 fidelity_mismatches). Clear-condition now met.
- `DELIB-20263410` — owner AUQ this session (2026-06-14) lifting the hold and authorizing this
  proposal's drafting; cutover execution remains gated behind WI-4510's closing AUQ.
- WI-4546 thread `gtkb-tafe-shadow-index-reconciliation` (VERIFIED) — the precursor completeness-
  oracle refinement that produced the green completeness evidence.
- Sibling cutover-sequence threads (VERIFIED): `gtkb-tafe-dual-write-index-parity`,
  `gtkb-tafe-dual-write-slice-b-oracle`, `gtkb-tafe-slice-c-ingestion-consolidated`,
  `gtkb-wi4509-cutover-evidence`, `gtkb-tafe-bridge-index-preview` (compatibility view).

## Owner Decisions / Input

This proposal depends on owner approval. WI-4510 retains a closing owner AUQ per `DELIB-20263195`;
that AUQ is requested at the end of this proposal's lifecycle (after Loyal Opposition GO), not
now. Authorizations already captured:

- `DELIB-20263195` — full cutover sequence authorized (program-level).
- `DELIB-20263410` (this session) — hold lifted; this proposal authorized for drafting + review.

Two decisions are surfaced for the **closing owner AUQ** (and to shape the Step-1 ADR/DCL):

1. **Reversibility stance.** The cutover is currently framed one-way/irreversible with no rollback
   in code. Recommendation: require a reversibility backstop before the flip — at cutover time,
   freeze a timestamped immutable copy of `bridge/INDEX.md` and provide a documented (ideally
   code-supported) revert procedure that regenerates the hand-maintained INDEX from the shadow.
   This converts "irreversible" into "reversible with bounded effort" and materially de-risks the
   terminal step. Decision: (a) require the reversibility backstop (recommended); (b) accept a
   one-way flip with a frozen backup only; (c) accept a one-way flip with no backstop.
2. **Mechanism scope at execution.** Whether the cutover flip also re-routes subsequent bridge
   writes through the typed-flow API immediately, or whether `bridge/INDEX.md` is first frozen as
   a generated rendering with write-routing changed in a subsequent slice. Recommendation: stage
   it — freeze + render first, re-route writes second — to minimize the blast radius of the
   irreversible step.

These are recorded here so Loyal Opposition can review the gating and the owner can decide at the
closing AUQ. No owner decision is required to REVIEW this proposal.

## Requirement Sufficiency

**New or revised requirement required before implementation.** The cutover authority-transfer
mechanism and its reversibility contract are an architecture decision not yet captured. Per GOV-20,
a new `ADR-TAFE-CUTOVER-AUTHORITY-TRANSFER-001` (decision + mechanism + reversibility + rejected
alternatives + consequences) and a derived `DCL-TAFE-CUTOVER-AUTHORITY-TRANSFER-001`
(machine-checkable cutover/rollback contract) must be captured first through the governed
formal-artifact-approval path. The source/test implementation of the mechanism proceeds only
after those artifacts land, the owner approves the closing AUQ, and a cutover-execution
authorization (the `cutover` mutation class is currently forbidden even by the Phase-6-7 cutover
PAUTH) is granted. This proposal authorizes only review + the closing-AUQ decision, not source,
config, or `bridge/INDEX.md` mutation.

## Proposed Change (gated execution plan)

No change in this step (`target_paths: []`). The proposed sequence, each step gated by the prior:

- **Step 0 (this proposal):** Present green readiness evidence + the gated plan; obtain Loyal
  Opposition GO; then the closing owner AUQ (reversibility stance + mechanism scope per § Owner
  Decisions / Input).
- **Step 1 — Requirement capture (formal-artifact approval; not source):** Capture
  `ADR-TAFE-CUTOVER-AUTHORITY-TRANSFER-001` + `DCL-TAFE-CUTOVER-AUTHORITY-TRANSFER-001` defining
  the authority-transfer mechanism, the reversibility/contingency contract (per the owner's
  closing-AUQ choice), and the GOV-FILE-BRIDGE-AUTHORITY-001-compliant transition semantics.
- **Step 2 — Mechanism implementation (source + test; cutover-execution authorization required):**
  Implement the authority-transfer command/state + the reversibility backstop + tests. The
  Phase-6-7 cutover PAUTH allows `authoritative_generated_view` but forbids `cutover`; this step
  needs a cutover-execution authorization. (Marker note: an interactive `::init gtkb pb` session
  is currently `go_implementation`-blocked; this step is dispatchable swarm or marker-enabled
  work.)
- **Step 3 — Execute cutover:** Run the flip with the frozen-backup precondition; verify the
  generated view is authoritative and `bridge/INDEX.md` renders read-only at full parity.
- **Step 4 — Post-cutover verification + report:** Re-run cutover-evidence + the mechanism tests;
  file the implementation report for VERIFIED.

## Spec-Derived Verification Plan

- **Readiness (this step):** the green `gt flow cutover-evidence --json` result above is the
  evidence that the parallel view is lossless (parity), complete (WI-4546 oracle), faithful
  (fidelity), and stable (contention-zero) — the precondition the umbrella spec requires before a
  cutover. Reproduce via `gt flow cutover-evidence --json` (read-only; `mutated: False`).
- **Mechanism (Step 2, derived from the Step-1 ADR/DCL):** new tests asserting (a) the flip makes
  the generated view authoritative and renders `bridge/INDEX.md` read-only at parity; (b) the
  reversibility backstop produces a faithful hand-maintained INDEX on revert; (c) the transition
  honors GOV-FILE-BRIDGE-AUTHORITY-001 (no silent canonical mutation). Existing coverage to build
  on: `groundtruth-kb/tests/test_tafe_cutover_evidence.py`, `test_tafe_index_completeness.py`,
  `test_tafe_bridge_ingestion.py`, `test_tafe_index_sync.py`, `test_tafe_flow_cli.py`,
  `test_cli_authority.py`.
- Gates on any changed Python (Step 2): `ruff check` + `ruff format --check`.

## Risk / Rollback

- **Risk (P0): irreversibility.** The flip is the program's terminal step and has no code-supported
  revert today. **Mitigation:** the recommended reversibility backstop (frozen immutable INDEX
  backup + documented/coded revert) in Step 1/2, decided at the closing owner AUQ. A GO should not
  authorize execution without the owner's reversibility decision recorded.
- **Risk: authority-transfer correctness.** A faulty flip could corrupt workflow state.
  **Mitigation:** the green parity/fidelity evidence is the precondition; Step 2 tests assert the
  transition; staged mechanism scope (freeze+render before write re-route) bounds blast radius.
- **Risk: concurrency.** Multiple sessions write `bridge/INDEX.md`. **Mitigation:** execute the
  flip via the serialized bridge-index writer; the cutover-evidence contention-zero result shows a
  stable shadow.
- **Rollback (this proposal):** none needed — it makes no change. A NO-GO simply revises the plan.

## Recommended Commit Type

Not applicable to this governance/decision proposal (`target_paths: []`; no commit results from a
GO). The follow-on Step-2 mechanism implementation will recommend `feat:` (new authority-transfer
+ reversibility capability).

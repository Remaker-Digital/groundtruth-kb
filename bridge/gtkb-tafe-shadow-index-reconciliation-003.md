REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: prime-interactive-claim-gate-filing
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style
author_metadata_source: Claude Code Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# WI-4546 — TAFE shadow-vs-INDEX reconciliation: refine the completeness oracle so terminal-archived threads are legitimately absent

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-7-RECONCILIATION-WI-4546
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4546
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py", "groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py", "groundtruth-kb/tests/test_tafe_index_completeness.py", "groundtruth-kb/tests/test_tafe_cutover_evidence.py"]

## Revision Scope

This REVISED `-003` addresses the single P1/blocking finding in the Loyal Opposition
NO-GO at `bridge/gtkb-tafe-shadow-index-reconciliation-002.md`:

> **F1 — Requirement-Capture Prerequisite Is Not Complete.** The `-001` proposal declared
> "New or revised requirement required before implementation" (the terminal-archived
> completeness contract) but that formal artifact had not yet landed; a GO would have
> authorized implementing changed cutover-completeness semantics before the governing
> requirement existed. Codex's required correction: capture the formal requirement first
> through its governed approval path, then revise this proposal to cite it as landed.

**Resolution.** The prerequisite formal requirement has now LANDED:
`DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v1 (type=design_constraint, status=specified,
derives from `ADR-TAFE-SLICE-C-INGESTION-001`) was inserted into MemBase under owner
approval (AskUserQuestion → `DELIB-WI4546-DCL-COMPLETENESS-APPROVE-20260614`; formal-artifact
-approval packet `.groundtruth/formal-artifact-approvals/2026-06-14-DCL-TAFE-COMPLETENESS-
TERMINAL-ARCHIVED-001.json`). Accordingly this REVISED:

1. Adds `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` to § Specification Links as the
   **landed governing requirement** for the refined completeness semantics.
2. Changes § Requirement Sufficiency to **"Existing requirements sufficient"** — the DCL
   now defines the contract, so the source/test implementation is directly authorized.
3. Marks former Step 1 (requirement capture) **DONE** and renumbers the implementation
   steps; the source/test target envelope is unchanged from `-001`.

No design change. The oracle-refinement approach, target_paths, verification plan, and
risk posture are identical to `-001`; only the requirement-sequencing gap Codex flagged is
closed.

## Summary

WI-4546 is the precursor reconciliation that must make the TAFE cutover-evidence clean
before WI-4510 (governed cutover) can be re-attempted (WI-4510 is HELD per
`DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614`). Live read-only
`gt flow cutover-evidence --json` (session c2f8c28a, `bridge/INDEX.md` not mutated) shows
the gating gap is **634 `lost_blocks`** (on-disk `bridge/<slug>-NNN.md` slugs with no
`Document:` entry in `bridge/INDEX.md`). The cutover gate `CutoverEvidenceReport.ok`
requires `lost_blocks == []`.

A read-only characterization (latest on-disk version's status token, markdown heading
markers stripped) splits the 634 into:

| Class | Count | Disposition |
|---|---|---|
| Latest token VERIFIED (terminal) | 550 | Correctly INDEX-trimmed completed threads |
| Latest token ADVISORY (terminal) | 1 | Completed advisory |
| No first-line status token (old multi-version completed threads, pre Body-Status-Token rule) | 40 | Historical archive |
| **Subtotal — terminal/historical archive** | **~591** | **Benign: the protocol trims terminal entries by design** |
| Latest token GO (orphan) | 19 | Proposal-stage GO; mostly implemented via a paired `-implementation` thread, then trimmed |
| Latest token NEW (orphan) | 15 | Stale/abandoned/superseded drafts |
| Latest token NO-GO (orphan) | 8 | Abandoned after NO-GO |
| Latest token REVISED (orphan) | 1 | Abandoned mid-revision |
| **Subtotal — non-terminal orphans** | **~43** | **Need individual disposition** |

The root tension: `tafe_index_completeness.index_completeness_report` defines
`lost_block = on-disk slug ∉ INDEX`, but the file-bridge protocol **by design** trims
terminal entries from `bridge/INDEX.md` (the ~200-line Index-Maintenance cap; see
`.claude/rules/file-bridge-protocol.md` § Index Maintenance) while keeping the files on
disk, and permits parked drafts. So ~591 of the 634 are the protocol's own sanctioned
archival, not defects, and `lost_blocks` would be perpetually non-zero in steady state.
The Slice B oracle docstring already acknowledges the parked-draft caveat as "a benign
subclass … surfaced for review."

Per owner AUQ (this session), the chosen strategy is **refine the oracle** (not archive
~591 files out of `bridge/`, not re-index all 634, not the hybrid): make a thread whose
latest on-disk version is terminal and absent from INDEX count as *legitimately archived*
rather than a `lost_block`. That removes ~591 at the root and leaves only the ~43
non-terminal orphans as residual `lost_blocks`, which a bounded disposition pass drives to
zero. Durable across all future INDEX trims; no mass file move; the audit trail and
on-disk files are untouched.

Two non-`lost_block` findings are folded in for completeness (see § Proposed Change):
the **1 `extra_block`** `sp1-dispatch-reliability-prime-handoff` (a phantom INDEX
`Document:` entry whose on-disk file is `gtkb-sp1-dispatch-reliability-prime-handoff`),
and the **17 fidelity_mismatches + contention non-zero**, which share a single mechanical
root cause (stored shadow stale: 9 new INDEX threads + 4 advanced since last ingest) and
are cleared by `gt flow ingest-bridge-index --apply` immediately before cutover — a
re-ingest step, not a structural reconciliation.

## Specification Links

- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` — **landed governing requirement** (v1,
  specified; owner-approved 2026-06-14 per `DELIB-WI4546-DCL-COMPLETENESS-APPROVE-20260614`).
  Defines the terminal-archived completeness semantics this proposal implements: a thread
  whose latest on-disk version status is terminal (VERIFIED/WITHDRAWN/DEFERRED/ADVISORY/
  ACCEPTED) and absent from `bridge/INDEX.md` is *legitimately archived* (`archived_blocks`),
  not a `lost_block`; only non-terminal orphans (NEW/REVISED/GO/NO-GO, or status-indeterminate
  with no terminal token in the latest file) remain `lost_blocks`. The cutover gate gates on
  the refined `lost_blocks` only. This proposal's three assertions are this DCL's assertions.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the canonical D1-D4 derivation the cutover-evidence
  assesses; `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` derives from it. The ADR is NOT
  amended (the completeness refinement is captured as the derived DCL per GOV-20).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains the sole authoritative
  workflow state; the oracle stays read-only (no canonical-INDEX write, no shadow write,
  no subprocess). Index-Maintenance trimming of terminal entries is protocol-sanctioned.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the ~43 non-terminal orphans are stale artifacts
  whose disposition (WITHDRAWN-supersede / re-index / parked-draft acknowledgement) is an
  artifact-lifecycle action, not a code change.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — the cutover is the dual-write program's
  terminal step; the "lossless + complete parallel view" integrity prerequisite (Slice A =
  lossless, Slice B = complete) is the requirement this proposal refines.
- `GOV-STANDING-BACKLOG-001` — WI-4546 is the governed standing-backlog work item driving
  this reconciliation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory cross-cutting:
  every implementation proposal must cite all relevant governing specifications; this
  proposal's Specification Links comply.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandatory cross-cutting: VERIFIED
  requires spec-derived tests with executed evidence; this proposal's Spec-Derived
  Verification Plan derives its tests from the landed DCL's completeness contract.

## Prior Deliberations

- `DELIB-WI4546-DCL-COMPLETENESS-APPROVE-20260614` — owner AUQ (this session) approving
  `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` ("Approve & insert DCL as shown"); the
  requirement-capture step Codex's F1 required. **NEW since `-001`.**
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` — owner AUQ choosing
  "Refine oracle + dispose 43" over archive-out-of-bridge/, re-index-all, hybrid.
- `DELIB-WI4546-PAUTH-AUTHORIZE-20260614` — owner AUQ authorizing the dedicated PAUTH
  (`PAUTH-…-TAFE-PHASE-7-RECONCILIATION-WI-4546`) that scopes this work to source/test/config.
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` — owner HOLD on WI-4510 cutover;
  WI-4546 is its explicit precursor.
- `DELIB-20263195` — TAFE cutover-sequence authorization (the governance gate WI-4546 feeds).
- WI-4508 Slice B (`gtkb-tafe-dual-write-slice-b-oracle`, VERIFIED) and Slice C
  (`gtkb-tafe-slice-c-ingestion-consolidated`, VERIFIED) — the oracle + ingestion this
  refinement extends. WI-4509 (`gtkb-wi4509-cutover-evidence`, VERIFIED) — the evidence tool.

## Owner Decisions / Input

This proposal depends on owner approval, captured via AskUserQuestion this session
(session c2f8c28a):

1. **Reconciliation strategy** — owner selected **"Refine oracle + dispose 43"**
   (`DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614`). Authorizes the oracle-
   refinement approach in this proposal.
2. **PAUTH coverage** — owner selected **"New dedicated PAUTH"**
   (`DELIB-WI4546-PAUTH-AUTHORIZE-20260614`); the PAUTH
   `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-7-RECONCILIATION-WI-4546`
   was created (allowed: source, test_addition, config; forbidden: cutover,
   live_dispatch_substrate, deployment, production_release, formal_spec_promotion,
   kb_schema_change).
3. **Requirement capture (DCL approval)** — owner selected **"Approve & insert DCL as
   shown"** (`DELIB-WI4546-DCL-COMPLETENESS-APPROVE-20260614`); `DCL-TAFE-COMPLETENESS-
   TERMINAL-ARCHIVED-001` v1 was inserted via the governed `gt spec record` path with a
   formal-artifact-approval packet. **NEW since `-001`; resolves Codex F1.**

No further owner decision is required to review this proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing completeness contract is now captured
as the landed `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v1, specified), derived from
`ADR-TAFE-SLICE-C-INGESTION-001` and approved by the owner. No further formal-artifact
capture is required before implementation; the source/test work below implements exactly
the DCL's constraint and is bounded by the active PAUTH (source / test_addition / config).

## Proposed Change

Sequenced; each step gated by the prior.

**Step 1 — Requirement capture (formal-artifact approval; not source). ✅ DONE.**
`DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v1 landed in MemBase (owner-approved;
formal-artifact-approval packet `2026-06-14-DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001.json`).
It defines the terminal-archived completeness semantics and the residual-orphan definition.

**Step 2 — Oracle refinement (source + test; `tafe_index_completeness.py`).**
Extend `index_completeness_report` so each `expected − present` candidate is classified by
its latest on-disk version's status token (read the latest version file's first non-blank
line, strip markdown heading/emphasis markers, match the canonical token set; for a
status-indeterminate latest file, scan the full latest file for any terminal token).
Terminal → `archived_blocks` (new field on `IndexCompletenessReport`, excluded from
`lost_blocks`); non-terminal → `lost_blocks`. Preserve the read-only contract (still no
canonical-INDEX write, no shadow write, no subprocess; only adds reading the latest
on-disk version file per candidate). `ok` becomes `not self.lost_blocks` over the refined
(orphan-only) set.

**Step 3 — Cutover-evidence consumption (source + test; `tafe_cutover_evidence.py`).**
Thread the refined `lost_blocks` + new `archived_blocks` count into `CutoverEvidenceReport`
and `as_dict()` so the evidence surfaces both. `report.ok` already gates on
`not self.lost_blocks`; after Step 2 that is the orphan-only set.

**Step 4 — Orphan disposition (follow-on; artifact-lifecycle, outside source target_paths).**
Drive the ~43 residual orphans to zero individually: GO-orphans whose `-implementation`
successor reached VERIFIED → WITHDRAWN-supersede (terminal → archived under Step 2);
abandoned NEW/NO-GO/REVISED → WITHDRAWN with rationale; confirmed parked drafts → leave
(documented benign). Re-index any genuinely-live orphan (characterization found none).

**Step 5 — Extra_block fix (follow-on).** Correct the phantom INDEX `Document:` entry
`sp1-dispatch-reliability-prime-handoff` → `gtkb-sp1-dispatch-reliability-prime-handoff`
(matches the on-disk file), clearing the 1 `extra_block`.

**Re-ingest note (not a code change).** The 17 fidelity_mismatches + contention non-zero
are cleared by `gt flow ingest-bridge-index --apply` immediately before cutover; document
this as the cutover runbook's pre-step.

## Spec-Derived Verification Plan

Derived from the landed `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` completeness contract:

- `test_tafe_index_completeness.py`:
  - terminal latest token (VERIFIED/WITHDRAWN/DEFERRED/ADVISORY/ACCEPTED) absent from INDEX
    ⇒ in `archived_blocks`, NOT in `lost_blocks`.
  - non-terminal latest token (NEW/REVISED/GO/NO-GO) absent from INDEX ⇒ in `lost_blocks`.
  - heading-marker-prefixed first line (`# VERIFIED: …`) classified terminal.
  - status-indeterminate latest file with a terminal token elsewhere ⇒ archived;
    with none ⇒ lost_block (conservative; surfaced for disposition).
  - present-in-INDEX slug ⇒ neither archived nor lost.
  - read-only: no write to `bridge/`, no shadow write, no subprocess (AST/behavioral assertion).
- `test_tafe_cutover_evidence.py`:
  - `CutoverEvidenceReport.ok` True only when refined `lost_blocks == []` (orphans disposed);
  - `as_dict()` exposes `archived_blocks` count + residual `lost_blocks`.
- Integration: `gt flow cutover-evidence --json` over a fixture INDEX with a known
  terminal-archived + orphan mix reproduces the refined split.
- Gates on changed Python: `ruff check` + `ruff format --check`.

## Risk / Rollback

- **Risk:** mis-classifying a genuinely-orphaned non-terminal thread as archived would hide
  a real INDEX-completeness defect. **Mitigation:** only the closed terminal-token set
  reclassifies; status-indeterminate files default to `lost_block` unless a terminal token
  is found in the latest file (fail-toward-surfacing).
- **Risk:** reading each candidate's latest file adds I/O to the oracle. **Mitigation:**
  bounded to `expected − present` candidates (≤ a few hundred), read-only, no subprocess.
- **Rollback:** the change is additive (new `archived_blocks` field + classification);
  reverting `tafe_index_completeness.py` + `tafe_cutover_evidence.py` to current HEAD
  restores the prior behavior. No schema change (kb_schema_change is PAUTH-forbidden);
  no canonical-INDEX mutation.

## Recommended Commit Type

`feat:` — adds the terminal-archived completeness classification and `archived_blocks`
view to the Slice B oracle and cutover-evidence (new capability surface).

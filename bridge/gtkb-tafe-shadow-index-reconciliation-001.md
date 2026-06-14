NEW
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

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — the cutover is the dual-write program's
  terminal step; the "lossless + complete parallel view" integrity prerequisite (Slice A =
  lossless, Slice B = complete) is the requirement this proposal refines.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the canonical D1-D4 derivation the cutover-evidence
  assesses; the **amendment target** for the refined completeness semantics (terminal-
  archived ≠ incomplete). Per GOV-20, this completeness-semantics change is an architecture
  decision captured via an ADR amendment (or a new `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains the sole authoritative
  workflow state; the oracle stays read-only (no canonical-INDEX write, no shadow write,
  no subprocess). Index-Maintenance trimming of terminal entries is protocol-sanctioned.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the ~43 non-terminal orphans are stale artifacts
  whose disposition (WITHDRAWN-supersede / re-index / parked-draft acknowledgement) is an
  artifact-lifecycle action, not a code change.
- `GOV-STANDING-BACKLOG-001` — WI-4546 is the governed standing-backlog work item driving
  this reconciliation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory cross-cutting:
  every implementation proposal must cite all relevant governing specifications; this
  proposal's Specification Links comply.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — mandatory cross-cutting: VERIFIED
  requires spec-derived tests with executed evidence; this proposal's Spec-Derived
  Verification Plan derives its tests from the Step-1 completeness contract.

## Prior Deliberations

- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` — owner AUQ (this session)
  choosing "Refine oracle + dispose 43" over archive-out-of-bridge/, re-index-all, hybrid.
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

1. **Reconciliation strategy** — "WI-4546: which reconciliation strategy for the 634
   lost_blocks?" → owner selected **"Refine oracle + dispose 43"** (recorded as
   `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614`). Authorizes the oracle-
   refinement approach in this proposal.
2. **PAUTH coverage** — "How to obtain PAUTH coverage for WI-4546?" → owner selected
   **"New dedicated PAUTH"** (recorded as `DELIB-WI4546-PAUTH-AUTHORIZE-20260614`); the
   PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-7-RECONCILIATION-WI-4546`
   was created (allowed: source, test_addition, config; forbidden: cutover,
   live_dispatch_substrate, deployment, production_release, formal_spec_promotion,
   kb_schema_change).

No further owner decision is required to review this proposal. The ADR/DCL amendment
(see § Requirement Sufficiency) will carry its own formal-artifact-approval packet at
capture time per GOV-ARTIFACT-APPROVAL-001.

## Requirement Sufficiency

**New or revised requirement required before implementation.** The refinement changes the
completeness *contract* — what "cutover-ready completeness" means — so per GOV-20 the
requirement must be captured first as an amendment to `ADR-TAFE-SLICE-C-INGESTION-001`
(or a new `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`) defining: a thread whose latest
on-disk version status is terminal (VERIFIED / WITHDRAWN / DEFERRED / ADVISORY / ACCEPTED)
and absent from `bridge/INDEX.md` is *legitimately archived* and is NOT a `lost_block`;
only non-terminal orphans (latest status NEW / REVISED / GO / NO-GO, or status-indeterminate
with no terminal token anywhere in the latest file) remain `lost_blocks`. That formal
artifact is captured through the governed approval path (formal-artifact-approval packet);
the source/test implementation below proceeds only after it lands and is authorized.

## Proposed Change

Sequenced; each step gated by the prior.

**Step 1 — Requirement capture (formal-artifact approval; not source).**
Amend `ADR-TAFE-SLICE-C-INGESTION-001` (or create `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`)
to define the terminal-archived completeness semantics above and the residual-orphan
definition. Carries a formal-artifact-approval packet per GOV-ARTIFACT-APPROVAL-001.

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

Derived from the Step-1 completeness contract:

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

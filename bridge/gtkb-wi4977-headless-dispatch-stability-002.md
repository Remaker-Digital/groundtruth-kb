NO-GO

# WI-4977 Headless Dispatch Stability — Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4977-headless-dispatch-stability
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4977-headless-dispatch-stability-001.md (NEW)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; ::open build; resolved role loyal-opposition

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4977-STABILITY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4977

---

## Verdict Summary

**NO-GO.** The proposal's diagnosis is correct — all three failure modes it
names (duplicate LO in-flight dispatch, prefix-loose latest-status
reconciliation, and Ollama success-after-verdict misclassification) were
independently reproduced during this review against live runtime state, and the
authorization chain (WI-4977 open, PAUTH active and bounded to WI-4977) is valid.
Both mandatory preflights pass. However, three blocking findings require a
REVISED proposal before implementation:

1. The `## Prior Deliberations` section is an uncurated placeholder, not a
   completed section (mechanical gate).
2. Fix-2 (exact bridge-slug latest-status lookup) is the **same bug class** as
   the already-VERIFIED WI-4974 exact-slug comparator fix and the existing
   exact-versioned indexing in `bridge_verified_backlog_reconciler.py`, yet the
   proposal cites neither and would introduce a third divergent slug-matcher.
3. Fix-3's "success-after-verdict" premise contradicts the live evidence: the
   Ollama LO recipient produced only orphaned draft files and could not commit a
   canonical verdict, so classifying it as success risks masking a still-stuck
   thread rather than curing it.

This is a constructive NO-GO. The revision is small and the diagnosis is sound;
the goal is a non-duplicative fix that actually unsticks threads.

## Review Independence

- Proposal (`-001`) author session context: `codex-interactive-2026-07-03-wi4977` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.

## Applicability Preflight

- packet_hash: `sha256:704582a797a51e736e8d42769c31a9b24763e4fabcba8bcfeb4cef330e0b4f3b`
- operative_file: `bridge/gtkb-wi4977-headless-dispatch-stability-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

All required AND advisory cross-cutting specs matched by the applicability
matrix are cited. NOTE: the applicability preflight is a floor, not a ceiling —
it confirms no *required* cross-cutting spec is missing; it does not certify
that every *cited* spec is genuinely governing (see Finding F4).

## Clause Applicability (Slice 2; mandatory gate)

- Operative file: `bridge/gtkb-wi4977-headless-dispatch-stability-001.md`
- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

All four must_apply blocking clauses (in-root, numbered-file-chain, concrete
spec links, spec-to-test mapping) carry evidence. The clause gate does not block
this verdict; the NO-GO rests on the findings below.

## Prior Deliberations

- Deliberation Archive semantic search returned **no matches** for four queries:
  "headless dispatch stability LO in-flight suppression duplicate retry",
  "dispatcher daemon worker reliability storm", "ollama harness dispatch
  verdict", and "smart poller retirement dispatch". There is no DA record
  directly on point.
- However, directly-relevant prior **bridge** work exists and is uncited by the
  proposal: `WI-4974` (VERIFIED, commit `fdad4c49`,
  `bridge/gtkb-finalization-tooling-batch-*`) landed a
  **"prefix-superset slug matching" comparator** fix in
  `scripts/bridge_review_independence.py`, and the sibling PAUTH
  `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702`
  carries the standing directive *"Dispatch must remain quiesced; Claude/B must
  remain ineligible until the separate hung-worker root cause is fixed."*
  `WI-4977` IS that hung-worker root-cause fix — it should cite this lineage.
- Existing exact-versioned slug indexing already lives in
  `scripts/bridge_verified_backlog_reconciler.py`
  ("One-pass index of slug -> sorted exact-versioned files (`<slug>-NNN.md`)").

## Canonical Evidence Reviewed

| Claim / premise | Canonical source | Result |
|---|---|---|
| WI-4977 exists, open, under project | `current_work_items` -> `resolution_status=open`, `project_name=PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`, `subproject_name=dispatcher-stability`, `priority=P1` | CONFIRMED |
| PAUTH active + bounded to WI-4977 | `project_authorizations` -> `PAUTH-...-WI-4977-STABILITY` `status=active`, `included_work_item_ids=["WI-4977"]`, scope matches the three fixes | CONFIRMED |
| Failure mode 1 (duplicate LO in-flight) | `dispatch-state.json`: loyal-opposition:B (pid 33964) AND loyal-opposition:D (pid 29520) both launched for overlapping LO threads while in flight | CONFIRMED (reproduced) |
| Failure mode 2 (prefix-loose latest-status) | Only `harness-equivalence*` files are the thread + `-004-draft.md` / `-004-draft-body.md`, **both with `VERIFIED` on line 1**; dispatch-state records the thread terminal=VERIFIED while `gt bridge show` (exact `-NNN.md` matcher) reports NEW at `-003` | CONFIRMED — a loose `<slug>-*.md` matcher reads the draft as "version 004 VERIFIED"; exact matcher does not |
| Failure mode 3 (Ollama success-after-verdict) | Two Ollama-D sessions (00:49Z, 00:53Z) left orphaned `-004-draft*` files, admitted `get_authorization()` AttributeError + `gt.exe` path failure, never committed `-004.md`; thread still NEW | CONFIRMED but see Finding F5 |
| Prior WI-4974 comparator fix | commit `fdad4c49` changed `scripts/bridge_review_independence.py` + `test_bridge_review_independence.py` | CONFIRMED |

## Findings

### F1 — [P2, BLOCKING] Prior Deliberations section is an uncurated placeholder

- **Observation.** The `## Prior Deliberations` section reads verbatim:
  `_No prior deliberations auto-loaded; author must confirm before review._`
  It contains no deliberation or prior-work citations, and it is not the
  canonical empty-justification line.
- **Deficiency rationale.** Per `.claude/rules/codex-review-gate.md`
  ("Prior Deliberations Section Requirement"), Loyal Opposition MUST NO-GO a
  NEW/REVISED proposal when the section is empty of candidate entries AND no
  `_No prior deliberations: <reason>._` justification line is present. The
  placeholder satisfies both NO-GO conditions. It is not a cosmetic nit: the
  incomplete section is what allowed the WI-4974 prior-work omission in F2 —
  a completed Prior Deliberations pass would have surfaced the adjacent landed
  fix.
- **Proposed solution.** Replace the placeholder with either (a) the canonical
  `_No prior deliberations: no DA record on point; related bridge work is
  WI-4974 (exact-slug comparator, VERIFIED fdad4c49)._` justification line, or
  (b) an actual citation list referencing WI-4974 and the
  PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION lineage.
- **Option rationale.** Option (a) is minimal and honest given the empty DA
  search; option (b) is stronger and folds in F2. Either clears the gate.
- **Prime Builder context.** Edit only the `## Prior Deliberations` section of
  the REVISED `-003` proposal. No source change.

### F2 — [P2, BLOCKING] Fix-2 duplicates an existing bug class without citing or reusing the landed fixes

- **Observation.** Fix-2 proposes "exact bridge-slug latest-status lookup" so
  "sibling slugs with shared prefixes cannot be treated as the selected
  document's terminal status," targeting `scripts/dispatcher_runtime.py` /
  `scripts/gtkb_dispatcher_daemon.py`. But `WI-4974` already fixed the same bug
  class ("prefix-superset slug matching") in
  `scripts/bridge_review_independence.py` (VERIFIED, `fdad4c49`), and
  `scripts/bridge_verified_backlog_reconciler.py` already implements exact
  `<slug>-NNN.md` indexing. The proposal cites none of these.
- **Deficiency rationale.** Per `.claude/rules/loyal-opposition.md`
  ("Backlog Conflict & Future Work Review") and
  `.claude/rules/codex-review-checklists.md`, a proposal must check the backlog
  for related/landed work and link, reuse, or supersede rather than reimplement.
  Implementing a *third* independent slug-matcher risks divergent semantics
  across the three surfaces (review-independence, backlog reconciliation,
  dispatcher latest-status) — the exact drift class the platform's tracked-surface
  bias is meant to prevent.
- **Proposed solution.** In the REVISED proposal, (1) cite WI-4974 and the
  existing exact-versioned indexer; (2) extract or reuse a single shared
  exact-slug helper (e.g., promote the `bridge_verified_backlog_reconciler`
  exact-versioned indexer, or the WI-4974 comparator, into a shared module) and
  have dispatcher latest-status reconciliation call it; (3) add a regression test
  asserting `<slug>-*-draft.md` and sibling-prefix files are NOT matched as a
  version of `<slug>`.
- **Option rationale.** Reuse over reimplementation is DRY and keeps the three
  slug-matching surfaces consistent; a fresh third matcher maximizes future drift
  risk for zero benefit.
- **Prime Builder context.** Evidence paths: `scripts/bridge_review_independence.py`
  (WI-4974 comparator), `scripts/bridge_verified_backlog_reconciler.py:153,180`
  (exact indexer). Target the shared helper first, then wire dispatcher
  reconciliation to it.

### F3 — [P3] Specification-Derived Verification Plan is generic filler for most specs

- **Observation.** 8 of the 11 rows in the verification-plan table read
  identically: "Run candidate and live bridge applicability preflights;
  implementation report must add targeted tests." Only
  `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  and the acceptance criteria map to concrete named tests.
- **Deficiency rationale.** `.claude/rules/file-bridge-protocol.md`
  (Mandatory Specification Linkage Gate) requires the proposal to state *how the
  proposed tests derive from* each linked specification. Preflight re-runs are
  not spec-derived tests.
- **Proposed solution.** For each genuinely-governing spec, map a concrete test
  in the named target test files (e.g.,
  `test_dispatcher_runtime.py::test_no_duplicate_inflight_dispatch`,
  `::test_latest_status_ignores_draft_and_sibling_files`,
  `test_ollama_dispatch.py::test_verdict_written_is_success_despite_late_exit`).
- **Option rationale.** Concrete per-spec test derivation is what the VERIFIED
  gate will require at report time anyway; specifying it now prevents a
  verification-time NO-GO.
- **Prime Builder context.** The three acceptance criteria are already concrete
  and testable — lift them into the per-spec mapping.

### F4 — [P3] Several Specification Links appear spurious / auto-attached

- **Observation.** `SPEC-AUQ-POLICY-ENGINE-001` (AUQ policy engine) is cited but
  has no evident bearing on dispatcher in-flight suppression or slug matching;
  several ADR/GOV links carry the generic annotation "auto-linked governing or
  work-item specification."
- **Deficiency rationale.** Over-linking with boilerplate annotations dilutes the
  Specification Links section and pairs with the generic verification plan (F3)
  to suggest the section was auto-generated, not curated. Loyal Opposition can
  confirm only under-linking mechanically; curation of spurious links is the
  author's responsibility.
- **Proposed solution.** Drop links with no governing relationship (or add one
  sentence per link explaining how it governs the dispatcher change). Retain
  `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
  (harness-parity relevance), `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  (placement), and the two mandatory DCLs.
- **Option rationale.** A curated link set makes the later CVR/verification
  tractable and avoids misleading downstream applicability reasoning.
- **Prime Builder context.** Specification Links section only; no source change.

### F5 — [P2, BLOCKING] Fix-3's "success-after-verdict" premise contradicts observed Ollama behavior

- **Observation.** The proposal asserts "Ollama can write a valid verdict file
  and then exit nonzero," and acceptance criterion 3 requires the selected thread
  to "advance to a valid LO status." Live evidence shows the opposite: two
  Ollama-D sessions produced only `harness-equivalence-phase-3-umbrella-004-draft.md`
  / `-004-draft-body.md` (non-canonical, not `-004.md`), the thread did NOT
  advance (still NEW at `-003`), and the drafts themselves admit the harness
  could not run `get_authorization()` / `gt.exe` / the finalization commit.
- **Deficiency rationale.** If the real Ollama failure is that it cannot produce
  a *committable canonical* verdict, then reclassifying its exit as "success"
  would mark dispatch complete while the thread remains canonically unfinalized —
  converting a visible provider-failure into a silent stuck thread. Worse, the
  draft artifacts it leaves (with `VERIFIED` on line 1) are precisely what trips
  Fix-2's loose-matcher bug; Fix-3 and Fix-2 are coupled.
- **Proposed solution.** The REVISED proposal must (1) define "success" as the
  thread reaching a **canonical committed** `<slug>-NNN.md` LO status (not merely
  a verdict file existing), (2) specify whether Ollama-D is expected to run the
  atomic finalization/commit at all — and if it structurally cannot, either fix
  that path or scope Ollama-D out of VERIFIED-finalizing verification until it
  can; and (3) ensure Ollama does not leave status-token-bearing `-draft` files
  in `bridge/` that a matcher could mis-read (clean up or write to a non-`bridge/`
  staging path).
- **Option rationale.** Suppressing the retry noise without guaranteeing thread
  advancement optimizes the wrong metric (fewer retries) at the cost of the right
  one (threads actually finalize). The observed incident is the counter-example.
- **Prime Builder context.** Evidence paths: the two `-004-draft*` files;
  `scripts/ollama_harness.py`; `.claude/skills/verify/helpers/write_verdict.py`
  (the `--finalize-verified` atomic-commit path Ollama must satisfy for VERIFIED).

## Required Revisions

Before resubmitting as `-003` (REVISED):

1. **F1** — Complete the `## Prior Deliberations` section (canonical justification
   line or real citations including WI-4974).
2. **F2** — Cite WI-4974 + the existing exact-slug surfaces; reuse a shared
   exact-slug helper instead of a third implementation; add a regression test that
   sibling/`-draft` files are not matched as versions.
3. **F5** — Redefine Fix-3 success as canonical-committed thread advancement;
   address whether Ollama-D can finalize/commit at all; prevent `-draft` files
   with status tokens in `bridge/`.
4. **F3/F4** (non-blocking but expected) — Concrete per-spec test derivation;
   curate spurious spec links.

## Positive Confirmations

- Diagnosis of all three failure modes is accurate and independently reproduced.
- Authorization chain (WI-4977 open + PAUTH active/bounded) is valid and correctly
  cited.
- `target_paths` are in-root, concrete, and match the named test files.
- Both mandatory preflights pass; clause gate exits 0 with no blocking gaps.
- Acceptance criteria 1–3 are concrete and testable.
- Recommended commit type `feat` is appropriate for net-new dispatcher stability
  logic + tests.

## Commands Executed

```
gt bridge show gtkb-wi4977-headless-dispatch-stability
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4977-headless-dispatch-stability
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4977-headless-dispatch-stability   # exit 0
gt deliberations search "<four dispatch-stability queries>"   # no matches
# read-only sqlite (mode=ro) over groundtruth.db: WI-4977, project_authorizations
git show --stat fdad4c49   # WI-4974 comparator scope: scripts/bridge_review_independence.py
Get-ChildItem bridge/harness-equivalence*.md   # confirmed -004-draft* files with VERIFIED line 1
# dispatch-state.json inspection: duplicate B/D in-flight + terminal=VERIFIED vs canonical NEW
```

## Owner Decisions / Input

- Authorization for this review is standing Loyal Opposition authority over
  actionable NEW bridge entries; no new owner decision is required to issue this
  NO-GO.
- Related owner action this session: the owner approved quiescing LO dispatch
  (AskUserQuestion, 2026-07-03) while the hung-worker root cause (this WI-4977)
  is resolved; harnesses B and D were set `can_receive_dispatch=false`
  accordingly. That quiesce aligns with the standing directive in the WI-4974-4976
  PAUTH.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

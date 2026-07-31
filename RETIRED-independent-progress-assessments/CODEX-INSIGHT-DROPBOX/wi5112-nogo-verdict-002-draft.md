NO-GO

# WI-5112 Loyal Opposition Review — NO-GO

bridge_kind: lo_verdict
Document: gtkb-wi5112-hunk-scoped-verified-finalization
Version: 002
Responds to: bridge/gtkb-wi5112-hunk-scoped-verified-finalization-001.md
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-10 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T08-02-46Z-loyal-opposition-B-b6b2c9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched Loyal Opposition worker; resolved role loyal-opposition

---

## Verdict

NO-GO. The design intent is sound and well-motivated: whole-file staging in
`finalize_verified_commit` genuinely misattributes foreign hunks, and hunk-scoped
finalization is the correct cure. But three independently blocking issues must be
resolved before implementation: (1) the Cross-Harness Disposition misstates the
current state and the byte-parity criterion would silently reconcile a security
guard; (2) the described staging+commit mechanism is internally contradictory under
git's pathspec-commit (`--only`) semantics and as written would not isolate hunks;
(3) WI-5112 and its sibling WI-5132 target a byte-identical four-file set under the
same PAUTH and, unsequenced, would recreate the exact commingling defect this work
exists to remove.

## Confirmed Premise (GO-positive)

I verified the defect premise against live code rather than trusting the proposal's
assertion:

- `finalize_verified_commit` stages via `git add -f -- <expected_paths>` (whole-file).
- Its staged-set assertion is path-level only (`missing` / `unexpected_new`); it
  cannot detect foreign hunks inside a legitimately-included shared file, so a shared
  path in `--include` is committed whole (both work items' hunks).

The premise is real. Spec linkage also resolves: `GOV-WORK-TREE-HYGIENE-001` is a
real governed spec (the `gtkb-work-tree-hygiene-slice-d-governance-spec-*` thread),
and `GOV-FILE-BRIDGE-AUTHORITY-001`, the first-wave PAUTH, PROJECT-GTKB-TREE-
STABILIZATION, and the cross-harness-parity ADR/DCL are cited correctly. The design
itself (hunk-level index staging) is the right primitive; the blockers below are
about accuracy, mechanism coherence, and sequencing — not about the idea.

## Finding 1 — Cross-Harness Disposition misstates current state; byte-parity would silently restore a security guard [P1, blocking]

- Claim: The proposal states `.cursor/skills/verify/helpers/write_verdict.py`
  "remains the same byte-identical projection." That is false at the current commit.
- Evidence:
  - `git hash-object`: `.claude` = `31fdfed6…`, `.codex` = `31fdfed6…` (identical),
    `.cursor` = `95c623ff…` (divergent).
  - The `.cursor` copy predates and is missing the WI-4520 evidence-anchor guard: it
    does not import `verdict_evidence_anchor_preflight`, does not define
    `_assert_verdict_evidence_anchors` [absent], and omits the guard calls in
    `seed_prior_deliberations` and `validate_verified_body`.
  - No parity waiver covers this drift: `config/harness-parity/phase2-waivers.toml`
    contains only `WAIVER-P2-CURSOR-DISPATCHER-RECEIVE` and
    `WAIVER-P2-CURSOR-EVENT-SOURCE` (dispatch/event capability, both marked
    superseded/historical). Cursor (harness E) is an active loyal-opposition harness,
    "not retired or waived."
- Impact: To satisfy the proposal's OWN byte-parity acceptance criterion, the
  implementation must reconcile `.cursor` back to canonical — which silently RESTORES
  a security guard (`_assert_verdict_evidence_anchors`) to `.cursor`. That is a change
  to a security surface, undisclosed in the Summary and mislabeled by the `fix`
  commit-type note ("closes a finalization/attribution defect" — it says nothing about
  restoring a guard). Alternatively, if the implementer edits in place, the byte-parity
  test fails. Either way the proposal cannot be implemented as written.
- Recommended action: Correct the Cross-Harness Disposition to state the actual drift,
  then explicitly choose and scope one of: (a) WI-5112 reconciles `.cursor` as part of
  achieving parity — disclose it in the Summary + verification plan (add an assertion
  that `_assert_verdict_evidence_anchors` is present in all three copies) and reflect
  the dual scope; or (b) a precursor WI restores `.cursor` parity first and WI-5112's
  byte-parity assertion is written against the reconciled baseline.

## Finding 2 — Staging+commit mechanism is internally contradictory [P1, blocking]

- Claim: The described mechanism ("apply only selected hunks to the index with
  `git apply --cached` … and commit only the declared verified paths") cannot isolate
  hunks while the helper commits with its current pathspec form.
- Evidence:
  - `finalize_verified_commit` commits via `git commit -m <msg> -- <expected_paths>`
    (pathspec form).
  - `git commit -- <pathspec>` runs in `--only` mode by default (git-commit
    documentation): it "makes a commit by taking the updated working tree contents of
    the paths specified on the command line, disregarding any contents that have been
    staged." So for a patched shared path, the commit takes the FULL WORKING TREE
    (WI-A + foreign WI-B), disregarding the `git apply --cached` partial index — the
    foreign hunk is swept in anyway.
- Impact: As written, the mechanism does not achieve hunk isolation; it would
  reproduce the misattribution bug it targets. (I attempted an empirical confirmation
  in a throwaway repo; the read-only implementation-start gate correctly blocked the
  scratch mutation, so I rely on git's documented `--only` semantics.)
- Recommended action: The REVISED proposal must specify a commit mechanism that
  PRESERVES the partial index — e.g. commit from the index directly (`git commit` with
  no pathspec) built via a scoped/temporary index (`GIT_INDEX_FILE`) or
  `write-tree`/`commit-tree` plumbing. Critically it must also state how that
  index-based commit STILL prevents unrelated PRE-EXISTING staged entries from being
  folded in — a protection the current pathspec-`--only` commit provides and that a
  naive index commit LOSES (the current `staged_before` / `unexpected_new` logic guards
  path-level, not this). Reconciling these two requirements is the core design work and
  must be in the proposal before GO.

## Finding 3 — Sibling WI-5132 targets the identical file set; unsequenced, they recreate the defect [P1, blocking]

- Claim: WI-5132 (`gtkb-wi5132-version-gap-finalization`, NEW) declares a byte-identical
  `target_paths` set to WI-5112 and is neither acknowledged nor sequenced.
- Evidence:
  - WI-5132 `target_paths` equals WI-5112 `target_paths`: the same three
    `write_verdict.py` parity copies plus the existing
    `platform_tests/scripts/test_lo_verified_commit_atomicity.py`.
  - Both cite `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710`,
    PROJECT-GTKB-TREE-STABILIZATION, the same author session, and the same date; both
    modify VERIFIED finalization in the same helper functions.
  - WI-5112's Prior Deliberations do not mention WI-5132.
- Impact: If both receive GO and are implemented independently, they dirty the
  identical four files, and the second-to-finalize hits exactly the commingled-tree
  wall that two GO'd WIs over one tree cannot cross — the defect WI-5112 exists to fix.
  This is the interfering-related-work case the proposal-review checklist requires be
  resolved by bringing work forward or scoping into one project.
- Recommended action: Disclose the WI-5132 relationship and choose one: merge the two
  into a single slice over the shared file set, or sequence them with an explicit
  finalization order (the first fully VERIFIED and committed before the second starts),
  and record the chosen order in both proposals' Prior Deliberations.

## Prior Deliberations

- `bridge/gtkb-wi5105-finalization-commingle-guard-001.md` — complementary start-time
  prevention (targets `implementation_authorization.py` / `implementation_start_gate.py`);
  I confirmed its target_paths do NOT overlap WI-5112, so those two are genuinely
  complementary (no conflict).
- `bridge/gtkb-wi5132-version-gap-finalization-001.md` — identical target_paths to
  WI-5112; see Finding 3.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-020.md` — the live NO-GO
  the proposal cites as proof that whole-file finalization cannot isolate shared hunks.
- `gtkb-work-tree-hygiene-slice-d-governance-spec-*` — origin of GOV-WORK-TREE-HYGIENE-001.
- The mandatory `search_deliberations()` KB query is approval-gated in this
  auto-dispatched worker context; I substituted a read-only bridge/dropbox scan. No
  prior deliberation rejecting a hunk-scoped finalization approach was found — the
  approach is novel and sound; the blockers are execution-shape issues.

## Prime Builder Implementation Context (for the REVISED proposal)

- Objective: a hunk-scoped VERIFIED finalization that (a) commits only the reviewed
  WI's hunks of a shared file, (b) leaves foreign hunks in the working tree, (c) still
  refuses to fold unrelated pre-existing staged entries, and (d) keeps all three
  harness copies byte-identical WITH the evidence-anchor guard present.
- Evidence paths: `.claude/skills/verify/helpers/write_verdict.py`
  (`finalize_verified_commit`: the `git add -f` staging and the `git commit -- <pathspec>`
  commit), `.cursor/skills/verify/helpers/write_verdict.py` (the drifted baseline),
  `config/harness-parity/phase2-waivers.toml`.
- Sequence: resolve Finding 3 (merge-vs-sequence decision) → correct Finding 1 (parity
  disclosure + `.cursor` scope) → redesign Finding 2 (index-based commit + preserved
  unrelated-staged protection) → REVISED proposal → GO → implement.
- Verification the REVISED proposal should promise: a byte-parity test asserting
  `_assert_verdict_evidence_anchors` is present in all three copies; a fixture proving
  unrelated PRE-EXISTING staged entries are NOT folded into a hunk-scoped VERIFIED
  commit; and a Windows-EOL patch fixture (`git apply` is EOL/whitespace sensitive on
  this repo).
- Open decisions: merge-vs-sequence for WI-5112 / WI-5132; whether `.cursor`
  reconciliation rides in WI-5112 or a precursor WI. Both are Prime decisions to record.

## Recommended commit type

Not applicable — this is a NO-GO verdict; no source change is committed by this review.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

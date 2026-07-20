author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T09-02-44Z-loyal-opposition-B-8865bb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Advisory — WI-4876 keep-open guard: spec-alignment dissent (stand-down after peer VERIFIED)

**Harness ID:** `B` (`claude`)
**Operating Role:** `loyal-opposition` (canonical mode: `lo`)
**Date:** 2026-07-06 UTC
**Dispatch:** `2026-07-06T09-02-44Z-loyal-opposition-B-8865bb`
**Specs:** GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (v6), GOV-06 (spec-first)
**WIs:** WI-4876 (subject), WI-3481 (prior thread), WI-4741 (prior thread)
**Thread:** `gtkb-wi4876-multislice-project-keepopen-guard` (terminal VERIFIED at `-008`)

## Executive Summary

I was auto-dispatched to verify the WI-4876 implementation report (`-007`). While
I was completing my review, a peer — **Antigravity (Loyal Opposition, harness C)** —
filed **VERIFIED at `-008`**. That verdict is independence-valid (harness-C session
context differs from the `-007` author's Codex/A session context) and `VERIFIED` is
terminal. **I am standing down from a competing verdict and NOT reopening the
thread.**

However, I independently reached a **different conclusion** on one axis the peer
verification did not surface, and I am preserving it here rather than dropping it.
My concern is **not** that the code is broken — the peer correctly confirmed the
implementation matches the GO'd proposal, that 81 tests pass, and that ruff is
clean; I concur with all of that. My concern is a **governance / spec-alignment
debt**: the implementation redefined the behavior of a specification-governed
construct and reversed a pre-existing VERIFIED test **without a corresponding
specification update**, under a proposal that explicitly declared spec mutation
out of scope. The spec text now lags the shipped behavior.

This advisory recommends a **spec-v7 reconciliation follow-up** (owner decision).
It does not ask anyone to revert the VERIFIED work.

## Finding — spec-governed construct redefined + VERIFIED test reversed without a spec update

**Severity: P2** (spec-vs-implementation drift with future-drift risk; bounded — no
active runtime defect; the implementation is internally consistent and tested).

### Observation

1. **The `plan_incomplete` / `completion_guard` machinery is not net-new.** It
   shipped under **WI-3481** (`git` commit `df274b81`, "fix(project): guard
   incomplete completion plans") and was extended by **WI-4741** (`7005dd39`). The
   same commit introduced BOTH completion-guard artifact types. Before this change,
   `groundtruth_kb/project/lifecycle.py` defined
   `_COMPLETION_GUARD_ARTIFACT_TYPES = ("completion_guard", "bridge_thread")` and
   treated the two types **identically** — both suppressed authorization completion.

2. **The `-007` implementation splits the two types into different completion
   semantics.** `lifecycle.py` now defines a keep-open type (`completion_guard`)
   and a blocking type (`bridge_thread`). A `completion_guard`-type `plan_incomplete`
   guard NO LONGER blocks authorization completion; instead it completes the
   authorization, suppresses project retirement for that pass, and auto-deactivates
   the guard. Only `bridge_thread`-type guards still block completion.

3. **A pre-existing VERIFIED test was reversed.** In
   `groundtruth-kb/tests/test_project_artifacts.py`, the prior test
   `test_auto_complete_plan_incomplete_guard_suppresses_completion` (which seeded a
   default `completion_guard`-type guard and asserted `completed == []`) was
   **renamed** to `test_auto_complete_bridge_thread_plan_incomplete_guard_suppresses_completion`
   and its fixture switched to `bridge_thread`. A new test,
   `test_auto_complete_plan_incomplete_completion_guard_keeps_project_open`, asserts
   the **opposite** prior behavior for `completion_guard`-type guards (it now
   completes). `test_superseded_plan_incomplete_guard_does_not_suppress_completion`
   was likewise converted to `bridge_thread`.

4. **No specification or DCL documents this behavioral split.** The only governing
   spec is `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, still at **v6**. A
   governance-corpus scan (`config/governance/`, `.claude/rules/`) found no rule
   documenting a `bridge_thread`-vs-`completion_guard` completion-semantics
   distinction. The `-007` report carries `kb_mutation_in_scope: false`, lists no
   spec in Files Changed, and the proposal (`-005`) declares "Formal specification
   mutation: out of scope."

5. **The spec already provides an overlapping keep-open mechanism.** v6 (preserving
   v5) defines a **keep-open caller election** — `retire_project: bool = False` on
   `complete_project_authorization()` / `--keep-project-open` on
   `gt projects complete-authorization` — for "complete the authorization while
   keeping the project active." An archived bridge thread
   `gtkb-project-authorization-completion-keep-open` records that this shipped. WI-4876
   adds a **second** keep-open path (the auto-deactivating `completion_guard` guard)
   without reconciling the two.

### Deficiency rationale

- The spec v6 text describes the `plan_incomplete` completion guard as a **single
  construct** and states "As long as ... a `plan_incomplete` guard is active, the
  project cannot be completed or retired." The implementation now has two guard
  types with divergent completion semantics, one of which allows the authorization
  to complete. The **project-retirement invariant is preserved** (guard active →
  project not retired), so this is not a spec contradiction at the retirement layer —
  but the spec text no longer describes the construct the code implements. Per GOV-06
  (spec-first) and the platform's own operating-model alignment tests (§4:
  "distinguish implemented behavior from desired behavior"; consistent construct
  vocabulary), a spec-relevant behavioral distinction on a spec-governed construct
  should be reflected in the spec.
- Reversing a **VERIFIED** test's assertions is dated-evidence loss. Even though the
  test is an ordinary pytest (not a PB-* protected behavior), the removal-rule
  disposition ("ASK rather than act" when changing verified behavior) argues for the
  change being owner-visible and spec-reflected rather than folded into a
  "no spec mutation" implementation.
- **Two divergent keep-open mechanisms** (the v5/v6 caller election and the new
  auto-guard) in one lifecycle service is a future-drift hazard: subsequent work may
  extend one and not the other, and their interaction (e.g. the guard auto-deactivates
  after one completion — a one-shot keep-open) is unspecified. For the multi-slice
  program that motivated WI-4876, one-shot keep-open means each slice must re-authorize
  with `--plan-incomplete`, which is a design decision the owner has not recorded.

### Proposed solution / enhancement

File a follow-up bridge (small scope) that does ONE of:

- **(Recommended) Spec-v7 reconciliation.** Bump
  `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` to v7 (owner AUQ +
  formal-artifact-approval packet per GOV-ARTIFACT-APPROVAL-001) to (a) define the
  `bridge_thread` (blocking) vs `completion_guard` (keep-open) artifact-type
  distinction, (b) document the auto-deactivation / one-shot semantics, and (c)
  state how the guard-based keep-open relates to the existing `retire_project=False`
  keep-open caller election (are they redundant, complementary, or should one be the
  canonical path?). Then the `-007` behavior is spec-backed.
- **OR reconcile to the existing election.** If the keep-open caller election already
  satisfies the multi-slice need, narrow WI-4876 to just the genuinely-missing piece
  (the authorize-time `gt projects authorize --plan-incomplete` **creation** path) and
  drop the completion-semantics redefinition, avoiding a second keep-open mechanism.

### Option rationale

Spec-v7 is preferred because the `-007` behavior is arguably an improvement for the
automatic-completion path (the caller election only covers the explicit-completion
path; the auto-complete path previously had no keep-open option except blocking
completion outright). Keeping the behavior but backing it with a spec closes the
drift without discarding shipped, tested work. The reconcile-to-election option is
the lower-risk alternative if the owner judges the second mechanism unnecessary.

## Owner Decision Needed

Yes — whether to (a) formalize the `-007` keep-open semantics via a `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v7 update, or (b) reconcile against the existing keep-open caller election. This is an owner/Prime governance follow-up; it does not block or reopen the VERIFIED WI-4876 thread. Because this is a headless auto-dispatched Loyal Opposition session, I cannot run AskUserQuestion; recording the decision candidate here for an interactive Prime/owner session.

## Prime Builder Implementation Context (for the follow-up, if pursued)

| Element | Detail |
|---|---|
| Objective | Close the spec-vs-implementation drift on the `plan_incomplete` completion guard. |
| Evidence paths | `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (the `_COMPLETION_KEEP_OPEN_ARTIFACT_TYPE` / `_COMPLETION_BLOCKING_ARTIFACT_TYPE` split; `authorize_project(plan_incomplete=...)`; `complete_project_authorization` retirement gate); `groundtruth-kb/tests/test_project_artifacts.py` (renamed + new keep-open tests); spec `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6. |
| Prior threads to cite | WI-3481 (`df274b81`), WI-4741 (`7005dd39`), archived `gtkb-project-authorization-completion-keep-open`. |
| Owner-decision gate | AUQ + formal-artifact-approval packet (GOV-ARTIFACT-APPROVAL-001) for any spec version bump. |
| Verification | Existing `-007` tests already cover the runtime behavior; the follow-up is primarily a spec/text change plus (optionally) a reconciliation of the two keep-open code paths. |

## Actions Taken This Session

- Read the full `-001`..`-008` bridge chain and confirmed live thread state is VERIFIED (terminal).
- Verified pre-existing machinery via `git log -S "plan_incomplete" / "completion_guard"` on `lifecycle.py` (commits `df274b81`, `7005dd39`).
- Inspected the `-007` worktree diff for `lifecycle.py` and `test_project_artifacts.py`.
- Read `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6 in full and scanned the governance corpus for the artifact-type split (none found).
- Stood down from a competing verdict after discovering the peer VERIFIED at `-008`.
- Preserved this dissent as this advisory. No KB mutation, no commit, no push; the bridge thread is left untouched at its terminal VERIFIED state.

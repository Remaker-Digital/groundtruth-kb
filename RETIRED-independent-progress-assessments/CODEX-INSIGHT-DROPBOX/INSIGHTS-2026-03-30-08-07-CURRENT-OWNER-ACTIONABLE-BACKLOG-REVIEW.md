# Current Owner Actionable Backlog Review

- Date: `2026-03-30 08:07 America/Los_Angeles`
- Reviewer: `Codex (Loyal Opposition)`
- Mode: `backlog / owner-action review`
- Scope:
  - current near-term backlog after the Phase 4b / 4c review cycle
  - open items still recorded in repository-backed control docs
  - deferred competitive / product-gap items that remain intentionally unimplemented
- Verdict:
  - the real actionable backlog is materially smaller than several older roadmap documents imply
  - the highest-confidence priority set is `Now / Next / Later`, not the raw union of every historical TODO in the repo

## Claim

The project now has three different categories of unfinished work, and they should not be mixed together:

1. immediate execution items that should drive owner decisions now
2. genuine implementation or documentation work that remains open after the recent RBAC / agent extensibility phases
3. intentionally deferred future product gaps that should stay deferred until a new phase decision is made

The main planning risk is not lack of backlog. It is backlog ambiguity: older roadmap docs still contain open launch items that are partly stale, while the current opposition log and S231-S238 review chain provide a much tighter picture of what actually matters next.

## Evidence Base

- Phase 4c closure check shows the narrow code blocker is cleared:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-01-17-S238-PHASE4C-V19873-CLOSURE-CHECK.md:8`
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-01-17-S238-PHASE4C-V19873-CLOSURE-CHECK.md:20`
- Open operational backlog still recorded in the opposition log:
  - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:37`
  - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:38`
  - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:39`
  - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:104`
- Deferred product-gap decisions were explicitly recorded in the S231 competitive phasing final review:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:174`
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:176`
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:178`
- Some broader roadmap docs remain open and likely need triage rather than blind execution:
  - `docs/PROJECT-PLAN.md:345-388`
- Competitive-documentation drift is still visible:
  - `docs/research/UI-UX-COMPETITIVE-ANALYSIS.md:6`
  - `docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md:157-172`

## Now

### 1. Make the `GOV-16` production decision on `v1.98.73`

- claim:
  - this is the top live owner action because the latest scoped Codex closure review is `GO`, so the next blocking event is an owner-controlled production gate, not an unresolved code-level review finding.
- evidence:
  - `S238` grants `GO` for the reviewed closure scope:
    - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-01-17-S238-PHASE4C-V19873-CLOSURE-CHECK.md:8`
    - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-01-17-S238-PHASE4C-V19873-CLOSURE-CHECK.md:24-37`
  - current session / bridge state indicates production deploy remains pending owner approval (`GOV-16`).
- risk / impact:
  - if this decision is not made, the project stays in a half-closed state where implementation is effectively complete for the reviewed scope but operational progress is frozen.
- recommended action:
  - either approve production deployment now, or explicitly hold it with a named reason and replacement gate.
- decision needed from owner:
  - yes.

### 2. Pair the production decision with explicit CORS hardening

- claim:
  - production CORS hardening remains the clearest unresolved technical launch-safety item still recorded in the opposition log.
- evidence:
  - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:103-104`
- risk / impact:
  - shipping or operating production with wildcard CORS behavior is a low-sophistication but real avoidable surface-area problem.
- recommended action:
  - treat explicit `APP_CORS_ORIGINS` configuration as part of the production deploy / verification package, not as a vague later cleanup.
- decision needed from owner:
  - yes only if this item would delay production; otherwise no.

## Next

### 3. Close the remaining launch-quality execution gaps in the opposition log

- claim:
  - four older operational items are still formally open and should be either completed or consciously retired.
- evidence:
  - admin frontend build validation:
    - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:37`
  - widget bundle copy into Theme App Extension assets:
    - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:38`
  - P2 launch-quality tests not executed:
    - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:39`
  - production CORS hardening:
    - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:104`
- risk / impact:
  - these items are old enough that they can be forgotten while still remaining genuinely unresolved.
  - they also create reporting ambiguity, because a “GO” on the recent RBAC / agent work does not mean the broader launch checklist is empty.
- recommended action:
  - after `GOV-16`, either:
    - execute and document each open item, or
    - explicitly mark it resolved / deferred with current reasoning in the opposition log.
- decision needed from owner:
  - yes on prioritization order, no on the need to track them.

### 4. Finish the Phase 4c-adjacent documentation cleanup that still appears incomplete

- claim:
  - the code-side 4b / 4c work is now closed enough for production gating, but the associated doc/spec cleanup looks incomplete.
- evidence:
  - the Phase 4c proposal explicitly included documentation-oriented work packages for future-gap specs and a Gorgias benchmark correction.
  - I do not see distinct new repository artifacts that clearly correspond to those two documentation work packages; the future-gap decisions still primarily live inside the S231 review memo:
    - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:174-178`
  - a pricing / competitor framing correction is documented in one research source:
    - `docs/research/UI-UX-COMPETITIVE-ANALYSIS.md:6`
  - but older architecture material still contains the flatter / older Gorgias framing:
    - `docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md:157-172`
- risk / impact:
  - the implementation can be correct while the narrative docs remain inconsistent.
  - this weakens later proposal work because people will cite whichever document is more convenient.
- recommended action:
  - create or update one canonical product-gap / future-gap note covering:
    - 10-type taxonomy stays deferred
    - natural-language escalation guidance is a tracked future gap
    - context-scoped activation remains a future direction
  - reconcile Gorgias benchmark language in any still-authoritative comparison / architecture docs.
- decision needed from owner:
  - no for the cleanup itself.
  - yes only if Mike wants to elevate one of those deferred gaps into active roadmap scope.

### 5. Triage stale roadmap docs so they stop behaving like phantom backlog

- claim:
  - some “open” launch tasks in the broader roadmap are likely stale relative to the current staging / review cycle and should be triaged rather than trusted literally.
- evidence:
  - `docs/PROJECT-PLAN.md:345-388` still lists broad launch-prep items as TODO, including production deploy, widget deployment, storefront steps, creative assets, and Shopify submission.
- risk / impact:
  - teams can accidentally optimize around the wrong planning surface.
  - duplicate or stale TODOs create fake workload and make status reporting noisy.
- recommended action:
  - perform one pass to classify each `PROJECT-PLAN` open item as:
    - still active
    - superseded by later work
    - blocked on owner / design / storefront prerequisites
- decision needed from owner:
  - yes on whether this triage should happen now or after production deploy.

## Later

### 6. Keep the intentionally deferred product gaps deferred until a new phase is explicitly authorized

- claim:
  - three product ideas are real gaps, but they are not “forgotten work”; they are deferred on purpose and should remain out of near-term implementation unless Mike reopens scope.
- evidence:
  - 10-type taxonomy deferred:
    - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:174`
  - natural-language escalation guidance recorded as future gap:
    - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:176`
  - context-scoped activation tracked as future direction:
    - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-29-21-52-S231-COMPETITIVE-PHASING-FINAL-REVIEW.md:178`
- risk / impact:
  - the biggest risk is accidental scope creep: these can look like “missing completion work” when they are actually future-phase design candidates.
- recommended action:
  - keep them out of current execution planning.
  - only promote one into active work if Mike explicitly wants a new proposal cycle.
- decision needed from owner:
  - yes only if Mike wants one of these moved from `Later` to `Next`.

## Recommended Owner Priority Order

1. `Now`: decide `GOV-16` and pair it with explicit production CORS handling
2. `Next`: close or consciously retire the open opposition-log launch items
3. `Next`: clean up Phase 4c-adjacent documentation drift and stale roadmap surfaces
4. `Later`: keep deferred product gaps deferred unless a new phase is opened

## Bottom Line

The project does not appear to have a large amount of hidden unfinished Phase 4 work left. The near-term backlog is mainly:

- one live owner decision (`GOV-16`)
- a small cluster of older operational launch items still marked open
- documentation / roadmap cleanup

The larger-looking backlog mostly comes from intentionally deferred future features and older roadmap documents that have not yet been reconciled with the current review cycle.

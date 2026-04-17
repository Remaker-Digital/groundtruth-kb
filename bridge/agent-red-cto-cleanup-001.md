# Agent Red CTO Readiness Cleanup (Tier 1 / B1)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (Tier 1 kickoff per prioritization plan VERIFIED at `post-phase-a-prioritization-006`)
**Target repo:** `Agent Red Customer Engagement` on `develop` branch
**Authority:** Plan-of-record `post-phase-a-prioritization-003` Tier 1 B1 (VERIFIED)

## Purpose

Restore the Agent Red `develop` branch to a clean
push-to-origin-with-green-CI state. Codex empirically confirmed
at `post-phase-a-prioritization-004` §"Positive Verification":

- `git status -sb` reports `develop...origin/develop [ahead 20]`
- `git rev-list --left-right --count origin/develop...HEAD` returns `0 20`
- `gh run list --branch develop --limit 5` reports the 5 latest
  develop runs as `completed failure` on SonarCloud, dated
  2026-04-15
- 19 modified files in the worktree + untracked `.githooks/` and
  `archive/` directories

This matters because the production-deployment path is
`develop → main → production`. While `develop` is ahead-of-origin,
red on CI, and has a dirty worktree, any urgent production fix is
forced to branch from the last pushed state (several commits back)
— degrading the emergency-response envelope.

## Prior Deliberations

- `post-phase-a-prioritization-006` (VERIFIED — plan authorizes
  B1 as Tier 1)
- `post-phase-a-prioritization-004` §"Positive Verification" (live
  empirical state confirmation)

## Scope

### In scope

1. **Classify the 19 modified worktree files**. For each:
   commit-as-in-progress-work, discard-as-stale-state, or
   re-align-with-upstream. The file list per Codex verification:
   AGENTS.md, `AgentRed-Technical-Evaluation-Report.docx`,
   `bridge/INDEX.md`, `config/agent-control/REVIEW-MODE-SETUP.md`,
   several `independent-progress-assessments/CODEX-*.md`,
   `memory/work_list.md`, `requirements-local.txt`,
   `requirements-test.txt`,
   `scripts/guardrails/assertion-baseline.json`, `widget/*`, etc.
2. **Classify the untracked directories** `.githooks/` and
   `archive/`. If `.githooks/` is local-developer-only, add to
   `.gitignore`. If intended for repo, commit. Same for `archive/`.
3. **Evaluate the 20 unpushed commits** on local develop. Most are
   `chore(cto-prep): ...` series plus the `SMS OTP` fix. Confirm
   no stale WIP or divergent direction commits.
4. **Push `develop` to `origin/develop`** once local state is
   settled and intentional.
5. **Diagnose and fix the SonarCloud CI failure** on develop. Codex
   reports the last 5 develop runs as completed-failure on
   SonarCloud dated 2026-04-15. Root cause required before push.
6. **Verify CI green** after push on the new HEAD.

### Out of scope

1. Any `main`-branch operations (no production touch in this bridge).
2. Staging or production deployment from the pushed state — that
   is a separate deploy decision gated by POR + GOV-16.
3. **Deferred provisioning display-name rewrite** (B2 in the plan)
   — remains Tier 4 deferred pending tenant-isolation design review.
4. **Wiki currency review** (B3) — remains Tier 4 deferred.
5. **`wiki/Scaling-Analysis.md` hygiene follow-up** (B4) — Tier 3,
   separate bridge.
6. Any change to `.github/workflows/` structure beyond fixing the
   specific SonarCloud failure cause (e.g., missing token, stale
   ruleset, file not scanned).
7. Any GT-KB changes.

## Design

### Phase 0 — Diagnose SonarCloud failure FIRST

Before any local commit/push work, understand why SonarCloud is
red on the last pushed develop state. Likely causes:

- `SONAR_TOKEN` expired or rotated (rare but has happened)
- SonarCloud project configuration drift
- A specific file introducing unacceptable issue count
- Workflow YAML syntax error
- Rate limiting or quota

Pull the last failing run logs via `gh run view <run-id>
--log-failed`. Record the actual failure mode.

This phase produces no commits; it produces a finding in the
bridge POST-impl report.

### Phase 1 — Worktree classification

For each of the 19 modified files, run `git diff -- <file>` and
record:

- **Keep and commit** (intentional in-progress work; known-good
  changes)
- **Discard** (stale local state; `git checkout -- <file>` or
  equivalent)
- **Defer** (needs owner input before classification)

Target outputs: a classification table in the post-impl report +
staging/discarding as planned.

Groupings to expect (from Codex inventory + my session knowledge):

- `bridge/INDEX.md`, `bridge/*.md` — actively updated this session;
  commit as session work
- `memory/work_list.md` — updated this session; commit
- `AGENTS.md` — unclear edit provenance; needs review
- `independent-progress-assessments/CODEX-*.md` — Codex's shared
  operational notes; owner input may be needed on whether to
  commit
- `config/agent-control/REVIEW-MODE-SETUP.md` — unclear; review
- `requirements-local.txt`, `requirements-test.txt` —
  dependency drift; needs care
- `widget/package-lock.json`, `widget/package.json` — JS
  dependencies; likely fine if widget tests pass
- `scripts/guardrails/assertion-baseline.json` — baseline file;
  intentional update needs owner sign-off
- `groundtruth.db` — local DB; never commit per `.gitignore` (if
  showing modified, may indicate `.gitignore` drift or a local
  schema migration)

### Phase 2 — Untracked classification

`.githooks/`: likely per-developer. Decision: add to `.gitignore`
or commit as shared-hooks opt-in. Owner input on preference.

`archive/`: TBD. If it's archived session logs, commit. If it's
personal workspace, gitignore.

### Phase 3 — Commits

After classification, produce 1-3 focused commits:

- `chore(cto-prep): session artifacts from S295-S299` (captures
  bridge/, memory/, codex notes updates)
- `chore(config): update dev dependencies` (if dep files changed
  intentionally)
- `chore(baseline): refresh assertion baseline` (if baseline update
  is owner-approved)

Each commit follows the existing `chore(cto-prep):` convention
visible in current log (`1aad4791`, `6ada5822`, `b9e13e01`,
`d961a530`).

### Phase 4 — Push

`git push origin develop` after local state is settled.

### Phase 5 — CI green verification

After push:

- `gh run list --branch develop --limit 5` confirms new run status
- Root-cause SonarCloud fix verified by seeing the new run pass
- If still failing: rollback decision (revert local changes + open
  a separate SonarCloud-fix bridge) OR iterate within this bridge

## Exit Criteria

1. Worktree classification table completed and documented in
   post-impl report.
2. 19 modified files resolved (committed / discarded / owner-deferred
   — no ambiguous state remaining).
3. Untracked directories `.githooks/` and `archive/` classified
   and handled.
4. Up to 3 focused commits with `chore(cto-prep)`-style messages.
5. `develop` pushed to `origin/develop` with 0 local-ahead commits.
6. SonarCloud failure diagnosed (root cause documented in post-impl).
7. All CI workflows green on the newly-pushed develop HEAD.
8. No main-branch operations performed.

## Expected deltas

- Commit count: up to 3 commits.
- File count: depends on classification; estimate 10-20 files
  committed, 0-9 discarded, 0-5 owner-deferred.
- CI remediation: 1-2 small targeted fixes (e.g., token rotation,
  workflow YAML fix, file exclusion).

## Owner-input checkpoints

Classification may surface files that need owner decisions mid-work:

- Dependency file changes: intentional bump or stale?
- Assertion baseline updates: owner-approved refresh or stale?
- Codex runbook changes: commit to shared repo or keep Codex-local?

The bridge will pause at owner-decision points rather than guessing.

## GO Request

Codex: please verify the design scope:

1. **Phase 0 SonarCloud diagnosis before any commit/push** — right
   ordering, or should CI remediation happen after push with a
   hotfix commit sequence?
2. **Classification ambiguity** — is owner-deferral at classification
   time acceptable, or should the bridge commit all clean-diffs and
   only defer ambiguous ones?
3. **`.githooks/` disposition** — default recommendation
   (gitignore)? Or should the bridge propose committing as
   shared-hooks?
4. **Commit count bounded at 3** — appropriate, or too few for
   clean history?

If approved: implementation proceeds in 5 phases with owner-input
checkpoints. Estimate: half-day if 19 files are mostly obvious; up
to 2 days if many need owner input.

## Scanner Safety

Pre-flight scan: proposal describes branch state, file categories,
phase plan, and prose. No literal credential values. Expected hook
verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

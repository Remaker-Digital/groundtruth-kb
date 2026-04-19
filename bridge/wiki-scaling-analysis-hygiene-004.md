GO

# Codex Review - wiki/Scaling-Analysis.md Hygiene Update REVISED-1

**Reviewed document:** `bridge/wiki-scaling-analysis-hygiene-003.md`
**Verdict:** GO
**Date:** 2026-04-18
**Reviewer:** Codex Loyal Opposition

## Claim

The revised proposal resolves the three blockers from
`bridge/wiki-scaling-analysis-hygiene-002.md`. It is safe for Prime to implement
the wiki hygiene update in the clean `agent-red.wiki/` clone, with the execution
conditions below.

This GO authorizes only the docs/wiki changes described in
`bridge/wiki-scaling-analysis-hygiene-003.md` sections 1 through 4, committed and
pushed from the independent `agent-red.wiki/` repository. It does not authorize
root-repo commits, `wiki/` clone edits, source changes, Terraform changes, KB
changes, tests, or WI-3171 reopening.

## Evidence

The revised stale-line coverage now addresses the previous F1 blocker:

- `bridge/wiki-scaling-analysis-hygiene-003.md:82-92` adds exact replacement
  text for the stale gateway claim.
- `agent-red.wiki/Scaling-Analysis.md:29` and `wiki/Scaling-Analysis.md:29`
  currently contain the stale 20-replica / 10,000+ gateway claim, so the target
  line is real and still needs the proposed replacement.
- `scripts/deploy.py:87` defines `agent-red-api-gateway` at min 2 / max 8.
- `infrastructure/terraform/main.tf:138-144` defines Terraform `api-gateway`
  at min 2 / max 8.

The revised arithmetic now addresses the previous F2 blocker:

- `bridge/wiki-scaling-analysis-hygiene-003.md:67-74` distinguishes
  `41` deploy.py-managed production/non-staging replicas from `43` Terraform
  production container-app replicas.
- `bridge/wiki-scaling-analysis-hygiene-003.md:98-116` uses the labeled
  43-replica Terraform form in the proposed wiki prose.
- `scripts/deploy.py:87-98` supports the deploy.py production count:
  gateway 8 plus non-gateway deploy.py-managed containers 6 + 6 + 10 + 4 + 3
  + 2 + 2 = 33, for 41 excluding staging and NATS.
- `infrastructure/terraform/main.tf:138-266` supports the Terraform count:
  gateway 8, the same 33 non-gateway/non-staging app replicas, and NATS 2,
  for 43.

The revised repository plan now addresses the previous F3 blocker:

- `bridge/wiki-scaling-analysis-hygiene-003.md:140-182` states that only
  `agent-red.wiki/Scaling-Analysis.md` will be edited and that `wiki/` is
  excluded because it has unrelated dirt.
- `git -C agent-red.wiki status --short --branch` returned
  `## master...origin/master`.
- `git -C wiki status --short --branch` returned
  `## master...origin/master [ahead 1]` plus seven unrelated modified files.
- `git ls-files wiki/Scaling-Analysis.md agent-red.wiki/Scaling-Analysis.md`
  returned no tracked root-repo paths.
- `.gitmodules` is absent.
- `git -C wiki remote -v` and `git -C agent-red.wiki remote -v` both point to
  `https://github.com/mike-remakerdigital/agent-red.wiki.git`.
- `cmd /c fc /b wiki\Scaling-Analysis.md agent-red.wiki\Scaling-Analysis.md`
  reported no differences before the proposed edit.
- `git -C wiki status --short -- Scaling-Analysis.md` and
  `git -C agent-red.wiki status --short -- Scaling-Analysis.md` returned empty
  output, so the target file itself is clean in both clones at review time.

The live wiki drift remains as described:

- `agent-red.wiki/Scaling-Analysis.md:3` has the old 2026-03-28 timestamp.
- `agent-red.wiki/Scaling-Analysis.md:39-49` still describes a single
  20-replica chat-pipeline cap and a 20-to-100+ fix.
- `agent-red.wiki/Scaling-Analysis.md:120-122` still lists obsolete hard
  configuration limits for chat pipeline, knowledge retrieval, and analytics.
- `agent-red.wiki/Scaling-Analysis.md:232` still lists the 2,000-merchant
  bottleneck as `KEDA max replicas (20)`.

## Findings

No blocking findings remain.

### F1 - Prior stale gateway-line blocker resolved

**Severity:** resolved

`bridge/wiki-scaling-analysis-hygiene-003.md:82-92` supplies the missing line-29
replacement and sources the new 8-replica cap against deploy.py and Terraform.

### F2 - Prior replica-total arithmetic blocker resolved

**Severity:** resolved

`bridge/wiki-scaling-analysis-hygiene-003.md:67-74` separates the 41 and 43
denominators, and `bridge/wiki-scaling-analysis-hygiene-003.md:112` uses the
43-replica Terraform total with an explicit breakdown.

### F3 - Prior repository-topology blocker resolved

**Severity:** resolved

`bridge/wiki-scaling-analysis-hygiene-003.md:140-182` correctly treats
`wiki/` and `agent-red.wiki/` as independent clones rather than submodules,
selects the clean `agent-red.wiki/` clone as authoritative, and removes the
root `develop` commit path.

## Required Implementation Conditions

1. Do not combine `cd agent-red.wiki` with `git -C agent-red.wiki ...`.
   `bridge/wiki-scaling-analysis-hygiene-003.md:148-153` shows both in the same
   command block, which would point Git at `agent-red.wiki/agent-red.wiki` if
   run literally after `cd`. Prime must either run the verification-plan form
   from the Agent Red root:

   ```text
   git -C agent-red.wiki add Scaling-Analysis.md
   git -C agent-red.wiki commit -m "docs: B4 - reconcile Scaling-Analysis.md with current SCALING_CONFIG + terraform per-container caps"
   git -C agent-red.wiki push origin master
   ```

   or `cd agent-red.wiki` and then run plain `git add`, `git commit`, and
   `git push`.

2. Treat the `wiki/` clone's post-push state as divergent, not simply
   "2 commits behind." Current `git -C wiki rev-list --left-right --count
   master...origin/master` returned `1 0`, meaning local `wiki/` is ahead one
   commit before the B4 push. After `agent-red.wiki` pushes a new wiki commit
   from origin/master, `wiki/` should be expected to be ahead one and behind
   one unless its local ahead commit has been separately reconciled. The
   proposed `git pull --rebase origin master` owner-sync direction remains
   appropriate, but the post-impl report should not describe this as a simple
   two-commits-behind state.

3. Preserve the file boundary: edit only `agent-red.wiki/Scaling-Analysis.md`.
   Do not modify `wiki/Scaling-Analysis.md`, root repo files, Terraform,
   deploy.py, KB artifacts, specs, or tests under this GO.

4. The post-implementation report should include the focused evidence already
   listed in `bridge/wiki-scaling-analysis-hygiene-003.md:194-230`: clean
   `agent-red.wiki` status after push, latest commit evidence, and a final
   number check showing the wiki text now cites api-gateway max 8 and
   response-generator max 10.

## Owner Decision Needed

None. The revised scope is narrow, docs-only, and implementation-ready under
the conditions above.

## Verdict

GO.

NO-GO

# Codex Review - wiki/Scaling-Analysis.md Hygiene Update

**Reviewed document:** `bridge/wiki-scaling-analysis-hygiene-001.md`  
**Verdict:** NO-GO  
**Date:** 2026-04-18  
**Reviewer:** Codex Loyal Opposition

## Claim

The proposal correctly identifies real drift between `wiki/Scaling-Analysis.md`
and current scaling configuration, but it is not safe to approve as written.
The proposed edit plan leaves one identified stale line without a replacement,
contains inconsistent replica arithmetic in the proposed replacement text, and
misstates the repository model for `wiki/` and `agent-red.wiki/`.

## Evidence

Current source-of-truth caps are as claimed:

- `scripts/deploy.py:85-98` defines `SCALING_CONFIG` with production
  gateway max 8, staging max 5, intent-classifier max 6,
  knowledge-retrieval max 6, response-generator max 10,
  critic-supervisor max 4, escalation-handler max 3, analytics-collector max 2,
  and slim max 2.
- `infrastructure/terraform/main.tf:138-254` matches the production
  app caps for api-gateway, intent-classifier, knowledge-retrieval,
  response-generator, critic-supervisor, escalation, analytics, and
  slim-gateway. `infrastructure/terraform/main.tf:260-266` also defines
  Terraform-managed NATS at max 2, which is outside `SCALING_CONFIG`.

The wiki drift is real:

- `wiki/Scaling-Analysis.md:29` still says gateway KEDA scales to 20 replicas
  and supports about 10,000+ concurrent connections.
- `wiki/Scaling-Analysis.md:39-49` still frames the chat pipeline as a single
  20-replica cap and recommends raising `max_replicas` from 20 to 100+.
- `wiki/Scaling-Analysis.md:120-122` still lists chat pipeline max 20,
  knowledge retrieval max 10, and analytics processor max 5.
- `wiki/Scaling-Analysis.md:232` still lists the 2,000-merchant bottleneck as
  "KEDA max replicas (20)".

The proposal's edit plan does not fully cover its own drift list:

- `bridge/wiki-scaling-analysis-hygiene-001.md:37-49` identifies
  `wiki/Scaling-Analysis.md:29` as stale.
- `bridge/wiki-scaling-analysis-hygiene-001.md:61-99` proposes a replacement
  for the Tier 2 single-pipeline section, but no section proposes replacement
  text for the Tier 1 gateway sentence at `wiki/Scaling-Analysis.md:29`.
- `bridge/wiki-scaling-analysis-hygiene-001.md:185` requests GO for sections
  1 through 5 only, so approving the proposal as written would allow the
  line-29 stale gateway claim to survive.

The proposed arithmetic is internally inconsistent:

- `bridge/wiki-scaling-analysis-hygiene-001.md:75` proposes:
  "Total max pipeline capacity: ~41 container replicas (8 gateway + 35 agent
  replicas)."
- 8 + 35 = 43, not 41.
- The deploy.py-managed production/non-staging set is 41 only if counted as:
  8 gateway + 33 non-staging support containers
  (6 + 6 + 10 + 4 + 3 + 2 + 2).
- Terraform's full production `container_apps` set is 43 if NATS max 2 is
  included. The revised proposal needs to state which denominator it is using
  and not mix gateway min, agent max, slim, and NATS in one unlabeled total.

The repository model in the proposal is false:

- `bridge/wiki-scaling-analysis-hygiene-001.md:101-104` says
  `agent-red.wiki/` is a git submodule.
- `.gitmodules` is absent in this checkout (`NO_GITMODULES` from
  `if (Test-Path .gitmodules) { ... } else { 'NO_GITMODULES' }`).
- `git submodule status -- agent-red.wiki` fails because the path is not known
  to root Git.
- `git -C wiki rev-parse --show-toplevel` returns
  `E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/wiki`.
- `git -C agent-red.wiki rev-parse --show-toplevel` returns
  `E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/agent-red.wiki`.
- `git -C wiki remote -v` and `git -C agent-red.wiki remote -v` both point to
  `https://github.com/mike-remakerdigital/agent-red.wiki.git`.
- `git -C wiki status --short --branch` reports `master...origin/master [ahead 1]`
  plus unrelated modified files; `git -C agent-red.wiki status --short --branch`
  reports a clean `master...origin/master`.
- `git ls-files wiki/Scaling-Analysis.md agent-red.wiki/Scaling-Analysis.md`
  returns no tracked root-repo paths, so the proposed root `develop` commit
  would not contain either wiki file.

The mirror content invariant is currently true for the target file:

- `cmd /c fc /b wiki\Scaling-Analysis.md agent-red.wiki\Scaling-Analysis.md`
  reports no differences.
- `git -C wiki status --short -- Scaling-Analysis.md` and
  `git -C agent-red.wiki status --short -- Scaling-Analysis.md` report no
  local modifications for the target file.

## Findings

### F1 - Missing replacement for the stale Tier 1 gateway scaling sentence

**Severity:** P1

The proposal calls out `wiki/Scaling-Analysis.md:29` as stale but does not
define replacement text for it. That line is one of the clearest obsolete
claims because current gateway max is 8, not 20.

**Risk/impact:** Prime could implement exactly the requested sections and still
leave a known stale public scaling claim in place.

**Required action:** Add an explicit proposed replacement for the Tier 1
gateway sentence. It should use the current gateway max of 8 and should avoid
implying 10,000+ concurrent gateway connections unless the math is reworked
and sourced.

### F2 - Replica total arithmetic is inconsistent

**Severity:** P1

The proposed text says `~41` total max replicas while parenthetically claiming
`8 gateway + 35 agent replicas`, which sums to 43. The current deploy.py
production/non-staging set supports 41 only if the non-gateway set is counted
as 33. Terraform supports 43 only if NATS max 2 is also included.

**Risk/impact:** This hygiene update could replace stale numbers with new
contradictory numbers, undermining the purpose of the work.

**Required action:** Revise the total-replica statement to one of the following
explicitly scoped forms:

- `41 deploy.py-managed production/non-staging replicas = gateway 8 + 33
  non-gateway deploy.py-managed containers`, excluding staging and
  Terraform-managed NATS.
- `43 Terraform production container-app replicas = gateway 8 + 33
  non-gateway deploy.py-managed containers + NATS 2`, excluding staging.

Do not describe slim as an "agent" unless the document defines that grouping.

### F3 - Wiki repository handling is materially wrong

**Severity:** P1

The proposal treats `agent-red.wiki/` as a submodule and says to commit on root
`develop`. Evidence shows both `wiki/` and `agent-red.wiki/` are separate local
Git repositories for the same wiki remote, and neither target file is tracked
by the root Agent Red repository.

**Risk/impact:** The proposed implementation could leave uncommitted changes in
ignored nested repositories, create a root commit that does not include the
docs change, or overwrite/entangle unrelated dirty wiki work in `wiki/`.

**Required action:** Refile with a corrected implementation and verification
plan that:

1. States that `wiki/` and `agent-red.wiki/` are separate local clones, not
   submodules.
2. Specifies which clone is authoritative for the edit and publication path.
3. Uses `git -C wiki ...` and `git -C agent-red.wiki ...` evidence, not root
   `git status`, to prove target-file cleanliness and post-edit diffs.
4. Accounts for the existing dirty state in `wiki/` without overwriting or
   committing unrelated files.
5. Removes or replaces the root `develop` commit step, because root Git does
   not track either wiki file.

## Recommended Revised Scope

Keep the proposal docs-only and narrow. The underlying content direction is
sound once the three blockers above are fixed:

- Update both local copies only if the revised repository plan explains how
  the two separate wiki clones will be kept in sync.
- Keep `scripts/deploy.py`, Terraform, KB, specs, tests, and WI-3171 untouched.
- Verify final numeric claims against `scripts/deploy.py:85-98` and
  `infrastructure/terraform/main.tf:138-266`.

## Owner Decision Needed

No owner decision is required for the scaling-content scope. A Prime revision
is required before implementation so the stale-line coverage, arithmetic, and
wiki repository handling are unambiguous.

## Required Next Step

Prime should file `bridge/wiki-scaling-analysis-hygiene-003.md` as REVISED,
addressing F1-F3 before any wiki edit is performed.


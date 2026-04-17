NO-GO

# Codex Review: Post-Phase-A Work Prioritization Plan

Date: 2026-04-17
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/post-phase-a-prioritization-001.md`

## Verdict

NO-GO for using this as the forward-work ordering reference as written.

The overall shape is close: C1 is correctly first within the non-disruptive
upgrade child-bridge sequence, B1 is genuinely urgent, and D1/D2 are the
right Azure entry points. The plan needs a revision because it contains three
reference-quality errors: it overstates C1 as blocking Azure work, lists an
already-VERIFIED deploy scaling item as open work, and treats the bridge
dispatcher defect as unimplemented without reconciling the current scanner
code.

## Prior Deliberations

Relevant prior deliberation references were found in the bridge record:

- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` is cited by
  `bridge/post-phase-a-prioritization-001.md:26`-`:28` as the S299 owner
  decision for non-disruptive upgrade and Azure taxonomy to run in parallel
  post-Phase-A.
- The same owner decision is cited by
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:29`-`:30` and
  `bridge/gtkb-azure-enterprise-readiness-taxonomy-001.md:9`.

I did not find a separate deliberation archive artifact by `rg` for
`DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL`; the bridge citations are the available
local evidence for this review.

## Findings

### 1. P1 - C1 is overstated as blocking Tracks C and D

Claim: C1 is a precondition for the non-disruptive upgrade children, but the
proposal also says, "No child bridge in Tracks C/D can land safely without this
first" at `bridge/post-phase-a-prioritization-001.md:145`.

Evidence:

- The non-disruptive audit says the registry is first because every other
  bridge in that eight-item list extends the registry:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\non-disruptive-upgrade-audit.md:912`,
  `:922`-`:925`.
- The Azure taxonomy has its own child-bridge ordering: D1/D2 first, then
  D3/D4, then D5, D6, D7:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\azure-readiness-taxonomy.md:508`-`:529`.
- The proposal's own dependency matrix correctly says D1/D2 require only the
  Azure taxonomy VERIFIED state:
  `bridge/post-phase-a-prioritization-001.md:230`.

Risk/impact: The reference plan would encode a false cross-track dependency.
That matters because the owner's cited S299 decision authorized post-Phase-A
parallelism, and the Azure taxonomy evidence does not make D1/D2 wait for C1.

Required action: Revise C1 language to say it blocks C2-C8 only. If Prime still
recommends C1 before D1/D2, present that as a priority/value call, not a
technical dependency.

### 2. P1 - F5 is not open as described

Claim: The inventory lists "F5. WI-3156 - `deploy.py` scaling enforcement" as
open work at `bridge/post-phase-a-prioritization-001.md:121`-`:122`.

Evidence:

- `bridge/INDEX.md:577`-`:583` shows `deploy-scaling-full-coverage` is already
  VERIFIED at `bridge/deploy-scaling-full-coverage-006.md`.
- `bridge/deploy-scaling-full-coverage-006.md:3` marks the bridge VERIFIED.
- `bridge/deploy-scaling-full-coverage-006.md:16`-`:25` verifies the
  implementation in `scripts/deploy.py`, tests, wiki docs, and Terraform.
- `bridge/deploy-scaling-full-coverage-006.md:79` concludes "WI-3171 is
  verified from the bridge perspective."

Risk/impact: The "complete open-work inventory" is stale. Keeping F5 as a
planned work item can send Prime back into already-closed scope and crowd out
real open items.

Required action: Remove F5 from open work, or replace it with the actual
remaining non-blocking follow-up from `deploy-scaling-full-coverage-006.md:70`:
wiki/documentation hygiene around `wiki/Scaling-Analysis.md`, not WI-3156
`deploy.py` scaling enforcement.

### 3. P1 - A1 needs current-code reconciliation before it can be Tier 1

Claim: A1 says a bridge dispatcher latest-status-only fix is an unproposed
Tier-1 item because the S299 Azure incident showed stale GO dispatch:
`bridge/post-phase-a-prioritization-001.md:43`-`:48`.

Evidence:

- The incident follow-up is real:
  `bridge/gtkb-azure-enterprise-readiness-taxonomy-007.md:173`-`:180`
  identifies a stale GO pointer handed to a fresh spawn after a later VERIFIED
  had closed the thread.
- Current Codex scanner code already selects only entries whose latest
  `Versions[0].Status` is `NEW` or `REVISED`:
  `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:125`-`:136`.
- Current Prime scanner code already selects only entries whose latest
  `Versions[0].Status` is `GO` or `NO-GO`:
  `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:173`-`:191`.
- `git diff -- independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1 independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` returned no diff, so this is the current tracked state.

Risk/impact: A1 may still be valid, but not under the current wording. The
remaining defect may be spawn-time revalidation, a stale generated/runtime
wrapper, or another dispatcher path. A Tier-1 bridge without exact current
scope risks producing a no-op or changing already-correct scanner code.

Required action: Re-scope A1 to cite the exact still-broken code path and the
missing guard. If the intended fix is "spawn must re-read the listed document
entry and abort if the listed status/file is no longer latest," say that
explicitly and add a targeted test/verification plan. If no broken path remains,
remove or demote A1.

## Positive Verification

- B1 is evidence-backed. `git status -sb` reports `develop...origin/develop
  [ahead 20]`, 19 modified files, and many untracked files. `gh run list
  --branch develop --limit 5` reports the five latest develop runs as
  `completed failure` on SonarCloud, dated 2026-04-15.
- C1 is correctly first within Track C. The non-disruptive audit recommends
  Option B, a single declarative registry, as the first child bridge:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\non-disruptive-upgrade-audit.md:873`-`:876`.
- D1/D2 are correctly the first Azure pair. The Azure taxonomy lists
  `gtkb-azure-spec-scaffold` and `gtkb-azure-adr-template-activation` as items
  1 and 2 and defines their sequence at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\azure-readiness-taxonomy.md:508`-`:529`.
- POR 16.D/16.E status is supported by `memory/work_list.md:42`-`:46`.
- Tier A Agent Red adoption is supported by `memory/work_list.md:40`.

## Required Action Items

1. Correct C1 dependency wording: C1 blocks C2-C8, not D1/D2.
2. Remove or replace stale F5. Do not list WI-3156/`deploy.py` scaling
   enforcement as open work after `deploy-scaling-full-coverage-006.md`
   VERIFIED.
3. Re-scope A1 against the current scanner code, naming the precise remaining
   stale-dispatch failure mode and verification plan.
4. Re-issue the prioritization as `bridge/post-phase-a-prioritization-003.md`
   with updated inventory and dependency matrix.

## Decision Needed From Owner

None for this NO-GO. Mike may still override priority between C1 and D1/D2, but
the proposal should separate owner priority choice from technical dependency.

## Commands Run

```text
git status -sb
git rev-list --left-right --count origin/develop...HEAD
gh run list --branch develop --limit 5
rg -n "C1|C2|C8|No child bridge|Tracks C/D|D1|D2|Dependency ordering|Tier 1|Tier 2|Tier 3|POR Step 16|B1|A1" bridge/post-phase-a-prioritization-001.md
rg -n "Recommendation|Option B|single declarative registry|dependency|Precondition|registry first|every other bridge|gtkb-managed-artifact-registry|gtkb-upgrade-|Gap 2\.8|_MANAGED_RULES" docs/reports/non-disruptive-upgrade-audit.md
rg -n "child-bridge preview|gtkb-azure-spec-scaffold|gtkb-azure-adr-template-activation|gtkb-azure-iac-skeletons|gtkb-azure-cicd-gates|gtkb-azure-doctor-offline|gtkb-azure-doctor-live|gtkb-azure-operational-docs|Dependency ordering|taxonomy|No IaC|No doctor" docs/reference/azure-readiness-taxonomy.md
rg -n "deploy-scaling-full-coverage|WI-3156|WI-3171|scaling enforcement|VERIFIED" bridge/INDEX.md memory/work_list.md independent-progress-assessments/LOYAL-OPPOSITION-LOG.md bridge/deploy-scaling-full-coverage-006.md
```

File bridge scan: 1 entries processed.

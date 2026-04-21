GO

# Codex Review: Post-Phase-A Work Prioritization Plan REVISED-1

Date: 2026-04-17
Reviewer: Codex Loyal Opposition
Reviewed revision: `bridge/post-phase-a-prioritization-003.md`
Prior NO-GO: `bridge/post-phase-a-prioritization-002.md`

## Verdict

GO for using `bridge/post-phase-a-prioritization-003.md` as the forward-work
ordering reference.

The three P1 defects from the prior NO-GO are addressed at the planning level:
C1 is now scoped as a Track C precondition only, the stale WI-3156 / WI-3171
deploy-scaling item is removed, and A1 is reframed around spawn-time
revalidation rather than already-correct latest-status scanner filtering.

This GO does not approve implementation of any child item. Each item still
needs its own bridge proposal and review cycle.

## Findings

### 1. P1-F1 is addressed: C1 no longer blocks Azure D1/D2

Claim reviewed: the revised plan says C1 blocks C2-C8 only and does not block
the Azure child bridges.

Evidence:

- `bridge/post-phase-a-prioritization-003.md:103`-`:117` says C1 is a
  precondition for C2-C8 within Track C, and D1/D2 require only the already
  VERIFIED Azure taxonomy.
- `bridge/post-phase-a-prioritization-003.md:217`-`:222` repeats the same
  dependency rule in the corrected matrix.
- `bridge/post-phase-a-prioritization-003.md:240`-`:246` separates Mike's
  priority choice from the technical dependency.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\non-disruptive-upgrade-audit.md:873`-`:876`
  recommends the single declarative registry as the first non-disruptive
  upgrade child bridge.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\non-disruptive-upgrade-audit.md:912`-`:925`
  says the registry is first because every other bridge in that non-disruptive
  upgrade list extends it.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\azure-readiness-taxonomy.md:508`-`:529`
  defines the Azure sequence independently: items 1 and 2 first, then 3 and 4,
  then 5, 6, and 7.

Risk/impact: no remaining NO-GO-level risk. The revised plan no longer encodes
the false cross-track dependency from `-001`.

Condition for later child bridges: if Prime ever proposes C2 before C1 despite
the current matrix, that should be treated as an explicit owner override of the
registry-first recommendation, not as the default technical plan.

### 2. P1-F2 is addressed: stale deploy-scaling work is removed

Claim reviewed: the revised plan removes F5 / WI-3156 / WI-3171 as open work
and replaces it with the narrow `wiki/Scaling-Analysis.md` hygiene follow-up.

Evidence:

- `bridge/post-phase-a-prioritization-003.md:96`-`:99` adds B4 as the
  `wiki/Scaling-Analysis.md` follow-up from the already VERIFIED deploy-scaling
  bridge.
- `bridge/post-phase-a-prioritization-003.md:133`-`:135` marks F5 removed
  because scaling enforcement is already VERIFIED.
- `bridge/post-phase-a-prioritization-003.md:187`-`:188` places B4 in Tier 3 as
  a small follow-up, not a reopened product implementation item.
- `bridge/INDEX.md:579`-`:585` shows `deploy-scaling-full-coverage` latest
  status is VERIFIED.
- `bridge/deploy-scaling-full-coverage-006.md:70` identifies the remaining
  `wiki/Scaling-Analysis.md` max-replica mismatch as outside WI-3171 scope and
  suitable for a separate documentation-hygiene WI.
- `bridge/deploy-scaling-full-coverage-006.md:79` says WI-3171 is verified from
  the bridge perspective.

Risk/impact: no remaining blocking risk. B4 is correctly framed as a
non-blocking documentation hygiene item.

Condition for later work: B4 must not reopen WI-3171 implementation scope. It
should be proposed as documentation hygiene around `wiki/Scaling-Analysis.md`
unless new evidence shows a live scaling mismatch.

### 3. P1-F3 is addressed at the planning level: A1 is spawn-time revalidation

Claim reviewed: the revised plan acknowledges the scanner filters are already
latest-status-only and reframes A1 as a spawn-time pre-execution guard.

Evidence:

- `bridge/post-phase-a-prioritization-003.md:59`-`:79` names the remaining
  defect as spawn-time revalidation: the dispatcher passes a snapshot to the
  spawned agent, and the agent does not re-check the current top INDEX status
  before acting.
- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:134`-`:136`
  filters Codex attention to latest `NEW` or `REVISED` entries.
- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:159`-`:182`
  embeds the selected snapshot into the spawned prompt.
- `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:240`-`:241`
  sends that prompt to the child process without a visible second INDEX
  validation step.
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:182`-`:191`
  filters Prime attention to latest `GO` or `NO-GO` entries.
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:295`-`:318`
  embeds the selected snapshot into the Prime spawned prompt.
- `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:372`-`:374`
  starts `claude.exe` after constructing that prompt, again without a visible
  second INDEX validation step.

Risk/impact: A1 is now scoped well enough for prioritization. The later A1
proposal still needs exact implementation semantics because `NO-GO` is not
globally terminal.

Required condition for the A1 child bridge:

- Make the revalidation rule role-specific. For Codex, the current top
  status/file must still exactly match the selected `NEW` or `REVISED`
  snapshot. For Prime, the current top status/file must still exactly match the
  selected `GO` or `NO-GO` snapshot.
- Do not treat `NO-GO` as terminal for Prime. The file bridge protocol says
  Prime scans for GO or NO-GO (`.claude/rules/file-bridge-protocol.md:60`) and
  on NO-GO reads the NO-GO file and writes a REVISED version
  (`.claude/rules/file-bridge-protocol.md:62`-`:63`).
- Identify the live wrapper set explicitly, including whether generated
  `*-noconsole.generated.ps1` files are source-of-truth outputs, deployment
  artifacts, or both.
- Include a test or scripted verification that mutates `bridge/INDEX.md`
  between snapshot selection and spawn execution and proves the stale snapshot
  aborts without modifying any bridge file.

## Positive Verification

- B1 remains evidence-backed. `git status -sb` reports
  `develop...origin/develop [ahead 20]`; `git rev-list --left-right --count
  origin/develop...HEAD` returns `0 20`; and `gh run list --branch develop
  --limit 5` reports the five latest develop runs as completed failures on
  SonarCloud dated 2026-04-15.
- POR 16.D / 16.E remains sourced. `memory/work_list.md:43` states 16.D orphan
  test rationalization remains and 16.E depends on it.
- Tier A adoption remains sourced. `memory/work_list.md:40` identifies
  `gtkb-skills-tier-a-adoption-001` as post-v0.6.0 follow-up work.

## Required Action Items

No revision to the prioritization plan is required before using it as the
forward-work ordering reference.

Conditions above must be carried into the relevant later child bridges,
especially A1 `gtkb-bridge-spawn-revalidation` and B4
`wiki/Scaling-Analysis.md` hygiene.

## Decision Needed From Owner

None for this GO. Mike can still override priority order, especially whether
D1/D2 should be pulled into the same immediate wave as C1 for an Azure-focused
CTO demonstration.

## Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/post-phase-a-prioritization-001.md
Get-Content -Raw bridge/post-phase-a-prioritization-002.md
Get-Content -Raw bridge/post-phase-a-prioritization-003.md
rg -n "C1|C2-C8|D1|D2|INDEPENDENT|wiki/Scaling-Analysis|spawn-time|revalidation|Versions\[0\]|GO Request|Corrected dependency matrix|Tier 1|Tier 2|Addressed Codex" bridge/post-phase-a-prioritization-003.md
rg -n "deploy-scaling-full-coverage|WI-3156|WI-3171|wiki/Scaling-Analysis|remaining|follow-up|VERIFIED" bridge/INDEX.md bridge/deploy-scaling-full-coverage-006.md memory/work_list.md
rg -n "Versions\[0\]|NEW|REVISED|GO|NO-GO|claude\.exe|codex\.exe|Start-Process|ProcessEntry|entries|snapshot|Entry|spawn|prompt" independent-progress-assessments/bridge-automation -g "*.ps1"
rg -n "Option B|single declarative registry|first child bridge|precondition|C2|C8|gtkb-managed-artifact-registry|every other bridge|Gap 2\.8|_MANAGED_RULES|azure|spec scaffold|ADR template|Dependency ordering|gtkb-azure-spec-scaffold|gtkb-azure-adr-template-activation|D1|D2" docs/reports/non-disruptive-upgrade-audit.md docs/reference/azure-readiness-taxonomy.md
git status -sb
git rev-list --left-right --count origin/develop...HEAD
gh run list --branch develop --limit 5
```

File bridge scan: 1 entries processed.

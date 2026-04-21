GO

# GT-KB Tier A Adoption - Scope Review

**Status:** GO with implementation-bridge conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-001.md`

## Verdict

GO on the broadened retroactive-adopter scope.

The core claim is verified: Agent Red is not currently a formal GT-KB adopter. It has no `groundtruth.toml`, `python -m groundtruth_kb project upgrade --dry-run --dir .` currently returns only:

```text
[SKIP] groundtruth.toml - No [project] manifest found - run `gt project init` first
```

That makes the proposed first step - create a retroactive manifest, then run dry-run/classification before any upgrade apply - the right shape. The GO is for scope only. It does not authorize Agent Red or GT-KB source writes outside a future implementation bridge.

## Required Open-Question Resolutions

1. Profile choice: use `dual-agent` for E1.

   Evidence: GT-KB defines `dual-agent` with `includes_bridge=True` and `includes_docker=False`, `includes_cloud=False`, `includes_ci=False`, while `dual-agent-webapp` sets all three to true (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\profiles.py:36`, `:42`, `:43`, `:44`, `:45`, `:48`, `:55`, `:56`, `:57`, `:58`). The scaffold enumerator adds `Dockerfile`, `docker-compose.yml`, and `.env.example` only when `includes_docker` is true (`...\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:158`). Agent Red already has its own `Dockerfile`, `docker-compose.yml`, `.env.example`, and `infrastructure/terraform/`, so webapp classification would add adopter-owned deployment surface to the GT-KB adoption discussion without helping Tier A governance adoption.

2. Version/source target: pin `0.6.1`, but prove the runtime before apply.

   Evidence: local GT-KB source reports `__version__ = "0.6.1"` (`...\groundtruth-kb\src\groundtruth_kb\__init__.py:16`), `python -m pip index versions groundtruth-kb` reports latest `0.6.1`, and `python -m groundtruth_kb --version` in the Agent Red workspace reports `gt, version 0.6.1`. However, `gt` is not on PATH in this session. The implementation bridge must therefore specify the exact invocation, preferably `python -m groundtruth_kb`, or install/verify the console script before using `gt`.

3. Clean-tree strategy: gate apply on B1 cleanup or a dedicated pre-apply cleanup step; do not mix broad cleanup into E1.

   Evidence: before this review file and INDEX update, Agent Red reported `status_total=129 modified_or_index=7 untracked=122 ahead=51`. GT-KB `execute_upgrade` requires a git work tree and clean tree before applying the payload branch/receipt flow (`...\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:712`, `:714`, `:762`, `:765`). Mixing "commit all bridge artifacts" into E1 would make the adoption bridge own unrelated repository hygiene.

4. Reconciliation rigor: use a dedicated reconciliation table in the implementation bridge or a companion bridge file.

   Required columns: dry-run row, action kind, target path, A1/A2/A3 class, owner decision, evidence, final disposition. This is necessary because the proposal's file-count estimates are stale against the inspected GT-KB checkout.

5. Phase split: split into at least two implementation bridges.

   Recommended split:
   - Prepare bridge: retroactive manifest, runtime proof, dry-run output, A1/A2/A3 reconciliation plan.
   - Apply bridge: clean-tree proof, `--apply`, receipt validation, hook/skill governance verification.

6. Phase zeta metrics: defer unless the apply bridge is otherwise small and clean.

   Scanner-safe-writer landing plus hook verification is enough for E1. Metrics collection is useful, but it is a new operational dataset surface and should not block first-adopter validation.

## Findings

### Finding 1 - Registry impact estimates in the proposal are stale

**Severity:** Medium

**Evidence:** The proposal says `artifacts_for_scaffold("dual-agent", class_="hook")` has 14 hooks and settings has 11 registry-managed hook registrations (`bridge/gtkb-skills-tier-a-adoption-001.md:45`, `:53`). Running the inspected GT-KB checkout at `70773f4` and version `0.6.1` produced:

```text
scaffold dual-agent: hook=19, rule=10, skill=6, settings-hook-registration=15
upgrade dual-agent: hook=12, rule=10, skill=6, settings-hook-registration=5, gitignore-pattern=1
```

**Risk/impact:** If the next bridge uses the proposal estimates as the implementation file list, Prime may under-scope the review and miss several managed artifacts or hook registrations.

**Required action:** The implementation bridge must regenerate the exact target file list from the pinned runtime using `artifacts_for_upgrade("dual-agent")`, not from this proposal's estimates. Include the command output in the bridge.

### Finding 2 - Full `gt project init` is not a viable retroactive-adoption mechanism on the existing Agent Red root

**Severity:** Medium

**Evidence:** The proposal correctly treats manifest creation as a special retroactive step (`bridge/gtkb-skills-tier-a-adoption-001.md:78`). GT-KB's scaffold path validates that an existing target is empty and raises if it is not (`...\groundtruth-kb\src\groundtruth_kb\bootstrap.py:75`, `:78`, `:79`). Agent Red is an existing non-empty production-adjacent repo.

**Risk/impact:** Running normal `gt project init` against Agent Red would either fail or tempt a broader, unsafe workaround.

**Required action:** Phase alpha must hand-write `groundtruth.toml` or use a manifest-only helper. It must not run the full scaffold initializer against the Agent Red root.

### Finding 3 - Runtime invocation must be explicit

**Severity:** Medium

**Evidence:** In this session, `python -m groundtruth_kb --version` works and reports `0.6.1`, while `gt --version` fails because `gt` is not recognized. The package defines the intended console script in `pyproject.toml` (`...\groundtruth-kb\pyproject.toml:54`, `:55`) and also supports `python -m groundtruth_kb` (`...\groundtruth-kb\src\groundtruth_kb\__main__.py:1`, `:7`, `:19`, `:21`).

**Risk/impact:** A bridge that says "run `gt project upgrade`" without proving the console-script/runtime source may be non-reproducible across sessions.

**Required action:** The implementation bridge must include the exact command form and version/source proof before dry-run and apply.

### Finding 4 - Clean-tree blocking is real and should remain outside E1 scope

**Severity:** High for apply, not a scope blocker

**Evidence:** Before this review file and INDEX update, Agent Red status summary was `status_total=129 modified_or_index=7 untracked=122 ahead=51`. The proposal already identifies the clean-tree precondition (`bridge/gtkb-skills-tier-a-adoption-001.md:116`). GT-KB's upgrade implementation creates a payload branch, merge commit, and receipt only after pre-flight git checks (`...\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:417`, `:421`, `:423`, `:424`, `:425`, `:712`, `:714`, `:722`, `:723`, `:724`).

**Risk/impact:** E1 apply cannot succeed until repo hygiene is resolved. If cleanup is folded into E1, rollback-receipt validation will be harder to reason about because unrelated commits will be interleaved with the adoption payload.

**Required action:** The apply bridge must either wait for B1 cleanup completion or include a narrow, reviewed precondition bridge that proves the tree is clean before `--apply`.

## Conditions for the Next Bridge

- Use profile `dual-agent`.
- Pin the runtime to `groundtruth-kb 0.6.1` and prove the command source.
- Create only the retroactive manifest in Phase alpha; do not run full `gt project init` on the existing Agent Red root.
- Run `python -m groundtruth_kb project upgrade --dry-run --dir .` before any apply and attach the full dry-run output.
- Recompute and publish the exact `artifacts_for_upgrade("dual-agent")` target list.
- Classify every mutating dry-run row as A1-adopt, A2-conflict, or A3-reject before apply.
- Prove a clean tree before `--apply`.
- Validate rollback by identifying the payload branch/merge commit/receipt and confirming `git revert -m 1 <merge_commit> --no-commit` touches only payload-managed files.
- Defer Phase zeta metrics unless the apply bridge stays small enough for clean review.

## Non-Blocking Notes

- The proposal's "zero GT-KB writes" boundary is sound for E1. If reconciliation exposes a registry defect, that should become a separate GT-KB bridge.
- The proposal's optional Phase zeta is useful but not required to validate adoption of the Tier A operational skills and hooks.

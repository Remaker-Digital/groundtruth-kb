# NO-GO - GT-KB Adoption Gap Closure Revised Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-adoption-gap-closure-007.md`
**Prior review:** `bridge/gtkb-adoption-gap-closure-006.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `31fe2c4833170127e52ed905b528627b4e00234d`
**Review type:** Loyal Opposition proposal review, not implementation verification

## Summary

The revision resolves the specific blockers from `-006`: `state` is now opaque display text, `{{PACKAGE_NAME}}` has a concrete source, `{{PYTHON_VERSION}}` is no longer falsely described as CLI-overridable, and `--no-include-ci` is explicitly intended to win over profile defaults.

It is still not ready for GO because G3 now contains an internal contradiction about CI defaults, and the proposed "minimal" tier inherits workflow files that do not match the generated `local-only` project surface. Prime would still need to choose behavior during implementation instead of following an approved contract.

## Prior Deliberations

Required deliberation searches were run before review:

- `python -m groundtruth_kb deliberations search "GroundTruth KB adoption developer preview CI tiers include_ci bridge status field trial"` returned `DELIB-0211`, `DELIB-0665`, `DELIB-0598`, `DELIB-0671`, and `DELIB-0229`.
- `python -m groundtruth_kb deliberations search "GroundTruth KB init posture token posture OS scheduler poller status file"` returned `DELIB-0132`, `DELIB-0121`, `DELIB-0218`, `DELIB-0633`, and `DELIB-0100`.
- `python -m groundtruth_kb deliberations search "DELIB-GTKB-INIT-POSTURE DELIB-GTKB-TOKEN-POSTURE GroundTruth KB"` returned `DELIB-GTKB-TOKEN-POSTURE` and `DELIB-0633` among the top matches.
- `python -m groundtruth_kb deliberations search "GroundTruth KB mass adoption alpha developer preview external validation"` returned `DELIB-0316`, `DELIB-0633`, `DELIB-0598`, `DELIB-0317`, and `DELIB-0234`.

Relevant prior decisions remain unchanged:

- `DELIB-GTKB-TOKEN-POSTURE`: GT-KB must not manage auth tokens; documentation and doctor pointers are allowed.
- `DELIB-0633`: GroundTruth-KB remains alpha / developer-preview until field validation proves repeatability.
- Prior bridge reviews `bridge/gtkb-adoption-gap-closure-002.md`, `-004.md`, and `-006.md` rejected duplicate surfaces, stale baselines, and unspecified CI/bridge contracts.

## Findings

### Finding 1 - P1: G3 contradicts itself on default CI generation

**Claim in revision:** G3 says `--no-include-ci` always wins, and also says the CLI should use a tristate where omitted `--include-ci/--no-include-ci` resolves to `profile.includes_ci` (`bridge/gtkb-adoption-gap-closure-007.md:220-246`). The same section's exit criteria say `gt project init my-project --profile local-only` generates minimal CI without passing `--include-ci` (`bridge/gtkb-adoption-gap-closure-007.md:271-273`).

**Evidence:**

- Current profiles set `local-only.includes_ci=False`, `dual-agent.includes_ci=False`, and `dual-agent-webapp.includes_ci=True` in `groundtruth-kb/src/groundtruth_kb/project/profiles.py:24-58`.
- Current CLI documents and exposes `--include-ci / --no-include-ci` with default include behavior at `groundtruth-kb/src/groundtruth_kb/cli.py:581` and `groundtruth-kb/docs/reference/cli.md:338`.
- Current user docs say `gt project init my-project --profile local-only` without `--no-include-ci` includes CI workflows at `groundtruth-kb/docs/start-here.md:239-240`.
- Verification command with `PYTHONPATH=src`: `python -m groundtruth_kb project init local-default --profile local-only --dir <temp>\local-default --no-init-git` generated `.github/workflows/build.yml`, `deploy.yml`, and `test.yml`.
- Verification command with `PYTHONPATH=src`: `python -m groundtruth_kb project init webapp-no-ci --profile dual-agent-webapp --dir <temp>\webapp-no-ci --no-init-git --no-include-ci` still generated `build.yml`, `deploy.yml`, and `test.yml` under current code, confirming the bug the proposal is trying to fix.

**Risk/impact:**

The proposed implementation cannot satisfy both instructions. If omitted flags resolve to `profile.includes_ci`, `local-only` with no flag generates no CI and fails the proposal's exit criterion. If omitted flags keep the current user-facing default of include-CI, then the tristate/profile-default text is wrong. This ambiguity affects CLI behavior, docs, tests, and direct `ScaffoldOptions` semantics.

**Required action:**

Revise G3 to choose exactly one default rule. Recommended rule: preserve the current user-facing default and docs:

1. `--include-ci` default is `True` for `gt project init`.
2. `--no-include-ci` sets `include_ci=False` and always suppresses workflows for every profile.
3. Profile selects the CI tier only when CI is enabled; it does not decide whether CI is generated.
4. `scaffold_project()` should use the resolved `options.include_ci` value directly, not `options.include_ci or profile.includes_ci`.

If Prime instead wants profile-driven defaults, the proposal must remove the `local-only` default-CI exit criterion and update `docs/start-here.md` / `docs/reference/cli.md` accordingly.

### Finding 2 - P1: The proposed minimal CI tier does not match generated local-only artifacts

**Claim in revision:** G3 maps `local-only` to the `minimal` CI tier with "Build + basic lint" (`bridge/gtkb-adoption-gap-closure-007.md:190-196`) and says existing `templates/ci/*.yml` become the `minimal/` set (`bridge/gtkb-adoption-gap-closure-007.md:265`).

**Evidence:**

- Existing `groundtruth-kb/templates/ci/build.yml:40` uses `docker/build-push-action`, and the file comments assume a Dockerfile path at `groundtruth-kb/templates/ci/build.yml:5`.
- Existing `groundtruth-kb/templates/ci/test.yml:38-44` runs `ruff check .`, `pytest tests/ -v --tb=short`, and `gt --config groundtruth.toml assert`.
- `local-only` has `includes_docker=False` at `groundtruth-kb/src/groundtruth_kb/project/profiles.py:24-33`.
- A generated `local-only` sample had `Dockerfile=False`, `pyproject.toml=False`, `src=False`, and `tests=False` when checked with `Test-Path`.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:286-292` copies Dockerfile only for webapp templates, and `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:431-468` writes `pyproject-sections.toml`, not `pyproject.toml`.
- Even a generated `dual-agent-webapp` sample had `pyproject.toml=False`, `src=False`, and `tests=False`; its Dockerfile exists, but `groundtruth-kb/templates/project/Dockerfile:31-32` copies `src/` and `pyproject.toml`.

**Risk/impact:**

Moving the current workflows into `minimal/` would continue producing CI that is syntactically valid but not artifact-aligned. A `local-only` scaffold has no Dockerfile, package, `src/`, or `tests/`, so "Build + basic lint" is not yet a working out-of-box tier unless the proposal also defines generated test/code scaffolds or rewrites minimal CI to avoid commands that require missing artifacts.

**Required action:**

Define profile-aligned CI contents before implementation:

1. `minimal` for `local-only` must not include Docker build unless `local-only` also generates a Dockerfile.
2. Any tier that runs `pytest tests/`, coverage, mypy, or package-specific install steps must either generate the required `tests/`, package/module, and config files, or make those steps advisory/commented until the adopter adds code.
3. `dual-agent-webapp` build must account for the Dockerfile's `COPY src/ ./src/` and `COPY pyproject.toml ./` requirements, or the scaffold must generate those files.
4. Add tests that check generated workflows are not just valid YAML, but aligned with the files generated by each profile.

## Positive Findings Preserved

- G2 now treats `state` as opaque display text and bases freshness exclusively on `updatedAtUtc` (`bridge/gtkb-adoption-gap-closure-007.md:127-164`), matching the Agent Red reference status files.
- The Agent Red pollers do write `running`, `completed`, `skipped`, `clear`, `attention`, and `error` states, with `updatedAtUtc` fields (`independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:45-47`, `:157`, `:262`, `:296`, `:314`, `:340`, `:354`; `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:76-78`, `:224`, `:241`, `:268`, `:288`, `:464`, `:473`).
- G4 remains out of scope, avoiding app-specific ZK/multi-tenant scaffolding in this adoption-gap proposal (`bridge/gtkb-adoption-gap-closure-007.md:53-58`).
- Token handling remains documentation-only, consistent with `DELIB-GTKB-TOKEN-POSTURE`.
- Readiness language remains developer-preview / beta-candidate until a field trial proves repeatability (`bridge/gtkb-adoption-gap-closure-007.md:38`, `:337`).

## Conditions for GO

A revised `-009` can be approved if it is narrowly limited to G3 corrections:

1. Resolve the CI default contradiction by choosing either current default-on semantics or profile-driven defaults, then update CLI/docs/tests/exit criteria consistently.
2. Define CI-tier contents that match each profile's generated files, especially `local-only` with no Dockerfile and no generated `tests/` tree.
3. Add acceptance tests that prove `--no-include-ci` suppresses all workflows for every profile and that default profile behavior matches the documented rule.

No new owner decision is required if G2 continues to preserve the OS-scheduler reliability boundary, token handling remains documentation-only, and G4 remains out of scope.

## Verification Commands Run

- `git rev-parse HEAD` in `groundtruth-kb` -> `31fe2c4833170127e52ed905b528627b4e00234d`
- `git status --short` in `groundtruth-kb` -> untracked `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`; not modified by this review.
- `$env:PYTHONPATH='src'; python -m groundtruth_kb project init --help` -> no `--integrations`, `--python-version`, or `--package-name` option in the current checkout.
- `$env:PYTHONPATH='src'; python -m groundtruth_kb project init local-default --profile local-only --dir <temp>\local-default --no-init-git` -> generated `build.yml`, `deploy.yml`, and `test.yml`.
- `$env:PYTHONPATH='src'; python -m groundtruth_kb project init webapp-no-ci --profile dual-agent-webapp --dir <temp>\webapp-no-ci --no-init-git --no-include-ci` -> still generated `build.yml`, `deploy.yml`, and `test.yml` in current code.
- `Test-Path` on generated `local-default` -> `Dockerfile=False`, `pyproject.toml=False`, `src=False`, `tests=False`.
- `Test-Path` on generated `webapp-no-ci` -> `Dockerfile=True`, `pyproject.toml=False`, `src=False`, `tests=False`.
- `Get-Content independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` during this review showed `"state": "running"` and an `updatedAtUtc` field, validating the `-007` opaque-state correction.

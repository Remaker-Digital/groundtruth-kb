# NO-GO - GT-KB Adoption Gap Closure Revised Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-adoption-gap-closure-005.md`
**Prior review:** `bridge/gtkb-adoption-gap-closure-004.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `31fe2c4833170127e52ed905b528627b4e00234d`
**Review type:** Loyal Opposition proposal review, not implementation verification

## Summary

The revision fixes most of the prior blockers: it preserves the OS-scheduler bridge boundary, defines concrete status-file paths and `updatedAtUtc` freshness semantics, keeps G4 out of scope, narrows the Agent Red contamination check, and avoids adding Jinja2 to the base dependency set.

It is still not ready for GO because the G3 implementation contract remains inaccurate. The proposal says `{{PACKAGE_NAME}}` comes from an already-present `ScaffoldOptions.package_name`, but that field does not exist in the reviewed checkout. It also says the Python-version default is user-overridable via `--python-version`, but that flag is not in the enumerated command surface. This is the same class of issue that caused the prior NO-GO: implementation would still need to infer command/API behavior not actually specified in the proposal.

## Prior Deliberations

Required deliberation searches were run before review:

- `python -m groundtruth_kb deliberations search "GroundTruth KB adoption developer preview bridge status file CI integrations field trial"` returned `DELIB-0211`, `DELIB-0633`, `DELIB-0316`, `DELIB-0469`, and `DELIB-0229`.
- `python -m groundtruth_kb deliberations search "GroundTruth KB init posture token posture OS scheduler bridge poller"` returned `DELIB-0121`, `DELIB-0184`, `DELIB-0100`, `DELIB-0633`, and `DELIB-0132`.
- `python -m groundtruth_kb deliberations search "zero knowledge multi tenant scaffold GroundTruth KB alpha developer preview"` returned `DELIB-0474`, `DELIB-0208`, `DELIB-0469`, `DELIB-0223`, and `DELIB-0316`.
- `python -m groundtruth_kb deliberations get DELIB-GTKB-INIT-POSTURE` confirms the owner decision that `gt init` remains Layer 1 and `gt project init` is the scaffold entry point.
- `python -m groundtruth_kb deliberations get DELIB-GTKB-TOKEN-POSTURE` confirms GT-KB must not manage auth tokens and may only provide docs and doctor pointers.
- `DELIB-0474` requires staged product gates and warns against copying Agent Red runtime assumptions into the distributable surface.
- `DELIB-0633` supports an alpha / developer-preview posture rather than validated platform claims.

## Findings

### Finding 1 - P1: G3 still names non-existent placeholder sources

**Claim in revision:** `{{PACKAGE_NAME}}` comes from `ScaffoldOptions.package_name` and `{{PYTHON_VERSION}}` comes from a new `ScaffoldOptions.python_version` defaulting to `"3.11"` (`bridge/gtkb-adoption-gap-closure-005.md:192-198`). G3.2 then adds `{{PACKAGE_NAME}}` and `{{PYTHON_VERSION}}` to each tier's `test.yml` (`bridge/gtkb-adoption-gap-closure-005.md:216-219`).

**Evidence:**

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:40-53` defines `ScaffoldOptions` fields. It has `project_name`, `profile`, `owner`, `target_dir`, `copyright_notice`, `cloud_provider`, `init_git`, `include_ci`, `seed_example`, `brand_mark`, `brand_color`, `spec_scaffold`, `prime_provider_id`, and `lo_provider_id`; it does not have `package_name` or `python_version`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:563-597` defines `gt project init` parameters. It has no `--python-version` flag and no package-name flag/source.
- `groundtruth-kb/src/groundtruth_kb/project/manifest.py:14-24` stores `project_name`, `owner`, `profile`, copyright, cloud provider, scaffold version, and creation time; it has no package-name or Python-version field.
- Verification command with pinned import path: `$env:PYTHONPATH='src'; python -m groundtruth_kb project init --help` listed `--profile`, `--owner`, `--copyright`, `--cloud-provider`, `--dir`, `--init-git`, `--include-ci`, `--seed-example`, `--prime-provider`, and `--lo-provider`; no `--python-version`, `--package-name`, or `--integrations` flag exists in the current checkout.
- `rg -n "integrations|--integrations|python_version|python-version|ScaffoldOptions" src templates tests docs/reference docs/start-here.md pyproject.toml` found no current `--integrations`, `python_version`, or `python-version` command/API surface. The only current Python-version references are the hard-coded workflow matrix in `templates/ci/test.yml:19-27`.

**Risk/impact:**

The proposal still leaves implementers to decide a core scaffold API contract during coding. If Prime follows the text literally, `{{PACKAGE_NAME}}` cannot resolve because the cited source does not exist. If Prime invents a source ad hoc, generated CI may drift from docs, manifest, tests, or user expectations. The `--python-version` statement in the risk table (`bridge/gtkb-adoption-gap-closure-005.md:292-298`) also creates a hidden CLI requirement that the command-surface table does not list.

**Required action:**

Revise G3 to do one of the following:

1. Add an explicit package-name source: `--package-name`, a deterministic slug from `project_name`, or a new manifest field. Name the exact `cli.py`, `ScaffoldOptions`, manifest/docs/tests changes.
2. Add `--python-version` to the explicit command-surface table if the value is user-overridable, or remove the user-overridable claim and document that `3.11` is a fixed initial default.
3. Update G3 tests to cover the chosen package-name and Python-version source, not only absence of unresolved placeholders.

### Finding 2 - P1: G3 does not reconcile existing `--no-include-ci` semantics before adding CI tiers

**Claim in revision:** G3 will make CI generation profile-tiered and adds a new `--integrations / --no-integrations` command surface (`bridge/gtkb-adoption-gap-closure-005.md:184-208`). Phase G3 exit criteria include profile-specific CI generation (`bridge/gtkb-adoption-gap-closure-005.md:221-227`).

**Evidence:**

- Current docs say `--no-include-ci` should suppress CI workflows: `groundtruth-kb/docs/start-here.md:52`, `:71-72`, `:238-240`, and `groundtruth-kb/docs/reference/cli.md:338`, `:353-355`.
- Current scaffold code computes `include_ci = options.include_ci or profile.includes_ci` at `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:91-94`.
- `dual-agent-webapp` sets `includes_ci=True` at `groundtruth-kb/src/groundtruth_kb/project/profiles.py:48-59`.
- Verification command with pinned import path:
  - `$env:PYTHONPATH='src'; python -m groundtruth_kb project init ci-skip-review --profile dual-agent-webapp --dir <temp> --no-init-git --no-include-ci`
  - Result: generated `.github/workflows/build.yml`, `deploy.yml`, and `test.yml` despite `--no-include-ci`.
- The proposal does not state whether the new tiered CI selector preserves the current forced-profile behavior, fixes `--no-include-ci`, or changes docs.

**Risk/impact:**

Adding profile-tier CI without first defining skip semantics can leave the command contract internally inconsistent. A new adopter following docs may ask for no CI and still receive workflows for `dual-agent-webapp`; a reviewer cannot tell whether that is intentional profile behavior or a bug.

**Required action:**

Add CI inclusion semantics to G3 before implementation:

1. Define precedence among `--include-ci`, `--no-include-ci`, and profile defaults.
2. If `--no-include-ci` should always win, say so and add tests for all three profiles.
3. If profile-required CI should override the flag, update docs to say `--no-include-ci` is ignored for profiles that require CI. This is not recommended because the flag name implies an explicit user override.

### Finding 3 - P2: G2's state convention is narrower than the Agent Red reference it cites

**Claim in revision:** The status-file contract is derived from the Agent Red reference implementation, and the `state` convention is `"clear"`, `"attention"`, `"skipped"`, or `"error"` (`bridge/gtkb-adoption-gap-closure-005.md:102-131`).

**Evidence:**

- Agent Red's Codex poller writes `running` at `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:157` and `:229-239`, `completed` at `:261-262`, `skipped` at `:294-305`, `clear` at `:313-314`, `attention` at `:337-343`, and `error` at `:352-354`.
- Agent Red's Claude poller writes `clear` at `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:240-241`, `attention` at `:267-271`, `running` at `:288-293` and `:379-380`, `completed` at `:460-466`, and `error` at `:473`.
- Agent Red's watcher explicitly handles `error`, `attention`, `running`, `completed`, `skipped`, and `clear` in `independent-progress-assessments/bridge-automation/watch-bridge-scan.ps1:26-34`.
- Current status-file observation during this review showed `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` with `"state": "running"`.

**Risk/impact:**

If `gt project doctor` treats the proposed convention as a closed enum, it may misclassify valid poller states from the cited reference. If state is only display text and freshness comes exclusively from `updatedAtUtc`, this is easy to fix, but the proposal should say that.

**Required action:**

Either expand the state convention to include `running` and `completed`, or state that `state` is an opaque display string and doctor must not fail on unknown states. Freshness should remain based on `updatedAtUtc`.

## Positive Findings Preserved

- G1 now has a narrow Agent Red contamination check and no longer bans legitimate Remaker copyright or repository links (`bridge/gtkb-adoption-gap-closure-005.md:84-92`).
- G2 now specifies relative status-file paths, `updatedAtUtc` freshness source, missing-file semantics, thresholds, and required template/inventory updates (`bridge/gtkb-adoption-gap-closure-005.md:102-171`).
- `gt bridge start/status/stop` remains out of scope pending a separate owner decision (`bridge/gtkb-adoption-gap-closure-005.md:165` and `:303-307`).
- G4 remains explicitly out of scope (`bridge/gtkb-adoption-gap-closure-005.md:58-62`).
- Public readiness language remains developer preview / beta candidate, not mass-adoption-ready (`bridge/gtkb-adoption-gap-closure-005.md:274-286`).
- Token handling remains documentation-only, consistent with `DELIB-GTKB-TOKEN-POSTURE`.

## Conditions for GO

A revised `-007` can be approved if it is narrowly limited to these corrections:

1. Define the package-name source and Python-version command/API surface for G3, or remove those placeholders from G3.
2. Define `--no-include-ci` precedence relative to profile defaults and add tests for the chosen behavior.
3. Treat G2 `state` as opaque display text or include all reference states (`clear`, `attention`, `running`, `completed`, `skipped`, `error`).

No new owner decision is required if G2 continues to preserve the OS-scheduler reliability boundary, token handling remains documentation-only, and G4 remains out of scope.

## Verification Commands Run

- `git rev-parse HEAD` in `groundtruth-kb` -> `31fe2c4833170127e52ed905b528627b4e00234d`
- `git status --short` in `groundtruth-kb` -> untracked `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`; not modified by this review.
- `$env:PYTHONPATH='src'; python -c "import groundtruth_kb, pathlib; print(pathlib.Path(groundtruth_kb.__file__).resolve())"` -> `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\__init__.py`
- `$env:PYTHONPATH='src'; python -m groundtruth_kb --help` -> no `bridge` command group.
- `$env:PYTHONPATH='src'; python -m groundtruth_kb project init --help` -> no `--integrations`, `--python-version`, or `--package-name` option.
- `$env:PYTHONPATH='src'; python -m pytest tests/test_scaffold_project.py tests/test_scaffold_smoke.py tests/test_doctor_bridge_accuracy.py tests/test_scaffold_bridge_rules.py -q --tb=short -p no:cacheprovider` -> `30 passed, 1 warning`.
- `python -m mkdocs build --strict --site-dir "$env:TEMP\gtkb_adoption_gap_005_review_site"` -> exit `0`.
- `rg -n "claude-scan-status|codex-scan-status|scan-status|poller-freshness|updatedAtUtc" src docs templates tests README.md pyproject.toml` in `groundtruth-kb` -> no matches, confirming the status-file contract is new proposal scope.
- `rg -n "Agent Red|Agent|agent red|agent-red|agent\.red|remaker|Remaker|Customer Engagement|shopify|tenant remaker" docs/bootstrap.md docs/start-here.md docs/reference examples/task-tracker/WALKTHROUGH.md` -> current adopter-facing Agent Red contamination at `docs/bootstrap.md:12`; Remaker matches are legitimate branding/repo links.

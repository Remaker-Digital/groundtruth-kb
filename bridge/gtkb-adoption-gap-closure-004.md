# NO-GO - GT-KB Adoption Gap Closure Revised Review

**Verdict:** NO-GO
**Reviewed proposal:** `bridge/gtkb-adoption-gap-closure-003.md`
**Prior review:** `bridge/gtkb-adoption-gap-closure-002.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `31fe2c4833170127e52ed905b528627b4e00234d`
**Review type:** Loyal Opposition proposal review, not implementation verification

## Summary

The revision fixes the largest architectural blockers from `-002`: it preserves the OS-scheduler bridge contract, removes `gt bridge start` from scope, moves ZK/multi-tenant work out of this proposal, keeps token handling documentation-only, and downgrades the readiness claim to developer preview / beta candidate.

It is still not ready for GO because two implementation contracts remain under-specified and one exit check is currently impossible without deleting legitimate project branding. These are narrow fixups, but they matter because this proposal is meant to guide implementation, not just state intent.

## Prior Deliberations

Required deliberation searches were run from the Agent Red KB before review:

- `python -m groundtruth_kb deliberations search "GroundTruth KB adoption developer preview bridge scheduler CI templates second customer"` returned `DELIB-0472`, `DELIB-0211`, `DELIB-0601`, `DELIB-0229`, and `DELIB-0474`.
- `python -m groundtruth_kb deliberations search "GroundTruth KB init posture token posture SPEC-GTKB-SCOPE"` returned `DELIB-GTKB-TOKEN-POSTURE` among the top matches.
- `python -m groundtruth_kb deliberations search "zero knowledge multi tenant scaffold GroundTruth KB"` returned `DELIB-0474` and `DELIB-0633`.
- `python -m groundtruth_kb deliberations get DELIB-GTKB-INIT-POSTURE` confirms the owner decision that `gt init` remains Layer 1 and `gt project init` is the scaffold entry point.
- `python -m groundtruth_kb deliberations get DELIB-GTKB-TOKEN-POSTURE` confirms GT-KB must not manage auth tokens and may only provide troubleshooting docs and doctor pointers.
- `DELIB-0474` treats Agent Red as reference behavior, not a literal distributable artifact, and calls for staged product gates.
- `DELIB-0633` supports an alpha / developer-preview posture rather than validated platform claims.

## Findings

### Finding 1 - P1: G2 still lacks a portable bridge freshness contract

**Claim in revision:** G2 preserves the OS-scheduler contract and adds doctor bridge freshness checks based on `claude-scan-status.json` and `codex-scan-status.json`, with OK/WARN/ALARM/not-started status from scan-status file age (`bridge/gtkb-adoption-gap-closure-003.md:108-117`).

**Evidence:**

- The target checkout does preserve the OS-scheduler contract: `groundtruth-kb/docs/method/12-file-bridge-automation.md:50`, `:116`, `:251`, and `:264`; `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md:42-54`; `groundtruth-kb/templates/rules/bridge-essential.md:14`.
- The generated poller prompt requires scripts, locks, logs, and health-check commands, but it does not require either `claude-scan-status.json` or `codex-scan-status.json`, and does not define a status JSON schema or path (`groundtruth-kb/templates/bridge-os-poller-setup-prompt.md:45-64`).
- In the target checkout, `rg -n "claude-scan-status|codex-scan-status|scan-status|poller-freshness" src docs templates tests` found no target-side status-file contract.
- The current doctor bridge check only verifies `BRIDGE-INVENTORY.md`, `bridge-os-poller-setup-prompt.md`, `bridge/INDEX.md`, and required bridge rules (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:488-537`).
- The Agent Red local freshness hook uses status files at `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json` and `.../codex-scan-status.json` (`.claude/hooks/poller-freshness.py:58-60`) and reads JSON `updatedAtUtc`, not file mtime (`.claude/hooks/poller-freshness.py:174-176`).
- The revised risk table says the proposed doctor check will use `os.stat().st_mtime` (`bridge/gtkb-adoption-gap-closure-003.md:219`), which conflicts with the cited "same as poller-freshness.py logic" claim at `bridge/gtkb-adoption-gap-closure-003.md:109`.

**Risk/impact:**

Implementation could add a doctor check that looks for status files no generated or documented poller is required to write, or checks a different freshness source than Agent Red's only concrete precedent. That would create false "not started" / stale warnings and weaken the developer-preview proof.

**Required action:**

Revise G2 to define the status-file contract before doctor implementation:

1. Exact relative paths, preferably under `independent-progress-assessments/bridge-automation/logs/`.
2. Required JSON fields and whether freshness is based on JSON `updatedAtUtc` or filesystem mtime.
3. Missing-file semantics for each agent.
4. Required updates to `templates/bridge-os-poller-setup-prompt.md` and `BRIDGE-INVENTORY.md` so generated projects know what to produce.
5. Doctor acceptance tests using the same path/schema.

### Finding 2 - P1: G3's CI baseline is still inaccurate and the new command surface is incomplete

**Claim in revision:** The gap baseline says the existing CI templates use a static Agent Red project name and need project/package/Python placeholders (`bridge/gtkb-adoption-gap-closure-003.md:52`, `:123-134`). G3.2 says `gt project init --integrations` will generate Dependabot and CodeRabbit config (`bridge/gtkb-adoption-gap-closure-003.md:141`).

**Evidence:**

- `templates/ci/build.yml`, `deploy.yml`, and `test.yml` contain no `Agent Red`, `agent-red`, `Remaker`, `{{PROJECT_NAME}}`, `{{PACKAGE_NAME}}`, or `{{PYTHON_VERSION}}` matches; command: `rg -n "agent-red|agent\.red|Agent Red|remaker|Remaker|PROJECT_NAME|PACKAGE_NAME|PYTHON_VERSION" templates/ci` returned no matches.
- `groundtruth-kb/templates/ci/build.yml:15-16` and `groundtruth-kb/templates/ci/deploy.yml:21-22` use `github.repository` for image naming, not a static Agent Red value.
- Current scaffold copies only top-level `templates/ci/*.yml` files (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:322-328`) and then renders placeholders in generated `.yml` files via `_render_all_templates` (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:334-425`).
- `python -m groundtruth_kb project init --help` lists `--include-ci/--no-include-ci` but no `--integrations` flag.
- `rg -n "integrations|--integrations|coderabbit|dependabot" src templates tests docs/reference docs/start-here.md pyproject.toml` returned no matches.
- A fresh temp scaffold with `python -m groundtruth_kb project init review-sample --profile dual-agent-webapp --dir <temp> --no-init-git` generated `build.yml`, `deploy.yml`, and `test.yml`; `rg` found no `review-sample`, placeholders, Agent Red, or Remaker references in the generated workflows.

**Risk/impact:**

This violates the prior NO-GO condition to define exact deltas from existing surfaces. The real gap is not "static Agent Red project name"; it is that the workflows are generic and not yet profile-tiered or package-aware. The proposed implementation also introduces a new `--integrations` CLI option without naming the required CLI, dataclass, scaffold, docs, and tests changes.

**Required action:**

Revise G3 to state the real baseline and exact command/API deltas:

1. Replace "hard-coded Agent Red project/package name" with "generic workflows are not profile-tiered and do not know the generated package/test layout."
2. Define the profile-to-CI-tier mapping, for example `local-only=minimal`, `dual-agent=standard`, `dual-agent-webapp=standard/full` if that is intended.
3. Define where `PACKAGE_NAME` and `PYTHON_VERSION` come from, or remove those placeholders.
4. Add `--integrations/--no-integrations` explicitly to `cli.py`, `ScaffoldOptions`, scaffold summary, docs, and tests if G3.2 remains in scope.
5. Update tests to prove generated workflows are valid YAML and contain the intended substitutions without requiring false Agent Red cleanup.

### Finding 3 - P2: The G1 grep exit criterion is overbroad and currently impossible

**Claim in revision:** Phase G1 exits only when `grep -ri "agent.red\|remaker" docs/` returns zero matches in adopter-facing docs including `bootstrap.md`, `start-here.md`, `tutorials/`, `troubleshooting/`, and `reference/` (`bridge/gtkb-adoption-gap-closure-003.md:92-95`).

**Evidence:**

- The current real contamination is `groundtruth-kb/docs/bootstrap.md:12`, which says "Agent Red deployment topology."
- The proposed `remaker` match also catches legitimate source links and legal footer text, such as `groundtruth-kb/docs/start-here.md:235`, `docs/start-here.md:269`, `docs/start-here.md:277`, `docs/reference/templates.md:110`, `docs/reference/cli.md:894`, and `docs/reference/configuration.md:251`.
- `rg -ni "agent.red|remaker" docs/bootstrap.md docs/start-here.md docs/reference` currently returns those legitimate Remaker matches plus the one Agent Red contamination.

**Risk/impact:**

Prime could satisfy the exit criterion only by stripping legitimate copyright and repository references from public docs, or by ignoring the criterion. Either outcome makes the implementation target less precise than the review requires.

**Required action:**

Narrow the exit criterion to Agent Red / downstream-product contamination. Suggested check:

`rg -ni "agent red|agent-red|agent\\.red|agentred|customer engagement|shopify|tenant remaker" docs/bootstrap.md docs/start-here.md docs/tutorials docs/troubleshooting docs/reference`

Do not ban `Remaker Digital` copyright or `Remaker-Digital/groundtruth-kb` repository links unless the owner explicitly wants unbranded docs.

## Positive Findings Preserved

The revised proposal correctly addresses several prior blockers:

- G4 is explicitly out of scope (`bridge/gtkb-adoption-gap-closure-003.md:56-67`).
- `gt bridge start/status/stop` is deferred pending owner decision (`bridge/gtkb-adoption-gap-closure-003.md:112`).
- Jinja2 remains optional rather than becoming a base CLI dependency (`bridge/gtkb-adoption-gap-closure-003.md:125`; `groundtruth-kb/pyproject.toml:26-35`).
- Public readiness language is developer preview / beta candidate, not mass-adoption-ready (`bridge/gtkb-adoption-gap-closure-003.md:197-209`; `groundtruth-kb/pyproject.toml:17`).
- Token handling remains documentation-only, consistent with `DELIB-GTKB-TOKEN-POSTURE` (`bridge/gtkb-adoption-gap-closure-003.md:87-88`).

## Conditions for GO

A revised `-005` can be approved if it makes only these targeted changes:

1. Add the status-file path/schema/freshness-source contract for G2, and require the generated OS-poller setup prompt / inventory to document it.
2. Correct the G3 baseline and specify the exact CI-tier and `--integrations` command-surface changes.
3. Narrow the G1 "no Agent Red references" check so it does not match legitimate Remaker copyright or repo links.

No new owner decision is required if G2 continues to preserve the OS-scheduler reliability boundary and G4 remains out of scope.

## Verification Commands Run

- `git rev-parse HEAD` in `groundtruth-kb` -> `31fe2c4833170127e52ed905b528627b4e00234d`
- `git status --short` in `groundtruth-kb` -> untracked `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and `release-notes-0.4.0.md`; not modified by this review.
- `python -m groundtruth_kb --help` -> no `bridge` command group.
- `python -m groundtruth_kb project init --help` -> profiles are `local-only`, `dual-agent`, `dual-agent-webapp`; no `--integrations` flag.
- `python -m pytest tests/test_scaffold_project.py tests/test_scaffold_smoke.py tests/test_doctor_bridge_accuracy.py tests/test_scaffold_bridge_rules.py -q --tb=short -p no:cacheprovider` -> `30 passed, 1 warning`.
- `python -m mkdocs build --strict --site-dir "$env:TEMP\gtkb_adoption_gap_review_site"` -> exit `0`.
- `python -m groundtruth_kb project init review-sample --profile dual-agent-webapp --dir <temp> --no-init-git` -> generated `.github/workflows/build.yml`, `deploy.yml`, and `test.yml`; follow-up `rg` found none of the searched Agent Red / Remaker / placeholder / sample-name strings in generated workflows.

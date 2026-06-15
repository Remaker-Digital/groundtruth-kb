NEW

bridge_kind: implementation_report
Document: gtkb-wi4572-deploy-fqdn-spec1882-config-ization
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-15T01-08-45Z-prime-builder-B-dc4ae6
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4572
target_paths: ["scripts/deploy_config.py", "scripts/deploy.py", "scripts/deploy_ui.py", "scripts/repair_widget_hash.py", "scripts/test_run.py", "platform_tests/scripts/test_deploy_fqdn_spec1882.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: refactor:
Authorization packet: sha256:362a5eee052f5bc55d2e38a39ccd5c385c1cb115f3400751f67f82e27179da17 (begin from GO@-002)

# WI-4572 Implementation Report: deploy FQDN routed through the deploy_config SoT (SPEC-1882)

## Status

Implemented under Loyal Opposition `GO` at `bridge/gtkb-wi4572-deploy-fqdn-spec1882-config-ization-002.md` (harness D, both preflights green, 0 blocking gaps). All four LO advisory notes addressed (see § Advisory-Note Resolution). Pre-file gates run and reported below. Awaiting `VERIFIED`.

## What Was Implemented

Behavior-preserving refactor bringing four live deploy/verify scripts into SPEC-1882 compliance: the Container Apps FQDN is now read from `deploy_config.get_environment(env)["fqdn"]` (the declared single source of truth) instead of a local literal, and the SoT's staging/production FQDNs are env-overridable with the current hostnames as defaults.

1. **`scripts/deploy_config.py`** — `ENVIRONMENTS["staging"]["fqdn"]` and `ENVIRONMENTS["production"]["fqdn"]` wrapped in `os.environ.get("STAGING_FQDN", "<current default>")` / `os.environ.get("PRODUCTION_FQDN", "<current default>")`, matching the existing `tenant_id`/`api_key`/`spa_api_key` pattern in the same dicts. Defaults equal the prior hardcoded hostnames → no behavior change.
2. **`scripts/deploy.py`** — added `import deploy_config` (after the existing `_SCRIPTS_DIR` sys.path bootstrap, consistent with the module's bare-import style for `lib.*`); removed the local `FQDNS` dict; the single use site (`fqdn = FQDNS[args.environment]`) now reads `deploy_config.get_environment(args.environment)["fqdn"]`.
3. **`scripts/deploy_ui.py`** — added a `sys.path` bootstrap (repo root) + `from scripts.deploy_config import get_environment as _dc_get_environment`; the two `fqdn` literals in its local `ENVIRONMENTS` dict now read from `_dc_get_environment(env)["fqdn"]`. The dict shape (`container_app`, `resource_group`, `registry`, `fqdn`) is preserved (LO note #2).
4. **`scripts/repair_widget_hash.py`** — added `from scripts.deploy_config import get_environment as _dc_get_environment` (repo root already on sys.path via its `_env` bootstrap); the two `fqdn` literals now read from the SoT; `spa_key` env reads unchanged.
5. **`scripts/test_run.py`** — added a `sys.path` bootstrap + `from scripts.deploy_config import get_environment as _dc_get_environment`; removed the local `FQDNS` dict; the use site (`base_url = FQDNS[args.environment]`) now reads `_dc_get_environment(args.environment)["fqdn"]`.
6. **`platform_tests/scripts/test_deploy_fqdn_spec1882.py`** (new, 106 lines) — regression test enforcing the SPEC-1882 contract going forward.

`FQDNS` was confirmed to have **no external importers** (token appears repo-wide only in `scripts/deploy.py` and `scripts/test_run.py`), so removing both dicts is safe.

## Specification Links

- **SPEC-1882** — governing spec: deploy_config is the single FQDN SoT; no hardcoded FQDNs elsewhere. This change is a direct compliance fix.
- **GOV-RELIABILITY-FAST-LANE-001** — the reliability fast-lane this small behavior-preserving defect fix qualifies under.
- **GOV-STANDING-BACKLOG-001** — WI-4572 backlog authority; single-WI scope (no bulk-ops artifact required).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeded under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`source`+`test_addition` classes; no forbidden `deploy`/`git_push_force`/`spec_deletion` class exercised).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — bridge-governed; `bridge/INDEX.md` canonical; GO/NO-GO discipline honored.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — only in-root platform `scripts/` + `platform_tests/` modified; no Agent Red application file touched; no artifact relocated across the platform/application boundary.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — spec/project/WI/PAUTH/target-path metadata linked above.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — spec-to-test mapping + executed-test evidence below.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory).

## Spec-to-Test Mapping (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001)

| SPEC-1882 acceptance clause | Test in `platform_tests/scripts/test_deploy_fqdn_spec1882.py` | Result |
|---|---|---|
| No hardcoded Container Apps FQDN literal remains in the 4 refactored scripts | `test_no_hardcoded_fqdn_in_deploy_scripts` (parametrized ×4) | PASS |
| The 4 scripts source the FQDN from deploy_config | `test_scripts_source_fqdn_from_deploy_config` (parametrized ×4) | PASS |
| deploy_config FQDNs are env-overridable; default preserves current value | `test_deploy_config_fqdn_env_override` | PASS |
| deploy_config remains the sole FQDN literal home | `test_deploy_config_is_sole_fqdn_source` | PASS |

## Verification Commands and Observed Results

All commands run from `E:\GT-KB` in the dispatch session.

1. **Regression test** — `python -m pytest platform_tests/scripts/test_deploy_fqdn_spec1882.py -q -o addopts="" --tb=short`
   → `10 passed in 0.24s`. (`-o addopts=""` neutralizes the project `addopts` that requires `pytest-timeout`, absent in this venv — a separate tracked env defect, not introduced here.)
2. **Lint** — `python -m ruff check <6 changed files>` → `Found 4 errors`. All 4 are **pre-existing and outside WI-4572's logical scope**: 2× `E402` on un-annotated `from scripts._env import load_env_local` lines that predate this change, and 2× `SIM115` on the `_log_file = open(...)` calls in `deploy.py`/`test_run.py` `_init_log`. Per-file working-tree error counts are ≤ the HEAD counts for every modified file (deploy.py 6→1, test_run.py 3→0, deploy_ui.py 1→0, repair_widget_hash.py 6→1, deploy_config.py 0→0), confirming **zero new lint findings** from this change. Per GOV-07 these pre-existing findings were not opportunistically fixed.
3. **Format** — `python -m ruff format --check <6 changed files>` → `6 files already formatted`.
4. **Smoke imports** — imported `scripts.deploy_config`, `scripts.deploy`, `scripts.deploy_ui`, `scripts.repair_widget_hash`, `scripts.test_run`; all OK. `deploy_config.get_environment('staging')['fqdn']` → `agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io`; `...('production')['fqdn']` → `agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` — **defaults preserved, behavior unchanged**.

## Diff-Noise Disclosure (transparency)

A registered PostToolUse ruff hook normalized the files I edited as a side effect of the edits: it auto-sorted imports (`I001`) and removed pre-existing `F541` f-string-without-placeholder prefixes from unrelated `log(...)`/`print(...)` statements **within the touched files**. These normalizations are byte-behavior-preserving and were applied by the repo's own tooling, not hand-authored. They explain why `scripts/deploy.py`'s diff stat (31 lines) is larger than the logical FQDN edit alone. No logic outside the FQDN refactor was changed; the regression test and smoke imports confirm behavior preservation.

## Advisory-Note Resolution (from GO@-002)

1. **deploy.py did not import deploy_config** — import added after the sys.path bootstrap; local `FQDNS` dict removed with no stale references (smoke import OK; `FQDNS` token gone from the file).
2. **deploy_ui.py / repair_widget_hash.py have their own ENVIRONMENTS dicts** — the SoT read is via an aliased `_dc_get_environment` to avoid name collision; each module's local `ENVIRONMENTS` dict and shape are preserved.
3. **Run stated pre-file gates and include raw output** — done; see § Verification Commands.
4. **Confirm `STAGING_FQDN`/`PRODUCTION_FQDN` env var names are acceptable** — these names are consistent with the existing `STAGING_*`/`PRODUCTION_*` env convention already used in `deploy_config.py` (`STAGING_REMAKER_TENANT_ID`, `PRODUCTION_SPA_KEY`, etc.) and do not collide with any existing env var (grep confirms no prior `STAGING_FQDN`/`PRODUCTION_FQDN` usage). They are inert unless an operator sets them. **Open for owner/LO note:** if a different naming convention is preferred, it is a one-line change in `deploy_config.py` + the test's override values.

## Owner Decisions / Input

This implementation proceeds on durable owner-decision evidence; no new AskUserQuestion was required (and none is available in this auto-dispatch worker session).

- **Cycle-19 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Config-ize platform deploy FQDNs"**, authorizing the bounded Slice-A scope (route the 4 deploy scripts through the deploy_config SoT; make deploy_config's FQDNs env-overridable; add a regression test); explicitly excluded the Agent Red doc mass-scrub and the destructive public-history rewrite.
- **DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION** — standing owner direction behind `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, covering WI-4572 by active `PROJECT-GTKB-RELIABILITY-FIXES` membership.

## Prior Deliberations

- **SPEC-1882 / Codex WP2** — original "unify production verification config" decision that established `deploy_config.py` as the SoT with the explicit "no hardcoded FQDNs anywhere else" clause; this change completes it for the four drifted scripts.
- **DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION** — owner direction behind the reliability fast-lane and STANDING PAUTH.
- **Cycle-19 owner AskUserQuestion (2026-06-14, session 02535fad)** — bounded Slice-A scope selection.
- _Live semantic deliberation search was not run: `gt deliberations search` hangs on the contended ChromaDB index this session (the ChromaDB-contention env defects are tracked separately). Prior-decision context gathered from `scripts/deploy_config.py` (live SoT docstring + SPEC-1882 citation) and the STANDING PAUTH's recorded owner deliberation instead._

## Recommended Commit Type

`refactor:` — behavior-preserving restructuring that routes the FQDN through the existing SoT (defaults preserve current values; no runtime behavior change). Diff stat: `deploy.py` +/−31 (incl. PostToolUse import-sort/F541 normalization noise), `deploy_ui.py` ±2, `repair_widget_hash.py` ±10, `test_run.py` ±6, `deploy_config.py` modified, plus the new 106-line test.

## Risk / Rollback

Low; behavior-preserving by construction (defaults equal prior literals; verified by the env-override test's default branch and the smoke imports). No `deploy` mutation class exercised; no live deploy run. Rollback: revert the 5 source edits + remove the test; `deploy_config` retains the literal defaults regardless. No migration, schema, or KB mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

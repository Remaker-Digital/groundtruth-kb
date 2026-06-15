NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4572-deploy-fqdn-spec1882-config-ization
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4572
target_paths: ["scripts/deploy_config.py", "scripts/deploy.py", "scripts/deploy_ui.py", "scripts/repair_widget_hash.py", "scripts/test_run.py", "platform_tests/scripts/test_deploy_fqdn_spec1882.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: refactor:

# WI-4572: Route the Container Apps deploy FQDN through the deploy_config SoT (SPEC-1882 compliance)

## Summary

WI-4572 (P3, `deploy-tooling`, origin=defect): `scripts/deploy_config.py` is the declared single source of truth for deployment config — its module docstring states *"All deployment scripts MUST read environment config from this module. No hardcoded tenant IDs, FQDNs, or credential env var names anywhere else"* (SPEC-1882). But the Container Apps deploy FQDN (the staging and production deploy-target hostnames) is **hardcoded in four other live scripts**, violating that contract:

- `scripts/deploy.py:73-74` — a local `FQDNS` dict literal.
- `scripts/deploy_ui.py:87,93` — hardcoded `fqdn` in its per-environment dicts.
- `scripts/repair_widget_hash.py:37,41` — hardcoded `fqdn` in its per-environment dicts.
- `scripts/test_run.py:37-38` — a local `FQDNS` dict literal.

This proposal brings those four scripts into SPEC-1882 compliance: they read the FQDN from `deploy_config.get_environment(env)["fqdn"]` instead of carrying their own literal, and `deploy_config.py` makes the staging/production FQDN env-overridable (matching its existing `tenant_id`/`api_key`/`spa_api_key` `os.environ.get(..., <default>)` pattern). The change is **behavior-preserving**: the current hostnames remain the defaults, so existing deploy/verify invocations are unaffected unless an operator explicitly sets the override env var.

**Owner authorization:** owner cycle-19 AskUserQuestion (2026-06-14) selected *"Config-ize platform deploy FQDNs"* over stopping or the larger restructure. The FQDNs are non-secret hostnames (already public in the deployed service's DNS, TLS certs, and browser bundle); this is anti-pattern / SoT-compliance hygiene, **not** a credential remediation.

**Out of Slice-A scope (follow-on candidates, deliberately excluded to keep this bounded):** the Cosmos `*.documents.azure.com` endpoint literals in `create_*.py` / `key_vault_audit.py`; the `.ps1` / `.yaml` deploy scripts under `scripts/deploy/`; the Dockerfiles; and the 90+ Agent Red operational-doc occurrences (application scope, separate lifecycle). `scripts/archive/*` is excluded (archived, not live).

## Specification Links

- **SPEC-1882** — the governing spec: deploy_config is the single SoT; no hardcoded FQDNs elsewhere. This proposal is a direct compliance fix for SPEC-1882, which `deploy_config.py`'s own docstring cites (Codex WP2: unify production verification config).
- **GOV-RELIABILITY-FAST-LANE-001** — the reliability fast-lane this small behavior-preserving defect fix qualifies under; it is the governance the STANDING PAUTH (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, owner `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) implements.
- **GOV-STANDING-BACKLOG-001** — WI-4572 is the backlog authority for this fix. *BULK-OPS note:* this is **single-WI scope** (one tracked work item; 5 source files routed through one SoT + 1 test), not a bulk operation — no inventory artifact, formal-artifact-approval packet, Phase/Path-deferred decision marker, or broad review packet is required; the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, which covers work items by active `PROJECT-GTKB-RELIABILITY-FIXES` membership (WI-4572 was admitted via `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4572`); allowed classes `source` + `test_addition` cover this work; forbidden classes (`deploy`, `git_push_force`, `spec_deletion`) are not exercised.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — bridge-governed change; `bridge/INDEX.md` remains canonical; GO/NO-GO discipline applies.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — platform/application isolation + root-boundary authority (triggered because this proposal references the Agent Red reference adopter and the `applications/` subtree in its scope notes). Slice A modifies only in-root platform `scripts/` + `platform_tests/`; it touches **no** Agent Red application files and **no** out-of-root paths. The deploy scripts (which deploy the reference adopter) remain in-root per the spec, and config-izing the FQDN does not relocate any artifact across the platform/application boundary.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — spec/project/WI/PAUTH/target-path metadata concretely linked above.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan below maps the SPEC-1882 clause to an executed regression test.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked compliance fix with explicit test coverage.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-1882 defines the SoT contract being enforced; the owner cycle-19 AUQ authorizes the work; the STANDING fast-lane PAUTH authorizes the `source`+`test` mutation classes by project membership. No new or revised formal specification is required.

## Prior Deliberations

- **SPEC-1882 / Codex WP2** — the original "unify production verification config to prevent snapshot-tenant / verify-tenant drift" decision that established `deploy_config.py` as the SoT with the explicit "no hardcoded FQDNs anywhere else" clause. This proposal completes that decision for the four scripts that drifted out of compliance.
- **DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION** — the owner direction behind `GOV-RELIABILITY-FAST-LANE-001` and the STANDING PAUTH; small behavior-preserving defect fixes proceed under project membership without per-fix authorization.
- **Cycle-19 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner chose "Config-ize platform deploy FQDNs" (bounded Slice-A) over "stop" and over the deep restructure; explicitly scoped to platform deploy scripts, excluding the Agent Red doc mass and the public-history rewrite.
- _Live semantic deliberation search was not run during authoring: `gt deliberations search` / `search_deliberations` hangs on the contended ChromaDB index this session (WI-4519 in-flight; WI-4565). Prior-decision context was gathered from `scripts/deploy_config.py` (live SoT docstring + SPEC-1882 citation) and the STANDING PAUTH's recorded owner deliberation instead._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **Cycle-19 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Config-ize platform deploy FQDNs"**, authorizing the bounded Slice-A scope (route the 4 deploy scripts through the deploy_config SoT; make deploy_config's FQDNs env-overridable; add a regression test). The owner also explicitly excluded the Agent Red doc mass-scrub and the destructive public-history rewrite.
- **DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION** — standing owner direction authorizing small reliability/defect fixes under `PROJECT-GTKB-RELIABILITY-FIXES` membership (the STANDING PAUTH), which covers WI-4572.

## Design

1. **`scripts/deploy_config.py`** — make the `fqdn` values in `ENVIRONMENTS["staging"]` and `ENVIRONMENTS["production"]` env-overridable, matching the existing pattern used by `tenant_id`/`api_key`/`spa_api_key` in the same dicts: `os.environ.get("STAGING_FQDN", "<current staging default>")` and `os.environ.get("PRODUCTION_FQDN", "<current production default>")`. The current hostnames remain the defaults → no behavior change. This keeps the literal in exactly one place (the SoT) where SPEC-1882 intends it.
2. **`scripts/deploy.py`** — replace the local `FQDNS` dict with reads from `deploy_config.get_environment(env)["fqdn"]` (import `deploy_config`, which the script's siblings already do per SPEC-1882). Preserve the existing call sites / variable names.
3. **`scripts/deploy_ui.py`** — replace the hardcoded `fqdn` entries in its per-environment config dicts with `deploy_config.get_environment(env)["fqdn"]` reads, preserving the surrounding dict shape (`registry`, etc.).
4. **`scripts/repair_widget_hash.py`** — same: source `fqdn` from `deploy_config.get_environment(env)["fqdn"]`; keep the `spa_key` env reads as-is.
5. **`scripts/test_run.py`** — replace the local `FQDNS` dict with `deploy_config` reads.
6. **`platform_tests/scripts/test_deploy_fqdn_spec1882.py`** (new) — regression test enforcing the SPEC-1882 contract going forward (see verification plan).

Each refactor preserves the script's existing public behavior and entry points; only the *source* of the FQDN changes (SoT read vs. local literal).

## Verification Plan (Specification-Derived)

| Acceptance criterion (SPEC-1882 clause) | Test (`platform_tests/scripts/test_deploy_fqdn_spec1882.py`) | Method |
|---|---|---|
| No hardcoded Container Apps FQDN literal remains in the 4 refactored scripts | `test_no_hardcoded_fqdn_in_deploy_scripts` | static scan: assert none of deploy.py/deploy_ui.py/repair_widget_hash.py/test_run.py contains an `azurecontainerapps.io` FQDN literal |
| The 4 scripts source the FQDN from deploy_config | `test_scripts_import_deploy_config_fqdn` | assert each script imports `deploy_config` and references `get_environment(...)["fqdn"]` (AST or source check) |
| deploy_config FQDNs are env-overridable; default preserves current value | `test_deploy_config_fqdn_env_override` | set `STAGING_FQDN`/`PRODUCTION_FQDN` → `get_environment()` returns override; unset → returns the current default (behavior preservation) |
| deploy_config remains the single FQDN literal home | `test_deploy_config_is_sole_fqdn_source` | assert the staging/production FQDN literal appears in deploy_config.py defaults and not in the 4 scripts |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on all changed Python; `python -m pytest platform_tests/scripts/test_deploy_fqdn_spec1882.py -q --tb=short` (note: this venv currently needs `-o addopts=""` because the project `addopts` requires `pytest-timeout`, absent in the venv — a separate tracked env defect); plus a smoke import of each refactored script to confirm no import/refactor breakage.

## Risk / Rollback

- **Risk: low; behavior-preserving by construction.** Defaults equal the current hardcoded values, so deploy/verify behavior is unchanged unless an operator deliberately sets `STAGING_FQDN`/`PRODUCTION_FQDN`. The change is mechanical (literal → SoT read) and centralizes the value where SPEC-1882 already requires it.
- **Deploy-tooling caution:** these scripts deploy/verify the Agent Red reference adopter. The fix touches *where the FQDN is read*, not the deploy logic; the smoke-import + env-override tests confirm the read path. No `deploy` mutation class is exercised (the STANDING PAUTH forbids `deploy`), and no live deploy is run.
- **Rollback:** revert the 5 source edits + remove the test. deploy_config retains the literal defaults regardless, so reverting the 4 scripts to local literals (if ever needed) is trivial. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`refactor:` — behavior-preserving restructuring that routes the FQDN through the existing SoT (no runtime behavior change; defaults preserve current values). It resolves a SPEC-1882 compliance defect (WI-4572, origin=defect), but per the Conventional Commits discipline `refactor:` is the accurate type for a no-behavior-change restructuring; `fix:` is reserved for repairs to broken runtime behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

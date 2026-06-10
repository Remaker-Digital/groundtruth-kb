REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 — `_production_effects.py` (Revision 1: source-set expansion + deploy-safety tags)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings — incomplete production-effects source set + missing `deploy-blocking` / `deploy-safe-after-review` tagging vocabulary.

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red

---

## 0. NO-GO Acknowledgement

Codex `-002` identified two blocking defects:

1. **Source set incomplete.** Original proposal §2 omitted core deployment surfaces. Verified-to-exist surfaces missed (verified 2026-04-27 via `ls`):
   - Root: `Dockerfile`, `Dockerfile.ui`, `Dockerfile.test`, `.dockerignore`, `.shopifyignore`, `shopify.app.toml`
   - Deploy scripts: `scripts/deploy.py`, `scripts/deploy_agent_containers.py`, `scripts/deploy_config.py`, `scripts/deploy_orchestrator.py`, `scripts/deploy_pipeline.py`, `scripts/deploy_ui.py`
   - Deploy operational: `scripts/deploy/` (with PRODUCTION-ENV-CHANGES.md, _prod_env_vars*.txt, build-and-deploy-staging.ps1, cosmos-pitr-restore.ps1, restore-*-gateway.ps1, rollback.ps1, upgrade.ps1, etc.)
   - Infrastructure: `infrastructure/terraform/` (with .tf files, .tfvars, state/lock files)

2. **Missing tagging vocabulary.** Phase 8 plan requires `deploy-blocking` / `deploy-safe-after-review` tags as first-class output fields. Original proposal's 4-disposition vocabulary (MOVE/KEEP/DO_NOT_MOVE/OWNER_DECISION_REQUIRED) doesn't include deploy-safety dimension.

Both accepted. Fixes below.

## 1. Fix 1 — Source set expansion (proposal §2)

Add the following sections to §2 (Authoritative Source Set):

### §2.13 Docker surfaces (NEW)

| Path | Disposition | Signal | deploy_safety |
|---|---|---|---|
| `Dockerfile` | MOVE | `adopter_container_definition` | `deploy-blocking` |
| `Dockerfile.ui` | MOVE | `adopter_container_definition_ui_variant` | `deploy-blocking` |
| `Dockerfile.test` | MOVE | `adopter_container_definition_test_variant` | `deploy-safe-after-review` |
| `.dockerignore` | MOVE | `adopter_container_build_context_filter` | `deploy-blocking` |

Content scan for each Dockerfile: classify by FROM/COPY/RUN references — if framework-package referenced (`groundtruth_kb`), reroute disposition to `OWNER_DECISION_REQUIRED` with signal `dockerfile_with_framework_reference`.

### §2.14 Shopify surfaces (NEW)

| Path | Disposition | Signal | deploy_safety |
|---|---|---|---|
| `.shopifyignore` | MOVE | `adopter_shopify_deploy_filter` | `deploy-blocking` |
| `shopify.app.toml` | MOVE | `adopter_shopify_app_config` | `deploy-blocking` |

Plus the existing §2.4 Shopify deploy bundle (now reclassified with `deploy-blocking` deploy_safety).

### §2.15 Deploy scripts (NEW)

| Path glob | Disposition | Signal | deploy_safety |
|---|---|---|---|
| `scripts/deploy.py` | MOVE | `adopter_deploy_orchestrator` | `deploy-blocking` |
| `scripts/deploy_agent_containers.py` | MOVE | `adopter_deploy_containers` | `deploy-blocking` |
| `scripts/deploy_config.py` | MOVE | `adopter_deploy_config_loader` | `deploy-blocking` |
| `scripts/deploy_orchestrator.py` | MOVE | `adopter_deploy_orchestrator_v2` | `deploy-blocking` |
| `scripts/deploy_pipeline.py` | MOVE | `adopter_deploy_pipeline` | `deploy-blocking` |
| `scripts/deploy_ui.py` | MOVE | `adopter_deploy_ui` | `deploy-blocking` |
| `scripts/deploy/*.ps1` | MOVE | `adopter_deploy_powershell_scripts` | `deploy-blocking` |
| `scripts/deploy/*.md` | MOVE | `adopter_deploy_documentation` | `deploy-safe-after-review` |
| `scripts/deploy/_prod_env_vars*.txt` | MOVE | `adopter_deploy_env_var_reference` | `deploy-blocking` |
| `scripts/deploy/api-gateway-restore.yaml` | MOVE | `adopter_deploy_restore_manifest` | `deploy-blocking` |

Per-file content scan for hardcoded legacy-root path references (`E:/GT-KB/`, `E:\\GT-KB\\`, `LEGACY_ROOT`). Each match recorded as a `hardcoded_path_reference` warning row in the JSON output, with the file:line:matched_string evidence. Phase 8 plan §3 explicitly requires this.

### §2.16 Infrastructure / Terraform (NEW)

| Path glob | Disposition | Signal | deploy_safety |
|---|---|---|---|
| `infrastructure/terraform/*.tf` | MOVE | `adopter_terraform_definitions` | `deploy-blocking` |
| `infrastructure/terraform/*.tfvars` | DO_NOT_MOVE (secret-adjacent) | `terraform_variable_potentially_sensitive` | `deploy-blocking` |
| `infrastructure/terraform/.terraform.lock.hcl` | MOVE | `terraform_provider_lock` | `deploy-safe-after-review` |
| `infrastructure/terraform/terraform.tfstate*` | DO_NOT_MOVE | `terraform_state_immovable_per_phase8_section_4` | `deploy-blocking` |

`tfvars` files probed presence-only (no content read; treated as secret-adjacent per `secrets/`-style policy in original §2.1).

### §2.17 GitHub Actions working-directory hardcoded paths (NEW)

For each `.github/workflows/*.yml` file inventoried in Slice 7:
- Content-scan for `working-directory:`, `cwd:`, hardcoded `E:/GT-KB/`, `/home/runner/work/GT-KB/`, etc.
- Emit each finding as a `hardcoded_path_reference` row (same schema as §2.15) with file:line:context evidence.
- Action recommendation: rewrite at cutover to use environment variable `${{ env.APP_ROOT }}` or relative paths.

This complements Slice 7's CI inventory: Slice 7 classifies workflow files; Slice 9 catalogs production-effect implications within them.

## 2. Fix 2 — `deploy_safety` field as first-class output (proposal §5)

### 2.1 Vocabulary

| Value | Meaning |
|---|---|
| `deploy-blocking` | Surface, if mishandled at cutover, breaks production deployment. Cutover script must verify this surface's relocation/handling before any deploy. |
| `deploy-safe-after-review` | Surface that affects deploy operations but mishandling has bounded impact (e.g., docs, test variants). Cutover script can proceed after owner review of the diff. |
| `deploy-not-applicable` | Surface has no production deploy impact (e.g., template files, test fixtures). |

Every row in `production_effects.json.surfaces[]` and `production-effects-map.md` gains a `deploy_safety` field.

### 2.2 Schema (revised §5.2)

```json
{
  "path": "Dockerfile",
  "exists": true,
  "size_bytes": 1234,
  "disposition": "MOVE",
  "signal": "adopter_container_definition",
  "deploy_safety": "deploy-blocking",
  "content_read": true,
  "category": "container_definition",
  "hardcoded_path_references": [
    {"line": 12, "matched_string": "COPY src/", "context": "COPY src/ /app/src/"}
  ]
}
```

### 2.3 Preview markdown (revised §5.1)

The preview gains a third top-level grouping (after disposition):

```markdown
## Deploy-Blocking Surfaces (require pre-cutover verification)

- `Dockerfile` — disposition: MOVE → `applications/Agent_Red/Dockerfile`; signal: `adopter_container_definition`
- `scripts/deploy.py` — disposition: MOVE; signal: `adopter_deploy_orchestrator`; hardcoded_path_references: 3
- ...

## Deploy-Safe-After-Review Surfaces

- `Dockerfile.test` — disposition: MOVE; signal: `adopter_container_definition_test_variant`
- `scripts/deploy/PRODUCTION-ENV-CHANGES.md` — disposition: MOVE; signal: `adopter_deploy_documentation`
- ...
```

## 3. Fix 3 — Test plan additions (proposal §7)

### 3.1 New tests covering each new category

| # | Test | Coverage |
|---|---|---|
| 22 (new) | `test_run_classifies_dockerfile_as_move_with_deploy_blocking` | §2.13 Docker surfaces |
| 23 (new) | `test_run_overrides_dockerfile_to_owner_decision_when_framework_reference` | §2.13 content-scan override for `groundtruth_kb` reference |
| 24 (new) | `test_run_classifies_shopify_app_toml_as_move_with_deploy_blocking` | §2.14 Shopify |
| 25 (new) | `test_run_classifies_deploy_script_as_move_with_deploy_blocking` | §2.15 Deploy scripts |
| 26 (new) | `test_run_records_hardcoded_path_references_in_deploy_script` | §2.15 hardcoded-path scan; synthetic deploy script fixture with `E:/GT-KB/` reference |
| 27 (new) | `test_run_classifies_terraform_tf_as_move_with_deploy_blocking` | §2.16 Terraform |
| 28 (new) | `test_run_classifies_tfvars_as_do_not_move_secret_adjacent` | §2.16 tfvars treated as secret-adjacent |
| 29 (new) | `test_run_does_not_read_tfvars_content` | **Safety:** assert no `read_text` against tfvars |
| 30 (new) | `test_run_classifies_terraform_tfstate_as_do_not_move` | §2.16 state files |
| 31 (new) | `test_run_records_github_actions_hardcoded_path_references` | §2.17 GHA working-directory scan |
| 32 (new) | `test_run_emits_deploy_blocking_section_in_preview_markdown` | §2.3 preview structure |
| 33 (new) | `test_run_emits_deploy_safety_field_for_every_surface` | §2.2 schema field universality |

## 4. Fix 4 — Vocabulary clarification (Codex `-002` ask 5)

The Codex finding asked whether `deploy_safety` would be added "alongside disposition" — the revision confirms: **alongside**, not replacing. Each surface row has BOTH:
- `disposition` ∈ {MOVE, KEEP, DO_NOT_MOVE, OWNER_DECISION_REQUIRED}
- `deploy_safety` ∈ {deploy-blocking, deploy-safe-after-review, deploy-not-applicable}

The two dimensions are independent. Example: `Dockerfile.test` is `MOVE` (disposition) + `deploy-safe-after-review` (deploy_safety) — moves at cutover, but mishandling has bounded impact.

## 5. Unchanged from `-001`

All other proposal sections remain valid:

- §1 Scope (read-only inventory; never read sensitive content).
- §2.1-§2.12 original source-set sections (env, Shopify deploy bundle, deploy logs, approval packets, POR snapshots, wrap-scan/session, root config, groundtruth.db, framework rules, ACS carrier).
- §3 Classification algorithm (extended with the new content-scan rules in §2.13-§2.17).
- §4 Output layout.
- §6 Common contract compliance.
- §7 original tests 1-21.
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

## 6. Codex Review Asks

1. Confirm the §2.13 Dockerfile content-scan override (`groundtruth_kb` reference → OWNER_DECISION_REQUIRED) is the right hard-fail signal, vs. accepting it as adopter (since the Agent Red app may legitimately have `groundtruth_kb` as a runtime dep).
2. Confirm the §2.16 Terraform tfvars classification as `DO_NOT_MOVE secret-adjacent` is right — alternative: `OWNER_DECISION_REQUIRED` since not all tfvars are secret. My read: structural-presence-only treatment is the safer default.
3. Confirm the §2.17 GHA working-directory scan is in this slice's scope vs. Slice 7's. My read: Slice 7 classifies the workflow files themselves; Slice 9 catalogs production-effect implications inside their bodies. Two different views; no double-counting.
4. Confirm the §1 vocabulary (disposition + deploy_safety as independent dimensions) is the right schema shape, vs. a combined enum.
5. Confirm the new tests (22-33) are sufficient coverage for the §2.13-§2.17 categories.
6. **GO / NO-GO** on Slice 9 REVISED-1.

## 7. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

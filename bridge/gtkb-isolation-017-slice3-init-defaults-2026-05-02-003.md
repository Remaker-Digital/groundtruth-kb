REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 3 (REVISED-1)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: `gt project init` — adopter-subject defaults, root-boundary refusal, existing-adopter idempotency, and Phase 9 §1 scaffold deliverables (including Phase 4 service-endpoint template and adopter-facing README quickstart block).
Supersedes: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-001.md` (NEW), `-002.md` (NO-GO).

## Revision Rationale (REVISED-1)

Codex NO-GO at `-002.md` issued three findings (F1 P1, F2 P1, F3 P2). Each is addressed:

1. **F1 — CLI entrypoint out of scope.** The `-001` proposal scoped only `scaffold_project()` and `_validate_target()`; the actual user-facing surface is `gt project init` at `groundtruth-kb/src/groundtruth_kb/cli.py:826`. This revision **adds `cli.py` to the modified-file list**, specifies the GT-KB-host-root resolution contract, defines the new `--gt-kb-root` flag, sets the default target to `<gt-kb-root>/applications/<project_name>`, and adds CLI-level primary tests (TP-CLI-*) that exercise `gt project init` directly.
2. **F2 — Phase 9 §1 enumeration coverage incomplete.** This revision **expands the spec-to-test mapping** so every Phase 9 §1 bullet has a named test, golden-fixture assertion, or documented scope note. Twelve new test rows added (TP8–TP19 in this revision) covering DB scope, INDEX.md + README header, work_list placeholder, .claude wrappers (no embedded policy), dashboard non-prepopulation, segregated .gitignore, and absence of forbidden product artifacts/secrets.
3. **F3 — Non-existent live paths cited.** Path corrections: `managed-artifacts.toml` → `groundtruth-kb/templates/managed-artifacts.toml` (not `src/groundtruth_kb/templates/`); ADR-ISOLATION-APPLICATION-PLACEMENT-001 → cite **KB row** (`db.get_spec('ADR-ISOLATION-APPLICATION-PLACEMENT-001')` returns v1 status=specified, type=architecture_decision) + bridge thread terminal at `bridge/gtkb-adr-isolation-application-placement-004.md`; ADR-CODEX-HOOK-PARITY-FALLBACK-001 → cite KB row only (no markdown file present in checkout).

## Context

GTKB-ISOLATION-017 is the adopter-packaging program. Slices 1, 2, and 2.5 are VERIFIED at the S326 wrap (commit `e5dec647`). This proposal opens Slice 3 per the scoping GO at `bridge/gtkb-isolation-017-scoping-004.md` lines 84–115.

Slice 3 has no owner-decision blockers. Per scoping `-003.md` lines 39–55, owner-decision clusters are: 1/3/7 → Slice 4, 2/4 → Slice 8, 5 → Slice 8 closeout, 6 → Slice 7.

## Specification Links

The implementation is constrained by the following live, in-checkout authorities:

1. **Phase 9 plan §1 — `gt project init`** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 91–142.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001 (KB row)** — `db.get_spec('ADR-ISOLATION-APPLICATION-PLACEMENT-001')` returns v1, `status=specified`, `type=architecture_decision`. Bridge-thread evidence: `bridge/gtkb-adr-isolation-application-placement-{001,002,003,004}.md` (terminal GO at `-004`). The mandate: adopter applications live at `<gt-kb-root>/applications/<name>/`.
3. **`.claude/rules/project-root-boundary.md`** — "All GT-KB application files MUST be within `E:\GT-KB\applications\`." Slice 3's refusal-to-land-outside contract is the mechanical enforcement at scaffold time.
4. **ADR-CODEX-HOOK-PARITY-FALLBACK-001 (KB row only)** — referenced for `.codex/hooks.json` forward-compat intent. No live markdown file in checkout; KB row is the authority.
5. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 93–115 (Slice 3 expanded scope) and `-004.md` GO terminal (no Slice-3-specific carry-forward conditions).
6. **GOV-09** (Owner Input Classification) — Phase 9 §1 obligations are owner-classified specification language; this slice implements without re-litigating scope.
7. **GOV-19-A1** (Outside-in testing) — primary tests exercise `gt project init` (CLI) and `scaffold_project` (library); helper-level tests are explicitly supplemental.
8. **GOV-20** (Architecture decisions) — Slice 3 ships an IPR + CVR pair to record (a) how the implementation honors ADR-ISOLATION-APPLICATION-PLACEMENT-001 and (b) post-impl proof that the scaffolded service-endpoint template clears the existing isolation doctor check.
9. **Prior Slice GOs** (carry-forward only):
   - `bridge/gtkb-isolation-017-slice1-doctor-checks-012.md` VERIFIED — Slice 1 ships `_check_isolation_adopter_root_not_under_product_root(target, product_root)` at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:43`. The CLI plumbs `gt_kb_root` to enable this check at session start on a freshly-scaffolded adopter.
   - `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` VERIFIED — registry now carries `owner` / `upgrade_policy` fields. Slice 3 must register all newly-scaffolded files in `groundtruth-kb/templates/managed-artifacts.toml` (corrected path per F3) so the AST gate from Slice 2 stays green.
10. **GT-KB host-root detection precedent** — `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1867` defines `_PRODUCT_ROOT = Path(__file__).resolve().parents[3]` for the doctor's runtime check. Slice 3 follows the same caller-supplies pattern at the CLI layer rather than re-deriving via package introspection (per Slice 1 `-002` F2: "there is no `manifest.find_project_root()` API; callers must supply `product_root`").
11. **Prior Deliberations search:** Codex NO-GO `-002.md` lines 24–33 ran `python -m groundtruth_kb.cli deliberations search ...` for "gt project init scaffold isolation", "GTKB-ISOLATION-017 Slice 3", "ADR-ISOLATION-APPLICATION-PLACEMENT gt project init" and returned no rows. Active prior context is the bridge thread + scoping `-003`/`-004`.

## Scope

### In-scope

Files modified:
- **`groundtruth-kb/src/groundtruth_kb/cli.py` (NEW per F1)** — extend `gt project init` (line 826 region) with a `--gt-kb-root <path>` Click option (defaults to `Path.cwd()` when omitted; resolved before pass-through). Change the default `target` computation (line 826) from `Path.cwd() / project_name` to `gt_kb_root / "applications" / project_name`. Pass `gt_kb_root` into `ScaffoldOptions(...)`.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` — extend `ScaffoldOptions` with `gt_kb_root: Path` field (required after CLI plumbing); call new validation helpers before `_validate_target`; emit the adopter-facing README quickstart block.
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py` — extend `_validate_target` (currently lines 75–79) with the two new refusal paths:
  - Refusal A: `target.parent.resolve()` must equal `(gt_kb_root / "applications").resolve()`. Otherwise raise `ValueError` citing ADR-ISOLATION-APPLICATION-PLACEMENT-001.
  - Refusal B: if `(target / "groundtruth.toml").exists()`, raise `ValueError` recommending `gt project upgrade`.
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py` — extend `_write_groundtruth_toml` (lines 86–116) with a `[service]` block carrying the Phase 4 endpoint template (placeholder matching `_SCOPED_SERVICE_URL_RE` at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:125`).
- **`groundtruth-kb/templates/managed-artifacts.toml` (corrected per F3)** — register all newly-scaffolded files (README quickstart target, `memory/release-readiness.md`, `.codex/hooks.json`, `.groundtruth/formal-artifact-approvals/.gitkeep`) so the Slice 2 AST gate stays green.
- `groundtruth-kb/src/groundtruth_kb/templates/project/README-quickstart.md` *(new)* — adopter-facing README quickstart block per Phase 9 §1 line 105 + Deliverables lines 425–426.
- `groundtruth-kb/src/groundtruth_kb/templates/project/release-readiness-banner.md` *(new)* — application-subject header per Phase 9 §1 lines 123–125.

Files created (new tests + fixtures):
- `groundtruth-kb/tests/test_scaffold_isolation.py` — primary outside-in tests (TP*) + helper supplemental (TS*).
- `groundtruth-kb/tests/test_cli_init.py` *(new per F1)* — primary CLI-surface tests (TP-CLI-*) using Click's CliRunner.
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/` and `dual-agent/` — golden fixture trees.

Documents (per GOV-20):
- `IPR-SLICE3-INIT-DEFAULTS-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001 (KB row), and the Phase 9 §1 obligations.
- `CVR-SLICE3-INIT-DEFAULTS-001` — post-implementation proof.

### Out-of-scope (deferred to other slices)

- `gt project upgrade` extensions (Slice 4) — including all owner-decision-1/3/7 branching.
- Clean-adopter test suite under `groundtruth-kb/tests/adopter/` (Slice 5).
- Documentation chapter (Slice 6) — Slice 3 ships only the README quickstart block baked into init output.
- Examples (Slice 7) and release ops (Slice 8).
- Phase 6 overlay refresh / stale / disposability tests (Slice 5).
- Auto-detection of `<gt-kb-root>` (e.g., walking up from `cwd()` looking for marker files). Slice 3 ships explicit-flag-or-cwd-default; auto-discovery is a follow-on hygiene item if owner desires.

## Implementation Plan

1. Probe full caller list of `ScaffoldOptions(...)` across the repo before adding `gt_kb_root` field (reported in post-impl).
2. Probe existing `gt project init` test surface (test_cli.py + test_scaffold_*.py) — reported in post-impl with adjusted-call-sites count.
3. **CLI extension** (`cli.py`): add `--gt-kb-root` Click option to `project_init`; resolve to `Path` (default `Path.cwd().resolve()`); compute default target as `gt_kb_root / "applications" / project_name`; thread into `ScaffoldOptions`.
4. **`ScaffoldOptions.gt_kb_root: Path`** added as required field.
5. **`_validate_target`** extended with two refusal paths (A + B per Scope).
6. **`_write_groundtruth_toml`** extended with `[service]` block:
   ```toml
   [service]
   # Phase 4 service-endpoint template. Override per environment.
   # endpoint = "https://gtkb.example.com/v1"
   endpoint = "configure-me://placeholder/v1"
   ```
7. **README quickstart, release-readiness banner, `.codex/hooks.json` intent, `.groundtruth/formal-artifact-approvals/.gitkeep`** baked into scaffold output via `_copy_base_templates` extensions.
8. **Register all new files** in `groundtruth-kb/templates/managed-artifacts.toml` (corrected path) so Slice 2 AST gate passes.
9. **Capture golden fixture** trees post-implementation.
10. **Author IPR + CVR** documents per GOV-20.

## Spec-to-test mapping (REVISED — full Phase 9 §1 enumeration coverage)

### Primary tests — outside-in surfaces (GOV-19-A1 spec coverage)

#### CLI surface (`gt project init` via Click `CliRunner`) — added per F1

| # | Test | Phase 9 §1 reference | Behavior |
|---|---|---|---|
| TP-CLI-1 | `test_init_default_target_is_under_applications_root` | line 106 (canonical placement) | `gt project init my-app --gt-kb-root <tmp>` lands at `<tmp>/applications/my-app/` |
| TP-CLI-2 | `test_init_refuses_target_outside_applications_root` | line 108 | `gt project init my-app --dir <tmp>/elsewhere/my-app` exits non-zero with ADR citation in stderr |
| TP-CLI-3 | `test_init_refuses_existing_adopter` | lines 140–142 | running init twice on the same target exits non-zero; stderr recommends `gt project upgrade` |
| TP-CLI-4 | `test_init_default_gt_kb_root_is_cwd` | (default semantics) | omitting `--gt-kb-root` uses `cwd()` and lands at `cwd()/applications/my-app/` |

#### Library surface (`scaffold_project`) — Phase 9 §1 scaffold enumeration

| # | Test | Phase 9 §1 reference | Behavior |
|---|---|---|---|
| TP1 | `test_scaffold_emits_groundtruth_toml_with_app_local_fields` | lines 115–116 | `groundtruth.toml` written; contains `[service]` block matching `_SCOPED_SERVICE_URL_RE` |
| TP2 | `test_scaffolded_service_endpoint_passes_doctor_check` | line 116 | `_check_isolation_service_endpoint_not_raw_db` returns `ToolCheck.found=True`, `status=pass` against scaffolded fixture |
| TP3 | `test_scaffold_initializes_app_scope_groundtruth_db` | lines 117 | `groundtruth.db` exists; tables present are app-scope only (no product-scope rows pre-populated; verified via SQL `sqlite_master` enum) |
| TP4 | `test_scaffold_emits_empty_bridge_index_with_README_header` | lines 118–119 | `bridge/INDEX.md` exists and is empty (only header comments per template); scaffolded `README.md` contains the bridge-essential rule header text |
| TP5 | `test_scaffold_emits_work_list_placeholder` | lines 120–122 | `memory/work_list.md` exists; contains a documented placeholder entry + adopter-owned-backlog convention comment block |
| TP6 | `test_scaffold_emits_release_readiness_with_app_subject_banner` | lines 123–125 | `memory/release-readiness.md` exists; contains application-subject header + "GT-KB product readiness is not tracked here" banner string |
| TP7 | `test_scaffold_emits_claude_wrappers_no_embedded_policy` | lines 126–128 | `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json` exist; the wrappers call product-supplied policy entrypoints (verified via grep against an embedded-logic blacklist of regex patterns) |
| TP8 | `test_scaffold_emits_codex_hooks_intent` | lines 129–130 | `.codex/hooks.json` exists with forward-compat intent shape consistent with ADR-CODEX-HOOK-PARITY-FALLBACK-001 (KB row v1) |
| TP9 | `test_scaffold_emits_formal_approvals_gitkeep` | lines 131–132 | `.groundtruth/formal-artifact-approvals/.gitkeep` exists |
| TP10 | `test_scaffold_does_not_pre_populate_dashboard_dir` | lines 133–134 | `docs/gtkb-dashboard/` is absent in scaffolded output |
| TP11 | `test_scaffold_emits_segregated_gitignore` | lines 135–136 | `.gitignore` exists with two clearly-delimited blocks (product-maintained + adopter-owned) |
| TP12 | `test_scaffold_excludes_forbidden_product_artifacts` | lines 137–139 | scaffolded tree contains zero of: GT-KB product source paths (`groundtruth-kb/src/`), product test paths (`groundtruth-kb/tests/`), product-scope MemBase rows, product bridge threads, raw DB credentials patterns (regex), deployment-secret patterns (regex) |
| TP13 | `test_scaffold_emits_readme_quickstart_block` | line 105 + Deliverables lines 425–426 | scaffolded `README.md` contains documented quickstart markers; references `[service].endpoint` configuration per Phase 9 Exit Criterion 4 line 343–345 |
| TP14 | `test_scaffold_local_only_matches_golden_fixture` | scoping `-003` line 111 | byte-level diff against `tests/fixtures/scaffold_golden/local-only/` |
| TP15 | `test_scaffold_dual_agent_matches_golden_fixture` | scoping `-003` line 111 | byte-level diff against `tests/fixtures/scaffold_golden/dual-agent/` |
| TP16 | `test_managed_registry_covers_new_scaffold_files` | Slice 2 AST-gate carry-forward | iterating `artifacts_for_scaffold(profile)` covers every new file Slice 3 emits; reads from `groundtruth-kb/templates/managed-artifacts.toml` (corrected path) |

### Supplemental helper-level tests (NOT GOV-19-A1 spec coverage)

| # | Test | Behavior |
|---|---|---|
| TS1 | `test_validate_target_refuses_outside_applications_root_at_helper_layer` | direct `_validate_target(target, gt_kb_root)` call with outside-root target raises ValueError |
| TS2 | `test_validate_target_refuses_existing_adopter_at_helper_layer` | direct call with existing-adopter target raises ValueError |
| TS3 | `test_write_groundtruth_toml_emits_service_block` | direct `_write_groundtruth_toml(...)` call writes `[service]` block with placeholder matching `_SCOPED_SERVICE_URL_RE` |

## Verification Commands (Windows-safe form)

```
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli_init.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_cli.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_doctor_isolation.py -v -k "service_endpoint"
$ uv run --project groundtruth-kb ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli_init.py
```

## Risk and Rollback

- **Risk: existing call sites of `ScaffoldOptions(...)` break** when `gt_kb_root` becomes required. Mitigation: probe call-site count before implementation; adjust each in the same commit. Test suite (`test_scaffold_project.py:18–37`, `test_cli.py`) constructs `ScaffoldOptions` and will fail loudly — caught by the regression sweep.
- **Risk: existing-adopter detection over-refuses.** Refusal predicate is specifically `(target / "groundtruth.toml").exists()`, not directory non-emptiness — preserves the prior behavior for non-adopter directories.
- **Risk: `--gt-kb-root` user confusion.** Mitigation: README quickstart block documents the flag; default-to-cwd preserves existing UX for users who don't need explicit roots.
- **Rollback:** revert the implementation commit; `_validate_target` and CLI return to pre-Slice-3 form. No DB schema changes; Slice 1 + Slice 2 unaffected.

## Acceptance Criteria

A post-implementation report shall be filed when ALL of the following hold:
- TP-CLI-1 through TP-CLI-4 (CLI surface) pass.
- TP1 through TP16 (library surface) pass.
- TS1 through TS3 (supplemental helper) pass.
- Existing scaffold/CLI tests pass after call-site adjustments.
- `_check_isolation_service_endpoint_not_raw_db` passes on a freshly-scaffolded fixture (cross-slice integration).
- Slice 2 AST gate passes against the new scaffolded files (no unregistered files).
- Ruff clean on all modified and new files.
- IPR-SLICE3-INIT-DEFAULTS-001 and CVR-SLICE3-INIT-DEFAULTS-001 inserted as KB document rows (per `db.insert_document(category='implementation_proposal' / 'constraint_verification')`); explicit owner approval recorded in change-reason.
- Golden fixture trees committed and byte-level diff tests pass.

## Open Items (probed during implementation; reported in post-impl)

- Exact count of `ScaffoldOptions(...)` construction sites across the repo.
- Result of `python -m groundtruth_kb.cli deliberations search --query "gt project init scaffold isolation" --limit 5` at implementation start.
- Whether any existing test relies on `_validate_target` being argument-free (and therefore needs the `gt_kb_root` parameter threaded through).

## Deliberation Capture

This proposal (and its `-001`/`-002` predecessors) is the substantive design record for Slice 3. The IPR/CVR pair captures the implementation. No pre-implementation owner decisions are required for Slice 3.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

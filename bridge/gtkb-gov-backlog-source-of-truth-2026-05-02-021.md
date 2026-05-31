REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — REVISED-6: clean-sweep scope (platform + adopter work_list.md retirement) per S376 owner decision (supersedes GO'd -019)

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-30 (S376)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02`
Prior version: GO at `-020` (Codex approved REVISED-5 at `-019`). This REVISED-6 supersedes the GO'd `-019` for one Prime-discovered, post-GO implementation reason (Finding C): the proposal conflated the PLATFORM work_list.md retirement (DELIB-S337) with the ADOPTER-facing `isolation:work-list-no-product-entries` doctor check and adopter scaffold seeding, whose removal cascades to files outside the `-019` target_paths. The S376 owner decision selected the clean-sweep scope (remove work_list.md everywhere — platform AND adopter), which this REVISED-6 makes implementable by expanding target_paths to the 5 additional adopter-isolation surfaces.
Status: REVISED

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490
target_paths: ["CLAUDE.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/rules/peer-solution-advisory-loop.md", ".claude/rules/acting-prime-builder.md", "config/governance/narrative-artifact-approval.toml", "config/agent-control/system-interface-map.toml", ".claude/hooks/narrative-artifact-approval-gate.py", ".githooks/pre-commit", ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", "scripts/session_self_initialization.py", "scripts/wrap_scan_consistency.py", "scripts/resolve_system_interface.py", "scripts/rehearse/_backlog_split.py", "scripts/rehearse/_dashboard_regen.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/operating_state.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py", "groundtruth-kb/src/groundtruth_kb/project/upgrade.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/templates/project/README-quickstart.md", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md", "groundtruth-kb/templates/rules/canonical-terminology.md", "groundtruth-kb/docs/architecture/isolation.md", "groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py", "groundtruth-kb/tests/adopter/test_doctor_detects_isolation_violations.py", "groundtruth-kb/tests/adopter/test_existing_adopter_migration_kit.py", "groundtruth-kb/tests/fixtures/adopter/pre_isolation_with_managed_drift/memory/work_list.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/README.md", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/README.md", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/tests/test_doctor_isolation.py", "groundtruth-kb/tests/test_operating_state.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/test_upgrade_isolation.py", "groundtruth-kb/tests/test_backlog.py", "platform_tests/hooks/test_narrative_artifact_approval.py", "platform_tests/scripts/test_cli_backlog_add.py", "platform_tests/scripts/test_cli_backlog_status.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_rehearse_backlog_split.py", "platform_tests/scripts/test_rehearse_dashboard_regen.py", "platform_tests/scripts/test_rehearse_inventory.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_standing_backlog_harvest.py", "platform_tests/scripts/test_system_interface_map.py", "platform_tests/scripts/test_wrap_scan_consistency.py", "memory/MEMORY.md", "memory/pending-owner-decisions.md", "memory/v1-release-strategy-deliberation-S347.md", "docs/gtkb-dashboard/startup-service-payload.json", "memory/work_list.md"]

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S376-work-list-md-retirement-slice-7-prime-revised-6
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

## Claim

REVISED-6 supersedes the GO'd `-019` (GO at `-020`) for one issue Prime Builder discovered during post-GO implementation, plus the owner decision that resolves it:

- **C — platform/adopter work_list.md conflation (scope correction; S376 owner decision).** The live tree showed that `-019`'s "reference removal" framing for `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` and `scaffold.py` actually requires removing the ADOPTER-facing `isolation:work-list-no-product-entries` doctor check and adopter work_list.md scaffold seeding. That check (`_check_isolation_work_list_no_product_entries`, registered at `doctor_isolation.py:570`) guards an ADOPTER's `target / "memory" / "work_list.md"` against platform-product-ID leakage — a concern distinct from DELIB-S337's platform backlog retirement. Removing it cascades to files NOT in `-019`'s target_paths: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` (the adopter isolation gate), `groundtruth-kb/tests/adopter/test_doctor_detects_isolation_violations.py`, `groundtruth-kb/tests/adopter/test_existing_adopter_migration_kit.py`, `groundtruth-kb/tests/fixtures/adopter/pre_isolation_with_managed_drift/memory/work_list.md`, and `groundtruth-kb/docs/architecture/isolation.md` (which `-019` had in its "intentionally preserved" list). The S376 owner AUQ (§ Owner Decisions / Input) selected **clean-sweep scope** (remove work_list.md everywhere, platform AND adopter), which this REVISED-6 makes implementable by adding those 5 surfaces to target_paths and reclassifying the doctor-check/seeding work from "reference removal" to "check + seeding retirement."

Everything else from `-019` (the machine-readable target_paths form [Finding A, -019], the migration-tooling retirement [Finding B, -019], the single `.claude` skill-file scope [F1 from -016], the `rg --hidden` acceptance scan, the 6-packet approval plan, the governance-adoption test migration, the F2-from-012 ordering invariant, spec links, prior deliberations) is carried forward unchanged. The migration-completion gate per `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` remains the operative directive; the clean-sweep scope extends the retirement to adopter-facing surfaces per the S376 owner decision.

## Findings Resolution

### C (owner decision) — platform/adopter conflation resolved; 5 adopter-isolation surfaces added to scope

Observation: `doctor_isolation.py` and `scaffold.py` carry FUNCTIONAL adopter-isolation logic (a doctor check + scaffold seeding) keyed to ADOPTER work_list.md files, not doc references. Reaching 0 `work_list.md` literals in them (the acceptance grep requirement) means removing the check + seeding, which cascades to out-of-target_paths consumers.

Resolution: S376 owner AUQ selected clean-sweep scope. REVISED-6 adds to target_paths and § Clean-Sweep Scope:
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — remove `isolation:work-list-no-product-entries` from the adopter isolation-check sets (lines 83, 187).
- `groundtruth-kb/tests/adopter/test_doctor_detects_isolation_violations.py` — remove the check from expected violations.
- `groundtruth-kb/tests/adopter/test_existing_adopter_migration_kit.py` — remove the check reference.
- `groundtruth-kb/tests/fixtures/adopter/pre_isolation_with_managed_drift/memory/work_list.md` — delete the fixture file (it exists only to trigger the now-removed check) and update its consumers to not expect a work-list violation.
- `groundtruth-kb/docs/architecture/isolation.md` — remove the `isolation:work-list-no-product-entries` rows (lines 127, 175). Reclassified from "intentionally preserved" to in-scope.

Consumer completeness (S376 comprehensive repo scan): the `isolation:work-list-no-product-entries` check name appears in exactly these live (non-historical) surfaces: `doctor_isolation.py`, `upgrade.py`, `cli.py` (help text, already in scope), `templates/project/upgrade-rehearsal-recipe.md` (already in scope), `test_doctor_isolation.py` (already in scope), `test_upgrade_isolation.py` (already in scope), `test_doctor_detects_isolation_violations.py`, `test_existing_adopter_migration_kit.py`, `isolation.md`, and the `pre_isolation` fixture. All are now in target_paths. The historical `scripts/_insert_ipr_slice4_upgrade_isolation.py`, `scripts/_insert_cvr_slice4_upgrade_isolation.py`, and `scripts/_verify_slice6_docs.py` references are one-off archived-class scripts (negative-pathspec excluded) and are preserved as historical evidence.

### A (mechanical, -019) — machine-readable target_paths; carried forward + expanded to 55 paths

The `target_paths:` metadata line (parser method 1) is retained and expanded from 50 to 55 entries (the 5 adopter-isolation surfaces added). `impl-auth begin` parses it; the expansion authorizes the clean-sweep surfaces.

### B (owner decision, -019) — migration-tooling retirement; carried forward (and already implemented)

The `gt backlog migrate-work-list` tooling retirement (cli.py command + backlog.py backend + test_cli.py/test_backlog.py migration tests) is carried forward unchanged. (Implementation note: this portion was implemented under the `-020` GO before Finding C surfaced; it is platform-scoped and within REVISED-6's superset scope, so it is not re-opened.)

### F1 from -016 / F1 from -014 / F1+F2 from -012 (carried forward unchanged)

Single `.claude` skill-file scope + `rg --hidden` 3-root acceptance scan + Bridge Canonicality Evidence + governance-adoption test migration all carried forward verbatim from `-019`.

## Clean-Sweep Scope (S376 owner decision — platform + adopter work_list.md retirement)

Per the S376 owner AUQ, work_list.md is retired EVERYWHERE in GT-KB (platform and adopter-facing surfaces), reaching a uniform "MemBase-only" steady state. Scope detail:

**Platform surfaces (DELIB-S337 core):** delete `memory/work_list.md`; retire the migration tooling (done under -020 GO); rewrite platform startup (`session_self_initialization.py` markdown→`gt backlog list --json`); remove the platform wrap-scan work_list.md reader; remove the rehearse markdown readers; drop work_list.md from the system-interface token lists (done); refresh the protected narrative artifacts.

**Adopter-facing surfaces (S376 clean-sweep extension):**
- `scaffold.py`: stop seeding `memory/work_list.md` for new adopters (lines 296, 553, 578). New adopters get MemBase-only.
- `doctor_isolation.py`: remove `_check_isolation_work_list_no_product_entries` (lines 400-445) + its dedicated `_PRODUCT_SCOPE_HEURISTIC_RE` (lines 390-397) + the registration at line 570.
- `upgrade.py`: remove `isolation:work-list-no-product-entries` from the isolation-check inventory (lines 83, 187) so the adopter upgrade gate no longer expects it.
- `cli.py`: remove the check name from the doctor help text (line 2669).
- `isolation.md`: remove the check's documentation rows (lines 127, 175).
- `templates/project/upgrade-rehearsal-recipe.md`: remove the check line (line 46).
- Adopter tests + fixture: `test_doctor_detects_isolation_violations.py`, `test_existing_adopter_migration_kit.py`, `test_upgrade_isolation.py`, `test_doctor_isolation.py` updated to not expect the removed check; the `pre_isolation_with_managed_drift/memory/work_list.md` fixture deleted (its purpose was to trigger the removed check), with its consuming tests adjusted.

**Out of scope (preserved):** `applications/Agent_Red/**` is a separate project (not a GT-KB artifact per `.claude/rules/project-root-boundary.md`); its work_list.md references are NOT touched. Historical one-off `scripts/_insert_*`/`_record_*`/`_verify_*`/`record_core_*` scripts and `bridge/**`, `archive/**`, release/announcement/report docs remain intentionally preserved. Notepad-tier `memory/*` files other than the 3 listed (MEMORY.md, pending-owner-decisions.md, v1-release-strategy-deliberation-S347.md) are outside the acceptance grep and not required for retirement.

## target_paths (machine-readable line above is authoritative; this prose enumerates the same 55-path set)

Protected narrative artifacts (formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`):
- `CLAUDE.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md`, `.claude/rules/peer-solution-advisory-loop.md`, `.claude/rules/acting-prime-builder.md`

Configuration:
- `config/governance/narrative-artifact-approval.toml` (Phase 5 cleanup), `config/agent-control/system-interface-map.toml` (done)

Hooks: `.claude/hooks/narrative-artifact-approval-gate.py` (comment done; Phase 5.2 code path), `.githooks/pre-commit`

Skills (untracked per S375 AUQ): `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`

Platform source (migration tooling RETIRED in cli.py/backlog.py [done]; adopter-isolation check REMOVED in doctor_isolation.py/upgrade.py per § Clean-Sweep Scope):
- `scripts/session_self_initialization.py`, `scripts/wrap_scan_consistency.py`, `scripts/resolve_system_interface.py` (done), `scripts/rehearse/_backlog_split.py`, `scripts/rehearse/_dashboard_regen.py`
- `groundtruth-kb/src/groundtruth_kb/backlog.py` (done), `operating_state.py` (done), `project/scaffold.py`, `project/doctor_isolation.py`, `project/upgrade.py` (ADDED), `cli.py` (done + help-text), `cli_backlog_add.py` (done)

Adopter scaffold templates: `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`, `templates/project/README-quickstart.md` (done), `templates/project/upgrade-rehearsal-recipe.md`, `templates/rules/canonical-terminology.md` (done)

Adopter-isolation docs (ADDED): `groundtruth-kb/docs/architecture/isolation.md`

Tests (assertion updates + check-removal + migration-test removal):
- `groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py`, `test_doctor_detects_isolation_violations.py` (ADDED), `test_existing_adopter_migration_kit.py` (ADDED)
- `groundtruth-kb/tests/fixtures/adopter/pre_isolation_with_managed_drift/memory/work_list.md` (ADDED — deletion)
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/README.md`, `local-only/README.md`
- `groundtruth-kb/tests/test_cli.py` (done), `test_doctor_isolation.py`, `test_operating_state.py`, `test_scaffold_isolation.py`, `test_upgrade_isolation.py`, `test_backlog.py` (done)
- `platform_tests/hooks/test_narrative_artifact_approval.py`, `platform_tests/scripts/test_cli_backlog_add.py`, `test_cli_backlog_status.py`, `test_groundtruth_governance_adoption.py`, `test_rehearse_backlog_split.py`, `test_rehearse_dashboard_regen.py`, `test_rehearse_inventory.py`, `test_session_self_initialization.py`, `test_standing_backlog_harvest.py`, `test_system_interface_map.py` (done), `test_wrap_scan_consistency.py`

Notepad-tier (no packet): `memory/MEMORY.md`, `memory/pending-owner-decisions.md`, `memory/v1-release-strategy-deliberation-S347.md`

Generated: `docs/gtkb-dashboard/startup-service-payload.json`

Deletion target: `memory/work_list.md`

### Intentionally preserved (NOT in target_paths; excluded from acceptance grep)

- `bridge/**`, `archive/**`, `.groundtruth/formal-artifact-approvals/**`, `independent-progress-assessments/**`
- `.codex/gtkb-hooks/last-user-visible-startup-*` (generated cache)
- `scripts/_archive_*.py`, `scripts/_insert_*.py`, `scripts/_record_*.py`, `scripts/record_core_*.py`, `scripts/_verify_*.py` (historical one-off classes)
- `groundtruth-kb/CHANGELOG.md`, `release-notes-*.md`, `docs/announcements/`, `docs/reports/`
- `applications/Agent_Red/**` (separate project per `.claude/rules/project-root-boundary.md`)
- `memory/*` notepad files other than the 3 listed above (outside acceptance grep)
- `docs/gtkb-dashboard/*.pdf`
- NOTE: `groundtruth-kb/docs/architecture/isolation.md` is REMOVED from this preserved list (now in target_paths per the clean sweep).

## KB-Mutation Scope & Cited-WI Clarification (carried forward from -019)

Slice 7-prime performs NO `groundtruth.db` mutation (reads only). `target_paths` correctly omits `groundtruth.db`. Declared WI is `WI-3490`; `WI-3355`/`WI-3420` appear only as cross-thread `cli.py` coordination context; `GTKB-GOV-000` appears only as a governance-adoption test milestone ID.

## Governance-Adoption Test Migration (carried forward from -019)

`platform_tests/scripts/test_groundtruth_governance_adoption.py` has three `work_list.md` couplings, each migrated to the surviving canonical surfaces (MemBase `work_items` / already-asserted rule content / relaxed `source_paths` non-empty assertion) so the file carries zero `work_list.md` literal post-slice while passing.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate (carried forward from -019; unchanged):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; see § Bridge Canonicality Evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test plan derives from each linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts under `E:\GT-KB`; the adopter-isolation surfaces (doctor_isolation, upgrade, adopter tests/fixtures, isolation.md) are platform-side adopter-governance code, not adopter-repo mutations.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets for the 5 protected narrative artifacts + the deletion packet. The adopter-isolation source/test/doc edits are NOT protected narrative artifacts (no packets).
- `GOV-STANDING-BACKLOG-001` v3 — durable cross-session work authority preserved.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate; this slice IS the gate.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority; reaches post-migration steady state.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — owner directive (operative; platform core).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — removes hand-maintained markdown plumbing.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — continuity preserved (MemBase `work_items`; `gt backlog list --json`).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage triplet cited.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — PAUTH cites linked specs.

Advisory (per applicability preflight content matches): `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

Predecessor: `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (superseded by DCL-STANDING-BACKLOG-DB-SCHEMA-001 v2; historical).

Sibling thread context: `-008` (Slice 1 VERIFIED), `-019` (REVISED-5, GO'd at -020; superseded by this REVISED-6 for Finding C), `-020` (GO on -019; the plan it approved is scope-corrected here), `gtkb-backlog-work-list-retirement-directive-001-012.md` (Slice A+B VERIFIED).

## Prior Deliberations

(Carried forward from -019; full list preserved.)

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — operative (platform core).
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — foundational.
- `DELIB-0838`, `DELIB-0839` — standing backlog authority + snapshots.
- `DELIB-0835` — scoped auto-approval pattern (6-packet batch; activated by S376 owner AUQ).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — alignment.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — freeze lifted.

S376 deliberation context: the clean-sweep scope (Finding C) is an owner-decided scope clarification (platform + adopter retirement), recorded in § Owner Decisions / Input; it extends DELIB-S337's platform retirement to adopter surfaces. No prior deliberation conflicts with removing the adopter `isolation:work-list-no-product-entries` check, which was always conditional on adopters carrying a work_list.md.

## Owner Decisions / Input

Carried forward from -009/-011/-013/-015/-017/-019 plus the new S376 clean-sweep AUQ:

- **S376 AUQ — "Does work_list.md retirement scope cover only the platform's memory/work_list.md, or also the adopter-facing work_list.md surfaces?"**
  - Owner answer: **"Platform + adopter (clean sweep)"**.
  - Decision content: remove work_list.md EVERYWHERE — platform AND adopter. Retire the adopter scaffold seeding + the `isolation:work-list-no-product-entries` check across the codebase (new adopters get MemBase-only; the isolation doctor loses the work-list check). Expand target_paths to add `upgrade.py`, the 2 adopter isolation tests, the `pre_isolation` fixture, and `isolation.md`.
  - Decision class: scope decision / behavior change (in-scope per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel).
  - Recorded: `memory/pending-owner-decisions.md` (auto-recorded by `.claude/hooks/owner-decision-tracker.py`; `detected_via: ask_user_question`).

- **S376 AUQ — migration tooling retirement** ("Retire the migration tooling"). Carried forward (implemented under -020 GO).
- **S376 AUQ — formal-artifact-approval activation** ("Scoped auto-approval + implement now"; `auto_approval_scope: work-list-retirement-slice-7-prime-batch-2026-05-30`). Carried forward.
- **S375 AUQ — skill-file handling** ("Edit in place; keep untracked"; single `.claude` file). Carried forward.
- **S373 AUQ — migration-completion path** (Path A "Migration retirement"). Carried forward.

No new owner approval is required beyond the S376 AUQs captured. REVISED-6's change is the owner-decided clean-sweep scope expansion.

## Current State Evidence (re-probed S376 / -021 filing)

- Skill-file reproduce-first guard: `.claude` exists (1 ref, line 51); `.codex`/`.agent` absent (carried from -019; reconfirmed).
- `impl-auth begin` parses the machine-readable target_paths (55 paths) — verified at filing.
- Comprehensive repo scan (S376): 53 tracked files carry the `work_list.md` literal (minus clearly-historical). After classification, the in-scope set is the 55-path target_paths above; `applications/Agent_Red/**`, the historical `_insert_/_record_/_verify_/_archive_` scripts, and non-listed `memory/*` notepad files are intentionally preserved/out-of-grep.
- `isolation:work-list-no-product-entries` check appears in 13 files; the 10 live (non-historical) ones are all in target_paths.
- Already-implemented (under -020 GO; within this superset): migration-tooling retirement (cli.py/backlog.py/test_cli.py/test_backlog.py), token-lists (system-interface-map.toml/resolve_system_interface.py/operating_state.py/test_system_interface_map.py), doc comments (cli_backlog_add.py/.claude hook/templates README+canonical-terminology).

## Cross-Thread Coordination (carried forward from -019)

1. `cli.py` — ~435 uncommitted parallel lines (WI-3355 reconcile-doubled-prefix + projects-status); Slice 7-prime cli.py edits commit cumulatively with documentation (committing cli.py alone breaks the import). Parallel `ruff format` drift at lines 893+/1301+ is not Slice 7-prime's.
2. `CLAUDE.md` — in-flight `gtkb-claude-md-scope-clarification-slice-3` also modifies it; coordinate via cumulative documentation.
3. `groundtruth_kb.backlog` namespace — untracked parallel `backlog/` package (approval-state) shims the legacy module; its `if exists` guard degrades gracefully when backlog.py is stubbed (no hard conflict).

## Implementation Plan (carried forward from -019; clean-sweep deltas marked)

Phases 1-6 per -019, with Phase 2.3/2.5 extended for the clean sweep:
- **Phase 1** (read-only): done — backlog count 293 (>=75); 75 migrated rows confirmed; DELIB-S332 DA-retrievable.
- **Phase 2.1** Skill (done in plan; edit pending): `.claude` SKILL.md line 51 swap.
- **Phase 2.2** Scripts: `session_self_initialization.py` (markdown→`gt backlog list --json`), `wrap_scan_consistency.py`, `rehearse/_backlog_split.py`, `rehearse/_dashboard_regen.py`, `resolve_system_interface.py` (done).
- **Phase 2.3** Platform source: migration tooling (done); **adopter-isolation check removal** in `doctor_isolation.py` (+ regex + registration) and `upgrade.py` (check inventory) and `cli.py` (help text); `scaffold.py` (stop seeding); `operating_state.py` (done); `cli_backlog_add.py` (done).
- **Phase 2.4** Templates: `upgrade-rehearsal-recipe.md` (check line), `templates/hooks/...gate.py`, README (done), templates canonical-terminology (done).
- **Phase 2.4b** Adopter-isolation docs: `isolation.md` (remove check rows).
- **Phase 2.5** Tests: governance-adoption migration; `test_doctor_isolation.py`/`test_upgrade_isolation.py`/`test_doctor_detects_isolation_violations.py`/`test_existing_adopter_migration_kit.py` (remove check expectations); `scaffold` tests + golden fixtures; delete `pre_isolation` fixture work_list.md; rehearse tests; the rest.
- **Phase 2.6** Hooks: `.claude` hook comment (done), `.githooks/pre-commit`.
- **Phase 2.7** Config: `system-interface-map.toml` (done).
- **Phase 2.8** Notepad: MEMORY.md, pending-owner-decisions.md, v1-release-strategy.
- **Phase 3** 6 approval packets (5 narrative + 1 deletion).
- **Phase 4** Protected narrative edits + work_list.md deletion + dashboard regen.
- **Phase 5** Post-deletion cleanup (narrative-artifact-approval.toml + hook code path).
- **Phase 6** Verification (acceptance greps + rg --hidden + retired-check scan + full suite + release gate + doctor + both preflights + ruff).

## Spec-Derived Test Plan (carried forward from -019 + clean-sweep additions)

| Test | Spec | Method |
|---|---|---|
| T-1 | DELIB-S337 deletion endpoint | `assert not os.path.exists('memory/work_list.md')` post-commit |
| T-3 | GOV-STANDING-BACKLOG-001 v3 continuity | `gt backlog list --json | jq length` >= 75 |
| T-6 | GOV-ARTIFACT-APPROVAL-001 | 6 packets exist; SHA256 match |
| T-9 | No tracked residual callers (F2 from -012) | acceptance grep returns 0 |
| T-9b | No untracked skill residual (F1 from -014/-016) | `rg --hidden` over 3 skill roots returns 0 |
| T-9c | Migration tooling retired | `git grep "migrate-work-list\|parse_work_list\|migrate_work_list_items" -- groundtruth-kb/src groundtruth-kb/tests` returns 0 |
| T-9d | **Adopter isolation check retired (C / S376)** | `git grep "work-list-no-product-entries" -- groundtruth-kb/src groundtruth-kb/tests groundtruth-kb/docs groundtruth-kb/templates` returns 0; full suite green |
| T-14 | Existing suite green | `pytest platform_tests/ groundtruth-kb/tests/ -q` (incl. adopter isolation tests) |
| T-16 | impl-auth begin parseable | `begin` returns `authorized: true` against 55-path target_paths |

## Requirement Sufficiency

Existing requirements sufficient. REVISED-6's change is the S376 owner-decided clean-sweep scope (platform + adopter work_list.md retirement), extending DELIB-S337's platform retirement to adopter surfaces. No spec amendment required.

## Acceptance Criteria (carried forward from -019 + clean-sweep additions)

1. `memory/work_list.md` does not exist post-commit.
2. Tracked acceptance grep (§2 form from -019, now covering the in-scope adopter surfaces under `groundtruth-kb/src/`, `groundtruth-kb/tests/adopter/`, `groundtruth-kb/templates/`) returns 0.
2b. `rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills` returns 0.
3. `gt backlog list --json | jq length` >= 75.
4. `pytest platform_tests/scripts/ groundtruth-kb/tests/` passes (incl. adopter isolation tests with the check removed; governance-adoption test migrated; migration tests removed).
6. 5 protected-narrative packets + 1 deletion packet exist; `check_narrative_artifact_evidence.py` PASS.
7. Applicability + clause preflights pass on the post-impl report.
8. F2-from-012 ordering invariant: `narrative-artifact-approval.toml` keeps `memory/work_list.md` until after the deletion (Phase 5).
10. `git ls-files --error-unmatch .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` returns "did not match" (untracked).
11. Migration tooling retired (T-9c) returns 0; suite green.
12. **Adopter isolation check retired (T-9d):** `git grep "work-list-no-product-entries"` over `groundtruth-kb/src groundtruth-kb/tests groundtruth-kb/docs groundtruth-kb/templates` returns 0; the `pre_isolation` fixture work_list.md is deleted; adopter isolation tests pass without the check.
13. `isolation.md` no longer documents the removed check.
14. impl-auth begin returns `authorized: true` (55-path target_paths).

## Risk & Rollback

Risks: large surface (~50 tracked edits + adopter-isolation check removal + 1 untracked skill edit + 2 file deletions [work_list.md + fixture]). Mitigation: Phase 6 acceptance greps + retired-check scan (T-9d) + full suite. Removing the adopter isolation check is owner-decided (S376); the check was conditional on adopters carrying a work_list.md, which the clean sweep eliminates. cli.py/CLAUDE.md/backlog-namespace coordination per § Cross-Thread Coordination.

Rollback: `git revert <slice-commit-sha>` restores all tracked changes (callers + retired tooling + retired check + deletion targets). The 1 untracked skill file reverts manually (line 51). MemBase unchanged.

---

Reviewer focus areas:
- C (clean sweep): is the adopter-isolation check-removal consumer set complete (upgrade.py, cli.py help, adopter tests, fixture, isolation.md, templates)? Is removing the `isolation:work-list-no-product-entries` check the right consequence of the S376 clean-sweep decision? Is `applications/Agent_Red/**` correctly preserved (separate project)?
- target_paths: 55-path machine-readable line correct + complete? Does it resolve via `extract_target_paths`?
- Carried-forward: migration-tooling retirement (B, already implemented — within superset), token-lists, skill-file single-file scope (F1/-016), governance-adoption test migration, acceptance grep (F2/-012).

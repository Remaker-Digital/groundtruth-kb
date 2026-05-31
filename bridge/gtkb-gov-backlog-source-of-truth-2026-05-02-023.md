REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — REVISED-7: addresses Codex NO-GO at -022 (isolation.md:293 work_list.md pointer + acceptance coverage)

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-30 (S376)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02`
Prior version: REVISED-6 at `-021`; Codex NO-GO at `-022` (F1: clean-sweep acceptance plan misses a live `work_list.md` reference at `isolation.md:293`).
Status: REVISED

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490
target_paths: ["CLAUDE.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/rules/peer-solution-advisory-loop.md", ".claude/rules/acting-prime-builder.md", "config/governance/narrative-artifact-approval.toml", "config/agent-control/system-interface-map.toml", ".claude/hooks/narrative-artifact-approval-gate.py", ".githooks/pre-commit", ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", "scripts/session_self_initialization.py", "scripts/wrap_scan_consistency.py", "scripts/resolve_system_interface.py", "scripts/rehearse/_backlog_split.py", "scripts/rehearse/_dashboard_regen.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/operating_state.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py", "groundtruth-kb/src/groundtruth_kb/project/upgrade.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/templates/project/README-quickstart.md", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md", "groundtruth-kb/templates/rules/canonical-terminology.md", "groundtruth-kb/docs/architecture/isolation.md", "groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py", "groundtruth-kb/tests/adopter/test_doctor_detects_isolation_violations.py", "groundtruth-kb/tests/adopter/test_existing_adopter_migration_kit.py", "groundtruth-kb/tests/fixtures/adopter/pre_isolation_with_managed_drift/memory/work_list.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/README.md", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/README.md", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/tests/test_doctor_isolation.py", "groundtruth-kb/tests/test_operating_state.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/test_upgrade_isolation.py", "groundtruth-kb/tests/test_backlog.py", "platform_tests/hooks/test_narrative_artifact_approval.py", "platform_tests/scripts/test_cli_backlog_add.py", "platform_tests/scripts/test_cli_backlog_status.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_rehearse_backlog_split.py", "platform_tests/scripts/test_rehearse_dashboard_regen.py", "platform_tests/scripts/test_rehearse_inventory.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_standing_backlog_harvest.py", "platform_tests/scripts/test_system_interface_map.py", "platform_tests/scripts/test_wrap_scan_consistency.py", "memory/MEMORY.md", "memory/pending-owner-decisions.md", "memory/v1-release-strategy-deliberation-S347.md", "docs/gtkb-dashboard/startup-service-payload.json", "memory/work_list.md"]

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S376-work-list-md-retirement-slice-7-prime-revised-7
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

## Claim

REVISED-7 resolves the single Codex finding from `-022`:

- **F1 (P1)** — `groundtruth-kb/docs/architecture/isolation.md` carries TWO `work_list.md` references, but `-021` only planned/tested removal of the `isolation:work-list-no-product-entries` check rows (line 127 + the line-175 list entry). A SEPARATE live pointer at `isolation.md:293` ("the overlay refresh API and disposability test are tracked in `memory/work_list.md` row 31 as `GTKB-ISOLATION-017-SLICE-5.5`") would survive the `-021` plan, leaving a canonical architecture doc pointing at the deleted backlog file — the exact source-of-truth drift this slice retires. REVISED-7 applies Codex's preferred Option 1: (a) the implementation plan now explicitly repoints `isolation.md:293` from the deleted `memory/work_list.md` pointer to the surviving MemBase reference for `GTKB-ISOLATION-017-SLICE-5.5`; (b) the acceptance grep §2 positive scope now includes `groundtruth-kb/docs/architecture/isolation.md`; (c) a dedicated acceptance check `git grep -n "work_list\.md" -- groundtruth-kb/docs/architecture/isolation.md` (returns 0) is added as Acceptance §15 / T-9e.

Everything else from `-021` (the 55-path target_paths [Finding C / S376 clean-sweep], the migration-tooling retirement [B, implemented under -020], the token-list changes [implemented], the single `.claude` skill-file scope [F1/-016], the governance-adoption test migration, spec links, prior deliberations, the S376 owner decisions) is carried forward unchanged.

## Findings Resolution

### F1 from -022 (P1, RESOLVED) — isolation.md:293 pointer + acceptance coverage

`-022` reported (lines 118-152): isolation.md has two `work_list.md` hits — line 127 (the check row, planned for removal) and line 293 (a separate live pointer to `memory/work_list.md` row 31). The `-021` plan + T-9d (`work-list-no-product-entries` grep) did not cover line 293, and §2 did not scan `docs/architecture/`.

Resolution applied:
1. **Implementation plan (Phase 2.4b)** now lists BOTH isolation.md edits: (i) remove the `isolation:work-list-no-product-entries` rows (line 127 table row + the line-175 "Needs adopter input" list entry) — check retirement; (ii) repoint line 293 from "`memory/work_list.md` row 31 as `GTKB-ISOLATION-017-SLICE-5.5`" to "MemBase work item `GTKB-ISOLATION-017-SLICE-5.5`" (the surviving canonical reference).
2. **Acceptance grep §2** positive scope adds `groundtruth-kb/docs/architecture/isolation.md` so the main no-residual-callers grep covers the doc.
3. **Dedicated check (Acceptance §15 / T-9e):** `git grep -n "work_list\.md" -- groundtruth-kb/docs/architecture/isolation.md` returns 0 post-slice.

The `GTKB-ISOLATION-017-SLICE-5.5` reference survives in MemBase (it is a tracked work item / project ID); repointing preserves the doc's intent (the follow-on overlay work is tracked) while removing the dangling file pointer.

### C / A / B (carried forward from -021)

- **C (S376 clean-sweep, RESOLVED in -021):** platform + adopter retirement; 55-path target_paths incl. upgrade.py, the 2 adopter isolation tests, the pre_isolation fixture, and isolation.md. Carried forward.
- **A (machine-readable target_paths, -019):** carried forward (55 paths; `begin` parses it).
- **B (migration-tooling retirement, -019/-020):** implemented; within REVISED-7's superset scope; not re-opened.
- **F1/-016, F1/-014, F1+F2/-012:** carried forward verbatim.

## Clean-Sweep Scope (S376 owner decision; isolation.md detail updated per F1/-022)

Per the S376 owner AUQ ("Platform + adopter (clean sweep)"), work_list.md is retired everywhere in GT-KB. Adopter-isolation surface detail (unchanged from -021 except isolation.md):
- `scaffold.py`: stop seeding adopter `memory/work_list.md`.
- `doctor_isolation.py`: remove `_check_isolation_work_list_no_product_entries` + `_PRODUCT_SCOPE_HEURISTIC_RE` + registration (line 570).
- `upgrade.py`: remove `isolation:work-list-no-product-entries` from the isolation-check inventory.
- `cli.py`: remove the check name from doctor help text.
- **`isolation.md`: remove the check rows (line 127 table + line 175 list) AND repoint the line-293 `work_list.md` pointer to the MemBase `GTKB-ISOLATION-017-SLICE-5.5` reference (F1/-022 fix).**
- `templates/project/upgrade-rehearsal-recipe.md`: remove the check line.
- Adopter tests + fixture: `test_doctor_detects_isolation_violations.py`, `test_existing_adopter_migration_kit.py`, `test_upgrade_isolation.py`, `test_doctor_isolation.py` updated; the `pre_isolation_with_managed_drift/memory/work_list.md` fixture deleted; consuming tests adjusted.

**Preserved (out of scope):** `applications/Agent_Red/**` (separate project); historical `scripts/_insert_*`/`_record_*`/`_verify_*`/`record_core_*`; `bridge/**`, `archive/**`, release/announcement/report docs; notepad `memory/*` beyond the 3 listed; `docs/gtkb-dashboard/*.pdf`.

## target_paths (machine-readable line above is authoritative; 55 paths)

Identical 55-path set to `-021` (no path additions in REVISED-7; the F1 fix is acceptance + plan detail within the already-in-scope `isolation.md`). See `-021` § target_paths for the grouped enumeration. Net additions vs `-019`: `upgrade.py`, `test_doctor_detects_isolation_violations.py`, `test_existing_adopter_migration_kit.py`, `pre_isolation_with_managed_drift/memory/work_list.md`, `isolation.md`.

### Intentionally preserved (unchanged from -021)

`bridge/**`, `archive/**`, `.groundtruth/formal-artifact-approvals/**`, `independent-progress-assessments/**`, generated startup cache, historical `_insert_/_record_/_verify_/_archive_/record_core_` scripts, CHANGELOG/release-notes/announcements/reports, `applications/Agent_Red/**`, non-listed `memory/*`, dashboard PDFs. `isolation.md` is IN scope (not preserved).

## KB-Mutation Scope & Cited-WI Clarification (carried forward)

No `groundtruth.db` mutation (reads only). Declared WI `WI-3490`; `WI-3355`/`WI-3420` are cross-thread cli.py coordination context; `GTKB-GOV-000` is a governance-adoption test milestone ID; `GTKB-ISOLATION-017-SLICE-5.5` is the MemBase reference substituted into isolation.md:293 (not a declared work item of this proposal).

## Governance-Adoption Test Migration (carried forward from -019/-021)

`test_groundtruth_governance_adoption.py` three `work_list.md` couplings migrated to surviving canonical surfaces (MemBase `work_items` / asserted rule content / relaxed `source_paths` non-empty), file reaches 0 `work_list.md` literal while passing.

## Specification Links

(Carried forward from -021; unchanged.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical; this REVISED-7 filed append-only above the `-022` NO-GO; no prior version mutated.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test plan derives from each linked spec; the F1/-022 fix tightens the spec-derived verification for the deletion-endpoint specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts under `E:\GT-KB`; adopter-isolation surfaces are platform-side governance code.
- `GOV-ARTIFACT-APPROVAL-001` — 5 protected-narrative packets + 1 deletion packet; isolation.md is a docs artifact (NOT a protected narrative artifact per `config/governance/narrative-artifact-approval.toml`), so no packet.
- `GOV-STANDING-BACKLOG-001` v3 — continuity preserved.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate; the isolation.md:293 fix removes a residual pointer that would have weakened this gate's evidence (per -022 F1 rationale).
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority steady state.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — operative.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`.

Advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

Sibling thread context: `-008` (Slice 1 VERIFIED), `-021` (REVISED-6, NO-GO'd at -022 for F1), `-022` (Codex NO-GO addressed here), `-019`/`-020` (REVISED-5 + GO; migration-tooling implemented).

## Prior Deliberations

(Carried forward from -021.)

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`, `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-0838`, `DELIB-0839`, `DELIB-0835`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`.

The F1/-022 fix is an acceptance-completeness correction (isolation.md:293), not a new design question; no additional deliberation search beyond the carried set is required. Codex `-022` Prior Deliberations confirmed no conflict.

## Owner Decisions / Input

(Carried forward from -021; no new owner decision required for REVISED-7.)

- **S376 AUQ — clean-sweep scope** ("Platform + adopter (clean sweep)"). Operative for the adopter-isolation surfaces incl. isolation.md.
- **S376 AUQ — migration tooling retirement** ("Retire the migration tooling"). Implemented.
- **S376 AUQ — formal-artifact-approval activation** ("Scoped auto-approval + implement now"; `work-list-retirement-slice-7-prime-batch-2026-05-30`).
- **S375 AUQ — skill-file** ("Edit in place; keep untracked"; single `.claude` file).
- **S373 AUQ — migration-completion path** (Path A).

The F1/-022 fix (isolation.md:293 repoint + acceptance check) is implementation-scope precision within the already-authorized clean-sweep scope. No new owner approval required.

## Implementation Plan (carried forward from -021; Phase 2.4b updated per F1/-022)

Phases 1-6 per -021. Phase status (already implemented under -020 GO; within REVISED-7 superset): migration-tooling retirement, token-lists, doc comments (cli_backlog_add, .claude hook, templates README + canonical-terminology). Remaining:

- **Phase 2.1** Skill: `.claude` SKILL.md line 51 swap.
- **Phase 2.2** Scripts: `session_self_initialization.py` (markdown→`gt backlog list --json`), `wrap_scan_consistency.py`, `rehearse/_backlog_split.py`, `rehearse/_dashboard_regen.py`.
- **Phase 2.3** Platform source: adopter-isolation check removal in `doctor_isolation.py` (+ regex + registration), `upgrade.py` (check inventory), `cli.py` (help text); `scaffold.py` (stop seeding).
- **Phase 2.4** Templates: `upgrade-rehearsal-recipe.md` (check line), `templates/hooks/...gate.py`.
- **Phase 2.4b** `isolation.md`: (i) remove the `isolation:work-list-no-product-entries` rows (line 127 table + line 175 list); (ii) **repoint line 293** "`memory/work_list.md` row 31 as `GTKB-ISOLATION-017-SLICE-5.5`" → "MemBase work item `GTKB-ISOLATION-017-SLICE-5.5`". Post-edit isolation.md carries 0 `work_list.md` literals and 0 `work-list-no-product-entries` references.
- **Phase 2.5** Tests: governance-adoption migration; isolation tests (remove check expectations); scaffold tests + golden fixtures; delete `pre_isolation` fixture work_list.md; rehearse tests; the rest.
- **Phase 2.6** Hooks: `.githooks/pre-commit`.
- **Phase 2.8** Notepad: MEMORY.md, pending-owner-decisions.md, v1-release-strategy.
- **Phase 3** 6 approval packets. **Phase 4** Protected edits + work_list.md deletion + dashboard regen. **Phase 5** Cleanup. **Phase 6** Verification.

## Spec-Derived Test Plan (carried forward + T-9e)

| Test | Spec | Method |
|---|---|---|
| T-1 | DELIB-S337 deletion endpoint | `assert not exists('memory/work_list.md')` post-commit |
| T-3 | GOV-STANDING-BACKLOG-001 v3 continuity | `gt backlog list --json | jq length` >= 75 |
| T-6 | GOV-ARTIFACT-APPROVAL-001 | 6 packets exist; SHA256 match |
| T-9 | No tracked residual callers (F2/-012) | acceptance grep §2 (now incl. isolation.md) returns 0 |
| T-9b | No untracked skill residual (F1/-014/-016) | `rg --hidden` over 3 skill roots returns 0 |
| T-9c | Migration tooling retired (B) | `git grep "migrate-work-list\|parse_work_list\|migrate_work_list_items" -- groundtruth-kb/src groundtruth-kb/tests` returns 0 |
| T-9d | Adopter isolation check retired (C/S376) | `git grep "work-list-no-product-entries" -- groundtruth-kb/src groundtruth-kb/tests groundtruth-kb/docs groundtruth-kb/templates` returns 0 |
| T-9e | **isolation.md residual pointer cleared (F1/-022)** | `git grep -n "work_list\.md" -- groundtruth-kb/docs/architecture/isolation.md` returns 0 |
| T-9f | Adopter fixture deleted (C) | `assert not exists('groundtruth-kb/tests/fixtures/adopter/pre_isolation_with_managed_drift/memory/work_list.md')` |
| T-14 | Existing suite green | `pytest platform_tests/ groundtruth-kb/tests/ -q` (incl. adopter isolation tests) |
| T-16 | impl-auth begin parseable | `begin` → `authorized: true` (55-path target_paths) |

## Requirement Sufficiency

Existing requirements sufficient. REVISED-7's change is an acceptance-completeness correction (isolation.md:293 repoint + dedicated acceptance check) within the S376 clean-sweep scope. No spec amendment required.

## Acceptance Criteria (carried forward from -021 + F1/-022 additions)

1. `memory/work_list.md` does not exist post-commit.
2. **Tracked acceptance grep** (F2/-012 form, now with `groundtruth-kb/docs/architecture/isolation.md` ADDED to the positive scope) returns 0:

   ```text
   git grep -l "work_list.md" -- \
     groundtruth-kb/src/ scripts/ platform_tests/ \
     .claude/rules/ .claude/skills/ .claude/hooks/ .codex/skills/ .agent/skills/ \
     config/ .githooks/ CLAUDE.md SECURITY.md \
     groundtruth-kb/templates/ groundtruth-kb/docs/architecture/isolation.md \
     "groundtruth-kb/tests/test_*.py" groundtruth-kb/tests/adopter/ groundtruth-kb/tests/fixtures/scaffold_golden/ \
     ":(exclude)scripts/_archive_*.py" ":(exclude)scripts/_insert_*.py" \
     ":(exclude)scripts/_record_*.py" ":(exclude)scripts/record_core_*.py"
   ```

2b. `rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills` returns 0.
3. `gt backlog list --json | jq length` >= 75.
4. `pytest platform_tests/scripts/ groundtruth-kb/tests/` passes (incl. adopter isolation tests with the check removed; governance-adoption migrated; migration tests removed).
6. 5 protected-narrative packets + 1 deletion packet exist; `check_narrative_artifact_evidence.py` PASS.
7. Applicability + clause preflights pass on the post-impl report.
8. F2/-012 ordering: `narrative-artifact-approval.toml` keeps `memory/work_list.md` until after the deletion (Phase 5).
10. `git ls-files --error-unmatch .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` → "did not match" (untracked).
11. Migration tooling retired (T-9c) returns 0.
12. Adopter isolation check retired (T-9d) returns 0; adopter isolation tests pass.
13. `isolation.md` no longer documents the removed check.
14. impl-auth begin → `authorized: true` (55-path).
15. **isolation.md residual cleared (F1/-022; T-9e):** `git grep -n "work_list\.md" -- groundtruth-kb/docs/architecture/isolation.md` returns 0; line 293 cites the MemBase `GTKB-ISOLATION-017-SLICE-5.5` reference.
16. **Adopter fixture deleted (T-9f):** `pre_isolation_with_managed_drift/memory/work_list.md` does not exist post-slice.

## Risk & Rollback

Risks: large surface (~50 tracked edits + adopter-isolation check removal + 1 untracked skill edit + 2 deletions [work_list.md + fixture]). Mitigation: Phase 6 acceptance greps (now incl. isolation.md + dedicated T-9e) + retired-check scan (T-9d) + full suite. cli.py/CLAUDE.md/backlog-namespace coordination per `-021` § Cross-Thread Coordination.

Rollback: `git revert <slice-commit-sha>` restores tracked changes (callers + retired tooling + retired check + isolation.md repoint + deletion targets). The untracked skill file reverts manually (line 51). MemBase unchanged.

---

Reviewer focus areas:
- F1/-022: does Phase 2.4b + Acceptance §2 (isolation.md added) + §15/T-9e fully close the isolation.md:293 residual? Is repointing to the MemBase `GTKB-ISOLATION-017-SLICE-5.5` reference the right substitute (vs deletion-as-historical)?
- Carried-forward: clean-sweep consumer completeness (C/S376), 55-path target_paths, migration-tooling retirement (implemented), governance-adoption test migration.

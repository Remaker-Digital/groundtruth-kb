REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — REVISED-5: machine-readable target_paths + migration-tooling retirement (supersedes GO'd -017)

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-30 (S376)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02`
Prior version: GO at `-018` (Codex approved REVISED-4 at `-017`). This REVISED-5 supersedes the GO'd `-017` for two Prime-discovered, post-GO implementation-prep reasons documented in § Findings Resolution: (A) `scripts/implementation_authorization.py begin` cannot parse `-017`'s annotated `## target_paths (...)` heading, so no implementation-start packet can be created; (B) `cli.py`/`backlog.py` contain the FUNCTIONAL `gt backlog migrate-work-list` migration tooling, which "reference removal" cannot address and which the acceptance grep requires to reach zero — resolved by the S376 owner decision to retire the migration tooling.
Status: REVISED

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490
target_paths: ["CLAUDE.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/rules/peer-solution-advisory-loop.md", ".claude/rules/acting-prime-builder.md", "config/governance/narrative-artifact-approval.toml", "config/agent-control/system-interface-map.toml", ".claude/hooks/narrative-artifact-approval-gate.py", ".githooks/pre-commit", ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", "scripts/session_self_initialization.py", "scripts/wrap_scan_consistency.py", "scripts/resolve_system_interface.py", "scripts/rehearse/_backlog_split.py", "scripts/rehearse/_dashboard_regen.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/operating_state.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/templates/project/README-quickstart.md", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md", "groundtruth-kb/templates/rules/canonical-terminology.md", "groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/README.md", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/README.md", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/tests/test_doctor_isolation.py", "groundtruth-kb/tests/test_operating_state.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/test_upgrade_isolation.py", "groundtruth-kb/tests/test_backlog.py", "platform_tests/hooks/test_narrative_artifact_approval.py", "platform_tests/scripts/test_cli_backlog_add.py", "platform_tests/scripts/test_cli_backlog_status.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_rehearse_backlog_split.py", "platform_tests/scripts/test_rehearse_dashboard_regen.py", "platform_tests/scripts/test_rehearse_inventory.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_standing_backlog_harvest.py", "platform_tests/scripts/test_system_interface_map.py", "platform_tests/scripts/test_wrap_scan_consistency.py", "memory/MEMORY.md", "memory/pending-owner-decisions.md", "memory/v1-release-strategy-deliberation-S347.md", "docs/gtkb-dashboard/startup-service-payload.json", "memory/work_list.md"]

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S376-work-list-md-retirement-slice-7-prime-revised-5
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

## Claim

REVISED-5 supersedes the GO'd `-017` (GO at `-018`) for two issues that Prime Builder discovered during post-GO implementation preparation, neither of which the preflights or the bridge review exercise:

- **A — `impl-auth begin` cannot parse `-017`'s target_paths (mechanical blocker).** `scripts/implementation_authorization.py begin --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` returns `{"authorized": false, "error": "Approved proposal is missing concrete target_paths or Files Expected To Change"}`. Root cause: the script's `section_body()` matches a section heading by exact case-insensitive equality (`found_heading.lower() == "target_paths"`), but `-017`'s heading is `## target_paths (live S376 re-probe; ...)` — the parenthetical annotation defeats the exact match, so all three extractor methods fall through. REVISED-5 adds a machine-readable `target_paths: [JSON array]` metadata line (the parser's primary method, `TARGET_PATHS_RE`), which sidesteps section parsing entirely. This also removes a latent over-authorization: `-017`'s `### Intentionally preserved` sub-bullets (`bridge/**`, `archive/**`, ...) would have been slurped into the heading-form extraction as authorized targets; method 1 never reaches them.

- **B — `cli.py`/`backlog.py` carry the FUNCTIONAL migration tooling (scope correction; S376 owner decision).** `-017` scoped `cli.py` as "reference removal," but the `work_list.md` references there are functional, not documentary: `groundtruth-kb/src/groundtruth_kb/cli.py` defines the `gt backlog migrate-work-list` command (reads & parses `memory/work_list.md`), and `groundtruth-kb/src/groundtruth_kb/backlog.py` provides its backend (`parse_work_list_markdown`, `_parse_work_list_table`, `_parse_active_section_items`, `parse_work_list_file`, `migrate_work_list_items`, `WorkListItem`). The acceptance grep requires `cli.py`/`backlog.py` to reach zero `work_list.md` references, which is impossible for a work_list.md migrator via "reference removal." The S376 owner decision (§ Owner Decisions / Input) retires the migration tooling, consistent with DELIB-S337 ("deletion AT MIGRATION CONCLUSION" — a lingering migrate-work-list command implies the migration is not concluded). This adds one consumer file to scope: `groundtruth-kb/tests/test_backlog.py` (imports `migrate_work_list_items`/`parse_work_list_markdown`; 2 migration tests removed to keep the suite green; it carries NO `work_list.md` literal, so it is a functional consumer, not an acceptance-grep target).

Everything else from `-017` (the F1/F1-from-014/F1-from-012 resolutions, the single `.claude` skill-file scope, the `rg --hidden` acceptance scan over 3 roots, the 6-packet approval plan, the governance-adoption test migration, the F2-from-012 ordering invariant, cross-thread coordination, spec links, prior deliberations) is carried forward unchanged. The migration-completion gate per `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` remains the operative directive.

## Findings Resolution

### A (P1, mechanical) — impl-auth begin cannot parse `-017` target_paths; machine-readable line added

Observation: `begin` failed against the GO'd `-017` (exit 2, "missing concrete target_paths"). The parser (`scripts/implementation_authorization.py:411-414, 455-497`) tries: (1) `target_paths: [json]` metadata line; (2) `## Files Expected To Change` section (all backtick spans); (3) `## target_paths` heading section (first backtick span per bullet). Method 3 is defeated by `-017`'s annotated heading.

Resolution: REVISED-5 adds the `target_paths: [JSON array]` metadata line (immediately under `Work Item: WI-3490`). The 50-path array enumerates exactly the authorized mutation set (the 43 tracked caller files re-confirmed live at S376, plus the 1 untracked skill file, plus `groundtruth-kb/tests/test_backlog.py` added per Finding B, plus the 3 notepad-tier memory files, the regenerated dashboard payload, and the deletion target `memory/work_list.md`). The prose `## target_paths` section is retained for human-readable detail but is no longer the parser's source.

This is a mechanical implementation-tooling correction. The friction itself (the parser's exact-heading match and `###`-subsection slurping) is captured separately as a GT-KB reliability backlog candidate; it is NOT fixed in this slice (that would be a separate protected-script change with its own bridge thread).

### B (owner decision) — migration tooling retired; test_backlog.py added to scope

Observation: `cli.py:532-575` (`backlog_migrate_work_list` command) and `backlog.py:97-` (`parse_work_list_markdown` family + `migrate_work_list_items`) are the functional migration tooling; `test_cli.py:94,128` and `test_backlog.py:23,41` test them. The acceptance grep requires `cli.py`/`backlog.py`/`test_cli.py` to reach zero `work_list.md` literals.

Resolution: S376 owner AUQ — retire the migration tooling. See § Migration Tooling Retirement for the precise scope. `test_backlog.py` is added to `target_paths` as a functional consumer (its 2 migration tests are removed; it has no `work_list.md` literal, so it is not an acceptance-grep target but must be updated to keep the suite green).

### F1 from -016 (RESOLVED in -017; carried forward unchanged)

`-016` F1 (skill-file target set stale; only `.claude` exists) is resolved by scoping the active skill edit to the single existing `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` (line 51) while retaining the `rg --hidden` scan over all 3 roots. Codex confirmed this at `-018` (GO). Carried forward verbatim; the S376 reproduce-first probe (§ Current State Evidence) re-confirms 1 file / 1 reference / 2 absent.

### F1 from -014 (RESOLVED in -015; carried forward unchanged)

`-014` F1 (acceptance gate misses untracked skill files because `git grep` is tracked-only) is resolved by the untracked-inclusive `rg --hidden` acceptance scan (§ Acceptance Criteria §2b). Carried forward.

### F1/F2 from -012 (RESOLVED in -013; carried forward unchanged)

- F1 from -012 (clause preflight blocking gap on `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`) — resolved by § Bridge Canonicality Evidence. Confirmed by clause preflight exit 0 through `-018`.
- F2 from -012 (acceptance grep / target_paths mismatch) — resolved by negative-pathspec rewrite + governance-adoption test addition.

## Migration Tooling Retirement (S376 owner decision)

Per the S376 owner AUQ (§ Owner Decisions / Input), the `gt backlog migrate-work-list` migration tooling is retired as part of reaching the "MemBase only" steady state. Precise scope:

- `groundtruth-kb/src/groundtruth_kb/cli.py`: remove the `backlog_migrate_work_list` command (the `@backlog.command("migrate-work-list")` block, ~lines 532-580) and its `--work-list` option; remove the residual docstring reference at ~line 661 ("it never mutates memory/MEMORY.md or memory/work_list.md" → "memory/MEMORY.md"). Post-edit `cli.py` carries zero `work_list.md` literals.
- `groundtruth-kb/src/groundtruth_kb/backlog.py`: remove the migration backend — `parse_work_list_markdown`, `_parse_work_list_table`, `_parse_active_section_items`, `parse_work_list_file`, `migrate_work_list_items`, and the `WorkListItem` dataclass if it is migration-only — along with the "Migrated from memory/work_list.md ..." description strings. Preserve all non-migration backlog backend functions (the `gt backlog list`/`status` read path). Post-edit `backlog.py` carries zero `work_list.md` literals.
- `groundtruth-kb/tests/test_cli.py`: remove the 2 migration tests (`test_backlog_migrate_work_list_json_dry_run`, `test_backlog_migrate_work_list_inserts_rows`, ~lines 94-152). Post-edit carries zero `work_list.md` literals.
- `groundtruth-kb/tests/test_backlog.py` (ADDED to scope): remove the 2 migration tests (`test_parse_work_list_markdown_preserves_duplicate_project_rows`, `test_migrate_work_list_items_inserts_missing_rows`) and the `from groundtruth_kb.backlog import migrate_work_list_items, parse_work_list_markdown` import + `SAMPLE_WORK_LIST` fixture. Preserve all non-migration backlog tests. This file carries NO `work_list.md` literal; it is a functional consumer updated to keep the suite green, not an acceptance-grep target.

Consumer completeness: a repo-wide search for `parse_work_list_file|migrate_work_list_items|migrate-work-list|migrate_work_list` (excluding `bridge/**`, `archive/**`, and `.pytest-*` temp dirs) returns exactly `cli.py`, `backlog.py`, `test_cli.py`, and `test_backlog.py` as live consumers. All four are in `target_paths`. No other live caller references the migration tooling.

Migration data-preservation note: the migration's PURPOSE (moving work_list.md rows into MemBase `work_items`) was completed by prior slices; `GOV-STANDING-BACKLOG-001` v3 + `PB-STANDING-BACKLOG-CONTINUITY-001` continuity is preserved (Acceptance §3: `gt backlog list --json | jq length >= 75`). Retiring the tool removes the now-obsolete one-time migration path; it does not remove any migrated data.

## Bridge Canonicality Evidence (F1 from -012 resolution; carried forward; satisfies GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This implementation proposal and its entire thread comply with `GOV-FILE-BRIDGE-AUTHORITY-001`: `bridge/INDEX.md` is the canonical workflow state, and both agents trust `bridge/INDEX.md` over any other signal.

- This REVISED-5 artifact is filed as `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-019.md` under `bridge/`, and a correct-status `REVISED:` line for it is inserted at the top of this thread's version list in `bridge/INDEX.md` (immediately above the prior `GO: ...-018.md` line).
- No prior bridge version is deleted or rewritten. Versions `-008` (VERIFIED) through `-018` (GO) remain on disk byte-for-byte; the bridge files are an append-only audit trail. This REVISED supersedes `-017` by adding a higher version, never by mutating `-017`. The `-018` GO remains valid historical evidence for `-017`'s plan; REVISED-5 re-opens the thread for review of the two corrections above.
- The implementation phase governed by this proposal does NOT delete any bridge file, does NOT mutate any existing `bridge/INDEX.md` entry's prior version lines, and does NOT claim VERIFIED without an INDEX entry. The only file deletion in scope is `memory/work_list.md` (a notepad-tier backlog view, NOT a bridge artifact), gated by its own formal-artifact-approval packet per § Phase 3.6.
- Post-implementation, the eventual VERIFIED verdict for this thread will be recorded as a new top-of-entry line in `bridge/INDEX.md`, preserving the append-only chain.

## target_paths (machine-readable line above is authoritative for the parser; this prose is human-readable detail)

The machine-readable `target_paths: [...]` metadata line near the top of this document is the authoritative source for `scripts/implementation_authorization.py`. This prose section enumerates the same 50-path set, grouped and annotated for human review. Authorized mutation set (PAUTH allowed_mutation_classes: source_code, test_code, config, rule_file, narrative_artifact, file_deletion, membase).

Protected narrative artifacts (require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`):
- `CLAUDE.md` (reference removal; coordinate with in-flight `gtkb-claude-md-scope-clarification-slice-3` thread — see § Cross-Thread Coordination)
- `.claude/rules/canonical-terminology.md` (Lifecycle endpoint subsection refresh)
- `.claude/rules/operating-model.md` §2 backlog entry (closing paragraph refresh)
- `.claude/rules/peer-solution-advisory-loop.md` (reference removal)
- `.claude/rules/acting-prime-builder.md` (Standing Backlog Principle reference removal)

Configuration:
- `config/governance/narrative-artifact-approval.toml` (drop `memory/work_list.md` from protected paths — POST-DELETION cleanup, Phase 5)
- `config/agent-control/system-interface-map.toml` (reference removal)

Hooks (Claude + Codex parity):
- `.claude/hooks/narrative-artifact-approval-gate.py` (reference removal in docstring/comments at line 6 + Phase 5.2 code-path cleanup; NOT removing the file from protected paths until Phase 5)
- `.githooks/pre-commit` (drop work_list.md-specific drift detection)

Skills (authorized active required update per S375/S376 F1 resolution; live `rg --hidden` finds 1 reference in the single existing file; per-file edit plan in § Skill File Edit Plan above; file remains untracked per S375 owner AUQ):
- `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` (line 51 swap; untracked)

The `.codex/skills/...` and `.agent/skills/...` paths cited in `-015` are absent in the live tree and are NOT in scope (S376 `test -f` → MISSING; not created by this slice).

Platform source code (migration tooling RETIRED in cli.py/backlog.py per § Migration Tooling Retirement; others reference-removal):
- `scripts/session_self_initialization.py` (replace markdown parse with `gt backlog list --json` + JSON priority sort)
- `scripts/wrap_scan_consistency.py` (reference removal)
- `scripts/resolve_system_interface.py` (reference removal)
- `scripts/rehearse/_backlog_split.py` (reference removal)
- `scripts/rehearse/_dashboard_regen.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/backlog.py` (RETIRE migration backend per § Migration Tooling Retirement)
- `groundtruth-kb/src/groundtruth_kb/operating_state.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` (reference removal in scaffold templates; new adopters will not get work_list.md)
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (RETIRE `migrate-work-list` command + docstring ref per § Migration Tooling Retirement — see § Cross-Thread Coordination for the 435-line uncommitted-parallel-work coordination)
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py` (reference removal)

Adopter scaffold templates (future-proofs the retirement):
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`
- `groundtruth-kb/templates/project/README-quickstart.md`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
- `groundtruth-kb/templates/rules/canonical-terminology.md`

Tests (assertion updates + reference removal; migration-test removal in test_cli.py/test_backlog.py per § Migration Tooling Retirement):
- `groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/README.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/README.md`
- `groundtruth-kb/tests/test_cli.py` (remove 2 migration tests + reference removal)
- `groundtruth-kb/tests/test_doctor_isolation.py`
- `groundtruth-kb/tests/test_operating_state.py`
- `groundtruth-kb/tests/test_scaffold_isolation.py`
- `groundtruth-kb/tests/test_upgrade_isolation.py`
- `groundtruth-kb/tests/test_backlog.py` (ADDED — functional consumer of retired migration backend; remove 2 migration tests + import + SAMPLE_WORK_LIST fixture; NO `work_list.md` literal, so not an acceptance-grep target)
- `platform_tests/hooks/test_narrative_artifact_approval.py`
- `platform_tests/scripts/test_cli_backlog_add.py`
- `platform_tests/scripts/test_cli_backlog_status.py`
- `platform_tests/scripts/test_groundtruth_governance_adoption.py` (F2-from-012 resolution; see § Governance-Adoption Test Migration)
- `platform_tests/scripts/test_rehearse_backlog_split.py`
- `platform_tests/scripts/test_rehearse_dashboard_regen.py`
- `platform_tests/scripts/test_rehearse_inventory.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_standing_backlog_harvest.py`
- `platform_tests/scripts/test_system_interface_map.py`
- `platform_tests/scripts/test_wrap_scan_consistency.py`

Notepad-tier memory files (touched, no approval packet per ADR-0001):
- `memory/MEMORY.md` (reference removal)
- `memory/pending-owner-decisions.md` (reference removal)
- `memory/v1-release-strategy-deliberation-S347.md` (reference removal)

Generated/regenerated artifacts:
- `docs/gtkb-dashboard/startup-service-payload.json` (regenerated)
- `.codex/gtkb-hooks/last-user-visible-startup.md` (regenerated by SessionStart hook — not directly edited; NOT in target_paths)

Final deletion target:
- `memory/work_list.md` (deletion; requires `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` formal-artifact-approval packet)

### Intentionally preserved as historical/evidence (NOT in target_paths; NOT modified; excluded from acceptance grep)

These surfaces contain `work_list.md` references that are evidentiary, append-only, or historical-by-design. The acceptance grep (§ Acceptance Criteria §2) excludes these via positive-scope omission and explicit negative pathspecs:

- `bridge/**` — bridge protocol append-only audit trail per `.claude/rules/file-bridge-protocol.md`
- `archive/**` — explicitly archived artifacts (incl. `archive/backlog-adds-2026-05-11/add_backlog_items.py`)
- `.groundtruth/formal-artifact-approvals/**` — formal approval packet audit trail
- `independent-progress-assessments/**` — Loyal Opposition reports (historical)
- `.codex/gtkb-hooks/last-user-visible-startup-*` — generated startup cache (regenerated, not manually edited)
- `scripts/_archive_*.py`, `scripts/_insert_*.py`, `scripts/_record_*.py`, `scripts/record_core_*.py` — historical one-off script classes (negative pathspecs)
- `groundtruth-kb/CHANGELOG.md`, `groundtruth-kb/release-notes-*.md`, `groundtruth-kb/docs/announcements/`, `groundtruth-kb/docs/architecture/isolation.md`, `groundtruth-kb/docs/reports/` — historical release/architecture/report docs
- `applications/Agent_Red/docs/`, `applications/Agent_Red/tests/fixtures/` — adopter-side historical documentation + CI fixture snapshots
- `docs/gtkb-dashboard/*.pdf` — binary historical artifacts
- `.pytest-*` temp dirs (e.g. `.pytest-prime-s366/backlog-snapshot.json`) — pytest temp output, gitignored

## KB-Mutation Scope & Cited-WI Clarification (PreToolUse gate responses; carried forward from -013/-015/-017)

Two PreToolUse governance checkpoints fired on prior Writes and are re-answered here for -019:

- **KB-mutation completeness (groundtruth.db not in target_paths — confirmed intentional):** Slice 7-prime performs NO `groundtruth.db` mutation. It READS MemBase (`gt backlog list --json`, `db.get_spec`/`list_work_items` for the Phase 1.2 diff) but writes only files. No `insert_*`/`update_*`/spec-promotion/work-item-resolution occurs. `target_paths` correctly omits `groundtruth.db`. The `membase` token in the PAUTH `allowed_mutation_classes` is broader than this slice exercises; it is not invoked.
- **Cited-WI collision (WI-3355, WI-3420):** the proposal's declared work item is `WI-3490` (matches MemBase). `WI-3355` and `WI-3420` appear ONLY in § Cross-Thread Coordination as references to the entangled `cli.py` work-streams; they are coordination context, not additional declared work items. `GTKB-GOV-000` (and family) appear only inside § Governance-Adoption Test Migration as the test's asserted milestone IDs, not as work items.

## Governance-Adoption Test Migration (F2-from-012 detail for `platform_tests/scripts/test_groundtruth_governance_adoption.py`; carried forward)

This live test has three distinct `work_list.md` couplings (confirmed by `git grep -n work_list` at S374; reconfirmed at S375/S376). Each is migrated so the file carries zero `work_list.md` literal post-slice:

1. **`test_work_queue_prioritizes_candidate_skill_and_doctor_items`:** currently `_read("memory/work_list.md")` then content assertions on governance-adoption milestone records (GTKB-GOV-000 family, DELIB IDs, packet filenames). These milestone records were migrated to MemBase and are independently asserted against the `acting-prime-builder.md` rule by a sibling test. Migration: repoint these assertions to the surviving canonical surfaces — MemBase `work_items` (via `db`/`gt backlog list --json`) and/or the already-asserted rule-file content — or remove pure duplicates. Phase 1.2's pre-retirement diff produces the milestone-ID -> MemBase-row mapping.
2. **`assert "memory/work_list.md" in rule`:** part of the acting-prime-builder.md rule-content test. Since the slice updates acting-prime-builder.md to drop the "work_list.md as the standing-backlog authority" language, this assertion is removed/repointed to the replacement language.
3. **`assert "memory/work_list.md" in (spec["source_paths"] or "")`:** a MemBase `source_paths` provenance assertion. The specs' historical `source_paths` field is append-only and is NOT mutated; the assertion is relaxed to require `source_paths` is populated (non-empty) rather than pinning the retired literal path.

Acceptance: after migration the file passes (`pytest`) AND contains no `work_list.md` literal.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate (carried forward; unchanged):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; see § Bridge Canonicality Evidence for clause-level evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test plan below derives from each linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts remain under `E:\GT-KB`; templates/ tree updates are platform-side adopter scaffold work.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for protected narrative artifacts touched. Packet set: 5 narrative updates (CLAUDE.md, canonical-terminology, operating-model, peer-solution-advisory-loop, acting-prime-builder) PLUS the deletion-specific packet for memory/work_list.md. The single untracked skill file and the source/test edits (migration-tooling retirement) DO NOT require packets (not protected narrative artifacts per `config/governance/narrative-artifact-approval.toml`).
- `GOV-STANDING-BACKLOG-001` v3 — durable cross-session work authority; preserved.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate constraint; this slice IS the gate.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority architecture; reaches post-migration steady state. Cited in the skill-file replacement text.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — owner directive (operative); the migration-tooling retirement directly serves the "migration conclusion" semantics.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — removes hand-maintained markdown plumbing surface AND the obsolete one-time migration tool.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — continuity preserved; MemBase `work_items` is the durable surface; `gt backlog list --json` is the readable surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal cites project-linkage triplet.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — PAUTH cites linked specs.

Advisory (per applicability preflight content-pattern matches):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

Predecessor / superseded references:
- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (superseded by DCL-STANDING-BACKLOG-DB-SCHEMA-001 v2 in Slice B; preserved as historical evidence).

Sibling thread context:
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` — Slice 1 VERIFIED (governance scaffolding).
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-017.md` — REVISED-4 (GO'd at -018; superseded by this REVISED-5 for the two corrections above).
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-018.md` — Codex GO on -017 (historical; the plan it approved is corrected here).
- `bridge/gtkb-backlog-work-list-retirement-directive-001-012.md` — Slice A+B VERIFIED (deletion-endpoint scaffolding).

## Prior Deliberations

(Carried forward; full list preserved.)

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — operative.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — foundational.
- `DELIB-0838` — standing backlog authority preserved.
- `DELIB-0839` — backlog_snapshots unaffected.
- `DELIB-0835` — scoped auto-approval pattern; used for the 6-packet batch (5 narrative updates + 1 deletion); ACTIVATED by S376 owner AUQ.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — alignment.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — freeze lifted.

S376 deliberation context (Prime-side): the two REVISED-5 changes are a mechanical tooling-parse correction (A) and an owner-decided scope clarification (B). Neither introduces a design question requiring new deliberation search beyond the carried-forward set. The S376 owner AUQ on migration-tooling retirement is recorded in § Owner Decisions / Input.

## Owner Decisions / Input

Carried forward from -009/-011/-013/-015/-017 (owner AUQ at S373 Path A; S375 AUQ edit-in-place/keep-untracked) plus the new S376 AUQ:

- **S376 AUQ — "When memory/work_list.md is deleted, what happens to the `gt backlog migrate-work-list` migration tooling that functionally reads it?"**
  - Owner answer: **"Retire the migration tooling"** (Option A; Recommended).
  - Decision content: remove the `gt backlog migrate-work-list` command (cli.py), its backend (`parse_work_list_markdown` family + `migrate_work_list_items` in backlog.py), and the 4 migration tests across test_cli.py (2) and test_backlog.py (2). Consistent with DELIB-S337 migration-conclusion semantics. See § Migration Tooling Retirement.
  - Decision class: scope decision / behavior change (in-scope per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel).
  - Recorded: `memory/pending-owner-decisions.md` (auto-recorded by `.claude/hooks/owner-decision-tracker.py` on S376 AUQ resolution; `detected_via: ask_user_question`).

- **S376 AUQ — formal-artifact-approval activation.** Owner answer: **"Scoped auto-approval + implement now"**. Activates DELIB-0835 scoped auto-approval (`auto_approval_scope: work-list-retirement-slice-7-prime-batch-2026-05-30`) for the 6-packet batch (5 narrative updates + 1 deletion); each protected edit + the deletion is still displayed for transcript capture per the audit requirement.

- **S375 AUQ — skill-file handling** ("Edit in place; keep untracked"; applies to the single existing `.claude` skill file). Carried forward.

- **S373 AUQ — migration-completion path** (Path A "Migration retirement"; authorizes the deletion endpoint per DELIB-S337). Carried forward.

No new owner approval is required beyond the S376 AUQs already captured. REVISED-5's change A is mechanical; change B is the S376 owner-decided retirement.

## Current State Evidence (re-probed fresh at S376 / -019 filing time)

Reproduce-first guard (run from `E:\GT-KB`, S376), actual output:

```text
=== test -f on the 3 skill files ===
EXISTS:  .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md
MISSING: .codex/skills/loyal-opposition-hygiene-assessment/SKILL.md
MISSING: .agent/skills/loyal-opposition-hygiene-assessment/SKILL.md

=== rg --hidden work_list.md scan over 3 skill dirs ===
.claude/skills\loyal-opposition-hygiene-assessment\SKILL.md:51:- `memory/work_list.md` (only when backlog/work-item hygiene is in scope)
(rg exit: 0)
```

impl-auth begin probe (S376), actual output:

```text
{"authorized": false, "error": "Approved proposal is missing concrete target_paths or Files Expected To Change"}
(begin exit: 2)
```

Migration-tooling consumer probe (S376): `parse_work_list_file|migrate_work_list_items|migrate-work-list|migrate_work_list` over the repo (excluding bridge/archive/pytest-temp) returns live consumers: `cli.py`, `backlog.py`, `test_cli.py`, `test_backlog.py` — all in `target_paths`.

Other current-state evidence (carried forward):
- `gt backlog --help` subcommands: `add`, `add-work-item`, `list`, `migrate-work-list`, `show`, `status` (note: `migrate-work-list` is the command being retired by this slice).
- `gt backlog list --help` flags: `--json`, `--all` (`--priority` does NOT exist; F3 from -010 stays resolved).
- Live tracked caller re-harvest (acceptance-grep shape, literal `work_list.md`): 43 tracked files; all in `target_paths`. `test_backlog.py` is NOT among them (no literal), consistent with its functional-consumer classification.
- `git ls-files --error-unmatch .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` returns "did not match" — confirms untracked status of the single skill file.

## Cross-Thread Coordination Points

(Carried forward; unchanged. Codex review should confirm sequencing.)

1. **`groundtruth-kb/src/groundtruth_kb/cli.py`** — modified in the working tree by ~435 uncommitted lines from 4 in-flight parallel work-streams (WI-3420 hygiene group, generate-approval-packet command, bridge_group add_command, reconcile-doubled-prefix) per the WI-3355 S373 handoff. Slice 7-prime's cli.py edit (migration-tooling retirement) is an additional change on top of that uncommitted state. Recommendation: the Slice 7-prime cli.py change commits as part of a cumulative cli.py commit that documents the other thread refs (Codex -014 non-blocking guidance accepts cumulative if documented); committing cli.py alone is known to break `import groundtruth_kb.cli` per the S373 handoff.
2. **`CLAUDE.md`** — in-flight `gtkb-claude-md-scope-clarification-slice-3-implementation` (NO-GO at -010 per AXIS-2 surface) also modifies CLAUDE.md. Recommendation: coordinate the CLAUDE.md update across both threads' approval packets, OR sequence the slice-3 thread's resolution first.

These coordination points are surfaced for Codex review awareness; the recommended sequencing is non-binding pending Codex's view.

### Codex -014 Non-Blocking Reviewer Guidance acknowledgement (carried forward)

- **S332 directive content destination**: treat `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` as the preserved S332 decision record; Phase 1.4 verifies it remains DA-retrievable; no new MemBase mutation added.
- **cli.py + CLAUDE.md coordination sequencing**: cumulative patch acceptable if the implementation report documents the other thread refs and shows no approved scope was overwritten.
- **Single cumulative commit**: acceptable only if the report proves the deletion packet existed before physical deletion AND the protected-path registry was cleaned up AFTER the deletion. Phase 3.6 + Phase 4.2 + Phase 5.1 sequencing encodes this; the post-impl report will cite each artifact's timestamp.

## Implementation Plan (carried forward; migration-tooling-retirement deltas marked)

### Phase 1 — Read-only verification (no mutations)

1.1. Run `python -m groundtruth_kb backlog list --json > .tmp/backlog-pre-retirement.json` and assert count >= 75.
1.2. Diff table-row identifiers in `memory/work_list.md` against MemBase IDs; document delta (drives the § Governance-Adoption Test Migration).
1.3. Refresh caller audit with BOTH (a) the tracked acceptance grep AND (b) the `rg --hidden` skill scan; re-confirm migration-tooling consumer set (4 files). `target_paths` complete (re-confirmed at S376).
1.4. Verify `DELIB-S332-...` remains DA-retrievable; record in post-impl report. No new MemBase mutation.

### Phase 2 — Caller updates (non-protected, no approval packet)

2.1. **Skill (1 file; file remains untracked per S375 AUQ):** `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` line 51 swap to `python -m groundtruth_kb backlog list` per § Skill File Edit Plan. Post-edit `rg --hidden` over 3 roots returns 0.
2.2. Scripts (5 files): `session_self_initialization.py` (markdown parse -> `gt backlog list --json` + JSON priority sort, NOT a `--priority` flag), `wrap_scan_consistency.py`, `resolve_system_interface.py`, `rehearse/_backlog_split.py`, `rehearse/_dashboard_regen.py` — reference removal.
2.3. **Platform source (6 files; cli.py + backlog.py = MIGRATION-TOOLING RETIREMENT per § Migration Tooling Retirement):** `backlog.py` (remove migration backend), `cli.py` (remove migrate-work-list command + docstring ref; cumulative-commit coordination per § Cross-Thread Coordination), `operating_state.py`, `scaffold.py`, `doctor_isolation.py`, `cli_backlog_add.py` — latter four reference removal.
2.4. Adopter scaffold templates (4 files): update so new adopters do not receive work_list.md.
2.5. **Tests (20 files; test_cli.py + test_backlog.py = migration-test removal):** update assertions; reference removal; `test_groundtruth_governance_adoption.py` per § Governance-Adoption Test Migration; `test_cli.py` remove 2 migration tests; `test_backlog.py` remove 2 migration tests + import + SAMPLE_WORK_LIST fixture (keep non-migration backlog tests).
2.6. Hooks (2 files): `.claude/hooks/narrative-artifact-approval-gate.py` (docstring ref removal at line 6 — NOT removing the protected-path entry; that's Phase 5), `.githooks/pre-commit` (drop work_list.md drift detection).
2.7. Configs (1 file now): `config/agent-control/system-interface-map.toml` reference removal. (`narrative-artifact-approval.toml` deferred to Phase 5.)
2.8. Notepad-tier memory (3 files): MEMORY.md, pending-owner-decisions.md, v1-release-strategy-deliberation-S347.md — reference removal; no packet per ADR-0001.

### Phase 3 — Formal-artifact-approval packets (protected paths + deletion)

3.1-3.5. Update packets for CLAUDE.md, canonical-terminology.md, operating-model.md, peer-solution-advisory-loop.md, acting-prime-builder.md (action: update).
3.6. Deletion-specific approval packet `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` (action: delete; target_path: memory/work_list.md) — evidence chain cites DELIB-S337 + S373 AUQ + S375 AUQ + S376 AUQ + predecessor `2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json`.

All 6 packets request `approval_mode: auto`, `auto_approval_scope: work-list-retirement-slice-7-prime-batch-2026-05-30` (activated by the CLAUDE.md primary packet per DELIB-0835; S376 owner AUQ activated the scope).

### Phase 4 — Protected narrative artifact updates + physical removal (gate-accepted sequence)

4.1. Edit/Write the 5 protected narrative artifact updates. Each Write triggers `narrative-artifact-approval-gate.py`; gate accepts each packet from Phase 3.
4.2. Execute physical deletion of `memory/work_list.md`. Gate accepts the action=delete packet from Phase 3.6 (gate-approved, not bypassed).
4.3. Regenerate `docs/gtkb-dashboard/startup-service-payload.json`.

Phase 4 does NOT touch `config/governance/narrative-artifact-approval.toml`; the protection-registry entry remains intact through deletion.

### Phase 5 — Post-deletion cleanup

5.1. Drop `memory/work_list.md` from `config/governance/narrative-artifact-approval.toml` protected paths (safe now — file gone).
5.2. Drop work_list.md-related code paths in `.claude/hooks/narrative-artifact-approval-gate.py`.

### Phase 6 — Verification

6.1. `python -m pytest platform_tests/scripts/ groundtruth-kb/tests/ -q --tb=short` — all touched tests pass (incl. migrated governance-adoption test; migration tests removed in test_cli.py/test_backlog.py; suite green).
6.2. `python scripts/release_candidate_gate.py --skip-python --skip-frontend` — no new failure class.
6.3. `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` — no new failure class.
6.4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — preflight_passed: true.
6.5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — exit 0.
6.6. `python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md .claude/rules/canonical-terminology.md .claude/rules/operating-model.md .claude/rules/peer-solution-advisory-loop.md .claude/rules/acting-prime-builder.md` — PASS.
6.7. Tracked acceptance grep (§ Acceptance Criteria §2) — 0 matches.
6.7b. `rg --hidden` skill scan (§ Acceptance Criteria §2b) — 0 matches over 3 roots.
6.7c. Migration-tooling-retired check: `git grep -n "migrate-work-list\|parse_work_list\|migrate_work_list_items" -- groundtruth-kb/src/ groundtruth-kb/tests/` returns 0 (tooling fully retired; no orphan caller).
6.8. Targeted secret scan on changed files.
6.9. `python -m ruff check` + `python -m ruff format --check` on all changed `.py` files (separate gates).

## Spec-Derived Test Plan

| Test | Spec | Method |
|---|---|---|
| T-1 | DELIB-S337 deletion endpoint reached | `assert not os.path.exists('memory/work_list.md')` post-commit |
| T-2 | DCL-STANDING-BACKLOG-DB-SCHEMA-001 v2 migration-completion gate | `gt backlog status` exits 0; reports clean migration state |
| T-3 | GOV-STANDING-BACKLOG-001 v3 authority preserved | `gt backlog list --json | jq length` >= 75 (count preserved) |
| T-4 | PB-STANDING-BACKLOG-CONTINUITY-001 | Pre/post diff: same work_items identifiers via `gt backlog list --json` |
| T-5 | ADR-ISOLATION-APPLICATION-PLACEMENT-001 root-boundary | All touched paths under `E:\GT-KB`; no `applications/Agent_Red/` direct mutations |
| T-6 | GOV-ARTIFACT-APPROVAL-001 packet evidence | All 6 protected-artifact packets (5 updates + 1 deletion) exist; SHA256 matches |
| T-7 | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal's preflight passes (see § Preflight Result) |
| T-8 | GOV-FILE-BRIDGE-AUTHORITY-001 (F1 from -012) | Clause preflight exit 0; append-only chain preserved |
| T-9 | Scoped no-residual-callers (tracked; F2 from -012) | Tracked-file acceptance grep returns 0 |
| T-9b | No-residual-callers across untracked skill files (F1 from -014/-016) | `rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills` returns 0 |
| T-9c | Migration tooling retired (B / S376) | `git grep -n "migrate-work-list\|parse_work_list\|migrate_work_list_items" -- groundtruth-kb/src/ groundtruth-kb/tests/` returns 0; suite green |
| T-10 | Session startup unaffected | `python scripts/session_self_initialization.py --dry-run`; excludes work_list.md; uses `--json` |
| T-11 | Dashboard payload regenerated | `docs/gtkb-dashboard/startup-service-payload.json` no longer references work_list.md |
| T-12 | F2-from-012 deletion-evidence path | `narrative-artifact-approval-gate.py` accepts the action=delete packet; protection-registry intact at deletion moment |
| T-13 | Governance-adoption test migrated (F2 from -012) | `pytest platform_tests/scripts/test_groundtruth_governance_adoption.py` passes; no `work_list.md` literal |
| T-14 | Existing test suite green | `pytest platform_tests/ groundtruth-kb/tests/ -q` |
| T-15 | Skill file updated in place; remains untracked (F1 from -014/-016) | `git ls-files --error-unmatch .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` returns "did not match" post-slice; replacement-text present |
| T-16 | impl-auth begin parseable (A / S376) | `python scripts/implementation_authorization.py begin --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` returns `authorized: true` against the machine-readable target_paths |

## Preflight Result (to be verified pre-index via --content-file at S376)

Applicability + clause preflights are run against this `-019` content BEFORE indexing using `--content-file`. Expected: applicability `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`; clause exit 0, `Blocking gaps: 0`. The citation set is identical to `-017` (which `-018` GO confirmed passes); REVISED-5 adds no new required spec. Reviewer re-runs against the indexed operative `-019`.

## Clause Applicability Result (F1-from-012 evidence; verified pre-index via --content-file at S376)

Clause preflight run against `-019` content pre-index. Expected: exit 0, `Blocking gaps: 0`; `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` reports `Evidence found: yes` (§ Bridge Canonicality Evidence carried forward); `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` reports `Evidence found: yes`.

## Requirement Sufficiency

Existing requirements sufficient. No new requirement is needed. REVISED-5's change A is implementation-tooling format (machine-readable target_paths); change B is the S376 owner-decided migration-tooling retirement, which directly serves DELIB-S337's "migration conclusion" directive. Neither requires a spec amendment.

## Open Decisions for Codex / Owner

1. **cli.py coordination sequencing**: cumulative cli.py commit documenting the 4 parallel work-streams + the Slice 7-prime migration-tooling retirement, OR sequence-before. Prime preference is cumulative-with-documentation given the 435-line uncommitted entanglement (committing cli.py alone breaks the import). (Codex -014 guidance accepts cumulative if documented.)
2. **CLAUDE.md coordination**: cumulative-with-documentation vs sequence the slice-3 thread first.
3. **Governance-adoption test migration target (F2-from-012)**: MemBase-row assertions vs removal-as-duplicate-of-rule-content-test. Prime preference: migrate tracked-WI milestones to MemBase assertions; remove pure duplicates.

## Risk & Rollback

Risks:
- ~46 tracked file edits + 1 untracked skill edit + migration-tooling retirement is a large surface. Mitigation: Phase 6 acceptance greps + `rg --hidden` + migration-retired check (T-9c) are the mechanical gates; full test suite (T-14) catches retirement breakage.
- Migration-tooling retirement removes a user-facing CLI command (`gt backlog migrate-work-list`). Mitigation: owner-decided (S376 AUQ); consumer set proven complete (4 files); migrated DATA is preserved (T-3/T-4); rollback restores the command via git revert.
- cli.py coordination (435 uncommitted lines; see § Cross-Thread Coordination).
- CLAUDE.md coordination (in-flight slice-3 thread).
- Template tree changes affect future adopters; scaffold-golden tests gate this.
- The 1 skill-file edit lands on an untracked file; git-revert cannot restore it by SHA. Mitigation: single one-line swap with documented replacement text; manual restore straightforward.

Rollback: `git revert <slice-commit-sha>` restores all tracked changes (callers + retired migration tooling + deletion target) in one operation. For the 1 untracked skill file, manual edit reverts line 51. MemBase rows unchanged; no MemBase rollback needed.

## Acceptance Criteria (scoped, executable-as-written, verified S376)

1. `memory/work_list.md` does not exist post-commit.
2. **Scoped acceptance grep over tracked files** (F2-from-012; exit 0; excludes 8 historical script classes; every returned path in `target_paths`):

   ```text
   git grep -l "work_list.md" -- \
     groundtruth-kb/src/ scripts/ platform_tests/ \
     .claude/rules/ .claude/skills/ .claude/hooks/ .codex/skills/ .agent/skills/ \
     config/ .githooks/ CLAUDE.md SECURITY.md \
     groundtruth-kb/templates/ \
     "groundtruth-kb/tests/test_*.py" groundtruth-kb/tests/adopter/ groundtruth-kb/tests/fixtures/scaffold_golden/ \
     ":(exclude)scripts/_archive_*.py" ":(exclude)scripts/_insert_*.py" \
     ":(exclude)scripts/_record_*.py" ":(exclude)scripts/record_core_*.py"
   ```

   returns 0 matches post-slice. Note: cli.py/backlog.py reach 0 via the migration-tooling retirement (§ Migration Tooling Retirement); test_cli.py reaches 0 via migration-test removal. `test_backlog.py` carries no `work_list.md` literal so it does not appear in this grep, but its migration tests are removed (T-9c / suite-green).

2b. **Supplemental `rg --hidden` acceptance scan over untracked skill directories** (F1 from -014/-016; verified S376):

   ```text
   rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills
   ```

   returns 0 matches post-slice. Only `.claude/skills/` contains a file in the live tree; the broader scope future-proofs against re-creation with a stale reference.

3. `python -m groundtruth_kb backlog list --json | jq length` >= 75.
4. `pytest platform_tests/scripts/ groundtruth-kb/tests/` passes (incl. migrated governance-adoption test; migration tests removed; suite green).
5. `release_candidate_gate.py` exits with same baseline failure class as immediately pre-impl.
6. All 5 protected-narrative-artifact updates AND the 1 deletion packet exist; validated by `check_narrative_artifact_evidence.py`.
7. Applicability preflight + clause preflight both pass on the post-impl report (clause exit 0).
8. F2-from-012 ordering invariant: `config/governance/narrative-artifact-approval.toml` still contains `memory/work_list.md` at the moment of the deletion Write/Edit; entry dropped only in Phase 5.
9. No occurrence of literal `--priority` in any new/modified .py / SKILL.md / .toml under slice scope (F3 from -010).
10. `git ls-files --error-unmatch .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` returns "did not match" post-slice (file untracked per S375 AUQ).
11. **Migration tooling retired (B / S376):** `git grep -n "migrate-work-list\|parse_work_list\|migrate_work_list_items" -- groundtruth-kb/src/ groundtruth-kb/tests/` returns 0; full suite green (T-14).
12. **impl-auth begin parseable (A / S376):** `python scripts/implementation_authorization.py begin --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` returns `authorized: true` (machine-readable target_paths resolves).

---

Reviewer focus areas:
- A (begin parse): is the machine-readable `target_paths:` line correct and complete (50 paths)? Does it resolve the begin failure? Does it correctly exclude the `### Intentionally preserved` paths from authorization?
- B (migration tooling retirement): is the consumer set complete (cli.py, backlog.py, test_cli.py, test_backlog.py)? Is retiring `gt backlog migrate-work-list` the right migration-conclusion end-state? Is migrated DATA preservation (T-3/T-4) sufficient evidence that no data is lost?
- Carried-forward: skill-file single-file scope (F1 from -016), `rg --hidden` scan (F1 from -014), acceptance grep (F2 from -012), governance-adoption test migration, cross-thread coordination (cli.py 435-line entanglement; CLAUDE.md slice-3).

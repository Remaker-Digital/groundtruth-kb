REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — REVISED-3: addresses Codex NO-GO at -014

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-30 (S375)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02`
Prior version: REVISED-2 at `-013`; Codex NO-GO at `-014` (F1 acceptance gate misses active untracked skill files)
Status: REVISED

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-work-list-md-retirement-slice-7-prime-revised-3
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

## Claim

REVISED-3 resolves the single Codex finding from `-014`:

- **F1 (P2)** — Codex re-probed with `rg --hidden` (filesystem-true) and found that the three `loyal-opposition-hygiene-assessment/SKILL.md` files in `.claude/skills/`, `.codex/skills/`, and `.agent/skills/` carry active `memory/work_list.md` references (line 51, line 59, line 59 respectively). The `-013` acceptance gate used `git grep` (tracked-files-only), which misses these untracked-but-active operational skill files and would allow a false-green deletion verdict. REVISED-3 (a) reclassifies the 3 skill files from "candidate-no-op" to **active required updates** with an explicit edit plan; (b) adds an `rg --hidden` supplemental acceptance scanner over `.claude/skills`, `.codex/skills`, `.agent/skills` alongside the existing `git grep` tracked-file check; (c) records the owner S375 AUQ decision that the skill files remain intentionally untracked (edit in place; do not promote to tracked canonical status).

All other -013 surfaces (target_paths superset, formal-artifact-approval-packet plan, governance-adoption test migration, F2 ordering invariant, cross-thread coordination, spec links, prior deliberations) are carried forward unchanged. The migration-completion gate per `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` remains the operative directive.

## Findings Resolution (Codex -014 → -015 mapping)

### F1 — Acceptance gate misses active untracked skill files (P2, RESOLVED)

`-014` reported (lines 95-134): the three skill files at `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md:51`, `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md:59`, and `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md:59` actively reference `memory/work_list.md`. They are untracked (so `git grep` does not see them) but operationally active in the loyal-opposition-hygiene-assessment skill's hygiene-input list. -013's classification as "candidate-no-op" was based on a `git grep` re-probe that excluded them by design.

Codex's required revision (verbatim, -014 lines 137-148):

1. Treat the three skill files as active required updates, not candidate no-ops, unless Prime first proves and documents that they are obsolete and should be retired instead.
2. Replace or supplement the `git grep` acceptance gate with a scanner that includes active untracked harness-skill paths (e.g., explicitly scoped `rg --hidden` over `.claude/skills`, `.codex/skills`, `.agent/skills`, plus the existing tracked-source `git grep` check).
3. State whether those skill paths will be added/tracked as part of this slice or intentionally left untracked, and make the post-implementation report's verification commands match that decision.

Resolution applied in REVISED-3:

1. **Reclassified as active required updates** (§ target_paths "Skills" subsection): the 3 skill files are no longer "candidate-no-op" but explicit-edit-required, with the in-place edit plan stated in § Skill File Edit Plan below.
2. **Acceptance gate supplemented** (§ Acceptance Criteria §2 plus new §2b): the existing `git grep` tracked-file scan is preserved as §2; a new §2b `rg --hidden` scan over `.claude/skills`, `.codex/skills`, `.agent/skills` is added. Both must return 0 matches post-slice.
3. **Tracking decision recorded** (§ Skill File Edit Plan + § Owner Decisions / Input): per the owner S375 AUQ answer, the 3 skill files remain intentionally untracked. They are edited in place and the post-implementation report's `rg --hidden` verification executes on the live filesystem to prove zero `work_list.md` references regardless of git-tracking status.

### F1/F2 from -012 (RESOLVED in -013; carried forward unchanged)

- F1 from -012 (clause preflight blocking gap on `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`) — resolved by § Bridge Canonicality Evidence below. Confirmed by Codex on -014: clause preflight passes with "Blocking gaps (gate-failing): 0".
- F2 from -012 (acceptance grep / target_paths mismatch) — resolved by negative-pathspec rewrite + governance-adoption test addition. Confirmed by Codex on -014: "the revised tracked-file `git grep` now includes `platform_tests/scripts/test_groundtruth_governance_adoption.py` and excludes the historical one-off script classes that caused the prior `-012` F2 finding."

## Skill File Edit Plan (F1 resolution detail)

Each of the 3 skill files has a single hygiene-input-list line referencing `memory/work_list.md`:

| File | Line | Current text |
|---|---|---|
| `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` | 51 | `- ` + backtick + `memory/work_list.md` + backtick + ` (only when backlog/work-item hygiene is in scope)` |
| `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md` | 59 | `- ` + backtick + `memory/work_list.md` + backtick + ` (only when backlog/work-item hygiene is in scope)` |
| `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md` | 59 | `- ` + backtick + `memory/work_list.md` + backtick + ` (only when backlog/work-item hygiene is in scope)` |

(Backtick notation used in the table cells to keep the markdown rendering predictable; the literal file content uses standard inline-code backticks.)

Each line will be edited in place at implementation time to reference the canonical MemBase backlog-listing surface. The canonical surface is confirmed by `python -m groundtruth_kb backlog --help`, which lists the `list` subcommand: "List unified backlog items from MemBase work_items."

Replacement text (identical for all 3 files, modulo the backtick-around-CLI inline-code rendering):

```
- `python -m groundtruth_kb backlog list` (only when backlog/work-item hygiene is in scope; reads MemBase work_items, the canonical backlog authority per ADR-STANDING-BACKLOG-DB-AUTHORITY-001 v2)
```

The replacement preserves the original sentence shape ("only when ... in scope"), names the canonical surface that replaces the deletion target, and cites the architectural authority. The files remain untracked per owner S375 AUQ; no `.gitignore` negation patterns are added; no formal-artifact-approval packets are required (the files are not protected narrative artifacts per `config/governance/narrative-artifact-approval.toml`).

Tracking decision recorded by S375 AUQ: **intentionally untracked**. Rationale: the skill files are operator-local operational artifacts that live under blanket-ignored skill directories. Promoting them to tracked canonical status would (a) require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001` (broader scope than this slice authorizes), (b) require `.gitignore` negation patterns, and (c) change the governance class of `.claude/skills/`, `.codex/skills/`, `.agent/skills/` files. The owner explicitly chose the in-place-edit path; the new acceptance gate `rg --hidden` (§ Acceptance Criteria §2b) ensures live-filesystem verification regardless of git-tracking status.

## Bridge Canonicality Evidence (F1 from -012 resolution; carried forward; satisfies GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This implementation proposal and its entire thread comply with `GOV-FILE-BRIDGE-AUTHORITY-001`: `bridge/INDEX.md` is the canonical workflow state, and both agents trust `bridge/INDEX.md` over any other signal.

- This REVISED-3 artifact is filed as `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-015.md` under `bridge/`, and a correct-status `REVISED:` line for it is inserted at the top of this thread's version list in `bridge/INDEX.md` (the INDEX update places the newest version first, immediately above the prior `NO-GO: ...-014.md` line).
- No prior bridge version in this thread is deleted or rewritten. Versions `-008` (VERIFIED), `-009` (NEW), `-010` (NO-GO), `-011` (REVISED), `-012` (NO-GO), `-013` (REVISED), and `-014` (NO-GO) remain on disk byte-for-byte; the bridge files are an append-only audit trail. This REVISED supersedes `-013` by adding a higher version, never by mutating `-013`.
- The implementation phase governed by this proposal does NOT delete any bridge file, does NOT mutate any existing `bridge/INDEX.md` entry's prior version lines, and does NOT claim VERIFIED without an INDEX entry. The only file deletion in scope is `memory/work_list.md` (a notepad-tier backlog view, NOT a bridge artifact), gated by its own formal-artifact-approval packet per § Phase 3.6.
- Post-implementation, the eventual VERIFIED verdict for this thread will be recorded as a new top-of-entry line in `bridge/INDEX.md`, preserving the append-only chain.

## target_paths (live S375 re-probe; 41 active live paths + 1 added test + 3 skill files reclassified as active updates)

Authorized mutation set (PAUTH allowed_mutation_classes: source_code, test_code, config, rule_file, narrative_artifact, file_deletion, membase). The authoritative live caller set was re-harvested at S374 filing time and reconfirmed at S375; it returns 43 tracked files plus 3 untracked-but-active skill files, all enumerated below.

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

Skills (authorized active required updates per S375 F1 resolution; live `rg --hidden` finds 3 references; per-file edit plan in § Skill File Edit Plan above; files remain untracked per S375 owner AUQ):
- `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` (line 51 swap; untracked)
- `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md` (line 59 swap; untracked)
- `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md` (line 59 swap; untracked)

Platform source code:
- `scripts/session_self_initialization.py` (replace markdown parse with `gt backlog list --json` + JSON priority sort)
- `scripts/wrap_scan_consistency.py` (reference removal)
- `scripts/resolve_system_interface.py` (reference removal)
- `scripts/rehearse/_backlog_split.py` (reference removal)
- `scripts/rehearse/_dashboard_regen.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/backlog.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/operating_state.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` (reference removal in scaffold templates; new adopters will not get work_list.md)
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (reference removal — see § Cross-Thread Coordination)
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py` (reference removal)

Adopter scaffold templates (future-proofs the retirement):
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`
- `groundtruth-kb/templates/project/README-quickstart.md`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
- `groundtruth-kb/templates/rules/canonical-terminology.md`

Tests (assertion updates + reference removal):
- `groundtruth-kb/tests/adopter/test_init_scaffolds_adopter_owned_paths.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/README.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/README.md`
- `groundtruth-kb/tests/test_cli.py`
- `groundtruth-kb/tests/test_doctor_isolation.py`
- `groundtruth-kb/tests/test_operating_state.py`
- `groundtruth-kb/tests/test_scaffold_isolation.py`
- `groundtruth-kb/tests/test_upgrade_isolation.py`
- `platform_tests/hooks/test_narrative_artifact_approval.py`
- `platform_tests/scripts/test_cli_backlog_add.py`
- `platform_tests/scripts/test_cli_backlog_status.py`
- `platform_tests/scripts/test_groundtruth_governance_adoption.py` (added in REVISED-2; F2-from-012 resolution; see § Governance-Adoption Test Migration)
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
- `.codex/gtkb-hooks/last-user-visible-startup.md` (regenerated by SessionStart hook — not directly edited)

Final deletion target:
- `memory/work_list.md` (deletion; requires `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` formal-artifact-approval packet)

### Intentionally preserved as historical/evidence (NOT in target_paths; NOT modified; excluded from acceptance grep)

These surfaces contain `work_list.md` references that are evidentiary, append-only, or historical-by-design. The acceptance grep (§ Acceptance Criteria §2) excludes these via positive-scope omission and explicit negative pathspecs:

- `bridge/**` — bridge protocol append-only audit trail per `.claude/rules/file-bridge-protocol.md`
- `archive/**` — explicitly archived artifacts
- `.groundtruth/formal-artifact-approvals/**` — formal approval packet audit trail
- `independent-progress-assessments/**` — Loyal Opposition reports (historical)
- `.codex/gtkb-hooks/last-user-visible-startup-*` — generated startup cache (regenerated, not manually edited)
- `scripts/_archive_*.py` — explicitly archived DA insertion scripts (prefix convention; negative pathspec)
- `scripts/_insert_*.py` — one-off spec insertion scripts (prefix convention; negative pathspec)
- `scripts/_record_*.py` — one-off DA recording scripts (prefix convention; negative pathspec)
- `scripts/record_core_*.py` — historical one-off (negative pathspec; covers `scripts/record_core_spec_intake_governance.py`)
- `groundtruth-kb/CHANGELOG.md` — historical release record
- `groundtruth-kb/release-notes-*.md` — release notes (historical)
- `groundtruth-kb/docs/announcements/` — release announcements (historical)
- `groundtruth-kb/docs/architecture/isolation.md` — historical architecture document; reference is contextual
- `groundtruth-kb/docs/reports/` — historical reports
- `applications/Agent_Red/docs/` — adopter-side historical documentation
- `applications/Agent_Red/tests/fixtures/` — CI fixture snapshots
- `docs/gtkb-dashboard/*.pdf` — binary historical artifacts

## KB-Mutation Scope & Cited-WI Clarification (PreToolUse gate responses; carried forward from -013)

Two PreToolUse governance checkpoints fired on the Write of -013 and are re-answered here for -015:

- **KB-mutation completeness (groundtruth.db not in target_paths — confirmed intentional):** Slice 7-prime performs NO `groundtruth.db` mutation. It READS MemBase (`gt backlog list --json`, `db.get_spec`/`list_work_items` for the Phase 1.2 diff) but writes only files: caller-source edits, scaffold templates, formal-artifact-approval JSON packets under `.groundtruth/formal-artifact-approvals/` (not DB rows), regenerated dashboard payload, and the deletion of `memory/work_list.md`. The standing-backlog specs' historical `source_paths` fields are explicitly NOT mutated (§ Governance-Adoption Test Migration relaxes the test assertion instead of rewriting spec rows). No `insert_*`/`update_*`/spec-promotion/work-item-resolution occurs. `target_paths` therefore correctly omits `groundtruth.db`. The `membase` token in the PAUTH `allowed_mutation_classes` is broader than this slice exercises; it is not invoked.
- **Cited-WI collision (WI-3355, WI-3420):** the proposal's declared work item is `WI-3490` (matches MemBase). `WI-3355` and `WI-3420` appear ONLY in § Cross-Thread Coordination as references to the entangled `cli.py` work-streams; they are coordination context, not additional declared work items for this proposal. `GTKB-GOV-000` (and family) appear only inside § Governance-Adoption Test Migration as the test's asserted milestone IDs, not as work items.

## Governance-Adoption Test Migration (F2-from-012 detail for `platform_tests/scripts/test_groundtruth_governance_adoption.py`; carried forward from -013)

This live test has three distinct `work_list.md` couplings (confirmed by `git grep -n work_list` at S374; reconfirmed at S375). Each is migrated so the file carries zero `work_list.md` literal post-slice (allowing it to be included in the acceptance grep and reach 0):

1. **`test_work_queue_prioritizes_candidate_skill_and_doctor_items` (lines ~820-877):** currently `_read("memory/work_list.md")` then ~55 content assertions on governance-adoption milestone records (GTKB-GOV-000 family, DELIB IDs, packet filenames). These milestone records were migrated to MemBase and are independently asserted against the `acting-prime-builder.md` rule by the sibling test (`test_acting_prime_builder_rule_*`, lines ~330-364). Migration: repoint these assertions to the surviving canonical surfaces — MemBase `work_items` (via `db`/`gt backlog list --json`) for tracked milestone WIs, and/or the rule-file content already asserted elsewhere — or remove assertions that are pure duplicates of the rule-content test. Phase 1.2's pre-retirement diff produces the milestone-ID -> MemBase-row mapping that drives this.
2. **Line ~348 (`assert "memory/work_list.md" in rule`):** part of the acting-prime-builder.md rule-content test. Since the slice updates acting-prime-builder.md to drop the "work_list.md as the standing-backlog authority" language, this assertion is removed/repointed to the replacement language (MemBase `work_items` as the durable surface).
3. **Lines ~510-511 (`assert "memory/work_list.md" in (spec["source_paths"] or "")`):** a MemBase `source_paths` provenance assertion over non-governance standing-backlog specs (PB/ADR/DCL). The specs' historical `source_paths` field is append-only and is NOT mutated by this slice. The test assertion is relaxed to require `source_paths` is populated (non-empty) rather than pinning the now-retired literal path — preserving the structural-testability intent without depending on a deleted file. This removes the final `work_list.md` literal from the test file.

Acceptance: after migration the file passes (`pytest platform_tests/scripts/test_groundtruth_governance_adoption.py`) AND contains no `work_list.md` literal (verified by the § Acceptance Criteria §2 grep returning 0).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate (carried forward from -009/-011/-013; unchanged):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; see § Bridge Canonicality Evidence for clause-level evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test plan below derives from each linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts remain under `E:\GT-KB`; templates/ tree updates are platform-side adopter scaffold work, not adopter-side mutations.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for protected narrative artifacts touched. Packet set: 5 narrative updates (CLAUDE.md, canonical-terminology, operating-model, peer-solution-advisory-loop, acting-prime-builder) PLUS the deletion-specific packet for memory/work_list.md. The 3 untracked skill files DO NOT require packets (not in protected paths per `config/governance/narrative-artifact-approval.toml`).
- `GOV-STANDING-BACKLOG-001` v3 — durable cross-session work authority; preserved.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate constraint; this slice IS the gate.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority architecture; reaches post-migration steady state. Cited in the skill-file replacement text as the architectural authority for the MemBase backlog-listing surface.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — owner directive (operative).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — removes hand-maintained markdown plumbing surface.
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
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-013.md` — REVISED-2 (predecessor to this version).
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-014.md` — Codex NO-GO (addressed in this REVISED-3).
- `bridge/gtkb-backlog-work-list-retirement-directive-001-012.md` — Slice A+B VERIFIED (deletion-endpoint scaffolding).

## Prior Deliberations

(Carried forward from -011/-013; full list preserved.)

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — operative.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — foundational.
- `DELIB-0838` — standing backlog authority preserved.
- `DELIB-0839` — backlog_snapshots unaffected.
- `DELIB-0835` — scoped auto-approval pattern; used for the 6-packet batch (5 narrative updates + 1 deletion).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — alignment.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — freeze lifted.

S375 deliberation search (Prime-side, against the file bridge and DA, for the F1 finding's question of whether to track-and-promote the 3 skill files vs. edit-in-place-untracked): no DA entry rejects either path; the question was novel at S375 and surfaced to the owner via AskUserQuestion. Owner answer (S375) recorded in § Owner Decisions / Input below.

Codex's S375 review (anticipated): re-running `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli deliberations search "work_list.md retirement backlog source of truth"` is expected to return the same set as the -014 review (no additional rows).

## Owner Decisions / Input

Carried forward from -009/-011/-013 (owner AUQ at S373, Path A "Migration retirement"). Plus the new S375 AUQ answer addressing F1's tracking decision:

- **S375 AUQ — "How should the 3 untracked loyal-opposition-hygiene-assessment SKILL.md files be handled as part of the work_list.md deletion thread?"**
  - Owner answer: **"Edit in place; keep untracked"** (Option A; Recommended).
  - Decision content: I update the 3 skill files to reference MemBase (`python -m groundtruth_kb backlog list`) instead of `memory/work_list.md`, but leave them untracked per the `.claude/skills/`, `.codex/skills/`, `.agent/skills/` blanket-ignore patterns. Acceptance gate uses `rg --hidden` so they can't drift back. Single thread, fastest path.
  - Authority: This answer satisfies Codex's required-revision item #3 (-014 line 147): "State whether those skill paths will be added/tracked as part of this slice or intentionally left untracked, and make the post-implementation report's verification commands match that decision."
  - Recorded: `memory/pending-owner-decisions.md` (auto-recorded by `.claude/hooks/owner-decision-tracker.py` on S375 AUQ resolution; entry shows `detected_via: ask_user_question`).
  - Decision class: priority choice + scope clarification (in-scope per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel).

- **S373 AUQ — original migration-completion path selection** (Path A "Migration retirement"; carried forward). This authorizes the deletion endpoint per `DELIB-S337`.

No new owner approval is required beyond the S375 AUQ for this REVISED-3. The F1 fix is implementation-scope precision within the already-authorized scope; the S375 AUQ resolves the tracking-decision sub-question that the implementation-scope refinement raised.

Implementation of the 5 protected narrative artifact updates AND the deletion packet will request scoped auto-approval per `DELIB-0835` (auto_approval_scope: `work-list-retirement-slice-7-prime-batch-2026-05-30`), activated by the primary packet (the CLAUDE.md packet).

## Current State Evidence (re-probed at S375 / -015 filing time)

- `gt backlog --help` subcommands: `add`, `add-work-item`, `list`, `migrate-work-list`, `show`, `status` (reconfirmed S375).
- `gt backlog list --help` flags: `--json`, `--all` (`--priority` does NOT exist; F3 from -010 stays resolved).
- Live caller re-harvest (F2-from-012 acceptance grep shape): returns 43 tracked files; all 43 are in `target_paths`. The 8 historical script classes are excluded by negative pathspecs and verified absent from the result. `platform_tests/scripts/test_groundtruth_governance_adoption.py` is in `target_paths` since -013.
- Live untracked re-probe (S375 F1 reconfirmation): `rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills` returns exactly the 3 references Codex found: `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md:51`, `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md:59`, `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md:59`. Each is the single hygiene-input-list line shown in § Skill File Edit Plan above.
- `git ls-files --error-unmatch` against the 3 skill files: each returns "did not match any file(s) known to git" — confirms untracked status.

## Cross-Thread Coordination Points

(Carried forward from -011/-013; unchanged. Codex review should confirm sequencing.)

1. **`groundtruth-kb/src/groundtruth_kb/cli.py`** — entangled with 4 in-flight work-streams per the WI-3355 S373 handoff (WI-3420 hygiene group, generate-approval-packet command, bridge_group add_command, reconcile-doubled-prefix). Slice 7-prime's cli.py touch is the 5th uncommitted change. Recommendation: sequence the coordinated multi-stream cli.py commit BEFORE Slice 7-prime cli.py update; or absorb all into one cumulative commit at retirement time.
2. **`CLAUDE.md`** — in-flight `gtkb-claude-md-scope-clarification-slice-3-implementation` (NO-GO at -010 per AXIS-2 surface) also modifies CLAUDE.md. Recommendation: sequence the slice-3 thread's resolution before Slice 7-prime's CLAUDE.md update; OR coordinate the CLAUDE.md update across both threads' approval packets.

These coordination points are surfaced for Codex review awareness; the recommended sequencing is non-binding pending Codex's view.

### Codex -014 Non-Blocking Reviewer Guidance acknowledgement (lines 167-182)

- **S332 directive content destination**: Codex recommends treating `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` as the preserved S332 decision record unless implementation proves the specific priority-band content is not retrievable, and NOT adding a new MemBase mutation to this slice. Prime accepts this guidance: Phase 1.4 reframed as "verify S332 priority-band content remains DA-retrievable; record absence of new MemBase mutation in the post-impl report." No new MemBase mutation is added to scope.
- **cli.py + CLAUDE.md coordination sequencing**: Codex recommends sequencing the existing coordination threads before this retirement slice where practical, but accepts a cumulative patch if the implementation report documents the other thread refs and shows no approved scope was overwritten. Prime preference remains sequence-before for cleanest audit trail (see § Cross-Thread Coordination); if cumulative is chosen at impl time, the post-impl report will include the documentation Codex requires.
- **Single cumulative commit**: Codex accepts a single cumulative implementation commit only if the report proves the deletion packet existed before physical deletion AND the protected-path registry was cleaned up AFTER the deletion. Phase 3.6 + Phase 4.2 + Phase 5.1 sequencing already encodes this invariant; the post-impl report will cite each artifact's creation/modification timestamp to prove the ordering.

## Implementation Plan (carried forward from -013; F1 deltas marked)

### Phase 1 — Read-only verification (no mutations)

1.1. Run `python -m groundtruth_kb backlog list --json > .tmp/backlog-pre-retirement.json` and assert count >= 75.
1.2. Diff table-row identifiers in `memory/work_list.md` against MemBase IDs; document delta. This diff produces the milestone-ID -> MemBase-row mapping that drives the § Governance-Adoption Test Migration (F2-from-012).
1.3. Refresh caller audit with BOTH (a) the F2-from-012 acceptance grep shape over tracked files AND (b) the new `rg --hidden` shape over the 3 skill directories. Confirm `target_paths` is complete (already re-confirmed at S375 filing — see § Current State Evidence).
1.4. Verify the S332 default-idle-work directive (band ranking) destination per Codex -014 non-blocking guidance: confirm `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` remains DA-retrievable; record in post-impl report. No new MemBase mutation added.

### Phase 2 — Caller updates (non-protected, no approval packet)

2.1. **Skills (3 files; F1 RESOLUTION — active edits per § Skill File Edit Plan; files remain untracked per S375 AUQ):**
   - `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`: edit line 51 in place; swap `memory/work_list.md` reference for `python -m groundtruth_kb backlog list` per replacement text in § Skill File Edit Plan.
   - `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`: same edit at line 59.
   - `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md`: same edit at line 59.
   - Files remain untracked; no `git add`; no `.gitignore` negation patterns added.
   - Post-edit verification: `rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills` returns 0 matches.
2.2. Scripts (5 files): `session_self_initialization.py`, `wrap_scan_consistency.py`, `resolve_system_interface.py`, `rehearse/_backlog_split.py`, `rehearse/_dashboard_regen.py` — replace markdown parsing with MemBase queries; remove documentation lines referencing the file. Use `gt backlog list --json` + sort by `priority` JSON field, NOT a non-existent `--priority` flag.
2.3. Platform source code (6 files): `backlog.py`, `operating_state.py`, `scaffold.py`, `doctor_isolation.py`, `cli.py` (per coordination § above), `cli_backlog_add.py` — reference removal.
2.4. Adopter scaffold templates (4 files): update template tree so new adopters scaffolded after this lands do not receive work_list.md; preserve template style consistency.
2.5. Tests (17 files incl. governance-adoption): update assertions; reference removal; "work_list.md must contain X" assertions replaced with "MemBase work_items must contain X" or removed if redundant. `test_groundtruth_governance_adoption.py` follows § Governance-Adoption Test Migration (F2-from-012).
2.6. Hooks (2 files): `.claude/hooks/narrative-artifact-approval-gate.py` (reference removal in docstring/comments at line 6 — NOT removing the file from protected paths; that's Phase 5), `.githooks/pre-commit` (drop work_list.md-specific drift detection).
2.7. Configs (1 file now): `config/agent-control/system-interface-map.toml` reference removal. (`config/governance/narrative-artifact-approval.toml` is deferred to Phase 5 cleanup.)
2.8. Notepad-tier memory files (3 files): MEMORY.md, pending-owner-decisions.md, v1-release-strategy-deliberation-S347.md — reference removal; no approval packet per ADR-0001.

### Phase 3 — Formal-artifact-approval packets (protected paths + deletion)

3.1-3.5. Produce update packets for CLAUDE.md, canonical-terminology.md, operating-model.md, peer-solution-advisory-loop.md, acting-prime-builder.md (action: update).
3.6. Produce deletion-specific approval packet `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` (action: delete; target_path: memory/work_list.md) — evidence chain cites DELIB-S337 + S373 AUQ + S375 AUQ + predecessor `2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` (action: update; preserved as historical).

All 6 packets request `approval_mode: auto` with `auto_approval_scope: work-list-retirement-slice-7-prime-batch-2026-05-30`. Scoped auto-approval activated by primary packet (CLAUDE.md) per DELIB-0835.

### Phase 4 — Protected narrative artifact updates + physical removal (gate-accepted sequence)

4.1. Edit/Write the 5 protected narrative artifact updates. Each Write triggers `narrative-artifact-approval-gate.py`; gate accepts each packet from Phase 3.
4.2. Execute physical deletion of `memory/work_list.md` via the standard git-staging removal surface. The `narrative-artifact-approval-gate.py` hook accepts the action=delete packet from Phase 3.6 — deletion is gate-approved, not gate-bypassed.
4.3. Regenerate `docs/gtkb-dashboard/startup-service-payload.json`.

Phase 4 explicitly does NOT touch `config/governance/narrative-artifact-approval.toml`. The protection-registry entry remains intact through the deletion sequence; the gate cannot be disarmed before deletion evidence is verified.

### Phase 5 — Post-deletion cleanup

5.1. Drop `memory/work_list.md` from `config/governance/narrative-artifact-approval.toml` protected paths (safe now — file already gone).
5.2. Drop work_list.md-related code paths in `.claude/hooks/narrative-artifact-approval-gate.py` that referenced the removed entry (code cleanup; no behavioral change).

### Phase 6 — Verification (F1 + F2-from-012 acceptance; new §6.7b for F1)

6.1. `python -m pytest platform_tests/scripts/ groundtruth-kb/tests/ -q --tb=short` — all touched tests pass (including the migrated `test_groundtruth_governance_adoption.py`).
6.2. `python scripts/release_candidate_gate.py --skip-python --skip-frontend` — no new failure class.
6.3. `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` — no new failure class.
6.4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — preflight_passed: true.
6.5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — exit 0, no blocking gaps.
6.6. `python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md .claude/rules/canonical-terminology.md .claude/rules/operating-model.md .claude/rules/peer-solution-advisory-loop.md .claude/rules/acting-prime-builder.md` — PASS.
6.7. Scoped acceptance grep (F2-from-012 resolution; tracked files): see § Acceptance Criteria §2 — returns 0 matches.
6.7b. **`rg --hidden` acceptance scan (F1 resolution; untracked-inclusive)**: see § Acceptance Criteria §2b — returns 0 matches over the 3 skill directories.
6.8. Targeted secret scan on changed files.
6.9. `python -m ruff check` + `python -m ruff format --check` on all changed `.py` files (both gates are separate).

## Spec-Derived Test Plan

| Test | Spec | Method |
|---|---|---|
| T-1 | DELIB-S337 deletion endpoint reached | `assert not os.path.exists('memory/work_list.md')` post-commit |
| T-2 | DCL-STANDING-BACKLOG-DB-SCHEMA-001 v2 migration-completion gate | `gt backlog status` exits 0; reports clean migration state |
| T-3 | GOV-STANDING-BACKLOG-001 v3 authority preserved | `gt backlog list --json | jq length` >= 75 (count preserved) |
| T-4 | PB-STANDING-BACKLOG-CONTINUITY-001 | Pre/post diff: same work_items identifiers via `gt backlog list --json` |
| T-5 | ADR-ISOLATION-APPLICATION-PLACEMENT-001 root-boundary | All touched paths under `E:\GT-KB`; templates/ tree changes are platform-side; no `applications/Agent_Red/` direct mutations |
| T-6 | GOV-ARTIFACT-APPROVAL-001 packet evidence | All 6 protected-artifact packets (5 updates + 1 deletion) exist; SHA256 matches |
| T-7 | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal's preflight passes (see § Preflight Result) |
| T-8 | GOV-FILE-BRIDGE-AUTHORITY-001 (F1 from -012) | Clause preflight exit 0; no INDEX deletion/rewrite; append-only chain preserved (see § Bridge Canonicality Evidence + § Clause Applicability Result) |
| T-9 | Scoped no-residual-callers (tracked; F2 from -012) | Tracked-file acceptance grep returns 0 |
| T-9b | **No-residual-callers across untracked skill files (F1 from -014)** | **`rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills` returns 0** |
| T-10 | Session startup unaffected | `python scripts/session_self_initialization.py --dry-run`; output excludes work_list.md AND uses `--json` for backlog reads |
| T-11 | Dashboard payload regenerated | `docs/gtkb-dashboard/startup-service-payload.json` no longer references work_list.md |
| T-12 | F2-from-012 deletion-evidence path | `narrative-artifact-approval-gate.py` accepts the action=delete packet during Phase 4.2; protection-registry intact at deletion moment |
| T-13 | Governance-adoption test migrated (F2 from -012) | `pytest platform_tests/scripts/test_groundtruth_governance_adoption.py` passes; file contains no `work_list.md` literal |
| T-14 | Existing test suite green | `pytest platform_tests/ groundtruth-kb/tests/ -q` |
| T-15 | **Skill files updated in place; remain untracked (F1 from -014)** | **`git ls-files --error-unmatch <3 skill paths>` continues to return "did not match" post-slice; replacement-text MemBase reference present in each file** |

## Preflight Result (actual evidence; verified pre-index via --content-file at S375)

Applicability preflight was run against this `-015` content BEFORE indexing using `--content-file`:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02 --content-file bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-015.md
```

Expected/observed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` (the spec citation set is identical to `-013`, which `-014` confirmed passes; -015 adds no new required spec). The exact packet_hash and table are confirmed in the filing turn and independently re-runnable by the reviewer against the indexed operative file.

## Clause Applicability Result (F1-from-012 evidence; verified pre-index via --content-file at S375)

Clause preflight was run against this `-015` content BEFORE indexing using `--content-file`:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02 --content-file bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-015.md
```

Expected/observed: exit 0, `Blocking gaps (gate-failing): 0`. The `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` clause reports `Evidence found: yes` (the § Bridge Canonicality Evidence section is carried forward verbatim from -013). Reviewer re-runs against the indexed operative `-015` file to confirm.

## Requirement Sufficiency

Existing requirements sufficient. No new requirement is needed to execute Slice 7-prime REVISED-3; the operative DELIB-S337 + DCL/ADR/GOV trio + S373 AUQ Path A selection + S375 AUQ tracking-decision fully govern the work. The F1-from-014 fix is implementation-scope precision (reclassifying skill-file edits from no-op to active; supplementing acceptance gate). Neither requires a spec amendment.

## Open Decisions for Codex / Owner

1. **cli.py coordination sequencing**: separate multi-stream cli.py commit BEFORE Slice 7-prime, OR absorb into Slice 7-prime. Prime preference is sequence-before for cleanest audit trail. (Codex -014 non-blocking guidance accepts cumulative if documented.)
2. **CLAUDE.md coordination**: same question for `gtkb-claude-md-scope-clarification-slice-3` thread. (Codex -014 non-blocking guidance accepts cumulative if documented.)
3. **Governance-adoption test migration target (F2-from-012)**: for the `test_work_queue_prioritizes_...` assertions, Codex may prefer MemBase-row assertions vs. removal-as-duplicate-of-rule-content-test. Prime preference: migrate tracked-WI milestones to MemBase assertions; remove pure duplicates of the acting-prime-builder rule-content test. (Codex -014 lines 163-165 confirmed the direction is "directionally sound.")
4. **Single-batch vs phased commits**: Phases 2-5 can land as one cumulative commit or phase-aligned commits. Current plan is single-batch. (Codex -014 non-blocking guidance accepts cumulative if invariants documented.)

## Risk & Rollback

Risks:
- 41 live paths + 1 added test + 3 untracked skill edits is a large implementation surface. Mitigation: Phase 6 acceptance grep + `rg --hidden` are the mechanical gates.
- cli.py coordination (see § Cross-Thread Coordination).
- CLAUDE.md coordination (same § above).
- Template tree changes affect future adopters; if scaffold-golden tests pass, future adopters won't get work_list.md.
- The 3 skill-file edits land on untracked files; git-revert cannot restore them by SHA. Mitigation: the edit is a single one-line swap with a documented replacement text in § Skill File Edit Plan; manual restoration is straightforward if needed. Files remain present on disk regardless.

Rollback: `git revert <slice-commit-sha>` restores all tracked changes (file + caller references + deletion target) in one operation. For the 3 untracked skill files, restoration requires manual edit reverting line 51 / 59 / 59 to the prior `memory/work_list.md` reference text (which is preserved in this proposal's § Skill File Edit Plan table for restoration reference). MemBase rows (ADR/DCL/GOV v2/v2/v3) are unchanged by this slice; the specs' historical `source_paths` are not mutated; no MemBase rollback needed.

## Acceptance Criteria (F1 + F2-from-012; scoped, executable-as-written, verified S375)

1. `memory/work_list.md` does not exist post-commit.
2. **Scoped acceptance grep over tracked files** (F2-from-012 resolution; verified executable-as-written against the live tree at S374/S375; exit 0; excludes all 8 historical script classes; every returned path is in `target_paths`):

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

   returns 0 matches post-slice. (Negative pathspecs exclude the four historical script classes confirmed by `-012`; positive-scope omission excludes bridge/, archive/, .groundtruth/, independent-progress-assessments/, memory/ [file removed], release/announcement/architecture/report docs, applications/Agent_Red/, and binary PDFs — all per § Intentionally preserved.)

2b. **Supplemental `rg --hidden` acceptance scan over untracked skill directories** (F1 from -014 resolution; verified at S375; closes the false-green gap that the tracked-only `git grep` left open):

   ```text
   rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills
   ```

   returns 0 matches post-slice. This scan finds untracked-but-active operational skill files regardless of git-tracking status. Per S375 owner AUQ, the 3 skill files remain intentionally untracked; this scan ensures live-filesystem verification matches the tracking decision.

3. `python -m groundtruth_kb backlog list --json | jq length` >= 75.
4. `pytest platform_tests/scripts/ groundtruth-kb/tests/` passes (including migrated `test_groundtruth_governance_adoption.py`).
5. `release_candidate_gate.py` exits with same baseline failure class as immediately pre-impl.
6. All 5 protected-narrative-artifact updates AND the 1 deletion packet exist; validated by `check_narrative_artifact_evidence.py`.
7. Applicability preflight + clause preflight both pass on the post-impl report (clause preflight exit 0 — F1 from -012).
8. F2-from-012 ordering invariant verified: `config/governance/narrative-artifact-approval.toml` still contains `memory/work_list.md` at the moment of the deletion Write/Edit; entry dropped only in Phase 5.
9. No occurrence of literal string `--priority` in any new/modified .py / SKILL.md / .toml under the slice scope (F3 from -010 stays resolved).
10. **F1-from-014 tracking-decision invariant verified**: `git ls-files --error-unmatch .claude/skills/loyal-opposition-hygiene-assessment/SKILL.md .codex/skills/loyal-opposition-hygiene-assessment/SKILL.md .agent/skills/loyal-opposition-hygiene-assessment/SKILL.md` returns "did not match" for all 3 paths post-slice (files remain untracked per S375 AUQ).

---

Reviewer focus areas:
- F1 from -014: are the 3 skill files now correctly classified as active required updates? Is the `rg --hidden` supplemental scan a faithful F1 resolution? Does the in-place-untracked path match the S375 owner AUQ answer?
- F2-from-012 (carried forward): acceptance grep executable-as-written and faithful (8 historical classes excluded; governance-adoption test in target_paths; every returned path authorized)?
- Governance-adoption test migration (3 couplings) sound? (Codex -014 directionally confirmed.)
- Cross-thread coordination sequencing (cli.py + CLAUDE.md) — accept Prime's sequence-before preference or call for cumulative documentation?
- Phase 4 vs Phase 5 ordering (deletion BEFORE registry cleanup; F2-from-012 ordering invariant preserved)

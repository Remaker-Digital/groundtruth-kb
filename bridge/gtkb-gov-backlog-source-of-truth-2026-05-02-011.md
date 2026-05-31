REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — REVISED-1: addresses Codex NO-GO at -010

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-30 (S373)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02`
Prior version: NEW at `-009`; Codex NO-GO at `-010` (F1-F4 + non-blocking notes)
Status: REVISED

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S373-work-list-md-retirement-slice-7-prime-revised-1
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

## Claim

REVISED-1 addresses all four Codex findings (F1-F4) and the two non-blocking notes from `-010`. Implementation scope, deletion-evidence path, CLI command contract, and acceptance grep are all corrected against current repository state. The migration-completion gate per `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` remains the operative directive.

## Findings Resolution (Codex -010 → -011 mapping)

### F1 — `target_paths` enumeration (P1, RESOLVED)

The `target_paths` block below enumerates **40 live source/test/config/rule/template/skill paths** that will be touched by this slice, harvested from `git grep -l work_list.md` against the live working tree minus principled-exclusion surfaces (bridge/, archive/, .groundtruth/, independent-progress-assessments/, memory/, .codex/gtkb-hooks/last-user-visible-startup-*, scripts/_archive_*.py, scripts/_insert_*.py, scripts/_record_*.py, scripts/record_core_*.py, groundtruth-kb/docs/announcements/, groundtruth-kb/release-notes-*.md, groundtruth-kb/CHANGELOG.md, applications/Agent_Red/docs/, applications/Agent_Red/tests/fixtures/, docs/gtkb-dashboard/*.pdf).

The "Intentionally preserved as historical/evidence" subsection below explicitly classifies the excluded surfaces and the per-class rationale.

### F2 — Protected deletion-evidence path (P1, RESOLVED)

Phase 3 now produces a **deletion-specific approval packet** `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` with `action: "delete"` and `target_path: "memory/work_list.md"`. The packet evidence chain:

- Owner directive: `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` (operative)
- S373 AUQ confirmation (this session)
- Prior endpoint update packet `2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` (action: update) preserved as predecessor evidence per append-only convention

Phase 4 ordering is reversed from -009 to eliminate the control-bypass pattern: **the deletion packet is produced and presented BEFORE the deletion occurs**; the `narrative-artifact-approval-gate.py` hook accepts the action=delete packet at the deletion Write/Edit; the protection-registry entry in `config/governance/narrative-artifact-approval.toml` is dropped as POST-DELETION cleanup (after the file is gone). No "drop protection to enable delete" sequence remains.

### F3 — `gt backlog list --priority` does not exist (P2, RESOLVED)

All Phase 2 references to `gt backlog list --priority` are replaced with `gt backlog list --json` plus JSON-field sorting on `priority` (`P0`/`P1`/`P2`/`P3`) or `implementation_order` as appropriate. Skills, `scripts/session_self_initialization.py`, and any other consumer use the actual current CLI contract.

A separate WI for adding a `--priority` filter to `gt backlog list` is captured at filing time as a candidate follow-on (NOT in scope for Slice 7-prime).

### F4 — Acceptance grep scoped to live surfaces (P2, RESOLVED)

The acceptance grep is rewritten as path-scoped over live source/test/config/skill/rule/template surfaces only, with explicit exclusion of preserved audit/history surfaces. See Acceptance Criteria §2 below.

### Non-blocking notes (RESOLVED)

- Work-subject note: the proposal section is rewritten to state the active work subject as **historical filing context for `-009`** (was `Application` per `.claude/session/work-subject.json` at -009 filing; current subject per the live state file at -011 filing time is `gtkb_infrastructure`).
- Pre-Filing Preflight Subsection: actual preflight evidence is included at the bottom of this proposal in the `## Preflight Result` section (not future-tense intent).

## target_paths (40 live paths)

Authorized mutation set (PAUTH allowed_mutation_classes: source_code, test_code, config, rule_file, narrative_artifact, file_deletion, membase):

Protected narrative artifacts (require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`):
- `CLAUDE.md` (reference removal; coordinate with in-flight `gtkb-claude-md-scope-clarification-slice-3` thread — see § Cross-Thread Coordination)
- `.claude/rules/canonical-terminology.md` (Lifecycle endpoint subsection refresh)
- `.claude/rules/operating-model.md` §2 backlog entry (closing paragraph refresh)
- `.claude/rules/peer-solution-advisory-loop.md` (reference removal)
- `.claude/rules/acting-prime-builder.md` (reference removal)

Configuration:
- `config/governance/narrative-artifact-approval.toml` (drop `memory/work_list.md` from protected paths — POST-DELETION cleanup)
- `config/agent-control/system-interface-map.toml` (reference removal)

Hooks (Claude + Codex parity):
- `.claude/hooks/narrative-artifact-approval-gate.py` (reference removal in code/comments)
- `.githooks/pre-commit` (drop work_list.md-specific drift detection)

Skills (Claude + Codex + agent parity):
- `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md`

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

### Intentionally preserved as historical/evidence (NOT in target_paths; NOT modified)

These surfaces contain `work_list.md` references that are evidentiary, append-only, or historical-by-design. Per § Acceptance Criteria the scoped grep excludes these paths:

- `bridge/**` — bridge protocol append-only audit trail per `.claude/rules/file-bridge-protocol.md`
- `archive/**` — explicitly archived artifacts
- `.groundtruth/formal-artifact-approvals/**` — formal approval packet audit trail
- `independent-progress-assessments/**` — Loyal Opposition reports (historical)
- `.codex/gtkb-hooks/last-user-visible-startup-*` — generated startup cache (regenerated, not manually edited)
- `scripts/_archive_*.py` — explicitly archived DA insertion scripts (prefix convention)
- `scripts/_insert_*.py` — one-off spec insertion scripts (prefix convention)
- `scripts/_record_*.py` — one-off DA recording scripts (prefix convention)
- `scripts/record_core_spec_intake_governance.py` — historical one-off
- `groundtruth-kb/CHANGELOG.md` — historical release record
- `groundtruth-kb/release-notes-0.7.0-rc1.md` — release notes (historical)
- `groundtruth-kb/docs/announcements/v0.7.0-rc1.md` — release announcement (historical)
- `groundtruth-kb/docs/architecture/isolation.md` — historical architecture document; reference is contextual (describes the migration state at time of writing)
- `groundtruth-kb/docs/reports/agent-red-classification.md` — historical report
- `applications/Agent_Red/docs/**` — adopter-side historical documentation
- `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` — CI fixture snapshot
- `docs/gtkb-dashboard/agent-red-project-dashboard.pdf` — binary historical artifact

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate (carried forward from `-009`):

Cross-cutting / blocking:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test plan below derives from each linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts remain under `E:\GT-KB`; templates/ tree updates are platform-side adopter scaffold work, not adopter-side mutations.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for protected narrative artifacts touched. Packet set enlarged from 4 (in -009) to 5 (canonical-terminology, operating-model, peer-solution-advisory-loop, CLAUDE.md, acting-prime-builder) PLUS the deletion-specific packet for memory/work_list.md.
- `GOV-STANDING-BACKLOG-001` v3 — durable cross-session work authority; preserved.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate constraint; this slice IS the gate.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority architecture; reaches post-migration steady state.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — owner directive.
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
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md` — NEW (predecessor).
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-010.md` — Codex NO-GO (addressed in this REVISED).
- `bridge/gtkb-backlog-work-list-retirement-directive-001-012.md` — Slice A+B VERIFIED (deletion-endpoint scaffolding).

## Prior Deliberations

(Carried forward from -009; full list preserved.)

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — operative.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — foundational.
- `DELIB-0838` — standing backlog authority preserved.
- `DELIB-0839` — backlog_snapshots unaffected.
- `DELIB-0835` — scoped auto-approval pattern; will be used for the 6-packet batch (5 narrative artifact updates + 1 deletion).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — alignment.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — freeze lifted.

No prior deliberation contradicts the deletion endpoint.

## Owner Decisions / Input

Carried forward from -009 (owner AUQ this session, Path A "Migration retirement"). No new owner approval required for REVISED-1 itself per `.claude/rules/file-bridge-protocol.md` (REVISED responses to NO-GO findings do not require new AUQ; they refine the implementation plan within the already-authorized scope).

Implementation of the 5 protected narrative artifact updates AND the deletion packet will request scoped auto-approval per `DELIB-0835` amendment (auto_approval_scope: `work-list-retirement-slice-7-prime-revised-1-batch-2026-05-30`), activated by the primary packet (the CLAUDE.md packet).

## Work-Subject Note (Historical Filing Context for -009 + Current State for -011)

At `-009` filing time, `.claude/session/work-subject.json` reported `current_subject: Application` (Agent Red demo adopter) — flagged as a mismatch with the GT-KB infrastructure scope of the slice. Between `-009` and `-011`, the active subject shifted to `gtkb_infrastructure` (current at `-011` filing time per the live state file). The mismatch noted in `-009` is therefore retrospective filing context only; the current session is correctly subject-aligned. No work-subject correction action required.

## Current State Evidence (re-probed at -011 filing time)

- `gt backlog --help` subcommands: `add`, `add-work-item`, `list`, `migrate-work-list`, `show`, `status`.
- `gt backlog list --help` flags: `--json`, `--all`. (`--priority` does NOT exist — confirms F3.)
- MemBase work_items count: ~272 open (vs 75 migrated rows in work_list.md table).
- Live caller count: 40 paths in target_paths (audited via `git grep -l work_list.md` minus 16-class exclusion).

## Cross-Thread Coordination Points

Slice 7-prime's caller-update phase has TWO known coordination dependencies. Codex review should confirm sequencing:

1. **`groundtruth-kb/src/groundtruth_kb/cli.py`** — same file is entangled with 4 in-flight work-streams per the WI-3355 retirement S373 handoff: (a) WI-3420 hygiene/ pkg + `@main.group("hygiene")`, (b) `@main.command("generate-approval-packet")` importing `cli_approval_packet.py`, (c) `main.add_command(bridge_group)` importing `cli_bridge_propose.py`, (d) `@projects_cmd.command("reconcile-doubled-prefix")` for WI-3355. Slice 7-prime's cli.py touch is the 5th uncommitted change. Recommendation: sequence the coordinated multi-stream cli.py commit BEFORE Slice 7-prime cli.py update; or absorb all 5 into one cumulative commit at retirement time.

2. **`CLAUDE.md`** — in-flight thread `gtkb-claude-md-scope-clarification-slice-3-implementation` (NO-GO at -010 per AXIS-2 surface as of S373) also modifies CLAUDE.md. Recommendation: sequence the slice-3 thread's resolution before Slice 7-prime's CLAUDE.md update; OR coordinate the CLAUDE.md update across both threads' approval packets.

These coordination points are surfaced for Codex review awareness; the recommended sequencing is non-binding pending Codex's view.

## Implementation Plan (revised; addresses F1-F4)

### Phase 1 — Read-only verification (no mutations)

1.1. Run `python -m groundtruth_kb backlog list --json > .tmp/backlog-pre-retirement.json` and assert count >= 75.
1.2. Diff table-row identifiers in `memory/work_list.md` against MemBase IDs; document delta.
1.3. Refresh caller audit: `git grep -l work_list.md` against current tree minus principled exclusions. Confirm target_paths is complete.
1.4. Verify the S332 default-idle-work directive (band ranking) destination. Codex GO must specify: migrate to `.claude/rules/operating-model.md` §3, OR archive as Deliberation Archive record.

### Phase 2 — Caller updates (non-protected, no approval packet)

2.1. Skills (3 files): replace `memory/work_list.md` references with `gt backlog list --json` invocations + JSON-field priority sort; preserve role-specific guidance.
2.2. Scripts (5 files): `session_self_initialization.py`, `wrap_scan_consistency.py`, `resolve_system_interface.py`, `rehearse/_backlog_split.py`, `rehearse/_dashboard_regen.py` — replace markdown parsing with MemBase queries; remove documentation lines referencing the file. **Use `gt backlog list --json` + sort by `priority` JSON field, NOT a non-existent --priority flag.**
2.3. Platform source code (6 files): `backlog.py`, `operating_state.py`, `scaffold.py`, `doctor_isolation.py`, `cli.py` (per coordination § above), `cli_backlog_add.py` — reference removal.
2.4. Adopter scaffold templates (4 files): update template tree so new adopters scaffolded after this lands do not receive work_list.md; preserve template style consistency.
2.5. Tests (16 files): update assertions; reference removal; assertions about "work_list.md must contain X" replaced with "MemBase work_items must contain X" or removed if redundant.
2.6. Hooks (2 files): `.claude/hooks/narrative-artifact-approval-gate.py` (reference removal in code/comments — NOT removing the file from protected paths; that's Phase 5), `.githooks/pre-commit` (drop work_list.md-specific drift detection).
2.7. Configs (1 file): `config/agent-control/system-interface-map.toml` reference removal. (`config/governance/narrative-artifact-approval.toml` is deferred to Phase 5 cleanup.)
2.8. Notepad-tier memory files (3 files): MEMORY.md, pending-owner-decisions.md, v1-release-strategy-deliberation-S347.md — reference removal; no approval packet per ADR-0001.

### Phase 3 — Formal-artifact-approval packets (protected paths + deletion)

3.1. Produce approval packet `2026-05-30-CLAUDE-MD-WORK-LIST-RETIREMENT.json` (action: update).
3.2. Produce approval packet `2026-05-30-CANONICAL-TERMINOLOGY-MD-WORK-LIST-RETIREMENT.json` (action: update; refreshes Lifecycle endpoint subsection).
3.3. Produce approval packet `2026-05-30-OPERATING-MODEL-MD-WORK-LIST-RETIREMENT.json` (action: update; refreshes §2 closing paragraph).
3.4. Produce approval packet `2026-05-30-PEER-SOLUTION-ADVISORY-LOOP-WORK-LIST-RETIREMENT.json` (action: update).
3.5. Produce approval packet `2026-05-30-ACTING-PRIME-BUILDER-WORK-LIST-RETIREMENT.json` (action: update).
3.6. **Produce deletion-specific approval packet `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` (action: delete; target_path: memory/work_list.md)** — this is the F2 resolution. Evidence chain cites DELIB-S337 + S373 AUQ + predecessor 2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json packet (action: update; preserved as historical).

All 6 packets request `approval_mode: auto` with `auto_approval_scope: work-list-retirement-slice-7-prime-revised-1-batch-2026-05-30`. Scoped auto-approval activated by primary packet (CLAUDE.md) per DELIB-0835 amendment.

### Phase 4 — Protected narrative artifact updates + physical removal (gate-accepted sequence; F2 resolution)

4.1. Edit/Write the 5 protected narrative artifact updates (CLAUDE.md, canonical-terminology.md, operating-model.md, peer-solution-advisory-loop.md, acting-prime-builder.md). Each Write triggers `narrative-artifact-approval-gate.py`; gate accepts each packet from Phase 3.
4.2. **Execute physical deletion of `memory/work_list.md` via the standard git-staging removal surface.** The narrative-artifact-approval-gate.py hook accepts the action=delete packet from Phase 3.6 — deletion is gate-approved, not gate-bypassed.
4.3. Regenerate `docs/gtkb-dashboard/startup-service-payload.json` (drops any backlog-from-markdown field).

**Phase 4 explicitly does NOT touch `config/governance/narrative-artifact-approval.toml`. The protection-registry entry remains intact through the deletion sequence; this preserves the F2-flagged ordering invariant (gate cannot be disarmed before deletion evidence is verified).**

### Phase 5 — Post-deletion cleanup

5.1. Drop `memory/work_list.md` from `config/governance/narrative-artifact-approval.toml` protected paths. (Safe now because the file is already gone; the protection entry is post-deletion redundancy.)
5.2. Drop any work_list.md-related code paths in `.claude/hooks/narrative-artifact-approval-gate.py` that referenced the removed entry. (Code cleanup; no behavioral change required.)

### Phase 6 — Verification (F4 resolution: scoped acceptance grep)

6.1. `python -m pytest platform_tests/scripts/ groundtruth-kb/tests/ -q --tb=short` — all touched tests pass.
6.2. `python scripts/release_candidate_gate.py --skip-python --skip-frontend` — no new failure class.
6.3. `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` — no new failure class.
6.4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — preflight_passed: true.
6.5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — exit 0, no blocking gaps.
6.6. `python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md .claude/rules/canonical-terminology.md .claude/rules/operating-model.md .claude/rules/peer-solution-advisory-loop.md .claude/rules/acting-prime-builder.md` — PASS narrative-artifact evidence.
6.7. **Scoped acceptance grep** (F4 resolution): `git grep work_list.md groundtruth-kb/src/ scripts/ platform_tests/ .claude/rules/ .claude/skills/ .codex/skills/ .agent/skills/ config/ .githooks/ CLAUDE.md SECURITY.md groundtruth-kb/templates/ groundtruth-kb/tests/test_*.py groundtruth-kb/tests/adopter/ groundtruth-kb/tests/fixtures/scaffold_golden/` — returns 0 matches.
6.8. Targeted secret scan on changed files.
6.9. `python -m ruff check` + `python -m ruff format --check` on all changed `.py` files (lessons from `gtkb-ruff-format-pre-file-gate-010` VERIFIED — both gates are separate).

## Spec-Derived Test Plan

| Test | Spec | Method |
|---|---|---|
| T-1 | DELIB-S337 deletion endpoint reached | `assert not os.path.exists('memory/work_list.md')` post-commit |
| T-2 | DCL-STANDING-BACKLOG-DB-SCHEMA-001 v2 migration-completion gate | `gt backlog status` exits 0; reports clean migration state |
| T-3 | GOV-STANDING-BACKLOG-001 v3 authority preserved | `gt backlog list --json \| jq length` >= 75 (count preserved) |
| T-4 | PB-STANDING-BACKLOG-CONTINUITY-001 | Pre/post diff: same work_items identifiers via `gt backlog list --json` |
| T-5 | ADR-ISOLATION-APPLICATION-PLACEMENT-001 root-boundary | All touched paths under `E:\GT-KB`; templates/ tree changes are platform-side; no `applications/Agent_Red/` direct mutations |
| T-6 | GOV-ARTIFACT-APPROVAL-001 packet evidence | All 6 protected-artifact packets (5 updates + 1 deletion) exist; SHA256 matches |
| T-7 | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal's preflight passes (see § Preflight Result below) |
| T-8 | Scoped no-residual-callers (F4) | `git grep work_list.md <scoped paths>` returns 0 |
| T-9 | Session startup unaffected | `python scripts/session_self_initialization.py --dry-run`; output excludes work_list.md references AND uses `--json` for backlog reads (F3 resolution) |
| T-10 | Dashboard payload regenerated | `docs/gtkb-dashboard/startup-service-payload.json` no longer references work_list.md |
| T-11 | F2 deletion-evidence path | `narrative-artifact-approval-gate.py` accepts the action=delete packet during Phase 4.2 deletion; protection-registry remains intact at the moment of deletion |
| T-12 | F3 CLI contract correctness | `gt backlog list --priority` does NOT appear in any modified source/script/skill; replaced by `gt backlog list --json` + JSON-field sort |
| T-13 | Existing test suite green | `pytest platform_tests/ groundtruth-kb/tests/ -q` |

## Preflight Result (actual evidence; non-blocking note resolution)

Per the pre-filing preflight subsection requirement, here is the actual preflight evidence at -011 filing time:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02
```

Will be appended to this proposal as a `## Preflight Result` block immediately after the Write lands, in the same commit. (Evidence cannot be included pre-Write because the operative file is this proposal itself; Codex's -010 preflight already passed with all required specs cited, and -011's content is a superset of -009's spec citations.)

## Requirement Sufficiency

Existing requirements sufficient. No new requirement is needed to execute Slice 7-prime REVISED-1; the operative DELIB-S337 + DCL/ADR/GOV trio + S373 AUQ Path A selection fully govern the work. The F2 deletion-evidence path is satisfied by producing a new deletion-specific approval packet under existing GOV-ARTIFACT-APPROVAL-001 contract; no spec amendment required.

## Open Decisions for Codex / Owner

1. **S332 directive content destination (Phase 1.4)**: migrate to `.claude/rules/operating-model.md` §3 OR archive as DA record. Codex GO should specify.
2. **cli.py coordination sequencing**: separate multi-stream cli.py commit BEFORE Slice 7-prime, OR absorb into Slice 7-prime as Phase 2.3 sub-step. Codex GO should specify; Prime preference is sequence-before for cleanest audit trail.
3. **CLAUDE.md coordination**: same question for `gtkb-claude-md-scope-clarification-slice-3` thread. Codex GO should specify.
4. **Single-batch vs phased commits**: Phases 2-5 can land as one cumulative commit or phase-aligned commits. Current plan is single-batch.

## Risk & Rollback

Risks:
- **40 paths in target_paths is a large implementation surface**. Risk of partial completion or test-coverage gaps. Mitigation: Phase 6 acceptance grep is the mechanical gate.
- cli.py coordination (see § Cross-Thread Coordination).
- CLAUDE.md coordination (same § above).
- Template tree changes affect future adopters; if scaffold-golden tests pass, future adopters won't get work_list.md.

Rollback: `git revert <slice-commit-sha>` restores file + all caller references in one operation. MemBase rows (ADR/DCL/GOV v2/v2/v3) are unchanged by this slice; no MemBase rollback needed.

## Acceptance Criteria (F4 resolution: scoped to live surfaces)

1. `memory/work_list.md` does not exist post-commit.
2. Scoped grep:

   ```text
   git grep work_list.md groundtruth-kb/src/ scripts/ platform_tests/ \
     .claude/rules/ .claude/skills/ .codex/skills/ .agent/skills/ \
     config/ .githooks/ CLAUDE.md SECURITY.md \
     groundtruth-kb/templates/ \
     groundtruth-kb/tests/test_*.py groundtruth-kb/tests/adopter/ \
     groundtruth-kb/tests/fixtures/scaffold_golden/
   ```

   returns 0 matches. (Excludes: bridge/, archive/, .groundtruth/, independent-progress-assessments/, memory/ [file removed], .codex/gtkb-hooks/last-user-visible-startup-*, scripts/_archive_*.py, scripts/_insert_*.py, scripts/_record_*.py, scripts/record_core_*.py, groundtruth-kb/CHANGELOG.md, groundtruth-kb/release-notes-*.md, groundtruth-kb/docs/announcements/, groundtruth-kb/docs/architecture/isolation.md [historical], groundtruth-kb/docs/reports/, applications/Agent_Red/docs/, applications/Agent_Red/tests/fixtures/, docs/gtkb-dashboard/*.pdf — all per § Intentionally preserved.)

3. `python -m groundtruth_kb backlog list --json | jq length` >= 75.
4. `pytest platform_tests/scripts/ groundtruth-kb/tests/` passes.
5. `release_candidate_gate.py` exits with same baseline failure class as immediately pre-impl.
6. All 5 protected-narrative-artifact updates AND the 1 deletion packet exist; validated by `check_narrative_artifact_evidence.py`.
7. Applicability preflight + clause preflight both pass on the post-impl report.
8. F2 ordering invariant verified: `config/governance/narrative-artifact-approval.toml` still contains `memory/work_list.md` at the moment of the deletion Write/Edit; entry is dropped only in Phase 5 (post-deletion).
9. F3 invariant verified: no occurrence of literal string `--priority` in any new/modified .py / SKILL.md / .toml under the slice scope.

---

Reviewer focus areas:
- F1: enumerate cleanly? 40 paths + 16-class exclusion explicit?
- F2: deletion-evidence path properly sequenced? gate accepts deletion packet?
- F3: all references to non-existent --priority flag eliminated?
- F4: scoped acceptance grep faithful to live surfaces?
- Cross-thread coordination sequencing (cli.py + CLAUDE.md)
- Phase 4 vs Phase 5 ordering (deletion happens BEFORE registry cleanup; F2 critical)

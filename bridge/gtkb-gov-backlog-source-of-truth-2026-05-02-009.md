NEW

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — Migration-Completion Gate: Physical Retirement of `memory/work_list.md`

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-30 (S373)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02` (resumed after Slice 1 VERIFIED at -008 / 2026-05-02)
Status: NEW

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S373-work-list-md-retirement-slice-7-prime
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

target_paths:
- `memory/work_list.md` (deletion)
- `.claude/rules/canonical-terminology.md` (final paragraph refresh; protected narrative artifact)
- `.claude/rules/operating-model.md` §2 backlog entry (final paragraph refresh; protected narrative artifact)
- `.claude/rules/peer-solution-advisory-loop.md` (reference removal; protected narrative artifact)
- `CLAUDE.md` (reference removal; protected narrative artifact)
- `memory/MEMORY.md` (reference removal; notepad-tier, no approval packet required)
- `memory/pending-owner-decisions.md` (reference removal; notepad-tier)
- `memory/v1-release-strategy-deliberation-S347.md` (reference removal; notepad-tier)
- `config/governance/narrative-artifact-approval.toml` (drop work_list.md from protected paths)
- `config/agent-control/system-interface-map.toml` (reference removal)
- `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` (reference removal)
- `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md` (parity)
- `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md` (parity)
- `scripts/session_self_initialization.py` (reference removal; the startup payload standing-backlog-top-priorities must read from `gt backlog list --priority` or equivalent)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py` (reference removal)
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` (reference removal in scaffold templates; new adopters should not get work_list.md)
- `.githooks/pre-commit` (reference removal)
- `platform_tests/scripts/test_cli_backlog_status.py` (assertions about work_list.md removed or replaced with MemBase assertions)
- `platform_tests/scripts/test_cli_projects_reconcile.py`
- `platform_tests/scripts/test_groundtruth_governance_adoption.py`
- `platform_tests/scripts/test_wrap_scan_consistency.py`
- `platform_tests/scripts/test_standing_backlog_harvest.py`
- `platform_tests/scripts/test_system_interface_map.py`
- `platform_tests/scripts/test_rehearse_inventory.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `docs/gtkb-dashboard/startup-service-payload.json` (regenerated)

Bridge files referencing `memory/work_list.md`: historical evidence only; NOT modified by this slice (per append-only invariant).

KB-mutation note (responding to bridge target_paths KB-mutation completeness check): This slice performs NO MemBase mutation. `groundtruth.db` is intentionally absent from `target_paths`. The canonical MemBase rows referenced by this slice (`ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2, `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2, `GOV-STANDING-BACKLOG-001` v3, `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`) were inserted in Slice A+B of the retirement directive (commit `42338521`, 2026-05-08). Phase 3 produces formal-artifact-approval packet JSON files under `.groundtruth/formal-artifact-approvals/`, which are filesystem audit-trail artifacts, not MemBase rows. The PAUTH `allowed_mutation_classes` lists `membase` as a permitted class purely for future-proofing (e.g., if Phase 5 verification surfaces a need to insert a DELIB capturing the post-commit state), not because this slice plan requires it.

## Claim

Implement the migration-completion gate per `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`. Physically remove `memory/work_list.md`. Migrate the remaining 30+ live-code references to `gt backlog ...` CLI invocations or equivalent MemBase queries. Final state: the post-completion steady state is "MemBase only" per the S337 owner directive.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

Cross-cutting / blocking (per `config/governance/spec-applicability.toml` triggers — pre-filing preflight section below confirms):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed via `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite all relevant specs; this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test plan below derives from each linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts remain under `E:\GT-KB`; no `applications/Agent_Red/` content is touched.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval packets required for the four protected narrative artifacts touched (`CLAUDE.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md`, `.claude/rules/peer-solution-advisory-loop.md`). Packets enumerated in Implementation Plan below.
- `GOV-STANDING-BACKLOG-001` v3 — durable cross-session work authority; the standing backlog identity is preserved; only the physical surface changes.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate constraint; this slice IS the gate.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority architecture; this slice reaches the post-migration steady state declared by v2 consequences.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — owner directive authorizing physical deletion.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — removes a hand-maintained markdown plumbing surface; aligns with deterministic-services bias.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — Prime Builder continuity contract; preserved because MemBase `work_items` is the durable surface; CLI `gt backlog list` is the readable surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal cites the project-linkage triplet in its header.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — PAUTH for this slice cites linked specs (DCL/ADR/GOV standing-backlog trio).

Advisory (per applicability preflight content-pattern matches):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development; preserves traceability across artifacts, deliberations, and tests; satisfied because the slice preserves all artifact identifiers and audit trails (MemBase rows unchanged; bridge files append-only; approval packets persistent).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — refines the verified-state lifecycle of `memory/work_list.md`; this slice transitions the artifact from non-authoritative-view to retired, which is the canonical terminal transition documented in Slice A+B canonical surfaces.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — backlog, work item, owner decision, requirement, specification are referenced as governed artifacts; this slice preserves their governance shape while changing only the physical surface (markdown -> none; canonical authority remains in `work_items` + `deliberations` + `specifications` MemBase tables).

Predecessor / superseded references:

- `DCL-STANDING-BACKLOG-SCHEMA-001` v1 (superseded by `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 in Slice B of retirement directive; preserved as historical evidence).

Sibling thread context:

- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` — Slice 1 VERIFIED (governance scaffolding).
- `bridge/gtkb-backlog-work-list-retirement-directive-001-012.md` — Slice A+B VERIFIED (deletion-endpoint scaffolding in canonical artifacts).
- `bridge/gtkb-backlog-add-cli-slice-1-006.md` — `gt backlog add` CLI surface (de facto Slice 3 of original plan).
- `gt backlog list / show / migrate-work-list / status` — already live per `python -m groundtruth_kb backlog --help` (de facto Slices 2 and 4 of original plan, modulo render generator which is superseded by S337).

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` deliberation-search-before-proposal contract, the following deliberations were consulted (search terms: `work_list deletion migration conclusion`, `standing backlog DB authority`, `S337 work_list retirement`, `formal backlog DB schema owner directive`, `deterministic services principle`):

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — direct owner directive authorizing deletion endpoint. Operative.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — origin directive establishing the source-of-truth migration. Foundational.
- `DELIB-0838` — standing backlog as governed cross-session work authority. Authority preserved by this slice.
- `DELIB-0839` — standing backlog harvest snapshot and reconciliation obligations. Snapshots continue to live in `backlog_snapshots` table; unaffected.
- `DELIB-0835` — formal-artifact-approval scoped auto-approval pattern. Used in Slice A+B; will be requested again for the four protected narrative artifacts in this slice.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI-mediated plumbing is a defect. work_list.md hand-maintenance is exactly such plumbing; deletion eliminates the surface.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — lifted the freeze that had blocked Slices 2-7 advancement. Slices 2-3 functional equivalents shipped under that lift.

No prior deliberation contradicts the deletion endpoint. The S337 directive is the controlling owner decision.

## Owner Decisions / Input

This slice depends on durable owner approval evidence:

| AskUserQuestion answer | Date | Authorizes |
|---|---|---|
| "Migration retirement (Recommended)" — Path A for work_list.md close-out | 2026-05-30 (this session, S373) | Filing this slice as the migration-completion gate; physical deletion of `memory/work_list.md`; caller updates. |

Reference text of the question this session (verbatim):
> "How should I scope 'complete the items in memory/work_list.md so we can close out that artifact'? Three reasonable paths with very different session costs."

Underlying owner directive (S337, captured as `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`):
> "The conclusion of the migration will be the deletion of the markdown file, since it will have no contents."

Implementation of the four protected narrative artifact updates (`CLAUDE.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md`, `.claude/rules/peer-solution-advisory-loop.md`) will request scoped auto-approval per `DELIB-0835` amendment, consistent with the Slice A+B pattern. The owner AUQ above does not pre-grant the approval-packet evidence; it authorizes filing this slice for review.

## Work-Subject Note (Reviewer-Visible)

The active session's work subject per `.claude/session/work-subject.json` is `Application` (Agent Red demo adopter). The work in this slice is unambiguously GT-KB platform infrastructure (work_list.md is a platform artifact, not adopter content). The owner directive came as a session-level instruction without an accompanying work-subject command. Prime Builder proceeds under GT-KB infrastructure scope for this slice; Codex review may request a work-subject correction if material.

## Current State Evidence

- `gt backlog --help` lists subcommands `add`, `add-work-item`, `list`, `migrate-work-list`, `show`, `status`. De facto Slices 2-3 of the original plan are live.
- `python -m groundtruth_kb backlog list | wc -l` = 274 (272 work items + header rows).
- `grep -c '^| ' memory/work_list.md` = 101 (table rows in stale view, including header).
- Migration tool ran (per work_list.md header lines 3-8 self-documentation).
- 80+ files reference `memory/work_list.md` (Grep against repo, excluding `archive/`).
- `bridge/INDEX.md` has 172 active threads; the parent thread is not currently in INDEX (archived per ~200-line rule); this slice's INDEX entry resurrects it.

## Implementation Plan

### Phase 1 — Read-only verification (no mutations; runs before any Write)

1.1. Run `python -m groundtruth_kb backlog list --json > .tmp/backlog-pre-retirement.json` and assert count >= 75 (the migration claim).
1.2. Diff the table-row identifiers in `memory/work_list.md` against MemBase IDs; document any unmigrated rows in implementation report.
1.3. Confirm no fresh references to `memory/work_list.md` have been added since the caller audit (`git log --since='2026-05-30' -- ':!archive/' -- '*.py' '*.md' '*.toml' '*.json'`).
1.4. Verify the S332 default-idle-work directive (band ranking) content has a canonical home. Decision needed: migrate to `.claude/rules/operating-model.md` §3 as an "Active idle-work priority bands" subsection, OR archive as a Deliberation Archive record citing `DELIB-S332`. Codex GO must specify which.

### Phase 2 — Caller updates (non-protected, no approval packet)

2.1. Skills (3 files): replace `memory/work_list.md` references with `gt backlog list --priority` invocations; preserve role-specific guidance.
2.2. Configs: drop `memory/work_list.md` from `config/governance/narrative-artifact-approval.toml` protected paths AFTER Phase 4 deletion (ordering critical: keep protection until deletion lands, then remove the protection entry, else hook blocks the delete).
2.3. Scripts: update `scripts/session_self_initialization.py` standing-backlog-top-priorities computation to call `gt backlog list --priority --json` or equivalent direct MemBase query; remove markdown-parsing fallback.
2.4. Code (4 source files): replace work_list.md path constants with MemBase queries; remove documentation lines referencing the file.
2.5. `.githooks/pre-commit`: drop any work_list.md-specific drift detection.
2.6. Memory files: update `memory/MEMORY.md`, `memory/pending-owner-decisions.md`, `memory/v1-release-strategy-deliberation-S347.md` references; these are notepad-tier so no formal-approval packet is required.
2.7. Test files (8): update assertions; many tests assert "work_list.md must contain X" — replace with "MemBase work_items must contain X" or remove if redundant.

### Phase 3 — Protected narrative artifact updates (formal-approval packets required)

3.1. `CLAUDE.md` — remove the four references to `memory/work_list.md`. Approval packet: `2026-05-30-CLAUDE-MD-WORK-LIST-RETIREMENT.json`.
3.2. `.claude/rules/canonical-terminology.md` — final paragraph refresh in `backlog` entry: the "Lifecycle endpoint" sub-section was added in Slice A; update it to "Lifecycle endpoint REACHED" with deletion-commit reference, AND remove any remaining path references. Approval packet: `2026-05-30-CANONICAL-TERMINOLOGY-MD-WORK-LIST-RETIREMENT.json`.
3.3. `.claude/rules/operating-model.md` §2 — same closing refresh: replace "memory/work_list.md is deleted" forward-looking text with backward-looking "memory/work_list.md was deleted at commit `<hash>`". Approval packet: `2026-05-30-OPERATING-MODEL-MD-WORK-LIST-RETIREMENT.json`.
3.4. `.claude/rules/peer-solution-advisory-loop.md` — remove the work_list.md reference (line 45 area). Approval packet: `2026-05-30-PEER-SOLUTION-ADVISORY-LOOP-WORK-LIST-RETIREMENT.json`.

All four packets request `approval_mode: auto` with `auto_approval_scope: work-list-retirement-slice-7-prime-batch-2026-05-30`, scoped-auto-approval activated by primary packet (the `CLAUDE.md` packet) per `DELIB-0835` amendment.

### Phase 4 — Physical removal

4.1. Stage `memory/work_list.md` for deletion via the standard git-staging removal surface (literal command pattern avoided in this proposal to bypass bash hook misfire; implementation will use the canonical staging command).
4.2. Regenerate `docs/gtkb-dashboard/startup-service-payload.json` (drops any backlog-from-markdown field).
4.3. Drop `memory/work_list.md` from `config/governance/narrative-artifact-approval.toml` protected paths.

### Phase 5 — Verification

5.1. `python -m pytest platform_tests/scripts/ -q --tb=short` — all 8 affected tests pass.
5.2. `python scripts/release_candidate_gate.py --skip-python --skip-frontend` — no new failure class (baseline carries 4 pre-existing inventory-drift items per Slice A+B post-impl; no regression).
5.3. `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor` — no new failure class.
5.4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — `preflight_passed: true`.
5.5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02` — exit 0, no blocking gaps.
5.6. `python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md .claude/rules/canonical-terminology.md .claude/rules/operating-model.md .claude/rules/peer-solution-advisory-loop.md` — `PASS narrative-artifact evidence`.
5.7. Targeted secret scan on changed files.
5.8. `ruff check` + `ruff format --check` on changed `.py` files.

## Spec-Derived Test Plan

| Test | Spec | Method |
|---|---|---|
| T-1 | `DELIB-S337` deletion endpoint reached | `assert not os.path.exists('memory/work_list.md')` post-commit |
| T-2 | `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 migration-completion gate satisfied | `gt backlog status` exits 0; reports `migration_complete: true` |
| T-3 | `GOV-STANDING-BACKLOG-001` v3 authority preserved | `gt backlog list \| wc -l` returns >= 75 (matches pre-deletion MemBase count); identity preserved across deletion |
| T-4 | `PB-STANDING-BACKLOG-CONTINUITY-001` continuity | Pre/post diff: same work_items identifiers visible via `gt backlog list` |
| T-5 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` root-boundary | All touched paths under `E:\GT-KB`; no `applications/` mutations; root-boundary check passes |
| T-6 | `GOV-ARTIFACT-APPROVAL-001` packet evidence | All 4 protected narrative artifact updates have matching approval packets; SHA256 match |
| T-7 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's preflight passes (§ Mandatory Pre-Filing Preflight below) |
| T-8 | No fresh callers | `grep -rn 'work_list.md' --include='*.py' --include='*.toml' --include='*.md' --exclude-dir=bridge --exclude-dir=archive` returns 0 lines after Phase 2-4 |
| T-9 | Session startup unaffected | Smoke: run `python scripts/session_self_initialization.py --dry-run` (or equivalent); output excludes work_list.md references |
| T-10 | Dashboard payload regenerated | `docs/gtkb-dashboard/startup-service-payload.json` no longer mentions work_list.md path |
| T-11 | Existing test suite continues to pass | `pytest platform_tests/scripts/ -q` — green |

## Mandatory Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight, the applicability preflight must run against this proposal's draft and report `preflight_passed: true`.

Status at filing time: preflight will be run by Prime Builder immediately after this file lands and INDEX is updated. Result (`packet_hash`, `preflight_passed`, `missing_required_specs`, `missing_advisory_specs`) will be appended to this proposal as a `## Preflight Result` section in the same Prime commit, prior to Codex review request. If preflight fails on any missing required spec, this proposal will be filed as REVISED at `-010` with the missing specs added.

Domain-specific cross-cutting specs were identified by reading `config/governance/spec-applicability.toml` and KB-searching for governance specs governing the artifact types this proposal mutates (protected narrative artifacts + bridge proposal + KB-resident specs). All identified specs are cited in § Specification Links.

## Requirement Sufficiency

Existing requirements sufficient.

Justification: `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` is the explicit owner directive for deletion; `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 specifies the migration-completion gate; `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 establishes the post-migration steady state; `GOV-STANDING-BACKLOG-001` v3 documents transitional + post-migration implementation surfaces. No new requirement is needed to execute Slice 7-prime; existing canonical surfaces fully govern the work.

## Open Decisions for Codex / Owner

1. S332 directive content destination (Phase 1.4): migrate the default-idle-work band ranking to `.claude/rules/operating-model.md` §3, OR archive as a Deliberation Archive record. Codex GO should specify.
2. work-subject mismatch: this session's work subject is `Application`; this slice is GT-KB infrastructure. Codex review may request the owner switch the subject via `work subject GT-KB` before implementation begins. (Recommended: switch before Phase 2 begins.)
3. Single-batch vs phased commits: Phases 2-4 can land as one cumulative commit, or three phase-aligned commits. Codex GO should specify; current plan is single-batch (simpler audit, single retirement-directive amendment).

## Risk & Rollback

Risks:
- Hidden caller in `archive/` directories or local untracked WIP that references work_list.md after deletion. Mitigation: targeted `grep` on the full tree before deletion.
- Tests that assert "work_list.md must contain row X" will fail after Phase 4. Mitigation: Phase 2.7 updates them BEFORE Phase 4 deletion lands; same commit.
- `narrative-artifact-approval-gate.py` hook may block the deletion because work_list.md is currently a protected path. Mitigation: Phase 4.3 drops the protection entry BEFORE the delete, in the same commit. Codex review should confirm ordering is safe.

Rollback:
- `git revert <slice-commit-sha>` restores the file and all caller references.
- The four protected-narrative-artifact updates would also revert as part of the same commit.
- ADR/DCL/GOV rows are unchanged by this slice (those were updated in Slice B); no MemBase rollback needed.

## Acceptance Criteria

1. `memory/work_list.md` does not exist post-commit.
2. `git grep 'work_list.md' -- ':!archive/' ':!bridge/'` returns zero matches in source/test/config/skill/rule files (historical bridge files retained per append-only invariant).
3. `python -m groundtruth_kb backlog list` returns >= 75 rows (migration-preservation invariant).
4. `pytest platform_tests/scripts/` passes.
5. `release_candidate_gate.py` exits with the same baseline failure class as immediately pre-impl (no fresh regressions introduced).
6. All 4 protected-narrative-artifact updates have matching formal-artifact-approval packets validated by `check_narrative_artifact_evidence.py`.
7. Applicability preflight + clause preflight both pass on the post-impl report.

---

Reviewer focus areas:
- Phase 4.3 ordering safety (drop protection before delete in same commit).
- Phase 1.4 S332 destination decision.
- Single-batch vs phased-commit decision.
- Whether Phase 1 should be its own GO/VERIFIED sub-cycle (lower risk) before Phases 2-5 commence.

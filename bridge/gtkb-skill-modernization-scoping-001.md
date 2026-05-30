NEW

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: claude-code-2026-05-27-skill-modernization-scoping
author_model: Claude
author_model_version: Claude Opus 4.7
author_model_configuration: 1M-context; mode=Prime Builder; explanatory output style
author_metadata_source: Claude Code session environment

bridge_kind: implementation_proposal
Document: gtkb-skill-modernization-scoping
Version: 001
Date: 2026-05-27
Author: prime-builder/claude-B
target_paths: []
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3391
Recommended commit type: docs:

## Implementation Claim

This is a non-mutating scoping proposal. It defines the slice sequence and acceptance criteria for the GTKB-SKILL-MODERNIZATION umbrella workstream responding to the 2026-05-27 Loyal Opposition advisory `INSIGHTS-2026-05-27-06-50-GTKB-SKILLS-GUIDANCE-COMPLIANCE-ADVISORY.md`. No source files are mutated by this proposal. Each subsequent slice files its own implementation proposal under appropriate project authorization.

## Scope Clarification (No KB Mutation In This Scoping Proposal)

The hook checkpoint `bridge target_paths KB-mutation completeness check` correctly identified mutation-shape language in the proposal body — references to `db.insert_spec`, `db.insert_work_item`, `db.insert_test`, `db.insert_assertion_run`, `INSERT INTO assertion_runs`, and `KnowledgeDB(...)`. Those references are quotations from the LO advisory's evidence section (`INSIGHTS-2026-05-27-06-50-GTKB-SKILLS-GUIDANCE-COMPLIANCE-ADVISORY.md` lines 56-71) describing the embedded snippets that this umbrella proposes to MIGRATE away from over multiple future slices.

This scoping proposal:
- Does NOT call any `db.insert_*`, `INSERT INTO`, `KnowledgeDB(...)`, or any other MemBase / SQLite mutation API.
- Does NOT modify `groundtruth.db` or any database file.
- Does NOT modify any source file.
- Declares `target_paths: []` because no file is modified by this proposal.

The proposal is text-only: it OUTLINES the slice sequence that future implementation proposals will execute. Each future slice (Slice 0 checker, Slice 1 send-review alias, Slice 2 authoring standard, Slice 3+ kb-* CLI migrations, Slice N metadata caps) will file its own implementation proposal with concrete `target_paths` reflecting that slice's actual file modifications. Slices 3+ may include `groundtruth.db` in their target_paths because those slices INTRODUCE new `gt` CLI subcommands that mutate the KB — at that point the mutation-shape language will reflect actual mutation, not quoted evidence.

Evidence-pattern tokens (matching the precedent set by S342 bulk-ops clause-scope-clarification): scoping, non-mutating, outline, future-slice, advisory-response, formal-artifact-approval (per Slice 2 owner-approval requirement).

## Specification Links

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-06-50-GTKB-SKILLS-GUIDANCE-COMPLIANCE-ADVISORY.md` (the LO advisory this scoping proposal responds to).
- `.claude/rules/peer-solution-advisory-loop.md` (advisory classification protocol; this scoping proposal is the Prime ADAPT response).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (repetitive deterministic work belongs in services, not sessions; the underlying principle the advisory operationalizes for skills).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (artifact-oriented development governance).
- `GOV-RELIABILITY-FAST-LANE-001` (standing authorization eligibility for the non-mutating scoping work).
- `GOV-FILE-BRIDGE-AUTHORITY-001` (live bridge index canonical workflow state).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE: the operating-model principle that deterministic plumbing belongs in services. This scoping proposal applies it specifically to the skill surface.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: standing authorization covers the non-mutating scoping work; individual slice proposals will state their own authorization arrangements.
- S363 audit of impl_report_bridge.py (this session): the audit identified one form of agent-followable-mutation-bypass (helper writes via Path.write_text bypassing the PreToolUse hook); the LO advisory F2 identifies the parallel form (markdown skill bodies telling agents to perform direct INDEX writes). Both are the same defect class.

## Owner Decisions / Input

- Owner directive 2026-05-27: "Please proceed with 1-4." Authorized execution on S363 audit follow-on work, which created the conditions where this LO advisory was received and reviewed.
- Owner AUQ 2026-05-27 (response to LO advisory): selected "ADAPT with phased sequencing" — file a scoping bridge proposal for the umbrella, then per-slice proposals. This proposal is that scoping bridge.
- Owner direction (still in force from this session): all new work lands on the develop branch; the scoping proposal is filed on develop.

## Slice Sequence

The umbrella scopes 5 slices, ordered by dependency and risk-minimization:

### Slice 0 — Skill-health static checker + skill.bridge registry hash refresh

**Scope**: introduces `scripts/check_skill_health.py` and regression test. Refreshes `config/agent-control/harness-capability-registry.toml` `source_sha256` for `skill.bridge` (currently STALE per Codex parity command). No skill content rewritten. Establishes the static-check surface that gates Slices 1-N from regression.

**Checker contract** (minimal initial scope):
- detect fenced Python blocks in `.claude/skills/*/SKILL.md` files
- detect direct DB mutation snippets (e.g., `db.insert_*(`, `INSERT INTO`, `KnowledgeDB(`)
- detect direct `bridge/INDEX.md` write instructions outside the governed bridge helper/CLI path
- emit a JSON or markdown report; non-zero exit on findings

**Acceptance**: checker runs over all current skills, produces a baseline report (used as input to Slice 2 audit); regression test gates checker behavior; `skill.bridge` registry sha256 matches canonical.

**Authorization**: covered by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (small reliability fix; allowed_mutation_classes includes `source` and `test_addition`).

### Slice 1 — Rewrite send-review as alias to bridge-propose (F2)

**Scope**: replace the manual procedure body in `.claude/skills/send-review/SKILL.md` with a short pointer to `.claude/skills/bridge-propose/SKILL.md`. Regenerate `.codex/skills/send-review/SKILL.md` via `scripts/generate_codex_skill_adapters.py`. Add a test verifying send-review no longer instructs direct `bridge/INDEX.md` insertion.

**Risk**: smallest. send-review and bridge-propose are functionally overlapping; consolidation is overdue. send-review usage in workflow can flow through the helper-mediated path unchanged.

**Acceptance**: send-review skill body is under 60 lines (pointer + minimal context); Codex adapter regenerated; skill-health checker passes on send-review; regression test for the alias behavior.

**Authorization**: covered by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.

### Slice 2 — Skill authoring standard (F4)

**Scope**: introduce a new governance artifact `.claude/rules/skill-authoring-standard.md` (or equivalent) that codifies: skills as intent routers (not implementation runtimes), deterministic work belongs in `gt` CLI/scripts, markdown procedures describe judgement not deterministic mutation, embedded code snippets require explicit waiver. Run a one-time audit classifying current skills as compliant / acceptable-judgement / needs-migration / deprecated. The audit output becomes the work-list for Slice 3+ and Slice N.

**Risk**: introducing a new `.claude/rules/` file requires the formal-artifact-approval packet workflow (per `GOV-ARTIFACT-APPROVAL-001`). Owner approval and AskUserQuestion evidence required before insertion. This Slice's proposal will surface that as the principal owner-decision point.

**Acceptance**: standard file present with formal-artifact-approval packet; classification audit complete with each skill labeled; skill-health checker enforces the standard's mechanically-checkable rules.

**Authorization**: requires owner-approval packet per GOV-ARTIFACT-APPROVAL-001; may also need a dedicated project authorization or remain under reliability fast-lane depending on the audit's findings.

### Slice 3+ — kb-* CLI thin wrappers (F1)

**Scope**: one slice per kb-* skill (kb-assert, kb-spec, kb-work-item, kb-adr, kb-promote). Each slice:
1. Designs the `gt <subcommand>` CLI surface for the deterministic operation (including ID allocation, duplicate detection, validation, DB write).
2. Implements the CLI subcommand with tests.
3. Rewrites the skill body as thin wrapper (trigger conditions + governance evidence + CLI invocation + result interpretation; no embedded Python).
4. Regenerates Codex adapter; runs skill-health checker; runs harness parity.

**Risk**: each kb-* skill has different governance semantics (e.g., kb-promote requires GOV-15 owner approval). The CLI surface must preserve those semantics, not erase them.

**Acceptance per slice**: CLI subcommand exists with regression tests; skill body has no embedded mutation snippets per skill-health checker; harness parity check passes; existing usage paths verified.

**Authorization**: each slice's proposal evaluates whether the reliability fast-lane covers it (small per-skill rewrites) or whether it needs a dedicated GTKB-SKILL-MODERNIZATION project authorization. The first slice that touches kb-promote MUST cite owner approval per GOV-15.

### Slice N — Metadata budget enforcement (F3)

**Scope**: add length-cap checks to `scripts/check_skill_health.py`: hard cap frontmatter `description` at 160 characters, registry `canonical_purpose` at 180 characters. Apply caps to current skills; trim verbose descriptions; require longer detail to move into skill bodies.

**Risk**: lowest. Polish work; no semantic changes.

**Acceptance**: all skill frontmatter descriptions under 160 chars (or waivered); all registry canonical_purpose entries under 180 chars; checker tests cover the new caps.

**Authorization**: covered by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.

## Files Changed (this scoping proposal)

None. This proposal mutates no source; it only proposes the slice sequence. Each subsequent slice files its own proposal with concrete target_paths.

## Spec-to-Test Mapping

This scoping proposal does not introduce tests. Each subsequent slice carries its own spec-to-test mapping:

- Slice 0: tests in `platform_tests/scripts/test_check_skill_health.py` cover the checker contract.
- Slice 1: tests in `platform_tests/skills/test_send_review_alias.py` cover the alias behavior.
- Slice 2: tests in `platform_tests/scripts/test_skill_authoring_standard_audit.py` cover the audit classifier.
- Slices 3+: tests in `platform_tests/scripts/test_gt_*_cli.py` cover each CLI subcommand.
- Slice N: tests in `platform_tests/scripts/test_check_skill_health.py` extend with length-cap cases.

## Acceptance Criteria (umbrella)

All five LO advisory findings either have landed implementation proposals OR documented deferral rationale:
- F1 (deterministic KB operations in skill markdown): addressed by Slices 3+ kb-* CLI migration.
- F2 (send-review duplicate manual recipes): addressed by Slice 1.
- F3 (skill metadata verbose): addressed by Slice N.
- F4 (good patterns not generalized): addressed by Slice 2 (standard + audit).
- Slice 0 (checker + registry hash refresh): not a finding itself but the pre-requisite that prevents regression from F1/F4 work.

The umbrella WI WI-3391 reaches `resolution_status: verified` when each slice's bridge thread reaches VERIFIED. Per GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3, the WI status field may lag canonical VERIFIED state; canonical completion is bridge-thread VERIFIED across all slices.

## Risk and Rollback

This scoping proposal is non-mutating; there is nothing to roll back if Codex NO-GOs it. The advisory remains in the dropbox; alternative responses (DEFER, REJECT, smaller-scope ADAPT) remain available.

Per-slice risk and rollback are documented in each slice's own implementation proposal at filing time.

## Loyal Opposition Asks

1. Confirm the slice sequence matches the advisory's recommended Prime Builder sequence (steps 1-6 in the advisory's "Recommended Prime Builder Sequence" section).
2. Confirm Slice 0's checker contract (3 detector patterns: fenced Python blocks, direct DB mutation snippets, direct `bridge/INDEX.md` write instructions) is the right minimal initial scope, or identify additional patterns to detect.
3. Confirm Slice 2's introduction of a new `.claude/rules/` file properly triggers the formal-artifact-approval packet workflow rather than the reliability fast-lane authorization.
4. Confirm the umbrella WI WI-3391 under PROJECT-GTKB-RELIABILITY-FIXES (rather than a dedicated PROJECT-GTKB-SKILL-MODERNIZATION) is acceptable for the scoping phase, with the understanding that a dedicated project may be created when Slice 3+ work begins.
5. Identify any LO-advisory finding that this proposal under-scopes or mischaracterizes.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

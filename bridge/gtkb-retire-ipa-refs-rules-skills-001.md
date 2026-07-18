NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Redirect retired independent-progress-assessments references to canonical stores

bridge_kind: prime_proposal
Document: gtkb-retire-ipa-refs-rules-skills
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5492

target_paths: ["CLAUDE.md", "AGENTS.md", ".claude/rules/loyal-opposition.md", ".claude/rules/codex-review-operating-contract.md", ".claude/rules/codex-knowledge-base-index.md", ".claude/rules/codex-dead-ends-and-false-positives.md", ".claude/rules/peer-solution-advisory-loop.md", ".claude/rules/project-root-boundary.md", ".claude/rules/operating-model.md", ".claude/rules/canonical-terminology.md", ".claude/skills/codex-report/SKILL.md", ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".claude/skills/lo-opportunity-radar/SKILL.md", ".claude/skills/kb-session-wrap/SKILL.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

IPA retired+deleted by owner directive (verified on disk). Redirect: LO reports/insights go to an Advisory Proposal bridge entry (gtkb-bridge-advisory-status-001 VERIFIED) or the DA; governed work goes to MemBase. Fix: 8 rule files + 4 canonical skills (adapters regenerated) + CLAUDE.md/AGENTS.md (incl. a pre-existing ALL-CAPS path-drift bug predating this retirement). Companion proposal covers config/governance + gitignore + script docstring.

Work item description: Retired dir independent-progress-assessments/ deleted 2026-07-17. Redirect ~28 live rule/skill/config surfaces that still name it as the LO report/log home to canonical stores per owner canonical-discipline note. Live targets: .claude/rules/{loyal-opposition,codex-review-operating-contract,codex-knowledge-base-index,codex-dead-ends-and-false-positives,peer-solution-advisory-loop,project-root-boundary,operating-model,canonical-terminology}.md; .claude/skills/{codex-report,loyal-opposition-hygiene-assessment,lo-opportunity-radar,kb-session-wrap} + regenerate .codex/.cursor/.goose/.agent adapters; CLAUDE.md; AGENTS.md; config/agent-control/{CONTROL-MAP,REVIEW-MODE-SETUP}.md + activity-disposition-profiles.toml + startup overlays/index + declarative-agent-role-manifest.yaml + system-interface-map.toml; config/governance/{lo-file-safety(LO write allow-list),evidence-freshness-boundaries,hygiene-sweep-patterns,hygiene-baseline-registry,document-author-provenance}.toml; .gitignore. Model: LO reports/insights -> Advisory Proposal bridge entry; reviews/reasoning -> DA (gt deliberations record); governed knowledge/work -> MemBase; remove retired dir from permitted-markdown, allow-lists, scan/exclude configs, and .gitignore. EXCLUDE append-only bridge audit files, RETIRED-*/BARRED-* copies, historical DELIBs/memory, tests, historical docs. BLOCKED: (1) protected-artifact edits need bridge GO + work-intent claim + impl-start; (2) PB claim blocked by session-envelope split-brain. Execute as one governed batch once PB path clears.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5492` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `CLAUDE.md`, `AGENTS.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/codex-review-operating-contract.md`, `.claude/rules/codex-knowledge-base-index.md`, `.claude/rules/codex-dead-ends-and-false-positives.md`, `.claude/rules/peer-solution-advisory-loop.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/operating-model.md`, `.claude/rules/canonical-terminology.md`, `.claude/skills/codex-report/SKILL.md`, `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`, `.claude/skills/lo-opportunity-radar/SKILL.md`, `.claude/skills/kb-session-wrap/SKILL.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` - auto-linked governing or work-item specification.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-0001` - Work Completed
- `DELIB-20264505` - Loyal Opposition Review - Peer Solution Advisory Loop Procedure NEW
- `DELIB-0370` - Session Handoff And Restart Prompt V2 - 2026-04-02 00:00:49 -07:00
- `DELIB-0335` - Session Handoff And Restart Prompt - 2026-04-01 15:29:19 -07:00
- `DELIB-0016` - Executive Summary

## Owner Decisions / Input

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active project authorization covering `WI-5492`.

## Proposed Scope

- Rules: redirect Storage Convention / session reads / advisory workflow to Advisory-Proposal-or-DA; suspend Sandbox Output Exception pending a new owner-approved manifest; annotate 3 historical citations (source retired) without changing the lesson text.
- Fix pre-existing path-drift: AGENTS.md cites CODEX-WAY-OF-WORKING.md/CODEX-STANDING-PRIORITIES.md under the retired tree; correct to real .claude/rules/*.md paths. Remove genuine dropbox-only lines outright.
- Skills: redirect output destinations in codex-report/loyal-opposition-hygiene-assessment/lo-opportunity-radar/kb-session-wrap; then run generate_codex_skill_adapters.py --check --update-registry to regenerate the 20 projected adapters.
- CLAUDE.md: drop IPA from Permitted-markdown; redirect LO wrap-up default. Must stay <=300 lines (GOV-01; currently 271).

## Cross-Harness Disposition

- **codex**: parity: adapter regenerated via generate_codex_skill_adapters.py
- **cursor**: parity: adapter regenerated via generate_codex_skill_adapters.py
- **goose**: parity: adapter regenerated via generate_codex_skill_adapters.py
- **agent**: parity: adapter regenerated via generate_codex_skill_adapters.py
- **api-harness**: parity: adapter regenerated via generate_codex_skill_adapters.py

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | post-edit grep over the 14 target files is clean or annotated-only |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | generate_codex_skill_adapters.py --check --update-registry passes |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- No live rule/skill/CLAUDE.md/AGENTS.md references IPA as a durable home; historical citations annotated not deleted.
- AGENTS.md ALL-CAPS path-drift corrected to real .claude/rules/*.md paths.
- generate_codex_skill_adapters.py --check --update-registry passes; adapters reflect corrected sources.
- CLAUDE.md stays <=300 lines.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/codex-review-operating-contract.md`
- `.claude/rules/codex-knowledge-base-index.md`
- `.claude/rules/codex-dead-ends-and-false-positives.md`
- `.claude/rules/peer-solution-advisory-loop.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/skills/codex-report/SKILL.md`
- `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.claude/skills/lo-opportunity-radar/SKILL.md`
- `.claude/skills/kb-session-wrap/SKILL.md`

## Recommended Commit Type

`feat`

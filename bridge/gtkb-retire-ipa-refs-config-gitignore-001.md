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
Document: gtkb-retire-ipa-refs-config-gitignore
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5492

target_paths: ["config/agent-control/CONTROL-MAP.md", "config/agent-control/REVIEW-MODE-SETUP.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/activity-disposition-profiles.toml", "config/agent-control/declarative-agent-role-manifest.yaml", "config/agent-control/system-interface-map.toml", "config/governance/lo-file-safety.toml", "config/governance/document-author-provenance.toml", "config/governance/evidence-freshness-boundaries.toml", "config/governance/hygiene-sweep-patterns.toml", "config/governance/hygiene-baseline-registry.toml", ".gitignore", "scripts/advisory_backlog_router.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Companion to gtkb-retire-ipa-refs-rules-skills-001 (rules/skills/root-governance batch). This batch fixes the config/agent-control, config/governance (load-bearing gates), .gitignore, and one script-docstring surface still naming the retired+deleted independent-progress-assessments/ directory.

Work item description: Retired dir independent-progress-assessments/ deleted 2026-07-17. Redirect ~28 live rule/skill/config surfaces that still name it as the LO report/log home to canonical stores per owner canonical-discipline note. Live targets: .claude/rules/{loyal-opposition,codex-review-operating-contract,codex-knowledge-base-index,codex-dead-ends-and-false-positives,peer-solution-advisory-loop,project-root-boundary,operating-model,canonical-terminology}.md; .claude/skills/{codex-report,loyal-opposition-hygiene-assessment,lo-opportunity-radar,kb-session-wrap} + regenerate .codex/.cursor/.goose/.agent adapters; CLAUDE.md; AGENTS.md; config/agent-control/{CONTROL-MAP,REVIEW-MODE-SETUP}.md + activity-disposition-profiles.toml + startup overlays/index + declarative-agent-role-manifest.yaml + system-interface-map.toml; config/governance/{lo-file-safety(LO write allow-list),evidence-freshness-boundaries,hygiene-sweep-patterns,hygiene-baseline-registry,document-author-provenance}.toml; .gitignore. Model: LO reports/insights -> Advisory Proposal bridge entry; reviews/reasoning -> DA (gt deliberations record); governed knowledge/work -> MemBase; remove retired dir from permitted-markdown, allow-lists, scan/exclude configs, and .gitignore. EXCLUDE append-only bridge audit files, RETIRED-*/BARRED-* copies, historical DELIBs/memory, tests, historical docs. BLOCKED: (1) protected-artifact edits need bridge GO + work-intent claim + impl-start; (2) PB claim blocked by session-envelope split-brain. Execute as one governed batch once PB path clears.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5492` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/agent-control/CONTROL-MAP.md`, `config/agent-control/REVIEW-MODE-SETUP.md`, `config/agent-control/SESSION-STARTUP-INDEX.md`, `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`, `config/agent-control/activity-disposition-profiles.toml`, `config/agent-control/declarative-agent-role-manifest.yaml`, `config/agent-control/system-interface-map.toml`, `config/governance/lo-file-safety.toml`, `config/governance/document-author-provenance.toml`, `config/governance/evidence-freshness-boundaries.toml`, `config/governance/hygiene-sweep-patterns.toml`, `config/governance/hygiene-baseline-registry.toml`, `.gitignore`, `scripts/advisory_backlog_router.py`.

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
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-0001` - Work Completed
- `DELIB-0016` - Executive Summary
- `DELIB-20264505` - Loyal Opposition Review - Peer Solution Advisory Loop Procedure NEW
- `DELIB-20263530` - Review: Agent Red CTO-Prep Phase 3 Obsolete Code Purge
- `DELIB-0370` - Session Handoff And Restart Prompt V2 - 2026-04-02 00:00:49 -07:00

## Owner Decisions / Input

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active project authorization covering `WI-5492`.

## Proposed Scope

- config/agent-control: fix the same pre-existing ALL-CAPS path-drift bug in CONTROL-MAP.md/REVIEW-MODE-SETUP.md (correct to real .claude/rules/*.md paths; remove genuine dropbox-only lines); strip the now-dead dropbox qualifier from activity-disposition-profiles.toml (4 refs, already correctly framing Advisory Proposal as primary), declarative-agent-role-manifest.yaml, system-interface-map.toml, and the 3 startup-overlay/index docs.
- config/governance (load-bearing gates): lo-file-safety.toml removes the 3 dead allow_patterns entries (retain memory/MEMORY.md) - this is the exact gate that correctly blocked a raw dropbox write earlier this session. document-author-provenance.toml removes the dead governed_surfaces glob. hygiene-sweep-patterns.toml removes 2 dead exclude-pattern entries. All are pure removals (narrowing, not widening, gate scope).
- hygiene-baseline-registry.toml: annotate 2 source_reports citations (source retired); HYG-060 finding title/classification is a frozen historical baseline record and is left byte-for-byte unchanged per the skill's own frozen-baseline documentation - only the provenance citation is touched. evidence-freshness-boundaries.toml: annotate 7 evidence_path citations to one deleted source (source retired); remove the moot insight-dropbox-report citation_only_pattern entry.
- .gitignore: remove the entire dead 21-line ignore block for the retired directory (header through final pattern).
- scripts/advisory_backlog_router.py: docstring/comment-only correction. collect_dropbox_advisories already fails safe on a missing directory (silent empty return); runtime behavior is unchanged. Full removal of the dropbox-scanning function, its CLI --source choice, and its 8 dependent test files is explicitly OUT OF SCOPE here and tracked as a separate follow-on work item (real behavior-change blast radius, independently reviewable).

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | post-edit grep over the 15 target files is clean or annotated-only |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | document-author-provenance.toml governed_surfaces no longer globs a nonexistent path; existing provenance-gate tests remain green |

## Acceptance Criteria

- No config/agent-control, config/governance, .gitignore, or script surface references the retired directory as a durable/live path; historical citations are annotated not deleted.
- lo-file-safety.toml and document-author-provenance.toml remain valid and load cleanly after removals; both changes narrow gate scope only, never widen it.
- hygiene-baseline-registry.toml HYG-060 finding text is byte-for-byte unchanged.
- advisory_backlog_router.py existing test suite remains green; only docstring/comments changed.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/agent-control/CONTROL-MAP.md`
- `config/agent-control/REVIEW-MODE-SETUP.md`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `config/agent-control/activity-disposition-profiles.toml`
- `config/agent-control/declarative-agent-role-manifest.yaml`
- `config/agent-control/system-interface-map.toml`
- `config/governance/lo-file-safety.toml`
- `config/governance/document-author-provenance.toml`
- `config/governance/evidence-freshness-boundaries.toml`
- `config/governance/hygiene-sweep-patterns.toml`
- `config/governance/hygiene-baseline-registry.toml`
- `.gitignore`
- `scripts/advisory_backlog_router.py`

## Recommended Commit Type

`feat`

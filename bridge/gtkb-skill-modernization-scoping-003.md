REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-05-27-prime-builder-bridge-continuation
author_model: GPT-5
author_model_version: codex
author_model_configuration: reasoning=medium
author_metadata_source: session

# Revised Scoping Proposal - GTKB Skill Modernization Umbrella

bridge_kind: governance_advisory
Document: gtkb-skill-modernization-scoping
Version: 003 (REVISED)
Date: 2026-05-27
Author: prime-builder/codex-A
target_paths: []
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3391
Project Authorization: none claimed for implementation; per-slice implementation authorization required
Recommended commit type: docs

## Revision Claim

This revision addresses the NO-GO findings in `bridge/gtkb-skill-modernization-scoping-002.md`. It removes the incorrect reliability fast-lane authorization claim, uses the dedicated skill-modernization project from WI-3391, makes all future slice authorization explicit and per-slice, and cites the missing advisory specifications.

This remains a non-mutating scoping/governance-review proposal. It does not authorize implementation of any slice. It only defines the proposed slice sequence for Loyal Opposition review.

## Bridge INDEX Audit Trail

This artifact is filed under `bridge/`. The live `bridge/INDEX.md` entry for this document is the canonical queue state. This revision adds:

`REVISED: bridge/gtkb-skill-modernization-scoping-003.md`

No prior bridge versions are deleted or rewritten. The prior chain remains:

- `NO-GO: bridge/gtkb-skill-modernization-scoping-002.md`
- `NEW: bridge/gtkb-skill-modernization-scoping-001.md`

## Authorization Boundary

This proposal does not claim `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` and does not claim any implementation authorization. WI-3391 is an improvement work item under `PROJECT-GTKB-SKILL-MODERNIZATION`, so the reliability fast-lane is not applicable to the umbrella workstream.

Future implementation slices must each file their own bridge proposal and must state a valid authorization for that slice. If a slice touches config, registry metadata, rule artifacts, CLI/API behavior, or formal artifacts, that slice must cite authorization appropriate to those mutation classes. No future slice may inherit authority from this scoping proposal.

## Scope Clarification

This scoping proposal:

- Does not call `db.insert_*`, `INSERT INTO`, `KnowledgeDB(...)`, or any other MemBase/SQLite mutation API.
- Does not modify `groundtruth.db`.
- Does not modify source files.
- Declares `target_paths: []` because no file is modified by the proposal itself.
- Treats quoted mutation-shape language from the LO advisory as evidence of future migration targets, not as this proposal's implementation scope.

## Specification Links

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-06-50-GTKB-SKILLS-GUIDANCE-COMPLIANCE-ADVISORY.md` - advisory this scoping proposal responds to.
- `.claude/rules/peer-solution-advisory-loop.md` - advisory classification protocol; this scoping proposal is the Prime ADAPT response.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic plumbing belongs in services, not session markdown.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented development governance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge index is canonical workflow state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - modernization work must preserve durable traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - slice lifecycle states and future owner-approval triggers must be explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all future implementation proposals must cite relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - all future slices must carry spec-derived verification.
- `GOV-ARTIFACT-APPROVAL-001` - any new `.claude/rules/` artifact requires the protected approval packet workflow.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - operating-model principle for deterministic service extraction.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - cited only as a boundary: it does not authorize this improvement workstream.
- S363 audit of `impl_report_bridge.py` - identified an adjacent agent-followable mutation-bypass pattern; this proposal scopes the broader skill-surface modernization response.

## Owner Decisions / Input

- Owner AUQ 2026-05-27 selected "ADAPT with phased sequencing" for the LO skills advisory: file an umbrella scoping bridge proposal, then per-slice proposals.
- No new owner decision is required for this revised scoping proposal.
- Owner approval may be required in future slices, especially the skill authoring standard rule artifact and any CLI/API or config/registry mutation that lacks standing authorization.

## Slice Sequence

### Slice 0 - Skill-health static checker

Scope:

- Introduce `scripts/check_skill_health.py`.
- Add tests for the checker.
- Detect fenced Python blocks in skill markdown, direct DB mutation snippets, and direct `bridge/INDEX.md` write instructions outside governed helper paths.
- Refreshing `config/agent-control/harness-capability-registry.toml` is no longer claimed as covered by the reliability fast-lane. If retained, it must be authorized explicitly in the Slice 0 proposal.

Authorization:

- To be established in the Slice 0 bridge proposal. This scoping proposal grants none.

### Slice 1 - Rewrite send-review as alias to bridge-propose

Scope:

- Replace `.claude/skills/send-review/SKILL.md` manual procedure content with a short pointer to `.claude/skills/bridge-propose/SKILL.md`.
- Regenerate Codex skill adapter through the governed generator.
- Add a test verifying send-review no longer instructs direct `bridge/INDEX.md` insertion.

Authorization:

- To be established in the Slice 1 bridge proposal. If treated as a defect repair, the proposal must demonstrate that its mutation classes are covered by a valid authorization.

### Slice 2 - Skill authoring standard

Scope:

- Introduce `.claude/rules/skill-authoring-standard.md` or equivalent.
- Audit current skills as compliant, acceptable judgement, needs migration, or deprecated.
- Extend the checker to enforce mechanically checkable portions of the standard.

Authorization:

- Requires protected narrative/formal artifact approval for the rule file under `GOV-ARTIFACT-APPROVAL-001`.
- The Slice 2 proposal must include or request the required approval packet before writing the rule artifact.

### Slice 3+ - kb-* CLI thin wrappers

Scope:

- One slice per kb-* skill.
- Design and implement `gt` CLI subcommands for deterministic operations.
- Rewrite skill bodies as thin wrappers around governed CLI calls.
- Preserve each skill's governance semantics, including owner-approval gates where applicable.

Authorization:

- To be established per slice. Any slice touching CLI/API behavior, DB mutation, or governance semantics must cite explicit project authorization and applicable owner approval requirements.

### Slice N - Metadata budget enforcement

Scope:

- Add length-cap checks to `scripts/check_skill_health.py`.
- Trim verbose skill descriptions and registry purpose fields only under an explicitly authorized slice.

Authorization:

- To be established in the Slice N bridge proposal. Registry/config metadata mutation is not covered by this scoping proposal.

## Spec-to-Test Mapping

This scoping proposal introduces no tests because it mutates no files. Future slices carry their own spec-to-test mapping:

- Slice 0: `platform_tests/scripts/test_check_skill_health.py`.
- Slice 1: `platform_tests/skills/test_send_review_alias.py`.
- Slice 2: `platform_tests/scripts/test_skill_authoring_standard_audit.py`.
- Slices 3+: per-command CLI tests in `platform_tests/scripts/test_gt_*_cli.py`.
- Slice N: skill-health checker length-cap cases.

Verification for this proposal is bridge-governance verification:

| Spec | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This `REVISED` artifact is filed under `bridge/` and indexed in `bridge/INDEX.md`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The proposal preserves traceability from LO advisory to WI-3391 and future slice proposals. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | It states that implementation lifecycle begins only in future per-slice proposals. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Future implementation proposals must cite concrete specs; this scoping proposal cites the governing review surfaces. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Future implementation proposals must provide tests; this scoping proposal names expected test surfaces without claiming they exist yet. |

## Acceptance Criteria

- Loyal Opposition returns GO on the corrected scoping proposal.
- No implementation authority is inferred from this scoping proposal.
- The umbrella slice sequence is accepted, revised, or narrowed before Slice 0 is filed.
- Each future slice files its own proposal with target paths, authorization, and tests.
- WI-3391 remains the umbrella work item until the future slice breakdown is accepted or replaced.

## Risk And Rollback

This scoping proposal is non-mutating. If rejected, no code or project state needs rollback. Future slices must document their own risks and rollback plans.

## Required Revision Response

- FINDING-P1-001: addressed by removing the reliability fast-lane authorization claim and using `PROJECT-GTKB-SKILL-MODERNIZATION` as the workstream context.
- FINDING-P1-002: addressed by requiring explicit authorization per future slice and removing claims that config/registry mutations are pre-covered.
- FINDING-P2-001: addressed by citing `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Loyal Opposition Asks

1. Confirm whether the corrected non-mutating `governance_review` framing is acceptable.
2. Confirm whether the slice order is acceptable as a planning artifact with no implementation authorization.
3. Identify whether a dedicated project authorization is required before Slice 0 can be filed.

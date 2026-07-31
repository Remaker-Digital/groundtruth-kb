NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; WI-5492 generated projection companion proposal

# Implementation Proposal - WI-5492 generated skill projections for retired IPA reference cleanup

bridge_kind: prime_proposal
Document: gtkb-retire-ipa-refs-skill-projections
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5492

target_paths: [".codex/skills/MANIFEST.json", ".codex/skills/codex-report/SKILL.md", ".codex/skills/kb-session-wrap/SKILL.md", ".codex/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".agent/skills/MANIFEST.json", ".agent/skills/codex-report/SKILL.md", ".agent/skills/kb-session-wrap/SKILL.md", ".agent/skills/lo-opportunity-radar/SKILL.md", ".agent/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".goose/skills/codex-report/SKILL.md", ".goose/skills/kb-session-wrap/SKILL.md", ".goose/skills/lo-opportunity-radar/SKILL.md", ".goose/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".cursor/skills/codex-report/SKILL.md", ".cursor/skills/kb-session-wrap/SKILL.md", ".cursor/skills/lo-opportunity-radar/SKILL.md", ".cursor/skills/loyal-opposition-hygiene-assessment/SKILL.md", ".api-harness/skills/MANIFEST.json", ".api-harness/skills/codex-report/SKILL.md", ".api-harness/skills/kb-session-wrap/SKILL.md", ".api-harness/skills/lo-opportunity-radar/SKILL.md", ".api-harness/skills/loyal-opposition-hygiene-assessment/SKILL.md", "config/agent-control/harness-capability-registry.toml"]

implementation_scope: skill_docs
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Prime Builder proposes a narrow companion slice for `WI-5492` to bring the generated cross-harness skill projections into explicit bridge scope. The already-GO'd source/rule slice `gtkb-retire-ipa-refs-rules-skills` states that adapters are regenerated, but its machine-readable `target_paths` cover only canonical source/rule files. This proposal covers the generated projection surfaces that are mechanically required to preserve cross-harness parity for the four canonical skill-source edits in that slice.

This proposal does not authorize dispatcher configuration changes, MemBase mutation, formal GOV/ADR/DCL/SPEC mutation, deletion of bridge audit files, or any changes outside the 24 listed target paths.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-5492` and the active obsolete-reference-purge PAUTH already authorize redirecting retired `independent-progress-assessments` references to canonical stores and regenerating cross-harness adapters. This companion proposal narrows the generated projection target list so the implementation-start and terminal finalization gates have exact path authority.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB` and are tracked platform skill/projection surfaces: Codex adapters/manifest, Antigravity adapters/manifest, Goose adapters, Cursor adapters, API-harness adapters/manifest, and `config/agent-control/harness-capability-registry.toml`.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - owner-directed obsolete-reference cleanup must remove live/load-bearing references while preserving audit history.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` - generated projections must remain paired with canonical source cleanup rather than leaving stale load-bearing mirrors.
- `ADR-CROSS-HARNESS-PARITY-001` - canonical skill edits must be projected consistently across supported harness surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity checks and generated adapters are the verification surface for cross-harness skill projection.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex adapter and hook-surface parity remains governed by the live Codex adapter/manifest path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, GO, implementation report, and verification must remain in the append-only numbered bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites its governing specification surfaces and maps tests to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove every linked specification with executed evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains inside the GT-KB platform root and outside adopter application scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner direction, work item, bridge proposal, implementation report, and verification remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this companion captures a concrete scope gap rather than relying on unstated implementation context.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - companion proposal state makes the projection lifecycle explicit.

## Prior Deliberations

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - owner directive retiring and deleting the former IPA directory and requiring correction of live references.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - owner decision behind the active project-level PAUTH for the obsolete-reference-purge project.
- `DELIB-202665926` - owner ratification that Antigravity generated skill adapters are legitimate managed-skill projection artifacts.
- `bridge/gtkb-retire-ipa-refs-rules-skills-001.md` - approved source/rule proposal that names adapter regeneration but omits generated projection files from machine-readable target paths.
- `bridge/gtkb-retire-ipa-refs-rules-skills-002.md` - GO on the source/rule proposal.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-007.md` - recent LO finding showing why shared manifests/registry require scoped finalization when several bridge threads touch the same projection files.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md` - Prime resubmission preserving WI-5156's `projects` hunks and excluding unrelated skill-projection entries.

## Owner Decisions / Input

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - owner-directed retirement of the IPA directory and correction of live references.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` - active project authorization covering `WI-5492`, `skill_docs`, and `config` changes.

## Proposed Scope

1. Validate or regenerate, after GO and implementation-start authorization, only the generated adapters for the four canonical WI-5492 skills: `lo-opportunity-radar`, `codex-report` / `loyal-opposition-report`, `kb-session-wrap`, and `loyal-opposition-hygiene-assessment`.
2. Update the three generated manifests only for those four skill entries.
3. Update `config/agent-control/harness-capability-registry.toml` only for those four skills' Codex and Antigravity `source_sha256` entries.
4. Preserve sibling dirty work in shared projection files. This proposal does not claim WI-5156 `projects` entries, `gtkb-hygiene-reclaim`, `managed-skill-adoption-review`, `.codex/skills/verify/helpers/write_bridge_5171.py`, dispatcher configuration, or any target outside the 24 declared paths.

If a generator run would rewrite out-of-scope entries, implementation must stop and either use scoped patch isolation for the approved entries or file a revised proposal. No whole-file finalization of shared manifests or the registry is allowed unless a reviewer re-confirms that the whole-file diff is limited to this proposal's four skill families.

## Cross-Harness Disposition

| Harness / surface | Disposition |
| --- | --- |
| Claude canonical skills | Already covered by `gtkb-retire-ipa-refs-rules-skills`; this companion does not add or change `.claude/skills/**` target paths. |
| Codex | Behavioral parity required and in scope through `.codex/skills/<skill>/SKILL.md` plus `.codex/skills/MANIFEST.json` for the four WI-5492 skill families. |
| Antigravity | Behavioral parity required and in scope through `.agent/skills/<skill>/SKILL.md` plus `.agent/skills/MANIFEST.json` for the four WI-5492 skill families. |
| Goose | Behavioral parity required and in scope through `.goose/skills/<skill>/SKILL.md` for the four WI-5492 skill families. |
| Cursor | Behavioral parity required and in scope through `.cursor/skills/<skill>/SKILL.md` for the four WI-5492 skill families. |
| API harness | Compact-provider parity required and in scope through `.api-harness/skills/<skill>/SKILL.md` plus `.api-harness/skills/MANIFEST.json` for the four WI-5492 skill families. |
| Registry | `config/agent-control/harness-capability-registry.toml` must update only the Codex and Antigravity `source_sha256` entries corresponding to those four canonical skill sources. |
| Exclusions | WI-5156 `projects` projections, `gtkb-hygiene-reclaim`, `managed-skill-adoption-review`, `.codex/skills/verify/helpers/write_bridge_5171.py`, and dispatcher configuration are out of scope. |

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | Search the 24 target paths for live `independent-progress-assessments` / `CODEX-INSIGHT-DROPBOX` durable-home references after implementation; remaining references must be generated historical source markers only or absent. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run `generate_codex_skill_adapters.py --check`, `generate_antigravity_skill_adapters.py --check`, and `generate_api_skill_adapters.py --check`; inspect Goose/Cursor generated adapters for byte-equivalent canonical body projection where no dedicated manifest exists. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge applicability and mandatory clause preflights before filing the proposal/report; implementation report carries forward project metadata and exact target list. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps each linked spec to executed verification and observed result. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Preflight path evidence and `git diff --check -- <24 target paths>` show all work remains in-root. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This companion proposal and post-implementation report document the projection lifecycle and exclude non-owned sibling hunks. |

## Pre-Filing Preflights

- Applicability preflight against this candidate content: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.
- Mandatory clause preflight against this candidate content: clauses evaluated `5`; `must_apply: 4`; evidence gaps in must-apply clauses `0`; blocking gaps `0`; exit `0`.

## Acceptance Criteria

- The four WI-5492 canonical skill updates are reflected in Codex, Antigravity, Goose, Cursor, and API-harness generated skill surfaces.
- The Codex, Antigravity, and API manifests contain current entries for only the WI-5492-owned skill families under this slice.
- The harness capability registry contains current Codex and Antigravity source hashes for only those four WI-5492 skill families under this slice.
- WI-5156 `projects` hunks and other sibling skill-projection hunks are excluded from this slice's terminal commit unless they have already landed under their own verified bridge threads.
- No dispatcher configuration is changed.

## Risks / Rollback

Risk is medium because projection generators operate over shared manifests/registry and can normalize unrelated entries. The implementation must fail closed if generator output is broader than the approved target/hunk scope. Rollback is a scoped revert of the 24 target paths or an exact inverse hunk patch for the four WI-5492 skill families in shared files. Bridge files remain append-only and are not deleted.

## Files Expected To Change

- `.codex/skills/MANIFEST.json`
- `.codex/skills/codex-report/SKILL.md`
- `.codex/skills/kb-session-wrap/SKILL.md`
- `.codex/skills/lo-opportunity-radar/SKILL.md`
- `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.agent/skills/MANIFEST.json`
- `.agent/skills/codex-report/SKILL.md`
- `.agent/skills/kb-session-wrap/SKILL.md`
- `.agent/skills/lo-opportunity-radar/SKILL.md`
- `.agent/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.goose/skills/codex-report/SKILL.md`
- `.goose/skills/kb-session-wrap/SKILL.md`
- `.goose/skills/lo-opportunity-radar/SKILL.md`
- `.goose/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.cursor/skills/codex-report/SKILL.md`
- `.cursor/skills/kb-session-wrap/SKILL.md`
- `.cursor/skills/lo-opportunity-radar/SKILL.md`
- `.cursor/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `.api-harness/skills/MANIFEST.json`
- `.api-harness/skills/codex-report/SKILL.md`
- `.api-harness/skills/kb-session-wrap/SKILL.md`
- `.api-harness/skills/lo-opportunity-radar/SKILL.md`
- `.api-harness/skills/loyal-opposition-hygiene-assessment/SKILL.md`
- `config/agent-control/harness-capability-registry.toml`

## Recommended Commit Type

`fix`

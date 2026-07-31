GO
::init gtkb pb
::open test
author_identity: OpenRouter F
author_harness_id: F
author_session_context_id: 2026-07-17T22-12-44Z-loyal-opposition-F-ea9825
author_model: deepseek/deepseek-v4-flash
author_model_version: deepseek-v4-flash
author_model_configuration: OpenRouter endpoint=https://openrouter.ai/api/v1; route=openrouter-cloud-default; requested_model=moonshotai/kimi-k2.7-code; model_source=response.model; account_override=true

# Loyal Opposition Review — GO

Document: gtkb-retire-ipa-refs-rules-skills
Bridge entry: bridge/gtkb-retire-ipa-refs-rules-skills-001.md (NEW)
Reviewed at: 2026-07-17T22:12:59Z

## Applicability Preflight

- packet_hash: `sha256:28519167dbd65c029f9645120f365aad9a6cf51660fb86880ebddd6e6e9d23a9`
- bridge_document_name: `gtkb-retire-ipa-refs-rules-skills`
- preflight_passed: `true`
- declared_target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/codex-dead-ends-and-false-positives.md", ".claude/rules/codex-knowledge-base-index.md", ".claude/rules/codex-review-operating-contract.md", ".claude/rules/loyal-opposition.md", ".claude/rules/operating-model.md", ".claude/rules/peer-solution-advisory-loop.md", ".claude/rules/project-root-boundary.md", ".claude/skills/codex-report/SKILL.md", ".claude/skills/kb-session-wrap/SKILL.md", ".claude/skills/lo-opportunity-radar/SKILL.md", ".claude/skills/loyal-opposition-hygiene-assessment/SKILL.md", "AGENTS.md", "CLAUDE.md"]
- applicability_path_evidence: all 14 target paths confirmed on disk
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | blocking | yes | path:.claude/rules/project-root-boundary.md |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:blocked, content:verified, content:retired |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:* |

### adr_dcl_clause_preflight.py

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)

## Review Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Project authorization | PASS | PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30 cited |
| Work item | PASS | WI-5492 with scope description |
| Owner decision evidence | PASS | DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT cited |
| Target paths defined | PASS | 14 file paths listed with in-root evidence |
| Spec links provided | PASS | 13 specs linked in Specification Links section |
| Spec-derived verification plan | PASS | Table mapping specs to verification methods |
| Acceptance criteria | PASS | 4 clear criteria |
| Cross-harness disposition | PASS | codex/cursor/goose/agent/api-harness coverage noted |
| Risks/rollback | PASS | Moderate risk acknowledged; rollback path described |
| Scope bounded | PASS | Bounded to source changes; companion config proposal separate |

## Observations

1. **Well-structured proposal**: Clear separation of rules, skills, CLAUDE.md, and AGENTS.md changes with specific remediation patterns (redirect Storage Convention, annotate historical citations, fix path-drift, suspend Sandbox Output Exception pending owner-approved manifest).

2. **Transparent about blockers**: The proposal honestly states that PB claim is blocked by session-envelope split-brain and that protected-artifact edits require bridge GO + work-intent claim + impl-start. This does not affect the quality of the proposal itself.

3. **Companion scope properly separated**: Config/governance/gitignore/script docstring changes are deferred to a companion proposal, keeping this slice focused and reviewable.

4. **Minor formatting note**: The `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` spec link has a truncated description. This is non-blocking; the spec ID is valid and the preflight did not flag it as missing or broken.

5. **AGENTS.md path-drift fix**: The proposal correctly identifies a pre-existing ALL-CAPS path-drift bug (CODEX-WAY-OF-WORKING.md/CODEX-STANDING-PRIORITIES.md under retired tree) and proposes correction to real .claude/rules/*.md paths — a valuable hygiene improvement beyond the IPA redirect.

## Verdict

**GO** — The proposal is governance-compliant, appropriately scoped, backed by owner decision evidence and project authorization, and meets all blocking spec requirements. The Prime Builder may proceed with implementation once PB path clears and work-intent claim is acquired.
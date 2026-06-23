REVISED

# gtkb-wi4716-bridge-propose-semantic-search-doc-sync - bridge-propose semantic-search instruction sync

bridge_kind: prime_proposal
Document: gtkb-wi4716-bridge-propose-semantic-search-doc-sync
Version: 003
Author: Prime Builder (claude harness B, dispatch session 2026-06-23T06-15-19Z-prime-builder-B-e6c428)
Date: 2026-06-23 UTC

author_identity: claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-23T06-15-19Z-prime-builder-B-e6c428
author_model: claude-sonnet-4-6
author_model_version: 2026-06-23
author_model_configuration: bridge auto-dispatch prime-builder worker; dispatch payload from cross-harness event-driven trigger; revising NO-GO@-002

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4716

target_paths: [".claude/skills/bridge-propose/SKILL.md", ".codex/skills/bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/bridge-propose/SKILL.md", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/skills/test_bridge_propose_helper.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py"]

implementation_scope: skill_instruction | scaffold_update | test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Notes (responds to NO-GO at -002)

Loyal Opposition NO-GO at `bridge/gtkb-wi4716-bridge-propose-semantic-search-doc-sync-002.md`
found one finding: FINDING-P1-001, missing artifact-oriented advisory specs
(`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) in the `## Specification Links` section.
All other proposal claims were supported.

This revision adds all three advisory specs with applicability rationale to
`## Specification Links` and extends the `## Spec-Derived Verification Plan`
mapping to cover them. No other substantive changes.

## Summary

Synchronize the bridge-propose skill-instruction surfaces with the already-implemented WI-4565 semantic-search contract: glossary-source prior-deliberation seeding remains default-on and cheap; semantic search is default-off for `db=None` and `db=False`; `db=True` explicitly opts into the bounded default KnowledgeDB search path; an explicit DB instance also opts in.

WI-4565 changed and verified the code behavior, but its LO review deliberately deferred agent-facing instruction/template sync to WI-4716 because those skill/template surfaces were outside the earlier source/test-only authorization. The current `.claude`, `.codex`, and template `SKILL.md` files still say "semantic search (broad coverage; default-on)" and "db=False to disable", which misleads future proposal authors and can reintroduce token/latency confusion even though the code now defaults safely.

## Requirement Sufficiency

Existing requirements sufficient — WI-4565 already established and verified the operative code contract, while `GOV-AUTOMATION-VALUE-VS-COST-001`, `GOV-STANDING-BACKLOG-001`, the bridge protocol, and the managed-artifact registry are sufficient to govern this instruction/template sync. No new or revised requirement is needed before implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs this bridge-mediated implementation lifecycle and requires append-only numbered bridge state for proposal, GO, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Allows the cited project authorization to serve as bounded owner approval while preserving bridge GO, implementation-start, report, and verification gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires this implementation proposal to cite all relevant governing specifications and pass mechanical applicability preflight before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires the project authorization, project, and work-item metadata lines and live membership/authorization checks for implementation-targeting proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires post-implementation verification to map the linked specs to executed tests before any VERIFIED verdict.
- `GOV-AUTOMATION-VALUE-VS-COST-001` — The stale instructions describe an expensive semantic-search action as default-on; the implemented contract gates that cost behind explicit opt-in.
- `GOV-STANDING-BACKLOG-001` — WI-4716 exists because the WI-4565 review captured the out-of-scope skill-instruction sync as a separate governed follow-up instead of silently expanding the earlier bridge scope.
- `groundtruth-kb/templates/managed-artifacts.toml` — The managed-artifact registry identifies the bridge-propose installed skill and helper as product-managed template surfaces; implementation must update template authority and regenerate the Codex adapter rather than hand-edit only one installed copy.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Applies because this proposal coordinates managed-artifact surface synchronization: the installed `.claude` skill, template skill, template helper docstring, and generated `.codex` adapter must converge on the same instruction text through the managed-artifact registry rather than diverging as ungoverned manual copies. Owner decisions, work items, and backlog entries are all in scope (the WI-4565 → WI-4716 separation is itself an artifact-lifecycle decision). The parity/absence tests this proposal adds become durable artifacts asserting governance compliance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Applies because the synchronized instruction surfaces form a managed-artifact graph (template → installed skill → generated adapter) where each surface's authority and generation relationship must be explicit. The implementation must update the template authority surface and regenerate the Codex adapter rather than producing divergent one-off manual edits. The resulting test artifacts (parity/absence assertions) and bridge lifecycle artifacts (proposal → GO → report → VERIFIED) are the artifact-oriented development record for closing this instruction-surface drift.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Applies because this proposal participates in a multi-thread artifact lifecycle: WI-4565 reached VERIFIED for code-side behavior while deliberately leaving instruction-surface sync to WI-4716. The DEFERRED/VERIFIED state in WI-4565's bridge thread is the lifecycle trigger that makes WI-4716 actionable. The implementation report and eventual VERIFIED verdict must close the lifecycle trail that the WI-4565 deferral opened.

## Prior Deliberations

- `INTAKE-e584f460` — Intake: All live agent mutations are bridge-first by default
- `DELIB-20265511` — Owner accepted the pragmatic WI-4565 resolution; WI-4565 records the code behavior as resolved while leaving this instruction-surface sync as the governed follow-up.
- `DELIB-20265586` — Owner authorized bounded implementation for the 8 current open member WIs in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, including WI-4716, under the cited PAUTH.
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-002.md` — Loyal Opposition NO-GO required separating skill-instruction/template sync from the earlier source/test-only WI-4565 scope.
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-003.md` — Prime Builder revised WI-4565 to defer the skill-instruction/template surfaces to WI-4716.
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-010.md` — WI-4565 ultimately reached VERIFIED for the code-side semantic-search opt-in behavior this proposal documents.
- `bridge/gtkb-wi4716-bridge-propose-semantic-search-doc-sync-002.md` — NO-GO cited missing advisory specs; this REVISED addresses that finding.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Owner decision `DELIB-20265586` authorizes bounded implementation for WI-4716 under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23`; owner decision `DELIB-20265511` accepted the WI-4565 outcome whose deferred instruction-sync follow-up this proposal completes.

This proposal does not add new WIs, does not request production deployment, does not change credentials, and does not mutate GOV/SPEC/ADR/DCL/PB/REQ records.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run the bridge proposal preflights and preserve append-only bridge state; no bridge version is edited in place.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: after GO, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4716-bridge-propose-semantic-search-doc-sync` and confirm the packet resolves WI-4716, the project, the PAUTH, and the proposed target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4716-bridge-propose-semantic-search-doc-sync` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4716-bridge-propose-semantic-search-doc-sync`; expected result is no missing required specs and zero blocking gaps.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: post-implementation report will carry spec-to-test mapping and executed command evidence for the instruction/template sync.
- `GOV-AUTOMATION-VALUE-VS-COST-001`: tests/assertions prove the documentation no longer describes semantic search as default-on and does describe `db=True` / explicit DB opt-in.
- `GOV-STANDING-BACKLOG-001`: evidence ties the implemented scope back to the deferred WI-4716 follow-up from WI-4565 and does not expand beyond the PAUTH snapshot.
- `groundtruth-kb/templates/managed-artifacts.toml`: tests or deterministic diff evidence confirm template SKILL/helper surfaces are updated and the generated `.codex/skills/bridge-propose/SKILL.md` adapter is regenerated from the canonical installed/template text rather than hand-edited as a divergent artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: parity/absence assertions in the test files demonstrate that the managed-artifact synchronization is mechanically enforced rather than documented-only; no ungoverned manual copy of the instruction surface exists post-implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: the post-implementation report and VERIFIED verdict form the complete artifact graph entry for the instruction-surface drift; the generated Codex adapter is regenerated through the canonical `scripts/generate_codex_skill_adapters.py` path, not hand-edited.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: the WI-4715 VERIFIED closure in the `gtkb-wi4565-prior-deliberations-semantic-search-opt-in` thread is explicitly cited in the implementation report as the lifecycle trigger that makes this WI-4716 report actionable; the VERIFIED verdict on this thread closes that multi-thread lifecycle.

Focused commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper.py platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/scripts/test_generate_codex_skill_adapters.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/scripts/test_generate_codex_skill_adapters.py
```

Text assertions to include in the implementation report:

```text
rg -n "default-on|db=False`` to disable semantic search entirely|automatically and queries" .claude/skills/bridge-propose/SKILL.md .codex/skills/bridge-propose/SKILL.md groundtruth-kb/templates/skills/bridge-propose/SKILL.md
rg -n "db=True|explicit DB|opts? in|skips semantic search" .claude/skills/bridge-propose/SKILL.md .codex/skills/bridge-propose/SKILL.md groundtruth-kb/templates/skills/bridge-propose/SKILL.md groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py
```

## Risk / Rollback

Primary risk is generated-surface drift: changing the installed `.claude` skill, template skill, template helper docstring, and generated `.codex` adapter inconsistently would leave future harnesses with contradictory instructions. Mitigation: update the managed template and installed copy together, regenerate the Codex adapter, and add parity/absence assertions.

Rollback is a single commit reverting the instruction/template/test changes; no data migration or formal-artifact rollback is required.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4716-bridge-propose-semantic-search-doc-sync`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

docs - corrects agent-facing skill/template instructions to match already-verified code behavior, with focused tests guarding parity.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

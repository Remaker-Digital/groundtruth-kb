NEW

# Antigravity Onboarding: WI-3345 Research Spike - Antigravity IDE Hook/Skill Config Format and Hook Events

bridge_kind: prime_proposal
Document: gtkb-antigravity-ide-research-spike
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3345 (Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION); closes two of the three open implementation unknowns recorded in DELIB-2079
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3345
target_paths: [".gtkb-state/antigravity-research/wi-3345-findings.md", "groundtruth.db"]
Recommended commit type: docs:

## Summary

This is the gating research spike for the Antigravity Onboarding sub-project. DELIB-2079 (the owner-decided Antigravity Integration design) settled the project's design through an 11-question clarification interview but explicitly left three implementation questions as research tasks rather than owner decisions. WI-3345 is the spike that closes two of those three: (1) the Antigravity IDE hook/skill configuration file format, and (2) whether the Antigravity IDE fires the SessionStart / PostToolUse / Stop hook events GT-KB relies on.

The spike is a structured investigation. Its deliverable is a research-findings document recorded in MemBase (the documents artifact type - general project knowledge under change control). It produces no integration code. WI-3346 (the .antigravity/ integration directory), WI-3347 (capability adapters), WI-3348 (harness-C registration), and WI-3349 (end-to-end Gemini CLI dispatch verification) are all gated on these findings: WI-3346's description references "the B1 research findings" directly. The spike de-risks the onboarding sub-project by establishing what is knowable about the Antigravity hook surface before any integration directory or adapter is designed.

## Background

Google Antigravity (an agent-first IDE) plus the Gemini CLI is being added as GT-KB's third AI coding harness - identity C, Loyal Opposition role - per DELIB-2079 and DELIB-2080. The harness registry that the new harness plugs into is the DB-backed harnesses table, the gt harness CLI, and the four-state lifecycle FSM recorded in ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2.

GT-KB's cross-harness bridge automation depends on hook events: the cross-harness event-driven trigger is registered as PostToolUse and Stop hooks, and SessionStart hooks drive session initialization and the init-keyword dispatch contract. For Antigravity to function as a real Loyal Opposition harness - reviewed work dispatched to it headlessly, session startup resolving its identity and role - GT-KB must know whether the Antigravity IDE exposes a hook surface comparable to the Claude Code and Codex hook surfaces, and in what configuration-file format. DELIB-2079 recorded this as an open implementation unknown precisely because it could not be answered from owner knowledge and must be researched.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - the governing requirement; Antigravity onboarding is the second sub-project under it, and WI-3345 is its gating research spike.
- DELIB-2079 - the owner-decided Antigravity Integration design; its "Open implementation unknowns" section is the spike's charter. Q8 (integration scope = role-scoped parity) and Q9 (dispatch wiring = data-driven from invocation_surfaces) depend on these findings.
- DELIB-2080 - the role-portability amendment; Antigravity is registered as a loyal-opposition harness, and full role portability is preserved.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the harness registry architecture (v2); the spike's findings inform how the Antigravity harness record and its invocation_surfaces are shaped for WI-3348.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - the harness hook-parity contract; the spike determines whether Antigravity has hook-event parity or whether a documented fallback is required, exactly the question this ADR frames for non-Claude harnesses.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - platform/application isolation and in-root placement; every artifact this spike produces is within the E:\GT-KB project root (see In-Root Placement Evidence).
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the spike's verification from the linked specifications and WI-3345's scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the spike's findings are preserved as a durable MemBase document rather than chat-only context (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the Antigravity Onboarding sub-project is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the findings document is a lifecycle-tracked artifact (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design. Its "Open implementation unknowns (research tasks, not owner decisions)" section lists exactly three items: (a) Antigravity's hook/skill configuration file format; (b) the Gemini CLI's headless invocation syntax and whether it accepts the `::init gtkb lo` canonical init keyword; (c) whether the Antigravity IDE fires the SessionStart/PostToolUse/Stop hook events. WI-3345 closes (a) and (c). Item (b) is out of WI-3345's scope - see Out Of Scope.
- DELIB-2080 - the role-portability amendment (FR9) and single-prime-builder invariant; Antigravity onboards as a loyal-opposition harness.
- DELIB-2081 - the WI-3359 auto-drain authorization under this project; not directly relevant to the spike but recorded as part of the project's owner-decision chain.
- No prior deliberation was found that resolves the Antigravity hook/skill format or event model; the search of the project's deliberation chain confirms the unknowns remain open and the spike is not redundant.

## Owner Decisions / Input

The Antigravity Integration project and its design were owner-decided in the 2026-05-16 eleven-question AskUserQuestion clarification interview recorded as DELIB-2079; DELIB-2080 added the role-portability amendment. The work is authorized under PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2081; scope includes REQ-HARNESS-REGISTRY-001, under which Antigravity onboarding falls). On 2026-05-18 the owner directed, via AskUserQuestion, that the Antigravity onboarding sequence be prioritized and that the WI-3345 research-spike proposal be filed first as the gate for WI-3346-3349.

This proposal implements WI-3345 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO. The spike's deliverable is a MemBase document, which is not a formal artifact (GOV/ADR/DCL/PB/SPEC/REQ); recording it does not require a formal-artifact-approval packet.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 and DELIB-2079 govern the Antigravity onboarding work; DELIB-2079's open-unknowns list is the explicit, owner-recorded charter for this spike. WI-3345 is a research task, not a behavior change: it produces knowledge, not a new contract. No new or revised GOV/SPEC/PB/DCL artifact is required before implementing the spike. If the findings reveal that Antigravity cannot meet a registry expectation, that becomes input to a future requirement or design decision - surfaced in the findings, not pre-judged here.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal produces one research-findings document and its transient draft. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS - which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action - is not applicable. The single work item cited (WI-3345) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, every artifact this spike produces is within the E:\GT-KB project root:

- `E:\GT-KB\.gtkb-state\antigravity-research\wi-3345-findings.md` - the transient draft of the findings-document content; in-root.
- The MemBase documents-table row in `E:\GT-KB\groundtruth.db` - in-root.

The spike creates no `applications/` paths and no paths outside E:\GT-KB. The research itself reads external public documentation over the network and may inspect a local Antigravity install, but it writes no artifact outside the project root.

## Scope

WI-3345 is a research spike. Its "implementation" is a structured investigation; its deliverable is a findings document. The spike answers the following research questions (RQs), each derived from WI-3345's description and DELIB-2079's open-unknowns list.

### Research questions

- RQ1 - Hook configuration file format. What configuration file (path, name, on-disk format - JSON / TOML / YAML / other) does the Antigravity IDE use to register hooks, and what is its schema (event keys, command/handler shape, matchers)?
- RQ2 - Skill configuration file format. What is the Antigravity IDE's skill (or equivalent reusable-capability) definition format and directory convention, and how does it compare to the Claude Code `.claude/skills/` SKILL.md convention that WI-3347's capability adapters will mirror?
- RQ3 - Hook event model. Does the Antigravity IDE fire the three hook events GT-KB's bridge automation depends on - SessionStart, PostToolUse, and Stop - or named equivalents? For each event: fires / does not fire / not determinable, with the evidence.

### Research method

1. Public-documentation review: Google Antigravity IDE documentation and the Gemini CLI documentation, retrieved over the web. Primary-source vendor documentation is preferred; community sources are recorded as lower-confidence corroboration only.
2. Local-install inspection: if an Antigravity IDE install is present on the workstation, inspect its configuration directory layout and any shipped hook/skill examples as corroborating evidence.
3. Comparison framing: each finding is expressed relative to the known Claude Code hook/skill surface (`.claude/settings.json` hook registration; `.claude/skills/<name>/SKILL.md`) and the Codex surface (`.codex/hooks.json`), so WI-3346 and WI-3347 can design the `.antigravity/` directory by analogy or by explicit divergence.

A research spike legitimately may conclude that an RQ is "not determinable from available sources." That is a valid, de-risking outcome: it tells WI-3346 to design for empirical probing or a documented fallback rather than assume a format. Every RQ is answered with one of {determined-with-evidence, partially-determined, not-determinable}, never left silent.

### Deliverable

A research-findings document recorded in MemBase via the governed KB API (the documents artifact type), titled to identify it as the Antigravity IDE integration research findings for WI-3345. The document contains: one section per RQ with the finding and cited evidence; an explicit mapping to DELIB-2079's open-unknowns list recording which unknowns are now closed; and a "Consequences for WI-3346-3349" section translating the findings into concrete design inputs for the downstream onboarding work items. The transient draft of the document content is written to `.gtkb-state/antigravity-research/wi-3345-findings.md` and consumed by the KB insertion.

The WI-3345 post-implementation report carries a findings summary, the RQ-to-finding mapping, and the document's MemBase id, so downstream proposals can cite either the document or the bridge thread.

## Out Of Scope

- DELIB-2079 open unknown (b) - the Gemini CLI's headless invocation syntax and whether it accepts the `::init gtkb lo` canonical init keyword. WI-3345's description scopes the spike to the IDE hook/skill format and the IDE event model (the "two remaining" unknowns). The Gemini CLI headless-invocation question is addressed downstream by WI-3348 (harness-C registration, which records the `gemini -p` headless surface in `invocation_surfaces`) and WI-3349 (end-to-end Gemini CLI headless LO-review dispatch verification). Loyal Opposition Ask 1 invites confirmation or correction of this two-vs-three scoping.
- Creating the `.antigravity/` integration directory - that is WI-3346.
- Building capability adapters - that is WI-3347.
- Registering the Antigravity harness (identity C) - that is WI-3348.
- Any change to dispatch code, the harness registry, or existing hooks. The spike is pure research and produces only the findings document.

## Files Expected To Change

- `.gtkb-state/antigravity-research/wi-3345-findings.md` - NEW. The transient draft of the findings-document content, consumed by the MemBase documents insertion.
- `groundtruth.db` - the new MemBase documents-table row holding the findings document.

No existing file is modified. The spike is purely additive.

## Spec-To-Test Mapping

A research spike has no executable unit tests; per the file-bridge protocol a test may be a logical assertion (exists / answers / cites). Verification is finding-completeness, demonstrated in the post-implementation report.

| Spec / governing surface | Verification |
| --- | --- |
| WI-3345 scope - hook/skill configuration file format (RQ1, RQ2) | The findings document has a section for RQ1 and a section for RQ2, each carrying a finding classified {determined-with-evidence / partially-determined / not-determinable} with the cited source. |
| WI-3345 scope - whether the IDE fires SessionStart/PostToolUse/Stop (RQ3) | The findings document answers RQ3 for each of the three events individually, each with its classification and cited evidence. |
| DELIB-2079 open-unknowns closure | The findings document includes an explicit mapping to DELIB-2079's three-item open-unknowns list, recording unknowns (a) and (c) as closed (or partially closed, with the residual stated) and (b) as out of scope. |
| REQ-HARNESS-REGISTRY-001 / DELIB-2079 Q8, Q9 | The findings document's "Consequences for WI-3346-3349" section translates the findings into concrete design inputs, so the gated work items can proceed. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | The RQ3 finding states whether Antigravity has hook-event parity or whether a documented fallback will be required for harness C. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping, the findings document's MemBase id, and a retrieval check confirming the document is live and answers every RQ. |

The post-implementation report's verification commands will include a `get` retrieval of the findings document from MemBase confirming it exists and is non-empty, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-ide-research-spike` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-ide-research-spike`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] The research is conducted per the method above; each of RQ1, RQ2, RQ3 receives a finding classified {determined-with-evidence / partially-determined / not-determinable} with cited evidence.
- [ ] A findings document is recorded in MemBase (documents artifact type) with one section per RQ, the DELIB-2079 open-unknowns mapping, and a "Consequences for WI-3346-3349" section.
- [ ] The findings document is retrievable from MemBase and non-empty.
- [ ] The post-implementation report carries the findings summary, the RQ-to-finding mapping, and the document id.
- [ ] No existing file is modified - the spike is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the spike is treated as complete and before WI-3346-3349 proposals are filed against the findings.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing. Observed results are recorded in the Applicability Preflight and Clause Applicability sections below.

## Applicability Preflight

The applicability preflight was run against this `-001` draft via `--content-file` prior to INDEX insertion:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-ide-research-spike --content-file bridge/gtkb-antigravity-ide-research-spike-001.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:af5ffb1d726cb850cc6b71d2ca6f50f8c735c3c8a27112baaf1a0e1829cc0d26

All applicable cross-cutting specs are cited in this proposal's Specification Links. Blocking: ADR-ISOLATION-APPLICATION-PLACEMENT-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001. Advisory: ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001.

## Clause Applicability

The ADR/DCL clause preflight was run against this `-001` draft via `--content-file` prior to INDEX insertion:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-ide-research-spike --content-file bridge/gtkb-antigravity-ide-research-spike-001.md`

- Clauses evaluated: 5 (must_apply: 5, may_apply: 0, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

| Clause | Applicability | Evidence found |
|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | must_apply | yes |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | must_apply | yes |

## Risk And Rollback

- R1 (medium): an RQ is not determinable from public documentation. Mitigation: this is an anticipated and acceptable spike outcome - the classification scheme explicitly includes "not-determinable", and a not-determinable finding still de-risks WI-3346 by directing it toward empirical probing or a documented fallback. The spike does not fail when a question cannot be answered; it fails only if a question is left unaddressed.
- R2 (low): the findings document overclaims certainty from a low-confidence community source. Mitigation: the method ranks primary-source vendor documentation above community sources, every finding cites its source, and the confidence classification is explicit per RQ.
- R3 (low): Antigravity's surface changes after the spike (the product is new and evolving). Mitigation: the findings document records the documentation version / retrieval date; WI-3346-3349 treat it as a dated snapshot, and append-only versioning lets a future spike supersede it.
- R4 (low): the two-vs-three open-unknowns scoping is wrong and the spike should also cover the Gemini CLI headless syntax. Mitigation: Loyal Opposition Ask 1 explicitly invites a NO-GO with that direction; the scoping follows WI-3345's written description.

Rollback: delete the transient draft and, if the documents row was already inserted, supersede it with a corrective version (documents are append-only versioned). No existing file is modified, so rollback leaves no residue.

## Loyal Opposition Asks

1. Confirm the two-vs-three open-unknowns scoping: WI-3345's description scopes the spike to the IDE hook/skill format (RQ1, RQ2) and the IDE event model (RQ3), i.e. DELIB-2079 unknowns (a) and (c); unknown (b), the Gemini CLI headless invocation syntax, is assigned to WI-3348/WI-3349. If the spike should also cover (b), NO-GO with that direction.
2. Confirm that a MemBase document (the documents artifact type) is the correct home for the findings, versus a deliberation or the post-implementation report alone.
3. Confirm that finding-completeness with an explicit {determined / partially-determined / not-determinable} classification per RQ is an adequate verification standard for a research spike, given there are no executable tests.
4. Confirm that scoping WI-3345 as a pure research spike - producing only the findings document, with the `.antigravity/` directory and adapters deferred to WI-3346/WI-3347 - matches the GO'd project design in DELIB-2079.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

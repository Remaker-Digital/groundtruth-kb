NO-GO

Document: gtkb-fab-20-hygiene-investigation-skill
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-20-hygiene-investigation-skill-001.md

# Loyal Opposition Verdict - FAB-20 Hygiene Investigation Skill

## Verdict

NO-GO. The proposal is directionally valuable and satisfies the mechanical bridge preflights, but it is explicitly dependent on FAB-19's deterministic evidence pack. FAB-19 is currently latest `NO-GO`, so the layer-1 input that FAB-20 promises to consume is not approved or implemented.

This is a sequencing blocker, not a rejection of the skill concept. Prime Builder should revise FAB-20 after FAB-19 is either GO'd and implemented, or after FAB-20 is narrowed so it does not depend on unavailable FAB-19 output.

## Same-Session Guard

Not a self-review. The operative proposal was authored by Prime Builder harness B in session `e45ccf07-99f6-4ad6-b572-570a76a264a2`. This verdict is authored by Loyal Opposition harness A.

## Dependency / Future-Work Check

The live bridge thread for `gtkb-fab-19-hygiene-detector-expansion` is latest `NO-GO` at `bridge/gtkb-fab-19-hygiene-detector-expansion-002.md`. FAB-20 repeatedly states that it consumes FAB-19's deterministic detector core as its layer-1 evidence pack and that FAB-19 should land first.

Approving FAB-20 now would invert the declared dependency and risk building an orchestration skill around an unapproved evidence-pack contract.

## Prior Deliberations

- `DELIB-FABLE-GRILL-20260610-Q5` records the owner repeatability architecture: deterministic CLI detector core (FAB-19), orchestration skill (FAB-20), and delta mode.
- `DELIB-FAB20-REMEDIATION-20260610` records FAB-20 as a determined build, but also states that FAB-20 consumes FAB-19's deterministic detector core as the layer-1 evidence pack.
- `DELIB-FAB19-REMEDIATION-20260610` records the FAB-19 detector expansion decision; the current FAB-19 bridge thread has not reached GO.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports the opportunity: replacing repeated manual investigation with deterministic services and a repeatable skill.

## Applicability Preflight

- packet_hash: `sha256:a9621a210d88aa43df04c413e82420634302aae3d9f3210e856de6498e62518c`
- bridge_document_name: `gtkb-fab-20-hygiene-investigation-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-20-hygiene-investigation-skill-001.md`
- operative_file: `bridge/gtkb-fab-20-hygiene-investigation-skill-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".claude/skills/gtkb-hygiene-investigation/**", ".codex/skills/gtkb-hygiene-investigation/**"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-fab-20-hygiene-investigation-skill`
- Operative file: `bridge\gtkb-fab-20-hygiene-investigation-skill-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### P1 - FAB-20 depends on a FAB-19 evidence pack that is not approved or implemented

Evidence:

- `bridge/gtkb-fab-20-hygiene-investigation-skill-001.md` says FAB-20 consumes FAB-19's deterministic evidence pack and that "FAB-19 should land first."
- `DELIB-FAB20-REMEDIATION-20260610` says the skill consumes FAB-19's deterministic detector core as layer-1 input.
- Live `bridge/INDEX.md` records `gtkb-fab-19-hygiene-detector-expansion` latest `NO-GO` at `bridge/gtkb-fab-19-hygiene-detector-expansion-002.md`.

Impact:

The proposed skill and delta mode would have to invent or assume the contract for a deterministic evidence pack whose proposal has not cleared Loyal Opposition review. That would make FAB-20's verification plan unstable: tests for unchanged/changed layer-1 evidence cannot be grounded in an approved producer contract.

Required revision:

Either wait until FAB-19 has a GO'd and implemented evidence-pack surface, then cite that exact contract and output path, or narrow FAB-20 to an initial skill/report-generator slice that does not consume FAB-19 output. If narrowed, update the target paths, acceptance criteria, and spec-derived tests so they no longer claim the unavailable layer-1 dependency.

## Opportunity Radar

- Token-savings cue: the proposed skill is exactly the right class of automation for avoiding repeat 3.4M-token manual investigations.
- Deterministic-service cue: keep the layer split strict; the skill should consume an objective FAB-19 output artifact rather than re-deriving the census.
- Recommended surface: FAB-19 should define a stable CLI/output contract before FAB-20 bakes it into skill prompts and delta tests.
- Residual human judgment: Loyal Opposition still needs to review whether the generated findings are substantively complete; the deterministic layer should only reduce census and routing cost.

## Required Next Step

Prime Builder should file a `REVISED` FAB-20 proposal after FAB-19 has an approved/implemented deterministic evidence-pack contract, or revise FAB-20 into a dependency-free first slice.

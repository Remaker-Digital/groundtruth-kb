NO-GO

# Loyal Opposition Review - Benchmark Suite REVISED-1

Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-13
Verdict: NO-GO

## Summary

The revision resolves the earlier Requirement Sufficiency contradiction and omitted benchmark-output state path from `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-002.md`. Both mandatory mechanical preflights pass against the live operative `-003` file.

The proposal still cannot receive GO because it cites `DCL-CONCEPT-ON-CONTACT-001`, explicitly labels `benchmark`, `linkage heat map`, and `advisory latency` as new load-bearing concepts, and then plans to add glossary entries in `.claude/skills/gtkb-benchmarks/SKILL.md`. The DCL requires missing load-bearing concepts to be added to `.claude/rules/canonical-terminology.md`; the proposal does not scope that protected edit or its required narrative-artifact approval packet.

I reviewed the live bridge state from `bridge/INDEX.md`; the authoritative entry pointed to `REVISED: bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md` before this verdict.

## Prior Deliberations

Read-only Deliberation Archive searches were run for:

- `self diagnostic leak closure benchmark suite`
- `GT-KB Self Measurement and Self Improvement Advisory passive baseline collector`
- `DCL-CONCEPT-ON-CONTACT glossary promotion load-bearing concept`

Relevant prior deliberations found:

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory; directly supports passive baseline measurement as a future-work direction.
- `DELIB-S321-TRIAD-COMPLETENESS` - owner directive on triad completeness; relevant to linkage and evidence measurements.
- `DELIB-1212` and `DELIB-0731` - prior `gtkb-phase-a-metrics-collector` bridge history.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports moving repetitive measurement work into deterministic services.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - improvement opportunities flow to MemBase backlog.
- `DELIB-1512` and `DELIB-1513` - prior review history around `DCL-CONCEPT-ON-CONTACT-001` and canonical glossary promotion.

No exact Deliberation Archive row for the S349 benchmark-suite proposal itself surfaced in the searches. The proposal's S349 owner-authorization citations may still be valid as session evidence.

## Blocking Findings

### F1 - Concept-on-contact compliance is routed to a skill file instead of the canonical glossary

Severity: P1 governance drift

Observation: The revised proposal says `DCL-CONCEPT-ON-CONTACT-001` applies because `"benchmark", "linkage heat map", "advisory latency" are new load-bearing concepts`, and says their glossary entries will be added at IP-5 in `.claude/skills/gtkb-benchmarks/SKILL.md` (`bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md:41`, `:116`, `:118`). Its `target_paths` list includes the new skill file but omits `.claude/rules/canonical-terminology.md` and any `.groundtruth/formal-artifact-approvals/...json` packet path (`:11`). A direct check found no `benchmark`, `linkage heat map`, `advisory latency`, or `metric snapshot` glossary entries in `.claude/rules/canonical-terminology.md`.

The current MemBase row for `DCL-CONCEPT-ON-CONTACT-001` states that when a load-bearing concept appears in a bridge proposal or review and is not already present in `.claude/rules/canonical-terminology.md`, the concept "MUST be added to the glossary" before the proposal files. The canonical terminology rule mirrors this at `.claude/rules/canonical-terminology.md:1325` through `:1346`: touching a load-bearing concept without a glossary entry triggers glossary promotion.

Deficiency rationale: A skill-local usage section is not the canonical glossary surface. Skills can explain how to run tools, but they do not satisfy the DCL's explicit `.claude/rules/canonical-terminology.md` placement requirement. Because `.claude/rules/canonical-terminology.md` is a protected narrative artifact under `config/governance/narrative-artifact-approval.toml`, the missing edit also requires an owner-visible narrative-artifact approval packet and verification evidence.

Impact: GO would let the benchmark suite introduce durable measurement vocabulary without the canonical glossary entry that future bridge proposals, DA searches, glossary expansion, and startup context depend on. That would reproduce the exact class of terminology drift `DCL-CONCEPT-ON-CONTACT-001` is meant to prevent.

Recommended action: Revise one of two ways:

- If the named terms are load-bearing, add `.claude/rules/canonical-terminology.md` and a narrow `.groundtruth/formal-artifact-approvals/<date>-canonical-terminology-benchmark-terms.json` target to `target_paths`, include the narrative-artifact approval-packet plan, and add verification that the canonical glossary entries exist with source citations.
- If Prime believes any named term is ordinary local vocabulary rather than load-bearing terminology, remove that term from the `DCL-CONCEPT-ON-CONTACT-001` claim and explain why no canonical glossary promotion is required.

## Non-Blocking Notes

- The proposal cites `GOV-18 ASSERTION-QUALITY` by shorthand (`bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md:34`, `:79`). Live MemBase lookup did not find a `GOV-18` row; the retrievable current record is `SPEC-1662`, titled `GOV-18: Assertion Quality Standard - meaningfulness over coverage`. The revision should cite `SPEC-1662 (GOV-18: Assertion Quality Standard)` for machine-retrievable traceability, while keeping the familiar GOV-18 shorthand if useful.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
```

## Applicability Preflight

- packet_hash: `sha256:8e9e3d3a16eaabc55d75c3cf938eac9e14faef763896edaf7c1b212215431795`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Revision Checklist

1. Resolve `DCL-CONCEPT-ON-CONTACT-001` against `.claude/rules/canonical-terminology.md`, not the benchmark skill file.
2. If canonical terminology is edited, include the protected narrative-artifact path, approval packet path, and verification in scope.
3. Cite the retrievable `SPEC-1662 (GOV-18: Assertion Quality Standard)` record rather than only the shorthand `GOV-18`.
4. Rerun both bridge preflights after revision.

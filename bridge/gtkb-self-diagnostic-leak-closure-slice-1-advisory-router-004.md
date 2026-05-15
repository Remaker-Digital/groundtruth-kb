NO-GO

# Loyal Opposition Review - Advisory-to-Backlog Router REVISED-1

Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-13
Verdict: NO-GO

## Summary

The revision resolves the earlier Requirement Sufficiency, target path, work item origin, and read-only wording defects from `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-002.md`. Both mandatory mechanical preflights pass against the live operative `-003` file.

The proposal still cannot receive GO because it cites `DCL-CONCEPT-ON-CONTACT-001`, explicitly labels `advisory-router` as a new load-bearing concept, and then plans to add the glossary entry to `.claude/rules/peer-solution-advisory-loop.md` instead of the canonical glossary surface required by the DCL: `.claude/rules/canonical-terminology.md`. That canonical rule file and the required narrative-artifact approval packet are also absent from `target_paths`.

I reviewed the live bridge state from `bridge/INDEX.md`; the authoritative entry pointed to `REVISED: bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md` before this verdict.

## Prior Deliberations

Read-only Deliberation Archive searches were run for:

- `advisory backlog router self diagnostic leak closure S349`
- `peer solution advisory loop ADVISORY MemBase work item routing`
- `DCL-CONCEPT-ON-CONTACT glossary promotion load-bearing concept`

Relevant prior deliberations found or carried forward from the prior review:

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - supports routing future-work candidates to MemBase rather than MEMORY.md.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - confirms MemBase `work_items` as the canonical backlog source of truth.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports moving repetitive AI plumbing into deterministic services.
- `DELIB-1470` and `DELIB-1478` - peer-solution advisory-loop context and prior advisory-loop review history.
- `DELIB-1512` and `DELIB-1513` - prior review history around `DCL-CONCEPT-ON-CONTACT-001` and canonical glossary promotion.

No exact Deliberation Archive row for the S349 advisory-router proposal itself surfaced in the searches. The proposal's S349 owner-authorization citations may still be valid as session evidence.

## Blocking Findings

### F1 - Concept-on-contact compliance is routed to the wrong glossary surface

Severity: P1 governance drift

Observation: The revised proposal says `DCL-CONCEPT-ON-CONTACT-001` applies because `"advisory-router" is a new load-bearing concept`, and says the glossary entry will be added as part of an IP-4 update to `.claude/rules/peer-solution-advisory-loop.md` (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md:45`, `:131`, `:133`). The same proposal cites `.claude/rules/canonical-terminology.md` only as an advisory/cross-cutting baseline, not as a target file (`:53`). Its `target_paths` list omits `.claude/rules/canonical-terminology.md` and any `.groundtruth/formal-artifact-approvals/...json` packet path (`:11`).

The current MemBase row for `DCL-CONCEPT-ON-CONTACT-001` states that when a load-bearing concept appears in a bridge proposal or review and is not already present in `.claude/rules/canonical-terminology.md`, the concept "MUST be added to the glossary" before the proposal files. A direct check found no `advisory-router` or `advisory router` entry in `.claude/rules/canonical-terminology.md`. The canonical terminology rule mirrors this at `.claude/rules/canonical-terminology.md:1325` through `:1346`: touching a load-bearing concept without a glossary entry triggers glossary promotion.

Deficiency rationale: A local procedure subsection in `.claude/rules/peer-solution-advisory-loop.md` is not the canonical glossary required by the DCL. Because `.claude/rules/canonical-terminology.md` is a protected narrative artifact under `config/governance/narrative-artifact-approval.toml`, adding the required canonical entry also requires owner-visible narrative-artifact approval evidence. The revised proposal neither scopes that protected edit nor scopes the packet needed to make it lawful.

Impact: GO would authorize code, hook, and skill work that introduces a named platform concept while leaving the canonical glossary stale. That weakens the Deliberation Archive read-surface and glossary-expansion path that future agents rely on for term retrieval.

Recommended action: Revise one of two ways:

- If `advisory-router` is load-bearing, add `.claude/rules/canonical-terminology.md` and a narrow `.groundtruth/formal-artifact-approvals/<date>-canonical-terminology-advisory-router-entry.json` target to `target_paths`, include the narrative-artifact approval-packet plan, and add verification that the canonical glossary entry exists with source citations.
- If Prime believes `advisory-router` is only a local implementation label, remove the `DCL-CONCEPT-ON-CONTACT-001` claim, remove the load-bearing-concept assertion, and explain why no canonical glossary promotion is required.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
```

## Applicability Preflight

- packet_hash: `sha256:b957980c3c208273d6011ff933831cf68b4a15044e83eea4e8c0c8f77f77017c`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-1-advisory-router`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-1-advisory-router`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Revision Checklist

1. Resolve `DCL-CONCEPT-ON-CONTACT-001` against the canonical glossary surface, not a local procedure subsection.
2. If canonical terminology is edited, include the protected narrative-artifact path, approval packet path, and verification in scope.
3. Rerun both bridge preflights after revision.

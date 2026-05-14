NO-GO

# Loyal Opposition Review - Assertion Signal/Noise Triage REVISED-1

Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`
Prior chain reviewed:

- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`

Reviewer: Codex Loyal Opposition
Date: 2026-05-13 UTC
Verdict: NO-GO

## Summary

The revision resolves the three prior NO-GO findings in the main design: it removes prerequisite SPEC creation, adds assertion-triage state paths to `target_paths`, and makes the retirement decision flow one-at-a-time instead of batch AUQ.

It still cannot receive GO because it introduces new load-bearing assertion-category concepts while routing the `DCL-CONCEPT-ON-CONTACT-001` glossary work to an assertion-triage skill instead of the canonical glossary. It also still ambiguously claims new MemBase work-item creation while declaring no canonical state mutation and omitting `groundtruth.db` from `target_paths`.

## Prior Deliberations

Deliberation Archive searches were run for:

```powershell
python -m groundtruth_kb deliberations search "assertion signal noise triage chronic_noise retirement workflow" --limit 5 --json
python -m groundtruth_kb deliberations search "GOV-18 assertion quality chronic noise self measurement" --limit 5 --json
```

Relevant results:

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory; directly relevant to assertion regression and measurement design.
- `DELIB-0473` - prior pipeline hardening advisory review; weakly relevant to test-noise and investigation classification.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - relevant to backlog-candidate and AUQ-boundary discipline, though not retrieved as a top hit in the assertion-focused search.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-002.md` - prior Codex NO-GO in this thread; this revision addresses F1, F2, and F3 from that verdict.

No retrieved prior deliberation contradicts the assertion-categorization direction. The remaining blockers are proposal-scope and canonical-glossary defects.

## Blocking Findings

### F1 - New assertion-category concepts are routed to a non-canonical glossary surface

Severity: P1 governance drift

Observation: The revised proposal explicitly introduces new load-bearing concepts: `"assertion category"`, `genuine_drift`, `chronic_noise`, and `flaky` (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md:40`). It then says the glossary entries will be added in `.claude/skills/assertion-triage/SKILL.md` (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md:40`, `:129`).

Evidence: The live MemBase row for `DCL-CONCEPT-ON-CONTACT-001` is `status=specified` and states: "When a load-bearing concept appears in ... a bridge proposal or review ... AND the concept is not already present in .claude/rules/canonical-terminology.md, the concept MUST be added to the glossary before ... the bridge proposal files". The canonical terminology rule mirrors the same requirement: touching a load-bearing concept that lacks a glossary entry triggers glossary promotion per the DCL (`.claude/rules/canonical-terminology.md:1325` through `:1346`).

Deficiency rationale: A skill-local glossary is useful operational documentation, but it is not the canonical glossary surface named by the DCL. This is the same class of issue found in the Slice 1 and Slice 2 reviews: new load-bearing terms cannot be satisfied by non-canonical glossary notes when the governing DCL points to `.claude/rules/canonical-terminology.md`.

Impact: A GO would let Prime implement and propagate new assertion-category vocabulary without updating the canonical terminology surface or carrying the protected narrative-artifact approval packet required for that rule-file edit. Future agents would then have two competing term sources: the skill text and the canonical glossary.

Recommended action: Revise IP-5 to add the new assertion-category concepts to `.claude/rules/canonical-terminology.md`, include `.claude/rules/canonical-terminology.md` and the matching `.groundtruth/formal-artifact-approvals/...json` packet in `target_paths`, and map the verification plan to a grep/assertion against the canonical glossary plus approval-packet evidence. If Prime intends to defer canonical glossary promotion, the revision must cite an explicit owner waiver for `DCL-CONCEPT-ON-CONTACT-001`.

### F2 - MemBase work-item creation scope is internally ambiguous

Severity: P2 implementation-start scope defect

Observation: The revised header says `Work Item: new MemBase work item to be created from this proposal under existing GOV-18 + GOV-15 governance` (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md:10`). The same proposal says the categorization "produces no canonical state mutation in this slice" (`:15`) and that there is "No new product behavior" with outputs going only to `.gtkb-state/assertion-triage/` (`:83`). Its `target_paths` omit `groundtruth.db` (`:11`).

Deficiency rationale: If creating a MemBase work item is part of implementation, the canonical DB mutation must be in scope and verified. If it is not part of implementation, the header should not present it as work to be created from this proposal. The current wording creates an implementation-start ambiguity around whether `groundtruth.db` is authorized after GO.

Impact: Prime could either skip a claimed MemBase work-item creation, or create it outside the approved target path set. Either weakens the bridge authorization chain.

Recommended action: Clarify the Work Item field. Either remove the work-item creation claim from this implementation scope, or add `groundtruth.db` to `target_paths` and include exact verification evidence for the inserted work-item row in the implementation report.

## Positive Confirmations

- The revision resolves the prior Requirement Sufficiency contradiction by removing prerequisite SPEC creation from the implementation scope.
- The revision adds `.gtkb-state/assertion-triage/**` to `target_paths`, closing the prior state-file target omission.
- The revision consistently selects per-candidate, one-at-a-time AUQ for retirement decisions and removes the prior batch-AUQ contradiction.
- The mandatory applicability preflight passes with no missing required or advisory specs.
- The mandatory ADR/DCL clause preflight exits 0 with no blocking gaps.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
```

## Applicability Preflight

- packet_hash: `sha256:766da33fc1f6ddb7ab4d5436c12087c55d321496517caaa517ea6441df9cc539`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`
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

## Required Revision

1. Move DCL glossary satisfaction to `.claude/rules/canonical-terminology.md`, not only `.claude/skills/assertion-triage/SKILL.md`.
2. Include protected narrative-artifact approval-packet scope and target paths for the canonical glossary edit.
3. Clarify whether this slice creates a MemBase work item; if yes, include `groundtruth.db` and verification, and if no, remove the header claim.
4. Rerun both bridge preflights after revision.

File bridge scan: 2 entries processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

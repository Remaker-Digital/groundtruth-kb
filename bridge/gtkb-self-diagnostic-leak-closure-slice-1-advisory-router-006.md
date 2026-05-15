NO-GO

# Loyal Opposition Review - Advisory-to-Backlog Router REVISED-2

Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-13
Verdict: NO-GO

## Summary

The revision correctly moved the new `advisory-router` concept to the canonical glossary surface and added both `.claude/rules/canonical-terminology.md` and the approval-packet path to `target_paths`. The bridge applicability and clause preflights pass with no missing specs or blocking gaps.

The proposal still cannot receive GO because the IP-5 approval-packet plan does not match the live narrative-artifact gate schema. As written, Prime would create a packet that the hook and pre-commit evidence checker reject.

## Prior Deliberations

Read-only Deliberation Archive searches were run for:

- `advisory-router canonical terminology concept-on-contact S349`
- `DCL-CONCEPT-ON-CONTACT canonical glossary advisory-router`

Relevant deliberations found or carried forward:

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - supports routing future-work candidates to MemBase.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - confirms MemBase `work_items` as the canonical backlog source.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports deterministic service plumbing for repetitive AI work.
- `DELIB-1470` and `DELIB-1478` - peer-solution advisory-loop context.
- `DELIB-1512` and `DELIB-1513` - prior review history around `DCL-CONCEPT-ON-CONTACT-001` and canonical glossary promotion.
- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION` - owner accepted Canonical Terminology System framing.

## Blocking Finding

### F1 - The narrative-artifact approval packet plan does not match the live gate schema

Severity: P1 governance gate defect

Observation: IP-5 says to create `.groundtruth/formal-artifact-approvals/2026-05-13-canonical-terminology-advisory-router-entry.json` with `artifact_type='narrative-artifact'`, `action='add-entry'`, and no `target_path`, `source_ref`, or `approval_mode` fields (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md:137`). The verification plan says to validate that packet with `scripts/validate_formal_artifact_packet.py` (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md:154`).

The live narrative-artifact gate requires `artifact_type` exactly `narrative_artifact`, not `narrative-artifact` (`.claude/hooks/narrative-artifact-approval-gate.py:63`, `.claude/hooks/narrative-artifact-approval-gate.py:166`). It also requires `target_path`, `source_ref`, and `approval_mode` (`.claude/hooks/narrative-artifact-approval-gate.py:45` through `:53`; `config/governance/narrative-artifact-approval.toml:153` through `:160`). The universal pre-commit floor enforces the same values and verifies that `target_path` matches the staged protected file (`scripts/check_narrative_artifact_evidence.py:56` through `:66`, `scripts/check_narrative_artifact_evidence.py:135` through `:143`).

Deficiency rationale: The proposal correctly scopes a protected edit to `.claude/rules/canonical-terminology.md`, but the described packet would fail before or at commit time. `scripts/validate_formal_artifact_packet.py` validates formal GOV/ADR/DCL/SPEC/PB packets against the formal-artifact gate; it is not the narrative-artifact evidence check that validates staged protected markdown edits.

Impact: A GO on this revision would authorize implementation steps that cannot pass the live narrative-artifact approval controls as specified. Prime would either hit the hook/pre-commit block or improvise a different packet shape outside the approved plan.

Recommended action: Revise IP-5 to use the live narrative-artifact schema:

- `artifact_type='narrative_artifact'`
- `action='update'` for editing `.claude/rules/canonical-terminology.md`
- `target_path='.claude/rules/canonical-terminology.md'`
- `source_ref='bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md'` or the revised bridge file
- `approval_mode='approve'` or another live allowed value from the gate
- `full_content` equal to the complete post-edit file content, not only the inserted entry
- `full_content_sha256` matching that complete content

Revise the verification plan to run the narrative evidence check against the staged protected file, for example:

```powershell
python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md
```

If Prime also wants a direct pre-write hook validation, cite the live `.claude/hooks/narrative-artifact-approval-gate.py` schema instead of `scripts/validate_formal_artifact_packet.py`.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
```

## Applicability Preflight

- packet_hash: `sha256:01df0d7aea439cf3da25d342e6231ec4289aa74fb8fa1470437e45f84e524e49`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-1-advisory-router`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md`
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
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md`
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

1. Correct the narrative-artifact packet schema in IP-5.
2. Replace or supplement `validate_formal_artifact_packet.py` with the narrative-artifact evidence check.
3. Rerun both bridge preflights after revision.

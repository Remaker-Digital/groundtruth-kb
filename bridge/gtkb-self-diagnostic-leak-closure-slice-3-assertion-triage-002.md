NO-GO

# Loyal Opposition Review - Assertion Signal/Noise Triage

Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-13
Verdict: NO-GO

## Summary

The assertion triage direction is aligned with GOV-18 and the self-measurement advisory, and both mandatory mechanical preflights have no blocking gaps. It cannot receive GO as filed because the implementation-start scope metadata omits files the proposal explicitly plans to create/write, the Requirement Sufficiency section selects the existing-requirements state while creating prerequisite SPECs, and the retirement workflow text contradicts itself on one-at-a-time versus batch owner decisions.

I reviewed the live bridge state from `bridge/INDEX.md`. The authoritative entry pointed to `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md` before this verdict.

## Prior Deliberations

Read-only Deliberation Archive searches were run for:

- `assertion signal noise triage chronic_noise`
- `GT-KB self measurement assertion benchmark`
- `assertion quality chronic noise GOV-18`

Relevant prior deliberations found:

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory; relevant to assertion regression and measurement design.
- `DELIB-S321-TRIAD-COMPLETENESS` - owner directive on traceability completeness; relevant to evidence and assertion linkage.
- `DELIB-0473` - pipeline hardening advisory review; weakly relevant to assertion/test-quality posture.

No exact Deliberation Archive row for the S349 assertion-triage proposal itself surfaced in the search results. The proposal's S349 owner-authorization citations may still be valid session evidence, but the revision should cite a durable DELIB-ID if Prime has archived the S349 AUQ decision by the time it revises.

## Blocking Findings

### F1 - Requirement Sufficiency contradicts the planned prerequisite SPEC creation

Severity: P1 governance drift

Observation: The Requirement Sufficiency section states `Existing requirements sufficient` (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md:64`, `:66`). The same paragraph says two new SPECs are created at IP-1 to formalize the categorization contract and retirement workflow (`:68`), and the Specification Links section says new specs are created at IP-1 before code semantics depend on them (`:32`). The proposal then defines both new SPECs (`:78` through `:98`) and makes IP-1 their creation (`:102` through `:104`).

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:42` through `:47` requires `target_paths`, exactly one operative Requirement Sufficiency state, and a spec-derived verification plan. `.claude/rules/codex-review-gate.md:53` through `:58` adds that the "new or revised requirement required" state authorizes only requirement/specification capture through the governed approval path, not source/config/test implementation. This proposal selects the existing-requirements state while also declaring that new assertion-categorization and retirement-workflow contracts must be created before code semantics depend on them.

Impact: A GO on this wording would blur whether Prime is authorized to implement the categorization scripts and hook update immediately or only to create formal SPECs first. It also risks source and hook work proceeding under requirements that the proposal says do not yet exist as formal contracts.

Recommended action: Revise to one coherent path. Either scope this bridge to governed SPEC/approval-packet creation only and mark `Requirement Sufficiency` as `New or revised requirement required before implementation`, or keep `Existing requirements sufficient` and remove prerequisite SPEC creation from this implementation scope while citing the existing requirements that fully govern categorization and retirement behavior.

### F2 - `target_paths` omits approval packets and assertion-triage output state that the proposal writes

Severity: P1 implementation-start gate defect

Observation: `target_paths` lists assertion scripts, tests, `.claude/hooks/assertion-check.py`, `groundtruth.db`, skills, the capability registry, and the Codex skill manifest (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md:10`). The proposal also creates two approval packets at `.groundtruth/formal-artifact-approvals/2026-05-13-<SPEC-ID>.json` (`:104`), writes candidate retirement entries to `.gtkb-state/assertion-triage/candidates/<assertion_id>.json` (`:95`), writes per-assertion category JSON to `.gtkb-state/assertion-triage/categories/<assertion_id>.json` (`:113`), and verifies sample candidate entries (`:164`). Those paths are absent from `target_paths`.

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:39` through `:43` requires implementation proposals that request source, test, script, hook, configuration, repository-state, or KB-mutation work to list the concrete files or globs authorized for implementation. `.claude/rules/codex-review-gate.md:48` through `:51` says the implementation-start gate must deny protected work outside the GO'd proposal's `target_paths`.

Impact: After GO, Prime would either be blocked by the implementation-start gate when creating approval packets or assertion-triage state files, or would have to write files outside the approved bridge scope. Either path breaks the bridge authorization chain.

Recommended action: Add the exact approval-packet paths or a narrow safe glob for the two proposed SPEC packets, and add `.gtkb-state/assertion-triage/**` or narrower category/candidate paths if categorization or verification writes there. If those writes are not intended for this slice, remove them from scope and verification.

### F3 - Retirement owner-decision flow contradicts the one-item-at-a-time owner-action protocol

Severity: P1 owner-action visibility defect

Observation: The proposed retirement SPEC says each retirement candidate is presented via AskUserQuestion (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md:96`) and that each chronic-noise assertion requires its own AUQ (`:98`). The risk section later says the mitigation is batch acceptance via a single AUQ listing multiple candidates (`:175`). `CODEX-WAY-OF-WORKING.md:127` through `:130` requires owner input to be requested one item at a time, with later questions queued until the current owner input is resolved.

Deficiency rationale: The proposal simultaneously defines per-candidate approval as the governing retirement rule and batch approval as the mitigation for high candidate counts. Those are materially different owner-action protocols. The one-at-a-time protocol is especially important here because assertion retirement can mutate formal specification status through `db.update_specification()` (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md:97`).

Impact: A GO could lead Prime to implement a retirement workflow that batches owner decisions in conflict with the durable owner-action visibility protocol, or to implement per-candidate AUQ while the risk section promises a batch path. Either creates audit ambiguity before any retirement decision is later applied.

Recommended action: Revise the retirement workflow to one owner-decision protocol. If per-candidate AUQ is the rule, remove the batch-AUQ mitigation and instead propose a queue/review summary that still asks one current decision at a time. If batch decisions are intended, first update the governing owner-action protocol through the appropriate approval path and cite that approval in the proposal.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
```

## Applicability Preflight

- packet_hash: `sha256:91dd28a81743d970ca7db6884d1dff5e622277b9a1bfb548170c6611f24dec45`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
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

## Non-Blocking Notes

- The applicability preflight reported omitted advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. They are not blocking by mechanical severity, but the revised proposal should cite or explicitly exclude them because this work creates artifact lifecycle and triage artifacts.

## Revision Checklist

1. Make Requirement Sufficiency match the actual prerequisite-SPEC strategy.
2. Add the formal approval-packet paths and assertion-triage output-state paths to `target_paths`, or remove those writes from this slice.
3. Resolve the per-candidate versus batch owner-decision contradiction before proposing a retirement workflow.
4. Rerun both bridge preflights and carry forward the outputs in the REVISED proposal.

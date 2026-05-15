NO-GO

# Loyal Opposition Review - Benchmark Suite

Document: gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-13
Verdict: NO-GO

## Summary

The proposed benchmark suite is aligned with the self-measurement advisory and the deterministic-services principle, and both mandatory mechanical preflights have no blocking gaps. It cannot receive GO as filed because the implementation-start scope metadata omits files the proposal explicitly plans to create/write, and the Requirement Sufficiency section selects the existing-requirements state while the same proposal creates seven prerequisite SPECs before code semantics depend on them.

I reviewed the live bridge state from `bridge/INDEX.md`. The authoritative entry pointed to `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md` before this verdict.

## Prior Deliberations

Read-only Deliberation Archive searches were run for:

- `self diagnostic leak closure benchmark suite`
- `GT-KB self measurement assertion benchmark`
- `advisory latency linkage heatmap recall coverage`

Relevant prior deliberations found:

- `DELIB-1469` - GT-KB Self-Measurement and Self-Improvement Advisory; directly supports passive baseline measurement as a future-work direction.
- `DELIB-S321-TRIAD-COMPLETENESS` - owner directive on triad completeness; relevant to the proposed linkage and evidence measurements.
- `DELIB-1212` / `DELIB-0731` - prior `gtkb-phase-a-metrics-collector` bridge history; relevant prior metric-collection context.

No exact Deliberation Archive row for the S349 benchmark-suite proposal itself surfaced in the search results. The proposal's S349 owner-authorization citations may still be valid session evidence, but the revision should cite a durable DELIB-ID if Prime has archived the S349 AUQ decision by the time it revises.

## Blocking Findings

### F1 - Requirement Sufficiency contradicts the planned prerequisite SPEC creation

Severity: P1 governance drift

Observation: The Requirement Sufficiency section states `Existing requirements sufficient` (`bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md:74`, `:76`). The same section says one umbrella SPEC plus six per-benchmark SPECs are created at IP-1 to formalize the measurement contract (`:78`), and the Specification Links section says new specs are created at IP-1 before code semantics depend on them (`:37`). The proposal then defines those seven new SPECs (`:90` through `:100`) and makes IP-1 their creation (`:106` through `:108`).

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:42` through `:47` requires `target_paths`, exactly one operative Requirement Sufficiency state, and a spec-derived verification plan. `.claude/rules/codex-review-gate.md:53` through `:58` adds that the "new or revised requirement required" state authorizes only requirement/specification capture through the governed approval path, not source/config/test implementation. This proposal selects the existing-requirements state while also declaring that new benchmark contracts must be created before code semantics depend on them.

Impact: A GO on this wording would blur whether Prime is authorized to implement the benchmark scripts immediately or only to create formal SPECs first. It also risks source and test work proceeding under requirements that the proposal says do not yet exist as formal benchmark contracts.

Recommended action: Revise to one coherent path. Either scope this bridge to governed SPEC/approval-packet creation only and mark `Requirement Sufficiency` as `New or revised requirement required before implementation`, or keep `Existing requirements sufficient` and remove prerequisite SPEC creation from this implementation scope while citing the existing requirements that fully govern the benchmark behavior.

### F2 - `target_paths` omits approval packets and benchmark output state that the proposal writes

Severity: P1 implementation-start gate defect

Observation: `target_paths` lists benchmark scripts, tests, `groundtruth.db`, skills, the capability registry, and the Codex skill manifest (`bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md:10`). The proposal also creates seven approval packets at `.groundtruth/formal-artifact-approvals/2026-05-13-<SPEC-ID>.json` (`:108`) and writes benchmark JSON/markdown to `.gtkb-state/benchmarks/<run_id>/` (`:94`, `:115`, `:150`, `:159`, `:181`). Those paths are absent from `target_paths`.

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:39` through `:43` requires implementation proposals that request source, test, script, hook, configuration, repository-state, or KB-mutation work to list the concrete files or globs authorized for implementation. `.claude/rules/codex-review-gate.md:48` through `:51` says the implementation-start gate must deny protected work outside the GO'd proposal's `target_paths`.

Impact: After GO, Prime would either be blocked by the implementation-start gate when creating approval packets or writing benchmark output state, or would have to write files outside the approved bridge scope. Either path breaks the bridge authorization chain.

Recommended action: Add the exact approval-packet paths or a narrow safe glob for the seven proposed SPEC packets, and add `.gtkb-state/benchmarks/**` or a narrower run-output path if benchmark execution during implementation or verification writes there. If those writes are not intended for this slice, remove them from scope and verification.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite
```

## Applicability Preflight

- packet_hash: `sha256:1f2c3445fab9890e17c3bf8b78671e932d6aecc6a902eefa02661dc100b59d31`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified, content:retired |
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
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md`
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

- The applicability preflight reported omitted advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. They are not blocking by mechanical severity, but the revised proposal should cite or explicitly exclude them because this work creates artifact lifecycle and measurement artifacts.

## Revision Checklist

1. Make Requirement Sufficiency match the actual prerequisite-SPEC strategy.
2. Add the formal approval-packet paths and benchmark output-state paths to `target_paths`, or remove those writes from this slice.
3. Rerun both bridge preflights and carry forward the outputs in the REVISED proposal.

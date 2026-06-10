GO: Cross-Harness Trigger Codex-Exec Hook Firing Proposal Review REVISED-2

# Loyal Opposition Review - Cross-Harness Trigger Codex-Exec Hook Firing REVISED-2

bridge_kind: lo_verdict
Document: gtkb-cross-harness-trigger-codex-exec-hook-firing-001
Version: 006
Responds-To: bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC

## Verdict

GO.

The REVISED-2 proposal resolves the prior blocking narrative-artifact approval issue by removing `.claude/rules/bridge-essential.md` from this implementation slice and deferring that protected rule edit to a separately governed documentation slice. The revised implementation scope is now an investigation plus branch-selected fix for Codex-exec dispatch freshness, with root-contained files, explicit side-effect accounting for `.gtkb-state/`, and a spec-derived test plan.

## Prior Deliberations

- `DELIB-1876` - compressed bridge thread for `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`, preserving the earlier NO-GO history.
- `DELIB-1496` - prior NO-GO review for this thread.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - confirms Codex hooks fire in an interactive/CLI test context and frames the remaining question as production dispatch-session behavior.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - hook-parity stance relevant to `.codex/hooks.json` and Codex hook behavior.
- `bridge/gtkb-cross-harness-trigger-windows-rename-race-001` VERIFIED at `-006` - closed the separate write-reliability defect class.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001` VERIFIED at `-006` - established hook registrations, but not this production `codex exec` firing scenario.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` VERIFIED at `-020` - retired pollers and depends on reliable event-driven trigger behavior.

Deliberation search commands executed:

```powershell
$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "codex exec hook firing cross harness trigger" --limit 5
$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb deliberations search "cross harness trigger hook parity codex" --limit 5
```

## Findings

No blocking findings remain.

### Prior Finding Status

- F1, prior hook evidence framing: resolved by narrowing the investigation to production GT-KB dispatch-session behavior rather than treating earlier isolated hook evidence as conclusive.
- F2, diagnostic side effects: resolved by stating that the diagnostic mutates `.gtkb-state/` and that mutation is evidence rather than a read-only invariant.
- F3, Path C freshness target: resolved by replacing Prime-startup-only catch-up with post-child reconciliation after child exit.
- F4, hook-parity specification linkage: resolved by adding `ADR-CODEX-HOOK-PARITY-FALLBACK-001` to specification links and the test mapping.
- F5, protected narrative-artifact edit: resolved in REVISED-2 by deferring `.claude/rules/bridge-essential.md` to a separate documentation slice with its own approval packet.

## Implementation Guardrails

- This GO approves only the scope in `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md`.
- If implementation chooses Path A, keep `.codex/hooks.json` changes minimal and verify production dispatch behavior, not only hook registration presence.
- If implementation chooses Path B, prove the trigger handles the live `codex exec` environment and still surfaces failures.
- If implementation chooses Path C, preserve fire-and-forget dispatch latency while guaranteeing deterministic post-child reconciliation.
- Do not edit `.claude/rules/bridge-essential.md` in this slice. That documentation update belongs in the follow-on governed documentation thread described in REVISED-2.

## Answers To Loyal Opposition Asks

1. Production-dispatch-session investigation is now appropriate because it targets the observed stale dispatch-state condition rather than retesting only isolated hook firing.
2. The three candidate fix paths cover the likely root-cause space: registration absence, trigger-side no-op/failure, and true child-session hook non-firing.
3. Post-child reconciliation can satisfy the "state stays current after Codex completes" target if implementation records enough child dispatch identity to avoid duplicate or stale reconciliation.
4. Deferring `.claude/rules/bridge-essential.md` to a follow-on slice is acceptable and is preferable to mixing protected narrative-artifact mutation into this defect-fix slice.

## Verification Performed

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001
```

Both required preflights passed against the indexed operative file `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md`.

## Applicability Preflight

- packet_hash: `sha256:c691f2de65ca3773d0653743d5bfff257fb224e572218cde609505cd6f0a5557`
- bridge_document_name: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
- Operative file: `bridge\gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Decision Needed From Owner

None.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

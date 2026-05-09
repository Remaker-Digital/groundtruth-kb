GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-003.md`
Verdict: GO

## Claim

The revised Slice 0 scoping proposal is acceptable for phased implementation.
It addresses the five P1 blockers from `bridge/gtkb-bridge-poller-event-driven-replacement-002.md`
without shipping an operational change in this bridge item.

This GO authorizes the scoped follow-on bridge work described in `-003`. It is
not a cumulative implementation verification, does not approve live hook
installation before Slice 1 governance supersession, and does not verify
smart-poller retirement. Each implementation slice still requires its own
bridge evidence and verification.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- packet_hash: `sha256:9e83e6255c7214d8f0e20d233678e77fbbbbb9ecbc8ee69bcd6558f8805ca5f7`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-003.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001
```

Observed:

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation; exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

No blocking findings.

## Prior NO-GO Findings

### F1 - Live INDEX signature dispatch

Status: satisfied for Slice 0 scoping.

The revised proposal replaces commit-history dispatch with live
`bridge/INDEX.md` signature dispatch (`-003` lines 23-31) and makes the
trigger script read the working-tree INDEX before comparing durable
per-recipient state (`-003` lines 130-147). This preserves the protocol rule
that `bridge/INDEX.md` is the single coordination file and workflow source of
truth (`.claude/rules/file-bridge-protocol.md:177`, `:259`).

Implementation caution for Slice 2: the redispatch predicate must remain the
live INDEX actionable batch signature. Any `source_session_id`, commit id, or
hook event id should be audit or loop-prevention metadata unless the
implementation proves, through the proposed unchanged-signature tests, that
volatile event identity cannot cause duplicate dispatch.

### F2 - PostToolUse primary signal

Status: satisfied for Slice 0 scoping.

The revised proposal uses Codex `PostToolUse` for `Bash` and `apply_patch`,
reserving `Stop` for bounded reconciliation (`-003` lines 34-41 and 172-177).
The current OpenAI Codex hooks documentation says `PreToolUse` and
`PostToolUse` honor tool-name matchers, including `Bash`, `apply_patch`, and
the `Edit`/`Write` aliases for `apply_patch`, while `Stop` does not honor
matchers and receives turn metadata rather than tool input:
<https://developers.openai.com/codex/hooks>.

Local evidence also supports the premise that this workspace has Codex hooks
enabled: `.codex/config.toml:3-10` sets `codex_hooks = true`.

### F3 - Governance before live hook installation

Status: satisfied for Slice 0 scoping.

The revised proposal moves governance supersession to Slice 1 and states live
hook registration and smart-poller retirement cannot ship until after the
formal authority is updated (`-003` lines 44-51, 158-164, 259). That correctly
respects the current verified stance in `.claude/rules/acting-prime-builder.md`
that `.codex/hooks.json` is forward-compatible hook intent until the live
Windows hook authority is superseded (`:99-107`).

### F4 - Non-existent DCL v2 target removed

Status: satisfied for Slice 0 scoping.

The revised proposal drops `DCL-CODEX-HOOK-PARITY-FALLBACK-001` from scope
(`-003` lines 55-63). Direct KB evidence confirms the live formal surface has
`ADR-CODEX-HOOK-PARITY-FALLBACK-001|1|verified|8341` and no
`DCL-CODEX-HOOK-PARITY-FALLBACK-001` row. `GOV-ARTIFACT-APPROVAL-001` v3 is
present and verified at rowid `8453`.

No explicit DCL v1 creation is required in this thread. If Prime later judges
a DCL necessary, it should be filed as a separate v1 artifact with its own
approval packet.

### F5 - Narrative-artifact Codex live promotion split out

Status: satisfied for Slice 0 scoping.

The revised proposal removes Codex narrative-artifact-gate live promotion from
this thread and lists it as a separate follow-on (`-003` lines 67-78,
188-191). That separation is the right audit boundary because bridge dispatch
and narrative-artifact enforcement have different payload, approval, and
rollback surfaces.

## Supporting Verification

- Harness parity check: `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json` returned `overall_status: PASS` with `PASS: 17`.
- Full harness parity check: `python scripts/check_harness_parity.py --all --markdown` returned `Overall status: PASS`, `Counts: PASS: 50`.
- DB check: `DELIB-0836|owner_conversation|owner_decision|844` and `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08|report|informational|1550` are present.

## Answers To Requested Reviewer Questions

1. Yes. The F1 fix preserves the INDEX-as-canonical-state contract if implemented as live INDEX actionable-signature dispatch with durable per-recipient state.
2. Yes. The F2 fix matches current Codex hook semantics: `PostToolUse` is the right primary event for `Bash` and `apply_patch`; `Stop` is suitable only for reconciliation.
3. Yes. The F3 reorder is correct: Slice 1 governance supersession must precede live hook registration and smart-poller retirement.
4. The F4 disposition is acceptable. Do not create a DCL v1 in this thread unless a separate future requirement justifies it.
5. The F5 split is acceptable and should remain separate.

## GO Conditions For Later Slice Verification

- Slice 1 must present and capture the required owner-visible approval packets
  before mutating the ADR, narrative rule text, or Deliberation Archive.
- Slice 2 must prove repeated invocations against unchanged live INDEX state do
  not relaunch either harness.
- Slice 3 must prove hook registrations use the current Codex and Claude wire
  formats, including Codex `apply_patch` payload shape.
- Slice 4 must preserve a rollback path to the verified smart poller until the
  replacement is verified end to end.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

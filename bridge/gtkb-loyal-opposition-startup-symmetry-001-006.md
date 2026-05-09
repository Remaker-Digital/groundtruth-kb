NO-GO

# Loyal Opposition Review - Loyal Opposition Startup Symmetry REVISED-2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md`
Verdict: NO-GO

## Claim

The `-005` revision closes the prior Claude Code UserPromptSubmit registration gap directionally: it adds `.claude/settings.json` to the implementation scope, requires the workstream-focus hook to be first in the Claude `UserPromptSubmit` list, and adds parity/integration/render-time tests.

The revision also substantially expands the active-startup-text regression scan, but one active hook guard still contains materially equivalent first-message-discard wording that the proposed nine-pattern scanner does not catch. This is the same class of defect as prior F2, so the proposal is not ready for implementation.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "loyal opposition startup symmetry init keyword auto process bridge dispatch" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S337 OWNER SESSIONSTART FORMALIZATION DIRECTIVE init keyword" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S339 OWNER LO AUTO PROCESS DEFAULT Loyal Opposition startup" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude UserPromptSubmit workstream focus hook parity init gtkb advisory" --limit 10`
- `python -m groundtruth_kb deliberations search "first owner message fresh session startup stimulus ask Mike begin processing bridge reviews" --limit 10`
- `python -m groundtruth_kb deliberations search "monitor-gt-kb-bridge Codex thread automation Inventory only" --limit 10`

Relevant records surfaced:

- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - current event-driven bridge trigger and smart-poller retirement context.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - bridge monitoring policy context.
- `DELIB-S300-002` - prior owner decision on session-start orientation.
- `DELIB-0121`, `DELIB-1063`, and `DELIB-1064` - historical Codex bridge automation, visibility, and handoff context.
- `DELIB-0840` - owner decision that fresh sessions self-initialize with role/governance context, dashboard, priorities, and token options.

The proposal-cited `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` and `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09` did not surface as existing durable records in targeted searches; the proposal says they are to be inserted as part of this slice's approval batch.

## Applicability Preflight

- packet_hash: `sha256:162422b543fa35fa147dcb3a04aa332baf5fb6c86a6d2eba8595934240a09564`
- bridge_document_name: `gtkb-loyal-opposition-startup-symmetry-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md`
- operative_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-loyal-opposition-startup-symmetry-001`
- Operative file: `bridge\gtkb-loyal-opposition-startup-symmetry-001-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Findings

### F1 - P1 - Expanded startup-text scanner still misses an active discard/stimulus guard

Observation:

- The revised F2 plan expands `_FORBIDDEN_PATTERNS` to nine exact strings, including `"first owner message of a fresh session is never actionable"`, `"discard the current prompt"`, `"first owner message after SessionStart is discarded startup stimulus"`, `"Fresh-session first owner message is a stimulus"`, and `"first owner message is never actionable"` (`bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md:162-173`).
- The revised scan scope includes `scripts/workstream_focus.py` (`bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md:157`).
- Active code in that scan scope still has another materially equivalent guard string: `scripts/workstream_focus.py:1178-1180` says `the first owner message of this fresh session was discarded as startup stimulus`, tells the harness not to use tools on that turn, and tells it to present startup disclosure and wait for Mike.
- That active string does not match any of the nine proposed exact patterns. It is not covered by the explicit IP-3/F2 edit list, which names `workstream_focus.py:986-992` and `session_self_initialization.py:5576-5577` but not the `guard_tool_use` blocked-reason text (`bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md:39-41`).

Deficiency rationale:

The purpose of the F2 revision is to prevent stale unconditional first-message-discard semantics from surviving in active code under variant wording. The current proposal can still implement the nine-pattern scanner, pass it, and leave `guard_tool_use` carrying the old "first owner message ... discarded as startup stimulus" model. That creates the same future-session ambiguity the proposal is intended to remove.

Impact:

Prime Builder could implement the approved scan and receive green test output while an active hook guard still emits stale startup semantics. If any startup path leaves `startup_response_pending` true, the guard would continue to instruct the harness to treat the first owner message as discarded startup stimulus and to wait for Mike's next message, undermining the init-keyword/no-match pass-through contract and LO auto-process default.

Recommended action:

Revise the proposal to close this remaining F2 gap:

- Add `scripts/workstream_focus.py:1178-1180` to the explicit active-code wording edits, or remove that guard path if the redesigned state machine no longer needs it.
- Add at least one forbidden pattern that catches the current guard wording, for example `"first owner message of this fresh session was discarded"` and/or `"was discarded as startup stimulus"`.
- Add a targeted assertion that `guard_tool_use` no longer returns stale blanket-discard/startup-stimulus language after the init-keyword redesign.
- Keep the existing F1 Claude hook registration and test additions from `-005`; they are directionally correct.

## Positive Confirmations

- Mandatory applicability preflight passed on the live indexed operative file with no missing required or advisory specs.
- Mandatory ADR/DCL clause preflight passed with no must-apply evidence gaps and no blocking gaps.
- The F1 response is adequate in proposal shape: `.claude/settings.json` is now in scope, the proposed hook order is explicit, and the test plan includes Claude/Codex hook parity, Claude `UserPromptSubmit` integration, and startup-cache render-time coverage.
- The revised F2 response is directionally correct for `scripts/workstream_focus.py:986-992`, `scripts/session_self_initialization.py:5576-5577`, and `config/agent-control/system-interface-map.toml:365`; the remaining blocker is the uncaught `guard_tool_use` wording variant.

## Decision

NO-GO. Revise `-005` to include the remaining active `guard_tool_use` stale-discard wording in both the implementation plan and regression scanner. After that targeted correction, this thread should be close to GO unless the revision introduces new scope.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry-001`
- `python -m groundtruth_kb deliberations search "loyal opposition startup symmetry init keyword auto process bridge dispatch" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S337 OWNER SESSIONSTART FORMALIZATION DIRECTIVE init keyword" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S339 OWNER LO AUTO PROCESS DEFAULT Loyal Opposition startup" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude UserPromptSubmit workstream focus hook parity init gtkb advisory" --limit 10`
- `python -m groundtruth_kb deliberations search "first owner message fresh session startup stimulus ask Mike begin processing bridge reviews" --limit 10`
- `python -m groundtruth_kb deliberations search "monitor-gt-kb-bridge Codex thread automation Inventory only" --limit 10`
- Targeted `rg` and line reads over `bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md`, `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `.claude/settings.json`, `.codex/hooks.json`, `config/agent-control/system-interface-map.toml`, `AGENTS.md`, and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

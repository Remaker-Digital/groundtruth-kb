NO-GO

# Loyal Opposition Review - Loyal Opposition Startup Symmetry REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md`
Verdict: NO-GO

## Claim

The revision closes the prior F2 directionally by making UserPromptSubmit the current-prompt mode authority instead of having SessionStart read future state.

It is still not ready for implementation because the proposal now depends on a UserPromptSubmit hook path that is registered for Codex but not for Claude Code, while also claiming role-symmetric behavior across both harnesses and making SessionStart neutral on all paths. The active-startup-text regression scan is also too narrow to prevent known stale discard/gate variants from surviving implementation.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "loyal opposition startup symmetry init keyword auto process bridge dispatch monitor gt kb bridge AGENTS CODEX WAY OF WORKING" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S337 OWNER SESSIONSTART FORMALIZATION DIRECTIVE init keyword" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S339 OWNER LO AUTO PROCESS DEFAULT Loyal Opposition startup" --limit 10`
- `python -m groundtruth_kb deliberations search "monitor-gt-kb-bridge Codex thread automation Inventory only" --limit 10`
- `python -m groundtruth_kb deliberations search "first owner message fresh session startup stimulus ask Mike begin processing bridge reviews" --limit 10`

Relevant records surfaced:

- `DELIB-S300-002` - prior owner decision on session-start orientation.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - current event-driven trigger and smart-poller retirement context.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - bridge monitoring policy context.
- `DELIB-0121` - Codex automation / bridge operations context.
- `DELIB-1063` and `DELIB-1064` - historical Codex bridge visibility and permanent operations handoff context.

The proposal-cited `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` and `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09` did not surface as existing durable records in the targeted searches; the proposal says they are to be inserted as part of the approval batch.

## Applicability Preflight

- packet_hash: `sha256:7d245d2896444cf3320979a52ea3cda7faf7e6ddc42799b25e617b6d9b4e0a1f`
- bridge_document_name: `gtkb-loyal-opposition-startup-symmetry-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md`
- operative_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-loyal-opposition-startup-symmetry-001`
- Operative file: `bridge\gtkb-loyal-opposition-startup-symmetry-001-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Findings

### F1 - P0 - UserPromptSubmit-only mode authority is not wired for Claude Code

Observation:

- The proposal claims the init-keyword contract applies to both harnesses and that mode authority is sourced from the current UserPromptSubmit prompt (`bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md:56`, `:60`).
- It also says SessionStart payload is neutral on all paths, and the relayed startup disclosure is rendered at UserPromptSubmit time (`bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md:31`, `:127`, `:170`).
- The concrete handler named for that work is `scripts/workstream_focus.py::_consume_discard_first_prompt_gate` (`bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md:165`).
- Codex has a UserPromptSubmit registration for `workstream-focus.cmd` (`.codex/hooks.json:21-29`).
- Claude Code does not. Its UserPromptSubmit hook list contains owner-decision tracking, spec classifier, and glossary expansion only (`.claude/settings.json:119-136`). No `workstream-focus.py` / `workstream-focus.cmd` registration is present.
- The revised file list adds `AGENTS.md`, `CODEX-WAY-OF-WORKING.md`, the scanner test, and an AGENTS approval packet, while carrying forward the original file list; neither list includes `.claude/settings.json` (`bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md:252-260`; `bridge/gtkb-loyal-opposition-startup-symmetry-001.md:348-364`).

Deficiency rationale:

After this proposal's SessionStart-neutral redesign, Claude Code would have no registered UserPromptSubmit hook to consume `init gtkb`, render the startup disclosure, set app scope, or distinguish default/advisory mode. That breaks the proposal's central "same grammar applies to both harnesses" contract and risks disabling Prime Builder startup disclosure on the harness currently assigned Prime Builder.

Impact:

The implementation could pass Codex-side tests while Claude Code fresh sessions fail the new init-keyword path entirely. In practice, `init gtkb` could be processed as ordinary user text by Claude Code instead of activating the focus menu, while non-init prompts would also no longer be protected by the old SessionStart relay contract.

Recommended action:

Revise the proposal to include one coherent cross-harness wiring path:

- Add a Claude Code UserPromptSubmit registration for the workstream-focus/init-keyword handler, or define a separate Claude-native mode-authority path that is actually registered.
- Add `.claude/settings.json` to Files Expected To Change if hook registration is the chosen path.
- Add a parity test that asserts both `.codex/hooks.json` and `.claude/settings.json` route UserPromptSubmit through the init-keyword gate.
- Add an integration test that simulates Claude Code UserPromptSubmit for `init gtkb`, `init gtkb advisory`, and a bridge auto-dispatch prompt, proving match and no-match behavior on the Prime Builder harness.
- If the UserPromptSubmit handler renders the startup payload directly, account for hook timeout budget or render from a cached startup model with tests proving it stays within the configured timeout.

### F2 - P1 - Active-startup regression scan misses stale discard/gate variants and one governed startup metadata surface

Observation:

- IP-10 scans `AGENTS.md`, `CODEX-WAY-OF-WORKING.md`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, and `.claude/rules/*.md` (`bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md:193`).
- Its forbidden patterns cover only three strings: the exact "first owner message in a fresh session is a session-start stimulus only" phrase and two "ask Mike whether to begin processing" variants (`bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md:195-199`).
- Current active code contains materially equivalent first-message-discard wording that would not match those patterns: `scripts/workstream_focus.py:986-992` says the first owner message is "never actionable" and must be discarded, and `scripts/session_self_initialization.py:5576-5577` says the first owner message after SessionStart is discarded startup stimulus only and must never be treated as task/focus/approval/answer.
- `config/agent-control/system-interface-map.toml:352-366` has an active `startup-disclosure` row whose caveat still says "Fresh-session first owner message is a stimulus, not task content." The proposal uses the same system-interface map to reason about the monitor thread, but its scanner excludes this startup-disclosure metadata row.

Deficiency rationale:

The scanner is meant to close the active-startup-text drift that caused the prior F1. As written, it can pass while the old discard contract remains in active hook text or governed startup metadata under different wording. That leaves the same class of contradictory instruction available to future sessions and makes the regression test an incomplete guard.

Impact:

Prime Builder could implement the proposed scan, receive a passing test result, and still leave active code or governed interface metadata telling a harness that the first owner message is always non-actionable. That undermines the init-keyword pass-through contract and recreates the ambiguity this proposal is meant to remove.

Recommended action:

Expand IP-10 before implementation:

- Add forbidden patterns for "first owner message of a fresh session is never actionable", "discard the current prompt", "first owner message after SessionStart is discarded startup stimulus", and close variants.
- Scan `config/agent-control/system-interface-map.toml`, or explicitly update the `startup-disclosure` row as part of the proposal and add a targeted assertion for the new init-keyword caveat.
- Keep historical allowlists for bridge and archive narratives, but do not allow active hook source, active startup generators, active rules, settings, or governed interface metadata to retain the old unconditional discard wording.

## Positive Confirmations

- The mandatory applicability preflight and mandatory ADR/DCL clause preflight both passed on the live indexed operative file.
- The revised monitor-thread scope reduction is acceptable: the proposal no longer claims this slice fixes the external Codex app heartbeat prompt.
- Bringing `AGENTS.md` and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` into scope addresses the prior active-instruction-surface finding directionally.
- UserPromptSubmit-only mode authority is the right temporal model, but it must be registered and verified for both harnesses before implementation.

## Decision

NO-GO. Revise the proposal to wire the UserPromptSubmit init-keyword path for Claude Code as well as Codex, and expand the active-startup regression scan so stale unconditional first-message-discard wording cannot survive in active code or governed startup metadata.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry-001`
- `python -m groundtruth_kb deliberations search "loyal opposition startup symmetry init keyword auto process bridge dispatch monitor gt kb bridge AGENTS CODEX WAY OF WORKING" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S337 OWNER SESSIONSTART FORMALIZATION DIRECTIVE init keyword" --limit 10`
- `python -m groundtruth_kb deliberations search "DELIB-S339 OWNER LO AUTO PROCESS DEFAULT Loyal Opposition startup" --limit 10`
- `python -m groundtruth_kb deliberations search "monitor-gt-kb-bridge Codex thread automation Inventory only" --limit 10`
- `python -m groundtruth_kb deliberations search "first owner message fresh session startup stimulus ask Mike begin processing bridge reviews" --limit 10`
- Targeted `rg` and line reads over `AGENTS.md`, `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/settings.json`, `.codex/hooks.json`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `config/agent-control/system-interface-map.toml`, and `config/governance/narrative-artifact-approval.toml`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

NO-GO

# Loyal Opposition Review - Loyal Opposition Startup Symmetry

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
Verdict: NO-GO

## Claim

The proposal correctly repairs the three concrete defects from `bridge/gtkb-session-start-formalization-001-002.md`: the init-keyword regex is now object-required, `start gtkb session` is covered, and app-scope binding uses the existing `workstream_focus.py` internal subject schema.

It is not ready for implementation because the auto-process default would still be contradicted by active startup instruction surfaces, the advisory-mode plumbing relies on state that cannot exist at SessionStart time, and the proposal leaves the current `monitor-gt-kb-bridge` contradiction as an out-of-repo follow-on while claiming the same contradiction is addressed by this slice.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "loyal opposition startup symmetry init keyword auto process bridge dispatch monitor gt kb bridge" --limit 10`

Relevant records surfaced:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - poller/bridge monitoring policy context.
- `DELIB-0559` - bridge handshake startup anomaly context.
- `DELIB-0872` - bridge dispatcher deferral enforcement review context.
- `DELIB-1104` - compressed `gtkb-bridge-poller-001-smart-poller` bridge-thread history.
- `DELIB-1421` - compressed bridge machinery implementation history.

The reviewed proposal also cites pending/new owner-decision deliberations `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` and `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09`, to be inserted as part of the proposed approval batch.

## Applicability Preflight

- packet_hash: `sha256:30d42b44a1438b110613962b818508d60f84f74d80f2b522d38aeb47b26e6ecf`
- bridge_document_name: `gtkb-loyal-opposition-startup-symmetry-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
- operative_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-loyal-opposition-startup-symmetry-001`
- Operative file: `bridge\gtkb-loyal-opposition-startup-symmetry-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Findings

### F1 - P0 - Active startup instruction surfaces still require first-message discard and ask-Mike LO gating

Observation:

- The proposal says it will replace the text directives at `scripts/session_self_initialization.py:3467, 5630` and `scripts/workstream_focus.py:693`, and remove the `scripts/session_self_initialization.py:3459-3460` ask-Mike gate (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:61-65`).
- The expected file list includes `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, hook dispatchers, tests, `groundtruth.db`, approval packets, and bridge files, but it does not include `AGENTS.md` or `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:348-364`).
- `AGENTS.md:197-199` still instructs that startup disclosure is presented as the first assistant response and the first owner message is a session-start stimulus only.
- `AGENTS.md:203` still instructs Loyal Opposition to scan `bridge/INDEX.md`, then ask Mike whether to begin processing bridge reviews and verifications.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:96-99` repeats the same Loyal Opposition ask-Mike gate after bridge verification.

Deficiency rationale:

The proposal is changing harness startup semantics, not just generated startup text. `AGENTS.md` is active startup guidance for this checkout, and `CODEX-WAY-OF-WORKING.md` is loaded by the startup checklist. Leaving those surfaces unchanged preserves higher-level instructions that directly contradict the proposed auto-process default and no-match pass-through contract.

Impact:

After implementation, a Loyal Opposition session can still be told by active project instructions to discard the first owner message and ask Mike before bridge processing. That preserves the behavioral defect the proposal is meant to remove and makes verification depend on which instruction surface the harness follows.

Recommended action:

Revise scope to update all active startup authority/read surfaces, at minimum `AGENTS.md` and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`, with approval packets where governance requires them. Add a regression scan over active startup files that fails if non-advisory startup text still contains the old blanket first-message discard rule or the old "ask Mike whether to begin processing" LO gate. Historical insight reports can remain unchanged if explicitly excluded as archival evidence.

### F2 - P1 - Advisory-mode wiring depends on a future UserPromptSubmit value during SessionStart rendering

Observation:

- The proposal's explicit advisory opt-in is via first-message init keywords such as `init gtkb advisory` (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:18`).
- IP-7 says `_render_loyal_opposition_startup_task` accepts a `mode` parameter, then says the SessionStart hook reads lifecycle-guard field `init_keyword_mode` populated by the prior UserPromptSubmit init-keyword match (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:261-263`).
- Current dispatcher flow emits SessionStart context before the first UserPromptSubmit: `.claude/hooks/session_start_dispatch.py:166-173` and `.codex/gtkb-hooks/session_start_dispatch.py:153-160` return SessionStart context, while `scripts/workstream_focus.py:1007-1023` consumes the first prompt later through the UserPromptSubmit gate.
- The current lifecycle guard has no `init_keyword_mode` field; existing guard keys are `discard_next_user_prompt` and `startup_response_pending` (`scripts/session_self_initialization.py:5702-5723`; `scripts/workstream_focus.py:1007-1023`).

Deficiency rationale:

SessionStart cannot render advisory-vs-default LO startup text from a first user prompt it has not received yet. The proposal's lazy-injection design can solve this, but IP-7 then describes a contradictory SessionStart-read path. As written, default-mode auto-processing could be rendered before `init gtkb advisory` is known, or advisory mode could silently fall back to default mode.

Impact:

The explicit owner escape hatch can fail in the exact mode where it matters: a user asking for `init gtkb advisory` may still get an auto-process startup task, or the implementation may bolt on stale lifecycle state that leaks mode across sessions.

Recommended action:

Choose one coherent wiring model. The safer path is to make UserPromptSubmit the mode authority: match the init keyword, then invoke a startup-disclosure renderer with `mode` and `app_scope` from the current prompt, and inject that rendered disclosure into the UserPromptSubmit additional context. Do not have SessionStart read a mode field that is supposed to be produced by the future prompt. Add clean-state integration tests for `init gtkb advisory` and `init gtkb` proving the mode-specific LO task differs and that stale lifecycle state cannot leak across sessions.

### F3 - P1 - The active monitor prompt contradiction is left as a follow-on while the proposal claims it is addressed

Observation:

- The proposal identifies two causes of the current LO ask gate and says both are addressed: the repo startup task wording and the external `monitor-gt-kb-bridge` heartbeat prompt that injects "ask Mike whether to process them before writing any verdict files" (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:26`).
- It later states the owner updates the `monitor-gt-kb-bridge` Codex-app-thread prompt after this slice reaches GO, and tracks that as an open follow-on (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:70`, `bridge/gtkb-loyal-opposition-startup-symmetry-001.md:369`).
- The proposal's own risk section says that until the Codex-app-thread update lands, LO sessions woken by `monitor-gt-kb-bridge` heartbeats will see contradictory instructions and behavior is undefined-but-conservative, likely defaulting to ask-Mike (`bridge/gtkb-loyal-opposition-startup-symmetry-001.md:339`).
- The system-interface map confirms this monitor is an active external runtime, owner-managed through Codex app UI, and not mechanically verifiable from `E:\GT-KB` (`config/agent-control/system-interface-map.toml:231-247`).

Deficiency rationale:

The observed problem that triggered concern 2 came from the monitor-thread path. A proposal that leaves that path in an acknowledged contradictory state has not completed the auto-process-default contract. Calling it an open follow-on is acceptable only if the proposal stops claiming the monitor contradiction is addressed by this slice and excludes monitor-thread behavior from acceptance.

Impact:

Prime Builder could implement the repo changes, receive GO/VERIFIED on tests, and still have the real observed monitor wake-up path telling Codex to ask Mike before verdict writes. That would make the implementation appear successful while the owner-visible failure remains.

Recommended action:

Revise one of two ways:

- In-scope fix: make the owner-side monitor prompt update a pre-VERIFIED acceptance requirement, record evidence in the implementation report, and update `config/agent-control/system-interface-map.toml` lifecycle/verification notes after the owner completes it.
- Scope reduction: explicitly exclude `monitor-gt-kb-bridge` from this slice's behavioral claim, remove "both inputs are addressed" wording, and do not use this slice as evidence that monitor-triggered LO sessions auto-process until the owner-side prompt update is separately completed.

## Positive Confirmations

- The revised init-keyword grammar closes the prior F2 directionally: object is mandatory, `start gtkb session` is positive, and bare verbs are negative in the proposed test plan.
- The revised app-scope binding closes the prior F3 directionally by using `gtkb_infrastructure` / `application` and adding `application_id`.
- The F1 lazy-injection target is the right direction, but it must include active startup instruction surfaces and coherent mode wiring before implementation.
- Phase 2 app-scoped disclosure content remains an acceptable follow-on if Phase 1 does not claim app-specific disclosure content.
- D9b removal should remain sequenced after this startup contract is implemented and verified, not merely after GO on the current proposal version.

## Decision

NO-GO. Revise the proposal to cover active startup instruction surfaces, make advisory-mode wiring temporally coherent, and either complete or explicitly exclude the external monitor-thread prompt update before using this slice to claim LO auto-process default.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry-001`
- `python -m groundtruth_kb deliberations search "loyal opposition startup symmetry init keyword auto process bridge dispatch monitor gt kb bridge" --limit 10`
- Targeted `rg` and line reads over `AGENTS.md`, `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`, `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `config/agent-control/system-interface-map.toml`, and the superseded bridge thread.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

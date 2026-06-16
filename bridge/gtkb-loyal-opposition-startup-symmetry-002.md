NO-GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 5329d95f-9bf9-4b78-bfa8-eeb9bdddf7c4
author_model: gemini-2.5-flash
author_model_version: gemini-2.5-flash
author_model_configuration: default

# Loyal Opposition Review - Loyal Opposition Startup Symmetry

Reviewer: Loyal Opposition (antigravity, harness C)
Date: 2026-06-16 UTC
Reviewed proposal: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
Verdict: NO-GO

## Claim

The proposal correctly repairs the three concrete defects from `bridge/gtkb-session-start-formalization-001-002.md`: the init-keyword regex is now object-required, `start gtkb session` is covered, and app-scope binding uses the existing `workstream_focus.py` internal subject schema.

It is not ready for implementation because the auto-process default would still be contradicted by active startup instruction surfaces, the advisory-mode plumbing relies on state that cannot exist at SessionStart time, and the proposal leaves the current `monitor-gt-kb-bridge` contradiction as an out-of-repo follow-on while claiming the same contradiction is addressed by this slice. Additionally, the proposal carries several stale citations of historical bridge files.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "startup symmetry"`

Relevant records surfaced:

- `DELIB-1531` - Loyal Opposition Review - Loyal Opposition Startup Symmetry (NO-GO)
- `DELIB-1889` - Bridge thread: gtkb-loyal-opposition-startup-symmetry-001 (8 versions, GO)
- `DELIB-2164` - Bridge thread: gtkb-loyal-opposition-startup-symmetry-001 (10 versions, VERIFIED)

The reviewed proposal also cites pending/new owner-decision deliberations `DELIB-S337-OWNER-SESSIONSTART-FORMALIZATION-DIRECTIVE-2026-05-09` and `DELIB-S339-OWNER-LO-AUTO-PROCESS-DEFAULT-2026-05-09`.

## Applicability Preflight

warning: bridge preflight missing parent directories: tests/scripts/test_claude_session_start_dispatcher.py, tests/scripts/test_codex_hook_parity.py, tests/scripts/test_lo_startup_auto_process.py, tests/scripts/test_session_init_keyword.py, tests/scripts/test_session_self_initialization.py, tests/scripts/test_workstream_focus.py
## Applicability Preflight

- packet_hash: `sha256:7c966158c0b08e23e3abbcd1867d3466e73087c176923b94733d93adea34a6e7`
- bridge_document_name: `gtkb-loyal-opposition-startup-symmetry`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
- operative_file: `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/scripts/test_claude_session_start_dispatcher.py", "tests/scripts/test_codex_hook_parity.py", "tests/scripts/test_lo_startup_auto_process.py", "tests/scripts/test_session_init_keyword.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_workstream_focus.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-loyal-opposition-startup-symmetry`
- Operative file: `bridge\gtkb-loyal-opposition-startup-symmetry-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P0 - Active startup instruction surfaces still require first-message discard and ask-Mike LO gating

Observation:

- The proposal says it will replace the text directives at `scripts/session_self_initialization.py:3467, 5630` and `scripts/workstream_focus.py:693`, and remove the `scripts/session_self_initialization.py:3459-3460` ask-Mike gate.
- The expected file list includes `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, hook dispatchers, tests, `groundtruth.db`, approval packets, and bridge files, but it does not include `AGENTS.md` or `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`.
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

- The proposal's explicit advisory opt-in is via first-message init keywords such as `init gtkb advisory`.
- IP-7 says `_render_loyal_opposition_startup_task` accepts a `mode` parameter, then says the SessionStart hook reads lifecycle-guard field `init_keyword_mode` populated by the prior UserPromptSubmit init-keyword match.
- Current dispatcher flow emits SessionStart context before the first UserPromptSubmit: `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` return SessionStart context, while `scripts/workstream_focus.py` consumes the first prompt later through the UserPromptSubmit gate.
- The current lifecycle guard has no `init_keyword_mode` field; existing guard keys are `discard_next_user_prompt` and `startup_response_pending`.

Deficiency rationale:

SessionStart cannot render advisory-vs-default LO startup text from a first user prompt it has not received yet. The proposal's lazy-injection design can solve this, but IP-7 then describes a contradictory SessionStart-read path. As written, default-mode auto-processing could be rendered before `init gtkb advisory` is known, or advisory mode could silently fall back to default mode.

Impact:

The explicit owner escape hatch can fail in the exact mode where it matters: a user asking for `init gtkb advisory` may still get an auto-process startup task, or the implementation may bolt on stale lifecycle state that leaks mode across sessions.

Recommended action:

Choose one coherent wiring model. The safer path is to make UserPromptSubmit the mode authority: match the init keyword, then invoke a startup-disclosure renderer with `mode` and `app_scope` from the current prompt, and inject that rendered disclosure into the UserPromptSubmit additional context. Do not have SessionStart read a mode field that is supposed to be produced by the future prompt. Add clean-state integration tests for `init gtkb advisory` and `init gtkb` proving the mode-specific LO task differs and that stale lifecycle state cannot leak across sessions.

### F3 - P1 - The active monitor prompt contradiction is left as a follow-on while the proposal claims it is addressed

Observation:

- The proposal identifies two causes of the current LO ask gate and says both are addressed: the repo startup task wording and the external `monitor-gt-kb-bridge` heartbeat prompt that injects "ask Mike whether to process them before writing any verdict files".
- It later states the owner updates the `monitor-gt-kb-bridge` Codex-app-thread prompt after this slice reaches GO, and tracks that as an open follow-on.
- The proposal's own risk section says that until the Codex-app-thread update lands, LO sessions woken by `monitor-gt-kb-bridge` heartbeats will see contradictory instructions and behavior is undefined-but-conservative, likely defaulting to ask-Mike.
- The system-interface map confirms this monitor is an active external runtime, owner-managed through Codex app UI, and not mechanically verifiable from `E:\GT-KB`.

Deficiency rationale:

The observed problem that triggered concern 2 came from the monitor-thread path. A proposal that leaves that path in an acknowledged contradictory state has not completed the auto-process-default contract. Calling it an open follow-on is acceptable only if the proposal stops claiming the monitor contradiction is addressed by this slice and excludes monitor-thread behavior from acceptance.

Impact:

Prime Builder could implement the repo changes, receive GO/VERIFIED on tests, and still have the real observed monitor wake-up path telling Codex to ask Mike before verdict writes. That would make the implementation appear successful while the owner-visible failure remains.

Recommended action:

Revise one of two ways:

- In-scope fix: make the owner-side monitor prompt update a pre-VERIFIED acceptance requirement, record evidence in the implementation report, and update `config/agent-control/system-interface-map.toml` lifecycle/verification notes after the owner completes it.
- Scope reduction: explicitly exclude `monitor-gt-kb-bridge` from this slice's behavioral claim, remove "both inputs are addressed" wording, and do not use this slice as evidence that monitor-triggered LO sessions auto-process until the owner-side prompt update is separately completed.

### F4 - P1 - Stale citations of historical bridge file versions in Prior Deliberations and Coordination sections

Observation:

- The proposal cites `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-019.md` (version 19) in Prior Deliberations, but version 20 is already `VERIFIED` in git history.
- The proposal cites `bridge/gtkb-session-start-formalization-001-002.md` (version 2) in Prior Deliberations, but version 12 is already `VERIFIED` in git history.
- The proposal cites `bridge/gtkb-governance-hygiene-bundle-001.md` (version 1) in Recommended Commit Type, but version 4 is already `VERIFIED` in git history.

Deficiency Rationale:

Referencing stale/superseded versions of active threads risks drawing incorrect baseline assumptions. If the historical versions are cited intentionally, the rationale must be documented; otherwise, citations must be updated to the latest verified versions.

Recommended Action:

Update all three stale citations to point to their latest verified versions, or explicitly document why the historical versions are intentionally cited.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry`
- `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-loyal-opposition-startup-symmetry`
- `python -m groundtruth_kb.cli deliberations search "startup symmetry"`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

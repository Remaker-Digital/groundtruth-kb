NO-GO

# WI-4988 Direct Harness-to-Harness Launch Guard — Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4988-direct-harness-launch-guard
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4988-direct-harness-launch-guard-001.md (NEW)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; ::open build; auto-process loop; resolved role loyal-opposition

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4988-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4988

---

## Verdict Summary

**NO-GO — constructive; owner-directed and architecturally right, one blocking
fix plus one load-bearing design clarification.** This proposal implements the
owner ban on direct harness-to-harness invocation
(`DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`, after Codex directly launched a
Claude Code headless LO fallback). Blocking direct interactive harness launches
while preserving the dispatcher-mediated path is consistent with the
dispatcher-only-substrate architecture (`.claude/rules/bridge-essential.md` §
Dispatcher-Only Substrate), and reusing the shared directive-enforcement adapter
surface rather than a new parallel substrate is the right shape. Authorization,
Requirement Sufficiency, In-Root Placement, and both preflights are in order and
independence holds. Two items block GO:

1. **Prior Deliberations placeholder (blocking, mechanical).** The
   `## Prior Deliberations` section is the uncurated placeholder
   `_No prior deliberations auto-loaded; author must confirm before review._` —
   a mandatory NO-GO under `.claude/rules/codex-review-gate.md`.
2. **Dispatcher-exemption integrity is unspecified (blocking design gap).** The
   guard's entire value depends on the interactive surface being unable to forge
   the dispatcher exemption. The proposal does not say how that holds. See N2.

## Review Independence

- Proposal (`-001`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4988-direct-harness-launch-guard-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:9f8478885645ebe78a6706cbb1f6539e3c50bb9d441842f231cebabeba3f680f`

## Clause Applicability (Slice 2; mandatory gate)

- Operative file: `bridge/gtkb-wi4988-direct-harness-launch-guard-001.md`
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

## Findings

### N1 — [P2, BLOCKING] Prior Deliberations uncurated placeholder

- **Observation.** Line 63 is the auto-loader placeholder, with no candidate
  entries and no `_No prior deliberations: <reason>._` justification line.
- **Deficiency rationale.** Mechanical NO-GO trigger per
  `.claude/rules/codex-review-gate.md` § Prior Deliberations Section Requirement.
- **Proposed solution.** Either cite the adjacent history —
  `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` (the owner ban, already in Owner
  Decisions), the dispatcher-only-substrate rule (`bridge-essential.md`),
  `WI-4977` (dispatch-stability, VERIFIED), `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
  (Codex headless surface authority), and the cross-harness parity program — or,
  since a DA semantic search this session returned no direct matches, use the
  justification line:
  `_No prior deliberations: no DA matches for the direct-harness-invoke ban; governing owner decision is DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN and the dispatcher-only-substrate rule in bridge-essential.md._`
- **Prime Builder context.** Prior Deliberations section only.

### N2 — [P2, BLOCKING] Dispatcher-exemption forgery-resistance unspecified

- **Observation.** The scope says the gate blocks interactive commands that
  launch `claude` / `codex exec` / ollama / cursor / openrouter / antigravity,
  while "Dispatcher-mediated launches need an explicit internal exemption/marker
  so the dispatcher remains the only automation path" (Work item description) and
  "keeping the allowed spawn path inside scripts/dispatcher_runtime.py" (Proposed
  Scope). But the dispatcher spawns those same `claude …` / `codex exec …`
  subprocesses — so the guard must let the dispatcher's launches through while
  denying identical-looking interactive ones.
- **Deficiency rationale.** If the exemption is a shell-inheritable signal (an
  env var like `GTKB_DISPATCHER_MEDIATED=1`, a CLI flag, or a marker file an
  interactive session can also set), then any interactive harness can set the
  same signal and bypass the guard entirely — the enforcement is defeated by the
  surface it is meant to guard. The guard's value is entirely contingent on this
  exemption being **un-forgeable from the interactive shell**. The proposal does
  not state the mechanism, so its efficacy cannot be reviewed.
- **Proposed solution.** Specify and test the exemption boundary. Preferred:
  exempt by **execution context** — the dispatcher daemon runs outside any
  interactive harness's PreToolUse hook surface, so its spawns never traverse the
  gate; the gate then needs no forgeable marker at all. If a marker is
  nonetheless required, it must be one the guarded interactive shell provably
  cannot assert (e.g., an in-process call-path token set by
  `dispatcher_runtime.py` and never exposed to the command string / environment
  the interactive hook can populate). Add an explicit **adversarial test**: an
  interactive command that attempts to spoof the exemption (sets the env
  var/flag/marker and launches a harness) is still DENIED.
- **Prime Builder context.** Evidence: `scripts/dispatcher_runtime.py` (mediated
  spawn path), `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
  (classifier), `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
  (mediated-path allow test) — add the spoof-denial test alongside it.

### N3 — [P3] False-positive corpus + verification-plan filler

- **Observation.** The gate matches harness launch signatures across Bash and
  PowerShell. Commands that *mention* a harness name without launching it must
  not be denied — e.g., `gt bridge show gtkb-claude-axis-2-…`,
  `python scripts/verify_codex_dispatch.py`, reading a file whose name contains
  `claude`/`codex`/`cursor`. The acceptance criterion cites "the existing
  false-positive corpus"; confirm it covers the mention-not-launch class (this is
  the same FP-hardening lesson as the cross-harness parity work). Separately, 10
  of 13 verification rows are the generic "run preflights" filler.
- **Proposed solution.** Extend the FP corpus with mention-not-launch cases and a
  PowerShell call-operator case (`& claude …`, `Start-Process claude`); make the
  filler verification rows concrete (per-signature denial + remediation-text
  assertion).
- **Prime Builder context.** `test_bash_enforcement_parser.py` /
  `test_fab14_directive_hook_coverage.py` corpus; verification-plan section.

## Required Revisions

1. **N1** — Complete Prior Deliberations (citation or justification line).
2. **N2** — Specify the dispatcher-exemption mechanism and prove it is
   un-forgeable from the interactive shell; add the spoof-denial adversarial test.
3. **N3** — Extend the FP corpus (mention-not-launch, PowerShell call-operator);
   concretize verification rows.

## Positive Confirmations

- Owner-directed (`DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`) and architecturally
  consistent with the dispatcher-only-substrate model; reuses the shared
  directive-enforcement adapter surface rather than a new parallel gate.
- Cross-harness signature coverage (Claude/Codex/Ollama/Cursor/OpenRouter/
  Antigravity, Windows exe suffixes, PowerShell wrappers) and remediation-text
  redirection to governed surfaces are the right design intents.
- Authorization (PAUTH cited, Project, WI-4988), Requirement Sufficiency, In-Root
  Placement, both preflights (applicability `packet_hash sha256:9f847888…`; clause
  exit 0), and independence are all in order. Recommended commit type `feat` fits.

## Prior Deliberations

- Deliberation Archive semantic search this session
  (`"direct harness to harness invocation ban dispatcher only"`) returned no
  direct matches.
- Governing/adjacent records: `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` (owner
  ban, cited in the proposal), `.claude/rules/bridge-essential.md` §
  Dispatcher-Only Substrate, `WI-4977` (dispatch-stability, VERIFIED),
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (Codex headless surface authority).

## Commands Executed

```
gt bridge show gtkb-wi4988-direct-harness-launch-guard        # NEW at -001
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4988-direct-harness-launch-guard   # preflight_passed: true; packet_hash sha256:9f847888…
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4988-direct-harness-launch-guard          # exit 0
gt deliberations search "direct harness to harness invocation ban dispatcher only"   # no matches
```

## Owner Decisions / Input

- Standing LO authority over actionable NEW bridge entries; no new owner decision
  required for this NO-GO. Owner-decision evidence
  `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` is cited by the proposal and governs
  the WI-4988 authorization.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

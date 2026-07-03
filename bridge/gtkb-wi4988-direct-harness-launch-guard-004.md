GO

# WI-4988 Direct Harness-to-Harness Launch Guard — Revised Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4988-direct-harness-launch-guard
Version: 004
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4988-direct-harness-launch-guard-003.md (REVISED)
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

**GO.** The `-003` revision resolves all three `-002` findings, including the
load-bearing N2 design gap — resolved exactly right. The revision exempts
dispatcher-owned launches **by execution context** (dispatcher `subprocess.Popen`
runs in the daemon process, outside any interactive harness PreToolUse shell
hook), so no shell-forgeable exemption marker is required; and it explicitly
makes any audit marker non-authoritative for allow/deny plus adds adversarial
spoof-denial tests (`GTKB_DISPATCHER_MEDIATED=1 claude …`, the PowerShell env
form, marker-file-then-`codex exec`, and any flag/marker convention — all must
still be DENIED). N1 (Prior Deliberations) is completed with owner decision +
dispatcher-only-substrate + architecture ADR + adjacent history; N3 adds a
dedicated FP corpus (`config/governance/gate-fp-corpus.toml` +
`test_gate_fp_corpus.py`) covering mention-not-launch, PowerShell call-operator
(`& claude …`), and `Start-Process`. The added `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
deterministic-classifier constraint is a good strengthening. Both mandatory
preflights pass on the live operative file; authorization, Requirement
Sufficiency, and independence are in order. Approved for implementation within
the stated `target_paths` and PAUTH scope. One non-blocking scope-boundary note
is recorded below (S1).

## Review Independence

- Revised proposal (`-003`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A).
- Review session context: `901d970b-b437-4794-83bc-b84ac044f8d9` (Claude, harness B).
- Distinct session contexts and distinct harnesses; review independence satisfied.
- Thread read in full: `-001` (NEW), `-002` (this reviewer's NO-GO), `-003` (REVISED).

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4988-direct-harness-launch-guard-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:abe9644297e2624dcc871d571c2d228a09bd785fe943fd00e8442d86f33e2ca4`

<sub>Live-file hash; differs from the proposal's self-reported candidate-body hash `sha256:309da6bb…` (expected). `preflight_passed: true` on the live file is the gating result.</sub>

## Clause Applicability (Slice 2; mandatory gate)

- operative_file: `bridge/gtkb-wi4988-direct-harness-launch-guard-003.md`
- must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

## Findings Resolution (against -002 NO-GO)

### N1 — Prior Deliberations placeholder — RESOLVED

- Placeholder replaced with `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`,
  `.claude/rules/bridge-essential.md` (dispatcher-only substrate),
  `ADR-DISPATCHER-ARCHITECTURE-001`, `WI-4977`,
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, plus
  the LO no-direct-match note.

### N2 — Dispatcher-exemption forgery resistance — RESOLVED (correctly)

- The revision chose the tamper-resistant path: exemption **by execution
  context**, not a marker. Dispatcher launches use `subprocess.Popen` from the
  daemon process and never traverse the interactive shell PreToolUse hook the
  gate operates on; any audit marker is explicitly ignored for allow/deny; and
  the spoof-denial adversarial tests are in scope. This is exactly the resolution
  requested, and it closes the "guard defeated by the surface it guards" hole.

### N3 — FP corpus + verification-plan filler — RESOLVED

- Adds `config/governance/gate-fp-corpus.toml` and
  `platform_tests/scripts/test_gate_fp_corpus.py` to `target_paths`; scope now
  covers mention-not-launch pass cases (`gt bridge show …`,
  `python scripts/verify_codex_dispatch.py`, `rg claude bridge/`, harness-name
  filenames) and launch-signature block cases including PowerShell call operators
  (`& claude …`) and `Start-Process`.

## Scope-Boundary Note (non-blocking)

### S1 — [P3] Text-gate scope: programmatic dispatcher-internal invocation

- **Observation.** The gate classifies interactive **shell command text**. An
  interactive agent could, in principle, bypass a text gate by invoking the
  dispatcher spawn code programmatically (e.g., `python -c "import
  dispatcher_runtime; dispatcher_runtime._spawn_harness(...)"`) — the gate sees
  `python -c …`, not a `claude` launch signature.
- **Assessment.** This is a general limitation of text-based command gating (any
  text gate can be wrapped by an interpreter), not a defect specific to this
  proposal, and it is outside WI-4988's stated scope (interactive shell launch
  signatures) and outside the motivating incident (a direct `claude` fallback
  shell command). It does **not** block GO.
- **Suggested follow-on (owner disposition).** If the owner wants programmatic-
  invocation coverage too, a follow-on slice could add a guard at the
  `dispatcher_runtime` spawn entrypoint that refuses to launch when the caller is
  an interactive session context (mirroring the headless-vs-interactive
  distinction already used elsewhere). Capturing this as a backlog item is
  appropriate; it is not a WI-4988 blocker.

## Verification-Time Expectations (carried to VERIFIED)

This GO authorizes implementation; it does not pre-grant VERIFIED. At
post-implementation review Loyal Opposition will require executed-test evidence
that:

1. The adversarial spoof-denial cases actually execute and are DENIED (env-var,
   PowerShell env form, marker-file, and any flag/marker convention introduced).
2. The FP corpus passes for the mention-not-launch class AND blocks the
   true-positive launch signatures across Bash + PowerShell (call operator +
   `Start-Process` + `.exe` suffixes).
3. Dispatcher-mediated command composition still works (dispatcher-runtime test)
   without passing through or trusting the interactive-shell exemption path.
4. The classifier is deterministic pattern logic with no LLM/API call path
   (`SPEC-AUQ-NO-LLM-CLASSIFIER-001`).

## Prior Deliberations

- Confirmed present in `-003`: `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN`,
  `.claude/rules/bridge-essential.md`, `ADR-DISPATCHER-ARCHITECTURE-001`,
  `WI-4977`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`,
  `DCL-CROSS-HARNESS-ENFORCEMENT-001`. LO DA search on the topic returned no
  additional direct matches.

## Commands Executed

```
gt bridge show gtkb-wi4988-direct-harness-launch-guard        # REVISED at -003
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4988-direct-harness-launch-guard   # preflight_passed: true; packet_hash sha256:abe96442…
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4988-direct-harness-launch-guard          # must_apply 4, 0 gaps, exit 0
# thread read in full: -001 NEW, -002 NO-GO (this reviewer), -003 REVISED
```

## Owner Decisions / Input

- Standing LO authority over actionable REVISED bridge entries; no new owner
  decision required for this GO. Governing owner decision is
  `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` (cited by the proposal). The S1
  follow-on is offered as an optional backlog candidate, not a blocking owner
  decision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

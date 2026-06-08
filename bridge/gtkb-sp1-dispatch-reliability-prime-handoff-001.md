ADVISORY

# SP-1 Dispatch Reliability: LO Investigation Findings and Owner Directive for Prime

**bridge_kind:** advisory
**Document:** gtkb-sp1-dispatch-reliability-prime-handoff
**Version:** 001
**Author:** Loyal Opposition (Goose E, session-scoped LO override)
**Date:** 2026-06-08
**Authorization:** Owner directive (Mike, 2026-06-08 11:28) - convert LO SP-1 advisories to Prime NEW proposals

---

## Summary (Non-Actionable for Prime Dispatch)

This advisory documents Loyal Opposition investigation findings regarding the Ollama dispatch
reliability pipeline, transferred to Prime Builder via owner directive. **LO findings are preserved
here as audit trail. Prime Builder should review, then file separate NEW implementation proposals
per subproject scope.**

**Four withdrawn advisories:** sp1a (prompt restructure), sp1b (outcome tracker), sp1c (author
guard), sp1d (turn budget). All contain findings + premature scope specifications that crossed
LO/Prime role boundary. LO has preserved findings; Prime files proposals.

## LO Investigation Findings (Preserved from Sp1a-Sp1d Withdrawals)

### Dispatch Mechanism Health: Working Reliably ✅
- Cross-harness trigger fires correctly on PostToolUse hooks
- Dispatch state tracking functions (`dispatch-state.json`)
- Ollama launches successfully (82+ dispatch runs logged since June 5, last successful 2026-06-08T14:35:26Z)
- Substrate correctly configured as `cross_harness_trigger` in `harness-state/bridge-substrate.json`

### Five Failure Modes Identified (Ranked P0 → P2)

| ID | Finding | Severity |
|---|---|---|
| **F1** | Ollama LO rejects 100% of proposals on spec-linkage technicalities rather than substantive review | **P0** |
| **F2** | Model inconsistently executes claim-before-write, causing bridge-compliance-gate hard-block | **P0** |
| **F3** | Turn budget (16 turns, 180s) exhaustion before verdict production | **P1** |
| **F4** | No dispatch outcome feedback loop - silent failures undetected | **P2** |
| **F5** | Same-agent meta-rejection loop - Ollama reviews its own proposals | **P2** |

### Evidence Sources

- Dispatch state: `.gtkb-state/cross-harness-trigger/dispatch-state.json` (82+ runs)
- Dispatch logs: `.gtkb-state/cross-harness-trigger/dispatch-run-logs/` (82+ files)
- Diagnostic log: `.gtkb-state/cross-harness-trigger/trigger-diagnostic.jsonl`
- Bridge substrate: `harness-state/bridge-substrate.json` (correctly `cross_harness_trigger`)
- Ollama prompt: `scripts/ollama_harness.py:265-299` (`build_system_prompt()`)

### Recommended Implementation Order (LO Stance, Not Prescription)

Based on leverage and dependency: SP-1a → SP-1d → SP-1c → SP-1b

- SP-1a (prompt restructure) addresses F1 + F2 simultaneously; highest-leverage fix
- SP-1d (turn budget) is quick 3-line change that eliminates F3
- SP-1c (author guard) prevents F5 but doesn't block usefulness
- SP-1b (outcome tracker) addresses F4 but low urgency

### Detailed Investigation Report

Full evidence inventory, per-finding deep analysis, target paths, and acceptance tests preserved at:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`

## Owner Decision / Evidence

**Context:** LO filed 4 ADVISORY bridge entries with `target_paths` and implementation scope
sections. This crossed the LO/Prime role boundary per `.claude/rules/file-bridge-protocol.md`
§Advisory Reports.

**LO self-identified violation:** Same-agent self-review mode demonstrated - LO authored work that
should be independently reviewed, then filed it. Same failure mode as F5 (meta-rejection) we were
proposing to fix in dispatch.

**Owner directive:** Option 2 selected from LO's 4-option disposition menu -
> "Convert to NEW implementation proposals for Prime - Withdraw the advisories and queue them for
> Prime Builder to file as formal NEW proposals with proper work-intent claims and spec linkage."

## Expected Prime Action

Prime Builder should, for each subproject (sp1a, sp1b, sp1c, sp1d):

1. Review the withdrawn advisory (`gtkb-sp1<N>-*-001.md`) for context
2. Review the LO investigation report for evidence
3. File a NEW implementation proposal with:
   - Proper work-intent claim via `scripts/bridge_claim_cli.py claim <slug>`
   - `Specification Links` section citing applicable governance specs
   - `Requirement Sufficiency` subsection (`Existing requirements sufficient` / `New or revised requirement required before implementation`)
   - `target_paths` metadata listing authorized files
   - Specification-derived verification plan
4. Run `scripts/bridge_applicability_preflight.py --bridge-id <intended-bridge-id>` before INDEX update
5. Register in `bridge/INDEX.md` as `NEW`

## Related Artifacts

- Withdrawn advisories (superseded): `gtkb-sp1a-ollama-lo-prompt-restructure-00[12].md`, `gtkb-sp1b-dispatch-outcome-tracker-00[12].md`, `gtkb-sp1c-author-meets-reviewer-guard-00[12].md`, `gtkb-sp1d-turn-budget-optimization-00[12].md`
- Investigation report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`

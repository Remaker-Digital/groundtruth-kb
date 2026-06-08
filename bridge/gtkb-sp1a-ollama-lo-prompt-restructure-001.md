ADVISORY

# Advisory: SP-1a — Ollama LO Prompt Restructure (Verdict-First Strategy)

**bridge_kind:** advisory
**Document:** gtkb-sp1a-ollama-lo-prompt-restructure
**Version:** 001
**Author:** Loyal Opposition (Goose E, session-scoped LO override)
**Date:** 2026-06-08
**Priority:** P0
**Supersedes:** bridge/gtkb-ollama-lo-prompt-hardening-003.md (REVISED, unimplemented — this advisory absorbs and restructures F1/F2)

---

## Claim

The Ollama LO dispatch pipeline (`scripts/ollama_harness.py` → `build_system_prompt()`) produces
correctly-formatted NO-GO verdicts that are operationally useless. The prompt instructs the model to:

1. Run mandatory preflights (line 284-288)
2. Treat nonzero preflight exits as automatic NO-GO inputs (line 288)
3. Acquire claim via `bridge_claim_cli.py` before any Write (line 279-281)

Finding (F1): 100% of dispatched Ollama reviews produce NO-GO on spec-linkage technicalities rather
than substantive proposal review. The preflights are mechanical gates; the model faithfully rejects
proposals that fail them without evaluating the proposal's actual content.

Finding (F2): The model inconsistently executes claim-before-write, causing bridge-compliance-gate
hard-block on Write calls. The prompt presents claim as one step among many with no enforcement
beyond "you must do this."

## Evidence

| Source | Evidence |
|---|---|
| `scripts/ollama_harness.py:265-299` | `build_system_prompt()` encodes preflight-as-blocking and claim-before-write |
| 15 × `-002.md` NO-GO verdict files in `bridge/` | All cite spec-linkage gaps as primary NO-GO reason |
| `dispatch-runs/2026-06-08T14-35-26Z-loyal-opposition-e6ebc4.stdout.log` | Last dispatch produced NO-GO on identical grounds |
| `bridge/gtkb-ollama-lo-prompt-hardening-003.md` | Prime identified F1/F2 at REVISED; not yet implemented |
| `bridge/gtkb-ollama-dispatch-state-recovery-002.md` | Meta-example: Ollama LO reviewed Ollama PB's own proposal and NO-GO'd it |

## Recommended Implementation Scope

### A. Restructure `build_system_prompt()` prompt hierarchy

Move preflight execution from "mandatory gate" to "advisory evidence." The revised prompt should:

1. **Claim is FIRST and mandatory** — not one step among many. If claim fails, the session exits
   gracefully rather than attempting Write.
2. **Read chain, then produce verdict skeleton** — "Based on your reading, draft your GO or NO-GO
   reasoning as the body of your verdict file."
3. **Preflight output is advisory evidence** — "Run preflights and report their output as FINDINGS
   within your verdict. Preflight failures are review evidence, not automatic NO-GO gates."
4. **Write the verdict file AFTER drafting reasoning** — not before preflights, not after turn exhaustion.

### B. Replace blocking semantics in prompt text

Current (blocking):
> "Nonzero preflight exits are review evidence: exit 5 from the ADR/DCL clause preflight is a NO-GO input unless an explicit owner waiver is present."

Proposed (advisory):
> "Preflight results are findings to include in your verdict. A preflight failure is substantive evidence for your NO-GO reasoning, not an automatic gate. You retain judgment on whether the proposal's content is sound despite preflight gaps."

### C. Enforce claim-before-write structurally

Rather than relying on prompt compliance:
- Make `bridge_claim_cli.py claim` the very first tool call the model makes
- If claim fails (exit code != 0), the model exits the session with a diagnostic message
- The claim exit code is the model's go/no-go on proceeding, not a soft instruction

### D. Acceptance Test

| Criterion | Threshold |
|---|---|
| Dispatches producing verdict files | ≥ 4 of 5 |
| Verdicts with substantive reasoning (not just preflight output) | ≥ 3 of 5 |
| Verdicts based on proposal content, not only spec-linkage | ≥ 2 of 5 |
| Claim-before-write compliance | 5 of 5 |

## target_paths

```
scripts/ollama_harness.py          (MODIFY build_system_prompt function)
tests/test_ollama_harness.py       (MODIFY prompt-structure assertions)
```

## Relationship to Existing Bridge Threads

| Thread | Status | Relationship |
|---|---|---|
| `gtkb-ollama-lo-prompt-hardening` | REVISED at -003 | This advisory absorbs F1 (preflight blocking) and F2 (claim timing) and restructures them |
| `gtkb-ollama-dispatch-state-recovery` | NO-GO at -002 | Independent — this advisory does not address dispatch state recovery |

## Expected Prime Action

Prime Builder should either:
1. File a normal `REVISED` implementation proposal on `gtkb-ollama-lo-prompt-hardening-004.md` implementing the restructure
2. Convert this advisory to a new `NEW` implementation proposal on a new bridge thread
3. Defer with documented rationale

## Related Artifacts

- Investigation report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`
- Protocol: `.claude/rules/file-bridge-protocol.md` (Advisory Reports section)

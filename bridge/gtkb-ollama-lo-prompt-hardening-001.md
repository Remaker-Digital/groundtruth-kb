# Bridge Proposal: Ollama LO System Prompt Hardening (Phase 3)

**Status:** NEW  
**Author:** Prime Builder  
**Date:** 2026-06-08  
**Bridge ID:** gtkb-ollama-lo-prompt-hardening  
**Priority:** HIGH  
**Related Work:** gtkb-mcp-stable-harness-surface-implementation

---

## Problem Statement

The Ollama Loyal Opposition harness (harness ID: D) has been experiencing three critical failure modes when dispatched for bridge reviews:

1. **Claim-before-write violation:** The model attempts to write bridge verdict files without first acquiring the mandatory claim via `bridge_claim_cli.py`, causing the bridge-compliance-gate to deny the write.

2. **Turn exhaustion:** The model exhausts its 8-turn budget without producing a final verdict, indicating it's not following the multi-step protocol correctly.

3. **Float-string coercion:** The model emits tool arguments like `"max_chars": "300.0"` instead of integer values, causing crashes in older code paths (this is now fixed via `_positive_int_argument()`).

These failures indicate the current system prompt does not effectively guide the smaller model through the mandatory multi-step protocol.

---

## Root Cause Analysis

The current system prompt is a large prose block that describes the protocol but does not enforce step-by-step execution. The Ollama model (typically smaller and less capable than Claude/GPT-4) fails to:

- Internalize the mandatory claim step before writes
- Track its progress through the protocol
- Decide when to stop and report errors vs. retry
- Converge on a verdict within the turn budget

**Evidence:** Analysis of dispatch logs from 2026-06-07 shows multiple instances of:
- `bridge-compliance-gate.py: No claim found for bridge/gtkb-...-NNN.md`
- `OllamaHarnessError: max-turn exhaustion`
- Model attempting to write verdict files in turn 1-2 without claiming

---

## Proposed Solution

Restructure the system prompt from prose to a numbered, mandatory protocol with explicit decision points:

```python
SYSTEM_PROMPT_TEMPLATE = """You are the Loyal Opposition harness (ID: D) for GT-KB.

## MANDATORY PROTOCOL (Follow exactly in order)

### Step 1: Acquire Bridge Claim
- Run: python scripts/bridge_claim_cli.py claim <bridge-slug>
- If claim fails, STOP and report the error. Do not proceed.
- If claim succeeds, proceed to Step 2.

### Step 2: Read Bridge Entry
- Read the assigned bridge entry file.
- If the file is missing or unreadable, STOP and report the error.
- Proceed to Step 3.

### Step 3: Review and Analyze
- Review the bridge entry content.
- Identify what verdict is required (GO/NO-GO for proposals, VERIFIED/NO-GO for implementations).
- Gather any additional evidence needed (read related files if necessary).
- Proceed to Step 4.

### Step 4: Write Verdict
- Write your verdict to the bridge file using the Write tool.
- Include: verdict, reasoning, evidence, and signature.
- If write fails, STOP and report the error.
- Proceed to Step 5.

### Step 5: Finalize
- Report completion: "Bridge review complete for <bridge-slug>. Verdict: <verdict>."
- STOP. Do not perform additional actions.

## CRITICAL RULES
- NEVER skip Step 1 (claim acquisition).
- NEVER retry a failed step more than once.
- If any step fails, STOP immediately and report the error.
- Keep responses concise to stay within turn budget.
"""
```

**Key Changes:**
1. **Numbered steps** with explicit decision points (proceed/stop)
2. **Mandatory claim step** as Step 1 with clear failure handling
3. **Stop conditions** for each step to prevent infinite loops
4. **Concise response guidance** to conserve turns
5. **No retry loops** — fail fast and report

---

## Implementation Details

### File: `scripts/ollama_harness.py`

Replace the current `SYSTEM_PROMPT` constant with the new template above.

Update `build_system_prompt()` to inject the bridge slug:

```python
def build_system_prompt(role: str, bridge_slug: str | None = None) -> str:
    if role == 'loyal-opposition' and bridge_slug:
        return SYSTEM_PROMPT_TEMPLATE.replace('<bridge-slug>', bridge_slug)
    return BASE_SYSTEM_PROMPT
```

### Dispatch Integration

The cross-harness trigger already passes the bridge slug via the prompt. No changes needed to the trigger itself.

---

## Testing Plan

1. **Manual dispatch test:**
   ```bash
   python scripts/ollama_harness.py --bridge-id gtkb-test-bridge-001
   ```
   Verify the model:
   - Acquires claim in turn 1
   - Reads the bridge file in turn 2
   - Writes verdict in turn 3-4
   - Completes within 8 turns

2. **Failure mode test:**
   - Simulate a missing bridge file
   - Verify the model stops and reports the error (does not retry)

3. **Turn budget test:**
   - Monitor dispatch logs to confirm verdicts are produced within 8 turns

---

## Risk Assessment

**Risk Level:** LOW

- **Risk:** Model may still fail to follow the protocol
  - **Mitigation:** If this fails, Phase 4 (dispatch-state recovery) will prevent infinite retry loops
  - **Fallback:** Consider switching to a larger model (e.g., `llama3:70b`) if the protocol doesn't work with the current model

- **Risk:** Protocol may be too rigid for complex reviews
  - **Mitigation:** Protocol is designed for standard bridge reviews; complex cases can be handled by Prime Builder or Claude Loyal Opposition

---

## Acceptance Criteria

- [ ] Ollama LO successfully acquires claim before writing verdict files
- [ ] Ollama LO produces verdicts within 8 turns for standard bridge reviews
- [ ] Ollama LO stops and reports errors instead of retrying indefinitely
- [ ] Bridge compliance gate no longer denies writes due to missing claims
- [ ] Turn exhaustion errors eliminated from dispatch logs

---

## Related Work

- `gtkb-mcp-stable-harness-surface-implementation` — May overlap if that proposal includes prompt engineering for Ollama
- Phase 4 (dispatch-state recovery) — Complements this proposal by preventing infinite retry loops when the model fails

---

## Decision Required

**OWNER ACTION REQUIRED**

Approve this proposal for implementation?

**Why it matters:** This addresses the core protocol-following failure in Ollama LO dispatches. Without this, even with the float-string fix, the model will continue to violate claim-before-write and exhaust turns.

**Expected reply:** APPROVE / REJECT / REQUEST_CHANGES

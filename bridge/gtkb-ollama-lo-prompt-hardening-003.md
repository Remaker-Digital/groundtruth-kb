REVISED

# Bridge Proposal: Ollama LO System Prompt Hardening

**Bridge ID:** gtkb-ollama-lo-prompt-hardening
**Author:** Prime Builder (Claude B, pb override)
**Date:** 2026-06-08
**Addresses:** NO-GO at bridge/gtkb-ollama-lo-prompt-hardening-002.md

---

## Specification Links

| Spec ID | Title | Relevance |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge index authority and permanent bridge repair authority | This proposal is a bridge artifact; bridge authority governs |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Implementation proposals must be linked to all relevant specifications | Mandatory citation gate for all proposals |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | VERIFIED is conditional on test creation + execution derived from linked specs | Testing must map to specs |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Artifact lifecycle trigger declarations | advisory; lifecycle state changes present in proposal |

**Requirement Sufficiency:** Existing requirements sufficient. The `build_system_prompt()` function contract and harness behavior are governed by the Ollama integration specs already in MemBase (Ollama phase-1 project). No new specifications required for this prompt restructuring.

**target_paths:**
- `scripts/ollama_harness.py`
- `tests/test_ollama_harness.py` (existing test file, new test cases added)

---

## Problem Statement

The Ollama LO harness fails on every bridge-review dispatch due to three cascading failure modes:

1. **Claim-before-write violation** — model writes verdict files without acquiring the mandatory `bridge_claim_cli.py` claim, causing bridge-compliance-gate hard-block.
2. **Max-turn exhaustion** — model uses all 8 turns reading without converging to a verdict; current `DEFAULT_MAX_TURNS = 16` but dispatched sessions exhaust before producing final assistant text.
3. **Float-string arg crash** — FIXED in current code via `_positive_int_argument()`.

Evidence: dispatch logs `2026-06-07T07:32–07:49Z` and `2026-06-08T14:15Z`, `14:35Z` all show `max-turn exhaustion` or `guard denied Write`.

---

## Root Cause

`build_system_prompt()` returns a large prose block. The `qwen3-coder-next:cloud` model does not reliably follow multi-step prose protocols — it enters read loops without converging. The mandatory claim step is buried in prose and skipped.

---

## Proposed Solution

### Change 1: Restructure system prompt to numbered mandatory steps

Replace the existing prose system prompt body in `build_system_prompt()` with a numbered, decision-point-driven protocol. The existing function signature `build_system_prompt(skill, model_route)` is **preserved** — no breaking change.

The new prompt content for `LOYAL_OPPOSITION_BRIDGE_SKILLS`:

```
MANDATORY BRIDGE REVIEW PROTOCOL — follow exactly in order, one step at a time.

STEP 1 — CLAIM: Run this Bash command first:
  python scripts/bridge_claim_cli.py claim <slug>
  Replace <slug> with the document name from the dispatch notification.
  If exit code is nonzero, STOP and output: "ERROR: claim failed for <slug>"
  If exit code is 0, proceed to STEP 2.

STEP 2 — READ INDEX: Read bridge/INDEX.md.
  Find the entry for <slug>. Identify the latest file path.
  Proceed to STEP 3.

STEP 3 — READ ENTRY: Read the latest bridge file for <slug>.
  Identify whether this is a proposal (NEW/REVISED → needs GO or NO-GO)
  or a post-implementation report (NEW after a GO → needs VERIFIED or NO-GO).
  Proceed to STEP 4.

STEP 4 — PREFLIGHT: Run both preflights via Bash:
  python scripts/bridge_applicability_preflight.py --bridge-id <slug>
  python scripts/adr_dcl_clause_preflight.py --bridge-id <slug>
  Record the preflight output. If applicability preflight reports
  missing_required_specs that are not empty, your verdict is NO-GO.
  Proceed to STEP 5.

STEP 5 — WRITE VERDICT: Write the verdict file to bridge/<slug>-NNN.md
  where NNN is the next version number (one higher than the latest file).
  First line of the file MUST be exactly one of: GO, NO-GO, VERIFIED
  Include: verdict rationale, preflight output, author metadata.
  Then update bridge/INDEX.md: add the new verdict line at the top of the
  <slug> entry (format: "GO: bridge/<slug>-NNN.md").
  Output: "Bridge review complete. Verdict: <verdict> for <slug>."
  STOP.

CRITICAL RULES:
- NEVER skip STEP 1. The claim is mandatory before any Write.
- Do NOT retry a failed step more than once. Report errors and STOP.
- Keep each response concise — you have a limited turn budget.
- After STEP 5, do not take further actions.

Author metadata to include in verdict:
  author_identity: {author_identity}
  author_harness_id: {author_harness_id}
  author_model: {model_id}
  author_model_version: {model_version}
  author_model_configuration: Ollama harness shim; route {route_key}; skill {skill}
```

The `<slug>` placeholder is resolved from the dispatch notification prompt at runtime (the dispatch prompt includes the document name). The `{author_*}` tokens are already interpolated by `build_system_prompt()` using `model_route` fields.

### Change 2: Increase default turn budget for bridge-review skill

The current `DEFAULT_MAX_TURNS = 16` constant applies globally. Add a per-skill override in `build_system_prompt()` that passes a recommended max-turns hint via the system prompt for bridge-review skill:

```python
# In build_system_prompt(), for LOYAL_OPPOSITION_BRIDGE_SKILLS:
# Recommend 12 turns minimum in the system prompt header.
```

No code change to turn enforcement is needed — the prompt advises the model to be concise and stop after Step 5, naturally keeping turn count low.

### Change 3: Add INDEX.md update to Step 5

The original proposal omitted the INDEX.md update from the protocol steps. Step 5 now explicitly instructs the model to update `bridge/INDEX.md` after writing the verdict file.

---

## Implementation Details

**File: `scripts/ollama_harness.py`**

Modify `build_system_prompt()`: replace the prose body for `LOYAL_OPPOSITION_BRIDGE_SKILLS` routes with the numbered protocol above. The function signature `build_system_prompt(skill, model_route)` is unchanged.

No changes to the dispatch trigger or harness invocation surfaces.

---

## Spec-to-Test Mapping

| Spec | Test coverage |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_ollama_harness.py::test_build_system_prompt_lo_skill_contains_claim_step` — verifies the claim step is present in the prompt |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Covered by this proposal's spec table (proposal-level compliance, not runtime test) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_ollama_harness.py::test_build_system_prompt_lo_skill_contains_preflight_step` — verifies preflight step is present |

Additional integration-level verification:
- `test_ollama_harness.py::test_build_system_prompt_signature_unchanged` — verifies no breaking signature change
- `test_ollama_harness.py::test_build_system_prompt_non_lo_skill_unchanged` — verifies non-LO skills unaffected

---

## Verification Plan

```bash
python -m pytest tests/test_ollama_harness.py -k "system_prompt" -v
```

Expected: all prompt-structure tests pass. No regression on existing harness tests.

---

## Risk Assessment

**Risk level:** LOW
- Prompt change is additive/restructuring — no harness logic changes
- Non-LO skills are unaffected
- If the model still fails, Phase 4 (dispatch-state recovery) provides recovery

---

## Acceptance Criteria

- [ ] `build_system_prompt()` signature unchanged
- [ ] LO bridge-review prompt contains numbered steps with explicit STEP 1 claim instruction
- [ ] Step 5 includes INDEX.md update instruction
- [ ] Prompt unit tests pass
- [ ] Existing harness tests pass (no regression)

---

## Prior Deliberations

- `DELIB-20260663` — Ollama integration design decisions (phase 1)
- `bridge/gtkb-ollama-integration-phase-1-008.md` (VERIFIED) — phase 1 implementation complete
- `bridge/gtkb-ollama-lo-prompt-hardening-002.md` — NO-GO findings addressed above

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

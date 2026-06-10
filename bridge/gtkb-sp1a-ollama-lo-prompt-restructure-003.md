NEW

# Implementation Proposal — SP-1a: Ollama LO Prompt Restructure (Verdict-First Strategy)

**Status:** NEW (awaiting Loyal Opposition review)
**Author:** Prime Builder (Goose, harness E)
**Session:** S509 continuation, 2026-06-08 (PB processing owner directive to convert SP-1 advisories)
**Document:** gtkb-sp1a-ollama-lo-prompt-restructure
**Version:** 003
**In response to:** owner directive (2026-06-08 11:28) converting LO SP-1 ADVISORY -001/-002 withdrawn files to PB implementation proposals

bridge_kind: prime_proposal
implementation_scope: ollama_dispatch_prompt_restructure

Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4431 (to be created via MemBase CLI)
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO
Owner Decision: DELIB-20260608-SP1-CONVERT-ADVISORIES (owner: "Convert to NEW implementation proposals for Prime")

## Owner Decisions / Input

Owner (Mike) explicitly directed at 2026-06-08 11:28 UTC:
> "Convert to NEW implementation proposals for Prime — Withdraw the advisories and queue them for Prime Builder to file as formal NEW proposals with proper work-intent claims and spec linkage."

(Recorded in `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md` and LO -002 withdrawal files.)

This decision authorizes PB to file implementation proposals for all four SP-1 subprojects. This proposal addresses **SP-1a only**. (SP-1b/SP-1c/SP-1d to follow as separate bridge threads.)

## Prior Deliberations

- `DELIB-20260608-SP1-CONVERT-ADVISORIES` — owner directive to convert LO advisories to PB proposals.
- `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md` — LO handoff advisory (current).
- `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-001.md` — LO ADVISORY, WITHDRAWN (role-boundary violation).
- `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-002.md` — LO withdrawal notice (WITHDRAWN).
- `bridge/gtkb-ollama-lo-prompt-hardening-003.md` — prior Prime REVISED (not yet implemented); this proposal supersedes the unresolved F1/F2/F3 scope in that thread with a narrower, verdict-first intervention.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md` — LO investigation report (findings F1–F5).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge files remain role handoff / verdict authority; this proposal modifies the dispatch prompt that produces bridge verdicts, so the new prompt must still satisfy all file-bridge gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation report must map claims to spec-derived tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization.
- `.claude/rules/file-bridge-protocol.md` §Pre-Drafting Claim Step — work-intent claim acquired.
- `.claude/rules/file-bridge-protocol.md` §Pre-Filing Preflight Subsection — preflight executed before INDEX update.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is required for this slice. The dispatch prompt is internal scaffolding for the Ollama LO review workflow and is already governed by the existing `GOV-FILE-BRIDGE-AUTHORITY-001` file-bridge authority and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` artifact lifecycle triggers.

## Summary

This proposal restructures `scripts/ollama_harness.py:build_system_prompt()` to switch the dispatched Ollama LO session from a **preflight-blocking** workflow to a **verdict-first** strategy. Two P0 failure modes from the SP-1 investigation report are addressed together:

- **F1: preflight-as-blocking** — current prompt instructs "exit 5 from the ADR/DCL clause preflight is a NO-GO input unless an explicit owner waiver is present". This produces 100% NO-GO rates on governance form rather than substantive review.
- **F2: claim-before-write timing** — current prompt mentions claim acquisition as one step among many, with no enforcement. Model inconsistently skips, producing bridge-compliance-gate hard-blocks.

## Scope

This slice does **not** address F3 (turn budget), F4 (outcome feedback loop), or F5 (self-review loop). Those map to SP-1d, SP-1b, and SP-1c respectively and will be filed as separate proposals.

## Changes to be Made

### C1: Restructure `build_system_prompt()` to verdict-first strategy

**File:** `scripts/ollama_harness.py`

Remove the preflight-as-blocking instruction. Replace with:

> "Run preflight checks and include their raw output in the verdict as **advisory context for the Prime Builder**. A nonzero preflight exit is a note to attach to the verdict body, not a rejection criterion. Your verdict (GO / NO-GO / VERIFIED) evaluates the **substantive quality** of the proposal or implementation report being reviewed — not whether every applicable cross-cutting spec appears in the linked specs list."

Keep the preflight invocation commands themselves (`bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py`) but instruct the model to treat output as evidence of spec coverage, not as a gate.

### C2: Enforce claim-before-write with explicit ordering and guard language

Move the claim acquisition instruction to the **top** of the prompt (immediately after role identification), and reword to emphasize mandatory ordering:

> "Before you can write any bridge verdict, you MUST acquire the work-intent claim: `python scripts\\bridge_claim_cli.py claim <document-slug>`. If the claim command reports an existing holder, treat that JSON output as claim evidence — not as a harness crash. Do not proceed to Write until the claim command returns success."

### C3: Add `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py`

New test file covering the two P0 claims:
- `test_build_system_prompt_uses_verdict_first_language` — verifies the prompt no longer contains "NO-GO input unless an explicit owner waiver" and instead contains "advisory context" language.
- `test_build_system_prompt_enforces_claim_first` — verifies claim acquisition appears before any Write instruction in the prompt text.
- `test_build_system_prompt_retains_preflight_commands` — verifies preflight commands remain in the prompt (we're making them non-blocking, not removing them).

### C4: Update dispatch-related tests

No existing tests in `platform_tests/scripts/test_ollama_*.py` are expected to break — the current tests exercise harness behavior, not prompt substring semantics. Any test that does match prompt substring will be updated in place as part of C4.

## target_paths metadata

target_paths: [
  "scripts/ollama_harness.py",
  "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py",
]

## Spec-Derived Verification Plan

| Spec clause | Test covering it |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` C-001 "bridge files remain the role handoff authority" | `test_build_system_prompt_retains_preflight_commands` (preflight commands preserved) |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` VERIFIED/GO/NO-GO lifecycle | `test_build_system_prompt_uses_verdict_first_language` (prompt no longer blocks verdict production) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` proposal links governing specs | `test_build_system_prompt_uses_verdict_first_language` (prompt references preflight as advisory evidence of linkage) |

## Risks and Mitigations

**Risk 1:** The verdict-first prompt could overcorrect and cause Ollama to write GO verdicts on substantively broken proposals that also happen to have good spec linkage.

**Mitigation:** The prompt retains all preflight invocations as evidence gathering. The restructure changes only how the verdict decision is framed (substantive review vs. form rejection), not whether the evidence is gathered. LO retains discretion to NO-GO on substantive grounds.

**Risk 2:** The F2 claim-first enforce language could still be bypassed by a sufficiently non-compliant model.

**Mitigation:** The bridge-compliance-gate hook remains the hard blocker. This slice adds stronger prompt instruction to reduce the frequency of bypass attempts. Full enforcement would require a hook-level guard on the model's tool-call sequence, which is out of scope for this slice (flag for future slice).

## Bridge Protocol Compliance Note

This proposal was filed by running `bridge_claim_cli.py claim gtkb-sp1a-ollama-lo-prompt-restructure` before any file write. Pre-filing applicability preflight executed before INDEX update. The `gtkb-sp1a-ollama-lo-prompt-restructure-001.md` and `-002.md` files remain on disk as historical audit trail; they are not superseded in the protocol sense — they are WITHDRAWN advisory entries that have been dispositioned per the owner directive to convert to PB proposals.

## Recommended Commit Type

`feat(ollama-harness):` — restructures the Ollama LO dispatch prompt strategy with new capability surface (verdict-first, claim-first enforcement).

---

*Prime Builder: goose (harness E), session S509
2026-06-08 ~11:37 UTC*

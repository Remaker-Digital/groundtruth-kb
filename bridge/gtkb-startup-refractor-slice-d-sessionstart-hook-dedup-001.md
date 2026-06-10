NEW

# GTKB-STARTUP-REFRACTOR-001 Slice D — SessionStart Hook De-Duplication

bridge_kind: prime_proposal
Document: gtkb-startup-refractor-slice-d-sessionstart-hook-dedup
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (PAUTH-authorized implementation)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-startup-refractor-slice-d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4272

target_paths: [".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/session_start_dispatch_core.py", "platform_tests/scripts/test_*session_start*.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272) — the highest-blast-radius slice,
sequenced **last**. `.claude/hooks/session_start_dispatch.py` and
`.codex/gtkb-hooks/session_start_dispatch.py` share ~250 character-identical
lines (the `StartupDecision` enum, role-set resolution, the ephemeral
session-role marker lifecycle, and the dispatch-context templates), kept in sync
today by byte-identity parity tests — i.e., the current "fix" for the
duplication is a test that asserts the duplication stays identical (advisory F4
at the code layer).

This slice extracts that shared logic into one stdlib-light shared module,
`scripts/session_start_dispatch_core.py`, leaving each hook as a thin
harness-specific wrapper (differing only in `HARNESS_NAME`, output dir, and
the one comment), and converts the parity tests from "the two files are
byte-identical" to "both wrappers import and delegate to the shared module."

This is a **behavior-preserving refactor**: no change to SessionStart decision
logic, role resolution, init-keyword dispatch, or the disclosure-relay contract.

### Sequencing

Implement **after Slices B/E/C land and the recently-VERIFIED active-status
capability-gate work in this same hook area settles**, to avoid collision. The
GO on this proposal authorizes the design; the implementation-start packet
should be minted only when the area is quiet.

### Invariants the refactor must preserve

- **stdlib-light / fast-import:** the shared module imports only the standard
  library; the hooks' fast SessionStart path is not slowed. (This property is
  why the duplication existed; it must survive de-duplication.)
- **Harness parity:** `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Claude and Codex
  SessionStart behavior stays identical; the parity tests are rewritten to
  assert shared-module delegation, not deleted.
- **Role resolution:** `DCL-SESSION-ROLE-RESOLUTION-001` resolution table and
  the ephemeral marker lifecycle behavior unchanged.
- **Init-keyword contracts:** `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` +
  `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` parsing/assertion unchanged.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the SessionStart dispatch behavior preserved here. PAUTH-linked.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — de-duplication reduces the maintained startup surface. PAUTH-linked.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Claude/Codex hook parity must be preserved; parity tests are the contract.
- `DCL-SESSION-ROLE-RESOLUTION-001` — role-resolution table the hooks consume; behavior unchanged.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — init-keyword syntax the hooks parse; unchanged.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — init-keyword assertion; unchanged.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH linkage.
- `GOV-STANDING-BACKLOG-001` — WI-4272 linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all target paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Prior Deliberations

- `DELIB-20260622` — owner PAUTH decision (covers WI-4272).
- `bridge/gtkb-startup-refractor-scoping-002.md` — scoping GO defining Slice D (and noting it as the discovered code-consolidation target sequenced last).
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md` — Slice A VERIFIED; the control-map classifies both hooks as active de-dup targets.

## Owner Decisions / Input

- Implementation authority: project PAUTH (active), owner decision `DELIB-20260622`,
  allowed mutation classes include `source`, `hook`, `test`. No embedded owner
  content decision; this is a behavior-preserving refactor.

## Requirement Sufficiency

**Existing requirements sufficient.** The behavior contract is fully specified by
the cited parity/role/init-keyword specs; this slice preserves that contract
while removing duplication. No new specification is required.

## Spec-Derived Verification Plan

| Specification / Invariant | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | rewritten parity test asserts both hooks delegate to `session_start_dispatch_core` and produce identical decisions for identical inputs | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py -q --no-header -p no:cacheprovider` | PASS |
| `DCL-SESSION-ROLE-RESOLUTION-001` + init-keyword specs | existing SessionStart dispatcher tests (role resolution, init-keyword routing, STRICT_DROP) pass unchanged against the refactored hooks | (same pytest, full session-start test set) | PASS |
| stdlib-light invariant | a test asserts `session_start_dispatch_core` imports only stdlib (no third-party / DB imports) | (same pytest) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on changed Python | `ruff check` / `ruff format --check` on the hooks + shared module + tests | clean |

The implementation report will carry observed pytest + ruff results.

## Risk / Rollback

Highest blast radius in the umbrella (every session start runs these hooks). Risk
is mitigated by: behavior-preserving extraction, the rewritten parity tests, the
full existing SessionStart dispatcher test suite as a regression floor, the
stdlib-light import assertion, and sequencing this slice last. Rollback is a
single-commit revert restoring the two self-contained hooks.

## Recommended Commit Type

`refactor` — extracts shared SessionStart logic into one module with thin
wrappers; no behavior change, no new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

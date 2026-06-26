NEW

# gtkb-wi4788-slice-1-dispatch-config-state-gate — Black-box gate slice 1: PreToolUse decision blocking direct agent writes to dispatcher config + runtime state

bridge_kind: prime_proposal
Document: gtkb-wi4788-slice-1-dispatch-config-state-gate
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4788

target_paths: ["scripts/dispatch_blackbox_gate.py", "platform_tests/scripts/test_dispatch_blackbox_gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4788 (the "full black box") makes the dispatcher a GT-KB-owned service that harnesses cannot directly mutate, per ADR-DISPATCHER-ARCHITECTURE-001 isolation invariants 1-3. The existing implementation-start gate (`scripts/implementation_start_gate.py`) already guards dispatcher *implementation source* (writes need a bridge-GO packet). WI-4788's distinct contribution is the **config + runtime-state** half: an agent must not directly hand-edit dispatcher config or runtime state — those mutations must go through the governed CLI (`gt bridge dispatch config`, `gt mode set-role`, `gt harness`). This slice 1 delivers the gate **decision logic** (a testable pure core + a PreToolUse entry point); wiring it into the live hook arrays is a thin follow-on activation step.

This is the structural fix for the WI-4820 class I hit earlier this session: the only safe way to change dispatch eligibility is the CLI (which write-throughs the projection); a direct hand-edit of `rules.toml` or `harness-registry.json` is exactly what produced the false-green drift. The gate makes that hand-edit impossible.

## Design (for LO review)

New module `scripts/dispatch_blackbox_gate.py`, mirroring the structure of `scripts/implementation_start_gate.py` (PreToolUse Write/Edit gate) and the read-discipline hook:

- **`PROTECTED_DISPATCHER_PATHS`** — the registry of dispatcher config + runtime-state surfaces, as exact files and directory prefixes:
  - config: `config/dispatcher/rules.toml`
  - eligibility/role projection: `harness-state/harness-registry.json`
  - runtime state: `.gtkb-state/bridge-poller/` (dispatch-state.json, dispatch-failures.jsonl, quiesce-state.json, dispatch-runs/), `.gtkb-state/cross-harness-trigger/`, `.gtkb-state/dispatcher-daemon/`
- **`classify_protected_path(rel_path) -> str | None`** — pure; returns the protected class (`dispatcher_config` / `harness_registry` / `dispatcher_runtime_state`) or None.
- **`gate_decision(tool_name, target_path, *, bypass) -> GateDecision`** — pure; for `Write` / `Edit` / `NotebookEdit` to a protected path, returns `block=True` with a `reason` naming the governed CLI for that class (e.g., config -> `gt bridge dispatch config set-eligibility`; registry/role -> `gt mode set-role` / `gt harness`). Non-protected paths and non-mutating tools pass. `bypass=True` (owner override) passes with an audit note.
- **`main()`** — PreToolUse entry point: reads the hook JSON from stdin (`tool_name`, `tool_input.file_path`), calls `gate_decision`, and emits a block decision (per the established hook contract) or allows. Owner bypass via `GTKB_DISPATCH_BLACKBOX_BYPASS=1` (logged to the gate-denials JSONL like the impl-start gate).

**Why this is the right enforcement boundary.** The gate fires on the **Write/Edit tools** (direct agent file authoring). The governed CLIs mutate these files through Python file I/O, NOT the Write tool, so they bypass the gate naturally — exactly the asymmetry that makes "config/state via CLI+skill only" mechanical rather than advisory. The projection regen (`generate_harness_projection`) is likewise Python I/O and unaffected.

Scope boundary: slice 1 is the decision module + tests (tracked, reviewable, unit-testable). Registering the hook in `.claude/settings.json` + `.codex/hooks.json` PreToolUse arrays is the activation step (local, `.claude/` is git-ignored) and is a thin follow-on — kept separate so the decision logic is reviewed and tested on its own, the same split used for `bridge-compliance-gate` (logic in templates, activation in settings).

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — isolation invariants 1-3 (harnesses MUST NOT trigger/mutate dispatch; config/state is GT-KB-owned); this gate makes invariants 1-3 mechanical for the config/state surface.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — forcing eligibility/config mutations through the CLI is what keeps the projection write-through consistent (the WI-4820 class); direct hand-edits are the drift source this gate forbids.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — `harness-registry.json` is the SoT projection; direct writes bypass its generator and are blocked here.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4788-slice-1-dispatch-config-state-gate-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4788 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation drive; WI-4788 is the black-box gate on the critical path.
- `DELIB-20265888` — the 8 harness/dispatch isolation invariants this gate enforces for config/state.
- `DELIB-20265882` — dispatcher target architecture (black-box service).
- `DELIB-20266084` — WI-4787 daemon foundation the black box protects.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`); WI-4788 is authorized under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. Topology Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition. Cursor (E) reviews this proposal.
- No further owner decision is required for this slice; it adds a gate decision module + tests and changes no runtime behavior until the activation step registers the hook.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` (invariants 1-3) + `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` constrain which surfaces are protected and why. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (invariants 1-3: config/state is GT-KB-owned) | `test_gate_blocks_dispatcher_config_and_state_writes` (new) | `gate_decision("Write", p)` blocks for `config/dispatcher/rules.toml`, `harness-state/harness-registry.json`, and paths under the dispatch state dirs; the reason names the governed CLI for that class. |
| ADR-DISPATCHER-ARCHITECTURE-001 (CLI bypass asymmetry) | `test_gate_allows_non_protected_and_non_write_tools` (new) | Non-protected paths (e.g., `scripts/foo.py`) and non-mutating tools (e.g., `Read`) pass; `classify_protected_path` returns None for them. |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (owner bypass is explicit + audited) | `test_owner_bypass_allows_with_audit` (new) | `gate_decision(..., bypass=True)` passes and is flagged for audit; without bypass the same write blocks. |
| No-regression | `ruff check` + `ruff format --check` on the new files; module imports cleanly | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_dispatch_blackbox_gate.py -q --tb=short`; `ruff check <new .py>`; `ruff format --check <new .py>`.

## Risk / Rollback

- Risk: low for this slice. The decision module is additive (a new file + tests) and not wired into the live hook arrays until the activation follow-on, so it changes no runtime behavior yet. When activated, the gate is fail-safe: it blocks only Write/Edit to the enumerated dispatcher surfaces, with an owner bypass env var; CLI-mediated mutations (Python I/O) are unaffected.
- Rollback: delete the two new files (and, post-activation, unregister the hook). Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: hook registration/activation (thin follow-on), the implementation-source half (already covered by `implementation_start_gate.py`), and any change to the CLI surfaces themselves.

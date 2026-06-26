NEW

# gtkb-wi4788-slice-3-cursor-blackbox-gate-parity — Extend the live black-box gate to the Cursor harness surface

bridge_kind: prime_proposal
Document: gtkb-wi4788-slice-3-cursor-blackbox-gate-parity
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

target_paths: [".cursor/hooks.json", "platform_tests/scripts/test_dispatch_blackbox_gate_activation.py"]

implementation_scope: config
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4788 slice 2 made the dispatcher black-box gate live on the Claude surface, but it currently enforces only there — a Cursor session can still write directly to `config/dispatcher/rules.toml` / `harness-state/harness-registry.json` / the dispatch state-dirs. This matters now: Cursor (harness E) runs active Prime-Builder auto-process work on dispatcher-reliability threads, so it is the live gap, not a hypothetical one. This slice closes the Cursor half of the parity: it registers the VERIFIED gate (`scripts/dispatch_blackbox_gate.py`) on Cursor's `preToolUse` `Write` event via the existing `cursor_hook_adapter.py`, exactly as `bridge-compliance-gate.py` is already registered there. Codex parity (its `apply_patch`/`Bash` adapter) is the explicit follow-on; Codex is out of token budget today, so the Cursor gap is the one worth closing first.

## Why Cursor-first (and why it's a one-line registration)

`.cursor/hooks.json` already has a `preToolUse` array with `matcher: "Write"` entries that run Claude hooks through `scripts/cursor_hook_adapter.py` — `bridge-compliance-gate.py`, `narrative-artifact-approval-gate.py`, `implementation-start-gate.py`, etc. (L98-L129). The black-box gate is the same shape (a PreToolUse Write gate that self-filters by path), so Cursor parity is adding one adapter line — no new adapter code. Codex parity is heavier (its file authoring is `apply_patch`/`Bash`, needing the `bridge-compliance-gate-apply-patch-adapter.cmd`-style wrapper), so it is deferred to keep this slice tight and immediately protective.

## Design (for LO review)

Add one entry to the `preToolUse` array in `.cursor/hooks.json`, alongside the existing adapter-routed Write gates:

```
{ "command": "python E:\\GT-KB\\scripts\\cursor_hook_adapter.py E:\\GT-KB\\scripts\\dispatch_blackbox_gate.py", "matcher": "Write", "timeout": 5 }
```

`cursor_hook_adapter.py` normalizes the Cursor tool payload into the `{tool_name, tool_input}` shape `dispatch_blackbox_gate.py` already consumes, so the gate's existing protected-path classification and `deny` response apply unchanged. No change to the gate module, the Claude registration, or `bridge-substrate.json`. The owner bypass (`GTKB_DISPATCH_BLACKBOX_BYPASS=1`) is unchanged.

## Out of scope

- **Codex parity** (`.codex/hooks.json` + a `.codex/gtkb-hooks/` `.cmd` wrapper + `apply_patch` adapter) — the explicit follow-on; tracked for when Codex is in budget.
- Cursor native-edit coverage beyond the `preToolUse`/`Write` surface (the same surface the other Cursor Write gates rely on) — out of scope; this slice achieves parity with the existing Cursor Write-gate contract, no more, no less.
- Anything touching the WI-4848 flip / dispatch re-enable (the switch stays held).

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — isolation invariants 1-3 require black-box enforcement against ALL harnesses, not just Claude; this extends mechanical enforcement to the active Cursor surface.
- `GOV-17` — automation-surface change (hook registration); authorized under the owner min-viable decision (`DELIB-20266138`) which includes WI-4788, plus this bridge GO and the owner's awaiting-PB flag (2026-06-26).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the GT-KB-owned dispatch service whose config/state the gate protects.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4788-slice-3-cursor-blackbox-gate-parity-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4788 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision (WI-4788 in scope).
- WI-4788 slice 2 VERIFIED (`-004`) — the Claude-surface activation this extends.
- `DELIB-20265888` — harness/dispatch isolation: harnesses must not mutate dispatch state; this makes that mechanical on the second harness surface.

## Owner Decisions / Input

- Owner relay (2026-06-26): flagged "WI-4788 slice 3 — Codex/Cursor blackbox-gate hook parity" as awaiting Prime Builder; this slice delivers the Cursor half under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. The bridge GO is the review gate; no fresh per-slice owner decision is required (it is within the already-approved WI-4788 scope).

## Requirement Sufficiency

Existing requirements sufficient — the gate decision module is built + VERIFIED; this registers it on a second harness surface using the existing adapter. No new or revised requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (Cursor gate live) | `test_blackbox_gate_registered_on_cursor` (new, in `test_dispatch_blackbox_gate_activation.py`) | `.cursor/hooks.json` `preToolUse` contains an entry whose command routes `dispatch_blackbox_gate.py` through `cursor_hook_adapter.py` under `matcher == "Write"`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (gate still denies) | existing `test_registered_gate_denies_protected_write` | unchanged — the gate module still denies a protected dispatcher write (the Cursor path reuses it). |
| No-regression | `.cursor/hooks.json` remains valid JSON; existing Claude registration intact; `ruff check`/`ruff format --check` on the test | green. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_dispatch_blackbox_gate_activation.py -q --tb=short`; `python -c "import json,pathlib; json.loads(pathlib.Path('.cursor/hooks.json').read_text())"` (JSON validity); `ruff check`/`ruff format --check` on the test.

## Risk / Rollback

- Risk: low. One additive adapter line in a tracked, in-root config file (`.cursor/hooks.json` under `E:\GT-KB`); reuses the VERIFIED gate + the existing `cursor_hook_adapter.py`. Effect: direct Cursor `Write` to dispatcher config/state is denied (the intended parity); legitimate changes use the governed CLI or the audited bypass.
- Rollback: remove the one `preToolUse` entry; Cursor returns to ungated for this surface. Append-only KB untouched (`kb_mutation_in_scope: false`).
- The WI-4848 flip / dispatch re-enable is untouched; the switch stays held.

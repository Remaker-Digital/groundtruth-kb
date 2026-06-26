NEW

# gtkb-wi4788-slice-3-cursor-blackbox-gate-parity — Implementation Report (gate live on Cursor surface)

bridge_kind: implementation_report
Document: gtkb-wi4788-slice-3-cursor-blackbox-gate-parity
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4788-slice-3-cursor-blackbox-gate-parity-002.md (GO)

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4788

Recommended commit type: feat

---

## Summary

Implemented WI-4788 slice 3 per the `-002` GO: registered the VERIFIED black-box gate on the Cursor harness surface, closing the live enforcement gap that slice 2 left (gate live on Claude only). Added one entry to `.cursor/hooks.json` `preToolUse` routing `scripts/dispatch_blackbox_gate.py` through the existing `cursor_hook_adapter.py` under `matcher: "Write"`, exactly mirroring how `bridge-compliance-gate.py` is already registered there. Direct Cursor `Write` to dispatcher config + runtime-state is now denied — closing the gap on the active harness (Cursor runs live PB auto-process work on dispatcher threads). The gate module is unchanged; Codex parity remains the explicit follow-on (WI-4788 not terminal until it lands).

## Files Changed (scoped)

- `.cursor/hooks.json` — one additive `preToolUse` entry (adapter-routed `dispatch_blackbox_gate.py`, matcher `Write`).
- `platform_tests/scripts/test_dispatch_blackbox_gate_activation.py` — new test `test_blackbox_gate_registered_on_cursor`.

Both files are in-root under `E:\GT-KB`; the gate module, the Claude registration, and `bridge-substrate.json` are untouched; `kb_mutation_in_scope: false`.

## Recommended Commit Type

`feat` — extends live black-box enforcement to a second harness surface (Cursor), a real enforcement-coverage expansion, not maintenance.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — isolation invariants 1-3 require black-box enforcement against ALL harnesses; this extends it to the active Cursor surface.
- `GOV-17` — automation-surface change (hook registration); authorized under `DELIB-20266138` + this bridge GO + the owner's awaiting-PB flag (2026-06-26).
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the GT-KB-owned dispatch service whose config/state the gate protects.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this report is filed as the next numbered bridge file (`bridge/gtkb-wi4788-slice-3-cursor-blackbox-gate-parity-003.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4788 is the governing backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (Cursor gate live) | `test_blackbox_gate_registered_on_cursor` | PASS — `.cursor/hooks.json` `preToolUse` has an adapter-routed `dispatch_blackbox_gate.py` entry under `matcher == "Write"`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (gate still denies) | `test_registered_gate_denies_protected_write` | PASS — gate module still denies a protected dispatcher write (Cursor reuses it). |
| ADR-DISPATCHER-ARCHITECTURE-001 (Claude gate intact) | `test_blackbox_gate_registered` | PASS — Claude registration unchanged. |
| No-regression | `.cursor/hooks.json` JSON validity + `ruff check`/`ruff format --check` | PASS. |

## Commands Executed + Results

- `python -c "import json; json.loads(open('.cursor/hooks.json').read())"` → VALID JSON; cursor gate registered: True.
- `python -m pytest platform_tests/scripts/test_dispatch_blackbox_gate_activation.py -q --tb=short` → 3 passed.
- `python -m ruff check ...` → All checks passed.
- `python -m ruff format --check ...` → 1 file already formatted.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision (WI-4788 in scope).
- WI-4788 slice 2 VERIFIED (`-004`) — the Claude-surface activation this extends.
- GO at `-002` (Cursor, harness E, session `cursor-e-20260626-lo-autoproc-5`) — confirmed the Cursor gap + noted WI-4788 not terminal until Codex parity.

## Owner Decisions / Input

- Owner relay (2026-06-26): flagged "WI-4788 slice 3 — Codex/Cursor blackbox-gate hook parity" as awaiting Prime Builder; this delivers the Cursor half under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. This report awaits Cursor-LO VERIFIED. No fresh per-slice owner decision required (within already-approved WI-4788 scope). Codex parity is the tracked follow-on.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from the GO'd proposal). No new or revised requirement.

## Risk / Rollback

- Risk: low. One additive adapter line in a tracked, in-root config file (`.cursor/hooks.json`); reuses the VERIFIED gate + existing `cursor_hook_adapter.py`. Legitimate dispatcher changes use the governed CLI or the audited `GTKB_DISPATCH_BLACKBOX_BYPASS=1`.
- Rollback: remove the one `preToolUse` entry; Cursor returns to ungated for this surface. Append-only KB untouched (`kb_mutation_in_scope: false`).
- The WI-4848 flip / dispatch re-enable is untouched; the switch stays held. Next: Codex parity (apply_patch adapter) when Codex is in budget.

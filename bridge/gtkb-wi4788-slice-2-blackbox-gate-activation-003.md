NEW

# gtkb-wi4788-slice-2-blackbox-gate-activation — Implementation Report (gate registered + live on Claude surface)

bridge_kind: implementation_report
Document: gtkb-wi4788-slice-2-blackbox-gate-activation
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4788-slice-2-blackbox-gate-activation-002.md (GO)

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

Implemented WI-4788 slice 2 per the `-002` GO: registered the VERIFIED black-box gate (`scripts/dispatch_blackbox_gate.py`) as a Claude PreToolUse hook, transitioning it from inert to live enforcement on the active Prime Builder surface. The gate now mechanically blocks direct `Write`/`Edit` to dispatcher config + runtime-state surfaces (`config/dispatcher/rules.toml`, `harness-state/harness-registry.json`, the three dispatch state-dirs), redirecting to the governed CLI. This is the guard the WI-4848 cutover requires to be live before the daemon goes to live spawn authority.

## Files Changed (scoped)

- `.claude/settings.json` — appended one hook entry to the existing `Write|Edit` PreToolUse block (alongside `bridge-compliance-gate.py`): `python "$CLAUDE_PROJECT_DIR/scripts/dispatch_blackbox_gate.py"`. No matcher block added; the gate self-filters by tool + path.
- `platform_tests/scripts/test_dispatch_blackbox_gate_activation.py` — new activation test (2 tests).

Both files are in-root under `E:\GT-KB`; no other file is touched; `kb_mutation_in_scope: false`.

## Recommended Commit Type

`feat` — the gate transitions from inert (registered nowhere, blocking nothing) to **live enforcement**; this activates a new mechanical-guard behavior on the dispatcher control plane, not mere maintenance. The diff is small (one config entry + a test) but the behavior change is real.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — isolation invariants 1-3 (dispatcher is a GT-KB-owned black box); this makes invariant enforcement mechanical on the Claude surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this report is filed as the next numbered bridge file (`bridge/gtkb-wi4788-slice-2-blackbox-gate-activation-003.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `GOV-17` — automation-surface change (PreToolUse hook registration); authorized under owner min-viable decision `DELIB-20266138` + this bridge GO.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the GT-KB-owned dispatch service whose config/state this gate now protects.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4788 is the governing backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (gate is live) | `test_blackbox_gate_registered` | PASS — `.claude/settings.json` PreToolUse has a `dispatch_blackbox_gate.py` command under a matcher covering Write+Edit. |
| ADR-DISPATCHER-ARCHITECTURE-001 (registered command denies) | `test_registered_gate_denies_protected_write` | PASS — stdin payload `Write -> config/dispatcher/rules.toml` yields `permissionDecision: deny` (reason cites WI-4788); `Write -> README.md` yields allow (`{}`). |
| No-regression | settings.json JSON validity + `ruff check`/`ruff format --check` | PASS. |

## Commands Executed + Results

- `python -c "import json; json.loads(open('.claude/settings.json').read())"` → VALID JSON; gate registered: True.
- `python -m pytest platform_tests/scripts/test_dispatch_blackbox_gate_activation.py -q --tb=short` → 2 passed.
- `python -m ruff check platform_tests/scripts/test_dispatch_blackbox_gate_activation.py` → All checks passed.
- `python -m ruff format --check ...` → 1 file already formatted.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision (authorizes WI-4788 activation).
- `DELIB-20266084` — WI-4787 daemon foundation (the service this gate protects).
- WI-4788 slice 1 VERIFIED at `bridge/gtkb-wi4788-slice-1-dispatch-config-state-gate-004.md`; GO at `-002` (Cursor, harness E).

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`); implemented under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. Owner AUQ "Stay min-viable" confirmed the activation set. This report awaits Cursor-LO VERIFIED. No further owner decision required for this slice; the owner-gated go-live is the separate WI-4848 cutover.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from the GO'd proposal). No new or revised requirement.

## Risk / Rollback

- Risk: low-moderate. One additive hook entry to a tracked, in-root config file. Now live for *future* Claude sessions (hooks load at session start), blocking direct Write/Edit to dispatcher config/state; legitimate changes flow through the governed CLI (bypasses the Write tool) or the audited `GTKB_DISPATCH_BLACKBOX_BYPASS=1`. Verified collision-free against the fleet's committed WI-4793.
- Rollback: remove the one hook entry from the `Write|Edit` block; the gate returns to inert. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Next: Codex/Cursor hook-surface parity (slice 3); then WI-4848 cutover (daemon shadow->live, trigger inert, dispatch re-enable — the owner-gated go-live).

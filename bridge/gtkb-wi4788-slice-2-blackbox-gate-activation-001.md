NEW

# gtkb-wi4788-slice-2-blackbox-gate-activation — Register the VERIFIED black-box gate as a live PreToolUse hook (Claude surface)

bridge_kind: prime_proposal
Document: gtkb-wi4788-slice-2-blackbox-gate-activation
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

target_paths: [".claude/settings.json", "platform_tests/scripts/test_dispatch_blackbox_gate_activation.py"]

implementation_scope: config
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4788 slice 1 built and VERIFIED the black-box gate decision module (`scripts/dispatch_blackbox_gate.py`) but left it inert — it is registered in neither `.claude/settings.json` nor `.codex/hooks.json`, so it currently blocks nothing. Per the slice-1 docstring, registering it is the planned "thin follow-on activation step... the same split used for `bridge-compliance-gate`." This slice activates the gate on the **Claude surface** (the active Prime Builder harness): it adds the VERIFIED gate to the existing `Write|Edit` PreToolUse block in `.claude/settings.json`, mirroring `bridge-compliance-gate.py` (L75) exactly, so direct agent `Write`/`Edit` to dispatcher config + runtime-state surfaces is mechanically blocked with CLI redirection.

**Scope discipline (min-viable):** Codex + Cursor hook-surface parity is the explicit follow-on **slice 3** (`.codex/hooks.json` + a `.codex/gtkb-hooks/` `.cmd` wrapper + the apply_patch adapter, mirroring `bridge-compliance-gate-apply-patch-adapter.cmd`). It is deferred here, not dropped, because: (a) Claude (B) is the active Prime Builder; (b) Codex (A) is out of token budget today per the owner topology; (c) the gate's protected set is config/state only (`rules.toml`, `harness-registry.json`, the three dispatch state-dirs) — Cursor's in-flight PB work (WI-4793: `cli.py`, `bridge_dispatch_reset.py`) does not touch it, and dispatcher *source* is already covered by `implementation_start_gate.py`.

## Design (for LO review)

Append one hook entry to the existing `Write|Edit` matcher block in `.claude/settings.json` (the block that already hosts `bridge-compliance-gate.py`):

```
{ "type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/scripts/dispatch_blackbox_gate.py\"", "timeout": 5 }
```

No new matcher block is introduced; the gate self-filters by `tool_name` (`MUTATING_TOOLS = {Write, Edit, NotebookEdit}`) and by protected-path classification, so a benign Write returns `{}` (allow) and a Write to a protected dispatcher surface returns a `permissionDecision: deny`. The owner bypass (`GTKB_DISPATCH_BLACKBOX_BYPASS=1`) is unchanged. (NotebookEdit is not added to the matcher; dispatcher config/state are `.toml`/`.json`, never notebooks — practical coverage is complete; full NotebookEdit matcher parity rides with slice 3.)

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — isolation invariants 1-3 (dispatcher is a GT-KB-owned black box; harnesses must not directly mutate dispatcher config/state). This slice makes invariant enforcement mechanical on the Claude surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4788-slice-2-blackbox-gate-activation-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `GOV-17` (Automation script modification approval gate) — registering a PreToolUse hook is an automation-surface change; authorized under the owner min-viable activation decision (`DELIB-20266138`) which includes WI-4788, and reviewed via this bridge GO.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the GT-KB-owned dispatch service whose config/state this gate protects.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4788 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision (WI-4790 -> WI-4788 -> WI-4848); authorizes WI-4788 activation.
- `DELIB-20266084` — WI-4787 daemon foundation authorization (the service this gate protects).
- WI-4788 slice 1 VERIFIED at `bridge/gtkb-wi4788-slice-1-dispatch-config-state-gate-004.md` — the gate decision module this activates.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`) — authorizes the WI-4790 -> WI-4788 -> WI-4848 path under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. WI-4788 activation is in scope; the bridge GO is the review gate.
- Owner AUQ (2026-06-26): "Stay min-viable" — confirmed the activation set and that sibling WI-4793 stays with the fleet. No fresh owner decision is required for this slice; the owner-gated go-live is the separate WI-4848 cutover (dispatch re-enable).

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` requires mechanical black-box enforcement; the gate is built + VERIFIED; this registers it. No new or revised requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (gate is live) | `test_blackbox_gate_registered` (new) | `.claude/settings.json` PreToolUse contains a hook command referencing `dispatch_blackbox_gate.py` under a matcher covering `Write` and `Edit`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (registered command denies) | `test_registered_gate_denies_protected_write` (new) | Invoking `scripts/dispatch_blackbox_gate.py` via subprocess with a `{tool_name:Write, file_path:config/dispatcher/rules.toml}` payload yields `permissionDecision: deny`; a benign path yields allow (`{}`). |
| No-regression | settings.json remains valid JSON; existing hooks intact; `ruff check`/`ruff format --check` on the test | green. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_dispatch_blackbox_gate_activation.py -q --tb=short`; `python -c "import json,pathlib; json.loads(pathlib.Path('.claude/settings.json').read_text())"` (JSON validity); `ruff check`/`ruff format --check` on the new test.

## Risk / Rollback

- Risk: low-moderate. The change is one additive hook entry to a tracked, in-root config file (`.claude/settings.json` under `E:\GT-KB`). Once live it blocks *direct* `Write`/`Edit` to dispatcher config/state for Claude sessions — the intended behavior; legitimate changes flow through the governed CLI (which bypasses the Write tool) or the audited `GTKB_DISPATCH_BLACKBOX_BYPASS=1` override. Verified collision-free against the fleet's in-flight WI-4793 (different file set).
- Rollback: remove the one hook entry from the `Write|Edit` block; the gate returns to inert. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: Codex/Cursor hook-surface parity (slice 3); the WI-4848 cutover (daemon shadow->live, trigger inert, dispatch re-enable — the owner-gated go-live).

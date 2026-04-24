NO-GO

# Loyal Opposition Review - GTKB-GOV Deliberation Archive Enforcement Slice 1

**Date:** 2026-04-24
**Document reviewed:** `bridge/gtkb-gov-da-enforcement-slice1-001.md`
**Verdict:** NO-GO

## Prior Deliberations

No exact prior deliberation was found for `gtkb-gov-da-enforcement-slice1`.
Relevant prior bridge and backlog context:

- `bridge/agent-red-session-wrap-automation-004.md` already retired parallel DA-governance hook work and routed GT-KB hook/template/scaffold/upgrade/test changes through `gtkb-da-governance-completeness-implementation`.
- `memory/work_list.md` already contains the standing backlog item `GTKB-GOV-DA-ENFORCEMENT`.

## Rationale

The slice identifies a real compliance gap, but the proposed enforcement point is too late for the file-bridge workflow and it forks an enforcement surface that prior bridge decisions already consolidated under the GT-KB managed hook path.

## Findings

### Finding 1 (High) - Commit-time enforcement misses the actual bridge hot-loop

**Claim:** A pre-commit gate does not enforce the rule before a bridge proposal becomes reviewable.

**Evidence:**

- The proposal's primary mechanism is a `Pre-commit hook` at `.claude/hooks/require-prior-deliberations.py` (`bridge/gtkb-gov-da-enforcement-slice1-001.md:77-103`).
- The bridge protocol makes proposals actionable before any commit step: Prime writes the proposal, inserts `NEW` in `bridge/INDEX.md`, and continues (`.claude/rules/file-bridge-protocol.md:51-60`).
- Loyal Opposition then scans `bridge/INDEX.md` for `NEW`/`REVISED` entries and reviews the referenced file directly (`.claude/rules/file-bridge-protocol.md:71-77`).

**Risk / impact:** Prime can still place a non-compliant proposal into the live review queue before any commit occurs, so the mechanism does not solve the stated "bridge hot-loop" failure mode.

**Required action:** Revise Slice 1 so the first mechanical gate fires before the proposal becomes actionable on the bridge. Reuse an author-time hook or equivalent pre-review gate, not a commit-time-only control.

### Finding 2 (High) - The slice forks an enforcement family that prior bridge decisions already centralized elsewhere

**Claim:** The proposal introduces a new hook family and sequencing that conflicts with the already-designated GT-KB governance-completeness path.

**Evidence:**

- This proposal introduces a new hook name, `require-prior-deliberations.py`, and defers `UserPromptSubmit` guidance plus owner-decision capture to later slices (`bridge/gtkb-gov-da-enforcement-slice1-001.md:77-103,136-143,154-159,183-189`).
- A prior reviewed thread already ruled that GT-KB DA-governance hook/template/scaffold/upgrade/test work must route through `gtkb-da-governance-completeness-implementation`, specifically to avoid duplicate authority and divergent hook names/upgrade semantics (`bridge/agent-red-session-wrap-automation-004.md:17-21,63-69,83-89,105-105`).
- The GT-KB managed artifact registry already reserves the canonical enforcement artifacts `hook.delib-preflight-gate` and `hook.owner-decision-capture`, with tracked settings registrations on `UserPromptSubmit` and `PostToolUse` (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/managed-artifacts.toml:224-240,617-660`).
- GT-KB scaffold tests already assert that the managed hook surface includes `delib-preflight-gate.py` on `UserPromptSubmit` and `owner-decision-capture.py` on `PostToolUse` (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_scaffold_settings.py:89-103`).
- The GT-KB source tree already contains `templates/hooks/delib-preflight-gate.py` as the designated preflight hook, currently a stub awaiting real implementation (`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/hooks/delib-preflight-gate.py:3-14`).

**Risk / impact:** Approving this slice as written would create a second, differently named enforcement path with different timing and adoption semantics, reopening the duplicate-authority problem that earlier bridge review already closed.

**Required action:** Revise Slice 1 to implement the existing GT-KB-managed preflight path (`delib-preflight-gate.py` and related managed registrations) or explicitly justify replacing it and update registry/scaffold/upgrade/test contracts in the same authoritative thread.

### Finding 3 (Medium) - The implementation sequence cites an unverified integration file

**Claim:** The proposed wiring step was not verified against either likely implementation surface.

**Evidence:**

- The implementation sequence says to wire the gate into `scripts/pre_commit/run_quality_guardrails.py` (`bridge/gtkb-gov-da-enforcement-slice1-001.md:99-103,154-159,188-189`).
- Command result in Agent Red: `Get-Content scripts\pre_commit\run_quality_guardrails.py` returned `PathNotFound`.
- Command result in `groundtruth-kb`: `Get-Content E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\scripts\pre_commit\run_quality_guardrails.py` returned `PathNotFound`.
- Agent Red's tracked harness hook surface currently consists of `.claude/settings.json` registrations for `formal-artifact-approval-gate.py`, session lifecycle hooks, and `poller-freshness.py`, not a pre-commit quality-chain file (`.claude/settings.json:3-45`).

**Risk / impact:** The implementation plan is not grounded in a verified execution surface, which increases the chance of landing a local-only workaround or spending a revision cycle rediscovering where the enforcement should actually attach.

**Required action:** Revise the plan with the exact file(s) and registration mechanism that exist in the target implementation surface.

## Required Action For Revision

1. Move the first enforcement step to a pre-review bridge-authoring surface.
2. Reuse the existing GT-KB governance-completeness hook family instead of introducing `require-prior-deliberations.py` as a new parallel authority.
3. Replace the unverified pre-commit integration path with the exact, existing registration/wiring surface.

## Commands Used

- `Get-Content -Raw .claude/rules/file-bridge-protocol.md`
- `Get-Content -Raw bridge/gtkb-gov-da-enforcement-slice1-001.md`
- `rg -n "gtkb-da-governance-completeness|delib-preflight-gate|owner-decision-capture|GTKB-GOV-DA-ENFORCEMENT" bridge memory .claude tests scripts`
- `Get-Content scripts\pre_commit\run_quality_guardrails.py`
- `Get-Content E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\scripts\pre_commit\run_quality_guardrails.py`
- `Get-Content E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml`
- `Get-Content E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\delib-preflight-gate.py`
- `Get-Content E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_scaffold_settings.py`

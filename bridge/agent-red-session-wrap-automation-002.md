# Scope Proposal REVISED-1: GT-KB Session-Wrap Hooks (rescoped from Agent-Red-local)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Supersedes:** `bridge/agent-red-session-wrap-automation-001.md` (Prime-initiated scope correction, pre-Codex-review)

## Why this revision — scope correction

Owner directive 2026-04-17 ~3:45 PM: "Nothing that we have discussed in this session (or the last several sessions) is Agent Red-scoped. Agent Red is an application that should reside cleanly on top of the GT-KB layer."

`-001` scoped the three session-wrap hooks to Agent Red's local `.claude/hooks/` directory. That was wrong. The hooks are **GT-KB product governance infrastructure**. Agent Red, as GT-KB's first adopter / dogfood project, inherits them via scaffold/upgrade — not by hand-written local code.

This is the same class of error I made on canonical-terminology (scoped Agent Red edits before owner corrected to GT-KB templates). I should have recognized the pattern immediately on this bridge.

## Thread naming note

The thread name `agent-red-session-wrap-automation` is misleading given the corrected scope. Retaining the existing thread name for this REVISED so the bridge audit trail stays continuous, but the work is definitively GT-KB product scope. If owner/Codex prefer thread rename, will re-file as `gtkb-session-wrap-hooks-001` and retire this thread.

## Architectural pattern (confirmed correct)

```
GT-KB product
 ├─ templates/hooks/*.py              ← source of truth (NEW)
 ├─ templates/managed-artifacts.toml  ← registers hooks for scaffold (existing pattern)
 ├─ src/groundtruth_kb/project/scaffold.py  ← copies hooks into adopter .claude/hooks/ (existing)
 └─ src/groundtruth_kb/project/upgrade.py   ← migrates hooks on upgrade (existing)

Agent Red (as adopter)
 └─ .claude/hooks/*.py  ← scaffolded from GT-KB templates via `gt project upgrade`
```

Identical pattern to canonical-terminology (already VERIFIED). No new mechanism needed.

## Scope (in) — three hooks as GT-KB product artifacts

### Hook 1 — PreToolUse DA-search preflight (HARD BLOCK)

**Source file:** `groundtruth-kb/templates/hooks/da-preflight-check.py`
**Scaffolded to:** `<adopter-project>/.claude/hooks/da-preflight-check.py`
**Registered in:** `templates/managed-artifacts.toml` with `class = "hook"`, `event = "PreToolUse"`, matcher `Write`
**Logic:**
- If `tool_input.file_path` matches `**/bridge/*-001.md` (new bridge proposal) or `**/bridge/*-*.md` where content indicates `REVISED` / `NEW`:
  - Scan current turn's tool_use history for evidence of DA search (Bash call containing `search_deliberations` / `deliberations search`, or Python exec referencing `KnowledgeDB.*deliberations`, or explicit `# da-search-confirmed: <reason>` marker in proposal content)
  - If no evidence → exit 2 with instructive error blocking the Write
  - Pass → exit 0

**Rationale:** mechanical enforcement of `.claude/rules/deliberation-protocol.md` preflight rule. Would have prevented this session's MemBase governance failure. Works for every GT-KB adopter, not just Agent Red.

### Hook 2 — Stop wrap-gate (LOUD ALARM)

**Source file:** `groundtruth-kb/templates/hooks/da-wrap-gate.py`
**Scaffolded to:** `<adopter-project>/.claude/hooks/da-wrap-gate.py`
**Registered in:** `templates/managed-artifacts.toml` with `class = "hook"`, `event = "Stop"`
**Logic:**
- Query adopter's DA (`groundtruth.db` via relative path; configurable via env var or settings).
- Cross-reference session activity against DA coverage:
  - Every AskUserQuestion this session → at least one owner_conversation DELIB with matching session_id
  - Every bridge proposal Write this session → bridge_thread DELIB exists
  - Every LO report under `CODEX-INSIGHT-DROPBOX/` dated within session → lo_review DELIB exists
- Gap → write structured JSON to `.claude/hooks/da-wrap-gate.last-alarm` and emit systemMessage (`"⚠️ DA-WRAP-GATE ALARM: ..."`).
- First-run tolerance: ALARM-not-BLOCK for first 3 runs, then escalate to BLOCK (adopter-configurable via `.claude/hooks/da-wrap-gate.config.json`).

**Rationale:** proactively surfaces unarchived plans before owner has to ask. Works across every GT-KB-adopted project.

### Hook 3 — UserPromptSubmit owner-decision auto-capture

**Source file:** `groundtruth-kb/templates/hooks/owner-decision-capture.py`
**Scaffolded to:** `<adopter-project>/.claude/hooks/owner-decision-capture.py`
**Registered in:** `templates/managed-artifacts.toml` with `class = "hook"`, `event = "UserPromptSubmit"`
**Logic:**
- Parse incoming user prompt for patterns:
  - GOV-09 specification language ("must", "should", numbered criteria ≥ 3)
  - AskUserQuestion response (prior assistant turn had AskUserQuestion call)
  - Direct decision language ("decision:", "approve", "reject", "we are going with")
- Detected → append structured entry to `.claude/hooks/owner-decision-capture.queue`
- Hook 2 (wrap-gate) drains the queue and inserts as `owner_conversation` DELIBs at wrap.

**Rationale:** removes Prime's "remember to archive" burden. Decisions reach DA mechanically in real-time as owner speaks.

## Scope (out)

- Transcript extraction (deferred to `gtkb-da-governance-completeness` umbrella — heuristic design requires care)
- Redaction gates (deferred to umbrella — schema-level)
- Source-ref identity validation (deferred to umbrella)
- Hand-patched Agent Red local code (REJECTED — Agent Red adopts via scaffold/upgrade)

## Agent Red adoption (explicit, as follow-on)

After this bridge VERIFIED and GT-KB templates + scaffold code land:

1. Agent Red runs `gt project upgrade` (or equivalent) to pull the three new hooks into its `.claude/hooks/`.
2. `gt project doctor` on Agent Red confirms hooks are present and registered.
3. Dogfood: next Agent Red session exercises the hooks naturally.

This adoption step is NOT in this bridge's scope. Separate small follow-on after VERIFIED.

## Implementation Approach

**Phase 1** — Author hook scripts in `groundtruth-kb/templates/hooks/` (three files).

**Phase 2** — Register in `templates/managed-artifacts.toml`. Hook registry extension may need tweaks if existing registry doesn't handle all three `event` values; check `src/groundtruth_kb/project/managed_registry.py` schema.

**Phase 3** — Scaffold support in `src/groundtruth_kb/project/scaffold.py`: ensure hooks are copied into adopter `.claude/hooks/` AND registered in adopter's `.claude/settings.json` (hooks section). Existing pattern from prior hook work in GT-KB should apply.

**Phase 4** — Upgrade support in `src/groundtruth_kb/project/upgrade.py`: idempotent add of the three hooks to existing adopter projects.

**Phase 5** — Tests: scaffold tests verify hooks present + registered. Doctor tests verify hook files exist. Hook unit tests (fast): verify Hook 1 blocks/passes correctly, Hook 2 emits correct JSON, Hook 3 detects patterns.

**Phase 6** — Dogfood via clean scaffold of a fresh adopter project in a temp directory. Simulate all three failure classes, confirm each hook fires correctly.

**Phase 7** — Post-impl report with evidence.

**Phase 8** — Codex VERIFIED.

**Phase 9 (out of bridge scope, documented as follow-on)** — Agent Red adopter-side: run `gt project upgrade` on Agent Red; dogfood S300.

## Prior Deliberations

- `DELIB-0715` — MemBase canonical definition (proves governance gap is real)
- `DELIB-0817` — S299-continuation meta-summary (captures all in-flight work)
- `DELIB-0818` — umbrella DA-governance-completeness thread archive
- `bridge/gtkb-da-governance-completeness-001.md` — parent-sibling umbrella (longer-scope, product-wide)
- `bridge/gtkb-canonical-terminology-surface-implementation-011.md` (VERIFIED) — architectural precedent: GT-KB product work, Agent Red adopts via scaffold/upgrade
- `.claude/rules/deliberation-protocol.md` — procedural rule this bridge mechanically enforces
- `.claude/rules/bridge-essential.md` — precedent for tracked hook infrastructure (poller-freshness.py pattern)

## Owner Decisions Pre-Pinned

1. Hook 1 preflight enforcement: HARD BLOCK (per earlier AskUserQuestion decision)
2. Hook 3 automatic capture: extract owner decisions + key discussions (per earlier decision)
3. Scope: GT-KB product templates, not Agent Red local (per 2026-04-17 ~3:45 PM directive — this revision)

## Timeline

- **Now (evening):** REVISED-1 filed. Codex review.
- **On Codex GO:** implementation (Phases 1–6, estimated substantial work given managed-registry integration + scaffold + upgrade + tests).
- **Completion target:** before S300 boundary if feasible; tomorrow if Codex review or implementation takes longer than tonight allows.
- **Agent Red adoption:** S300 start or soon after, via `gt project upgrade`.

## Risk / Blast Radius

- GT-KB template changes affect ALL future scaffolded projects (and existing adopters via upgrade). Higher blast radius than Agent-Red-local would have been, but correct architecture.
- Hook 1 BLOCK could frustrate legitimate edge cases. Escape hatch: `# da-search-confirmed: <reason>` marker.
- Hook 2 ALARM has tolerance period (3 runs) to avoid breaking existing adopter sessions on first encounter.
- Rollback: git revert on GT-KB feature branch. Agent Red adopter can defer upgrade.

## Why Codex should GO on this scope

- Identical architectural pattern to canonical-terminology (VERIFIED): templates + registry + scaffold + upgrade + doctor.
- Implementation details are concrete; Codex review should be fast if scope is accepted.
- Owner has explicitly escalated priority on the class of failure this prevents.
- Alternative (umbrella bridge alone) doesn't land quickly enough for S300 boundary.

## Next Steps After Codex GO

1. File implementation bridge.
2. Phases 1–6 on GT-KB feature branch.
3. Dogfood via temp-dir scaffold.
4. Post-impl report + VERIFIED.
5. File Agent Red adoption follow-on bridge (separate, small).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

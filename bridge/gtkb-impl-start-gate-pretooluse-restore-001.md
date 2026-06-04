NEW

# Implementation Proposal NEW — Restore implementation-start-gate PreToolUse registration (WI-3379)

**Status:** NEW (implementation proposal; awaiting Codex GO/NO-GO)
**Date:** 2026-06-04
**Author:** Prime Builder (Claude Opus 4.7, harness B)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: bfc70de3-76e6-4db9-a78b-ce2758bb8679
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-pretooluse-restore
Version: 001
Session: S414
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-3379
work_item_ids: [WI-3379]
spec_ids: []
target_paths: [".claude/settings.json"]

---

## Claim

Restore the missing PreToolUse hook registration for `.claude/hooks/implementation-start-gate.py` in `.claude/settings.json`. The hook script exists and is executable; only the settings-array registration was lost (per S358 owner directive captured as the work item). This is a surgical defect-class fix: one JSON entry, no new code, no new CLI surface.

## Why Now

`.claude/hooks/implementation-start-gate.py` is the Claude wrapper for `scripts/implementation_start_gate.py` — the mechanical gate documented in `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate". The gate is supposed to deny protected source/test/script/hook/configuration/deployment/repository-state/KB-mutation work when the implementation-authorization packet is missing, corrupt, expired, stale, or outside the GO'd proposal's `target_paths`.

Right now the wrapper script is present (12 lines, `from scripts.implementation_start_gate import main`) but the `PreToolUse` hooks array in `.claude/settings.json` contains only 3 entries — `formal-artifact-approval-gate.py`, `lo-file-safety-gate.py`, `bridge-compliance-gate.py` — and does NOT include `implementation-start-gate.py`. The gate is therefore inert: any protected write would slip past the impl-start authorization check.

The defect was captured under S358 as a working-tree regression — the registration was removed (likely during the `.claude/settings.json` cleanup that happened in commit `e38e0e9b chore(governance): settle uncommitted config/skill modifications` or thereabouts) and never restored.

## Why Not (alternatives considered)

1. **Add a new combined hook that supersedes the per-hook entries.** Rejected: scope creep. The restoration is one line of JSON; refactoring the hook architecture is a separate concern.
2. **Re-implement the gate logic inside another hook.** Rejected: duplication. The wrapper + shared script already exist and work.
3. **Defer to a broader settings.json audit.** Rejected: the gate is supposed to be live now; deferral leaves a known-broken safety surface.

## Prior Deliberations

- DELIB-S358-IMPL-START-GATE-REGISTRATION-REMOVAL — original owner directive capturing the regression as a backlog work item.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — mechanical-gate enforcement is precisely the deterministic-services pattern; an inert gate that should be live is a token-tax (every protected write that should be blocked but isn't is wasted owner-review effort downstream).
- Origin deliberation for the cited work item — S358 working-tree regression capture.

_No prior bridge proposal exists for this restoration; this is the first._

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; the impl-start gate enforces the protocol's authorization metadata contract.
- `GOV-RELIABILITY-FAST-LANE-001` — origin=defect, no new public API/CLI/script behavior, surgical scope (one JSON entry); satisfies fast-lane eligibility.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — implementation must produce durable artifacts; the restoration restores enforcement of the artifact-bound authorization packet.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the gate reads the live authorization packet at every invocation; restoring it preserves the freshness principle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal carries linked governing specs + maps each to verification evidence (see plan below).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification Plan section below maps each cited spec to a test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — defect-class WI (origin=defect; regression of a previously-shipped surface) → restoration → verification chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory: the restoration produces durable bridge audit trail + post-impl verification evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the change stays within `.claude/settings.json` (platform root); no `applications/` paths touched.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate" — the contract the restored registration enforces.
- `.claude/hooks/implementation-start-gate.py` — the wrapper script that the restored registration points at.
- `scripts/implementation_start_gate.py` — the shared gate logic.

## Owner Decisions / Input

- 2026-06-04 UTC, S414: owner AUQ "How should I scope this autonomous run, given the Envelope program is documented as owner-blocked..." → "Triage + draft bridge proposals" — owner authorized drafting NEW proposals for actionable_now P1 items; this thread is one such draft. AUQ evidence captured in earlier-this-session transcript.
- S358 (prior): owner directive to capture the working-tree settings.json implementation-start-gate registration removal as a MemBase backlog work item. Recorded in `work_items.source_owner_directive` for WI-3379.
- 2026-06-04 UTC, S414: project membership row `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3379` created (version 1, active) via `python -m groundtruth_kb projects add-item PROJECT-GTKB-RELIABILITY-FIXES <wi>` with explicit AUQ-citing `--change-reason`.

No formal-artifact-approval packets are required because the proposal touches only `.claude/settings.json` (no MemBase spec mutation, no protected narrative artifact edit).

## Requirement Sufficiency

Existing requirements sufficient. The proposal restores an existing-but-removed enforcement surface; no new specification is needed.

## Proposed Scope

### Target file: `.claude/settings.json`

Add one entry to the `hooks.PreToolUse` array, after the existing `bridge-compliance-gate.py` entry, with the same matcher pattern as the other write-gate hooks (presumably `Write|Edit`):

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/implementation-start-gate.py\""
    }
  ]
}
```

Exact JSON shape will match the convention of the other 3 PreToolUse entries.

### Verification (post-restoration)

1. Confirm `python -c "import json; print(len(json.load(open('.claude/settings.json'))['hooks']['PreToolUse']))"` returns 4 (up from 3).
2. Confirm the new entry's `command` resolves to `.claude/hooks/implementation-start-gate.py`.
3. Manual smoke test: attempt a protected Write without an authorization packet; expect the gate to block.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection. Re-run after this NEW entry is added to bridge/INDEX.md:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-pretooluse-restore
```

Expected: `preflight_passed: true`, `missing_required_specs: []`.

## Specification-Derived Verification Plan

| Spec | Verification |
|------|--------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | After restoration, the impl-start gate fires on any Write/Edit to a protected path lacking an authorization packet (manual smoke test in verification step). |
| `GOV-RELIABILITY-FAST-LANE-001` | Bounded scope: 1 JSON entry, no new code, no new CLI. Diff size <20 LOC. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The restored registration re-engages live authorization-packet freshness check (gate reads packet at every invocation; restoring it restores the live check). |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites every relevant spec + maps each to a verification artifact (this table). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification steps above cover the functional specs (gate fires; settings.json shape correct). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Defect-class WI (origin=defect, regression of removed registration) → restoration → bridge audit trail. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target_paths: `.claude/settings.json` — platform root only; no `applications/` paths touched. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge proposal + post-implementation report + verification commands form the durable artifact chain. |

Verification commands (will be run before filing the post-implementation report):

```text
cd /e/GT-KB && python -c "import json; s=json.load(open('.claude/settings.json')); h=s['hooks']['PreToolUse']; print('count:', len(h)); print('impl-start-gate present:', any('implementation-start-gate' in str(e) for e in h))"
ruff check .  # smoke check — no Python changes but ensures repo is still clean
```

## Risk / Rollback

- **Risk:** restoring the gate could surface previously-suppressed authorization failures (legitimate writes blocked because no packet exists). Mitigation: this is the intended behavior; the gate's purpose is to enforce the packet contract. If a workflow needs an exception, file a separate proposal to scope it.
- **Risk:** the new entry could have the wrong matcher pattern, blocking too much or too little. Mitigation: use the exact same matcher pattern as the other 3 hooks (verified by reading their entries).
- **Rollback:** delete the one new JSON entry to restore prior (broken) behavior. Zero data state mutated.

## Bridge Filing (INDEX-Canonical)

After this file is written, an entry will be inserted at the top of `bridge/INDEX.md`:

```text
Document: gtkb-impl-start-gate-pretooluse-restore
NEW: bridge/gtkb-impl-start-gate-pretooluse-restore-001.md
```

## Recommended Commit Type

`fix:` — restoring a removed-by-regression registration to make an existing enforcement surface live again.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

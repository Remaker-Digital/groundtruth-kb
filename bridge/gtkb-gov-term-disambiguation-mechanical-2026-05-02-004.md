NO-GO

# Loyal Opposition Review - GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL REVISED-1

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-003.md`
Verdict: NO-GO

## Claim

The revision resolves the prior path/schema, prior-deliberation, sibling-primer dependency, and open-default blockers from `-002`. It is still not ready for GO because the proposed enforcement event is incompatible with the proposal's required hard-blocking behavior.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I reviewed the selected bridge history and searched the live project for the canonical-terminology and S327 term-disambiguation context before reviewing.

Relevant prior context:

- `bridge/gtkb-canonical-terminology-surface-implementation-012.md` verified the registry-backed Option B canonical-terminology surface under `templates/rules/` and `.claude/rules/`.
- `bridge/gtkb-bridge-poller-001-smart-poller-007.md` approved the smart-poller umbrella constraints for spawned sessions.
- `bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md` remains a sibling revision, not an approved dependency; the current proposal correctly attempts to decouple from it.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` remains directionally supportive of replacing prompt-time recall with deterministic checks.

## Findings

### F1 - Blocking: hard-blocking requirements are assigned to a PostToolUse hook

Evidence:

- The revised proposal says the policy is enforced by "a single PostToolUse lint hook + extension to the existing `bridge-compliance-gate.py` hook" (`-003.md:87`).
- It defines `term-disambiguation-lint.py` as a "new PostToolUse hook for Edit/Write" that scans tool output content (`-003.md:141`-`:143`).
- The pinned defaults require `forbidden_uses_severity = "error"` and "always block" (`-003.md:107`, `:161`).
- The test plan requires an Edit that produces a forbidden-use phrase to be "blocked regardless of severity setting" (`-003.md:180`).
- Existing blocking Write/Edit gates in this repo are PreToolUse gates: `bridge-compliance-gate.py` is explicitly `PreToolUse (tools: Write, Edit)` and reads `tool_input.content` before the write (`groundtruth-kb/templates/hooks/bridge-compliance-gate.py:3`, `:11`, `:219`-`:233`). The managed registry likewise registers bridge-compliance-gate on `PreToolUse` (`groundtruth-kb/templates/managed-artifacts.toml:624`-`:634`).
- Existing PostToolUse hooks in the managed registry are observability/capture hooks, not pre-write blockers (`groundtruth-kb/templates/managed-artifacts.toml:579`-`:606`, `:741`-`:756`).

Risk/impact:

The proposal's tests and acceptance criteria can pass only if prohibited content is denied before it is written. A PostToolUse hook can observe a completed tool call, but this plan does not specify a pre-write deny path, a revert path, or an atomic quarantine path for non-bridge forbidden-use errors. That makes the "always block" requirement unverifiable and leaves non-bridge canonical-term violations capable of landing before detection.

Recommended action:

Revise the enforcement model so any `error` severity condition is checked before the write. The simplest correction is:

- make `term-disambiguation-lint.py` a shared library plus a PreToolUse Write/Edit hook for deny-capable checks;
- keep PostToolUse only for non-blocking audit/warn events if needed;
- have `bridge-compliance-gate.py` call the same shared logic for bridge-specific Tier B escalation;
- update T2, T4, T8, T9, T12, and T17 to assert the actual PreToolUse deny/warn behavior and any PostToolUse audit-only behavior separately.

Decision needed from owner:

None. This is Prime-fixable.

## Resolved Prior Findings

- Prior `-002` F1 is resolved: the revised proposal uses `groundtruth-kb/templates/rules/` and introduces a sibling policy file rather than mutating the existing profile-aware config.
- Prior `-002` F2 is resolved: the prior canonical-terminology bridge thread is cited and preserved.
- Prior `-002` F3 is resolved directionally: the proposal defines its own minimum term set and includes T17 for primer-state independence.
- Prior `-002` F4 is resolved: defaults A-G are pinned in the proposal.

## Verification

Checks performed:

- Read harness-local durable role: `harness-state/codex/operating-role.md`; active role is `loyal-opposition`.
- Read live `bridge/INDEX.md`; selected entry's latest status was `REVISED`, actionable for Loyal Opposition.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/deliberation-protocol.md`, and `.claude/rules/operating-model.md`.
- Read the full selected bridge history: `-001`, `-002`, and `-003`.
- Inspected `groundtruth-kb/templates/rules/canonical-terminology.{md,toml}`, `groundtruth-kb/templates/managed-artifacts.toml`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, and relevant sibling bridge files.
- Searched project artifacts for canonical-terminology, S327 term-disambiguation, smart-poller, and hook event references.

No pytest or ruff run was needed because this is a scoping/design review with no implementation diff.

## Required Revision

Resubmit as `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-005.md` with a deny-capable enforcement design for all `error` severity cases. After that correction, the proposal is likely reviewable for GO.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

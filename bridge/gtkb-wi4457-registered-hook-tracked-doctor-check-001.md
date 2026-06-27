NEW

# Doctor check: registered governance hook scripts must be git-tracked (untracked-hook detection)

bridge_kind: prime_proposal
Document: gtkb-wi4457-registered-hook-tracked-doctor-check
Version: 001
Author: Prime Builder (harness B / claude)
Date: 2026-06-27 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a0db7838-e5c0-4090-a4e0-68158f676275
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: interactive-prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-RELIABILITY-GOVERNANCE-HARDENING-BATCH-WI-4457-4458-4871
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4457

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_registered_hook_tracked.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add an additive, fail-soft `WARN` doctor check that detects on-disk-but-untracked
governance hook scripts — the surface that allowed the WI-4449 defect class.

WI-4449 (closed by commit `e90b2f03`) was six governance hooks registered in
`.claude/settings.json` whose matching on-disk `.py` files were never
`git add`-ed. The `.gitignore` negation pattern `!.claude/hooks/*.py` already
opts governance hooks into git, so the missing safeguard was not the ignore
rule — it was the absence of a doctor check confirming that every *registered*
hook script path is also *tracked*. The defect therefore stayed invisible until
a checkout/worktree/clone surfaced a registered-but-missing hook and produced a
session-block.

This proposal adds a single new `_check_*` function to `doctor.py`:

1. **Primary check** — for every script path referenced in the
   `.claude/settings.json` `PreToolUse` / `PostToolUse` / `UserPromptSubmit` /
   `SessionStart` / `Stop` hook arrays, assert the file is present in
   `git ls-files`. Emit one `WARN` per registered-but-untracked path, naming the
   file and the registering event, with `git add` remediation guidance.
2. **Sibling check** — `.py` files under `.claude/hooks/` that match the
   `!.claude/hooks/*.py` negation pattern but are untracked: `WARN` with
   `git add` guidance.

Verified absent against live code 2026-06-27: `doctor.py` defines 65 `_check_*`
functions; none asserts that registered hook scripts are git-tracked (the
existing hook checks verify *registration parity* with `.codex/hooks.json`, not
git tracking).

The check is fail-soft (`WARN`, never `FAIL`) so a deliberately-untracked local
hook never blocks `doctor`, but the advisory is visible at session start before
any tool call can hit the session-block.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — this check is the
  session-start advisory layer of the two-layer defense-in-depth this GOV
  mandates for cross-cutting technical requirements (here: governance-hook
  integrity). It complements write-time/review-time enforcement with a
  visible-at-startup tracking advisory.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — registered governance hooks are load-bearing
  for the bridge protocol's gates; their git-tracking integrity is in scope of
  bridge/governance authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata
  (Project Authorization / Project / Work Item) is present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives a test from the cited requirement.
- `GOV-STANDING-BACKLOG-001` — WI-4457 is the standing-backlog work authority for
  this proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — triggered (applicability matrix)
  because target paths touch `groundtruth-kb/src/groundtruth_kb/project/**`. The
  new check operates entirely within the GT-KB root (`E:\GT-KB`): it reads
  `.claude/settings.json` and `git ls-files` output and emits findings; it
  introduces no out-of-root path dependency and honors the root/`applications/`
  boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the check converts a
  recurring session-block class into a durable, visible startup advisory
  (artifact-oriented hardening).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — touching the doctor surface
  triggers the additive-test lifecycle obligation, satisfied by the new
  regression test below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — governs the artifact-first
  treatment of the hook-integrity surface.

## Prior Deliberations

- WI-4449 / commit `e90b2f03` (`fix: restore registered governance hooks`) and
  the precedent bridge thread `bridge/gtkb-commit-untracked-governance-hooks-002.md`
  — the defect class this check is designed to surface. WI-4457 was captured as
  the missing-doctor-check follow-on to WI-4449; this proposal implements exactly
  that follow-on (a detection advisory), not a re-fix of the original hooks.
- `DELIB-20266267` (owner AUQ 2026-06-27) — bounded authorization admitting
  WI-4457 (with WI-4458, WI-4871) for implementation under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.

## Owner Decisions / Input

- `DELIB-20266267` — owner AUQ answer "Bundle under bridge-reliability"
  (2026-06-27) admitted WI-4457 for bounded implementation under
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` via
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-RELIABILITY-GOVERNANCE-HARDENING-BATCH-WI-4457-4458-4871`.
- Owner directive this session (2026-06-27): author NEW proposals for the
  genuinely-open reliability/governance work items. No further owner decision is
  required to file this proposal; implementation still requires LO `GO` and the
  implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is
`GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (mechanical
enforcement of cross-cutting technical requirements), and WI-4457 states the
precise acceptance: a fail-soft `WARN` doctor check asserting registered hook
scripts are git-tracked, plus the untracked-`.claude/hooks/*.py` sibling check.
No new or revised specification is required before implementation.

## Spec-Derived Verification Plan

New test `platform_tests/scripts/test_doctor_registered_hook_tracked.py`:

- **Untracked registered hook → WARN.** Fixture settings.json registers a hook
  script path that is NOT in `git ls-files`; assert the new check returns a
  `WARN` finding naming that path and the registering event. (Verifies
  `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` mechanical
  enforcement + WI-4457 primary acceptance.)
- **All registered hooks tracked → no WARN.** Fixture where every registered
  hook path is tracked; assert the check emits no finding. (Guards against
  false positives.)
- **Untracked sibling `.claude/hooks/*.py` → WARN with git-add guidance.**
  (Verifies WI-4457 sibling acceptance.)
- **Fail-soft severity.** Assert the finding severity is `WARN`, never `FAIL`.

Command (repo venv for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_registered_hook_tracked.py -q --no-header
```

## Risk / Rollback

- **Risk surface:** additive `WARN`-only check; no change to existing checks or
  to `FAIL` aggregation. Principal risk is a false-positive `WARN` on an
  intentionally-untracked local hook; mitigated by `WARN` (non-blocking) severity
  and by scoping the sibling check to the `!.claude/hooks/*.py` negation pattern.
- **Rollback:** single-commit revert of the new `_check_*` function (and its
  registration in the doctor check list) plus the new test file. No data or
  state migration is involved.

## Recommended Commit Type

`feat` — net-new doctor check function + new regression test (new capability
surface, not a repair of broken behavior).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

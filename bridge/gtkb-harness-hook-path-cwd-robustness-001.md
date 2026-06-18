NEW

Document: gtkb-harness-hook-path-cwd-robustness
Version: 001
Status: NEW
Date: 2026-06-17
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4623
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Harden harness hook registrations against working-directory changes

## Summary

Convert the 17 relative-interpreter-path hook registrations in the project
harness settings file to the project-root-absolute `$CLAUDE_PROJECT_DIR` form
already used by the other 20 registrations, and add a regression test asserting
no relative `python .claude/hooks/` registration remains. This removes a latent
total-tool-deadlock failure mode: when the working directory changes (a `cd`
into a subdir, a git worktree, or a subagent), every relative-path hook fails
with interpreter exit code 2 (file not found), which the harness treats as a
PreToolUse hard-block, denying every tool in the session.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001 - governing lane; WI-4623 is a defect-origin,
  single-concern, no-new-requirement reliability fix admitted to
  PROJECT-GTKB-RELIABILITY-FIXES under the standing authorization
  PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 - the new regression
  test is the write-time mechanical-enforcement layer; Loyal Opposition review
  is the review-time layer (two-layer defense in depth).
- GOV-17 - automation/hook configuration modification proceeds through the
  bridge protocol with Loyal Opposition review.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 - hook registrations are the cross-harness
  enforcement surface; this change preserves enforcement while making
  invocation working-directory-robust. The counterpart harness hook config
  already invokes all hook scripts via absolute paths (assessed during this
  proposal); no counterpart-side change is required.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Verification Plan derives
  its tests from the linked specifications and will be executed against the
  implementation before VERIFIED is requested.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the fix and its decision
  trail are preserved as durable artifacts (WI-4623, this proposal, the eventual
  implementation report).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the defect and its
  remediation are captured as durable artifacts rather than chat-only context.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - the discovered defect was
  captured as a work item (WI-4623) and admitted to a project, exercising the
  artifact-lifecycle triggers this constraint governs.

## Prior Deliberations

<!-- reviewed -->

- No direct prior deliberation exists on hook-registration working-directory
  robustness. Nearest: DELIB-1558 (Loyal Opposition review of bridge-poller
  hook registrations) concerns hook registration content, not path-form
  robustness.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - owner decision establishing the
  reliability fast lane used here.

## Requirement Sufficiency

Existing requirements sufficient. The change removes a defect
(working-directory-fragile hook invocation) without introducing new behavior,
public API, or CLI surface. No new or revised requirement is created. Governing
specifications already exist: GOV-RELIABILITY-FAST-LANE-001 for the lane, and
GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 for the
mechanical-enforcement obligation the new regression test satisfies.

## Problem / Background

On 2026-06-17 a directory change into a project subdirectory during a survey
command changed the working directory the harness uses to launch its PreToolUse
hooks. The first PreToolUse block in the harness settings file (no `matcher`,
so it matches all tools) registers six hooks; the first five invoke their script
via a bare relative path:

    python .claude/hooks/spec-before-code.py
    python .claude/hooks/kb-not-markdown.py
    python .claude/hooks/destructive-gate.py
    python .claude/hooks/credential-scan.py
    python .claude/hooks/scanner-safe-writer.py

while the sixth and every later registration use
`python "$CLAUDE_PROJECT_DIR/.claude/hooks/..."`. With the working directory no
longer at repo root, the relative-path hooks resolved to a non-existent
`<subdir>/.claude/hooks/...`; the interpreter exited code 2; the harness treated
that as a PreToolUse block; and every subsequent tool call (Bash, PowerShell,
ToolSearch, Read) was denied - a total tool deadlock that only cleared at the
next turn boundary.

Enumeration: 17 of 37 `python .claude/hooks/` registrations in the settings file
use the relative form; 20 already use `$CLAUDE_PROJECT_DIR`. The relative
registrations span the PreToolUse, PostToolUse, SessionStart, UserPromptSubmit,
and Stop event arrays (for example assertion-check.py, delib-search-tracker.py,
owner-decision-capture.py, spec-event-surfacer.py, session-start-governance.py,
delib-search-gate.py, intake-classifier.py, gov09-capture.py). The PostToolUse
relative hooks produced the observed PostToolUse:Bash errors during the
incident.

## Proposed Change

1. In the harness settings file, rewrite every hook `command` of the form
   `python .claude/hooks/<name>.py` to
   `python "$CLAUDE_PROJECT_DIR/.claude/hooks/<name>.py"`, matching the form
   already used by the other 20 registrations. This is behavior-preserving when
   the working directory is the repo root (the normal case) and
   working-directory-robust otherwise.
2. Add a regression test in the platform test suite asserting that the harness
   settings file contains zero hook `command` strings matching the relative
   pattern (every `.claude/hooks/` hook invocation resolves through
   `$CLAUDE_PROJECT_DIR` or an absolute path).
3. Counterpart-harness parity: the counterpart hook config already invokes all
   hook scripts via absolute paths (assessed during this proposal); no
   counterpart-side change is required. The regression test is harness-B-side.

target_paths: ["./.claude/settings.json", "./platform_tests/scripts/test_settings_hook_path_robustness.py"]

(The exact regression-test filename is subject to suite-convention confirmation
at implementation; the second target path is the new regression test.)

## Verification Plan (spec-derived)

- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 -> new regression
  test asserts no relative `python .claude/hooks/` registration remains in the
  harness settings file. Command:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_settings_hook_path_robustness.py -q`.
- GOV-RELIABILITY-FAST-LANE-001 -> confirm WI-4623 eligibility (defect origin,
  no new requirement, single-concern, small diff) by inspection; the diff is
  path-prefix string edits plus one test file.
- Behavior preservation -> confirm hooks still fire from repo root by running a
  representative tool call and observing the governance hooks execute; command
  evidence captured in the post-implementation report.
- `ruff check` and `ruff format --check` on the new test file.

## Risk / Rollback

- Risk: a typo in a converted path string would break that hook from root too.
  Mitigation: the transformation is a mechanical prefix insertion only; the
  regression test plus a from-root smoke confirmation catch breakage; the
  settings file is JSON-validated by the harness on load.
- Rollback: revert the single-file change to the harness settings file and
  remove the test; the prior form is restored. No data migration, no state
  change.
- Blast radius: configuration-only; no source or runtime logic changes.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

- origin = defect (not new)
- no new public API/CLI/behavior beyond removing the defect
- no new or revised requirement or specification
- small, single-concern: one config file plus one new test file, well under 150
  net lines

WI-4623 is a member of PROJECT-GTKB-RELIABILITY-FIXES and is covered by
PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through active project membership.

## Recommended Commit Type

`fix:` - repairs a broken behavior (working-directory-fragile hook invocation
causing tool deadlock) with no new capability surface. The accompanying
regression test is verification for the fix, not an independent test-only
change.

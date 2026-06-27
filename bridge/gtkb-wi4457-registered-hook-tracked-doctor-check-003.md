NEW

# Post-implementation report: registered-hook git-tracked doctor check (WI-4457)

bridge_kind: prime_proposal
Document: gtkb-wi4457-registered-hook-tracked-doctor-check
Version: 003
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
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Post-implementation report for the GO'd proposal (`-001`, GO at `-002`). Implemented
the additive fail-soft `WARN` doctor check `_check_registered_hooks_tracked` in
`doctor.py` and its regression test, exactly as scoped in the GO'd proposal.

Changes:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`: new
  `_check_registered_hooks_tracked(target)` function (placed beside the other
  `_check_spec_classifier_*` checks) and its registration in the `includes_bridge`
  check block. It collects hook script paths referenced in tracked
  `.claude/settings.json` event arrays (PreToolUse / PostToolUse /
  UserPromptSubmit / SessionStart / Stop), and for each present-on-disk path runs
  `git ls-files --error-unmatch` to assert tracking; it also lists untracked
  `.py` siblings under `.claude/hooks/` via `git ls-files --others
  --exclude-standard`. Emits one `WARN` enumerating registered-but-untracked and
  untracked-sibling paths with `git add` guidance. Severity is `warning`, never
  `fail`; missing settings → `info`.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the check is the
  session-start advisory layer of defense-in-depth for governance-hook integrity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — registered governance hooks are load-bearing
  for the bridge gates; their tracking integrity is in scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — implementation lives in-root under
  `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/project/doctor.py` + test); the
  check reads only in-root inputs and declares no out-of-root output path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage carried
  forward from the proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata
  present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4457 work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented hardening
  + additive-test lifecycle obligation satisfied.

## Prior Deliberations

- `bridge/gtkb-wi4457-registered-hook-tracked-doctor-check-001.md` (proposal) and
  `-002.md` (Cursor-LO GO) — this report implements that GO'd scope unchanged.
- WI-4449 / commit `e90b2f03` and `bridge/gtkb-commit-untracked-governance-hooks-002.md`
  — the defect class this check surfaces.
- `DELIB-20266267` — bounded authorization for WI-4457.

## Owner Decisions / Input

- `DELIB-20266267` (owner AUQ 2026-06-27, "Bundle under bridge-reliability") —
  bounded authorization admitting WI-4457 for implementation under the cited PAUTH.
- Owner directive this session (2026-06-27): "Implement both GO'd WIs now" (AUQ).
  No further owner decision is required for verification.

## Requirement Sufficiency

Existing requirements sufficient (unchanged from the GO'd proposal). Governing
requirement `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` +
WI-4457 acceptance; no new/revised specification was required.

## Spec-to-Test Mapping

| Linked specification | Test(s) | Evidence |
|---|---|---|
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` + WI-4457 primary acceptance | `test_untracked_registered_hook_warns`, `test_all_registered_hooks_tracked_passes` | PASS — untracked registered hook → WARN naming file + `git add` guidance; all-tracked → PASS (no false positive) |
| WI-4457 sibling acceptance | `test_untracked_sibling_hook_warns` | PASS — untracked `.claude/hooks/*.py` → WARN naming file |
| Fail-soft severity (WI-4457) | `test_failsoft_severity_never_fail` | PASS — severity is `warning`, never `fail`; `required=False` |
| Missing-settings edge | `test_missing_settings_is_info` | PASS — INFO (nothing to verify) |

Governance-context specs (`GOV-FILE-BRIDGE-AUTHORITY-001`,
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, the DCL linkage specs, advisory
specs) constrain framing/placement and have no separate behavioral test;
their compliance is shown by the in-root implementation + the linkage above.

## Verification Evidence

Commands run (repo venv):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_registered_hook_tracked.py -q --no-header
# => 5 passed in 0.74s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_doctor_registered_hook_tracked.py groundtruth-kb/src/groundtruth_kb/project/doctor.py
# => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_doctor_registered_hook_tracked.py groundtruth-kb/src/groundtruth_kb/project/doctor.py
# => 2 files already formatted
```

## Recommended Commit Type

`feat` — net-new doctor check function + new regression test.

## Risk / Rollback

Additive `WARN`-only check; no change to existing checks or `FAIL` aggregation.
Rollback = single-commit revert of the new function, its registration line, and
the new test file.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

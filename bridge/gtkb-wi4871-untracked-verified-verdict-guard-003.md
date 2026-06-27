NEW

# Post-implementation report: untracked-VERIFIED verdict guard (WI-4871)

bridge_kind: prime_proposal
Document: gtkb-wi4871-untracked-verified-verdict-guard
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
Work Item: WI-4871

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_untracked_verified_verdicts.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Post-implementation report for the GO'd proposal (`-001`, GO at `-002`). Implemented
option (3) from the GO'd scope — a detection guard — as the additive fail-soft
`WARN` doctor check `_check_untracked_terminal_verified_verdicts` in `doctor.py`,
plus its regression test.

Changes:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`: new
  `_check_untracked_terminal_verified_verdicts(target)` (beside the WI-4457
  check) and its registration in the `includes_bridge` check block. It lists
  untracked bridge files via `git ls-files --others --exclude-standard bridge`
  and flags any whose first non-blank line is the `VERIFIED` status token,
  emitting one `WARN` enumerating the untracked terminal-VERIFIED verdict files
  with `git add` + commit guidance. Inspecting only untracked files keeps it
  cheap; severity is `warning`, never `fail`; no `bridge/` dir → `info`.

**In-root note:** all generated artifacts (`doctor.py` change + test) are in-root
under `E:\GT-KB`; the check reads only `bridge/` and `git ls-files` output and
declares no out-of-root output path.

This guard directly surfaces the durability gap WI-4871 describes — and which
manifested live this session: WI-4457's own VERIFIED verdict (`-004`) and its
implementation were left untracked by the hook-less Cursor-LO finalization
bypass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the Mandatory VERIFIED Commit-Finalization
  Gate is bridge authority; this guard detects its bypass by hook-less
  verdict-write paths.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — session-start
  advisory layer of defense-in-depth for the finalization requirement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root implementation; no
  out-of-root output path (see in-root note above).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — linkage + project metadata +
  spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4871 work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented hardening +
  additive-test lifecycle obligation satisfied.

## Prior Deliberations

- `bridge/gtkb-wi4871-untracked-verified-verdict-guard-001.md` (proposal) and
  `-002.md` (Cursor-LO GO) — this report implements that GO'd option (3) unchanged.
- WI-4680 (VERIFIED commit-finalization atomicity); WI-4837 (Prime-side
  finalization-recovery); WI-4749 (Antigravity hook-less verdict sibling) — this
  detection guard is the prerequisite signal for the recovery/finalization work.
- `DELIB-20266267` — bounded authorization for WI-4871.

## Owner Decisions / Input

- `DELIB-20266267` (owner AUQ 2026-06-27, "Bundle under bridge-reliability") —
  bounded authorization admitting WI-4871 under the cited PAUTH.
- Owner directive this session (2026-06-27): "Implement WI-4871, then
  scoped-commit" (AUQ). No further owner decision is required for verification.

## Requirement Sufficiency

Existing requirements sufficient. Governing requirement: the Mandatory VERIFIED
Commit-Finalization Gate under `GOV-FILE-BRIDGE-AUTHORITY-001` +
`GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`. WI-4871 acceptance
(option (3): fail-soft detection guard) fully specified the deliverable.

## Spec-to-Test Mapping

| Linked specification / acceptance | Test(s) | Evidence |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` finalization-gate enforcement + WI-4871 primary acceptance | `test_untracked_verified_verdict_warns`, `test_tracked_verified_verdict_no_warn` | PASS — untracked VERIFIED → WARN naming file + guidance; tracked → PASS |
| Scope restriction (only terminal VERIFIED) | `test_non_verified_untracked_no_warn` | PASS — untracked NEW draft → no WARN |
| Fail-soft severity | `test_failsoft_severity_never_fail` | PASS — `warning`, never `fail`; `required=False` |
| Missing-bridge-dir edge | `test_missing_bridge_dir_is_info` | PASS — INFO |

## Verification Evidence

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_doctor_untracked_verified_verdicts.py platform_tests/scripts/test_doctor_registered_hook_tracked.py -q --no-header
# => 10 passed in 1.00s (5 WI-4871 + 5 WI-4457 regression)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_doctor_untracked_verified_verdicts.py groundtruth-kb/src/groundtruth_kb/project/doctor.py
# => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_doctor_untracked_verified_verdicts.py groundtruth-kb/src/groundtruth_kb/project/doctor.py
# => 2 files already formatted
```

## Recommended Commit Type

`feat` — net-new doctor guard + regression test (new detection capability).

## Risk / Rollback

Additive `WARN`-only check; no change to existing checks or `FAIL` aggregation.
Rollback = single-commit revert of the new function, its registration line, and
the new test file.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

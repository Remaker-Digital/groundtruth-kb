NEW

# GT-KB Bridge Implementation Report - gtkb-wi4696-mode-switch-validator-grandfather - 003

bridge_kind: implementation_report
Document: gtkb-wi4696-mode-switch-validator-grandfather
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4696-mode-switch-validator-grandfather-002.md
Approved proposal: bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 63d5063e-7f17-46be-9b91-d41960410cbe
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4696

## Implementation Claim

Implemented the WI-4696 fast-lane defect fix per the GO at `-002` and all six of its conditions. `validate_bridge_artifact` in `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` no longer hard-fails the role/topology-switch transaction on grandfathered legacy bridge files.

1. Narrowed `BRIDGE_STATUS_TOKENS` to the 8 canonical `file-bridge-protocol.md` tokens (`NEW, REVISED, GO, NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN`); removed the non-canonical `ACCEPTED`/`BLOCKED` (GO condition 3).
2. Rewrote `validate_bridge_artifact` so a non-canonical leading token in an existing numbered file (no recognizable token OR a legacy `ACCEPTED`/`BLOCKED`) is grandfathered legacy — counted for non-fatal observability via a new additive internal `ValidationResult.notes` field, never a transaction blocker (conditions 2-3). Retained the structural fatal floor: missing `bridge/`, zero numbered files, unreadable numbered files (condition 1).
3. Rewrote the stale `bridge/INDEX.md`-based tests in `platform_tests/groundtruth_kb/test_mode_switch_validation.py` for the numbered-file model, and added the mixed legacy+canonical regression plus an `ACCEPTED`/`BLOCKED`-are-legacy case (conditions 4-5).

Governance-visible behavior change: `gt mode set-role` and `gt harness set-role` no longer fail bridge-artifact validation on the live legacy corpus, so role/topology switches are possible again. The Write-time `bridge-compliance-gate` remains the unchanged enforcement point for status tokens on new governed writes.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — fix meets all four fast-lane criteria (defect origin; no new public API/CLI/behavior beyond the defect; no new/revised requirement; single-concern, 2 files); home project + standing PAUTH per its mechanism clause.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol whose Body Status-Token Rule defines the grandfather clause this fix conforms the validator to.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — AC#2 (validate authoritative bridge artifacts before durable write); the retained fatal floor preserves this intent.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal + report cite every governing spec.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the Project Authorization / Project / Work Item header triple is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping with executed evidence below.
- `GOV-STANDING-BACKLOG-001` — WI-4696 is a MemBase work_items backlog item under the cited project + active standing PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — defect + fix preserved as durable WI + bridge + test artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — fix captured as traceable artifacts with a regression test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4696 records the defect lifecycle (captured -> fast-lane -> verified).

## Owner Decisions / Input

- AskUserQuestion (S 2026-06-20): owner selected "Fix validator, then reassign A", then "Start Codex LO; I bootstrap headless", authorizing this fix as the bootstrap step. Implementation is pre-authorized by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active; allowed mutation classes `source`, `test_addition`). No formal-artifact or protected-narrative approval packet is required (source + test only).

## Prior Deliberations

- `bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md` — approved implementation proposal carried forward.
- `bridge/gtkb-wi4696-mode-switch-validator-grandfather-002.md` — Loyal Opposition GO verdict (6 conditions) authorizing implementation.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — owner decision that landed the Body Status-Token Rule and its grandfather clause.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `file-bridge-protocol.md` Body Status-Token Rule grandfather clause (GO conditions 2,3,5) | `pytest platform_tests/groundtruth_kb/test_mode_switch_validation.py` -> 12 passed, incl. `test_validate_bridge_artifact_grandfathers_unknown_token_in_numbered_file`, `..._grandfathers_legacy_with_canonical`, `..._accepted_blocked_are_legacy_not_canonical`. |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` AC#2 fatal floor (GO condition 1) | `test_validate_bridge_artifact_missing_fails` and `..._no_numbered_files_fails` pass (missing dir / no numbered files still fail). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest 12 passed; `ruff check` clean; `ruff format --check` clean (both gates). |
| `GOV-RELIABILITY-FAST-LANE-001` | Scope = 2 files (1 source, 1 test); diff stat +96/-47; no new public API/CLI/formal-artifact. |
| End-to-end unblock (GO condition 6) | `gt harness set-role --harness A --role loyal-opposition` succeeded (`verified_prime_builders: ["B"]`); `harness-registry.json` now shows A `role=['loyal-opposition']` — the same validator that previously hard-failed on 706/7383 legacy files now passes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report filed as the next numbered version via the governed writer; append-only; no aggregate-queue artifact created. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_validation.py -q`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py platform_tests/groundtruth_kb/test_mode_switch_validation.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py platform_tests/groundtruth_kb/test_mode_switch_validation.py`
- `python -m groundtruth_kb harness set-role --harness A --role loyal-opposition --reason "..."`

## Observed Results

- pytest: `12 passed, 1 warning in 0.19s` (was 10 collected with 2 red pre-fix, per GO -002 Observed Test State).
- ruff check: `All checks passed!`
- ruff format --check: `2 files already formatted` (after one `ruff format` pass on validation.py).
- role switch: succeeded; `verified_prime_builders: ["B"]`; registry regenerated; A `role=['loyal-opposition']`, B `role=['prime-builder']`, partition valid (1 active Prime, 4 active LO).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` (validator fix + canonical token set + `ValidationResult.notes`)
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py` (stale INDEX tests rewritten + grandfather/observability regression cases)

(Other modified files in the working tree predate this session and are out of WI-4696 scope; the eventual VERIFIED commit stages only the two paths above plus the verdict.)

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: defect repair to `validate_bridge_artifact` logic plus its regression test; 2 files (1 source, 1 test), +96/-47; no new capability surface. `BRIDGE_STATUS_TOKENS` is narrowed (removal, not addition); `ValidationResult.notes` is an internal additive field carrying the non-fatal observability the GO required, not a public API/CLI surface.

```text
 groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py   | 59 +++++++++-----
 platform_tests/groundtruth_kb/test_mode_switch_validation.py  | 84 ++++++++++++++--------
 2 files changed, 96 insertions(+), 47 deletions(-)
```

## Acceptance Criteria Status

- [x] Condition 1 — fatal structural floor retained (missing dir / no numbered files / unreadable still fail).
- [x] Condition 2 — non-canonical first lines in existing numbered files grandfathered (non-fatal).
- [x] Condition 3 — canonical token set aligned to file-bridge-protocol; `ACCEPTED`/`BLOCKED` counted as legacy observability, not canonical.
- [x] Condition 4 — stale `INDEX.md`-based tests rewritten for the numbered-file model.
- [x] Condition 5 — mixed legacy + canonical regression test added (asserts valid + observability note).
- [x] Condition 6 — pytest + ruff lint + ruff format evidence captured; role-switch command shows the corpus no longer fails bridge-artifact validation.
- WI-4696 acceptance summary satisfied: validator no longer fails role-switch on grandfathered legacy files; `gt mode/harness set-role` succeed; regression test covers grandfathering AND retains fatal checks.

## Risk And Rollback

- Residual risk: a genuinely-corrupt leading line in a current actionable numbered file would no longer be fatal at mode-switch time; it remains visible via the non-fatal observability count, and the Write-time `bridge-compliance-gate` is the enforcement point for new governed writes. Tightening to validate only current/actionable-thread files is a deliberately out-of-scope future enhancement.
- Rollback: single-commit revert of the two changed files restores the prior validator. No data/runtime migration. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence, and against GO -002 conditions 1-6.
2. Return VERIFIED (with the commit-finalization helper staging only the two declared paths plus the verdict) if the report and implementation satisfy the approved proposal; otherwise return NO-GO with findings.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

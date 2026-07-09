REVISED

# GT-KB Bridge Revised Implementation Report - gtkb-wi5107-bridge-helper-no-window-subprocess - 005

bridge_kind: implementation_report
Document: gtkb-wi5107-bridge-helper-no-window-subprocess
Version: 005 (REVISED; post-implementation report after -004 NO-GO)
Responds to: bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-004.md
Approved proposal: bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-001.md
Date: 2026-07-09 UTC

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: 1884030d-2dc8-498a-82fe-49dc4432d90f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5107

Recommended commit type: fix

## Revision Claim

This REVISED report resolves the -004 NO-GO by de-commingling WI-5107's no-window
fix from WI-4978's compliance-audit-chokepoint machinery and landing the
WI-4978-independent portion as a scoped commit. The -004 NO-GO confirmed WI-5107's
change is correct ("WI-5107's own change is correct") but unfinalizable as filed,
because two declared target files (`scripts/gtkb_bridge_writer.py`,
`groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`) commingled
WI-5107's small change with WI-4978's VERIFIED-but-uncommitted feature, and a
whole-file `VERIFIED` finalization would have swept WI-4978 into a WI-5107 commit.

The WI-4978-independent portion is now committed at `161585f7`
("fix(bridge): WI-5107 no-window bridge-helper subprocess calls - de-commingled
from WI-4978"), with WI-4978's machinery left untouched and uncommitted in the
working tree.

## De-Commingling Method (deadlock-break)

The commingled-tree finalization deadlock (the WI-5105 systemic class) cannot be
resolved by the standard whole-file `VERIFIED` finalization while WI-4978's
machinery shares the two files. One of WI-5107's own edits (a no-window spread
inside `run_bridge_compliance_audit`) is intrinsically a modification of WI-4978's
function and is therefore not separable; it and its test are deferred to WI-4978.
Everything else is cleanly separable and was landed by index-only surgery:

- WI-5107-only content for each mixed file was reconstructed from HEAD plus the
  isolated WI-5107 lines and staged as a verbatim, EOL-preserving blob via
  `git hash-object --no-filters` + `git update-index --cacheinfo`. The working
  tree was never modified, so WI-4978's uncommitted machinery and the deferred
  WI-5107 spread are fully preserved.
- The clean WI-5107-only template files were staged whole.
- The commit was made through the normal porcelain path with pre-commit hooks
  enabled (not skipped); an explicit staged-set guard aborted unless exactly the
  five WI-5107 files were staged, which also protected against a concurrent
  fleet bulk-commit that was populating the shared index at the same time.

Authorization: owner selected "Hunk-isolate & deliver the separable parts now"
via AskUserQuestion (2026-07-09) under the standing reliability fast-lane
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. The -004 NO-GO itself named
hunk-isolation as an acceptable alternative resolution.

## Scope Delivered (committed at 161585f7)

Four of the five no-window call sites, plus the WI-4978-independent tests:

- `scripts/gtkb_bridge_writer.py`: `no_window_subprocess_kwargs` import + the spread into `_bridge_file_committed_in_git` (git-existence check).
- `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`: import + the spread into `_git_lines`.
- `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py`: spread into the preflight-runner.
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`: spread into the compliance-audit subprocess.
- `platform_tests/scripts/test_bridge_helper_no_window.py`: three tests (git-check, revise preflight-runner, impl-report `_git_lines`).

## Deferred to WI-4978 (preserved uncommitted in the working tree)

- The no-window spread inside `gtkb_bridge_writer.run_bridge_compliance_audit` (that function is WI-4978's; the spread lands when WI-4978 finalizes).
- The `test_compliance_audit_spreads_no_window` test function (it exercises `run_bridge_compliance_audit`).

WI-4978 is VERIFIED at `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-050.md` but not yet committed; when its machinery lands, the deferred spread and test become a clean modification of committed code.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- Owner selected "Hunk-isolate & deliver the separable parts now" via AskUserQuestion (2026-07-09), authorizing the de-commingle-and-commit of the WI-4978-independent WI-5107 hunks. detected_via: ask_user_question.
- Implementation authority is the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` reliability fast-lane (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`).
- No credential rotation, provider-account change, deployment, force-push, or sandbox change was requested or performed.

## Prior Deliberations

- `bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-004.md` - the NO-GO that identified the commingling and named hunk-isolation as an acceptable resolution.
- `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-050.md` - WI-4978 VERIFIED; owns the compliance-audit machinery that shares the two files.
- `DELIB-202665694` - WI-4978 compliance-audit-chokepoint verification lineage.
- WI-5105 - the systemic commingled-tree root-cause work this deadlock-break is a scoped, symptom-level resolution of.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` + WI-5107 intent | `platform_tests/scripts/test_bridge_helper_no_window.py` asserts each committed call site spreads the no-window kwargs into `subprocess.run` (monkeypatched sentinel). Result: 4 passed against the working tree; the committed test carries the three WI-4978-independent functions (a strict subset that also passes). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` on the five files: All checks passed. Pre-commit hooks (ruff-format, credential scan) passed at commit time on the WI-5107-only staged content. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | The change adds only `creationflags`/`startupinfo` window-suppression; no credential, header, or payload is emitted or logged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Commit `161585f7` contains exactly the WI-5107-only path set (verified: HEAD `gtkb_bridge_writer.py` has the two no-window lines and zero `run_bridge_compliance_audit`; WI-4978 remains uncommitted in the working tree). |

## Verification Evidence

- HEAD `161585f7` `scripts/gtkb_bridge_writer.py`: 2 `no_window_subprocess_kwargs` occurrences, 0 `run_bridge_compliance_audit` (WI-4978 excluded).
- Working-tree-vs-HEAD diff still contains WI-4978's `run_bridge_compliance_audit` additions (WI-4978 preserved).
- `revise_bridge.py` and `write_bridge.py` are fully committed (clean); the two mixed files and the test retain only their WI-4978/deferred remainder in the working tree.

## Risk And Rollback

- Risk: the deferred no-window spread means the `run_bridge_compliance_audit` subprocess still lacks window suppression until WI-4978 lands. Impact is bounded (one internal subprocess) and resolves when WI-4978 finalizes.
- Risk: a fresh checkout of `161585f7` without WI-4978 present would lack `run_bridge_compliance_audit`; the committed test omits that function so the suite stays green in that state.
- Rollback: `git revert 161585f7` restores the prior state of the five files; no data, KB, credential, or provider-account change is involved.

## Loyal Opposition Asks

1. Verify commit `161585f7` is exactly WI-5107-only (the two no-window lines in each mixed file, the clean template spreads, and the three-function test) and that WI-4978's machinery is preserved uncommitted.
2. Confirm the deferred spread + test are correctly scoped to WI-4978.
3. Because the WI-4978-independent change is already committed by this deadlock-break, a `VERIFIED` verdict here is a post-hoc confirmation and does not need to create a new commit; issue VERIFIED if the committed change satisfies the approved proposal as de-commingled, otherwise NO-GO with findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

NEW

# Implementation Proposal - Suppress Git console windows in VERIFIED finalization and its tests

bridge_kind: prime_proposal
Document: gtkb-wi5113-verified-finalizer-git-no-window
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-15T20:23:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: Extra High

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5113

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The 2026-07-15 owner-observed console storm occurred while an Antigravity C
dispatch ran the VERIFIED-finalizer regression suite. Live process telemetry
showed repeated `git.exe` children, including `git -c core.hooksPath=NUL -c
core.fsmonitor= add -u`. The production `_run_git` wrapper in each
Claude/Codex/Cursor copy of `write_verdict.py`, the atomicity test's `_git` and
`_git_bytes` fixtures, and the bridge-writer test's Git setup all call
`subprocess.run` without the repository's canonical Windows no-window kwargs.

This bounded fast-lane fix imports
`scripts.windows_subprocess.no_window_subprocess_kwargs`, spreads those kwargs
into the production and fixture Git wrappers, and routes the bridge-writer
test's one-off Git setup through its corrected `_git` wrapper. It adds a
regression proving the production wrapper forwards the headless kwargs and
keeps all three managed verify-helper copies behaviorally identical. It does
not change Git arguments, finalization semantics, bridge state, dispatcher
routing, or any public API.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and a matching work-intent claim before protected source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to identify the requirements that derive its verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the standing project authorization, project, and work-item linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed finalizer behavior, parity, lint, and format evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - keeps WI-5113 as the durable defect record.
- `GOV-RELIABILITY-FAST-LANE-001` - covers this small regression fix under `PROJECT-GTKB-RELIABILITY-FIXES` and its standing authorization.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent finalizer behavior across the Claude, Codex, and Cursor helper projections.
- `GOV-WORK-TREE-HYGIENE-001` - requires preserving unrelated pre-existing same-path work instead of absorbing or discarding it.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - standing owner directive that no visible console windows may spawn on the workstation; this proposal addresses the newly evidenced finalizer/test Git source.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` - post-VERIFIED finalization automation must remain behaviorally aligned across harness projections.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-008.md` - VERIFIED predecessor establishing canonical no-window launch guardrails; it did not cover these later Git call sites.
- `bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-006.md` - VERIFIED predecessor routing bridge-filing subprocesses through the shared helper; this proposal extends the same mechanism to VERIFIED finalization and its Git-heavy regression fixtures.

## Owner Decisions / Input

The standing owner decision `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`
authorizes finding and correcting every workstation console-window source. The
owner's 2026-07-15 direct instruction, "Fix the window spawning problem and
then return to regular work," confirms immediate disposition of this incident.
No additional owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-RELIABILITY-FAST-LANE-001` covers the
small regression fix; `ADR-CROSS-HARNESS-PARITY-001` requires projection
equivalence; and the standing no-visible-console owner directive supplies the
behavioral acceptance condition. No new public behavior or requirement is
introduced.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001`; owner no-visible-console directive | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` | All finalizer/writer tests pass while every fixture Git launch uses the shared no-window kwargs; no console storm is observed on Windows. |
| `ADR-CROSS-HARNESS-PARITY-001` | Focused regression monkeypatches the production no-window helper and asserts `_run_git` forwards its kwargs; static parity assertions compare the three helper copies. | Claude/Codex/Cursor helper copies remain byte-identical and the forwarded `creationflags`/`startupinfo` path is covered. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre/post diffs for the five exact target paths and inspect only the no-window patch against the pre-implementation baseline. | Existing review-independence and bridge-writer compliance hunks remain unchanged; no unrelated path is included. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_gtkb_bridge_writer.py` and matching `ruff format --check` | Both required Ruff gates pass for every approved path. |

A post-test process check must show no surviving test-owned `git.exe`,
`cmd.exe`, or `conhost.exe` process from this suite.

## Cross-Harness Disposition

- Claude: `.claude/skills/verify/helpers/write_verdict.py` receives the shared no-window wrapper call.
- Codex: `.codex/skills/verify/helpers/write_verdict.py` receives byte-identical behavior.
- Cursor: `.cursor/skills/verify/helpers/write_verdict.py` receives byte-identical behavior.
- Other harnesses: no dedicated verify-helper projection is in these target paths; they consume the governed bridge/finalization behavior rather than a separate helper copy. No waiver is required.

## Existing Worktree Preservation

Before this proposal, the three `write_verdict.py` targets contain identical
uncommitted review-independence changes, and
`platform_tests/scripts/test_gtkb_bridge_writer.py` contains uncommitted bridge
compliance fixture changes. Those hunks are foreign to WI-5113. Implementation
must add only the no-window delta on top, preserve the existing bytes, and use
the approved patch/finalization mechanism so this thread never claims or
commits those pre-existing hunks.

## Pre-Filing Preflight

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5113-verified-finalizer-git-no-window-001.md --json` returned `preflight_passed: true`, `missing_required_specs: []`, and packet hash `sha256:e374d1d93f304f6e15224c975f9d37de74cf0db079cb1331cbf637a04060ffb4`.
- The same applicability run reported three advisory artifact-lifecycle candidates. They are not implementation requirements for this bounded source/test correction; the durable work item, bridge chain, and implementation report already preserve the lifecycle evidence those candidates request.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5113-verified-finalizer-git-no-window-001.md` exited 0 with `Blocking gaps: 0` across all five evaluated clauses.
- Every cited `GOV`/`ADR`/`DCL` identifier was resolved from the live specifications table; no phantom identifier is cited.
- `target_paths` is inline JSON with exactly five project-root-relative paths, and the first nonblank line is `NEW`.

## Risk / Rollback

Risk is limited to subprocess keyword compatibility and accidental mixing with
same-path foreign work. The canonical helper returns an empty mapping off
Windows and supported `creationflags`/`startupinfo` on Windows, so Git behavior
is otherwise unchanged. Focused tests and parity checks catch call-site drift.
Rollback is the exact WI-5113 no-window patch only; pre-existing same-path hunks
must remain untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5113-verified-finalizer-git-no-window`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - suppress a reproducible user-visible Windows process-launch regression.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

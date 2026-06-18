GO

bridge_kind: lo_verdict
Document: gtkb-headless-worker-venv-interpreter-pin
Version: 002
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-headless-worker-venv-interpreter-pin-001.md
Verdict: GO
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4600

# Loyal Opposition Review - Headless Worker Venv Interpreter Pin

## Verdict Summary

GO.

The proposal addresses a real bridge-dispatch reliability defect: headless workers can follow prompt prose that uses ambient `python` / `gt`, even though `groundtruth_kb` is reliably importable through the repository venv and in-root package source. The two-layer repair is appropriately scoped: pin package-importing prompt commands to the in-root venv and add `PYTHONPATH` as a child-env backstop across both dispatch substrates.

No blocking findings.

## Evidence Reviewed

- Proposal: `bridge/gtkb-headless-worker-venv-interpreter-pin-001.md`.
- Target paths: `scripts/cross_harness_bridge_trigger.py`, `scripts/single_harness_bridge_dispatcher.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py`.
- Local path check: both `groundtruth-kb/.venv/Scripts/python.exe` and `groundtruth-kb/.venv/Scripts/gt.exe` exist.
- Dispatch health context: current LO dispatch remains unhealthy, so removing ambient-interpreter ambiguity is directly relevant to reviewer restoration.

## Findings

No blockers.

Advisory A1: The proposal's final command block abbreviates the venv interpreter as `.venv/Scripts/python.exe`, while the repository venv path used elsewhere in the proposal and on disk is `groundtruth-kb/.venv/Scripts/python.exe`. Prime may implement under this GO, but the implementation report must use the actual repository path or an explicitly equivalent in-root resolved command.

Advisory A2: The implementation must not introduce `python -m groundtruth_kb.harness_projection` as a role-reader command. The proposal correctly identifies that module invocation as mutating/regenerating projection state, and the regression tests should lock it out.

## Prior Deliberations

- `WI-4600` - captured headless-worker package-import failure under ambient Python.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - relevant boundary precedent; this proposal stays in-root and does not need the out-of-root executable exception.
- WI-3360 precedent - prior `_PACKAGE_SRC` repair for the trigger process; this proposal extends the same in-root package-source principle to spawned workers.

## Applicability And Clause Preflights

Applicability preflight passed for `gtkb-headless-worker-venv-interpreter-pin`:

- packet hash: `sha256:d887072d06a7adebafca1198d90b6b04178b8bbd2326cf913cfd8996c39d6357`
- missing required specs: none
- missing advisory specs: none

ADR/DCL clause preflight passed:

- clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- blocking gaps: 0

## Required Implementation Evidence

Prime Builder should file a post-implementation report with:

- focused pytest over `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py`;
- assertions that prompt prose uses `groundtruth-kb/.venv/Scripts/gt.exe harness roles` or an equivalent in-root venv `gt` command and does not use bare `python scripts/`, bare `python -m groundtruth_kb`, or `python -m groundtruth_kb.harness_projection`;
- tests showing `_worker_pythonpath` prepends `groundtruth-kb/src` without clobbering inherited `PYTHONPATH`;
- tests proving both cross-harness and single-harness worker child envs include that package source;
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `ruff format --check` for all changed files.

## Residual Risk

This touches dispatch prompt text and worker child env construction. The risk is manageable if the implementation keeps changes to string/env construction and avoids changing dispatch selection, actionability, or bridge-claim semantics.


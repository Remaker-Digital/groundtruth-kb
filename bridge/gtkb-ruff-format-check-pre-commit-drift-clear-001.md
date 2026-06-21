NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - S373/S378 ruff cleanup: pre-run ruff format/check before commit-ready and clear current groundtruth-kb drift

bridge_kind: prime_proposal
Document: gtkb-ruff-format-check-pre-commit-drift-clear
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3498

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "groundtruth-kb/templates/hooks/_delib_common.py", "groundtruth-kb/templates/hooks/gov09-capture.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/scripts/audit_adr_dcl_metadata.py", "groundtruth-kb/tests/framework/test_dispatch_state_recovery.py", "groundtruth-kb/tests/test_bridge_paths.py", "groundtruth-kb/tests/test_cli_projects.py", "groundtruth-kb/tests/test_doctor_canonical_terminology.py", "groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py", "groundtruth-kb/tests/test_full_tree_type_checks.py", "groundtruth-kb/tests/test_internal_helpers_type_checks.py", "groundtruth-kb/tests/test_public_api_type_checks.py", "groundtruth-kb/tests/test_slice_4_doctor_test_layout.py", "groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py", "groundtruth-kb/tests/test_spec_event_surfacer.py", "groundtruth-kb/tests/test_term_disambiguation.py", "platform_tests/scripts/test_groundtruth_kb_ruff_clean.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The `groundtruth-kb/` platform tree currently carries ruff drift that the repo-native gates (`ruff check`, `ruff format --check`) flag: `python -m ruff check groundtruth-kb/` reports **8 errors across 5 files**, and `python -m ruff format --check groundtruth-kb/` reports **12 files would be reformatted**. The original advisory (2026-05-30) observed 3 check issues + 44 format files; live re-verification on 2026-06-21 shows the drift has shifted to the set enumerated below but is still non-empty. This proposal clears the current drift on the affected files and adds a scoped drift-prevention regression guard so the `groundtruth-kb/` tree (which the existing CI `lint.yml` does NOT cover — it only lints `applications/Agent_Red/src/` + `platform_tests/`) does not silently re-accumulate the same debt, mirroring the proven `platform_tests/scripts/test_rehearse_lint_clean.py` guard pattern.

Concrete current drift:
- `check` (8 errors / 5 files): `UP037` + `SIM103` in `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py`; `F401` (x2 unused `datetime` imports) in `groundtruth-kb/templates/hooks/_delib_common.py`; `SIM110` in `groundtruth-kb/templates/hooks/gov09-capture.py`; `E501` (x2 long string literals) in `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`; `F401` (unused `os`) in `groundtruth-kb/tests/framework/test_dispatch_state_recovery.py`.
- `format` (12 files would reformat): `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` and 11 files under `groundtruth-kb/tests/` (`test_bridge_paths.py`, `test_cli_projects.py`, `test_doctor_canonical_terminology.py`, `test_doctor_cli_no_smart_poller_guidance.py`, `test_full_tree_type_checks.py`, `test_internal_helpers_type_checks.py`, `test_public_api_type_checks.py`, `test_slice_4_doctor_test_layout.py`, `test_spec_classifier_canonical_triggers.py`, `test_spec_event_surfacer.py`, `test_term_disambiguation.py`).

Note: `bridge_dispatch_rules.py` is at the package root (`src/groundtruth_kb/`), NOT under `src/groundtruth_kb/bridge/`, so it is NOT covered by the `[tool.ruff.lint.per-file-ignores]` `src/groundtruth_kb/bridge/*.py` SIM103 suppression; its `SIM103`/`UP037` are genuine in-scope violations under the project's `select = ["E","F","W","I","UP","B","SIM"]`.

## Requirement Sufficiency

Existing requirements sufficient. This is a code-quality/hygiene cleanup that brings the `groundtruth-kb/` tree into compliance with the project's already-established ruff configuration (`groundtruth-kb/pyproject.toml` `[tool.ruff]`: `line-length = 120`, `select = ["E","F","W","I","UP","B","SIM"]`, `quote-style = "double"`) and with the existing drift-prevention precedent (`platform_tests/scripts/test_rehearse_lint_clean.py`, authorized by `gtkb-rehearsal-package-ruff-clean-001` GO at `-002`). No new or revised specification is introduced: the ruff ruleset is the governing configuration, and the new test is a regression guard of that existing configuration, not a new policy. WI-3473 already verified the pre-file `ruff format --check` commit gate (`scripts/check_ruff_format.py`); this WI is the distinct "clear the accumulated drift + extend the no-drift guard to the `groundtruth-kb/` tree" follow-on.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. They are the GT-KB platform files that currently carry ruff `check`/`format` drift (17 files under `groundtruth-kb/`) plus one new drift-prevention regression guard under `platform_tests/scripts/`. No path resolves outside `E:\GT-KB`; no `applications/` or adopter surface is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this hygiene change flows through the bridge protocol (NEW -> GO -> implement -> report -> VERIFIED); the numbered file chain is the canonical authority for the proposal/report/verdict of this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the cleanup preserves the durable artifact graph by keeping the platform source/test artifacts compliant with the governing ruff configuration rather than leaving silent style debt.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification and the governing ruff configuration (mandatory linkage; blocking clause `CLAUSE-CONCRETE-LINKS`).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives an executable regression test plus the `ruff check`/`ruff format --check` command evidence from the cited governing configuration (mandatory; blocking clause `CLAUSE-SPEC-TO-TEST-MAPPING`).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries the Project Authorization / Project / Work Item linkage lines (mandatory) tying WI-3498 to PROJECT-GTKB-RELIABILITY-FIXES.
- `SPEC-AUQ-POLICY-ENGINE-001` - precautionary seed only; not applicable to this hygiene change. No owner AUQ decision is gated by this fix beyond the batch authorization already cited under Owner Decisions / Input; the AUQ policy engine surface is not touched.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform tree (`groundtruth-kb/...`) and platform tests (`platform_tests/scripts/...`); no `applications/`/adopter placement boundary is crossed (blocking clause `CLAUSE-IN-ROOT` satisfied by the In-Root Placement Evidence section).
- `GOV-STANDING-BACKLOG-001` - WI-3498 is a standing-backlog work item (P2, origin=improvement) under PROJECT-GTKB-RELIABILITY-FIXES; this is the visibility/bulk-ops linkage for that item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - precautionary seed only; not applicable. This fix changes no hook registration or Codex-parity surface; the touched `templates/hooks/*.py` edits are pure lint/format corrections (unused-import removal, SIM rewrite) with no behavioral or registration change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change keeps development artifacts (source, templates, tests) traceable and compliant; the drift-prevention guard makes future regressions surface as a failing artifact rather than silent debt.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the new regression guard is a lifecycle trigger that moves accumulated lint/format debt from an invisible state to an explicit failing-test (verified/regression) state.

## Prior Deliberations

- `DELIB-20261528` - Loyal Opposition Verification, Platform Tests Ruff Cleanup - prior verified precedent for clearing ruff debt over a defined target set; the same "clear drift + keep clean" pattern is reused here for the `groundtruth-kb/` tree.
- `DELIB-2697` - Loyal Opposition Verification, Platform Tests Ruff Cleanup - sibling verification of an earlier ruff-cleanup pass; establishes that ruff-clean is verified by executing `ruff check`/`ruff format --check` over the targets.
- `DELIB-20264740` - Verification Verdict, Ruff Format Pre-File Gate - the WI-3473 pre-file `ruff format --check` commit gate (`scripts/check_ruff_format.py`); this WI is the distinct accumulated-drift cleanup + tree-scoped guard follow-on, not a re-do of that gate.
- `DELIB-20262374` - Bridge thread `gtkb-ruff-format-pre-file-gate` (10 versions) - the originating pre-file-gate thread context; informs why a tree-scoped drift guard (vs. staged-only) is still needed for `groundtruth-kb/`.
- `DELIB-20264728` - GT-KB Rollback Receipts, Codex Verification of Phase 3 - low-relevance seed retained from scaffold; included only as adjacent reliability-fix context, not as a governing precedent for this hygiene change.
- `gtkb-rehearsal-package-ruff-clean-001` (GO at `-002`) - the proven drift-prevention regression-guard precedent (`platform_tests/scripts/test_rehearse_lint_clean.py`) whose structure the new `groundtruth-kb/`-scoped guard mirrors.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane batch; WI-3498 is in scope.

## Owner Decisions / Input

- `DELIB-20265457` - owner AUQ (2026-06-21) directing the authoring of NEW implementation proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items as a governed batch; this is the durable owner-decision evidence authorizing WI-3498 to be proposed.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the non-fast-lane batch project authorization that scopes implementation of this WI through active project membership; WI-3498 (P2, origin=improvement) is covered by this authorization, so no further per-item owner approval is required beyond the bridge GO. (This WI is NON-fast-lane: it spans 18 target files, exceeding the small-defect fast-lane size guide, hence batch PAUTH coverage rather than the reliability fast-lane standing authorization.)

## Proposed Scope

Minimal, mechanical-where-safe cleanup of the currently-drifting `groundtruth-kb/` files, plus a scoped drift-prevention guard. No behavior change to any runtime path.

1. **Lint fixes (`ruff check`), per file:**
   - `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py`: apply `UP037` (drop quotes from the `-> "DispatchRule"` return annotation; the class is in scope via `from __future__ import annotations` or forward-ref resolution) and `SIM103` (inline `return self.activities and not _matches_optional(...)` -> `return not (...)` per ruff's suggestion). These are `--fix`/`--unsafe-fixes` safe but will be reviewed line-by-line.
   - `groundtruth-kb/templates/hooks/_delib_common.py`: remove the unused `from datetime import UTC, datetime` import (`F401` x2). Confirm no later use before removal.
   - `groundtruth-kb/templates/hooks/gov09-capture.py`: apply `SIM110` (replace the `for`-loop-with-early-return by `return any(pat.search(prompt) for pat in GOV09_PATTERNS)`), preserving identical truth semantics.
   - `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`: fix `E501` (x2) by wrapping the two long string-literal fragments (lines ~358 and ~384) into adjacent concatenated string literals under the 120-col limit, with byte-identical rendered output (no change to the generated report text).
   - `groundtruth-kb/tests/framework/test_dispatch_state_recovery.py`: remove the unused `import os` (`F401`). Confirm no `os.` usage remains.
2. **Format fixes (`ruff format`):** run `ruff format` on the 12 files `ruff format --check` currently flags (`groundtruth-kb/scripts/audit_adr_dcl_metadata.py` + the 11 `groundtruth-kb/tests/test_*.py` files listed in Claim). These are whitespace/wrapping-only rewrites; no logic changes.
3. **Drift-prevention regression guard (new):** add `platform_tests/scripts/test_groundtruth_kb_ruff_clean.py` modeled on `platform_tests/scripts/test_rehearse_lint_clean.py` — two tests that run `ruff check groundtruth-kb/` and `ruff format --check groundtruth-kb/` via `sys.executable -m ruff` and assert returncode 0, so this class of drift fails fast in the future (the existing CI `lint.yml` does not cover the `groundtruth-kb/` tree). The guard is scoped to the whole `groundtruth-kb/` tree so it also prevents regressions in files not currently drifting.

Out of scope: any change to `groundtruth-kb/pyproject.toml` ruff configuration (ruleset, per-file-ignores, line-length); any non-style refactor; any change under `applications/`.

## Specification-Derived Verification Plan

| Spec / governing config clause | Derived test | Assertion |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + `groundtruth-kb/pyproject.toml` `[tool.ruff.lint]` `select` (check compliance) | `test_groundtruth_kb_passes_ruff_check` (new, in `platform_tests/scripts/test_groundtruth_kb_ruff_clean.py`) | `python -m ruff check groundtruth-kb/` exits 0 (no `UP037`/`SIM103`/`F401`/`SIM110`/`E501` violations remain). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + `groundtruth-kb/pyproject.toml` `[tool.ruff.format]` `quote-style` (format compliance) | `test_groundtruth_kb_passes_ruff_format_check` (new) | `python -m ruff format --check groundtruth-kb/` exits 0 (0 files would be reformatted). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (debt surfaces as a failing artifact) | both new tests, as a drift guard | The new guard fails (non-zero) if any future change reintroduces `groundtruth-kb/` ruff drift, mirroring `test_rehearse_lint_clean.py`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` `CLAUSE-IN-ROOT` | manual/path review (no separate test) | All 18 changed paths are inside `E:\GT-KB`; none under `applications/`. |
| No-regression of edited test modules | existing `groundtruth-kb/tests/` suite + edited templates/hooks | The reformatted/edited test and template files still import and run; the touched hook templates are syntactically valid and behavior-identical. |

Execution commands (post-implementation, run by Prime then re-checked by Loyal Opposition):
- `python -m pytest platform_tests/scripts/test_groundtruth_kb_ruff_clean.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py groundtruth-kb/templates/hooks/_delib_common.py groundtruth-kb/templates/hooks/gov09-capture.py groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py groundtruth-kb/scripts/audit_adr_dcl_metadata.py groundtruth-kb/tests/framework/test_dispatch_state_recovery.py groundtruth-kb/tests/test_bridge_paths.py groundtruth-kb/tests/test_cli_projects.py groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py groundtruth-kb/tests/test_full_tree_type_checks.py groundtruth-kb/tests/test_internal_helpers_type_checks.py groundtruth-kb/tests/test_public_api_type_checks.py groundtruth-kb/tests/test_slice_4_doctor_test_layout.py groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py groundtruth-kb/tests/test_spec_event_surfacer.py groundtruth-kb/tests/test_term_disambiguation.py platform_tests/scripts/test_groundtruth_kb_ruff_clean.py`
- `python -m ruff format --check` over the same 18 paths (whole-tree equivalent: `python -m ruff check groundtruth-kb/` and `python -m ruff format --check groundtruth-kb/` should both exit 0).

## Acceptance Criteria

1. `python -m ruff check groundtruth-kb/` exits 0 (0 errors).
2. `python -m ruff format --check groundtruth-kb/` exits 0 (0 files would be reformatted).
3. The new `platform_tests/scripts/test_groundtruth_kb_ruff_clean.py` passes (both tests return 0).
4. `python -m ruff check` and `python -m ruff format --check` are clean on the new test file itself.
5. No behavioral change: the touched template/hook files render byte-identical generated output (esp. `impl_report_bridge.py` report text), and the edited `groundtruth-kb/tests/` modules still collect and run.
6. No change to `groundtruth-kb/pyproject.toml` ruff configuration and nothing under `applications/` is modified.

## Risks / Rollback

- Risk: an `--unsafe-fixes` auto-fix (`UP037` forward-ref, `SIM103` inline) changes evaluation semantics. Mitigation: apply those two fixes by hand / review the diff line-by-line; the SIM103 negation must preserve the exact boolean result; `UP037` is annotation-only (no runtime effect under `from __future__ import annotations`).
- Risk: removing an "unused" import that is actually used dynamically. Mitigation: grep each removed symbol (`UTC`, `datetime`, `os`) in its file before removal; ruff `F401` is conservative but the diff will be reviewed.
- Risk: the `E501` string-literal wrap accidentally alters generated text. Mitigation: split only at existing token boundaries into adjacent literals; verify rendered output is byte-identical (the generator concatenates fragments).
- Risk: the new whole-tree guard later flags drift introduced by an unrelated change, blocking that change's CI. This is the intended behavior (it surfaces debt early), not a defect; the remedy is to run `ruff check/format` before commit.
- Rollback: each edit is style-only and independently revertible; the new test file can be deleted. No migration, no data change, no schema change — fully reversible by `git revert` of the implementing commit.

## Files Expected To Change

Lint fixes (`ruff check`):
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py`
- `groundtruth-kb/templates/hooks/_delib_common.py`
- `groundtruth-kb/templates/hooks/gov09-capture.py`
- `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`
- `groundtruth-kb/tests/framework/test_dispatch_state_recovery.py`

Format fixes (`ruff format`):
- `groundtruth-kb/scripts/audit_adr_dcl_metadata.py`
- `groundtruth-kb/tests/test_bridge_paths.py`
- `groundtruth-kb/tests/test_cli_projects.py`
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py`
- `groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py`
- `groundtruth-kb/tests/test_full_tree_type_checks.py`
- `groundtruth-kb/tests/test_internal_helpers_type_checks.py`
- `groundtruth-kb/tests/test_public_api_type_checks.py`
- `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py`
- `groundtruth-kb/tests/test_spec_classifier_canonical_triggers.py`
- `groundtruth-kb/tests/test_spec_event_surfacer.py`
- `groundtruth-kb/tests/test_term_disambiguation.py`

New drift-prevention guard:
- `platform_tests/scripts/test_groundtruth_kb_ruff_clean.py`

(18 paths total; matches the `target_paths` line above.)

## Recommended Commit Type

`fix` - this clears accrued lint/format defects in the `groundtruth-kb/` tree and adds a regression guard against their reintroduction; it repairs drift from the project's governing ruff configuration with no new capability surface.

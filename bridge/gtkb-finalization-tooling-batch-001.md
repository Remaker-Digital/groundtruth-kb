NEW

# Finalization Tooling Batch - Review Independence, Claimed Paths, And VERIFIED-Gated Auto-Retire

bridge_kind: prime_proposal
Document: gtkb-finalization-tooling-batch
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; dispatch quiesced before filing; no protected implementation edits before GO.

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4974
Related Work Items: WI-4975, WI-4976

target_paths: ["scripts/bridge_review_independence.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "platform_tests/scripts/test_bridge_review_independence.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "platform_tests/skills/test_auto_retire_actuation_helper_parity.py", "platform_tests/hooks/test_project_completion_surface.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "groundtruth.db"]

implementation_scope: source, skill-helper, tests, backlog-metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal batches the three finalization-tooling defects Mike prioritized on 2026-07-02: WI-4974, WI-4975, and WI-4976. The objective is to remove the current one-by-one finalization workaround loop by fixing the underlying tools that misclassify bridge independence, miss metadata-only path evidence, and retire projects before the bridge reaches VERIFIED.

The dispatch topology is intentionally out of implementation scope for this batch. The dispatcher daemon must remain stopped, Claude/B must remain ineligible in `config/dispatcher/rules.toml`, and this batch must not re-enable B or restart automated dispatch after implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires the bridge file chain and dispatcher/TAFE state to remain the workflow authority. This proposal is a `NEW` Prime Builder request and must receive a Loyal Opposition `GO` before protected implementation begins.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Requires project implementation authority before protected source, test, or configuration mutation. This proposal is covered by `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702`.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - Governs the defect class directly: project auto-retirement must be gated by verified completion evidence, not merely terminal work-item resolution.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - Requires explicit author identity, harness, session, model, and configuration metadata on status-bearing bridge documents.
- `GOV-STANDING-BACKLOG-001` - The defects were preserved as backlog work items and are being handled through governed work-item/project metadata rather than ad hoc cleanup.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Treats the owner priority update, the defect batch, the bridge proposal, the work items, and final verification evidence as durable governed artifacts instead of transient chat-only coordination.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires the implementation to preserve traceability across work items, proposal/report artifacts, tests, and completion state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Applies because this batch changes lifecycle behavior around verified, complete, and retired project states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Applies to edits under `groundtruth-kb/src/groundtruth_kb/project/**`; the batch changes GT-KB platform project lifecycle code in-root and does not move application or adopter boundaries.
- `ADR-CROSS-HARNESS-PARITY-001` - Applies because this proposal touches harness-specific verify helper copies. The intended behavior is equivalent across Claude Code, Codex, and Cursor.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Requires an explicit cross-harness disposition when harness-surface files are in scope. This proposal declares parity below and does not request a waiver.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires proposal linkage to a project and work item. This proposal declares `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`, WI-4974, WI-4975, WI-4976, and the governing PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete governing specification links. The linked GOV/DCL records above define the acceptance surface.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the implementation report and LO verification to cite specification-derived tests, not just code inspection.

## Cross-Harness Disposition

Behavioral parity required; no waiver requested.

- Claude Code / harness B: `.claude/skills/verify/helpers/write_verdict.py` must receive the same leading-dot path preservation behavior as Codex and Cursor.
- Codex / harness A: `.codex/skills/verify/helpers/write_verdict.py` must receive the same leading-dot path preservation behavior as Claude Code and Cursor.
- Cursor / harness E: `.cursor/skills/verify/helpers/write_verdict.py` must receive the same leading-dot path preservation behavior as Claude Code and Codex.
- Antigravity / harness C, Ollama / harness D, and OpenRouter / harness F: no harness-specific verify-helper file is targeted in this batch, so no behavioral delta or waiver is requested for those harnesses.

Verification must include a parity-sensitive test path that fails if one updated verify helper preserves dot-directory paths while another strips or drops them.

## Prior Deliberations

- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` - Owner directive for this exact batch: keep dispatch quiesced, keep B ineligible until the hung-worker root cause is fixed, fix WI-4974/WI-4975/metadata-slice handling together, then resume auto-processing only after the fixes land.
- `DELIB-WI4723-OWNER-PROCEED-20260621` - Prior owner authorization for VERIFIED finalization-gate retry repair. This batch continues the same finalization reliability line but addresses different failure modes.
- `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` - Prior decision establishing strict implementation-start and verification-heading alignment. This batch keeps source edits behind a GO and defines spec-derived test evidence up front.
- `bridge/gtkb-wi4940-bridge-metadata-write-time-enforcement-004.md` - Prior bridge metadata hardening predecessor. This batch relies on write-time bridge metadata being authoritative enough for review-independence and VERIFIED-gated retirement decisions.
- `platform_tests/skills/test_verified_finalization_validation_hardening.py` - Existing finalization validation hardening test surface to extend for dot-directory claimed-path extraction.

## Owner Decisions / Input

Owner approval evidence is `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE`, captured from Mike's 2026-07-02 priority update. The same directive is also the operational constraint: do not restart automated dispatch, do not re-enable Claude/B dispatch eligibility, and do not fold this work into a broad dirty-worktree sweep commit.

No additional owner AUQ is required before filing this proposal. A Loyal Opposition `GO` is required before Prime Builder edits protected source, skill-helper, or test files.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` cover the behavioral requirements for bridge authority, project authorization, verified completion retirement, and specification-derived verification. The three concrete work items define the defect-specific deltas:

- WI-4974: Fix bridge review-independence comparator glob over-match on prefix-superset slugs.
- WI-4975: Fix `write_verdict` leading-dot stripping that excludes dot-directory paths from VERIFIED claimed-path extraction.
- WI-4976: Fix metadata-only finalization path extraction and auto-retirement so metadata-backed slices cannot retire before bridge VERIFIED.

## Spec-Derived Verification Plan

- For `GOV-FILE-BRIDGE-AUTHORITY-001` and WI-4974, add or extend `platform_tests/scripts/test_bridge_review_independence.py` so versioned bridge-file matching is exact for `gtkb-<slug>-NNN.md` and `slug-NNN.md`, and prefix-superset slugs are excluded. Include an explicit test that reviewed-reference parsing tolerates a path followed by a descriptor instead of falling back to overbroad glob discovery.
- For `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, preserve required author metadata in this proposal and in the implementation report; run the existing bridge author metadata gate if the implementation produces another status-bearing bridge file.
- For `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, confirm the implementation report cites the owner directive, PAUTH, WI-4974/WI-4975/WI-4976, bridge file, and targeted tests as the durable artifact chain.
- For `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, verify the implementation only changes in-root GT-KB platform paths declared in `target_paths` and does not relocate adopter/application artifacts.
- For `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, run parity-sensitive helper tests that exercise the Claude Code, Codex, and Cursor `write_verdict.py` copies and fail on divergent leading-dot path handling.
- For `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` and WI-4976, extend project completion/retirement tests so a terminal/resolved work item with only `NEW` or `GO` bridge evidence does not auto-retire the project. Add a positive case where the same member can retire only after related bridge evidence reaches `VERIFIED`.
- For WI-4976 metadata-only path handling, extend `scripts/project_verified_completion_scanner.py` and related project completion tests so `groundtruth.db`-only/member-metadata slices are visible to the scanner but remain excluded from retirement until VERIFIED evidence exists.
- For `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and WI-4975, extend `platform_tests/skills/test_verified_finalization_validation_hardening.py` so `.claude/`, `.codex/`, `.cursor/`, `.github/`, and comparable leading-dot directory paths remain eligible claimed paths in `write_verdict` helpers.
- Run targeted tests after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_review_independence.py -q --tb=short
python -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short
python -m pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short
```

- Run style and focused regression checks after implementation:

```text
python -m ruff check scripts/bridge_review_independence.py scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_bridge_review_independence.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py
python -m ruff format --check scripts/bridge_review_independence.py scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_bridge_review_independence.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py
```

- Before and after implementation, verify dispatch remains quiesced:

```text
python -m groundtruth_kb.cli bridge dispatch daemon status --json
python -m groundtruth_kb.cli bridge dispatch status --json
```

Expected result: the daemon remains stopped, Claude/B remains `can_receive_dispatch=false`, and no implementation step reactivates automated dispatch.

## Risk / Rollback

Primary risk is that stricter VERIFIED-gated retirement leaves more projects open until their bridge metadata is repaired. That is the intended fail-safe: an open project is preferable to an auto-retired project whose bridge never reached LO VERIFIED. Rollback is a single scoped revert of the source/test/skill-helper changes plus any batch-specific backlog metadata changes; append-only bridge and deliberation records must remain as history.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-finalization-tooling-batch`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the batch corrects existing finalization defects and adds regression coverage around the corrected behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

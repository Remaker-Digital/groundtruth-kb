NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: prime_proposal
Document: gtkb-inventory-drift-toolchain-flux-stability
Project Authorization: PAUTH-WI-4217-INVENTORY-DRIFT-TOOLCHAIN-FLUX
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4217
target_paths: ["scripts/collect_dev_environment_inventory.py", "scripts/check_dev_environment_inventory_drift.py", "platform_tests/scripts/test_collect_dev_environment_inventory.py", "platform_tests/scripts/test_check_dev_environment_inventory_drift.py", ".groundtruth/inventory/dev-environment-inventory.json", ".groundtruth/inventory/dev-environment-inventory.md"]

# Implementation Proposal: Inventory Drift Toolchain Flux Stability

## Summary

Complete WI-4217 by preventing the inventory-drift gate from stranding commits during legitimate toolchain/version flux. The fix must keep public inventory evidence stable enough that a regenerated baseline matching live normalized inventory can be committed, without loosening material drift checks.

This is one of two coordinated sibling proposals for the inventory-drift gate. The sibling proposal uses the same target paths because the root fix is shared. Implementation must wait until both sibling threads have Loyal Opposition GO verdicts and both implementation-start packets are active before touching the overlapping target paths.

## Prior Deliberations

- Backlog row WI-4217 records the inventory-drift gate defect being addressed by this proposal.
- DELIB-2813 records the current owner directive to continue until the listed items are completed and supports the narrow PAUTH cited above.
- The related sibling thread is the other half of the shared root fix; neither sibling authorizes partial overlapping implementation by itself.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1924` — seed=search; bridge_thread; Bridge thread: gtkb-env-inventory-drift-control-001 (10 versions, VERIFIED)
- DA: `DELIB-1650` — seed=search; bridge_thread; Loyal Opposition Verification - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001
- DA: `DELIB-2533` — seed=search; bridge_thread; Bridge thread: gtkb-inventory-regen-chore-commit-2026-05-29 (6 versions, VERIFIE
- DA: `DELIB-1653` — seed=search; bridge_thread; Loyal Opposition Verification - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001
- DA: `DELIB-1652` — seed=search; bridge_thread; Loyal Opposition Verification - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001

## Owner Decisions / Input

No new owner decision is required. The active PAUTH authorizes source, test, config, and governance-evidence changes for WI-4217 while preserving normal bridge GO, implementation-start packet, post-implementation report, and Loyal Opposition verification gates.

## Specification Links

- .claude/rules/file-bridge-protocol.md
- .claude/rules/codex-review-gate.md
- .claude/rules/project-root-boundary.md
- .claude/rules/operating-model.md
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- SPEC-SEC-HOOK-PORTABILITY-001
- SPEC-DSI-COMMIT-GATE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001

## Requirement Sufficiency

Existing requirements are sufficient. The implementation is constrained to making writer/checker public inventory probe evidence deterministic and shared while preserving the material inventory-drift gate for non-toolchain and protected-path changes.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep public inventory and tests credential-free; private diagnostics remain redacted. | Collector validation tests and helper credential scan. | |
| CQ-PATHS-001 | Yes | Keep all edits under listed in-root target paths; no out-of-root probe evidence in public output. | Public validator and targeted pytest. | |
| CQ-COMPLEXITY-001 | Yes | Add a narrow shared public probe-normalization path instead of redesigning the drift gate. | Focused collector/checker tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing status/classification/version conventions and registry volatility semantics. | Regression tests for version flux and non-version drift. | |
| CQ-SECURITY-001 | Yes | Preserve credential and absolute-path rejection in public inventory. | Existing public validator test plus new probe-failure tests. | |
| CQ-DOCS-001 | Yes | Update generated inventory markdown only through the collector if source hash/baseline changes. | Regenerated .groundtruth/inventory/dev-environment-inventory.md. | |
| CQ-TESTS-001 | Yes | Add tests for deterministic gh public evidence, writer/checker parity, baseline-update acceptance, and non-version gate preservation. | python -m pytest platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py -q --tb=short. | |
| CQ-LOGGING-001 | Yes | Preserve checker summary/JSON shape and blocking reason names. | Existing checker tests plus JSON drift-check command. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check/format, collector regeneration, and drift check before implementation report. | Commands recorded in post-implementation report. | |

## Scope

In scope:

- Make public tool probe evidence deterministic and shared between scripts/collect_dev_environment_inventory.py and scripts/check_dev_environment_inventory_drift.py.
- Keep transient run diagnostics, resolved executable paths, raw output, and execution failures in private or local-only surfaces rather than public protected inventory evidence.
- Preserve public inventory validation against credentials and absolute paths.
- Preserve material drift blocking for non-toolchain keys and protected-path changes.
- Preserve baseline-update acceptance only when the regenerated baseline matches live normalized inventory.
- Preserve review_evidence_present, local_only_notice, path-boundary, and protected-artifact routing behavior.
- Regenerate .groundtruth/inventory/dev-environment-inventory.json and .groundtruth/inventory/dev-environment-inventory.md only through the collector if the source hash or public baseline changes.

Out of scope:

- Broad toolchain evidence volatility as a first-choice fix.
- Changes to .githooks/pre-commit or unrelated commit-gate behavior.
- Loosening credential, absolute-path, or protected-artifact checks.
- Treating this adjacent commit-gate issue as bridge queue dispatch work.

## Acceptance Criteria

- Public tool probe evidence is byte-stable between the writer and checker for the same tool and interpreter environment.
- gh probe success/failure wording no longer creates non-reconcilable public drift between the collector and checker.
- Legitimate toolchain version flux can be reconciled by regenerating the baseline when live normalized inventory matches the regenerated public inventory.
- Non-toolchain material drift remains blocking.
- Protected-path and bridge-evidence behavior is unchanged.
- Toolchain version/status/classification volatility semantics are preserved and verified against the current registry behavior.
- WI-4217 is resolved only after Loyal Opposition verifies the implementation report.

## Specification-Derived Verification Plan

- SPEC-DSI-COMMIT-GATE-001: run collector/checker regression tests proving material drift remains blocking while regenerated matching-live inventory is accepted.
- SPEC-SEC-HOOK-PORTABILITY-001: run public inventory validation tests proving credential and absolute path rejection are preserved.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001: run the collector and checker against live inventory after implementation and record the JSON result.
- Code behavior: run python -m pytest platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py -q --tb=short.
- Lint: run python -m ruff check scripts/collect_dev_environment_inventory.py scripts/check_dev_environment_inventory_drift.py platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py.
- Formatting: run python -m ruff format --check scripts/collect_dev_environment_inventory.py scripts/check_dev_environment_inventory_drift.py platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py.
- Inventory commands: run python scripts/collect_dev_environment_inventory.py and python scripts/check_dev_environment_inventory_drift.py --changed-path .groundtruth/inventory/dev-environment-inventory.json --json.

## Pre-Filing Preflight

Manual catch-22 check performed before filing: this proposal cites bridge authority, project linkage, source-of-truth freshness, standing backlog, security/commit-gate, and artifact-oriented governance specs triggered by the target paths and implementation proposal content.

The bridge artifact is filed under bridge/, and the live queue state is the bridge/INDEX.md entry for gtkb-inventory-drift-toolchain-flux-stability; the helper inserts the NEW: bridge/gtkb-inventory-drift-toolchain-flux-stability-001.md line at the top of that document entry without deleting or rewriting prior versions.

After filing, Prime Builder will run applicability, clause, and citation-freshness preflights and will revise if any blocking gap is reported.

## Risk And Rollback

Risk: normalizing public probe evidence too broadly could hide real toolchain drift. Mitigation: keep the fix narrow, preserve non-toolchain blocking behavior, and test that material drift still blocks. Rollback restores the source/test/inventory baseline changes from the implementation commit; bridge audit files remain append-only.

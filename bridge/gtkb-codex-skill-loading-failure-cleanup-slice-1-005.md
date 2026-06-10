REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e8991-a63a-7181-8f15-9e412e44f46d
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Codex Skill-Loading Failure Cleanup - Slice 1 - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-codex-skill-loading-failure-cleanup-slice-1
Version: 005 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-02 UTC
Responds-To: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-004.md`
Supersedes: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-003.md`
Recommended commit type: fix:
target_paths: [".claude/skills/*/SKILL.md", ".codex/skills/*/SKILL.md", "scripts/generate_codex_skill_adapters.py", "scripts/check_harness_parity.py", "scripts/check_codex_hook_parity.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_codex_skill_load_smoke.py"]

## Revision Claim

This revision preserves the approved scope from `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-003.md` and corrects the single implementation-start blocker identified by Loyal Opposition in `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-004.md`.

The only substantive change is the `## Requirement Sufficiency` operative wording. It now uses the exact gate-recognized phrase `Existing requirements sufficient`.

## NO-GO Resolution

### F1 - Requirement Sufficiency wording will fail implementation-start authorization

Accepted and corrected. The prior wording said "Existing requirements are sufficient." The revised section below says `Existing requirements sufficient` exactly, then explains the evidence.

## Background

Owner directive in S350 (2026-05-14), throughput improvement point 5, requested cleanup of Codex skill-loading failures. The reported failure mode is that Codex startup logs show malformed or missing YAML frontmatter in several `.codex/skills/*/SKILL.md` files while parity checks still pass.

The prior Loyal Opposition reviews confirmed the problem and accepted the durable repair shape: fix canonical skill sources and/or the generator, regenerate `.codex` adapters, and add parity/doctor loadability checks so "hash-current but not Codex-loadable" fails.

## In-Root Placement Evidence

All paths are under `E:\GT-KB`:

- `.claude/skills/*/SKILL.md` - canonical skill sources when frontmatter repair is needed.
- `.codex/skills/*/SKILL.md` - generated Codex adapters, regenerated for verification.
- `scripts/generate_codex_skill_adapters.py` - adapter generator.
- `scripts/check_harness_parity.py` - harness parity surface.
- `scripts/check_codex_hook_parity.py` - Codex parity/helper surface where applicable.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` - `gt platform doctor` integration.
- `platform_tests/scripts/test_codex_skill_load_smoke.py` - regression tests.

No `applications/` paths and no paths outside `E:\GT-KB` are in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Prior Deliberations

- `DELIB-1565` - bridge-skill unified verification; generated skill surfaces and parity checks can miss behavior defects.
- `DELIB-1646` and `DELIB-1645` - Codex harness parity baseline review and GO context.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - owner approval of the Codex harness parity specification bundle.
- `DELIB-1473` - Loyal Opposition hygiene-assessment skill advisory context.
- `bridge/gtkb-codex-hook-parity-fallback-*` family - establishes the Codex parity surface this proposal extends.

## Owner Decisions / Input

- Owner directive in S350 (2026-05-14): "Clean up Codex skill-loading failures."
- Owner directive in S350 (2026-05-14): "Please continue to parallelize work."

No new owner decision is required for this revision.

## Requirement Sufficiency

Existing requirements sufficient.

The harness-parity contract at `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 is unchanged; this proposal extends the parity check's failure detection surface. The file-bridge and verification requirements cited above already define the implementation and report evidence needed for this cleanup.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use generated or governed text only; do not include credentials. | Credential scan before filing and commit. | |
| CQ-PATHS-001 | Yes | Keep all target paths under `E:\GT-KB` and within declared `target_paths`. | Bridge preflight and implementation authorization validation. | |
| CQ-COMPLEXITY-001 | Yes | Keep parser and parity logic focused on frontmatter loadability. | Focused smoke tests review behavior boundaries. | |
| CQ-CONSTANTS-001 | Yes | Name any new status or parser constants clearly near existing parity constants. | Ruff check and focused test review. | |
| CQ-SECURITY-001 | Yes | Treat malformed adapters as startup-health defects without executing adapter content. | Tests use fixture files and parse-only behavior. | |
| CQ-DOCS-001 | Yes | Implementation report documents changed surfaces and generated adapter behavior. | Loyal Opposition bridge verification. | |
| CQ-TESTS-001 | Yes | Add smoke tests for missing frontmatter, malformed YAML, and valid frontmatter. | Focused pytest command in report. | |
| CQ-LOGGING-001 | N/A | | | Proposal does not change runtime logging. |
| CQ-VERIFICATION-001 | Yes | Run focused tests plus ruff check and ruff format check on changed Python files. | Commands and observed results in implementation report. | |

## Implementation Plan

1. Inventory all `.codex/skills/*/SKILL.md` files and parse YAML frontmatter.
2. Repair the durable source of malformed generated adapters by normalizing canonical `.claude/skills/*/SKILL.md` frontmatter and/or updating `scripts/generate_codex_skill_adapters.py`.
3. Regenerate `.codex/skills/*/SKILL.md` adapters from canonical source.
4. Extend harness parity, Codex parity, and/or `gt platform doctor` so a current-but-unloadable Codex adapter reports FAIL.
5. Add focused regression tests in `platform_tests/scripts/test_codex_skill_load_smoke.py`.

Direct hand edits to generated `.codex/skills/*/SKILL.md` files are acceptable only as generated outputs or temporary investigation artifacts removed before report filing.

## Spec-to-Test Mapping

- Codex skill adapters are loadable: new smoke tests cover missing frontmatter, malformed YAML, and valid skill frontmatter.
- Parity/doctor checks surface skill-load failures: focused parity/doctor tests assert parse failures report FAIL rather than PASS.
- Generated adapters remain governed outputs: generator check and regenerated adapter diff are reported in the implementation report.
- In-root placement: `git diff --check` over changed files and bridge artifacts.

## Acceptance Criteria

- Malformed or missing frontmatter in Codex skill adapters is detected by a deterministic test/check.
- The durable repair path is through canonical source/generator changes, not untracked hand edits.
- The implementation-start gate accepts this proposal after GO because `target_paths` and `Requirement Sufficiency` are parseable.
- Focused tests, ruff check, and ruff format check pass on changed Python files.

## Risk and Rollback

Risk is limited to generated skill adapter loadability and parity reporting. Rollback is a single revert of source/generator/check/test changes plus regenerated adapters.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

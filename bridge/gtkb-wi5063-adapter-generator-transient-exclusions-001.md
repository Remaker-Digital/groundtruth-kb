NEW
author_identity: prime-builder/antigravity/C
author_harness_id: C
author_session_context_id: 2026-07-07T00-39-00Z-prime-builder-C-antigravity
author_model: gemini-3.5-flash
author_model_version: Gemini 3.5 Flash (High)
author_model_configuration: Antigravity interactive; prime-builder

# Defect-Fix Proposal - Adapter generator _should_mirror_resource_file excludes transient temp/draft file prefixes

bridge_kind: prime_proposal
Document: gtkb-wi5063-adapter-generator-transient-exclusions
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5063

target_paths: ["scripts/generate_codex_skill_adapters.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The Codex skill adapter generator (`scripts/generate_codex_skill_adapters.py`) mirrors all files from `.claude/skills/<name>/helpers/` to `.codex/skills/<name>/helpers/` via `_sync_resource_mirror()`. This resource mirroring fails to exclude gitignored temporary or draft files (such as those prefixed with `_temp_`, `tmp_`, `draft-`, or `draft_`), leading to false-positive parity check failures in `test_codex_skill_adapter_parity_check`. This proposal adds prefix-based exclusions for transient files in the adapter generator.

## Defect / Reproduction

1. Create a transient file `_temp_verdict_xxx.md` in `.claude/skills/verify/helpers/`.
2. Run `test_codex_skill_adapter_parity_check`.
3. The check fails because the generator identifies that `.codex/skills/verify/helpers/_temp_verdict_xxx.md` would be updated/created, even though the file is gitignored.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/generate_codex_skill_adapters.py`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - Governs parity between Claude and Codex skill adapters. Exclusion of transient files is necessary to keep tests stable and prevent false-positives without compromising actual adapter parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Proposal must be filed and approved before source modification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Formalizes work-item defect reporting and bridge tracking.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Links this proposal to cross-harness parity specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification against the specified parity check.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Establishes PAUTH, project, and work-item linkage.
- `SPEC-AUQ-POLICY-ENGINE-001` - Binds interactive/automated role decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Focuses the fix strictly within the GT-KB internal platform development environment.
- `GOV-STANDING-BACKLOG-001` - Tracks this defect through `WI-5063` in the backlog.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Uses Codex/Antigravity helper write pathways.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Captures scope and requirements.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Triggers implementation upon GO approval.

## Prior Deliberations

- `DELIB-202665681` - WI-4978 Helper Compliance Audit Chokepoint - Loyal Opposition Verdict
- `DELIB-20265755` - Loyal Opposition Review - WI-4723 VERIFIED finalization index-lock retry revision
- `DELIB-202665698` - Loyal Opposition Verdict — WI-4978 Helper Compliance Audit Chokepoint (Post-Implementation Verification)
- `DELIB-202665696` - Loyal Opposition Verdict — WI-4978 Helper Compliance Audit Chokepoint (Post-Implementation Verification)
- `DELIB-202665697` - Loyal Opposition Verdict — WI-4978 Helper Compliance Audit Chokepoint (Post-Implementation Verification)


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - Active standing authorization for `PROJECT-GTKB-RELIABILITY-FIXES` under MemBase record.

## Requirement Sufficiency

Existing requirements sufficient.

## Proposed Scope

1. Modify `scripts/generate_codex_skill_adapters.py`'s `_should_mirror_resource_file(path: Path) -> bool` function.
2. Introduce a new constant `RESOURCE_EXCLUDED_PREFIXES = ("_temp_", "tmp_", "draft-", "draft_")` or similar.
3. Filter out any resource file whose `name` starts with any of these prefixes.
4. Ensure all existing tests in `platform_tests/skills/test_bridge_propose_helper.py` pass.
5. Create a specific test in `platform_tests/skills/test_bridge_propose_helper.py` that verifies transient prefixed files are ignored by resource mirroring.

## Out of Scope
- Modifying other harness adapter logic or registry settings outside `scripts/generate_codex_skill_adapters.py`.
- Changing other parts of `generate_codex_skill_adapters.py` unrelated to resource file mirroring exclusions.

## Specification-Derived Verification Plan

| Specification | Test or Verification Command |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Run `groundtruth-kb\.venv\Scripts\python.exe scripts/generate_codex_skill_adapters.py --update-registry --check` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the new unit test asserting that transient file mirroring is skipped, and run the full parity test. |

## Acceptance Criteria

- Running `scripts/generate_codex_skill_adapters.py` with transient files (e.g. `_temp_verdict_xxx.md`) present in `.claude/skills/verify/helpers/` does NOT result in copying them to `.codex/`.
- Existing and new tests pass successfully.
- No trailing whitespaces in the updated `scripts/generate_codex_skill_adapters.py`.

## Risks / Rollback

Risk is low as it only affects skill adapter generator mirroring exclusions.
Rollback: Revert `scripts/generate_codex_skill_adapters.py` changes.

## Files Expected To Change

- `scripts/generate_codex_skill_adapters.py`

## Recommended Commit Type

`fix`

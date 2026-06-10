REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Codex Skill-Loading Failure Cleanup - Slice 1 - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-codex-skill-loading-failure-cleanup-slice-1
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Responds-To: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-002.md`
Supersedes: `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`
Recommended commit type: `fix:`
target_paths: [".claude/skills/*/SKILL.md", ".codex/skills/*/SKILL.md", "scripts/generate_codex_skill_adapters.py", "scripts/check_harness_parity.py", "scripts/check_codex_hook_parity.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_codex_skill_load_smoke.py"]

## Summary

This revision preserves the original goal: remove Codex worker startup noise caused by malformed or missing YAML frontmatter in `.codex/skills/*/SKILL.md`, and make skill-load health visible in parity/doctor checks.

It resolves the Loyal Opposition NO-GO by:

- adding parser-supported top-level `target_paths` metadata;
- shifting durable repair away from hand-editing generated `.codex` adapters;
- including canonical source, adapter generator, parity, doctor, and tests in the implementation scope.

Implementation after GO must fix the durable source of malformed generated adapters, regenerate adapters, and add a loadability gate so "adapter hash-current but not Codex-loadable" fails.

## NO-GO Resolution

### F1: Implementation-start-compatible target paths

The revised proposal includes a top-level `target_paths: [...]` line so `scripts/implementation_authorization.py begin --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1` can derive the approved scope after GO.

### F2: Durable repair path

Generated `.codex/skills/*/SKILL.md` files are not the source of truth. They may be touched only as generated outputs from the canonical source/generator path. Durable repair must use one or more of these mechanisms:

- normalize malformed canonical `.claude/skills/*/SKILL.md` frontmatter where that source shape causes bad generated adapter output;
- update `scripts/generate_codex_skill_adapters.py` so generated Codex adapters preserve YAML frontmatter at line 1 when source frontmatter exists, and fail/diagnose when source frontmatter is missing or malformed;
- update `scripts/check_harness_parity.py`, `scripts/check_codex_hook_parity.py`, and/or `groundtruth-kb/src/groundtruth_kb/project/doctor.py` so an adapter that is current but not Codex-loadable reports FAIL.

Direct hand edits to `.codex/skills/*/SKILL.md` are not an acceptable durable repair unless they are produced by the generator or are strictly temporary investigation artifacts removed before implementation report filing.

## Background

Owner directive in S350 (2026-05-14), throughput improvement point 5, requested cleanup of Codex skill-loading failures. The reported failure mode is that Codex startup logs show malformed or missing YAML frontmatter in several `.codex/skills/*/SKILL.md` files while parity checks still pass.

The Loyal Opposition review confirmed the problem:

- three generated Codex adapters were observed with a first line that is not YAML frontmatter;
- `python scripts/generate_codex_skill_adapters.py --update-registry --check` reported PASS;
- `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json` reported PASS.

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
- `.claude/rules/bridge-essential.md`
- `.claude/rules/file-bridge-protocol.md`

## Prior Deliberations

- `DELIB-1565` - generated skill-surface semantics matter and parity checks can miss behavior defects.
- `DELIB-1646` and `DELIB-1645` - harness parity baseline NO-GO/GO context.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - owner approval of the Codex harness parity specification bundle.
- `DELIB-1473` - Loyal Opposition hygiene-assessment skill advisory and generated-adapter context.
- `bridge/gtkb-codex-hook-parity-fallback-*` - parity surface precedent.

## Owner Decisions / Input

Owner direction in S350 (2026-05-14) authorized cleanup of Codex skill-loading failures and continued parallel bridge work. No new owner input is required for this revised scope.

## Requirement Sufficiency

Existing requirements are sufficient. This change extends the existing Codex parity and doctor surface; it does not create a new harness role or skill-governance model.

## Implementation Plan

1. **Inventory phase**
   - Enumerate `.codex/skills/*/SKILL.md`.
   - Check that the first non-BOM bytes begin with YAML frontmatter at line 1.
   - Parse the YAML frontmatter for each adapter.
   - Record loadability failures and their canonical source path, when known.

2. **Durable repair phase**
   - Repair malformed canonical `.claude/skills/*/SKILL.md` frontmatter only when source-frontmatter shape is the cause.
   - Update `scripts/generate_codex_skill_adapters.py` so regenerated adapters keep YAML frontmatter at line 1 and place generated-marker comments after the frontmatter block.
   - Regenerate `.codex/skills/*/SKILL.md` through the generator; do not hand-maintain generated adapter content.

3. **Parity and doctor phase**
   - Add a Codex skill-load smoke check to `scripts/check_harness_parity.py` and/or `scripts/check_codex_hook_parity.py`.
   - Surface the check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` so `gt platform doctor` fails when generated adapters are hash-current but not loadable.
   - Report file path and parse error for each bad adapter.

4. **Regression tests**
   - Missing frontmatter fixture fails.
   - Malformed YAML fixture fails.
   - Generated-marker-before-frontmatter fixture fails.
   - Valid generated adapter passes.
   - Generator preserves YAML frontmatter at line 1 after regeneration.
   - Parity/doctor reports FAIL for a bad adapter even when generated metadata/hash appears current.

## Scope Boundaries

- This slice repairs load-time YAML/frontmatter health only.
- Semantic quality of skill instructions is out of scope.
- Removing a stale skill is allowed only when the inventory proves it is generated/stale and the removal is reflected by the generator/source-of-truth path.
- Broad skill redesigns must be split into separate bridge proposals.

## Spec-to-Test Mapping

| Linked specification / rule | Verification evidence |
|---|---|
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Parity/doctor checks fail for non-loadable Codex skill adapters and pass after generator/source repair. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_codex_skill_load_smoke.py` covers missing frontmatter, malformed YAML, marker-before-frontmatter, valid adapter, generator preservation, and parity/doctor failure behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched paths remain under `E:\GT-KB`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work proceeds only after GO and fresh implementation authorization. |
| `GOV-STANDING-BACKLOG-001` | Owner-directed throughput cleanup remains visible as bridge-mediated work, not hidden ad hoc repair. |

## Risks

- **Inventory finds many semantic skill defects:** this slice stops at loadability; semantic defects become separate bridge work.
- **Doctor FAIL breaks existing flows:** the intended final state is FAIL for non-loadable adapters; implementation may stage internal helper behavior, but the final report must prove invalid adapters fail.
- **Generated adapters drift again:** generator and parity changes are required specifically to prevent recurrence.

## Rollback

Revert source/generator/parity/doctor/test changes and regenerate adapters from the prior generator state. No MemBase mutation is expected.

## Verification Procedure

Required implementation verification after GO:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1
python scripts\generate_codex_skill_adapters.py --update-registry --check
python scripts\check_harness_parity.py --harness codex --role loyal-opposition --json
python -m pytest platform_tests/scripts/test_codex_skill_load_smoke.py -q --tb=short
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1 --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1
```

Manual or scripted smoke must also prove every `.codex/skills/*/SKILL.md` starts with YAML frontmatter at line 1 and parses cleanly.

## Acceptance Criteria

1. Proposal scope is machine-readable by `implementation_authorization.py`.
2. Durable repair includes canonical source and/or generator changes, not only generated adapter edits.
3. Generated `.codex` adapters parse cleanly and preserve YAML frontmatter at line 1.
4. Parity/doctor checks fail on malformed adapters and pass after repair.
5. Targeted regression tests pass.
6. Applicability and clause preflights pass.

## Planned Post-File Checks

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1 --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-loading-failure-cleanup-slice-1
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-codex-skill-loading-failure-cleanup-slice-1 --format json --preview-lines 20
git diff --check -- bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-003.md .gtkb-state/bridge-revisions/drafts/gtkb-codex-skill-loading-failure-cleanup-slice-1-003.md
```

End of proposal.

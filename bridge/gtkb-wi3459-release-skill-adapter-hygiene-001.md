NEW

# gtkb-wi3459-release-skill-adapter-hygiene - Clear release-blocking Codex skill adapter drift

bridge_kind: prime_proposal
Document: gtkb-wi3459-release-skill-adapter-hygiene
Version: 001
Author: Codex Prime Builder
Date: 2026-06-28 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; formal-release adapter hygiene

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3459

target_paths: [".claude/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-body.md", ".claude/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-draft.md", ".claude/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-final.md", ".claude/skills/verify/helpers/gtkb-wi4761-restore-ci-testing-integration-health-014-body.md", ".codex/skills/bridge/helpers/impl_report_bridge.py", ".codex/skills/bridge/helpers/revise_bridge.py", ".codex/skills/bridge/helpers/show_thread_bridge.py", ".codex/skills/bridge/helpers/draft-4676-verdict.md", ".codex/skills/bridge/helpers/draft-4678-verdict.md", ".codex/skills/bridge-propose/helpers/write_bridge.py", ".codex/skills/decision-capture/helpers/record_decision.py", ".codex/skills/spec-intake/helpers/spec_intake.py", ".codex/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/__pycache__/write_verdict.cpython-314.pyc", ".codex/skills/verify/helpers/_temp_verdict_gtkb-target-paths-coverage-preflight-006.md", ".codex/skills/verify/helpers/draft-gtkb-wi4678-finalization-git-write-retry-002.md", ".codex/skills/verify/helpers/draft-gtkb-wi4678-git-write-finalization-002.md", ".codex/skills/verify/helpers/draft-verdict-gtkb-reconcile-included-work-item-ids-semantics-011.md", ".codex/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-body.md", ".codex/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-draft.md", ".codex/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-final.md", ".codex/skills/verify/helpers/gtkb-wi4761-restore-ci-testing-integration-health-014-body.md", "platform_tests/scripts/test_no_tracked_skill_helper_scratch.py"]

implementation_scope: scaffold_update,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the release-candidate adapter drift gate by removing tracked scratch/verdict-body artifacts from skill helper directories and regenerating the Codex skill adapters from the canonical Claude skills.

The current release worktree fails the canonical adapter check:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check --update-registry
Codex skill adapters: would update 14 file(s)
```

The drift list includes current generated helper code plus noncanonical verdict drafts and temporary verdict bodies under `.codex/skills/**/helpers`. A direct tracked-file scan also shows canonical `.claude/skills/verify/helpers/*-body.md`, `*-draft.md`, and `*-final.md` files. These are completed bridge/verdict working artifacts, not reusable skill helper code. Keeping them under skill helper directories creates canonical-looking but non-authoritative fragments, inflates context, and violates the owner's release hygiene note that the path to good hygiene is reductive.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected skill adapter/test files require bridge GO and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specs and maps tests to the work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, work item, and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map specs to executed evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-3459` is the open backlog authority for clean-tree skill adapter regeneration and parity follow-on work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is bounded by the active skill-modernization PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - release-blocking hygiene findings are preserved through a work item, bridge proposal, report, and verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - scratch/verdict bodies should not masquerade as durable helper sources; durable evidence belongs in bridge artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the release-blocking adapter drift finding is promoted from scratch observation into a formal implementation slice.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the work remains inside GT-KB root and does not treat Agent Red or external wiki state as implementation authority.
- `ADR-CROSS-HARNESS-PARITY-001` - skill-surface changes must preserve cross-harness parity or declare a waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface proposals require an explicit Cross-Harness Disposition section.

## Prior Deliberations

- `DELIB-20265586` - owner authorized the bounded 2026-06-23 skill-modernization implementation set, including `WI-3459`.
- `WI-3459` - expressly deferred Codex/adapter regeneration until the tree was clean; the formal release worktree now provides the clean condition.
- Owner hygiene note, 2026-06-27 - architectural north star is minimal drift; actively clear stray noncanonical artifacts and avoid adding information that merely warns other information is unreliable.
- `bridge/gtkb-harness-registry-parity-sweep-009.md` - prior VERIFIED skill/parity thread is closed and cannot authorize fresh release-candidate drift.

## Owner Decisions / Input

No new owner decision is required. The active PAUTH `PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-BOUNDED-IMPLEMENTATION-2026-06-23` includes `WI-3459`, is active, and covers bounded source/test/hook/scaffold updates for the clean-tree skill modernization follow-on. The owner also made the formal release the top priority on 2026-06-27.

## Requirement Sufficiency

Existing requirements sufficient - `WI-3459`, `DELIB-20265586`, the active PAUTH, and the 2026-06-27 release hygiene note are enough to remove the stale helper scratch and converge generated adapters. No new user-facing behavior or governance rule is being added.

## Proposed Implementation

1. Delete the tracked canonical `.claude/skills/verify/helpers/*-body.md`, `*-draft.md`, and `*-final.md` verdict scratch artifacts listed in `target_paths`.
2. Run `scripts/generate_codex_skill_adapters.py` so Codex helper mirrors update to current canonical helper code and remove codex-only stale draft/temp/pycache helper files.
3. Add a focused regression guard that fails if tracked `.claude/skills/**/helpers` or `.codex/skills/**/helpers` paths contain scratch-like verdict/body artifacts (`draft-*`, `_temp*`, `*-body.md`, `*-draft.md`, `*-final.md`) or tracked Python cache artifacts.
4. Keep the implementation reductive: do not add warning prose or alternate documentation that explains these helper artifacts are unreliable; remove the ambiguity.

## Cross-Harness Disposition

- Claude skill surface: the canonical `.claude/skills/verify/helpers` directory loses only completed verdict/report scratch artifacts, not reusable helper code. Behavioral parity is preserved because the remaining canonical helper code is unchanged.
- Codex skill surface: generated `.codex/skills/**/helpers` files are regenerated from the canonical Claude skill surface through `scripts/generate_codex_skill_adapters.py`; codex-only scratch/temp/cache files are removed as mirror orphans. Behavioral parity is restored by the generator check passing.
- Antigravity/API skill surfaces: not directly targeted by this slice. No waiver is requested; the work is limited to Claude canonical skill helpers and Codex generated adapters.

## Spec-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Claim this bridge thread, create implementation-start packet, and validate the target paths before mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and ADR/DCL clause preflights before implementation and include the results in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Verify the bridge proposal carries the active PAUTH, `PROJECT-GTKB-SKILL-MODERNIZATION`, `WI-3459`, and concrete `target_paths`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps this table to executed command evidence. |
| `GOV-STANDING-BACKLOG-001` / `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `gt projects show PROJECT-GTKB-SKILL-MODERNIZATION`, `gt backlog show WI-3459 --json`, and `gt projects authorizations PROJECT-GTKB-SKILL-MODERNIZATION --json`. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `scripts/generate_codex_skill_adapters.py --check --update-registry` and the new helper-scratch regression guard prove Codex/Claude skill helper parity is restored without waivers. |
| Adapter drift gate | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check --update-registry` must pass. |
| Scratch-artifact hygiene | New focused pytest for tracked helper scratch artifacts must pass. |
| Existing no-cache guard | `python -m pytest platform_tests\scripts\test_no_tracked_pyc_artifacts.py <new-test> -q --tb=short` must pass. |
| Generator behavior | `python -m pytest platform_tests\scripts\test_generate_codex_skill_adapters.py -q --tb=short` must pass. |
| Formatting/lint | `python -m ruff check platform_tests\scripts\test_no_tracked_skill_helper_scratch.py` and `python -m ruff format --check platform_tests\scripts\test_no_tracked_skill_helper_scratch.py` must pass. |

## Acceptance Criteria

- `scripts/generate_codex_skill_adapters.py --check --update-registry` exits 0.
- No tracked `.claude/skills/**/helpers` or `.codex/skills/**/helpers` file matches the scratch/verdict-body patterns named above.
- No tracked `.pyc` or `__pycache__` artifact exists.
- Codex adapter helper mirrors remain byte-for-byte current with mirrorable canonical helper files.
- The release worktree remains clean after the implementation commit except for subsequent intentional release work.

## Risk And Rollback

Risk is low and mostly limited to accidentally deleting a genuinely reusable helper file whose name looks like a draft. The target paths have been inspected as verdict/report working artifacts rather than helper APIs, and the implementation is limited to the listed files. Rollback is a single revert of the implementation commit, which restores the prior adapter drift and helper scratch artifacts.

## Loyal Opposition Asks

1. Verify that the deletion targets are noncanonical scratch/verdict artifacts, not reusable helper code.
2. Verify that the existing generator is sufficient and no new generator behavior is needed.
3. Verify that the regression guard matches the owner's reductive hygiene direction without forbidding legitimate skill helper scripts.
4. Return GO if this is a safe release-blocker cleanup; otherwise return NO-GO with concrete path-specific findings.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

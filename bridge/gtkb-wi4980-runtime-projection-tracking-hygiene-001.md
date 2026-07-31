NEW

# WI-4980 Runtime Projection Tracking Hygiene

bridge_kind: prime_proposal
Document: gtkb-wi4980-runtime-projection-tracking-hygiene
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07T16:43:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4980-RUNTIME-PROJECTION-HYGIENE-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4980

target_paths: [".gitignore", ".cursor/gtkb-hooks/last-session-start*", ".cursor/gtkb-hooks/last-user-visible-startup*", ".cursor/gtkb-hooks/workstream-focus.cmd", "groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "scripts/worktree_finalization_triage.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_worktree_finalization_triage.py"]

implementation_scope: repository_metadata/source/test/governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4980 addresses a residual work-tree hygiene problem: regenerating harness runtime projection files are tracked or insufficiently ignored, so they reappear as dirty state every session and dilute real worktree-safety signals. The immediate observed case is the Cursor hook projection set under `.cursor/gtkb-hooks/`, including `last-session-start.json`, `last-user-visible-startup*.md`, `last-user-visible-startup*.meta.json`, and `workstream-focus.cmd`.

Recent WI-4979 already VERIFIED the report-only hygiene planner that classifies harness/runtime projections as `harness_runtime_projection` with candidate action `auto_ignore`. This proposal must not duplicate that planner. The remaining WI-4980 implementation should close the repository hygiene gap by ensuring regenerating runtime projections stop being treated as ordinary tracked work, while preserving local runtime files and keeping real source/test/config edits visible.

Expected implementation shape:

- Add precise ignore patterns for regenerating Cursor runtime projection outputs, and review whether analogous non-durable projection outputs are missing from existing ignore coverage.
- If tracked runtime projection files must be removed from version control, do so only through an enumerated, reviewable, non-destructive index/tracking change that preserves local runtime state; do not delete local files.
- Keep durable hook launchers and governed source files tracked.
- Add focused tests proving runtime projections are ignored or classified as auto-ignore while protected source/test/config changes remain visible.
- Preserve WI-4979's report-only default and refusal behavior for live cleanup.

This proposal does not authorize destructive cleanup, stash drop, worktree pruning, untracked-file deletion, broad worktree mutation, deployment, credential lifecycle, force-push, direct harness-to-harness invocation, or committing unrelated dirty files.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - default behavior is non-mutating; stale work-tree and runtime projection findings require evidence-first remediation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation proceeds only after bridge GO, implementation-start authorization, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - item-specific PAUTH bounds WI-4980 but does not bypass bridge lifecycle.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH satisfies owner approval only; it does not authorize implementation without GO and implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal carries PAUTH/project/work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites concrete governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map these requirements to executed tests.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - hygiene claims must derive from live git status and canonical registry reads rather than cached startup artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4980 remains a MemBase work item and must reach terminal state through evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve traceability across WI, PAUTH, bridge proposal, tests, report, and final disposition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner approval, proposal scope, and repository hygiene rationale are durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - recurring runtime projection dirt is a lifecycle trigger for explicit disposition, not silent accumulation.

## Prior Deliberations

- `DELIB-20260707-WI4980-IMPLEMENTATION-APPROVAL` - owner authorized WI-4980 for governed implementation proposal filing.
- `DELIB-202665836` / `bridge/gtkb-wi4980-runtime-projection-gitignore-authorization-002.md` - Loyal Opposition advisory GO confirmed WI-4980 was owner-gated and required fresh PAUTH plus a subsequent implementation proposal/GO before implementation.
- `bridge/gtkb-wi4980-runtime-projection-gitignore-authorization-001.md` - advisory proposal preserving the governance gate and candidate target paths.
- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - nearby work-tree hygiene batch context, but not direct WI-4980 implementation authorization.
- `DELIB-20260867` - owner authorization for the recurring work-tree hygiene program and stale-work threshold.
- `bridge/gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-006.md` - VERIFIED report-only auto-resolve planner; WI-4980 must build on it rather than duplicate it.

## Owner Decisions / Input

Owner approval is recorded by `DELIB-20260707-WI4980-IMPLEMENTATION-APPROVAL`.

Bounded implementation authorization is recorded as `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4980-RUNTIME-PROJECTION-HYGIENE-20260707`.

The PAUTH includes WI-4980 only and forbids credential lifecycle, deployment, force-push, secret disclosure, destructive bulk cleanup, stash drop, branch/worktree prune, untracked-file deletion, deletion of local runtime state, broad bulk status mutation, direct harness-to-harness invocation, and committing unrelated dirty files.

## Bulk Operation Guard

This is not a bulk cleanup, bulk status mutation, or broad worktree operation. It is a single-WI implementation proposal for WI-4980 with enumerated target paths and item-specific owner approval evidence (`DELIB-20260707-WI4980-IMPLEMENTATION-APPROVAL`) plus item-specific PAUTH (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4980-RUNTIME-PROJECTION-HYGIENE-20260707`).

No formal-artifact-approval packet is required because this proposal does not create, promote, retire, or mutate GOV/ADR/DCL/SPEC records. If implementation discovers that a formal artifact mutation is required, implementation must stop and return through the applicable formal-artifact approval path before mutating that artifact.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-WORK-TREE-HYGIENE-001`, WI-4980's backlog record, the WI-4980 advisory GO, and the verified WI-4979 planner define enough behavior for this residual implementation. No new or revised GOV/ADR/DCL/SPEC mutation is proposed.

## Spec-Derived Verification Plan

| Governing surface | Required implementation behavior | Verification |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Runtime projection outputs stop appearing as ordinary worktree dirt while local runtime state is preserved. | Add or extend tests with `.cursor/gtkb-hooks/last-session-start.json`, `last-user-visible-startup*.md`, `.meta.json`, and `workstream-focus.cmd`, proving the intended ignore/tracking behavior or auto-ignore classification. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Hygiene checks derive from live git status and do not rely on cached startup reports. | Run focused CLI/planner tests that initialize a git repo, create projection files, and assert live status classification. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | PAUTH does not authorize source/test/config mutation until latest GO and implementation-start packet. | Implementation report must cite `implementation_authorization.py begin --bridge-id gtkb-wi4980-runtime-projection-tracking-hygiene` before protected edits. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Each linked requirement has executed test evidence. | Post-implementation report must include exact pytest commands and separate `ruff check` and `ruff format --check` results for changed Python files. |
| Standing backlog and artifact-oriented governance | WI-4980 terminal state is tied to bridge evidence and does not hide unrelated dirty files. | Backlog/project metadata update only after implementation report and VERIFIED; tests assert protected source/test/config files remain manual-review visible. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py scripts/worktree_finalization_triage.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_worktree_finalization_triage.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py scripts/worktree_finalization_triage.py platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_worktree_finalization_triage.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4980-runtime-projection-tracking-hygiene --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4980-runtime-projection-tracking-hygiene
```

If the implementation only changes `.gitignore` plus repository tracking metadata and no Python files, the ruff commands may be reported as not applicable with that exact changed-file rationale; the focused pytest and bridge preflights still apply.

## Risk / Rollback

Main risk is hiding meaningful harness or configuration changes by over-broad ignore patterns. Keep patterns exact, test that durable hook launchers remain tracked/visible, and avoid blanket `.cursor/` or `.codex/` ignores.

Second risk is accidental loss of local runtime state. If tracked projection files are removed from version control, use only an enumerated non-destructive tracking/index approach and preserve local working copies; do not delete local files.

Rollback is a single revert of the implementation commit plus any enumerated tracking changes. Bridge files and PAUTH records remain append-only audit evidence.

## Bridge Filing

This proposal is filed as the first implementation proposal for `gtkb-wi4980-runtime-projection-tracking-hygiene`. The prior `gtkb-wi4980-runtime-projection-gitignore-authorization` chain is advisory context only and is not treated as implementation authorization.

## Recommended Commit Type

`fix:` - repairs recurring worktree-hygiene noise caused by regenerating runtime projection files being tracked or insufficiently ignored.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

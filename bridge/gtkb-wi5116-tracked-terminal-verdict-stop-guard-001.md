NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; transcript role ::init gtkb pb; Default mode; PowerShell; project root E:\GT-KB
author_metadata_source: explicit current Codex session metadata

# WI-5116 - Tracked terminal verdict STOP guard for finalization repair planner

bridge_kind: prime_proposal
Document: gtkb-wi5116-tracked-terminal-verdict-stop-guard
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5116

target_paths: ["scripts/per_thread_finalization_repair.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "docs/procedures/per-thread-finalization-repair.md"]

implementation_scope: source, focused tests, and documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harden the just-verified per-thread finalization repair planner so tracked modified or deleted terminal `VERIFIED` verdict files are classified as `mixed_provenance_stop`, not `terminal_verified_repair_candidate`, even when their implementation target paths are clean.

## Claim

After WI-5116 finalization repair landed, the live planner reported `gtkb-wi4567-bridge-proposal-filing-service` as a `terminal_verified_repair_candidate`. Inspection showed the only dirty path in that thread is a tracked modified terminal verdict file: `M bridge/gtkb-wi4567-bridge-proposal-filing-service-004.md`. That is not auto-finalizable and matches the modified-terminal-verdict provenance hazard covered by `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`.

## Defect / Reproduction

Commands run after commit `b1750002`:

```text
python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330
```

Observed one `terminal_verified_repair_candidate`:

```text
gtkb-wi4567-bridge-proposal-filing-service
```

But:

```text
git status --short -- bridge/gtkb-wi4567-bridge-proposal-filing-service-*.md
```

reported:

```text
 M bridge/gtkb-wi4567-bridge-proposal-filing-service-004.md
```

This must be a STOP class, not a repair candidate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`

## Prior Deliberations

- `bridge/gtkb-wi5116-per-thread-finalization-repair-004.md` - VERIFIED implementation of the first planner slice.
- `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` - precedent requiring modified terminal verdict provenance to fail closed.
- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - prior worktree-sprawl precedent: do not bulk-commit ambiguous terminal bridge dirt.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- `DELIB-202666274` backs the active Tree Stabilization PAUTH.
- Owner directive in Codex session `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem has been resolved.

## Requirement Sufficiency

Existing requirements are sufficient. This is a fail-closed correction to the already approved WI-5116 planner and does not change finalization authority.

## Proposed Scope

- Update `scripts/per_thread_finalization_repair.py` so any dirty tracked terminal `VERIFIED` bridge file in a thread forces `mixed_provenance_stop`.
- Add focused tests for tracked modified and tracked deleted terminal `VERIFIED` verdicts.
- Update the runbook class/STOP wording to mention tracked modified/deleted terminal verdicts explicitly.

## Explicit Non-Scope

- No commits, staging, deletion, dispatcher mutation, PAUTH mutation, or finalization of `gtkb-wi4567-bridge-proposal-filing-service`.
- No changes to `write_verdict.py`, `auto_finalize_sweep.py`, or `groundtruth_kb.hygiene.auto_resolve`.
- No broad drain.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fixture with tracked modified terminal `VERIFIED` bridge file | Planner reports `mixed_provenance_stop`. |
| `GOV-WORK-TREE-HYGIENE-001` | Fixture with tracked deleted terminal `VERIFIED` bridge file | Planner reports `mixed_provenance_stop`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight | Required spec linkage is mechanically satisfied. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Existing no-mutation checks | Tool remains report-only with empty mutation capabilities. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short` | Focused tests pass. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | GO plus implementation-start packet before protected edits | No protected edit occurs before GO/start. |

Expected verification commands:

```text
python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short
python -m ruff check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
python -m ruff format --check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330
```

## Acceptance Criteria

- Tracked modified terminal `VERIFIED` bridge files never produce `terminal_verified_repair_candidate`.
- Tracked deleted terminal `VERIFIED` bridge files never produce `terminal_verified_repair_candidate`.
- The live `gtkb-wi4567-bridge-proposal-filing-service` case is classified as `mixed_provenance_stop` or another STOP class.
- Existing clean untracked terminal candidate fixture still reports `terminal_verified_repair_candidate`.

## Risks / Rollback

Risk is low and limited to making the planner more conservative. Rollback is a scoped revert of the three target files, preserving bridge audit files.

## Files Expected To Change

- `scripts/per_thread_finalization_repair.py`
- `platform_tests/scripts/test_per_thread_finalization_repair.py`
- `docs/procedures/per-thread-finalization-repair.md`

## Recommended Commit Type

`fix`

REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-22T15-20Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation Prime Builder auto-builder

# Revised Proposal - Auto-retire on VERIFIED, aligned to implements-linked VERIFIED coverage

bridge_kind: prime_proposal
Document: gtkb-auto-retire-on-verified-actuation-slice-1
Version: 007
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-auto-retire-on-verified-actuation-slice-1-006.md

Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4741

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "scripts/project_verified_completion_scanner.py", "platform_tests/scripts/test_auto_retire_on_verified.py"]

## First-Line Role Eligibility Check

Resolved session role: Prime Builder, by explicit owner instruction for this fresh automation session. Latest bridge status reviewed: NO-GO in `bridge/gtkb-auto-retire-on-verified-actuation-slice-1-006.md`. Status authored here: REVISED. Prime Builder is authorized to author REVISED proposal entries responding to Loyal Opposition NO-GO verdicts.

## Revision Claim

This revision addresses the `-006` P1 finding by removing the member-WI terminal-state retirement criterion from the proposal. Implementation will remain aligned to `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5:

- A project can auto-retire only when its explicitly linked gating work items are covered by implements-linked bridge threads whose VERIFIED status is established.
- The project-artifact link must be active, `artifact_type = 'bridge_thread'`, `relationship = 'implements'`, and point to the bridge thread slug.
- The covered work item id must appear in a `Work Item:` metadata line in that implements-linked thread's version chain.
- Member work item terminal statuses such as `resolved`, `retired`, `wont_fix`, or `not_a_defect` do not satisfy the automatic-retirement trigger by themselves.
- Active `plan_incomplete` completion guards continue to block retirement.

The detector archival-blindness fix is retained, but it does not change the retirement criterion. It only lets the checker find VERIFIED status evidence for the same implements-linked bridge thread after the live bridge queue has archived or pruned that VERIFIED thread from the live status surface. It must not count incidental VERIFIED citations, unrelated bridge threads, or member terminal statuses.

## Findings Addressed

### P1 - Proposed member-WI terminal criterion is not yet backed by the governing specification or cited decision evidence

Response: corrected by choosing the alignment path requested in the NO-GO. This revision does not seek a spec update and does not cite the undocumented "member-WI terminal" criterion as sufficient. `WI-4755` remains the separate hygiene item for deciding whether that broader practice should ever become a governed criterion. WI-4741 proceeds against the current specified implements-linked VERIFIED rule.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governing rule for automatic project completion and retirement, including the v5 keep-open election, the v4 implements-linked VERIFIED discriminator, and the fail-safe behavior.
- `GOV-STANDING-BACKLOG-001` - WI-4741 is a governed backlog item and the implementation must preserve project lifecycle state truth.
- `GOV-08` - MemBase remains the single source of truth for project, authorization, and work-item lifecycle mutations.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation is bridge-mediated and the VERIFIED finalization event is a bridge authority surface.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - both Claude and Codex verify-helper twins must perform the same post-VERIFIED actuation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are within the GT-KB root and no adopter application surface is touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation preserves traceability among projects, work items, bridge threads, deliberations, and tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the implementation keeps lifecycle transitions grounded in durable governed artifacts rather than scratch state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - project retirement is a lifecycle transition and must expose clear trigger and guard behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing specification applicable to the bridge, project lifecycle, and harness parity surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is mapped to the cited specifications and executed against the changed implementation.
- `.claude/rules/bridge-essential.md` - bridge-essential operational guardrails apply to the proposal and implementation handoff.

## Prior Deliberations

- `DELIB-20265569` - owner decision to build WI-4741 auto-retire-on-VERIFIED automation now through the normal bridge path.
- `DELIB-20265228` - owner-approved v5 keep-open caller election; default auto-retirement behavior remains the specified automatic path.
- `DELIB-2276` - prior GO on retirement-machinery correction history.
- `DELIB-20264096` - prior NO-GO on project-retirement spec work.
- `bridge/gtkb-auto-retire-on-verified-actuation-slice-1-001.md` through `-006.md` - proposal/review history for WI-4741, including the helper-parity correction and the current criterion-alignment NO-GO.
- `WI-4750` - helper parity defect captured during review; this revision keeps both verify-helper twins in target scope and regression-locks byte identity.
- `WI-4755` - newly captured governance cleanup item for the member-terminal-status criterion drift; this proposal avoids depending on that unresolved broader criterion.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 already defines the automatic retirement trigger, the implements-linked VERIFIED work-item definition, the keep-open election, and the fail-safe behavior. `GOV-HARNESS-ROLE-PORTABILITY-001` already requires parity across harness helper surfaces. The revised implementation plan does not introduce a new retirement criterion, so no new requirement or owner decision is needed before implementation.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, add or extend a project-completion predicate that follows the current `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 rule:
   - collect the project's explicitly linked gating work items;
   - require active `project_artifact_links` rows for implements-linked bridge threads;
   - require each gating work item to be represented by a `Work Item:` metadata line in an implements-linked thread's version chain;
   - require the implements-linked thread's VERIFIED status evidence;
   - block when an active `plan_incomplete` completion guard exists;
   - emit fail-safe/manual-review output rather than retiring when coverage is missing.
2. In `scripts/project_verified_completion_scanner.py`, use the same implements-linked VERIFIED predicate or shared helper so the detector and runtime actuation cannot drift. The scanner may read archived VERIFIED evidence only for the same implements-linked thread slug, preserving the current discriminator while fixing archival-blindness.
3. In both `.claude/skills/verify/helpers/write_verdict.py` and `.codex/skills/verify/helpers/write_verdict.py`, add the same post-successful-VERIFIED finalization actuation call. The call must be lazy-imported and best-effort, and it must never roll back or block a valid VERIFIED finalization if actuation fails.
4. Add `platform_tests/scripts/test_auto_retire_on_verified.py` covering the automatic actuation, fail-safe guards, archived VERIFIED evidence, and helper parity.

Out of scope: member-WI terminal-status retirement, spec mutation, owner-decision mutation, direct canonical MemBase updates during implementation, bridge automation rewrites, and project retirement based on incidental VERIFIED citations.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` implements-linked VERIFIED definition | `test_auto_retire_requires_implements_linked_verified_coverage` | A project with all gating WIs covered by implements-linked VERIFIED bridge threads retires after VERIFIED finalization. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` fail-safe behavior | `test_member_terminal_statuses_alone_do_not_retire_project` | A project whose member WIs are terminal but lack implements-linked VERIFIED coverage remains active. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` guard behavior | `test_plan_incomplete_guard_blocks_auto_retire` | An active `plan_incomplete` guard prevents retirement even when VERIFIED coverage exists. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` scoped discriminator | `test_incidental_verified_thread_does_not_cover_work_item` | A VERIFIED thread without an active `relationship='implements'` project artifact link does not satisfy coverage. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` archival-blindness fix without criterion drift | `test_archived_verified_implements_thread_is_detected` | Archived VERIFIED evidence for the same implements-linked thread is counted, while unrelated archived VERIFIED evidence is not. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | `test_verify_helper_twins_remain_byte_identical_and_call_auto_retire` | The Claude and Codex verify-helper files are byte-identical and both contain the same actuation call site. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest and ruff commands on changed surfaces. | Executed checks prove the implementation against the cited spec clauses. |

Execution commands after implementation:

- `python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py platform_tests/scripts/test_auto_retire_on_verified.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py platform_tests/scripts/test_auto_retire_on_verified.py`

## Acceptance Criteria

1. Auto-retirement fires only when current `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 coverage is satisfied.
2. Member terminal statuses alone are explicitly regression-tested as insufficient.
3. Archived VERIFIED evidence is accepted only for an implements-linked thread slug that covers the relevant work item.
4. Active `plan_incomplete` guards and missing coverage fail safe without retirement.
5. Claude and Codex verify-helper twins remain byte-identical and invoke the same best-effort actuation call.
6. The detector and runtime actuation use the same completion predicate or shared helper.
7. Focused pytest and ruff verification commands pass.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION` - project authorization for WI-4741 implementation.
- `DELIB-20265569` - owner decision to build WI-4741 now.
- `DELIB-20265228` - owner decision approving the v5 keep-open election while preserving default automatic retirement.

No new owner input is required because this revision chooses the current specified criterion rather than advancing the unresolved member-terminal-status criterion.

## Risk And Rollback

Risk: archived VERIFIED evidence could be over-counted. Mitigation: gate archival evidence by the same active implements-link discriminator and work-item metadata scan, and add negative tests for unrelated archived VERIFIED records.

Risk: helper actuation could disrupt VERIFIED finalization. Mitigation: lazy import, broad best-effort exception handling, and a test proving an actuation failure does not roll back the verdict.

Risk: detector/runtime drift. Mitigation: share the predicate or test both paths against the same fixtures.

Rollback: remove the actuation call from both verify-helper twins, revert the lifecycle/scanner predicate changes, and remove `platform_tests/scripts/test_auto_retire_on_verified.py`. No canonical project lifecycle state is mutated during implementation.

## Recommended Commit Type

`feat`

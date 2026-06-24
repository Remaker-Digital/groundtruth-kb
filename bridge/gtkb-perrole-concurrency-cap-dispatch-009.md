REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-24T16-45-31Z-prime-builder-A-412357
author_model: Codex
author_model_version: GPT-5
author_model_configuration: bridge auto-dispatch; approval_policy=never; sandbox=workspace-write
author_metadata_source: auto-dispatch runtime prompt and durable harness registry

# Remediation Plan - Per-Role Concurrency Cap Dispatch Finalization

bridge_kind: prime_proposal
Document: gtkb-perrole-concurrency-cap-dispatch
Version: 009 (REVISED)
Date: 2026-06-24 UTC
Responds-To: bridge/gtkb-perrole-concurrency-cap-dispatch-008.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-CA9165

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py", "bridge/gtkb-perrole-concurrency-cap-dispatch-003.md"]
implementation_scope: verification-finalization remediation plan only; no source/test/config/KB/deployment/credential mutation in this revision
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Revision Claim

Prime Builder accepts the Loyal Opposition `NO-GO` at `bridge/gtkb-perrole-concurrency-cap-dispatch-008.md`.

This version provides the second required revision option from version 008: an interactive remediation plan that can re-establish a valid atomic finalization helper transaction without unsafe git-history changes, synthetic source edits, or unrelated worktree damage. It is not a request for `VERIFIED`, not a self-authored `DEFERRED`, and not another blocker-only restatement.

The plan is based on the current verified-finalization helper semantics. The helper builds `expected_paths` from the declared `--include` paths plus the new verdict path, records that path set in the verdict body, stages that explicit path set, and commits with the same explicit pathspec. It only requires paths with actual dirty/untracked content to appear in the staged set. Therefore already-committed implementation/report paths can still be part of the finalization path set without synthetic edits, as long as they are not carrying unrelated dirty changes at finalization time.

This auto-dispatched Prime Builder session does not run finalization. Current read-only evidence shows `scripts/cross_harness_bridge_trigger.py` has unrelated dirty worktree content (`git diff --stat HEAD -- scripts/cross_harness_bridge_trigger.py` reports two insertions), so finalizing now would risk bundling unrelated changes. The safe remediation is to return this concrete plan for Loyal Opposition review, then execute verification/finalization only in a session where the target path cleanliness preconditions below hold.

## First-Line Role Eligibility Check

- Durable identity source: `harness-state/harness-identities.json` maps `codex` to harness ID `A`.
- Role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` maps harness `A` to `prime-builder`.
- Live latest bridge status before this revision: `NO-GO` at `bridge/gtkb-perrole-concurrency-cap-dispatch-008.md`, confirmed by `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-perrole-concurrency-cap-dispatch --json`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-perrole-concurrency-cap-dispatch` reports rowid `23814` for session `2026-06-24T16-45-31Z-prime-builder-A-412357`.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to write `REVISED` after a latest `NO-GO`.

## Requirement Sufficiency

Existing requirements sufficient.

No new or revised product, platform, or governance requirement is needed for this remediation plan. The active issue is applying the existing Mandatory VERIFIED Commit-Finalization Gate through the verified helper's current pathspec semantics while avoiding unrelated dirty target-path content.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs bridge workflow authority, Prime Builder `NO-GO -> REVISED` response authority, and terminal verification discipline.
- `.claude/rules/file-bridge-protocol.md` - contains the Mandatory VERIFIED Commit-Finalization Gate and defines `DEFERRED` as owner-only.
- `.claude/rules/codex-review-gate.md` - defines implementation-start and verification gates and requires `VERIFIED` to use the atomic finalization helper.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification closure requires linked specification evidence and spec-derived test mapping.
- `SPEC-INTAKE-ca9165` - governing requirement for the per-role concurrency cap implementation.
- `SPEC-INTAKE-9cb2ee` - claim-gated implementation-start and per-item dedup context.
- `SPEC-INTAKE-57a736` - per-document lease context for same-role dispatch safety.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - deterministic dispatch cap value case carried forward from the approved proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - linkage and verification mapping requirements carried forward.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work-item metadata remain carried forward.
- `GOV-STANDING-BACKLOG-001` - `WI-AUTO-SPEC-INTAKE-CA9165` is governed backlog work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and evidence remain inside `E:\GT-KB`.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - carried from the approved proposal because the implementation intentionally leaves the single-harness dispatcher substrate unchanged.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - finalization semantics are audit artifacts and cannot be silently bypassed.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the blocker, plan, and next-step requirement are preserved as an artifact rather than transient dispatch memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - an audit/finalization blocker crossing governance semantics triggers explicit artifact disposition.

## Prior Deliberations

- `DELIB-20262483` - prior Loyal Opposition `NO-GO` for cross-harness dispatch concurrency-cap verification.
- `DELIB-20265831` - prior Loyal Opposition `NO-GO` on this per-role concurrency-cap blocker response, cited in version 008.
- `DELIB-20265459` - owner AUQ authorization on 2026-06-21 re-opened `WI-AUTO-SPEC-INTAKE-CA9165` for the per-role concurrency cap.
- `DELIB-20263189` - owner AUQ authorization on 2026-06-13 for the P1 dispatch specs and bridge-protocol reliability project scope.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-001.md` - original implementation proposal.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-002.md` - Loyal Opposition `GO` approving implementation.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-003.md` - Prime Builder implementation report.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-004.md` - Loyal Opposition `NO-GO` identifying the already-committed path set as the verification blocker.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-005.md` - Prime Builder blocker revision accepting the version 004 finding.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-006.md` - Loyal Opposition `NO-GO` continuing the blocker and confirming that version 005 did not create a valid `VERIFIED` path.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-007.md` - Prime Builder blocker revision preserving the need for governed direction.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-008.md` - Loyal Opposition `NO-GO` requiring a governed waiver/protocol amendment, an interactive remediation plan, or owner-directed `DEFERRED`.

Deliberation search in this session:

```text
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "gtkb-perrole-concurrency-cap-dispatch VERIFIED finalization after-the-fact committed implementation report paths remediation plan" --limit 10
```

No later owner waiver or protocol amendment was found in the returned set. This revision therefore chooses the non-waiver remediation-plan path.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch, and this revision does not claim a new owner approval.

Carried-forward owner authorization evidence:

- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165` authorized the original implementation flow.
- `DELIB-20265459` and `DELIB-20263189` are the carried-forward AUQ evidence for the work item and project scope.

Owner-only `DEFERRED` is not available to this worker because `.claude/rules/file-bridge-protocol.md` requires concrete owner evidence plus a deferral reason and clear/resume condition for `DEFERRED`. This Prime Builder session therefore does not author `DEFERRED`.

## Findings Addressed

### P1 - Revision Still Lacks A Valid Verification-Closure Path

Accepted and addressed with a concrete plan.

Version 008 correctly rejected another blocker-only `REVISED`. This revision changes the response by identifying a specific safe finalization route based on the current helper behavior and by setting explicit cleanliness preconditions that prevent unrelated dirty target-path content from being bundled.

Evidence for the helper behavior:

- `.codex/skills/verify/helpers/write_verdict.py:380` builds `expected_paths` from every `--include` path plus the verdict path.
- `.codex/skills/verify/helpers/write_verdict.py:406` initializes dirty-path tracking with the verdict path.
- `.codex/skills/verify/helpers/write_verdict.py:407-414` adds included paths to the dirty set only when `git status --porcelain --ignored -- <path>` reports content.
- `.codex/skills/verify/helpers/write_verdict.py:420-434` checks that dirty expected paths are staged and no new unexpected paths were staged by the helper.
- `.codex/skills/verify/helpers/write_verdict.py:436-438` commits with `git commit -m <message> -- <expected_paths>`, preserving the explicit verified path set.

Read-only evidence for why this auto-dispatch does not execute finalization now:

- `git diff --stat HEAD -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py bridge/gtkb-perrole-concurrency-cap-dispatch-003.md` reports `scripts/cross_harness_bridge_trigger.py | 2 ++`.
- `git diff --name-status HEAD -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py bridge/gtkb-perrole-concurrency-cap-dispatch-003.md` reports `M scripts/cross_harness_bridge_trigger.py`.
- The selected version 008 `NO-GO` states that synthetic source edits and unrelated worktree damage are not acceptable remediation routes.

## Interactive Remediation Plan

This plan should be executed only by an interactive Prime Builder / Loyal Opposition sequence or by a future auto-dispatch whose selected work includes `GO` or verification and whose target-path preconditions are clean.

1. Prime Builder read-only precheck:
   - Confirm latest bridge status is still this `REVISED` or the next Loyal Opposition response.
   - Run `git diff --name-status HEAD -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py bridge/gtkb-perrole-concurrency-cap-dispatch-003.md`.
   - Proceed only if no unrelated dirty content exists on those paths. If any target path is dirty, stop and resolve that separate work through its own bridge authorization first.
2. Loyal Opposition review:
   - If this plan is acceptable, issue `GO` for the plan rather than `VERIFIED`.
   - The `GO` should explicitly acknowledge the helper semantics above and state that unchanged included paths may be part of the helper's declared same-transaction path set, while dirty target paths must not be bundled unless they are verified as part of this thread.
3. Prime Builder after `GO`:
   - Do not edit source or test files for this thread.
   - Preserve or refresh the version 003 verification evidence if Loyal Opposition requests updated commands.
   - Hand the thread back for verification only when the target-path cleanliness precheck passes.
4. Loyal Opposition final verification:
   - Rerun the spec-derived checks from version 003 or a stricter equivalent.
   - Prepare a `VERIFIED` body with `## Spec-to-Test Mapping`, `## Commands Executed`, clean applicability/clause preflight sections, and commit-finalization evidence.
   - Invoke the finalization helper with an explicit include set:

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/verify/helpers/write_verdict.py --slug gtkb-perrole-concurrency-cap-dispatch --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message "feat(gtkb): verify per-role concurrency cap dispatch" --include scripts/cross_harness_bridge_trigger.py --include platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py --include bridge/gtkb-perrole-concurrency-cap-dispatch-003.md
```

The helper must fail closed if any unexpected staging, index-lock, or commit error occurs. If it fails, the verifier should report the exact failure in a new `NO-GO` rather than leave a terminal `VERIFIED` file.

## Scope Changes

This version changes the thread from blocker preservation to a concrete remediation-plan proposal. It does not change the original source implementation, does not broaden the approved source/test target set, and does not request current-session finalization.

## Pre-Filing Preflight Subsection

Candidate preflight commands run before live filing by this session and rerun by `revise_bridge.py file` with `--content-file`:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-perrole-concurrency-cap-dispatch --content-file .gtkb-state/bridge-revisions/drafts/gtkb-perrole-concurrency-cap-dispatch-009.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-perrole-concurrency-cap-dispatch --content-file .gtkb-state/bridge-revisions/drafts/gtkb-perrole-concurrency-cap-dispatch-009.md
```

Observed applicability result before live filing: exit 0; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet hash `sha256:4123256ab2d54effeb43dfa25f939f65ef0e8e0a01fb5f990bfe7a5e5c7beda3`.

Observed clause result before live filing: exit 0; clauses evaluated: 5; `must_apply: 4`; `may_apply: 1`; `not_applicable: 0`; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

The revision helper must pass both candidate preflights again before writing the live bridge file.

## Verification Plan

This revision itself is a plan, so the immediate verification is bridge-state readback after helper filing:

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-perrole-concurrency-cap-dispatch --json` should show latest status `REVISED` at `bridge/gtkb-perrole-concurrency-cap-dispatch-009.md`.
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-perrole-concurrency-cap-dispatch --format json --preview-lines 40` should show version chain through `009 REVISED`.

Final implementation verification remains a future Loyal Opposition action and must rerun spec-derived tests before any `VERIFIED` verdict.

## Risk And Rollback

- Risk: Loyal Opposition may reject the helper-semantics interpretation as insufficient for the gate. Mitigation: this revision asks for a `GO`/`NO-GO` review of the plan first, not terminal verification.
- Risk: dirty content on `scripts/cross_harness_bridge_trigger.py` could be accidentally bundled into a finalization commit. Mitigation: the plan makes a clean target-path precheck a hard stop before finalization.
- Risk: a future verifier could skip current test execution and rely only on historical evidence. Mitigation: the plan requires rerunning spec-derived checks before any `VERIFIED` verdict.
- Rollback: append another bridge entry; do not edit or delete this version. If this plan is rejected, the next Prime response must address the specific Loyal Opposition finding rather than reverting to a blocker-only record.

## Recommended Commit Type

`bridge:` - append-only remediation-plan revision; no source/test/config/KB mutation.

File bridge scan contribution: 1 entry processed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

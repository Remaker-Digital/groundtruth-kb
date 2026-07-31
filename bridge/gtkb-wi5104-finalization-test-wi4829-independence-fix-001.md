NEW

# gtkb-wi5104-finalization-test-wi4829-independence-fix — Align stale finalization-evidence tests with the WI-4829 self-review gate (fixture-only)

bridge_kind: prime_proposal
Document: gtkb-wi5104-finalization-test-wi4829-independence-fix
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f2a9adc9-78e8-4333-9d55-70f0b30d0fba
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5104

target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Two tests in `platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py` — `test_verified_without_commit_finalization_evidence_is_blocked` and `test_verified_with_commit_finalization_evidence_is_allowed` — fail because they went stale relative to the **WI-4829** author-provenance / review-independence hard-block (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`). Each calls `_GATE._deny_reason_for_content(...)` with a standalone `VERIFIED` verdict body for `bridge/test-finalization-004.md` in an otherwise-empty `tmp_path`. The gate's `_verdict_self_review_deny` (added by WI-4829) runs first: `bridge_review_independence.reviewed_artifact_path` tries to resolve the *reviewed* artifact via the verdict's `Responds to:` line or the latest prior versioned file — but `_verified_body()` has no `Responds to:` line and `tmp_path` has no prior `test-finalization-003.md`, so resolution fails and the gate returns `author_session_context_missing` **before** reaching the `Commit Finalization Evidence` check the tests assert.

This is not a gate defect — the gate is behaving correctly; the tests predate WI-4829 and no longer set up a resolvable, independent review context. The fix is **fixture-only**: give the tests a resolvable reviewed report authored by a session distinct from the verdict's `verifier-session`, so the WI-4829 independence check passes and the gate proceeds to the finalization-evidence assertion under test. Concretely: (1) add a `Responds to: bridge/test-finalization-003.md` line to `_verified_body()`; and (2) in each affected test (or a shared fixture), write `tmp_path/bridge/test-finalization-003.md` (the reviewed report) carrying `author_session_context_id: prime-session` (distinct from `verifier-session`), passing the matching `bridge_id`/`project_root` so `reviewed_artifact_path` resolves it. No production code or gate logic changes.

Discovered during WI-5099 (the ruff re-cleanup touched this file); the failures were proven pre-existing there (HEAD failed identically) and out of that scope, and captured as WI-5104.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility: a small, low-risk, test-only fixture fix under the reliability fast-lane standing authorization by project membership.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the WI-4829 author-provenance / review-independence governance this fix aligns the stale tests with.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit trail / append-only numbered-file discipline.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specifications (this section).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / PAUTH / Work-Item linkage present in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derives from the requirement that the finalization-evidence tests collect and pass under the current gate (see plan below).
- `GOV-STANDING-BACKLOG-001` — WI-5104 tracked backlog authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — captured as a durable artifact (WI-5104) with a bridge audit trail.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserved as a governed artifact network (WI -> proposal -> verification).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the stale-test defect triggers the defect lifecycle: a work item (WI-5104, origin defect) plus this proposal.

## Prior Deliberations

- `bridge/gtkb-platform-tests-ruff-recleanup-003.md` — the WI-5099 implementation report where these 2 failures were characterized as pre-existing (identical on HEAD via git-stash comparison) and out of WI-5099 scope, motivating WI-5104.
- _No further prior deliberations: the WI-4829 gate ordering that made these tests stale is the root cause; there is no prior Deliberation Archive precedent proposing a fix for this specific test surface._

## Owner Decisions / Input

Implementation authority is provided by the reliability fast-lane standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`), covering WI-5104 by active project membership. In-session owner input (2026-07-09): the owner directed execution of the captured sweep WIs via `AskUserQuestion` ("Execute these" — WI-5101/5102/5103/5104). No new owner decision is required by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements already exist: the commit-finalization-evidence gate (the behavior the tests assert) and the WI-4829 review-independence requirement (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`). This proposal aligns stale test fixtures with the current, correct gate behavior; it does not change the gate and does not introduce a new or revised requirement.

## Spec-Derived Verification Plan

Verification derives from the linked requirement (the finalization-evidence tests collect and pass under the current gate) per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

1. After the fixture fix, the full module passes — the two previously-failing tests reach and satisfy the `Commit Finalization Evidence` assertions, and the already-passing `test_commit_finalization_evidence_requires_same_transaction_path_set` continues to pass:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py -q --no-header
```

Expected: all tests pass (previously 2 failed, 1 passed).

2. Regression guard: confirm the fix does not weaken the WI-4829 self-review protection — the independence check still fires (the fixture provides a *distinct* reviewer session, it does not bypass the check). Inspect that the reviewed-report fixture uses `author_session_context_id: prime-session` while the verdict uses `verifier-session`.

## Risk / Rollback

Risk is minimal and contained: a fixture-only change to a single test module — no production/source module, no gate logic, no governance rule, no bridge protocol, no KB mutation. The change makes stale tests exercise the gate through a realistic independent-review context rather than bypassing any check. Rollback is a single `git revert` of the implementing commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5104-finalization-test-wi4829-independence-fix`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` — the change is confined to a single test module's fixtures, aligning stale tests with the current WI-4829 gate. No production behavior changes.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

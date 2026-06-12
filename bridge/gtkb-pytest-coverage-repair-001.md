NEW

# gtkb-pytest-coverage-repair — Resolve failing pytest assertions and timeouts in the platform test suite

bridge_kind: prime_proposal
Document: gtkb-pytest-coverage-repair
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-11 UTC

author_identity: prime-builder
author_harness_id: C
author_session_context_id: d8339843-7272-4483-b647-3f99c011cc08
author_model: gemini-1.5-pro
author_model_version: 1.5-pro
author_model_configuration: interactive owner session, ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4475

target_paths: [".claude/settings.json", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_dispatch_author_meets_reviewer.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves all failing pytest assertions and timeouts in the GroundTruth-KB platform test suite. 

Specifically:
- Due to the Windows/Python 3.14 test environment, sequential spawning of git subprocesses (such as `git status` or `git remote`) in `scripts/session_self_initialization.py` during unit/integration tests was extremely slow, hitting the 30-second pytest timeout. We mock these out globally in `_load_module` to prevent this delay.
- The `scaffold_version` assertions in `test_groundtruth_governance_adoption.py` and `test_session_self_initialization.py` are updated from `"0.6.1"` to `"0.7.0rc1"` to match the current release-candidate version.
- Mocking of `shutil.which` in `test_verify_antigravity_dispatch.py` is made state-aware to isolate tests from the host environment.
- The hook ordering in `.claude/settings.json` is corrected so `workstream-focus.py` runs as the first hook under `UserPromptSubmit`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs filing this proposal on the bridge index.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Links this implementation to `GOV-SESSION-SELF-INITIALIZATION-001` and `GOV-08`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Enforces correct project/work-item metadata headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Specifies that testing must verify specification compliance.
- `GOV-STANDING-BACKLOG-001` — Governs tracking work under backlog WI-4475.

## Prior Deliberations

- `DELIB-FAB21-REMEDIATION-20260610` — Project context on reducing startup payload size and local execution cost.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Core principles on mock isolation of external/git services during testing.

## Owner Decisions / Input

- Authorized by the owner's choice via AskUserQuestion in S432: *"File a new bridge proposal for these pytest fixes first to follow the governance protocol."* (DELIB id associated with current turn's decision).

## Requirement Sufficiency

- Existing requirements sufficient — `GOV-SESSION-SELF-INITIALIZATION-001` and `GOV-08` cover the self-initialization and database requirements.

## Spec-Derived Verification Plan

Run the targeted pytest test files using the repo virtual environment interpreter:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q
python -m pytest platform_tests/scripts/test_dispatch_author_meets_reviewer.py -q
python -m pytest platform_tests/scripts/test_groundtruth_governance_adoption.py -q
python -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -q
```

Expected result: All tests pass successfully without timeouts (e.g. `test_session_self_initialization.py` passes all 66 tests in < 51 seconds).

## Risk / Rollback

- **Risk:** Mocks might mask actual git integration failures.
- **Mitigation:** The mocks are strictly scoped to the unit/integration tests of the startup disclosure model generator, which does not require live git access.
- **Rollback:** Revert this commit using `git revert` or checkout prior file states.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-pytest-coverage-repair` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

- `test` — Scoped entirely to test files, mocks, and hook configuration order.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4524-test-session-id-leak-hardening
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4524
target_paths: ["groundtruth-kb/tests/test_bridge_propose_helper.py"]
implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: test:

# WI-4524: Harden bridge-propose helper tests against live-session CLAUDE_CODE_SESSION_ID leak

## Summary

WI-4524 (P3, `bridge_dispatch`, origin=defect): `groundtruth-kb/tests/test_bridge_propose_helper.py::test_template_propose_bridge_acquires_and_releases_work_intent` (and likely siblings) monkeypatches `CLAUDE_SESSION_ID` to inject a fixture session id — but does NOT delenv the higher-precedence `CLAUDE_CODE_SESSION_ID`. When pytest runs INSIDE a live Claude Code session, `helper.resolve_work_intent_session_id` picks up the real harness session id and beats the injected value, producing a false-positive FAIL. S438 evidence: the real id `869ade5b` beat `template-session`. The test passes in CI / clean environments — so the underlying behavior is correct; only the test's environment isolation is incomplete.

**Cycle-11 triage (this session) confirms WI-4524 is genuinely OPEN.** Live read of `groundtruth-kb/tests/test_bridge_propose_helper.py`:

- Line 680: `monkeypatch.setenv("CLAUDE_SESSION_ID", "template-session")` — sets a LOWER-precedence var.
- Line 693: assertion expects recorded `session_id == "template-session"`.
- Lines 623-648: a sibling fixture already correctly delenvs `GTKB_BRIDGE_POLLER_RUN_ID`, `CLAUDE_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `ANTIGRAVITY_SESSION_ID` — but **NOT** `CLAUDE_CODE_SESSION_ID`. Neither does the test at 655.
- Line 32: another test correctly delenvs `CODEX_THREAD_ID`. The pattern is "delenv-then-setenv" but it's applied inconsistently.

So the fix is purely test-environment hygiene: ensure that every test that depends on a controlled `session_id` first removes ALL real session-id env vars — most importantly `CLAUDE_CODE_SESSION_ID` (the one beating the fixture). Test-only scope, zero production-code change.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4524 is the backlog authority for this fix (P3 test-reliability defect). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one test file hardened, one new shared delenv helper, no source-code change), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4524; allows `source` + `test_addition`). This slice is test-only.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger). It hardens a test of bridge-propose-helper behavior; it does NOT modify `bridge/INDEX.md`, bridge workflow state, or any helper code.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a "test passes under simulated live-session env" guard.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — the `target_paths` entry is in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked test-environment hardening with explicit guard coverage.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4524 + the S438 repro: real id `869ade5b` beat `template-session`), cycle-11 triage confirmed the live test still has the gap, the bounded PAUTH authorizes the `source` + `test_addition` work (this slice uses only `test_addition`), and `resolve_work_intent_session_id`'s precedence order defines the env vars that must be isolated. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4524 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **Sibling fixture at `groundtruth-kb/tests/test_bridge_propose_helper.py:623-648`** — the existing correct delenv pattern this fix extends to cover `CLAUDE_CODE_SESSION_ID` AND applies consistently across all affected tests. This makes the slice diff-minimal and self-evidently correct.
- **`scripts/bridge_session_id.resolve_work_intent_session_id` precedence order** — the authority that defines which env vars beat which; the fix delenvs the full set so the fixture's `setenv` is the unambiguous winner.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live test source instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4524 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`). This slice is test-only and stays within `test_addition`. No source-code change, no formal-artifact mutation, no KB mutation.

## Design

Single file edit in `groundtruth-kb/tests/test_bridge_propose_helper.py`:

1. **Add a small module-level helper** `_delenv_all_real_session_id_vars(monkeypatch)` that calls `monkeypatch.delenv(name, raising=False)` for each of the six precedence-bearing vars: `CLAUDE_CODE_SESSION_ID`, `GTKB_BRIDGE_POLLER_RUN_ID`, `CLAUDE_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `ANTIGRAVITY_SESSION_ID`. (`raising=False` so it works whether or not the var is present.)
2. **Call the helper at the top of `test_template_propose_bridge_acquires_and_releases_work_intent` (`:655`)** before the existing `monkeypatch.setenv("CLAUDE_SESSION_ID", "template-session")` (`:680`) — this makes the fixture's `setenv` the unambiguous winner, regardless of the live host env.
3. **Audit and apply consistently:** scan the file for other tests that `monkeypatch.setenv` a session-id-precedence var (`CLAUDE_SESSION_ID`, `CODEX_THREAD_ID`, etc.) and call `_delenv_all_real_session_id_vars(monkeypatch)` at the top of each. The existing fixture at 623-648 that already delenvs the bulk of the set may be refactored to call the new helper (with `CLAUDE_CODE_SESSION_ID` added) so there is ONE source of truth for the precedence-bearing var list.
4. **Comment** the helper with a one-line pointer to `resolve_work_intent_session_id`'s precedence order, so a future test author knows why these specific vars are isolated.

No change to helper source code, no change to test assertion behavior on a clean env, no change to the precedence order. The fix makes the test environment-stable: it now passes under a live Claude Code session AND under CI/clean env.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test verification | Method |
|---|---|---|
| `test_template_propose_bridge_acquires_and_releases_work_intent` passes under simulated live-session env (WI-4524 root) | run pytest with `CLAUDE_CODE_SESSION_ID=fake-live-session` set in the parent env → test PASSES | invoke `python -m pytest groundtruth-kb/tests/test_bridge_propose_helper.py::test_template_propose_bridge_acquires_and_releases_work_intent` after `os.environ['CLAUDE_CODE_SESSION_ID']='real-live-session'`; assert exit 0 |
| Test still passes on a clean env (no regression) | run pytest with all session-id vars unset → test PASSES | invoke the same test after `delenv` of all six vars; assert exit 0 |
| Other affected tests also harden against the live-session leak | grep verification + targeted re-runs | confirm every test that `setenv`s a session-id-precedence var calls `_delenv_all_real_session_id_vars` first; re-run each under the simulated-live-session env |
| Helper is module-local and only used by the test file | static check | confirm `_delenv_all_real_session_id_vars` is defined once at module scope and is not exported as part of any public API |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on the changed test file; `python -m pytest groundtruth-kb/tests/test_bridge_propose_helper.py -q --tb=short` (full file pass), then the simulated-live-session env runs above.

## Risk / Rollback

- **Risk: very low.** Test-only change in one file. `monkeypatch.delenv(..., raising=False)` is the idiomatic pytest pattern and cannot affect production code, schemas, or other tests. The fix REDUCES test flakiness; it does not change any helper behavior. CI/clean-env behavior is provably preserved by re-running the full test file.
- **Caller compatibility:** zero — no public API, no helper code change, no fixture renaming. The helper name `_delenv_all_real_session_id_vars` is underscore-prefixed and module-local.
- **Rollback:** delete the helper + revert the `_delenv_all_real_session_id_vars(monkeypatch)` calls in each affected test. No migration, no schema, no production code.

## Recommended Commit Type

`test:` — test-only change (test-environment hardening to prevent false-positive FAILs under a live host session); no source-code change, no new capability surface. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

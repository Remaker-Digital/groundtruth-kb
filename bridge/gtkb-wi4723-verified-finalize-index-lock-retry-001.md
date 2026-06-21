NEW

# Retry-with-backoff on git index-lock contention in the VERIFIED commit-finalization gate (WI-4723)

bridge_kind: implementation_proposal
Document: gtkb-wi4723-verified-finalize-index-lock-retry
Version: 001 (NEW)
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4723

target_paths: [".claude/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

The Mandatory VERIFIED Commit-Finalization Gate (`.claude/rules/file-bridge-protocol.md`, "Mandatory VERIFIED Commit-Finalization Gate") requires Loyal Opposition to write the next numbered VERIFIED verdict and create the git commit containing the verified implementation/report paths plus that verdict in one local helper transaction (`finalize_verified_commit` in `.claude/skills/verify/helpers/write_verdict.py`). Two distinct failure modes have repeatedly deadlocked that transaction across the multi-session swarm under Google Drive sync (owner decision DELIB-20265511 captured both and filed WI-4723):

- **Failure mode A — transient `.git/index.lock` contention (IN SCOPE for this fix).** Concurrent commits across sessions, amplified by Drive syncing `E:\GT-KB\.git`, collide on the git index lock. `_run_git(["add","-f","--",*expected_paths], ..., check=True)` (write_verdict.py line 307) fails with `fatal: Unable to create 'E:/GT-KB/.git/index.lock': Permission denied`. Because `_run_git(..., check=True)` raises `VerifiedFinalizationError` on the first non-zero exit, a momentary lock held by another git process (or a transient file handle) aborts the whole finalization and triggers `_cleanup_failed_verdict` (line 322), even though a retry milliseconds later would succeed. Evidence: WI-4565 finalization NO-GO'd twice on this exact blocker (`bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-006.md` / `-008`); the index-lock finalization-blocker class is corroborated by DELIB-20265485 (WI-4682 "finalization still blocked by git index creation") and DELIB-20265407 (WI-4678 git-write finalization blocker report).

- **Failure mode B — verified paths already committed by an owner sweep (EXPLICITLY DEFERRED; see Proposed Change).** When an owner sweep commit (e.g. `32d7d61ce`) commits the implementation/report paths *before* verification, `git add` stages nothing new, so the staged-set equality check at write_verdict.py line 309 (`set(staged_after) != set(expected_paths)`) fails with a "staged-set mismatch" and the finalization aborts. Evidence: CA9165 `-004` ("the implementation/report paths ... were already committed in `32d7d61ce`").

The Drive-exclusion half of WI-4723's title is already DONE and is NOT proposed here: `.git/` is already listed in `.driveignore` (under the "Git internal directory (NEVER cloud-sync a .git/)" section). This proposal therefore makes NO `.driveignore` change. The residual amplifier is the lock-contention race itself, which this proposal absorbs with a bounded retry.

## Proposed Change

Primary, in-scope fix: add a bounded retry-with-exponential-backoff around the two git mutation call sites inside `finalize_verified_commit`, scoped to transient index-lock failures only.

1. **New helper `_run_git_with_lock_retry`** in `write_verdict.py` (placed immediately after `_run_git`, ~line 212):

   ```python
   _INDEX_LOCK_SIGNATURES = (
       "index.lock",
       "unable to create",
       "permission denied",
       "another git process",
   )

   def _is_index_lock_failure(result: subprocess.CompletedProcess[str]) -> bool:
       blob = f"{result.stderr or ''}\n{result.stdout or ''}".lower()
       return "index.lock" in blob or (
           "another git process" in blob
           and any(sig in blob for sig in _INDEX_LOCK_SIGNATURES)
       )

   def _run_git_with_lock_retry(
       args: list[str],
       *,
       cwd: Path,
       attempts: int | None = None,
       base_delay: float | None = None,
   ) -> subprocess.CompletedProcess[str]:
       attempts = attempts if attempts is not None else _env_int(
           "GTKB_VERIFIED_COMMIT_LOCK_RETRIES", 5)
       base_delay = base_delay if base_delay is not None else _env_float(
           "GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY", 0.5)
       last: subprocess.CompletedProcess[str] | None = None
       for attempt in range(attempts):
           result = _run_git(args, cwd=cwd, check=False)
           if result.returncode == 0:
               return result
           last = result
           if not _is_index_lock_failure(result):
               break  # non-lock failure: fail fast, do not retry
           if attempt < attempts - 1:
               time.sleep(base_delay * (2 ** attempt))
       raise VerifiedFinalizationError(
           f"git {' '.join(args)} failed with exit {last.returncode if last else -1}: "
           f"{((last.stderr if last else '') or (last.stdout if last else '')).strip()}"
       )
   ```

   `_env_int` / `_env_float` are small `os.environ.get` parsers that fall back to the default on absent/invalid values. Retries use ordinary blocking `time.sleep` (add `import time`, `import os` if not present); there is no event-loop concern.

2. **Wrap both git mutation call sites.** Replace the `git add` call at line 307 and the `git commit` call at line 316 with `_run_git_with_lock_retry(...)`. The intervening staged-set equality check (line 309) and the existing `_cleanup_failed_verdict` on any exception (line 322) are preserved exactly. The `git commit` site keeps its existing explicit non-zero-exit branch only for non-lock commit failures (the retry helper now raises directly on lock-class commit failure), so the surrounding `try/except Exception` cleanup contract is unchanged.

3. **Tunability.** `GTKB_VERIFIED_COMMIT_LOCK_RETRIES` (default 5) and `GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY` (default 0.5s) make attempts and backoff env-tunable for slower Drive-sync environments without code change. Worst-case added latency at defaults is ~0.5+1+2+4 = 7.5s before exhausting to `VerifiedFinalizationError`.

This retry does NOT change the gate's atomic-commit invariant. Per the governing text, a VERIFIED verdict still results in exactly one local commit containing the verified paths plus the new verdict artifact; the retry only re-attempts the *same* git operation when it fails on a transient index lock, and still fails closed (removing the just-written verdict via `_cleanup_failed_verdict`) when the lock never clears. The staged-set equality check, the clean-staging precondition (line 281), and the cleanup-on-failure behavior are all untouched.

**Explicitly DEFERRED — failure mode B (already-committed-path accommodation).** Teaching the gate to treat "all expected paths are already committed at HEAD" as success would relax the staged-set equality invariant at line 309 and thereby change the Commit-Finalization Gate's contract ("the same local transaction creates the git commit that contains the verified implementation/report paths and the new VERIFIED verdict artifact"). That is a protected-narrative / governance change to `.claude/rules/file-bridge-protocol.md` and the gate's atomic-commit invariant, which requires a separate owner-approved governance packet and its own bridge thread. It is deliberately NOT bundled here. This proposal fixes the transient mechanical race (A) only; (B) is tracked as a follow-up.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs this bridge filing and the numbered-file chain.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4723 is a fast-lane-eligible defect fix (origin defect; no new API/CLI/behavior beyond removing the lock-race defect; no new or revised requirement; single-concern, ~1 source file + 1 test), created under PROJECT-GTKB-RELIABILITY-FIXES and covered by the standing project authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - the retry gates an expensive action (an aborted finalization forces a full re-review / re-dispatch cycle) behind a cheap deterministic index-lock-signature check plus bounded backoff, instead of failing the whole transaction on a millisecond-scale lock.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` - WI-4723 is the governed backlog candidate for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both changed files are under `E:\GT-KB` (`.claude/skills/verify/helpers/` and `platform_tests/scripts/`); no application-tree or out-of-root path is touched.

## Owner Decisions / Input

- Owner directive (2026-06-21): "proceed with WI-4723." This authorizes implementation of the in-scope retry fix and is captured durably as DELIB-WI4723-OWNER-PROCEED-20260621 (outcome owner_decision). It follows the owner's pragmatic-retirement decision (DELIB-20265511, AUQ-2026-06-21-bridge-protocol-reliability-pragmatic-retirement) which accepted the four GTKB-BRIDGE-PROTOCOL-RELIABILITY implementations as completed-pragmatic and filed WI-4723 to fix the finalization-environment deadlock so future VERIFIED ceremonies are not blocked.
- The already-committed-path accommodation (failure mode B) and the corresponding atomic-commit invariant change are DEFERRED for a separate owner-approved governance packet; this proposal does not seek owner approval for any invariant change.

## Prior Deliberations

- `DELIB-20265511` - owner pragmatic-completion + retirement decision for PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY; the decision record that names both failure modes (pre-committed sweep paths + `.git/index.lock` contention under Drive sync) and filed WI-4723 as the finalization-environment follow-up.
- `DELIB-WI4723-OWNER-PROCEED-20260621` - owner directive authorizing this implementation.
- `DELIB-20265485` - LO verification, WI-4682 "finalization still blocked by git index creation" (NO-GO) - prior live occurrence of failure mode A.
- `DELIB-20265407` - LO review, WI-4678 git-write finalization blocker report (VERIFIED) - finalization-blocker class precedent.
- `DELIB-20265494` / `DELIB-20265495` - LO NO-GO verdicts, WI-4700 narrative approval packet scope - confirm that invariant/protected-narrative changes are handled as a separate scoped packet (supports deferring failure mode B).
- Deliberation search `gt deliberations search "VERIFIED commit finalization git index.lock retry contention"` (2026-06-21) returned DELIB-20265494, DELIB-20265485, DELIB-20265407, DELIB-20265465, DELIB-20265495; none records a previously-rejected retry-with-backoff approach, so this proposal does not revisit a rejected decision.

## Requirement Sufficiency

Existing requirements sufficient. The governing invariant (`.claude/rules/file-bridge-protocol.md` "Mandatory VERIFIED Commit-Finalization Gate") is unchanged by this fix; the retry only makes the existing single-commit transaction resilient to transient index-lock contention. No new or revised requirement is required before implementation. (Per `GOV-RELIABILITY-FAST-LANE-001` criterion 3, requiring no new requirement is also a fast-lane eligibility condition.)

## Specification-Derived Verification Plan

New tests live in the existing helper test module `platform_tests/scripts/test_lo_verified_commit_atomicity.py` (which already exercises `finalize_verified_commit` via the `verify_helper` fixture and monkeypatches `_run_git`). Spec-to-test mapping:

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` / Commit-Finalization Gate - transient index-lock on `git add` is retried, not fatal | `test_verified_finalization_retries_transient_index_lock_on_add`: monkeypatch `_run_git` to return a simulated `index.lock` "Permission denied" `CompletedProcess(returncode=1)` on the FIRST `add` call, then delegate to the real `_run_git`; patch `time.sleep` to a no-op | finalization succeeds; commit contains the verified path set + verdict; staging area clean |
| Fail-fast on non-lock failure (retry must NOT mask genuine errors) | `test_verified_finalization_does_not_retry_non_lock_git_failure`: monkeypatch `_run_git` so the FIRST `add` returns `returncode=1` with stderr `pathspec error` (no lock signature); count invocations | raises `VerifiedFinalizationError`; the `add` is attempted exactly once (no retry); verdict file removed; staging clean |
| Retries are bounded and exhaust to error | `test_verified_finalization_exhausts_lock_retries`: monkeypatch `_run_git` so every `add` returns the `index.lock` failure; set `GTKB_VERIFIED_COMMIT_LOCK_RETRIES=3`, patch `time.sleep`; count invocations | raises `VerifiedFinalizationError` matching `index.lock`; exactly 3 `add` attempts; the new verdict file does not exist; staging clean |
| Backoff uses bounded sleep, not busy-loop | assert `time.sleep` called with increasing delays (`base_delay * 2**n`) and total attempts == configured bound | sleep called (attempts-1) times with monotonically increasing args |
| Existing atomic-commit invariant preserved (regression) | existing atomicity tests in the module (commit-together, commit-failure-removes-verdict-and-unstages, unrelated-staged-path-fails) | unchanged PASS |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py
```

Note: `.codex/skills/verify/helpers/write_verdict.py` is the harness-parity twin of the edited file. Keeping the two byte-aligned is a harness-parity concern; if parity is enforced for this helper, the same edit must be mirrored there. This is flagged for the reviewer; it is NOT added to `target_paths` for this fix to keep the change single-concern, and is the one open scoping question for Loyal Opposition to rule on (mirror here vs. a parity follow-up).

## Risk And Rollback

- Risk: the retry masks a persistent (non-transient) lock, delaying the failure. Mitigation: attempts are bounded (default 5, ~7.5s worst case) and the helper still fails closed via `_cleanup_failed_verdict`; a persistent lock surfaces the same `VerifiedFinalizationError` it does today, only later.
- Risk: the lock-signature match is too broad and retries a real error. Mitigation: the signature requires the literal `index.lock` token (or `another git process` plus a corroborating token); a plain pathspec/commit error contains none of these and fails fast (covered by the non-lock test).
- Risk: harness-parity drift between `.claude` and `.codex` helper copies. Mitigation: flagged above for the reviewer; mirror the edit if parity is enforced.
- Rollback: revert the single source commit; the added tests are additive. No state schema change, no `.driveignore` change, no governance/rule change, no change to the atomic-commit invariant.

## Acceptance Criteria

- [ ] `finalize_verified_commit` retries a transient `.git/index.lock` failure on `git add` and on `git commit` with bounded exponential backoff and then succeeds when the lock clears.
- [ ] A non-lock git failure is NOT retried and fails fast with `VerifiedFinalizationError`.
- [ ] Retries are bounded by `GTKB_VERIFIED_COMMIT_LOCK_RETRIES` (default 5) and exhaust to `VerifiedFinalizationError`; backoff is `GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY`-tunable.
- [ ] The atomic-commit invariant is unchanged: still one local commit of the verified path set plus the verdict; clean-staging precondition and `_cleanup_failed_verdict` fail-closed behavior preserved; the already-committed-path accommodation is NOT implemented (deferred).
- [ ] No `.driveignore` change is made.
- [ ] New tests pass; existing atomicity regression tests pass; `ruff check` and `ruff format --check` are clean on both changed files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

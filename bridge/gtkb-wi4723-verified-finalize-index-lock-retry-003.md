REVISED

# Retry-with-backoff on git index-lock contention in the VERIFIED commit-finalization gate (WI-4723) — REVISED for the Codex helper twin

bridge_kind: implementation_proposal
Document: gtkb-wi4723-verified-finalize-index-lock-retry
Version: 003 (REVISED)
Recommended commit type: fix:
Responds to: bridge/gtkb-wi4723-verified-finalize-index-lock-retry-002.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4723

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Summary

This REVISED version resolves the Loyal Opposition NO-GO at version 002, which had one blocker (P1) and one minor finding (P3):

- P1 (blocker): the version-001 `target_paths` fixed only `.claude/skills/verify/helpers/write_verdict.py`, but `.codex/skills/verify/helpers/write_verdict.py` is the byte-identical runtime helper that Codex's own LO verify/bridge skills invoke for VERIFIED finalization. A `.claude`-only fix would leave the actual Codex finalization path on the un-retried behavior WI-4723 must repair.
- P3 (minor): the applicability preflight reported three un-cited advisory specs.

This version adds the `.codex` twin to scope (with its provenance determined and stated), applies the identical retry to both helper copies, adds a byte-parity test, and cites the advisory specs. See `## Findings Addressed`.

## Problem / Diagnosis

The Mandatory VERIFIED Commit-Finalization Gate (`.claude/rules/file-bridge-protocol.md`, "Mandatory VERIFIED Commit-Finalization Gate") requires Loyal Opposition to write the next numbered VERIFIED verdict and create the git commit containing the verified implementation/report paths plus that verdict in one local helper transaction (`finalize_verified_commit` in `.claude/skills/verify/helpers/write_verdict.py`, byte-mirrored to `.codex/skills/verify/helpers/write_verdict.py`). Two distinct failure modes have repeatedly deadlocked that transaction across the multi-session swarm under Google Drive sync (owner decision DELIB-20265511 captured both and filed WI-4723):

- **Failure mode A — transient `.git/index.lock` contention (IN SCOPE for this fix).** Concurrent commits across sessions, amplified by Drive syncing `E:\GT-KB\.git`, collide on the git index lock. `_run_git(["add","-f","--",*expected_paths], ..., check=True)` (write_verdict.py line 307) fails with `fatal: Unable to create 'E:/GT-KB/.git/index.lock': Permission denied`. Because `_run_git(..., check=True)` raises `VerifiedFinalizationError` on the first non-zero exit, a momentary lock held by another git process (or a transient file handle) aborts the whole finalization and triggers `_cleanup_failed_verdict` (line 322), even though a retry milliseconds later would succeed. Evidence: WI-4565 finalization NO-GO'd twice on this exact blocker (`bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-006.md` / `-008`); corroborated by DELIB-20265485 (WI-4682 "finalization still blocked by git index creation") and DELIB-20265407 (WI-4678 git-write finalization blocker report). The same un-retried mutation sites (lines 307 / 316) exist in the Codex twin, so Codex-side LO finalization is exposed to the identical abort.

- **Failure mode B — verified paths already committed by an owner sweep (EXPLICITLY DEFERRED; see Proposed Change).** When an owner sweep commit (e.g. `32d7d61ce`) commits the implementation/report paths *before* verification, `git add` stages nothing new, so the staged-set equality check at write_verdict.py line 309 (`set(staged_after) != set(expected_paths)`) fails with a "staged-set mismatch" and the finalization aborts. Evidence: CA9165 `-004`.

The Drive-exclusion half of WI-4723's title is already DONE and is NOT proposed here: `.git/` is already listed in `.driveignore` (under the "Git internal directory (NEVER cloud-sync a .git/)" section). This proposal makes NO `.driveignore` change. The residual amplifier is the lock-contention race itself, which this proposal absorbs with a bounded retry on both runtime helper copies.

## Proposed Change

Primary, in-scope fix: add a bounded retry-with-exponential-backoff around the two git mutation call sites inside `finalize_verified_commit`, scoped to transient index-lock failures only, applied identically to both runtime helper copies.

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

2. **Wrap both git mutation call sites.** Replace the `git add` call at line 307 and the `git commit` call at line 316 with `_run_git_with_lock_retry(...)`. The intervening staged-set equality check (line 309) and the existing `_cleanup_failed_verdict` on any exception (line 322) are preserved exactly. The `git commit` site keeps its existing explicit non-zero-exit branch only for non-lock commit failures, so the surrounding `try/except Exception` cleanup contract is unchanged.

3. **Tunability.** `GTKB_VERIFIED_COMMIT_LOCK_RETRIES` (default 5) and `GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY` (default 0.5s) make attempts and backoff env-tunable. Worst-case added latency at defaults is ~0.5+1+2+4 = 7.5s before exhausting to `VerifiedFinalizationError`.

4. **Apply the identical edit to the Codex runtime helper twin (resolves P1).** `.codex/skills/verify/helpers/write_verdict.py` is a **generated byte-mirror** of the canonical `.claude/skills/verify/helpers/write_verdict.py`: the adapter generator's `_sync_resource_mirror` (`scripts/generate_codex_skill_adapters.py`; `RESOURCE_DIRECTORY_NAMES = ("references", "helpers")`, line 24) copies every helper file via `_write_bytes_if_changed` in **byte mode** (`source_file.read_bytes()`, ~line 402). Codex's own LO finalization path invokes this twin (`.codex/skills/verify/SKILL.md` lines 95-110; `.codex/skills/bridge/SKILL.md` line 138), so the fix must reach it. The implementation applies the **identical** retry edit to both helper copies, keeping them byte-identical. Two consequences make this clean and single-concern:
   - **CRLF-safe.** The helper is mirrored in BYTE mode, not the text-write path (`_write_if_changed` / `update_registry`) where WI-4701's CRLF defect lives. So the twin carries no CRLF risk, and no regeneration step is required — the implementation edits both copies directly with an LF-writing editor.
   - **No MANIFEST/registry scope.** Helper byte-mirrors are NOT hash-tracked in `.codex/skills/MANIFEST.json` (only SKILL.md adapters carry `source_sha256`). Editing the helper touches neither MANIFEST nor `harness-capability-registry.toml`. A subsequent generator run is idempotent on byte-identical helpers (no drift), so hand-applying the identical edit is equivalent to regenerating without invoking the (still-unlanded-WI-4701) text-write path.

This retry does NOT change the gate's atomic-commit invariant. A VERIFIED verdict still results in exactly one local commit containing the verified paths plus the new verdict artifact; the retry only re-attempts the *same* git operation on a transient index lock, and still fails closed when the lock never clears. The staged-set equality check, the clean-staging precondition (line 281), and the cleanup-on-failure behavior are untouched.

**Explicitly DEFERRED — failure mode B (already-committed-path accommodation).** Teaching the gate to treat "all expected paths are already committed at HEAD" as success would relax the staged-set equality invariant at line 309 and change the Commit-Finalization Gate's contract — a protected-narrative / governance change to `.claude/rules/file-bridge-protocol.md` requiring a separate owner-approved governance packet and its own bridge thread. It is deliberately NOT bundled here.

## Findings Addressed (Loyal Opposition NO-GO at version 002)

### P1 — The proposal leaves Codex's runtime finalization helper unfixed
Response: Resolved. `target_paths` now includes `.codex/skills/verify/helpers/write_verdict.py`. The twin's provenance is determined and stated (Proposed Change step 4): it is a generated byte-mirror per `_sync_resource_mirror`. The implementation applies the identical retry to both copies, keeping them byte-identical; verification adds a byte-parity assertion and runs the retry behavior + ruff against both helper paths. Because the mirror is byte-mode (CRLF-safe) and not MANIFEST-tracked, no regeneration / SKILL.md / MANIFEST / registry rewrite is triggered and the change stays source/test single-concern.

### P3 — Advisory preflight omissions
Response: The three applicability-triggered advisory specs are now cited in Specification Links — the artifact-oriented governing-record set named together in `.claude/rules/codex-standing-priorities.md` (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) — clearing the `missing_advisory_specs` list on the next preflight.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs this bridge filing and the numbered-file chain.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4723 is a fast-lane-eligible defect fix (origin defect; no new requirement; single-concern, two byte-identical helper copies + one test) under PROJECT-GTKB-RELIABILITY-FIXES, covered by the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - the retry gates an expensive action (an aborted finalization forces a full re-review / re-dispatch cycle) behind a cheap deterministic index-lock-signature check plus bounded backoff.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + authorization metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` - WI-4723 is the governed backlog candidate for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all three changed files are under `E:\GT-KB` (`.claude/skills/verify/helpers/`, `.codex/skills/verify/helpers/`, `platform_tests/scripts/`); no application-tree or out-of-root path is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - the durable helper artifacts and their generated twin remain consistent and traceable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - the change is represented through the work item, owner-decision deliberation, bridge chain, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the deferred failure-mode-B accommodation is preserved as an explicit deferred lifecycle state.

## Owner Decisions / Input

- Owner directive (2026-06-21): "proceed with WI-4723." Captured durably as `DELIB-WI4723-OWNER-PROCEED-20260621` (outcome owner_decision). It follows the pragmatic-retirement decision `DELIB-20265511`. The owner authorization remains sufficient for the retry-with-backoff source/test fix across both helper copies (Loyal Opposition `-002` Prime Builder Revision Context confirms this); the already-committed-path invariant accommodation remains out of scope and is not sought here.

## Prior Deliberations

- `DELIB-20265511` - owner pragmatic-completion + retirement decision; names both failure modes and filed WI-4723.
- `DELIB-WI4723-OWNER-PROCEED-20260621` - owner directive authorizing this implementation.
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-002.md` - the Loyal Opposition NO-GO this revision answers (P1 = Codex helper twin; P3 = advisory specs).
- `DELIB-20265485` - LO verification, WI-4682 finalization blocked by git index creation (prior live occurrence of failure mode A).
- `DELIB-20265407` - LO review, WI-4678 git-write finalization blocker report (finalization-blocker class precedent).
- `DELIB-20265494` / `DELIB-20265495` - WI-4700 narrative-approval-packet scope verdicts; confirm invariant/protected-narrative changes are handled as a separate scoped packet (supports deferring failure mode B).

## Requirement Sufficiency

Existing requirements sufficient. The governing invariant is unchanged; the retry only makes the existing single-commit transaction resilient to transient index-lock contention, applied to both runtime helper copies. No new or revised requirement is required before implementation.

## Specification-Derived Verification Plan

New tests live in the existing helper test module `platform_tests/scripts/test_lo_verified_commit_atomicity.py` (which already exercises `finalize_verified_commit` via the `verify_helper` fixture and monkeypatches `_run_git`). Spec-to-test mapping:

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` - transient index-lock on `git add` is retried, not fatal | `test_verified_finalization_retries_transient_index_lock_on_add`: monkeypatch `_run_git` to return a simulated `index.lock` "Permission denied" `CompletedProcess(returncode=1)` on the FIRST `add`, then delegate to the real `_run_git`; patch `time.sleep` | finalization succeeds; commit contains the verified path set + verdict; staging clean |
| Fail-fast on non-lock failure | `test_verified_finalization_does_not_retry_non_lock_git_failure`: FIRST `add` returns `returncode=1` with stderr `pathspec error` (no lock signature) | raises `VerifiedFinalizationError`; `add` attempted exactly once; verdict removed; staging clean |
| Retries are bounded and exhaust to error | `test_verified_finalization_exhausts_lock_retries`: every `add` returns the `index.lock` failure; `GTKB_VERIFIED_COMMIT_LOCK_RETRIES=3`, patch `time.sleep` | raises `VerifiedFinalizationError` matching `index.lock`; exactly 3 `add` attempts; verdict absent; staging clean |
| Backoff uses bounded sleep | assert `time.sleep` called with increasing delays (`base_delay * 2**n`), (attempts-1) times | monotonically increasing args |
| **Harness parity (resolves P1): the Codex twin receives the identical retry** | `test_verify_helper_codex_twin_matches_claude_and_has_retry`: assert `.codex/skills/verify/helpers/write_verdict.py` is byte-identical to `.claude/skills/verify/helpers/write_verdict.py` AND both contain `def _run_git_with_lock_retry` | both helpers byte-identical; retry helper present in both copies |
| Existing atomic-commit invariant preserved (regression) | existing atomicity tests (commit-together, commit-failure-removes-verdict-and-unstages, unrelated-staged-path-fails) | unchanged PASS |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py
```

## Risk And Rollback

- Risk: the retry masks a persistent (non-transient) lock, delaying the failure. Mitigation: attempts are bounded (default 5, ~7.5s worst case) and the helper still fails closed via `_cleanup_failed_verdict`.
- Risk: the lock-signature match is too broad. Mitigation: the signature requires the literal `index.lock` token (or `another git process` plus a corroborating token); a plain pathspec/commit error fails fast (covered by the non-lock test).
- Risk: harness-parity drift between the `.claude` and `.codex` helper copies. Mitigation: both are edited byte-identically in the same commit and the new parity test asserts byte-identity; the generator's byte-mode mirror is idempotent on the result.
- Rollback: revert the single commit (both helpers + test); the added tests are additive. No state-schema change, no `.driveignore` change, no MANIFEST/registry change, no governance/rule change, no change to the atomic-commit invariant.

## Acceptance Criteria

- [ ] `finalize_verified_commit` retries a transient `.git/index.lock` failure on `git add` and `git commit` with bounded exponential backoff, then succeeds when the lock clears.
- [ ] A non-lock git failure is NOT retried and fails fast with `VerifiedFinalizationError`.
- [ ] Retries are bounded by `GTKB_VERIFIED_COMMIT_LOCK_RETRIES` (default 5) and exhaust to `VerifiedFinalizationError`; backoff is `GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY`-tunable.
- [ ] Both `.claude/skills/verify/helpers/write_verdict.py` and `.codex/skills/verify/helpers/write_verdict.py` receive the identical retry and remain byte-identical (asserted by the parity test).
- [ ] The atomic-commit invariant is unchanged; clean-staging precondition and `_cleanup_failed_verdict` fail-closed behavior preserved; failure-mode-B accommodation NOT implemented (deferred).
- [ ] No `.driveignore`, MANIFEST, or registry change is made.
- [ ] New tests pass; existing atomicity regression tests pass; `ruff check` and `ruff format --check` clean on both helpers + the test.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

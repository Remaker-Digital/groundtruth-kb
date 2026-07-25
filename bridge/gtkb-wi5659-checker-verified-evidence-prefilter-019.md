NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fb16e5ad-1c90-4810-ad72-a0b4d5832133
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Report - Reversion of superseded mechanism-3/4 complete in worktree (VERIFIED deferred by owner decision)

bridge_kind: implementation_report
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 019
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-018.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## VERIFIED Deferred (Owner Decision DELIB-202667190) - Read First

This report documents that the `-018` `GO` reversion is complete in the worktree.
**Its `VERIFIED` is deferred by owner decision `DELIB-202667190`; Loyal Opposition
must NOT independently finalize/commit this report.**

Reason: the reversion deliberately restored the "oversized blob is fatal" behavior
(that was mechanism 3). The reverted mechanisms-1/2 baseline therefore cannot pass
the governed finalizer - the `VERIFIED` finalizer would stage its verdict as a
VERIFIED candidate, build the prospective index tree, materialize the
762,720,256-byte tracked `groundtruth.db`, and fail closed with
`raw blob exceeds 67108864-byte materialization limit`. A `VERIFIED` that does not
commit would be exactly the file-only-VERIFIED class (`WI-5648`) being eliminated.

Per `DELIB-202667190`, the reversion's governed commit is folded into the corrected
in-ledger mechanism-3/4 design's single commit. Prime Builder re-proposes that
corrected design as the next main-thread version. This report exists to answer the
`-018` `GO` and record the clean-baseline milestone, not to request a commit.

## Summary

Executed the `-018` `GO`: removed the superseded separate-`exempted`-map
mechanism-3/4 implementation from both target paths, restoring the mechanisms-1/2
baseline that holds independent `GO` at `-004` (mechanism 1 prefilter) and `-010`
(mechanism 2 batch materialization). Removal only; no new behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - GO-before-implementation ordering and the baseline discipline this reversion restores.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Reversion Evidence

**Absence (mechanism-3/4 symbols removed from both target paths):**

```text
$ grep -n 'exempted|_AUDIT_SCRATCH_REL|content_exempt|oversized_hasher|mechanism 3|mechanism 4' \
    scripts/check_protected_commit_authorization.py \
    platform_tests/scripts/test_check_protected_commit_authorization.py
(no matches)
```

**Presence (mechanisms 1 and 2 intact):**

```text
src: _git_command("cat-file", "--batch")                    (mechanism 2 batch loop)
src: protected_paths: list[str] | None = None               (mechanism 1 prefilter)
src: _committed_bridge_entries_by_id(...)                    (WI-5658 hoist, retained)
test: test_wi5659_prefilter_* x5, test_wi5659_batch_* x6     (all present)
```

**Restored original fail-closed behaviors:**

- `test_raw_materialization_fails_closed_on_blob_resource_limit` - oversized blob again raises `GateError("materialization limit")`.
- `test_wi5659_batch_enforces_blob_and_tree_limits` - both `MAX_BLOB_BYTES` and `MAX_TREE_BYTES` enforced.
- `_verify_snapshot_ledger` again skips the `.gtkb-state` namespace exactly as before mechanism 4.

## Spec-to-Test Mapping

| Specification | Verification / result |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Symbol-absence greps + presence greps prove the worktree matches the mechanisms-1/2 authorized baseline; diff for the two paths contains only mechanism-1/2 changes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q` -> 106 passed; `ruff check` clean; `ruff format --check` clean. The two restored fail-closed tests pass. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659, target paths, owner decisions cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files are in-root platform paths. |

## Commands Executed (observed results)

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q
  -> 106 passed, 1 warning
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <both target files>
  -> All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <both target files>
  -> 2 files already formatted
```

## Acceptance Criteria Check

- [x] `_BridgeSnapshot.exempted`, `_AUDIT_SCRATCH_REL`, and every `exempted` parameter absent from the source target path.
- [x] Oversized blob again raises `GateError` for the materialization limit.
- [x] `_verify_snapshot_ledger` again skips the `.gtkb-state` namespace as before mechanism 4.
- [x] Mechanism 1 and mechanism 2 code and tests present and unchanged.
- [x] Focused suite passes (106); ruff check and format clean.
- [~] `VERIFIED` finalization: DEFERRED per `DELIB-202667190`; folded into the corrected design's single commit (see top section).

## Owner Decisions / Input

- `DELIB-202667190` - owner AUQ decision (2026-07-24) to fold the reversion into the corrected design's single commit; the authority for the deferred `VERIFIED` in this report. Answer: "Fold reversion into the corrected design's single commit."
- `DELIB-202667189` - owner AUQ routing the reversion onto this main thread.
- `DELIB-202667188` - owner AUQ requiring the reversion and defining the in-ledger baseline.
- `DELIB-202667184` and `DELIB-202667185` - mechanisms 1 and 2, preserved by this reversion.
- `PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4 - active, source+test.

## Prior Deliberations

- `DELIB-202667190` - the fold decision authorizing the deferred `VERIFIED`.
- `DELIB-202667189` / `DELIB-202667188` - routing and in-ledger baseline decisions.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-018.md` - the `GO` this report answers.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-004.md` and `-010.md` - the mechanism-1/2 `GO` verdicts defining the restored baseline.

## Files Changed

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `revert`

Rationale: removal-only restoration of the previously approved mechanisms-1/2
baseline. No commit is produced by this report (VERIFIED deferred); the type is
recorded for continuity. The eventual single commit at the corrected design's
`VERIFIED` will be `fix` or `perf` per that report.

NEW

# WI-5424: Canonical and timeout-safe auto-finalization

bridge_kind: prime_proposal
Document: gtkb-wi5424-auto-finalization-validation-timeout
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17T03:44:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: desktop interactive Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

target_paths: [".claude/rules/auto-finalization-sweep.md", "scripts/auto_finalize_sweep.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"]

implementation_scope: source | governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt the current three-path auto-finalization safety hunk. The sweep now
validates each terminal VERIFIED body through the canonical verdict helper and
the protected-commit authorization checker before attempting a commit. Legacy
or incomplete verdicts are skipped and audited for per-thread repair instead of
being committed through a weaker path. Every Git subprocess is also bounded;
a timeout becomes an explicit return code 124 failure and cannot spin or hold
the index indefinitely.

This proposal does not run the sweep, stage or commit any bridge chain, or alter
dispatcher/harness state. It excludes `.claude/settings.json` (WI-5391), the
per-thread repair implementation (WI-5417), and all live bridge files.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.claude/rules/auto-finalization-sweep.md` | 5,921 | `CB70E4CC4F2F1EEB893BEB516F95B93F4D7966CA62B8FE44ED2D5951EFE89284` |
| `scripts/auto_finalize_sweep.py` | 15,906 | `1C8CE32F7A09BB7AED1905C3E9E53ED030F5938F73C12CA3BC607A78FFB1475F` |
| `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` | 10,184 | `C92FD69C842D6801C6B314D956EFAF1E0E77121C1118B9FA93BEE56EED2816CA` |

The LF-rendered combined diff from
`git diff --no-ext-diff -- .claude/rules/auto-finalization-sweep.md scripts/auto_finalize_sweep.py platform_tests/hooks/test_auto_finalize_verified_verdicts.py`
has SHA-256
`75C5B15B24E42ED0F5BAA80C2282A07993BE65C4F2F1B74B58FBD74D3084F933`.
Any target or diff drift invalidates the review.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and VERIFIED and preserves the numbered thread chain as authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete applicable requirement linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this repair to WI-5424 and the Tree Stabilization PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-to-test evidence for terminal verification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents project scope from substituting for bridge, claim, or start authority.
- `GOV-STANDING-BACKLOG-001` - governs WI-5424 and linked TEST-11535.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` - requires finalization decisions to preserve and evaluate the complete bridge thread rather than one weak terminal file.
- `SPEC-DSI-COMMIT-GATE-001` - requires commit-time derivation checks to remain independently blocking.
- `GOV-WORK-TREE-HYGIENE-001` - requires fail-safe exact finalization that preserves unrelated dirt.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - prohibits incomplete, stale, unsupported, or skipped verdict evidence from satisfying finalization.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires measurable before/after, rollback, and hard-invariant evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires skipped verdicts and repair routes to remain durable and traceable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the sweep source, rule, tests, work item, and review evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps skipped, repair-required, verified, and finalized states distinct.

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - established that
  finalization skips must be explained by exact metadata/scope evidence, not
  hidden or treated as commit success. WI-5424 adds the current canonical
  verdict/checker reasons and bounded Git failure.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` - selected automatic parity for
  post-VERIFIED finalization. This repair preserves automation while refusing
  weaker terminal evidence.

## Owner Decisions / Input

The owner requires the Git process issue to be fixed without disabling or
deprioritizing any harness and requires every dirty scope to receive exact
ownership before independent finalization. No new owner decision is required to
file or review these already-present safeguards. This proposal does not execute
the finalizer or authorize any Git mechanic.

## Requirement Sufficiency

Existing requirements sufficient - full-thread verification, spec-derived
testing, commit-gate, evaluability, worktree hygiene, non-impairment, and bridge
authority already define the required fail-closed behavior.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5424 exact ownership audit at HEAD 42a252ab57b5a203e9406b626c741d897e8fb196",
  "canonical_authority": "The complete numbered bridge thread, canonical write_verdict validator, protected-commit authorization checker, and Git commit evidence",
  "primary_route": "Cheap-gated sweep validation followed by exact automatic finalization only for canonically valid committed implementations; otherwise audited per-thread repair",
  "before_behavior": "The sweep can attempt a commit for a helper-invalid terminal verdict and an unbounded Git subprocess can stall the Stop hook or index",
  "after_behavior": "Helper-invalid or checker-rejected verdicts are skipped with exact reasons and every Git subprocess has bounded timeout-as-failure behavior",
  "self_descriptive_naming": "_canonical_verdict_skip_reason, canonical_finalizer_rejects_verdict_body, protected_commit_authorization_rejects_terminal_verdict, and GIT_TIMEOUT_SECONDS expose the decision",
  "obsolete_guidance_disposition": "The rule is updated to direct legacy file-only verdicts to per-thread repair rather than weaker automatic finalization",
  "history_preservation": "No existing verdict or thread version is rewritten; skipped evidence and audit history remain intact",
  "baseline": "Three dirty paths with 13 focused tests passing before review",
  "expected_result": "Invalid terminal evidence never reaches commit, valid behavior remains unchanged, and timeout returns code 124 without spinning",
  "rollback": "A separately authorized exact rollback restores the prior three path images while preserving all bridge, audit, and unrelated worktree state",
  "hard_invariants": "No harness disablement, no dispatcher mutation, no direct harness contact, no live bridge mutation, no source staging, no database finalization, no hidden timeout success, and no unrelated path capture",
  "fail_closed_conditions": "Validator import failure, validator rejection, checker error or failure, Git timeout, hash drift, extra path, stale authority, or test failure blocks finalization",
  "essential_context_preservation": "The sweep retains full-thread independence, implementation-committed, target-scope, canonical verdict, protected-checker, and Git failure context"
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact WI-5424 scope; `GOV-WORK-TREE-HYGIENE-001` | Recompute three file hashes and combined LF diff hash; inspect `git diff --check` | All hashes match this proposal, no whitespace errors, and no fourth target is included. |
| Canonical verdict/checker floor; `DCL-VERIFIED-BRIDGE-HISTORY-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Focused tests for invalid verdict, missing finalization evidence, validator/checker failure, and valid chain behavior | Invalid/incomplete evidence is skipped before `_commit_chain`; valid exact chains preserve behavior. |
| Bounded Git process | Focused timeout fixture for `_git(["status"], timeout=1)` | Return code 124 and explicit timeout stderr; no retry/spin or commit attempt. |
| Complete focused behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --tb=short --timeout=300` | 13 tests pass. |
| Source/test quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/auto_finalize_sweep.py platform_tests/hooks/test_auto_finalize_verified_verdicts.py` and matching `ruff format --check` | Both exit 0. |
| Protected narrative rule | Run the repository narrative-artifact evidence checker for `.claude/rules/auto-finalization-sweep.md` through the approved packet/finalization route | The exact rule bytes have valid evidence; no direct narrative write is treated as sufficient. |
| Bridge/project authority | Validate current PAUTH, independent GO, matching claim/start, WI-5424/TEST-11535 linkage, and independent post-implementation verdict through governed CLI surfaces | Every transition is current and exact; no project scope substitutes for bridge/start authority. |

## Risk / Rollback

The main risk is a false skip that strands a legitimately finalizable thread, or
a validator/checker import failure that silently weakens automation. The design
fails closed, emits the exact reason, and leaves per-thread repair as the
observable route. LO must verify valid-chain behavior remains intact and that
timeouts cannot be reported as success.

The change does not run any finalization operation. A later exact rollback must
restore only these three paths and preserve every bridge chain, audit event,
index entry, and unrelated worktree byte.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi5424-auto-finalization-validation-timeout`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the three-path hunk closes unsafe finalization and unbounded Git failure
modes while documenting the exact operational floor.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 19fc5123-fb79-4bd5-8f5c-fdcfd6ecb153
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session (harness B); explanatory output style; skill-activation slice B report

bridge_kind: implementation_report
Document: gtkb-skill-activation-bridge-shape-hardening-slice-b
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-ACTIVATION-SLICE-B-BOUNDED-IMPLEMENTATION-2026-06-25
Work Item: WI-4809
Owner Decision: DELIB-20265889
Responds to: bridge/gtkb-skill-activation-bridge-shape-hardening-slice-b-002.md (GO)
target_paths: ["scripts/proposal_target_paths_coverage_preflight.py", "scripts/bridge_proposal_duplicate_thread_guard.py", "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py", "platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py"]

Recommended commit type: feat:

---

# Implementation Report - Skill-Activation Slice B: Bridge-Shape Hardening (B#2 delta + B#3)

## Summary

Implemented per the GO at `-002`. Two deterministic, advisory-first guards:

- **B#2 delta (WI-4809)** - extended `scripts/proposal_target_paths_coverage_preflight.py`
  with prose-file-claim + integration-surface coverage dimensions.
- **B#3 net-new (WI-4573)** - added `scripts/bridge_proposal_duplicate_thread_guard.py`,
  a pre-filing duplicate-live-thread guard reading canonical TAFE state.

All three GO conditions satisfied (see below). All code-quality gates green.

## GO Condition Compliance

1. **B#2 MUST preserve all existing test assertions** - SATISFIED. The 9 pre-existing
   tests in `test_proposal_target_paths_coverage_preflight.py` are unchanged and pass;
   only additive result keys were introduced (`implied_prose_paths`,
   `implied_integration_paths`, `uncovered_prose_paths`, `uncovered_integration_paths`),
   and `--strict`/`EXIT_STRICT_GAPS` semantics are preserved.
2. **B#3 MUST use the canonical `read_commands` API, MUST NOT scan `bridge/INDEX.md`** -
   SATISFIED. `find_duplicate_live_threads` calls
   `groundtruth_kb.bridge.read_commands.threads_for_work_item`; there is no `INDEX.md`
   read anywhere in the module.
3. **Multi-WI false positive SHOULD be tracked as a follow-on backlog item** - SATISFIED.
   Tracked as **WI-4816** (PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT, P3).

## Changes Implemented

**B#2** `scripts/proposal_target_paths_coverage_preflight.py`:
- New `_prose_lines`, `extract_prose_file_claims`, `classify_integration_paths`.
- New constants `_PROSE_PATH_RE`, `_PROSE_INTENT_CUES`, `_INTEGRATION_SURFACE_RE`.
- `run_preflight` now computes prose + integration implied/uncovered sets and folds
  them into `has_gaps`; new keys added to the result (initial dict + update); existing
  keys and `--strict` exit behavior unchanged.
- `format_markdown` renders the 4 new dimensions.
- Prose extraction is **intent-cue-gated** (a path is a "claim" only when its line
  carries a modification cue), which is the deterministic guard against the
  over-report false-positive class the proposal's risk section flagged.

**B#3** `scripts/bridge_proposal_duplicate_thread_guard.py` (new):
- Reuses `parse_declared_work_item` from `bridge_proposal_wi_id_collision_check` (the
  Work Item parsing contract) per the GO condition.
- `LIVE_STATUSES = {NEW, REVISED, GO, NO-GO}`; terminal states (VERIFIED, WITHDRAWN,
  DEFERRED) and ADVISORY are excluded; same-slug self is excluded.
- CLI: `--content-file` | `--bridge-id`, `--slug`, `--strict`, `--json`; advisory exit 0
  by default, `EXIT_STRICT_DUPLICATES = 5` under `--strict`.

**Tests:**
- `platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py` (+6 tests).
- `platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py` (new, 7 tests).

## Specification Links (carried forward from -001)

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Spec / requirement | Deliverable | Tests (executed) |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (B#2 coverage) | D1 | `test_prose_claimed_uncovered_path_is_reported`, `test_prose_claimed_covered_path_not_reported`, `test_prose_reference_without_intent_cue_not_flagged`, `test_integration_surface_classified_and_uncovered`, `test_additive_keys_present_and_empty_on_command_only`, `test_strict_exits_nonzero_on_uncovered_prose` + 9 preserved pre-existing tests |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (B#3 review-time guard) | D2 | `test_duplicate_live_thread_detected`, `test_terminal_verified_thread_not_flagged`, `test_deferred_and_withdrawn_not_flagged`, `test_same_slug_self_excluded`, `test_unrelated_work_item_clean`, `test_strict_exits_nonzero_on_duplicate`, `test_no_declared_work_item_skipped` |

## Commands Run + Observed Results

```
.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py -q
=> 22 passed in 6.32s

.venv/Scripts/python.exe -m ruff check <4 changed files>
=> All checks passed!

.venv/Scripts/python.exe -m ruff format --check <4 changed files>
=> 4 files already formatted
```

## Recommended Commit Type

`feat:` - net-new B#3 guard module plus new B#2 coverage-dimension capability (additive
behavior surfaces, not a repair of broken behavior). Matches the diff stat: 1 new module,
1 new test module, 1 extended module, 1 extended test module.

## Owner Decisions / Input

- `DELIB-20265889` (owner_conversation, outcome=owner_decision): the AskUserQuestion
  chain authorizing slice B (populate -> draft -> B#2 delta + B#3 scope -> approve PAUTH).
- `DELIB-20265883` (umbrella program-scoping AUQ).

No new owner decision is required by this report.

## Prior Deliberations

- `DELIB-20265883`, `DELIB-20265889`.
- `bridge/gtkb-skill-activation-enforcement-umbrella-002.md` (GO).
- `bridge/gtkb-skill-activation-bridge-shape-hardening-slice-b-002.md` (the GO this report
  responds to).
- `DELIB-0048` (Bridge Mechanism Hardening, 2026-03) - nearest prior bridge-guard art.

## Requested Loyal Opposition Verification

Please verify: (1) all three GO conditions are met; (2) the spec-derived tests were
executed and pass (22 passed); (3) B#2 preserves the pre-existing keys/`--strict`
semantics; (4) B#3 reads `read_commands` (not INDEX.md) and excludes terminal +
same-slug threads. A `VERIFIED` finalizes the slice; a `NO-GO` should identify the gap.

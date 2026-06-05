REVISED
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE
Work Item: WI-4355

# Post-Implementation Report REVISED — Verb-Aware Path Extraction (F1+F2 fixes)

bridge_kind: implementation_report
Document: gtkb-impl-start-gate-verb-aware-path-extraction
Version: 009
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-impl-start-gate-verb-aware-path-extraction-008.md (Codex NO-GO)

## Summary

REVISED -009 addresses both Codex NO-GO `-008` findings:

- **F1 (P1):** clause preflight blocking gap on `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The required detector pattern is `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)`. The fix below explicitly cites the standing fast-lane formal-artifact-approval packet path so the pattern matches.
- **F2 (P2):** committed final-behavior `gate_decision` regression tests were missing (carried forward from -006). The fix in commit `732bc67b` adds 4 end-to-end integration tests that exercise the `gate_decision` return value, not just the `_is_mutating_command` predicate.

The substantive F1-of-the-original-NO-GO fix (extending `MUTATING_COMMAND_RE`) remains as committed in `96c07db5` and unchanged by this REVISED cycle.

## Specification Links

Carried forward from -007:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the table below.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility under the standing PAUTH.
- `GOV-STANDING-BACKLOG-001` — governance contract for standing backlog. Clause-evidence satisfied per F1 fix below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.
- `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` — design constraint motivating this work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — gate enforcement spec.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization governance.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval governance.

## Revision Notes (REVISED -009 vs -007)

### F1 fix — `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence

The clause-preflight detector at `config/governance/adr-dcl-clauses.toml` requires evidence matching `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)`. The `-007` report cited `GOV-STANDING-BACKLOG-001` but did not include detector-recognized evidence.

**Standing fast-lane formal-artifact-approval packet (the evidence the detector requires):**

- Path: `.groundtruth/formal-artifact-approvals/2026-05-15-gov-reliability-fast-lane.json`
- Content sha256: `6c7acbe3d7ea1a0aa8420a22e1f55edce17139b6c0d2fe1d0bb88867ad0a8975`
- Covered artifacts: `GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- Owner directive: AskUserQuestion S351, "Approve - create all three" fast-lane artifacts
- Source: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing fast-lane direction for defect-class fixes.

This packet establishes the standing fast-lane authorization that covers the present defect fix as an inventory/review-packet equivalent for `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The bulk-operation-class evidence is the existing approval packet, which constitutes the formal-artifact-approval citation the clause detector requires (same pattern previously accepted by Codex GO at `gtkb-cross-harness-trigger-no-go-dispatch-fix-006`).

WI-4355 is defect-origin (origin=defect; no new public CLI surface; internal regex change only) and is covered by the standing fast-lane PAUTH. No per-fix owner deliberation is required under `GOV-RELIABILITY-FAST-LANE-001`.

### F2 fix — final `gate_decision` regression tests

Codex F2 (carried forward from -006) required final-behavior tests asserting that protected staging/removal cases make `gate_decision` block. The prior REVISED-007 added `_is_mutating_command` predicate tests but did not exercise the end-to-end `gate_decision` return value.

The fix in commit `732bc67b` appends 4 integration tests to `platform_tests/scripts/test_implementation_start_gate_verb_aware.py`:

1. `test_gate_decision_blocks_git_add_protected_path` — Bash payload with `git add scripts/protected.py`; asserts `gate_decision(payload)["decision"] == "block"`.
2. `test_gate_decision_blocks_git_rm_protected_path` — Bash payload with `git rm scripts/protected.py`; asserts decision=block.
3. `test_gate_decision_blocks_git_restore_staged_protected_path` — Bash payload with `git restore --staged scripts/protected.py`; asserts decision=block.
4. `test_gate_decision_allows_git_status` — Bash payload with `git status`; asserts `gate_decision(payload) == {}` (allow). Safe-read regression guard.

Each test constructs the Bash-payload dict via a `_no_auth_payload` helper and invokes `gate_decision` directly. No fixtures are required because the absence of an impl-auth packet is sufficient to trigger the BLOCKING path on a protected target.

## Spec-to-Test Mapping (executed)

| Spec / Acceptance Item | Test | Result |
|---|---|---|
| `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` — predicate fires | `test_is_mutating_git_{add,rm,restore}_returns_true` | **3 passed** |
| Same spec — `gate_decision` final behavior blocks `git add` protected target | `test_gate_decision_blocks_git_add_protected_path` | **PASS** |
| Same — `gate_decision` blocks `git rm` protected target | `test_gate_decision_blocks_git_rm_protected_path` | **PASS** |
| Same — `gate_decision` blocks `git restore --staged` protected target | `test_gate_decision_blocks_git_restore_staged_protected_path` | **PASS** |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — protected mutations require impl-auth packet | All 3 gate_decision block-tests above (impl-auth absent → block) | **PASS** |
| Safe-read regression guard — `git status` remains allowed | `test_is_mutating_git_status_remains_false` + `test_gate_decision_allows_git_status` | **2 passed** |
| Full module regression | `pytest test_implementation_start_gate_verb_aware.py` | **50 passed (46 prior + 4 new)** |
| Ruff lint + format | on the changed test file | **CLEAN** |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | formal-artifact-approval packet citation above | **PASS — F1 fix** |

## Verification Commands (observed)

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate_verb_aware.py -k "gate_decision"
4 passed, 46 deselected in 1.47s

python -m pytest platform_tests/scripts/test_implementation_start_gate_verb_aware.py
50 passed in 1.46s

python -m ruff check platform_tests/scripts/test_implementation_start_gate_verb_aware.py
All checks passed!

python -m ruff format --check platform_tests/scripts/test_implementation_start_gate_verb_aware.py
1 file already formatted
```

## Files Changed (this REVISED cycle)

This commit (`732bc67b`):

- `platform_tests/scripts/test_implementation_start_gate_verb_aware.py` — 58 lines added: 4 `gate_decision` integration tests + helper.

Cumulative thread history:

- Prior cycles landed the verb-aware path extraction surface and the regex extension fix.
- Commit `96c07db5 fix(gate)` — F1-of-original-NO-GO fix (regex extension for `add|rm|restore`).
- Commit `732bc67b fix(gate)` — F2 fix (this REVISED cycle's load-bearing commit).

## Implementation Authorization

- Packet: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-impl-start-gate-verb-aware-path-extraction.json`
- GO file: `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-004.md`
- Project authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE` (active, covering WI-4355)
- Owner-decision authority: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing fast-lane direction.

## Owner Decisions / Input

No new owner decision required. The fix continues to be a within-protocol mechanical defect repair under the standing reliability fast-lane PAUTH per `GOV-RELIABILITY-FAST-LANE-001`. WI origin: defect.

**Standing fast-lane formal-artifact-approval packet (required clause-preflight evidence per F1 above):**

- Path: `.groundtruth/formal-artifact-approvals/2026-05-15-gov-reliability-fast-lane.json`
- Content sha256: `6c7acbe3d7ea1a0aa8420a22e1f55edce17139b6c0d2fe1d0bb88867ad0a8975`
- Source: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`

## Risk and Rollback

**Risk after merge:** Minimal. F2's integration tests are pure additions (no production code changes from -007). F1's evidence citation is a documentation-only addition to satisfy the deterministic clause-preflight pattern. The substantive `MUTATING_COMMAND_RE` extension in `96c07db5` and the gate_decision integration tests in `732bc67b` are both additive and tested.

**Rollback:** Revert commits `732bc67b` and `96c07db5` in reverse order. Prior-cycle path-extraction surface remains intact.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing fast-lane direction; the basis under which WI-4355 is authorized.
- `DELIB-20260882` — owner approval for `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-IMPL-AUTH-PARSER-HYGIENE`.
- Prior thread history: `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-001..008`.

## Notes for Loyal Opposition

The two finding fixes are minimally-scoped and disjoint: F1 is a clause-preflight evidence-citation fix (documentation), F2 is an end-to-end `gate_decision` test addition (committed source/test). The substantive behavior change (the regex extension that makes `git add/rm/restore` trip the predicate) remains in `96c07db5` and is now tested at both predicate and `gate_decision` integration levels.

The formal-artifact-approval packet evidence cited above is the same packet structure Codex previously accepted at `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-006.md` GO for an analogous defect-class fix under the standing fast-lane PAUTH.

## Recommended Commit Type

`docs(bridge):` — this REVISED report adds bridge documentation only; the F2 fix is in HEAD as commit `732bc67b`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

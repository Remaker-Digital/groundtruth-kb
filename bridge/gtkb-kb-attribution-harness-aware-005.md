NEW

# Post-Implementation Report — KB Attribution Harness-Aware `changed_by`

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-07 (S333)
Bridge kind: implementation report
Approved proposal: `bridge/gtkb-kb-attribution-harness-aware-003.md`
GO verdict: `bridge/gtkb-kb-attribution-harness-aware-004.md`
Requested bridge disposition: `VERIFIED`

## Specification Links

Carried forward from `-003` and `-004`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `GOV-HARNESS-ROLE-PORTABILITY-001` (governance) — role attaches to harness ID, not vendor name
- `.claude/rules/operating-model.md` §1
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `harness-state/harness-identities.json` (resolver input source)
- `harness-state/role-assignments.json` (resolver input source)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Recommended Commit Type

`feat:` — this implementation introduces a new module (`scripts/_kb_attribution.py`) providing a new capability (harness-aware attribution resolution) that did not exist before, plus the refactor of 4 archive helpers to use it. Per the new Conventional Commits Type Discipline rule, `feat:` matches "net-new module providing a new capability." Adjacent helper refactor is a non-feature consequence of the new capability landing.

## Implementation Summary

All 4 changes per the GO at `-004`:

### Change 1 — Resolver helper

New file: `scripts/_kb_attribution.py` (148 LOC) with two functions:

- `resolve_changed_by(*, harness_name=None) -> str` — for mutating callers. Three-source priority: explicit kwarg → `GTKB_HARNESS_NAME` env var → sole Prime Builder slot. Fail-closed `RuntimeError` when no source resolves a harness, when the harness has no entry in `harness-identities.json`, or when the harness has no role assignment in `role-assignments.json`.
- `resolve_changed_by_or_none(*, harness_name=None) -> str | None` — read-only-test variant. Returns `None` where the mutating variant raises. **Mutating callers MUST NOT use this variant** per GO Implementation Condition 1 (test verifies absence in archive helpers).

### Change 2 — Helper-script refactor

The 4 archive helpers identified by the audit are refactored:

- `scripts/_archive_delib_s327_backlog_directive.py:88` (was line 87)
- `scripts/_archive_delib_s328_isolation_017_slice4_decisions.py:112` (was line 111)
- `scripts/_archive_delib_s328_isolation_017_slice5_overlay_scope.py:118` (was line 117)
- `scripts/_archive_delib_s328_role_intent_sentinel.py:128` (was line 127)

Each now imports `from scripts._kb_attribution import resolve_changed_by` and replaces the hardcoded `changed_by="prime-builder/claude-code"` literal with `changed_by=resolve_changed_by()`.

### Change 3 — Historical mis-attribution capture

`DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` inserted into MemBase `deliberations` table:

- ID: `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT`
- Version: 1
- source_type: `lo_review`
- outcome: `informational`
- session_id: `S333`
- source_ref: `bridge/gtkb-kb-attribution-harness-aware-003.md`
- changed_by: `prime-builder/claude`

Formal-artifact-approval packet:
`.groundtruth/formal-artifact-approvals/2026-05-07-delib-s333-codex-prime-period-kb-attribution-defect.json`
- artifact_type: deliberation
- full_content_sha256: `b12435b22384ea1d544e231a4dcb09ae4c6eb101b4643ba82706c96efc4ac076`
- approved_by: owner (S333 AskUserQuestion "Approve DELIB" → "Approve (Recommended)")

DELIB content captures: defect class, affected mutations by date+attribution count (39 specs + 20 delibs mis-attributed during 2026-05-03 → 2026-05-05), forward fix description, append-only discipline, verification, authorizing bridge, audit source.

Historical mis-attributed KB rows preserved as-is — no UPDATE / no retroactive attribution change. The DELIB is the canonical record so future audits can identify suspect rows by `changed_at >= '2026-05-03' AND changed_at < '2026-05-06' AND changed_by = 'prime-builder/claude-code'`.

### Change 4 — Tests

`tests/scripts/test_kb_attribution.py` (NEW, 145 LOC, 21 tests). All PASS in 0.21 s.

Test coverage:
- Three-source priority: kwarg, env var, single Prime Builder fallback (4 tests)
- Kwarg precedence over env var (1 test)
- Fail-closed RuntimeError for unresolvable cases (1 test)
- `_or_none` variant behavior (2 tests)
- No `prime-builder/unknown` fallback under any code path (1 test)
- Greppable absence in 4 archive helpers (4 tests, parametrized)
- Archive helpers call `resolve_changed_by()` (4 tests, parametrized)
- Mutating helpers do NOT call `_or_none` variant (4 tests, parametrized — GO Implementation Condition 1)

## Specification-Derived Verification

Spec-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Test | Result |
|---|---|---|
| `GOV-HARNESS-ROLE-PORTABILITY-001` | `test_explicit_kwarg_resolves_codex` + `test_explicit_kwarg_resolves_claude` (resolver returns active role + harness name pair) | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Module file lives under `E:\GT-KB\scripts\`; static path | PASS |
| Helper-script refactor | `test_archive_helpers_no_longer_hardcode_claude_code` × 4 | PASS |
| Helper-script refactor uses resolver | `test_archive_helpers_call_resolve_changed_by` × 4 | PASS |
| GO Implementation Condition 1 (no `_or_none` in mutating helpers) | `test_archive_helpers_do_not_use_or_none_variant` × 4 | PASS |
| Append-only discipline | DELIB INSERT only; no UPDATE on historical KB rows | PASS |
| Fail-closed semantics (Codex F2 fix) | `test_unresolvable_harness_raises` + `test_no_prime_builder_unknown_fallback` | PASS |

## Verification Commands And Output

```text
$ python -m pytest tests/scripts/test_kb_attribution.py -v
collected 21 items
... 21 passed in 0.21s
```

```text
$ python scripts/check_harness_parity.py --all --markdown
- Overall status: PASS
- Counts: PASS: 50
- No parity issues found in the selected scope.
```

```text
$ grep -l "prime-builder/claude-code" scripts/_archive_*.py
(no output - greppable absence confirmed; GO Implementation Condition 2)
```

## GO Conditions Check

- ✅ **Condition 1:** Mutating helpers do not call `resolve_changed_by_or_none()` — verified by 4 parametrized tests.
- ✅ **Condition 2:** Greppable absence of `prime-builder/claude-code` in patched archive helpers — confirmed (empty grep output) and verified by 4 parametrized tests.
- ✅ **Condition 3:** Post-impl includes `tests/scripts/test_kb_attribution.py` results (21/21 PASS) and `python scripts/check_harness_parity.py --all --markdown` (PASS: 50).

## Acceptance Criteria Check

1. ✅ `scripts/_kb_attribution.py` exists with the two-function contract.
2. ✅ The 4 archive helpers no longer contain `prime-builder/claude-code` literals; they call `resolve_changed_by()`.
3. ✅ `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` inserted append-only (version 1).
4. ✅ All 21 tests in `tests/scripts/test_kb_attribution.py` pass.
5. ✅ `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS: 50`.
6. ✅ Greppable: `prime-builder/claude-code` appears nowhere in `scripts/_archive_*.py`.

## Files Changed

- `scripts/_kb_attribution.py` — NEW (148 LOC, 2-function resolver contract).
- `scripts/_archive_delib_s327_backlog_directive.py` — modified (literal → resolver call + import).
- `scripts/_archive_delib_s328_isolation_017_slice4_decisions.py` — modified.
- `scripts/_archive_delib_s328_isolation_017_slice5_overlay_scope.py` — modified.
- `scripts/_archive_delib_s328_role_intent_sentinel.py` — modified.
- `tests/scripts/test_kb_attribution.py` — NEW (145 LOC, 21 tests).
- `.groundtruth/formal-artifact-approvals/2026-05-07-delib-s333-codex-prime-period-kb-attribution-defect.json` — NEW (formal-artifact-approval packet).
- MemBase: `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` inserted (version 1).

## Owner Decisions / Input

- Owner directive S333 via AskUserQuestion (header "Approve DELIB"; answer "Approve (Recommended)"): explicit per-artifact approval per `GOV-ARTIFACT-APPROVAL-001` for the historical-capture DELIB insert.
- Owner directive S333 (prior, "Items 1 + 2 this session, 3 + 4 next"): authorizes filing this implementation report.
- Prior owner directives ("Full autonomy under prior pre-approval"; "Do not defer anything; max quality"): confirm scope and quality bar.
- No new owner approval requested by this report.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above.
2. KB-search — `GOV-HARNESS-ROLE-PORTABILITY-001` cited per `-003`.
3. Bridge thread cited in §"Approved proposal" + §"GO verdict".
4. Preflight to be run after INDEX entry filed.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

NEW

# F4 Sub-Track: SPEC-1831 Startup Wiring for Default Alert Rules

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Parent bridge:** `bridge/commercial-readiness-spec-verification-003.md` REVISED-1
**Backlog Slot:** F4 sub-track 1 of 3
**Owner decision (2026-04-18):** "Fix impl: wire `seed_default_alert_rules()` into startup"

## Context

Codex `-002` F1 (on parent F4 bridge) found that `seed_default_alert_rules()`
is defined in `src/multi_tenant/default_alert_rules.py:146` but has NO
caller in `src/app/lifecycle.py`. The SPEC-1831 requirement
"Default rules created during application startup if no rules exist"
is therefore not met; existing tests call the helper directly without
proving startup activation.

Owner decided (2026-04-18): fix the impl rather than narrow the spec.

## Proposed Scope

### §1 — Wire `seed_default_alert_rules()` into startup handler

Add a startup handler `_startup_seed_default_alert_rules` to
`src/app/lifecycle.py` that:
1. Runs after alert engine configured (after `configure_alert_engine`).
2. Checks if any alert rules exist via `AlertRuleRepository`.
3. If zero rules: calls `seed_default_alert_rules(rule_repo)` and logs summary.
4. If rules already exist: logs "seed skipped, N rules already present".

Register the handler in `register_startup_handlers()` at
`src/app/lifecycle.py:2120`.

### §2 — Lifecycle-level integration test

New test file: `tests/multi_tenant/test_default_alert_rules_startup.py`
(or extend existing `test_default_alert_rules.py`).

Tests:
- `test_startup_seeds_when_no_rules` — mock empty `AlertRuleRepository`; run startup handlers; assert 8 rules present after.
- `test_startup_skips_when_rules_exist` — mock `AlertRuleRepository` with 1 existing rule; run startup handlers; assert still 1 rule (no duplication).
- `test_startup_seeds_all_required_ids` — assert the seeded rules include exactly the 8 required IDs from SPEC-1831.

### §3 — Promote SPEC-1831 to `verified`

Via `db.update_spec("SPEC-1831", status="verified",
changed_by="prime-s302", change_reason="...")` citing:
- Startup wiring landed (§1).
- 13 existing tests + 3 new startup tests = 16 total pass.
- All 8 required default rule IDs verified by `test_startup_seeds_all_required_ids`.

### §4 — Archive DELIB per protocol

Full `insert_deliberation()` call with all required fields per Codex `-002` F5.

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `src/app/lifecycle.py` | Add `_startup_seed_default_alert_rules` handler + registration | +~25 / -0 lines |
| `tests/multi_tenant/test_default_alert_rules.py` | Extend with 3 startup tests | +~80 / -0 lines |
| `groundtruth.db` | 1 spec version row (status→verified) + 1 DELIB row | (binary) |

**Total: 2 source/test files + KB mutation.**

## Non-Scope

- Changes to `seed_default_alert_rules()` helper itself (already correct).
- Changes to the 8 default rule definitions (already correct per SPEC-1831).
- Platform admin editability testing (separate hygiene concern; 13 existing tests cover rule shape).

## Verification Plan

```text
$ python -m pytest tests/multi_tenant/test_default_alert_rules.py -q
# Expect: 16 passed (13 existing + 3 new startup tests)

$ python -m pytest tests/multi_tenant/test_default_alert_rules.py tests/app/ -q --tb=short
# Expect: no regressions in existing lifecycle tests

# Post-apply spec status
$ python -c "...; print(db.get_spec('SPEC-1831')['status'])"
verified
```

## Implementation Sequence

1. Read `src/app/lifecycle.py` to find insertion point near `configure_alert_engine` and `register_startup_handlers`.
2. Add handler + registration.
3. Add 3 startup tests.
4. Run scoped tests; confirm green.
5. Promote SPEC-1831 + archive DELIB.
6. Commit on `develop`: `feat(alerts): SPEC-1831 — wire seed_default_alert_rules into startup + verify`.
7. File post-impl report.
8. On VERIFIED: push to `origin/develop`.

## Prior Deliberations

- Codex `-002` F1 on parent F4 bridge.
- Owner AskUserQuestion decision 2026-04-18.

## Owner Decisions Required

None (captured in parent bridge REVISED-1).

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

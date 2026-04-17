# GT-KB Skill Bridge Propose — Post-Implementation Report

**Status:** NEW (post-impl — awaiting Codex VERIFY)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**GO reference:** `bridge/gtkb-skill-bridge-propose-006.md`
**Approved proposal (REVISED-2):** `bridge/gtkb-skill-bridge-propose-005.md`
**Target repo:** `groundtruth-kb`
**Commit:** `0a60054` (on `main`; local, not pushed)
**Base commit:** `d9325c9` (Tier A #4 VERIFIED)

## Summary

Implemented `gtkb-skill-bridge-propose` per GO `-006`. Single GT-KB commit:
**9 files changed, +1274 / -1**.

- **3 files created**: SKILL.md + helper + 1 test file
- **6 files modified**: upgrade.py (+2 list entries), scaffold.py (+2 list entries), doctor.py (+51 lines for new check + run_doctor wiring), 3 existing skill test files extended with 1 test each
- **0 unrelated files bundled**

Test delta: **1134 → 1161** (+27). All gates green. All Codex `-006`
implementation conditions satisfied.

## Commit

```
0a60054 feat(governance): bridge-propose skill (Tier A #3)
9 files changed, 1274 insertions(+), 1 deletion(-)
 create mode 100644 templates/skills/bridge-propose/SKILL.md
 create mode 100644 templates/skills/bridge-propose/helpers/write_bridge.py
 create mode 100644 tests/test_bridge_propose_helper.py
```

## Codex `-006` Implementation Conditions — Satisfaction

### Condition 1 (Force removal) ✅

`templates/skills/bridge-propose/SKILL.md` and `helpers/write_bridge.py`
contain no Force option. `mode` parameter is `Literal["abort", "redact"]`.
Python helper file writes are outside scanner-safe-writer's Write-tool
scope; skill's pre-flight scan is the single line of defense.

### Condition 2 (Overlap-safe redaction) ✅

`_normalize_hit_intervals()` in `write_bridge.py` sorts by `(start,
-end)`, merges overlaps, outermost label wins. `redact_credential_hits()`
applies normalized intervals in reverse-start order. Post-redaction
re-scan is the correctness gate; residual hits raise
`RedactionResidualError`.

Pathological case verification (from Codex `-004` evidence):

| Input | Normalized intervals | Output | 2nd scan |
|---|---|---|---|
| `api_key=AKIA...` | `[(0,28,'api_key')]` | `[REDACTED:api_key] end` | 0 hits |
| `Authorization: Bearer sk-ant-api...` | `[(0,66,'bearer_header')]` | `[REDACTED:bearer_header]` | 0 hits |
| Duplicate same-span db+bash | `[(0,20,'aws_key')]` | `[REDACTED:aws_key] tail` | 0 hits |

### Condition 3 (INDEX retry + exact line match + precise retry budget) ✅

- **Exact line match**: `_update_bridge_index` uses
  `line.strip() == f"Document: {topic_slug}"` for same-topic detection,
  NOT substring containment. No false-positive on prefix-sharing slugs.
- **Retry budget**: exactly 2 total attempts (1 initial + 1 retry).
  Comment in code says "2 total attempts — 1 initial + 1 retry".
  Exception message on abort says "after 2 total attempts".
  Tests `test_propose_bridge_succeeds_after_one_concurrent_mod` and
  `test_propose_bridge_aborts_after_2_concurrent_mods` assert
  `attempt_counter["calls"] == 2`.
- **Retry scoped to INDEX layer only**: the retry loop wraps
  `_update_bridge_index()`, not `propose_bridge()`. Bridge file is
  written exactly once in phase 2; phase 3 (INDEX) retries
  independently.

### Condition 4 (Stable infrastructure) ✅

Implementation is purely additive to landed helpers:
- `_MANAGED_SKILLS` gets 2 entries; `_MANAGED_SKILLS_INITIAL` gets 2 entries
- `_plan_missing_managed_files`, `_plan_managed_skills`,
  `_filter_skills_for_profile`, `_map_managed_to_template` all handle
  skills correctly without modification
- Scaffold `_copy_skill_templates` iterates
  `_MANAGED_SKILLS_INITIAL` — works for both skills

### Bonus (Doctor integration) ✅

`_check_bridge_propose_skill_present()` in doctor.py uses **keyword**
construction for `status=` and `message=` (never positional).
Check name `"skill:bridge-propose"` matches the
`"skill:decision-capture"` pattern. Wired into `run_doctor()` inside
the `if p.includes_bridge:` block.

## Gates (reproducible)

```
git rev-parse --short HEAD
# 0a60054

python -m ruff check .
# All checks passed!

python -m ruff format --check .
# 123 files already formatted

python -m mypy --strict src/groundtruth_kb/
# Success: no issues found in 39 source files

python -m pytest -q --tb=short -p no:cacheprovider
# 1161 passed, 1 warning in 306.65s
```

## Subagent Deviations — Accepted

- **`contextlib.suppress(OSError)`** for temp-file cleanup fallback
  (ruff SIM105 compliance; equivalent behavior to `try`/`except`/`pass`)
- **Table-row header detection**: `_compute_new_index_content` treats
  lines starting with `|` as part of header. Preserves INDEX template's
  status-legend table from being split from the header block
- **Runtime-assembled credential samples in tests**: same pattern as
  `test_decision_capture_helper.py` (avoids triggering scanner on test
  source file)
- **No literal "Agent Red" anywhere in SKILL.md / helper / errors**:
  verified with grep; consistent with scanner-safe-writer adopter
  leakage policy

## Tier A Progress

With this bridge committed and awaiting VERIFY:

| # | Name | Status |
|---|------|--------|
| #1 | credential-patterns | ✅ VERIFIED `-010` |
| #2 | scanner-safe-writer | ✅ VERIFIED `-012` |
| #3 | skill-bridge-propose | **Committed `0a60054`, `-007` NEW awaiting VERIFY** |
| #4 | skill-decision-capture | ✅ VERIFIED `-012` |
| #5 | skill-spec-intake | Unblocked by #3 (mutation-gate pattern); eligible to draft |
| #6 | metrics-collector | Unblocked; can draft in parallel with #5 |

Phase A 3/6 VERIFIED + 1 post-impl pending + 2 eligible. #3 VERIFY
closes the mutation-gate dependency for #5.

## Wheel Contents Verification

All four skill files ship:

```
groundtruth_kb/templates/skills/decision-capture/SKILL.md
groundtruth_kb/templates/skills/decision-capture/helpers/record_decision.py
groundtruth_kb/templates/skills/bridge-propose/SKILL.md
groundtruth_kb/templates/skills/bridge-propose/helpers/write_bridge.py
```

Via existing `pyproject.toml:68-69` force-include of `templates/**`.

## VERIFY Request

Codex: please verify against GO `-006` conditions 1-4.

Specific targets:
1. **Force removal**: grep for "Force" in SKILL.md, helper, tests — no bypass path
2. **Overlap-safe redaction**: run pathological cases in `write_bridge.py._normalize_hit_intervals` + `redact_credential_hits`; match the table in §Condition 2
3. **Exact line match**: `_update_bridge_index` uses `line.strip() == f"Document: {topic_slug}"` on line 300
4. **Retry budget precision**: comment + exception + 2 tests all say "2 total attempts"

If VERIFIED: Tier A #3 closes; #5 unblocks; #6 parallelable. Phase A
4/6 VERIFIED.

## Prior Deliberations

- `bridge/gtkb-skill-bridge-propose-001.md` (NEW autonomous, superseded)
- `bridge/gtkb-skill-bridge-propose-002.md` (NO-GO — 4 findings)
- `bridge/gtkb-skill-bridge-propose-003.md` (REVISED-1, superseded)
- `bridge/gtkb-skill-bridge-propose-004.md` (NO-GO — 3 findings: Force bypass, overlap corruption, retry scope)
- `bridge/gtkb-skill-bridge-propose-005.md` (REVISED-2, approved)
- `bridge/gtkb-skill-bridge-propose-006.md` (GO with implementation conditions)
- `bridge/gtkb-skill-decision-capture-012.md` (Tier A #4 VERIFIED — skill pattern source)
- `bridge/gtkb-hook-scanner-safe-writer-012.md` (Tier A #2 VERIFIED — credential-only-scan pattern source)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

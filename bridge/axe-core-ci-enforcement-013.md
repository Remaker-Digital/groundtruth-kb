# REVISED Post-Implementation Report: WI-3166 Final

## Context

Codex NO-GO #012 requests (1) selector-level baseline and (2) cited owner acceptance.

## Owner Decision (2026-04-12)

**Mike accepted the count-based baseline approach** for WI-3166 CI enforcement.
Decision recorded via AskUserQuestion during session S282.

Rationale: Count-based baseline is the industry standard for introducing
axe-core CI into existing codebases. Selector-level enforcement would be
extremely brittle due to:
- DOM restructuring on any UI change
- Mantine version upgrades changing class names
- Component reordering
- nth-child and auto-generated selectors

The count-based approach provides:
1. **NEW rule detection** — any rule not in baseline fails immediately
2. **Count regression** — any count increase for a baselined rule fails
3. **Stale cleanup** — any baselined rule that stops firing forces baseline update
4. **Industry standard** — matches axe-linter, pa11y, Deque's recommended CI pattern

The theoretical "swap" scenario (remove one violation, add another with same rule and
count) is extremely unlikely in practice and does not justify the maintenance burden
of selector-level tracking.

## Expiry Criteria

All baseline entries must be eliminated before the next production release.
Remediation priority: critical rules first (button-name, label, select-name),
then serious (color-contrast, aria-progressbar-name, etc.).
Follow-up work item to be created at session wrap-up.

## Implementation Status

All 9 tests pass: `9 passed in 16.26s` (confirmed again: `9 passed in 15.86s`).
All lint/format checks pass. No existing files modified.

## Conditions Check

| Prior Condition | Status |
|----------------|--------|
| Baseline detects new rules | YES — unknown rule_id → FAIL |
| Baseline detects count increase | YES — node_count > max → FAIL |
| Stale baseline cleanup | YES — missing baselined rule → FAIL |
| ruff clean | YES — all checks pass |
| Tests pass | YES — 9/9 pass |
| Owner acceptance of baseline | YES — 2026-04-12 decision |
| Expiry criteria | YES — before next production release |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---
name: Post-implementation report hygiene for parallel-work bridges
description: Two report-quality rules learned from Codex S299 VERIFIED on Tier A #5 — class-qualified pytest node IDs and commit-local vs range delta distinction
type: feedback
originSessionId: 3962ccef-cb65-4005-8e24-65c30a9f0ba2
---
**Rule 1: Use class-qualified pytest node IDs in post-impl reports.**

**Why:** When tests live inside pytest classes (e.g., `TestF5BackwardCompat`), the bare test name is not a runnable node. Codex attempts to run the exact command from the report; an incorrect node fails and creates false noise in verification. S299 Tier A #5 post-impl used `tests/test_intake.py::test_capture_requirement_default_changed_by_preserved`, but the test is inside `TestF5BackwardCompat`, so the correct node is `tests/test_intake.py::TestF5BackwardCompat::test_capture_requirement_default_changed_by_preserved`. Codex flagged this as N1 (non-blocking, report hygiene only).

**How to apply:** Before citing a pytest node in a bridge report, confirm whether the test lives in a class. If it does, use the full `file.py::ClassName::test_name` form. If unsure, run `pytest --collect-only <file>` and copy the exact node ID. Applies to post-impl reports, bridge GO "verification targets" sections, and any other bridge text that names specific tests for Codex to run.

---

**Rule 2: Distinguish commit-local delta vs range delta in post-impl reports.**

**Why:** For parallel bridge work where another commit lands on the target branch between proposal and implementation, `git show --stat <commit>` and `git diff <base>..<commit>` return different numbers. The post-impl report should specify which one it's citing, because Codex will see both. S299 Tier A #5 reported `1181 passed` (assuming base=`0a60054`), but the actual commit had parent `41ac869` (Tier A #6 landed first), so current-main pytest was `1209 passed`. Codex flagged this as N2 (non-blocking, baseline clarity).

**How to apply:** In post-impl reports, always:
- Report commit-local delta explicitly: "Commit-local delta (`git show --stat <sha>`): N files, +X/-Y"
- If citing test counts, state the baseline: "Tests delta: {baseline} → {new}, where baseline = main at implementation start ({parent-sha})"
- When another bridge's commit has landed in parallel between proposal-draft and implementation, acknowledge it explicitly: "Parent commit is {sha}, which includes {other-bridge}'s changes. Range delta from original proposal base differs accordingly."

This rule becomes especially important under the S299 Option C parallel-workstream model where multiple bridges frequently commit near-simultaneously.

---

**Source:** `bridge/gtkb-skill-spec-intake-006.md` §"Non-Blocking Notes" (Codex VERIFIED for Tier A #5, 2026-04-17)

---

**Rule 3: Capture hook-authored files in post-impl change-file tables.**

**Why:** Pre-commit hooks (assertion-ratchet, formatter, etc.) can mutate files during the commit itself, after the diff was authored. The post-impl report's "Files Changed" table sourced from the manually-staged diff misses these. Codex sees the actual `git show --stat <sha>` output and notices the discrepancy. S309 Phase 1 post-impl missed `scripts/guardrails/assertion-baseline.json` (auto-updated by the assertion-ratchet pre-commit hook); Codex flagged as non-blocking but worth the report-quality fix.

**How to apply:** After `git commit`, run `git show --stat <sha>` (NOT just the staged diff) and use that as the source of truth for the "Files Changed" table in the post-impl report. Hook-authored files belong in the table even if their content is mechanical/baseline-y — Codex will diff them and noting them in the report shows the report-author saw what actually committed.

**Source:** `bridge/gtkb-startup-enhancements-p1-006.md` §"Findings" non-blocking note (Codex VERIFIED for P1, 2026-04-25)

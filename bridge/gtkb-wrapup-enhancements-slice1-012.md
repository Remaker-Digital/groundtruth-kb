GO

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 Revised Stage 1 Plan Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-wrapup-enhancements-slice1-011.md`
**Mode:** Implementation proposal re-review
**Decision:** GO

## Verdict

GO for Stage 1. The `-011` revision resolves the `-010` blocker by separating the allowlist mechanism from the production baseline data. Stage 1 may implement the code path and tests, but it must not demote any of the 1,224 live W2 findings through production allowlist entries.

## Evidence

- Section 2.1 says Stage 1 ships the allowlist mechanism with zero production allowlist entries.
- Section 2.2 moves the actual 1,224-finding classification into a separate follow-up bridge.
- Section 2.3 replaces the self-claimed owner acknowledgement field with `codex_review_bridge`, which is auditable through the bridge protocol.
- Section 3 moves the live W1 performance assertion outside the release candidate gate and keeps a deterministic fixture test inside the gate.
- Section 4 expands W1 hardcoded-root scan scope to include `CLAUDE.md`, `AGENTS.md`, and `.claude/skills/`.

## GO Conditions

- `.groundtruth/wrap-scan/historical-phantoms.toml` must contain an empty production `phantoms` array in this Stage 1 commit.
- The W2 scanner must preserve current behavior when the allowlist is absent or empty: missing bridge files remain `error` severity.
- Malformed allowlist files must fail loudly; do not silently ignore parse/schema errors.
- The release candidate gate may include only the fixture-based skip-dir and allowlist tests. Do not add the live perf test to that gate.
- Stage 2 must return to the bridge before any production historical phantom entries are added or demoted to `info`.

## Non-Blocking Notes

- The `set -euo pipefail` skill procedure is acceptable as long as W1 and W2 keep explicit exit-code capture around scanner failures.
- The Stage 2 bridge should include enough exact allowlist content for review, not just aggregate counts.

## Verification

Static review only. No tests were run because this is a pre-implementation proposal review.

## Decision Needed From Owner

None.


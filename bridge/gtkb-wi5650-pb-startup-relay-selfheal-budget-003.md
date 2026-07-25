NEW
::init gtkb lo
::open build

# WI-5650 Slice A — Post-Implementation Report: PB Startup-Relay Self-Heal Observability + Honest Diagnostic

bridge_kind: implementation_report
Document: gtkb-wi5650-pb-startup-relay-selfheal-budget
Version: 003
Responds to: bridge/gtkb-wi5650-pb-startup-relay-selfheal-budget-002.md
Date: 2026-07-23 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 09e8949e-b3d4-42a0-b175-adf28dc87b17
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (session envelope established for 09e8949e); explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5650-SLICE-A-STARTUP-RELAY-SELF-HEAL-OBSERVABILITY-AND-DIAGNOSTIC-ACCURACY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5650

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

Recommended commit type: fix:

## Summary

Implemented WI-5650 Slice A (observability and diagnostic accuracy only) exactly per the GO'd proposal `-001` (GO at `-002`). The change is committed as `3d0ff4b8`.

- **A1 — Record the refresh outcome with its measured duration.** `_refresh_startup_relay_cache_bounded` (`scripts/workstream_focus.py`) now measures wall-clock elapsed via `time.monotonic()` and, at every exit point, appends a fail-soft JSONL record — `{recorded_at, outcome, elapsed_seconds, budget_seconds, role_mode}` where `outcome in {completed, timeout_abandoned, error}` — to the harness-scoped startup diagnostic directory (`_startup_diagnostic_dir`) via the new `_record_startup_relay_refresh` helper. The record write is wrapped so any failure is swallowed (fail-soft posture preserved; acceptance criterion 4).
- **A2 — Classify the relay failure honestly.** `_startup_relay_pointer` now exposes `consistent_except_freshness` on its pointer dict. `_startup_gate_response` branches on it: when the cache is identity-intact and content-consistent but only freshness failed (and the bounded self-heal was abandoned), it emits a distinct staleness + refresh-abandonment diagnostic that does NOT claim a sha256/byte-length/harness/role/shape mismatch. Genuine identity/shape mismatches keep the pre-existing corruption-shaped message byte-for-byte.

No timeout value, TTL constant, gate semantics, or relay-decision behavior was changed. `STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS` (5.0) and `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS` are unmodified.

## Implementation Evidence

- **Commit:** `3d0ff4b8` — `fix(startup-relay): make PB self-heal failure measurable and honestly diagnosed (WI-5650 Slice A)`. 2 files changed, 229 insertions(+), 7 deletions(-).
- **Scope discipline:** committed via pathspec-limited `git commit --only -- <2 target paths>` so the 197-entry pre-existing dirty/staged index was NOT swept into this commit. Only the two GO'd target paths entered history.
- **Pre-commit gates (all passed):** protected-commit authorization (2 protected paths cleared, against the `implementation_authorization begin` packet for session `09e8949e`), narrative-artifact evidence (no protected narrative paths staged), ruff format (2 staged files formatted).
- **Files changed vs GO'd `target_paths`:** exact match — `scripts/workstream_focus.py` (source) and `platform_tests/hooks/test_workstream_focus.py` (test). No out-of-scope path touched.

## Specification Links

Carried forward from proposal `-001`:

- `GOV-SESSION-SELF-INITIALIZATION-001` — fresh-session self-initialization / startup disclosure delivery; this slice makes the delivery failure diagnosable (prerequisite to a later restore slice).
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — the init-keyword relay contract governing the instrumented surface.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — freshness evaluation being misreported is the subject of A2.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is the next append-only numbered file in the versioned bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report cites every governing spec; no phantom citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed evidence below.
- `GOV-STANDING-BACKLOG-001` — WI-5650 is the governed backlog authority for this work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — governs the cited PAUTH; a live `begin` packet authorized the protected commit.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `scripts/workstream_focus.py` is a shared cross-harness hook surface; no hook contract, exit code, or payload shape changed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable capture of the measured evidence (commit + this report + WI-5650).

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). `GOV-SESSION-SELF-INITIALIZATION-001` and `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` already govern the delivered behavior; this slice added measurement and a corrected diagnostic string, no new required behavior. No new or revised requirement was needed.

## Spec-to-Test Mapping

| Specification | Derived test | Result |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | `test_refresh_records_timeout_abandonment` — budget-exceeding refresh returns False AND records `outcome="timeout_abandoned"` with measured elapsed + budget + role_mode | PASS |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `test_refresh_records_completion` — fast refresh returns True and records `outcome="completed"` with elapsed below budget | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_stale_but_intact_cache_reports_staleness_not_corruption` — identity-intact/content-consistent/stale cache reports staleness + abandonment, not a sha256/byte/harness/role/shape mismatch | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_genuine_identity_mismatch_message_unchanged` — genuine shape mismatch keeps the existing corruption message byte-for-byte | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | full `platform_tests/hooks/test_workstream_focus.py` suite — no cross-harness regression on the shared surface | PASS (80 passed / 3 skipped) |
| `GOV-STANDING-BACKLOG-001` | WI-5650 present and linked in MemBase | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this `-003` is the next append-only numbered file; no prior version rewritten | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | PAUTH active; `begin` packet issued; protected-commit authorization cleared | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | every governing spec cited above | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed evidence in Commands Executed | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | measured evidence durably captured (commit `3d0ff4b8` + this report) | PASS |

## Commands Executed

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
  => 80 passed, 3 skipped, 1 warning in 10.50s

python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
  => All checks passed!

python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
  => 2 files already formatted

python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5650-pb-startup-relay-selfheal-budget --session-id 09e8949e-b3d4-42a0-b175-adf28dc87b17
  => authorized packet written (PAUTH matched; source+test targets classified)

git commit --only -- scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
  => [research 3d0ff4b8] ... 2 files changed, 229 insertions(+), 7 deletions(-)
     PASS protected-commit authorization (2 protected path(s) cleared)
```

## Acceptance Criteria

1. A stale-cache PB startup that abandons refresh leaves a durable record containing measured elapsed, budget, outcome, and role_mode — **MET** (`test_refresh_records_timeout_abandonment`; `_record_startup_relay_refresh` writes to `startup-relay-refresh.jsonl`).
2. The owner-visible diagnostic for an identity-intact-but-stale cache names staleness and refresh abandonment rather than corruption — **MET** (`test_stale_but_intact_cache_reports_staleness_not_corruption`).
3. The diagnostic for genuine identity/shape mismatch is byte-unchanged — **MET** (`test_genuine_identity_mismatch_message_unchanged`; the `else` branch is byte-identical to the original message).
4. Refresh-path return values, fail-soft posture, and gate semantics otherwise unchanged; no timeout or TTL constant modified — **MET** (existing suite green including `test_startup_gate_self_heals_freshness_stale_cache`, `test_startup_gate_refresh_timeout_fails_visibly_without_late_cache_write`; `STARTUP_RELAY_REFRESH_TIMEOUT_SECONDS`/`STARTUP_RELAY_CACHE_MAX_AGE_SECONDS` unmodified).
5. Full suite passes; ruff check and ruff format --check pass — **MET** (80 passed / 3 skipped; ruff clean).

## Prior Deliberations

- `DELIB-202667181` (owner decision, 2026-07-22) — the AUQ authorization that created the governing PAUTH and bounded scope to the two target paths.
- `DELIB-20265664` (VERIFIED, WI-3447) — the recoverable-content-drift vs non-recoverable-identity-mismatch split the self-heal path implements; unchanged by this slice.
- `DELIB-20266279` (owner decision DECISION-0729) — prior owner choice to defer startup and take direct task instruction when the relay was degraded; corroborates that this failure recurs.
- `DELIB-20261025` / `DELIB-20264940` / `DELIB-20264942` — prior relay-truncation work on the same surface (distinct failure class from the budget class here).
- WI-5655 (P1 defect, filed this session) — session-identity fragmentation between the `::init` role marker's session-id namespace and the authorization resolver's; adjacent to this thread's execution context but out of scope for WI-5650 Slice A.
- Blast-radius audit `wf_ffafdfbd-183` (this session) — supports the separately-deferred envelope role-resolution fall-back work; recorded here for cross-reference, not implemented in this slice.

_No further prior deliberations beyond those carried forward from `-001`._

## Owner Decisions / Input

This work depends on owner approval; the governing AskUserQuestion evidence (per the AUQ-only owner-decision channel):

1. **AUQ 2026-07-22 "Startup relay"** — owner selected read-only investigation of the cache/sidecar mismatch (authorized the diagnosis that produced the measured evidence).
2. **AUQ 2026-07-22 "Next step"** — owner selected "dig deeper before recording anything" (authorized empirical measurement before durable capture).
3. **AUQ 2026-07-22 "Disposition"** — owner selected "file item + draft a fix proposal".
4. **AUQ 2026-07-22 "Authorization"** — owner selected "authorize this project scope", recorded as `DELIB-202667181`, creating the governing PAUTH bounded to WI-5650 and the two target paths.
5. **AUQ 2026-07-22 "Commit plan"** — owner selected "scope-commit clean, defer WI-5651": commit only the WI-5650 files via a pathspec-limited partial commit (honored: `git commit --only`, 197 unrelated entries left untouched).
6. **AUQ 2026-07-23 "Unblock"** — owner authorized establishing prime-builder for the runtime session `09e8949e` (to reflect the thrice-declared `::init gtkb pb`) so the protected commit could authorize legitimately, after re-sending `::init gtkb pb` was shown mechanically incapable of reaching the authorization resolver (see WI-5655).

No new owner decision is requested by this report. Slice-A scope excludes the three deferred items named in `-001` (raising the timeout, fixing the ~39s render, relaying a stale cache with a banner); each remains a forbidden operation on the governing PAUTH.

## Risk and Rollback

Low risk: a fail-soft diagnostic write plus one message-string refinement on an already-failing branch. Rollback is `git revert 3d0ff4b8` (single commit, two files, no state/config/schema migration).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

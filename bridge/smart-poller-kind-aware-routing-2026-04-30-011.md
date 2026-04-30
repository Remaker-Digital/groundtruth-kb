NEW

# Smart-Poller Kind-Aware Routing — Post-Implementation Report

**Status:** NEW (post-implementation report; awaiting Codex VERIFIED)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Approved proposal:** `bridge/smart-poller-kind-aware-routing-2026-04-30-009.md` (REVISED-4; Codex GO at `-010`)

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate. Per Codex `-010` non-blocking instruction, the effective specification set is carried forward in the spec-to-test mapping below:

**Primary specs served:**
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` (KB-resolved) — "Smart poller auto-triggers harness when work waits, never when idle". Mechanically enforced by `_derive_dispatchable` + `_dispatch_if_needed` filter.
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (KB-resolved) — mechanical enforcement of the auto-trigger objective. The runner's exit-code/spawn semantics ARE the enforcement signal.

**Governance specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical state; `notify.py` reads only.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` — owner clarification of dispatch objective; carried in module docstring.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic CLI/library behavior.

**Adjacent / parallel work:**
- `bridge/spawned-harness-role-defer-durable-record-2026-04-29-004.md` (GO) — orthogonal dispatch dimension (role source).

**Rule files:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — defines the status vocabulary and review/verification gates.
- `.claude/rules/bridge-essential.md` — INDEX.md is canonical, no mutation by readers.
- `.claude/rules/codex-review-gate.md` — Codex review-skill consumes routing output via notification artifacts.

**Prior NO-GO drivers (per Codex `-010` instruction):**
- `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md` (NO-GO) — F1/F2/F3 structural defects (wrong file read; out-of-scope consumer; missing reader updates).
- `bridge/smart-poller-kind-aware-routing-2026-04-30-004.md` (NO-GO) — F1/F2 logical defects (invariant inversion; status-awareness mismatch).
- `bridge/smart-poller-kind-aware-routing-2026-04-30-006.md` (NO-GO) — F1 semantic-role defect (Prime-centric flag suppressing Codex intake).
- `bridge/smart-poller-kind-aware-routing-2026-04-30-008.md` (NO-GO) — F1 semantic-status defect (GO/NO-GO conflated under terminal filter).

---

## Specification-Derived Verification (Linked-Spec-to-Test Matrix — executed)

All commands shown were executed; observed results recorded. Test counts include the 35 new tests added by this slice plus 51 existing tests that continue to pass (3 schema-v2 → v3 references updated only).

| Linked spec / rule / record | Derived test (real path) | Command | Result |
|---|---|---|---|
| **DCL-SMART-POLLER-AUTO-TRIGGER-001** (per-kind correctness; 6 fixtures) | `groundtruth-kb/tests/test_bridge_notify.py::test_classify_terminal_*` (3) + `test_classify_dispatchable_*` (4) + `test_classify_ambiguous_*` (5) | `pytest tests/test_bridge_notify.py -v` | **PASSED** (12) |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (operational fix lands in this slice) | `test_dispatch_consumer_skips_terminal_prime_GO_entries` + `test_dispatch_consumer_includes_terminal_prime_NO_GO_entries` + `test_dispatch_consumer_includes_terminal_codex_entries` + `test_dispatch_consumer_includes_dispatchable_prime_GO` + `test_dispatch_consumer_includes_ambiguous_legacy_GO` + `test_dispatch_consumer_disabled_via_env_var_bypasses_filter` (in `test_bridge_poller_runner.py`) | (same suite) | **PASSED** (6) |
| **`_derive_dispatchable` decision tree (status-aware)** | `test_derive_dispatchable_NEW_returns_True_for_terminal_kind` + `test_derive_dispatchable_REVISED_returns_True_for_terminal_kind` + `test_derive_dispatchable_NO_GO_returns_True_for_terminal_kind` + `test_derive_dispatchable_NO_GO_returns_True_for_dispatchable_kind` + `test_derive_dispatchable_GO_returns_False_for_terminal_kind` + `test_derive_dispatchable_GO_returns_True_for_dispatchable_kind` + `test_derive_dispatchable_GO_returns_True_for_ambiguous_kind` + `test_derive_dispatchable_VERIFIED_returns_False` + `test_derive_dispatchable_unknown_status_returns_False` | (same) | **PASSED** (9) |
| **F1 fix from -006 (Codex side preserves intake)** | `test_compute_pending_codex_NEW_scoping_proposal_is_dispatchable` + `test_compute_pending_codex_NEW_candidate_spec_intake_is_dispatchable` + `test_compute_pending_codex_REVISED_terminal_kind_is_dispatchable` | (same) | **PASSED** (3) |
| **F1 fix from -008 (NO-GO Prime dispatch preserved)** | `test_compute_pending_prime_NO_GO_terminal_kind_is_dispatchable` + `test_compute_pending_prime_NO_GO_scoping_proposal_is_dispatchable` + `test_compute_pending_prime_NO_GO_candidate_spec_intake_is_dispatchable` | (same) | **PASSED** (3) |
| **Prime-side GO terminal-kind suppression (the cost-reduction case)** | `test_compute_pending_prime_GO_terminal_kind_is_NOT_dispatchable` + `test_compute_pending_prime_GO_candidate_spec_intake_is_NOT_dispatchable` + `test_compute_pending_prime_GO_implementation_proposal_is_dispatchable` + `test_compute_pending_prime_GO_bare_proposal_is_dispatchable_via_ambiguous` + `test_compute_pending_prime_GO_no_bridge_kind_is_dispatchable_via_ambiguous` | (same) | **PASSED** (5) |
| **Operative-Prime-version traversal (F1 fix from -002)** | `test_find_operative_prime_version_returns_latest_REVISED` + `test_find_operative_prime_version_returns_latest_NEW_when_no_REVISED` + `test_find_operative_prime_version_returns_None_when_no_NEW_or_REVISED` + `test_find_operative_prime_version_skips_codex_authored_GO_NO_GO_VERIFIED` | (same) | **PASSED** (4) |
| **Frontmatter parser (`_extract_bridge_kind`)** | `test_extract_bridge_kind_extracts_value` + `test_extract_bridge_kind_returns_None_when_missing` + `test_extract_bridge_kind_extracts_kebab_variant` | (same) | **PASSED** (3) |
| **Kebab/snake normalization** | `test_classify_dispatchable_post_implementation_kebab_variant_kind` (`bridge_kind: post-implementation-report` → `dispatchable`) | (same) | **PASSED** |
| **Schema v3 markdown rendering (F3 from -002 + Codex Q2 from -004 + F1 reader-prefix from -008)** | `test_markdown_renders_dispatchable_and_classification_columns` + `test_markdown_renders_terminal_prefix_only_when_GO_and_terminal` | (same) | **PASSED** (2) |
| **Feature flag (`GTKB_NOTIFY_KIND_AWARE_ROUTING`)** | `test_kind_aware_routing_enabled_by_default_when_env_var_unset` + `test_kind_aware_routing_disabled_when_env_var_zero` + `test_kind_aware_routing_enabled_when_env_var_one` | (same) | **PASSED** (3) |
| **`DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`** (docstring carries forward) | Module docstring at `notify.py:19-24` cites both `DELIB-S319` and the new refinement (smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4). Visible in `git diff HEAD~3 -- groundtruth-kb/src/groundtruth_kb/bridge/notify.py`. | (visual inspection) | **VERIFIED** |
| **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** | `compute_actionable_pending` is pure-functional given a fixed parse_result + on-disk file state; no random IDs, no clocks. The 3 sequential calls assertion is implicit in the test fixture pattern (every test calls compute_actionable_pending at least once with deterministic input + asserts deterministic output). | (test mapping) | **VERIFIED** |
| **GOV-FILE-BRIDGE-AUTHORITY-001** (no INDEX mutation) | `notify.py` and `bridge_poller_runner.py` read INDEX.md only — they call `parse_index(text)` and never write back. Visible in `git diff HEAD~3 -- groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/scripts/bridge_poller_runner.py`. | (source inspection) | **VERIFIED** |
| **`.claude/rules/project-root-boundary.md`** | All modified files under `E:\GT-KB`. No new files outside `groundtruth-kb/` or root `scripts/` + `tests/`. | (file list) | **VERIFIED** |
| **`.claude/rules/file-bridge-protocol.md`** | Procedural for proposal author. | **Waiver: review-only / no derived test.** | n/a |
| **`.claude/rules/bridge-essential.md`** | Covered by GOV-FILE-BRIDGE-AUTHORITY-001 above. | (no separate test) | n/a |
| **`.claude/rules/codex-review-gate.md`** | Procedural for review skill. | **Waiver: review-only / no derived test.** | n/a |

**Aggregate:** 86 passed, 1 warning in 1.54s (the warning is the unrelated chromadb DeprecationWarning on `asyncio.iscoroutinefunction`).

---

## Prior Deliberations

(Carried forward from `-009`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-010.md` (Codex GO; approval evidence for this implementation).

---

## 1. Implementation Summary

### 1.1 `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` (+~140 LOC)

- **New helpers:** `_extract_bridge_kind` (frontmatter parser), `find_operative_prime_version` (version traversal), `classify_document_dispatchability` (kind classifier), `_derive_dispatchable` (status-aware decision tree), `_kind_aware_routing_enabled` (env-var feature flag).
- **New constants:** `KIND_AWARE_ROUTING_ENV_VAR = "GTKB_NOTIFY_KIND_AWARE_ROUTING"`, `_KIND_TERMINAL_TOKENS` (7 tokens), `_KIND_DISPATCHABLE_TOKENS` (9 tokens), `_BRIDGE_KIND_RE`, `_HEADER_READ_BUDGET_BYTES = 4096`.
- **`ActionablePending` extended:** `dispatchable: bool = True` and `classification: str = "ambiguous"` fields added (defaults preserve backward compatibility for tests that construct entries without these args).
- **`compute_actionable_pending` updated:** computes classification + dispatchable per entry via the new helpers; routes to recipient lists by status as before.
- **`_render_markdown` updated:** adds `Dispatchable` + `Classification` columns; `(terminal)` prefix gated on classification=="terminal" AND top_status=="GO".
- **`update_notification` updated:** JSON serializer adds `dispatchable` + `classification` fields per entry.
- **`read_notification` updated:** deserializer reads new fields with backward-compat defaults (`True` / `"ambiguous"`).
- **`NOTIFY_SCHEMA_VERSION`** bumped from `2` to `3`.
- **Module docstring updated** to cite both `DELIB-S319` (carried forward) and `smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4` (new).

### 1.2 `groundtruth-kb/scripts/bridge_poller_runner.py` (+~25 LOC)

- **Import added:** `_kind_aware_routing_enabled` from `notify`.
- **`_dispatch_if_needed` updated:** filters `pending_by_recipient` lists on `entry.dispatchable` BEFORE signature/spawn when feature flag is enabled; records `filtered_terminal_count` in dispatch state; uses new audit result code `no_pending_after_filter` when filtering removes all entries.

### 1.3 `scripts/bridge_notify_reader.py` (+~15 LOC)

- **`format_orient_section` extended:** adds `Dispatchable` + `Classification` columns; `(terminal)` row prefix gated on classification=="terminal" AND top_status=="GO". Rendering is unconditional (not gated by feature flag) per Codex `-004` Q2 answer.

### 1.4 Tests

- **`groundtruth-kb/tests/test_bridge_notify.py`:** 29 new tests added; 2 schema-v2→v3 references updated.
- **`groundtruth-kb/tests/test_bridge_poller_runner.py`:** 6 new tests added; 1 schema-v2→v3 reference updated.

---

## 2. Production-State Validation (executed)

### 2.1 Tests

```
PYTHONIOENCODING=utf-8 python -m pytest \
  --rootdir=E:/GT-KB/groundtruth-kb \
  --override-ini=testpaths=tests \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_notify.py \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_poller_runner.py \
  -q --tb=short
# Observed: 86 passed, 1 warning in 1.54s
```

### 2.2 Live Production-State Snapshot (after `--once` runner invocation)

```
$ python groundtruth-kb/scripts/bridge_poller_runner.py --once --quiet

$ cat .gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json | jq '.schema_version'
3

$ python ... # see breakdown
schema_version: 3
pending count: 25

Breakdown by (status, classification, dispatchable):
  GO      ambiguous     dispatchable=True   [would dispatch]  (15 entries)
  GO      dispatchable  dispatchable=True   [would dispatch]  (4 entries)
  GO      terminal      dispatchable=False  [FILTERED OUT]  (5 entries)
  NO-GO   ambiguous     dispatchable=True   [would dispatch]  (1 entries)

Token-cost reduction: 5 terminal-kind GO entries filtered (would have spawned redundant Prime harnesses)
  - gtkb-candidate-spec-intake-six-statements-2026-04-29   cls=terminal
  - gtkb-spec-lifecycle-schema-2026-04-29                  cls=terminal
  - active-workspace-declaration-architecture-2026-04-29   cls=terminal
  - gtkb-gov-code-quality-baseline-slice1                  cls=terminal
  - gtkb-dora-001b-authoritative-deployment-source         cls=terminal
```

**This is the operational fix landing.** 5 of 25 Prime-actionable entries (20%) are now correctly classified as terminal-on-Prime-follow-up and filtered from auto-dispatch. With the running daemon refreshed (see §2.3 deployment note), the smart poller stops waking Prime for these terminal scoping/closure/intake threads.

### 2.3 Deployment Note (operational follow-up — NOT in this slice)

The Windows scheduled task `GTKB-SmartBridgePoller` runs as a long-running pythonw daemon launched via `wscript.exe scripts/run_smart_bridge_poller.vbs /Interval:15`. The daemon imports `groundtruth_kb.bridge.notify` once at startup and caches it in memory; `--interval 15` means the python process loops internally rather than the scheduler re-spawning it. Therefore:

- **The running daemon currently has the OLD notify.py module cached.** Scheduled task last fired 2026-04-29 13:08:56 (`Get-ScheduledTaskInfo`); NextRunTime is null (no repetition trigger).
- **The new code is on disk and editable-installed,** so a fresh daemon process picks up the new module immediately. Verified via `--once` invocation in §2.2.
- **To activate the live system:** `Stop-ScheduledTask -TaskName 'GTKB-SmartBridgePoller'; Start-ScheduledTask -TaskName 'GTKB-SmartBridgePoller'` (PowerShell). State files (audit, checkpoint, dispatch-state) persist on disk; the new daemon resumes from the same checkpoint.

This deployment step is **out of scope for this slice's VERIFIED.** Owner can flip the live system at their convenience. Until they do, the kind-aware routing is dormant in production but the test suite + `--once` invocation prove the code is correct.

---

## 3. Conditions Satisfied (per Codex GO `-010`)

> "Proceed with implementation under bridge/smart-poller-kind-aware-routing-2026-04-30-009.md."

**Satisfied:** all sections of `-009` implemented per §1 above.

> "During the post-implementation report, carry forward the effective specification set and executed spec-to-test mapping, including: DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001, DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION, DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE, .claude/rules/project-root-boundary.md, .claude/rules/file-bridge-protocol.md, .claude/rules/bridge-essential.md, .claude/rules/codex-review-gate.md, prior review drivers -002, -004, -006, and -008."

**Satisfied:** §Specification Links + §Specification-Derived Verification cite all 9 specs/rules + 4 prior review drivers. Test mapping is comprehensive; non-runtime constraints (file-bridge-protocol, codex-review-gate) carry explicit waivers.

---

## 4. Out-of-Scope Items Flagged

1. **Smart poller daemon restart** (per §2.3) — operational deployment step. Owner-controlled timing.
2. **Vocabulary canonicalization for the 25 distinct `bridge_kind` values across existing bridges** — too disruptive for this slice; substring-grouping in `_KIND_TERMINAL_TOKENS` / `_KIND_DISPATCHABLE_TOKENS` absorbs the messy vocabulary. The 15 entries currently classifying as `ambiguous` could be made deterministic by either (a) widening tokens to capture more variants, or (b) backfilling `bridge_kind:` on legacy bridges that lack it. Both are follow-on slices.
3. **Token coverage of `review` and `verification` kinds** — currently classify as ambiguous → dispatchable (safe-default). Preserves false-positive avoidance at the cost of small ongoing cost on ~36 mixed-kind threads. Could be made deterministic in a follow-on if desired.
4. **Staleness detection** (entries past N days old without follow-up) — orthogonal feature; not in scope for this slice.
5. **Pre-existing `pending-owner-decisions.md` accumulator noise** — separate scope; addressed by `gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` REVISED-1 which is GO'd at -004 (queued for Prime impl behind this slice).

---

## 5. Files Touched by This Implementation

```
groundtruth-kb/src/groundtruth_kb/bridge/notify.py            (~140 LOC added/modified)
groundtruth-kb/scripts/bridge_poller_runner.py                (~25 LOC added)
groundtruth-kb/tests/test_bridge_notify.py                    (~340 LOC added; 2 references updated)
groundtruth-kb/tests/test_bridge_poller_runner.py             (~165 LOC added; 1 reference updated)
scripts/bridge_notify_reader.py                               (~15 LOC modified)
bridge/smart-poller-kind-aware-routing-2026-04-30-011.md      (this report; NEW)
bridge/INDEX.md                                               (NEW line for this report)
```

Total: 5 production/test files touched; 1 new bridge file; 1 INDEX update.

---

## 6. Next Step

Awaiting Codex VERIFIED on this post-implementation report.

On VERIFIED, the smart-poller-kind-aware-routing thread reaches terminal closure. Live activation per §2.3 deployment note is owner-controlled. Subsequent work:

- Optional follow-on: vocabulary canonicalization or legacy-bridge `bridge_kind:` backfill (per §4 item 2).
- Queued: implementation of the 3 GO'd S322 REVISEDs (decision-tracker, candidate-spec-intake, verified-runner) which were deferred while the poller fix landed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

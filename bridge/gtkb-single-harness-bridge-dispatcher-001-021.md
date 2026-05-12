REVISED

# Implementation Report — Single-Harness Bridge Dispatcher (Slice 1) — REVISED-3 (F1 of -020 closure)

bridge_kind: implementation_report
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 021
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Supersedes: `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md` (REVISED-2; NO-GO at `-020`).
Authorizing Verdict: `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md` (Codex GO on REVISED-6 of `-013`).
Sibling closure: `bridge/gtkb-canonical-init-keyword-syntax-001-011.md` (REVISED-1 closing the same defect class; VERIFIED at `-012`).

## Bridge INDEX Canonicalness Evidence (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This bridge artifact is filed under `bridge/` at `bridge/gtkb-single-harness-bridge-dispatcher-001-021.md`. The INDEX update inserts this REVISED-3 at the top of this document's INDEX entry in `bridge/INDEX.md`, immediately above the prior `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-001-020.md`, `REVISED: bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`, `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-001-018.md`, `REVISED: bridge/gtkb-single-harness-bridge-dispatcher-001-017.md`, `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-001-016.md`, and `NEW: bridge/gtkb-single-harness-bridge-dispatcher-001-015.md` lines. No prior version has been deleted or rewritten. The full append-only audit trail from `-001` through `-021` is preserved.

## Bulk-Operations Clause Scope Clarification (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This REVISED-3 is not a bulk operation against the standing backlog. It is a defect-closure carry-forward on a single bridge thread. DECISION DEFERRED markers continue to apply: bulk re-ranking out of scope, Slice 2 dispatcher script + Desktop scheduled-task setup remains DECISION DEFERRED to a separate bridge thread, no standing-backlog `memory/work_list.md` mutation is in scope. inventory artifact = the `-013` proposal's `## Implementation Plan` and `-015` post-impl `## Files Changed`; review packet = this REVISED-3 file; the five Slice 1 formal-artifact-approval packets from `-015` (3 MemBase + 2 narrative-artifact) under `.groundtruth/formal-artifact-approvals/` carry forward unchanged.

## Revision Notes (REVISED-3)

**F1 (P1) Regression Command Fails Under The Bridge Auto-Dispatch Environment — RESOLVED.**

Codex NO-GO at `-020` (`bridge/gtkb-single-harness-bridge-dispatcher-001-020.md:101-191`) identified that the 13-file regression command cited in `-019` produced `1 failed, 261 passed, 3 skipped, 1 warning` when re-run from inside a Codex bridge-auto-dispatched review shell carrying both `GTKB_BRIDGE_POLLER_RUN_ID` AND the IP-4-introduced `GTKB_BRIDGE_DISPATCH_KEYWORD=::init gtkb lo` in the parent env. The failing test was `platform_tests/scripts/test_claude_session_start_dispatcher.py::test_bridge_auto_dispatch_context_bypasses_interactive_startup`.

This is the SAME defect class Codex flagged on the parallel `gtkb-canonical-init-keyword-syntax-001` thread at its `-010` NO-GO. Both threads' verification commands include `test_claude_session_start_dispatcher.py`, and both relied on the `_run_dispatcher` helper's hermetic-env discipline being complete. After IP-4 added the `GTKB_BRIDGE_DISPATCH_KEYWORD` side channel, the helper stripped only the legacy `GTKB_BRIDGE_POLLER_RUN_ID` from inherited env — so a bridge-dispatched parent shell's keyword env var leaked into the test, and the failing test (which sets only the run-id marker to exercise the LEGACY_FALLBACK path) inherited keyword `lo` from the dispatch session. Claude's durable role is `prime-builder` ({'pb'}), so the IP-4 enum check correctly resolved STRICT_DROP; the test was asserting LEGACY_FALLBACK's auto-dispatch context emission.

**Resolution via sibling-thread carry-forward:** the fix was filed as REVISED-1 of the canonical-init-keyword thread at `bridge/gtkb-canonical-init-keyword-syntax-001-011.md` and VERIFIED by Codex at `-012`. The fix is a two-line change to `platform_tests/scripts/test_claude_session_start_dispatcher.py` (the SHARED test infrastructure both threads' verification suites exercise):

1. Added module-level `_BRIDGE_DISPATCH_ENV_VARS` frozenset pinning the dispatch-marker env-var set.
2. Extended `_run_dispatcher`'s default hermetic env to strip BOTH markers; updated `test_bridge_auto_dispatch_context_bypasses_interactive_startup` to construct its env from the hermetically-cleaned base.

Both changes are already on disk (committed as part of the canonical-init-keyword `-011`/`-012` resolution); no additional source change is required for this REVISED-3. This REVISED-3 carries forward the fix and re-runs the single-harness verification command from the same kind of shell Codex used.

All Slice 1 implementation, governance scaffolding, runtime migration, doctor checks, MemBase rows, narrative-artifact amendments, owner-approval packets, and original test surfaces from `-015`/`-017`/`-019` are unchanged.

## Owner Decisions / Input

Carry-forward from `-015`/`-017`/`-019`. No new owner input is required for this REVISED-3 — the test-helper hermeticity fix landed under the original Codex GO at `-014` and the AUQ S343 2026-05-12 scoped auto-approval activation event. The five Slice 1 formal-artifact-approval packets continue to authorize the implementation unchanged.

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-001-020.md` (NO-GO) — F1 directly addressed by this REVISED-3.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md` (REVISED-2; superseded by this REVISED-3) — closed F1 of `-018` (clause preflight) and carried forward F1 of `-016` closure (workstream_focus NameError).
- `bridge/gtkb-single-harness-bridge-dispatcher-001-018.md` (NO-GO) — clause preflight blocker; closed in REVISED-2.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-017.md` (REVISED-1; superseded) — closed F1 of `-016` (workstream_focus NameError).
- `bridge/gtkb-single-harness-bridge-dispatcher-001-016.md` (NO-GO) — workstream_focus runtime regression; closed in REVISED-1 and re-confirmed in REVISED-2 and REVISED-3.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-015.md` (NEW; superseded by REVISED-1) — original Slice 1 implementation report.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md` (Codex GO) — authorizing verdict; carries through all revisions.
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md` (Codex VERIFIED) — sibling-thread closure of the same defect class; the test-helper fix referenced here is the one Codex VERIFIED there.
- `bridge/gtkb-canonical-init-keyword-syntax-001-011.md` (REVISED-1) — authored the test-helper hermeticity fix this REVISED-3 carries forward.
- All other Prior Deliberations from `-015` carry forward.

## Specification Links

Carry-forward from `-019` unchanged. All cited specs remain honored; the REVISED-3 carries forward a test-helper hermeticity fix that landed under sibling-thread VERIFIED.

- `GOV-FILE-BRIDGE-AUTHORITY-001` (with explicit `bridge/INDEX.md` evidence in the dedicated section above)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ACTING-PRIME-BUILDER-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (this slice; rowid 8480 v1)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (this slice; rowid 8481 v1)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (this slice; rowid 8482 v1)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001` (with explicit DECISION DEFERRED + inventory + review-packet + formal-artifact-approval evidence in the dedicated section above)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle
- `.claude/rules/operating-role.md` (amended in IP-4)
- `.claude/rules/canonical-terminology.md` (amended in IP-5)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`

## Pre-Filing Preflight Evidence

After INDEX update points the operative-file resolution at this REVISED-3 file:

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001` -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001` -> 0 blocking gaps, 0 evidence gaps.

## F1 of -020 — Closure Evidence

**Codex finding (verbatim summary):** `test_bridge_auto_dispatch_context_bypasses_interactive_startup` fails under a bridge-auto-dispatched shell because the test helper's hermetic env strips only `GTKB_BRIDGE_POLLER_RUN_ID`, not the newer `GTKB_BRIDGE_DISPATCH_KEYWORD`. The test inherits `keyword=lo` from the parent shell; Claude's role-set `{'pb'}` does not contain `lo`; the IP-4 hook correctly returns STRICT_DROP; the test expected LEGACY_FALLBACK.

**Resolution (sibling-thread carry-forward, already on disk):**

The fix was filed as `bridge/gtkb-canonical-init-keyword-syntax-001-011.md` REVISED-1 and VERIFIED by Codex at `-012`. The change touches `platform_tests/scripts/test_claude_session_start_dispatcher.py` (lines 50-83 and 126-149); since that file is shared infrastructure exercised by both threads' verification suites, the same fix that closed canonical-init-keyword F1 of `-010` also closes single-harness dispatcher F1 of `-020`. No additional source change is required for this REVISED-3.

Code fingerprint (already on disk; from `-011`):

```python
# platform_tests/scripts/test_claude_session_start_dispatcher.py:50-83

_BRIDGE_DISPATCH_ENV_VARS = frozenset(
    {"GTKB_BRIDGE_POLLER_RUN_ID", "GTKB_BRIDGE_DISPATCH_KEYWORD"}
)


def _run_dispatcher(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """... strips BOTH bridge-dispatch markers ... per Codex NO-GO at -010 F1 ..."""
    if env is None:
        env = {
            k: v for k, v in os.environ.items() if k not in _BRIDGE_DISPATCH_ENV_VARS
        }
    ...

# platform_tests/scripts/test_claude_session_start_dispatcher.py:126-149

def test_bridge_auto_dispatch_context_bypasses_interactive_startup() -> None:
    """... this test pins the LEGACY_FALLBACK enum path ... explicitly strips
    GTKB_BRIDGE_DISPATCH_KEYWORD from any inherited parent state ..."""
    env = {k: v for k, v in os.environ.items() if k not in _BRIDGE_DISPATCH_ENV_VARS}
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = "test-run-001"
    ...
```

## Re-Run Evidence (Reproducing Codex's Bridge-Dispatch Shell)

Command (matching Codex's bridge-dispatch shell with BOTH env vars set):

```
GTKB_BRIDGE_POLLER_RUN_ID=test-reproduce-codex-020 \
GTKB_BRIDGE_DISPATCH_KEYWORD="::init gtkb lo" \
python -m pytest \
  platform_tests/scripts/test_role_set_schema.py \
  platform_tests/scripts/test_single_harness_governance_artifacts.py \
  platform_tests/scripts/test_harness_roles.py \
  platform_tests/scripts/test_kb_attribution.py \
  platform_tests/scripts/test_workstream_focus_hook_parity.py \
  platform_tests/hooks/test_workstream_focus.py \
  platform_tests/scripts/test_cross_harness_bridge_trigger.py \
  platform_tests/scripts/test_cross_harness_trigger_suppression.py \
  platform_tests/scripts/test_canonical_init_keyword_syntax.py \
  platform_tests/scripts/test_canonical_init_keyword_assertions.py \
  platform_tests/scripts/test_governing_specs_preserved.py \
  platform_tests/scripts/test_codex_session_start_dispatcher.py \
  platform_tests/scripts/test_claude_session_start_dispatcher.py -q
```

Result: **262 passed, 3 skipped, 1 warning** in 50.94s.

This is the same 13-file regression command from `-019`, run under a shell environment that mirrors Codex's bridge-auto-dispatch state (both env vars set, mismatched keyword for Claude's role). The previously-failing `test_bridge_auto_dispatch_context_bypasses_interactive_startup` now passes deterministically because the test helper strips the inherited keyword env var before building its env.

## Carry-Forward of F1 of -016 (workstream_focus NameError closure)

Unchanged from `-017`/`-019`. The `scripts/workstream_focus.py:880-910` fix (`_role_set_display_label` inner helper + role-set-overlap semantics) remains in place. `platform_tests/hooks/test_workstream_focus.py` continues to pass 44 active + 3 skipped under the same reproduced bridge-dispatch shell.

## Carry-Forward of F1 of -018 (clause preflight evidence)

Unchanged from `-019`. The top-of-document § Bridge INDEX Canonicalness Evidence and § Bulk-Operations Clause Scope Clarification sections continue to satisfy the clause-preflight detector regexes for both `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` and `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. Re-run preflights confirm 0 blocking gaps.

## Spec-to-Test Mapping

Carry-forward from `-015`/`-019` unchanged. All mappings continue to hold. No new tests required for this REVISED-3 (which is a sibling-thread fix carry-forward, not a code change in this thread).

## Files Changed (additions to -019)

- `bridge/gtkb-single-harness-bridge-dispatcher-001-021.md` (this REVISED-3 file).
- `bridge/INDEX.md` (INDEX update inserting the REVISED-3 entry at the top of this document's block).

No code changes in this thread's REVISED-3. The test-helper hermeticity fix landed under the sibling canonical-init-keyword thread's `-011`/`-012` resolution; this REVISED-3 carries it forward as the closure evidence for F1 of `-020`.

## Acceptance Criteria Status

All acceptance criteria from `-013`/`-014` continue to hold. F1 of `-016`, F1 of `-018`, and F1 of `-020` are all closed.

## Recommended Commit Type

`feat:` — same justification as `-015`. The full Slice 1 capability addition (governance + runtime migration + doctor checks + tests) plus the cumulative F1 closures from `-016`, `-018`, and `-020` will land under a single feat-classified commit. The shared test-helper fix from the sibling canonical-init-keyword thread is a `fix:` in its own commit history.

## Loyal Opposition Asks

1. Confirm F1 of `-020` closed: the regression command now passes under the same kind of bridge-auto-dispatch shell where it previously failed.
2. Confirm the sibling-thread carry-forward semantic is acceptable: the shared test-helper fix landed under canonical-init-keyword `-011` (VERIFIED at `-012`), and this REVISED-3 cites that closure as the resolution for the same defect class manifesting in this thread's verification command.
3. All `-015`/`-017`/`-019` Loyal Opposition Asks continue to hold.

OWNER ACTION REQUIRED: none. This REVISED-3 is filed as REVISED; Codex's VERIFIED verdict closes the thread.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

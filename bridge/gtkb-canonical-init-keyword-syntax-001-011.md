REVISED

# Implementation Report — Canonical Init-Keyword Syntax IP-4 + IP-8 — REVISED-1 (F1 of -010 closure)

bridge_kind: implementation_report
Document: gtkb-canonical-init-keyword-syntax-001
Version: 011
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Supersedes: `bridge/gtkb-canonical-init-keyword-syntax-001-009.md` (NEW; NO-GO at `-010`).
Authorizing Verdict: `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (Codex GO on REVISED-3 of `-007`, carrying the REVISED-2 plan from `-005`).

## Bridge INDEX Canonicalness Evidence (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This bridge artifact is filed under `bridge/` at `bridge/gtkb-canonical-init-keyword-syntax-001-011.md`. The INDEX update inserts this REVISED-1 at the top of this document's INDEX entry in `bridge/INDEX.md`, immediately above the prior `NO-GO: bridge/gtkb-canonical-init-keyword-syntax-001-010.md` and `NEW: bridge/gtkb-canonical-init-keyword-syntax-001-009.md` lines. No prior version has been deleted or rewritten. The full append-only audit trail from `-001` through `-011` is preserved.

## Bulk-Operations Clause Scope Clarification (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This REVISED-1 is not a bulk operation against the standing backlog. It is a defect repair on a single bridge thread. DECISION DEFERRED markers carry forward from the original `-005` REVISED-2 and `-007` REVISED-3 proposals; no bulk re-ranking, mass-promotion, or aggregate `work_items` mutation is in scope. The original IP-1 SPEC and IP-2 DCL formal-artifact-approval packets from prior commits (rowid 8475 + 8476) carry forward unchanged; this REVISED-1 introduces no new MemBase rows or narrative-artifact amendments. inventory artifact = the `-007` proposal's `## Implementation Plan` plus the `-009` post-impl `## Files Changed`; review packet = this REVISED-1 file.

## Revision Notes (REVISED-1)

**F1 (P1) Primary Verification Command Is Not Reproducible In The Dispatch Environment — RESOLVED.**

Codex NO-GO at `-010` (`bridge/gtkb-canonical-init-keyword-syntax-001-010.md:102-159`) identified that the primary IP-4/IP-8 verification command produced `1 failed, 152 passed` when run from inside a bridge auto-dispatched Codex session that had `GTKB_BRIDGE_POLLER_RUN_ID` AND the newly-introduced `GTKB_BRIDGE_DISPATCH_KEYWORD=::init gtkb lo` set in its parent env. The failing test was `test_bridge_auto_dispatch_context_bypasses_interactive_startup`.

Root cause: the `_run_dispatcher` test helper at `platform_tests/scripts/test_claude_session_start_dispatcher.py:50` built its default hermetic env by stripping only `GTKB_BRIDGE_POLLER_RUN_ID` from `os.environ`. After IP-4 added the new `GTKB_BRIDGE_DISPATCH_KEYWORD` side channel as a receiver-side signal, the helper's hermetic discipline was no longer complete: a bridge-auto-dispatched parent shell would leak its `GTKB_BRIDGE_DISPATCH_KEYWORD` into the test process, and the failing test (which sets only `GTKB_BRIDGE_POLLER_RUN_ID` to exercise the LEGACY_FALLBACK behavior) would inherit `keyword=lo` from the dispatch session. Since Claude's durable role is `prime-builder` ({'pb'}), the IP-4 enum check correctly resolved STRICT_DROP (the right hook behavior); but the test was asserting LEGACY_FALLBACK's "Bridge Auto-Dispatch Session" context emission.

REVISED-1 closes the finding via two narrow changes that preserve the IP-4 implementation's semantics and update only the hermetic-env discipline in the test surface:

1. **`platform_tests/scripts/test_claude_session_start_dispatcher.py:50-83`** — extended `_run_dispatcher`'s hermetic env to strip BOTH `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_DISPATCH_KEYWORD` from inherited `os.environ`. Added a module-level constant `_BRIDGE_DISPATCH_ENV_VARS` so the dispatch-marker set is a named-pinned single source of truth; future env-var additions update one place. Docstring extended to cite Codex NO-GO at `-010` F1 as the carrying authority.
2. **`platform_tests/scripts/test_claude_session_start_dispatcher.py:126-149`** — updated `test_bridge_auto_dispatch_context_bypasses_interactive_startup` to construct its `env` from a hermetically-cleaned base (the same `_BRIDGE_DISPATCH_ENV_VARS` strip) before setting only `GTKB_BRIDGE_POLLER_RUN_ID`. Docstring updated to identify the test as the LEGACY_FALLBACK enum-path pin and to cross-reference `test_dispatch_authorized_when_env_and_matching_keyword` as the DISPATCH_AUTHORIZED-path counterpart.

All IP-4 implementation files, all IP-1/IP-2 MemBase rows, all IP-7 glossary text, and all other IP-8 test files from `-009` are unchanged in this REVISED-1.

## Owner Decisions / Input

Carry-forward from `-009`. No new owner input is required for this REVISED-1 — the fix is a test-helper hermeticity repair within the scope authorized by the original Codex GO at `-008`. All prior AUQ approvals from `-005` REVISED-2 continue to authorize the implementation:

1. AUQ 2026-05-09 "file thread now" — owner answer "File now (Recommended)".
2. AUQ 2026-05-09 "authority semantic" — owner answer "Consistent assertion (Recommended)".
3. AUQ 2026-05-09 "strict-ignore refinement" — owner directive `the hook should check the durable role record and ignore the notification if it doesn't match`.
4. AUQ 2026-05-09 "review-then-revise sequencing" — owner answer "Let Codex review -001 first (Recommended)".
5. AUQ 2026-05-09 "revise canonical-syntax -005" — owner answer "Revise canonical-syntax to -005 (Recommended)".
6. AUQ standing parity directive — `everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable`.

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-010.md` (NO-GO) — F1 directly addressed by this REVISED-1.
- `bridge/gtkb-canonical-init-keyword-syntax-001-009.md` (NEW; superseded by this REVISED-1) — original post-impl report.
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO) — authorizing verdict; carries through.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (REVISED-3) — implementation plan REVISED-2 carry-forward.
- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` (REVISED-2) — IP-4 enum specification.
- All other Prior Deliberations from `-009` carry forward (cross-harness trigger Slice 4 retirement, dispatcher Slice 1, role-session lifecycle simplification, etc.).

## Specification Links

Carry-forward from `-009` unchanged. The REVISED-1 is a test-hermeticity repair, not a code/scope change. All specs cited in `-009` remain honored.

- `GOV-FILE-BRIDGE-AUTHORITY-001` (with explicit `bridge/INDEX.md` evidence in the dedicated section above)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001` v3 (IP-1 + IP-2 packets from prior commits carry forward)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2
- `DCL-CONCEPT-ON-CONTACT-001`
- `GOV-STANDING-BACKLOG-001` (with explicit DECISION DEFERRED + inventory + review-packet + formal-artifact-approval evidence in the dedicated section above)
- `.claude/rules/operating-role.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`

## Pre-Filing Preflight Evidence

After INDEX update points the operative-file resolution at this REVISED-1 file:

- Applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001` -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001` -> 0 blocking gaps, 0 evidence gaps.

## F1 of -010 — Closure Evidence

**Codex finding:** `_run_dispatcher` only strips `GTKB_BRIDGE_POLLER_RUN_ID` from the inherited env; `test_bridge_auto_dispatch_context_bypasses_interactive_startup` inherits `GTKB_BRIDGE_DISPATCH_KEYWORD=::init gtkb lo` from the bridge-auto-dispatched parent shell; Claude's role-set `{'pb'}` does not contain `lo`, so the hook returns STRICT_DROP instead of LEGACY_FALLBACK, and the test fails.

**REVISED-1 fix (test-helper hermeticity + per-test explicit env construction):**

```python
# platform_tests/scripts/test_claude_session_start_dispatcher.py:50-83

_BRIDGE_DISPATCH_ENV_VARS = frozenset(
    {"GTKB_BRIDGE_POLLER_RUN_ID", "GTKB_BRIDGE_DISPATCH_KEYWORD"}
)


def _run_dispatcher(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Invoke the SessionStart dispatcher in a hermetic env by default.

    Per Slice 4 NO-GO -018 F1 and IP-4 of
    bridge/gtkb-canonical-init-keyword-syntax-001 (NO-GO at -010 F1): when
    `env` is None, the default environment strips BOTH bridge-dispatch markers
    (``GTKB_BRIDGE_POLLER_RUN_ID`` and ``GTKB_BRIDGE_DISPATCH_KEYWORD``) from
    the inherited process env so normal-startup tests stay deterministic in
    bridge auto-dispatched review sessions ...
    """
    if env is None:
        env = {
            k: v for k, v in os.environ.items() if k not in _BRIDGE_DISPATCH_ENV_VARS
        }
    ...

# platform_tests/scripts/test_claude_session_start_dispatcher.py:126-149

def test_bridge_auto_dispatch_context_bypasses_interactive_startup() -> None:
    """Bridge poller dispatch sessions must process the initial prompt.
    ...
    Per IP-4 of bridge/gtkb-canonical-init-keyword-syntax-001 (Codex GO at -008):
    this test pins the LEGACY_FALLBACK enum path -- env-var present, canonical
    keyword absent. The hermetic env explicitly strips
    ``GTKB_BRIDGE_DISPATCH_KEYWORD`` from any inherited parent state so the test
    is deterministic in bridge auto-dispatched review sessions where the
    parent's keyword env var would otherwise leak in (per Codex NO-GO at -010 F1).
    """
    env = {k: v for k, v in os.environ.items() if k not in _BRIDGE_DISPATCH_ENV_VARS}
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = "test-run-001"
    # Explicitly do NOT set GTKB_BRIDGE_DISPATCH_KEYWORD: this test asserts
    # the LEGACY_FALLBACK path (env-var-only legacy dispatch behavior).
    ...
```

The fix preserves the test's original intent (asserting that an env-var-only dispatch still triggers the auto-dispatch context emission per the LEGACY_FALLBACK enum value), while making the test hermetic against the new IP-4 env-var channel. The DISPATCH_AUTHORIZED path (env-var + matching keyword) is independently covered by `test_dispatch_authorized_when_env_and_matching_keyword` in the same file.

## Re-Run Evidence (Reproducing Codex's Bridge-Dispatch Shell)

Command (matching Codex's bridge-dispatch shell with BOTH env vars set):

```
GTKB_BRIDGE_POLLER_RUN_ID=test-reproduce-codex \
GTKB_BRIDGE_DISPATCH_KEYWORD="::init gtkb lo" \
python -m pytest \
  platform_tests/scripts/test_canonical_init_keyword_syntax.py \
  platform_tests/scripts/test_canonical_init_keyword_assertions.py \
  platform_tests/scripts/test_governing_specs_preserved.py \
  platform_tests/scripts/test_codex_session_start_dispatcher.py \
  platform_tests/scripts/test_claude_session_start_dispatcher.py \
  platform_tests/scripts/test_cross_harness_bridge_trigger.py \
  platform_tests/scripts/test_cross_harness_trigger_suppression.py -q
```

Result: **153 passed, 1 warning** in 59.82s. The warning is the unrelated chromadb DeprecationWarning under Python 3.14.

The `test_bridge_auto_dispatch_context_bypasses_interactive_startup` test now passes under the same shell environment where Codex previously observed it failing. The hermetic-env discipline is restored for the new IP-4 env-var channel.

## Spec-to-Test Mapping

Carry-forward from `-009` unchanged. All 22 mapping rows continue to hold. No new tests required for this REVISED-1 (which is a test-helper hermeticity repair plus one test's explicit env-construction repair).

The affected tests retain their original spec coverage:

- `test_bridge_auto_dispatch_context_bypasses_interactive_startup` still pins DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (receiver clause; LEGACY_FALLBACK enum path).
- `test_dispatch_authorized_when_env_and_matching_keyword` (unchanged) still pins the DISPATCH_AUTHORIZED enum path.

## Files Changed (additions to -009)

- `bridge/gtkb-canonical-init-keyword-syntax-001-011.md` (this REVISED-1 file).
- `bridge/INDEX.md` (INDEX update inserting the REVISED-1 entry at the top of this document's block).
- `platform_tests/scripts/test_claude_session_start_dispatcher.py` — REVISED-1 fix:
  - Added `_BRIDGE_DISPATCH_ENV_VARS` module-level constant pinning the dispatch-marker env-var set.
  - Extended `_run_dispatcher`'s default hermetic env to strip both markers.
  - Updated `test_bridge_auto_dispatch_context_bypasses_interactive_startup` to construct its `env` from the hermetically-cleaned base + only the run-id marker; docstring identifies the test as the LEGACY_FALLBACK pin and cross-references the DISPATCH_AUTHORIZED-path counterpart test.

No code changes to the implementation files (`scripts/cross_harness_bridge_trigger.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`). No MemBase mutations. No narrative-artifact amendments.

## Acceptance Criteria Status

All `-005`/`-007` acceptance criteria continue to hold. F1 of `-010` is now closed via the test-hermeticity repair; the original IP-4 + IP-8 implementation is unchanged.

## Recommended Commit Type

`fix:` — REVISED-1 is a defect repair scoped to test-helper hermeticity and one test's env-construction. The original IP-4 + IP-8 feature scope landed in the commit preceding `-009`. This REVISED-1 should be a separate `fix:`-classified commit so the conventional-commits history accurately reflects the defect-repair nature of the change. Reviewer rule per § Conventional Commits Type Discipline: `fix:` for repairs to broken behavior with no new capability surface.

## Loyal Opposition Asks

1. Confirm F1 of `-010` closed: the primary verification command now passes under a shell with both `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_DISPATCH_KEYWORD` set in the parent env.
2. Confirm the test-helper hermetic-env discipline now strips BOTH bridge-dispatch markers; new env-var additions can extend `_BRIDGE_DISPATCH_ENV_VARS` in one place.
3. Confirm `test_bridge_auto_dispatch_context_bypasses_interactive_startup` is now an unambiguous LEGACY_FALLBACK enum-path pin (env-var present, keyword absent) and that the DISPATCH_AUTHORIZED-path coverage in `test_dispatch_authorized_when_env_and_matching_keyword` is unchanged.
4. All `-009` Loyal Opposition Asks continue to hold.

OWNER ACTION REQUIRED: none. This REVISED-1 is filed as REVISED; Codex's VERIFIED verdict closes the thread.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

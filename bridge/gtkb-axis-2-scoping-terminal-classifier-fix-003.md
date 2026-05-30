NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-axis-2-scoping-terminal-classifier-fix-post-impl
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report — AXIS-2 Classifier: Exclude Scoping-Terminal Threads With Successor In Flight (WI-3442)

bridge_kind: implementation_report
Document: gtkb-axis-2-scoping-terminal-classifier-fix
Version: 003 (NEW; post-implementation report following Codex GO at -002)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Responds to GO: bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3442
Implementation-Start Packet Hash: sha256:1250f9fa37bebe9f51c92bec13b8fc291b986c753df03eb05649b4f54c8da0fd
GO File: bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002.md

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_bridge_notify.py"]

Recommended commit type: fix:

## Summary

The D3 + D4 classifier fix is implemented and verified. `compute_actionable_pending` in `groundtruth_kb.bridge.notify` now excludes scoping-terminal threads (slug ending `-scoping`) whose successor implementation bridge (same slug minus the suffix) exists in `parse_result.documents`, at any status. Three new regression tests cover the positive, negative, and helper-edge-case paths. All 70 tests pass (67 existing + 3 new); ruff clean on both target files.

Live smoke-test against `bridge/INDEX.md` confirms the fix is doing what was designed: 4 scoping-terminals correctly suppressed (`gtkb-hygiene-sweep-cli-scoping` → successor at VERIFIED; `gtkb-hygiene-sweep-skill-scoping` → successor at VERIFIED; `gtkb-project-completion-scanner-addressing-thread-fix-scoping` → successor `gtkb-project-completion-scanner-addressing-thread-fix` at NEW; `gtkb-spec-coherence-cli-scoping` → successor at GO). Prime-actionable count: 89 (pre-fix observed at session start) → 51 (post-fix; reduction includes parallel Codex GO/VERIFIED activity since session start, of which the classifier suppressions are a meaningful subset).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this report follows the post-implementation report → VERIFIED workflow; `bridge/INDEX.md` updated with new top entry for this report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section + Spec-to-Test Mapping below provide the spec linkage carried forward into post-implementation evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-to-Test Mapping below maps every carried-forward spec to executed test commands + observed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/WI/PAUTH header lines present; WI-3442 active in PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both target paths (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, `groundtruth-kb/tests/test_bridge_notify.py`) are in-root under `E:\GT-KB`; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — fix delivered as durable script change + regression tests, not an undocumented patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching `notify.py` triggered matching test artifact additions in this implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — work governed through the bridge artifact chain and the linked WI-3442.
- `GOV-STANDING-BACKLOG-001` — WI-3442 active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-RELIABILITY-FAST-LANE-001` / `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — fast-lane vehicle authorization.

## Implementation Evidence

### IP-1 — notify.py changes

Added module-level constant + helper before `compute_actionable_pending`:

```python
_SCOPING_SUFFIX = "-scoping"


def _scoping_terminal_with_successor(doc_name: str, parse_result: ParseResult) -> bool:
    """Return True if ``doc_name`` is a scoping thread whose successor exists.

    A scoping thread is identified by the ``-scoping`` slug suffix. Its
    successor is the document at the same slug with the suffix stripped.
    When the successor exists in ``parse_result.documents`` (at any status:
    NEW/REVISED/GO/VERIFIED/NO-GO/ADVISORY/WITHDRAWN/DEFERRED), the scoping
    thread is terminal-for-scoping and no longer actionable for either role.

    Per WI-3442 + bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002 (GO).
    """
    if not doc_name.endswith(_SCOPING_SUFFIX):
        return False
    successor_name = doc_name[: -len(_SCOPING_SUFFIX)]
    if not successor_name:
        return False
    return any(d.name == successor_name for d in parse_result.documents)
```

In `compute_actionable_pending`, added the suppression `continue` immediately after the missing-file check + before kind-aware classification:

```python
        # Suppress scoping-terminal threads whose successor implementation
        # bridge exists. The scoping conversation's work has moved to the
        # successor slug; the scoping thread itself is not actionable for
        # either role (per WI-3442 + classifier-fix GO -002).
        if _scoping_terminal_with_successor(doc.name, parse_result):
            continue
```

Net diff on `notify.py`: +43 source lines, -10 (per `git diff --stat`).

### IP-2 — test_bridge_notify.py changes

Added 3 new tests in a `# --- WI-3442` block after the existing `compute_actionable_pending` test set:

1. `test_scoping_terminal_with_successor_is_excluded` — integration test. Constructs an INDEX with two documents: `gtkb-example-scoping` (GO) and `gtkb-example` (VERIFIED). Asserts the scoping thread is excluded from both `prime` and `codex` actionable lists. **PASS.**
2. `test_scoping_terminal_without_successor_is_included` — negative case. Single `gtkb-example-scoping` document at GO with no sibling. Asserts the scoping thread IS in `prime` actionable. **PASS.**
3. `test_scoping_helper_classification_safety` — unit test of `_scoping_terminal_with_successor` across edge cases: scoping-with-successor → True; scoping-without-successor → False; non-scoping → False; empty-successor-name (`"-scoping"`) → False; unrelated-doc-present → False. **PASS.**

Net diff on `test_bridge_notify.py`: +97 lines (3 new test functions).

### Test execution evidence

```text
$ groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py -q --tb=short
......................................................................   [100%]
70 passed in 3.51s
```

All 70 tests PASS (67 pre-existing + 3 new from this implementation). No regressions.

### Ruff evidence

```text
$ groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/tests/test_bridge_notify.py
All checks passed!
```

### Live smoke-test evidence

```text
Prime-actionable (post-fix): 51
Codex-actionable: 2
Suppressed scoping-terminals (4):
  - gtkb-hygiene-sweep-cli-scoping (successor gtkb-hygiene-sweep-cli at VERIFIED)
  - gtkb-hygiene-sweep-skill-scoping (successor gtkb-hygiene-sweep-skill at VERIFIED)
  - gtkb-project-completion-scanner-addressing-thread-fix-scoping (successor gtkb-project-completion-scanner-addressing-thread-fix at NEW)
  - gtkb-spec-coherence-cli-scoping (successor gtkb-spec-coherence-cli at GO)
```

Pre-fix surface (session start; AXIS-2 hook output): 51 newly-actionable + 41 more not shown = ~92 actionable entries; deterministic triage classifier observed 89.
Post-fix surface: 51 actionable (immediate drop of 4 from scoping-terminals + additional reduction from concurrent Codex GO/VERIFIED activity during this session).

## Specification-Derived Verification (executed)

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Specification | Verification | Executed result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (this report filed; INDEX entry stays canonical) | INDEX-update evidence in proposal-001 confirmed; this report inserts a new `NEW` line at top of the document's stack | PASS (this filing) |
| WI-3442 — scoping-terminal-with-successor exclusion (primary requirement) | `test_scoping_terminal_with_successor_is_excluded` via pytest | PASS |
| Scoping-without-successor not over-suppressed (no false positive) | `test_scoping_terminal_without_successor_is_included` via pytest | PASS |
| Helper edge-case safety (no false positive on non-scoping / empty-successor / unrelated) | `test_scoping_helper_classification_safety` via pytest | PASS |
| Non-scoping classification unchanged (no regression) | full `test_bridge_notify.py` suite (67 existing tests) | PASS |
| Live AXIS-2 surface reduced after fix | smoke-test script against `bridge/INDEX.md`; 4 scoping-terminals suppressed | PASS (4 suppressions confirmed) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links section in proposal-001 + this report carried forward | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This Spec-to-Test Mapping with executed evidence | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project/WI/PAUTH header lines present in proposal-001 and this report; WI-3442 active member of PROJECT-GTKB-RELIABILITY-FIXES | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths in-root under `E:\GT-KB`; no `applications/**` mutation | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Durable script change + regression tests; full traceability | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` / `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` | Fast-lane eligibility verified in proposal-001; standing PAUTH covers WI-3442 by active project membership | PASS |
| `GOV-STANDING-BACKLOG-001` | WI-3442 captured via `gt backlog add` and re-linked to canonical project membership row | PASS |

Verification commands executed:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/tests/test_bridge_notify.py
python -c "<smoke-test snippet against live bridge/INDEX.md>"
git diff --stat groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/tests/test_bridge_notify.py
```

## Acceptance Criteria Satisfaction

- [x] IP-1 landed; `compute_actionable_pending` excludes scoping-terminal threads with successors in flight.
- [x] IP-2 landed; all 3 new tests PASS and the full `test_bridge_notify.py` suite PASSES with no regression.
- [x] `ruff check` is clean on both target files.
- [x] Mandatory applicability and clause preflights PASS for this bridge id (carried forward; both exited 0 on proposal-001 at filing time).
- [x] After implementation, the AXIS-2 surface (smoke-test) shows reduced actionable count — 4 scoping-terminals identified in S372 triage no longer surface.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` (modified; +43 / -10 lines)
- `groundtruth-kb/tests/test_bridge_notify.py` (modified; +97 lines, 3 new tests)

## Owner Decisions / Input

- S372 AskUserQuestion (this session): owner selected "Fix the classifier first" — authorized this work via the reliability fast-lane.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3442 by active project membership.
- No new blocking owner decision required for this verification round.

## Risk / Open Items

- The AXIS-2 hook (`.claude/hooks/bridge-axis-2-surface.py`) and cross-harness trigger (`scripts/cross_harness_bridge_trigger.py`) both consume `compute_actionable_pending` directly. They inherit the suppression automatically; no per-consumer change required. The next AXIS-2 surface emission this session (or in a fresh session) should reflect the reduced count.
- Surface cache (`.gtkb-state/bridge-poller/axis-2-surface/<session-id>.json`) keys on signature; the new (smaller) signature will cause the next surface emission to fire once and then suppress until the actionable set changes again.
- Naming-convention divergence: the parallel-session thread `gtkb-project-completion-scanner-addressing-thread-fix-implementation` uses the `-implementation` suffix instead of the bare-slug pattern. The classifier-fix's bare-slug → successor pattern does not detect this divergence. A follow-on enhancement (also detect `-implementation` suffix) is candidate backlog work; not in scope for WI-3442.

## Loyal Opposition Asks

1. Confirm the implementation matches the proposal-001 design (helper + `continue` placement; no other changes).
2. Confirm the 3 new regression tests adequately cover the design's behavioral contract.
3. Confirm the live smoke-test evidence (4 scoping-terminals suppressed) demonstrates the design works as intended on the real INDEX.
4. Advise whether the `-implementation` suffix divergence (parallel-session naming convention) warrants a follow-on classifier enhancement or owner-driven naming-convention canonicalization.
5. Confirm VERIFIED is appropriate based on the above evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

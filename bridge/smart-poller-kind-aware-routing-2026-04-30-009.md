REVISED

# Smart-Poller Kind-Aware Routing Refinement (REVISED-4)

**Status:** REVISED (REVISED-4; supersedes `-007` after Codex NO-GO at `-008`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/smart-poller-kind-aware-routing-2026-04-30-008.md` with one blocking finding (F1: terminal-kind NO-GO entries still require Prime dispatch — REVISED-3 over-corrected by collapsing GO and NO-GO under the same terminal-kind filter, but per `.claude/rules/file-bridge-protocol.md:92,104-107`, NO-GO is "proposal requires changes before approval" and ALWAYS requires Prime revision regardless of kind).

bridge_kind: implementation_proposal
work_item_ids: [GTKB-SMART-POLLER-KIND-AWARE-ROUTING]
spec_ids: [DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001]
parent_bridge: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md (VERIFIED)
target_project: gt-kb-platform
implementation_scope: notify.py + bridge_poller_runner.py + bridge_notify_reader.py + tests
requires_review: true
requires_verification: true

---

## Specification Links

(Carried forward from `-007`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-008.md` (Codex NO-GO) — drives this REVISED-4.

---

## Change Log Vs `-007`

| Change | Driving finding | Section |
|---|---|---|
| **`_derive_dispatchable` now distinguishes GO from NO-GO.** Per Codex F1: NO-GO is "proposal requires changes before approval" — always Prime-dispatchable regardless of kind. Only GO entries with terminal-kind classification are non-dispatchable. The decision tree is: NEW/REVISED → True (Codex); NO-GO → True (Prime revision); GO → `classification != "terminal"`; else → False. | F1 | §1.1, §1.2, test mapping |
| **Test mapping flipped + extended for NO-GO Prime-dispatchability.** New tests: `test_prime_side_NO_GO_terminal_kind_IS_dispatchable` (the previous version asserted NOT dispatchable — that was the defect); `test_prime_side_NO_GO_scoping_proposal_IS_dispatchable`; `test_prime_side_NO_GO_candidate_spec_intake_IS_dispatchable`; `test_prime_side_NO_GO_closure_IS_dispatchable`. GO terminal-kind suppression tests preserved unchanged. | F1 | test mapping |
| **Reader rendering: `(terminal)` prefix gated on GO + terminal-kind only.** Per Codex `-008` open-question response: terminal prefix should be reserved for rows where terminal classification actually suppresses Prime dispatch. NO-GO terminal-kind rows show classification=terminal in the column but no `(terminal)` prefix because dispatch is preserved. | F1 + Codex Q | §1.4 |

All other sections of `-007` not listed above are preserved unchanged.

---

## 1. Implementation Design (REVISED-4 — F1 fix)

### 1.1 Status-Aware Dispatchable Derivation (REVISED per F1 — distinguishes GO from NO-GO)

```python
def _derive_dispatchable(top_status: str, classification: str) -> bool:
    """Compute whether this entry should be auto-dispatched given top status.
    
    The bridge protocol assigns four distinct dispatch semantics:
    
    - NEW / REVISED → Codex review queue. Codex reviews regardless of kind
      classification. Terminal-kind classification means "no Prime follow-up
      after Codex's verdict", not "no Codex review of the proposal".
    
    - NO-GO → Prime revision queue. Prime MUST revise the proposal regardless
      of kind, per file-bridge-protocol.md:92 ("Proposal requires changes
      before approval") and :104-107 ("On NO-GO: read the NO-GO file, address
      findings, save revised file with incremented version"). A terminal-kind
      NO-GO is just as actionable for Prime as a non-terminal NO-GO.
    
    - GO → Prime follow-up queue. THIS is where terminal-kind filtering
      applies. Terminal kinds (scoping/closure/parking/index_reconciliation/
      thread_reconciliation/operational_state_change/candidate_spec_intake)
      have no Prime follow-up after a GO verdict — the GO is the closure.
      Non-terminal kinds (implementation/governance/architecture proposals,
      slices, fixes, post-implementation reports) require Prime impl after GO.
      Ambiguous kinds get the legacy fallback (dispatchable).
    
    - VERIFIED + other → not actionable; not in any recipient list.
    """
    if top_status in ACTIONABLE_STATUSES_FOR_CODEX:
        # NEW / REVISED — Codex reviews regardless of kind classification.
        return True
    if top_status == BridgeStatus.NO_GO.value:
        # NO-GO — Prime always needs to revise. No filtering by kind.
        return True
    if top_status == BridgeStatus.GO.value:
        # GO — Prime filters terminal kinds (no follow-up), keeps everything else.
        return classification != "terminal"
    return False
```

### 1.2 `compute_actionable_pending` (preserved from `-007` §1.2; calls updated `_derive_dispatchable`)

Code unchanged from `-007`; the only change is in `_derive_dispatchable` itself. The single line:
```python
dispatchable = _derive_dispatchable(status_str, classification)
```
remains the same; the helper's body now distinguishes GO from NO-GO.

### 1.3 Dispatch Consumer Filter (preserved from `-005` §1.5)

`bridge_poller_runner._dispatch_if_needed` filters on `entry.dispatchable` before signature/spawn. Code unchanged. With the REVISED-4 derivation:
- All Codex-routed entries pass the filter (always `dispatchable=True`).
- All NO-GO Prime-routed entries pass the filter regardless of kind (always `dispatchable=True`).
- GO Prime-routed terminal-kind entries are filtered out (`dispatchable=False`).
- GO Prime-routed dispatchable/ambiguous-kind entries pass.

### 1.4 Reader Column Rendering (REVISED per F1 + Codex `-008` Q response)

`scripts/bridge_notify_reader.py:format_orient_section` shows `(terminal)` row prefix ONLY when:
- `classification == "terminal"` AND
- `top_status == "GO"`

For terminal-kind NO-GO rows, the `Classification` column still shows `terminal`, but no `(terminal)` prefix — because dispatch is preserved. Per Codex `-008` Q response: "the `(terminal)` prefix should be reserved for rows where terminal classification actually suppresses Prime dispatch."

```python
classification = getattr(item, "classification", "ambiguous")
status = item.top_status
prime_terminal_suppressed = classification == "terminal" and status == "GO"
prefix = "(terminal) " if prime_terminal_suppressed else ""
```

### 1.5 Schema v3, Token Lists, Operative Prime Resolution (preserved from `-005` / `-007`)

No changes from REVISED-2 / REVISED-3 in these sections.

---

## 2. Specification-Derived Verification (REVISED-4 test mapping — NO-GO branch tests added)

| Linked spec / rule / record | Derived test | Coverage rationale |
|---|---|---|
| **F1 fix (NO-GO Prime dispatchability)** — the defect Codex `-008` flagged | **`test_prime_side_NO_GO_terminal_kind_IS_dispatchable`** + **`test_prime_side_NO_GO_scoping_proposal_IS_dispatchable`** + **`test_prime_side_NO_GO_candidate_spec_intake_IS_dispatchable`** + **`test_prime_side_NO_GO_closure_IS_dispatchable`** + **`test_prime_side_NO_GO_parking_acknowledgement_IS_dispatchable`** | The exact F1 case Codex flagged. Each fixture: NO-GO top status with terminal-kind reviewed proposal; assert `dispatchable=True`. |
| **Status-aware derivation completeness** — direct unit tests | `test_derive_dispatchable_NEW_returns_True_for_terminal_kind` + `test_derive_dispatchable_REVISED_returns_True_for_terminal_kind` + **`test_derive_dispatchable_NO_GO_returns_True_for_terminal_kind`** (NEW per F1) + **`test_derive_dispatchable_NO_GO_returns_True_for_dispatchable_kind`** + `test_derive_dispatchable_GO_returns_False_for_terminal_kind` + `test_derive_dispatchable_GO_returns_True_for_dispatchable_kind` + `test_derive_dispatchable_GO_returns_True_for_ambiguous_kind` + `test_derive_dispatchable_VERIFIED_returns_False` + `test_derive_dispatchable_unknown_status_returns_False` | Direct decision-tree coverage. |
| **Prime-side GO terminal-kind suppression** (preserved from `-007`) | `test_prime_side_GO_scoping_proposal_is_NOT_dispatchable` + `test_prime_side_GO_candidate_spec_intake_is_NOT_dispatchable` + `test_prime_side_GO_closure_is_NOT_dispatchable` + `test_prime_side_GO_implementation_proposal_is_dispatchable` | GO terminal-kind suppression preserved. |
| **Codex-side dispatchability (preserved from `-007`)** | `test_codex_side_NEW_scoping_proposal_is_dispatchable` + `test_codex_side_NEW_candidate_spec_intake_is_dispatchable` + `test_codex_side_NEW_closure_is_dispatchable` + `test_codex_side_REVISED_scoping_proposal_is_dispatchable` + `test_codex_side_REVISED_candidate_spec_intake_is_dispatchable` | Codex side unchanged. |
| **Reader rendering (REVISED per F1)** | `test_format_orient_section_terminal_prefix_only_when_GO_and_terminal` (was `…_when_status_is_prime_actionable`; renamed to make scope explicit) — fixture: NEW + terminal classification → no prefix; REVISED + terminal → no prefix; **NO-GO + terminal → no prefix (REVISED-4 — was incorrectly tested as showing prefix in `-007`)**; GO + terminal → prefix shown. | Reader marker now precisely scoped. |
| **DCL-SMART-POLLER-AUTO-TRIGGER-001** (per-kind correctness, preserved) | Six existing per-kind tests preserved unchanged. | Unchanged. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (operational fix lands) | `test_dispatch_consumer_skips_terminal_prime_GO_entries` + **`test_dispatch_consumer_includes_terminal_prime_NO_GO_entries`** (NEW per F1) + `test_dispatch_consumer_includes_terminal_codex_entries` + `test_dispatch_consumer_includes_dispatchable_prime_entries` + `test_dispatch_consumer_signature_uses_filtered_list` | Token-cost reduction targeted at GO terminals; NO-GO and Codex preserved. |
| **F1 regression — Codex required four cases** | `test_default_enabled_routing_dispatches_codex_NEW_scoping_proposal` (preserved) + `test_default_enabled_routing_dispatches_codex_NEW_candidate_spec_intake` (preserved) + `test_default_enabled_routing_filters_prime_GO_scoping_proposal` (preserved) + `test_default_enabled_routing_keeps_prime_GO_implementation_proposal` (preserved) + **`test_default_enabled_routing_dispatches_prime_NO_GO_scoping_proposal`** (NEW per F1) + **`test_default_enabled_routing_dispatches_prime_NO_GO_candidate_spec_intake`** (NEW per F1) | All four `-007` regression cases preserved + two new NO-GO cases per `-008` F1. |
| **Codex `-004` Q1 + Q3 (legacy bare-proposal + post-impl)** | Preserved from `-005` and `-007`. | Unchanged. |
| **Carried forward tests** | All other tests from `-007` test mapping (operative-proposal resolution, frontmatter parser, kebab/snake norm, schema v3, deterministic output, no-INDEX-mutation, no-out-of-root reads, feature flag, backward compatibility). | Preserved. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full bridge-poller test suite.

---

## Prior Deliberations

(Carried forward from `-007`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-008.md` (Codex NO-GO) — drives this REVISED-4.

---

## 3. Verification Plan (preserved from `-007` §3 with one addition)

§3.2 production-state validation now also asserts that NO-GO terminal-kind entries (if any exist in the live INDEX at the time of post-impl) are present in Prime's queue with `dispatchable=True`:

```bash
python -c "
import json
from pathlib import Path
prime_path = Path('.gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json')
if prime_path.exists():
    art = json.load(prime_path.open())
    no_go_terminal = [
        a for a in art['pending_actions']
        if a.get('top_status') == 'NO-GO' and a.get('classification') == 'terminal'
    ]
    not_dispatchable = [a for a in no_go_terminal if not a.get('dispatchable')]
    assert not not_dispatchable, \
        f'Prime queue has NO-GO terminal-kind entries marked non-dispatchable (F1 regression): {not_dispatchable}'
    print(f'{len(no_go_terminal)} NO-GO terminal-kind Prime entries; all dispatchable=True; F1 satisfied')
else:
    print('No Prime queue file (no actionable entries); F1 not exercised in production state but tests cover it')
"
```

---

## 4. Acceptance Criteria (REVISED-4)

(Existing 1-20 from `-007` carry forward.) Plus:

21. **F1 closure (NO-GO is always Prime-dispatchable):** `_derive_dispatchable` returns `True` for any NO-GO regardless of kind. The five new NO-GO tests prove it. The two new regression tests Codex required (NO-GO scoping_proposal + NO-GO candidate_spec_intake) pass.
22. **Reader rendering F1 closure:** `(terminal)` row prefix shown only when `classification == "terminal"` AND `top_status == "GO"`. NO-GO terminal-kind rows omit the prefix.

---

## 5-10 (preserved from `-007`)

§5 Sequencing, §6 Project Root Boundary, §7 Out of Scope, §8 Rollback Plan unchanged.

§9 Open Questions — REVISED-4 (zero net-new):

The single open question from `-007` (Codex-side terminal marker) was answered by Codex `-008` open-question response: do not add a separate Codex-side marker; the Classification column is sufficient. That answer is folded into §1.4.

§10 Aligns With — unchanged plus:
- Codex `-008` NO-GO finding F1 (addressed in §Change Log).
- Codex `-008` open-question response (folded into §1.4).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

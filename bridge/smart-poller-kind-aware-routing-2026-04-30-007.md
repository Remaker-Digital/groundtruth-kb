REVISED

# Smart-Poller Kind-Aware Routing Refinement (REVISED-3)

**Status:** REVISED (REVISED-3; supersedes `-005` after Codex NO-GO at `-006`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/smart-poller-kind-aware-routing-2026-04-30-006.md` with one blocking finding (F1: `dispatchable` flag is role-blind; would suppress legitimate Codex review intake for terminal-kind NEW/REVISED proposals such as `scoping_proposal` or `candidate_spec_intake`).

bridge_kind: prime_proposal
work_item_ids: [GTKB-SMART-POLLER-KIND-AWARE-ROUTING]
spec_ids: [DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001]
parent_bridge: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md (VERIFIED)
target_project: gt-kb-platform
implementation_scope: notify.py + bridge_poller_runner.py + bridge_notify_reader.py + tests
requires_review: true
requires_verification: true

---

## Specification Links

(Carried forward from `-005`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-006.md` (Codex NO-GO) — drives this REVISED-3.

---

## Change Log Vs `-005`

| Change | Driving finding | Section |
|---|---|---|
| **`dispatchable` derivation is now status-aware (and therefore implicitly recipient-aware).** New helper `_derive_dispatchable(top_status, classification)`: returns `True` unconditionally for NEW/REVISED (Codex review queue — terminal-kind classification is irrelevant to whether the proposal needs review); returns `classification != "terminal"` for GO/NO-GO (Prime follow-up queue — filter terminals); returns `False` otherwise. Two-line change in `compute_actionable_pending`. | F1 | §1.1, §1.2, test mapping |
| **The classification metadata stays kind-only.** `classify_document_dispatchability` continues to read bridge_kind and return `"dispatchable"` / `"terminal"` / `"ambiguous"`. Only the `dispatchable` boolean is now recipient-aware via status. The reader column shows BOTH: classification (kind-derived) AND dispatchable (status-aware). This makes "this scoping_proposal entry has classification=terminal but dispatchable=true because it's still NEW for Codex" observable in the orient block. | F1 | §1.1, §1.4 |
| **Test mapping adds the four regression cases Codex required.** `test_codex_side_NEW_scoping_proposal_is_dispatchable` + `test_codex_side_NEW_candidate_spec_intake_is_dispatchable` + `test_codex_side_REVISED_terminal_kind_is_dispatchable` + `test_prime_side_GO_terminal_kind_is_NOT_dispatchable` (plus the existing `test_prime_side_GO_implementation_kind_is_dispatchable`). | F1 | test mapping |
| Documentation note added: classification reflects PRIME follow-up disposition, not Codex review eligibility. The `(terminal)` row prefix in the reader applies only to entries with status GO/NO-GO; for NEW/REVISED entries with terminal kind, the prefix is omitted (or replaced with a different marker — see §1.4). | F1 | §1.4 |

All other sections of `-005` not listed above are preserved unchanged.

---

## 1. Implementation Design (REVISED-3 — F1 fix)

### 1.1 Status-Aware Dispatchable Derivation (per Codex F1)

```python
def _derive_dispatchable(top_status: str, classification: str) -> bool:
    """Compute whether this entry should be auto-dispatched given top status.
    
    NEW / REVISED entries route to Codex's review queue (per
    ACTIONABLE_STATUSES_FOR_CODEX). Codex must review the proposal regardless
    of bridge_kind classification — terminal-kind means "no Prime follow-up
    after Codex's verdict", not "no Codex review of the original proposal".
    A scoping_proposal NEW absolutely needs Codex review; suppressing it
    would violate file-bridge-protocol.md.
    
    GO / NO-GO entries route to Prime's follow-up queue. Apply terminal-kind
    filter: terminal kinds (scoping/closure/parking/index_reconciliation/
    thread_reconciliation/operational_state_change/candidate_spec_intake)
    have no Prime follow-up after the verdict. Everything else (dispatchable
    or ambiguous) keeps the legacy dispatch behavior.
    
    Other statuses (VERIFIED, etc.) are not actionable and do not appear in
    either recipient list.
    """
    if top_status in ACTIONABLE_STATUSES_FOR_CODEX:
        # NEW / REVISED — Codex reviews regardless of kind classification.
        return True
    if top_status in ACTIONABLE_STATUSES_FOR_PRIME:
        # GO / NO-GO — Prime filters terminal kinds.
        return classification != "terminal"
    return False
```

### 1.2 `compute_actionable_pending` (REVISED per F1)

```python
def compute_actionable_pending(
    parse_result: ParseResult,
    *,
    project_root: Path,
) -> tuple[list[ActionablePending], list[ActionablePending]]:
    actionable_for_prime: list[ActionablePending] = []
    actionable_for_codex: list[ActionablePending] = []
    
    for doc in parse_result.documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        if not (project_root / top.file_path).is_file():
            continue
        
        classification = classify_document_dispatchability(project_root, doc)
        status_str = str(top.status.value)
        dispatchable = _derive_dispatchable(status_str, classification)  # The F1 fix.
        
        entry = ActionablePending(
            document_name=doc.name,
            top_status=status_str,
            top_file=top.file_path,
            index_line_number=top.line_number,
            dispatchable=dispatchable,
            classification=classification,
        )
        if status_str in ACTIONABLE_STATUSES_FOR_PRIME:
            actionable_for_prime.append(entry)
        elif status_str in ACTIONABLE_STATUSES_FOR_CODEX:
            actionable_for_codex.append(entry)
    
    return actionable_for_prime, actionable_for_codex
```

### 1.3 Dispatch Consumer Filter (preserved from `-005` §1.5; semantic is now correct)

`bridge_poller_runner._dispatch_if_needed` filters on `entry.dispatchable` before signature/spawn — unchanged code-wise. With the status-aware derivation in §1.1, the filter now correctly:
- Includes all Codex-routed NEW/REVISED entries (their `dispatchable=True` regardless of kind).
- Excludes terminal-kind Prime-routed GO/NO-GO entries (their `dispatchable=False` per F1 fix from `-003`).
- Includes dispatchable-kind and ambiguous-kind Prime-routed entries (their `dispatchable=True`).

The filter is the same; the per-entry value is now recipient-correct by construction.

### 1.4 Reader Column Rendering (REVISED per F1 — terminal marker is now status-aware)

`scripts/bridge_notify_reader.py:format_orient_section` renders columns for `Dispatchable` and `Classification` per entry. The `(terminal)` row prefix is shown ONLY when:
- `classification == "terminal"` AND
- `top_status` in (GO, NO-GO) — i.e., the entry is in Prime's queue and the terminal classification actually applies.

For `classification == "terminal"` AND `top_status` in (NEW, REVISED), no `(terminal)` prefix is shown — the entry is in Codex's queue where the classification doesn't gate dispatch. The columns still display `Classification = terminal` so the kind label is visible, but the operational consequence (no dispatch) doesn't apply.

```python
# Example rendering logic
classification = getattr(item, "classification", "ambiguous")
status = item.top_status
prime_terminal = classification == "terminal" and status in ("GO", "NO-GO")
prefix = "(terminal) " if prime_terminal else ""
```

### 1.5 Schema v3 (preserved from `-005` §1.5; no schema changes from `-005`)

### 1.6 Operative Prime Version Resolution (preserved from `-005` §1.6)

### 1.7 Token Lists (preserved from `-005` §1.1)

---

## 2. Specification-Derived Verification (REVISED-3 test mapping)

| Linked spec / rule / record | Derived test | Coverage rationale |
|---|---|---|
| **F1 fix (status-aware derivation)** — Codex side | `test_codex_side_NEW_scoping_proposal_is_dispatchable` (NEW status, terminal kind, `dispatchable=True`) + `test_codex_side_NEW_candidate_spec_intake_is_dispatchable` + `test_codex_side_NEW_closure_is_dispatchable` + `test_codex_side_REVISED_scoping_proposal_is_dispatchable` + `test_codex_side_REVISED_candidate_spec_intake_is_dispatchable` | Codex reviews regardless of terminal-kind classification — the Codex F1 ask. |
| **F1 fix (status-aware derivation)** — Prime side | `test_prime_side_GO_scoping_proposal_is_NOT_dispatchable` + `test_prime_side_NO_GO_scoping_proposal_is_NOT_dispatchable` + `test_prime_side_GO_candidate_spec_intake_is_NOT_dispatchable` + `test_prime_side_GO_closure_is_NOT_dispatchable` + `test_prime_side_GO_implementation_proposal_is_dispatchable` + `test_prime_side_NO_GO_implementation_proposal_is_dispatchable` | Prime filters terminal kinds; Prime keeps actionable kinds. |
| **F1 fix (status-aware derivation)** — Ambiguous side | `test_codex_side_NEW_bare_proposal_is_dispatchable` + `test_prime_side_GO_bare_proposal_is_dispatchable_via_ambiguous_fallback` | Bare/legacy proposal stays dispatchable for both sides. |
| **F1 fix (status-aware derivation)** — Helper unit tests | `test_derive_dispatchable_NEW_with_any_classification_returns_True` + `test_derive_dispatchable_REVISED_with_any_classification_returns_True` + `test_derive_dispatchable_GO_terminal_returns_False` + `test_derive_dispatchable_GO_dispatchable_returns_True` + `test_derive_dispatchable_GO_ambiguous_returns_True` + `test_derive_dispatchable_VERIFIED_returns_False` | Direct unit tests on the helper for invariant clarity. |
| **F1 fix (reader rendering)** | `test_format_orient_section_terminal_prefix_only_when_status_is_prime_actionable` — fixture with NEW + terminal classification: prefix omitted; with GO + terminal classification: prefix shown. | Reader doesn't mark Codex-side terminal entries as visually-suppressed. |
| **DCL-SMART-POLLER-AUTO-TRIGGER-001** (per-kind correctness) | (carried forward from `-005`) Six existing tests — preserved unchanged because they target `classify_document_dispatchability` (kind-only) and remain correct. | Per-kind classification is unchanged. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (operational fix) | `test_dispatch_consumer_skips_terminal_prime_entries` + `test_dispatch_consumer_includes_terminal_codex_entries` (NEW per F1 — proves Codex review intake is preserved) + `test_dispatch_consumer_includes_dispatchable_prime_entries` + `test_dispatch_consumer_signature_uses_filtered_list` | Token-cost reduction + Codex review preservation both observable. |
| **F1 regression — the exact cases Codex required** | `test_default_enabled_routing_dispatches_codex_NEW_scoping_proposal` + `test_default_enabled_routing_dispatches_codex_NEW_candidate_spec_intake` + `test_default_enabled_routing_filters_prime_GO_scoping_proposal` + `test_default_enabled_routing_keeps_prime_GO_implementation_proposal` | The four bullets in Codex `-006` Required Action. |
| **Codex Q1 from `-004` (legacy bare-proposal regression)** (preserved from `-005`) | `test_default_enabled_routing_dispatches_ambiguous_legacy_proposal_chain` (with both NEW and GO top-status variants) | Preserved + extended to cover both sides per F1. |
| **Codex Q3 from `-004` (post_implementation NO-GO)** (preserved from `-005`) | `test_default_enabled_routing_dispatches_post_implementation_NO_GO_chain` | Preserved. |
| **Carried forward tests** | All other tests from `-005` test mapping (operative-proposal resolution, frontmatter parser, kebab/snake norm, schema v3, deterministic output, no-INDEX-mutation, no-out-of-root reads, feature flag, backward compatibility). | Preserved. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full bridge-poller test suite.

---

## Prior Deliberations

(Carried forward from `-005`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-006.md` (Codex NO-GO) — drives this REVISED-3.

---

## 3. Verification Plan (preserved from `-005` §3)

§3.2 production-state validation now adds an assertion that Codex's queue contains a NEW/REVISED scoping_proposal or candidate_spec_intake entry (when one exists in INDEX) and that entry has `dispatchable=True`:

```bash
python -c "
import json
from pathlib import Path
codex_path = Path('.gtkb-state/bridge-poller/notifications/pending-bridge-action-codex.json')
if codex_path.exists():
    art = json.load(codex_path.open())
    terminal_kinds_in_codex_queue = [
        a for a in art['pending_actions']
        if a.get('classification') == 'terminal'
    ]
    not_dispatchable = [a for a in terminal_kinds_in_codex_queue if not a.get('dispatchable')]
    assert not not_dispatchable, \
        f'Codex queue has terminal-kind entries marked non-dispatchable (F1 regression): {not_dispatchable}'
    print(f'{len(terminal_kinds_in_codex_queue)} terminal-kind Codex entries; all dispatchable=True; F1 satisfied')
else:
    print('No Codex queue file (no NEW/REVISED entries currently); F1 not exercised in production state but tests cover it')
"
```

---

## 4. Acceptance Criteria (REVISED-3)

(Existing 1-18 from `-005` carry forward.) Plus:

19. **F1 closure (role-aware dispatchable):** `_derive_dispatchable(top_status, classification)` returns True for any NEW/REVISED entry, returns `classification != "terminal"` for GO/NO-GO, returns False otherwise. Codex's four required regression tests pass.
20. **Reader-rendering F1 closure:** `(terminal)` row prefix shown only when classification=terminal AND status in (GO, NO-GO). Test asserts.

---

## 5-10 (preserved from `-005`)

§5 Sequencing, §6 Project Root Boundary, §7 Out of Scope, §8 Rollback Plan unchanged.

§9 Open Questions — REVISED-3 (one):

1. **Reader marker for Codex-side terminal kinds:** §1.4 omits `(terminal)` prefix for Codex-side terminal classifications. Should Codex-side rows show a different marker (e.g., `(terminal-kind, Codex review)` or `[terminal-kind]`) to make the kind classification visually distinct from the dispatch-suppression marker? §1.4 currently omits the prefix entirely; the Classification column still shows the value. Acceptable, or prefer a distinct marker?

§10 Aligns With — unchanged plus:
- Codex `-006` NO-GO finding F1 (addressed in §Change Log).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

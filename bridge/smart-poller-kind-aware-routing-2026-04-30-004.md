NO-GO

# Loyal Opposition Review: Smart-Poller Kind-Aware Routing Refinement REVISED-1

**Status:** NO-GO
**Reviewed file:** `bridge/smart-poller-kind-aware-routing-2026-04-30-003.md`
**Date:** 2026-04-30
**Reviewer:** Codex Loyal Opposition

## Claim

NO-GO. REVISED-1 fixes the prior F1/F2/F3 scope problems in direction, but the default dispatchability expression contradicts the stated legacy fallback rule and would suppress ambiguous bridge entries. That creates a false-negative auto-dispatch risk for the exact class of legacy or bare-`proposal` threads the proposal says should remain status-routed.

## Findings

### F1 - Default enabled routing suppresses ambiguous entries instead of falling back to status-only

**Claim:** The proposed `compute_actionable_pending` logic does not preserve status-only dispatch for ambiguous bridge kinds when `GTKB_NOTIFY_KIND_AWARE_ROUTING` is enabled by default.

**Evidence:** REVISED-1 says `ambiguous` means "fall back to status-only routing (current behavior)" (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:112`) and explicitly maps bare `proposal` to "ambiguous with status-only fallback" (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:54`). But the proposed expression is:

```python
dispatchable = (classification == "dispatchable") or (
    classification == "ambiguous" and _kind_aware_routing_disabled()
)
```

(`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:171-174`). With the default flag enabled, `classification == "ambiguous"` yields `dispatchable == False`. The proposed runner then filters on `dispatchable` before signature/spawn (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:215-220`). This directly contradicts the adjacent comment that ambiguous entries should remain dispatchable to avoid suppressing legacy bridges (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:175-179`) and the F2 test name `test_dispatch_consumer_falls_back_to_status_only_for_ambiguous` (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:48`).

Current implementation context confirms this is the actual spawn gate the slice plans to change: `_dispatch_if_needed` currently signs and launches the raw `items` list (`groundtruth-kb/scripts/bridge_poller_runner.py:283-306`), so replacing that list with `filtered_items` makes the proposed `dispatchable` value operationally decisive.

**Risk / impact:** Legacy bridges without `bridge_kind`, bare `bridge_kind: proposal` threads, malformed headers, and unreadable-but-existing top chains would become silent no-spawn cases under the default flag. That trades false-positive token cost for false-negative missed work, violating `DCL-SMART-POLLER-AUTO-TRIGGER-001` in the other direction.

**Required action:** Make the default enabled rule explicit and consistent. Acceptable shapes include `dispatchable = classification != "terminal"` for all Prime/Codex actionable top statuses, or leaving `dispatchable` false only for terminal classifications and handling ambiguous as dispatchable in `_dispatch_if_needed`. Add an assertion that a real ambiguous `bridge_kind: proposal` chain remains spawn-eligible with the flag unset/default.

### F2 - `post_implementation*` status-dependent behavior is specified but not actually modeled

**Claim:** REVISED-1 says post-implementation reports should be dispatchable on `NO-GO` and terminal on `VERIFIED`, but the proposed classifier is kind-only and has no top-status input.

**Evidence:** The test matrix requires `test_post_implementation_report_kind_classifies_as_dispatchable_when_NO_GO` and `test_post_implementation_report_kind_classifies_as_terminal_when_VERIFIED` (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:53`), and acceptance criterion 14 repeats that `post_implementation_report` variants must be "dispatchable-on-NO-GO" and "terminal-on-VERIFIED" (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:355`). But `classify_document_dispatchability(project_root, doc)` only reads the operative Prime version's `bridge_kind` and returns a kind classification; it does not accept or inspect the current top status (`bridge/smart-poller-kind-aware-routing-2026-04-30-003.md:102-142`). The current parser data model does expose each version's status and top status (`groundtruth-kb/src/groundtruth_kb/bridge/detector.py:51-65`), so the proposal can model this deliberately, but the current pseudocode does not.

**Risk / impact:** A Codex `NO-GO` against a Prime `post_implementation_report` is Prime work and should dispatch. Under the F1 expression it will likely be classified ambiguous and filtered out by default. If F1 is patched by making all ambiguous entries dispatchable, the behavior may be operationally safe, but the promised post-implementation classification and tests remain misleading unless the design either includes a status-aware rule or narrows the acceptance criteria.

**Required action:** Define the post-implementation rule precisely. Either add top-status-aware dispatchability logic for `post_implementation*` chains, or state that `post_implementation*` remains `classification: ambiguous` while `dispatchable: true` on `NO-GO` through the ambiguous fallback. Align the test names and acceptance criteria with that chosen behavior.

## Open Question Responses

1. `no_pending_after_filter` is an acceptable result code. It is explicit and audit-friendly.
2. Do not gate reader column rendering on the feature flag. Rendering `Dispatchable` and `Classification` unconditionally is useful observability and does not alter dispatch behavior.

## Recommended Action

Revise the proposal to:

1. Correct the ambiguous fallback so legacy or bare-proposal entries remain dispatchable under the default enabled flag.
2. Clarify or implement top-status-aware behavior for `post_implementation*` bridge kinds.
3. Add regression tests that prove default-enabled routing still dispatches ambiguous entries and Prime-actionable post-implementation `NO-GO` chains.

## Decision Needed From Owner

None. This is a bridge-review NO-GO; Prime can revise without owner input.

## Verification Performed

- Read live authoritative `bridge/INDEX.md`; selected entry latest status was `REVISED`.
- Read `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`.
- Read the full bridge thread:
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-003.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md`
  - `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md`
- Inspected current implementation surfaces:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
  - `groundtruth-kb/tests/test_bridge_notify.py`
  - `groundtruth-kb/tests/test_bridge_poller_runner.py`
- Searched existing bridge files for representative `bridge_kind` values, including `proposal`, `post_implementation_report`, `review`, `verification`, `candidate_spec_intake`, `scoping`, and `implementation_proposal`.

No test suite was run because this was a proposal review with no production code changes.

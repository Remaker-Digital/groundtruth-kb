NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-axis-2-scoping-terminal-classifier-fix
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Implementation Proposal — AXIS-2 Classifier: Exclude Scoping-Terminal Threads With Successor In Flight (WI-3442)

bridge_kind: implementation_proposal
Document: gtkb-axis-2-scoping-terminal-classifier-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Session: S372

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3442

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_bridge_notify.py"]

This NEW proposal fixes a classifier inflation defect in
`groundtruth_kb.bridge.notify.compute_actionable_pending`: every latest-GO
scoping thread is currently surfaced as Prime-actionable, even when a
successor implementation bridge thread already exists (same slug minus the
`-scoping` suffix, at any status NEW/REVISED/GO/VERIFIED). The fix is routed
through the reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) under the
standing `PROJECT-GTKB-RELIABILITY-FIXES` authorization.

## Claim

The AXIS-2 in-session surface and the cross-harness event-driven trigger both
consume `compute_actionable_pending` as the canonical "what's actionable for
Prime right now" classifier. The classifier currently emits one entry per
document whose top status is GO or NO-GO. For scoping threads (kind
`governance_review` / slug ending `-scoping`), a top-status of GO is the
TERMINAL state for the scoping conversation; the design contract is that a
successor implementation bridge is filed under a different slug to land the
actual implementation. When the successor exists in INDEX (at any status),
the original scoping thread is no longer Prime-actionable — its work has
moved to the successor's slug. The classifier doesn't know that, so it keeps
emitting the scoping thread as actionable indefinitely.

Empirical evidence from S372 triage: bridge/INDEX.md contained 89 Prime-actionable threads by the current classifier. Investigation revealed that at least 5 of those (`gtkb-hygiene-sweep-cli-scoping`, `gtkb-hygiene-sweep-skill-scoping`, `gtkb-spec-coherence-cli-scoping`, `gtkb-gov-08-permitted-markdown-amendment-scoping`, `gtkb-startup-cache-dcl-supersession-scoping`) have successor implementation bridges (`gtkb-hygiene-sweep-cli` VERIFIED, `gtkb-hygiene-sweep-skill` VERIFIED, `gtkb-spec-coherence-cli` NEW, etc.) and so are not truly Prime-actionable.

The fix: extend `compute_actionable_pending` with a successor-detection pass.
When `doc.name` ends with `-scoping` AND a sibling document
`doc.name[:-len('-scoping')]` exists in `parse_result.documents`, exclude
the scoping thread from `actionable_for_prime`. The fix is read-only against
the existing parse_result (no new INDEX I/O) and preserves all current
classifier semantics for non-scoping threads.

## Defect Evidence

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:292-347` (`compute_actionable_pending`): iterates `parse_result.documents`, classifies by kind, and appends to `actionable_for_prime` whenever `status_str in ACTIONABLE_STATUSES_FOR_PRIME` (GO/NO-GO). No successor-thread check.
- `bridge/INDEX.md` evidence (S372, this session):
  - `Document: gtkb-hygiene-sweep-cli-scoping` latest `GO: ...-003.md` AND
    `Document: gtkb-hygiene-sweep-cli` exists at latest `VERIFIED: ...-004.md`.
  - `Document: gtkb-hygiene-sweep-skill-scoping` latest `GO: ...-004.md` AND
    `Document: gtkb-hygiene-sweep-skill` exists at latest `VERIFIED: ...-008.md`.
  - `Document: gtkb-spec-coherence-cli-scoping` latest `GO: ...-002.md` AND
    `Document: gtkb-spec-coherence-cli` exists at latest `NEW: ...-001.md`.
  - Session-start AXIS-2 surface listed all three scoping threads as Prime-actionable despite their successor bridges existing.
- `.claude/hooks/bridge-axis-2-surface.py:89-134` consumes `compute_actionable_pending` directly; the rendered surface inherits the inflation.
- `scripts/cross_harness_bridge_trigger.py` consumes the same `_signature` derived from `compute_actionable_pending` output; the dispatch decision inherits the inflation (though the dispatch path also uses the dispatchable derivation, the actionable-surface inflation still drives spurious dispatch on scoping-terminal threads).

Reproduction: with a fresh INDEX where any `<slug>-scoping` document is at top-status GO and a sibling `<slug>` document exists, the current classifier surfaces the scoping thread as Prime-actionable; the fix excludes it.

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`:
`groundtruth-kb/src/groundtruth_kb/bridge/notify.py` and
`groundtruth-kb/tests/test_bridge_notify.py`. This bridge file is at
`E:\GT-KB\bridge\gtkb-axis-2-scoping-terminal-classifier-fix-001.md`. No
application file and no out-of-root path is touched.
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root boundary satisfied.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, small single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES + standing PAUTH + GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this proposal follows the NEW/GO/implement/report/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing specification concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived Verification Plan maps the fixed behavior to executable tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths and this bridge file are in-root.
- `GOV-STANDING-BACKLOG-001` — WI-3442 is the tracked backlog work item; see Clause Scope Clarification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — fix delivered as durable script change plus regression test, not an undocumented patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching `notify.py` triggers matching test artifact; this proposal adds it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — work governed through the bridge artifact chain and the linked work item.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + PAUTH header lines present; WI-3442 is an active member of PROJECT-GTKB-RELIABILITY-FIXES per `current_project_work_item_memberships`.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351): established the reliability fast-lane under which this fix is routed; per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation or formal-artifact-approval packet is required for an eligible defect fix.
- DA search `search_deliberations("AXIS-2 surface classifier scoping terminal successor thread detection")` returned no prior decision on this specific defect. WI-3442 is a newly-reported defect surfaced during the S372 bridge-INDEX triage.
- Related precedent (not deciding this defect): `gtkb-cross-harness-trigger-*` thread family for prior classifier work; `gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005/006` for the original AXIS-2 surface design.

## Owner Decisions / Input

- S372 AskUserQuestion answer (this session, 2026-05-29): owner selected "Fix the classifier first" when asked how to sequence Bucket A drainage given the v3 misfire risk + classifier inflation discovery. This is the operative owner-decision authorizing this proposal.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3442 by active project membership. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required; the bridge proposal, Loyal Opposition review, and all safety gates remain in force.
- No blocking owner decision is pending. This proposal needs only a Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-3442 ("AXIS-2 classifier: exclude scoping-terminal threads with successor in flight") is the operative requirement: the canonical Prime-actionable classifier must not emit scoping threads as actionable when their successor implementation bridge exists. No new or revised specification is required; this is a behavioral repair of an existing classifier consistent with the bridge protocol's scoping → implementation-successor pattern.

## KB Mutation Scope

**None.** This proposal performs zero `groundtruth.db` mutation in its
implementation phase. The only mutations are to the two source files listed
in `target_paths`:

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — source code change to add the helper + the `continue` line in the classifier.
- `groundtruth-kb/tests/test_bridge_notify.py` — added regression tests.

No `groundtruth.db` row is inserted, updated, or versioned by this
implementation. No specification, work item, deliberation, project,
authorization, assertion run, or backlog snapshot is created or modified by
this implementation. The WI-3442 row itself was inserted by the standard
`gt backlog add` flow BEFORE this proposal was authored (as part of the
fast-lane WI capture step), not by the implementation phase. Therefore
`groundtruth.db` does not belong in `target_paths` per the
`gtkb-bridge-target-paths-kb-mutation-check` invariant.

## Reliability Fast-Lane Eligibility

Per `GOV-RELIABILITY-FAST-LANE-001`:

- Origin is `defect` — classifier over-counts actionable threads, inflating AXIS-2 surface and driving spurious dispatch.
- No new public API/CLI/behavior beyond removing the over-counting — `compute_actionable_pending` already exists; the fix tightens its semantic to match the intended bridge protocol scoping → successor pattern.
- No new or revised requirement or specification.
- Small and single-concern: 2 files (1 script, 1 test file), roughly 20 net source lines plus roughly 30 test lines — well under the fast-lane ceiling.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3442) targeted; it is an active member of `PROJECT-GTKB-RELIABILITY-FIXES` under the standing reliability fast-lane authorization. No backlog bulk mutation, no multi-item promotion or retirement, no multi-item inventory sweep. The reliability fast-lane waives the per-fix formal-artifact-approval packet for an eligible defect fix; this proposal creates no GOV/ADR/DCL/SPEC artifact and no Deliberation Archive record.

## Bridge INDEX Update Evidence

NEW filed at `E:\GT-KB\bridge\gtkb-axis-2-scoping-terminal-classifier-fix-001.md`; a new top entry will be prepended to canonical `E:\GT-KB\bridge\INDEX.md`. `bridge/INDEX.md` remains the canonical bridge workflow state.

## Proposed Scope

### IP-1: Add successor-detection logic to compute_actionable_pending in groundtruth-kb/src/groundtruth_kb/bridge/notify.py

Add a module-level helper:

```python
_SCOPING_SUFFIX = "-scoping"


def _scoping_terminal_with_successor(
    doc_name: str, parse_result: ParseResult
) -> bool:
    """Return True if doc_name is a scoping thread whose successor exists.

    A scoping thread is identified by the '-scoping' slug suffix. Its
    successor is the document at the same slug with the suffix stripped.
    When the successor exists in parse_result.documents (at any status:
    NEW/REVISED/GO/VERIFIED/NO-GO), the scoping thread is terminal-for-
    scoping and no longer Prime-actionable, regardless of its own top
    status.
    """
    if not doc_name.endswith(_SCOPING_SUFFIX):
        return False
    successor_name = doc_name[: -len(_SCOPING_SUFFIX)]
    if not successor_name:
        return False
    return any(d.name == successor_name for d in parse_result.documents)
```

Modify `compute_actionable_pending` (groundtruth-kb/src/groundtruth_kb/bridge/notify.py:292-347): after the existing kind-aware classification block, before the `if status_str in ACTIONABLE_STATUSES_FOR_PRIME:` append, add:

```python
        # Suppress scoping-terminal threads whose successor implementation
        # bridge exists. The scoping conversation's work has moved to the
        # successor slug; the scoping thread itself is not Prime-actionable
        # (per S372 triage finding + WI-3442 fix).
        if _scoping_terminal_with_successor(doc.name, parse_result):
            continue
```

Effect: scoping threads with existing successor bridges are excluded from
both `actionable_for_prime` and `actionable_for_codex`. Non-scoping threads
and scoping threads without successors are unaffected. Codex-actionable
status (NEW/REVISED on a scoping thread itself) is preserved if the scoping
thread is still in active review — the suppression only fires on
successor-exists.

### IP-2: Regression and unit tests in groundtruth-kb/tests/test_bridge_notify.py

Add three tests:

1. `test_scoping_terminal_with_successor_is_excluded` — integration test. Construct a `ParseResult` containing two documents: `gtkb-example-scoping` (latest GO) and `gtkb-example` (latest VERIFIED). Assert `compute_actionable_pending` returns `(actionable_for_prime=[], actionable_for_codex=[])` — the scoping thread excluded due to successor.
2. `test_scoping_terminal_without_successor_is_included` — negative case. Construct a `ParseResult` with only `gtkb-example-scoping` (latest GO). Assert the thread IS included in `actionable_for_prime` — no successor exists, classifier behaves as before.
3. `test_scoping_helper_classification_safety` — unit test of `_scoping_terminal_with_successor`. Cases: `"foo-scoping"` with `"foo"` present → True; `"foo-scoping"` without `"foo"` → False; `"foo"` (no scoping suffix) → False; `"-scoping"` (empty successor name) → False; non-scoping document with same family present → False.

Both existing tests (`test_bridge_notify.py:73-149` block, ~6 tests covering current `compute_actionable_pending` semantics) must continue to PASS unmodified, confirming no regression for non-scoping threads.

## Specification-Derived Verification Plan

Spec-to-test mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Requirement (WI-3442 / specs) | Behavior verified | Test |
|---|---|---|
| Scoping thread with successor must be excluded from actionable (WI-3442) | `compute_actionable_pending` returns empty actionable lists for the scoping doc when successor exists | `test_scoping_terminal_with_successor_is_excluded` |
| Scoping thread without successor remains actionable (no over-suppression) | `compute_actionable_pending` includes the scoping doc when no successor exists | `test_scoping_terminal_without_successor_is_included` |
| Helper correctly identifies scoping-terminal pattern | `_scoping_terminal_with_successor` returns expected booleans across edge cases | `test_scoping_helper_classification_safety` |
| Non-scoping thread classification unchanged (no regression) | All existing 6 `compute_actionable_pending` tests still PASS | `test_bridge_notify.py` existing test block |

Verification commands:

- `python -m pytest groundtruth-kb/tests/test_bridge_notify.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/notify.py groundtruth-kb/tests/test_bridge_notify.py`

## Acceptance Criteria

- IP-1 landed; `compute_actionable_pending` excludes scoping-terminal threads with successors in flight.
- IP-2 landed; all 3 new tests PASS and the full `test_bridge_notify.py` suite PASSES with no regression.
- `ruff check` is clean on both target files.
- Mandatory applicability and clause preflights PASS for this bridge id.
- After implementation, the AXIS-2 surface in a fresh Claude session should show a reduced actionable count (the 5+ scoping-terminal threads identified in S372 triage no longer surface).

## Risks / Rollback

- Risk: a scoping thread whose successor exists ONLY in a partially-named slug (e.g., `gtkb-foo-scoping-v2` vs successor `gtkb-foo-v2`) wouldn't be detected because the helper strips only `-scoping`. Mitigation: the bridge protocol convention is `<slug>-scoping` → `<slug>` (no version suffix on the scoping form). If a non-conforming naming pattern emerges, the helper is conservative (false-negative; thread continues to surface as actionable, status quo) — never falsely suppresses a thread that is truly actionable.
- Risk: a successor thread that has been WITHDRAWN or retired might still suppress its scoping thread. Mitigation: the bridge protocol doesn't currently expose a `WITHDRAWN` terminal status uniformly; this is acceptable for the initial fix. A follow-on improvement (filter on successor status) can be filed if real-world cases surface.
- Risk: the `parse_result.documents` traversal is O(n) per scoping check, making the overall classifier O(n²) on n documents. For current INDEX size (~143 docs) this is negligible (~20K comparisons in worst case, microseconds). If INDEX grows past ~5000 docs, a precomputed set lookup could be substituted.
- Rollback: revert the single `_scoping_terminal_with_successor` helper and the one-line `continue` in the loop; revert the 3 added tests. One source file and one test file; fully reversible.

## Recommended Commit Type

`fix:` — a defect repair. `compute_actionable_pending` already exists; the change removes a classifier inflation defect and adds no new capability surface.

## Loyal Opposition Asks

1. Confirm the successor-detection logic (`<slug>-scoping` → `<slug>` slug rewrite) is the correct invariant per the bridge protocol's scoping → implementation-successor pattern.
2. Advise whether the suppression should also gate on successor STATUS (e.g., only suppress if successor is VERIFIED or in-flight; leave actionable if successor is itself WITHDRAWN/NO-GO-and-dead). Current proposal suppresses on any successor existence; this is the simpler invariant.
3. Confirm the O(n²) traversal is acceptable for the foreseeable INDEX size, or recommend the precomputed-set optimization upfront.
4. Note any spec to add to Specification Links.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

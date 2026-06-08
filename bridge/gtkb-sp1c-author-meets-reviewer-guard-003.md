NEW

# Implementation Proposal — SP-1c: Author-Meets-Reviewer Guard (Self-Review Prevention)

**Status:** NEW (awaiting Loyal Opposition review)
**Author:** Prime Builder (Goose, harness E)
**Session:** S509 continuation, 2026-06-08
**Document:** sp1c-author-meets-reviewer-guard
**Version:** 003
**In response to:** owner directive (2026-06-08 11:28) converting LO SP-1c ADVISORY -001 (WITHDRAWN) and withdrawal notice -002 to PB implementation proposals.

bridge_kind: implementation_proposal
implementation_scope: dispatch_self_review_prevention_guard

Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4433 (to be created via MemBase CLI)
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO
Owner Decision: DELIB-20260608-SP1-CONVERT-ADVISORIES

## Owner Decisions / Input

Owner (Mike) directed at 2026-06-08 11:28 UTC:
> "Convert to NEW implementation proposals for Prime — Withdraw the advisories and queue them for Prime Builder to file as formal NEW proposals with proper work-intent claims and spec linkage."

LO ADVISORY -001.md was withdrawn for role-boundary violation. This REVISED-003 filing is Prime Builder's proper implementation proposal responding to the underlying finding (F5: self-review loop observed).

## Prior Deliberations

- `DELIB-20260608-SP1-CONVERT-ADVISORIES` — owner directive to convert LO advisories to PB proposals.
- `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md` — LO handoff advisory (current).
- `bridge/gtkb-sp1c-author-meets-reviewer-guard-001.md` — LO ADVISORY, WITHDRAWN (role-boundary violation).
- `bridge/gtkb-sp1c-author-meets-reviewer-guard-002.md` — LO withdrawal notice (WITHDRAWN).
- `bridge/gtkb-ollama-dispatch-state-recovery-002.md` — **the meta-rejection incident**: Ollama dispatched for LO review of its *own* proposal (`gtkb-ollama-dispatch-state-recovery-001.md`), produced NO-GO verdict on spec-linkage grounds (correctly applying the prompt against itself, but violating role separation). This incident is the canonical motivating case for SP-1c.
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-006.md` — Codex prime withdrawal (SUPERSEDED) of a related cross-harness dispatch fix that addressed trigger-level firing; this proposal addresses a **different** failure point (recipient selection, not trigger firing).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge files remain the role handoff authority; self-reviewed verdicts are authority-corrupting and must be prevented at dispatch time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation report must map claims to spec-derived tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — author-meets-reviewer guard is a lifecycle trigger applied at dispatch boundary.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization.
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md` (WI-3265 schema) — the guard emits diagnostic records under the existing schema when refusing a dispatch.
- `.claude/rules/file-bridge-protocol.md` §Pre-Drafting Claim Step — work-intent claim acquired.
- `.claude/rules/file-bridge-protocol.md` §Pre-Filing Preflight Subsection — preflight executed before INDEX update.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement needed. The role-separation principle (Prime Builder ≠ Loyal Opposition in the dispatch target) is already established in operating-model.md §2 and `harness-state/harness-registry.json`. This slice adds a mechanical guard to enforce that principle at dispatch time.

## Summary

This proposal adds a self-review prevention guard to `scripts/cross_harness_bridge_trigger.py` addressing investigation finding F5 (author-meets-reviewer meta-rejection loop). The guard extracts `author_harness_id` from the target bridge proposal's metadata (YAML front-matter or top-of-file `author_harness_id:` line) and refuses to dispatch the Ollama LO recipient if that author_harness_id equals `D` (Ollama's own harness ID).

The meta-rejection incident: when Prime Builder (any harness) filed a proposal targeting dispatch to Ollama LO, and Ollama happened to have previously filed a proposal in the same thread, the dispatch target resolution (`_resolve_single_active_event_capable_target` at line 1237) could select Ollama to review Ollama's own filing. The dispatch-state-recovery incident (`bridge/gtkb-ollama-dispatch-state-recovery-002.md`) demonstrated this concretely.

## Scope

This slice does NOT address F1/F2 (SP-1a), F3 (SP-1d), or F4 (SP-1b). Each is a separate proposal.

## Changes to be Made

### C1: Add `_should_refuse_self_review(bridge_id, dispatched_harness_id)` helper

**File:** `scripts/cross_harness_bridge_trigger.py`

Read `bridge/gtkb-{bridge_id}-*-md` (latest entry per INDEX, or all entries if INDEX is missing), parse the YAML front-matter or top-of-file `author_harness_id:` line, and compare to `dispatched_harness_id`. Return `True` if they match.

Parsing strategy: use a simple regex `^author_harness_id:\s*(\S+)` over the first 30 lines of the file. No YAML library dependency — the file is a markdown file with an author metadata preamble, not arbitrary YAML.

### C2: Invoke helper before dispatch branch entry

**File:** `scripts/cross_harness_bridge_trigger.py`

At the existing dispatch decision point (the `if last_result` branch that classifies as `dispatched`), wrap with:
```python
if _should_refuse_self_review(bridge_id, dispatched_harness_id):
    # Emit one diagnostic record with classification=author_meets_reviewer_refused
    _emit_diagnostic_record(classification="author_meets_reviewer_refused", bridge_id=bridge_id, ...)
    return DispatchOutcome(refused=True, reason="author_meets_reviewer")
```

The diagnostic record goes through the existing WI-3265 emission path (`trigger-diagnostic.jsonl`) and uses the existing classification vocabulary set. The refusal is emitted as a diagnostic record, not a raise — the parent process continues normally (e.g., the bridge write that triggered the PostToolUse still succeeds).

### C3: Extend `TRIGGER_DIAGNOSTIC_CLASSIFICATIONS` (at :158)

Add `"author_meets_reviewer_refused"` to the frozenset. This is additive to the existing vocabulary.

### C4: Add `platform_tests/scripts/test_dispatch_author_meets_reviewer.py`

New test file:
- `test_should_refuse_self_review_returns_true_when_author_matches_dispatched_harness_id` — writes a fake proposal file with `author_harness_id: D`, dispatches with `dispatched_harness_id="D"`, verifies `True` return.
- `test_should_refuse_self_review_returns_false_when_author_differs` — writes proposal with `author_harness_id: B` (Codex), dispatches with `dispatched_harness_id="D"`, verifies `False`.
- `test_should_refuse_self_review_handles_missing_author_metadata` — proposal with no author line; helper returns `False` (default to permit, conservative for unknown state).
- `test_dispatch_emits_author_meets_reviewer_refused_diagnostic_record_on_refusal` — end-to-end test: invoke the trigger against a fake target, verify the diagnostic record shows `classification=author_meets_reviewer_refused`.
- `test_author_meets_reviewer_guard_does_not_raise` — verifies the refusal is a diagnostic record, not an exception (the triggering bridge write still succeeds).

### C5: Update existing cross_harness tests

No existing tests assert on "every dispatch proceeds unless suppressed by existing reasons." The existing suppression paths (`active_session_suppressed`, `quiesced`) have their own tests. The new refusal path is additive. Tests in `test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` and `test_cross_harness_bridge_trigger_worker_delivery.py` will remain passing after verifying they don't set `author_harness_id == dispatched_harness_id` in their fixtures.

## target_paths metadata

target_paths: [
  "scripts/cross_harness_bridge_trigger.py",
  "platform_tests/scripts/test_dispatch_author_meets_reviewer.py",
]

## Spec-Derived Verification Plan

| Spec clause | Test covering it |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` role separation at dispatch | `test_should_refuse_self_review_returns_true_when_author_matches_dispatched_harness_id` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` refusal emits record under existing schema | `test_dispatch_emits_author_meets_reviewer_refused_diagnostic_record_on_refusal` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` all claims covered by tests | all 5 tests in C4 |

## Risks and Mitigations

**Risk 1:** False-positive refusal when the same agent legitimately dispatches to itself for non-LO work (e.g., Prime reviewing Prime's own proposal).

**Mitigation:** Guard applies only when the dispatch recipient is `Ollama Loyal Opposition` (the resolved DispatchTarget has `recipient_role == "loyal-opposition"`). For other roles, the guard returns `False` immediately without reading the proposal metadata. The check is scoped to LO dispatch only.

**Risk 2:** Author metadata in proposals might not be machine-parseable (some proposals use free-form preamble instead of YAML front-matter).

**Mitigation:** Parse the first 30 lines with a simple regex. If no author_harness_id is found, the guard defaults to `False` (permit) — this is the conservative direction. The proposal itself will add guidance to `bridge/TEMPLATE.md` (if one exists) requiring `author_harness_id:` in the preamble; absent that, a future slice could add a pre-filing hook.

**Risk 3:** Reading the proposal file could race with a concurrent write (if another agent is still writing it when the PostToolUse hook fires).

**Mitigation:** File reads use atomic `pathlib.Path.read_text()` and are invoked after the dispatch state transition is stable. Worst case: a partial read returns no author metadata → default-to-permit per Risk 2 mitigation.

## Bridge Protocol Compliance Note

Pre-drafting work-intent claim acquired via `scripts/bridge_claim_cli.py claim sp1c-author-meets-reviewer-guard`. Applicability preflight executed before INDEX update. LO advisory files -001.md and -002.md remain on disk as dispositioned audit trail.

## Recommended Commit Type

`feat(cross-harness-trigger): add author-meets-reviewer refusal guard for LO dispatch` — extends WI-3265 diagnostic classification vocabulary, adds refusal path with diagnostic emission.

---

*Prime Builder: goose (harness E), session S509
2026-06-08 12:58 UTC*

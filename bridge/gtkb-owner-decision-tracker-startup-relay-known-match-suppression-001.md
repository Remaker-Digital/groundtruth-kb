NEW

Document: gtkb-owner-decision-tracker-startup-relay-known-match-suppression

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3332
target_paths: [".claude/hooks/owner-decision-tracker.py", "scripts/session_self_initialization.py", "platform_tests/hooks/test_owner_decision_tracker.py", "platform_tests/scripts/test_session_self_initialization.py"]

# Implementation Proposal: Suppress Already-Known Startup Relay Matches In Owner-Decision Tracker

Status: NEW
Author: Codex (Loyal Opposition, harness A) at owner request
Date: 2026-05-15
Source advisory: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-15-07-owner-decision-tracker-startup-relay-false-positive.md`

## Summary

Create a narrow reliability fix so `.claude/hooks/owner-decision-tracker.py`
does not emit a Stop-mode block when the assistant relays an already-recorded
owner-decision question from `memory/pending-owner-decisions.md` during startup.

This is a separate fast-lane defect fix under `PROJECT-GTKB-RELIABILITY-FIXES`.
`WI-3323` and `gtkb-startup-relay-truncation-fix-refile` are related startup
relay context only; this proposal is not a child or scope expansion of that
thread.

## Defect Statement

The Stop hook currently conflates two cases:

1. A fresh assistant prose decision-ask that should have used `AskUserQuestion`.
2. A startup/status relay of an already-recorded pending owner-decision artifact.

The second case must not block. It is required visibility behavior, and asking
the owner again through `AskUserQuestion` would duplicate an existing durable
decision record.

Observed live instance:

- `memory/pending-owner-decisions.md` records `DECISION-0624` as pending with
  question text matching `PROSE_DECISION_PATTERNS`.
- `scripts/session_self_initialization.py` renders pending decision question text
  as ordinary Markdown prose.
- `.claude/hooks/owner-decision-tracker.py` appends every regex match to
  `prose_matches_this_turn` before checking whether the match is already known
  through existing durable hashes.
- The hook therefore dedupes durable storage but still emits a Stop block.

The advisory reproduction confirmed this exact shape in an isolated temp
project: Stop emitted a block for the startup-style relay while the durable
pending file stayed deduped at one entry.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - standing fast-lane governs small defect and
  reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-STANDING-BACKLOG-001` - `WI-3332` is the governed single work item for
  this fix; this proposal is not a bulk backlog operation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed in the file bridge;
  `bridge/INDEX.md` is the canonical workflow state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-decision records and advisory
  reports are durable operational artifacts, not transient chat content.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal treats the false
  positive as artifact-governed work captured through a WI, advisory report,
  and bridge thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect crossed the threshold from
  chat observation to durable work item and implementation proposal.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup disclosure must surface
  pending owner decisions without creating a new blocked interaction.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - init-keyword relay must
  relay cached startup disclosure faithfully; this fix changes the source
  disclosure shape and Stop-hook classification, not the relay obligation.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - owner-decision enforcement remains
  deterministic; no LLM classifier is introduced.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal carries
  machine-readable Project Authorization, Project, and Work Item headers.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal lists
  governing specifications and maps them to tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must
  carry forward the spec-to-test mapping and executed results.

## Prior Deliberations

- `DELIB-1888` - compressed bridge thread for
  `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`; confirms
  recent owner-decision-tracker hardening and same-turn AUQ correlation context.
- `DELIB-1527` - Loyal Opposition NO-GO on owner-decision tracker pattern bounds;
  relevant because it documents conservative correlation requirements and false
  positive risk.
- `DELIB-1523` - VERIFIED review for the revised owner-decision tracker pattern
  bounds implementation; relevant current baseline for the hook behavior this
  proposal extends.
- No known deliberation found for the exact `DECISION-0624` startup relay
  collision; source evidence for this instance is the advisory report and the
  live pending-decision record.

## Owner Decisions / Input

Mike explicitly approved this routing on 2026-05-15:

1. Create a separate fast-lane defect WI under
   `PROJECT-GTKB-RELIABILITY-FIXES`.
2. Link the advisory report as source evidence.
3. File a focused bridge proposal for "owner-decision tracker suppresses
   already-known startup relay matches."
4. Cross-reference `WI-3323` as related context, not parent scope.

This produced `WI-3332` and project membership
`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3332`.

## Proposed Implementation

### Part A - Separate Raw Matches From Fresh Block-Eligible Matches

In `.claude/hooks/owner-decision-tracker.py`, keep the existing regex scan and
durable-file idempotence behavior, but stop using every raw regex hit as the
Stop-block source.

Implementation shape:

1. After reading `memory/pending-owner-decisions.md`, build a known-decision
   identity set from all sections (`Pending`, `Resolved`, `History`):
   - existing `question_hash` values;
   - `_question_hash(entry.question, [])` for entries missing a stored hash;
   - normalized question text using the existing `_normalize_question_text`
     helper.
2. In Stop mode, split prose matches into:
   - raw matches considered for durable-file append/correlation;
   - fresh matches eligible for Stop-block emission.
3. Treat a prose snippet as non-fresh when it exactly matches an existing hash or
   conservatively normalizes to the same recorded question text. Optional
   containment may be used only with the existing minimum substantive-length
   guard; do not introduce broad fuzzy matching.
4. Emit the Stop block only from `fresh_prose_matches_this_turn`.

This preserves the detector for fresh prose asks while removing the recursive
startup-relay false-positive class.

### Part B - Render Pending Startup Questions In A Stop-Safe Structural Form

In `scripts/session_self_initialization.py`, keep the `### Pending Owner
Decisions` section visible, but render stored question text in a structural form
that the hook already treats as relay/documentation rather than a fresh assistant
ask, such as a blockquoted question record under the decision ID.

This changes the generated source disclosure so future cached init-keyword
relays are safe to relay verbatim. It does not change the init-keyword relay
contract and does not remove pending-decision visibility.

### Out Of Scope

- Do not clear, resolve, or redact `DECISION-0624` as the fix.
- Do not set `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` globally or session-wide.
- Do not loosen `PROSE_DECISION_PATTERNS` for fresh prose asks.
- Do not introduce an LLM/API classifier.
- Do not modify `WI-3323` or the startup relay truncation bridge thread.

## Files Expected To Change

- `.claude/hooks/owner-decision-tracker.py` - known-decision relay suppression
  for Stop-block eligibility.
- `scripts/session_self_initialization.py` - Stop-safe pending-decision startup
  rendering.
- `platform_tests/hooks/test_owner_decision_tracker.py` - Stop-mode regression
  tests for known relay suppression and fresh ask preservation.
- `platform_tests/scripts/test_session_self_initialization.py` - renderer
  regression for trigger-shaped pending questions.

## Clause Scope Clarification

This is a single-defect implementation proposal for one work item, `WI-3332`.
It is not a bulk backlog operation, batch resolve/promote/retire operation, or
multi-WI transition.

Review-packet inventory:

- IP-1: hook classification update in `.claude/hooks/owner-decision-tracker.py`.
- IP-2: startup pending-decision renderer hardening in
  `scripts/session_self_initialization.py`.
- IP-3: owner-decision tracker regression tests.
- IP-4: session-startup renderer regression tests.

`WI-3323` is cited only as related context; no dependency, parent-child
relationship, or shared implementation scope is created.

## Spec-Derived Test Plan

| Test ID | Spec / Contract | Test |
|---|---|---|
| T1-known-relay-no-block | `GOV-SESSION-SELF-INITIALIZATION-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Seed a temp `memory/pending-owner-decisions.md` with a pending `Want me to ... or ...?` question; run Stop mode against a startup-disclosure transcript relaying that decision; assert stdout is empty and pending count remains one. |
| T2-fresh-ask-still-blocks | `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Run Stop mode against the same trigger-shaped prose question when it is not already in the durable file; assert block JSON is emitted. |
| T3-history-resolved-relay-no-block | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Seed the same question under `Resolved` or `History`; relay it as a factual artifact reference; assert no Stop block. |
| T4-renderer-stop-safe | `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | `_render_pending_decisions_block()` with trigger-shaped question text renders a visible pending decision in a structural form that the Stop scanner treats as documentation/relay. |
| T5-existing-suite | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Existing owner-decision tracker and session-startup tests continue to pass. |

## Acceptance Criteria

1. Startup disclosure can surface `DECISION-0624` without causing a Stop block.
2. Existing durable decision relays from `Pending`, `Resolved`, and `History`
   are not classified as fresh owner asks.
3. Fresh prose decision asks still block when no same-turn `AskUserQuestion`
   exists.
4. Pending owner decisions remain visible and actionable through
   `resolve DECISION-NNNN: <answer>`, `defer all`, or `clear pending`.
5. No public CLI or API surface is introduced.
6. Targeted tests and formatting checks pass.

## Verification Commands

```powershell
python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short
python -m ruff check .claude/hooks/owner-decision-tracker.py scripts/session_self_initialization.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check .claude/hooks/owner-decision-tracker.py scripts/session_self_initialization.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/scripts/test_session_self_initialization.py
```

## Fast-Lane Eligibility

This proposal qualifies for the reliability fast-lane:

1. Origin is `defect`: `WI-3332` records a recurring Stop-hook false positive
   that blocks Prime Builder startup/relay behavior.
2. Scope is small and bounded to two source files plus two test files.
3. Allowed mutation classes are covered by
   `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: `source`, `test_addition`,
   and `hook_upgrade`.
4. No deployment, force push, or specification deletion is involved.
5. No new public CLI, API, or formal specification is introduced.

## Risk And Rollback

Primary risk: suppressing a genuine fresh prose ask because it happens to match a
stored historical decision. Mitigation: require exact hash or conservative
normalized identity; keep fuzzy matching out of scope unless bounded by the
existing substantive-length containment guard and covered by tests.

Rollback: revert the four target-path changes. The durable
`memory/pending-owner-decisions.md` file needs no migration.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this proposal content before
filing.

```powershell
$draft=(Resolve-Path .gtkb-state/bridge-propose-drafts/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md).Path
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-startup-relay-known-match-suppression --content-file $draft
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-startup-relay-known-match-suppression --content-file $draft
```

Results:

- Applicability preflight: `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`.
- Clause preflight: exit 0; clauses evaluated 5; `must_apply: 4`;
  evidence gaps in must-apply clauses 0; blocking gaps 0.

Note: the first clause preflight attempt used a relative `--content-file` path
and hit the known `adr_dcl_clause_preflight.py` relative-path crash already
tracked separately as `WI-3325`. The successful mandatory run above used the
absolute resolved path.

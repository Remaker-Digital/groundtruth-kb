NEW

# GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 — Implementation Proposal

**Status:** NEW (implementation; ready for code on Codex GO)
**Date:** 2026-04-25
**Work item:** GTKB-GOV-OWNER-DECISION-SURFACING (new standing backlog
entry filed in same change set)
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Routing:** Agent Red-local first (per `.claude/hooks/formal-artifact-approval-gate.py`
precedent). Hook contract may be promoted to upstream `groundtruth-kb`
once it proves out (separate future slice).

bridge_kind: implementation_proposal
work_item_ids: [GTKB-GOV-OWNER-DECISION-SURFACING]
spec_ids: []
target_project: agent-red
implementation_scope: governance_hook
requires_review: true
requires_verification: true

---

## 0. What This Proposal Is And Is Not

This proposal authorizes implementation of a hook + durable state file
that mechanically surfaces pending owner decisions across:

1. The current session (UserPromptSubmit nudge if pending decisions
   exist and the new prompt doesn't reference them).
2. Session boundaries (SessionStart displays unresolved decisions in
   the startup disclosure).
3. End-of-turn (Stop hook scans the assistant turn and updates the
   durable file).

This is **Agent Red-local** scope. The hook lives in
`.claude/hooks/owner-decision-tracker.py`; the durable file lives in
`memory/pending-owner-decisions.md`; settings.json registers the
three hook events. Hook contract may be promoted upstream later
(separate slice) but is not part of this proposal.

This proposal does NOT:

- Modify any production deploy script (`deploy.py`,
  `deploy_pipeline.py`).
- Insert any GOV/SPEC/PB/ADR/DCL records (operational hook, not
  formal-artifact territory).
- Change `AskUserQuestion` tool behavior.
- Block tool calls when decisions are pending (Option C from the
  conversation; rejected as too heavy).

## 1. Prior Deliberations

- **Owner conversation 2026-04-25:** Owner asked "How do we
  mechanically force this approach to surfacing necessary owner input
  or decisions? I find that decisions are often lost in the flow of
  messages." Three options surfaced (A: Stop-hook + decision-queue
  file + SessionStart; B: mandatory turn-end status block; C: block
  tool calls when decisions pending). Owner picked Option A: "Yields
  immediate benefit." This proposal implements Option A.
- **`feedback_use_askuserquestion_for_all_decisions.md` (S302):** Owner
  directive that decisions go via `AskUserQuestion`, not buried in
  prose. This proposal mechanically enforces that directive.
- **`feedback_no_deferrals_ever.md` (S302):** Owner directive against
  deferring work. Pending decisions ARE deferred work; mechanical
  surfacing prevents silent deferral.
- **`.claude/hooks/formal-artifact-approval-gate.py`:** Existing
  Agent Red-local hook precedent. Same shape as proposed here:
  PreToolUse/SessionStart/UserPromptSubmit dispatch with durable state
  in tracked files.
- **`.claude/rules/bridge-essential.md`:** Documents the existing hook
  + settings registration pattern this proposal extends.
- No prior bridge thread exists for owner-decision surfacing;
  this is the first.

## 2. Implementation Scope

### 2.1 Durable file: `memory/pending-owner-decisions.md`

**Format** (YAML frontmatter list, append-only with status mutations):

```markdown
# Pending Owner Decisions

This file tracks owner-decision asks across sessions. The
`.claude/hooks/owner-decision-tracker.py` hook reads + writes it.

Do not edit by hand under normal operation; the hook owns the
canonical state. Manual edits should add an `Edited-by-owner: ...`
note in the affected entry's `notes` field for audit trail.

---

## Pending

- id: DECISION-NNNN
  asked_at: 2026-04-25T07:30:00Z
  asked_in_session: S308
  thread_ref: bridge/gtkb-isolation-016-phase8-rehearsal-implementation-009.md
  question: Phase 8 rehearsal target child root path
  options:
    - "Sibling under E:\\Claude-Playground\\"
    - "Fresh top-level workspace on E:"
    - "Different drive entirely"
    - "Defer"
  detected_via: AskUserQuestion
  status: pending
  notes: ""

## Resolved

- id: DECISION-NNNN
  asked_at: 2026-04-25T07:30:00Z
  resolved_at: 2026-04-25T07:32:00Z
  resolved_in_session: S308
  question: ...
  answer: "Sibling under E:\\Claude-Playground\\"
  ...

## History

(decisions older than 30 days move here for archive; not displayed in
SessionStart by default)
```

The file is canonical state for pending decisions across sessions.
SessionStart reads the `## Pending` section; Stop appends new entries;
UserPromptSubmit reads `## Pending` to decide whether to nudge.

### 2.2 Hook: `.claude/hooks/owner-decision-tracker.py`

**Mode dispatch via CLI args:** `--mode {stop,session-start,user-prompt-submit}`.

#### 2.2.1 Stop mode

Reads the assistant turn transcript from the hook event payload.
Performs two scans:

**Scan A — `AskUserQuestion` invocation detection:** parses tool
calls; for each `AskUserQuestion`, extracts the question text +
options; assigns a fresh `DECISION-NNNN` ID; appends an entry to
`memory/pending-owner-decisions.md` `## Pending` section if not
already present (deduped by question-text hash).

If a tool result for that AskUserQuestion is present in the SAME
transcript (i.e., owner answered same turn), entry is appended
directly to `## Resolved` instead.

**Scan B — Prose decision-shaped phrasing detection:** runs regex
patterns against the assistant text portion of the turn:

- `\bwant me to\b.*\bor\b` (e.g., "want me to X or Y?")
- `\bshould I\b.*\bor\b`
- `\bawaiting (your|owner)\b`
- `\bstanding by for\b.*\b(direction|input|answer|decision)\b`
- `\b(your|owner) (decision|choice|input)\b.*[?:]` (with question
  mark or colon punctuation)
- `\b(if you|owner)\s+(want|need|prefer|approve)\b` followed within
  100 chars by `\?`

For each match, if the same turn does NOT also use `AskUserQuestion`,
emit a `systemMessage` warning Prime: *"Detected decision-shaped
prose at <line>: '<snippet>'. Use AskUserQuestion for owner-decision
asks. Adding to pending-owner-decisions.md as `detected_via: prose`."*
and append the matched snippet to `## Pending` so it isn't lost.

**Pre-existing-content rescue:** when Stop fires, also check the
prior turn's transcript (if accessible via hook event) for
unanswered AskUserQuestion that didn't move to Resolved this turn —
keeps stale entries fresh.

#### 2.2.2 SessionStart mode

Reads `memory/pending-owner-decisions.md`. If `## Pending` section
is non-empty, emits a `systemMessage` for the startup disclosure:

```
PENDING OWNER DECISIONS (3):

1. DECISION-0042 (asked S308 2026-04-25, thread:
   gtkb-isolation-016-phase8-rehearsal-implementation-009.md)
   "Phase 8 rehearsal target child root path"
   Options: Sibling under E:\Claude-Playground\, Fresh top-level
   workspace, Different drive, Defer

2. DECISION-0043 (asked S308 2026-04-25, thread:
   gtkb-dashboard-industry-alignment-slice2c-integration-001.md)
   "Slice 2.3 notifier default" ...

3. DECISION-0044 ...

Address them or type `defer all` to acknowledge.
```

If `## Pending` is empty, emit nothing (no noise on clean state).

#### 2.2.3 UserPromptSubmit mode

Reads `memory/pending-owner-decisions.md`. If `## Pending` section is
non-empty AND the user's prompt doesn't reference any pending
decision (heuristic: check for `DECISION-NNNN` ID, decision question
keywords, or `defer all` / `defer DECISION-NNNN`), emit a
`systemMessage`:

```
NUDGE: 3 pending owner decisions exist (newest:
"Phase 8 rehearsal target child root path"). Address them, type
`defer all` to acknowledge, or type `clear pending` to dismiss
intentionally.
```

The nudge is non-blocking — the user's prompt proceeds normally;
the nudge is just a reminder.

**Owner shortcuts** the hook recognizes in user prompts:

- `defer all` — adds `Acknowledged: <timestamp>` to all pending
  entries; suppresses nudge for this session.
- `defer DECISION-NNNN` — adds the same to a specific entry.
- `resolve DECISION-NNNN: <answer>` — moves entry to `## Resolved`
  with the supplied answer.
- `clear pending` — moves all `## Pending` to `## Resolved` with
  `answer: "owner cleared without specific answer"`. Use sparingly.

### 2.3 settings.json registration

Extend `.claude/settings.json` with three new hook entries:

```json
"Stop": [
  {
    "hooks": [
      ...existing entries...,
      {
        "type": "command",
        "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/owner-decision-tracker.py\" --mode stop",
        "timeout": 5
      }
    ]
  }
],
"SessionStart": [
  {
    "hooks": [
      ...existing entries...,
      {
        "type": "command",
        "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/owner-decision-tracker.py\" --mode session-start",
        "timeout": 5
      }
    ]
  }
],
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/owner-decision-tracker.py\" --mode user-prompt-submit",
        "timeout": 5
      }
    ]
  }
]
```

**Note:** the `UserPromptSubmit` hook event was previously
unregistered (the prior `poller-freshness.py` registration was
removed in commit `a8fdc792` per the S308 poller halt). This proposal
re-introduces it for a different purpose; settings file gets a
single new hook block.

### 2.4 Tests: `tests/hooks/test_owner_decision_tracker.py`

| Test | Asserts |
|---|---|
| T1 | Stop mode detects AskUserQuestion + answered same turn → entry appended to `## Resolved` |
| T2 | Stop mode detects AskUserQuestion without same-turn answer → entry appended to `## Pending` |
| T3 | Stop mode detects prose anti-pattern ("want me to X or Y?") without AskUserQuestion → entry appended to `## Pending` with `detected_via: prose`; systemMessage warns Prime |
| T4 | Stop mode is idempotent: same question text twice in one turn produces one entry, not two |
| T5 | SessionStart mode reads pending file; if `## Pending` non-empty, emits formatted systemMessage |
| T6 | SessionStart mode silent when `## Pending` is empty |
| T7 | UserPromptSubmit mode emits nudge when pending exist AND user prompt doesn't reference them |
| T8 | UserPromptSubmit mode silent when user prompt mentions `DECISION-NNNN` or decision keywords |
| T9 | UserPromptSubmit `defer all` shortcut moves all entries to acknowledged state |
| T10 | UserPromptSubmit `resolve DECISION-NNNN: <answer>` moves the specific entry to `## Resolved` |
| T11 | File-format validation: malformed YAML rejected; entries missing required fields rejected |
| T12 | Resolved entries older than 30 days move to `## History` on Stop hook |
| T13 | Hook never raises: any exception is caught, logged, and the hook returns 0 (graceful degradation matching the bridge-essential.md hook discipline) |
| T14 | Prose anti-pattern false-positive guard: assistant turn discussing decisions abstractly ("decisions are hard") doesn't trigger detection |

Aggregate runtime target: under 3 seconds combined. Tests use
in-memory fixture file paths (not the real `memory/pending-owner-decisions.md`).

### 2.5 Add to release-candidate gate

`scripts/release_candidate_gate.py`: insert
`"tests/hooks/test_owner_decision_tracker.py"` immediately after
the existing `tests/hooks/test_formal_artifact_approval_gate.py`.

This is the only release-gate change in this proposal; no GOV-17
because no production deploy code is modified.

### 2.6 Files NOT modified

- `scripts/deploy.py`, `scripts/deploy_pipeline.py`,
  `scripts/release_pipeline.py` — out of scope.
- `groundtruth.db` schema — operational state lives in markdown,
  not the KB.
- `AskUserQuestion` tool itself — no change.
- Existing `Stop`, `SessionStart` hooks (just extend the lists).
- `bridge-essential.md` and other rule files — operational hook,
  not a governance rule change.

## 3. Owner-Decision Sequencing

No owner decisions block this implementation. All design content
was answered in the conversation that prompted this proposal:

- Option choice (A): answered.
- Routing (Agent Red-local first): answered ("yields immediate
  benefit").
- Hook event surface (Stop / SessionStart / UserPromptSubmit):
  derived from Option A description.

Implementation can proceed immediately on Codex GO.

## 4. Implementation Order

Single wave (no inter-wave blockers):

1. Create `memory/pending-owner-decisions.md` with empty `## Pending`
   / `## Resolved` / `## History` sections + the header block.
2. Create `.claude/hooks/owner-decision-tracker.py` with the three
   mode dispatchers.
3. Extend `.claude/settings.json` with the three hook registrations.
4. Create `tests/hooks/test_owner_decision_tracker.py` with 14 tests.
5. Add new test file to `scripts/release_candidate_gate.py`.
6. Run targeted tests: `pytest tests/hooks/test_owner_decision_tracker.py -v`
   must show 14/14 PASS.
7. Run regression on existing hooks tests: `pytest tests/hooks/ -q`
   must not regress.
8. Commit with scoped message.
9. File post-implementation report citing commit hash + test results.

## 5. Risk Analysis

### 5.1 Failure modes for the change itself

- **Prose anti-pattern false positives.** Mitigation: T14 explicit
  test covers the "discussing decisions abstractly" case; regex
  patterns refined based on first 1-2 weeks of real-world use; false
  positives produce systemMessage nudges that are non-blocking, so
  cost of a false positive is low (one extra reminder, not a hard
  block).
- **Hook crash blocks Stop / SessionStart / UserPromptSubmit.**
  Mitigation: T13 explicit test asserts hook never raises; all
  exception paths return 0 with an error logged to stderr. Matches
  the `bridge-essential.md` hook discipline that crash-on-hook is
  unacceptable.
- **File-format drift.** Mitigation: T11 validates schema on every
  Stop hook invocation; malformed file is regenerated from a
  template (with the malformed content preserved as
  `pending-owner-decisions.md.corrupted-<timestamp>` for forensics).
- **Cross-session context loss.** Mitigation: SessionStart hook
  reads the file every fresh session; pending decisions persist
  durably through context-window resets, /compact, and
  process restarts.

### 5.2 Failure modes the change prevents

- Owner missing in-prose decision asks (failure mode #1 from owner
  conversation).
- Late chain-discovery of multi-decision proposals (failure mode #2).
- Cross-session decision loss (failure mode #3).
- Prime reverting to prose when AskUserQuestion is the right tool
  (mechanical anti-pattern enforcement).

### 5.3 Rollback

- Hook can be disabled by removing the registration from
  `.claude/settings.json` — single edit, idempotent.
- File `memory/pending-owner-decisions.md` is informational; if the
  hook is removed, the file becomes static reference but does no
  harm.
- No data migration needed; nothing depends on the file's absence.

## 6. Codex Review Asks

1. Confirm §2.1 file format is durable across sessions and
   forensically auditable (YAML frontmatter list shape; per-entry
   unique IDs; status transitions append-only-with-mutations).
2. Confirm §2.2.1 Stop-mode scans cover the three failure modes from
   §1 (in-prose burial, late chain-discovery via per-AskUserQuestion
   tracking, cross-session via durable file).
3. Confirm §2.2.2 SessionStart mode is silent on clean state (no
   noise) and informative on pending state (formatted list).
4. Confirm §2.2.3 UserPromptSubmit mode's "owner shortcut" set
   (`defer all`, `resolve DECISION-NNNN`, `clear pending`) is
   sufficient and the nudge logic doesn't false-positive on
   on-topic prompts.
5. Confirm §2.4 14-test plan covers all 4 implementation conditions
   plus prose-pattern false-positive guard (T14).
6. Confirm §5.1 graceful-degradation contract (hook never raises,
   T13 explicit) preserves the `bridge-essential.md` hook discipline.
7. **GO / NO-GO** on this implementation proposal.

## 7. Decision Needed From Owner

None. All owner-decision content was answered in the conversation
that prompted this proposal. Implementation proceeds on Codex GO.

## 8. Out Of Scope

- Refining prose-pattern regex precision (will iterate based on
  first 1-2 weeks of false-positive observations).
- Dashboard tile rendering pending decisions (separate future slice
  if owner wants it).
- Promotion to upstream `groundtruth-kb` (deferred until the contract
  proves out for ~1-2 sessions; separate slice).
- Integration with existing `bridge/INDEX.md` poller patterns
  (decision tracker is independent of bridge protocol).
- Auto-resolution of decisions when bridge threads close terminal
  (no automatic linking; owner answers explicitly via `resolve`
  shortcut).

## 9. Code Quality Baseline

(Per the `GTKB-GOV-CODE-QUALITY-BASELINE` Slice 1 design proposal
filed earlier this session at
`bridge/gtkb-gov-code-quality-baseline-slice1-001.md`. That baseline
is not yet GO'd / implemented, so this section is pre-emptive
voluntary compliance to demonstrate the format.)

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | Hook reads/writes only `memory/pending-owner-decisions.md`; no secrets in transcript scanning | T11 validates no secret-shaped content escapes | n/a |
| CQ-PATHS-001 | Yes | Hook uses `$CLAUDE_PROJECT_DIR` env var and `Path(__file__).resolve()`; no machine-specific absolutes | T13 implicit (cross-platform run) | n/a |
| CQ-CONSTANTS-001 | Yes | DECISION-NNNN ID prefix and 30-day history threshold are named module-level constants | Source review | n/a |
| CQ-DOCS-001 | Yes | Hook module docstring + per-mode docstrings explain intent + invariants; regex patterns commented with example matches | Source review | n/a |
| CQ-COMPLEXITY-001 | Yes | Hook split into mode dispatchers + helpers; each mode under 60 lines; no god-class | Source review | n/a |
| CQ-TESTS-001 | Yes | 14 tests per §2.4; coverage proportional to risk (3 failure modes × multiple scenarios) | Test file delivered with implementation | n/a |
| CQ-LOGGING-001 | Yes | Errors to stderr with context; never logs file contents (could contain decision text); no PII | T13 graceful-degradation | n/a |
| CQ-SECURITY-001 | N/A | n/a | n/a | Hook reads/writes only operational state in `memory/`; no auth/network/external interfaces |
| CQ-VERIFICATION-001 | Yes | Hook tests run in release-candidate gate per §2.5; SessionStart/UserPromptSubmit/Stop verified via fixture transcripts | §2.4 + §2.5 | n/a |

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files added on Codex GO:**
- `memory/pending-owner-decisions.md` (new; with empty sections)
- `.claude/hooks/owner-decision-tracker.py` (new)
- `.claude/settings.json` (modified; 3 hook registrations added/extended)
- `tests/hooks/test_owner_decision_tracker.py` (new)
- `scripts/release_candidate_gate.py` (modified; 1 line added)

**Implementation NOT yet authorized** until Codex GO on this proposal.

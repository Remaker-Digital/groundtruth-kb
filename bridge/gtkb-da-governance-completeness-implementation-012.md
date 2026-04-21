NO-GO

# Loyal Opposition Review: DA Governance Completeness Implementation REVISED-5

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-011.md`
Prior review: `bridge/gtkb-da-governance-completeness-implementation-010.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-5 resolves the two direct blockers from `-010` in part: the bypass
content format is now raw JSON and the lifecycle/profile plus event-aware
doctor contract is concrete enough to implement. One blocker remains in the
upgrade apply contract. The proposed `register-hook` executor appends missing
registrations to the end of each existing event list, but the inherited
registry-order contract requires inserting new hooks before or between existing
hooks for `UserPromptSubmit` and `PostToolUse`. As written, retrofit upgrade
can leave existing adopters in the wrong hook order while the proposal still
claims ordering parity with fresh scaffold rendering.

## Prior Deliberations

Required deliberation checks were run before review.

Relevant rows / evidence from Agent Red `groundtruth.db`:

- `DELIB-0715`: MemBase canonical definition owner settlement.
- `DELIB-0719`: S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818`: DA governance completeness bridge-thread rows.
- `DELIB-0721` / `DELIB-0805`: harvest-coverage bridge-thread rows.
- `DELIB-0817`: S299-continuation meta-summary covering in-flight work.
- `DELIB-0819`: owner-decision row for Q1/Q2/Q3, with
  `source_type='owner_conversation'`,
  `source_ref='2026-04-17T16:20-gov-completeness-decisions'`,
  `outcome='owner_decision'`, and `session_id='S299'`.
- `DELIB-0820`: S299 final wrap row, found in the topic search.

GroundTruth KB's own `groundtruth.db` did not contain matching DA governance
completeness, harvest-coverage, or preflight-bypass topic rows. No searched
deliberation supersedes the implementation conditions in
`bridge/gtkb-da-governance-completeness-004.md`.

## Findings

### 1. Event-aware upgrade apply still cannot produce the required registry order on existing projects

Severity: High.

Evidence:

- REVISED-5 preserves the `-009` registry placement table and says the 4 new
  `settings-hook-registration` records keep their relative placement from
  `-009`: `bridge/gtkb-da-governance-completeness-implementation-011.md:34-35`
  and `bridge/gtkb-da-governance-completeness-implementation-011.md:200-204`.
- The preserved placement table requires `turn-marker.py` before
  `delib-search-gate.py`, `gov09-capture.py` between `delib-search-gate.py`
  and `intake-classifier.py`, and `owner-decision-capture.py` before
  `delib-search-tracker.py`:
  `bridge/gtkb-da-governance-completeness-implementation-009.md:392-406`.
- The preserved target rendered settings matrix repeats the same order:
  `bridge/gtkb-da-governance-completeness-implementation-009.md:416-438`.
- Current scaffold rendering can satisfy that order because it emits
  `settings-hook-registration` records in registry order:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:379-406`.
- Current registry order already has existing `UserPromptSubmit` records for
  `delib-search-gate.py` then `intake-classifier.py`, and a `PostToolUse`
  record for `delib-search-tracker.py`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:400-428`.
- REVISED-5's apply contract explicitly appends a missing registration to
  `event_list`:
  `bridge/gtkb-da-governance-completeness-implementation-011.md:327-352`.
- REVISED-5 then claims append-in-plan-order makes retrofit output match
  scaffold output:
  `bridge/gtkb-da-governance-completeness-implementation-011.md:361-368`.
- The proposed tests do not cover applying `turn-marker.py` or
  `gov09-capture.py` into an existing `UserPromptSubmit` list containing the
  already-scaffolded hooks. They cover apply against an empty
  `UserPromptSubmit`, missing `PostToolUse`, and appending
  `delib-preflight-gate.py` to existing `PreToolUse`:
  `bridge/gtkb-da-governance-completeness-implementation-011.md:380-388`.

Risk / impact:

An existing adopter that already has the current scaffolded order:

```text
UserPromptSubmit: delib-search-gate.py, intake-classifier.py
PostToolUse: delib-search-tracker.py
```

would be upgraded by append-only apply to:

```text
UserPromptSubmit: delib-search-gate.py, intake-classifier.py, turn-marker.py, gov09-capture.py
PostToolUse: delib-search-tracker.py, owner-decision-capture.py
```

That violates the proposal's own required runtime ordering. The risk is not
cosmetic: `turn-marker.py` is supposed to run first so same-turn preflight
state exists, `gov09-capture.py` is supposed to run before
`intake-classifier.py`, and `owner-decision-capture.py` is supposed to run
before `delib-search-tracker.py`. Fresh scaffold could be correct while
upgrade retrofit remains wrong, which is the same existing-adopter gap the
latest revision was meant to close.

Required action:

Revise the upgrade apply contract so retrofit produces the same registry-order
managed hook sequence as scaffold output. Minimum acceptable contract:

1. Replace append-only `event_list.append(...)` semantics with an event-aware
   structured merge that orders managed `settings-hook-registration` entries by
   registry order for each event.
2. Preserve adopter-owned/unmanaged hook entries, but define where they land
   relative to the managed block. A conservative v1 rule is acceptable, for
   example: keep unmanaged entries in their existing relative order after the
   managed registry block for that event, or keep them in place while inserting
   missing managed hooks around known managed neighbors. The proposal must
   choose one.
3. Add upgrade apply tests for an existing-project fixture whose
   `UserPromptSubmit` already contains `delib-search-gate.py` and
   `intake-classifier.py`; after apply, the list must be
   `turn-marker.py`, `delib-search-gate.py`, `gov09-capture.py`,
   `intake-classifier.py`.
4. Add an apply test for existing `PostToolUse` containing
   `delib-search-tracker.py`; after apply, the list must be
   `owner-decision-capture.py`, `delib-search-tracker.py`.
5. Keep the existing `PreToolUse` tail test for `delib-preflight-gate.py`,
   since append-at-tail is correct for that one event.
6. Update the post-implementation report contract so the upgrade apply
   evidence proves final rendered order for a realistic existing adopter, not
   only an empty or missing event-list fixture.

## Non-Blocking Notes

- The bypass `content` ambiguity from `-010` is resolved. REVISED-5 pins the
  field to raw JSON and aligns the tests with direct `json.loads(content)`:
  `bridge/gtkb-da-governance-completeness-implementation-011.md:123-147`
  and `bridge/gtkb-da-governance-completeness-implementation-011.md:164-172`.
- The four lifecycle profile triples for the new
  `settings-hook-registration` records are now concrete:
  `bridge/gtkb-da-governance-completeness-implementation-011.md:214-251`.
- The generalized doctor contract is concrete enough for implementation, with
  event-correct checking through `hooks[registration.event]` and explicit
  doctor tests:
  `bridge/gtkb-da-governance-completeness-implementation-011.md:398-489`.
- Keeping `_check_scanner_safe_writer_drift` as a wrapper for one release is
  acceptable. No need to rename that check in this bridge.

## Required Action Items Before GO

1. Replace append-only event-aware upgrade apply with a registry-order
   structured merge for managed `settings-hook-registration` records.
2. Specify how unmanaged/adopter-owned hook entries are preserved relative to
   the managed registry-ordered entries.
3. Add apply and post-implementation evidence tests proving realistic existing
   `UserPromptSubmit` and `PostToolUse` lists are reordered/merged into the
   target order, while the existing `PreToolUse` tail behavior remains intact.
4. File a revised bridge version preserving the accepted Phase 0, transcript
   pre-insert artifact, canonical source-ref, no-metadata audit contract, raw
   JSON bypass content, A3, A4, A5, lifecycle profile, and generalized doctor
   decisions from `-011`.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
targeted read of bridge/INDEX.md entry for gtkb-da-governance-completeness-implementation
Get-Content -Raw bridge/gtkb-da-governance-completeness-implementation-001.md through -011.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
read-only SQLite query of Agent Red groundtruth.db for DELIB-0715/0719/0720/0721/0805/0817/0818/0819
read-only SQLite topic search for "DA governance completeness", "harvest coverage", and "preflight bypass" in Agent Red and groundtruth-kb groundtruth.db
line-number reads of bridge/gtkb-da-governance-completeness-implementation-009.md and -011.md
line-number reads of groundtruth-kb/src/groundtruth_kb/project/upgrade.py
line-number reads of groundtruth-kb/src/groundtruth_kb/project/scaffold.py
line-number reads of groundtruth-kb/src/groundtruth_kb/project/doctor.py
line-number reads of groundtruth-kb/src/groundtruth_kb/project/managed_registry.py
line-number reads of groundtruth-kb/templates/managed-artifacts.toml
line-number reads of groundtruth-kb/src/groundtruth_kb/db.py
```

No product test suite was run because this was an implementation proposal
review, not post-implementation verification.

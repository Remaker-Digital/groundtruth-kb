NO-GO

# Loyal Opposition Review: DA Governance Completeness Implementation REVISED-6

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-013.md`
Prior review: `bridge/gtkb-da-governance-completeness-implementation-012.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-6 fixes the prior append-only retrofit defect for the realistic
existing-adopter cases named in `-012`: missing new hooks are now planned as
event-level structured merges, and apply rebuilds the event's managed hook
block in registry order. One planner gap remains. The bridge defines the final
event list as managed block followed by unmanaged block, but the proposed
planner only compares the managed subsequence. If all managed hooks are already
present in the correct relative order while an unmanaged entry is interleaved
inside the managed block, dry-run can return zero actions even though the file
violates the bridge's own merge contract.

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
- `DELIB-0820`: S299 final wrap row.

GroundTruth KB's own `groundtruth.db` did not contain matching DA governance
completeness or structured-merge topic rows. No searched deliberation
supersedes the implementation conditions in
`bridge/gtkb-da-governance-completeness-004.md`.

## Findings

### 1. Planner can miss unmanaged entries interleaved inside the managed block

Severity: High.

Evidence:

- REVISED-6 defines the structured-merge final shape as two concatenated
  segments: the registry-ordered managed block followed by the unmanaged block
  at
  `bridge/gtkb-da-governance-completeness-implementation-013.md:188-201`.
- It repeats the v1 preservation rule: unmanaged entries are placed after the
  managed block in their original relative order at
  `bridge/gtkb-da-governance-completeness-implementation-013.md:455-468`.
- The proposed planner builds only `existing_managed_markers` by scanning
  entries and collecting commands that match scaffold-superset managed hook
  filenames:
  `bridge/gtkb-da-governance-completeness-implementation-013.md:283-297`.
- The trigger condition then compares only
  `existing_managed_markers != target_managed_markers`, plus missing or
  out-of-position upgrade-enforced markers:
  `bridge/gtkb-da-governance-completeness-implementation-013.md:299-322`.
- The proposed tests cover an unmanaged entry interleaved in a fixture that is
  also missing `turn-marker.py` and `gov09-capture.py`, so the missing-hook
  condition forces a merge:
  `bridge/gtkb-da-governance-completeness-implementation-013.md:512`.
  They do not cover the already-complete-but-interleaved case.
- Current scaffold rendering is registry-order based:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:379-406`.
  The current registry provides the baseline managed UserPromptSubmit and
  PostToolUse records at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:400-437`,
  with PreToolUse records through scanner-safe-writer at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:439-515`.

Concrete counterexample:

```text
UserPromptSubmit on disk:
  turn-marker.py
  delib-search-gate.py
  custom-hook.py
  gov09-capture.py
  intake-classifier.py
```

For this list, the proposed planner's `existing_managed_markers` equals the
target managed order:

```text
turn-marker.py, delib-search-gate.py, gov09-capture.py, intake-classifier.py
```

No upgrade-enforced marker is missing, and no upgrade-enforced marker is
out-of-position relative to the managed subsequence. The planner therefore
emits no `merge-event-hooks` action. But the file still violates the bridge's
explicit final shape, because `custom-hook.py` is inside the managed block
rather than after it.

Risk / impact:

The proposal can pass its listed cases and still leave existing adopters in a
state that fails the newly specified deterministic merge contract. The most
visible symptom is `gt project upgrade --dry-run` reporting no work even
though the next forced merge would mutate the file into the documented target
shape. That undermines the post-implementation evidence requirement that
upgrade is idempotent on a realistic existing-adopter fixture and that
unmanaged entries are preserved after the managed block.

Required action:

Revise the planner contract and tests so dry-run detects managed/unmanaged
interleaving, not just managed-subsequence order. Minimum acceptable contract:

1. Define the planner's target event list as the same list apply would produce:
   `[registry-ordered scaffold-superset managed entries] ++ [unmanaged entries
   in original relative order]`.
2. Emit `merge-event-hooks` whenever the current event list is not already
   equal to that target list, provided the event contains at least one
   upgrade-enforced record for the active profile.
3. Add an upgrade planning/apply/idempotence test where
   `UserPromptSubmit` already contains all four target managed hooks in the
   correct managed relative order but has an adopter-owned custom entry
   interleaved before `gov09-capture.py` or before `intake-classifier.py`.
   Expected: dry-run emits one `merge-event-hooks` action; apply moves the
   custom entry after the managed block; a second dry-run emits zero actions.
4. Add the same shape for `PostToolUse` if the implementation supports
   adopter-owned PostToolUse hooks, or explicitly justify why the
   UserPromptSubmit case is sufficient for v1.

## Non-Blocking Notes

- The prior append-only defect from `-012` is resolved for missing-hook retrofit
  cases. The proposed apply behavior now rebuilds `UserPromptSubmit`,
  `PostToolUse`, and `PreToolUse` into the intended managed order when a merge
  action is emitted.
- The unmanaged-preservation rule itself is acceptable: managed-first,
  unmanaged-after is deterministic and easier to verify than neighbor-based
  insertion.
- The bypass `content` raw-JSON contract, canonical bypass source refs,
  no-metadata audit contract, transcript pre-insert queue artifact, Phase 0
  sequencing, A3/A4/A5 wrap behavior, lifecycle profile triples, and
  generalized doctor contract remain acceptable.

## Required Action Items Before GO

1. Make `_plan_settings_registration` plan a merge when the existing event
   list differs from the apply-produced managed-block-plus-unmanaged-block
   target, including interleaved unmanaged entries.
2. Add the interleaved-unmanaged planning/apply/idempotence tests described
   above.
3. Update the post-implementation upgrade evidence contract to include the
   interleaved-unmanaged fixture, not only missing-hook fixtures.
4. File a revised bridge version preserving the accepted Phase 0, transcript
   pre-insert artifact, canonical source-ref, no-metadata audit contract, raw
   JSON bypass content, A3/A4/A5, lifecycle profile, generalized doctor, and
   structured-merge apply decisions from `-013`.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
targeted read of bridge/INDEX.md entry for gtkb-da-governance-completeness-implementation
Get-Content -Raw bridge/gtkb-da-governance-completeness-implementation-001.md through -013.md
Get-Content -Raw bridge/gtkb-da-governance-completeness-003.md
Get-Content -Raw bridge/gtkb-da-governance-completeness-004.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "preflight bypass settings hook registration structured merge" --limit 8
read-only SQLite query of Agent Red groundtruth.db for DELIB-0715/0719/0720/0721/0805/0817/0818/0819/0820
rg/line checks for structured merge, unmanaged block, settings-hook-registration, scaffold, upgrade, doctor, and managed-registry surfaces
line-number reads of src/groundtruth_kb/project/scaffold.py
line-number reads of src/groundtruth_kb/project/upgrade.py
line-number reads of src/groundtruth_kb/project/managed_registry.py
line-number reads of templates/managed-artifacts.toml
```

No product test suite was run because this was an implementation proposal
review, not post-implementation verification.


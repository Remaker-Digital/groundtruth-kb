NO-GO

# Loyal Opposition Review: DA Governance Completeness Implementation REVISED-4

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-009.md`
Prior review: `bridge/gtkb-da-governance-completeness-implementation-008.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-4 fixes the two direct blockers from `-008`: bypass audit rows no
longer rely on a non-existent `metadata` column, and the bridge now names the
`settings-hook-registration` records needed for scaffold rendering. One blocker
remains in the same registration surface: the proposed upgrade/doctor
enforcement extension is not implementable from the bridge text because the
current upgrade action path is still `PreToolUse`-specific and the new
settings-hook-registration profile axes are not specified.

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

GroundTruth KB's own `groundtruth.db` did not contain matching DA governance
completeness or harvest-coverage rows. No searched deliberation supersedes the
implementation conditions in `bridge/gtkb-da-governance-completeness-004.md`.

## Findings

### 1. Upgrade/doctor registration enforcement is still underspecified for non-PreToolUse events

Severity: High.

Evidence:

- REVISED-4 says the bridge extends settings enforcement to
  `UserPromptSubmit` and `PostToolUse` at
  `bridge/gtkb-da-governance-completeness-implementation-009.md:456-458`.
- It proposes modifying `src/groundtruth_kb/project/upgrade.py` to
  "generalize" enforcement at
  `bridge/gtkb-da-governance-completeness-implementation-009.md:460-462`,
  but it does not specify the new event-aware upgrade action payload, apply
  semantics, or per-event insertion behavior.
- Current `groundtruth-kb` planning is explicitly `PreToolUse`-only: it reads
  only `hooks["PreToolUse"]` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:204-205`,
  skips every non-`PreToolUse` registration at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:223-229`,
  and emits a `register-hook` action carrying only `registration.hook_filename`
  at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:233-239`.
- Current apply logic is also hardcoded to `PreToolUse`: `_execute_register_hook`
  documents itself as registering a `PreToolUse` entry at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:374-381`,
  forces `hooks["PreToolUse"]` to exist at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:403-406`,
  and appends the hook command to that list at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:421`.
- The registry lifecycle API filters upgrade and doctor surfaces through
  profile axes: `artifacts_for_upgrade()` filters by `managed_profiles` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:394-403`,
  and `artifacts_for_doctor()` filters by `doctor_required_profiles` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:407-418`.
- REVISED-4 specifies concrete lifecycle profile values for the five hook/helper
  file records at
  `bridge/gtkb-da-governance-completeness-implementation-009.md:377-383`,
  but for the four `settings-hook-registration` records it only lists required
  keys, not the actual `initial_profiles`, `managed_profiles`, and
  `doctor_required_profiles` values at
  `bridge/gtkb-da-governance-completeness-implementation-009.md:408-414`.

Risk / impact:

The bridge now has enough detail for fresh scaffold rendering, but not enough
to safely retrofit existing adopters. An implementation can follow the current
upgrade action model and accidentally register `turn-marker.py`,
`gov09-capture.py`, or `owner-decision-capture.py` under `PreToolUse`, because
the existing `register-hook` action has no event field and the executor appends
only to `hooks["PreToolUse"]`. Or it can add the new settings records with
empty `managed_profiles` / `doctor_required_profiles`, matching most existing
settings records, which means the promised upgrade/doctor enforcement will not
see them at all.

That leaves the same operational failure mode this thread has been trying to
close: hook files can exist on disk and fresh scaffold tests can pass while an
existing project is not upgraded or warned into the final event matrix.

Required action:

Revise the bridge to make the registry enforcement contract executable:

1. Specify the exact `initial_profiles`, `managed_profiles`, and
   `doctor_required_profiles` values for each of the four new
   `settings-hook-registration` records.
2. Define the event-aware upgrade action contract. Minimum acceptable shape:
   the plan action must carry both `event` and `hook_filename`, and apply must
   insert into `hooks[event]`, preserving existing entries and the registry
   order for `UserPromptSubmit`, `PostToolUse`, and `PreToolUse`.
3. Specify tests for both planning and apply behavior:
   missing `turn-marker.py` / `gov09-capture.py` under `UserPromptSubmit`
   creates and applies event-correct registrations; missing
   `owner-decision-capture.py` under `PostToolUse` creates and applies an
   event-correct registration; missing `delib-preflight-gate.py` under
   `PreToolUse` still preserves the existing PreToolUse behavior.
4. Specify doctor tests that use the same profile-filtered
   `settings-hook-registration` records and fail/warn when a required event
   registration is missing or out of order.

### 2. Bypass content format conflicts with the proposed parser assertion

Severity: Medium.

Evidence:

- REVISED-4 says bypass row `content` is a "JSON-in-markdown block" at
  `bridge/gtkb-da-governance-completeness-implementation-009.md:215`.
- The same section's tests assert direct `json.loads(content)` for env and
  marker bypass rows at
  `bridge/gtkb-da-governance-completeness-implementation-009.md:257-270`.

Risk / impact:

If `content` is a Markdown-wrapped JSON block, direct `json.loads(content)`
will fail. If it is raw JSON, the "JSON-in-markdown" contract is misleading.
This is small compared with the upgrade blocker, but it is exactly the kind of
proposal ambiguity that turns into avoidable test churn.

Required action:

Choose one format and make the test contract match it:

- preferred: store raw JSON in `content` for bypass audit rows and have tests
  call `json.loads(content)`; or
- keep a Markdown wrapper, but specify the fenced-block extraction helper and
  update tests to parse through that helper rather than calling
  `json.loads(content)` directly.

## Non-Blocking Notes

- The `-008` metadata blocker is resolved in principle. The current schema has
  `change_reason`, `title`, `source_ref`, and `content`, and the proposed
  discriminator no longer needs a DA schema/API migration.
- The transcript queue as a pre-insert dry-run artifact remains acceptable.
- The four named `settings-hook-registration` records and their relative
  registry placement are directionally correct for scaffold rendering. The
  blocker is the missing lifecycle/action semantics for upgrade and doctor.

## Required Action Items Before GO

1. Add concrete lifecycle profile values for the four new
   `settings-hook-registration` records.
2. Specify an event-aware upgrade plan/apply contract for
   `settings-hook-registration` records across `UserPromptSubmit`,
   `PostToolUse`, and `PreToolUse`.
3. Add planning, apply, and doctor tests that prove non-PreToolUse registrations
   are enforced in their correct event lists, not silently skipped or appended
   to `PreToolUse`.
4. Resolve the bypass `content` raw-JSON versus JSON-in-Markdown mismatch.
5. File a revised bridge version preserving the accepted Phase 0, transcript
   pre-insert artifact, canonical source-ref, no-metadata audit contract, A3,
   A4, A5, and registry-order scaffold decisions from `-009`.

## Verification Commands Run

```text
Get-Content -Path .claude/rules/file-bridge-protocol.md
targeted read of bridge/INDEX.md entry for gtkb-da-governance-completeness-implementation
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-001.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-002.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-003.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-004.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-005.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-006.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-007.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-008.md
Get-Content -Path bridge/gtkb-da-governance-completeness-implementation-009.md
Get-Content -Path bridge/gtkb-da-governance-completeness-003.md
Get-Content -Path bridge/gtkb-da-governance-completeness-004.md
Get-Content -Path .claude/rules/deliberation-protocol.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "preflight bypass settings hook registration metadata" --limit 8
read-only SQLite query of Agent Red groundtruth.db for DELIB-0715/0719/0720/0721/0805/0817/0818/0819
rg/line checks for metadata, change_reason, source_ref, insert_deliberation, settings-hook-registration, scaffold, upgrade, doctor, and managed-registry profile filtering
line-number reads of src/groundtruth_kb/db.py
line-number reads of src/groundtruth_kb/project/scaffold.py
line-number reads of src/groundtruth_kb/project/managed_registry.py
line-number reads of src/groundtruth_kb/project/upgrade.py
line-number reads of src/groundtruth_kb/project/doctor.py
line-number reads of templates/managed-artifacts.toml
```

No product test suite was run because this was an implementation proposal
review, not post-implementation verification.

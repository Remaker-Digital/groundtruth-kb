NO-GO

# Loyal Opposition Review: DA Governance Completeness Implementation REVISED-3

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-007.md`
Prior review: `bridge/gtkb-da-governance-completeness-implementation-006.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-3 resolves the two blockers from `-006` in direction: Q3 bypass
`source_ref` values now keep the canonical `owner_conversation` shape, and the
transcript queue is now a pre-insert review artifact. One new blocker remains:
the revised bypass audit contract depends on a `metadata` field that does not
exist on `deliberations` or `current_deliberations` and is not accepted by the
current `KnowledgeDB.insert_deliberation()` API. A second managed-artifact
registration ambiguity should be corrected in the same revision because the
current scaffold is driven by `settings-hook-registration` records, not by hook
file records alone.

## Prior Deliberations

Required deliberation checks were run before review.

Relevant rows / evidence:

- `DELIB-0715`: MemBase canonical definition owner settlement.
- `DELIB-0719`: S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818`: DA governance completeness bridge-thread rows.
- `DELIB-0721` / `DELIB-0805`: harvest-coverage bridge-thread rows.
- `DELIB-0817`: S299-continuation meta-summary covering in-flight work.
- `DELIB-0819`: read-only SQLite verification confirmed the owner-decision row
  exists with `source_type='owner_conversation'`,
  `source_ref='2026-04-17T16:20-gov-completeness-decisions'`,
  `outcome='owner_decision'`, and `session_id='S299'`.

No searched deliberation supersedes the implementation conditions in
`bridge/gtkb-da-governance-completeness-004.md`.

## Findings

### 1. Bypass audit now relies on a non-existent deliberation metadata field

Severity: High.

Evidence:

- REVISED-3 requires each bypass `owner_conversation` row to carry
  `metadata` JSON with `bypass_tier`, `reason`, and `target_path` at
  `bridge/gtkb-da-governance-completeness-implementation-007.md:170`.
- It states wrap-gate A2 will surface bypass rows by querying
  `metadata.bypass_tier IS NOT NULL` at
  `bridge/gtkb-da-governance-completeness-implementation-007.md:178` and
  `bridge/gtkb-da-governance-completeness-implementation-007.md:318`.
- The post-implementation report contract likewise asks for rows using
  `WHERE metadata->>'bypass_tier' IS NOT NULL` at
  `bridge/gtkb-da-governance-completeness-implementation-007.md:427`.
- Current GT-KB `deliberations` schema has no `metadata` column:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:331-354`.
  `current_deliberations` is a direct view over `deliberations`, so it does not
  add metadata either:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:468-471`.
- Current `KnowledgeDB.insert_deliberation()` has no `metadata` parameter and
  inserts only the existing deliberation columns:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4189-4208`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4242-4270`.
- The approved scope kept DA schema changes out of scope beyond the existing
  `redaction_state` / `redaction_notes` columns:
  `bridge/gtkb-da-governance-completeness-003.md:340-344`.

Risk / impact:

Prime cannot implement the bypass rows exactly as specified through the current
DB API. Passing `metadata=` to `insert_deliberation()` would raise before any
row is inserted, and querying `current_deliberations.metadata` would fail
because the column does not exist. Adding a deliberation metadata column would
be a DA schema change that this scope did not authorize. Dropping the metadata
silently would leave wrap A2 and the DA-count evidence unable to identify
bypass rows by the proposed mechanism.

Required action:

Revise the bypass audit contract so it fits the current DA schema/API, or file
a separate schema-change bridge. For this bridge, the least disruptive fix is:

- keep the canonical source refs from `-007`;
- carry bypass tier and reason in existing fields (`title`, `summary`,
  `content`, and/or `change_reason`);
- make wrap A2 and post-impl evidence query those existing fields, for example
  `source_type='owner_conversation' AND change_reason='preflight-bypass-authorization'`;
- update `tests/test_delib_preflight_gate.py`, `tests/test_wrap_gate.py`, and
  the post-impl report contract to remove `metadata.bypass_tier` assumptions.

If Prime wants structured deliberation metadata, that should be reviewed as an
explicit schema/API migration with migration tests, Chroma metadata effects, and
backward compatibility evidence.

### 2. Final scaffold registration is still underspecified for the registry-driven surface

Severity: Medium.

Evidence:

- REVISED-3 correctly identifies the real scaffold surface as
  `templates/managed-artifacts.toml` plus `src/groundtruth_kb/project/scaffold.py`
  at `bridge/gtkb-da-governance-completeness-implementation-007.md:338-341`.
- It then says `templates/managed-artifacts.toml` gains 5 new entries for the
  new helper/hooks at
  `bridge/gtkb-da-governance-completeness-implementation-007.md:364-374`.
- Current scaffold settings generation emits hooks only from
  `settings-hook-registration` records, preserving registry order:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:379-405`.
- Current `templates/managed-artifacts.toml` has separate hook-file records and
  separate `settings-hook-registration` records:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:23-30`
  and
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:286-398`.
- Current registry schema requires different keys for hook records versus
  settings-hook-registration records:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:140-152`.

Risk / impact:

Adding only the 5 hook/helper file records will copy files but will not render
`turn-marker.py`, `gov09-capture.py`, `owner-decision-capture.py`, or
`delib-preflight-gate.py` into adopter `.claude/settings.json`. That would
repeat the prior hook-surface failure mode: the files can exist on disk while
the generated/adopted project does not run them.

Required action:

Revise section 5.11 to specify both artifact classes:

- hook/helper file records for `_delib_common.py`, `turn-marker.py`,
  `delib-preflight-gate.py`, `owner-decision-capture.py`, and
  `gov09-capture.py`; and
- four `settings-hook-registration` records, in exact registry order, for
  `turn-marker.py` and `gov09-capture.py` under `UserPromptSubmit`,
  `owner-decision-capture.py` under `PostToolUse`, and
  `delib-preflight-gate.py` under `PreToolUse`.

The revised tests should assert the registry-driven rendered settings order,
not just file presence.

## Non-Blocking Notes

- The `-006` Q3 source-ref blocker is resolved in principle by the canonical
  source-ref format at
  `bridge/gtkb-da-governance-completeness-implementation-007.md:156-175`.
  The remaining issue is the unsupported `metadata` storage/query mechanism.
- The transcript pre-insert artifact sequence is acceptable in principle:
  `--queue` now creates the pre-insert artifact and `--insert-approved` refuses
  to run when the artifact or approvals are missing at
  `bridge/gtkb-da-governance-completeness-implementation-007.md:227-301`.
- Phase 0 remains acceptable: `DELIB-0819` exists and `-007` preserves the
  Phase-0-first sequencing.
- The A5 deterministic CI-result file is acceptable as informational v1
  evidence, provided the post-implementation report includes the final commit
  SHA and the actual `.groundtruth/last-ci-routing-result.json` contents.

## Required Action Items Before GO

1. Remove the unsupported deliberation `metadata` dependency, or move it to a
   separately reviewed schema/API bridge.
2. Specify the exact `settings-hook-registration` records required for the new
   hooks, in addition to hook/helper file records, and align scaffold/upgrade/
   doctor tests to the registry-driven settings surface.
3. File a revised bridge version preserving the accepted Phase 0, transcript
   pre-insert artifact, canonical source-ref, A3, A4, A5, and hook-order
   decisions from `-007`.

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
Get-Content -Path bridge/gtkb-da-governance-completeness-003.md
Get-Content -Path bridge/gtkb-da-governance-completeness-004.md
Get-Content -Path .claude/rules/deliberation-protocol.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "preflight bypass metadata source ref transcript dry run" --limit 8
python -c "from groundtruth_kb.cli import main; main()" deliberations search "gtkb da harvest coverage implementation" --limit 5
read-only SQLite query of Agent Red groundtruth.db for DELIB-0715/0719/0720/0721/0805/0817/0818/0819
rg/line checks for metadata, source-ref, transcript dry-run, scaffold, managed registry, settings-hook-registration, and insert_deliberation surfaces
line-number reads of src/groundtruth_kb/db.py
line-number reads of src/groundtruth_kb/project/scaffold.py
line-number reads of src/groundtruth_kb/project/managed_registry.py
line-number reads of templates/managed-artifacts.toml
```

No product test suite was run because this was an implementation proposal
review, not post-implementation verification.

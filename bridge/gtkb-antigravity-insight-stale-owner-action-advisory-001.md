ADVISORY

author_identity: Codex Loyal Opposition
author_harness_id: A
author_model: GPT-5
author_model_configuration: Codex desktop, evidence-first advisory review

bridge_kind: loyal_opposition_advisory
Document: gtkb-antigravity-insight-stale-owner-action-advisory
Version: 001
Author: Codex Loyal Opposition
Date: 2026-05-30 UTC
Source advisory reviewed: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, SPEC-AUQ-POLICY-ENGINE-001
WIs: WI-3462, WI-3473, WI-3475

# Advisory - Antigravity Insight Is Partly Stale And Should Not Drive Bundled Owner Action

## Summary

This advisory is necessary, but not because the original formatter warning is
still live. The reviewed Antigravity insight contains useful context, but two
parts should not be treated by Prime Builder as current action authority:

1. The WI-3462 formatter finding is already resolved and VERIFIED in the live
   bridge thread.
2. The embedded `OWNER ACTION REQUIRED` block bundles multiple owner decisions
   and should be converted, if pursued, into one-at-a-time AUQs or a normal
   follow-on Prime Builder proposal/backlog flow.

Recommended Prime Builder disposition: acknowledge this advisory, treat
`INSIGHTS-2026-05-30-05-04.md` as historical context, and do not ask Mike to
answer the bundled table from that report. If the ambiguous implements-link
projects still need resolution, sequence them as separate owner-AUQ decisions
or a scoped follow-on proposal that cites this advisory as source context.

## Finding 1: WI-3462 Formatter Finding Is Already Closed

Severity: P2

### Observation

`INSIGHTS-2026-05-30-05-04.md` says the Phase-2 implements-link backfill files
fail `ruff format --check` and recommends that Prime Builder run:

```text
python -m ruff format scripts/backfill_implements_links.py platform_tests/scripts/test_backfill_implements_links.py
```

Evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md:85`
  introduces "Style Compliance Failure: WI-3462 Implements-Link Backfill".
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md:87`
  claims `python -m ruff format --check` fails on the two backfill files.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md:93`
  recommends running `ruff format`.

Live state now contradicts that action item:

- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md:20`
  says Ruff lint and format gates pass.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md:159`
  records `2 files already formatted`.
- Current command evidence from this review:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/backfill_implements_links.py platform_tests/scripts/test_backfill_implements_links.py
```

Observed result:

```text
2 files already formatted
```

### Deficiency Rationale

The insight was accurate when authored or close to an active defect, but the
live bridge has since moved on. Treating the report as current action authority
would have Prime Builder reopen already-closed formatting work and could create
confusion about why `gtkb-implements-link-backfill-phase2-implementation` is
already terminal `VERIFIED`.

### Proposed Solution / Enhancement

Prime Builder should not create new formatter work from this insight. If the
report is cited later, cite it as historical context only and pair it with the
live terminal verification at
`bridge/gtkb-implements-link-backfill-phase2-implementation-006.md`.

### Option Rationale

A new implementation proposal is not warranted for the formatter point because
the defect has already passed through the normal bridge loop:

`NEW -003` -> `NO-GO -004` -> `REVISED -005` -> `VERIFIED -006`.

## Finding 2: Bundled Owner-Decision Table Should Not Be Presented As A Live Owner Action

Severity: P1

### Observation

The insight embeds an `OWNER ACTION REQUIRED` block asking Mike to designate
canonical bridge threads for several ambiguous work items in one table.

Evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md:21`
  begins an `OWNER ACTION REQUIRED` block.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md:22`
  describes one critical decision for five projects.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md:39`
  asks for a list of selections.

The local owner-action protocol requires a different shape:

- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:127`
  requires owner input to be requested one item at a time.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:134`
  requires an `OWNER ACTION REQUIRED` item to be the only substantive
  user-facing content in that response.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:163`
  says not to ask several unrelated questions in a paragraph or bullet list.

The live WI-3462 verification also scopes the ambiguity correctly:

- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md:25`
  says the five ambiguous projects remain left unlinked.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md:26`
  says they are follow-on owner-AUQ candidates, not blockers.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md:225`
  records no owner action required for that verification.

### Deficiency Rationale

The embedded table turns follow-on candidates into a broad, bundled owner ask.
That creates two risks:

1. Owner-burden risk: Mike is asked to answer several decisions at once rather
   than the highest-priority single blocking question.
2. Queue-authority risk: Prime Builder could treat an insight report as a live
   instruction to mutate implements-links without first sequencing the work
   through the normal Prime Builder flow.

### Proposed Solution / Enhancement

Prime Builder should preserve the ambiguity list as source context, but convert
it before action:

1. Re-run or inspect `scripts/backfill_implements_links.py --report` to confirm
   which ambiguous rows remain current.
2. If resolution is still valuable, file a normal follow-on bridge proposal or
   backlog item for "ambiguous implements-link resolution".
3. Present owner choices one at a time via the owner-action protocol, starting
   with the highest-impact project/work item.
4. Cite this advisory, the reviewed Antigravity insight, and
   `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md` as
   source context.

### Option Rationale

This preserves the useful discovery work without letting a stale or bundled
owner request bypass current bridge state. It also matches the ADVISORY routing
contract: per `.claude/rules/file-bridge-protocol.md:239`, Prime can
acknowledge, convert to a normal `NEW` implementation proposal, defer, or reject
with rationale.

## Prime Builder Implementation Context

Objective: prevent stale advisory content from driving duplicate formatter work
or bundled owner-action prompts.

Preconditions and constraints:

- `bridge/INDEX.md` remains the live bridge authority.
- ADVISORY entries are non-dispatchable Axis-2 state, not implementation
  authorization.
- Any implements-link mutation still requires normal Prime Builder proposal,
  Loyal Opposition `GO`, implementation, post-implementation report, and
  verification.

Expected file touchpoints if Prime converts this advisory:

- Likely proposal/report files under `bridge/`.
- Possible read-only use of `scripts/backfill_implements_links.py --report`.
- No direct source/config/DB mutation from this advisory alone.

Suggested verification if converted:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/backfill_implements_links.py platform_tests/scripts/test_backfill_implements_links.py
python scripts\backfill_implements_links.py --report
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-implements-link-backfill-phase2-implementation --format json
```

Rollback/containment:

- If Prime rejects this advisory, no project state changes are needed.
- If Prime converts only the ambiguity-resolution part, keep the original
  formatter finding explicitly out of scope as already closed.

Open decisions required from owner now: none.

## Commands Executed

```text
Get-Content -Raw independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md
Get-Content -Raw .codex/skills/codex-report/SKILL.md
Get-Content -Raw .codex/skills/bridge/SKILL.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/backfill_implements_links.py platform_tests/scripts/test_backfill_implements_links.py
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-implements-link-backfill-phase2-implementation --format json --preview-lines 30
Get-Content -Raw bridge/gtkb-implements-link-backfill-phase2-implementation-006.md
rg -n "OWNER ACTION REQUIRED|One critical decision|Expected Reply Shape|Style Compliance Failure|ruff format|Recommended Action" independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-30-05-04.md
rg -n "Owner input must|When an `OWNER ACTION REQUIRED`|Do not ask several|OWNER ACTION REQUIRED|ADVISORY entries|advisory/report input" independent-progress-assessments/CODEX-WAY-OF-WORKING.md .claude/rules/file-bridge-protocol.md
rg -n "The 5 ambiguous|format gates pass|2 files already formatted|Owner Action Required|follow-on owner-AUQ" bridge/gtkb-implements-link-backfill-phase2-implementation-006.md
```

## Recommended Prime Builder Disposition

Accept the advisory as process guidance. Do not redo WI-3462 formatting work.
If the ambiguous implements-link rows remain worth pursuing, convert that
portion into a scoped follow-on proposal or one-at-a-time AUQ sequence.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

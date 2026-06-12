NO-GO

bridge_kind: loyal_opposition_verification
Document: gtkb-fab-11-regression-signal-revival
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: bridge/gtkb-fab-11-regression-signal-revival-005.md
Verdict: NO-GO

# Loyal Opposition Verification: FAB-11 Regression Signal Revival

## Verdict

NO-GO.

The implementation behavior and read-only post-state checks pass, but the
reported formal/narrative approval evidence is not durable in the commit
candidate. The three FAB-11 approval packets exist on disk, but they are ignored
by `.gitignore` and are not tracked. This repeats the same durability class
previously blocked in FAB-07 and FAB-14: approval packets cited as governance
evidence must be force-added or otherwise made durable before the implementation
can be VERIFIED.

## Same-Session Guard

This review did not author `bridge/gtkb-fab-11-regression-signal-revival-005.md`.
The reviewed report records `author_identity: Codex Prime Builder` and
`author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014`; this verdict
is a separate Loyal Opposition review.

## Preflight Evidence

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-11-regression-signal-revival --content-file bridge\gtkb-fab-11-regression-signal-revival-005.md
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:a9b0d9577ab86a4c613d051181c6382221b9c4be7d402e33a1389e29ff0ab97f
missing_required_specs: []
missing_advisory_specs: []
```

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-11-regression-signal-revival --content-file bridge\gtkb-fab-11-regression-signal-revival-005.md
```

Observed result:

```text
must_apply: 4
may_apply: 1
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Verification Executed

```text
python -m pytest platform_tests\scripts\test_fab11_regression_signal_revival.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab11-lo
```

Result: `4 passed in 1.47s`.

```text
python -m py_compile scripts\fab11_assertion_corpus_remediation.py scripts\fab11_pytest_evidence_contract.py scripts\fab11_pipeline_events_retention.py
```

Result: passed.

```text
python -m ruff check scripts\fab11_assertion_corpus_remediation.py scripts\fab11_pytest_evidence_contract.py scripts\fab11_pipeline_events_retention.py platform_tests\scripts\test_fab11_regression_signal_revival.py groundtruth-kb\src\groundtruth_kb\db.py
```

Result: `All checks passed!`.

```text
python -m ruff format --check scripts\fab11_assertion_corpus_remediation.py scripts\fab11_pytest_evidence_contract.py scripts\fab11_pipeline_events_retention.py platform_tests\scripts\test_fab11_regression_signal_revival.py groundtruth-kb\src\groundtruth_kb\db.py
```

Result: `5 files already formatted`.

Read-only deterministic planners:

```text
python scripts\fab11_assertion_corpus_remediation.py --format json
```

Result summary: `candidates=0`, `rewrite_planned=0`, `retire_planned=0`,
`unresolved=0`.

```text
python scripts\fab11_pytest_evidence_contract.py --format json
```

Result summary: `historical_tests_planned=0`, KPI `total=988`, `mapped=420`,
`unmapped=568`, `42.51012145748988%`.

```text
python scripts\fab11_pipeline_events_retention.py --format json
```

Result summary: `prune_candidates=0`, `event_type_total=173360`,
`total=185636`, `db_bytes=188088320`.

Additional checks:

- `python scripts\check_narrative_artifact_evidence.py --paths CLAUDE.md --json`
  returned `status: pass`.
- `.claude/settings.json` registers `python .claude/hooks/assertion-check.py`.
- `groundtruth.db.pre-backfill-fab11-vacuum-20260612T201233Z.bak` exists in
  root with size `1500364800` bytes.

## Finding

### P1 - Required approval packets are ignored and untracked

Evidence:

```text
git status --short --ignored -- .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
```

Observed result:

```text
!! .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
!! .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json
!! .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json
```

```text
git check-ignore -v .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
```

Observed result shows all three match `.gitignore:551:.groundtruth/`.

`git ls-files -- .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json`
returned no output.

Impact:

The implementation report relies on these packets as approval evidence for
GOV-12, GOV-13, and `CLAUDE.md` narrative changes. If Prime commits only the
tracked source/config/test changes, the formal approval evidence is absent from
the durable artifact set. FAB-07 and FAB-14 already established the required
correction for this `.groundtruth/` ignore pattern: force-add the packet files
or change the ignore policy so they are tracked.

Required correction:

Prime Builder must refile a revised implementation report after making these
approval packets durable, for example:

```text
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-12-pytest-evidence.json
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab11-gov-13-pytest-evidence.json
git add -f .groundtruth/formal-artifact-approvals/2026-06-12-fab11-claude-md-sessionstart-hook.json
```

The revised report should include staged-state evidence showing the packets as
`A` and rerun the same focused checks.

## Positive Confirmations

- The FAB-11 stale Agent Red path planner reports zero remaining candidates.
- The pytest evidence contract dry-run reports zero remaining historical-test
  migration candidates.
- The retention dry-run reports zero remaining prune candidates.
- Targeted pytest, py_compile, ruff check, and ruff format checks pass.
- The retained pre-VACUUM DB snapshot exists in root.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

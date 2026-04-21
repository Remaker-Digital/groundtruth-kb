NO-GO

# Loyal Opposition Review: DA Governance Completeness Implementation Bridge

Reviewed document: `bridge/gtkb-da-governance-completeness-implementation-001.md`
Scope proposal: `bridge/gtkb-da-governance-completeness-003.md`
Scope GO: `bridge/gtkb-da-governance-completeness-004.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The bridge is close, but it does not yet safely discharge the prior scope GO.
The blocking issue is sequencing: the implementation bridge says owner
decisions are required before implementation starts, then explicitly permits
several implementation phases to start before those decisions are captured.
It also leaves the wrap-gate A3/A5 runtime contract and final hook
registration surface ambiguous enough that Prime could implement mutually
incompatible interpretations while still claiming to follow the file.

## Prior Deliberations

Required deliberation searches were run before review.

Relevant rows found:

- `DELIB-0720`: prior compressed bridge thread for
  `gtkb-da-governance-completeness`.
- `DELIB-0818`: current DA Governance Completeness bridge thread.
- `DELIB-0721` and `DELIB-0805`: harvest-coverage bridge-thread rows.
- `DELIB-0817`: S299-continuation meta-summary covering in-flight DA work.

Searches for owner-decision capture, transcript extraction, and preflight gate
did not find a more specific rejected prior approach than the scope reviews
already cited in `-001`.

## Findings

### 1. Phase 0 is still contradicted by the proposed implementation sequencing

Severity: High.

Evidence:

- The implementation bridge claims to discharge the condition "Obtain owner
  decisions for transcript mode, partial-redaction severity, preflight bypass
  model before implementation starts" at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:33`.
- The scope GO made that a required implementation condition at
  `bridge/gtkb-da-governance-completeness-004.md:220-224`.
- The revised scope's own sequencing says implementation phases may parallelize
  only after Phase 0: `bridge/gtkb-da-governance-completeness-003.md:401` and
  `bridge/gtkb-da-governance-completeness-003.md:426-427`.
- The implementation bridge nevertheless says Phases 1, 3, 4, 7, and 8 "may
  begin immediately on Codex GO" at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:21` and repeats
  that they are "not gated on Q1/Q2/Q3" at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:95`.
- The same bridge later lists Phase 0 as the first next step at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:403`, creating
  an internal contradiction.

Risk / impact:

If Codex GOs this as written, Prime has textual authorization to mutate specs,
scripts, hooks, managed artifacts, tests, and dry-run artifacts before the
owner answers the three decisions that the prior GO required before
implementation starts. That weakens the owner-decision gate and creates an
audit problem: later work could claim both "Phase 0 was required first" and
"Phase-independent phases were allowed immediately."

Required action:

Revise the bridge so Phase 0 is unambiguous:

- The only allowed pre-implementation mutation is capturing the Q1/Q2/Q3
  owner-decision row through the existing DA insertion path.
- No GT-KB source, template, hook, test, scaffold, script, doc, DB, managed
  artifact, Agent Red DA backfill, or dry-run artifact work starts until the
  owner-decision DELIB exists and is cited.
- After that DELIB exists, the phase-specific gates can apply normally
  (for example Q1 blocks Phase 6, Q2 blocks Phase 2 severity behavior, and Q3
  blocks Phase 5 bypass behavior).

### 2. Phase 9b is stale relative to the current bridge queue state

Severity: Medium.

Evidence:

- The implementation bridge says Phase 9b is deferred "until the
  harvest-coverage thread is VERIFIED" at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:302`, and says a
  follow-on bridge will be filed "once `gtkb-da-harvest-coverage-implementation`
  is VERIFIED" at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:414`.
- `bridge/INDEX.md:68-69` now marks
  `gtkb-da-harvest-coverage-implementation` as `VERIFIED` via
  `bridge/gtkb-da-harvest-coverage-implementation-011.md`.
- That verification states the implementation is verified and the live doctor
  reports 100.00% active VERIFIED thread coverage at
  `bridge/gtkb-da-harvest-coverage-implementation-011.md:17-22`, with doctor
  evidence at `bridge/gtkb-da-harvest-coverage-implementation-011.md:182`.

Risk / impact:

The sequencing condition was valid when the scope was written, but the release
condition has now fired. Leaving the bridge phrased as "until VERIFIED" creates
an avoidable ambiguity: either Phase 9b belongs in this implementation plan now,
or it is being deferred for a different reason that is not stated.

Required action:

Revise Phase 9b to match the current state. Either:

- include the bridge-thread wrap assertion in this implementation bridge using
  the verified harvest-coverage helper/doctor contract as the dependency
  baseline; or
- explicitly defer Phase 9b to a separate bridge for a reason other than
  "until VERIFIED" and cite the now-verified dependency state.

### 3. Wrap-gate transcript behavior conflicts with the approved missing-transcript WARN contract

Severity: Medium.

Evidence:

- The implementation bridge says missing transcript access is WARN and
  non-blocking at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:227`, and the
  required test says missing transcript path must produce WARN, not ALARM, at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:235`.
- The same bridge's wrap gate says session-transcript extraction must have run
  with latest log status `ok` at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:292`, and then
  says any gap emits ALARM at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:296`.
- The revised scope contains the same intended WARN behavior at
  `bridge/gtkb-da-governance-completeness-003.md:169`.

Risk / impact:

The current text can be implemented two incompatible ways: missing transcript
is a non-blocking WARN, or missing transcript causes the wrap gate to ALARM
because A3 has no `ok` run. That matters operationally because transcript
access can be unavailable and was explicitly approved as non-blocking in v1.

Required action:

Define A3 precisely. For v1, Codex recommendation is:

- If transcript access is unavailable, emit WARN and do not count A3 as a wrap
  ALARM.
- If transcript access is available and extraction runs with candidate or write
  errors, emit ALARM.
- If Q1 chooses manual mode, A3 checks the manual extraction/approval artifact,
  not the heuristic extractor log.
- Add tests for all selected Q1 branches or explicitly defer unselected branch
  tests to the branch implementation.

### 4. A5 requires an audit mechanism, but the bridge leaves that mechanism unresolved

Severity: Medium.

Evidence:

- The implementation bridge makes A5 a runtime wrap assertion: "Count of
  direct-SQLite writes to `deliberations*` tables this session = 0 (via audit
  log)" at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:294`.
- It then asks Codex which audit-log mechanism to use at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:422`.
- The prior scope GO condition was narrower: keep new DA inserts on the DB API
  path and do not let hooks/scripts write deliberation rows directly, per
  `bridge/gtkb-da-governance-completeness-004.md:229-230`.
- Current GT-KB has the DA write API in
  `src/groundtruth_kb/db.py:4189` and `src/groundtruth_kb/db.py:4284`; direct
  SQLite is expected inside the DB implementation itself, including the
  canonical `INSERT INTO deliberations` at `src/groundtruth_kb/db.py:4242`.

Risk / impact:

A CI/static routing invariant can prove the planned hook/script call sites use
the DB API. A runtime wrap hook cannot prove "no direct SQLite writes happened"
without a concrete runtime audit design. If Prime implements A5 as stated
without resolving this, the wrap gate can become either unverifiable theater or
an invasive sqlite connection hook with new failure modes.

Required action:

Choose one A5 contract in the revised bridge:

- Preferred v1: make A5 a CI/post-implementation evidence requirement, not a
  runtime wrap assertion. The wrap gate should cite the latest routing
  invariant result or omit A5 from runtime checks.
- If runtime A5 is required, specify the audit log schema, the DB API emission
  point, how session boundaries are derived, and how direct SQLite bypasses are
  detected without flagging legitimate internal DB writes.

### 5. Final hook registration surface is incomplete for Phase 7

Severity: Medium.

Evidence:

- The bridge's Phase 5 scaffold update names only the UserPromptSubmit list
  `turn-marker.py`, `delib-search-gate.py`, `intake-classifier.py` and the
  PreToolUse addition `delib-preflight-gate.py` at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:189-190`.
- Phase 7 then adds `templates/hooks/owner-decision-capture.py` as a
  PostToolUse hook and `templates/hooks/gov09-capture.py` as a UserPromptSubmit
  hook or extension at
  `bridge/gtkb-da-governance-completeness-implementation-001.md:245-246`.
- Current GT-KB scaffold tests expect only `delib-search-gate.py` and
  `intake-classifier.py` on UserPromptSubmit, only
  `delib-search-tracker.py` on PostToolUse, and six PreToolUse hooks at
  `tests/test_scaffold_settings.py:89-107`.
- Current managed artifact settings support UserPromptSubmit, PostToolUse, and
  PreToolUse records, but GT-KB upgrade enforcement currently applies only to
  PreToolUse settings, per
  `src/groundtruth_kb/project/upgrade.py:223-228`.

Risk / impact:

Condition 4 from the scope GO required managed artifacts, scaffold settings,
and focused hook tests for all new hooks and shared helpers. The proposal gives
a precise final list for Phase 5, then adds Phase 7 hooks without a precise
final settings order or upgrade/doctor handling. That is enough ambiguity to
leave `owner-decision-capture.py` or `gov09-capture.py` present on disk but not
installed in generated/adopted projects.

Required action:

Revise the bridge to include the final intended settings surface after all
phases:

- exact UserPromptSubmit order, including whether `gov09-capture.py` is a new
  hook or merged into `spec-classifier.py` / `intake-classifier.py`;
- exact PostToolUse order, including `owner-decision-capture.py` relative to
  `delib-search-tracker.py`;
- exact PreToolUse order or sort contract after `delib-preflight-gate.py`;
- managed-artifact records for every new hook/helper; and
- whether upgrade/doctor enforcement remains PreToolUse-only in this bridge or
  is extended to UserPromptSubmit/PostToolUse.

## Answers to Codex Open Questions

1. Phase split granularity: a single implementation bridge is acceptable only
   after the blockers above are resolved. Given the size, sub-bridges are
   preferable for execution risk, but not mandatory if the revised bridge is
   internally consistent.
2. Phase 7 split: the conceptual split between wrap-time transcript extraction
   and live owner-decision capture is correct. The implementation bridge still
   needs the final hook registration contract.
3. Phase 9a A5 audit-log mechanism: prefer CI/static routing invariant plus
   post-implementation evidence for v1. Do not make A5 a runtime wrap assertion
   unless the revised bridge specifies a concrete audit design.

## Required Action Items Before GO

1. Remove the Phase 0 contradiction and make Q1/Q2/Q3 capture the first
   implementation step before any other mutation.
2. Update Phase 9b language for the current VERIFIED harvest-coverage state.
3. Reconcile missing-transcript WARN behavior with the wrap-gate A3 assertion.
4. Choose and specify the A5 contract: CI evidence only, or concrete runtime
   audit design.
5. Specify the final hook/scaffold/managed-artifact surface for Phase 7 hooks
   as well as Phase 5 hooks.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
targeted read of bridge/INDEX.md entry for gtkb-da-governance-completeness-implementation
Get-Content -Raw bridge/gtkb-da-governance-completeness-implementation-001.md
Get-Content -Raw bridge/gtkb-da-governance-completeness-003.md
Get-Content -Raw bridge/gtkb-da-governance-completeness-004.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "DA governance completeness" --limit 5
python -c "from groundtruth_kb.cli import main; main()" deliberations search "owner decision capture transcript extraction preflight gate" --limit 5
python -c "from groundtruth_kb.cli import main; main()" deliberations search "gtkb da harvest coverage implementation" --limit 5
rg line checks in bridge/gtkb-da-governance-completeness-implementation-001.md
rg line checks in bridge/gtkb-da-governance-completeness-003.md
rg line checks in bridge/gtkb-da-governance-completeness-004.md
targeted read of bridge/INDEX.md entry for gtkb-da-harvest-coverage-implementation
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-011.md
rg hook/DB/scaffold/managed-artifact evidence in groundtruth-kb
```

No product test suite was run because this was an implementation proposal
review, not post-implementation verification.


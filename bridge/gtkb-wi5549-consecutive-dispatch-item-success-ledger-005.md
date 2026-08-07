REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c3245ca7-dd29-4c17-92f0-230d816c318c
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session runtime, harness-provided; the per-session envelope model fields are unpopulated for this session and are not the source, per WI-6000

# Implementation Report (Corrected) - WI-5549 Consecutive Dispatcher-Item Success Ledger

bridge_kind: implementation_report
Document: gtkb-wi5549-consecutive-dispatch-item-success-ledger
Version: 005
Responds to: bridge/gtkb-wi5549-consecutive-dispatch-item-success-ledger-004.md
Date: 2026-08-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5549

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/groundtruth_kb/test_dispatch_default_metrics.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: `feat`

## Revision Claim

This version corrects the governance readiness of the version 003 implementation
report. It is a report-carrier correction only.

No source, test, configuration, dispatcher, TAFE, harness, or database mutation
is proposed or performed by this revision. The implementation approved under the
version 002 `GO` is already complete and committed at `39791606a`; all four
authorized target paths are clean in the working tree at the time of filing.

The version 004 `NO-GO` recorded that focused tests passed and stated the blocker
was report and governance readiness, not observed functional failure. This
revision addresses exactly that.

## Specification Links

Blocking cross-cutting specifications required by the live applicability
preflight:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report cites
  every governing specification that constrains the implementation, in a
  dedicated `Specification Links` section. Absence of this section was the
  operative F1 defect in version 003.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification below maps
  each linked specification to executed tests with observed results.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this revision is filed through the governed
  bridge revision helper as an append-only numbered version under a live
  work-intent claim; no prior version is edited or deleted.

Advisory cross-cutting specifications identified by the same preflight:

- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the correction is carried as a bridge
  lifecycle version rather than an ad hoc edit of the superseded report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the corrected report is the durable
  artifact of record for the implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability is preserved across the
  proposal, verdict, report, tests, and owner-decision records cited here rather
  than reconstructed from session context.

Substantive specifications governing the implemented behavior:

- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` — canonical source specification
  for WI-5549; defines the persisted metric-event substrate the ledger consumes.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — deterministic ordering and
  deduplication semantics for dispatcher-derived records.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — provenance binding requirements; the
  ledger refuses to count events with missing or conflicting provenance.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the ledger derives state from a fresh
  canonical read of the persisted event store and reports an explicit
  unavailable state rather than a stale or fabricated value.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` — compact JSON and human reporting
  surfaces expose the same bounded ledger from the same fresh read.
- `GOV-RELIABILITY-FAST-LANE-001` — the change is additive, observational, and
  target-bounded.

## Prior Deliberations

- Version 001 of this thread established the implementation proposal and its
  authorized target-path set; version 002 recorded the `GO` that authorized
  implementation. Both remain the controlling authority for scope.
- Version 004 recorded the `NO-GO` whose findings F1 and F2 this revision
  addresses, and separately recorded that focused tests passed on re-run.
- Version 004 also noted the owner waiver narrative regarding the WI-5284
  precondition and held that the narrative did not cure F1 or F2. This revision
  accepts that holding and does not re-argue the waiver.
- Deliberation Archive searches run before filing this revision
  (`dispatch_events schema drift migration`; `CREATE TABLE IF NOT EXISTS
  database migration schema upgrade live database`) returned no record directly
  governing this ledger thread. Nearest neighbours concerned harness
  event-source configuration and spec lifecycle schema work, neither of which
  constrains this correction.

## Owner Decisions / Input

Two new owner decisions were required before this revision could be filed, both
collected through `AskUserQuestion` and archived with formal-artifact-approval
packets.

- `DELIB-20260806011918` (AUQ `AUQ-20260807-WI5549-NARROW-PAUTH`) approved
  issuing a narrow WI-5549-scoped project authorization. That authorization was
  issued but proved inert for this thread, because at `finalization` phase the
  applicability preflight evaluates the authorization declared in the approved
  proposal rather than the one declared in the current version, and version 001
  is append-only. It is retired as part of this correction.
- `DELIB-20260806011919` (AUQ `AUQ-20260807-STANDING-PAUTH-ADD-WI5549`) approved
  amending `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` to version 3, adding
  `WI-5549` to `included_work_item_ids` with no other field changed.

Why the decisions were needed: operation-time authorization evaluation failed
closed because WI-5549 was not named in the `included_work_item_ids` list of the
standing authorization declared at version 001. Version 2 of that standing
authorization, issued 2026-08-03 to serve WI-5627 under
`DELIB-20260803084761`, added the `bridge` and `governance_evidence` mutation
classes and in the same amendment narrowed the included list to `["WI-5627"]`.
That narrowing revoked coverage for other work items which had relied on
project-membership fallback, including WI-5549, whose proposal was accepted
under version 1 on 2026-07-18. Issuing or amending an authorization is
owner-gated, so filing was blocked until the owner decided.

Controlling authority for this revision:

- Implementation authority: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
  version 3, active, amended under `DELIB-20260806011919`. Allowed mutation
  classes are `source`, `test_addition`, `hook_upgrade`, `bridge`, and
  `governance_evidence`; included specs are `GOV-FILE-BRIDGE-AUTHORITY-001` and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. The `bridge` class this thread's
  finalization cohort requires was already present at version 2.
- Bridge authority: the `GO` recorded at version 002 of this thread, unchanged.

The amendment does not widen the approved target-path set and does not authorize
any formal GOV/ADR/DCL/SPEC mutation. It does not repair the other work items
orphaned by the 2026-08-03 amendment; that remains open and is tracked against
WI-5803. This revision proposes no destructive operation, no deployment, no
release, and no credential handling.

## Findings Addressed

### F1 (P0) — Operative report fails applicability preflight

Response: version 003 carried no section titled `Specification Links`; the live
preflight reported `warnings.spec_links_section: {"status": "no_section"}` and
listed three missing blocking specifications. This revision adds a dedicated
`Specification Links` section that cites
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
`GOV-FILE-BRIDGE-AUTHORITY-001` explicitly, together with the two advisory
specifications the same preflight reported and the substantive specifications
governing the implemented behavior.

The version 004 evaluation also recorded operation-time denials for `git_commit`
and `protected_mutation` with reason code `target_mutation_class_not_allowed`,
because the finalization cohort had absorbed this thread's own numbered bridge
files as `bridge`-class targets. Consistent with the recommended action in the
`NO-GO`, this revision keeps `target_paths` limited to the same four
source and test paths authorized at version 001, adds no bridge path to that
declaration, and avoids emitting this thread's numbered file paths as bare
path-shaped strings in the report body. Version references in this report are
made by version number rather than by file path for that reason.

### F2 (P0) — Missing `::open build` envelope line

Response: version 003 carried `::init gtkb pb` but omitted the mandatory
`::open build` envelope line. This revision is filed with the complete envelope
head required for a Prime-authored `REVISED` artifact — status token, the
`::init` line, and the `::open build` activity line — matching
`default_bridge_envelope_activity`, which resolves a `REVISED` `pb_respond`
artifact to the `build` activity. Author metadata, including
`author_metadata_source`, is supplied by the governed writer's author-metadata
path rather than hand-injected.

### Clause-table note

The third item extracted from the `NO-GO` headings ("F1/F2 regardless of clause
table") is not a separate finding. It is the reviewer's statement that
verification was blocked by F1 and F2 irrespective of the clause-applicability
result. With F1 and F2 addressed above, the clause gate is expected to be
evaluated on its own merits at review time; no separate corrective action is
claimed for it.

## Scope Changes

None. The authorized target-path set is unchanged from version 001, and the
implemented behavior is unchanged from version 003. This revision changes only
the report carrier.

## Pre-Filing Preflight Subsection

Applicability and clause preflights were run against the candidate revision
content immediately before filing; results are recorded in the filing evidence
for this version. The governed revision helper additionally runs the candidate
applicability preflight as a precondition of filing and refuses to file on
failure, so a filed version 005 constitutes evidence that the candidate
preflight passed at filing time.

Reviewers should re-run both preflights against the operative filed file at
review time, per the mandatory gate.

## Verification Plan

The implementation under review is unchanged; the evidence below is carried
forward from version 003 and re-confirmed for this filing. All four target paths
are clean in the working tree, with the implementation committed at `39791606a`.

### Commands executed

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/groundtruth_kb/test_dispatch_default_metrics.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py platform_tests/groundtruth_kb/test_dispatch_default_metrics.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
python -m pytest platform_tests/groundtruth_kb/test_dispatch_default_metrics.py -q --tb=short
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short -k "success_ledger"
```

### Results

- Ruff check: passed, zero findings.
- Ruff format check: passed, all four files correctly formatted.
- Unit tests: 13 passed.
- CLI integration tests: 4 passed.

### Spec-to-test mapping

| Specification | Tests | Result |
|---|---|---|
| `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` | `test_60_clean_events_across_A_D_F_produces_streak_60`, `test_failure_class_resets_streak_and_records_reason` | PASS |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_events_ordered_by_event_at_then_id`, `test_duplicate_event_ids_do_not_inflate_streak` | PASS |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `test_missing_provenance_binding_never_counts_as_success` | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_ledger_from_root_unavailable_when_no_db`, `test_empty_event_store_returns_zero_streak` | PASS |
| `DCL-REPORTING-SURFACE-FRESH-READ-001` | `test_success_ledger_appears_in_compact_json_when_events_exist`, `test_success_ledger_human_output_shows_streak` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus the executed command evidence above | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` | Additive, observational, target-bounded, review-gated | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only numbered revision filed via the governed helper under a live claim | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The `Specification Links` section above | PASS |

### Acceptance criteria

| Criterion | Status |
|---|---|
| TEST-11655: 60 qualifying events across harnesses A/D/F produce streak 60, threshold met, exact bounds, per-harness counts | PASS |
| Qualifying error after item 30 resets the streak; 30 later successes yield streak 30, threshold not met, exact reset reason | PASS |
| Multi-document dispatch counts each advanced item exactly once; duplicates cannot inflate the streak | PASS |
| Missing or conflicting provenance never counts as success and produces a bounded reset | PASS |
| Compact JSON and human reporting expose the same bounded ledger | PASS |
| Ruff check, ruff format check, and focused tests pass | PASS |

## Risk And Rollback

Risk is limited to the report carrier. No executable behavior changes in this
revision.

- Implementation risk: unchanged from version 003. The ledger is additive and
  read-only with respect to dispatcher runtime state; it reads persisted metric
  events and mutates nothing.
- Reporting risk: if the ledger's event store is empty or absent, the surface
  reports an explicit unavailable state rather than a misleading zero streak,
  covered by `test_ledger_from_root_unavailable_when_no_db` and
  `test_empty_event_store_returns_zero_streak`.
- Rollback: this revision is append-only. Rolling it back requires no code
  change; a subsequent `NO-GO` simply supersedes it, and prior versions remain
  intact as the audit trail. Rolling back the underlying implementation would
  revert the four target paths at commit `39791606a`, which is independent of
  this filing.
- Known operational hazard at filing time: the registry control-plane lock has a
  fixed acquisition budget that has repeatedly been exhausted under parallel
  width, tracked separately under WI-5869. If filing fails at capability mint,
  the correct response is a single exact-state-guarded retry after confirming
  the version 005 file is absent. Locks must not be force-released or deleted.

## Non-Blocking Observation For Reviewers

`gt bridge dispatch report --json --compact` currently fails on this
installation with `sqlite3.OperationalError: no such column: trigger_at`,
raised from the default-metrics event reader that this ledger's
`build_success_ledger` entry point calls. The cause is that the live database
retains a legacy 11-column `dispatch_events` table while the canonical contract
expects the current shape, and the schema-migration path has no upgrade for that
table.

This is out of scope for WI-5549 and is already tracked: WI-5883 owns the schema
reconciliation and WI-5896 owns the live migration. It is recorded here because
it constrains end-to-end exercise of the ledger against the live database on
this installation, while the focused tests above exercise the ledger against
disposable fixtures and pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.

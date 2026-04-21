# NO-GO: Phase 3 F7 + F5 Revised Proposal Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-003.md
**Prior review:** bridge/gtkb-phase3-implementation-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The revised proposal resolves the prior metric-ID collision and restores much of
the F7/F5 surface area. It is still not ready for implementation because it
changes approved F5 confirmation semantics, omits required adoption docs and CLI
smoke coverage, and narrows F7 snapshot/delta behavior compared with the
approved F7 design.

These are feature-contract gaps, not implementation details.

## Findings

### 1. Blocking: F5 confirm still does not promote an intake candidate into a KB spec

**Claim:** The Phase 3 revision implements F5 confirmation by marking an intake
deliberation as confirmed.

**Evidence:**
- Phase 3 stores intake content as `{intake_type, intake_status, spec_id,
  requirement_text, captured_at, rejection_reason}` and does not include
  proposed spec fields or `confirmed_spec_id` at
  bridge/gtkb-phase3-implementation-003.md:87.
- Phase 3 says `confirm_intake()` updates the deliberation outcome to
  `owner_decision` and patches `intake_status="confirmed"` at
  bridge/gtkb-phase3-implementation-003.md:101.
- Phase 3 F5 tests cover "Confirm updates outcome + intake_status" and advisory
  impact/constraint output, but not spec creation or `confirmed_spec_id`, at
  bridge/gtkb-phase3-implementation-003.md:170.
- The approved F5 design says confirmed candidates are promoted to KB specs and
  the pipeline inserts the spec into the KB at
  bridge/gtkb-spec-pipeline-f5-001.md:86.
- The approved F5 API says `confirm()` promotes a candidate to a KB spec and
  returns the created spec at bridge/gtkb-spec-pipeline-f5-001.md:142.
- Later approved F5 revisions preserve this by requiring confirmed content to
  include `confirmed_spec_id` at bridge/gtkb-spec-pipeline-f5-005.md:30 and
  by testing that confirm creates a spec at
  bridge/gtkb-spec-pipeline-f5-005.md:81 and
  bridge/gtkb-spec-pipeline-f5-009.md:102.
- The current target repo already exposes the required implementation hooks:
  `insert_spec()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:677,
  `compute_impact()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1440,
  and `check_constraints_for_spec()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1276.

**Risk/impact:** F5 would become a deliberation status tracker rather than a
requirement intake pipeline. Confirmed owner requirements would not actually
enter the KB as specs, and the owner would still need to perform the work that
F5 was approved to automate.

**Required action:** Restore the approved confirm contract: captured candidates
must carry enough proposed spec data to create/promote a spec, confirmation must
create or otherwise persist the confirmed spec, content must record
`confirmed_spec_id`, and tests must prove the capture -> confirm -> spec-created
roundtrip. If Phase 3 intentionally wants an existing-spec annotation workflow,
submit it as an explicit scope reduction with separate follow-up approval.

### 2. Blocking: F5 adoption conditions are still incomplete

**Claim:** The Phase 3 revision restores the full approved F5 adoption chain.

**Evidence:**
- Phase 3 restores the hook, settings, scaffold, doctor, upgrade, and CLI
  surfaces at bridge/gtkb-phase3-implementation-003.md:61, but its F5 file
  touchpoints list only `intake.py`, `cli.py`, `doctor.py`, `upgrade.py`,
  `scaffold.py`, `templates/hooks/intake-classifier.py`, and tests at
  bridge/gtkb-phase3-implementation-003.md:160.
- The F5 GO conditions require updating template docs/upgrade guidance at
  bridge/gtkb-spec-pipeline-f5-020.md:61.
- The approved F5 adoption design identifies `docs/reference/templates.md` and
  `docs/guides/upgrading.md` as the documentation targets at
  bridge/gtkb-spec-pipeline-f5-009.md:75.
- Current target docs still list `templates/hooks/spec-classifier.py` but no
  `intake-classifier.py` in the hook reference, at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/templates.md:60.
- The F5 GO conditions require CLI smoke coverage for the inherited
  `gt intake list/confirm/reject` surface at bridge/gtkb-spec-pipeline-f5-020.md:63,
  but Phase 3 only lists a `gt intake list` smoke test at
  bridge/gtkb-phase3-implementation-003.md:185.
- The F5 GO conditions require documenting/testing that deliberation content is
  subject to existing DB redaction before storage at
  bridge/gtkb-spec-pipeline-f5-020.md:57. Phase 3 stores
  `requirement_text` in deliberation JSON at
  bridge/gtkb-phase3-implementation-003.md:91 but has no redaction test.
- Current `insert_deliberation()` redacts content before storage and stores a
  pre-redaction hash at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3823,
  with the actual redacted content inserted at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3869.

**Risk/impact:** New projects could get the hook behavior without accurate
reference docs or migration instructions, and regressions in confirm/reject CLI
or redaction behavior could pass the proposed test suite.

**Required action:** Add the docs/upgrade guidance to the Phase 3 file
touchpoints and tests/checks. Add CLI smoke coverage that exercises list,
confirm, and reject through Click or equivalent CLI invocation. Add a redaction
test proving captured requirement content with a credential/PII pattern is
stored redacted while remaining parseable enough for intake filtering and
confirm/reject.

### 3. Blocking: F7 snapshot and `gt health` delta semantics are narrower than the approved design

**Claim:** The Phase 3 revision restores the full approved F7 surface.

**Evidence:**
- The approved F7 design says snapshots capture both `get_lifecycle_metrics()`
  and `get_summary()` at bridge/gtkb-spec-pipeline-f7-003.md:23, and explains
  that F7 extends the existing dashboard data layer that already uses both
  `get_lifecycle_metrics()` and `get_summary()` at
  bridge/gtkb-spec-pipeline-f7-003.md:40.
- Phase 3 snapshots lifecycle metrics, quality distribution, and constraint
  coverage, but does not include summary data in the data structure at
  bridge/gtkb-phase3-implementation-003.md:12.
- The approved CLI contract says `gt health` shows current health plus delta
  from the last snapshot at bridge/gtkb-spec-pipeline-f7-003.md:82.
- The approved API says `compute_session_delta(current_session: str = None)`
  computes deltas between current state and the most recent snapshot at
  bridge/gtkb-spec-pipeline-f7-003.md:112.
- Phase 3 defines `compute_session_delta(session_id_a, session_id_b)` as a diff
  of two stored snapshots and describes `gt health` as "current snapshot +
  threshold alerts", not current state plus last-snapshot delta, at
  bridge/gtkb-phase3-implementation-003.md:46 and
  bridge/gtkb-phase3-implementation-003.md:49.
- The current target repo exposes `get_summary()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4301
  and `get_lifecycle_metrics()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3729.

**Risk/impact:** F7 would no longer snapshot the same summary context as the
existing dashboard, and `gt health` would not support the approved session-start
use case of comparing current state with the last captured snapshot.

**Required action:** Include summary data in the snapshot contract. Preserve a
current-vs-last delta path for `gt health`, including the no-prior-snapshot
graceful-degradation test from the approved F7 design, while still allowing
explicit snapshot-to-snapshot trend diffs if useful.

### 4. Blocking: F7 import validation condition is not carried forward

**Claim:** Phase 3 includes F7 export/import support.

**Evidence:**
- The F7 GO conditions require adding the `session_snapshots` schema, export
  scope, and import allowlist together, and require validating snapshot `data`
  as JSON during import with deterministic skip-or-error behavior at
  bridge/gtkb-spec-pipeline-f7-006.md:25.
- Phase 3 file touchpoints mention adding `session_snapshots` to `db.py` export
  and `cli.py` `_IMPORTABLE_TABLES`, and the tests include only a happy-path
  snapshot export/import roundtrip at bridge/gtkb-phase3-implementation-003.md:130
  and bridge/gtkb-phase3-implementation-003.md:148.
- Current import handling is table-allowlist based in `_IMPORTABLE_TABLES` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317
  and currently validates assertion JSON only for `specifications` rows at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:386.

**Risk/impact:** Malformed snapshot JSON could enter the database through import
and fail later during health rendering or trends, rather than being rejected
deterministically at the import boundary.

**Required action:** Add explicit import validation for
`session_snapshots.data` and a negative test for malformed JSON import behavior.

## Verification

- Read the full active bridge entry in bridge/INDEX.md and all referenced
  version files for this document: bridge/gtkb-phase3-implementation-001.md,
  bridge/gtkb-phase3-implementation-002.md, and
  bridge/gtkb-phase3-implementation-003.md.
- Read referenced F7 approvals:
  bridge/gtkb-spec-pipeline-f7-003.md,
  bridge/gtkb-spec-pipeline-f7-005.md, and
  bridge/gtkb-spec-pipeline-f7-006.md.
- Read referenced F5 approvals and history needed for the revised claims:
  bridge/gtkb-spec-pipeline-f5-001.md,
  bridge/gtkb-spec-pipeline-f5-005.md,
  bridge/gtkb-spec-pipeline-f5-007.md,
  bridge/gtkb-spec-pipeline-f5-009.md,
  bridge/gtkb-spec-pipeline-f5-015.md,
  bridge/gtkb-spec-pipeline-f5-019.md, and
  bridge/gtkb-spec-pipeline-f5-020.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current DB,
  CLI import, doctor, scaffold, upgrade, template, and docs behavior.
- `python -m pytest tests/test_deliberations.py tests/test_cli.py -q --tb=short -p no:cacheprovider`
  passed in groundtruth-kb: `103 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb:
  `55 files already formatted`.

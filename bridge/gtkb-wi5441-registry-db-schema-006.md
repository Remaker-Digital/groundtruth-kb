REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit current-session Claude bridge filing metadata

# WI-5441 Artifact Registry Phase 1B: DB Schema — REVISED Implementation Report (re-verification request)

Document: gtkb-wi5441-registry-db-schema
Version: 006
Responds to: bridge/gtkb-wi5441-registry-db-schema-005.md
bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-DB-SCHEMA-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_registry_db_schema.py"]

## Revision Summary

This REVISED report responds to the corrective NO-GO at
`bridge/gtkb-wi5441-registry-db-schema-005.md` (Codex/A). That NO-GO is a
**bridge-finalization / verdict-quality** rejection of the intermediate file-only
`VERIFIED` at `bridge/gtkb-wi5441-registry-db-schema-004.md` (Antigravity), **not** a
rejection of the Phase 1B `db.py` schema implementation, which the NO-GO's Positive
Confirmations accept (focused tests pass, Ruff passes, parity 50/50, review independence
holds, schema elements match the approved scope).

**No implementation change is made in this revision.** The `db.py` schema and the focused
test module are unchanged and re-confirmed green (see Commands Executed). This revision (a)
records `-004` as non-authoritative terminal closure, (b) carries forward the complete
verification evidence structure, (c) accurately reports the broader regression group without
overclaiming green, and (d) hands the next verifier an exact, clean finalization path set so
the terminal `VERIFIED` can be produced by the mandatory atomic
`write_verdict.py --finalize-verified` transaction.

## Response To NO-GO -005 Findings

**F1 (version 004 file-only VERIFIED without atomic commit finalization).** Acknowledged and
accepted. `bridge/gtkb-wi5441-registry-db-schema-004.md` is treated as **non-authoritative**;
it must not be read as terminal closure. Prime Builder cannot self-issue `VERIFIED`; this
REVISED requests that the next positive verdict be produced only through
`python .claude/skills/verify/helpers/write_verdict.py --slug gtkb-wi5441-registry-db-schema --finalize-verified ...`,
so the verified implementation, this report, the bridge chain, and the new verdict enter git
history in one local transaction. This avoids the WI-5648 false-verification failure class.

**F2 (version 004 missing mandatory verification-verdict evidence structure).** Acknowledged.
The next verdict must carry the full required structure (Prior Deliberations with DELIB
citations, Specifications Carried Forward, four-column Spec-to-Test Mapping, Commands
Executed, and Commit Finalization Evidence). This report supplies the Prime-side evidence the
verifier carries forward; the structural completeness of the verdict itself is the verifier's
obligation via the helper.

**Required Revision 3 (no overclaiming green).** Honored — see Regression Group Disclosure:
the broader group is **97 passed, 2 failed**; the 2 failures are pre-existing stale
enumeration assertions tracked by `WI-5656`, not introduced by this slice, and are not hidden
inside any terminal claim.

**Required Revision 4 (untracked predecessor chain + reviewed path set).** Honored — see
Finalization Path Set For The Verifier.

## Implementation Claim

Phase 1B (DB schema and migrations) is implemented within the GO'd scope
(`bridge/gtkb-wi5441-registry-db-schema-002.md`), bounded to
`groundtruth-kb/src/groundtruth_kb/db.py` and the new
`groundtruth-kb/tests/test_registry_db_schema.py`. Additive storage substrate only — no CLI,
loader validation, hook, sweep, quarantine, expiry, or coverage-mode backfill behavior.

1. `coverage_mode TEXT` added to `sot_artifacts` in `SCHEMA_SQL` (nullable, no default), plus a
   guarded `PRAGMA table_info` + `ALTER TABLE ... ADD COLUMN` migration ("Migration 6b") in
   `_migrate_schema`. No default per `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3.
2. `sot_artifact_revisions` (append-only observed-revision ledger) with the nine DCL-required
   fields plus audit columns and indexes.
3. `sot_registry_transaction_journal` with intent + completion columns and `journal_state` for
   deterministic recovery per `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1.
4. `sot_quarantine_receipts` binding every field `DCL-QUARANTINE-RETENTION-EXPIRY-001` requires,
   plus immutable `quarantined_at`/`expires_at` and `restore_pending`.

New tables are created via `CREATE TABLE IF NOT EXISTS` in `SCHEMA_SQL` (run on every DB open);
only the `coverage_mode` column needs the guarded ALTER migration for existing databases.

## Specification Links

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-002.md` — independent architecture GO.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` (v3) — coverage-mode locator semantics; no silent default.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` (v2) — declaration vs observed-revision split; revisions do not grant membership.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` (v1) — transaction journal / recoverable transactions.
- `DCL-QUARANTINE-RETENTION-EXPIRY-001` (v1) — quarantine receipt binding fields; immutable 30-day retention.
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001` (v1) — compound declaration/revision-ledger architecture.
- `GOV-PLATFORM-SOT-REGISTRY-001` (v2) — registry as platform artifact-membership authority.
- `GOV-WORK-TREE-HYGIENE-001` (v2) — registry-authoritative sweep and quarantine model.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active bounded PAUTH + operation-time freshness.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact approval governance (no formal-artifact mutation in this slice).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec linkage and spec-derived testing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered-file bridge authority, independent review, and VERIFIED commit-finalization gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; no `applications/<child>` touched.

## Requirement Sufficiency

Existing requirements sufficient. The Phase 1A-formalized specifications define the target
schema semantics; this slice implements only the additive storage substrate. No new or revised
requirement was required.

## Owner Decisions / Input

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — owner authorization of the
  program, cited by the active PAUTH.
- Owner mandate (2026-07-22 transcript) — carry WI-5441 through bounded per-slice proposals with
  independent GO/VERIFIED.
- Owner AUQ (2026-07-23, this session) — after a session restart dropped the interactive Prime
  Builder role (resolver fell back to loyal-opposition despite the recorded `::init gtkb pb`),
  the owner selected "Re-assert programmatically." Prime Builder role for session `87ea6b9f...`
  was restored via canonical `ensure_worker_session` (role_source `transcript_init_keyword`)
  before the implementation claim. Review independence is unaffected (keyed on session context,
  not role); the verifier must still be an unrelated session.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-001.md` / `-002.md` — architecture governance review and independent GO (defines the Registry Data Model this schema realizes).
- `bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md` — Phase 1A VERIFIED verdict (the nine specs realized here are `specified`).
- `bridge/gtkb-wi5441-registry-db-schema-002.md` — the independent GO (antigravity/C, session `e47005c5...`).
- `bridge/gtkb-wi5441-registry-db-schema-005.md` — the corrective NO-GO this REVISED responds to (Codex/A, session `A-2026-07-23T04-53-20Z`).
- `bridge/gtkb-wi5648-file-move-false-verification-incident-002.md` — precedent for rejecting unsupported terminal-looking `VERIFIED` when finalization evidence is absent (the failure class -005 guards against).

## Specifications Carried Forward

`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`,
`DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`,
`DCL-QUARANTINE-RETENTION-EXPIRY-001`, `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`,
`GOV-PLATFORM-SOT-REGISTRY-001`, `GOV-WORK-TREE-HYGIENE-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `GOV-ARTIFACT-APPROVAL-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Spec-to-Test Mapping

All tests in `groundtruth-kb/tests/test_registry_db_schema.py`; all executed, all PASS (re-run below).

| Governing spec clause | Test node / command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 — coverage_mode nullable, no default | `test_coverage_mode_present_nullable_no_default` | yes | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 — migration adds column, preserves rows at NULL | `test_migration_adds_coverage_mode_and_preserves_rows` | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1 + `DCL-QUARANTINE-RETENTION-EXPIRY-001` v1 — required journal/receipt/revision columns | `test_registry_tables_present_with_required_columns` | yes | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2 — observed revisions do not grant membership | `test_observed_revision_does_not_change_membership` | yes | PASS |
| GO invariant 3 — idempotent migration | `test_schema_migration_idempotent` | yes | PASS |
| GO invariant 4 + `GOV-PLATFORM-SOT-REGISTRY-001` v2 — parity preserved | `gt registry validate --json` | yes | PASS 50/50 |

## Commands Executed (re-run at current HEAD)

- `python -m pytest groundtruth-kb/tests/test_registry_db_schema.py -q` -> **5 passed**.
- `python -m ruff check <db.py> <test>` -> **All checks passed!**
- `python -m ruff format --check <db.py> <test>` -> **2 files already formatted**.
- `gt registry validate --json` -> `in_sync: true`, `toml_count: 50`, `projection_count: 50`, no divergences.
- `git diff --stat -- <db.py> <test>` -> `db.py` **94 insertions, 0 deletions** (single file; no commingled unrelated changes).

## Regression Group Disclosure (no overclaiming)

`python -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/unit/test_knowledge_db_artifacts.py platform_tests/scripts/test_check_sot_registry_completeness.py -q`
-> **97 passed, 2 failed.** The 2 failures are
`platform_tests/unit/test_knowledge_db_artifacts.py::TestSchemaExists::test_all_tables_exist`
and `::test_all_views_exist`. They are **pre-existing** (already red on HEAD: the actual schema
contains five `dispatch_lane*` tables + `current_dispatch_lane_projection_snapshots` view absent
from the tests' hardcoded expected lists, none added by this slice) and the file is outside this
slice's `target_paths`. Tracked by **`WI-5656`**. This slice does not claim the broader group is
green and does not remediate the out-of-scope file.

## Live-DB Migration Note

Opening the live `groundtruth.db` (via tests / `gt registry validate`) applies the additive
migration automatically — inherent `_ensure_schema` behavior, additive, idempotent,
parity-preserving (50/50). No KB record/data/membership mutation. `groundtruth.db` is left
unstaged; this slice performs no git add/commit/push/release/deploy.

## Finalization Path Set For The Verifier

For a clean atomic terminal `VERIFIED`, the `write_verdict.py --finalize-verified --include ...`
set must cover the reviewed implementation + report + full predecessor bridge chain (all
currently untracked except `db.py`, which is modified-and-clean at 94 additive lines):

- `groundtruth-kb/src/groundtruth_kb/db.py` (modified; 94 insertions, no unrelated changes)
- `groundtruth-kb/tests/test_registry_db_schema.py` (new)
- `bridge/gtkb-wi5441-registry-db-schema-001.md` ... `-006.md` (chain; `-004.md` retained as the
  append-only audit record of the superseded non-authoritative file-only VERIFIED)
- the new `-007` VERIFIED verdict the helper writes

A pathspec-limited commit over exactly this set is clean; the worktree's unrelated dirty files
are preserved and not captured.

## Recommended Commit Type

`feat:` — net-new registry storage substrate (one column, three tables, one migration) plus a
new focused test module; additive net-new capability.

## Verification Requested

Independent LO re-verification that: (a) the four DCL-required column sets are complete; (b)
`coverage_mode` is nullable with no default; (c) the migration is idempotent and row-preserving;
(d) projection parity remains 50/50; (e) no premature feature/behavior was added. The terminal
`VERIFIED`, if issued, MUST be produced by `write_verdict.py --finalize-verified` with the
include set above. Reviewer session context MUST differ from author `87ea6b9f...`.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

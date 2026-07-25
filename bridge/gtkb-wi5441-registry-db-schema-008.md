REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c58a8564-bed2-41d4-851b-075b84e86797
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Document: gtkb-wi5441-registry-db-schema
Version: 008
Responds to: bridge/gtkb-wi5441-registry-db-schema-007.md
bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-DB-SCHEMA-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_registry_db_schema.py"]

# WI-5441 Artifact Registry Phase 1B: DB Schema — REVISED Implementation Report (re-verification request after finalization-blocker repair)

## Revision Claim

This REVISED report responds to the NO-GO at `bridge/gtkb-wi5441-registry-db-schema-007.md`
(Codex/A, session `A-2026-07-23T04-53-20Z`). That NO-GO is a **bridge-finalization /
protected-commit** rejection only: its Verdict and Positive Confirmations explicitly accept the
Phase 1B `db.py` schema implementation as substantively verified (focused schema tests `5 passed`,
Ruff lint and format pass, `gt registry validate --json` reports parity 50/50 in-sync, review
independence holds, and the ADR/DCL clause preflight on version 006 exits 0 with zero blocking
gaps). The single finding F1 is that the mandatory atomic `VERIFIED` finalization could not
complete because the protected-commit checker counted the superseded, file-only predecessor
`bridge/gtkb-wi5441-registry-db-schema-004.md` as a second terminal `VERIFIED` candidate alongside
the new terminal verdict.

**No implementation change is made in this revision.** The `db.py` schema and the focused test
module `groundtruth-kb/tests/test_registry_db_schema.py` are unchanged since version 006. This
revision (a) records that the F1 finalization blocker has since been repaired by completed,
independently-governed bridge-tooling work that landed AFTER the NO-GO, (b) carries forward version
006's complete verification evidence unchanged, and (c) hands the verifier an updated, clean
finalization path set so the terminal `VERIFIED` can now be produced by the mandatory atomic
`write_verdict.py --finalize-verified` transaction.

## Findings Addressed

### F1 - P1 - The mandatory VERIFIED finalization transaction is blocked by uncommittable predecessor version 004

Response: Resolved by completed, independently-governed bridge-tooling repairs that post-date the
NO-GO and are committed on the current branch:

- **WI-5657** (commit `7b838d9e7`, 2026-07-23T15:00:05Z — "treat superseded predecessor VERIFIED as
  non-authoritative in protected-commit checker"). Added
  `scripts/check_protected_commit_authorization.py::_superseded_versioned_bridge()`, which
  classifies a numbered bridge file as a superseded predecessor when a higher-numbered version of
  the same slug is staged in the SAME commit transaction (`snapshot.selected_paths`). Both
  enforcement points now exclude such a predecessor:
  - The exactly-one-`VERIFIED`-candidate loop skips it ("Superseded predecessor VERIFIED is
    non-authoritative history, not a live terminal candidate"), so the v007 error
    `same-transaction clearance requires exactly one VERIFIED candidate; found 2: ...-004.md,
    ...-007.md` no longer fires for version 004.
  - The finalization-evidence finding returns `None` for it, so the v007 error `...-004.md:
    terminal VERIFIED bridge file lacks Commit Finalization Evidence` no longer fires.
- **WI-5659** (commits `f0b27999a` + `c0c4c40e4`, 2026-07-24T04:44–04:55Z — "restore governed
  commit-finalization (4 mechanisms)" plus its P1 audit-scratch bound). Hardens the governed
  commit-finalization path that the atomic `VERIFIED` transaction depends on.

The NO-GO's required-revision #2 directed Prime Builder to "file a successor response that cites a
completed bridge-sustaining repair to the finalizer/protected-commit checker." This REVISED cites
exactly that repair. Both errors quoted in v007 F1 map directly to code paths the repair now
guards, and `scripts/check_protected_commit_authorization.py` is committed-clean in the working
tree (not among the modified scripts), so the repaired behavior is live. Because supersession is
judged against the STAGED transaction, the repair is effective only when the finalization helper
stages version 004 alongside the new higher-numbered terminal `VERIFIED`; the updated Finalization
Path Set below does exactly that.

Required-revision #3 (no overclaiming green) and #4 (untracked predecessor chain plus reviewed path
set) from the parent NO-GO chain remain honored — see Regression Group Disclosure and Finalization
Path Set, carried forward unchanged from version 006.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active bounded PAUTH plus operation-time freshness.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact approval governance (no formal-artifact mutation in this slice).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec linkage and spec-derived testing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered-file bridge authority, independent review, and VERIFIED commit-finalization gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; no `applications/<child>` touched.

## Requirement Sufficiency

Existing requirements sufficient. No implementation change is made; no new or revised requirement
was required. This REVISED cites a completed, separately-governed repair (WI-5657 / WI-5659) and
does not itself mutate protected source, tests, configuration, or KB.

## Owner Decisions / Input

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — owner authorization of the
  artifact-registry program, cited by the active PAUTH
  `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-DB-SCHEMA-20260722`.
- Owner mandate (2026-07-22 transcript) — carry WI-5441 through bounded per-slice proposals with
  independent GO/VERIFIED.
- Owner AUQ (2026-07-24, this session `c58a8564-bed2-41d4-851b-075b84e86797`) — after diagnosing
  that WI-5441 Phase 1B was stuck at NO-GO v007 on a finalization blocker that WI-5657/WI-5659 had
  already repaired (roughly 10–24 hours after the NO-GO), the owner selected "Unblock Phase 1B
  now," authorizing this REVISED re-verification-request filing. This does not authorize any
  source/config/KB mutation; the implementation is unchanged from version 006. Review independence
  is unaffected (keyed on session context, not role); the verifier MUST be an unrelated session
  (author here is `c58a8564...`; the prior report author was `87ea6b9f...`).

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — controlling owner decision.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-001.md` / `-002.md` — architecture
  governance review and independent GO (defines the Registry Data Model this schema realizes).
- `bridge/gtkb-wi5441-artifact-registry-governance-formalization-execution-004.md` — Phase 1A
  VERIFIED verdict (the specs realized here are `specified`).
- `bridge/gtkb-wi5441-registry-db-schema-002.md` — the independent GO for this Phase 1B scope
  (antigravity/C, session `e47005c5...`).
- `bridge/gtkb-wi5441-registry-db-schema-005.md` — the corrective NO-GO that rejected the file-only
  `VERIFIED` at version 004 while positively confirming the schema implementation.
- `bridge/gtkb-wi5441-registry-db-schema-007.md` — the NO-GO this REVISED responds to (Codex/A,
  session `A-2026-07-23T04-53-20Z`); F1 is the finalization/protected-commit blocker addressed here.
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-001.md` through `-004.md` — the governed
  superseded-predecessor repair (committed as `7b838d9e7`) cited in the F1 response.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-002.md` — precedent for failing closed
  on unsupported terminal-looking bridge closure (the failure class the finalization gate protects).

## Specifications Carried Forward

`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`,
`DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`,
`DCL-QUARANTINE-RETENTION-EXPIRY-001`, `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`,
`GOV-PLATFORM-SOT-REGISTRY-001`, `GOV-WORK-TREE-HYGIENE-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `GOV-ARTIFACT-APPROVAL-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Verification Plan (Spec-to-Test Mapping)

All tests in `groundtruth-kb/tests/test_registry_db_schema.py`; all executed, all PASS. Unchanged
from version 006 (no implementation change).

| Governing spec clause | Test node / command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 — coverage_mode nullable, no default | `test_coverage_mode_present_nullable_no_default` | yes | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3 — migration adds column, preserves rows at NULL | `test_migration_adds_coverage_mode_and_preserves_rows` | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1 + `DCL-QUARANTINE-RETENTION-EXPIRY-001` v1 — required journal/receipt/revision columns | `test_registry_tables_present_with_required_columns` | yes | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2 — observed revisions do not grant membership | `test_observed_revision_does_not_change_membership` | yes | PASS |
| GO invariant 3 — idempotent migration | `test_schema_migration_idempotent` | yes | PASS |
| GO invariant 4 + `GOV-PLATFORM-SOT-REGISTRY-001` v2 — parity preserved | `gt registry validate --json` | yes | PASS 50/50 |

## Commands Executed (version 006 evidence, carried forward)

- `python -m pytest groundtruth-kb/tests/test_registry_db_schema.py -q` -> **5 passed**.
- `python -m ruff check <db.py> <test>` -> **All checks passed!**
- `python -m ruff format --check <db.py> <test>` -> **2 files already formatted**.
- `gt registry validate --json` -> `in_sync: true`, `toml_count: 50`, `projection_count: 50`, no divergences.
- `git diff --stat -- <db.py>` -> `db.py` **94 insertions, 0 deletions** (single file; no commingled unrelated changes — independently re-confirmed by the Prime Builder session filing this REVISED at HEAD).

## Regression Group Disclosure (no overclaiming)

`python -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/unit/test_knowledge_db_artifacts.py platform_tests/scripts/test_check_sot_registry_completeness.py -q`
-> **97 passed, 2 failed.** The 2 failures are
`platform_tests/unit/test_knowledge_db_artifacts.py::TestSchemaExists::test_all_tables_exist` and
`::test_all_views_exist`. They are **pre-existing** (already red on HEAD: the live schema contains
five `dispatch_lane*` tables plus `current_dispatch_lane_projection_snapshots` view absent from the
tests' hardcoded expected lists, none added by this slice) and the file is outside this slice's
`target_paths`. Tracked by **`WI-5656`**. This slice does not claim the broader group is green and
does not remediate the out-of-scope file.

## Finalization Path Set For The Verifier

For a clean atomic terminal `VERIFIED`, the `write_verdict.py --finalize-verified --include ...` set
must cover the reviewed implementation, the report, and the full predecessor bridge chain. Updated
for the current chain: the next terminal `VERIFIED` verdict the helper writes is **version 009**.

- `groundtruth-kb/src/groundtruth_kb/db.py` (modified; 94 insertions, no unrelated changes)
- `groundtruth-kb/tests/test_registry_db_schema.py` (new)
- `bridge/gtkb-wi5441-registry-db-schema-001.md` ... `-008.md` (full chain; `-004.md` retained as
  the append-only audit record of the superseded, non-authoritative file-only VERIFIED; the `-007`
  NO-GO and this `-008` REVISED are included)
- the new `-009` VERIFIED verdict the helper writes

With WI-5657 live, staging `-004.md` alongside the new `-009` VERIFIED causes `-004.md` to be
classified as a superseded predecessor and excluded from the terminal-`VERIFIED`-candidate count,
leaving exactly one live terminal `VERIFIED` candidate (`-009`). A pathspec-limited commit over
exactly this set is clean; the worktree's unrelated dirty files are preserved and not captured.

## Scope Changes

None. No implementation, specification, test, configuration, or KB change is made in this revision.
This is a re-verification request citing a completed, separately-governed external repair.

## Pre-Filing Preflight Subsection

The governed revise-helper `file` path runs `scripts/bridge_applicability_preflight.py
--content-file` and `scripts/adr_dcl_clause_preflight.py --content-file` against this content before
publishing. This content carries forward version 006's Specification Links and spec-to-test mapping
unchanged, which cleared the applicability preflight (`missing_required_specs: []`) and the clause
preflight (0 blocking gaps) at version 006 per the v007 verdict's Positive Confirmations. The
advisory-only misses reported at v007 (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are non-blocking.

## Risk And Rollback

Risk: minimal. No source, test, configuration, or behavior change is made; the implementation is
byte-identical to version 006. The only residual risk is that the atomic finalization re-attempt
fails for an unforeseen reason, in which case the verifier issues NO-GO again and the thread remains
revisable — no partial or false-terminal state is created because the finalization helper fails
closed and removes any candidate verdict on commit failure. Rollback: none required; this REVISED is
append-only bridge history and mutates no project state.

## Recommended Commit Type

`feat:` — the eventual `VERIFIED` finalization commit carries the net-new registry storage substrate
(one column, three tables, one migration) plus a new focused test module: additive net-new
capability. This REVISED report itself produces no source commit.

## Verification Requested

Independent Loyal Opposition re-verification and atomic terminal `VERIFIED` produced only via
`python .claude/skills/verify/helpers/write_verdict.py --slug gtkb-wi5441-registry-db-schema
--finalize-verified` with the include set above. Confirm: (a) the four DCL-required column sets are
complete; (b) `coverage_mode` is nullable with no default; (c) the migration is idempotent and
row-preserving; (d) projection parity remains 50/50; (e) no premature feature/behavior was added;
and (f) the finalization transaction now completes cleanly (WI-5657 / WI-5659 repair effective).
Reviewer session context MUST differ from author `c58a8564-bed2-41d4-851b-075b84e86797` and from the
version 006 author `87ea6b9f-89d5-4e90-a637-a7f9fe8cb561`.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

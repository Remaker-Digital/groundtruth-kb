NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4521-backlog-update-source-spec-id
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4521
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/tests/test_backlog_update_source_spec_id.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4521: Add `--source-spec-id` to `gt backlog update` so existing work items can be backfilled

## Summary

WI-4521 (P3, `bridge_dispatch`, origin=improvement): `gt backlog add` accepts `--source-spec-id` (cli.py:2112) and sets it at creation, but `gt backlog update` exposes NO such flag — so there is no supported CLI path to backfill or correct `source_spec_id` on an existing work item. WI-4517 part (b) needed exactly that (set `source_spec_id=GOV-CODE-QUALITY-BASELINE-001` on the CQ Slice-2 tracker) and the gap forced an ad-hoc workaround.

**Cycle-10 triage (this session) confirms WI-4521 is genuinely OPEN, and shows the fix is even smaller than the WI suggests:**

- `gt backlog update` (cli.py:2817-2876) declares options for `resolution-status`, `stage`, `priority`, `related-bridge-threads`, `status-detail`, `title`, `description` — **no `--source-spec-id`**.
- The CLI command threads its options into `BacklogUpdateRequest` (cli_backlog_update.py:34) and then `update_backlog_item` builds a `fields` dict and passes it as `**fields` to `db.update_work_item` (cli_backlog_update.py:201-207).
- `db.update_work_item` (db.py:4339) already carries forward `source_spec_id` from `current` when not in `**fields` (`:4367`), so it accepts a new `source_spec_id` override transparently. **The receiver already supports the field perfectly.**

So the gap is purely on the CLI surface. Fix = add the `--source-spec-id` Click option to the `update` command, add `source_spec_id` to `BacklogUpdateRequest`, set `fields["source_spec_id"]` when provided. Three minimal touches + a test.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4521 is the backlog authority for this fix (P3 tooling-completeness improvement on the standing backlog's primary update surface). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, three small in-PAUTH source touches + one test), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no review packet, no Phase/Path-deferred marker, and no formal-artifact-approval packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface for a single WI.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4521; allows `source` + `test_addition`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger); it is a CLI-surface fix that does not modify `bridge/INDEX.md` or any bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a backfill-roundtrip and a no-flag-no-change guard.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked CLI-completeness fix with explicit test coverage.

## Requirement Sufficiency

Existing requirements sufficient. The gap is documented (WI-4521 + the WI-4517 (b) ad-hoc workaround it surfaced), cycle-10 triage confirmed it open and localized the fix to three trivial touches on the CLI surface, the bounded PAUTH authorizes the `source` + `test_addition` work, and the `db.update_work_item` receiver already supports the field. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4521 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **`gt backlog add` precedent** — the canonical creation-time CLI exposure of `--source-spec-id` (cli.py:2112), already wired through `db.insert_work_item`. This proposal mirrors that surface on the `update` command.
- **`db.update_work_item` carry-forward semantics** (db.py:4339-4373) — the receiver already preserves unchanged fields from `current` and accepts `**fields` overrides, so adding `source_spec_id` to the CLI's `fields` dict is byte-clean.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live CLI source instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4521 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`). This fix stays within that scope: it edits the CLI + its supporting service (source) + adds a test. No formal-artifact or KB mutation.

## Design

Three minimal touches:

1. **`groundtruth-kb/src/groundtruth_kb/cli.py` — `backlog_update`** (~`:2817-2876`): add `@click.option("--source-spec-id", default=None, help="New source specification id.")` to the option block (mirroring the `add` command's `:2112` declaration), add `source_spec_id: str | None` to the function signature, and thread it into the `BacklogUpdateRequest`.
2. **`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` — `BacklogUpdateRequest`** (`:34-48`): add `source_spec_id: str | None = None` to the dataclass.
3. **`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` — `update_backlog_item`** (~`:170-178`): in the `fields` construction block (where `title`/`description` are conditionally set), add `if request.source_spec_id is not None: fields["source_spec_id"] = request.source_spec_id`. The existing `**fields` pass-through at `:206` carries it into `db.update_work_item`, which already supports it.

No change to vocabulary validation (`source_spec_id` is free-form text per existing schema), no change to the text-edit gate (which guards `title`/`description` only), no change to the GOV-15 owner-approval gate (which guards terminal-status transitions on defect/regression items), no change to `db.update_work_item`'s logic.

**Optional companion: dry-run reporting.** The existing `--dry-run` path returns a `fields` dict; the addition appears there automatically. No design change required.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `groundtruth-kb/tests/test_backlog_update_source_spec_id.py`) | Method |
|---|---|---|
| `--source-spec-id` accepted and persisted on update (WI-4521 root) | `test_update_sets_source_spec_id` | seed WI with `source_spec_id=None`; invoke `gt backlog update <WI> --source-spec-id GOV-FOO-001 --change-reason "…"`; assert the new row carries `source_spec_id == "GOV-FOO-001"` |
| Backfill: blank → set works (WI-4517 (b) use case) | `test_backfill_blank_source_spec_id` | seed WI with `source_spec_id=None`; update with the new flag → assert it's set |
| Correction: existing → new works | `test_correct_existing_source_spec_id` | seed WI with `source_spec_id="OLD"`; update to `"NEW"` → assert overwrite |
| No flag → no change (carry-forward preserved) | `test_no_flag_preserves_source_spec_id` | seed WI with `source_spec_id="X"`; update unrelated field WITHOUT `--source-spec-id` → assert `source_spec_id` remains `"X"` |
| Dry-run reports the would-be update | `test_dry_run_reports_source_spec_id` | invoke with `--dry-run --source-spec-id "Y"` → `fields` payload includes `source_spec_id="Y"`, no row written |
| Other gates unaffected (text-edit gate, GOV-15) | `test_other_gates_unchanged_with_source_spec_id` | combine `--source-spec-id` with `--title` (still subject to text-edit gate) and with a terminal-status transition (still subject to GOV-15) → gates fire as today |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on all changed files; `python -m pytest groundtruth-kb/tests/test_backlog_update_source_spec_id.py -q --tb=short`; plus the existing backlog-update regression suite must still pass.

## Risk / Rollback

- **Risk: very low.** Three single-line additions on a well-tested CLI surface, mirroring the existing `add` precedent. The receiver `db.update_work_item` already supports the field; no schema change, no migration, no new dependency. Cannot affect any other CLI flag, the GOV-15 gate, the text-edit gate, or any non-`backlog update` path.
- **Rollback:** revert the three additions + delete the test. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`feat:` — net-new CLI capability (a new `--source-spec-id` flag on `gt backlog update`), exposing an already-supported receiver field. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

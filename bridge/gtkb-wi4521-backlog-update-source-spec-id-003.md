NEW

bridge_kind: implementation_report
Document: gtkb-wi4521-backlog-update-source-spec-id
Version: 003
Responds-To: bridge/gtkb-wi4521-backlog-update-source-spec-id-002.md
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T07-34-33Z-prime-builder-B-6f5291
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4521
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/tests/test_backlog_update_source_spec_id.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

# WI-4521 Implementation Report: `--source-spec-id` on `gt backlog update`

## Summary

Implemented the GO'd proposal (`-002` GO) exactly as scoped: exposed the
already-supported `source_spec_id` work-item field through the `gt backlog update`
CLI surface, mirroring the `gt backlog add` precedent (cli.py:2112). The
implementation is three source touches plus one focused, spec-derived test module.
The `db.update_work_item` receiver (db.py:4367) already carried forward and
accepted `source_spec_id`, so no receiver, schema, migration, or vocabulary
change was needed. Implementation-start authorization packet was minted from the
live GO (`packet_hash: sha256:67aad0a7b32554308168c9e04ad2afa00ab1f9ca3461e6694a379241cce52926`,
expires 2026-06-14T09:39:46Z).

## Specification Links

Specifications governing this implementation (carried forward from the `-002` GO):

- **GOV-STANDING-BACKLOG-001** — backlog authority for this P3 tooling-completeness fix. `CLAUSE-VISIBILITY-BULK-OPS` is `not_applicable`: single-WI scope, three in-PAUTH source touches + one test, no bulk operation.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeded under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4521; allows `source` + `test_addition`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge; no `bridge/INDEX.md` workflow-state mutation beyond this report's own audit-trail entry.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (table below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all touched/created paths are in-root under `E:\GT-KB\groundtruth-kb\`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**, **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tested CLI-completeness fix.

## Implementation Evidence

### 1. CLI help readback (proves the flag is exposed)

```text
python -m groundtruth_kb.cli backlog update --help
  -> --source-spec-id TEXT          New source specification id (set, backfill, or correct).
```

### 2. Code evidence (option threaded into request + fields dict only when provided)

`groundtruth-kb/src/groundtruth_kb/cli.py` (WI-4521 contribution = 3 lines):

```text
+@click.option("--source-spec-id", default=None, help="New source specification id (set, backfill, or correct).")
+    source_spec_id: str | None,            # backlog_update signature
+        source_spec_id=source_spec_id,     # threaded into BacklogUpdateRequest(...)
```

`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` (2 lines):

```text
+    source_spec_id: str | None = None      # BacklogUpdateRequest dataclass field
+    if request.source_spec_id is not None: # fields dict, set only when provided
+        fields["source_spec_id"] = request.source_spec_id
```

The `fields` dict is the existing `**fields` pass-through to `db.update_work_item`,
which carries the value through unchanged. The field is added to `fields` ONLY
when the flag is provided, so absence preserves the receiver's carry-forward.

### 3. Target-path diff summary (scope compliance)

```text
git diff --stat -- cli.py cli_backlog_update.py
  groundtruth-kb/src/groundtruth_kb/cli.py            | 266 +++++ (see note)
  groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py |   3 +
git status --short -- tests/test_backlog_update_source_spec_id.py
  ?? groundtruth-kb/tests/test_backlog_update_source_spec_id.py
```

**Transparency note (scope honesty):** `cli.py` was already modified (`M`) in the
working tree at session start by prior/parallel work unrelated to WI-4521; the
266-insertion stat conflates that pre-existing edit with my change. My WI-4521
contribution to `cli.py` is exactly the **3 `source_spec_id` lines** shown in
section 2 (verified by `git diff -- cli.py | grep source_spec_id`). All three
touched paths are within the GO's approved `target_paths`; no out-of-scope path
was modified. Per dispatched-worker discipline this report does **not** commit;
the pre-existing `cli.py` edit remains the owning session's responsibility.

## Spec-to-Test Mapping (Specification-Derived Verification Gate)

Test module: `groundtruth-kb/tests/test_backlog_update_source_spec_id.py` (8 tests).

| Acceptance criterion (spec clause) | Test | Result |
|---|---|---|
| `--source-spec-id` accepted + persisted on update (WI-4521 root; GOV-STANDING-BACKLOG-001) | `test_update_sets_source_spec_id` | PASS |
| Backfill blank -> value (WI-4517 (b) use case) | `test_backfill_blank_source_spec_id` | PASS |
| Correction existing -> new value | `test_correct_existing_source_spec_id` | PASS |
| No flag -> carry-forward preserved (db.py:4367 semantics) | `test_no_flag_preserves_source_spec_id` | PASS |
| Dry-run reports would-be update, writes no version | `test_dry_run_reports_source_spec_id` | PASS |
| Text-edit gate still fires with `--title` (no bypass; WI-4357) | `test_text_edit_gate_unchanged_with_source_spec_id` | PASS |
| GOV-15 still fires for defect terminal transition (no bypass) | `test_gov15_gate_unchanged_with_source_spec_id` | PASS |
| Flag discoverable on `--help` surface | `test_update_help_lists_source_spec_id` | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all paths under `E:\GT-KB\groundtruth-kb\` | PASS |

## Commands Executed (exact + observed results)

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4521-backlog-update-source-spec-id
  -> packet minted; latest_status=GO; packet_hash=sha256:67aad0a7...cce52926; expires 2026-06-14T09:39:46Z

groundtruth-kb/.venv/Scripts/python.exe -m ruff check \
  groundtruth-kb/src/groundtruth_kb/cli.py \
  groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py \
  groundtruth-kb/tests/test_backlog_update_source_spec_id.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same 3 files>
  -> 3 files already formatted

groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= \
  groundtruth-kb/tests/test_backlog_update_source_spec_id.py \
  groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short
  -> 19 passed in 9.22s   (8 new WI-4521 tests + 11 existing backlog-update regression tests)
```

Both code-quality gates were run as SEPARATE gates (`ruff check` AND
`ruff format --check`) per the file-bridge-protocol pre-file requirement.

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new owner AskUserQuestion is
required to implement or verify this work.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4521 under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (allowed: `source`, `test_addition`). This implementation stayed within that scope (CLI + supporting service source + one test; no formal-artifact or KB mutation).
- The `-002` GO explicitly recorded "No owner action is required for this GO."

## Recommended Commit Type

`feat:` — net-new CLI capability (the `--source-spec-id` flag on
`gt backlog update`), exposing an already-supported receiver field. The diff is
additive (new option + dataclass field + conditional `fields` assignment + new
test module); no behavior change to existing flags, the text-edit gate, the
GOV-15 gate, or `db.update_work_item`. Per the Conventional Commits discipline
in `.claude/rules/file-bridge-protocol.md`.

## Risk / Rollback

- **Risk: very low.** Three single-line additions on a well-tested CLI surface, mirroring the existing `add` precedent; the receiver already supported the field. No schema change, migration, or new dependency. Negative tests confirm the text-edit and GOV-15 gates are not bypassed.
- **Rollback:** revert the 3 + 2 source lines and delete the test module. No migration, no schema change, no KB mutation.

## Verification Request

Loyal Opposition: please verify the spec-to-test mapping and execute (or inspect
execution of) the focused suite + code-quality gates, then record `VERIFIED` or
`NO-GO`. No owner action is required.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

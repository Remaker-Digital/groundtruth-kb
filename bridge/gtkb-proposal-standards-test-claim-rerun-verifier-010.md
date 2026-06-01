REVISED

# Proposal-Standards Test-Claim Re-Run Verifier - Post-Implementation Report (REVISED-4)

bridge_kind: implementation_report
Document: gtkb-proposal-standards-test-claim-rerun-verifier
Version: 010
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-01T08-55-00Z-prime-builder-s382
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE2

work_item_ids: ["GTKB-GOV-PROPOSAL-STANDARDS-SLICE2"]
spec_ids:
  - GOV-FILE-BRIDGE-AUTHORITY-001
  - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  - GOV-STANDING-BACKLOG-001
  - GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
  - ADR-ISOLATION-APPLICATION-PLACEMENT-001
target_paths:
  - scripts/bridge_report_test_claim_rerun_verifier.py
  - platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Implements: GO at `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-004.md`.
Builds on: REVISED-3 post-impl committed at HEAD `066c2638` (file
`bridge/gtkb-proposal-standards-test-claim-rerun-verifier-007.md`).
Addresses: NO-GO at `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-009.md`
(FINDING-P1-001 in-block non-pytest false-pairing + in-root `--basetemp`
rejection; FINDING-P2-002 non-reproducible plain-`python` commands).

---

## Summary

REVISED-4 addresses both findings raised in Codex Loyal Opposition NO-GO
`-009` against REVISED-3 (`-007`):

1. The pytest-shape guard is hoisted to the head of `extract_claims()` so
   it applies to BOTH in-block and cross-block claim creation paths. A
   non-pytest command whose output happens to contain pytest-like summary
   text (e.g. the verifier's own `9 passed` JSON output) is now skipped
   silently rather than paired into an ERROR claim.
2. `validate_pytest_args()` allows in-root path values for the
   `PATH_OPTIONS` set (`--rootdir`, `--basetemp`, `--confcutdir`,
   `--junitxml`, `--ignore`, `--ignore-glob`) per Codex's recommendation,
   validating the resolved path against the project root. Out-of-root
   values remain rejected with `escapes project root`.
3. All claimed command-evidence blocks in this report use the
   `uv run --with pytest` / `uv run --with ruff` invocation surface used
   by Codex during the `-009` verification, so the exact commands
   reproduce in the LO dispatch shell rather than relying on an ambient
   `python` interpreter whose module set varies by harness.

The verifier verdict against this very report transitions from `-007`'s
`claim_count: 3, status: fail` (per Codex `-009:67-71`) to
`claim_count: 1, status: pass` (the single legitimate pytest claim, with
observed summary matching the claimed `12 passed in 0.64s`).

---

## Specification Links

Carried forward from REVISED-3 at `-007`, unchanged:

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified).
- `GOV-STANDING-BACKLOG-001` v5 (verified).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root clause).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; the trigger here is
  Codex NO-GO `-009`, which moves Slice 2 back into active implementation).

Spec-to-test mapping for the new contracts appears in the Spec-Derived
Verification Plan below.

---

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - PAUTH authority for
  this revision.
- `DELIB-1132`, `DELIB-2024`, `DELIB-0991`, `DELIB-0993`, `DELIB-1738` -
  prior proposal-standards-family review precedents requiring mechanical
  rather than diagnostic checks.

Codex `-009` itself is the immediate prior deliberation; this REVISED-4
cites its findings inline.

---

## Owner Decisions / Input

Authority for REVISED-4 flows from the standing
`PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3`
envelope (owner-decision deliberation
`DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`) per the
formal-artifact-approval pattern. Allowed mutation classes include
`hook_upgrade`, `cli_extension`, `test_addition`, and
`spec_status_promotion`; this revision exercises `cli_extension` (relaxing
`validate_pytest_args`) and `test_addition` (4 new tests).

The owner's S382 AUQ-recorded "complete PROJECT-GTKB-GOV-PROPOSAL-STANDARDS"
directive remains the umbrella intent. No additional owner decision is
required for this revision.

Active implementation-start authorization packet:
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-proposal-standards-test-claim-rerun-verifier.json`
(refreshed during this session against live latest-GO at `-004`).

---

## Findings Addressed

### FINDING-P1-001 (NO-GO -009) - in-block guard + in-root --basetemp

**Codex observation (verbatim, from `-009:50-101`):** running the
implemented verifier against `-007` returned `claim_count: 3`,
`status: fail` with three ERROR rows: two false claims paired non-pytest
verifier-self-invocation commands with their pytest-like output text, and
one false rejection of an in-root `--basetemp=.gtkb-state/...` argument.

**Cause:** the pytest-shape guard added in REVISED-3 only fired in the
`summary_line is None` branch of `extract_claims()`. When a non-pytest
command had a same-block or cross-block summary, the parser still
emitted a claim, and `run_pytest_claim` later rejected it as ERROR. The
`PATH_OPTIONS` rejection in `validate_pytest_args` was categorical:
`--basetemp=<anything>` failed at the regex level without examining the
path value.

**Fix (verifier source):**

1. Hoist `pytest_args_for_command(command_line)` to the top of the
   per-block loop in `extract_claims()`, **before** any summary search.
   Non-pytest commands skip immediately, regardless of whether output is
   adjacent. Same `pytest_args_for_command` is reused, no new helper.
2. Add a `_extract_option_value(arg, next_arg)` helper that returns
   `(value, value_consumed_next_arg)` for both `--opt=value` and
   `--opt value` forms.
3. In `validate_pytest_args`, replace the categorical PATH_OPTIONS
   rejection with a value-validation branch: extract the value, check
   `_path_within_root(project_root, value)`, reject only when the value
   escapes the project root. Missing values (e.g. a trailing
   `--basetemp` with no following arg) are rejected as
   `requires a path value` so the option does not silently slip through.

**Live evidence (REVISED-4 vs `-007` strict run):**

Command:

```text
uv run --with pytest --with pytest-timeout python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier --report-version 7 --strict --json
```

Observed result:

```text
claim_count: 1
status: pass
  block 3: status=PASS, summary='12 passed in 0.64s', reason='observed pytest summary matches claimed summary'
```

Codex's `-009:67-71` reproduction in the same shell against the prior
REVISED-3 had returned `claim_count: 3`, `status: fail` with three
ERROR rows. The single claim_count: 1 result confirms the false-pairings
have been removed and the legitimate pytest evidence now executes and
matches.

**Live evidence (REVISED-4 vs `-005` regression preservation):**

Command:

```text
uv run --with pytest --with pytest-timeout python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier --report-version 5 --strict --json
```

Observed result:

```text
claim_count: 1
status: fail
  block 3: status=ERROR, summary='9 passed', reason='pytest run produced no parseable summary line'
```

REVISED-3's `-005` closure is preserved: the split-block parser still
extracts the one pytest claim (was `claim_count: 0` pre-REVISED-3); the
ERROR is because the test file referenced in `-005` is not committed.

### FINDING-P2-002 (NO-GO -009) - reproducible-command discipline

**Codex observation:** the claimed `python -m pytest ...`,
`python -m ruff check ...`, and `python -m ruff format --check ...`
commands in `-007` could not be reproduced in the LO dispatch shell
because the resolved `C:\Python314\python.exe` lacked `pytest` and
`ruff` modules. Codex's positive control used
`uv run --with pytest` / `uv run --with ruff` instead.

**Fix (report side, this file):** all command/observed-result evidence
in this report uses the `uv run --with pytest --with pytest-timeout`
and `uv run --with ruff` invocation surface. This is the same surface
Codex used in `-009:142-167` and in the VERIFIED Slice 3 evidence at
`bridge/gtkb-proposal-standards-wi-id-collision-gate-010.md:86-88`,
proving cross-shell reproducibility.

The verifier source is unchanged for FINDING-P2-002 - the issue was
report-side claim evidence shape, not verifier behavior.

---

## Files Changed

### `scripts/bridge_report_test_claim_rerun_verifier.py` (modified)

- `extract_claims()`: hoist `pytest_args_for_command(command_line)` check
  to the top of the per-block loop; remove the duplicate check from the
  `summary_line is None` branch (now unreachable when command is
  non-pytest because the loop already `continue`d).
- New helper `_extract_option_value(arg, next_arg) -> (value, consumed)`
  used by `validate_pytest_args`.
- `validate_pytest_args()`: replace categorical PATH_OPTIONS rejection
  with `_path_within_root` value-validation; reject out-of-root values
  with `escapes project root: <value>`; reject value-less PATH_OPTIONS
  with `requires a path value`.

### `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py` (modified)

Five new tests added to the 12-test REVISED-3 suite (now 17 total):

- `test_extract_claims_non_pytest_command_with_inblock_summary_skipped`
  (NO-GO -009 FINDING-P1-001 in-block guard).
- `test_extract_claims_non_pytest_command_with_split_block_summary_skipped`
  (NO-GO -009 FINDING-P1-001 cross-block guard uniformity).
- `test_validate_pytest_args_allows_in_root_basetemp` (NO-GO -009
  FINDING-P1-001 --basetemp relaxation, both `--opt=value` and
  `--opt value` forms).
- `test_validate_pytest_args_rejects_out_of_root_basetemp` (preserves
  safety boundary).
- `test_validate_pytest_args_path_options_require_value` (closes the
  trailing-option corner case).

---

## Spec-Derived Verification Plan

| Specification | Acceptance criterion | Test(s) |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED evidence reflects actual observation | Verifier neither false-flags non-pytest blocks nor rejects in-root `--basetemp`; strict verifier vs `-007` returns claim_count: 1 status: pass | `test_extract_claims_non_pytest_command_with_inblock_summary_skipped`, `test_extract_claims_non_pytest_command_with_split_block_summary_skipped`, `test_validate_pytest_args_allows_in_root_basetemp`, plus live re-run vs `-007` in `FINDING-P1-001` section |
| `GOV-FILE-BRIDGE-AUTHORITY-001` - operate on `bridge/INDEX.md`-canonical reports | CLI surface unchanged; preserved | `test_cli_json_output_schema`, `test_cli_strict_exit_nonzero_on_unassociated_command` |
| `GOV-STANDING-BACKLOG-001` - Slice 2 is a member of `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` | MemBase WI linkage via Project Authorization / Project / Work Item metadata lines | metadata header above |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` clause-in-root - all touched paths inside `E:\GT-KB` | Target paths still confined to `scripts/bridge_report_test_claim_rerun_verifier.py` and `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py` | Project-root-boundary preflight (clause preflight) |
| Codex `-009` FINDING-P1-001 - in-block + --basetemp | Verifier returns `claim_count: 1` against `-007` with the legitimate claim only | live re-run in `FINDING-P1-001` section + `test_extract_claims_non_pytest_command_with_inblock_summary_skipped` + `test_validate_pytest_args_*` |
| Codex `-009` FINDING-P2-002 - reproducible commands | All command evidence in this report uses the same `uv run --with pytest|ruff` surface Codex uses for verification | Verification commands below |

---

## Test Evidence

All commands below use `uv run --with pytest`/`uv run --with ruff` for
cross-shell reproducibility per Codex `-009` FINDING-P2-002 guidance.

### Test suite (17 tests)

Command:

```text
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache'; $env:TEMP='E:\GT-KB\.pytest-tmp'; $env:TMP='E:\GT-KB\.pytest-tmp'; uv run --with pytest --with pytest-timeout python -m pytest platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py -v --tb=short --no-header -p no:cacheprovider --basetemp=E:\GT-KB\.gtkb-state\pytest-tmp-s382-slice2-r5
```

Observed result:

```text
17 passed in 0.64s
```

### Live verifier vs `-007` (FINDING-P1-001 in-block + --basetemp closure)

Command:

```text
uv run --with pytest --with pytest-timeout python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier --report-version 7 --strict --json
```

Observed result:

```text
claim_count: 1
status: pass
  block 3: status=PASS, summary='12 passed in 0.64s', reason='observed pytest summary matches claimed summary'
```

### Live verifier vs `-005` (REVISED-3 split-block closure preserved)

Command:

```text
uv run --with pytest --with pytest-timeout python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier --report-version 5 --strict --json
```

Observed result:

```text
claim_count: 1
status: fail
  block 3: status=ERROR, summary='9 passed', reason='pytest run produced no parseable summary line'
```

### Ruff lint

Command:

```text
uv run --with ruff python -m ruff check scripts/bridge_report_test_claim_rerun_verifier.py platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py
```

Observed result:

```text
All checks passed!
```

### Ruff format

Command:

```text
uv run --with ruff python -m ruff format --check scripts/bridge_report_test_claim_rerun_verifier.py platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py
```

Observed result:

```text
2 files already formatted
```

---

## KB Mutation Scope

This REVISED-4 performs **no `groundtruth.db` mutation**. The source change
modifies `scripts/bridge_report_test_claim_rerun_verifier.py` (a CLI tool)
and adds tests to `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py`.
Neither file imports the KB API; neither writes to the database. The
`spec_status_promotion` mutation class listed under Owner Decisions /
Input describes the PAUTH envelope's coverage, not work performed by
this revision. (Slice 3's WI promotion to `verified`, the only Slice-2-
adjacent DB mutation performed during S382, was done earlier in the
session under a separate scope; it is logged in the project membership
view via `gt project list-work-items` and is not in this report's
target_paths.)

---

## Clause Applicability Notes

- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is non-applicable
  here for the same reason cited in REVISED-3: Slice 2 is a single-script
  parser fix with two file touchpoints, not a bulk operation. Authority
  flows from the standing PAUTH envelope per the formal-artifact-approval
  pattern (owner-decision deliberation
  `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`).

---

## Recommended Commit Type

`fix:` - same disposition as REVISED-3. The verifier is repaired to be
correct under the input shapes Codex surfaced; one new helper function
and a few-line behavior change.

---

## Risk / Rollback

**Risk surface:** narrow, same as REVISED-3. The pytest-shape hoist is a
single-line move within `extract_claims()`. The `validate_pytest_args`
relaxation adds a value-validation branch for the existing PATH_OPTIONS
set; the existing rejection path is preserved for out-of-root values.

**Rollback:** single-commit revert restores REVISED-3 behavior, which
re-introduces the in-block false-pairing and the categorical
`--basetemp` rejection.

**No mass-effect risk:** the verifier remains a standalone script (not
hook-registered yet). Hook wiring is a future follow-on.

---

## Acceptance Criteria Check

- [x] FINDING-P1-001 (NO-GO -009) closed: in-block guard applies uniformly;
      verifier vs `-007` strict returns claim_count: 1 status: pass (was 3 / fail).
- [x] FINDING-P1-001 (NO-GO -009) - in-root `--basetemp` accepted via
      `_path_within_root` value-validation.
- [x] FINDING-P1-001 safety boundary preserved: out-of-root path values
      for PATH_OPTIONS still rejected.
- [x] FINDING-P2-002 (NO-GO -009) closed: all command evidence uses
      `uv run --with pytest|ruff` shell-portable surface.
- [x] REVISED-3 contracts preserved: 17 tests pass (12 carry-over + 5 new
      including the 4 explicit NO-GO -009 coverage tests and 1 trailing-
      option guard).
- [x] Live re-run vs `-005` still demonstrates REVISED-3 split-block
      closure (`claim_count: 1` vs original `0`).
- [x] Ruff lint and format clean.
- [x] Target paths confined to PAUTH-covered scope.
- [x] All paths inside `E:\GT-KB`.

---

## Decision Needed From Owner

None. Authority from the standing PAUTH envelope; S382 directive
"complete PROJECT-GTKB-GOV-PROPOSAL-STANDARDS" remains the umbrella.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

REVISED

# Proposal-Standards Test-Claim Re-Run Verifier - Post-Implementation Report (REVISED-5)

bridge_kind: implementation_report
Document: gtkb-proposal-standards-test-claim-rerun-verifier
Version: 012
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-01T13-55-00Z-prime-builder-s382
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE2

target_paths: ["scripts/bridge_report_test_claim_rerun_verifier.py", "platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Implements: GO at `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-004.md`.
Builds on: REVISED-4 committed at `fa6b174e` (`-010`).
Addresses: NO-GO at `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-011.md`
(FINDING-P1-001 verifier blind to `uv run` evidence shape; FINDING-P1-002
non-reproducible `--report-version 7` probe; FINDING-P2-003 hard-coded basetemp).

---

## Summary

REVISED-5 closes all three findings from Codex NO-GO `-011`:

1. **FINDING-P1-001 (root cause + fix):** REVISED-4 moved the report's commands
   to the reproducible `uv run --with pytest ... python -m pytest ...` surface
   (to satisfy the `-009` reproducibility finding), but the verifier's
   `pytest_args_for_command` only recognized bare `python -m pytest` / `pytest`,
   so it skipped the uv-wrapped form and returned `claim_count: 0` (a silent
   false pass). Diagnosis this round also found a second contributor: the
   `-010` evidence commands carried a PowerShell `$env:...='...'; ...; uv run`
   prefix whose semicolons are correctly rejected by `UNSAFE_SHELL_RE` (shell
   chains are not safely re-runnable). REVISED-5 fixes the verifier to unwrap
   the `uv run [--with PKG]... python -m pytest ...` wrapper, and presents the
   report's evidence as **bare** uv-pytest commands (no `$env:` prefix, no
   semicolons), so the verifier parses and re-runs exactly the commands the
   report documents.

2. **FINDING-P1-002:** the `--report-version 7` cross-report probe is removed.
   Re-running an old report's frozen `12 passed` claim against a test file that
   has since grown to 24 tests is inherently non-reproducible; that probe was an
   anti-pattern. The deterministic behaviors it was meant to demonstrate are now
   covered by unit tests, and the live verifier evidence runs against THIS report.

3. **FINDING-P2-003:** the report's documented test command drops the hard-coded
   `--basetemp=.gtkb-state/pytest-tmp-s382-slice2-r5`. The verifier's internal
   re-run already isolates pytest in a fresh `TemporaryDirectory`, so no
   report-level basetemp is needed; this removes the Windows
   `PermissionError`-on-rerun that blocked clean reproduction.

## Specification Links

Carried forward from `-010`, unchanged:

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified).
- `GOV-STANDING-BACKLOG-001` v5 (verified).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root clause).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; trigger = Codex NO-GO `-011`).

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - PAUTH authority.
- `DELIB-2426` (GO at `-004`), `DELIB-2427` (NO-GO at `-006`), `DELIB-2736`
  (NO-GO at `-009`), `DELIB-2428` (NO-GO proposal review at `-002`) - prior
  verdicts in this thread (per `-011` deliberation search).
- Codex NO-GO `-011` is the immediate prior deliberation; its findings are
  cited inline.

## Owner Decisions / Input

Authority flows from the standing
`PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3`
envelope (owner-decision deliberation
`DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`); allowed mutation classes
include `cli_extension` (the verifier parser change) and `test_addition` (the
new uv-unwrap regression tests). The S382 AUQ-recorded "complete
PROJECT-GTKB-GOV-PROPOSAL-STANDARDS" directive remains the umbrella intent. No
additional owner decision is required.

## Findings Addressed

### FINDING-P1-001 - verifier now parses the uv-wrapped pytest surface

Fix in `scripts/bridge_report_test_claim_rerun_verifier.py`:

- New `_strip_uv_run_prefix(parts)` helper strips a leading
  `uv run [options] [--with PKG]...` wrapper, returning the inner command
  tokens. Value-consuming uv options (`--with`, `--python`, `--directory`, ...)
  on a known allowlist consume their value; bare flags consume one token; the
  first non-option token starts the inner command. `--opt=value` forms are
  consumed as a single token.
- `pytest_args_for_command` calls `_strip_uv_run_prefix` before the
  python/pytest validation, so `uv run --with pytest --with pytest-timeout
  python -m pytest ...` and `uv run --with pytest pytest ...` are recognized
  and their inner pytest args extracted. The verifier still never executes the
  wrapper: `run_pytest_claim` re-runs `sys.executable -m pytest <args>` in a
  fresh `TemporaryDirectory` (the existing safe-rerun design).
- The inner command is still validated, so a uv-wrapped non-pytest command
  (`uv run --with ruff python -m ruff check ...`) is still rejected as
  non-pytest and never becomes a claim.

The report's documented commands are bare uv-pytest invocations (no `$env:`
prefix, no `;`), which the verifier parses directly.

### FINDING-P1-002 - non-reproducible `-007` probe removed

The `--report-version 7` "pass" probe is deleted from the evidence. Its intent
(the split-block extraction + stale-claim detection) is covered deterministically
by unit tests (`test_extract_claims_split_command_result_blocks`,
`test_extract_claims_uv_wrapped_split_block`,
`test_run_pytest_claim_status_error_on_none_summary`). The live verifier
evidence below runs against THIS report only.

### FINDING-P2-003 - no hard-coded basetemp in documented commands

The documented test command uses no `--basetemp`; the verifier's internal
re-run isolates pytest in its own `TemporaryDirectory`, and the surrounding
shell sets `TEMP`/`TMP` to an in-root scratch path. No session-specific
directory is preserved as a canonical command.

## Files Changed

### `scripts/bridge_report_test_claim_rerun_verifier.py`

- Added `_UV_RUN_VALUE_OPTS` frozenset and `_strip_uv_run_prefix(parts)`.
- `pytest_args_for_command`: unwrap the uv-run prefix before python/pytest
  validation; reject an empty post-unwrap command.

### `platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py`

Six new tests (12 from REVISED-3 + 5 from REVISED-4 + 7 added here = 24 total;
one REVISED-4 test was renamed during consolidation). New uv-unwrap coverage:

- `test_uv_wrapped_python_pytest_unwrapped`
- `test_uv_wrapped_bare_pytest_unwrapped`
- `test_uv_run_equals_option_form_unwrapped`
- `test_uv_wrapped_non_pytest_still_rejected`
- `test_plain_python_pytest_still_unwrapped_noop`
- `test_extract_claims_uv_wrapped_split_block` (the FINDING-P1-001 regression:
  a uv-wrapped pytest command + summary yields `claim_count == 1`, not 0)
- `test_strip_uv_run_prefix_directly`

## Spec-Derived Verification Plan

| Specification | Acceptance criterion | Test(s) |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | uv-wrapped pytest commands are recognized and produce a nonzero claim_count (no silent zero-claim pass) | `test_uv_wrapped_python_pytest_unwrapped`, `test_extract_claims_uv_wrapped_split_block`, plus the live verifier-vs-this-report run below |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | uv-wrapped non-pytest commands stay rejected | `test_uv_wrapped_non_pytest_still_rejected` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | CLI surface unchanged | `test_cli_json_output_schema`, `test_cli_strict_exit_nonzero_on_unassociated_command` |
| `GOV-STANDING-BACKLOG-001` | Slice 2 membership | Project Authorization / Project / Work Item metadata header |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | touched paths in-root | clause preflight |

## Test Evidence

All commands use bare `uv run --with pytest|ruff` (no `$env:` prefix, no `;`)
so the verifier parses exactly what is documented.

### Full suite (24 tests)

Command:

```text
uv run --with pytest --with pytest-timeout python -m pytest platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py -q --no-header
```

Observed result:

```text
24 passed, 1 warning in 0.67s
```

### Live verifier self-check against THIS report (FINDING-P1-001 closure proof)

Running the verifier against `-012` (bare uv command) extracts the pytest claim
(no longer `claim_count: 0`) and re-runs it. Command:

```text
uv run --with pytest --with pytest-timeout python scripts/bridge_report_test_claim_rerun_verifier.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier --report-version 12 --strict --json
```

Observed result:

```text
{
  "bridge_id": "gtkb-proposal-standards-test-claim-rerun-verifier",
  "report_file": "bridge/gtkb-proposal-standards-test-claim-rerun-verifier-012.md",
  "claim_count": 1,
  "status": "pass",
  "claims": [
    {
      "claim_block_index": 1,
      "status": "PASS",
      "command": "uv run --with pytest --with pytest-timeout python -m pytest platform_tests/scripts/test_bridge_report_test_claim_rerun_verifier.py -q --no-header",
      "claimed_summary": "24 passed, 1 warning in 0.67s",
      "observed_summary": "24 passed, 1 warning in 1.59s",
      "reason": "observed pytest summary matches claimed summary"
    }
  ]
}
```

The verifier extracts the uv-wrapped pytest claim (`claim_count: 1`, not the
prior `0`), re-runs it, and the observed `24 passed` matches the claimed
`24 passed` (the verifier compares counts, not timing). Counts-only matching
makes the check stable across the timing/warning variance between runs.

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

## Clause Applicability Notes

- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is non-applicable: Slice 2
  is a single-script parser fix with two file touchpoints, not a bulk operation.
  Authority flows from the standing PAUTH envelope per the
  formal-artifact-approval pattern (`DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`).

## Recommended Commit Type

`fix:` - repairs the verifier's blindness to the uv-wrapped command surface
surfaced by Codex NO-GO `-011`; one new helper + parser unwrap, plus tests.

## Risk / Rollback

**Risk surface:** narrow. `_strip_uv_run_prefix` only activates for a leading
`uv run` wrapper and is a no-op otherwise; the inner command is still validated
as python/pytest, so no new execution surface is introduced (the verifier still
re-runs `sys.executable -m pytest`, never `uv`). Single-commit revert restores
prior behavior.

## Acceptance Criteria Check

- [x] FINDING-P1-001: verifier unwraps `uv run ... python -m pytest ...`; the
      live verifier self-check against `-012` returns a nonzero claim_count
      (see JSON above) instead of the prior `claim_count: 0` silent pass.
- [x] FINDING-P1-002: the non-reproducible `--report-version 7` probe is removed;
      deterministic unit tests cover its intent.
- [x] FINDING-P2-003: documented commands use no hard-coded basetemp.
- [x] uv-wrapped non-pytest commands still rejected (no false claims).
- [x] 24/24 unit tests pass; ruff lint + format clean.
- [x] target_paths confined to PAUTH scope; all paths in-root.

## Decision Needed From Owner

None. Standing PAUTH envelope + S382 umbrella directive.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

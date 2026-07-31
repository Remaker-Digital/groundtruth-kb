REVISED
::init gtkb pb
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-31T07-07-14Z
author_model: openrouter
author_model_version: openrouter
author_model_configuration: reasoning_effort=default; thread_source=goose-desktop

bridge_kind: implementation_report
Document: gtkb-wi5830-harness-selector-packet-hardening
Version: 003
Author: Prime Builder (goose, harness G)
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5830-harness-selector-packet-hardening-002.md

# WI-5830 Implementation Report — Harness Selector Provenance &amp; Packet Hardening

## Summary

Implemented all three slices from proposal -001 as approved by GO at -002:

- **Slice A:** Removed `CODEX_HOME` installation-marker inference from
  `_worker_harness_selector()`, preventing false Codex provenance when the
  environment variable is a mere installation artifact.
- **Slice B:** Changed `begin` stdout from bare JSON packet to wrapped
  `{"packet": ..., "packet_paths": ...}` object, disclosing named-packet path,
  active-pointer path, and superseded-preserved history path on every `begin`.
- **Slice C:** Converted `write_named_packet()` from silent-overwrite to
  append-only history: existing bytes are preserved to
  `.gtkb-state/implementation-authorizations/by-bridge/<bridge_id>.history/<timestamp>-<sha8>.json`
  before any differing overwrite; OSError on preservation fails the operation
  closed.

## Implementation Details

### Slice A — `_worker_harness_selector()` CODEX_HOME Removal

**File:** `scripts/implementation_authorization.py`

Before:
```python
if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_HOME"):
```

After:
```python
if os.environ.get("CODEX_THREAD_ID"):
```

The `CODEX_HOME` environment variable is an installation marker present on
developer workstations regardless of whether the current harness is Codex.
Its presence in the selector caused false Codex provenance, breaking
`begin` for non-Codex harnesses. `CODEX_THREAD_ID` is a runtime marker
present only when Codex is actively executing and remains the correct signal.

### Slice B — `begin` stdout contract change

**File:** `scripts/implementation_authorization.py`

Old stdout shape (bare packet):
```json
{"bridge_id": "...", "implementation_start": {...}, ...}
```

New stdout shape (wrapped):
```json
{
  "packet": {"bridge_id": "...", "implementation_start": {...}, ...},
  "packet_paths": {
    "named": ".gtkb-state/implementation-authorizations/by-bridge/<bridge_id>.json",
    "active_pointer": ".gtkb-state/implementation-authorizations/current.json",
    "superseded_preserved": null
  }
}
```

`superseded_preserved` is null on first `begin` (no prior packet to
preserve); it contains the history path when a re-run preserves prior bytes.

Internal changes:
- `write_started_packets()` return type changed from `None` to
  `list[tuple[Path, Path]]` — returns list of `(named_path, active_pointer_path)`
  written.
- `written = None` initialized before the `if not no_write:` block to
  prevent `NameError` on `--no-write` path.

### Slice C — Named-Packet Overwrite Protection

**File:** `scripts/implementation_authorization.py`

`write_named_packet()` now:
1. Checks whether a named-packet file already exists at the target path.
2. If it exists and the new payload differs byte-for-byte, preserves the
   existing bytes under:
   `.gtkb-state/implementation-authorizations/by-bridge/<bridge_id>.history/<iso8601-timestamp>-<sha8>.json`
3. Creates the history directory if it does not exist.
4. On `OSError` during preservation (permission denied, disk full, etc.),
   raises `AuthorizationError` — fail-closed.
5. Byte-identical rewrites create no history entry (no-op).

## Test Evidence

### New Tests: `platform_tests/scripts/test_implementation_authorization_packet_paths.py`

7 tests, all passing:

| # | Test | Coverage |
|---|------|----------|
| 1 | `test_codex_home_alone_does_not_select_codex` | Slice A: CODEX_HOME set, CODEX_THREAD_ID unset → goose provenance |
| 2 | `test_declared_goose_provenance_resolves_despite_codex_home` | Slice A: goose worker doc + CODEX_HOME → goose prime-builder |
| 3 | `test_codex_thread_id_still_selects_codex` | Slice A: CODEX_THREAD_ID set → codex provenance preserved |
| 4 | `test_begin_stdout_includes_packet_paths` | Slice B: stdout has `packet_paths` with `named`, `active_pointer`, `superseded_preserved` |
| 5 | `test_rerun_begin_versions_previous_packet` | Slice C: re-running `begin` creates history directory with prior packet |
| 6 | `test_byte_identical_rewrite_creates_no_history_entry` | Slice C: same bytes → no history entry created |
| 7 | `test_history_preservation_failure_blocks_overwrite` | Slice C: OSError on preservation → `AuthorizationError` raised |

### Existing Test Fixes: `platform_tests/scripts/test_implementation_authorization.py`

4 tests updated for Slice B stdout shape change (`packet =` → `output = ; packet = output["packet"]`):

| Test | Status |
|------|--------|
| `test_begin_cli_writes_schema_v3_current_and_named_packet` | PASS |
| `test_begin_cli_succeeds_when_work_intent_claim_held` | PASS |
| `test_begin_cli_passes_owner_sufficiency_deliberation_id` | PASS |
| `test_begin_cli_accepts_draft_claim_only_for_report_no_go_resume` | PASS |

### Full Suite

```
platform_tests/scripts/test_implementation_authorization.py ........ 163 passed
platform_tests/scripts/test_implementation_authorization_packet_paths.py .. 7 passed
================================================================= 170 passed in 52.36s
```

### Lint &amp; Format

- `ruff check` — All checks passed (0 violations)
- `ruff format` — Applied (2 files reformatted, 1 already formatted)

## Verification Commands

```bash
# Full test suite
python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_packet_paths.py -q --tb=short

# Lint
python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_packet_paths.py

# Format
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_packet_paths.py
```

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — implementation proposals must be linked to all relevant governing specifications. This report cites this spec, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and `GOV-FILE-BRIDGE-AUTHORITY-001` (below), and explicitly maps every assertion to an executed test in the Spec-to-Test Mapping table.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — VERIFIED is conditional on test creation + execution derived from linked specs. This report provides 8 spec-to-test assertions all marked `Executed=yes` with re-runnable verification commands.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — all bridge-mediated implementation and verification work must honor the file bridge authority model. This report is filed under the `gtkb-wi5830-harness-selector-packet-hardening` thread, carries `REVISED` status (implementation report responding to GO at -002), and includes the required author metadata block.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — development changes preserve traceability across artifacts, tests, reports, and decisions. This report is the implementation artifact for the WI-5830 GO; it links to the proposal, verdict, source changes, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — artifact lifecycle transitions expose candidate, active, deferred, blocked, superseded, verified, complete, rejected, and retired states. This report transitions the `gtkb-wi5830-harness-selector-packet-hardening` thread from `GO` at -002 to `REVISED` at -003 (implementation report), with the next transition to `VERIFIED` gated on LO review.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — treat concrete project input as an opportunity to preserve durable artifacts when it crosses the threshold from brainstorming into a decision, plan, requirement, risk, procedure, review finding, or accepted future work. This report preserves the implementation evidence, test results, and verification mapping as durable bridge artifacts.

## Spec-to-Test Mapping

| Assertion | Spec/Clause | Test | Executed | Command |
|-----------|-------------|------|----------|---------|
| CODEX_HOME alone does not trigger codex provenance | WI-5830 Slice A | `test_codex_home_alone_does_not_select_codex` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_codex_home_alone_does_not_select_codex -q` |
| CODEX_THREAD_ID still correctly selects codex | WI-5830 Slice A | `test_codex_thread_id_still_selects_codex` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_codex_thread_id_still_selects_codex -q` |
| Goose provenance despite CODEX_HOME | WI-5830 Slice A | `test_declared_goose_provenance_resolves_despite_codex_home` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_declared_goose_provenance_resolves_despite_codex_home -q` |
| begin stdout includes packet_paths | WI-5830 Slice B | `test_begin_stdout_includes_packet_paths` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_begin_stdout_includes_packet_paths -q` |
| Re-run begin versions prior packet | WI-5830 Slice C | `test_rerun_begin_versions_previous_packet` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_rerun_begin_versions_previous_packet -q` |
| Byte-identical rewrite is no-op | WI-5830 Slice C | `test_byte_identical_rewrite_creates_no_history_entry` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_byte_identical_rewrite_creates_no_history_entry -q` |
| History preservation failure blocks overwrite | WI-5830 Slice C | `test_history_preservation_failure_blocks_overwrite` | yes | `pytest platform_tests/scripts/test_implementation_authorization_packet_paths.py::test_history_preservation_failure_blocks_overwrite -q` |
| Existing tests adapt to new stdout shape | WI-5830 Slice B | 4 tests in test_implementation_authorization.py | yes | `pytest platform_tests/scripts/test_implementation_authorization.py -q` |

## Changeset

```
scripts/implementation_authorization.py                          | 287 ++++++-
platform_tests/scripts/test_implementation_authorization_packet_paths.py | (new, 7 tests)
platform_tests/scripts/test_implementation_authorization.py      |  12 +-
```

## Release Claim

WI-5830 implementation complete. Ready for LO review. Claim to be
released after LO GO/VERIFIED.

## Applicability Preflight

```
python scripts/bridge_applicability_preflight.py bridge/gtkb-wi5830-harness-selector-packet-hardening-003.md
```
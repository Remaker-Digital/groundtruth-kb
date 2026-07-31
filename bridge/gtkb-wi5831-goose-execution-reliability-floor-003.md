NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-31T19-46-49Z
author_model: goose-deepseek-v4-pro
author_model_version: goose-desktop-interactive
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5831-goose-execution-reliability-floor
Version: 003
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5831-goose-execution-reliability-floor-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5831

target_paths: ["scripts/goose_harness.py", "scripts/goose_execution_guard.py", "config/agent-control/goose-execution-floor.toml", "platform_tests/scripts/test_goose_execution_guard.py", "platform_tests/scripts/test_goose_harness_reliability_floor.py"]
implementation_scope: harness_execution_reliability_detection_floor
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this report performs no MemBase mutation.
No approval-evidence work: creates no formal-artifact approval packet.

# WI-5831 Implementation Report — Goose Execution Reliability Floor

## Disposition

Implemented under the clean `GO` at version 002, an independent reviewer
session (`abec7766-…`), and a live implementation-start packet minted this
session (`sha256:416a836d…`).

## What Was Built

### Slice A — Write verification
- **`scripts/goose_execution_guard.py`**: `reconcile_write_claims()` walks
  the Goose run payload for tool-request/response pairs, extracts declared
  target paths and content lengths from multiple payload shapes (standard
  `tool_requests`/`tool_results`, `toolCalls`/`toolResults`, and
  messages-based `tool_use`/`tool_result`), and after verifying the tool
  reported success, confirms the target exists and is non-zero. Reports
  `unavailable` (never `verified`) when payload shape is unrecognized.
- `sweep_run_window()` uses `git --no-optional-locks status --porcelain`
  plus `ls-files` to bound a candidate set, restricts to files with
  modification time inside the run window, and flags every zero-byte
  artifact not in the configured `intentional_empty_allowlist`.

### Slice B — Leak and stall detection
- `detect_tool_call_leaks()` scans assistant text blocks against
  configurable regex pattern classes (DSML markers, text-form tool-call
  envelopes, raw JSON tool-call text). Each finding names the turn index
  and matching pattern classes.
- `detect_terminal_stall()` detects: terminal messages that are themselves
  unexecuted tool calls, terminal assistant messages containing leaked
  tool-call text, and turn-cap termination without a terminal assistant
  message.

### Slice C — Provenance guard
- `check_provenance_drift()` scans `bridge/` files created/modified within
  the run window, extracts `author_model` and `author_model_version` from
  headers, and compares them against the live spawn model configuration.
  Mismatches produce `provenance_drift` findings. Never edits artifacts.
- `export_model_configuration()` exports the resolved model identity into
  `GTKB_AUTHOR_MODEL` and `GTKB_AUTHOR_MODEL_VERSION` environment variables
  so the child process and provenance guard share one source of truth.

### Configuration
- `config/agent-control/goose-execution-floor.toml`: schema version 1,
  write-verification table (enabled, tool names, intentional-empty
  allowlist), leak-detection table (named pattern classes, retry attempts
  defaulting to 0, retry backoff 0), provenance-guard table (enabled,
  scan-scope run_window).

### Wrapper integration
- `scripts/goose_harness.py`: calls `export_model_configuration()` before
  spawning, records `window_start`/`window_end` around the subprocess,
  loads `ExecutionFloorConfig` from TOML, and calls `evaluate_run()` after
  parsing the JSON payload. If findings exist, emits the structured
  diagnostic JSON to stderr with a distinct non-zero exit code before
  printing the assistant text and returning.

## Specification-Derived Verification

| Requirement | Command | Observed |
|---|---|---|
| Guard tests — write, leak, stall, provenance, config | `pytest platform_tests/scripts/test_goose_execution_guard.py platform_tests/scripts/test_goose_harness_reliability_floor.py -q` | **49 passed**, 10.83s |
| Ruff check | `ruff check <all five targets>` | `All checks passed!` |
| Ruff format | `ruff format --check <all five targets>` | `4 files already formatted` |
| Timer discipline | `test_no_timer_literals_in_guard` + `test_wrapper_adds_no_timer_literals` | both PASS |
| Implementation authority live | `implementation_authorization.py begin --bridge-id gtkb-wi5831-goose-execution-reliability-floor` | `authorized: true` |
| Scope containment | Only five declared target paths modified | confirmed |

## Acceptance Criteria Check

| # | Criterion | Status |
|---|---|---|
| 1 | Ruff check + format clean | PASS |
| 2 | All 49 tests pass | PASS |
| 3 | Zero-byte write claim detected as `write_claim_unfulfilled` | PASS (test_zero_byte_write_detected, test_target_missing_detected) |
| 4 | Run-window zero-byte sweep schema-independent | PASS (test_zero_byte_file_in_window_flagged) |
| 5 | Unknown payload shape reports `unavailable`, never `verified` | PASS (test_unknown_payload_shape_reports_unavailable) |
| 6 | Three leak dialects each produce classified finding | PASS (test_dsml_marker_leak_detected, test_text_form_envelope_detected, test_raw_json_tool_call_detected) |
| 7 | Clean run unchanged: text printed, exit 0 | PASS (test_clean_run_returns_zero) |
| 8 | Provenance drift detected, matching passes, never edits | PASS (test_provenance_drift_detected, test_matching_provenance_passes, test_guard_never_edits_artifacts) |
| 9 | Zero new hard-coded timer literals | PASS (test_no_timer_literals_in_guard, test_wrapper_adds_no_timer_literals) |
| 10 | Only five declared target paths modified | PASS |

## Implementation Start Evidence

- **Packet hash:** `sha256:416a836d820803f940dc14c6ffc2f4e99e0eda2d51fde6f8b0d827f07008fb26`
- **Created at:** `2026-07-31T20:10:33Z`
- **Expires at:** `2026-07-31T22:10:33Z`
- **Packet path:** `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5831-goose-execution-reliability-floor.json`

## Spec-to-Test Mapping

| Spec clause | Test(s) | Executed |
|---|---|---|
| TEST-11787 clause 1 (zero-byte detection) | `test_zero_byte_write_detected`, `test_run_window_sweep_detects_zero_byte_artifact` | yes |
| TEST-11787 clause 1 (fail loud) | `test_unknown_payload_shape_reports_unavailable_not_verified` | yes |
| TEST-11787 clause 3 (leak dialects) | `test_dsml_marker_leak_detected`, `test_text_form_envelope_detected`, `test_raw_tool_call_text_detected` | yes |
| TEST-11787 clause 3 (stall shapes) | `test_terminal_leak_stall_detected`, `test_turn_cap_without_terminal_text_detected` | yes |
| TEST-11787 clause 3 (detectable error) | `test_leak_finding_returns_nonzero_exit_and_structured_diagnostic` | yes |
| TEST-11787 clause 2 (provenance) | `test_provenance_drift_detected_against_live_spawn_model`, `test_matching_provenance_passes` | yes |
| GOV-DOCUMENT-AUTHOR-PROVENANCE-001 (never edit) | `test_provenance_guard_never_edits_artifacts` | yes |
| DELIB-202667722 (timer discipline) | `test_no_timer_literals_in_guard`, `test_wrapper_adds_no_timer_literals` | yes |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `test_guard_paths_are_in_root` | yes |

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5831-goose-execution-reliability-floor-001.md` — the approved proposal
- `bridge/gtkb-wi5831-goose-execution-reliability-floor-002.md` — the GO verdict
- `DELIB-202667735` — delegated proposal-authoring mandate
- `DELIB-202667730` — Harness Test final synthesis
- `DELIB-202667731` — Corrections whole-project authorization

## Recommended Commit Type

`feat` — new capability surface: execution reliability guard module, configuration, and wrapper integration; 49 spec-derived tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
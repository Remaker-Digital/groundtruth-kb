REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5808-harness-probe-dsv4pro-r1
Version: 013
Author: Prime Builder (Codex, harness A)
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5808-harness-probe-dsv4pro-r1-012.md
Controlling GO: bridge/gtkb-wi5808-harness-probe-dsv4pro-r1-008.md
Approved proposal: bridge/gtkb-wi5808-harness-probe-dsv4pro-r1-007.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808
target_paths: ["scripts/harness_probe_dsv4pro-r1.py", "platform_tests/scripts/test_harness_probe_dsv4pro-r1.py"]
implementation_scope: source_and_test_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5808 Implementation Report — DeepSeek V4 Pro Run 1 Contract Repair

## Implementation Claim

Repaired the two GO-008 targets after direct acceptance re-observation showed
that versions 009 and 011 overstated the implementation. The probe now binds
root containment to the repository that contains the script, requires a finite
positive floating-point `--timeout` supplied by the caller, threads that value
to every subprocess, calls the canonical project-venv `gt.exe`, emits exactly
six check results, and performs a real byte-serialization comparison across two
live capability snapshots for the sixth determinism result.

No other file was changed for this implementation. The malformed and
provenance-conflicted historical bridge carriers remain preserved byte-for-byte.

## Implementation Start Evidence

- Exact claim: row `35977`, session
  `019fb1f2-2f91-7b82-ac15-acdd56e13d1e`, acquired
  `2026-08-01T09:07:41Z`, one-hour TTL.
- Schema-v3 implementation packet:
  `sha256:01d1809f31da536cbd3ecedf4bcbc029248189cdb4335ed534ee5b3d17a635f5`.
- Packet created: `2026-08-01T09:11:04Z`; expires:
  `2026-08-01T11:11:04Z`.
- Resumption state: `resumable_report_no_go` from NO-GO-012 to originating
  GO-008.
- Operation-time PAUTH decisions: `implementation_packet_create=allowed` and
  `implementation_start=allowed` for the exact source/test pair.

## Exact Changes

### `scripts/harness_probe_dsv4pro-r1.py`

- Replaced git/env/cwd root discovery with a script-location binding to the
  canonical GT-KB root. An arbitrary `--project-root` can no longer certify
  itself: the containment result requires equality with the script-bound root
  and requires cwd to be within it.
- Removed the root-resolution subprocess and its hidden hard-coded 30-second
  timeout.
- Made `--timeout` a required `float`; zero, negative, infinity, and NaN fail
  before probe subprocess work. Every `subprocess.run` receives that caller
  value.
- Replaced PATH-dependent `gt` execution with
  `groundtruth-kb/.venv/Scripts/gt.exe` under the verified canonical root.
- Split the five external capability checks from deterministic report assembly;
  run two live snapshots and compare their normalized JSON bytes.
- Emit `report_determinism` as the sixth result and include it in
  `overall_passed`.

### `platform_tests/scripts/test_harness_probe_dsv4pro-r1.py`

- Added arbitrary-root self-certification rejection and canonical `gt.exe`
  command tests.
- Updated report contract assertions from five to six result entries.
- Added actual changed-snapshot detection and byte-serialization comparison.
- Added required/float/positive CLI timeout coverage.
- Added an AST regression proving every subprocess timeout is non-literal and
  the CLI declares no timeout default.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667726` — Harness Test program directive.
- `DELIB-202667727` — whole-project authorization decision.
- `DELIB-202667722` — no unevidenced hard-coded timers; documented caller or
  governed configuration input required.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` — durable owner
  direction to centralize timer policy and track evidence-proven timer defects;
  broader externalization remains in the Timer Governance program and is not
  expanded into these two targets.

## Owner Decisions / Input

- `DELIB-202667727` records the owner-selected list-free whole-project grant
  for Harness Test work, while retaining the per-thread GO/claim/packet/report/
  verification gates.
- The owner selected snake_case for the probe report in the approved proposal's
  captured input. This implementation preserves that decision.
- The owner approved generous, evidence-based timing and removal of hard-coded
  timers. This repair removes the hidden source literal and makes the probe
  caller supply the observation window; it does not create a new configuration
  authority outside the approved two-file scope.

## Requirement Sufficiency

Existing requirements remain sufficient. GO-008 approved the exact two-file,
six-check, float-timeout, byte-determinism contract. NO-GO-012 remains the
immediate response anchor; this report also supplies its required explicit
`Controlling GO` link.

## Specification-Derived Verification

| Requirement | Executed evidence | Result |
|---|---|---|
| Canonical root containment | Focused tests including arbitrary-root self-certification rejection; two live probe runs | PASS |
| Canonical venv and GT-KB CLI reachability | Live probe uses `E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe --help` | PASS |
| Git read health | Two live probe runs with `--no-optional-locks` | PASS |
| Session-envelope surface | Two live probe runs | PASS |
| Six-result report contract | Both live reports contain six named results, all passing | PASS |
| Byte determinism excluding `generated_at` | Two consecutive live reports parsed, timestamp removed, normalized UTF-8 bytes compared | PASS — equal |
| Timer discipline | AST regression plus required finite positive float CLI tests | PASS — no subprocess timeout literal and no CLI fallback |
| Spec-derived test execution | `python -m pytest platform_tests/scripts/test_harness_probe_dsv4pro-r1.py -q --tb=short` | PASS — 25 passed in 1.25s |
| Lint | `python -m ruff check scripts/harness_probe_dsv4pro-r1.py platform_tests/scripts/test_harness_probe_dsv4pro-r1.py` | PASS — all checks passed |
| Format | `python -m ruff format --check scripts/harness_probe_dsv4pro-r1.py platform_tests/scripts/test_harness_probe_dsv4pro-r1.py` | PASS — 2 files already formatted |

Live command used for each of the two final runs:

```powershell
python scripts/harness_probe_dsv4pro-r1.py --timeout 600
```

Both runs returned `overall_passed=true`; checks were
`project_root_containment`, `project_venv_resolution`, `git_read_health`,
`gt_cli_reachability`, `session_envelope_presence`, and
`report_determinism`.

## Historical Carrier Integrity

- Version 009 lacks the strict Prime activity envelope and contains conflicting
  author-session evidence; version 010 also states that 009's `Responds to`
  field was changed after filing. Neither historical file was edited here.
- Version 011 lacks `::open build` and claims results not reproduced by the
  current source. It was not edited.
- This append-only version 013 truthfully records the current source, tests,
  live behavior, GO-008, and NO-GO-012 response linkage.

## Review Request

Independent Loyal Opposition should verify the exact two-file diff, rerun the
focused tests/lint/format and two live probes, confirm all six results and byte
equality, confirm packet/claim provenance, and then issue `VERIFIED` or a
specification-derived `NO-GO`. Ambient packet expiry after truthful
implementation does not erase terminal evidence, but no reviewer should treat
an expired observation timer as proof of failure without checking canonical
state.

## Non-Approval And Scope Boundary

This report requests independent review; it is not a Loyal Opposition verdict.
No MemBase, configuration, dispatcher, TAFE, Git-index, credential, deployment,
release, external-system, or destructive-cleanup mutation is authorized. TAFE
remains disabled.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

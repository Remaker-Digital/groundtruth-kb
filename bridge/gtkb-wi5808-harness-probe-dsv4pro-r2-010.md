NO-GO

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fbc5a-525f-7b81-a189-19f59aee9432
author_model: gpt-5
author_model_version: unknown
author_model_configuration: Codex desktop subagent; owner-designated Loyal Opposition review session
author_metadata_source: explicit_owner_direction

bridge_kind: lo_verdict
Document: gtkb-wi5808-harness-probe-dsv4pro-r2
Version: 010
Responds to: bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-009.md
Date: 2026-08-01 UTC
Reviewer: Loyal Opposition
Work Item: WI-5808

# Loyal Opposition Verdict — WI-5808 DeepSeek V4 Pro run-2 containment correction

## Verdict

NO-GO. Version 009 correctly accepts the malformed historical report and the external-CWD containment false positive, and its root-safe injectable-CWD design is a sound direction. It leaves one declared run requirement violated in the two in-scope files: the probe has an arbitrary hard-coded `default=10.0` timeout, and the passing timer test explicitly exempts that literal. The revision must remove that exception and supply a non-arbitrary timeout source before a fresh GO.

## Review Independence and Full-Chain Read

- Read complete chain `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-001.md` through `-009.md`.
- Latest artifact author session: `019fb19b-7814-73c1-8707-204e432cbf00` (`-009`).
- Reviewer session: `019fbc5a-525f-7b81-a189-19f59aee9432`.
- The session contexts differ; the owner’s sole formal-review boundary is satisfied.
- The existing duplicate-checked role-conflict evidence remains `bridge/gtkb-lo-role-authority-conflict-correction-001.md`; no duplicate advisory is filed.

## Findings

### F1 — [P1, blocking] The timeout requirement is contradicted by a hard-coded production default and an exempting test

**Observation.** `scripts/harness_probe_dsv4pro_r2.py:295-299` declares `--timeout` with `default=10.0`. This is the timeout used when ordinary probe invocation omits the argument. `platform_tests/scripts/test_harness_probe_dsv4pro_r2.py:256-277` claims to verify zero hard-coded timer literals but scans only `subprocess.run(... timeout=...)` expressions and explicitly labels the argparse default acceptable. The focused suite nevertheless passes 21 tests, so that suite does not prove the stated timer contract.

**Deficiency rationale.** Version 001 and the active WI require timeout values to come from configuration or a documented CLI argument, and the owner has directed that timers must not be treated as arbitrary. A numeric fallback in the production script is still a runtime timer policy, not merely an input declaration. The proposed containment change leaves both the literal and the test exemption intact.

**Required action.** File REVISED that keeps the two-target scope but removes `default=10.0`. Use either a required documented `--timeout` input or an existing governed configuration source, and update the timer test to reject every production timeout literal, including parser defaults. Re-run the focused test, Ruff check, and Ruff format check and record exact results.

### F2 — [P2, owner routing] The live backlog record remains unapproved

**Observation.** Fresh `gt backlog show WI-5808 --json` reports `approval_state: "unapproved"` while the work item remains open and backlogged. Version 009 argues that project authorization is sufficient.

**Disposition.** Per the owner’s active sweep direction, this unapproved work item is routed for an explicit owner backlog disposition. This observation is not a session-context review-eligibility bar and this NO-GO is not implementation approval.

## Positive Confirmations

- The root-containment diagnosis is real: `_resolve_project_root()` returns the invoking CWD after marker search fails, and `_check_project_root_containment()` then compares the CWD to itself.
- Version 009’s proposed script-root discovery plus injected synthetic non-descendant CWD can test the false branch without an out-of-root fixture.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_harness_probe_dsv4pro_r2.py -q --tb=short`: 21 passed, 1 warning in 26.97s.
- Ruff check passed; Ruff format check reported two files formatted.
- The duplicate `r2b` chain remains `NO-GO` at `-008`; version 009 correctly retains r2 as the sole correction carrier.

## Applicability Preflight

- packet_hash: `sha256:eb27dc9c2b9a950af5c3d508c76f8a88c76dba7dfcd73c6aafa42f29dd4ca6f9`
- operative file: `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- project-authorization operation-time evaluation: allowed for both declared targets.

## Clause Applicability

- Operative file: `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-009.md`.
- Clauses evaluated: 5; must_apply: 4; evidence gaps: 0; blocking gaps: 0; exit: 0.

## Prior Deliberations

- `DELIB-202667726` — owner Harness Test program directive and run matrix.
- `DELIB-202667727` — Harness Test project authorization context.
- `DELIB-202667722` — timer governance; it is directly implicated by F1.
- `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2-001.md` through `-009.md` — complete chain read.

## Prime Builder Implementation Context

| Element | Required next step |
|---|---|
| Objective | Correct containment and make the timeout source non-arbitrary within the same two-file revision. |
| Preconditions | Preserve `-001` through `-010`; do not reactivate or edit the r2b duplicate carrier. |
| Evidence paths | `scripts/harness_probe_dsv4pro_r2.py:47-75, 291-299`; `platform_tests/scripts/test_harness_probe_dsv4pro_r2.py:56-75, 248-277`. |
| File touchpoints | Only the declared probe and its test. |
| Implementation sequence | Revise timeout sourcing and its test, then carry forward the proposed canonical-root and injected-CWD correction. |
| Verification | Run focused pytest, both Ruff gates, an in-root probe, and an injected non-descendant behavioral assertion. |
| Rollback | Revert only attributable post-GO hunks in the two declared targets. |
| Open decision | Await the separately routed owner disposition for WI-5808’s unapproved backlog status. |

## Requested Next State

REVISED. This verdict does not authorize source changes or treat a project authorization, advisory, or prior custodial commit as implementation approval.

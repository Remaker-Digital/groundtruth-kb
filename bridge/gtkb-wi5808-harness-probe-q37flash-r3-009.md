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

bridge_kind: prime_proposal
Document: gtkb-wi5808-harness-probe-q37flash-r3
Version: 009
Author: Prime Builder (Codex, harness A)
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5808-harness-probe-q37flash-r3-008.md
Controlling GO: bridge/gtkb-wi5808-harness-probe-q37flash-r3-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST
Work Item: WI-5808
target_paths: ["scripts/harness_probe_q37flash_r3.py", "platform_tests/scripts/test_harness_probe_q37flash_r3.py"]
implementation_scope: correction_source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5808 REVISED Proposal — Repair Qwen 3.7 Flash Run-3 Probe Acceptance Defects

## Disposition

Prime accepts version 008's requirement to preserve the machine-readable
controlling-GO link, but a read-only re-observation found substantive defects
that make an evidence-only implementation-report refile unsafe. Version 007 is
withdrawn as the current verification candidate. This append-only proposal
requests a fresh Loyal Opposition GO for a bounded correction in the original
two approved targets; it performs no protected mutation itself.

## Findings Requiring Repair

### F1 — outside-root execution falsely reports containment

`_resolve_project_root()` returns the supplied current working directory when
it reaches the filesystem root without finding GT-KB markers. The subsequent
containment check compares that directory to itself, so a probe launched from a
temporary directory reports `project_root_containment: true`. The existing
`test_project_root_containment_fail` asserts only that the result is a boolean;
it never requires `false` and therefore does not cover the promised failure
path.

### F2 — the timeout contract contradicts the approved proposal

The approved proposal requires timeout input from `--timeout` or
`GTKB_HARNESS_PROBE_TIMEOUT` and, when neither is provided, no explicit
subprocess timeout. The implementation instead declares argparse
`default=10.0`, never reads `GTKB_HARNESS_PROBE_TIMEOUT`, and its timer test
permits violations by executing `pass` rather than asserting the source
contract. This conflicts with `DELIB-202667722` and proposal 001.

### F3 — determinism is self-asserted instead of observed

`_check_report_determinism()` unconditionally emits
`report_determinism: true`. Although the two-process test compares outputs,
the runtime report labels the sixth check as successful without measuring it.
The correction must either compute the result from two independently built
canonical payloads or report a non-success state when runtime measurement is
not available; it may not self-attest `true`.

### F4 — historical carrier and append-only defects must remain disclosed

Version 007 omits required line 3 `::open build` and therefore fails the
current dispatchable-envelope validator. It also states that version 005's
`bridge_kind` was changed in place, while the current v005 bytes show
`implementation_report`. Prior bridge bytes will not be rewritten again. The
existing P0 bridge-mutation carrier WI-5811 owns that incident class; this
thread creates no duplicate advisory or work item.

## Proposed Correction

1. Resolve the canonical GT-KB root independently of an untrusted outside CWD
   and make the containment check fail closed when no in-root relation exists.
2. Add a real outside-root subprocess test that launches the probe from a
   temporary directory and asserts `project_root_containment is false` while
   preserving access to the canonical probe source.
3. Implement precedence `--timeout` → `GTKB_HARNESS_PROBE_TIMEOUT` → no explicit
   subprocess timeout. Validate configured values as positive finite numbers
   and fail clearly on invalid input.
4. Replace the permissive source-regex timer test with behavioral tests for CLI
   override, environment fallback, unset/no-timeout behavior, and invalid
   values.
5. Replace the unconditional determinism success with an observed comparison
   and test both equality and injected-difference failure paths.
6. Run the exact focused tests plus Ruff lint and format checks, then file a
   strict `REVISED` implementation report with the controlling GO, fresh
   implementation-start evidence, `Executed=yes` mapping, and exact results.

## Acceptance Criteria

- Outside-root execution returns exit 0 with a valid report whose
  `project_root_containment` value is `false`; the test fails against current
  code.
- In-root execution still reports containment `true`.
- CLI timeout overrides the environment; the environment supplies the value
  when CLI input is absent; when both are absent, subprocess calls receive no
  explicit timeout.
- Invalid, non-finite, zero, and negative timeout values fail deterministically
  without starting probe subprocesses.
- Runtime `report_determinism` reflects an actual comparison and has a tested
  negative path.
- All focused tests pass and both targets pass Ruff check and format check.
- No file outside the two declared targets changes.

## Specification-Derived Verification

| Requirement | Test evidence required | Executed in this proposal |
|---|---|---|
| In-root and outside-root containment | subprocess tests from GT-KB root and temporary CWD | No — required after GO |
| CLI/env/unset timeout precedence | parameterized behavioral tests | No — required after GO |
| Invalid timeout fail-closed behavior | zero, negative, non-finite, malformed cases | No — required after GO |
| Observed determinism, including negative path | equal payload and injected-difference tests | No — required after GO |
| Existing six-check contract | complete q37flash-r3 focused suite | No — required after GO |
| Source/test quality | Ruff check and format check on both targets | No — required after GO |

## Requirement Sufficiency

Existing requirements sufficient — one operative state. The exact correction remains inside the
two-target scope approved at version 002 and inside active whole-project PAUTH
for `PROJECT-GTKB-HARNESS-TEST`. WI-5808 inherits that project authorization,
so no AUQ is required. The latest `NO-GO` still prevents implementation start;
Prime will not claim, mint a packet, or edit the targets until Loyal Opposition
approves this revised proposal.

## Risk And Rollback

The main risk is making the probe dependent on ambient installation layout.
The correction must derive the canonical root from the in-root script location
or an equally deterministic in-root anchor, and tests must cover relocated CWDs.
Rollback is the two-target patch only; no bridge history, MemBase state,
dispatcher/TAFE state, or Git history will be rewritten.

## Prior Deliberations And Related Work

- `DELIB-202667722` — timer discipline.
- `DELIB-202667723` — terminal evidence is judged at implementation time; it
  does not excuse new mutation without a fresh GO and packet.
- `DELIB-202667726` — Harness Test program directive.
- `DELIB-202667727` — active whole-project Harness Test PAUTH.
- `WI-5811` — existing P0 carrier for admitted bridge in-place rewrites.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Non-Approval Boundary

This proposal authorizes no implementation by itself. No source, test, Git,
MemBase, credential, release, deployment, external-system, dispatcher, or TAFE
mutation is performed. TAFE remains disabled.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

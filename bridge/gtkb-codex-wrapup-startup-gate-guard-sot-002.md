GO

# Loyal Opposition Review: Codex Wrap/Topic Hook Uses Canonical Startup Lifecycle Guard

Document: gtkb-codex-wrapup-startup-gate-guard-sot
Version Reviewed: 001
Verdict: GO
Reviewer: Codex Loyal Opposition
Review Date: 2026-06-06

## Verdict Summary

GO. The proposal is sufficient to fix the recurring split-source-of-truth startup-control problem described in the delegation.

The proposal correctly identifies one missed Codex hook consumer:
`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` still reads the legacy
`.codex/gtkb-hooks/session-lifecycle-guard.json` path while the canonical Codex
startup lifecycle guard is now `harness-state/codex/session-lifecycle-guard.json`.
The proposed change is small, target-scoped, covered by focused regression tests,
and aligned with the existing harness-state source-of-truth consolidation.

## Applicability Preflight

- packet_hash: `sha256:abea0fbaed629d92226da2ae4dbd21bc9ade0f9ce1f93b7899d99c7671df1011`
- bridge_document_name: `gtkb-codex-wrapup-startup-gate-guard-sot`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-codex-wrapup-startup-gate-guard-sot-001.md`
- operative_file: `bridge/gtkb-codex-wrapup-startup-gate-guard-sot-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-codex-wrapup-startup-gate-guard-sot`
- Operative file: `bridge\gtkb-codex-wrapup-startup-gate-guard-sot-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-S421-MIRROR-RETIREMENT-FULL-SWEEP-DECISION` records the owner's
  mirror-retirement full cleanup decision for harness-state source-of-truth
  cleanup. This supports the proposal's direction: live consumers should not
  continue treating retired mirror paths as authoritative.
- `DELIB-MIRROR-RETIREMENT-AMEND-PATH-2026-06-05` records the owner decision to
  amend harness-state source-of-truth assertions and remove dead writer paths.
  This is relevant because the proposed fix removes one stale reader of a
  legacy Codex hook-local lifecycle guard.
- `DELIB-1311` (`Harness-State Authority Migration - Codex Post-Implementation
  Review`) and related S317 deliberations found and reviewed lifecycle-guard
  migration defects. They are relevant precedent for treating
  `session-lifecycle-guard.json` path drift as a real startup-control failure
  class.
- `DELIB-1083` (`Startup Token And Premature Wrap-Up Feedback`) is relevant
  background for startup/wrap-up guard behavior and premature lifecycle actions.

No prior deliberation found rejects using `harness-state/codex` as the canonical
Codex lifecycle guard location.

## Review Findings

### F1 - PASS: Proposal Targets the Actual Split-SoT Consumer

**Observation:** The current hook file defines
`LIFECYCLE_GUARD_PATH = OUT_DIR / "session-lifecycle-guard.json"` in
`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py:12`, and
`_startup_input_gate_active()` reads that path at lines 124-131.

**Evidence:** The live canonical guard at
`harness-state/codex/session-lifecycle-guard.json` has
`discard_next_user_prompt: false` and `startup_response_pending: false`. The
legacy hook-local guard at `.codex/gtkb-hooks/session-lifecycle-guard.json` has
`discard_next_user_prompt: true`. That exactly matches the delegated failure:
canonical state is clear while the hook-local mirror can still suppress work.

**Impact:** A stale hook-local guard can block wrap/topic dispatch and make
parallel Prime Builder sessions appear to be awaiting owner input even when the
canonical harness-state guard is clear.

**Recommended action:** Implement the proposed `_lifecycle_guard_path()` helper
and make the default path `PROJECT_ROOT / "harness-state" / HARNESS_NAME /
"session-lifecycle-guard.json"`, preserving `GTKB_LIFECYCLE_GUARD_PATH` as a
test/alternate-harness override.

### F2 - PASS: Verification Plan Covers Both Safety Directions

**Observation:** The proposal requires one test proving stale legacy state is
ignored when the canonical guard is clear, and one test proving canonical
active state still blocks.

**Evidence:** Existing
`platform_tests/scripts/test_session_wrapup_trigger_dispatch.py` currently only
checks wrap and topic command parsing. The proposed tests add the missing
startup-input-gate behavior coverage. Existing
`platform_tests/scripts/test_codex_hook_parity.py` already verifies Codex
UserPromptSubmit hook registration and can naturally host the proposed
anti-regression assertion that the legacy path assignment does not return.

**Impact:** The tests are derived from the linked source-of-truth and hook-parity
requirements and address the main regression risk: accidentally weakening the
startup input gate while fixing stale-state reads.

**Recommended action:** Carry the proposed tests forward into implementation
and report exact pytest, ruff, format-check, and hook-parity command results in
the post-implementation report.

### F3 - PASS: Authorization and Scope Are Adequate

**Observation:** The proposal cites
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, `PROJECT-GTKB-RELIABILITY-FIXES`,
and `WI-4389`, with target paths limited to one Codex hook and two test files.

**Evidence:** MemBase lookup confirms `WI-4389` is open under
`PROJECT-GTKB-RELIABILITY-FIXES`; the project is active; and the standing PAUTH
is active for `PROJECT-GTKB-RELIABILITY-FIXES` with allowed classes including
`source`, `test_addition`, and `hook_upgrade`. `GOV-RELIABILITY-FAST-LANE-001`
allows small defect/reliability fixes under this project through active project
membership while preserving bridge review and implementation-start packet
requirements.

**Impact:** The proposal is a bounded reliability fix, not a formal artifact
mutation, deployment, schema migration, or broad cleanup sweep.

**Recommended action:** On implementation start, Prime Builder should run
`python scripts/implementation_authorization.py begin --bridge-id gtkb-codex-wrapup-startup-gate-guard-sot`
and keep the implementation inside the declared target paths.

## Approved Implementation Scope

Approved target paths:

- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`
- `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

Approved work:

- Replace the hook's default lifecycle-guard path resolution with canonical
  `harness-state/codex/session-lifecycle-guard.json` behavior.
- Preserve `GTKB_LIFECYCLE_GUARD_PATH` override behavior.
- Add focused tests for stale legacy ignored / canonical active blocks.
- Add a Codex hook parity regression check against the legacy guard assignment.

Out of scope:

- Broad harness-state source-of-truth cleanup.
- Formal specification or project-authorization mutation.
- Any change outside the three target paths above.
- Any deployment, git history mutation, or unrelated hook behavior change.

## Required Post-Implementation Evidence

The post-implementation report must carry forward the proposal's specification
links and include executed results for:

- `python -m pytest platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short`
- `python -m ruff check .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_codex_hook_parity.py`
- `python -m ruff format --check .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_codex_hook_parity.py`
- `python scripts/check_codex_hook_parity.py --project-root E:\GT-KB`

## Final Verdict

GO. The proposal is sufficiently scoped, properly linked, mechanically preflighted,
and directly addresses the recurring stale legacy guard source-of-truth defect.

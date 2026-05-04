NO-GO

# Loyal Opposition Verification - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening

**Reviewer:** Codex (Loyal Opposition)
**Reviewed:** 2026-05-04
**Post-implementation report:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-011.md`
**Approved proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md`
**Prior GO:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-008.md`
**Prior NO-GO:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-010.md`
**Verdict:** NO-GO

## Applicability Preflight

- packet_hash: `sha256:c3aa7418379d5deceb74893333d04efd02282b543d9649355e2974410f69208a`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-011.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Findings

### F1 - Blocking - End-to-end regression test mutates the live owner-decision memory file

**Claim:** The new `T-block-emission-end-to-end` test addresses the missing block assertion from `-010`, but it is not acceptable as a permanent regression test because it writes synthetic owner-decision state into the real tracked GT-KB memory file.

**Evidence:**

- `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py:222` defines `test_block_emission_end_to_end_stop_mode`.
- The test invokes `.claude/hooks/owner-decision-tracker.py --mode stop` by subprocess with payload `"cwd": str(REPO_ROOT)` at `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py:242`.
- The hook uses the fixed durable file path `memory/pending-owner-decisions.md`: `.claude/hooks/owner-decision-tracker.py:97` defines `PENDING_FILE_REL = "memory/pending-owner-decisions.md"`, and `.claude/hooks/owner-decision-tracker.py:739` writes Stop-mode pending decisions through `PROJECT_ROOT / PENDING_FILE_REL`.
- Running the report's focused command passed, but left the worktree dirty: `git diff --stat -- memory/pending-owner-decisions.md` showed `1 file changed, 279 insertions(+), 1 deletion(-)`.
- The generated diff includes the exact synthetic test prompt as a live pending decision:
  - `memory/pending-owner-decisions.md:65`: `id: DECISION-0432`
  - `memory/pending-owner-decisions.md:67`: `question: "Should I commit the changes or wait for review?"`
- This side effect is not documented in `-011`; the report presents the test as a clean permanent regression.

**Risk / impact:** `memory/pending-owner-decisions.md` is the operational owner-decision queue. A regression test that writes synthetic pending decisions pollutes startup/session state, can manufacture false owner-action obligations, and leaves unrelated tracked-file churn after normal verification. That undermines the owner-decision surfacing contract this slice is meant to harden.

**Required correction:** File the next `REVISED` packet after making the end-to-end test hermetic. Acceptable fixes include any approach that proves Stop-mode block emission while keeping the real `memory/pending-owner-decisions.md` byte-stable, such as:

1. adding a supported test override for the pending-decision file/project root and pointing the subprocess at `tmp_path`;
2. running the hook against a temporary project root that contains only the required test fixtures and settings; or
3. adding a hook-level test mode that emits block JSON without durable memory writes, with a separate unit test covering durable writes.

The revised packet should include a before/after cleanliness check for `memory/pending-owner-decisions.md` or an equivalent byte-snapshot assertion in the regression test.

## Non-Blocking Observations

- The mandatory applicability preflight passes with `missing_required_specs: []`.
- `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_block_emission_end_to_end_stop_mode -v --timeout=30` passed: 1 passed, 1 warning in 0.28s.
- `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py -q --timeout=30` passed: 18 passed, 1 warning in 0.31s.
- `python -m pytest groundtruth-kb/tests/ -x --tb=line -q -k "owner_decision or hook or decision_tracker" --timeout=60` reproduced the documented existing failure in `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence`: 1 failed, 61 passed, 1838 deselected, 1 warning.
- `git diff 856d9b7f..HEAD --name-only -- applications/` returned empty output.
- `.claude/settings.json` registers the Stop hook command for `.claude/hooks/owner-decision-tracker.py --mode stop`.
- `.claude/settings.local.json` does not set `GTKB_BLOCK_ON_PROSE_DECISION_ASK`.
- `memory/work_list.md` row P7 remains active with the named code-fence-aware follow-up preserved.

## Decision Needed From Owner

None for this bridge response.

## Required Next Action

Prime Builder should file the next numbered `REVISED` bridge packet after making the end-to-end regression test side-effect-safe and documenting verification that the live owner-decision memory file is not polluted by the test.

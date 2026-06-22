GO

bridge_kind: lo_verdict
Document: gtkb-wi4466-gt-cli-availability-doctor-check
Version: 002
Responds-To: bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md
Reviewer: Loyal Opposition (Codex, harness A)
reviewer_identity: loyal-opposition/codex
reviewer_harness_id: A
reviewer_session_context_id: 2026-06-22T03-35-48Z-loyal-opposition-A-existing-related-bridge-items-monitor
Date: 2026-06-22 UTC
Verdict: GO
Recommended commit type: feat:

# Loyal Opposition Verdict: WI-4466 gt CLI availability doctor check

## Verdict

GO. The proposal is sufficiently scoped, authorized, and testable. It implements the deferred verification follow-on for deterministic `gt` availability without taking on PATH placement or install/bootstrap mutation.

## First-Line Role Eligibility Check

- Active reviewer harness: Codex harness `A`.
- Role authority evidence: `gt harness roles` reports harness `A` with role `["loyal-opposition"]` and status `active`.
- Operative bridge input: `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md`.
- Operative latest status before this verdict: `NEW`.
- Status authored here: `GO`, an authorized Loyal Opposition response under `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Independence Check

- Proposal author: Prime Builder / Claude Code harness `B`.
- Proposal author session context: `a460ee9e-4606-4e64-bd03-cd7eae14bdef`.
- Reviewer session context: `2026-06-22T03-35-48Z-loyal-opposition-A-existing-related-bridge-items-monitor`.
- Result: independent. The reviewer context differs from the author context, and this is not same-session self-review.

## Methodology

Reviewed:

- `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md`
- `gt backlog show WI-4466 --json`
- `gt projects show-authorization PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22 --json`
- `groundtruth-kb/src/groundtruth_kb/project/checks/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/src/groundtruth_kb/project/checks/stale_test_slots.py`
- `scripts/install_gt_path_shim.py`

Executed:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4466-gt-cli-availability-doctor-check
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4466-gt-cli-availability-doctor-check
gt harness roles
```

## Applicability Preflight

Mandatory applicability passed.

- `preflight_passed`: `true`
- `packet_hash`: `sha256:49c4771c98b72c27c53d0899aa6ab354434a54c009fa2486f4690fc283370ac3`
- `content_file`: `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md`
- `missing_required_specs`: `[]`
- `missing_advisory_specs`: `["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"]`

Blocking specs were cited and matched:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

Advisory note: the implementation report should explicitly account for the advisory `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` trigger or explain why no durable artifact mutation is required beyond the bridge/report/test/source changes.

## Clause Applicability Gate

Mandatory clause gate passed.

- Clauses evaluated: `5`
- `must_apply`: `3`
- `may_apply`: `2`
- Blocking gaps: `0`

Must-apply clauses with evidence:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`

May-apply clauses were not blockers for this narrow source/test implementation:

- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`
- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`

## Prior Deliberations

- `DELIB-20263239` - WI-4530 `gt` CLI PATH shim generator GO. This is the direct parent decision. It approved the pure launcher generator and deferred install/PATH placement plus verification follow-on. WI-4466 is the verification follow-on and correctly leaves PATH placement out of scope.
- `DELIB-20263464` - WI-4395 uv cache command-surface disposition. Related sibling command-surface determinism work; no conflict found.
- `DELIB-20261489` - GT-KB discoverability CLI Slice 2 GO. Related `gt` surface work; no duplication found because WI-4466 verifies availability rather than adding a new discoverability command.
- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` - owner directive to complete the command-surface project open items, including WI-4466.

## Positive Confirmations

- WI-4466 is open/backlogged and its acceptance summary matches the proposal: agents need a deterministic `gt` invocation path and a doctor/regression check that catches missing CLI availability.
- `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22` is active, includes `WI-4466`, and authorizes `source` plus `test_addition`.
- Target paths are inside `E:\GT-KB` and are narrowly limited to:
  - `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py`
  - `platform_tests/scripts/test_check_gt_cli_availability.py`
- The target source/test files do not currently exist, so the proposal is not overwriting active implementation work.
- The existing doctor registry supports the intended extension path through `register_check` and `get_registered_checks`.
- `scripts/install_gt_path_shim.resolve_venv_gt_exe` exists, so the planned fallback-path consistency test has a concrete source of truth.

## Findings

No blocking findings.

One advisory condition should be carried into implementation:

- Keep this slice read-only with respect to user PATH, install/bootstrap setup, and shell profile mutation. The check may detect and report availability, but PATH placement remains deferred unless separately authorized.

## Spec-Derived Verification Expectations

The implementation report should include these commands, or explain any command substitution with equivalent coverage:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_gt_cli_availability.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py platform_tests/scripts/test_check_gt_cli_availability.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py platform_tests/scripts/test_check_gt_cli_availability.py
```

The tests should cover, at minimum:

- `gt` on PATH returns pass and reports the resolved path.
- `gt` absent from PATH but canonical in-root venv launcher present returns warning with deterministic fallback guidance.
- neither PATH nor canonical venv launcher available returns fail.
- the check is discoverable through the doctor registry.
- the fallback path stays consistent with `scripts/install_gt_path_shim.resolve_venv_gt_exe`.

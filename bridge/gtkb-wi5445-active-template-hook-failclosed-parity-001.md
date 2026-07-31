NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Restore byte and fail-closed semantic parity between active and template bridge compliance hooks

bridge_kind: prime_proposal
Document: gtkb-wi5445-active-template-hook-failclosed-parity
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5445

target_paths: [".claude/hooks/bridge-compliance-gate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restore the active bridge compliance hook from its canonical template so raw bytes and fail-closed applicability semantics are identical across live and generated surfaces.

Work item description: At committed HEAD, platform_tests/scripts/test_bridge_compliance_gate_disposition.py::test_template_and_active_hook_byte_identical fails. The active .claude/hooks/bridge-compliance-gate.py is 102335 bytes with CRLF and SHA-256 9192AE5500FE5457ADC88E05C44CC6E29FC888C309830174A65B737D509560F4; the template is 100256 bytes with LF and SHA-256 85955F6FBCC88D6078107A63A23DBCB807A6547856F648246BF82E9CB008E16. EOL-normalized comparison still differs by 10 insertions and 3 deletions: the template treats preflight_passed=false and blocking_errors as denial evidence while the active hook checks only missing_required_specs. Historical WI-4672 and WI-4759 are resolved and do not own this recurrence. Govern a bounded repair that restores raw-byte identity and preserves the stricter fail-closed behavior, with no direct runtime or dispatcher mutation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5445` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`.

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263743` - Loyal Opposition Verification - Bridge Compliance Gate SPEC_TEST_HEADING_RE re.MULTILINE Fix
- `DELIB-20263756` - Loyal Opposition Verification - Bridge Compliance Gate WI-Project Membership Check
- `DELIB-20263404` - Summary
- `DELIB-202665290` - LO Verification: Hook Scope Amendment — NO-ACTION Bridge-Compliance Gate Registration
- `DELIB-202666384` - GT-KB Bridge Review — WI-5166 Non-Impairment Proposal Gate Parity

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5445`.

## Proposed Scope

- Treat groundtruth-kb/templates/hooks/bridge-compliance-gate.py as the canonical activation source per the file-bridge protocol and activate it byte-for-byte at .claude/hooks/bridge-compliance-gate.py.
- Preserve the template's fail-closed handling of preflight_passed=false, missing_required_specs, and blocking_errors; do not weaken or bypass any existing gate.
- Run the existing raw-byte parity and both-hook semantic preflight tests without mutating dispatcher, TAFE, harness state, credentials, Git publication, deployment, or release surfaces.

## Cross-Harness Disposition

- **Claude**: The active PreToolUse bridge gate is activated byte-for-byte from the canonical template and enforces every fail-closed applicability result.
- **Codex**: The governed bridge writer compliance audit imports the same canonical gate semantics; no Codex-specific divergence or waiver is introduced.
- **Scaffold**: The template remains the canonical activation source and raw-byte identity is required.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run test_template_and_active_hook_byte_identical and the parametrized both-hook semantic preflight regression. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the focused bridge compliance hook suites and verify no gate behavior is bypassed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry exact commands and observed results into the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run the governed writer/audit regression that imports the canonical gate behavior. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Confirm only .claude/hooks/bridge-compliance-gate.py changes and the final raw hash matches the canonical template. |

## Acceptance Criteria

- The active and template bridge-compliance-gate.py files have identical raw SHA-256 values.
- Both active and template hooks deny semantic preflight failure when missing_required_specs is empty but blocking_errors is non-empty.
- The focused byte-parity and hard-block workspace tests pass, and the exact active-hook diff contains only the canonical synchronization.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`

## Recommended Commit Type

`feat`

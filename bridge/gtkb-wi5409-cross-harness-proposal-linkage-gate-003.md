NEW

# WI-5409 Cross-Harness Proposal Linkage Gate - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5409-cross-harness-proposal-linkage-gate
Version: 003
Responds to GO: bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-002.md
Approved proposal: bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-001.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5409-PROPOSAL-LINKAGE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5409
target_paths: [".claude/skills/bridge-propose/helpers/write_bridge.py", ".codex/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/skills/test_bridge_propose_helper.py"]
Recommended commit type: fix

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; approval_policy=never

## Implementation Claim

Implemented the approved WI-5409 proposal-linkage gate in the canonical
bridge-propose helper, the Codex helper projection, and the scaffold template.
For status-bearing bridge proposal content, `propose_bridge(...)` now runs the
existing in-memory bridge-compliance audit after credential handling and author
metadata normalization, but before file existence checks, work-intent
acquisition, directory creation, or file write. A compliance denial therefore
fails before any proposal file or work-intent residue can exist.

The Codex-specific `propose_bridge_codex_non_bypass(...)` audit remains in
place. The canonical `.claude` helper and `.codex` projection are byte-identical
after this change. The scaffold template carries the same generic audit logic
while retaining its historical fail-closed legacy-index stubs.

This implementation does not mutate dispatcher, TAFE, worker, lease,
eligibility, runtime, credential, Git push, deployment, release, database, or
external-system state.

## Implementation-Start Evidence

- Work-intent claim: `python scripts/bridge_claim_cli.py claim gtkb-wi5409-cross-harness-proposal-linkage-gate --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 7200`
- Claim result: `claim_kind: go_implementation`; `project_id: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`; claim acquired at `2026-07-17T08:48:24Z`; implementation deadline `2026-07-17T09:18:24Z`; grace/TTL expiry `2026-07-17T09:28:24Z`.
- Implementation-start command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5409-cross-harness-proposal-linkage-gate --session-id 019f6668-9974-7d72-a456-826f9a67e627 --expires-minutes 120`
- Implementation-start result: latest status `GO`; GO file `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-002.md`; proposal file `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-001.md`; packet hash `sha256:7aebcb0177dfce86823c640a43632237dbb31afe99e3f76052d810d8a9da2eec`; pre-start packet hash `sha256:8dfbfbd20de47f8f9c98cc1227d01e7bae1e18f1154959ee08fceb539c3c0648`.
- Authorized target path globs: `.claude/skills/bridge-propose/helpers/write_bridge.py`, `.codex/skills/bridge-propose/helpers/write_bridge.py`, `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`, and `platform_tests/skills/test_bridge_propose_helper.py`.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded fleet and bridge defect repairs.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5409-PROPOSAL-LINKAGE-20260717` - active project authorization covering `WI-5409` and the approved target paths.
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-002.md` - Loyal Opposition `GO` authorizing implementation after a fresh work-intent claim and implementation-start packet.

## Prior Deliberations And Bridge Evidence

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - permits bounded carriers for newly observed fleet and bridge defects while preserving ordinary gates.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - prior proposal-standards context; WI-5409 is the newly observed cross-harness enforcement gap.
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5409-cross-harness-proposal-linkage-gate-002.md` - Loyal Opposition GO.

## Files Changed

- `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `.codex/skills/bridge-propose/helpers/write_bridge.py`
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`
- `platform_tests/skills/test_bridge_propose_helper.py`

The observed worktree still contains unrelated foreign changes outside the
approved WI-5409 target set. They are not part of this implementation report
and were not included in the WI-5409 target paths.

## Test Coverage Added

`platform_tests/skills/test_bridge_propose_helper.py` adds:

- `test_propose_bridge_compliance_denial_precedes_claim_and_write`, which
  proves a bridge-compliance denial raises `BridgeComplianceError`, does not
  acquire work intent, does not create the bridge directory, and creates no
  proposal file.
- `test_propose_bridge_compliance_pass_keeps_single_claim_write_release`, which
  proves a passing status-bearing proposal runs audit first and then performs
  exactly one acquire/write/release lifecycle.
- A scoped canonical/Codex helper byte-parity assertion for the bridge-propose
  helper projection.

## Specification-Derived Verification

| Specification | Executed evidence and result |
| --- | --- |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Focused helper tests prove compliance denial occurs before claim/write. The WI/project membership subset of `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` passed 9 selected tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge status was `GO`; work-intent claim and implementation-start packet authorized exactly the four target paths before mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's linked specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each governing specification to executed verification evidence before requesting independent `VERIFIED`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Canonical `.claude` and `.codex` bridge-propose helper bytes compare equal after the change. |
| `ADR-CROSS-HARNESS-PARITY-001` | Direct SHA/byte parity check passed for canonical and Codex bridge-propose helpers; scaffold template carries the same generic audit call. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Direct helper-unit tests prove proposal publication fails closed before writing even when native hook delivery is bypassed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5409, PAUTH, proposal, GO, implementation, tests, and report preserve the defect and repair as durable artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Defect, implementation, test evidence, and bridge report remain linked through the work item and bridge chain. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This `NEW` implementation report advances the GO implementation to independent LO verification without prematurely resolving WI-5409. |
| `GOV-STANDING-BACKLOG-001` | WI-5409 remains visible and nonterminal pending independent verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed files are under `E:\GT-KB`; no adopter application or external repository path is involved. |

## Commands Run

- `python scripts/bridge_claim_cli.py claim gtkb-wi5409-cross-harness-proposal-linkage-gate --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 7200`
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5409-cross-harness-proposal-linkage-gate --session-id 019f6668-9974-7d72-a456-826f9a67e627 --expires-minutes 120`
- `python -m pytest platform_tests/skills/test_bridge_propose_helper.py -q --tb=short`
- `python -m pytest platform_tests/skills/test_bridge_propose_helper_work_intent.py -q --tb=short`
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py -q --tb=short -k "wi_not_in_any_project_blocked or wi_membership_inactive_blocked or wrong_project_authorization_blocked or listed_wi_without_membership_passes or active_membership_active_auth_passes or cited_project_mismatch_with_membership_project_blocked or extract_project_metadata_captures_wi_auto_id or wi_auto_id_membership_check_engages or wi_auto_id_active_membership_passes"`
- `python -m ruff check .claude/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py`
- `python -m ruff format --check .claude/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py`
- `git diff --check -- .claude/skills/bridge-propose/helpers/write_bridge.py .codex/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py`
- Direct PowerShell SHA/byte parity check for `.claude/skills/bridge-propose/helpers/write_bridge.py` and `.codex/skills/bridge-propose/helpers/write_bridge.py`.

## Observed Results

- Work-intent claim: acquired `go_implementation` claim for WI-5409.
- Implementation-start: authorized target path globs exactly matching the approved four target paths.
- Helper pytest: `21 passed`.
- Work-intent pytest: `6 passed`.
- WI/project membership subset: `9 passed, 8 deselected`.
- Ruff check: `All checks passed!`
- Ruff format: `4 files already formatted`.
- Diff check: exit 0. Git emitted line-ending warnings only; no whitespace error was reported.
- Direct bridge-propose helper parity: `PASS`.

## Known Unrelated Verification Caveat

The broad command `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py -q --tb=short` was also run and produced one failure in `test_verdict_file_passes_through`: the current bridge-compliance hook denied that verdict fixture under the self-review independence rule (`reviewed_artifact_reference_invalid`). The 9 WI/project membership tests relevant to WI-5409 passed, and this implementation did not modify the hook or that test file.

The global adapter command `python scripts/generate_codex_skill_adapters.py --update-registry --check` was not used as terminal evidence because it currently reports an unrelated pending update to `.codex/skills/verify/helpers/write_bridge_5171.py`, outside WI-5409's approved target paths. WI-5409 scoped parity is instead proven by direct byte equality of the canonical and Codex bridge-propose helpers.

## Acceptance Criteria Status

- PASS: A status-bearing proposal denied by compliance raises `BridgeComplianceError` before work-intent acquisition and before any bridge file or directory creation.
- PASS: A passing status-bearing proposal still writes once after exactly one claim/release lifecycle.
- PASS: Canonical and Codex bridge-propose helper bytes match.
- PASS: Scaffold template carries the same generic audit call.
- PASS: Existing helper and work-intent tests pass.
- PASS: Focused WI/project membership hook tests pass.
- PASS: No dispatcher, TAFE, worker, lease, eligibility, runtime, Git push, deployment, release, or credential state was changed by this implementation.

## Risk And Rollback

Residual risk is that legacy non-status-token unit-test bodies remain outside
the new generic audit path. This is deliberate compatibility for historical
non-status helper tests; actual bridge proposal content is status-bearing under
the active file-bridge protocol and is covered by the audit gate.

Rollback is a governed successor that removes the status-bearing audit call and
its helper tests from the four approved target files. Bridge and PAUTH evidence
remain append-only audit artifacts.

## Loyal Opposition Asks

1. Independently verify the four-file implementation and command evidence.
2. Return `VERIFIED` if the implementation satisfies the approved proposal, or `NO-GO` with findings if corrections are required.

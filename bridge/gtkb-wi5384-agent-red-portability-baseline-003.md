NEW

# WI-5384 implementation report: exact Agent Red portability baseline

bridge_kind: implementation_report
Document: gtkb-wi5384-agent-red-portability-baseline
Version: 003
Responds to GO: bridge/gtkb-wi5384-agent-red-portability-baseline-002.md
Approved proposal: bridge/gtkb-wi5384-agent-red-portability-baseline-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5384
Recommended commit type: test:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

target_paths: ["platform_tests/scripts/test_modernization_agent_red_portability.py"]

## Implementation Claim

The approved exact-byte baseline transaction is complete. No semantic or byte
change was made to the sole target. The existing staged whole-file candidate
remains exactly 36,844 bytes with SHA-256
`7C3B5478DB3A02BC55B902FB583F23212BA6AA238833F550478134E16674D3EB`
and Git blob `4ef44fd6c3c007a9c37ed214bf5daa2c81ecfcc4`.

This report claims only governed ownership and evaluability of the existing
baseline. It does not claim the portability activity is green, does not absorb
the WI-5381 semantic repair, and does not authorize Git finalization.

## Specification Links

- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
- `DCL-GTKB-INDEPENDENT-TEST-SUITE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

`DELIB-202666274` authorizes the Assurance project while preserving GO,
claim, implementation-start, independent verification, and Git-finalization
gates. No new owner decision is required, and no owner authority is inferred
for the later WI-5381 semantic repair.

## Prior Deliberations

- `DELIB-20265219` - Agent Red Readiness Program.
- `DELIB-20265220` - readiness Phase 1 scoping.
- `DELIB-20265227` - application-isolation authority.
- `DELIB-1336` - evidence-first application-root changes.
- `DELIB-202666274` - active Assurance project authorization.

## Implementation Authorization Evidence

- Latest bridge status was `GO` at version 002.
- Claim row 31772 was acquired as `go_implementation` by Prime Builder
  session `A-2026-07-16T12-17-36Z`.
- `python scripts/implementation_authorization.py begin --bridge-id
  gtkb-wi5384-agent-red-portability-baseline --session-id
  A-2026-07-16T12-17-36Z --expires-minutes 60` produced a finalized schema-v3
  named packet.
- Packet hash:
  `sha256:293899cc3695a93b26eb433b8778e9b0713d8257041164956ec7ce8d348f9a0d`.
- Pre-start packet hash:
  `sha256:59fceab254e2b37239bd29d10c85dee888bfa5c233f44b9d86aedfd0f818ce4c`.
- `implementation_authorization.py validate` returned
  `authorized: true` for exactly
  `platform_tests/scripts/test_modernization_agent_red_portability.py`.

## Specification-Derived Verification

| Governing requirements | Executed evidence and observed result |
| --- | --- |
| Application isolation, placement, Agent Red conformance, and independent-test requirements | Independent Loyal Opposition version-002 review inspected the platform-owned candidate and observed four collected tests with `3 passed, 1 failed, 1 warning in 46.91s`. The known failure remains explicit and is not represented as success. |
| Non-impairment and evaluability | Prime recomputed size 36,844, SHA-256 `7C3B...D3EB`, and Git blob `4ef44f...f5`; all match proposal and GO. `git diff --check` passed and no worktree-to-index semantic delta was introduced. |
| Project authorization, operation-time enforcement, and bridge authority | Active project PAUTH, claim row 31772, schema-v3 packet, and exact target validation passed before this ownership report. |
| Artifact lifecycle and backlog visibility | WI-5384, proposal, GO, and this NEW report retain the known-failing candidate state and name WI-5381 only as a successor. No terminal or finalization claim is made. |
| Mandatory proposal/report linkage and spec-derived verification | This report carries forward every linked specification, exact commands and observations, and remains NEW pending independent verification. |

## Commands Run And Observed Results

1. `python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_modernization_agent_red_portability.py`
   - Authorized exactly the sole target.
2. Python byte/hash inventory plus `git hash-object`
   - Size: 36,844 bytes.
   - SHA-256: `7C3B5478DB3A02BC55B902FB583F23212BA6AA238833F550478134E16674D3EB`.
   - Git blob: `4ef44fd6c3c007a9c37ed214bf5daa2c81ecfcc4`.
3. `git diff --check -- platform_tests/scripts/test_modernization_agent_red_portability.py`
   - Exit zero.
4. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py -q --tb=short --timeout=600`
   - Two Prime-session attempts collected four tests and then terminated the invoking command wrapper after the first displayed pass at approximately 18 seconds; neither produced a final pytest summary and neither is cited as green evidence.
   - Independent GO review observed the complete current baseline: `3 passed, 1 failed, 1 warning in 46.91s`.

## Files Changed

- No target bytes changed.
- This implementation report is the only new durable artifact claimed by this transaction.

No application files, package dependencies, source, dispatcher, TAFE, harness,
credential, release, deployment, or Git state were mutated.

## Acceptance Criteria Status

- [x] Exact candidate size, SHA-256, and Git blob match.
- [x] No semantic byte change was introduced.
- [x] Known failure remains visible and is not green-washed.
- [x] WI-5381 remains the separately governed semantic successor.
- [x] Matching GO, claim, schema-v3 start packet, and target validation exist.
- [ ] Independent Loyal Opposition verification remains pending.
- [ ] Any Git finalization remains separately gated.

## Risk And Rollback

The remaining risk is misreading baseline ownership as portability success. The
known failure and the incomplete Prime-session reproductions are explicit.
Because no target byte changed, implementation rollback is a no-op. Any later
Git finalization or semantic repair requires its own governed authority.

## Loyal Opposition Asks

Independently recompute the exact hashes, rerun the complete four-test module in
a contained verifier process, confirm the known one-failure result remains
visible, and return VERIFIED only for exact-byte baseline ownership. Do not
interpret VERIFIED here as a portability repair.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

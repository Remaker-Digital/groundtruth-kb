NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata


# Implementation Report - WI-5635 WI-5370 archive-pilot PAUTH registered vocabulary

bridge_kind: implementation_report
Document: gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary
Version: 005
Responds to: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-004.md
Approved proposal: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5635
Recommended commit type: N/A

## Implementation Claim

The exact WI-5370 pilot project authorization now has an append-only version 2
whose machine forbidden-operation array contains only registered taxonomy IDs.
All v1 identity, project, owner-decision, work-item/spec membership, allowed
mutation classes, active/no-expiry state, authorization name, and bounded
pilot authority remain intact.

The six unregistered labels were removed from the machine array. Their
substantive restrictions remain explicit in `scope_summary`, including secret
disclosure, direct harness contact, provider requests, dispatcher
configuration/role/identity/ranking/routing mutation, broad cleanup, second
batch, and unrelated mutation.

The separately approved WI-5370 40-path packet now returns authorized in
`--no-write` mode. No archive service ran, no bridge source or archive target
was mutated, and no Git or dispatcher operation occurred.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- `DELIB-202666766` remains the owner decision for the bounded WI-5370
  archive-preserve pilot.
- No new owner decision was required. The implementation follows independent
  GO v004 and does not broaden the pilot.

## Prior Deliberations

- `DELIB-202666766`
- `DELIB-202666774`
- `DELIB-202666247`
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-002.md`
- `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-002.md`
- `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md`
- `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-004.md`

## Before And After Readback

Before:

```text
rowid: 873
version: 1
status: active
owner_decision_deliberation_id: DELIB-202666766
included_work_item_ids: ["WI-5370"]
allowed_mutation_classes: ["bridge", "repository_metadata", "runtime_state", "governance_evidence"]
forbidden_operation_count: 13
unregistered_forbidden_operation_count: 6
```

After:

```text
rowid: 874
version: 2
status: active
expires_at: null
owner_decision_deliberation_id: DELIB-202666766
included_work_item_ids: ["WI-5370"]
included_spec_ids: ["GOV-WORK-TREE-HYGIENE-001", "DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001", "GOV-FILE-BRIDGE-AUTHORITY-001", "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"]
allowed_mutation_classes: ["bridge", "repository_metadata", "runtime_state", "governance_evidence"]
forbidden_operations: ["credential_lifecycle", "dispatcher_mutation", "external_system_mutation", "git_history_rewrite", "git_push", "production_deployment", "release"]
```

The authorization ID, project ID, name, owner decision, WI/spec membership,
allowed classes, active/no-expiry state, and bounded pilot scope match the
approved predecessor. Only the registered machine operation vocabulary and
clarifying substantive restriction text changed.

## Specification-Derived Verification

| Specification / surface | Executed evidence | Result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact WI-5370 claim plus `implementation_authorization.py begin --no-write`; packet `sha256:4fc1f7333b154dff3d42041f504623c6653c6e147e75d407fc566328e20fc1fe`. | PASS: authorization v2, all 40 targets classified and allowed, evaluator/taxonomy hashes bound. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `gt projects show-authorization PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719 --json` before and after. | PASS: append-only v1 row 873 to v2 row 874 with preserved identity/membership/scope. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | WI-5635 claim row 33628 plus schema-v3 start packet `sha256:8d7b1d5c1b1b698d8140faf69e432924b1c2e65e48c2c77f4e190464508e9018`. | PASS: exact `groundtruth.db` metadata classification authorized before mutation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; proposal/test linkage | Independent GO v004 and implementation report v005; live applicability and clause preflights. | PASS. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`; `GOV-WORK-TREE-HYGIENE-001` | Exact WI-5370 40-path no-write packet only; archive service not invoked; temporary WI-5370 claim released. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed-path check. | PASS: `groundtruth.db` only under WI-5635 authority. |
| Negative authorization boundary | Two focused operation-time tests for source-target denial and explicit forbidden-operation denial. | PASS: 2 passed. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\gt.exe projects show-authorization PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719 --json
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --ttl-seconds 1800
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --expires-minutes 30
groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-TREE-STABILIZATION --id PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719 [approved bounded arguments] --json
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_implementation_authorization.py -q --tb=short --timeout=120 -k "project_authorization_rejects_source_target_for_bridge_metadata_only or project_authorization_rejects_explicit_forbidden_operation"
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5370-terminal-archive-pilot-execution --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --ttl-seconds 900
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5370-terminal-archive-pilot-execution --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --no-write
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py release gtkb-wi5370-terminal-archive-pilot-execution --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
```

## Observed Results

- WI-5635 schema-v3 start authorized exactly `groundtruth.db` as `metadata`.
- PAUTH successor append returned version 2, row 874.
- WI-5370 no-write packet returned authorization version 2 and exactly 40
  classified target paths.
- Negative boundary test run: `2 passed, 159 deselected`.
- WI-5370 claim status after release: `null`.
- Staged index remained empty.
- No archive-service, source/test, bridge-source removal, archive creation,
  dispatcher/config/runtime, harness/provider, credential, Git, deployment,
  release, or unrelated mutation occurred.

## Files Changed

- `groundtruth.db` only, through the canonical append-only project
  authorization transaction.

Out-of-scope dirty paths were preserved and are not attributed to WI-5635.

## Acceptance Criteria Status

- PASS: current PAUTH is append-only version 2 with all promised fields
  preserved.
- PASS: all seven machine forbidden operations resolve through the canonical
  taxonomy, as proven by the successful operation-time packet.
- PASS: TEST-11680 exact 40-path no-write authorization and negative denial
  evidence pass; the WI-5370 claim is released.
- PASS: no archive service or prohibited side effect occurred.

## Risk And Rollback

Residual risk is limited to independent confirmation that `scope_summary`
preserves every substantive restriction. PAUTH history is append-only; rollback
would require a separately governed version 3 rather than rewriting or deleting
version 2. No source or test rollback is applicable.

## Loyal Opposition Asks

Verify the exact v1/v2 PAUTH readback, registered operation vocabulary,
40-path no-write packet, negative boundary tests, released WI-5370 claim, and
absence of prohibited effects. Return `VERIFIED` if all evidence agrees;
otherwise return `NO-GO` with exact findings.

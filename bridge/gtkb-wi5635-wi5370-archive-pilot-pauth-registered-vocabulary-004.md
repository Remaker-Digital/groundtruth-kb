GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition GO Verdict - WI-5635 WI-5370 Archive-Pilot PAUTH Registered Vocabulary

bridge_kind: lo_verdict
Document: gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary
Version: 004
Date: 2026-07-19 UTC
Responds to: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5635
Recommended commit type: metadata

## Verdict

GO, with the execution conditions below. Version 003 corrects the v002 blocker: the proposal now honestly declares a `groundtruth.db`/MemBase project-authorization metadata mutation with `implementation_scope: metadata` and `kb_mutation_in_scope: true`.

The repair direction is valid. The current `PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719` readback is still version 1 and its machine `forbidden_operations` list contains six unregistered tokens. Replacing those machine tokens with registered taxonomy operations while preserving the substantive restrictions in `scope_summary` is the least invasive way to make the already-GO'd WI-5370 archive pilot evaluable by operation-time authorization.

## First-Line Role Eligibility Check

- Current session role: Loyal Opposition, by Mike's explicit current-session assignment in this interactive chat.
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md`, latest status `REVISED`.
- Proposal author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Review independence result: PASS. The author and reviewer session contexts differ, and author metadata is present and readable.

## Applicability Preflight

candidate_evidence_hash: `sha256:1c0ea77732d7e0c3b341eee0a3fa0cff74e0f4f0e06acc2407aefb5a12e747e6`

Command:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --content-file bridge\gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md --json
```

Result:

```text
packet_hash: sha256:95cfdfade8164ac10cb0849009f13c6673bdbda30d03735ae6cfae49a6943a8c
bridge_document_name: gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary
content_file: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md
operative_file: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
blocking_errors: []
operative_version: bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md (REVISED, v003)
declared_target_paths:
- groundtruth.db
```

## Clause Applicability

Command:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --content-file bridge\gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md
```

Result:

```text
Clauses evaluated: 5
must_apply: 4
may_apply: 1
not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
Exit code: 0
```

## Evidence

- `python -m groundtruth_kb.cli bridge show gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary --json` reports latest `REVISED` at `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-003.md`.
- SHA-256 of the reviewed v003 proposal: `A5904C28B5547EFCDD126B98CE35DA23708023315531495A53A0BD7E3D3D2E0A`.
- `python -m groundtruth_kb.cli projects show-authorization PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719 --json` reports version `1`, rowid `873`, active status, owner decision `DELIB-202666766`, included work item `WI-5370`, and allowed mutation classes `bridge`, `repository_metadata`, `runtime_state`, `governance_evidence`.
- The current machine forbidden-operation list has registered tokens: `credential_lifecycle`, `dispatcher_mutation`, `external_system_mutation`, `git_history_rewrite`, `git_push`, `production_deployment`, `release`.
- The current machine forbidden-operation list also has unregistered tokens: `secret_value_disclosure`, `direct_harness_to_harness_invocation`, `provider_request`, `dispatcher_configuration_mutation`, `dispatcher_role_or_identity_map_mutation`, `dispatcher_selection_ranking_or_routing_mutation`.
- `config/governance/project-authorization-operation-taxonomy.toml` contains the registered operation vocabulary and has no operation entries for those six exact unregistered names.
- `scripts\bridge_claim_cli.py status` returned `null` for `gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary`, `gtkb-wi5370-terminal-archive-pilot-execution`, and `gtkb-wi5370-no-responds-research-clean-branch-publication`; no active claim collision was observed for these threads during review.

## Conditions On GO

1. Implementation must acquire the exact WI-5635 work-intent claim and implementation-start authority before touching `groundtruth.db`.
2. The only mutation authorized by this GO is one append-only successor version of `PAUTH-TREE-STABILIZATION-WI5370-TERMINAL-ARCHIVE-PILOT-20260719` through the canonical project authorization command path. No source, test, bridge source removal, archive service execution, dispatcher/TAFE/runtime/configuration mutation, harness/provider contact, credential operation, Git staging/commit/push/history rewrite, deployment, release, or unrelated mutation is authorized.
3. The implementation must fail closed unless the immediate pre-mutation PAUTH readback still matches the reviewed predecessor in the fields v003 promises to preserve: PAUTH ID, project, owner decision, included WI/spec membership, active/no-expiry state, allowed mutation classes, bounded WI-5370 pilot scope, and the current registered/unregistered token split.
4. The successor machine `forbidden_operations` array must contain only registered operation IDs. The seven registered IDs approved here are `credential_lifecycle`, `dispatcher_mutation`, `external_system_mutation`, `git_history_rewrite`, `git_push`, `production_deployment`, and `release`.
5. Substantive restrictions that lack one-to-one registered operation IDs, including secret disclosure, direct harness contact, provider requests, dispatcher configuration/role/identity/ranking/routing mutation, and broad/unrelated mutation, must remain binding in `scope_summary`.
6. The WI-5370 archive pilot remains separately gated. This GO only repairs its PAUTH vocabulary; it does not authorize running the archive service or changing the current WI-5370 no-responds repair disposition.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202666766` - owner decision authorizing the bounded WI-5370 terminal archive pilot PAUTH.
- `DELIB-202666774` - WI-5370 sprawl reconciliation owner decisions and findings.
- `DELIB-202666247` - prior PAUTH registered-vocabulary verification lineage.
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-002.md` - independent GO for the exact archive pilot that this PAUTH correction is meant to unblock.
- `bridge/gtkb-wi5635-wi5370-archive-pilot-pauth-registered-vocabulary-002.md` - independent NO-GO requiring honest metadata/KB mutation classification.

REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d63-c8c1-73e0-91cf-06f12b168a57
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop Prime Builder bridge-revision worker; reasoning xhigh; approval policy never

# Revised Implementation Proposal - WI-5240 Exact PAUTH Registered-Vocabulary Candidate

bridge_kind: prime_proposal
Document: gtkb-wi5240-wi5236-pauth-registered-vocabulary
Version: 007
Responds to: bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-006.md
Supersedes stand-down: bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-005.md
Reviewed implementation authority: bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-002.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5240-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5240
Downstream Work Item: WI-5236
target_paths: ["groundtruth.db"]
kb_mutation_in_scope: true
Recommended commit type: fix(governance):

## Revision Claim

The two prerequisites named by the latest NO-GO are now terminal. WI-5329 is MemBase-resolved and `bridge/gtkb-wi5329-bounded-database-carrier-restoration-004.md` is `VERIFIED`; WI-5113 is MemBase-resolved and `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md` is `VERIFIED`. Prime therefore selects the NO-GO's permitted reconstruction path instead of filing another stand-down.

Implementation will reconstruct `HEAD:groundtruth.db` in an in-root disposable evidence directory, replay only the reviewed WI-5240 PAUTH version-2 correction through the canonical `gt projects authorize` writer, prove exactly one logical application-row delta, and emit a hash-locked binary patch for independent VERIFIED finalization. The current dirty `groundtruth.db` is never a candidate source.

This revision itself changes no database, source, test, configuration, Git, release, deployment, credential, dispatcher, lease, runtime, or external-system state. A new independent GO, matching claim, and implementation-start packet remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient.

`DELIB-202666201`, WI-5240, TEST-11394, the original proposal/GO, and the version-004 semantic review remain sufficient. Version 004 confirmed the PAUTH correction itself and rejected only carrier commingling; versions 005 and 006 parked the thread pending WI-5329 and WI-5113. This revision does not expand the test-only downstream authority or invent a new owner decision.

## Restored Baseline And Fail-Closed Boundary

The revision is bound to the committed carrier observed at filing:

- commit: `42a252ab57b5a203e9406b626c741d897e8fb196`
- `HEAD:groundtruth.db` Git blob: `7c7d9f1e9668f1868ecffef10b2001b8ebc6a449`
- committed-carrier size: `694726656` bytes
- committed-carrier SHA-256: `dc48bc89c4dec51feeae32857e0575267b3a182264f7f3797e0c1f758881d711`
- live dirty carrier observed only as a rejection boundary: Git blob `99f6c2cc77792503b6a95b0151f135d0af76dd81`, SHA-256 `b9295bad56544c7b1457d874d9f0fd78c66db1c11c7413f427a3da9e9f9fb56d`

Implementation must stop without a candidate if the committed blob or its size/SHA-256 differs, the baseline already contains target version 2, or any command would resolve `GT_DB_PATH` to the live root `groundtruth.db`. Live bytes and WAL/SHM sidecars are prohibited inputs; their hashes may be recorded only to prove exclusion.

## Exact Row-Scoped Candidate

The only permitted application-table delta is one new row in `project_authorizations` for version 2 of `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714` with:

- `project_id`: `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`
- `status`: `active`
- `authorization_name`: `WI-5236 dispatcher_runtime fixture drift repair`
- `owner_decision_deliberation_id`: `DELIB-202666201`
- `scope_summary`: `Bounded repair of current-HEAD platform_tests/scripts/test_dispatcher_runtime.py fixture/API expectations blocking WI-5222 and WI-5233 verification. Only test-file mutation is authorized. Source behavior changes, dispatcher runtime JSON edits, lease-file edits, groundtruth.db mutation outside this append-only PAUTH version, registry or routing changes, and unrelated worktree mutations remain prohibited.`
- `allowed_mutation_classes`: `["test"]`
- `forbidden_operations`: `["dispatcher_mutation","credential_lifecycle","destructive_cleanup","external_system_mutation","git_history_rewrite","production_deployment"]`
- `included_work_item_ids`: `["WI-5236"]`
- `included_spec_ids`: `["SPEC-CENTRALIZED-DISPATCH-SERVICE-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"]`
- excluded work items/specs, expiration, supersedes, and superseded-by: SQL `NULL`
- `changed_by`: `prime-builder/codex/A`
- `change_reason`: `WI-5240 GO: replace unregistered forbidden-operation labels with registered taxonomy vocabulary while preserving the bounded test-only scope`

Capture generated `rowid` and `changed_at` from the canonical writer and immutable readback, then publish a canonical-JSON SHA-256 over every persisted column. All pre-existing authorization rows must remain column-for-column equal. Every other application table must retain identical ordered-row hashes and counts. Only `sqlite_sequence` for `project_authorizations` may advance.

## Governed Reconstruction Commands

After GO, claim, and implementation-start authorization, use a unique directory under `.gtkb-state/bridge-revisions/evidence/wi5240/`:

```powershell
$Evidence = ".gtkb-state/bridge-revisions/evidence/wi5240/<utc-stamp>"
New-Item -ItemType Directory -Path $Evidence | Out-Null
git cat-file blob 7c7d9f1e9668f1868ecffef10b2001b8ebc6a449 > "$Evidence/baseline-groundtruth.db"
Copy-Item -LiteralPath "$Evidence/baseline-groundtruth.db" -Destination "$Evidence/candidate-groundtruth.db"
$env:GT_DB_PATH = (Resolve-Path "$Evidence/candidate-groundtruth.db").Path
$env:GT_PROJECT_ROOT = (Resolve-Path ".").Path
groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-GOOSE-HARNESS-ADOPTION --id PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714 --owner-decision DELIB-202666201 --name "WI-5236 dispatcher_runtime fixture drift repair" --scope "Bounded repair of current-HEAD platform_tests/scripts/test_dispatcher_runtime.py fixture/API expectations blocking WI-5222 and WI-5233 verification. Only test-file mutation is authorized. Source behavior changes, dispatcher runtime JSON edits, lease-file edits, groundtruth.db mutation outside this append-only PAUTH version, registry or routing changes, and unrelated worktree mutations remain prohibited." --allowed-mutation test --forbid dispatcher_mutation --forbid credential_lifecycle --forbid destructive_cleanup --forbid external_system_mutation --forbid git_history_rewrite --forbid production_deployment --include-work-item WI-5236 --include-spec SPEC-CENTRALIZED-DISPATCH-SERVICE-001 --include-spec DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 --changed-by prime-builder/codex/A --change-reason "WI-5240 GO: replace unregistered forbidden-operation labels with registered taxonomy vocabulary while preserving the bounded test-only scope" --json
groundtruth-kb\.venv\Scripts\gt.exe projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714 --json
Remove-Item Env:GT_DB_PATH
Remove-Item Env:GT_PROJECT_ROOT
```

Before replay, immutable sidecar-free baseline checks must return `quick_check = ok`, no foreign-key violations, and target max version `1`. Candidate and independently patch-applied round-trip must return the same integrity results and target max version `2` with the exact row above.

Create the binary patch in an isolated disposable Git repository inside the evidence directory, with the baseline committed there solely as patch-generation input and the candidate at relative path `groundtruth.db`. The patch must mention only `groundtruth.db`. Record SHA-256 and Git blob IDs for baseline, candidate, patch, and round-trip. Candidate and round-trip hashes must match exactly, and `git apply --binary --check` against the pinned baseline must pass. The real worktree database and real index remain untouched.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666201` - owner authority for the bounded WI-5236/WI-5240 repair.
- `bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-001.md` and `-002.md` - original proposal and independent GO.
- `bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-004.md` - confirms semantic correctness and requires an isolated carrier.
- `bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-006.md` - expressly permits this reconstruction after WI-5329 and WI-5113 land.
- `bridge/gtkb-wi5329-bounded-database-carrier-restoration-004.md` - VERIFIED committed-carrier restoration.
- `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md` - VERIFIED clean-finalizer prerequisite.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-006.md` - VERIFIED binary-patch finalizer capability.

## Owner Decisions / Input

`DELIB-202666201` remains the governing owner evidence. No new owner decision is required because this revision follows the exact reconstruction alternative in the latest NO-GO and preserves the approved test-only downstream boundary.

## Specification-Derived Verification Plan

| Requirement | Required evidence |
| --- | --- |
| Registered vocabulary | Candidate readback and taxonomy comparison show `test` and every forbidden operation are registered; TEST-11394 reaches the next gate without `unknown_forbidden_operation`. |
| Exact row ownership | Baseline/candidate ordered-row manifests show exactly one target version-2 authorization row and no other application-table delta. |
| Carrier evaluability | Baseline, candidate, and round-trip pass quick/foreign-key checks; candidate and round-trip hashes match. |
| Canonical-carrier nonauthority | Candidate derives only from pinned `HEAD:groundtruth.db`; current live database and sidecars are excluded and separately hash-reported. |
| Finalizer safety | Binary patch touches only `groundtruth.db`, applies to the pinned baseline, and focused finalizer atomicity tests pass without real-index mutation. |
| Bridge gates | Candidate and post-filing applicability/clause preflights pass; implementation report carries GO, claim, start, commands, hashes, readback, and focused test output. |

## Acceptance Criteria

- Exactly one WI-5240-owned PAUTH version-2 row is added to the pinned committed baseline.
- No unregistered mutation class or forbidden-operation label remains in the candidate row.
- All other application-table content is unchanged.
- Candidate, binary patch, and round-trip are exact and hash-locked.
- Live dirty database bytes and sidecars are neither read as candidate authority nor overwritten.
- Focused operation-time, implementation-authorization, and finalizer tests pass before independent verification.

## Risk And Rollback

The risk is commingling ambient database state or broadening WI-5236 authority. The baseline hash gate, exact one-row manifest, registered-vocabulary comparison, and isolated patch generation constrain both risks. Before finalization, rollback deletes only the disposable evidence directory. After append-only PAUTH finalization, correction requires a governed successor authorization version; historical rows must not be deleted.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

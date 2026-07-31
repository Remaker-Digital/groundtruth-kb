REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d63-c8c1-73e0-91cf-06f12b168a57
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop Prime Builder bridge-revision worker; reasoning xhigh; approval policy never

# Revised Implementation Proposal - WI-5237 Exact PAUTH Configuration-Coverage Candidate

bridge_kind: prime_proposal
Document: gtkb-wi5237-wi5229-pauth-configuration-coverage
Version: 009
Responds to: bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-008.md
Supersedes stand-down: bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-007.md
Reviewed implementation authority: bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5229
Repair Work Item: WI-5237
target_paths: ["groundtruth.db"]
kb_mutation_in_scope: true
Recommended commit type: fix(governance):

## Revision Claim

The two prerequisites named by the latest NO-GO are now terminal. WI-5329 is MemBase-resolved and `bridge/gtkb-wi5329-bounded-database-carrier-restoration-004.md` is `VERIFIED`; WI-5113 is MemBase-resolved and its successor `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md` is `VERIFIED`. Prime therefore requests fresh implementation authority for the NO-GO's reconstruction path.

Implementation will reconstruct `HEAD:groundtruth.db` in an in-root disposable evidence directory, replay only the already reviewed WI-5237 PAUTH version-2 append through the canonical `gt projects authorize` writer, prove exactly one logical application-row delta, and emit a hash-locked binary patch suitable for the VERIFIED disposable-index finalizer. The live dirty `groundtruth.db` is neither copied nor opened as candidate input.

This revision performs no database reconstruction itself. No source, test, configuration, database, Git index, commit, push, release, deployment, credential, dispatcher, lease, runtime, or external-system mutation is authorized before a new independent GO, matching claim, and implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient.

Existing authority is sufficient. `DELIB-202666199` authorized the bounded WI-5229 PAUTH and binary-finalizer scope; the prior GO accepted the configuration-class correction; versions 003 through 006 established the semantic correctness and durability requirement; versions 007 and 008 parked the thread only until WI-5329 and WI-5113 became terminal. No new owner decision or scope expansion is introduced.

## Restored Baseline And Fail-Closed Boundary

The revision is bound to the committed carrier observed at filing:

- commit: `42a252ab57b5a203e9406b626c741d897e8fb196`
- `HEAD:groundtruth.db` Git blob: `7c7d9f1e9668f1868ecffef10b2001b8ebc6a449`
- committed-carrier size: `694726656` bytes
- committed-carrier SHA-256: `dc48bc89c4dec51feeae32857e0575267b3a182264f7f3797e0c1f758881d711`
- live dirty carrier observed only as a rejection boundary: Git blob `99f6c2cc77792503b6a95b0151f135d0af76dd81`, SHA-256 `b9295bad56544c7b1457d874d9f0fd78c66db1c11c7413f427a3da9e9f9fb56d`

Implementation must fail closed without writing a candidate when `git ls-tree HEAD groundtruth.db` does not return blob `7c7d9f1e...`, the materialized baseline does not match all three committed-carrier values, or the baseline already contains version 2 for the target PAUTH. The live carrier may be hashed to demonstrate separation, but no byte from it, `groundtruth.db-wal`, or `groundtruth.db-shm` may enter the baseline, candidate, patch, readback, or round-trip artifact.

## Exact Row-Scoped Candidate

The only permitted application-table delta is one new row in `project_authorizations` for version 2 of `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714` with:

- `project_id`: `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`
- `status`: `active`
- `authorization_name`: `WI-5229 binary VERIFIED finalizer repair`
- `owner_decision_deliberation_id`: `DELIB-202666199`
- `allowed_mutation_classes`: `["bridge","configuration","metadata","governance_evidence","source","test"]`
- `forbidden_operations`: `["dispatcher_mutation","destructive_cleanup","credential_lifecycle","production_deployment","git_history_rewrite","external_system_mutation","git_push"]`
- `included_work_item_ids`: `["WI-5229"]`
- `included_spec_ids`: `["GOV-FILE-BRIDGE-AUTHORITY-001","DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001","GOV-DOCUMENT-AUTHOR-PROVENANCE-001","DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001","ADR-CODEX-HOOK-PARITY-FALLBACK-001"]`
- excluded work items/specs, expiration, supersedes, and superseded-by: SQL `NULL`
- `changed_by`: `prime-builder/codex/A`
- `change_reason`: `WI-5237: correct WI-5229 PAUTH allowed_mutation_classes after work_intent_acquire failed closed on verify-helper configuration paths.`
- `scope_summary`: the exact bounded scope from version 001, ending with `without replacing groundtruth.db or altering commit 08cbc017.`

The generated `rowid` and `changed_at` must be captured from the canonical writer output and immutable candidate readback. The implementation report must publish a canonical-JSON SHA-256 over every persisted column, including those generated fields. All pre-existing `project_authorizations` rows must compare column-for-column equal between baseline and candidate. Every other application table must have identical ordered-row hashes and row counts. Only the internal `sqlite_sequence` counter for `project_authorizations` may advance as a consequence of this insert.

## Governed Reconstruction Commands

After GO, claim, and implementation-start authorization, use a unique directory under `.gtkb-state/bridge-revisions/evidence/wi5237/` and execute this bounded sequence:

```powershell
$Evidence = ".gtkb-state/bridge-revisions/evidence/wi5237/<utc-stamp>"
New-Item -ItemType Directory -Path $Evidence | Out-Null
git cat-file blob 7c7d9f1e9668f1868ecffef10b2001b8ebc6a449 > "$Evidence/baseline-groundtruth.db"
Copy-Item -LiteralPath "$Evidence/baseline-groundtruth.db" -Destination "$Evidence/candidate-groundtruth.db"
$env:GT_DB_PATH = (Resolve-Path "$Evidence/candidate-groundtruth.db").Path
$env:GT_PROJECT_ROOT = (Resolve-Path ".").Path
groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --id PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714 --owner-decision DELIB-202666199 --name "WI-5229 binary VERIFIED finalizer repair" --scope "Bounded authorization for WI-5229 to file a bridge proposal and, only after independent Loyal Opposition GO plus matching work-intent claim and implementation-start packet, repair binary-aware reviewed hunk-patch support in PublishBridgeVerdict / VERIFIED finalization. Scope is limited to finalizer writer/helper parity source, verify-helper configuration copies, focused regression tests, and bridge/governance evidence needed to unblock WI-5139 VERIFIED finalization without replacing groundtruth.db or altering commit 08cbc017." --allowed-mutation bridge --allowed-mutation configuration --allowed-mutation metadata --allowed-mutation governance_evidence --allowed-mutation source --allowed-mutation test --forbid dispatcher_mutation --forbid destructive_cleanup --forbid credential_lifecycle --forbid production_deployment --forbid git_history_rewrite --forbid external_system_mutation --forbid git_push --include-work-item WI-5229 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 --include-spec GOV-DOCUMENT-AUTHOR-PROVENANCE-001 --include-spec DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 --include-spec ADR-CODEX-HOOK-PARITY-FALLBACK-001 --changed-by prime-builder/codex/A --change-reason "WI-5237: correct WI-5229 PAUTH allowed_mutation_classes after work_intent_acquire failed closed on verify-helper configuration paths." --json
groundtruth-kb\.venv\Scripts\gt.exe projects show-authorization PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5229-BINARY-VERIFIED-FINALIZER-20260714 --json
Remove-Item Env:GT_DB_PATH
Remove-Item Env:GT_PROJECT_ROOT
```

Before the writer command, an immutable read of the baseline must prove `PRAGMA quick_check = ok`, an empty `PRAGMA foreign_key_check`, and target max version `1`. After the command, immutable sidecar-free reads of candidate and a patch-applied round-trip database must prove the same integrity results and target max version `2` with the exact row above.

Generate a `git diff --binary` patch in an isolated disposable Git repository rooted inside the evidence directory, with the baseline committed there only as patch-generation input and the candidate at relative path `groundtruth.db`. The patch must touch only `groundtruth.db`. Hash and report the baseline, candidate, patch, and independently patch-applied round-trip using both SHA-256 and Git blob IDs. The candidate and round-trip hashes must be identical; `git apply --binary --check` against the committed baseline must pass. No command may address the real index or overwrite the live worktree database.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666199` - owner authorization for the WI-5229 PAUTH and binary VERIFIED finalizer scope.
- `bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-001.md` and `-002.md` - original proposal and GO.
- `bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-006.md` - requires a stable exact WI-5237-only candidate.
- `bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-008.md` - permits this reconstruction after WI-5329 and WI-5113 land.
- `bridge/gtkb-wi5329-bounded-database-carrier-restoration-004.md` - VERIFIED committed-carrier restoration.
- `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md` - VERIFIED clean-finalizer prerequisite.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-006.md` - VERIFIED binary-patch finalizer capability.

## Owner Decisions / Input

`DELIB-202666199` remains the applicable owner decision. No new owner decision is required because this revision selects the exact reconstruction alternative already offered by the NO-GO after both named prerequisites became VERIFIED.

## Specification-Derived Verification Plan

| Requirement | Required evidence |
| --- | --- |
| PAUTH envelope and operation-time enforcement | Exact canonical-writer output/readback, taxonomy-clean values, and focused `test_project_authorization_operation_time_enforcement.py`. |
| Exact row ownership | Baseline/candidate ordered-row manifests prove one added target version-2 row and no other application-table delta. |
| Carrier evaluability | Baseline, candidate, and round-trip pass SQLite quick/foreign-key checks; candidate and round-trip hashes match. |
| Canonical-carrier nonauthority | Candidate begins only from hash-locked `HEAD:groundtruth.db`; live dirty carrier and sidecars are excluded and separately hash-reported. |
| VERIFIED finalizer safety | Binary patch touches only `groundtruth.db`, applies to the pinned baseline, and passes focused atomicity tests without touching the real index. |
| Bridge and authorization gates | Candidate and live applicability/clause preflights pass; implementation report cites GO, claim, start packet, hashes, commands, and observed results. |

## Acceptance Criteria

- Exactly one WI-5237-owned PAUTH version-2 row is added to the pinned committed baseline.
- All other application-table content is unchanged.
- Candidate, binary patch, and patch-applied round-trip are exact and hash-locked.
- The live dirty database and sidecars are never candidate inputs and are never overwritten.
- Focused PAUTH and finalizer tests pass, and the report reaches independent Loyal Opposition verification before any finalization.

## Risk And Rollback

The principal risk is silently absorbing ambient database state. Hash-locking the committed baseline, comparing every application table, and constructing the binary patch in an isolated evidence repository make that impossible without a failed gate. Before terminal finalization, rollback is deletion of the disposable evidence directory only. PAUTH history is append-only; after finalization, correction requires a separately governed successor version, never row deletion or live-carrier replacement.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

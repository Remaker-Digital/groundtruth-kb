NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; activity envelope ::open build; WI-6183 governed two-file implementation
author_metadata_source: explicit_interactive_session_metadata
session_init_keyword: ::init gtkb pb
activity_init_keyword: ::open build

# WI-6183 implementation report — copied-index PAUTH read snapshot

bridge_kind: implementation_report
Document: gtkb-wi6183-protected-commit-pauth-read-snapshot
Version: 003
Date: 2026-08-11 UTC
Responds to: bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-002.md
Approved proposal: bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-001.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6183
related_work_items: ["WI-5950", "WI-6140"]
target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source,test
kb_mutation_in_scope: false
database_registry_or_index_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
requires_review: true
requires_verification: true
Recommended commit type: fix

---

## Implementation Claim

The approved two-file repair is complete. Protected-commit transaction audits now retain current PAUTH read authority without copying, whole-file hashing, staging, trusting, or mutating the canonical `groundtruth.db`. For a PAUTH-bearing transaction-local terminal audit, one invocation-local compact SQLite projection is derived from exactly four current authority relations, entered as an ordinary non-exempt copied-root ledger object, consumed by both the bridge-compliance subprocess and direct operation-time PAUTH validation, checked for relevant logical currentness, and removed on every exit.

The copied Git index remains authoritative for prospective source, taxonomy, configuration, proposal, report, verdict, and target bytes. Operation-time PAUTH remains independently re-evaluated and packet-hash material. Missing, redirected, incomplete, stale, revoked, replaced, tampered, oversized, mismatched, sidecar-producing, or uncleanable authority state fails closed. Non-PAUTH transactions do not open or construct the projection.

This implementation performs no KB, MemBase, or groundtruth.db mutation. It changes no PAUTH, receipt, registry, bridge-publication, real-index, dispatcher, legacy TAFE, or Git-history state.

## Requirement Sufficiency

Existing requirements sufficient.

The approved proposal, independent GO, owner deliberation, active PAUTH v2, exact two-target schema-v3 implementation packet, and specification-derived matrix fully define this repair. No new behavior, target, authority class, waiver, database schema, packet schema, or user-visible workflow is required. WI-6140 remains a distinct source-horizon carrier and must fresh-read this terminal baseline before it resumes.

## Authorization And Start Evidence

- Proposal: `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-001.md`, SHA-256 `0F3DC88435321AF73208C33FCC62D157980CC707B322CF64E6D452FA4EAEA041`, 36,064 bytes; publication capability row 2178 consumed.
- Independent GO: `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-002.md`, SHA-256 `5C77F1C1872929EBBFC863E1D99C12B148E7E2F85A8FBF7A634DE871D27BE1EA`, 9,667 bytes; publication capability row 2179 consumed; revision `SOTREV-CF781FC09110447BBFF7587FE69572AE`.
- GO implementation claim: row 38060, `claim_kind=go_implementation`, acting role `prime-builder`, session `019fe0e5-4e93-7280-9778-8d6738c9626d`, project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.
- Finalized schema-v3 implementation-start packet: `sha256:9acf0329b00fb461c4a12cc1b8abb548556441fcd1e17a96cb7a09985760a1fd`; pre-start packet `sha256:695b0ccd485c1793f07298486aff68052ea342bee8d5a1d38500219ae88ff4b3`; bound to proposal v001, GO v002, PAUTH v2, this Prime Builder session, and exactly the two declared targets.
- Owner decision: `DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR`, row 14281, content hash `adb613c6e92f393d189e549420d2e24fa516e0edddd113f06acc576f9dd8d6b4`.

## Implemented Design

1. Canonical PAUTH metadata detection now uses the shared metadata extractor and accepted `Project Authorization` key grammar, including bullets, bold labels, backticks, and the `ID` spelling. No parallel narrow parser determines projection eligibility.
2. The live source is exactly `<project-root>/groundtruth.db`, opened by SQLite URI in read-only/query-only mode. Source identity excludes file size and page-layout hashes so unrelated database churn is not a false denial; link/reparse/redirection and replacement races fail closed.
3. The compact projection contains exactly `current_specifications`, `current_project_authorizations`, `current_projects`, and `current_project_work_item_memberships`, with a closed selected schema, deterministic typed-row encodings, row counts, and relation digests. No fifth or historical relation is copied.
4. The projection is exclusive-created with no-follow/no-replace binding. SQLite journal/WAL/SHM names are occupied by retained directory guards during both consumers. Descriptor-bound identity and permissions prevent pathname-swap mutation; cleanup never chmod-follows a link.
5. The projection replaces only the oversized content-exempt `groundtruth.db` entry in the effective derived ledger. It is ordinary, hashed, size-bound, identity-bound, logically described, and included in the aggregate `MAX_TREE_BYTES` limit. The original copied-index ledger is unchanged and reverified after cleanup.
6. One projection lifetime wraps both `_run_snapshot_compliance_audit` and direct finalized-packet PAUTH validation. Both consume the same effective copied-root database; neither falls back to a live-root or precomputed verdict.
7. Relevant four-relation drift, source replacement, schema change, projection tamper, sidecar creation, consumer mismatch, timeout, exception, or cleanup failure rejects. Unrelated-table churn may proceed when the consumed logical authority is identical.
8. PAUTH-free transaction evidence follows the prior route and proves the projection opener is never called.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v2
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001` v3
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations And Dependency Evidence

- `DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR` — exact owner approval for this bounded two-file repair before WI-5950, with no bypass authority.
- `bridge/gtkb-wi5950-strict-terminal-recovery-016.md` — immutable evidence of the copied-index PAUTH read-context failure; this carrier does not alter WI-5950 bytes or lifecycle state.
- `bridge/gtkb-wi6140-source-horizon-cycle-breaker-002.md` — independent NO-GO establishes that WI-6140 must rebase after WI-6183 terminalizes. The WI-6183 integration test intentionally reaches its separate stale-packet boundary after proving both PAUTH consumers succeed; that synthetic stale packet is not a WI-6183 defect or a combined-finalization requirement.

## Specification-Derived Verification

| Requirement / invariant | Executed evidence | Result |
| --- | --- | --- |
| Current operation-time PAUTH in copied-root audit | Real transaction-local integration invokes the real compliance audit and real PAUTH validator through the same effective root; live and projected applicability packet material agrees | PASS |
| Exact four-relation projection | Projection inspection asserts exact tables, declared columns, typed values, counts, relation digests, application identity, and no unrelated relation | PASS |
| Revocation and relevant currentness | Authority relation drift between construction and consumption rejects; unrelated-table churn with identical four-relation observations is allowed | PASS |
| Canonical metadata grammar | Plain, `ID`, bulleted, bold, and backticked PAUTH metadata forms all select the same projection route | PASS |
| Destination/sidecar containment | Exclusive destination, symlink/reparse injection, DB and every journal/WAL/SHM sidecar, no-replace guards, and identity changes are exercised | PASS |
| Fail-closed schema and authority | Missing relation/schema, unreadable source, projection tamper, consumer mismatch, raw I/O error, and cleanup failure reject deterministically | PASS |
| Oversized-blob and aggregate limits | Canonical oversized DB remains omitted; compact projection is an ordinary effective-ledger entry and total derived tree limit is enforced | PASS |
| Non-PAUTH fast path | Transaction test makes projection construction fatal if called and completes without calling it | PASS |
| Regression breadth | Full checker module includes the 176-test pre-change baseline plus 17 WI-6183 tests; adjacent applicability/implementation/operation-time suites pass | PASS |
| Static and worktree hygiene | Ruff lint/format, compile, diff check, exact target hashes, HEAD, real-index SHA, staged-entry census, and registry hashes rechecked | PASS |

## Commands Run And Results

1. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short -k wi6183`
   - `17 passed, 176 deselected, 1 warning in 3.51s`.
2. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short`
   - `193 passed, 1 warning in 78.71s`.
3. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short`
   - `230 passed, 1 warning in 39.10s` (final independent rerun; only the pre-existing unknown `asyncio_mode` warning).
4. `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS: `All checks passed!`
5. `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS: `2 files already formatted`.
6. `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS.
7. `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS.

## Exact Files Changed

| Path | Authorized preimage SHA-256 / size | Final SHA-256 / size | Diff |
| --- | --- | --- | --- |
| `scripts/check_protected_commit_authorization.py` | `978CE40C716F46DA08FFEE0F2806CAEA85660C74762CF897229DDB77C40B8B57` / 132,462 B | `DFF2168D727367DAA0015F771397C0077B336EED7A8372B835CD0AD16DC05B60` / 163,412 B | `+659/-22` |
| `platform_tests/scripts/test_check_protected_commit_authorization.py` | `EAC5B1A586514626E42805417B5A80B2DDC8440BD19469DF1CA421967C67E6DE` / 160,292 B | `031DA5ED050EBE063693DE9208DA232A05800984E270436222BA2995D44A7745` / 187,863 B | `+711/-0` |

Total: 1,370 insertions, 22 deletions. No other path was edited by this implementation lane. Both targets remain unstaged for independent scoped finalization.

## Acceptance Criteria Status

- [x] PAUTH-bearing copied-index audit uses one exact four-relation read-only projection for both consumers.
- [x] Relevant authority drift, source replacement, schema gaps, projection tamper, consumer mismatch, and cleanup failure reject.
- [x] Operation-time PAUTH remains re-evaluated and packet-hash material; no precomputed verdict or waiver exists.
- [x] PAUTH-free audits create no projection.
- [x] Canonical `groundtruth.db` is not copied wholesale, whole-file hashed, staged, committed, mutated, redirected, or linked.
- [x] Derived projection is ordinary-ledger protected, exact-relation bounded, sidecar guarded, aggregate-size bounded, and removed on every exit.
- [x] Prospective Git/taxonomy/candidate authority, oversized-blob omission, stale-packet rejection, and fail-closed behavior remain intact.
- [x] Full 193-test checker module, 230 adjacent tests, 17 focused tests, Ruff, formatting, compilation, and diff checks pass.
- [x] WI-6183 remained isolated from WI-6140; WI-6140 must rebase after this carrier's terminal commit.
- [x] Real index, foreign registry bytes, canonical database, bridge files, dispatcher/TAFE state, and Git history were not mutated during implementation/report preparation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR; WI-6183; bridge v001-v003; schema-v3 packet sha256:9acf0329b00fb461c4a12cc1b8abb548556441fcd1e17a96cb7a09985760a1fd",
  "canonical_authority": "Prospective Git inputs remain copied-index authoritative; current PAUTH authority comes only from a bounded read-only projection of the canonical live database's four evaluator relations.",
  "primary_route": "Approved proposal, independent GO, exact two-target implementation, complete report, and independent atomic VERIFIED using the scoped finalizer.",
  "before_behavior": "The copied-root compliance audit omitted groundtruth.db and converted a live allowed PAUTH decision into evaluation_error.",
  "after_behavior": "Both PAUTH consumers share one ledgered compact authority projection while every existing prospective-source and fail-closed boundary remains enforced.",
  "self_descriptive_naming": "The new helpers and tests explicitly name PAUTH read snapshot, projection, authority observation, sidecar guards, currentness, and cleanup responsibilities.",
  "obsolete_guidance_disposition": "The assumption that copied-index PAUTH evaluation needs no database read context is rejected; historical WI-5950 and WI-6140 evidence remains immutable.",
  "history_preservation": "Bridge versions, deliberations, PAUTH versions, receipts, database history, registry state, and Git history remain append-only; the projection is transient derived evidence.",
  "baseline": {
    "checker_tests": "176 pre-change; 193 final",
    "authorized_targets": "exactly two",
    "real_index": "unchanged through Prime implementation/report; only the two pre-existing registry TOMLs are staged",
    "legacy_tafe": "disabled"
  },
  "expected_result": {
    "pauth_audit": "Stable live and projected operation-time PAUTH material agree.",
    "denial": "Revocation, relevant drift, tamper, redirect, mismatch, or cleanup failure rejects.",
    "containment": "No database, registry, non-cohort index, dispatcher, TAFE, or foreign worktree mutation."
  },
  "rollback": {
    "instructions": "Before terminal verification, restore only the two WI-6183 target diffs. After VERIFIED, use a separately governed inverse commit.",
    "verification": "Rerun the 193-test checker module, 230 adjacent tests, static gates, exact hashes, and index/foreign-entry census."
  },
  "hard_invariants": [
    "Operation-time PAUTH remains independently evaluated and packet-hash material.",
    "The canonical database is never copied wholesale, whole-file hashed, staged, committed, or mutated.",
    "Only the exact four approved current authority relations enter the derived projection.",
    "Prospective source and taxonomy remain copied-index authoritative.",
    "All non-cohort index entries, especially the two foreign registry entries, remain unchanged.",
    "Legacy TAFE remains disabled."
  ],
  "fail_closed_conditions": [
    "Missing, unreadable, redirected, replaced, incomplete, revoked, or drifting canonical authority.",
    "Projection or sidecar tamper, schema mismatch, consumer mismatch, aggregate-size breach, or cleanup failure.",
    "Any attempt to trust precomputed PAUTH, remove packet binding, mutate an undeclared target, absorb WI-6140 bytes, or enable legacy TAFE."
  ],
  "essential_context_preservation": "The implementation preserves the owner-approved exact two-target boundary, copied-index authority, exact four-relation projection, relevant logical currentness, oversized-blob omission, sidecar and cleanup hardening, full regression matrix, WI-6140 sequencing, foreign-index preservation, and disabled-TAFE boundary."
}
```

## Finalization Manifest And Index Boundary

Independent Loyal Opposition should atomically include exactly:

- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-001.md`
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-002.md`
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-003.md`
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

The finalizer creates the terminal v004 verdict. No hunk patch is required: both implementation targets are full-file, WI-6183-owned changes from clean HEAD preimages. The disposable-index transaction may realign only the exact committed cohort to the new HEAD. Every non-cohort real-index entry must remain entry-identical; specifically both staged registry TOMLs must remain mode 100644, stage 0, blob `d4a1aca0e15172acad63f218f32c9814b2055677` and must remain the only cached-diff paths. Whole-index SHA is expected to change after successful commit realignment and is not an acceptance invariant.

Exclude all WI-6140 patches/targets, WI-5950 bytes, `groundtruth.db`, registry worktree bytes, runtime packets/session files, foreign bridge threads, dispatcher state, and legacy TAFE state.

## Risk And Rollback

Residual risk is concentrated in SQLite cross-platform file identity and cleanup behavior. The implementation bounds it with exclusive no-follow creation, retained handles, no-replace guards, exact identity checks, sidecar occupancy, ordinary ledger verification, relation-level currentness, and terminal cleanup failure. Windows and POSIX branches are covered by deterministic unit tests where platform behavior permits; independent verification should rerun the full matrix on the final candidate.

Before terminal verification, rollback restores only the two exact target preimages and reruns the complete matrix. After terminal verification, rollback requires a separately governed inverse commit. No rollback may rewrite bridge history, receipts, PAUTH, the database, registry state, real-index foreign entries, or Git history.

## Loyal Opposition Request

Fresh-read the complete v001-v003 chain, exact target bytes, consumed publication receipts, schema-v3 start packet, and final candidate gates. Rerun live pre-verdict executability after this report is receipt-complete. If every mapped invariant remains green, issue terminal `VERIFIED` only through the atomic scoped finalizer over the exact five-path manifest above; otherwise return a findings-specific `NO-GO` without modifying implementation bytes.

---

When you are finished working, close your session envelope by invoking ::wrap.

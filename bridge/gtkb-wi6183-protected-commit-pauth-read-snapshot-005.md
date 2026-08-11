REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; activity envelope ::open build; WI-6183 governed report resumption after independent NO-GO
author_metadata_source: explicit_interactive_session_metadata
session_init_keyword: ::init gtkb pb
activity_init_keyword: ::open build

# WI-6183 REVISED implementation report — copied-index PAUTH read snapshot

bridge_kind: implementation_report
Document: gtkb-wi6183-protected-commit-pauth-read-snapshot
Version: 005
Date: 2026-08-11 UTC
Responds to: bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-004.md
Approved proposal: bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-001.md
Controlling GO: bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-002.md
Prior implementation report: bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-003.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6183
related_work_items: ["WI-5950", "WI-6140"]
target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source,test
kb_mutation_in_scope: false
database_mutation_in_scope: false
registry_mutation_in_scope: false
database_registry_or_index_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
requires_review: true
requires_verification: true
Recommended commit type: fix

---

## Implementation Claim

The exact two-file WI-6183 repair is complete and the two findings in independent NO-GO v004 are corrected. Protected-commit transaction audits retain current PAUTH read authority without copying, whole-file hashing, staging, trusting, or mutating canonical `groundtruth.db`. One invocation-local compact SQLite projection of exactly four current authority relations is ledgered as ordinary derived evidence and consumed by both the copied-root compliance audit and direct operation-time PAUTH validation. The projection is checked for relevant logical currentness and removed on every exit.

The copied Git index remains authoritative for prospective source, taxonomy, configuration, proposal, report, verdict, and target bytes. Operation-time PAUTH remains independently re-evaluated and packet-hash material. Missing, redirected, incomplete, stale, revoked, replaced, tampered, oversized, mismatched, sidecar-producing, or uncleanable authority fails closed. Non-PAUTH transactions never open the projection.

This proposal performs no KB, MemBase, or groundtruth.db mutation. It performs no PAUTH, receipt, registry, bridge-publication, real-index, dispatcher, legacy TAFE, or Git-history mutation. Legacy TAFE remains disabled and is neither enabled, invoked, started, restarted, reconfigured, recovered, nor depended on by this carrier.

Every generated and governed artifact remains in-root under `E:/GT-KB`; the receipt-complete report will reside under `E:/GT-KB/bridge`, and no artifact outside the mandatory project root is an input, output, or dependency.

## Requirement Sufficiency

Existing requirements sufficient.

The approved proposal v001, independent GO v002, owner deliberation, active PAUTH v2, exact two-target schema-v3 resumption packet, independent NO-GO v004, and expanded specification-derived matrix fully define this correction. No new target, behavior, authority class, waiver, database schema, packet schema, or public workflow is required. WI-6140 remains a separate five-path carrier and follows the independently terminal WI-6183 baseline; it is not a prerequisite for WI-6183 finalization.

## Findings Addressed

### F1 — Corrected transaction-fixture attribution

V004 correctly stopped closure because the former transaction fixture returned `evidence is None` with a stale packet diagnostic. Fresh reproduction proved that result was fixture-derived, not a production dependency on WI-6140. The former fixture copied an incomplete evaluator package and did not give fixture PAUTH the bridge mutation class. Production `_run_snapshot_compliance_audit` quarantines the prospective verdict under `.gtkb-state` before recomputing applicability and restores it afterward, so the operative proposal/report horizon remains stable.

The corrected test prepares the candidate through the copied-root authority path, copies the complete `groundtruth_kb.governance` evaluator package, and gives fixture PAUTH the exact `bridge`, `source`, and `test` classes used by the transaction. It runs the real compliance audit and real direct PAUTH validator through recording wrappers against one effective snapshot. The result now asserts `evidence is not None`, the evidence bridge id is exact, `errors == []`, both consumers use the same effective root, and the projection plus SQLite sidecars are absent afterward. An independent unmocked replay of `_load_transaction_verified_evidence` and full `evaluate(root)` also returned accepted evidence with zero findings.

No WI-6140 source, test, patch, or bridge byte was absorbed. WI-6140 remains the next serialized carrier under the owner's bounded inversion authority, but no longer blocks WI-6183 terminal verification.

### F2 — Completed fail-closed matrix

The focused WI-6183 selection expanded from 17 to 59 cases. Parameterized tests now exercise every v004 line 206-210 class: unavailable/unreadable/locked/malformed/incomplete canonical authority; canonical-source linklike, replacement, nested-root, configuration, environment, and caller-substitution attacks; individual derived-ledger and logical-evidence tamper fields; producer/consumer mismatches; and cleanup after denial, exception, timeout, and outer exception. Every rejecting case binds an exact diagnostic and verifies that `groundtruth.db`, `-journal`, `-wal`, and `-shm` artifacts are absent afterward. The environment override is intentionally nonoperative and unable to redirect canonical authority; it is not misreported as a denial.

## Owner Decisions / Input

- `DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR`, row 14281, content hash `adb613c6e92f393d189e549420d2e24fa516e0edddd113f06acc576f9dd8d6b4` — exact owner approval for this governed two-file PAUTH snapshot repair before WI-5950, preserving oversized-blob omission and fail-closed behavior with no bypass authority.
- `DELIB-20260811-WI6140-SOURCE-HORIZON-BOUNDED-DEPENDENCY-INVERSION`, row 14282, content hash `d1357c38af43e1bf20e4007c19e348d29159369e44edcdd0d8da18258b44212c` — separate authority for the clean WI-6140 carrier after WI-6183 and before WI-5950.

No additional owner decision is required for independent WI-6183 verification.

## Authorization And Resumption Evidence

- Proposal v001: SHA-256 `0F3DC88435321AF73208C33FCC62D157980CC707B322CF64E6D452FA4EAEA041`, 36,064 bytes; capability row 2178 consumed.
- Independent GO v002: SHA-256 `5C77F1C1872929EBBFC863E1D99C12B148E7E2F85A8FBF7A634DE871D27BE1EA`, 9,667 bytes; row 2179 consumed; revision `SOTREV-CF781FC09110447BBFF7587FE69572AE`.
- Prior report v003: SHA-256 `E4C50486D70481F718942165DF03C04ED0C009B7BB2AB1905C245B66E05AA0BE`, 20,082 bytes; row 2180 consumed; revision `SOTREV-953332F87A9E4B06BC5525AF88CB4B2B`.
- Independent NO-GO v004: SHA-256 `72194965F2DD991FE4A674E7E58DE893750FAF56BED14C4E2586F6435A05D8FD`, 25,584 bytes; row 2181 consumed; revision `SOTREV-03079E84CD2D4E02A3011DC7CA167FF0`.
- Resumption claim: row 38062, acquired `2026-08-11T16:40:04Z`, `claim_kind=draft`, acting role `prime-builder`, session `019fe0e5-4e93-7280-9778-8d6738c9626d`, project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`; renewed under the same session and scope.
- Final schema-v3 resumption packet: `sha256:ad18edf8edeec82097d128560c2494d57ac7df7d8dc43eb3600276762f33e912`; pre-start `sha256:b3b840a09bad9d5cafdb16bd3a08bd0f9ad182d032adc04313eae22cae1a7dc2`; created `2026-08-11T16:41:38Z`, expires `2026-08-11T18:41:38Z`; bound to v001/v002, report v003, remediated v004, PAUTH v2, this PB session, and exactly the two targets.
- Both exact targets independently validate as authorized under the active packet.

## Exact Candidate And Boundary Readback

| Path | Authorized preimage SHA-256 / size | Final SHA-256 / size | Diff |
| --- | --- | --- | --- |
| `scripts/check_protected_commit_authorization.py` | `978CE40C716F46DA08FFEE0F2806CAEA85660C74762CF897229DDB77C40B8B57` / 132,462 B | `DFF2168D727367DAA0015F771397C0077B336EED7A8372B835CD0AD16DC05B60` / 163,412 B | `+659/-22` |
| `platform_tests/scripts/test_check_protected_commit_authorization.py` | `EAC5B1A586514626E42805417B5A80B2DDC8440BD19469DF1CA421967C67E6DE` / 160,292 B | `C6D97B0EEAB6FB39FA45C458E216290C211A9B0C8DD9EBB5AC67254F091F6E17` / 208,419 B | `+1216/-0` |

The v004 correction changed only the declared test target; the checker source remained byte-identical to v003. Total candidate delta from HEAD is 1,875 insertions and 22 deletions across the exact two targets. Both remain unstaged.

HEAD remained `de467cbc93bbad9f8d826ffd9fa96733f76c504a`. The real index SHA-256 remained `B8E7BB45F3526EBBA4FF586879B4890706F95526A666F45F0083936110DC4791` through Prime implementation and report preparation. The only cached paths remain the two foreign registry TOMLs, each mode 100644, stage 0, blob `d4a1aca0e15172acad63f218f32c9814b2055677`. No registry or foreign worktree byte was adopted.

## Implemented Design

1. Canonical PAUTH metadata detection uses the shared metadata extractor and accepted `Project Authorization` key grammar, including bullets, bold labels, backticks, and `ID` spelling.
2. Canonical live authority is exactly the project root's `groundtruth.db`, opened by SQLite URI read-only/query-only. Source identity excludes size and whole-file/page-layout hashes so unrelated database churn is not a false denial; redirection, reparse, replacement, and relevant logical drift fail closed.
3. The compact projection contains exactly `current_specifications`, `current_project_authorizations`, `current_projects`, and `current_project_work_item_memberships`, with closed selected schemas, deterministic typed-row encodings, counts, and relation digests.
4. Projection creation is exclusive/no-follow/no-replace. Retained destination and journal/WAL/SHM guards cover both consumers; cleanup never chmod-follows a link.
5. Only the oversized content-exempt `groundtruth.db` ledger entry is replaced in the effective derived ledger. The compact file is ordinary, hashed, identity-bound, logically described, and included in `MAX_TREE_BYTES`; the original copied-index ledger remains unchanged and is reverified after cleanup.
6. One projection lifetime wraps `_run_snapshot_compliance_audit` and finalized-packet PAUTH validation. Both consume the same effective copied-root authority with no live-root or packet-captured fallback.
7. Relevant relation drift, source replacement, schema change, projection tamper, sidecar creation, consumer mismatch, timeout, exception, or cleanup failure rejects. Unrelated-table churn passes only when the four consumed relations remain logically identical.
8. PAUTH-free transaction evidence follows the existing route and mechanically proves the projection opener is not called.

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

- `DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR` — exact owner approval and WI-6183 authority.
- `bridge/gtkb-wi5950-strict-terminal-recovery-016.md` — immutable evidence of copied-index PAUTH read-context loss; WI-6183 does not alter WI-5950 bytes or lifecycle state.
- `bridge/gtkb-wi6140-source-horizon-cycle-breaker-002.md` — independent NO-GO remains immutable history. Its former WI-6183 prerequisite conclusion relied on the old reduced fixture; the corrected production-faithful transaction test proves WI-6183 can terminalize independently. WI-6140 still follows this commit and must rebase its shared test hunk.

## Specification-Derived Verification

| Requirement / invariant | Executed evidence | Result |
| --- | --- | --- |
| Current operation-time PAUTH | Production-faithful transaction fixture runs real compliance and direct PAUTH consumers through one effective root; independent unmocked replay also accepts | PASS |
| Exact four-relation projection | Table/schema/type/count/digest/application identity assertions | PASS |
| Revocation and currentness | Revoked authorization, inactive project, missing membership, specification drift, four snapshot boundaries, and unrelated-table churn | PASS |
| Canonical metadata grammar | Plain, `ID`, bulleted, bold, and backticked metadata forms | PASS |
| Canonical source binding | Missing, unreadable, locked, malformed, incomplete, linklike, replacement, nested-root, configuration, environment, and caller-substitution cases | PASS |
| Ledger integrity | Path, file hash, size, source identity, schema digest, row count, typed-row digest, and construction version tamper | PASS |
| Consumer binding | Root, relation allowlist, schema, digest, and construction version mismatches | PASS |
| Cleanup on every exit | Denial, exception, timeout, outer exception, explicit cleanup failure, sidecar injection, and transaction-level cleanup matrix | PASS |
| Oversized/aggregate limits | Canonical large DB stays omitted; compact projection is ordinary-ledger and effective tree limit is enforced | PASS |
| Non-PAUTH fast path | Projection call is made fatal and remains uncalled | PASS |
| Regression and hygiene | 59 focused, 235 full checker, 230 adjacent, Ruff, format, compile, diff, target authorization, HEAD/index census | PASS |

## F2 Adversarial Coverage Matrix

| V004 obligation | Mechanical evidence |
| --- | --- |
| Unreadable, locked, malformed source | `test_wi6183_canonical_source_failures_deny_and_clean[unreadable|locked|malformed]`; also missing and schema-incomplete |
| Source symlink/junction/reparse, replacement, nested-root, environment/configuration override, caller substitution | `test_wi6183_canonical_source_binding_attacks_cannot_redirect_projection[...]`, eight parameter nodes |
| Ledger path/hash/size/source identity/schema/count/typed digest/construction version | `test_wi6183_derived_ledger_tamper_denies_and_cleans[...]`, eight nodes |
| Consumer root/allowlist/schema/digest/version | `test_wi6183_producer_consumer_mismatch_denies_without_fallback[...]`, five nodes |
| Cleanup after evaluator denial, exception, timeout, outer exception | `test_wi6183_transaction_consumer_failures_clean_projection_and_sidecars[...]`, four nodes, plus helper-level exit coverage |

Linklike source variants share the production `_path_is_linklike` denial predicate so the cross-platform test exercises the common fail-closed branch without requiring privileged creation of every Windows object type. The environment-variable case proves the hostile path is ignored and cannot redirect canonical authority.

## Commands Run And Observed Results

1. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short -k wi6183`
   - PASS: `59 passed, 176 deselected in 14.41s`.
2. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short`
   - PASS: `235 passed in 96.08s`.
3. `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short`
   - PASS: `230 passed in 37.97s`.
4. `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS: `All checks passed!`.
5. `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS: `2 files already formatted`.
6. In-memory compilation of both exact targets with `compile(..., 'exec')`
   - PASS; no `__pycache__` or `.pyc` write.
7. `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS.
8. `implementation_authorization.py validate --target scripts/check_protected_commit_authorization.py` and `implementation_authorization.py validate --target platform_tests/scripts/test_check_protected_commit_authorization.py`
   - PASS: both exact targets authorized.

The only pytest warning is the pre-existing unknown `asyncio_mode` configuration warning; it is unrelated to WI-6183.

## Pre-Filing Candidate Gates

The completed LF-normalized first-pass draft was 26,267 bytes, SHA-256 `950DBD966C103AFDC4D18DF48105880E620C65F56418755DC5B368DEEF26D227`. Candidate-aware applicability passed with packet `sha256:74fb0cb624fb4ae35cebbb81e6cad1245f00bc045cd3150687c9c73b01a42548`, source-content hash `sha256:950dbd966c103afdc4d18df48105880e620c65f56418755dc5b368deef26d227`, missing required/advisory lists empty, blocking errors empty, and PAUTH v2 finalization operations allowed. The clause gate evaluated five clauses as four `must_apply`, one `may_apply`, and zero gaps. Embedded-evidence/root-boundary verification passed with zero failures.

This outcome-only paragraph changes the draft bytes, so all three candidate-aware gates must be rerun on the unchanged final bytes immediately before the single governed writer call. The final packet/source hash is deliberately returned as external filing evidence rather than embedded self-referentially. No pre-publication live executability claim is made because `pre_verdict_executability_check.py` has no pending-content mode. Independent Loyal Opposition must rerun live executability after v005 is receipt-complete and bind that result before verdict.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR; WI-6183; bridge v001-v005; schema-v3 packet sha256:ad18edf8edeec82097d128560c2494d57ac7df7d8dc43eb3600276762f33e912",
  "canonical_authority": "Prospective Git inputs remain copied-index authoritative; current PAUTH authority comes only from a bounded read-only projection of the canonical live database's four evaluator relations.",
  "primary_route": "Approved proposal, independent GO, exact two-target implementation and correction, receipt-complete REVISED report, and independent atomic VERIFIED using the scoped finalizer.",
  "before_behavior": "The copied-root compliance audit omitted groundtruth.db and converted a live allowed PAUTH decision into evaluation_error.",
  "after_behavior": "Both PAUTH consumers share one ledgered compact authority projection while every prospective-source and fail-closed boundary remains enforced.",
  "self_descriptive_naming": "Helpers and tests name PAUTH read snapshot, projection, authority observation, sidecar guards, currentness, consumer binding, and cleanup responsibilities.",
  "obsolete_guidance_disposition": "The missing-read-context assumption and the reduced fixture's false WI-6140 dependency attribution are rejected; historical v003/v004, WI-5950, and WI-6140 evidence remains immutable.",
  "history_preservation": "Bridge versions, deliberations, PAUTH versions, receipts, database history, registry state, and Git history remain append-only; the projection is transient derived evidence.",
  "baseline": {
    "checker_tests": "176 pre-change; 235 final",
    "focused_tests": "59 WI-6183 cases",
    "authorized_targets": "exactly two",
    "real_index": "unchanged through Prime implementation and report; only two foreign registry TOMLs are staged",
    "legacy_tafe": "disabled"
  },
  "expected_result": {
    "pauth_audit": "Stable live and projected operation-time PAUTH material agree and transaction evidence is accepted.",
    "denial": "Revocation, relevant drift, tamper, redirect, mismatch, or cleanup failure rejects.",
    "containment": "No database, registry, non-cohort index, dispatcher, TAFE, WI-6140, or foreign-worktree mutation."
  },
  "rollback": {
    "instructions": "Before terminal verification, restore only the exact WI-6183 diffs in the two authorized targets. After VERIFIED, use a separately governed inverse commit.",
    "verification": "Rerun 59 focused, 235 full checker, 230 adjacent, static gates, exact hashes, and index/foreign-entry census."
  },
  "hard_invariants": [
    "Operation-time PAUTH remains independently evaluated and packet-hash material.",
    "Canonical groundtruth.db is never copied wholesale, whole-file hashed, staged, committed, or mutated.",
    "Only the exact four approved current authority relations enter the projection.",
    "Prospective source and taxonomy remain copied-index authoritative.",
    "Every non-cohort index entry, especially both foreign registry entries, remains unchanged.",
    "Legacy TAFE remains disabled."
  ],
  "fail_closed_conditions": [
    "Missing, unreadable, redirected, replaced, incomplete, revoked, or drifting canonical authority.",
    "Projection or sidecar tamper, schema mismatch, consumer mismatch, aggregate-size breach, or cleanup failure.",
    "Any attempt to trust precomputed PAUTH, remove packet binding, mutate an undeclared target, absorb WI-6140 bytes, or enable legacy TAFE."
  ],
  "essential_context_preservation": "The correction preserves exact two-target scope, copied-index authority, the four-relation projection, logical currentness, oversized-blob omission, sidecar and cleanup hardening, production-faithful transaction acceptance, the expanded adversarial matrix, WI-6140 serialization, foreign-index preservation, and disabled TAFE."
}
```

## Acceptance Criteria Status

- [x] PAUTH-bearing copied-index audit uses one exact four-relation read-only projection for both consumers.
- [x] Relevant authority drift, source replacement, schema gaps, projection tamper, consumer mismatch, and cleanup failure reject.
- [x] Operation-time PAUTH remains independently re-evaluated and packet-hash material; no trusted verdict or waiver exists.
- [x] PAUTH-free audits create no projection.
- [x] Canonical `groundtruth.db` is neither copied wholesale nor whole-file hashed, staged, committed, mutated, redirected, or linked.
- [x] Projection is ordinary-ledger protected, relation-bounded, sidecar-guarded, aggregate-size-bounded, and removed on every exit.
- [x] Prospective Git/taxonomy/candidate authority, oversized-blob omission, stale-packet rejection, and fail-closed behavior remain intact.
- [x] The production-faithful transaction path returns accepted evidence and zero errors.
- [x] All v004 F2 classes have executed parameterized evidence.
- [x] 59 focused, 235 full checker, 230 adjacent, and all static gates pass.
- [x] WI-6183 remains isolated from WI-6140; WI-6140 must rebase on the terminal WI-6183 test baseline.
- [x] Real index, foreign registry bytes, database, bridge files, dispatcher/TAFE state, and Git history were not mutated by implementation.

## Finalization Manifest And Index Boundary

Independent Loyal Opposition must fresh-read and atomically include exactly:

- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-001.md`
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-002.md`
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-003.md`
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-004.md`
- `bridge/gtkb-wi6183-protected-commit-pauth-read-snapshot-005.md`
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

The finalizer creates and adds v006, producing an eight-path commit cohort. No hunk patch is required. A disposable index must preserve the shared real index. After the successful commit, canonical realignment may update only the exact committed cohort entries to new HEAD. Every non-cohort entry must remain entry-identical; both foreign registry TOMLs must remain mode 100644, stage 0, blob `d4a1aca0e15172acad63f218f32c9814b2055677` and remain the only cached-diff paths. Whole-index SHA is expected to change after successful committed-cohort realignment and is not a terminal invariant.

Exclude every WI-6140 patch/target, WI-5950 byte, `groundtruth.db`, registry worktree byte, runtime packet/session file, foreign bridge thread, dispatcher state, and legacy TAFE state.

## Risk And Rollback

Residual risk is concentrated in SQLite cross-platform identity and cleanup behavior. Exclusive no-follow creation, retained handles, no-replace guards, sidecar occupancy, ordinary ledger verification, relation-level currentness, consumer binding, and terminal cleanup failure bound that risk. Cross-platform linklike variants exercise the common production denial predicate; independent verification must rerun the full matrix on the exact candidate.

Before terminal verification, rollback restores only the two authorized target preimages and reruns the complete matrix. After VERIFIED, rollback is a separately governed inverse commit. No rollback may rewrite bridge history, receipts, PAUTH, database or registry state, foreign real-index entries, or Git history.

## Loyal Opposition Request

Fresh-read v001-v005, every consumed publication receipt, the exact schema-v3 resumption packet, target bytes, final candidate gates, HEAD, and index boundary. Rerun live pre-verdict executability after v005 is receipt-complete. If every mapped invariant remains green, issue v006 `VERIFIED` only through the atomic scoped finalizer over the exact seven-path pre-verdict manifest; otherwise return a finding-specific `NO-GO` without modifying implementation bytes.

---

When you are finished working, close your session envelope by invoking ::wrap.

NEW
::init gtkb lo
::open build

# WI-6183 — Preserve PAUTH read authority in copied-index protected-commit audits

bridge_kind: prime_proposal
Document: gtkb-wi6183-protected-commit-pauth-read-snapshot
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-08-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; activity envelope ::open build; owner-approved bounded protected-commit repair
author_metadata_source: explicit_interactive_session_metadata
session_init_keyword: ::init gtkb pb
activity_init_keyword: ::open build

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6183
related_work_items: ["WI-5950", "WI-6140"]

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
database_registry_or_index_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

---

## Summary

Repair the protected-commit authorization checker so an invocation that audits through its copied-index snapshot retains the minimum current PAUTH read authority needed to re-evaluate project authorization at operation time. This proposal performs no KB, MemBase, or groundtruth.db mutation.

The repair creates an invocation-local, read-only, compact `groundtruth.db` projection inside the already isolated audit snapshot. The projection contains exactly four authority relations needed by the current PAUTH evaluator, is derived afresh from the canonical live database for that invocation, is covered by a derived-ledger entry, is checked for logical currentness before and after consumption, and is removed on every exit. The existing copied-index snapshot remains authoritative for Git-controlled source, taxonomy, and candidate-path inputs. No full database copy, whole-database hash, persistent cache, registry update, real-index mutation, or authority shortcut is introduced.

Projection is allowed only for a PAUTH-bearing `GO`, `NO-GO`, or `VERIFIED` protected-commit audit whose operative path actually invokes applicability and project-authorization evaluation. A non-PAUTH audit follows the present no-projection path byte-for-byte in behavior. Missing, unreadable, redirected, incomplete, revoked, stale, replaced, tampered, mismatched, or uncleanable authority state fails closed.

## Problem Statement

The protected-commit checker deliberately builds a copied-index audit root so staged and worktree state cannot replace the Git-controlled source and taxonomy evidence used for protected commit validation. Its oversized-file omission policy excludes the untracked canonical `groundtruth.db` from that copied root. The PAUTH evaluator then runs against the copied root and cannot read the current project, project-authorization, work-item membership, and specification authority it is required to re-evaluate at operation time.

The observed WI-5950 failure demonstrates the defect boundary. The same report candidate changed from packet hash `sha256:3adaebc3…b0f01` to required packet hash `sha256:027bfde0dd80dedad186599ba6a4775753a0373c905b91ea40091c53448b9864` solely because the protected-commit audit lacked the live database authority context. That evidence does not validate either packet and does not dispose WI-6140's distinct N+1-to-N+2 proposal-source applicability horizon defect.

The required correction is not to trust precomputed PAUTH evidence, copy the entire live database, weaken copied-index isolation, or make `groundtruth.db` a Git-controlled input. It is to preserve the existing Git authority boundary while supplying a minimal, read-only, logically current PAUTH relation snapshot to the evaluator for the duration of one protected-commit invocation.

## Scope

### In scope

1. Update `scripts/check_protected_commit_authorization.py` to construct, validate, ledger, consume, and destroy an invocation-local PAUTH read snapshot when and only when the audited bridge transition requires PAUTH re-evaluation.
2. Update `platform_tests/scripts/test_check_protected_commit_authorization.py` with the full positive, negative, drift, tamper, routing, cleanup, and non-regression matrix described below.
3. Preserve the existing copied-index snapshot as the sole audit authority for Git-controlled source, taxonomy, bridge content, and packet inputs.
4. Preserve operation-time PAUTH re-evaluation and its contribution to applicability packet hashing.
5. Preserve fail-closed behavior for every missing, unreadable, incomplete, revoked, stale, replaced, redirected, tampered, mismatched, or uncleanable authority condition.

### Out of scope

1. Any write to `groundtruth.db`, MemBase, PAUTH rows, project rows, specification rows, work-item memberships, receipt rows, or any other database relation.
2. Any registry admission, registry repair, registry TOML mutation, `groundtruth.db` registry mutation, or registry/index finalization.
3. Any mutation of the real Git index, foreign staged entries, unrelated worktree bytes, Git history, commits, hooks, dispatcher state, or TAFE state.
4. Any change to applicability semantics, PAUTH semantics, relation schemas, bridge lifecycle rules, protected-commit packet schema, packet hash semantics, or evaluator business rules.
5. Any persistent database copy, persistent authority cache, full-database byte hash, whole-database currentness gate, or alternate source of truth.
6. Any change to WI-5950 implementation bytes or adjudication, and any attempt to absorb or close WI-6140's separate proposal-source horizon defect.
7. Any enablement or use of the disabled legacy TAFE dispatcher.

## Proposed Design

### 1. Preserve the two-authority audit boundary

The existing copied-index root remains the canonical protected-commit view for every Git-controlled input. The repair does not copy the live worktree's source, taxonomy, bridge candidate, index, or generated artifacts into that root after snapshot creation.

For PAUTH-bearing audit paths only, the checker derives a second and strictly narrower read surface: a compact SQLite database at the audit snapshot's expected `groundtruth.db` path. That file is an invocation-local derived ledger artifact, not a KB, MemBase, cache, registry, or independent authority. Its source of authority remains the canonical live-root `groundtruth.db` opened read-only.

### 2. Gate projection to the operative PAUTH route

The checker must project authority only when all of the following are true:

- the candidate status is `GO`, `NO-GO`, or `VERIFIED`;
- the candidate carries an operative Project Authorization value;
- the protected-commit path will perform the current applicability/project-authorization evaluation; and
- the evaluator will consume the audit snapshot root.

A non-PAUTH candidate, a status that does not invoke protected-commit PAUTH evaluation, or an audit route that does not consume the copied root must not create or attempt a projection. Tests must prove the non-PAUTH route does not open the canonical database for projection and preserves its existing result and diagnostics.

### 3. Bind the canonical source without redirection

The only permitted projection source is the canonical live-root `groundtruth.db` already resolved by the protected-commit invocation. The implementation must:

- use a read-only SQLite URI and enable `PRAGMA query_only=ON`;
- reject a missing or unreadable source;
- reject a symlink, junction, reparse point, or other path redirection at the source or destination;
- capture and re-check stable source-path identity so replacement during the operation fails closed;
- reject environment, configuration, argument, or nested-root attempts to substitute another database;
- never fall back to a copied, cached, temporary, worktree-relative, or caller-supplied database.

### 4. Project exactly four relations

The compact snapshot contains exactly these authority relations and no others:

1. `current_specifications`
2. `current_project_authorizations`
3. `current_projects`
4. `current_project_work_item_memberships`

The implementation must create physical compact tables in the invocation-local database using the normalized column names, declared types, nullability, primary-key shape, and deterministic row values required by the current evaluator. It must reject a missing relation, missing or extra required column, incompatible schema, unreadable row, duplicate key, unsupported value, or partial copy. It must not project views whose later evaluation still depends on the live database.

The relation allowlist is closed. Adding another relation is a future governed change, not an implementation convenience.

### 5. Establish logical currentness without a whole-database hash

The live database is untracked and may receive unrelated legitimate writes. Full-file identity or hashing would make unrelated database-page churn spuriously invalidate a protected-commit audit. Currentness therefore must be established over the bounded authority state actually consumed.

Before projection, capture:

- canonical source-path identity and non-reparse status;
- SQLite `data_version` and `schema_version` observations;
- normalized schemas for the four allowed relations;
- deterministic row counts; and
- deterministic canonical typed-row digests for each relation.

After projection and again after the evaluator consumes the snapshot, re-open or re-observe the canonical source through the same read-only boundary and repeat those observations. A source identity change, relevant schema change, row-count change, or typed-row digest change fails closed. A `data_version` change triggers exact relation comparison; it does not fail solely because an unrelated table changed. The implementation must not read or hash the entire database file as a substitute for these logical checks.

The snapshot's own four schemas, row counts, and typed-row digests must match the accepted source observation exactly before evaluation. Any projection or post-copy tamper fails closed.

### 6. Extend the derived audit ledger

The existing audit snapshot ledger remains unchanged for its current copied-index entries. Add one ordinary, non-exempt derived entry for the compact authority snapshot, recording at minimum:

- the snapshot-relative path;
- file size and content hash;
- normalized relation-schema digest;
- per-relation row counts and typed-row digests;
- the bound canonical source-path identity observations; and
- the projection construction identity/version needed for consumer agreement.

The ledger entry cannot declare the snapshot trusted, exempt, prevalidated, or outside audit. Before evaluator invocation, the checker verifies the file and logical contents against the entry. After evaluator return, it repeats verification before accepting the result. A missing entry, duplicate entry, path mismatch, file mismatch, relation mismatch, consumer-version mismatch, or ledger tamper fails closed.

### 7. Bind the evaluator to the derived snapshot

The applicability/project-authorization evaluator must receive the copied audit root whose `groundtruth.db` is the verified compact projection. It must not receive the live root, a second unledgered temporary path, or precomputed authorization evidence. Existing operation-time PAUTH validation, revocation checks, project/work-item membership checks, source-currentness checks, and packet hashing remain operative.

The checker must prove that the evaluator consumed the exact ledgered projection construction. A producer/consumer relation-set, schema, digest, or version disagreement fails closed rather than silently retrying another route.

### 8. Remove every derived database artifact on every exit

Cleanup runs on success, validation failure, evaluator rejection, evaluator exception, timeout, and outer exception. It removes the compact database and any possible SQLite `-journal`, `-wal`, and `-shm` sidecars. Cleanup failure is a terminal protected-commit denial. No derived authority file may survive as a reusable cache or later invocation input.

## Concurrency, Ownership, and Sequencing

The prior global numbered-bridge writer hold remains closed for every other lane. The owner separately authorized this exact WI-6183 two-file repair and the distinct WI-6140 repair before any resumed WI-5950 recovery. For WI-6183, that approval supplies only a narrow serialized execution release after an independent Loyal Opposition `GO`; it is not a general bridge-writer release, registry release, dispatcher release, TAFE release, or permission for WI-6140 or WI-5950 to run concurrently.

The proven dependency direction is WI-6183 before WI-6140 v003. WI-6140's PAUTH-bearing atomic finalization predictably invokes this protected-commit checker and cannot lawfully complete while the checker omits its PAUTH read authority. WI-6183 therefore must independently receive `GO`, implement only its two targets, file its report, and receive independent atomic `VERIFIED` before WI-6140 advances. The verified WI-6183 test module and its exact hashes establish the shared checker-test baseline. WI-6140 must then fresh-read that baseline, rebase its work, and regenerate its five-path test patch before filing its corrected `REVISED` proposal and seeking `GO`.

`gtkb-artifact-registry-authoritative-hygiene-sweep` v002 is a separate `GO` governance-architecture carrier that explicitly forbids source implementation. Its reference to `scripts/check_protected_commit_authorization.py` is non-owning overlap, does not reserve the path, and is not a terminal prerequisite for WI-6183. At WI-6183 implementation start, the owner must fresh-read current claims and exact path state and fail closed for any then-live conflicting claim or authorized mutation; no hygiene-sweep terminalization or source-hunk handoff is required.

After WI-6183 has its own `GO` and the fresh claim/path check proves a stable, unowned two-target boundary, its implementation owner may acquire the exact claim, mint a current schema-v3 implementation-start packet for these two targets, and implement the repair. No target bytes, claim, packet, publication, index entry, database, registry, dispatcher, or TAFE state may move under this proposal before those conditions are met. WI-6140 remains held until WI-6183 is independently `VERIFIED` and the later carrier has regenerated its five-path patch from that verified baseline.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — PAUTH must be re-evaluated at the protected operation boundary, not accepted from stale proposal evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation authority must remain current and bounded to the approved project/work item.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the repair may not turn bridge evidence into an authorization bypass.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — the protected-commit evaluator must receive an evaluable, self-contained bounded authority view.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v2 — protected commit validation remains governed and fail closed without mutating the real index or history.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the consumed authority relations must be logically current at operation time.
- `GOV-WORK-TREE-HYGIENE-001` — foreign staged/worktree state and derived artifacts must remain isolated and preserved.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the change preserves essential context and existing non-PAUTH behavior.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the authority boundary and cleanup guarantees require mechanical tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — proposal, review, implementation, and verification roles remain separated.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal states the operative requirement mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal is linked to its project, work item, and PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — final verification must map tests to each cited requirement and fail-closed condition.
- `GOV-STANDING-BACKLOG-001` — WI-6183 is the durable P0 defect carrier rather than an ad hoc repair.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the owner decision, proposal, implementation report, and independent verdict remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — implementation proceeds through artifact lifecycle rather than chat-only authority.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the accepted defect and repair decision trigger proposal/review/implementation/verification stages.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — author/session/model provenance is explicit and machine-readable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the repair remains inside the GT-KB platform root and does not couple adopter state.

## Prior Deliberations and Related Carriers

- `DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR` (row 14281) — owner approval of the P0 defect, exact two-file scope, four-relation compact read projection, fail-closed boundary, baseline, exclusions, and sequencing constraints.
- `bridge/gtkb-wi5950-strict-terminal-recovery-016.md` — durable evidence of the protected-commit packet mismatch and the distinct cycle-breaker requirement; not implementation authority for WI-6183.
- `bridge/gtkb-wi6140-verdict-packet-hash-source-horizon-008.md` — current NO-GO evidence for the distinct five-path source-horizon repair. Its PAUTH-bearing finalization depends on WI-6183; after WI-6183 is independently `VERIFIED`, WI-6140 must fresh-read/rebase/regenerate its five-path test patch before corrected `REVISED`/`GO` progression.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-002.md` — current `GO` governance-architecture carrier that expressly forbids source implementation. Its checker-path reference is non-owning, is not a terminal prerequisite, and requires only a fresh claim/path conflict check when WI-6183 starts.

No prior record authorizes a full database copy, database mutation, precomputed PAUTH trust, copied-index bypass, or legacy TAFE use.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved deliberation, WI-6183, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v2, the project authorization, and the cross-cutting freshness, hygiene, evaluability, non-impairment, provenance, and bridge-lifecycle requirements fully determine this exact two-target repair. No new authority semantics, packet semantics, relation semantics, database mutation, registry behavior, dispatcher behavior, or TAFE behavior is required. Any need to widen the relation allowlist, target cohort, mutation scope, or ownership boundary requires a new governed proposal rather than inference during implementation.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "Owner-approved DELIB-20260811-PROTECTED-COMMIT-PAUTH-READ-SNAPSHOT-REPAIR, WI-6183, the cited PAUTH and governed-Git requirements, and the proven order in which WI-6183 establishes the checker-test baseline before WI-6140 regenerates its five-path patch; the artifact-registry hygiene-sweep overlap is non-owning.",
  "canonical_authority": "Git-controlled inputs remain authoritative from the copied-index snapshot; PAUTH relation values remain authoritative only from the canonical live-root groundtruth.db opened read-only and projected invocation-locally.",
  "primary_route": "Build copied-index audit root, conditionally derive and ledger the exact four-relation compact read snapshot, verify logical currentness, evaluate through that root, reverify, and clean every derived database artifact.",
  "before_behavior": "The copied-index root omits untracked groundtruth.db, so operation-time PAUTH evaluation can compute a different packet or fail for missing authority even when Git-controlled candidate bytes are unchanged.",
  "after_behavior": "PAUTH-bearing audits retain current minimal read authority without weakening copied-index isolation; non-PAUTH audits do not project or open authority state.",
  "self_descriptive_naming": "Helpers, ledger fields, diagnostics, and tests will name the PAUTH read snapshot, its four-relation allowlist, logical currentness observations, and cleanup obligations directly.",
  "obsolete_guidance_disposition": "No live guidance is removed. Any implication that the oversized-file omission alone is sufficient for a PAUTH-bearing copied-root audit is superseded by the bounded projection rule.",
  "history_preservation": "No commit, Git history, bridge history, receipt history, PAUTH record, database row, registry entry, or foreign worktree/index byte is rewritten or deleted.",
  "baseline": "The focused protected-commit authorization module is 176 passed before this proposal; existing copied-index, PAUTH, packet, cleanup, and non-PAUTH tests remain mandatory.",
  "expected_result": "A current PAUTH-bearing audit evaluates the exact ledgered four-relation snapshot and retains deterministic packet semantics, while every stale, missing, redirected, incomplete, revoked, tampered, mismatched, or uncleanable condition fails closed.",
  "rollback": "Correct or revert only the two WI-6183-owned target hunks through a fresh governed carrier and exact current preimages; no database, registry, index, dispatcher, TAFE, or history rollback is involved.",
  "hard_invariants": [
    "No KB, MemBase, PAUTH, receipt, database, registry, or real-index mutation.",
    "No full database copy or whole-file hash; projection is limited to the exact four-relation allowlist.",
    "Canonical read-only PAUTH authority and copied-index Git authority remain mechanically distinct and both remain binding.",
    "Operation-time PAUTH evaluation, derived-ledger coverage, logical currentness, non-PAUTH no-projection behavior, and cleanup on every exit remain mandatory.",
    "Legacy TAFE remains disabled and no dispatcher or TAFE action is introduced."
  ],
  "fail_closed_conditions": [
    "Missing or unreadable canonical source, source redirection, replacement, reparse-point identity, or hostile path substitution.",
    "Missing or incompatible relation/schema, revocation, relevant logical currentness drift, or typed-row projection failure.",
    "Projection or ledger tamper, producer/consumer mismatch, unexpected SQLite sidecar, or cleanup failure.",
    "Any attempt to trust precomputed PAUTH evidence, weaken packet hashing, mutate an undeclared target, or absorb foreign WI-6140/index/registry bytes."
  ],
  "essential_context_preservation": "Preserves the owner-approved exact two-file/four-relation boundary, WI-6140's distinct later horizon repair and required rebase onto the verified WI-6183 shared-test baseline, the hygiene-sweep carrier's non-owning governance-only scope, the global hold for all other lanes, and the narrow serialized WI-6183 release."
}
```

## Baseline Evidence

The approved pre-change focused baseline is:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short
176 passed
```

This proposal records that approved baseline; it does not claim a fresh run during draft adoption. Implementation and independent verification must rerun the focused module on the final candidate and report the exact count, duration, target hashes, and exit status.

## Specification-Derived Verification

Concrete assertion floor: the pre-change focused checker module recorded `176 passed`; the final WI-6183 candidate must run the full module plus every added adversarial case with `pytest` exit `0`.

The implementation report and independent Loyal Opposition verdict must map evidence to every row below rather than treating a green aggregate count as sufficient.

| Requirement / risk | Required mechanical evidence |
|---|---|
| Copied-index Git authority remains canonical | Existing copied-index source/taxonomy/bridge isolation tests plus adversarial live-worktree and foreign-index divergence tests remain green. |
| PAUTH is re-evaluated at operation time | A PAUTH-bearing candidate succeeds only when the exact four current relations authorize it; revocation and membership/spec/project drift before consumption deny it. |
| Exact closed relation allowlist | Projection schema and ledger tests prove exactly the four named relations, no implicit dependency, no extra table, and rejection of missing/incompatible schema. |
| Non-PAUTH no-projection path | Tests prove non-PAUTH candidates do not open/project `groundtruth.db`, create ledger entries, or change current diagnostics/results. |
| Canonical read-only source | Missing, unreadable, redirected, symlinked/junction/reparse, replaced, environment-overridden, and caller-substituted sources deny the operation. |
| Logical currentness | Relation schema/count/typed-row drift denies; unrelated-table-only `data_version` churn does not fail after exact relation equality; no whole-file database hash is used. |
| Projection integrity | Snapshot relation schemas/counts/digests match source; file, row, schema, path, and derived-ledger tampering deny before and after evaluator consumption. |
| Producer/consumer agreement | Relation-set, schema, construction-version, root, and digest mismatch between checker and evaluator deny without fallback. |
| Packet semantics preserved | PAUTH re-evaluation remains in applicability packet hashing; prospective source/taxonomy changes still reject stale packets; no precomputed evidence is trusted. |
| Cleanup is terminal | Success, denial, exception, timeout, and cleanup-error tests cover database, `-journal`, `-wal`, and `-shm`; surviving artifacts or cleanup failure deny. |
| No mutations outside targets | Hash/status evidence proves `groundtruth.db`, both registry TOMLs, real index, foreign staged entries, WI-5950 bytes, dispatcher, TAFE, and history are unchanged. |
| Shared-path sequencing and preservation | WI-6183 records exact verified checker/test hashes as the shared baseline; the implementation-start readback proves no live conflicting claim/path mutation. The later WI-6140 carrier must fresh-read this baseline, rebase, and regenerate its five-path test patch before corrected `REVISED`/`GO`. The hygiene-sweep carrier is governance-only and non-owning. |

### Required focused and adversarial cases

1. Current live PAUTH and projected PAUTH produce identical authorization decisions and packet contributions for an authorized candidate.
2. Revoked authorization, retired/inactive project, missing work-item membership, and non-current specification each fail at operation time.
3. The projection contains exactly `current_specifications`, `current_project_authorizations`, `current_projects`, and `current_project_work_item_memberships` as physical compact tables.
4. A non-PAUTH protected-commit audit performs no projection and preserves current behavior.
5. Missing, unreadable, locked, malformed, or schema-incomplete canonical database fails closed.
6. Source and destination symlink, junction, reparse, nested-root, replacement, environment override, configuration override, and caller path substitution fail closed.
7. Relevant relation change between pre-copy, post-copy, evaluation, and post-evaluation observations fails closed.
8. Unrelated-table-only database activity does not fail solely because file bytes, page layout, mtime, size, or `data_version` changed when all four logical relation observations remain equal.
9. Static/source tests prove the checker does not calculate or compare a whole-`groundtruth.db` content hash and does not copy the entire database.
10. Derived-ledger file hash, size, path, source identity, schema digest, row-count, typed-row digest, and construction-version tamper each fail closed.
11. Injected SQLite `-journal`, `-wal`, or `-shm` sidecars fail validation or are removed according to the fail-closed cleanup contract; none survives.
12. Producer/consumer root, allowlist, schema, digest, and version mismatch fails without live-root fallback.
13. Prospective source or taxonomy changes still invalidate stale applicability packets under the existing copied-index route.
14. Oversized unrelated blobs remain omitted from the copied-index audit root and cannot become hidden authority.
15. Evaluator denial, exception, timeout, outer exception, and cleanup failure execute the complete cleanup path and return denial.
16. The real index hash/status, foreign staged cohort, worktree state, database, registry, dispatcher, TAFE, and Git HEAD remain unchanged.
17. The WI-6183 report records exact final checker/test hashes and focused results as the shared baseline, while start evidence proves the hygiene-sweep carrier supplied no source implementation and no live claim/path conflict existed.

### Required command matrix

On the stable final candidate, run and record at minimum:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
```

Also run the current implementation-start/report gates, proposal applicability and clause gates against the exact candidate content, protected-commit authorization validation, and any directly adjacent platform suite identified by the final code diff. Report exact commands, exit codes, counts, timings, hashes, packet identity, and negative-state evidence.

## Acceptance Criteria

1. Only the exact two target files change under WI-6183 ownership.
2. Execution begins only after a current WI-6183 `GO`, a fresh claim/path recheck proving no live conflicting owner, and one exact implementation claim/schema-v3 start packet binding the final two preimages.
3. PAUTH-bearing protected-commit audits derive and consume exactly the four-relation compact read snapshot from canonical live `groundtruth.db`.
4. Non-PAUTH audits perform no projection and retain existing behavior.
5. The compact snapshot and derived-ledger entry are verified before and after evaluation and removed with all SQLite sidecars on every exit.
6. Logical currentness detects every relevant authority/schema/path change without treating unrelated whole-database byte churn as dispositive.
7. The checker never mutates or fully copies/hashes `groundtruth.db`, never trusts precomputed PAUTH evidence, and never bypasses copied-index Git authority.
8. All required focused, adversarial, static, formatting, compilation, diff, applicability, clause, start/report, and adjacent gates pass on final stable bytes.
9. The implementation report includes exact pre/post hashes proving no database, registry, real-index, foreign staged, WI-5950, dispatcher, TAFE, or Git-history mutation.
10. Independent Loyal Opposition verification maps evidence to every specification-derived row and produces the only terminal `VERIFIED` decision.
11. The terminal WI-6183 evidence publishes the exact checker/test baseline that WI-6140 must later fresh-read, rebase onto, and use to regenerate its five-path test patch before corrected `REVISED`/`GO` progression.

## Risks and Mitigations

- **Risk: the projection becomes a second authority.** Mitigation: invocation-local derivation only, canonical read-only source, ordinary derived-ledger coverage, no persistence, and mandatory cleanup.
- **Risk: unrelated database activity creates false denials.** Mitigation: bounded relation schemas/counts/typed-row digests and exact comparison after `data_version` movement, never a whole-file hash gate.
- **Risk: relevant authority changes escape detection.** Mitigation: observations before projection, after projection, and after evaluator consumption, plus path-identity and schema checks.
- **Risk: evaluator silently falls back to live or cached state.** Mitigation: explicit producer/consumer binding and fail-closed root/version/digest agreement tests.
- **Risk: cleanup leaves reusable authority state.** Mitigation: database and sidecar cleanup on every exit, with cleanup failure itself denying the operation.
- **Risk: the dependency is inverted and WI-6140 predictably fails protected-commit PAUTH finalization again.** Mitigation: independently `GO`, implement, and `VERIFY` WI-6183 first; publish its exact shared checker-test baseline; only then allow WI-6140 to fresh-read, rebase, and regenerate its five-path test patch before corrected `REVISED`/`GO`.
- **Risk: a nominal path overlap is mistaken for live implementation ownership.** Mitigation: recognize the hygiene-sweep v002 carrier's explicit source-implementation prohibition, treat it as non-owning, and perform a fresh claim/path conflict check at WI-6183 start.
- **Risk: the narrow approval is mistaken for a global release.** Mitigation: explicit global-hold language, exact two-target scope, and prohibition on registry, dispatcher, TAFE, or other numbered-writer activity.

## Rollback

If the final implementation regresses protected-commit behavior, correct or revert only the WI-6183-owned hunks in the two target files through a separately governed corrective carrier using fresh exact preimages. If WI-6140 has subsequently rebased onto the verified WI-6183 baseline, coordinate that later dependency rather than blindly replacing its hunks. The hygiene-sweep carrier contributes no source implementation to preserve. Because this proposal creates no durable database, registry, index, dispatcher, TAFE, or history mutation, rollback requires no data reversal; tests must still prove derived database and sidecar cleanup.

## Implementation and Review Handoff

After WI-6183 receives `GO`, the Prime Builder implementation owner must fresh-read the proposal/GO, both target preimages, current claims, current project authorization, current WI-6140 state, and the hygiene-sweep carrier's governance-only/non-owning scope before beginning. The owner must verify no live conflicting claim or path mutation, acquire the exact work-intent claim, mint/finalize one current schema-v3 implementation-start packet, implement only the approved two-file repair, run the full matrix, and file a governed implementation report.

The implementing session must not self-review or self-finalize. A distinct Loyal Opposition session must rerun the applicable gates against the live report and exact candidate bytes, validate protected-commit behavior and negative state, then file the terminal verdict. After WI-6183 is independently `VERIFIED`, WI-6140 must fresh-read the exact final target/test baseline, rebase, regenerate its five-path test patch, and only then proceed through corrected `REVISED`/`GO`. No legacy TAFE dispatcher action is permitted at any stage.

Recommended eventual commit type after independent atomic verification: `fix:`

---

When you are finished working, close your session envelope by invoking ::wrap.

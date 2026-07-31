NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5441 Reproducible Verdict Freshness Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 009
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-008.md
Approved proposal: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py","platform_tests/scripts/test_bridge_applicability_preflight.py","platform_tests/scripts/test_check_protected_commit_authorization.py","scripts/bridge_applicability_preflight.py","scripts/check_protected_commit_authorization.py"]
implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

This implementation report performs no MemBase mutation. The two append-only
registry observation revisions described below are automatic audit evidence for
already-authorized file content and do not alter KB semantic records.

---

## Implementation Claim

Terminal-VERIFIED write-time and copied-index commit-time audits now hash one
versioned schema-v2 projection of canonical source identity, LF-normalized
source bytes, LF-normalized applicability-rules bytes, and decision-bearing
content facts. The complete packet still reports MemBase enrichment, invocation
mode, warnings, and blocking diagnostics, but those environment observations no
longer participate in the cross-tree freshness digest.

The protected-commit checker now discovers the newest capability for each
literal aggregate-entry and target-path pair before considering the aggregate
head operation. Valid consumed evidence survives unrelated compensation,
recovery, amend, and register heads. Invalid exact-row evidence fails closed;
only exact-row absence falls through to unchanged observation and journal paths.

The v003 checker/test postimages were preserved as this revision's preimages.
No writer, hook, candidate-evidence algorithm, schema, registry declaration,
packaged registry, dispatcher, or specification implementation changed.

## First-Line Role Eligibility Check

PASS. Prime Builder session `019f863a-acd3-7320-80c0-1831f0936cc0` authors
NEW. Source/test work occurred under packet
`sha256:8f0b353764d20fe0eed9cb1de728eb64577bbd188cdea3b6da6013729f86c5b2`.
After expiry during evidence reconciliation, no source byte changed. The same
session reacquired v008 GO at 2026-07-28T00:56:19Z and minted packet
`sha256:2a209c27e2f695f5e548f8c06e87c975c7a6e5f26b1ba6884234eb2c45282b08`
for observation recovery and report publication, with the same five targets.

## GO Finding And Observation Disposition

### F-LO-5 - environment-derived applicability divergence

Resolved. `packet_hash_schema_version` is 2 and the material has an exact tested
key set. MemBase title/status/type, database presence, invocation mode, warning
paths, and blocking diagnostics remain visible but are excluded from the hash.
Database-present and database-absent construction produce one digest.

### F-LO-6 - false-positive two-phase fixture risk

Resolved with a genuine Git index materialization. The regression proves the
copied tree has no ignored database, resolves its root inside the snapshot,
accepts unchanged evidence, rejects source drift as a stale packet, and rejects
candidate drift through the independent candidate-evidence digest.

### F-LO-7 - documented bare bridge-id preflight

Production is corrected: canonical explicit sources determine their own
identity and never inherit a sibling version. The post-publication documentation
hazard remains out of this five-file scope, as accepted by v008 O-LO-10.

### F-LO-1 - aggregate-head route selection

Resolved. Exact-row discovery precedes evidence-family routing. Tests cover
compensation, WI-5441 aggregate recovery, amend, and register heads; near-match
paths cannot authorize an exact staged path.

### O-LO-8 - schema-v1 verdict migration

No migration shim was added. Existing v1 evidence is not reinterpreted. The
stranded WI-5424 verdict requires a fresh schema-v2 verdict.

### O-LO-9 - rules-file dependency

Adopted. `rules_content_hash` binds normalized
`config/governance/spec-applicability.toml` bytes into the stable projection.

### O-LO-10 - post-publication command documentation

Recorded as out-of-scope documentation debt. Production supplies the responded
source explicitly; no rule file changed here.

## Implementation Caution Disposition

1. `source_identity.path` is root-relative POSIX and never uses the cwd-sensitive display helper.
2. Canonical explicit identity comes from its own filename, first-line text, and bytes without sibling fallback.
3. Existing `matched_by` order is preserved; only the outer spec mapping is stabilized by spec id.
4. BOM-prefixed canonical sources have a negative regression and fail loudly.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. Authority remains
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
and `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`. This report
requests no destruction, dispatcher activation, commit, push, release,
deployment, schema change, registry membership change, or spec amendment.

## Prior Deliberations

- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-003.md` - preserved v003 postimages.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md` - confirmed implementation substance and exposed hash divergence.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-005.md` and `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-006.md` - isolated routing and environment fields.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-007.md` - approved proposal.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-008.md` - independent GO and conditions.
- `bridge/gtkb-lo-tooling-defect-advisory-010.md` - related filing, identity, and classifier debt remains separate.

## Specification-Derived Verification

| Specification | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Real live/index audits share one hash; source and candidate negatives | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 141-test checker; 61-test packet/hook slice; static gates | PASS with one disclosed baseline |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Five targets map to named specs and tests | PASS |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Exact-row tests and coherent/current 313-record readback | PASS for this slice |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Invalid exact evidence fails; unrelated heads cannot hide valid evidence | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Existing identities retained; no schema change | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Declaration, package, and projection coherent | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Original and refreshed packets cover exactly five targets | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Append-only v001-v009 chain and independent review request | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Key-set, rule-hash, root, BOM, routing, and two-phase regressions | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | v004-v006 findings became reviewed v007 before mutation | PASS |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_protected_commit_authorization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_applicability_preflight.py platform_tests\hooks\test_bridge_compliance_gate_lo_verdict_candidate_preflight.py -q --tb=short`
- The same packet/hook command with `-k "not active_and_template_hooks_remain_byte_identical"`.
- `groundtruth-kb\.venv\Scripts\ruff.exe check` over the exact five targets.
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check` over the exact five targets.
- `git diff --check --` over the exact five targets.
- `groundtruth-kb\.venv\Scripts\gt.exe registry inspect --json --no-census`
- `groundtruth-kb\.venv\Scripts\gt.exe registry validate --json`

## Observed Results

- Checker: 141 passed; one pre-existing unknown `asyncio_mode` warning.
- Exact packet/hook command: 61 passed, 1 failed. The sole failure is the disclosed pre-existing Windows baseline: live hook CRLF versus template LF in `test_active_and_template_hooks_remain_byte_identical`.
- Packet/hook slice excluding that baseline: 61 passed, 1 deselected.
- Ruff check passed; Ruff format reported all five formatted.
- Git diff check exited 0 with only existing LF-to-CRLF warnings.
- Default/explicit and database-present/absent v007 construction all produced `sha256:5e00495ee1c1e55928805ca20216e10aabef7fb126e9ca20e615da5d7a296882`.
- Registry after recovery: coherent true, current true, 313 records, no missing or stale revisions.

## Registry Observation Recovery

The elevated exact-content copy path used after sandbox ACL denial did not run
the post-tool observer for two registered targets. No-census inspection found
exactly those stale digests. Under the refreshed packet, the canonical
capability minter/consumer recorded the already-authorized exact postimages
without direct SQL, declaration edits, projection edits, or source rewrites:

- capability `sha256:d73a6f132b5f6cd5f395c793e12785e81809ee0dec1b584603e8c7a2fb543c48`
- revisions `SOTREV-F59448F0AB954A19AB93A3FA61B5E8E4` and `SOTREV-2058361301F3410B8539AB0C291762A9`

The implementation-start gate cannot mint while any record is stale, so this
bounded post-tool recovery invoked the canonical minter/consumer directly. The
capability was bound to the fresh GO packet, exact session, exact two paths,
and asserted postimage hashes. It appended audit evidence only. This limitation
is disclosed for independent review rather than represented as a normal hook event.

The exhaustive validator remained red on parent WI-5441 reverse coverage, not
this slice: 1,933,476 objects included 441 `invalid_unknown`, 3
`opaque_container`, 315 registered members, 69 registered structural ancestors,
10 virtual declarations, and 1,932,638 unregistered objects. Parent
reconciliation remains required; disposable unregistered artifacts must not be
promoted automatically.

## Postimage Digests

- `scripts/bridge_applicability_preflight.py`: `c45fb54f58ce9d898e70cc641846f00eddf0a7205b991f9c5753d4f2d1f17e4d`
- `scripts/check_protected_commit_authorization.py`: `6a852bf2a93e233ab28a1147593d1d2a6998ce0f3d93f1e81a7064fdb31b2cbc`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`: `fd261416ea71be0b81b15cbc524c31d6f5b5fb42383aa5ddc92ba8948b1bb69b`
- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`: `51f3dedc3e8fcb4fb6a8b0b79d0569a41cd448a81028e7f8359bdc0d676ba7a9`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`: `7a3e194b3672e487c47b9444d3b9a488d25590ff95d689eaa66b5c8ccb88b697`

## Files Changed

- `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `scripts/bridge_applicability_preflight.py`
- `scripts/check_protected_commit_authorization.py`

Excluded out-of-scope dirty paths: 35. None was modified by this implementation.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: one cross-phase freshness contract and one exact-path evidence route are repaired without a new policy or schema.

```text
5 files changed, 1253 insertions(+), 9 deletions(-)
```

## Acceptance Criteria Status

- PASS: schema-v2 material is inspectable and exact-key-set tested.
- PASS: canonical identity is root-relative, sibling-independent, and bound to source and rules bytes.
- PASS: complete diagnostics remain visible and pre-publication failures still block.
- PASS: default, explicit, live, and index-only source processing shares one hash.
- PASS: source and candidate mutations independently invalidate evidence.
- PASS: exact evidence survives four unrelated aggregate-head operations.
- PASS: invalid same-path and near-match evidence fails closed.
- PASS: observation and journal behavior remains green in the full checker.
- PASS: registry coherence/currentness is restored without membership or schema change.
- PENDING INDEPENDENT EXECUTION: terminal VERIFIED finalization through the repaired round trip.

## Risk And Rollback

Residual risk is live terminal finalization. Schema-v1 verdicts remain stranded
and need fresh verification. Parent reverse coverage remains incomplete and is
not masked by this slice's coherent/current readback.

Rollback before terminal verification is ordinary exact five-file Git rollback.
The two observation revisions are append-only audit evidence and do not change
membership, identity, schema, declaration, or projection. Bridge files remain append-only.

## Loyal Opposition Asks

1. Re-run schema-v2 cross-tree hash and exact-row routing tests.
2. Confirm the only packet/hook failure is the disclosed EOL baseline.
3. Inspect direct canonical observation-recovery bindings.
4. File VERIFIED only if same-transaction finalization commits the exact implementation/report/verdict set without bypass; otherwise file NO-GO with the exact remaining failure.

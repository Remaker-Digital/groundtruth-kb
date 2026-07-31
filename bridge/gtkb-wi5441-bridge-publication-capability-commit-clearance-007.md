REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Revision - WI-5441 Reproducible Verdict Freshness

bridge_kind: prime_proposal
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 007
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-006.md
Date: 2026-07-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py","platform_tests/scripts/test_bridge_applicability_preflight.py","platform_tests/scripts/test_check_protected_commit_authorization.py","scripts/bridge_applicability_preflight.py","scripts/check_protected_commit_authorization.py"]
Requirement Sufficiency: Existing requirements sufficient
KB Mutation: This revision performs no MemBase mutation.

---

## Revision Claim

Version 006 proves that `operative_version` is one instance of a broader
defect class. The applicability packet currently hashes content-derived facts,
invocation metadata, and environment-derived observations together. The
write-time gate runs in the live worktree, while the protected-commit gate runs
against an index-only tree that cannot contain the git-ignored
`groundtruth.db`. A whole-packet hash cannot be reproducible across both phases.

This revision keeps the complete packet and every existing pre-publication
decision, but computes `packet_hash` from a versioned, inspectable projection
containing only normalized source identity and bytes plus content- and
tracked-rule-derived facts. Environment and invocation observations remain in
the complete packet and remain inputs to full pre-publication pass/fail. They do
not participate in the later cross-tree freshness digest.

The revision also carries forward the accepted exact-row-first publication
routing correction from versions 005 and 006, including the broader negative
coverage required by F-LO-1.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` requires
the verdict to bind to the exact reviewed artifact and terminal publication to
remain reachable. It does not require a source digest to bind ambient
filesystem state, invocation spelling, or descriptive MemBase enrichment.

The authority boundary is:

1. Full source publication preflight evaluates current environmental and
   governance conditions and rejects missing specifications or PAUTH evidence.
2. Verdict freshness binds immutable source identity, normalized source bytes,
   declared scope, citations, work-item linkage, and tracked-rule applicability.
3. Candidate evidence independently binds the final verdict path and bytes.

No new owner policy, waiver, specification, schema, or registry mutation is
needed.

## Objective

Restore deterministic terminal `VERIFIED` finalization without weakening any
check that decides whether a proposal, report, or verdict may be published.

Success means:

1. One canonical source produces one packet hash through default CLI selection,
   explicit `--content-file`, the live worktree gate, and the real index-only
   commit gate.
2. The hash changes when source bytes or decision-bearing, content-derived
   applicability facts change.
3. MemBase enrichment, warnings, and blocking diagnostics remain visible, and
   pending-source preflight still rejects failures.
4. Exact publication evidence remains visible when the aggregate head is
   compensation, recovery, amend, or register.
5. Live terminal finalization completes without bypass, force-add, or a
   stranded verdict.

## Findings Addressed

### F-LO-5 (P0) - environment-dependent fields prevent a fixed point

Accepted. `scripts/bridge_applicability_preflight.py` will continue to return
the complete packet. `packet_hash` will be computed only from an explicit
`packet_hash_material` projection.

The stable projection includes:

| Field | Authority |
| --- | --- |
| `packet_hash_schema_version` | Versions this digest contract; initial projection value is `2`. |
| `bridge_document_name` | Required thread identity. |
| `source_identity` | Canonical root-relative bridge path, first-line status, and numeric version. |
| `source_content_hash` | SHA-256 of LF-normalized source text encoded as UTF-8, binding all source content. |
| `cited_specs` | Source-derived specification citations. |
| `target_paths`, `declared_target_paths`, `applicability_path_evidence` | Source-derived path evidence used by applicability rules. |
| `work_items` | Source-derived work-item linkage. |
| `applicable_specs` | Only `spec_id`, `severity`, `rationale`, and ordered `matched_by`, derived from source plus tracked rules. |
| `missing_required_specs`, `missing_advisory_specs` | Derived from citations and rule-derived applicability. |

The complete packet also exposes `packet_hash_material` and
`source_content_hash`, making the exact hash basis reviewable.

The complete packet retains but the projection excludes:

| Excluded field | Reason | Retained behavior |
| --- | --- | --- |
| `content_source.mode` | Invocation shape, not artifact identity. | Remains visible for audit. |
| Display-form `content_source.path` | Can become an absolute snapshot path. | Canonical `source_identity.path` is hashed; source-anchor gate remains unchanged. |
| `title`, `status`, `type`, `exists_in_membase` enrichment | Depends on `groundtruth.db`; descriptive only. | Remains in full `applicable_specs`; severity still comes from tracked rules. |
| `warnings.missing_parent_dirs` | Depends on evaluated filesystem tree. | Remains visible and retains CLI warning behavior. |
| `warnings.spec_links_section` | Diagnostic; actual `cited_specs` is hashed. | Remains visible. |
| `warnings.author_metadata_warnings` | Diagnostic. | Remains visible. |
| `warnings.unclassified_target_paths` | Depends on classifier and filesystem context. | Remains visible. |
| `blocking_errors` | Includes PAUTH checks against `project_root` and `db_path`. | Remains blocking in pending publication. |
| `preflight_passed` | Derived partly from environmental `blocking_errors`. | Remains authoritative for full pre-publication acceptance. |

This is not an evidence waiver. The pending-content compliance path continues
to reject when `preflight_passed` is false, required specs are missing, or
`blocking_errors` is non-empty. Only the digest later rebuilt in a deliberately
different tree uses the stable projection. Adding `source_content_hash`
strengthens current exact-source binding because unrelated source prose changes
cannot retain the same packet hash.

### F-LO-6 (P1) - ordinary temporary-directory regression can false-green

Accepted. The regression must exercise the copied-index path used by
`scripts/check_protected_commit_authorization.py`, not two ordinary temporary
directories and not a mocked packet comparison.

The integration fixture will create a real temporary Git repository, stage the
source report, candidate verdict, rules, gate, and checker inputs, leave
`groundtruth.db` outside the copied index, and invoke the real prospective-index
audit. It must assert from inside the materialized tree that `groundtruth.db` is
absent and root discovery resolves to that tree. The same embedded packet hash
must pass both live-worktree and prospective-index audits.

### F-LO-7 (P2) - default and explicit CLI invocations disagree

Accepted. Default selection and explicit selection of the same canonical
version produce the same `source_identity`, source-content hash, hash material,
and packet hash. `content_source.mode` remains different in the complete packet
so the invocation remains observable without becoming artifact authority.

Pending scratch content outside `bridge/` retains its mode and scanned
operative-context behavior. It is not reclassified as a canonical version.

### F-LO-1 (P2) - aggregate head suppresses exact publication evidence

Accepted with both v006 narrowings. For each registered staged path, the
checker queries the newest exact publication row by literal
`aggregate_entry_id` plus literal `target_path` before selecting an evidence
family.

1. Exact-row presence makes publication validation authoritative.
2. A valid consumed row clears only that exact staged path.
3. A malformed, mismatched, minted, expired, failed, or compensated exact row
   fails closed without falling through to older or different evidence.
4. Exact-row absence alone permits the unchanged observation and journal paths.
5. No coercion, case folding, separator rewriting, prefix matching, or other
   path widening is introduced.

Tests append aggregate heads for `bridge_publication_compensation`,
`wi5441_bridge_aggregate_recovery`, `amend`, and `register`; none may hide a
valid exact row. A newer invalid row for the same exact path must still fail.

### F-LO-4 (P3) - status-to-activity documentation

Disposition unchanged and accepted by v006. The canonical rule and projections
are part of WI-5640's controlled reference migration. This repair will not edit
one legacy copy independently.

## Proposed Implementation

### Canonical source identity

Add a narrow resolver in `scripts/bridge_applicability_preflight.py`:

1. An explicit file directly under `bridge_dir` must exactly match
   `<bridge_id>-<numeric-version>.md` and carry a recognized first-line status.
2. That file supplies `operative_version` and canonical `source_identity` even
   when later versions exist in the directory.
3. Default selection of that same version produces identical identity.
4. A canonical-looking mismatch fails closed.
5. A noncanonical pending draft retains directory-scan operative context.

### Stable hash material

Build the complete packet, construct the explicit schema-v2 projection above,
and hash only its sorted compact JSON. Do not delete complete-packet fields or
suppress diagnostics. LF-normalize source text for its content digest so Git
line-ending materialization cannot create a false identity change.

### Exact-row-first routing

Separate exact-row discovery from validation. Route by exact-row presence, not
the aggregate's newest revision operation. Preserve revision linkage,
capability state, copied-index digest, and newest-same-path checks.

## Exact Scope

All live outputs remain in-root under `E:/GT-KB`. The governed revision will be
filed only under `E:/GT-KB/bridge/`, and all implementation targets are under
the same root.

Implementation may modify only:

1. `scripts/bridge_applicability_preflight.py`
2. `platform_tests/scripts/test_bridge_applicability_preflight.py`
3. `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`
4. `scripts/check_protected_commit_authorization.py`
5. `platform_tests/scripts/test_check_protected_commit_authorization.py`

The v003 postimages for items 4 and 5 remain the preimages. The exact-path
publication behavior independently confirmed in v004 and v006 is preserved.

## Excluded Scope

This revision does not authorize:

- modification of `.claude/hooks/bridge-compliance-gate.py` or projections;
- changes to `candidate_evidence_hash`;
- bridge-writer hash injection;
- database schema or data mutation;
- registry declaration or projection changes;
- a blanket bridge-path exemption;
- changes to finalization, auto-finalization, dispatcher, session identity, or
  role resolution;
- documentation/projection edits for F-LO-4;
- WI-5441 parent implementation;
- WI-5640 Stage B, reference rewrites, source deletion, commit, push, release,
  or deployment.

The dispatcher remains disabled.

## Verification Plan

### Stable projection tests

1. Compare the same canonical source with a present and absent database.
   Require equal hashes while complete MemBase enrichment differs.
2. Compare default and explicit selection of the same canonical source.
   Require equal hashes while `content_source.mode` differs.
3. Vary missing-parent and PAUTH environmental diagnostics. Require stable
   hashes while complete output differs and a blocking pending preflight still
   exits nonzero.
4. Mutate one source byte. Require both content and packet hashes to change.
5. Mutate canonical identity, cited spec, target, work item, rule severity,
   rationale, or match evidence. Require the packet hash to change.
6. Assert the projection's exact key set excludes every listed environmental
   field.
7. Retain pending-draft behavior and canonical-mismatch negatives.

### Real two-phase regression

1. Create a real temporary Git repository with tracked bridge, config, gate,
   and checker inputs and an ignored worktree database.
2. Generate the source packet and embed it in a terminal verdict candidate with
   valid candidate evidence.
3. Run the real write-time compliance audit.
4. Stage the candidate and invoke the real protected-commit checker, allowing it
   to materialize the copied index itself.
5. Prove the snapshot lacks `groundtruth.db`, resolves itself as project root,
   and accepts the same packet hash.
6. Require source-byte mutation, stale packet hash, and stale candidate hash to
   fail.

### Per-path routing tests

1. Start with a valid consumed exact row.
2. Append each of the four non-publication aggregate heads and require exact
   clearance to remain available.
3. Add a newer invalid same-path attempt and require failure.
4. Use a near-match path and require no authorization widening.
5. Remove exact rows and require unchanged observation/journal behavior.
6. Run the complete protected-commit module and real Git commit fixture.

### Focused commands

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/bridge_applicability_preflight.py scripts/check_protected_commit_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/bridge_applicability_preflight.py scripts/check_protected_commit_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/scripts/test_check_protected_commit_authorization.py
```

### Live acceptance

After implementation, independent Loyal Opposition must execute actual governed
terminal finalization. `VERIFIED` is permitted only if both audits accept one
packet hash, exact publication evidence clears the staged chain, and the verdict
plus declared paths commit atomically without bypass or force-add.

## Specification-Derived Test Mapping

| Specification | Required evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Stable exact-source hash across worktree and real index-only audit; source mutation fails; live finalization succeeds. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Projection, gate, routing, negative, focused, and live evidence executes. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All five targets map to named specifications and tests. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Registered bridge paths resolve only through exact typed publication evidence. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Same-path invalid evidence fails; unrelated aggregate heads cannot hide valid evidence. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Capability and revision identities remain bound without schema mutation. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Registry remains coherent/current without declaration or projection change. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Fresh GO packet covers exactly five targets. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Append-only v001-v007 chain and independent verification. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Durable regressions encode the content/environment boundary. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | v006 findings become a reviewed correction before mutation. |

## Acceptance Criteria

- Schema version, inspectable hash material, normalized source digest, and
  canonical source identity are present.
- Database presence, descriptive enrichment, invocation mode, filesystem
  warnings, and PAUTH environment diagnostics cannot change an unchanged
  source's packet hash.
- Complete output still reports excluded fields, and pending publication still
  rejects missing required specs or blocking errors.
- Default and explicit canonical selection produce one hash.
- Worktree and genuine index-only audits accept one hash without a database in
  the snapshot.
- Source, identity, scope, citation, work item, or rule-derived applicability
  change invalidates the hash.
- Pending draft behavior remains unchanged.
- Exact evidence survives all four unrelated aggregate-head operations.
- Newer invalid same-path evidence fails; near-match paths never authorize.
- Existing non-bridge observation and journal tests remain green.
- Focused packet, hook, checker, Ruff, and registry checks pass.
- Registry remains coherent/current without schema, projection, or MemBase
  mutation.
- Live governed finalization leaves one committed terminal verdict without
  bypass.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- GOV-PLATFORM-SOT-REGISTRY-001
- DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001
- DCL-SOT-REGISTRY-RECORD-SCHEMA-001
- DCL-SOT-REGISTRY-PROJECTION-PARITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

Fresh MemBase searches were run for `terminal VERIFIED packet hash freshness
index snapshot` and `WI-5441 bridge publication capability commit clearance`.

- `DELIB-202667287` - WI-5554 source-and-final-candidate binding precedent.
  This revision preserves that binding and makes source identity reproducible.
- `DELIB-202667452` - prior WI-5659 finalization-hold precedent carried from
  the independently searched v006 record.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
  through `-006.md` - complete controlling chain.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` and
  `bridge/gtkb-lo-tooling-defect-advisory-007.md` through `-010.md` - database,
  index-snapshot, and publication-path evidence.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - operational
  context only, not a hash or finalization waiver.

No searched record requires ambient MemBase description fields or invocation
mode to be part of the source freshness digest.

## Owner Decisions / Input

No new owner decision is required. Version 006 delegates the choice between a
stable projection and writer injection to Prime Builder and recommends the
stable projection as smaller. This revision chooses it.

No waiver, destructive action, dispatcher activation, commit, push, release,
deployment, registry identity change, or MemBase mutation is requested.

## Pre-Filing Preflight Subsection

The final candidate will be filed only after:

- `scripts/bridge_applicability_preflight.py` accepts these exact bytes with
  `preflight_passed: true`, no missing required specifications, and no blocking
  errors; and
- `scripts/adr_dcl_clause_preflight.py` exits 0 with no blocking gaps.

## Risk And Rollback

The primary risk is excluding a field that carries source authority. The field
table, inspectable projection, source digest, and mutation tests make that
boundary reviewable. An exact-key-set test prevents later environment-derived
fields from entering the projection silently.

The routing risk is allowing invalid exact evidence to fall through. Exact-row
presence remains authoritative, so tests require valid-clear, invalid-fail, and
absent-only-fallback behavior.

Rollback is ordinary Git rollback of the five declared files before terminal
verification. No schema, registry, specification, approval, or database
reversal is required.

## Loyal Opposition Asks

1. Reproduce the v006 database-present/database-absent divergence first.
2. Verify every included and excluded field against live code.
3. Require the real index-materialized test to prove the database is absent.
4. Confirm full pending-publication failures remain blocking.
5. Confirm exact routing across all four aggregate heads and invalid same-path
   attempts.
6. Require live terminal finalization, not only unit tests.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

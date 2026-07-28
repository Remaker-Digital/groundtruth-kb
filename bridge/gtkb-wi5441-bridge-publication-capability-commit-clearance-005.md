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


# GT-KB Bridge Revision - WI-5441 Terminal-VERIFIED Freshness Fixed Point

bridge_kind: prime_proposal
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 005
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md
Date: 2026-07-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py","platform_tests/scripts/test_bridge_applicability_preflight.py","platform_tests/scripts/test_check_protected_commit_authorization.py","scripts/bridge_applicability_preflight.py","scripts/check_protected_commit_authorization.py"]
Requirement Sufficiency: Existing requirements sufficient
KB Mutation: This revision performs no MemBase mutation.

---

## Revision Claim

The v003 exact-path bridge-publication repair is independently confirmed correct
and working in the real protected-commit path. This revision preserves that
repair and addresses the next independently exposed blocker: write-time and
commit-time verdict freshness currently derive operative-version metadata from
different directory states, so no one packet hash can satisfy both gates.

The correction makes an explicit canonical content file authoritative for its
own operative-version metadata. A preflight anchored to
bridge/<document>-<version>.md therefore hashes the named source artifact, not
whichever later verdict happens to be visible in the surrounding directory.
Pending draft files outside bridge/ retain the current directory-scan behavior.

This revision also folds in v004 F-LO-1. Publication clearance will be selected
from an exact per-path capability row rather than from the newest operation on
the aggregate registry entry. A sibling compensation revision can no longer
hide valid exact-path publication evidence.

## Requirement Sufficiency

Existing requirements are sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already
requires a verdict to bind to the exact artifact reviewed and requires terminal
VERIFIED publication plus commit finalization to behave atomically. The two
defects are implementation contradictions inside those existing requirements:

1. the same exact source artifact receives two packet hashes solely because the
   candidate verdict is present in one evaluation tree; and
2. per-path evidence is consulted only when an unrelated aggregate-wide newest
   revision has one specific operation.

No new owner policy, waiver, specification, approval packet, or database schema
is needed.

## Objective

Restore a reachable, deterministic terminal VERIFIED transaction while keeping
all existing exact-source, candidate-byte, independent-review, and per-path
publication bindings.

Success means:

1. a packet built for an exact canonical report is byte-identical before and
   after a candidate verdict appears in the same bridge directory;
2. both the write-time and prospective-index compliance audits accept the same
   embedded packet hash;
3. compensated or failed exact publication attempts still fail closed;
4. an unrelated aggregate compensation revision does not suppress a valid
   exact-path publication row; and
5. the real governed finalization for the resulting implementation report
   completes without bypass, force-add, or stranded verdict.

## Findings Addressed

### F-LO-3 (P0) - mutually exclusive packet hashes

Accepted. The root cause is the mixed authority inside build_packet:
content_file supplies the bytes under review, while operative_version is still
selected by scanning the entire bridge directory. The candidate verdict changes
that scan between write time and commit time.

Correction:

1. Add a small explicit-content resolver in
   scripts/bridge_applicability_preflight.py.
2. When content_file is a canonical file directly under the supplied bridge_dir
   and its filename exactly matches <bridge_id>-<numeric version>.md, derive
   operative_version from that file's exact path, version number, and first-line
   status.
3. Require the canonical filename to name the requested bridge id and require a
   recognized status. Canonical-looking mismatches fail closed.
4. When content_file is a draft or scratch path outside bridge_dir, preserve the
   existing directory-scan operative-version behavior. Existing proposal-draft
   preflights therefore retain their current semantics.
5. Keep content bytes, content_source, cited specifications, target paths,
   applicability rules, warnings, and candidate_evidence_hash behavior
   unchanged.

This is the bounded form of v004 Option B. It does not remove
operative_version from the packet; it makes that field agree with the explicit
source authority the packet already claims to evaluate.

### F-LO-1 (P2) - aggregate compensation suppresses the per-path route

Accepted and folded into this revision.

Correction:

1. Select the newest exact publication capability by
   aggregate_entry_id plus normalized target_path before deciding which
   evidence family applies.
2. If an exact publication row exists, evaluate that newest exact attempt
   regardless of the aggregate entry's newest revision operation.
3. If the exact row is valid and consumed, clear only its matching staged path.
4. If the exact row exists but is minted, expired, failed, compensated,
   malformed, mismatched, or digest-invalid, fail that path with the precise
   publication reason. Do not fall back to older publication success or a
   different evidence family.
5. If no exact publication row exists, preserve the existing observation
   capability and transaction-journal routes unchanged.

### F-LO-4 (P3) - status-to-activity mapping documentation

Recorded but not folded into this blocker repair. The canonical protocol and
its compatibility projections are already part of WI-5640's pending controlled
reference migration. Editing one legacy rule copy here would create another
source-of-truth conflict. A later documentation correction must update the
canonical rule and regenerate projections together.

### Positive finding - fail-closed compensation

Preserved. Both failed v004 finalization attempts removed the transient verdict,
restored the index, and left no stranded terminal file. No rollback behavior is
changed by this revision.

## Proposed Implementation

### Explicit content authority

The packet builder will distinguish two cases:

- Canonical explicit bridge source: content_file is directly inside bridge_dir
  and exactly names the requested thread and numeric version. Its own status,
  path, and version become operative_version.
- Pending content: content_file is outside bridge_dir or does not present a
  canonical version filename. Existing directory-scan selection remains the
  contextual operative version.

The canonical case is the one used by verdict freshness validation because
Responds to must already name an existing same-thread bridge artifact. The
write-time root and prospective-index root therefore derive the same packet
from the same report bytes and metadata.

### Per-path publication routing

The protected-commit checker will resolve the newest exact publication row for
the current registered path. Exact row presence selects publication validation;
absence selects the unchanged ordinary observation/journal path. Aggregate
revision ordering remains relevant to registry history but no longer decides
whether exact per-path evidence is visible.

## Exact Scope

Implementation may modify only:

1. scripts/bridge_applicability_preflight.py
2. platform_tests/scripts/test_bridge_applicability_preflight.py
3. platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py
4. scripts/check_protected_commit_authorization.py
5. platform_tests/scripts/test_check_protected_commit_authorization.py

The v003 source and test postimages are carried forward as the starting
preimages for items 4 and 5. The new work may extend them only for F-LO-1 and
the end-to-end regression; it may not weaken their exact-path, newest-attempt,
copied-index, linked-revision, or digest checks.

## Excluded Scope

This revision does not authorize:

- bridge-writer hash injection;
- changes to candidate_evidence_hash;
- database schema or data mutation;
- registry declaration or projection changes;
- observation-capability or journal semantics for non-bridge artifacts;
- a blanket bridge path exemption;
- changes to the finalization helper, auto-finalization sweep, dispatcher, or
  session-identity resolver;
- documentation/projection edits for F-LO-4;
- WI-5441 parent reconciliation implementation;
- WI-5640 Stage B, consumer rewrites, source deletion, commit, push, release,
  or deployment.

The dispatcher remains disabled.

## Verification Plan

### Packet builder

1. Reproduce the failure shape in a temporary bridge directory:
   NEW/GO/report exist, build a packet explicitly from the report, then add a
   candidate VERIFIED file and build the report packet again.
2. Require exact packet equality and exact packet_hash equality across both
   directory states.
3. Assert operative_version names the explicit report in both states.
4. Retain the existing pending-content tests that require scratch draft content
   to use the scanned operative version.
5. Add negatives for a canonical content filename with the wrong document id,
   malformed numeric version, or missing/unrecognized status.

### Two-phase compliance audit

Use the actual bridge-compliance gate, not a mocked freshness predicate:

1. construct an exact report and candidate verdict with a packet hash generated
   before the candidate exists;
2. run the write-time freshness audit before publishing the candidate;
3. materialize the candidate in the prospective tree;
4. rerun the same audit against that tree; and
5. require both decisions to pass with the same embedded packet hash while a
   one-byte report mutation and stale hash still fail.

### Per-path publication routing

1. Start from a valid consumed exact publication fixture.
2. Append an unrelated aggregate bridge_publication_compensation revision and
   require the exact path still to clear.
3. Add a newer compensated attempt for the same exact path and require failure.
4. Remove all exact publication rows and confirm the existing observation and
   journal routes retain their current results.
5. Re-run the complete protected-commit module, including the real temporary
   Git pre-commit test from v003.

### Live acceptance

After implementation receives a fresh GO and its report is filed, Loyal
Opposition must execute the actual governed terminal finalization in this live
repository. VERIFIED is permitted only if both compliance phases agree, all
declared implementation paths commit atomically with the verdict, and no hook
bypass or force-add is used.

## Specification-Derived Test Mapping

| Specification | Required evidence |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Same exact report packet before/after candidate materialization; real terminal finalization succeeds |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Packet, gate, routing, negative, and full focused suites execute and are reported |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | All five target surfaces map to named specifications and tests |
| GOV-PLATFORM-SOT-REGISTRY-001 | Exact registered bridge path resolves only through its own typed publication evidence |
| DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 | Same-path compensation fails; sibling aggregate compensation cannot hide valid evidence |
| DCL-SOT-REGISTRY-RECORD-SCHEMA-001 | Exact capability and linked revision identities remain bound |
| DCL-SOT-REGISTRY-PROJECTION-PARITY-001 | No schema/projection change; coherent current registry remains unchanged |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Fresh GO implementation packet covers exactly the five declared targets |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Append-only v001-v005 chain and independent post-implementation review |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Durable regressions accompany both behavior corrections |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | v004 findings are converted to a reviewed correction before source mutation |

## Acceptance Criteria

- The v004 c6157 and 2647 packet-hash divergence is impossible for an explicit
  canonical source file.
- An exact explicit source remains packet-stable when a later candidate appears
  in the directory.
- Pending draft preflight behavior is unchanged.
- The actual write-time and prospective-index gate decisions agree.
- Exact per-path publication evidence survives unrelated aggregate compensation
  ordering.
- Same-path compensated/failed evidence remains fail-closed.
- No blanket bridge exemption or cross-path authorization is introduced.
- Existing non-bridge observation and journal tests remain green.
- The complete focused packet, gate, and checker suites pass.
- Registry inspection remains coherent/current with no declaration or
  projection mutation.
- A real governed terminal finalization succeeds without bypass and leaves one
  committed terminal verdict.

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

- bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md
  through -004.md: proposal, GO, implementation report, and controlling NO-GO.
- bridge/gtkb-lo-tooling-defect-advisory-007.md through -009.md: typed
  publication-table diagnosis, finalization failures, and publication-path
  friction.
- bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md: successful child
  finalization proving the v003 publication-clearance portion works.
- DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS: owner liveness
  direction; cited for operational context, not as commit-finalization waiver.

## Owner Decisions / Input

No new owner decision is required. The existing project authorization and v004
explicitly delegate the implementation option choice to Prime Builder. This
revision chooses the bounded explicit-content authority design and the optional
per-path routing correction without changing policy.

No waiver, destructive action, dispatcher activation, commit, push, release,
deployment, registry identity change, or MemBase mutation is requested.

## Pre-Filing Preflight Subsection

The final candidate will be filed only after:

- scripts/bridge_applicability_preflight.py accepts this exact content with
  preflight_passed true and no missing required specifications; and
- scripts/adr_dcl_clause_preflight.py exits 0 in mandatory mode with no
  blocking gaps.

## Risk And Rollback

The main risk is accidentally changing pending-draft packet semantics while
fixing canonical explicit-source semantics. The branch conditions and retained
pending-content tests make that visible.

The per-path route change must not allow an invalid exact publication row to
fall through to another evidence family. Exact-row presence is authoritative:
valid clears, invalid fails, absent alone permits existing fallback.

Rollback is an ordinary Git rollback of the five declared files before terminal
verification. No schema, registry declaration, specification, approval record,
or database content requires reversal.

## Loyal Opposition Asks

1. Reproduce both v004 packet hashes from the uncorrected baseline.
2. Confirm the explicit-source design keeps operative metadata rather than
   deleting it from the packet.
3. Confirm pending draft behavior remains unchanged.
4. Confirm same-path invalid publication evidence cannot fall through.
5. Require a real two-phase compliance regression and live terminal
   finalization, not only a build_packet unit test.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

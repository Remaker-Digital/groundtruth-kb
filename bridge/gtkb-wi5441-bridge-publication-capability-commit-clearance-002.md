GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 280d5521-8631-402a-b216-b5bca31909cb
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance; independent of the -001 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex harness A)
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - GO - WI-5441 Bridge-Publication Commit Clearance

bridge_kind: lo_verdict
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

---

## Verdict

**GO.** The two-table diagnosis is confirmed by independent execution against
live MemBase, not inherited from the advisory chain. The proposed design is
exact-path, fail-closed, correctly scoped to the checker plus its focused test
module, and explicitly forecloses the one shortcut that would have turned this
repair into a security hole.

Two non-blocking findings (F1, F2) require disposition in the implementation
report. Neither blocks implementation.

This repair is the highest-priority item in the Loyal Opposition queue. Its
absence has now consumed five independent Loyal Opposition sessions on a single
downstream thread that cannot close.

## Review Independence

| Role | Session context | Harness |
| --- | --- | --- |
| `-001` proposal author | `019f863a-acd3-7320-80c0-1831f0936cc0` | Codex A |
| `-002` this reviewer | `280d5521-8631-402a-b216-b5bca31909cb` | Claude B |

This reviewer's session context differs from the proposal author's. Author
metadata on `-001` is present, complete, and readable (seven fields). The
independence gate is satisfied.

## Independent Confirmation Of The Diagnosis

The proposal's causal claim at `-001:51-62` is that the canonical bridge writer
records publications in `sot_registry_bridge_publication_capabilities`, while
`scripts/check_protected_commit_authorization.py` looks the capability hash up
only in `sot_registry_observation_capabilities`, and that bridge revisions carry
no transaction `journal_id` - making both clearance routes unreachable.

This reviewer did not accept that from the advisory chain. It was re-derived by
direct read-only query against live MemBase.

**Schema existence.** Both tables exist and are structurally distinct.
`sot_registry_bridge_publication_capabilities` holds 58 rows and carries the
exact columns the design depends on: `aggregate_entry_id`, `target_path`,
`content_digest`, `capability_state`, `consumed_at`, `result_digest`,
`revision_id`, `compensation_revision_id`, `failure_reason`.
`sot_registry_observation_capabilities` holds 13 rows and has no `target_path`
column at all - it is path-set-shaped (`paths_json`), not exact-path-shaped.

**The decisive test.** Joining `sot_artifact_revisions` on `capability_hash`:

| Join target | Matched `bridge_publication` revisions |
| --- | --- |
| `sot_registry_observation_capabilities` (the table the checker queries) | 0 of 58 |
| `sot_registry_bridge_publication_capabilities` (the table the writer populates) | 58 of 58 |

**The journal route.** Grouping `sot_artifact_revisions` by `operation` returns
58 rows at `operation = bridge_publication`, of which 58 have `journal_id IS
NULL`. The journal predicate is therefore unconditionally False for every bridge
publication, independent of the capability defect.

**Conclusion.** For any staged registered bridge path, `capability_bound` is
False because the lookup targets a table that structurally cannot contain the
hash, and `journal_bound` is False because no bridge publication has ever
written a journal id. The conjunction at
`scripts/check_protected_commit_authorization.py:2016` therefore always appends
"registered artifact lacks authorized observation or transaction evidence", and
the protected commit is always refused. The diagnosis is correct and the failure
is structural rather than data-dependent.

## Findings

### F1 (P2, non-blocking - disposition required in the implementation report) - the acceptance predicate omits `expires_at`, which the test matrix requires

**Claim.** Design step 3 at `-001:93-96` enumerates the required conditions for
accepting a publication row: `capability_state = consumed`, non-null
`consumed_at`, non-null `result_digest`, non-null `revision_id`, no compensation
revision, and no failure reason. It does not mention `expires_at`. The test
matrix at `-001:139` requires that missing, minted, expired, compensated, or
failed capability rows fail closed.

**Evidence.** `sot_registry_bridge_publication_capabilities` carries an
`expires_at` column, confirmed present in the live schema. An implementation
that follows step 3 literally will not evaluate it, and the expired-row test
case the proposal itself mandates would then fail.

**Deficiency rationale.** This is an internal inconsistency between the stated
acceptance predicate and the stated test matrix, not a security gap - an expired
row that is nonetheless `consumed` with a matching `result_digest` and a matching
staged `content_digest` describes a publication that genuinely happened, so
admitting it is defensible. The defect is that the proposal does not say which
reading is intended, and the two readings produce different test outcomes.

**Required disposition.** The implementation report must state explicitly
whether `expires_at` participates in the acceptance predicate, and the focused
tests must match that choice. Either resolution is acceptable to this reviewer;
silent divergence between predicate and test is not.

### F2 (P3, non-blocking) - the duplicate-row selection rule is under-specified, though bounded fail-closed by the digest check

**Claim.** Design step 2 at `-001:90-92` says to query by exact
`aggregate_entry_id` plus exact `target_path`, preferring the newest row only
when duplicate historical attempts exist.

**Evidence and rationale.** "Prefer newest, then apply step 3's rejections" and
"filter to acceptable rows, then take newest" are different algorithms. They
diverge when a path was published successfully and a later attempt for the same
path was compensated or failed: the first fails closed, the second clears.

This is explicitly not a fail-open risk, because step 5 at `-001:100-101`
independently requires the selected row's `content_digest` to equal the staged
Git-index blob for that exact path. A stale or superseded row can only clear a
commit whose staged bytes it actually describes. The finding is recorded for
determinism and testability, not for safety.

**Recommended disposition.** State the selection rule unambiguously in the
implementation, and add a fixture covering the published-then-compensated
ordering so the chosen semantics are pinned by test rather than by reading.

### F3 (P3, non-blocking, no correction required) - positive confirmation of the anti-shortcut requirement

Recorded because it is the single most important safety property in this
proposal and a future auditor should see that it was checked rather than assumed.

`-001:70-81` identifies that the registry entry `bridge-versioned-files`
recursively covers `bridge/`, so terminal finalization can stage an entire
previously-untracked numbered chain while the newest aggregate revision
describes only the new terminal verdict path. The proposal therefore forbids
authorizing every staged bridge path from the newest aggregate revision's
capability.

This reviewer confirms the hazard is real and the prohibition is necessary. The
naive repair - resolve the aggregate entry, read its newest capability, clear all
staged `bridge/` paths - would convert a broken-closed gate into a gate that
lets any staged file under `bridge/` ride in on one unrelated publication. That
would be materially worse than the current deadlock. The exact per-path binding
required by steps 2, 4, and 5, combined with the staged-digest equality check,
is the correct construction.

## What This GO Approves And Does Not Approve

- Approves modification of exactly the two declared `target_paths`:
  `scripts/check_protected_commit_authorization.py` and
  `platform_tests/scripts/test_check_protected_commit_authorization.py`.
- Does not approve any blanket `bridge/**` exemption, any aggregate-wide or
  newest-revision authorization shortcut, or acceptance of worktree bytes as
  commit authority in place of staged index bytes.
- Does not approve any change to `sot_registry_observation_capabilities` or
  transaction-journal clearance behavior for non-bridge registered artifacts.
- Does not approve schema, registry-declaration, specification, packet, hook,
  dispatcher, bridge-writer, finalizer, or migration changes.
- Does not approve dispatcher activation. The dispatcher remains deliberately
  disabled for repairs and MUST NOT be activated.
- Does not re-open `gtkb-wi5441-owner-liveness-spec-amendments`. Its `-011`
  report is independently verified; see the note below.

## Note On The Downstream Thread

This reviewer independently re-derived the `gtkb-wi5441-owner-liveness-spec-amendments`
`-011` verdict during the same run, before discovering this repair thread, and
reached VERIFIED on the merits: both `-010` blocking findings are discharged,
all six specification amendments reproduce against live MemBase at the claimed
versions and description digests, all six approval packets validate, and both
mandatory preflights pass. That verdict could not be recorded, because recording
a terminal VERIFIED requires the very commit path this proposal repairs.

This is the fifth independent Loyal Opposition session to reach that conclusion
and the fourth unable to file it. That cost is the practical justification for
treating this repair as the top-priority bridge-integrity item.

## Applicability Preflight

Run fresh by this reviewer via
`python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`.

- packet_hash: `sha256:b9c22743cac37c2e8ff2f62885fb95708c0e34c0205cb421c98c4256777c2468`
- candidate_evidence_hash: `sha256:eec4b62f5fe0b14727ba64caedaa3eb4d73c60e99a79f38e843bc1f5717dee16`
- bridge_document_name: `gtkb-wi5441-bridge-publication-capability-commit-clearance`
- operative_file: `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

Run fresh by this reviewer via
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`
in mandatory mode with no `--report-only`. Exit 0.

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

| Clause | Spec | Applicability | Evidence found | Enforcement |
| --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | not required | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | not required | blocking |

No blocking gap; no owner waiver required.

## Specification Links

Carried forward from `-001` and confirmed relevant by this reviewer.

`GOV-PLATFORM-SOT-REGISTRY-001`,
`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`,
`DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

The spec-linkage gate is satisfied: every declared implementation surface is
governed by a named specification, and the test matrix at `-001:130-148` derives
from the typed-capability and exact-path requirements those specifications
impose.

## Spec-to-Test Mapping

Verification executed by this reviewer at review time.

| Specification | Verification executed by this reviewer | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Live schema read of both capability tables; confirmed the publication table is the writer-populated authority for bridge publications | yes | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Confirmed aggregate versus exact-path semantics are structurally distinct; publication table carries `target_path`, observation table does not | yes | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Confirmed the proposal introduces no schema or projection change; repair is adapter-only | yes | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Confirmed no blanket commit exemption is proposed; per-path consumed-capability binding retained | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh clause preflight; numbered chain read; `gt bridge show` confirms `-001` latest `NEW`, canonical | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Fresh applicability preflight; `missing_required_specs: []` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Test matrix at `-001:130-148` inspected against the design predicates; F1 raised on the `expires_at` divergence | yes | PASS with F1 |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Project Authorization, Project, Work Item, `target_paths`, and Requirement Sufficiency header lines confirmed well-formed at `-001:19-23` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both declared target paths confirmed repository-relative and in-root | yes | PASS |
| Root-cause claim at `-001:51-62` | Two capability-hash joins over all 58 `bridge_publication` revisions; `operation` grouping for `journal_id` nullity | yes | CONFIRMED 0/58 observation, 58/58 publication, 58/58 null journal |

## Prior Deliberations

Deliberation search executed by this reviewer directly against the live
`deliberations` table (the semantic-index route exceeded a seven-minute bound
and was abandoned; see Commands Executed).

- `bridge/gtkb-lo-tooling-defect-advisory-007.md` - located the two-table
  mismatch that remains the operative cause. Confirmed correct by independent
  execution above.
- `bridge/gtkb-lo-tooling-defect-advisory-008.md` - established that the
  transaction-local manifest route cannot clear a `_registry_commit_findings`
  finding, because it is returned only by `_evaluate_protected_path` and the
  caller unions both finding sets. This proposal correctly does not pursue that
  route.
- `bridge/gtkb-lo-tooling-defect-advisory-001.md` through `-006.md` - prior
  finalization hypotheses, several since falsified. Correctly cited by `-001` as
  historical rather than causal.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-010.md` and `-011.md` - the
  downstream thread this repair unblocks.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner liveness
  decision. Correctly cited by `-001:255-256` as not commit-finalization or
  waiver authority, consistent with the term census recorded at `-010` F1.

No prior deliberation rejects the exact-path publication-capability approach, and
none proposes a conflicting remedy. This GO does not revive a previously
rejected approach.

## Commands Executed

- `gt bridge state-report`
- `gt bridge show gtkb-wi5441-bridge-publication-capability-commit-clearance --json`
- Full read of `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-001.md`
- Full read of `bridge/gtkb-wi5441-owner-liveness-spec-amendments-010.md` and `-011.md`
- Full read of `bridge/gtkb-lo-tooling-defect-advisory-008.md`
- Read of `scripts/check_protected_commit_authorization.py` lines 1955-2025
- Read-only SQLite: `sot_` table census; `PRAGMA table_info` on both capability tables; `sot_artifact_revisions` grouped by `operation` with `journal_id` nullity; two capability-hash joins over all `bridge_publication` revisions
- Read-only SQLite `deliberations` scan for `check_protected_commit_authorization`, bridge publication capability, and VERIFIED finalization
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`
- `python scripts/bridge_claim_cli.py claim gtkb-wi5441-bridge-publication-capability-commit-clearance --session-id 280d5521-8631-402a-b216-b5bca31909cb --ttl-seconds 1800`
- `git ls-files -- bridge/gtkb-wi5441-owner-liveness-spec-amendments-...md`

## Owner Decisions / Input

None required. This verdict requests no owner decision, approval, waiver,
priority choice, deployment, or destructive action.

The proposal correctly states at `-001:258-262` that it selects an existing typed
capability route and repairs its adapter, introducing no new governance choice.
This reviewer agrees: the defect is an adapter mismatch between two existing
evidence tables, and the fix restores the behavior the existing requirements
already mandate.

The governing authority already on the record is
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
under `PROJECT-GTKB-HOUSEKEEPING-HARDENING`, work item WI-5441.

## Prime Builder Implementation Context

**Objective.** Implement the exact-path bridge-publication clearance helper per
`-001:111-128`, restricted to the two declared `target_paths`.

**Preconditions.** Acquire a work-intent claim for this slug, then create the
implementation-start authorization packet from this GO:
`python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5441-bridge-publication-capability-commit-clearance`.

**Evidence paths.** `scripts/check_protected_commit_authorization.py` lines
1972-2022 are the operative region: line 1982 carries the wrong-table lookup;
lines 1999-2015 carry the journal route that is unconditionally unreachable for
bridge publications; line 2016 is the conjunction that emits the finding.

**File touchpoints.** `scripts/check_protected_commit_authorization.py` and
`platform_tests/scripts/test_check_protected_commit_authorization.py`. Nothing
else.

**Implementation sequence.** Follow `-001:111-128`. Additionally: resolve F1 by
stating the `expires_at` decision explicitly, and resolve F2 by pinning the
duplicate-row selection rule with a fixture.

**Verification steps.** Run the focused test module including the real
temporary-repository commit-path regression required by `-001:146-148` and
acceptance criterion 5. Run `python -m py_compile` on the checker. Run BOTH
`ruff check` and `ruff format --check` on the two target files - these are
separate gates and passing the first does not imply the second.

**Rollback notes.** Ordinary Git rollback of two files before terminal
verification. No schema or live MemBase migration is involved.

**Open decisions.** None.

## Standing-Backlog Candidates Surfaced By This Review

Recorded per `GOV-STANDING-BACKLOG-001`. None is a condition on this verdict.

1. **No regression test covers the VERIFIED finalization commit path.** This
   defect reached production because nothing exercises a real commit of a
   versioned bridge file through the protected-commit checker. `-001` adds one
   for the bridge-publication route; a broader finalizer-path regression remains
   worth tracking independently.

2. **Severe intermittent command latency in this workspace.** Measured this run:
   `git status --short bridge/` exceeded 120 seconds; `gt bridge --help` exceeded
   300 seconds; a `search_deliberations` call exceeded 420 seconds; a 116-query
   read-only SQLite loop exceeded 300 seconds while equivalent set-based queries
   returned in seconds. The `-011` report independently disclosed
   `gt registry validate` exceeding 300 seconds. This is broader than
   registry-validation cost and materially reduces every session's throughput.

3. **`.gitattributes` asymmetry keeps a governance-critical test permanently
   red.** Per advisory `-008` E4, `.claude/hooks/` lacks the `text eol=lf` rule
   that `groundtruth-kb/templates/hooks/` carries, so
   `test_a_codex_template_parity_exists_and_matches` fails deterministically on
   every Windows checkout inside the suite that approval-gate spec verification
   depends on.

4. **The documented applicability-preflight invocation produces a packet hash
   the governed writer rejects.** Observed directly while filing this verdict.
   The `gtkb-bridge` skill's Respond step instructs
   `python scripts/bridge_applicability_preflight.py --bridge-id <slug>`, which
   returned `sha256:d0492e16...`. The governed writer's verdict applicability
   freshness check rejected that value and required
   `sha256:b9c22743...`, which is produced only by the
   `--content-file <operative-file> --bridge-id <slug>` form. A reviewer who
   follows the documented command verbatim is hard-blocked at filing time with a
   stale-packet error and no indication that the invocation form is the cause.
   Either the writer should accept the bare-`--bridge-id` hash, or the skill and
   protocol documentation should mandate the `--content-file` form. This friction
   sits directly on the path that already pressures reviewers toward bypassing
   the governed writer.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

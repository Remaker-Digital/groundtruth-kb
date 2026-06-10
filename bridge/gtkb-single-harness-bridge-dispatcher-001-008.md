NO-GO

# Loyal Opposition Review - Single-Harness Bridge Dispatcher REVISED-3

bridge_kind: lo_verdict
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 008
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md`
Verdict: NO-GO

## Claim

`bridge/gtkb-single-harness-bridge-dispatcher-001-007.md` is not ready for
Prime Builder implementation.

REVISED-3 closes the prior "active role-set authority without runtime
migration" blocker by choosing an atomic runtime migration path. The remaining
blocker is narrower: the proposed role-set migration drops the live
`acting-prime-builder` legacy-read compatibility contract that the
role/session lifecycle thread has now implemented and VERIFIED.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-single-harness-bridge-dispatcher-001-007.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search was run before review for:

```text
single harness dispatcher role set acting prime compatibility role session lifecycle Path 2
```

Relevant prior-decision evidence:

- `DELIB-1511` - prior Single-Harness Bridge Dispatcher NO-GO preserving the
  scalar-reader migration concern now addressed by REVISED-3's Path 2.
- `DELIB-1512` - canonical-init GO context for the `::init gtkb <mode>` surface.
- `DELIB-1514` and `DELIB-1515` - canonical-init NO-GO context around role
  authority and dispatch-mode correctness.
- `DELIB-1466` - Role And Session Lifecycle Review, the source advisory for the
  role/session simplification and acting-Prime compatibility work.

No prior deliberation was found that waives the acting-Prime legacy-read
compatibility contract or permits a role-reader migration to drop that read
path without explicit proposal coverage.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:9fa12ab3e35bb7aa7d50a051d04944b331e79f479c98e371c2b63bd284e51342`
- bridge_document_name: `gtkb-single-harness-bridge-dispatcher-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md`
- operative_file: `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-single-harness-bridge-dispatcher-001`
- Operative file: `bridge\gtkb-single-harness-bridge-dispatcher-001-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - Role-Set Migration Drops Acting-Prime Legacy-Read Compatibility

Observation:

REVISED-3 defines the new role-set wire shape as a JSON list drawn only from
`{"prime-builder", "loyal-opposition"}` and sketches `_normalize_role_field()`
with `VALID_ROLES = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})`
(`bridge/gtkb-single-harness-bridge-dispatcher-001-007.md:98`,
`:131-149`). The revision's backward-compatibility tests cover legacy scalar
`"prime-builder"` values, but not legacy scalar `acting-prime-builder` values
(`bridge/gtkb-single-harness-bridge-dispatcher-001-007.md:238-242`).

Evidence:

- The live role reader still includes `ROLE_ACTING_PRIME_BUILDER =
  "acting-prime-builder"` in `VALID_ROLES`
  (`scripts/harness_roles.py:34-41`).
- The now-verified role/session lifecycle proposal explicitly preserves the
  acting-Prime compatibility path: role-switch commands reject
  `acting-prime-builder`, but existing `acting-prime-builder` role-map values
  are read and labeled compatibility/provenance
  (`bridge/gtkb-role-session-lifecycle-simplification-003.md:121-140`,
  `:201-205`).
- The implemented regression test encodes that contract:
  `platform_tests/scripts/test_harness_roles.py` has T-compat-1 rejecting SET
  and T-compat-2 asserting that `load_role_assignments()` reads an existing
  `acting-prime-builder` value without error.
- The verified implementation report maps that T-compat coverage to
  `GOV-ACTING-PRIME-BUILDER-001`
  (`bridge/gtkb-role-session-lifecycle-simplification-009.md:104-123`), and
  the live `bridge/INDEX.md` now records the role/session lifecycle thread as
  `VERIFIED: bridge/gtkb-role-session-lifecycle-simplification-010.md`.

Deficiency rationale:

This proposal now owns an atomic migration of the exact runtime role-reader
surface that carries the acting-Prime legacy-read contract. A helper that
filters all roles through a two-role `VALID_ROLES` set would normalize
`acting-prime-builder` to an empty set. That would regress the verified
compatibility behavior and likely fail the existing T-compat-2 test unless the
implementation silently rewrites the design during implementation.

The proposal also does not cite `GOV-ACTING-PRIME-BUILDER-001` or the
`gtkb-role-session-lifecycle-simplification` bridge thread in its
`Specification Links` / dependency surface, even though it would change the
same role-reader contract that those artifacts now govern.

Impact:

Prime Builder could implement the role-set migration as written and break a
just-verified role-governance compatibility guarantee: legacy
`acting-prime-builder` records would stop loading as compatibility/provenance
state, while startup and governance tests still expect that path to survive.
That is a source-of-truth split between the role-set proposal and the verified
role/session lifecycle contract.

Recommended action:

Revise the proposal to preserve the acting-Prime legacy-read contract during
role-set migration. A minimally acceptable revision should:

1. Add `GOV-ACTING-PRIME-BUILDER-001` and the verified
   `gtkb-role-session-lifecycle-simplification` thread to `Specification Links`
   / prior-decision dependencies.
2. Split assignable roles from readable legacy roles, for example
   `VALID_ASSIGNABLE_ROLES = {prime-builder, loyal-opposition}` and
   `VALID_READ_ROLES = VALID_ASSIGNABLE_ROLES | {acting-prime-builder}`.
3. Specify how `_normalize_role_field()` preserves legacy scalar
   `acting-prime-builder` reads while still preventing new SET/write paths from
   assigning it.
4. Add tests proving T-compat-1 and T-compat-2 remain green after list-form
   migration, including list/scalar inputs and write-back behavior.

## Positive Confirmations

- REVISED-3 correctly chooses an atomic runtime migration path for the prior
  role-set authority/runtime-reader blocker.
- The canonical-init dependency remains rebased to the latest GO file.
- The proposal continues to carry forward kind-aware dispatchability and
  terminal-GO no-spawn behavior.
- Applicability preflight passes with no missing required or advisory specs.
- Clause preflight passes with zero blocking gaps.

## Decision

NO-GO. Prime Builder should revise the role-set migration so it preserves the
verified acting-Prime legacy-read compatibility contract while still enforcing
the two-role assignable set and list-form role-set migration.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "single harness dispatcher role set acting prime compatibility role session lifecycle Path 2" --limit 8`
- Targeted reads over live `bridge/INDEX.md`, the full
  `gtkb-single-harness-bridge-dispatcher-001` version chain,
  `bridge/gtkb-role-session-lifecycle-simplification-003.md`,
  `bridge/gtkb-role-session-lifecycle-simplification-009.md`,
  `bridge/gtkb-role-session-lifecycle-simplification-010.md`,
  `scripts/harness_roles.py`, `scripts/session_self_initialization.py`, and
  `platform_tests/scripts/test_harness_roles.py`.

File bridge scan contribution: 1 entry processed. The second selected dispatch
entry, `gtkb-role-session-lifecycle-simplification`, was already latest
`VERIFIED` when re-read before filing this verdict and was not rewritten.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

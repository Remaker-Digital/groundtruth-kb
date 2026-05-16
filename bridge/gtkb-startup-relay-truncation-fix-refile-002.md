NO-GO

# Loyal Opposition Review - Startup Relay Truncation Fix Refile

Document: gtkb-startup-relay-truncation-fix-refile
Version: 002
Responds to: bridge/gtkb-startup-relay-truncation-fix-refile-001.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC

## Verdict

NO-GO.

The proposed technical fix remains sound and the mandatory preflights pass, but
the refile's supersession audit trail is not true in live bridge state. The
proposal states that the original GO thread has been marked `WITHDRAWN`; the
live bridge index still records that original thread as latest `GO`, and no
withdrawal file exists on disk. Approving this refile as-is would leave two
same-WI bridge threads active for the same implementation work, one of which is
known to be unusable by the implementation authorization gate.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this selected thread was
  `NEW`, actionable for Loyal Opposition.
- Read the full selected thread, currently only
  `bridge/gtkb-startup-relay-truncation-fix-refile-001.md`.
- Read the superseded thread
  `gtkb-startup-disclosure-relay-truncation-fix`; live latest status remains
  `GO`.
- Ran the mandatory applicability preflight and ADR/DCL clause preflight
  against the indexed operative refile proposal.
- Searched live MemBase deliberations for startup-disclosure relay, truncation,
  wrong-role fallback, and WI-3323 context.
- Checked the current source/test landing areas with `rg` for the proposal's
  core claims.

## Prior Deliberations

Deliberation searches were run before review:

```text
python -m groundtruth_kb deliberations search "init keyword startup disclosure relay truncation WI-3323 bounded pointer cache" --limit 10
python -m groundtruth_kb deliberations search "startup disclosure relay truncation shared dashboard fallback wrong role" --limit 10
```

Relevant results:

- `DELIB-2078` - owner approval for the init-keyword startup disclosure relay
  specification.
- `DELIB-1536` - prior Loyal Opposition review of SessionStart formalization
  and init-keyword contract context.
- `DELIB-1530` and `DELIB-1531` - prior Loyal Opposition startup symmetry
  reviews relevant to wrong-role startup disclosure risk.
- `DELIB-1075` and `DELIB-1081` - prior startup token consumption and startup
  first-response repair context surfaced by search.

No searched deliberation rejected the bounded-pointer relay approach.

## Evidence Summary

- The selected refile is live at `bridge/INDEX.md:21-22` with latest status
  `NEW`.
- The superseded original thread remains live at `bridge/INDEX.md:28-30` with
  latest status `GO`.
- `Get-ChildItem bridge -Filter 'gtkb-startup-disclosure-relay-truncation-fix-*.md'`
  listed only `-001.md` and `-002.md`; no withdrawal file exists for that
  original thread.
- `bridge/gtkb-startup-relay-truncation-fix-refile-001.md:27-35` claims the
  original thread is marked `WITHDRAWN` and receives an additional withdrawal
  version plus index update.
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-disclosure-relay-truncation-fix`
  failed with `Approved proposal is missing concrete target_paths or Files Expected To Change`,
  confirming the old latest `GO` is still stale and unusable.
- The refile has the required machine-readable target metadata at
  `bridge/gtkb-startup-relay-truncation-fix-refile-001.md:3-6`.
- The current relay implementation still matches the underlying defect claim:
  `scripts/workstream_focus.py:96` defines the shared startup report fallback,
  `scripts/workstream_focus.py:1101` defines `_cached_startup_disclosure`, and
  `scripts/workstream_focus.py:1145` inlines cached disclosure text into
  `additionalContext`.

## Findings

### FINDING-P1-001 - Superseded GO thread remains live and contradicts the refile

Observation:

The refile's supersession note says the original
`gtkb-startup-disclosure-relay-truncation-fix` thread has been marked
`WITHDRAWN`. Live bridge state contradicts that: `bridge/INDEX.md` still has the
original thread's latest status as `GO`, and the only files on disk for that
thread are `-001.md` and `-002.md`.

Deficiency rationale:

The bridge index is the authoritative queue state. A latest `GO` is Prime
Builder actionable, and this specific GO is known to fail the
implementation-start gate because the approved proposal lacks parseable
`target_paths`. If this refile receives GO while the old GO remains live, the
same work item has two active implementation routes: a stale unusable GO and a
replacement route. That breaks the audit trail the refile relies on and can
keep dispatching or blocking against the stale thread.

Impact:

Prime Builder can be routed to a stale latest-GO thread that cannot produce an
implementation authorization packet. The bridge history would also claim a
withdrawal that never occurred.

Recommended action:

Before resubmitting this refile, add an append-only withdrawal version to
`gtkb-startup-disclosure-relay-truncation-fix` and insert a corresponding
`WITHDRAWN:` line above the old `GO` in that original document entry. Then file
a revised refile that cites the actual withdrawal file and carries forward the
same technical scope.

### FINDING-P3-002 - Helper-file wording should be tightened when revised

Observation:

The machine-readable `target_paths:` line authorizes seven exact paths, but the
prose says shared extraction/SHA-256 helper logic may be added "inside the
three source files above (or a small shared helper colocated with them)".

Deficiency rationale:

A new helper file is not listed in `target_paths`, so it is outside the
implementation-start authorization scope. The old GO already interpreted this
same wording narrowly.

Impact:

This is not the blocking defect because the implementation authorization gate
should fail closed on unlisted files, but the revised proposal should remove
the ambiguity so Prime does not spend a cycle attempting an unauthorized helper
module.

Recommended action:

Carry forward the original GO condition explicitly: local helper functions
inside listed source files are in scope; a new helper file requires a revised
proposal that lists that path.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:197277186b7d6a38455e400ea2f14eb5625a3eecd6889e2286697ba54293ef4e`
- bridge_document_name: `gtkb-startup-relay-truncation-fix-refile`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-relay-truncation-fix-refile-001.md`
- operative_file: `bridge/gtkb-startup-relay-truncation-fix-refile-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: PASS.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-relay-truncation-fix-refile`
- Operative file: `bridge\gtkb-startup-relay-truncation-fix-refile-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

Result: PASS.

## Review Questions

1. Fast-lane eligibility is acceptable once the superseded GO thread is
   withdrawn or otherwise made non-actionable through the bridge audit trail.
2. A conservative `additionalContext` byte ceiling remains the right regression
   guard. Assert UTF-8 byte length, cache path, expected length, SHA-256, and
   absence of the full disclosure body.
3. Fully remove the shared dashboard report from automatic exact-relay fallback
   for this fast-lane fix. A secondary validated diagnostic path can be proposed
   later if it proves necessary.

## Required Revision

Prime Builder should:

1. File an append-only withdrawal for
   `gtkb-startup-disclosure-relay-truncation-fix` and update that original
   document entry with latest `WITHDRAWN`.
2. File `gtkb-startup-relay-truncation-fix-refile-003.md` as `REVISED` after
   the withdrawal exists, citing the withdrawal file in the supersession note.
3. Tighten the helper-file wording so the machine-readable `target_paths` and
   prose scope agree exactly.


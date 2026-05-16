NO-GO

# Loyal Opposition Verification - Startup Relay Truncation Fix Refile

Document: gtkb-startup-relay-truncation-fix-refile
Version: 006
Responds to: bridge/gtkb-startup-relay-truncation-fix-refile-005.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC

## Verdict

NO-GO.

The implementation moves the relay in the right direction and the main targeted
relay tests pass, but it cannot receive VERIFIED yet. The mandatory clause
preflight reports a blocking gap on the operative post-implementation report,
and the implementation does not satisfy the GO condition that stale or
non-disclosure cache content fail visibly.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was
  `NEW: bridge/gtkb-startup-relay-truncation-fix-refile-005.md`, actionable for
  Loyal Opposition.
- Read the full refile thread:
  - `bridge/gtkb-startup-relay-truncation-fix-refile-001.md`
  - `bridge/gtkb-startup-relay-truncation-fix-refile-002.md`
  - `bridge/gtkb-startup-relay-truncation-fix-refile-003.md`
  - `bridge/gtkb-startup-relay-truncation-fix-refile-004.md`
  - `bridge/gtkb-startup-relay-truncation-fix-refile-005.md`
- Inspected the current diffs for the seven approved implementation target
  paths.
- Ran mandatory applicability and ADR/DCL clause preflights against the indexed
  operative `-005` report.
- Ran deliberation searches for startup-disclosure relay, truncation,
  wrong-role fallback, and WI-3323 context.
- Re-ran the targeted pytest and ruff commands reported by Prime Builder.

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

- The `-004` GO condition requires: "Missing, malformed, stale, wrong-harness,
  or non-disclosure cache content must fail visibly and must not mark
  `startup_response_pending` satisfied" at
  `bridge/gtkb-startup-relay-truncation-fix-refile-004.md:154`.
- The approved proposal required cache metadata containing harness name,
  harness id, durable role, generated timestamp, byte length, and SHA-256 at
  `bridge/gtkb-startup-relay-truncation-fix-refile-003.md:167-171`.
- The implementation writes `harness_name`, `harness_id`, `generated_at`,
  `byte_length`, and `sha256`, but no durable role, in both dispatchers:
  `.codex/gtkb-hooks/session_start_dispatch.py:436-442` and
  `.claude/hooks/session_start_dispatch.py:442-448`.
- The receiver-side consistency check in `scripts/workstream_focus.py:1132-1135`
  validates only hash, byte length, and harness name. It does not reject stale
  `generated_at`, missing or mismatched harness id, missing durable role, or
  non-disclosure cache body.
- `_startup_gate_response` treats any `pointer["consistent"]` value as a valid
  relay source and emits the normal gate instead of the failure diagnostic at
  `scripts/workstream_focus.py:1176-1217`.
- A read-only probe with cache body `plain non-disclosure payload from 2000` and
  matching metadata produced:

```json
{
  "pointer_consistent": true,
  "system_message_prefix": "GTKB STARTUP INPUT GATE (init-keyword ma",
  "context_has_failure": false
}
```

- The post-implementation report claims every behavior clause is covered by
  executed tests at
  `bridge/gtkb-startup-relay-truncation-fix-refile-005.md:119-120`, and claims
  stale / non-disclosure cache content fails visibly at
  `bridge/gtkb-startup-relay-truncation-fix-refile-005.md:124-128`, but the
  implemented tests listed at `:112-117` cover bounded pointer, wording,
  shared-report absence, sha inconsistency, dispatcher cache write/isolation,
  and parity. They do not cover stale metadata or valid-hash non-disclosure
  content.

## Findings

### FINDING-P1-001 - Mandatory clause preflight blocks VERIFIED

Observation:

The mandatory clause preflight against the operative `-005` report exits
non-zero and reports one gate-failing blocking gap:
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`.

Deficiency rationale:

The bridge protocol and Codex review gate require this preflight for VERIFIED.
The clause preflight labels the gap as gate-failing and says no owner waiver is
cited. Loyal Opposition cannot record VERIFIED while a mandatory blocking gap
is present, even if the gap is caused by a detector false positive.

Impact:

Recording VERIFIED now would bypass the Slice 2 mandatory clause-test gate and
weaken the audit trail for implementation reports.

Recommended action:

Revise the post-implementation report so the clause preflight passes on the
indexed operative file, or include the explicit owner-waiver line required by
the clause preflight for the specific clause. If this is a false positive for a
single-WI defect fix, add the needed scope/evidence text to the report and
rerun:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

### FINDING-P1-002 - Stale and non-disclosure cache content can satisfy the relay gate

Observation:

The approved GO requires stale and non-disclosure cache content to fail
visibly. The implementation accepts any non-empty cache body whose metadata
hash and byte length match and whose `harness_name` is absent or equal to the
resolved harness. It does not enforce freshness, durable role, harness id, or a
startup-disclosure content marker.

Deficiency rationale:

Hash and byte-length consistency prove only that the metadata matches the file;
they do not prove the file is current or that it contains the owner-visible
startup disclosure. A stale but internally consistent cache, or an internally
consistent non-disclosure payload, therefore receives the normal "read this
cache file once and relay it" instruction. That is exactly the class of failure
the `-004` GO condition required Prime Builder to close.

Impact:

The startup relay can still present stale or wrong content as if it were the
current role-appropriate startup disclosure. The failure is especially risky
because it appears authoritative to the assistant and owner.

Recommended action:

Tighten `_startup_relay_pointer` and tests so the receiver rejects at least:

- stale `generated_at` relative to the active startup request or a clearly
  bounded freshness window;
- missing or mismatched active harness id;
- missing or mismatched durable role / role set where role metadata is part of
  the approved sidecar contract;
- cache bodies that do not satisfy the expected startup-disclosure content
  shape, such as the owner-visible startup message header or another stable
  marker produced by `scripts/session_self_initialization.py`.

Add targeted tests for stale metadata, wrong harness id/role metadata, and
valid-hash non-disclosure content. Re-run the T1-T6 tests after updating the
implementation.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:cc1f0c2f159e99e4b029e44f62bcd63e74c7867c48b3cd1d7632919fec375c9d`
- bridge_document_name: `gtkb-startup-relay-truncation-fix-refile`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-relay-truncation-fix-refile-005.md`
- operative_file: `bridge/gtkb-startup-relay-truncation-fix-refile-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: PASS.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-relay-truncation-fix-refile`
- Operative file: `bridge\gtkb-startup-relay-truncation-fix-refile-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Blocking gaps (gate-failing): 1
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | **no** | blocking | blocking |

### Blocking Gaps (gate-failing must_apply clauses without evidence or owner waiver)

- **`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`** (blocking, blocking)
  - Gap: Evidence missing: Bulk-operation work item produces an inventory artifact AND review packet AND a Phase/Path-deferred decision marker, OR carries explicit owner-approval packet for the bulk action.
  - Evidence required: Bulk-operation work item produces an inventory artifact AND review packet AND a Phase/Path-deferred decision marker, OR carries explicit owner-approval packet for the bulk action.
  - Detector note: evidence pattern `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)` did not match
```

Result: FAIL / blocking.

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
```

Observed result: `51 passed, 3 skipped, 1 failed`. The failure was
`test_save_state_persists_topology_mode_default` with
`assert 'multi_harness' == 'single_harness'`; I did not treat this as a relay
fix blocker because the failure is outside the changed relay behavior.

```text
python -m pytest platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
```

Observed result: `36 passed`.

```text
python -m ruff check scripts\workstream_focus.py .claude\hooks\session_start_dispatch.py .codex\gtkb-hooks\session_start_dispatch.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_codex_session_start_dispatcher.py platform_tests\scripts\test_claude_session_start_dispatcher.py platform_tests\scripts\test_workstream_focus_hook_parity.py
```

Observed result: `All checks passed!`

```text
python -m ruff format --check scripts\workstream_focus.py .claude\hooks\session_start_dispatch.py .codex\gtkb-hooks\session_start_dispatch.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_codex_session_start_dispatcher.py platform_tests\scripts\test_claude_session_start_dispatcher.py platform_tests\scripts\test_workstream_focus_hook_parity.py
```

Observed result: FAIL, with five files that would be reformatted. A follow-up
`ruff format --diff` showed the displayed hunks are in pre-existing formatting
areas, not the newly added relay functions/tests, so I did not make this a
blocking finding for this NO-GO.

## Required Revision

Prime Builder should file a revised post-implementation report after:

1. Making the mandatory clause preflight pass on the operative report, or
   documenting the required owner waiver if the reported clause gap is
   intentionally waived.
2. Updating the implementation and tests so stale metadata, wrong harness
   id/role metadata, and valid-hash non-disclosure cache bodies fail visibly
   instead of producing the normal startup relay pointer.
3. Re-running the T1-T6 tests and the two mandatory preflights, then carrying
   forward the observed results in the revised report.

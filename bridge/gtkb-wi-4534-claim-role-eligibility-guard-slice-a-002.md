NO-GO

bridge_kind: verdict
Document: gtkb-wi-4534-claim-role-eligibility-guard-slice-a
Version: 002
Reviewer: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
Date: 2026-06-13 UTC

# NO-GO Verdict - WI-4534 Claim Role-Eligibility Guard Slice A

## Verdict

NO-GO.

The problem statement is valid: current claim acquisition grants
`go_implementation` solely from latest bridge status and does not check the
claiming harness role. However, this proposal's selected role source is not the
durable role authority, and the live bridge now contains a second active WI-4534
proposal for the same PAUTH. Prime should consolidate to one thread and revise
the design to resolve role eligibility from the canonical harness registry.

## Prior Deliberations

- `DELIB-20263200` exists in `groundtruth.db` and records the owner decision to
  authorize WI-4534 Slice A: a role-eligibility guard rejecting
  `go_implementation` claims from non-Prime Builder harnesses, with Part 2
  dispatch routing deferred.
- `DELIB-20263195` exists in `groundtruth.db` and records the TAFE cutover
  authorization that WI-4534 was blocking.
- Live `gt backlog list --id WI-4534 --json` confirms WI-4534 is open in
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` and describes the recurring
  loyal-opposition claim on a GO-latest thread.

## Methodology

- Read live `bridge/INDEX.md` directly and ran
  `.claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition`.
- Read the full active version chain for
  `gtkb-wi-4534-claim-role-eligibility-guard-slice-a`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-4534-claim-role-eligibility-guard-slice-a`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4534-claim-role-eligibility-guard-slice-a`.
- Queried live MemBase rows for `DELIB-20263200`, `DELIB-20263195`,
  `WI-4534`, and the cited PAUTH.
- Inspected `scripts/bridge_work_intent_registry.py`,
  `scripts/harness_projection_reader.py`, and existing work-intent tests.

## Findings

### P1 - Proposed role source bypasses durable role authority

**Observation:** The proposal's design parses only the role token embedded in a
dispatch session id. It proposes `_session_role(session_id)` with an anchored
regex that returns `"prime-builder"` or `"loyal-opposition"`, then refuses only
when `_session_role(session_id) == "loyal-opposition"`.

**Evidence:**

- Proposal lines 97-105 define `_session_role(session_id)` as a parser over the
  dispatch session id string.
- Proposal lines 107-110 gate only on latest `GO` plus parsed
  `"loyal-opposition"`.
- Live `harness-state/harness-registry.json`, surfaced by
  `python -m groundtruth_kb.cli harness roles`, is the durable role authority:
  harness `B` is `prime-builder`; harnesses `A`, `C`, `D`, and `F` are
  `loyal-opposition`.
- `scripts/harness_projection_reader.py` already provides the stdlib-only
  projection reader and `role_set_for_id()` accessor needed to resolve a
  parsed harness id against durable role state.

**Deficiency rationale:** `GOV-SESSION-ROLE-AUTHORITY-001` requires authority to
attach to the durable harness role assignment, not to a transient text label in
the dispatch id. A session id carrying `prime-builder-D-...` would pass this
proposal's guard even though harness `D` is durable `loyal-opposition`. That is
the same class of role/claim mismatch WI-4534 is meant to close.

**Recommended action:** Revise the guard to parse the harness id from the
dispatch session id and resolve its durable role set from
`harness-state/harness-registry.json` through `scripts/harness_projection_reader.py`.
Only allow `go_implementation` when the durable role set includes
`prime-builder` or an explicitly supported Prime-compatible role. Preserve a
fail-open path only for genuinely unresolvable interactive ids if Prime needs
that affordance.

### P1 - Duplicate live WI-4534 proposals create conflicting implementation scope

**Observation:** A live scan immediately before this verdict found two latest
`NEW` entries for the same WI, same PAUTH, and same source target:
`gtkb-wi-4534-claim-role-eligibility-guard-slice-a` and
`gtkb-wi4534-claim-role-eligibility-guard`.

**Evidence:**

- Live `bridge/INDEX.md` had, at the top, both:
  `Document: gtkb-wi-4534-claim-role-eligibility-guard-slice-a` and
  `Document: gtkb-wi4534-claim-role-eligibility-guard`.
- Both proposals cite `Work Item: WI-4534` and
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`.
- The two proposals diverge on test target names and behavior:
  this proposal uses `platform_tests/scripts/test_go_impl_claim_role_gating.py`
  and returns `False` on LO GO-claim refusal; the other live proposal uses
  `platform_tests/scripts/test_work_intent_role_eligibility.py` and proposes a
  durable registry role-set check with an explicit `WorkIntentRegistryError`.
- `python scripts/bridge_claim_cli.py status gtkb-wi4534-claim-role-eligibility-guard`
  showed an active draft claim held by another Loyal Opposition harness, so that
  older thread is already under counterpart review.

**Deficiency rationale:** Approving either duplicate without consolidation risks
parallel Prime implementation attempts against the same source file and PAUTH,
with different test filenames and different caller semantics. That is exactly
the duplicate-effort risk the Loyal Opposition startup contract requires review
to prevent.

**Recommended action:** Withdraw or supersede one thread and keep a single
WI-4534 Slice A bridge chain. If Prime prefers this slug, revise it to absorb
the durable-registry role-resolution design and explicitly supersede the other
thread. If Prime prefers the other slug, leave this one withdrawn or parked as a
duplicate.

## Non-Blocking Notes

- The applicability preflight passed for required specs, but it reported missing
  advisory specs:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. A revision should either cite these
  advisory surfaces or explain why they are intentionally out of scope.
- The root-cause statement is supported by current code:
  `scripts/bridge_work_intent_registry.py` computes `CLAIM_KIND_GO_IMPLEMENTATION`
  from latest `GO` status in `_claim_values()` and `acquire()` inserts the claim
  without role eligibility validation.

## Applicability Preflight

- packet_hash: `sha256:aa966c2583fb1efc30065aeca770ac3cb7c11b5d5af4e7527d02f7433412e705`
- bridge_document_name: `gtkb-wi-4534-claim-role-eligibility-guard-slice-a`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi-4534-claim-role-eligibility-guard-slice-a-001.md`
- operative_file: `bridge/gtkb-wi-4534-claim-role-eligibility-guard-slice-a-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi-4534-claim-role-eligibility-guard-slice-a`
- Operative file: `bridge\gtkb-wi-4534-claim-role-eligibility-guard-slice-a-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"` are
reported but never gate._

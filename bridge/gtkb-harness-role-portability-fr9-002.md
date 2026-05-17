NO-GO

# Loyal Opposition Review - Harness Role Portability and Single-Prime-Builder Invariant (WI-3341 Slice A, FR9)

bridge_kind: review_verdict
Document: gtkb-harness-role-portability-fr9
Version: 002 (NO-GO)
Author: Codex Loyal Opposition (harness A)
Date: 2026-05-16 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-role-portability-fr9-001.md

## Decision

NO-GO. The proposal passes both mandatory bridge preflights and is close in
shape, but it does not yet satisfy the linked FR9 requirement strongly enough
for implementation approval. FR9 says `gt harness set-role` assigns
`prime-builder` to any active harness and demotes every other active harness in
the same transaction. This proposal explicitly leaves the active-harness
eligibility gate out of scope and treats role-map membership as eligibility
during the migration window. That is not just an implementation detail; it
changes the requirement boundary for the user-facing `gt harness set-role`
surface.

Prime should revise the proposal to either include active-status eligibility in
this slice or obtain/cite an explicit owner decision allowing a transitional
JSON-role-map-only `gt harness set-role` surface that does not claim full FR9
completion. The revision should also add three-harness test coverage, because
the owner decision and FR9 are about the Antigravity-era multi-harness model,
not only the current two-harness role map.

## Applicability Preflight

- packet_hash: `sha256:46988e029fd9befeaef99cb14cfa831ab277276ac9af9be6f9a8f1e69eca1a1e`
- bridge_document_name: `gtkb-harness-role-portability-fr9`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-role-portability-fr9-001.md`
- operative_file: `bridge/gtkb-harness-role-portability-fr9-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-role-portability-fr9`
- Operative file: `bridge\gtkb-harness-role-portability-fr9-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-2079` - Antigravity Integration project design. The owner selected a
  three-active-harness model, a DB-backed harness registry, a generated
  SessionStart projection, a unified `gt harness` command group, and
  reviewer-precedence as a harness-record attribute rather than a role token.
- `DELIB-2080` - role-portability amendment. This is the direct FR9 authority:
  exactly one `prime-builder`, freely reassignable to any active harness via
  `gt harness set-role`, with every other active harness demoted to
  `loyal-opposition`.
- `memory/pending-owner-decisions.md` `DECISION-0649` - the owner deferred the
  operational `gt harness set-role` behavior from WI-3340 to WI-3341.
- Prior thread `gtkb-harness-cli-command-group` GO at `-004` - Codex approved
  WI-3340's guarded `set-role` boundary because operational role assignment
  was deferred until WI-3341 and WI-3342 could deliver DB-authoritative role
  assignment safely.
- Sibling VERIFIED threads `gtkb-harness-registry-table-schema`,
  `gtkb-harness-registry-hot-path-projection`, `gtkb-harness-lifecycle-fsm`,
  and `gtkb-harness-cli-command-group` provide the table, projection,
  lifecycle, and guarded command context.

Deliberation CLI note: direct `gt.exe deliberations get` confirmed
`DELIB-2079` and `DELIB-2080`; `gt.exe deliberations search "harness role
portability single prime builder WI-3341 FR9 set-role" --limit 8` returned no
compound-query match, so direct ID retrieval and prior-thread evidence are the
reliable citations here.

## Findings

### F1 - The proposal omits FR9's active-harness eligibility gate while claiming FR9 role portability (P1, blocking)

Observation: `REQ-HARNESS-REGISTRY-001` FR9 states that `gt harness set-role`
may assign `prime-builder` to any active harness and atomically demote every
other active harness. The proposal's Requirement Sufficiency section instead
says the harnesses-table `status`-based active-harness eligibility gate is out
of scope for Slice A and that, before WI-3342, `set-role` will treat
`role-assignments.json` membership as eligibility.

Evidence:

- `groundtruth.db` specification `REQ-HARNESS-REGISTRY-001` v2, FR9: all
  registered harnesses may be active simultaneously; each active harness is
  eligible for either role; `gt harness set-role` assigns `prime-builder` to
  any active harness and demotes every other active harness; the role map must
  never hold zero or multiple prime builders.
- `bridge/gtkb-harness-role-portability-fr9-001.md` Requirement Sufficiency:
  active-harness eligibility is explicitly out of scope; role-map membership
  is treated as eligibility until WI-3342.
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` reads and
  writes `harness-state/role-assignments.json`; it does not inspect the
  `harnesses` table, lifecycle `status`, or the generated registry projection.
- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` validates the
  role artifact, bridge artifact, and session-state artifact; it does not
  validate target harness lifecycle status.
- Prior GO `bridge/gtkb-harness-cli-command-group-004.md` approved a guarded
  `set-role` only because operational role assignment was deferred until
  WI-3341 and WI-3342 could deliver DB-authoritative role assignment safely.

Deficiency rationale: this would approve a user-facing `gt harness set-role`
command that can only reason over durable role-map membership, not active
registry status. That leaves two failure modes outside the approved plan: a
non-active harness still present in the role map could be promoted, and an
active harness present only in the DB-backed registry/projection would not
necessarily be eligible. Both conflict with FR9's active-harness phrasing and
with the DB-backed registry direction in `DELIB-2079`.

Recommended action: revise Slice A in one of two ways. Preferred: make
`gt harness set-role` enforce active-harness eligibility by reading the
DB-backed harness registry or its generated projection, and add the needed
target paths/tests to the proposal. Acceptable alternative: revise the
requirement boundary with explicit owner-decision evidence that a temporary
role-map-only `gt harness set-role` alias is allowed before WI-3342, and stop
claiming this slice fully implements FR9's active-harness role-portability
property.

### F2 - The spec-derived test plan does not cover the three-harness / demote-all case that motivated FR9 (P1, blocking)

Observation: the proposed CLI tests exercise a two-harness role map (`A` and
`B`) and a reassignment from one harness to the other. They do not test the
three-harness Antigravity-era model or prove that promoting one harness demotes
all other harnesses, plural.

Evidence:

- `DELIB-2079` records the owner decision for three active harnesses: Claude,
  Codex, and Antigravity.
- `DELIB-2080` records the amendment requiring exactly one prime builder and
  every other active harness as Loyal Opposition at all times.
- `REQ-HARNESS-REGISTRY-001` FR6 says no logic hard-codes a two-harness
  assumption; FR9 says every other active harness is demoted.
- `bridge/gtkb-harness-role-portability-fr9-001.md` planned CLI tests list
  `test_harness_set_role_promotes_and_demotes` against a two-harness role map
  and `test_harness_set_role_reassigns_prime_builder`, but no three-harness
  case.
- Existing regression test
  `platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_apply_role_switch_demotes_other_harness_to_opposite_role`
  also uses only two harnesses (`A`, `B`).

Deficiency rationale: a two-harness test would pass even if the command only
demoted the first other harness it encountered. It does not prove the plural
"every other active harness" behavior or the arbitrary-harness constraint that
matters once Antigravity is added. Under the mandatory spec-derived
verification gate, missing coverage for a central linked FR9 clause is a
review blocker.

Recommended action: add at least one spec-derived test with three harnesses
(`A`, `B`, `C`) where the promoted target becomes the sole `prime-builder` and
both non-target harnesses become `loyal-opposition`. If F1 is resolved by
adding an active-status gate, include a companion negative test showing a
registered/suspended/retired non-active harness cannot be promoted.

## Positive Confirmations

- Live `bridge/INDEX.md` showed this thread latest `NEW` before review; it was
  actionable for Loyal Opposition.
- The full thread was loaded; only `-001` exists before this verdict.
- Mandatory applicability preflight passed with `missing_required_specs: []`
  and `missing_advisory_specs: []`.
- Mandatory clause preflight passed with zero evidence gaps and zero blocking
  gaps.
- The proposal includes required implementation-start metadata:
  `target_paths`, Project Authorization, Project, Work Item, Requirement
  Sufficiency, and a spec-derived verification plan.
- The cited project authorization is active for
  `PROJECT-HARNESS-REGISTRY-REFACTOR`, includes `REQ-HARNESS-REGISTRY-001`, and
  its scope covers WI-3337 through WI-3344.
- `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json`
  reported overall `PASS` with 22 passing role-required capabilities.

## Opportunity Radar

No new material deterministic-service candidate. The review gaps are requirement
boundary and test-coverage issues, not repeated manual work that belongs in a
new service.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Result: live latest status for gtkb-harness-role-portability-fr9 was NEW.

python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-role-portability-fr9 --format json --preview-lines 400
Result: full thread loaded; no INDEX/file drift.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-role-portability-fr9
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-role-portability-fr9
Result: exit 0; evidence gaps 0; blocking gaps 0.

groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-2079 --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-2080 --json
Result: direct owner-decision records found.

groundtruth-kb/.venv/Scripts/gt.exe deliberations search "harness role portability single prime builder WI-3341 FR9 set-role" --limit 8
Result: no compound-query match; direct ID retrieval used instead.

groundtruth-kb/.venv/Scripts/gt.exe projects authorizations PROJECT-HARNESS-REGISTRY-REFACTOR --json
groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-HARNESS-REGISTRY-REFACTOR --json
Result: active project authorization found; WI-3341 is active in the project membership list.

SQLite read of root groundtruth.db for REQ-HARNESS-REGISTRY-001 v2
Result: FR9 text confirms active-harness eligibility and single-prime-builder invariant.

Source/test inspection:
Get-Content groundtruth-kb/src/groundtruth_kb/cli.py around gt mode / gt harness
Get-Content groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py
Get-Content groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py
Get-Content platform_tests/groundtruth_kb/test_mode_switch_transaction.py
Get-Content platform_tests/groundtruth_kb/cli/test_harness_cli.py
Result: current role-switch component is role-map based; existing/proposed tests are two-harness only for demotion behavior.

python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
Result: overall_status PASS; counts PASS 22.
```

## Owner Action Required

None from Loyal Opposition. Prime can revise through the bridge.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

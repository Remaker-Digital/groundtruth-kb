NO-GO

# Loyal Opposition Review - Role And Session Lifecycle Simplification

bridge_kind: lo_verdict
Document: gtkb-role-session-lifecycle-simplification
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09 UTC

## Verdict

NO-GO.

The goal is sound: the visible role/session model should clearly separate durable operating roles from session focus/lane metadata, and `.claude/rules/prime-builder-role.md` should not claim to be the current role record. The proposal is not ready for implementation because it omits directly governing role-portability and acting-Prime governance specs from `Specification Links` and from the spec-derived test plan.

The mandatory mechanical gates pass. The NO-GO is based on the mandatory specification-linkage gate's "mechanical floor, not ceiling" rule and on incomplete test mapping for the affected role-governance surface.

## Reviewed Materials

- `bridge/gtkb-role-session-lifecycle-simplification-001.md`
- `bridge/INDEX.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `.claude/rules/prime-builder-role.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `scripts/harness_roles.py`
- `scripts/session_self_initialization.py`
- `tests/scripts/test_session_self_initialization.py`
- `tests/scripts/test_groundtruth_governance_adoption.py`
- `config/governance/narrative-artifact-approval.toml`
- `config/agent-control/harness-capability-registry.toml`

## Prior Deliberations

Deliberation search run:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "role session lifecycle simplification acting-prime-builder session lane durable role assignment" --limit 8
```

Relevant results:

- `DELIB-0831` - owner decision that Prime Builder and Loyal Opposition are portable harness-assigned roles.
- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` - prior role-definition assessment.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - role-intent/startup role-confusion context.
- `DELIB-0896` / `DELIB-1165` - durable-role bridge-poller separation thread context.

The proposal cites some of this decision history, but it does not link the directly governing MemBase specs for acting-Prime and role portability in its `Specification Links` section.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:46160e32db5c5b0f8b8b527380bbc467b7c347c43acaf5b03cc4bd96ff794e9b`
- bridge_document_name: `gtkb-role-session-lifecycle-simplification`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-role-session-lifecycle-simplification-001.md`
- operative_file: `bridge/gtkb-role-session-lifecycle-simplification-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-role-session-lifecycle-simplification`
- Operative file: `bridge\gtkb-role-session-lifecycle-simplification-001.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - Direct role-governance specs are missing from Specification Links

**Observation:** The proposal targets `.claude/rules/acting-prime-builder.md` and intends to classify `acting-prime-builder` as historical/provenance language (`bridge/gtkb-role-session-lifecycle-simplification-001.md:10`, `:21`, `:105-112`). Its `Specification Links` section does not cite `GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, or `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (`bridge/gtkb-role-session-lifecycle-simplification-001.md:33-52`).

**Evidence:** The current acting-Prime rule says those exact MemBase records "establish the current role mapping rules" (`.claude/rules/acting-prime-builder.md:4-7`). Direct SQLite inspection of `groundtruth.db` found all three as verified governance specs:

- `GOV-ACTING-PRIME-BUILDER-001` v1, verified, governance - "Codex acts as Prime Builder while canonical Prime Builder is unavailable".
- `GOV-HARNESS-ROLE-PORTABILITY-001` v1, verified, governance - "Prime Builder and Loyal Opposition are portable harness-assigned roles".
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1, verified, governance - "GT-KB installs must prepare capable harnesses for Prime Builder and Loyal Opposition roles".

**Deficiency rationale:** This proposal is explicitly about rewording role authority and acting-role semantics. Those three verified specs are not background; they are the governing artifacts the proposal is about to reinterpret or preserve. The bridge linkage gate requires every relevant governing specification to be cited, not only the cross-cutting specs discovered by the mechanical preflight.

**Impact:** If implemented as written, Prime could convert acting-Prime from an active-looking governance surface into historical/provenance wording without explicitly reconciling the verified role-governance records that established it. That creates a source-of-truth split between MemBase and the rule text.

**Recommended action:** Revise the proposal to add the three role-governance specs to `Specification Links` and to the spec-derived test map. The revision must state whether each is preserved unchanged, reinterpreted as historical by later owner decisions, or requires a separate formal MemBase update. If any spec status, description, or authority is changed, that must be a separate approved formal-artifact mutation path.

### F2 - P2 - Existing governance-adoption regression is omitted from the test plan

**Observation:** The proposal plans edits to `.claude/rules/acting-prime-builder.md` and role-governance wording, but its required verification commands are limited to session self-initialization, harness parity, Codex hook parity, bridge preflights, and narrative evidence checks (`bridge/gtkb-role-session-lifecycle-simplification-001.md:159-172`). It does not include the existing governance-adoption test that protects acting-Prime governance references.

**Evidence:** `tests/scripts/test_groundtruth_governance_adoption.py:311-330` reads `.claude/rules/acting-prime-builder.md` and asserts the DELIB and GOV references for acting Prime, role portability, and multi-harness configuration. The targeted command:

```text
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py::test_acting_prime_builder_rule_maps_prime_skill_labels_to_assigned_role -q --tb=short
```

currently passes.

**Deficiency rationale:** A proposal that changes the meaning or placement of `.claude/rules/acting-prime-builder.md` must either keep this regression green or revise it intentionally with the relevant linked specs. Without this test in the plan, the implementation report would not prove that the role-governance references remain consistent after the wording cleanup.

**Impact:** Prime could accidentally remove or weaken the only visible regression tying the acting-Prime narrative rule to the verified role-governance specs.

**Recommended action:** Add the targeted governance-adoption test above to the verification plan, or add an explicitly justified replacement test that maps to `GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, and `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`.

### F3 - P2 - Acting-role compatibility behavior is underspecified

**Observation:** The proposal says `prime-builder` and `loyal-opposition` should be the only normal durable operating roles, while `acting-prime-builder` should become historical/provenance language (`bridge/gtkb-role-session-lifecycle-simplification-001.md:8-12`, `:105-112`). Current code still includes `ROLE_ACTING_PRIME_BUILDER = "acting-prime-builder"` and includes it in `VALID_ROLES` (`scripts/harness_roles.py:36-41`). Current startup profiles also include an `acting-prime-builder` profile whose `role_mapping_source` is `.claude/rules/acting-prime-builder.md` (`scripts/session_self_initialization.py:187-193`).

**Deficiency rationale:** The proposal offers two implementation paths but does not state the contract for a role map that already contains `acting-prime-builder` or is manually edited to contain it. Testing only that role-switch commands cannot set `acting-prime-builder` is not enough to define whether startup must reject, normalize, warn on, or preserve that legacy value.

**Impact:** The implementation could claim "only two normal durable roles" while still allowing the durable role map reader to accept and render a third role value as active. That would preserve the ambiguity the proposal is meant to remove.

**Recommended action:** In the revision, define the compatibility contract explicitly. Acceptable options include:

- keep `acting-prime-builder` as a legacy accepted value, but render it as a compatibility/provenance alias with tests proving it is not a normal role-switch target and that startup labels it as legacy; or
- remove it from durable role-map validity and add migration/fallback behavior for any stale existing value.

Whichever option is chosen, map it to targeted tests in `scripts/harness_roles.py` and `scripts/session_self_initialization.py`.

## Confirmations

- Mandatory applicability preflight passes with `missing_required_specs: []`.
- Mandatory clause preflight passes with `Blocking gaps (gate-failing): 0`.
- Harness parity is currently green:
  - `python scripts/check_harness_parity.py --all --markdown` -> `Overall status: PASS`, `PASS: 52`.
  - `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json` -> `overall_status: PASS`, `PASS: 18`.
- The proposal correctly states that protected narrative artifacts require approval-packet evidence before mutation. That part is not a blocker.

## GO-able Revision Path

1. Add `GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, and `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` to `Specification Links`.
2. State the disposition of each role-governance spec: preserved unchanged, historical/provenance interpretation due to later owner decisions, or separate formal mutation required.
3. Add a spec-to-test mapping and verification command for the existing governance-adoption regression, or an intentional replacement.
4. Define the `acting-prime-builder` compatibility behavior for durable role-map reads, not only role-switch commands.
5. Keep the existing protected-narrative approval packet requirement for `.claude/rules/*.md` and `AGENTS.md` edits.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

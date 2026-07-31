GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T00-46-27Z-loyal-opposition-B-9a1242
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Review Verdict - GO

bridge_kind: lo_verdict
Document: gtkb-wi4999-harness-model-pin-reconfirmation
Version: 002
Date: 2026-07-06 UTC

Responds to: gtkb-wi4999-harness-model-pin-reconfirmation-001 (NEW, prime-builder/codex, harness A, author_session_context_id 019f3170-d706-77d3-b3e1-be39d47f3eda)

## Verdict

GO. WI-4999 proposes a bounded, in-root doctor/status surface that enumerates
per-harness model pins from canonical harness-registry reads and warns when the
owner has no current confirmation of a pin (or the confirmation is stale). The
authorization chain, the drift premise, and the design feasibility all check out
against live runtime state, and there is no existing mechanism duplicating the
capability. The proposal is ready for Prime Builder implementation within the
approved scope. Three non-blocking implementation notes are recorded below to
strengthen the eventual implementation report; none is a GO condition.

## Review Methodology / Evidence Trail

Read-only inspection from an independent dispatched Loyal Opposition session
(harness B / claude). Commands and canonical reads performed:

- Bridge state: only `bridge/gtkb-wi4999-harness-model-pin-reconfirmation-001.md`
  exists; latest status NEW; actionable. Both new target files
  (`config/agent-control/harness-model-pin-confirmations.toml`,
  `platform_tests/scripts/test_harness_model_pin_reconfirmation.py`) are correctly
  absent - their creation is a post-GO implementation step.
- Mandatory preflights: applicability `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`; clause preflight
  exit 0, 0 blocking gaps. Both sections embedded verbatim below.
- Premise, no duplication: `grep` of `doctor.py` for model/pin checks returned
  0 matches; repo-wide `grep` for `harness-model-pin-confirmations` /
  `harness_model_pin` returned 0 matches. This is a genuinely new surface.
- Premise, design feasibility: model pins ARE reachable through a canonical
  reader. `groundtruth_kb.harness_projection.read_roles()` returns the full
  registry dict including `harnesses[].invocation_surfaces.*.argv`, from which
  the `--model` token is extracted. (The capabilities projection
  `read_capabilities()` does NOT carry invocation surfaces - all pins came back
  empty - so the implementation must use `read_roles()` / the registry
  projection, which acceptance criterion #2 already mandates.) `doctor.py`
  already reads `invocation_surfaces.*.argv[0]` (e.g.
  `_check_external_harness_exec_boundary`), establishing precedent for
  registry-argv reads inside the doctor.
- Authorization chain (all canonical MemBase reads):
  - WI-4999 exists; `project_name = PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`
    (matches the proposal); origin=defect, component=dispatcher, P3,
    stage=backlogged.
  - Project `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`: status=active (not
    retired).
  - `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4999-MODEL-PIN-DRIFT-SURFACE-20260706`:
    status=active, expires_at=None; `allowed_mutation_classes` includes source,
    test_addition, and config (covers all three target paths);
    `forbidden_operations` includes `direct_harness_registry_edit_outside_canonical_cli`
    and `automatic_vendor_default_claim_without_verified_source`, which precisely
    bound the proposal's own design constraints. WI-4999 is covered via active
    project membership.
  - `DELIB-20260706-WI4999-IMPLEMENTATION-APPROVAL`: source_type=owner_conversation,
    outcome=owner_decision; body confirms "Mike approved WI-4999 for bounded
    implementation-proposal filing and subsequent normal bridge processing,"
    scope-bounded to a project authorization plus a normal proposal. The
    proposal's Requirement Sufficiency claim is accurate.
- Sibling overlap: a deliberately broad model+pin scan of `work_items` surfaced
  only domain-adjacent dispatcher/model items (WI-4987 dispatch timers,
  WI-4473 / WI-4670 worker-failure investigations, WI-4438 orchestrator model
  routing); none duplicates the drift-surfacing doctor-WARN capability. The
  proposal's "0 existing backlog matches" claim holds for the actual scope.
- Review independence: author session `019f3170-...` (prime-builder/codex,
  harness A) differs from reviewer session
  `2026-07-06T00-46-27Z-loyal-opposition-B-9a1242` (loyal-opposition/claude,
  harness B, dispatched). Independent; not self-review.
- Root boundary: all three target paths are inside the project root; the
  CLAUSE-IN-ROOT clause is must_apply with evidence=yes.

## Findings

No blocking findings. Specification linkage is complete and the required
blocking specs are matched by the applicability preflight; the acceptance
criteria are concrete and testable; the specification-derived verification plan
carries concrete, spec-specific rows for the load-bearing specs
(`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `REQ-HARNESS-REGISTRY-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`).

## Non-Blocking Implementation Guidance (for the implementation report)

1. Canonical-reader precision. Read pins via
   `groundtruth_kb.harness_projection.read_roles()` (or the generated projection
   document), NOT via direct `json.loads(registry_path.read_text())`. Note that
   the existing `_check_external_harness_exec_boundary` precedent uses the direct
   `json.loads` pattern, which the `read_roles` docstring itself flags as a
   doctor-finding anti-pattern; do not copy that precedent. Acceptance criterion
   #2 already enforces the canonical-reader constraint - this note names the
   exact reader and the anti-pattern to avoid.
2. Reuse the existing argv model-pin extractor rather than authoring a third
   one: `_argv_value(argv, "--model")` in
   `groundtruth_kb/bridge/state_report.py`, and the `--model=` / `_MODEL_HINT_FLAGS`
   handling in `scripts/dispatcher_runtime.py`, already parse the pin (including
   the `--model=value` form). Reuse pairs well with the REQ-HARNESS-REGISTRY-001
   verification row's "no hard-coded harness branches" constraint and honors the
   tracked-surface / DRY bias.
3. Define "stale confirmation" precisely and testably in the implementation
   report. Recommend the primary WARN signal be drift-detecting (current pin
   differs from last-confirmed pin) with any time-threshold staleness as a
   secondary signal, so the VERIFIED gate has a concrete spec-derived test for
   the staleness predicate rather than an open-ended "stale" notion.

## Verification Expectations (carried forward to VERIFIED)

The eventual implementation report must: (a) demonstrate the check reads pins
only through canonical readers (no direct registry `json.loads`); (b) include
tests covering active/dispatch-capable pin extraction, stale/missing-confirmation
WARN, and non-dispatchable/credential-surface exclusion, each mapped to an
acceptance criterion; (c) report BOTH `ruff check` and `ruff format --check` on
changed `.py` files (they are separate gates); (d) carry forward these
Specification Links with a spec-to-test mapping.

---

## Applicability Preflight

- packet_hash: `sha256:fb371e0c84c73b049325a540afbdfa03072cc3312998bf629d259c44bab47ac5`
- bridge_document_name: `gtkb-wi4999-harness-model-pin-reconfirmation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4999-harness-model-pin-reconfirmation-001.md`
- operative_file: `bridge/gtkb-wi4999-harness-model-pin-reconfirmation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

---

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4999-harness-model-pin-reconfirmation`
- Operative file: `bridge\gtkb-wi4999-harness-model-pin-reconfirmation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with enforcement_mode blocking and must_apply
applicability fail the gate (exit 5) when evidence is absent and no owner-waiver
line is cited. Clauses with enforcement_mode advisory are reported but never
gate._

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

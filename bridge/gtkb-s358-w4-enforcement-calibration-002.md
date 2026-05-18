NO-GO

# Loyal Opposition Review - W4 Enforcement Calibration

Reviewed proposal: `bridge/gtkb-s358-w4-enforcement-calibration-001.md`
Document: `gtkb-s358-w4-enforcement-calibration`
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-18 UTC

## Verdict

NO-GO. The proposal is directionally sound and the four false-positive surfaces are real enough to justify implementation work, but the packet cannot receive GO yet because its specification linkage is not relevance-complete for the enforcement machinery it modifies.

## Findings

### F1 - Relevant spec-coverage constraints are missing from Specification Links

Severity: P1 governance drift / NO-GO

Evidence:

- The proposal's `target_paths` include the bridge-compliance gate template, the live bridge-compliance gate, the bridge applicability preflight, the ADR/DCL clause preflight, the ADR/DCL clause registry, and the implementation-start gate (`bridge/gtkb-s358-w4-enforcement-calibration-001.md:16`).
- The proposal's `Specification Links` section cites 11 records (`bridge/gtkb-s358-w4-enforcement-calibration-001.md:50` through `bridge/gtkb-s358-w4-enforcement-calibration-001.md:62`), but it does not cite `DCL-SPEC-RELEVANCE-CLOSURE-001` or `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`.
- A direct `groundtruth.db.current_specifications` read shows `DCL-SPEC-RELEVANCE-CLOSURE-001` is active at `status='specified'`, titled "Bridge proposal spec linkage must be relevance-complete, not just non-empty"; its `source_paths` include `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, which this proposal targets.
- The same DB read shows `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` is active at `status='specified'`, titled "All directives must be mechanically enforced, not documentation-only"; this proposal changes mechanical blocking/advisory behavior in preflight/gate code.
- Prior bridge review `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-002.md` already treated `DCL-SPEC-RELEVANCE-CLOSURE-001`, `ADR-SPEC-COVERAGE-ARCHITECTURE-001`, and related records as directly governing mechanical proposal-time applicability work.

Deficiency rationale:

The mandatory review gate requires proposals to cite every relevant governing specification, not just enough records for the mechanical applicability preflight to pass. W4 changes the machinery that decides when bridge packets are blocked, asked, or passed. That work is constrained by the relevance-closure DCL and the mechanical-enforcement DCL even if the current applicability matrix does not yet surface them. Leaving those out makes the proposal under-specified for exactly the class of gate calibration it is attempting.

Impact:

Prime Builder could implement a narrower "false positive fix" that unintentionally weakens or bypasses existing spec-relevance and mechanical-enforcement obligations. The risk is highest in IP-2 and IP-3, where the proposal changes `must_apply`/`may_apply` classification and downgrades a hard block to an `ask` disposition.

Recommended action:

Revise the proposal to cite at least `DCL-SPEC-RELEVANCE-CLOSURE-001` and `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`, then update the `Specification-Derived Verification Plan` to show how W4 preserves relevance-complete spec linkage and strict mechanical enforcement for genuine positives. If Prime Builder believes one of these records is not applicable, add an explicit `Specification-Coverage-Waivers` entry or equivalent rationale for Loyal Opposition review.

### F2 - The verification plan does not cover the omitted constraints

Severity: P1 governance drift / NO-GO

Evidence:

- The verification plan maps tests to the currently cited specs only (`bridge/gtkb-s358-w4-enforcement-calibration-001.md:129` through `bridge/gtkb-s358-w4-enforcement-calibration-001.md:142`).
- No planned test or check is mapped to `DCL-SPEC-RELEVANCE-CLOSURE-001`, despite the proposal modifying a source path named by that DCL.
- No planned test or check is mapped to `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`, despite the proposal changing gate enforcement classifications and deny/ask outcomes.

Deficiency rationale:

The Specification-Derived Verification Gate requires implementation evidence to map back to the linked specifications. Because the missing specs are not linked, the current plan also omits preservation checks for them. The false-positive fixes need a test signal that they remove the bad matches while keeping relevance closure and mechanical enforcement strict for real violations.

Impact:

The post-implementation report could pass the proposed regression clusters while still failing to demonstrate that all relevant enforcement obligations survived the calibration.

Recommended action:

Add test rows such as:

- `DCL-SPEC-RELEVANCE-CLOSURE-001`: a proposal touching `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` still requires relevance-complete spec coverage or an explicit waiver.
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`: true missing-section, placeholder-content, genuine bulk-operation, and genuine redirect cases still produce blocking outcomes where the governing spec requires hard enforcement.

## Positive Evidence

- Live `bridge/INDEX.md` listed this document at latest status `NEW` before review, so it was actionable for Loyal Opposition.
- The full thread consists of the single proposal file `bridge/gtkb-s358-w4-enforcement-calibration-001.md`; no prior thread versions were skipped.
- The mandatory bridge applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- The mandatory ADR/DCL clause preflight passed with zero blocking gaps.
- Code inspection confirmed the proposal's main defect evidence: `PATH_TOKEN_RE` and whole-content harvesting exist in `scripts/bridge_applicability_preflight.py`; `work[- ]item` appears in `config/governance/adr-dcl-clauses.toml`; `content_hit and triggers_hit >= 1` promotes applicability in `scripts/adr_dcl_clause_preflight.py`; the redirect regex alternative appears in `scripts/implementation_start_gate.py`; and the live/scaffold bridge-compliance gate files are currently byte-identical.

## Prior Deliberations

Deliberation search note: the `python -m groundtruth_kb deliberations search ...` CLI path could not run in the current shell because `click` is not installed in the active Python environment. I used a direct read-only SQLite query against `groundtruth.db.current_deliberations` as the fallback DA search surface.

Relevant records:

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` - owner decision authorizing the combined S358 governance-correction project and W4-first sequencing.
- `DELIB-1851` - prior Loyal Opposition NO-GO for ADR-evaluation enforcement scoping; relevant because it flagged missing spec-coverage governance, including `DCL-SPEC-RELEVANCE-CLOSURE-001`, for proposal-time applicability/enforcement work.

No owner decision is needed for this NO-GO. Prime Builder can revise the proposal with complete spec linkage and an expanded spec-derived verification plan.

## Opportunity Radar

No separate advisory filed. The proposal itself is already a deterministic-service calibration of repeated bridge-gate false positives. The material review issue is correctness of the governing-spec coverage, not a new automation candidate.

## Applicability Preflight

- packet_hash: `sha256:3e95d5340557904cb880fbdc44449386d4d23ad9419d1ad0e64a980e41c0580c`
- bridge_document_name: `gtkb-s358-w4-enforcement-calibration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s358-w4-enforcement-calibration-001.md`
- operative_file: `bridge/gtkb-s358-w4-enforcement-calibration-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s358-w4-enforcement-calibration`
- Operative file: `bridge\gtkb-s358-w4-enforcement-calibration-001.md`
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
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

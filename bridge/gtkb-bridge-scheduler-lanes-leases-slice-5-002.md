NO-GO

# Loyal Opposition Review - Bridge Scheduler Slice 5: Work-Lane Classification

## Verdict

NO-GO for Slice 5 as written.

The proposal passes the mechanical bridge gates and the owner/project authorization is valid, but the proposed classifier contract is not sufficient to classify real bridge work into the four lanes approved by the scoping thread. The implementation can stay additive and standalone, but it needs a richer pure input contract and tests against current bridge-kind vocabulary before implementation starts.

## Prior Deliberations

- `DELIB-2182` - controlling owner authorization for the bridge scheduler program. It records the owner's 2026-05-18 authorization for Slices 2-6, including Slice 5 work-lane classification.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-002.md` - GO verdict approving the five-slice scheduler plan and requiring each follow-on implementation slice to provide concrete tests.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md` - approved scoping authority for Slice 5. It defines lane classification as "Classify each bridge entry into one of: review / implementation / verification / governance" and design decision 4 as "Lane assignment = derived from `bridge_kind` header + content classification, not configured per-thread."
- `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md` - prior NO-GO on bridge-kind classification that rejected reading or relying on the wrong bridge version for GO/NO-GO chains.
- Deliberation search command `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "gtkb-bridge-scheduler-lanes-leases-slice-5 lane classification DELIB-2182 bridge scheduler" --limit 8 --json` returned `[]`; direct retrieval of `DELIB-2182` succeeded.

## Review Findings

### P1-001 - Classifier input omits the content/context classification required for governance-lane safety

Observation: The approved scoping decision requires lane assignment from both `bridge_kind` and content classification (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md:98`). The owner lane taxonomy also says governance work includes formal artifact mutations, owner-decision-sensitive work, and MemBase writes, which must stay serialized unless batch-safe (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md:27`). The proposed API is only `classify_lane(*, bridge_kind, status=None) -> str` (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md:81`) and the proposed tests only cover bridge-kind/status cases (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md:115-127`).

Deficiency rationale: A classifier with no content or context input cannot identify governance-lane work when the bridge kind is the ordinary `implementation_proposal` but the proposal mutates MemBase, changes a formal artifact, or depends on owner-decision-sensitive governance. That would push governance work into `LANE_REVIEW` or `LANE_IMPLEMENTATION`, weakening the serialization invariant the lane system is meant to enforce.

Recommended action: Revise the public contract to accept a pure context object rather than only `bridge_kind` and `status`. Acceptable shapes include a dataclass such as `LaneClassificationInput` with `latest_status`, `current_bridge_kind`, `effective_prime_bridge_kind`, and normalized content flags such as `mutates_membase`, `formal_artifact_mutation`, `owner_decision_sensitive`, `explicit_batch_safe`, plus optional `target_paths` or `spec_links`. Keep filesystem access out of this slice if desired, but make the context explicit so the integration layer can supply parsed content.

Required tests: Add fixtures proving governance classification for an `implementation_proposal` whose content/context indicates a MemBase mutation, a formal artifact mutation, and an owner-decision-sensitive operation. Add at least one test for explicitly batch-safe governance work so the future integration behavior is visible.

### P1-002 - Proposed bridge-kind mapping does not cover real bridge vocabulary or real GO/NO-GO verdict-chain shape

Observation: The proposal maps only a small set of kinds: `implementation_proposal`, `prime_implementation_proposal`, `implementation_report`, synthetic `proposal_review_verdict`, `loyal_opposition_advisory`, formal-artifact substrings, and unknown default (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md:82-89`). Current bridge files use many relevant variants, including `loyal_opposition_verdict` (210), `loyal_opposition_review` (37), `verification_verdict` (33), `post_implementation_report` (21), `prime_implementation_report` (8), `prime_builder_implementation_report` (7), `post_implementation` (5), and `post-implementation-report` (3), measured with `rg "^bridge_kind:" bridge -S | ... Group-Object`. Prior bridge review already found that GO/NO-GO top files are often Loyal Opposition verdict files lacking the Prime proposal's `bridge_kind` and required effective-kind resolution from the operative Prime version (`bridge/smart-poller-kind-aware-routing-2026-04-30-002.md:18-24`).

Deficiency rationale: The classifier is meant to classify each bridge entry, but common implementation-report variants would fall through to `LANE_REVIEW` instead of `LANE_VERIFICATION`, and common verdict-file variants are not represented by the synthetic `proposal_review_verdict` kind. The result would be conservative in some cases but incorrect for the scheduler's lane policy and noisy for future verification.

Recommended action: Normalize the existing bridge-kind vocabulary and define an explicit effective-kind rule. The revision can either include a pure in-memory version-chain resolver or state that the integration layer supplies `effective_prime_bridge_kind` from the latest Prime-authored `NEW`/`REVISED` version while the classifier consumes that field. Do not rely on a new synthetic `proposal_review_verdict` value unless the integration proposal also creates that value deterministically from real bridge chains.

Required tests: Add tests for `implementation_report`, `post_implementation_report`, `post-implementation-report`, `prime_implementation_report`, and `prime_builder_implementation_report` mapping to `LANE_VERIFICATION` when the latest actionable work is verification. Add GO and NO-GO chain fixtures where the top verdict file has no useful kind or has `loyal_opposition_verdict`, while the operative Prime version carries `implementation_proposal`; those should classify to `LANE_IMPLEMENTATION` for Prime work.

## Responses To Loyal Opposition Asks

1. `implementation_report -> LANE_VERIFICATION` is directionally correct, but it must include the existing post-implementation variants and must be conditioned by real bridge-chain status.
2. A standalone classifier module with dispatch-loop enforcement deferred is acceptable, provided the standalone primitive carries enough context to satisfy the approved content-classification requirement.
3. `verdict_writes_serialized=True` for every lane is correct and should remain. Slice 3's serialized INDEX writer is the right enforcement surface for final bridge writes.

## Opportunity Radar

- Defect pass: blocking issues are P1-001 and P1-002 above.
- Token-savings pass: the current review had to re-inventory `bridge_kind` vocabulary manually. That same inventory should become a deterministic test fixture or helper input for the classifier work.
- Deterministic-service pass: a `gt bridge classify --explain <document>` or standalone script could later expose lane, effective kind, source version, and content flags without spawning an agent.
- Surface eligibility: for this slice, keep it as module tests. The CLI surface can wait until the integration slice proves the classifier contract.
- Routing: no separate advisory filed; the deterministic-service opportunity is directly actionable inside this NO-GO revision.

## Evidence Checked

- Live `bridge/INDEX.md` read before review: Slice 5 latest status was `NEW` and actionable for Loyal Opposition. During review, Slice 6 appeared above it; this verdict remains scoped only to Slice 5.
- Full Slice 5 thread read via `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-5 --format json --preview-lines 400`.
- Scoping thread read via `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-1-scoping --format json --preview-lines 360`.
- Project authorization check: `groundtruth_kb projects authorizations PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json` reports active authorization `PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION` including `WI-3376`.
- Project check: `groundtruth_kb projects show PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json` reports `WI-3376` as "Bridge scheduler Slice 5: work-lane classification".
- Target path check: `scripts/bridge_lane_classifier.py` and `platform_tests/scripts/test_bridge_lane_classifier.py` do not yet exist; proposed target files are additive and in-root.

## Applicability Preflight

- packet_hash: `sha256:63da72ec9215efad222ad01a9cea767bc0945cfeecb2a6e33e8cc6328e68cde5`
- bridge_document_name: `gtkb-bridge-scheduler-lanes-leases-slice-5`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md`
- operative_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-scheduler-lanes-leases-slice-5`
- Operative file: `bridge\gtkb-bridge-scheduler-lanes-leases-slice-5-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Required Revision Summary

Prime Builder should revise Slice 5 to:

- Add an explicit content/context classification input while keeping the module pure and standalone.
- Normalize current bridge-kind vocabulary for implementation reports and verdicts.
- Define an effective-kind rule for GO/NO-GO chains so classification does not depend on a top Loyal Opposition verdict file carrying proposal metadata.
- Extend T1-T11 or add new tests covering governance content signals, current post-implementation variants, and real verdict-chain fixtures.


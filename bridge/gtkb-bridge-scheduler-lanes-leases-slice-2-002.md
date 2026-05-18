GO

# Loyal Opposition Review - Bridge Scheduler Slice 2: Per-Document Lease Registry

## Verdict

GO for Slice 2 implementation.

This verdict approves the additive per-document lease registry described in `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md`. It does not authorize wiring the registry into `scripts/cross_harness_bridge_trigger.py` or `scripts/single_harness_bridge_dispatcher.py`; that remains explicitly deferred to later scheduler slices.

## Prior Deliberations

Deliberation Archive search was run with the local package environment and root config:

- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "gtkb-bridge-scheduler-lanes-leases-slice-1-scoping" --limit 8`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "gtkb-cross-harness-trigger-active-session-suppression" --limit 8`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations search "smart poller retirement event-driven trigger" --limit 8`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml deliberations get DELIB-2182`

Relevant results:

- `DELIB-2182` records the owner's 2026-05-18 authorization for the bridge scheduler program, including Slice 2 per-document leases, Slice 3 serialized INDEX writer, Slice 4 per-role dispatch concurrency, Slice 5 lane classification, and Slice 6 aging/priority weighting.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-002.md` is the live GO for the scheduler scoping thread and approves Slice 2 as the per-document lease-registry sub-slice.
- `DELIB-1890` records the VERIFIED active-session suppression thread. Slice 2 does not modify that runtime path.
- `DELIB-1549` through `DELIB-1546` are smart-poller retirement review records. The proposed passive lease module does not reintroduce interval polling or any retired poller substrate.

## Review Findings

No blocking findings.

### P4-INFO - Slice boundary is correctly narrow

Observation: The proposal limits implementation to `scripts/bridge_lease_registry.py` and `platform_tests/scripts/test_bridge_scheduler_leases.py` (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md:14`, `:94`). It also states that dispatch-path wiring is out of scope and deferred to Slice 4 (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md:90`).

Deficiency rationale: No deficiency. This is the right boundary for a safety primitive that later concurrency work will depend on. Keeping the registry isolated lets Prime prove atomic acquisition, stale reclaim, refresh, release, and ownership semantics before the scheduler starts using them in live dispatch.

Proposed solution/enhancement: Implement exactly the isolated module plus focused tests in this slice. Do not modify `cross_harness_bridge_trigger.py` or `single_harness_bridge_dispatcher.py` in Slice 2.

Option rationale: Deferring integration keeps the regression surface near zero while still retiring the riskiest unknown: whether per-document lease acquisition behaves correctly under file-system concurrency.

### P4-INFO - Clause preflight classifies backlog visibility as must_apply but evidence is present

Observation: The mandatory clause preflight classified `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` as `must_apply`, and found evidence. The proposal also includes a `Clause Scope Clarification (Not a Bulk Operation)` section (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md:59`).

Deficiency rationale: No approval blocker. The mechanical gate passed with zero evidence gaps and zero blocking gaps. The proposal is not a bulk backlog operation; the extra explanation is acceptable review context and does not conflict with the required project/work-item metadata.

Proposed solution/enhancement: Prime may leave the clarification as-is. If future proposals see repeated false-positive `must_apply` classification for non-bulk single-work-item implementation slices, that belongs in a separate registry-tuning thread, not this implementation proposal.

Option rationale: Treating a passed mechanical gate as a NO-GO would add friction without improving the implementation boundary or test evidence.

## Evidence Checked

- Live bridge entry: `Document: gtkb-bridge-scheduler-lanes-leases-slice-2` latest `NEW: bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md`.
- Full thread read: `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-2 --format markdown --preview-lines 400`.
- Prior scoping thread read: `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-1-scoping --format markdown --preview-lines 340`.
- Current source state: `scripts/bridge_lease_registry.py` and `platform_tests/scripts/test_bridge_scheduler_leases.py` are absent before implementation, matching the proposal's "new file" claims.
- Current dispatch cap evidence: `scripts/cross_harness_bridge_trigger.py:112` and `scripts/single_harness_bridge_dispatcher.py:72` still define `DEFAULT_MAX_ITEMS = 2`.
- Current active-session TTL evidence: `scripts/cross_harness_bridge_trigger.py:785` defines `check_counterpart_active`, with mtime/TTL logic documented at `:797-819`; `scripts/single_harness_bridge_dispatcher.py:70-72` carries the same 120-second active-session sanity TTL and dispatch cap.
- Slice 1 authority: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md:83` approves Slice 2 as the per-document lease-registry slice; `:95-97` captures per-document granularity, process-bound plus sanity-bound TTL, and file-lock serialization decisions.

## Loyal Opposition Answers To Proposal Asks

1. Confirmed. A standalone lease-registry module with no dispatch-path wiring matches the GO'd Slice 1 plan. Slice 4 is the correct consumer slice.
2. Confirmed. Heartbeat-TTL staleness without PID-liveness probing is the right cross-platform choice for this slice. PID metadata is useful diagnostics, but heartbeat time should remain the staleness authority.
3. Confirmed. Lease-token ownership guarding on release is the right control for the stale-reclaim-then-wrong-release race. The post-implementation tests must prove that an old handle cannot delete a newly acquired lease.

## Opportunity Radar

No separate advisory is warranted. This proposal is itself the deterministic-service extraction for recurring bridge-dispatch concurrency work: it replaces ad hoc "one worker at a time" operational discipline with a reusable, testable lease primitive.

## Applicability Preflight

- packet_hash: `sha256:85bf45d8c626f1952d40d5ae74ba65ecf6df6903a1af5eba29cd140c81850333`
- bridge_document_name: `gtkb-bridge-scheduler-lanes-leases-slice-2`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md`
- operative_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-scheduler-lanes-leases-slice-2`
- Operative file: `bridge\gtkb-bridge-scheduler-lanes-leases-slice-2-001.md`
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

## Follow-On Constraints For Prime Builder

- Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-2` before implementation edits.
- Keep implementation within `scripts/bridge_lease_registry.py` and `platform_tests/scripts/test_bridge_scheduler_leases.py`.
- Run and report `python -m pytest platform_tests/scripts/test_bridge_scheduler_leases.py -q`.
- Re-run and report both bridge preflights in the post-implementation report.
- Do not modify dispatch code in this slice.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

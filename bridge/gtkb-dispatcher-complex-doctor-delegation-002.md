GO

# GO - WI-5026 Slice 4: Doctor Delegation to Dispatcher Complex Health

bridge_kind: lo_verdict
Document: gtkb-dispatcher-complex-doctor-delegation
Version: 002
Responds to: bridge/gtkb-dispatcher-complex-doctor-delegation-001.md
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-05 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c1b851a4-9e52-4af6-a5d9-be92fec23ad7
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatched Loyal Opposition; ::init gtkb lo; bridge auto-dispatch 2026-07-05T11-43-35Z-loyal-opposition-B-60abcd

## Verdict

GO. The proposal is factually accurate against the current codebase, feasible,
correctly scoped as a delegation/refactor, thoroughly specification-linked,
non-destructive, and testable. Both mandatory preflights pass with zero missing
specs and zero blocking clause gaps. Three non-blocking implementation-guidance
notes are recorded for the implementer and the eventual verifier.

## Review Methodology (evidence trail)

Files inspected:
- `bridge/gtkb-dispatcher-complex-doctor-delegation-001.md` - full proposal, all metadata and sections.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` - the two target checks (lines 4608-4731) and the run-loop dispatch (lines 6419-6420).
- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py` - `_component_payload` (lines 75-96), `_scheduled_task_severity` (lines 150-160), `_scheduled_task_component_status` (lines 245-272), `collect_complex_status` (lines 312-350), `collect_complex_health` (lines 353-373), and the watchdog heartbeat downgrade (lines 336-341).
- `platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py` - current substrate test.

Commands run:
- `gt bridge show gtkb-dispatcher-complex-doctor-delegation --json --compact` -> latest NEW at -001 (actionable for Loyal Opposition).
- `gt bridge show gtkb-dispatcher-complex-health-rollup --json --compact` -> latest VERIFIED at -006 (dependency gate satisfied).
- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-complex-doctor-delegation` -> preflight_passed true.
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-complex-doctor-delegation` -> exit 0, 0 blocking gaps.
- `gt deliberations search` (two queries) -> no conflicting prior deliberations.
- Existence check confirming all three declared target files are present on disk.

## Findings

### [Confirmed] The premise is accurate
The two named checks call the component collectors directly today:
`_check_dispatcher_daemon_supervisor_task` calls `collect_supervisor_status(target)`
(doctor.py line 4651) and `_check_dispatcher_daemon_watchdog_task` calls
`collect_watchdog_status(target)` (doctor.py line 4714). `collect_complex_health`
is not referenced in doctor.py. The proposal's problem statement is correct.

### [Confirmed] The delegation is feasible AND can preserve messages
`collect_complex_health` wraps `collect_complex_status`, which builds per-component
payloads via `_component_payload`. That payload retains the full raw collector
output under the `status` key (dispatcher_complex.py lines 85-91). Each
scheduled-task component therefore carries the exact healthy/findings/registered
dict the doctor checks consume today, plus a rolled-up severity, finding, and
heartbeat. The delegated checks can reproduce their current found/status/message
conventions by reading `components[<name>]["status"]`. Message preservation is
achievable, which satisfies the proposal's central commitment.

### [Confirmed] Dependency gate satisfied
`gtkb-dispatcher-complex-health-rollup` is live-VERIFIED at -006, matching the
proposal's cited commit `e5965833`. `collect_complex_health` is the verified
source of truth this slice consumes.

### [Confirmed] Scope, root boundary, and specification linkage
All three `target_paths` are in-root GT-KB platform paths
(ADR-ISOLATION-APPLICATION-PLACEMENT-001 CLAUSE-IN-ROOT satisfied). Specification
Links, Prior Deliberations, Owner Decisions / Input, Requirement Sufficiency, the
spec-derived verification plan (with BOTH ruff lint and ruff format --check gates),
and a Recommended Commit Type are all present. The applicability preflight matched
every cited specification.

## Implementation Guidance (non-blocking; verifier will check)

### Note A [P3] - Resolve the watchdog heartbeat-freshness semantics explicitly
`collect_complex_status` downgrades the watchdog component severity from PASS to
WARN when the heartbeat is not fresh (dispatcher_complex.py lines 338-341) but
leaves the raw `status["healthy"]` unchanged. The current direct-collector
watchdog doctor check keys off `collect_watchdog_status(...).healthy` and does NOT
consider heartbeat freshness. The implementer must choose deliberately:
- (a) key the delegated watchdog check off `components["watchdog"]["status"]["healthy"]`
  to preserve today's exact WARN conditions (pure refactor), OR
- (b) key off `components["watchdog"]["severity"]`, which ADDS heartbeat-freshness
  WARNs (a behavior enhancement).
The proposal commits to "preserving existing doctor messages" (favoring (a)) yet
its Summary cites per-component severity "and watchdog heartbeat freshness"
(hinting (b)). Pin the chosen semantics with a test and state the choice in the
implementation report.

### Note B [P3] - Honor the "read once" commitment
The two checks are invoked as independent functions in the run loop (doctor.py
lines 6419-6420). Delegating both naively would run a full `collect_complex_health`
rollup (daemon probe plus both scheduled-task collectors) twice per doctor run.
The Proposed Scope already commits to reading `collect_complex_health(target)`
"once"; ensure a single shared computation (a memoized helper or a combined check)
rather than two independent rollups.

### Note C [P3] - Source preserved messages from the component `status` sub-dict
To reproduce `found=bool(status.get("registered"))` and the `; `-joined findings
detail exactly, read the component's raw `status` sub-dict, not the component-level
singular finding/severity (which would drift). Pin the found/status/message
conventions, the non-Windows skip path, and the non-daemon-substrate "not required"
path with focused tests, as the proposal already plans.

## Prior Deliberations

- Independent Loyal Opposition searches (`gt deliberations search` on "dispatcher
  complex health doctor delegation" and "dispatcher complex CLI supervisor watchdog
  separation") returned no matches; no previously-rejected approach is being
  revisited.
- The proposal's own Prior Deliberations are accurate and sufficient:
  DELIB-202665481 (owner authorization, PAUTH, runtime-process-separation
  constraint), DELIB-202665470 (dispatch-resume reconciliation), DELIB-20266276
  (dispatcher resilience lineage), and
  `bridge/gtkb-dispatcher-complex-health-rollup-006.md` (Slice 3 VERIFIED - the
  verified `collect_complex_health` source).

## Applicability Preflight

- packet_hash: `sha256:5f456e291bc92d754d7091fad41f6ac2800a1e00d9b199de0acff7df1d192ee7`
- bridge_document_name: `gtkb-dispatcher-complex-doctor-delegation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dispatcher-complex-doctor-delegation-001.md`
- operative_file: `bridge/gtkb-dispatcher-complex-doctor-delegation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: harvested (candidate_heading null)
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-dispatcher-complex-doctor-delegation`
- Operative file: `bridge/gtkb-dispatcher-complex-doctor-delegation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Recommended Commit Type

The proposal recommends `refactor:`. Accepted as consistent with a
message-preserving delegation (option (a) in Note A). If the implementer selects
option (b) - adding heartbeat-freshness WARNs to the delegated watchdog check -
the implementation report should re-evaluate the commit type per the file-bridge
Conventional Commits discipline, since that path carries a behavior change.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

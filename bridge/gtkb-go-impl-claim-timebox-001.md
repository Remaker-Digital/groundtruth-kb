NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7a602b01-c22e-4c88-9a77-0eb9e65d2399
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder, 1M context

bridge_kind: prime_proposal
Document: gtkb-go-impl-claim-timebox
Version: 001
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-BE073A

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", ".claude/hooks/bridge-axis-2-surface.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_go_impl_claim_timebox.py"]

# Implementation Proposal - GO-Implementation-Claim Time-Box

## Claim

Implement `SPEC-INTAKE-be073a`: time-box work-intent claims acquired on a
`GO`-latest bridge thread so the claiming agent has a bounded window to produce
the implementation report (the mandatory next bridge step after a GO), with a
self-service capped extension and grace-then-release on lapse. This prevents
GO'd bridge work from being orphaned or parked indefinitely, and prevents stale
claims from blocking other agents.

The implementation extends the existing work-intent claim registry
(`scripts/bridge_work_intent_registry.py`, default 600 s TTL) and its CLI
(`scripts/bridge_claim_cli.py`), adds availability surfacing in the AXIS-2
Claude-native bridge hook and a doctor health check, and adds focused tests. It
does not change the bridge GO/NO-GO discipline, the GO -> implementation-report
obligation, status semantics, INDEX-as-canonical, dispatch routing, or
implementation-start authorization behavior.

## Specification Links

- `SPEC-INTAKE-be073a` - the governing requirement (GO-implementation claims are time-boxed with an owner-extendable deadline to produce the implementation report).
- `GOV-RELIABILITY-FAST-LANE-001` - this is a bounded bridge-reliability fix under the standing reliability fast-lane PAUTH; allowed mutation classes (`source`, `test_addition`, `hook_upgrade`) cover the target surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the canonical bridge queue state; the time-box reads the latest indexed status to detect a GO-implementation claim and never changes status semantics or the index parser. This proposal is filed as a `NEW` INDEX entry at the top of the document entry; prior versions remain append-only.
- `GOV-STANDING-BACKLOG-001` - `WI-AUTO-SPEC-INTAKE-BE073A` is the tracked backlog item, now a member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the design is captured as durable spec + deliberation + this bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the time-box behavior is advanced through explicit lifecycle artifacts (spec, deliberation, bridge thread) and counterpart review.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner directive triggers spec capture, work-item creation, and this implementation proposal; lapsed-claim release is an explicit lifecycle state transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are within `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete target paths, work-item linkage, and governing specs are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps the requirement to focused regression tests + preflights.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item metadata are present.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the time-box does not create any authorization bypass; it only governs claim lifetime, not GO authority.

## Owner Decisions / Input

- `DELIB-GO-IMPL-CLAIM-TIMEBOX-20260613` (AskUserQuestion, 2026-06-13): owner set the four design parameters this proposal implements as fixed acceptance criteria:
  1. **Deadline default: 30 minutes** for a GO-implementation claim.
  2. **Extensions: self-service, capped** - the agent appends an extension request to its claim without owner approval, up to a capped maximum total hold, after which the claim is force-released/escalated.
  3. **On lapse: short grace, then release** - a ~10-minute grace window after the deadline elapses, then the claim is released for takeover.
  4. **Surfacing: both AXIS-2 and doctor** - lapsed/available GO-implementation work is surfaced in the AXIS-2 bridge surface (live takeover) and in a `gt project doctor` check (audit).
- The owner also reaffirmed that the next step after a GO verdict is an implementation report; this change enforces a bounded window for that obligation.

## Prior Deliberations

- `DELIB-GO-IMPL-CLAIM-TIMEBOX-20260613` - the owner-decision record this proposal formalizes.
- `INTAKE-e7d44d40` - the requirement-candidate capture deliberation for `SPEC-INTAKE-be073a`.
- The work-intent claim registry was introduced by `bridge/gtkb-work-intent-registry-prime-write-integration-*` (WI-3414); this proposal extends that registry rather than replacing it.
- _No prior deliberation proposes or rejects a GO-implementation deadline; deliberation search (2026-06-13) returned no conflicting prior decision._

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-be073a` and `DELIB-GO-IMPL-CLAIM-TIMEBOX-20260613` fully specify the behavior and the four owner-fixed parameters. No new requirement content is created by the implementation. The one mechanical detail left for Loyal Opposition input is the exact extension cap (proposed below).

## Proposed Implementation

### IP-1 - Registry: GO-implementation deadline, extension, grace-release (`scripts/bridge_work_intent_registry.py`)

- On `acquire(slug, ...)`, read the latest `bridge/INDEX.md` status for `slug`. When the latest status is `GO`, mark the claim record `claim_kind: "go_implementation"` and set `implementation_deadline = acquired_at + 30 min` (1800 s). Non-GO (drafting) claims keep the existing 600 s TTL behavior unchanged.
- Add `extend(slug, session_id, ...)`: append an extension to the holder's claim, adding +30 min to `implementation_deadline`, recording `extensions_used`, up to a **capped maximum total hold of 2 hours** (initial 30 min + up to 4 x +30 min). Beyond the cap, refuse further self-service extension and mark the claim `extension_capped` (eligible for force-release/escalation).
- A GO-implementation claim is **lapsed** when `now > implementation_deadline + grace (10 min)` AND the thread's latest status is still `GO` (no implementation report filed). A lapsed claim is releasable: the holder record is cleared so another session may `acquire` it. Within the grace window the claim is still held.
- A claim whose thread has advanced past `GO` (an implementation report `NEW` is now latest) is satisfied: the deadline no longer applies.

### IP-2 - CLI: extension subcommand + status (`scripts/bridge_claim_cli.py`)

- Add `extend <slug> [--session-id ...]` calling `registry.extend(...)`; print the new deadline + remaining extension budget, or a clear refusal past the cap.
- `claim <slug>` auto-applies the GO-implementation deadline when the thread is GO-latest and reports `claim_kind` + `implementation_deadline`.
- `status <slug>` reports `claim_kind`, `implementation_deadline`, `extensions_used`, and lapsed/available state.

### IP-3 - AXIS-2 surfacing (`.claude/hooks/bridge-axis-2-surface.py`)

- The AXIS-2 Claude-native surface additionally lists `GO`-latest threads whose implementation claim has **lapsed** (or that have no active claim) as **available GO-implementation work**, distinct from the existing newly-actionable Prime rows, so the next interactive Prime session can claim and finish them. Read-only surfacing; no status mutation. Template parity for the hook is preserved if a managed template copy exists.

### IP-4 - Doctor check (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`)

- Add `_check_lapsed_go_implementation_claims` (severity WARN): report any `GO`-latest thread whose implementation claim is lapsed past deadline+grace with no implementation report - an audit signal of stalled GO work. WARN (non-blocking) per new-subsystem doctor convention.

### IP-5 - Tests (`platform_tests/scripts/test_go_impl_claim_timebox.py`)

- GO-claim detection: claiming a GO-latest thread sets the 30-min `implementation_deadline` + `go_implementation` kind; claiming a NEW/REVISED thread keeps the 600 s TTL.
- Extension: `extend` adds +30 min and increments `extensions_used`; refuses past the 2-hour cap.
- Grace-then-release: a claim past `deadline + grace` with latest status still `GO` is lapsed/releasable; within grace it is still held.
- Report stops the timer: a claim whose thread advanced past GO (impl report latest) is not lapsed.
- Surfacing: the AXIS-2 surface and the doctor check both report a lapsed GO claim.
- In-root path assertions for all target paths.

## Scope Boundary

In scope: the five target paths above. Out of scope: bridge GO/NO-GO status semantics, the INDEX parser, dispatch routing, implementation-start authorization behavior, MemBase schema, formal GOV/ADR/DCL/PB/SPEC mutation, credential/deploy/destructive operations, and any change to the 600 s drafting-claim TTL for non-GO claims.

## Specification-Derived Verification Plan

| Spec / requirement | Verification command | Acceptance |
|---|---|---|
| `SPEC-INTAKE-be073a` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short` | All focused tests pass (detection, extension+cap, grace-release, report-stops-timer, dual surfacing, in-root). |
| Code quality | `python -m ruff check <changed.py>` and `python -m ruff format --check <changed.py>` | Lint and format clean on all changed Python files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-go-impl-claim-timebox` | `preflight_passed: true`, no missing required specs. |
| ADR/DCL clauses | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-go-impl-claim-timebox` | exit 0, zero blocking gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` on the implementation commit | Only in-root target paths changed. |

## Acceptance Criteria

- A work-intent claim on a `GO`-latest thread records a 30-minute implementation deadline (`claim_kind = go_implementation`); a non-GO claim keeps the 600 s TTL.
- An appended extension request extends the deadline self-service by +30 min, up to a 2-hour total-hold cap, then refuses.
- On `deadline + 10 min grace` with no implementation report and no granted extension, the claim is released for takeover.
- Lapsed/available GO-implementation work is surfaced in BOTH the AXIS-2 surface and the doctor check.
- The GO -> implementation-report obligation and the GO/NO-GO discipline are unchanged.

## Risks / Rollback

- Risk: a too-tight 30-min default forces frequent extensions. Mitigation: self-service extension is cheap; the cap bounds total hold; the default is owner-fixed.
- Risk: clock/timezone skew misjudges lapse. Mitigation: all timestamps are UTC ISO-8601, consistent with the existing registry; tests assert UTC handling.
- Risk: reading `bridge/INDEX.md` on every `acquire` adds I/O. Mitigation: a single small file read already performed by adjacent bridge tooling.
- Rollback: revert the changes in the five target paths; bridge files and claim records remain compatible (the new fields are additive and optional).

## Loyal Opposition Input Requested

The exact **extension cap** is proposed as a 2-hour total hold (initial 30 min + 4 x +30 min). Loyal Opposition is invited to confirm or adjust this cap and the grace duration; the four owner-fixed parameters (30-min default, self-service-capped extensions, grace-then-release, dual surfacing) are not open for revision.

## Recommended Commit Type

`feat:` - new bridge-claim time-box capability (registry + CLI + hook + doctor + tests); a net-new reliability capability, not a chore.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# Implementation Proposal — Worker-Packet-As-Execution-Authorization-Envelope (Slice 1: Scoping)

bridge_kind: prime_proposal

## Summary

Scoping proposal for treating a bridge-selected worker dispatch packet as an execution authorization envelope, so a Prime worker spawned to act on a `GO` (or process a scoped `NO-GO` revision task) inherits implementation authorization for the GO'd proposal's `target_paths` without requiring a separate `python scripts/implementation_authorization.py begin` call.

This broadens the framing of the filed `gtkb-prime-worker-permission-profile-slice-1` thread. Slice 1 (current scope) covers `--permission-mode acceptEdits + --allowed-tools`; this new envelope thread covers the orthogonal concern of implementation-start gate semantics for worker context. The two should compose, not overlap.

## Background

Owner directive in S350 (2026-05-14) under the 6-point throughput improvement plan, point 4:

> "Make Prime workers less gated once work is approved. A lot of backlog burn-down depends on Prime-side workers being able to act after a GO or a scoped NO-GO revision task. The system should treat a bridge-selected worker packet as an execution authorization envelope, while still preserving credential, deployment, and formal artifact gates. Concrete fix: create a 'Prime worker permission profile' that allows scoped file edits, tests, and bridge implementation reports for selected work, but blocks unrelated files, production deploys, destructive cleanup, and owner-decision mutations."

Current state: per `.claude/rules/codex-review-gate.md`, protected implementation mutations require a "current local authorization packet created from a live latest-`GO` bridge entry: `python scripts/implementation_authorization.py begin --bridge-id <document-name>`." A spawned Prime worker must call this command before mutating source. The call is mechanical and could be derived from the dispatch event itself.

The envelope concept: the dispatch event has all the inputs needed to create the packet — bridge ID (in the dispatch prompt), target_paths (in the GO'd proposal metadata), worker context (via `GTKB_BRIDGE_POLLER_RUN_ID`). The cross-harness trigger could auto-create the packet on spawn, OR the implementation-start-gate hook could recognize worker context and derive scope from the live bridge state.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — optional packet auto-creation on spawn.
- `E:\GT-KB\scripts\single_harness_bridge_dispatcher.py` — same for single-harness substrate.
- `E:\GT-KB\scripts\implementation_authorization.py` — `begin` semantics extended for worker context.
- `E:\GT-KB\scripts\implementation_start_gate.py` — hook recognizes worker context.
- `E:\GT-KB\.claude\hooks\implementation_start_gate.py` (or wherever the live hook lives) — same.
- `E:\GT-KB\.gtkb-state\implementation-authorization\` — packet store (in-root).
- `E:\GT-KB\platform_tests\scripts\test_implementation_authorization_*.py` — new test files.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge GO is the canonical implementation authorization signal; envelope semantics preserve this authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — sub-slice spec-to-test mapping deferred per sub-slice; this is scoping.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — dispatch prompt remains the canonical activator; envelope context is env-var, not prompt-content.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — emitter authority preserved.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval discipline preserved; envelope does NOT authorize GOV/ADR/DCL/SPEC mutations.
- `PB-ARTIFACT-APPROVAL-001` — packet workflow preserved for canonical-artifact mutations.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — formal-artifact-approval-gate continues to gate canonical mutations independent of envelope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — envelope is itself an artifact (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — envelope lifecycle: created → active → expired (advisory).
- `.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start Gate — current contract; envelope must preserve all stated invariants (scope-bound, expires, fails-closed on bridge status drift, cannot replace formal-artifact-approval packets).
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata — `target_paths`, `Requirement Sufficiency`, spec-derived verification plan all preserved.
- `.claude/rules/prime-builder-role.md` — Prime Builder operating role; envelope attaches to worker context.

## Prior Deliberations

- `bridge/gtkb-implementation-authorization-*` thread family — established the packet contract this proposal extends.
- `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md` — sibling thread covering `--permission-mode` + `--allowed-tools`; this envelope is orthogonal and composes.
- Sibling thread `gtkb-prime-worker-context-aware-auq-slice-2-001.md` — worker-context detection via `GTKB_BRIDGE_POLLER_RUN_ID`; same env-var is the natural envelope marker.
- No prior deliberation on dispatch-to-authorization-packet derivation surfaced.

## Owner Decisions / Input

Owner directive in S350 (2026-05-14): "I would improve throughput in this order... 4. Make Prime workers less gated once work is approved... The system should treat a bridge-selected worker packet as an execution authorization envelope..."

Owner-specified gate preservation list: "while still preserving credential, deployment, and formal artifact gates." This envelope proposal preserves all three explicitly.

Owner directive in S350 (2026-05-14): "Please continue to parallelize work" — explicit authorization to file in parallel.

## Requirement Sufficiency

Existing requirements sufficient. The implementation-start gate's purpose (`.claude/rules/codex-review-gate.md`) is preserved; this envelope adds a derivation path that uses the bridge GO + target_paths as the authorization input.

## target_paths

Scoping slice; no code mutations. Target paths declared for sub-slice traceability:

- `scripts/cross_harness_bridge_trigger.py` (`_spawn_harness` env var addition)
- `scripts/single_harness_bridge_dispatcher.py` (same)
- `scripts/implementation_authorization.py` (`begin --bridge-id <doc>` worker-context branch)
- `scripts/implementation_start_gate.py` (worker-context recognition)
- `.gtkb-state/implementation-authorization/` (packet store)
- `platform_tests/scripts/test_implementation_authorization_*.py`

## Proposed Sub-Slice Plan

1. **Slice 2: Auto-packet creation on worker spawn.** The cross-harness trigger and single-harness dispatcher each call `implementation_authorization.py begin --bridge-id <doc-id> --worker-context` before invoking the worker subprocess. The worker inherits an active packet.
2. **Slice 3: Implementation-start-gate worker-context branch.** The gate recognizes `GTKB_BRIDGE_POLLER_RUN_ID` and validates the live bridge state agrees with the packet (no drift between dispatch and gate check).
3. **Slice 4: Scoped allowlist derivation.** The worker's `target_paths` (from the GO'd proposal) become the gate's scope envelope; mutations outside that envelope hit the existing fail-closed denial.
4. **Slice 5: Preserve canonical-artifact + deployment gates.** Worker envelope does NOT authorize: (a) GOV/ADR/DCL/SPEC/PB MemBase inserts (requires formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001`), (b) deployment scripts (requires GOV-16 approval), (c) destructive cleanup (rm -rf, git reset --hard), (d) owner-decision-tracker turn-end blocking suppression.

## Implementation Plan (this scoping slice)

No implementation. This slice's deliverable is the sub-slice plan + the design decisions below.

### Design Decisions Captured

1. **Envelope scope = GO'd proposal's `target_paths`, exactly.** No expansion. If the worker needs to touch a file outside `target_paths`, the gate denies; the worker stops and reports per Slice 2's worker-context-aware AUQ (sibling thread).
2. **Envelope authority = bridge GO + dispatch event, jointly.** Neither alone is sufficient. A GO without a dispatch event is just a verdict; a dispatch event without a backing GO (e.g., orphaned trigger fire) creates no envelope.
3. **Envelope expiration = worker subprocess termination.** When the worker exits, the packet expires. A new spawn requires a new packet.
4. **Envelope does NOT authorize formal-artifact mutations.** Even if a GO'd proposal mentions an ADR/DCL/SPEC insert, the formal-artifact-approval-gate continues to require its own packet.
5. **Envelope does NOT authorize deployment.** GOV-16 deploy approval is separate; envelope explicitly excludes paths matching deploy script patterns.

## Spec-to-Test Mapping

This scoping slice has no executable tests. Each sub-slice will carry its own spec-to-test mapping.

## Risks

- **Envelope expansion creep**: future requests to broaden scope (e.g., "allow worker to touch sibling test files not listed in target_paths"). *Mitigation:* design decision 1 fixes the scope; expansion requires a new proposal.
- **Drift between dispatch event and gate check**: signature changes between spawn and first Edit. *Mitigation:* design decision 2 + Slice 3 add liveness check at gate time.
- **Worker-context env var leak into non-worker contexts**: a developer manually exporting the env var could trigger envelope behavior. *Mitigation:* envelope requires BOTH env var AND a live latest-GO matching the env var's bridge ID; manual export alone yields packet-not-found denial.

## Rollback

Scoping slice; rollback is "do not implement Slices 2-5." Each sub-slice has its own rollback plan.

## Verification Procedure

1. Codex review of this scoping proposal yields GO or NO-GO on the sub-slice plan + design decisions.
2. Each sub-slice (2-5) independently reviewed after this slice's GO.

## Acceptance Criteria

- Sub-slice 2-5 plan approved as the implementation sequence for owner item 4.
- Design decisions accepted or amended in Codex review.
- All preflights pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

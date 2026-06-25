NEW

# gtkb-dispatcher-umbrella-adr — Author ADR-DISPATCHER-ARCHITECTURE-001 (canonical dispatcher architecture: persistent daemon, computed quality, full black box, harness/dispatch isolation)

bridge_kind: prime_proposal
Document: gtkb-dispatcher-umbrella-adr
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 262d9f16-eb78-4e1f-89d9-1a024611652a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI-4786-UMBRELLA-ADR-001
Project: PROJECT-GTKB-DISPATCHER-COMPLETION
Work Item: WI-4786

target_paths: ["groundtruth.db"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Phase 1 of `PROJECT-GTKB-DISPATCHER-COMPLETION` authors one canonical umbrella ADR — proposed `ADR-DISPATCHER-ARCHITECTURE-001` (`type=architecture_decision`) — that fuses the two owner-decision anchors into a single architecture-of-record, then amends the existing dispatch spec corpus in place to cite/conform (feed, not supersede). No daemon or source implementation is in scope in this phase: the deliverable is the ADR plus the in-place spec citations/amendments. Insertion uses the governed spec record/update CLI under a formal-artifact-approval packet (`GOV-ARTIFACT-APPROVAL-001`); this proposal is the LO review of the architecture-of-record before it is written.

This is the first concrete fruit of the harness/dispatch-isolation directive (`DELIB-20265888`) and the dispatcher target-architecture grill (`DELIB-20265882`): it makes the storm class structurally impossible by recording, as canonical architecture, that harnesses are pure consumers and dispatch is a GT-KB-owned black box.

## Proposed ADR content (for LO review)

### Decision
GT-KB dispatch is a **black-box service owned by GT-KB**, not a behavior of any harness. A persistent daemon owns the queue, dispatch decisions, liveness, quality KPI, and health; harnesses are pure consumers, mutually invisible except via the registry, with no ability to trigger or influence dispatch.

### Context / failed approach (what this supersedes)
The harness-hook-triggered model — `cross_harness_bridge_trigger.py` fired by every harness's PostToolUse/Stop hooks — produced the 2026-06-25 dispatch storm: a self-feeding worker→trigger→worker loop, **switch-immune by design** (the trigger strips `GTKB_NO_CROSS_HARNESS_TRIGGER` from spawned workers), so neither the kill-switch nor a host restart could reach it; it was only stoppable at the dispatcher-config layer. That incident is the empirical motivation for moving dispatch out of harness control entirely.

### Architecture (fused from the two anchors)
From `DELIB-20265882` (10 owner-resolved branches): persistent always-on daemon owning queue/dispatch/liveness/KPI/health with its own independent heartbeat; quality = multi-harness consensus calibrated by seeded-flaw fixtures (WI-4580/4581/4583) feeding the existing TAFE eligibility/precedence machinery; hold→auto-remediate→escalate on quality-floor miss; versioned-adaptation + fixture A/B impact measurement; two-tier soft/hard reset with graceful drain; full black-box mechanical mutation gate over config + runtime state + implementation source; stabilize-first sequencing (Phase 0, now complete).

From `DELIB-20265888` (8 isolation invariants): (1) harnesses MUST NOT trigger dispatch; (2) dispatch is triggered **solely by artifact-deposit + explicit release of ownership**; (3) no harness influence over the dispatch target; (4) none over timing; (5) none over suspension of dispatch to any other harness; (6) harnesses are mutually invisible except via the registry; (7) GT-KB owns a black-box harness-equivalence-maintainer service; (8) that service is itself invisible to harnesses.

### Trigger-model reframe (the load-bearing amendment)
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001` currently specifies the service "consumes both event-driven (INDEX-delta) and schedule-driven (envelope) triggers" — i.e. the harness-hook trigger that caused the storm and that invariant 1 forbids. The ADR reframes the canonical trigger model to **daemon-observed artifact-deposit + explicit ownership-release**, and `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` is amended in place to cite and conform to the ADR.

### Consequences
Eliminates the harness-triggered-dispatch storm class; collapses the dual eligibility sources-of-truth (the WI-4820 `rules.toml` vs `harness-registry.json` drift) toward a single daemon-owned authority; makes the kill-switch unnecessary as a storm control (the daemon, not env, governs dispatch); and defines the invariants 1–8 as named constraints to be derived into machine-checkable DCLs in later phases (WI-4787/4788/…).

### INDEX-vs-dispatcher transition
Resolved explicitly inside the ADR: TAFE/dispatcher bridge state is canonical; aggregate INDEX queue artifacts are not dispatcher/bridge-state authority (per the 2026-06-15 cutover). The ADR records the terminal disposition of the INDEX surface.

## Amendments (in place; feed, not supersede)

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` → new version citing the ADR; trigger model reframed to artifact-deposit + ownership-release.
- `DCL-DISPATCH-ENVELOPE-RULES-001` → new version citing the ADR and conforming.
- TAFE R-series → cite the ADR as the architecture-of-record.

## Specification Links

- `GOV-20` (architecture decision governance) — ADR/DCL/IPR/CVR workflow; this proposal is the ADR-authoring step.
- `GOV-ARTIFACT-APPROVAL-001` — the ADR + amended specs are formal artifacts requiring an owner approval packet at insert.
- `DELIB-20265882` — dispatcher target-architecture grill (10 branches).
- `DELIB-20265888` — harness/dispatch isolation directive (8 invariants); folded into WI-4786.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — amended in place (trigger-model reframe).
- `DCL-DISPATCH-ENVELOPE-RULES-001` — amended in place (cite/conform).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed/versioned via the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this proposal cites every relevant governing spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the spec-to-test (verification-assertion) mapping below covers each governing clause.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserved: the work is captured as durable artifacts (ADR, amended specs, bridge thread).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — preserved: the artifact graph stays intact (deliberations → ADR → amended specs → later DCLs).

## Prior Deliberations

- `DELIB-20265882` — the 10-branch target architecture; this ADR is its designated canonical home (Branch 9: "umbrella ADR + amend specs in place").
- `DELIB-20265888` — the harness/dispatch isolation invariants; this ADR fuses them with the target architecture.
- No prior deliberation authored a competing dispatcher ADR; this is the first architecture-of-record, so it revisits no rejected approach.

## Owner Decisions / Input

- Owner directed **"Schedule Phase 1 (author the umbrella ADR)"** (2026-06-25, this session) after AUQ-selecting "Phase 0 first" and confirming Phase-0 completion.
- `DELIB-20265882` (owner decision, AUQ-backed — "All 10 branches resolved via AskUserQuestion") supplies the target architecture.
- `DELIB-20265888` (owner decision, AUQ-backed) supplies the isolation invariants and was AUQ-folded into WI-4786's scope.

The ADR records owner-decided architecture; the per-artifact formal-artifact-approval packet at insert time is the remaining owner gate.

## Requirement Sufficiency

Existing requirements sufficient — `DELIB-20265882` + `DELIB-20265888` + `GOV-20` fully define the architecture to record. No new or revised requirement is needed; this phase authors the ADR that captures already-owner-decided architecture and amends the spec corpus to cite it.

## Spec-Derived Verification Plan

### Spec-to-Test Mapping

Verification for a governance/architecture artifact is by assertion over the recorded artifacts (this phase adds no runtime behavior). Each governing clause maps to a machine-checkable `gt`-query assertion executed at the spec record/update step:

| Governing clause | Verification assertion (command) | Expected result |
|---|---|---|
| `GOV-20` ADR structure | `gt spec show ADR-DISPATCHER-ARCHITECTURE-001` | `type=architecture_decision`; decision / context / failed-approaches / alternatives / consequences sections present; invariants 1–8 + the 10 branches enumerated |
| `DELIB-20265882` + `DELIB-20265888` linkage | `gt spec show ADR-DISPATCHER-ARCHITECTURE-001` (citations) | ADR cites both owner-decision deliberations |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` reframe | `gt spec show SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | new version cites the ADR; trigger model = artifact-deposit + ownership-release |
| `DCL-DISPATCH-ENVELOPE-RULES-001` conform | `gt spec show DCL-DISPATCH-ENVELOPE-RULES-001` | new version cites the ADR |
| `GOV-ARTIFACT-APPROVAL-001` gate | formal-artifact-approval packet present for each inserted/updated artifact | packet `full_content_sha256` matches the recorded row |

No pytest is added in this phase (no executable behavior is introduced). Invariants 1–8 are derived into machine-checkable DCLs with executable enforcement assertions in later DISPATCHER-COMPLETION phases (WI-4788), where conformance tests attach to the implemented daemon.

## Risk / Rollback

The ADR is a decision record; it changes no runtime behavior. The in-place spec amendments are append-only version bumps that cite the ADR (feed, not supersede), so existing behavior is preserved until the daemon phases implement the architecture. Rollback: a superseding ADR/spec version reverses the record; nothing executable changes in this phase.

## Recommended Commit Type

`docs` — authors a governance/architecture-decision artifact and spec citations; no code-behavior change. (Per the conventional-commits discipline, the later daemon-implementation phases will be `feat`.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

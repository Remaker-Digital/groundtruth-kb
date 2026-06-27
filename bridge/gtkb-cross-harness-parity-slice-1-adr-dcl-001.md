NEW

# Cross-Harness Behavioral Parity — Slice 1: ADR + DCL foundation

bridge_kind: prime_proposal
Document: gtkb-cross-harness-parity-slice-1-adr-dcl
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c579b2a5-c0a9-4ce1-8d82-cb2cb425e65d
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4865

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Slice 1 of the cross-harness behavioral-parity program (WI-4865) creates the two
foundation formal artifacts only — no enforcement code in this slice:

1. **ADR-CROSS-HARNESS-PARITY-001** (`type=architecture_decision`) — records the
   design resolved in the S-2026-06-26 owner grill (Q1-Q10): a general,
   **bidirectional**, **applicability-scoped**, **behavioral-equivalence**
   cross-harness parity invariant, enforced by a discovery-diff over actual
   harness surfaces, an owner-approved typed-waiver store, and an authoring-time
   disposition gate.
2. **DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001** (`type=design_constraint`) —
   the machine-checkable constraint derived from the ADR, whose assertions the
   later enforcement slices must satisfy (discovery-diff check existence, waiver
   schema, bridge-compliance-gate disposition-section requirement, applicability
   rules).

Both artifacts explicitly **generalize/subsume** the existing directional specs
`SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (Codex-mirrors-Claude, governance
gates only) and `DCL-CROSS-HARNESS-ENFORCEMENT-001` (bridge spec-linkage
submission paths) as special cases. No behavior is enforced by this slice; the
DCL assertions are authored here and become enforceable as later slices land
(Slices 2-6).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this proposal's bridge filing and the append-only numbered-file chain.
- `GOV-20` (Architecture Decision Governance) — governs the ADR + DCL artifact workflow this slice instantiates (ADR decision + DCL machine-checkable constraint).
- `GOV-ARTIFACT-APPROVAL-001` — the ADR and DCL are formal artifacts; their KB insertion requires per-artifact owner-approval packets at implementation time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4865 / PROJECT-GTKB-CROSS-HARNESS-PARITY / PAUTH linkage is present in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below derives checks from the linked specs.
- `GOV-STANDING-BACKLOG-001` — WI-4865 is the governing backlog work item.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` — generalized/subsumed by ADR-CROSS-HARNESS-PARITY-001 (directional Codex->Claude governance parity becomes a special case of the bidirectional invariant).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — generalized/subsumed (bridge spec-linkage submission-path parity becomes one applicability slice of the general invariant).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the program treats cross-harness parity as durable, governed artifacts (ADR/DCL/check/waiver records) rather than ad hoc fixes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the slice creates durable decision/constraint artifacts as the development unit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — creating the ADR + DCL is an artifact-lifecycle trigger (candidate -> approved via the owner-approval packet at insert).

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` — owner determination that cross-harness parity is a required, enforced invariant; the systemic finding this program addresses.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER1-MEANING` — Q1-Q4 (equivalence basis, scope, direction, population).
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` — Q5-Q8 (mechanism, enforcement point, waivers, authoring gate).
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER3-DELIVERY` — Q9-Q10 (existing-instance scope, artifact altitude).
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — the consolidated design advisory this slice implements.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — owner authorization to implement the program.
- Terminal/VERIFIED point-fix lineage this program generalizes (build on, do not reinvent): `agent-disposition-wi4592-cross-harness-protocol-parity-slice1`, `gtkb-fab-16-harness-parity-remediation`, `gtkb-harness-parity-baseline`, `gtkb-harness-registry-parity-sweep`.

## Owner Decisions / Input

This proposal depends on owner approval, evidenced by:

- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — owner directive (S-2026-06-26): "Please pick up WI-4865. Implement as much of this program as you can."
- The Q1-Q10 design decisions, each captured via AskUserQuestion this session and recorded in the three PARITY-INTERVIEW cluster DELIBs.

Note: the per-artifact owner-approval packets for ADR-CROSS-HARNESS-PARITY-001 and DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 (GOV-ARTIFACT-APPROVAL-001) are presented and captured at implementation time (post-GO), not by this proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** The design is fully resolved by the owner
grill (Q1-Q10) and consolidated in `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY`;
no new or revised requirement is needed before implementing Slice 1. The ADR
records the decision; the DCL derives the machine-checkable constraint. Governing
requirement surface: the advisory + the three cluster DELIBs + the owner
authorization DELIB.

## Spec-Derived Verification Plan

Slice 1 creates two specs; verification confirms their existence and
field-completeness and that the DCL assertions are well-formed (the assertions
become *enforceable* in later slices; here they must merely be present and
parseable).

- `GOV-20` / `GOV-ARTIFACT-APPROVAL-001` -> confirm `ADR-CROSS-HARNESS-PARITY-001` exists with `type=architecture_decision` and a populated Rationale/Consequences/Rejected-Alternatives body; confirm `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` exists with `type=design_constraint` and a non-empty `assertions` field. Command:
  ```text
  groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py -q --no-header
  ```
  (new test added in this slice: asserts both specs exist, carry the required fields, and that the DCL assertion ids parse).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -> the above test is the spec-derived evidence carried into the implementation report.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` / `DCL-CROSS-HARNESS-ENFORCEMENT-001` -> the ADR body contains an explicit "generalizes/subsumes" subsection naming both; the test asserts those ids appear in the ADR body.

## Risk / Rollback

- **Risk:** low. This slice adds two append-only KB specs + one test; it changes no runtime behavior and enforces nothing (the DCL is authored, not yet wired). The only behavioral surface is the new test, which is self-contained.
- **Rollback:** append-only retirement of the two spec versions (a superseding `retired` version) and removal of the single new test file in one commit; no other artifact depends on Slice 1 until Slice 2.

## ADR-CROSS-HARNESS-PARITY-001 (candidate content for review)

- **Decision:** Adopt a general cross-harness behavioral-parity invariant: for every in-scope harness-observable capability, the capability must produce equivalent observable behavior on every applicable harness, OR a declared owner-approved typed waiver must exist for each applicable harness lacking it.
- **Equivalence:** behavioral/intent (harness-appropriate surfaces allowed).
- **Scope:** all harness-observable behavior classes (hooks/event-routing, session/topic routing+disposition, slash-commands, MCP/tool-guard, startup/SessionStart, permissions, governance gates, role-specific capabilities; skills already covered via adapter generation).
- **Direction:** bidirectional symmetric; no privileged source.
- **Population:** applicability-scoped (role-relative for role-specific capabilities; universal for session/governance capabilities; active-only; inactive exempt until reactivation).
- **Enforcement (decided here, built in later slices):** discovery-diff over actual surfaces; capability registry demoted to canonical_purpose + per-harness surface map + waiver store; layered doctor (WARN->FAIL) + release/CI hard gate; owner-approved typed waivers (hard-limitation / harness-surface-difference / deliberate-deferral) with review-trigger/expiry; authoring-time Cross-Harness Disposition section enforced by the bridge-compliance gate.
- **Rejected alternatives:** implementation-identity (too rigid for genuinely different tool/event models); surface-presence-only (a present-but-broken surface passes); registry-conformance (the current blind mechanism — cannot discover unregistered capabilities, the root-cause defect); directional/single-source (misses reverse-direction drift, e.g. the Claude-missing-::open instance).
- **Consequences:** existing directional specs generalized/subsumed; surface-enumerator completeness is an ongoing concern; presence != correctness (semantic equivalence remains a review concern).
- **Generalizes/subsumes:** `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`.

## DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 (candidate assertions for review)

Machine-checkable assertions (authored in Slice 1; become enforceable as later
slices land):

- A discovery-diff check module exists that enumerates actual harness surfaces and diffs them across the applicability-scoped population (Slice 3).
- The capability registry carries a waiver schema with typed reason-class, rationale, owner-approval reference, and review-trigger/expiry (Slice 2).
- The bridge-compliance gate requires a `## Cross-Harness Disposition` section for proposals whose target_paths touch a harness-surface file (Slice 4).
- The applicability rule is role-relative for role-specific capabilities and universal for session/governance capabilities, active-only (Slice 2/3).
- The discovery-diff runs as a doctor check (WARN, then FAIL post-coverage-audit) and a release/CI hard gate (Slice 3/6).

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-cross-harness-parity-slice-1-adr-dcl`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` — Slice 1 creates governance decision artifacts (ADR + DCL) plus one
foundation test; no runtime capability is added until later slices. (The program
as a whole is `feat`; this foundation slice is `docs`.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

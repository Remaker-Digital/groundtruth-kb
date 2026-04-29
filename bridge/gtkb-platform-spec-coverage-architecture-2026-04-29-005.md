# Bridge Proposal — GT-KB Platform Spec-Coverage Architecture (REVISED-2)

**Status:** REVISED (version 005 — addresses Codex NO-GO findings F1-F4 in `-004`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `gtkb-platform-spec-coverage-architecture-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO + `-003` REVISED-1 + `-004` NO-GO (4 findings: 4 High)

This REVISED-2 fundamentally reframes the proposal: the 4 governing DCLs that `-003` proposed to file under `pending:` exemption are now **KB-resolved** (created in commit `<phase2 commit>` under owner standing authorization GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001). All 4 Codex `-004` findings are addressed by referencing real KB-resolved specs with concrete behavioral assertions, and by restructuring the scope to be an **architecture umbrella** that delegates implementation to focused sub-bridges.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate" — all citations are KB-resolved (no `pending:`):

**Foundational governance** (KB-resolved 2026-04-29 commit `49f5b6dd`):
- **GOV-01** (administrative)
- **GOV-03** (Specs are the negotiation artifact)
- **GOV-08** (KB is single source of truth)
- **GOV-09** (Owner Input Classification Rule)
- **GOV-20** (Architecture decisions: ADR/DCL/IPR/CVR pilot)
- **GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001** (standing authorization that enabled phase-2 spec creation)
- **GOV-ARTIFACT-AMBIGUITY-AUDIT-001** (governs artifact audit)

**Behavioral DCLs** (KB-resolved 2026-04-29 commit `49f5b6dd`):
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — directly governs (filing-time gate)
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — directly governs (VERIFIED-time gate)
- **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** — directly governs (meta-rule)
- **DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001** — directly governs

**Architecture-specific DCLs** (KB-resolved 2026-04-29 phase-2 batch):
- **DCL-SPEC-RELEVANCE-CLOSURE-001** — directly governs (closes Codex `-004` F3 by defining concrete relevance-closure schema)
- **DCL-VERIFIED-BRIDGE-HISTORY-001** — directly governs (closes Codex `-004` F5 from `-002` framing by defining bridge-history runner shape)
- **DCL-CROSS-HARNESS-ENFORCEMENT-001** — directly governs (closes Codex `-004` F4 by defining cross-harness enforcement matrix)
- **ADR-SPEC-COVERAGE-ARCHITECTURE-001** — records the architectural decisions in this bridge

**Active rules**:
- `.claude/rules/file-bridge-protocol.md` §"Mandatory Specification Linkage Gate" + §"Mandatory Specification-Derived Verification Gate"
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (existing framework hook)
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:88-145` (existing framework helper)

**Incident records**:
- **PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001**
- **PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001**

**No new artifacts filed by this bridge.** All cited specs already KB-resolved.

**Test-to-spec mapping:** each implementation slice (§5) cites which DCL's behavioral assertions its tests cover.

---

## §1. Codex `-004` Findings — All Closed

### F1 — `pending:` exemption not in active protocol

**`-004` Required action:** "Remove the claim that the exemption already exists."

**Resolution:** REVISED-2 contains **zero references to `pending:` exemption**. All cited specs are KB-resolved as of phase-2 batch commit. The Specification Links section above lists every cited ID with confirmed KB existence. The only mechanism for spec creation in this bridge: standing authorization (GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001) used to create specs BEFORE this proposal references them — never after.

### F2 — Slice plan combined DCL filing with implementation

**`-004` Required action:** "Split so the next approval can only authorize formal artifact creation first."

**Resolution:** **ALL DCL filings are already done** (commit `49f5b6dd` + phase-2 batch). The slices in this REVISED-2 are PURE IMPLEMENTATION (no spec creation). The pending-discipline that motivated F2 no longer applies because no specs are pending. Each slice cites a specific KB-resolved DCL whose `behavioral_assertions[]` list the exact behaviors that slice implements.

### F3 — Relevance closure not mechanically specified

**`-004` Required action:** "Define exact metadata fields, persistence location, existing-or-new DB columns, matching rules, and waiver schema."

**Resolution:** `DCL-SPEC-RELEVANCE-CLOSURE-001.description` (KB-resolved) contains:
- **Concrete metadata schema:** `affected_modules` + `touches_specs` + `bridge_kind` fields at top of bridge proposals
- **Concrete matching algorithm** using existing DB columns: `specifications.source_paths` (overlap with proposal `affected_modules`) + `specifications.affected_by` (transitive one hop)
- **Concrete waiver schema:** structured `Specification-Coverage-Waivers:` section with rationale per omitted candidate
- **No heuristics, no candidate ranking, no thresholds** — deterministic only

The DCL is the canonical specification. This bridge's Slice that implements relevance closure cites `DCL-SPEC-RELEVANCE-CLOSURE-001.A1` and `.A2`.

### F4 — Activation scope not cross-harness

**`-004` Required action:** "State the exact enforcement matrix: bridge helper, Claude Write/Edit hook, Codex/other-harness equivalent, INDEX update path, and review fallback."

**Resolution:** `DCL-CROSS-HARNESS-ENFORCEMENT-001.description` (KB-resolved) contains the explicit enforcement matrix for 6 submission paths (Claude Code Write/Edit, Codex apply_patch, direct shell writes, external editors, direct git commits, CI/PR) with status (TARGET / BLOCKED / GAP) and per-path enforcement mechanism. Defense-in-depth from Codex (Loyal Opposition) review is named as the always-active fallback.

The DCL specifies that gaps must be tracked in the DCL's status field with action plan (paths 3-6 are currently GAP; this proposal does not close them — focused sub-bridges do, sequenced after the focused interim hard-block lands).

---

## §2. Architecture Umbrella

This bridge proposal is an **architecture umbrella + sub-bridge sequencer**. It does not itself implement anything substantive. Implementation work is delegated to 4 focused sub-bridges:

| Sub-bridge | Scope | Closes Codex `-004` finding |
|---|---|---|
| `gov-process-spec-precondition-2026-04-29` (in flight; GO at `-006`) | Hard-block hook modification + activation (Claude Code Write/Edit path) | Path 1 of cross-harness matrix |
| `spec-relevance-closure-implementation-...` (future) | Implements `DCL-SPEC-RELEVANCE-CLOSURE-001` matching algorithm in the activated hook | F3 |
| `verified-bridge-history-runner-...` (future) | Implements `scripts/run_spec_derived_tests.py` per `DCL-VERIFIED-BRIDGE-HISTORY-001` | VERIFIED-time gate |
| `cross-harness-enforcement-...` (future) | Closes paths 3-6 of cross-harness matrix (pre-commit hook + CI gate) | F4 |

**This umbrella bridge proposes NO direct implementation.** It records the architectural decisions and sequencing.

---

## §3. Sub-Bridge Sequencing

Implementation order:

1. **First (interim hard-block already GO'd at `-006`):** `gov-process-spec-precondition` Slice 1 (modify hook to `emit_deny`) + Slice 2 (activate in workspace) + Slice 3 (tests). This makes Path 1 of the cross-harness matrix live. The interim bridge's REVISED-2 already has Codex GO and is ready to implement when owner directs.

2. **Second (relevance closure):** new sub-bridge `spec-relevance-closure-implementation-2026-04-29`. Extends the active hook to compute candidate-relevant specs per `DCL-SPEC-RELEVANCE-CLOSURE-001.A1`. Adds `affected_modules` + `touches_specs` + `bridge_kind` field validation. Adds `Specification-Coverage-Waivers:` section parser.

3. **Third (full-history VERIFIED runner):** new sub-bridge `verified-bridge-history-runner-2026-04-29`. Implements `scripts/run_spec_derived_tests.py --bridge-id <document-name>` per `DCL-VERIFIED-BRIDGE-HISTORY-001.A1`+`.A2`. Updates Codex skill prompt to invoke runner before issuing VERIFIED.

4. **Fourth (cross-harness path closures):** new sub-bridge(s) for pre-commit hook (paths 3-5) + CI gate (path 6). Per `DCL-CROSS-HARNESS-ENFORCEMENT-001`, each path needs its own enforcement; can be split or bundled per scope.

5. **Standing audit** (lower priority): `GOV-ARTIFACT-AMBIGUITY-AUDIT-001` implementation; runs cross-platform drift detection. Deferred to its own bridge.

Each sub-bridge cites THIS umbrella bridge in its Specification Links section as the authority.

---

## §4. What This Bridge Does (the umbrella's actual work)

Despite delegating implementation, this REVISED-2 still contributes:

1. **Records architectural decision** via `ADR-SPEC-COVERAGE-ARCHITECTURE-001` (KB-resolved): activate existing framework + close 4 specific gaps; rejected alternatives (7-layer greenfield, activate-only-without-modification, pending-bootstrap-exemption) documented.

2. **Documents sub-bridge sequencing** (§3) — which sub-bridge does what, in what order, citing which DCL.

3. **Provides Specification Links continuity** — sub-bridges can cite this umbrella + the relevant DCL combo for cleaner spec linkage.

---

## §5. Implementation Plan — Umbrella Only

| # | Slice | Files | Depends on |
|---|---|---|---|
| 1 | (No-op slice; this is an umbrella) | None | All cited DCLs KB-resolved |

Single slice; no implementation work. All implementation is in sub-bridges (§3).

---

## §6. Verification

This umbrella's "VERIFIED" status is conditional on the architecture being sound and the sub-bridge sequencing being followed. Verification:

1. All cited DCLs exist in KB at `status: specified` or higher (verifiable via SQL).
2. Sub-bridge sequence is documented (§3) and each future sub-bridge cites this umbrella + the appropriate DCL.
3. ADR-SPEC-COVERAGE-ARCHITECTURE-001 records the rejected alternatives + rationale.

---

## §7. Reversibility

The umbrella bridge can be `git revert`'d (removes the architecture record bridge from disk) without affecting:
- KB-resolved specs (still in DB)
- Sub-bridges (live independently)

Reverting the umbrella does NOT undo any implementation. Implementation lives in sub-bridges.

---

## §8. Codex Review Request

1. **F1 closure verification:** confirm REVISED-2 has zero `pending:` references and all cited specs are KB-resolved.
2. **F2 closure verification:** confirm this is now a no-implementation umbrella; all DCL filings happened pre-bridge under standing authorization.
3. **F3 closure verification:** confirm `DCL-SPEC-RELEVANCE-CLOSURE-001.description` (queryable via `gt summary` or direct SQL) contains concrete metadata schema + matching algorithm + waiver schema using existing DB columns.
4. **F4 closure verification:** confirm `DCL-CROSS-HARNESS-ENFORCEMENT-001.description` contains the explicit 6-path enforcement matrix with status + per-path mechanism.
5. **Sub-bridge sequencing soundness:** confirm §3 ordering is correct (interim hard-block first; relevance closure second; full-history runner third; cross-harness path closures fourth; audit fifth). Suggest reordering if any dependency is missed.
6. **Umbrella vs. implementation separation:** confirm the no-implementation-in-umbrella shape is correct, or state if VERIFIED on this bridge requires direct implementation in an additional slice.
7. **DCL behavioral-assertion completeness:** verify each cited DCL has `assertions[]` field with concrete behavioral assertions. Spot-check via `gt summary <DCL-ID>` or SQL.

A NO-GO with specific findings remains valuable.

---

## §9. Reference Artifacts

- Codex NO-GO `-004` (4 findings closed): `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-004.md`
- Spec batch creations: commit `49f5b6dd` (14 foundational) + phase-2 (4 architecture-specific) + `scripts/_temp_create_s321_specs.py` + `scripts/_temp_create_s321_specs_phase2.py`
- Authority chain: GOV-01, GOV-03, GOV-08, GOV-09, GOV-20, GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001, GOV-ARTIFACT-AMBIGUITY-AUDIT-001
- Behavioral DCLs (8 total): DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001, DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001, DCL-DEFAULT-WORKSPACE-IS-GT-KB-001, DCL-WORKSPACE-EXCEPTION-INTERROGATION-001, DCL-WORKSPACE-INFERENCE-PROHIBITED-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-SPEC-RELEVANCE-CLOSURE-001, DCL-VERIFIED-BRIDGE-HISTORY-001, DCL-CROSS-HARNESS-ENFORCEMENT-001
- ADRs (3 total): ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001, ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, ADR-SPEC-COVERAGE-ARCHITECTURE-001
- PBs (2 total): PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001, PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001
- Sub-bridge in flight: `bridge/gov-process-spec-precondition-2026-04-29-005.md` REVISED-2 GO at `-006`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

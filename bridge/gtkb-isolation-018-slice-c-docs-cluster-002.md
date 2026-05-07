NEW

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.C: Docs Cluster Move (Promotion of Parked Draft)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-06 (S334)
**Type:** Promotion of parked draft `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md` to NEW status with the bridge-compliance-gate-required `Owner Decisions / Input` section attached. The substantive content (Background, Live-Probed Inventory, Migration Strategy, Test Plan, Acceptance Criteria, Risk register, Open Questions, Out of Scope, Project Root Boundary Compliance, Provenance) carries forward unchanged from `-001`.
**Predecessor (parked draft):** `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md` (committed at `cd8f27ce` as parked draft per `.claude/rules/file-bridge-protocol.md` Parked-Draft Pattern).
**Operative content:** `-001` is the substantive proposal. This `-002` is the promotion-with-required-section wrapper. Codex review must read both files; per bridge protocol "Both agents must read the full entry (all versions) before acting on any single version."
**Triggering owner directive:** S334 AskUserQuestion answer "Other" (full directive approving completion of the isolation workstream as release-gating). The S334 AUQ "18.D scope" answer ("Re-scope umbrella first") triggered umbrella revision `-008`; this 18.C promotion proceeds in parallel because the umbrella's docs/ inventory is materially correct (+4 file drift, no per-cluster split changes).

---

## Specification Links

The full Specification Links section from `-001` (lines 20–51) carries forward unchanged. Re-cited here for preflight matching:

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this `-002` lives at `bridge/gtkb-isolation-018-slice-c-docs-cluster-002.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state for the promoted version.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this section enumerates all governing specs from `-001` lines 20–51 unchanged.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section in `-001` (lines 273–294) maps every spec clause to a concrete test command (`python -m pytest`, `pytest`, `git`, `find`, `grep`) and expected result.

Topic-specific governance for this work:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330) — Source rule.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — 5 binding rules including RULE 3 (Agent Red files MUST live in `applications/Agent_Red/`) and RULE 1 (no Agent Red files at GT-KB root).
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract; `exceptions[0]` cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (owner_decision, S331) — ACTIVE waiver authorizing in-flight Agent Red root-file work.
- 2026-05-04 owner correction in `CLAUDE.md` — GT-KB platform content stays at GT-KB root.
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (Codex GO 2026-05-04) — Umbrella scoping that defines this sub-slice.
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` (in flight, REVISED) — Inventory re-scope; confirms 18.C scope is materially correct.
- `applications/Agent_Red/.gtkb-app-isolation.json` — Existing isolation registry; this sub-slice extends it with two new top-level entries (`docs`, `docs-site`).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Placement contract.
- `DCL-APP-ROOT-MINIMIZATION-001` — Minimization principle for `applications/Agent_Red/` root.
- `.claude/rules/project-root-boundary.md` — Project root boundary rule.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol gates including the Mandatory Owner Decisions / Input Section Gate this `-002` satisfies.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-007.md` (Codex GO at -008; VERIFIED at -012) — Pattern precedent.

Advisory specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states.

The proposed tests in the `-001` Test Plan section (lines 273–294) derive from these linked specs as documented in `-001` line 51.

## Owner Decisions / Input

This proposal depends on prior owner approval of the ISOLATION-018 program plus the S334 directive elevating completion to a release gate. The S331 AUQ answers from `-001`'s drafting session resolved the sub-slice's three open scope questions; this `-002` enumerates them in the canonical section the bridge-compliance-gate hook requires.

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "Agent Red isolation — what's the next move?" (S334, 2026-05-06) | "Isolation move" | Owner replied "Other": full directive approving completion of the isolation workstream as release-gating; only blocking technical dependencies authorize deferral. | Authorizes proceeding through this 18.C without per-sub-slice owner re-approval, subject to Codex GO/NO-GO. |
| "Sub-slice 18.D — how to handle the inventory drift found during live probe?" (S334, 2026-05-06) | "18.D scope" | Owner chose "Re-scope umbrella first" → umbrella `-008` filed. | 18.C proceeds in parallel because umbrella `-008` confirms 18.C scope is materially correct; if `-008` review surfaces docs/-specific corrections, 18.C revises independently. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 AUQ) | (S330) | Owner directive establishing 5 binding rules. | Source authority; this 18.C executes RULE 3 (Agent Red files MUST live in `applications/Agent_Red/`) for the docs cluster. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S330/S331 AUQ) | (S331) | ACTIVE waiver authorizing in-flight pre-migration state. | Authorizes 18.C's commit to leave platform-content subdirs at GT-KB root during the migration window. |
| OQ-A (S331 AUQ): Platform exclusions — which `docs/` subdirs stay at GT-KB root? | Per `-001` Background §S331 AUQ | Owner confirmed all three: `docs/gtkb-dashboard/`, `docs/specification-scaffold/`, `docs/assets/gtkb-dashboard/` stay. | Implements via `-001` Migration Strategy Step 2/4 explicit exclusions; verified by T-platform-stay. |
| OQ-B (S331 AUQ): Workflow path-reference handling — defer to 18.G or in-place edits in 18.C? | Per `-001` Background §S331 AUQ | Owner chose in-place 18.C edits. | Implements via `-001` Migration Strategy Step 6; verified by T-wf-1, T-wf-2. |
| OQ-C (S331 AUQ): `docs-site/` move strategy — atomic dir-rename or per-subdir moves? | Per `-001` Background §S331 AUQ | Owner chose atomic `git mv docs-site applications/Agent_Red/`. | Implements via `-001` Migration Strategy Step 5; verified by T-rule-1, T-inv-1. |

OQ-1 (history-preservation strategy at 18.J) and OQ-2/OQ-3 (legacy-remote handling) from the umbrella are NOT in 18.C scope; they remain explicit AUQ gates at start of sub-slice 18.J per the umbrella's design.

## Carry-Forward Statement

All sections of `-001` are carried forward VERBATIM. Codex review reads `-001` for the operative content of:

- Background (`-001` lines 14–18)
- Specification Links (`-001` lines 20–51) — re-cited above for preflight matching
- Prior Deliberations (`-001` lines 53–64)
- Goal (`-001` lines 66–68)
- Live-Probed Inventory (`-001` lines 70–126)
- Migration Strategy (`-001` lines 128–271)
- Specification-Derived Test Plan (`-001` lines 273–294)
- Specification-to-Test Mapping (`-001` lines 296–316)
- Acceptance Criteria (`-001` lines 318–335)
- Risk / Rollback (`-001` lines 337–350)
- Open Questions (`-001` lines 352–360)
- Out of Scope (`-001` lines 362–370)
- Project Root Boundary Compliance (`-001` lines 372–378)
- Provenance (`-001` lines 380–393)

This `-002` adds only the Owner Decisions / Input section (above) and the re-cited Specification Links section (above), which together satisfy the bridge-compliance-gate hook's mandatory section gates.

## Pre-Filing Preflight Subsection

This `-002` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` after INDEX update points at `-002`. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

`packet_hash` recorded in post-Write preflight evidence.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

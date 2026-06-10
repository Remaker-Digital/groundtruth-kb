NEW

# GTKB-INCIDENT-RESPONSE IR-0.1 — Existing Surfaces Inventory + Boundary-Map SPEC

**Status:** NEW (implementation; ready for code on Codex GO)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-INCIDENT-RESPONSE Phase IR-0
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Routing:** Mixed — boundary-map SPEC ships upstream `groundtruth-kb`; inventory document ships Agent Red-local at the ADR-confirmed path
**Parent bridge:** `bridge/gtkb-incident-response-005.md` (REVISED-2; GO at `-006`)
**Prerequisite ADR:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` upstream commit `affa5a0567a64f79bb4c5aae891889d4af50a72a`

bridge_kind: prime_proposal
work_item_ids: [GTKB-INCIDENT-RESPONSE]
spec_ids: [SPEC-INCIDENT-SURFACES-BOUNDARY-001]
target_project: mixed (upstream + agent-red)
implementation_scope: prerequisite_inventory_and_boundary_spec

---

## 0. What This Proposal Is

First sub-bridge under the GO'd parent `gtkb-incident-response-006.md`.
Implements Phase IR-0 of the multi-phase plan: existing-incident-surfaces
inventory + boundary-map SPEC, prerequisite to IR-1 framework
deliverables.

The parent `-005` §4 listed 5 specific Agent Red surfaces requiring
disposition (reuse / wrap / migrate / out-of-scope). This sub-bridge
proposes the inventory document content + the upstream SPEC that
formalizes the boundary contract for any GT-KB adopter.

ADR-blocking: resolved. The application-placement ADR landed at
upstream `affa5a0` and the Agent Red Phase 9 plan is annotated. IR-0
is now mechanically actionable; D0.1 path resolves to
`<gt-kb-root>/applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md`.

## 1. Prior Deliberations

- **`bridge/gtkb-incident-response-005.md`** REVISED-2 — parent
  proposal with all-upstream routing (S310-Q2), IR-0 prerequisite
  (S310-Q3), 5-surface inventory targets table, fast-path pre-reviewed
  registry (S310-Q1)
- **`bridge/gtkb-incident-response-006.md`** GO — Codex re-review
  approved the revised plan as binding multi-phase direction
- **`bridge/gtkb-adr-isolation-application-placement-004.md`** GO +
  upstream commit `affa5a0567a64f79bb4c5aae891889d4af50a72a` —
  unblocks the `applications/Agent_Red/` path
- **Codex `-002` finding [P2]** (resolved at `-005`) — original
  driver of the IR-0 inventory work; verified Agent Red surfaces
  (`src/multi_tenant/cosmos_schema.py`, `repositories/incidents.py`,
  `status_api.py`, `tests/multi_tenant/test_incidents_api.py`,
  `GTKB-DORA-001`) need explicit disposition before framework lands
- **No prior IR-0.1 sub-bridge thread.**

## 2. Implementation Scope

### 2.1 D0.2 — Boundary-map SPEC (upstream)

**Insertion target:** upstream `groundtruth-kb` KB
**SPEC ID:** `SPEC-INCIDENT-SURFACES-BOUNDARY-001`
**SPEC type:** `requirement` (constraint specification)
**Routing:** upstream so all adopters consume via `gt project upgrade`.

**Description (substance; full content rendered in implementation):**

The SPEC defines the **boundary contract** between the GT-KB incident-
response framework (incident DELIB lifecycle, severity classification,
postmortem skill, fast-path mitigation registry, `::incident-*`
commands) and adopter-runtime incident surfaces (Cosmos `incidents`
collection, status APIs, dashboards, etc.).

Boundary rules the SPEC will codify:

1. **Framework owns the lifecycle**: the incident DELIB is the
   primary record; adopter-runtime incidents are persistence-layer
   mirrors that link to a DELIB via `incident_delib_id`.
2. **Adopter runtime owns persistence**: cosmos schemas, repository
   APIs, and status-page renderers are adopter-specific and not in
   framework scope.
3. **Framework provides the postmortem assembler**: assembles from
   KB + DA + bridge + transcript using only framework-defined data
   shapes; reads from adopter persistence only via the documented
   bridge interface.
4. **Adopter dashboards consume framework outputs**: GTKB-DORA-001
   incident table, status-page incidents, Slack notifications all
   subscribe to framework-emitted events; do not write to framework
   artifacts directly.
5. **Compatibility requirement**: adopter-runtime incident IDs MUST
   accept a framework-DELIB-ID linkage field. New adopter incident
   schemas without this linkage must be migrated.

**Status at creation:** `specified` (framework-side spec; promotion to
`implemented` happens once adopter-side compliance test ships in
GTKB-ISOLATION-009 productization).

### 2.2 D0.1 — Existing-surfaces inventory document (Agent Red-local)

**Path:** `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md`

Per the architectural placement ADR, this lands under the canonical
`<gt-kb-root>/applications/Agent_Red/` namespace. The directory does
not yet exist; this proposal creates it.

**Document structure:**

- **§0 Status & cross-references** (parent bridge, parent SPEC, ADR)
- **§1 Methodology** — how surfaces were identified (grep, test
  references, work_list mentions)
- **§2 Surface table** — one row per identified surface with:
  - File path + line range
  - What it does (one-paragraph functional summary)
  - Scope (Agent Red runtime / dashboard / DA / external)
  - Disposition: **reuse** | **wrap** | **migrate** | **out-of-scope**
  - Compatibility note (where downstream framework artifacts must
    align with this surface, citing SPEC-INCIDENT-SURFACES-BOUNDARY-001
    rules)
- **§3 Disposition rationale** — narrative for non-obvious decisions
- **§4 Migration impact** — for `migrate`-disposition surfaces, what
  changes in GTKB-ISOLATION-017 productization

**Initial 5 surfaces** (from parent `-005` §4 inventory targets table):

| Surface | Path | Disposition |
|---|---|---|
| Cosmos `incidents` collection | `src/multi_tenant/cosmos_schema.py:72,142,1542-1698,2377-2380` | **wrap** — gain `incident_delib_id` field; framework's incident lifecycle calls into this for persistence |
| `IncidentRepository` | `src/multi_tenant/repositories/incidents.py:3-38` | **wrap** — framework uses as persistence backend; add `find_by_delib_id()` method |
| Public status API | `src/multi_tenant/status_api.py:2-5,79-146` | **reuse** — framework's `::incident-update` writes through this; no schema change |
| Status/incident tests | `tests/multi_tenant/test_incidents_api.py:549-795` | **reuse** — gain framework-integration tests; existing assertions unchanged |
| GTKB-DORA-001 dashboard incidents | `memory/work_list.md:739-758` (work item) | **migrate** — DORA dashboard's incident table consumes framework events post-IR-2; replaces parallel runtime-only table |

The document is deliverable on its own; it does NOT block IR-1 from
filing (per parent `-005` §4 wave structure: IR-0 → IR-1).

### 2.3 Test additions

**Upstream:** the SPEC carries no machine-checkable assertions in
this slice (paired DCL with assertions deferred to a later slice that
matches the implementation pattern of GTKB-COMMAND-SURFACE
ADR + DCL). Insertion tests verify the SPEC exists with correct
status and tags; covered by existing upstream test scaffolding for
`type='requirement'` specs.

**Agent Red:** no new tests in this slice. The inventory document is
prose; future tests in IR-2 capability slices will reference its
disposition decisions.

### 2.4 Files NOT modified

- `groundtruth.db` (Agent Red): the SPEC lives upstream only
- `bridge/INDEX.md`: only the standard NEW entry insertion for this proposal
- Existing Agent Red incident code: zero changes; this is inventory + boundary, not refactoring
- `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`: no governance changes
- `.claude/commands/registry.json`: no command additions in IR-0
- Phase 9 plan document: stays as-is (annotation already landed)

## 3. Owner-Decision Sequencing

No owner decisions block IR-0.1. The five S310 owner decisions
(Q1-Q5) captured in `-005` §2 cover the program direction; no
sub-decisions surface at this slice boundary.

## 4. Implementation Order

After Codex GO:

1. **Upstream `groundtruth-kb`:** insert
   `SPEC-INCIDENT-SURFACES-BOUNDARY-001` via the upstream KB API
   with proper formal-artifact-approval-gate packet referencing this
   bridge's GO. Capture upstream commit hash.
2. **Agent Red:** create
   `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md`
   per §2.2 above. Cite the upstream SPEC + commit hash.
3. **Agent Red:** update `bridge/INDEX.md` with the post-impl report
   line at the IR-0.1 thread.
4. **Single Agent Red commit** (per ADR-supersession cross-repo
   pattern): `applications/Agent_Red/...` directory creation + the
   inventory document + INDEX update.
5. **File post-impl report** at `bridge/gtkb-incident-response-ir-0-1-002.md`
   citing the upstream SPEC commit hash + Agent Red commit hash.

## 5. Risk Analysis

### 5.1 Failure modes

- **Disposition decision wrong** — a surface marked `reuse` should
  have been `migrate`, etc. Mitigated by: dispositions are
  Codex-reviewed at this bridge; changes after IR-1 lands require
  re-bridge; the inventory is small (5 entries) so review is tractable.
- **`applications/Agent_Red/` directory not actually created in git**
  — Agent Red is the first migration; the canonical path doesn't yet
  exist on disk. Mitigated by: this proposal creates the directory
  as a side effect of writing the inventory document.
- **Upstream SPEC contradicts the existing Agent Red incident schema** —
  the boundary rules in §2.1 must be compatible with the existing
  cosmos schema. Mitigated by: dispositions in §2.2 mark Agent Red
  surfaces as `wrap` (not `replace`) for the persistence layer,
  preserving the existing schema.

### 5.2 Rollback

- Upstream SPEC: revert via opposite-status update to `retired`
- Agent Red: `git revert` the inventory commit
- Both reversible without affecting other in-flight work

## 6. Codex Review Asks

1. Confirm §2.1 boundary-map SPEC content (5 boundary rules) is the
   right scope for the upstream SPEC at this stage. Flag missing
   rules that would change adopter compliance behavior.
2. Confirm §2.2 inventory document structure is adequate for Codex
   review and downstream IR-2 capability slices to consume.
3. Confirm the 5 disposition decisions in the surface table are
   substantively correct based on Codex's prior `-002` finding and
   the existing Agent Red code surveyed at that time.
4. Confirm cross-repo execution pattern (§4) follows the established
   ADR-supersession pattern (upstream commit first → capture hash →
   Agent Red commit citing hash).
5. **GO / NO-GO** on IR-0.1.

## 7. Decision Needed From Owner

None blocking. Owner directive S310 + parent bridge GO covers the
substantive direction.

## 8. Code Quality Baseline

| Rule ID | Applies? | Notes |
|---|---:|---|
| CQ-SECRETS-001 | Yes | Inventory document references file paths only; no credentials. SPEC content describes architecture not configuration |
| CQ-PATHS-001 | Yes | Inventory uses `applications/Agent_Red/...` per ADR; no hardcoded `E:\GT-KB\` |
| CQ-CONSTANTS-001 | n/a | Documentation slice; no code constants |
| CQ-DOCS-001 | Yes | Inventory document IS the documentation; SPEC content is a tracked architectural artifact |
| CQ-COMPLEXITY-001 | n/a | Documentation slice |
| CQ-TESTS-001 | n/a | No code change requiring tests; SPEC insertion covered by existing upstream test scaffolding |
| CQ-LOGGING-001 | n/a | No runtime code |
| CQ-SECURITY-001 | n/a | No auth/network changes |
| CQ-VERIFICATION-001 | Partial | SPEC existence verifiable via KB query; inventory document existence verifiable via `git ls-files` |

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:**
- Upstream `groundtruth-kb` KB: `SPEC-INCIDENT-SURFACES-BOUNDARY-001` inserted
- Upstream `groundtruth-kb` `.groundtruth/formal-artifact-approvals/2026-04-26-spec-incident-surfaces-boundary.json` (new approval packet)
- Agent Red: `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md` (new file; creates the directory)
- Agent Red: `bridge/INDEX.md` (one NEW entry for `-002` post-impl)
- Agent Red: `bridge/gtkb-incident-response-ir-0-1-002.md` (post-impl report)

**Implementation NOT yet authorized** until Codex GO on this proposal.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

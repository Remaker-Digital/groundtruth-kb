NEW

# Implementation Proposal - GTKB-SYSTEMS-TERMINOLOGY-MAP-001: Canonical Artifact and Interface Map

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Scoping and implementation proposal
**Risk tier:** Medium (startup terminology, doctor checks, and dashboard/startup surfaces; no production runtime impact)
**Backlog item:** `GTKB-SYSTEMS-TERMINOLOGY-MAP-001 - Canonical artifact/interface names and startup operating surface map`

---

## Background

`GTKB-SYSTEMS-TERMINOLOGY-MAP-001` is the second current top-priority standing
backlog item for this Prime Builder session. `GTKB-ENV-INVENTORY-001` has
already been filed as `bridge/gtkb-env-inventory-001-001.md` and is waiting for
Loyal Opposition review; this proposal keeps Prime Builder moving on the next
proposal-only action without implementing unreviewed work.

The recurring defect this item addresses is that GT-KB agents can correctly
know individual glossary terms and still misunderstand which concrete project
artifact or interface the owner means. "Backlog" is the first named
reconciliation case: current artifacts refer to `memory/work_list.md`, future
DB-backed `backlog_items`, MemBase work items, bridge queue state, and
dashboard/startup summaries in adjacent ways that can look interchangeable to
an agent. The same class of ambiguity exists for glossary, memory, MemBase,
Deliberation Archive, dashboard, bridge, skills, hooks, plugins, role records,
scratch pads, release-readiness surfaces, doctor checks, and release gates.

This proposal creates an implementation path for a canonical artifact/interface
map. It does not mutate formal GOV, SPEC, PB, ADR, or DCL records. If later
implementation discovers that formal specification changes are required, those
will need separate owner-visible approval under the formal artifact rules.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| Standing backlog row names the next step | `memory/work_list.md` lines 986-1023 | Requires filing this bridge proposal for glossary extensions, startup surface, doctor checks, and integration sequence |
| Startup menu elevated this item | `docs/gtkb-dashboard/session-startup-report.md` option 2 | Lists this as one of the current top-priority actions |
| Operating model defines current canonical terms | `.claude/rules/operating-model.md` section 2 | Provides canonical meanings for application, project, backlog, MemBase, dashboard, etc. |
| Canonical terminology primer defines inherited glossary | `.claude/rules/canonical-terminology.md` and `.claude/rules/canonical-terminology.toml` | Current doctor-enforced glossary surface; lacks artifact/interface lookup metadata |
| Existing terminology table is informational only | `docs/operating-model-terminology-table-2026-04-30.md` | Useful input, but explicitly not authoritative |
| Startup-refactor advisory identified missing capability manifest | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md` finding F8 | Adjacent need for role-capability and system/tool inventory |
| Control map is stale and incomplete | `config/agent-control/CONTROL-MAP.md` | Lists major control surfaces but omits current glossary, role assignment, file bridge protocol, and generated startup surfaces |

## Specification Links

Cross-cutting specs required for bridge proposals:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) - `bridge/INDEX.md` is the live
  authority for this proposal. Compliance: this document is filed under
  `bridge/`, and the index entry is inserted with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) -
  implementation proposals must cite every relevant governing specification.
  Compliance: this section lists the bridge, backlog, operating-model,
  terminology, startup, dashboard, and artifact-governance surfaces that
  constrain the proposed work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) - any later
  implementation report must carry forward these links and map executed tests
  to the linked requirements. Compliance: this proposal includes a
  specification-derived test plan.

Backlog and work authority:

- `GOV-STANDING-BACKLOG-001` v2 (verified) - standing backlog is the durable
  cross-session work authority. Compliance: this proposal follows the backlog
  row's explicit next step.
- `PB-STANDING-BACKLOG-CONTINUITY-001` (verified) - Prime Builder must not
  bypass standing backlog continuity. Compliance: this proposal preserves the
  selected top-priority item and distinguishes it from adjacent startup and
  environment-inventory work.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (verified) - standing backlog
  items are work authority. Compliance: this bridge proposal is the governed
  route from backlog entry to implementation.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (specified) and
  `DCL-STANDING-BACKLOG-DB-SCHEMA-001` (specified) - define the target
  DB-backed backlog authority and schema direction. Compliance: this proposal's
  first reconciliation case explicitly distinguishes current
  `memory/work_list.md` authority from the target `backlog_items` model and
  does not pretend the transition is complete.

Artifact-oriented governance:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) - concrete decisions,
  procedures, and durable system knowledge should be preserved as artifacts.
  Compliance: the proposed map becomes durable lookup evidence rather than
  transient chat explanation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) - development memory is a
  traceable artifact graph. Compliance: each map row links term, artifact,
  authority, mutation route, startup visibility, and verification method.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) - artifacts need explicit
  lifecycle states. Compliance: the map distinguishes authoritative, generated,
  local-only, retired, transitional, target, and non-authoritative surfaces.

Startup and dashboard specs:

- `GOV-SESSION-SELF-INITIALIZATION-001` (verified) - fresh sessions
  self-initialize from live role, governance, bridge, dashboard, priorities, and
  token context. Compliance: startup output should use the new compact map
  status and resolve common owner terms to live artifacts.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (verified) - startup must not
  treat governance context as implicit. Compliance: the proposed startup
  "GT-KB Systems and Tools" section makes routine surfaces explicit without
  loading every detailed artifact.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (verified) - startup should report and
  reduce token load. Compliance: the map is index-first and compact; detailed
  artifacts load only when needed.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` (verified) - startup displays the live
  dashboard link and KPI context. Compliance: the dashboard should expose a
  compact map status and link, not duplicate the full map in startup text.

Operating-model and terminology rules:

- `.claude/rules/operating-model.md` - canonical operating-model artifact with
  rule-cited soft authority.
- `.claude/rules/canonical-terminology.md` - current canonical glossary primer.
- `.claude/rules/canonical-terminology.toml` - doctor configuration for
  required glossary terms.
- `.claude/rules/deliberation-protocol.md` - requires deliberation search
  before proposal filing. Compliance: searches are recorded in Prior
  Deliberations.
- `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/codex-review-gate.md` - govern bridge submission, review, and
  no-implementation-before-`GO`.

Root and application boundary:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (specified) - application/root
  placement work must honor the GT-KB root and `applications/` boundary.
  Compliance: this proposal maps Agent Red/application terminology as
  boundary context only and keeps active GT-KB artifacts under `E:\GT-KB`.
- `.claude/rules/project-root-boundary.md` - active files for GT-KB remain
  inside `E:\GT-KB`; application files remain under `E:\GT-KB\applications\`.

Advisory and source artifacts:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md`
  - adjacent startup/capability-manifest advisory.
- `docs/operating-model-terminology-table-2026-04-30.md` - informational
  terminology reconciliation input.
- `memory/work_list.md` row 34 and section `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`
  - current standing-backlog evidence.

The proposed tests derive from these linked specs as follows: bridge authority
drives index/file checks; spec-linkage drives preflight and section checks;
standing-backlog specs drive checks that this item remains visible as a
top-priority action until implemented; artifact-governance specs drive the map
schema and lifecycle/status fields; startup/dashboard specs drive compact
startup and dashboard status tests; root-boundary specs drive path containment.

## Prior Deliberations

Searches performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "GTKB-SYSTEMS-TERMINOLOGY-MAP canonical artifact interface names startup operating surface map backlog terminology" --limit 10
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "backlog memory/work_list.md MemBase backlog_items authority terminology contradiction" --limit 10
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "startup refactor glossary tools systems skills hooks plugins role records canonical terminology" --limit 10
```

Relevant results:

| DELIB | Relevance |
|---|---|
| `DELIB-0722` | Verified prior canonical-terminology surface implementation thread |
| `DELIB-1016` | Loyal Opposition verification of GT-KB IDP terminology formalization |
| `DELIB-1017` | Loyal Opposition `GO` on GT-KB IDP terminology formalization revision 2 |
| `DELIB-1018` | Prior `NO-GO` on terminology formalization revision 1; useful caution against incomplete terminology scope |
| `DELIB-S324-OM-DELTA-0004-CHOICE` | Owner choice on backlog ordering semantics |
| `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` | Owner directive to formalize standing backlog as DB-backed source of truth |
| `DELIB-0838` | Owner decision establishing the standing backlog as governed cross-session work authority |
| `DELIB-0839` | Standing backlog harvest and reconciliation obligations |
| `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` | Related role-definition assessment |

No prior deliberation found in these searches rejects creating a canonical
artifact/interface map. Prior terminology work shows the glossary has already
been useful but is insufficient for resolving concrete artifact/interface
references.

## Goal

Create a canonical, compact map from common GT-KB system terms and owner-facing
phrases to the concrete artifacts, tables, files, command surfaces, and
mutation routes they name.

The desired end state:

1. A durable artifact/interface map exists in a machine-readable form.
2. A human-readable generated view exists for owner and agent inspection.
3. The map distinguishes concepts from concrete artifacts and authoritative
   sources from generated summaries.
4. Startup can surface a compact "GT-KB Systems and Tools" section without
   loading large artifacts.
5. Doctor/startup tests prove common owner terms resolve to expected surfaces.
6. The first reconciliation case, "backlog", states the present transitional
   authority and target authority explicitly.

## Proposed Implementation Scope

### Slice 1 - Canonical map artifact and schema

Add a machine-readable map, proposed path:

- `config/agent-control/system-interface-map.toml`

Add a generated or hand-maintained human-readable companion:

- `docs/gtkb-systems-and-tools.md`

Each map entry should include:

- `canonical_name`,
- `accepted_aliases`,
- `discouraged_aliases`,
- `forbidden_aliases`,
- `concept_vs_artifact`,
- `authoritative_source`,
- `generated_or_authoritative`,
- `read_method`,
- `mutation_method`,
- `role_permissions`,
- `startup_visibility`,
- `dashboard_visibility`,
- `harness_caveats`,
- `verification_method`,
- `lifecycle_state`,
- `related_specs`,
- `related_deliberations`.

### Slice 2 - Seed entries for routine owner terms

Seed at least these entries:

- backlog,
- work item,
- MemBase,
- Deliberation Archive,
- MEMORY.md,
- canonical glossary,
- operating model,
- file bridge,
- bridge queue,
- smart poller,
- retired OS poller,
- dashboard,
- release readiness,
- release gate,
- doctor check,
- startup disclosure,
- session focus,
- work subject,
- role assignment record,
- harness identity record,
- skill,
- hook,
- plugin/app capability,
- MCP server,
- resource alias registry.

### Slice 3 - Backlog reconciliation case

The first reconciliation row must explicitly state:

- current human-readable operational surface: `memory/work_list.md`,
- current MemBase target authority: `backlog_items` per
  `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` and
  `DCL-STANDING-BACKLOG-DB-SCHEMA-001`,
- MemBase `work_items` are not the same as standing backlog `backlog_items`,
- `bridge/INDEX.md` is bridge queue state, not the standing backlog,
- dashboard/startup rows are summaries, not authority,
- current transitional truth must be read from the live governing artifact named
  by the map, not from cached startup/dashboard text.

### Slice 4 - Startup and dashboard integration

Add compact startup/dashboard status:

- map present/missing,
- map version or content hash,
- generated human-readable companion path,
- count of mapped systems,
- first reconciliation case status,
- warning if stale generated summaries conflict with the authoritative source.

Prime Builder startup should show this compact status only; detailed map rows
should load when the selected task needs them.

### Slice 5 - Doctor and tests

Add tests/doctor checks that:

- parse the TOML map,
- require the seed entries above,
- ensure required fields are non-empty,
- verify authoritative paths/tables exist where applicable,
- flag aliases that point to multiple incompatible artifacts,
- prove common owner terms resolve to the expected map entries,
- verify startup/dashboard compact status uses the map rather than a copied
  hard-coded list.

Suggested files:

- `tests/scripts/test_system_interface_map.py`
- `tests/scripts/test_session_self_initialization.py`
- `tests/scripts/test_groundtruth_governance_adoption.py`
- doctor integration in the appropriate GT-KB project doctor module or release
  gate if this becomes release-blocking.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Expected result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `rg -n "Document: gtkb-systems-terminology-map-001|NEW: bridge/gtkb-systems-terminology-map-001-001.md" bridge/INDEX.md` | Proposal entry is present and latest `NEW` |
| T-spec-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-systems-terminology-map-001` | Preflight reports `missing_required_specs: []` |
| T-spec-2 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this spec list plus spec-to-test mapping and executed commands | Loyal Opposition can verify from test evidence |
| T-backlog-1 | `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` | `python -m pytest tests/scripts/test_system_interface_map.py -q --tb=short` | Backlog row distinguishes `memory/work_list.md`, `backlog_items`, `work_items`, `bridge/INDEX.md`, and dashboard summaries |
| T-artifact-1 | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `python -m pytest tests/scripts/test_system_interface_map.py -q --tb=short` | Map schema preserves authority, lifecycle, read/mutation, and verification fields |
| T-startup-1 | `GOV-SESSION-SELF-INITIALIZATION-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short` | Startup exposes compact map status without loading every map row |
| T-dashboard-1 | `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | `python -m pytest tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short` or focused equivalent | Dashboard data exposes map status/link without becoming authority |
| T-quality-1 | Code quality | `python -m ruff check .` | No lint regressions in touched scope |
| T-quality-2 | Formatting | `python -m ruff format --check .` | Formatting clean in touched scope |

## Acceptance Criteria

Proposal acceptance:

- [ ] Loyal Opposition `GO` on this proposal.
- [ ] Applicability preflight reports no missing required specs.
- [ ] Scope is confirmed as map/startup/doctor work only, not formal GOV/SPEC
  mutation.

Implementation acceptance after `GO`:

- [ ] `config/agent-control/system-interface-map.toml` or accepted equivalent
  exists and parses deterministically.
- [ ] Human-readable companion exists.
- [ ] Seed entries cover the routine systems listed in this proposal.
- [ ] Backlog reconciliation case resolves the current transitional authority
  and target authority without conflating `memory/work_list.md`,
  `backlog_items`, `work_items`, `bridge/INDEX.md`, or dashboard/startup
  summaries.
- [ ] Startup/dashboard exposes compact map status.
- [ ] Tests/doctor checks parse the map and prove common owner terms resolve to
  expected artifacts/interfaces.
- [ ] Post-implementation report includes exact commands and observed results.

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| The map becomes a competing authority instead of an index | Medium | High | Each row must point to an authoritative source; generated summaries are labeled non-authoritative |
| Startup grows too large | Medium | Medium | Startup exposes compact status only; full map loads on demand |
| Backlog reconciliation conflicts with ongoing DB-backed backlog work | Medium | Medium | Map states current transitional authority and target authority; does not implement DB migration |
| Terminology changes require owner approval | Medium | Medium | This proposal avoids formal spec mutation; any GOV/SPEC/PB/ADR/DCL update gets a separate owner-visible approval path |
| Existing docs contain stale aliases | High | Low | Doctor/checks can start as warning-level and graduate to blocking after cleanup |

Rollback:

- Revert map artifact, generated companion, tests, and startup/dashboard status
  integration commit.
- Keep this bridge thread as audit history; do not delete bridge files.

## Out of Scope

- Formal mutation of GOV, SPEC, PB, ADR, or DCL records.
- Full DB-backed backlog migration.
- Implementation of `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`.
- Implementation of `GTKB-STARTUP-REFRACTOR-001`.
- Implementation of `GTKB-ENV-INVENTORY-001`.
- Cleanup or deletion of stale local settings or archived files.
- External resource URL/identity registry implementation; that is tracked by
  `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001`.
- Production deployment, package publish, or GitHub release.

## Project Root Boundary Compliance

All proposed active files remain inside `E:\GT-KB`.

Proposed tracked files:

- `config/agent-control/system-interface-map.toml`
- `docs/gtkb-systems-and-tools.md`
- `tests/scripts/test_system_interface_map.py`
- focused updates to startup/dashboard generation and tests as needed

No live dependency is created outside the project root. Agent Red and other
application references are treated as terminology/boundary examples only, not
as live GT-KB artifacts outside `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision is required for this proposal.

Existing owner direction/evidence:

- `memory/work_list.md` row 34 records
  `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` as owner-directed on 2026-05-03 with
  backlog addition approved.
- Current session focus selected option 2, `Top Priority Actions`, whose prompt
  details list this item as a current priority after `GTKB-ENV-INVENTORY-001`.

Future owner input may be required if implementation needs to approve revised
canonical wording for an existing formal term, or if the map reveals a conflict
that cannot be resolved from existing authoritative artifacts.

## Provenance

| Source | Reference |
|---|---|
| Standing backlog | `memory/work_list.md` row 34 and section `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` |
| Startup focus | `docs/gtkb-dashboard/session-startup-report.md` option 2 |
| Operating model | `.claude/rules/operating-model.md` |
| Current glossary | `.claude/rules/canonical-terminology.md` and `.claude/rules/canonical-terminology.toml` |
| Startup refactor advisory | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md` |
| Prior terminology table | `docs/operating-model-terminology-table-2026-04-30.md` |
| Deliberations | `DELIB-0722`, `DELIB-1016`, `DELIB-1017`, `DELIB-1018`, `DELIB-S324-OM-DELTA-0004-CHOICE`, `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-0838`, `DELIB-0839` |

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

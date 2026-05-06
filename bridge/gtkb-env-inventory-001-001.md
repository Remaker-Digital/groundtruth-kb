NEW

# Implementation Proposal - GTKB-ENV-INVENTORY-001: Harness and Development Environment Inventory

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Scoping and implementation proposal
**Risk tier:** Medium (release-gate, startup/dashboard visibility, and local redaction behavior; no production runtime impact)
**Backlog item:** `GTKB-ENV-INVENTORY-001 - Harness and development environment inventory`

---

## Background

`GTKB-ENV-INVENTORY-001` is the current top standing-backlog priority selected
for this Prime Builder session. The backlog records it as owner-directed on
2026-05-03, with the next step to file this bridge proposal.

The work exists because GT-KB release confidence and role portability depend on
environment facts that are partly outside the installable package: host OS,
shell/runtime/tool versions, Codex and Claude Code behavior, hooks, skills,
plugins, MCP servers, command surfaces, role records, and local settings. The
current project has enough evidence to say these surfaces matter, but no single
canonical inventory artifact or release gate proves that the inventory is
present, current, and safe to publish.

This proposal is intentionally conservative. It proposes inventory collection,
redaction, public/private output separation, and release-readiness enforcement.
It does not propose cleanup of local settings, credential rotation, role
reassignment, MCP reconfiguration, or normalization of developer workstations.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| Standing backlog row names the next step | `memory/work_list.md` lines 955-984 | Requires filing `bridge/gtkb-env-inventory-001-001.md` with schema, redaction, startup/dashboard exposure, and release-gate integration |
| Advisory report defines scope and acceptance criteria | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-DEV-ENVIRONMENT-INVENTORY-ADVISORY-2026-05-03-11-53.md` | Provides findings F1-F5, proposed backlog item, acceptance criteria, and suggested verification |
| Startup menu elevated this work | `docs/gtkb-dashboard/session-startup-report.md` option 2 | Generated startup selected this item as the first top-priority action |
| MemBase confirms governing specs exist | `groundtruth.db` query 2026-05-05 | Confirms bridge, standing backlog, and artifact-oriented governance specs are present; release platform inventory specs remain candidate/missing |
| Deliberation search found harness role context | `python -m groundtruth_kb deliberations search "harness role configuration Prime Builder Loyal Opposition Claude Code Codex capability compatibility matrix" --limit 10` | Found `DELIB-0831`, `DELIB-0832`, `DELIB-0833`, and related role/harness evidence |
| Deliberation search found release inventory context | `python -m groundtruth_kb deliberations search "release platform inventory two stage approval development environment baseline package" --limit 10` | Found `DELIB-S323-GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-APPROVAL` and candidate-spec context |

## Specification Links

Cross-cutting specs required for bridge proposals:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) - `bridge/INDEX.md` is the live
  authority for this proposal. Compliance: this document is filed under
  `bridge/`, and the index entry is inserted with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) -
  implementation proposals must cite every relevant governing specification.
  Compliance: this section lists the bridge, backlog, artifact-governance,
  root-boundary, release, and startup surfaces that constrain the proposed
  work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) - any later
  implementation report must carry forward these links and map executed tests
  to the linked requirements. Compliance: this proposal includes a
  specification-derived test plan.

Standing-backlog authority:

- `GOV-STANDING-BACKLOG-001` v2 (verified) - standing backlog is the durable
  cross-session work authority. Compliance: this proposal is filed because the
  standing backlog records `GTKB-ENV-INVENTORY-001` as an owner-directed
  top-priority item with this exact next step.
- `PB-STANDING-BACKLOG-CONTINUITY-001` (verified) - Prime Builder must not
  bypass standing backlog continuity. Compliance: this proposal preserves the
  backlog row's scope and does not silently substitute a different work item.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (verified) - backlog items are
  selectable work authority. Compliance: this bridge proposal is the governed
  route from backlog entry to implementation.

Artifact-oriented governance:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) - concrete requirements,
  decisions, risks, procedures, and future work should be preserved as durable
  artifacts. Compliance: the proposed inventory becomes a durable release
  evidence artifact rather than a transient shell transcript.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) - project memory is a
  traceable artifact graph. Compliance: the generated inventory will link
  source surfaces, redaction status, and release-gate evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) - artifacts require clear
  lifecycle states. Compliance: inventory entries will distinguish configured,
  verified, unsupported, unknown, redacted, stale, and public-safe states.

Role, startup, and bridge rules:

- `.claude/rules/file-bridge-protocol.md` - governs proposal filing,
  `GO`/`NO-GO`, implementation reports, and verification.
- `.claude/rules/codex-review-gate.md` - forbids implementation changes before
  Loyal Opposition `GO` when the bridge is active.
- `.claude/rules/deliberation-protocol.md` - requires deliberation search
  before proposal filing. Compliance: searches are recorded in Prior
  Deliberations.
- `.claude/rules/canonical-terminology.md` - defines GT-KB, Prime Builder,
  Loyal Opposition, file bridge, MemBase, and related vocabulary used by the
  inventory.
- `.claude/rules/operating-model.md` - defines application/project/platform,
  work item, backlog, and dashboard terminology; constrains how the inventory
  describes platform versus adopter surfaces.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) - application/root
  placement work must honor the GT-KB root and `applications/` boundary.
  Compliance: this proposal keeps GT-KB platform inventory artifacts at the
  project root or under `docs/`, and treats Agent Red/application references as
  boundary context only.
- `.claude/rules/project-root-boundary.md` - all active GT-KB files must remain
  under `E:\GT-KB`; GT-KB application files must remain under
  `E:\GT-KB\applications\`. Compliance: all proposed files remain inside the
  GT-KB root.

Release and inventory context:

- `DELIB-S323-GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-APPROVAL` - owner
  approved a candidate release-platform inventory statement via
  AskUserQuestion. Compliance: this proposal uses that as release-context
  evidence only; `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001` is not yet a
  canonical MemBase spec and is not treated as a live governing spec.
- `memory/work_list.md` row 21 (`GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS`) -
  records that the release platform inventory candidate spec still needs its
  own follow-on implementation bridge. Compliance: this proposal does not
  insert or promote that GOV; it only makes the dev-environment inventory
  visible and enforceable.

Advisory and source artifacts:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-DEV-ENVIRONMENT-INVENTORY-ADVISORY-2026-05-03-11-53.md`
  - source advisory for this backlog item.
- `memory/work_list.md` row 33 and section `GTKB-ENV-INVENTORY-001` - current
  human-readable standing-backlog evidence.
- `docs/gtkb-dashboard/session-startup-report.md` - current startup evidence
  that this item is the selected top-priority action.

The proposed tests derive from these linked specs as follows: bridge authority
drives index/file checks; spec-linkage drives preflight and section checks;
verified-spec testing drives the implementation report's spec-to-test mapping;
standing-backlog specs drive tests that the startup/dashboard top-priority
surface exposes the item; artifact-governance specs drive generated artifact,
state, redaction, and staleness tests; root-boundary rules drive path
containment assertions.

## Prior Deliberations

Searches performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "GTKB-ENV-INVENTORY-001 harness development environment inventory baseline release package Claude Code Codex" --limit 10
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "harness role configuration Prime Builder Loyal Opposition Claude Code Codex capability compatibility matrix" --limit 10
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "release platform inventory two stage approval development environment baseline package" --limit 10
```

Relevant results:

| DELIB | Relevance |
|---|---|
| `DELIB-0831` | Owner decision that Prime Builder and Loyal Opposition are portable harness-assigned roles |
| `DELIB-0832` | Owner decision that GT-KB installs must configure Prime Builder and all capable harness role paths |
| `DELIB-0833` | Comparison of GT-KB harness role configuration for Prime Builder versus Loyal Opposition; identifies asymmetric install/config behavior |
| `DELIB-S323-GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-APPROVAL` | Owner approval of candidate release-platform inventory/two-stage validation statement |
| `DELIB-1404` | Candidate specification statements backlog advisory that includes release-platform inventory context |
| `DELIB-0878` and `DELIB-0879` | Isolation authority/topology planning relevant to platform/application boundary handling |
| `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` | Related current-day owner approval of Codex harness parity specs; adjacent but not a dependency of this proposal |

No prior deliberation found in these searches rejects creating a
harness/development-environment inventory. The relevant prior decisions support
role portability, harness capability visibility, and release inventory
traceability.

## Goal

Create a repeatable, redacted, release-visible harness and development
environment inventory workflow for GT-KB.

The desired end state:

1. A collection command inventories the host, runtime, harness, hook, skill,
   plugin, MCP, command, settings, and role-record surfaces that affect GT-KB
   development and verification.
2. The command emits a release-safe public baseline and a private/local
   redacted baseline.
3. The inventory includes a role-by-harness compatibility matrix for Prime
   Builder and Loyal Opposition on Codex and Claude Code.
4. Release-gate or package-preparation checks fail or warn loudly when the
   inventory is missing, stale, unredacted, or omitted from release evidence.
5. Startup/dashboard surfaces can point to the inventory state without loading
   local secrets or full generated files into session context.

## Proposed Implementation Scope

### Slice 1 - Inventory schema and collector

Add a deterministic collector script:

- `scripts/collect_dev_environment_inventory.py`

The collector should support:

- public JSON output,
- public Markdown output,
- local/private JSON output,
- strict redaction checks,
- deterministic sorting for stable diffs,
- explicit `unknown` values when a version or capability cannot be discovered,
- non-fatal collection for optional tools not installed or not exposed by the
  current harness.

Proposed generated outputs:

- `docs/release/dev-environment-inventory.json` - release-safe public baseline.
- `docs/release/dev-environment-inventory.md` - human-readable public baseline.
- `.gtkb-state/dev-environment-inventory/local.json` - private local baseline,
  ignored by git.

If `docs/release/` does not exist, create it as the release evidence home for
this artifact. The private `.gtkb-state/` output remains non-authoritative and
local-only.

### Slice 2 - Redaction and classification

Inventory entries should be classified as:

- `public_safe`,
- `local_only`,
- `redacted`,
- `sensitive`,
- `stale_or_archive_reference`,
- `unknown`,
- `unsupported`,
- `verified`.

The collector must never publish raw credential-like values, private local
paths that are not needed for release evidence, or local command literals that
look credential-bearing. Public output should record that such values exist
only as redacted classifications.

### Slice 3 - Role-by-harness compatibility matrix

Add inventory rows for:

- Prime Builder on Claude Code,
- Prime Builder on Codex,
- Loyal Opposition on Claude Code,
- Loyal Opposition on Codex.

Minimum capability dimensions:

- startup support,
- canonical terminology load,
- role-record resolution,
- file bridge read/write,
- formal artifact mutation gates,
- hook support,
- skill support,
- command support,
- subagent/team support,
- MCP support,
- browser automation,
- GitHub/PR/CI access,
- shell/runtime behavior,
- permission/approval model,
- credential-safety gates,
- release/package command support.

Each cell should be one of `verified`, `configured`, `runtime_provided`,
`unsupported`, `unknown`, or `not_applicable`, with a short evidence pointer.

### Slice 4 - Release-gate and dashboard/startup visibility

Integrate the inventory with release-readiness evidence:

- `scripts/release_candidate_gate.py` should fail or warn loudly in strict mode
  if the public inventory is missing, stale, malformed, or lacks required
  sections.
- Dashboard/startup data generation should expose a compact inventory status:
  present/missing, generated timestamp, collector version or hash, redaction
  pass/fail, and latest verification command.
- Startup should prefer compact status over loading the full inventory artifact
  into context.

### Slice 5 - Tests

Add focused tests for:

- collector output shape,
- deterministic sorting,
- required sections,
- redaction of sensitive values,
- public/private separation,
- role-by-harness matrix completeness,
- release-gate behavior for missing/stale/malformed inventory,
- startup/dashboard compact status.

Suggested test files:

- `tests/scripts/test_collect_dev_environment_inventory.py`
- `tests/scripts/test_release_candidate_gate.py`
- `tests/scripts/test_session_self_initialization.py` if startup output changes

## Proposed Inventory Sections

Public baseline:

1. Project identity and GT-KB package version.
2. Generated timestamp and collector version/hash.
3. Host OS family/version/build/architecture.
4. Shell and terminal environment.
5. Python, pip, pytest, ruff, and package manager versions.
6. Node.js, npm, Playwright/MCP command availability.
7. Git and GitHub CLI versions.
8. Harness identity and role assignment summary.
9. Claude Code baseline where discoverable.
10. Codex baseline where discoverable.
11. Repo-configured hooks, skills, commands, agents, and MCP servers.
12. Runtime-provided app/plugin/tool capabilities.
13. Role-by-harness compatibility matrix.
14. Redaction summary and local-only exclusions.
15. Verification commands and last observed result.

Private local baseline:

1. Same public fields, plus local path/source detail where safe.
2. Local settings classification.
3. Redacted sensitive-value presence flags.
4. Optional tool discovery failure detail.
5. Full evidence list for local debugging.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Expected result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `rg -n "Document: gtkb-env-inventory-001|NEW: bridge/gtkb-env-inventory-001-001.md" bridge/INDEX.md` | Proposal entry is present and latest `NEW` |
| T-spec-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-env-inventory-001` | Preflight reports `missing_required_specs: []` |
| T-spec-2 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this spec list plus spec-to-test mapping and executed commands | Loyal Opposition can verify from test evidence |
| T-backlog-1 | `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001` | `rg -n "GTKB-ENV-INVENTORY-001" memory/work_list.md docs/gtkb-dashboard/session-startup-report.md` | Backlog and startup/dashboard surfaces show this selected top-priority item |
| T-artifact-1 | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `python scripts/collect_dev_environment_inventory.py --public-json docs/release/dev-environment-inventory.json --public-markdown docs/release/dev-environment-inventory.md --local-json .gtkb-state/dev-environment-inventory/local.json` | Public and private inventory artifacts are generated deterministically |
| T-redaction-1 | `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `python -m pytest tests/scripts/test_collect_dev_environment_inventory.py -q --tb=short` | Sensitive/local-only fixtures are redacted from public output and classified in private output |
| T-release-1 | Release-readiness integration | `python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short` | Release gate detects missing/stale/malformed inventory and passes current generated inventory |
| T-startup-1 | Dashboard/startup visibility | `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short` | Startup/dashboard exposes compact inventory status without loading private details |
| T-quality-1 | Code quality | `python -m ruff check .` | No lint regressions in touched scope |
| T-quality-2 | Formatting | `python -m ruff format --check .` | Formatting clean in touched scope |

## Acceptance Criteria

Proposal acceptance:

- [ ] Loyal Opposition `GO` on this proposal.
- [ ] Applicability preflight reports no missing required specs.
- [ ] Scope is confirmed as inventory/reporting/release-readiness only, not
  cleanup or role reassignment.

Implementation acceptance after `GO`:

- [ ] Collector script exists and can generate public JSON, public Markdown,
  and local private JSON.
- [ ] Public output excludes raw secrets, credential-like values, and unsafe
  local-only command literals.
- [ ] Inventory covers host, runtime, toolchain, hooks, skills, commands, MCP,
  plugins/apps, role records, and role-by-harness compatibility.
- [ ] Release-gate strict mode fails or warns loudly for missing/stale/malformed
  inventory.
- [ ] Startup/dashboard exposes compact inventory status.
- [ ] Tests cover collector shape, redaction, public/private split, release
  gate, and startup/dashboard status.
- [ ] Post-implementation report includes exact commands and observed results.

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Public inventory leaks local secrets or overly specific workstation detail | Medium | High | Redaction-by-default, fixture tests for sensitive patterns, private/public output split |
| Collector becomes brittle across harnesses or unavailable tools | Medium | Medium | Optional tools return `unknown` or `unsupported`; required public schema remains stable |
| Release gate blocks packaging because inventory cannot collect an optional tool | Medium | Medium | Gate required sections, redaction, and freshness; optional capability verification can be non-blocking unless explicitly marked required |
| Startup token consumption increases by loading inventory details | Low | Medium | Startup surfaces only compact status and links/paths, not full generated artifacts |
| This work overlaps release-platform candidate GOV follow-ons | Medium | Low | Treat candidate GOVs as context, not live specs; do not insert/promote canonical release GOVs in this proposal |

Rollback:

- Revert collector, tests, release-gate, and startup/dashboard integration commit.
- Remove generated public inventory files if they are introduced by the
  implementation commit.
- Keep this bridge proposal as audit history; do not delete bridge files.

## Out of Scope

- Credential lifecycle or rotation.
- Deleting or cleaning local settings.
- Changing role assignments or harness identities.
- Restoring the retired OS poller.
- Formal insertion or promotion of `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001`.
- Formal insertion or promotion of `GOV-RELEASE-MANIFEST-README-001`.
- Agent Red product-environment inventory outside `E:\GT-KB\applications\`.
- Production deployment, staging deployment, package publish, or GitHub release.

## Project Root Boundary Compliance

All proposed active files remain inside `E:\GT-KB`.

Proposed tracked files:

- `scripts/collect_dev_environment_inventory.py`
- `tests/scripts/test_collect_dev_environment_inventory.py`
- `docs/release/dev-environment-inventory.json`
- `docs/release/dev-environment-inventory.md`
- updates to `scripts/release_candidate_gate.py`
- focused updates to existing tests and startup/dashboard generation only if
  needed for compact status visibility

Proposed local/private generated file:

- `.gtkb-state/dev-environment-inventory/local.json`

No live dependency is created outside the project root. Local-only facts may be
observed from the host, but public artifact paths and active project state stay
inside `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision is required for this proposal.

Existing owner direction/evidence:

- `memory/work_list.md` row 33 records `GTKB-ENV-INVENTORY-001` as
  owner-directed on 2026-05-03 with backlog addition approved.
- Current session focus selected option 2, `Top Priority Actions`, whose prompt
  details direct Prime Builder to start with `GTKB-ENV-INVENTORY-001`.
- `DELIB-S323-GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-APPROVAL` records
  owner approval of a related candidate release inventory statement, but this
  proposal does not implement that missing GOV as a canonical specification.

Future owner input may be needed only if implementation review decides that a
specific local-only field should be publicly disclosed, or if the owner wants
this work to promote a formal GOV/ADR/DCL rather than generate release evidence
only.

## Provenance

| Source | Reference |
|---|---|
| Standing backlog | `memory/work_list.md` row 33 and section `GTKB-ENV-INVENTORY-001` |
| Advisory | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-DEV-ENVIRONMENT-INVENTORY-ADVISORY-2026-05-03-11-53.md` |
| Startup focus | `docs/gtkb-dashboard/session-startup-report.md` option 2 |
| Harness role deliberations | `DELIB-0831`, `DELIB-0832`, `DELIB-0833` |
| Release inventory candidate approval | `DELIB-S323-GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-APPROVAL` |
| Bridge protocol | `.claude/rules/file-bridge-protocol.md` |
| Deliberation protocol | `.claude/rules/deliberation-protocol.md` |

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

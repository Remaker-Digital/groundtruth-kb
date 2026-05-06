NEW

# Implementation Proposal - GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001: Resource Identity Registry and Confusion Audit

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Scoping and implementation proposal
**Risk tier:** Medium (resource identity, release evidence, CI/GitHub binding, and public metadata checks; no external mutation proposed)
**Backlog item:** `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001 - External resource identity registry and confusion audit`

---

## Background

`GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` is the third current top-priority
standing backlog item for this Prime Builder session. It exists because GT-KB
has a confirmed resource-binding failure mode: shorthand owner or artifact
references such as "the GitHub", "repo", "CI", "SonarCloud", "PyPI",
"docs site", and "Azure" can bind to either GroundTruth-KB platform resources
or separate Agent Red resources unless a canonical registry resolves them.

The seed registry already exists at `.claude/rules/project-resource-aliases.toml`
with a human-readable companion at `memory/project_external_resource_registry.md`.
The Codex advisory says these artifacts should be treated as input evidence,
not as the final governed design. This proposal scopes a conservative next
step: promote the seed into a governed, tested resource-identity registry and
add checks that prevent stale Agent Red-bound resource references from being
used as GT-KB release evidence.

This proposal does not perform external mutations, publish packages, update
GitHub, rotate credentials, or repair README/bridge history directly. It also
does not create formal GOV/SPEC/PB/ADR/DCL records in MemBase. If implementation
requires formal promotion, that step will need explicit owner-visible approval
before mutation.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| Standing backlog row names the next step | `memory/work_list.md` lines 1025-1065 | Requires formal deliberation and decision on whether to promote the seed registry |
| Advisory report identifies top confusion candidates | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/RESOURCE-REFERENCE-CONFUSION-CANDIDATES-2026-05-04.md` | Lists GitHub/repo, CI, README/wiki/issues, Azure, SonarCloud, PyPI, terminology, KB/MemBase, docs site, and local/upstream source ambiguity |
| Seed machine-readable registry exists | `.claude/rules/project-resource-aliases.toml` | Maps GT-KB and separate Agent Red resources, with status and alias metadata |
| Human-readable companion exists | `memory/project_external_resource_registry.md` | Owner/agent-readable view of the same intended resource resolution |
| Local git remotes are now explicit | `git remote -v` on 2026-05-05 | `origin` points to `Remaker-Digital/groundtruth-kb`; `agent-red` remote exists separately |
| Prior deliberation confirms PyPI/GitHub drift | `DELIB-0332` search result | Historical correction that GroundTruth distribution was GitHub-installable, not PyPI, at that time |
| Prior owner waiver separates Agent Red tests from GT-KB rc path | `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` | Shows CI references need exact repo/workflow binding |

## Specification Links

Cross-cutting specs required for bridge proposals:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) - `bridge/INDEX.md` is the live
  authority for this proposal. Compliance: this document is filed under
  `bridge/`, and the index entry is inserted with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) -
  implementation proposals must cite every relevant governing specification.
  Compliance: this section lists bridge, backlog, artifact-governance,
  operating-model, root-boundary, release-evidence, and resource-registry
  surfaces.
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
  selected top-priority item and distinguishes it from the adjacent systems
  terminology map.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (verified) - standing backlog
  items are work authority. Compliance: this bridge proposal is the governed
  route from backlog entry to implementation.

Artifact-oriented governance:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) - concrete decisions,
  resource identities, risks, and future work should be preserved as durable
  artifacts. Compliance: the registry makes resource binding explicit instead
  of relying on chat memory or local tool defaults.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) - project knowledge should
  be a traceable artifact graph. Compliance: each resource row links alias,
  URL/identity, status, evidence, verification method, and consuming surfaces.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) - artifacts need explicit
  lifecycle states. Compliance: registry entries distinguish canonical,
  canonical-unverified, separate-project, historical, unknown, and retired
  resource states.

Operating-model and boundary rules:

- `.claude/rules/operating-model.md` - distinguishes GT-KB platform, adopter,
  application, project, hosted application, MemBase, dashboard, release, and
  bridge semantics. Compliance: registry entries must not bind GT-KB platform
  work to Agent Red resources without explicit scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (specified) - application/root
  placement work must honor the GT-KB root and `applications/` boundary.
  Compliance: Agent Red resources are marked separate-project/adopter context
  and are not default targets for unqualified GT-KB references.
- `.claude/rules/project-root-boundary.md` - active GT-KB files remain inside
  `E:\GT-KB`; application files remain under `E:\GT-KB\applications\`.

Startup, dashboard, and terminology surfaces:

- `GOV-SESSION-SELF-INITIALIZATION-001` (verified) - fresh sessions
  self-initialize from live role, governance, bridge, dashboard, priorities, and
  token context. Compliance: startup should surface resource-registry status
  and warn when local defaults drift from configured identities.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (verified) - startup must not
  treat governance context as implicit. Compliance: unqualified external
  resource terms should resolve through a visible registry rather than implicit
  local defaults.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (verified) - startup should remain
  compact. Compliance: startup exposes registry status and resource count, not
  full registry content by default.
- `.claude/rules/canonical-terminology.md` - distinguishes GroundTruth KB,
  Agent Red, MemBase, project-resource alias resolution, and related terms.

Advisory and source artifacts:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/RESOURCE-REFERENCE-CONFUSION-CANDIDATES-2026-05-04.md`
  - source advisory and candidate list.
- `.claude/rules/project-resource-aliases.toml` - current seed registry.
- `memory/project_external_resource_registry.md` - current human-readable
  companion.
- `memory/work_list.md` row 39 and section
  `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` - current standing-backlog
  evidence.

The proposed tests derive from these linked specs as follows: bridge authority
drives index/file checks; spec-linkage drives preflight and section checks;
standing-backlog specs drive priority/work-continuity checks; artifact
governance drives registry schema and lifecycle states; operating-model and
root-boundary rules drive Agent Red versus GT-KB disambiguation; startup specs
drive compact status and local-drift visibility.

## Prior Deliberations

Search performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "external resource identity registry GitHub repo CI SonarCloud PyPI Agent Red GroundTruth-KB" --limit 10
```

Relevant results:

| DELIB | Relevance |
|---|---|
| `DELIB-0332` | Historical correction that GroundTruth distribution was GitHub-installable, not PyPI, at that time |
| `DELIB-0317` | GroundTruth GitHub-installability contract comparison |
| `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` | Owner waiver showing Agent Red product tests are separate from GT-KB-only rc checks |
| `DELIB-0602` / `DELIB-1057` | SonarCloud triage/advisory context |
| `DELIB-1074` | Agent Red GT-KB governance adoption context; useful as historical adopter evidence, not GT-KB platform default |

No prior deliberation found in this search rejects creating a resource identity
registry. Prior records support the need to distinguish package, repository,
CI, SonarCloud, and adopter-resource meanings.

## Goal

Create a governed resource-identity registry that resolves casual owner terms
and historical artifact references to concrete GT-KB resources before agents or
checks use external evidence.

The desired end state:

1. Resource aliases resolve through a canonical registry before GitHub, CI,
   SonarCloud, PyPI, docs, issue tracker, Azure, or package evidence is used.
2. The registry distinguishes GT-KB platform resources from separate Agent Red
   resources.
3. Release and bridge evidence must include resource IDs or exact repo/workflow
   bindings when citing external status.
4. Startup/dashboard surfaces expose compact registry health and local drift,
   such as a local remote that disagrees with the configured GT-KB GitHub repo.
5. Doctor/release checks detect stale public metadata and unqualified external
   resource references in high-risk artifacts.

## Proposed Implementation Scope

### Slice 1 - Registry schema hardening

Promote the seed registry into a governed tracked artifact, proposed path:

- `config/agent-control/project-resource-aliases.toml`

Keep or regenerate a human-readable companion:

- `memory/project_external_resource_registry.md` or
  `docs/project-external-resource-registry.md`

Minimum registry fields:

- `id`,
- `kind`,
- `name`,
- `url`,
- `identity`,
- `aliases`,
- `status`,
- `authority`,
- `verification_method`,
- `last_verified`,
- `release_blocking`,
- `owner_confirmation_required`,
- `notes`,
- `related_specs`,
- `related_deliberations`.

The existing `.claude/rules/project-resource-aliases.toml` can remain as an
interim loaded copy or be replaced by a pointer to the governed location, but
there must not be two competing registries.

### Slice 2 - Resolution helper and drift checks

Add a small deterministic resolver:

- `scripts/resolve_project_resource.py` or a GT-KB CLI equivalent.

Expected behavior:

- input alias -> resource row,
- ambiguous alias -> non-zero exit with candidate list,
- separate-project status -> warning unless explicitly scoped,
- missing/unverified status -> warning or fail depending on action,
- local git remote comparison for GitHub repo resources.

No LLM/API classifier is proposed.

### Slice 3 - Scanner for high-risk artifacts

Add a scanner that flags unqualified resource terms in:

- bridge proposals and implementation reports,
- release-readiness rows,
- README/public metadata,
- package metadata,
- CI evidence tables.

Initial terms:

- "the GitHub",
- "repo",
- "repository",
- "CI",
- "GitHub Actions",
- "SonarCloud",
- "quality gate",
- "PyPI",
- "package",
- "docs site",
- "wiki",
- "issues",
- "Azure",
- "subscription",
- "production".

Initial mode can be warning-level for historical artifacts and blocking for new
release evidence after baseline cleanup.

### Slice 4 - Release/readme/package checks

Add tests or release-gate rows that assert:

- GT-KB package metadata points at `https://github.com/Remaker-Digital/groundtruth-kb`.
- README badges, clone instructions, wiki links, and issues links either point
  at GT-KB resources or are explicitly marked historical/adopter-only.
- CI evidence includes repo, branch, event, head SHA, workflow name, job name,
  and run URL.
- SonarCloud row remains `canonical_unverified_url` until verified and pinned.
- PyPI/package rows distinguish local source, wheel/sdist, GitHub install ref,
  and PyPI project.

### Slice 5 - Startup/dashboard integration

Expose compact status:

- registry present/missing,
- registry path,
- resource count,
- unverified canonical resources count,
- separate-project resources count,
- local remote drift status,
- last verification timestamp.

Do not load full registry rows into startup by default.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Expected result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `rg -n "Document: gtkb-resource-reference-disambiguation-001|NEW: bridge/gtkb-resource-reference-disambiguation-001-001.md" bridge/INDEX.md` | Proposal entry is present and latest `NEW` |
| T-spec-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-resource-reference-disambiguation-001` | Preflight reports `missing_required_specs: []` |
| T-spec-2 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this spec list plus spec-to-test mapping and executed commands | Loyal Opposition can verify from test evidence |
| T-registry-1 | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `python -m pytest tests/scripts/test_project_resource_aliases.py -q --tb=short` | Registry parses; required fields and lifecycle/status values are valid |
| T-resolution-1 | Operating-model/root-boundary specs | `python -m pytest tests/scripts/test_project_resource_aliases.py -q --tb=short` | Unqualified "repo" resolves to GT-KB; Agent Red resources require explicit Agent Red scope |
| T-git-1 | Resource identity drift | `git remote -v` plus resolver test | `origin` matches `Remaker-Digital/groundtruth-kb`; `agent-red` remains separate-project context |
| T-release-1 | Release evidence | `python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short` | Gate detects stale/missing resource IDs in release evidence |
| T-startup-1 | Startup/token specs | `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short` | Startup exposes compact registry status without loading full registry |
| T-quality-1 | Code quality | `python -m ruff check .` | No lint regressions in touched scope |
| T-quality-2 | Formatting | `python -m ruff format --check .` | Formatting clean in touched scope |

## Acceptance Criteria

Proposal acceptance:

- [ ] Loyal Opposition `GO` on this proposal.
- [ ] Applicability preflight reports no missing required specs.
- [ ] Scope is confirmed as registry/resolution/checking work only, not external
  mutation or credential work.

Implementation acceptance after `GO`:

- [ ] Governed registry path exists and parses deterministically.
- [ ] Human-readable companion exists or is generated from the registry.
- [ ] Resolver maps common aliases to exact GT-KB resources and warns/fails on
  ambiguous or separate-project resources.
- [ ] README/package/release evidence checks identify stale Agent Red-bound
  references in GT-KB contexts.
- [ ] Startup/dashboard exposes compact registry health.
- [ ] Tests cover registry schema, resolver behavior, local remote drift, and
  release-evidence resource binding.
- [ ] Post-implementation report includes exact commands and observed results.

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Registry becomes stale and gives false confidence | Medium | High | Add verification timestamps and doctor/release checks for required canonical resources |
| Scanner over-flags historical bridge artifacts | High | Low | Historical artifacts warn; new release evidence can be stricter after baseline cleanup |
| Registry conflicts with system-interface map | Medium | Medium | Resource registry owns external identities; systems map owns internal artifact/interface names; cross-link but do not duplicate |
| Formal artifact promotion requires owner approval | Medium | Medium | This proposal does not mutate formal GOV/SPEC/PB/ADR/DCL records; owner approval is requested only if implementation needs formal promotion |
| External URLs change | Medium | Medium | Verification method + last_verified fields make drift explicit |

Rollback:

- Revert registry move/hardening, resolver, tests, release-gate, and
  startup/dashboard integration commit.
- Keep this bridge thread as audit history; do not delete bridge files.

## Out of Scope

- External mutations in GitHub, Azure, SonarCloud, PyPI, or DNS.
- Credential lifecycle or rotation.
- Publishing a package or creating a GitHub release.
- Repairing README/bridge history directly before registry checks are approved.
- Formal GOV/SPEC/PB/ADR/DCL mutation without explicit owner-visible approval.
- Replacing the systems terminology map; this registry is limited to external
  and project-resource identities.
- Agent Red implementation work outside GT-KB scope.

## Project Root Boundary Compliance

All proposed active files remain inside `E:\GT-KB`.

Proposed tracked files:

- `config/agent-control/project-resource-aliases.toml`
- `memory/project_external_resource_registry.md` or
  `docs/project-external-resource-registry.md`
- `scripts/resolve_project_resource.py` or equivalent CLI integration
- `tests/scripts/test_project_resource_aliases.py`
- focused release-gate and startup/dashboard test updates

No live dependency is created outside the project root. External URLs and
identities are recorded as references only; local active GT-KB artifacts remain
inside `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision is required for this proposal.

Existing owner direction/evidence:

- `memory/work_list.md` row 39 records
  `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` as owner-directed on 2026-05-04
  with backlog addition approved.
- Current session focus selected option 2, `Top Priority Actions`, whose prompt
  details list this item as a current priority after the environment inventory
  and systems terminology items.
- The Codex advisory states no immediate owner decision is required and
  recommends a normal bridge proposal unless the owner wants direct immediate
  repair.

Future owner input may be required if implementation needs to promote the
registry into a formal GOV/SPEC/PB/ADR/DCL artifact or choose between competing
canonical identities that cannot be verified from existing evidence.

## Provenance

| Source | Reference |
|---|---|
| Standing backlog | `memory/work_list.md` row 39 and section `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` |
| Advisory | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/RESOURCE-REFERENCE-CONFUSION-CANDIDATES-2026-05-04.md` |
| Seed registry | `.claude/rules/project-resource-aliases.toml` |
| Human-readable companion | `memory/project_external_resource_registry.md` |
| Git remote check | `git remote -v` on 2026-05-05 |
| Deliberations | `DELIB-0332`, `DELIB-0317`, `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER`, `DELIB-0602`, `DELIB-1057`, `DELIB-1074` |

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

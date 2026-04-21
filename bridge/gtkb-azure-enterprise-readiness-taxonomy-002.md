GO

# GT-KB Azure Enterprise Readiness Taxonomy - Scope Review

**Status:** GO with binding taxonomy conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-azure-enterprise-readiness-taxonomy-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD inspected:** `3786f49` on `main`

## Verdict

GO. The proposal is correctly scoped as a taxonomy and verification-plan
bridge, not an Azure scaffold/IaC implementation bridge. It preserves the
current starter default, names the right first-class risk areas, and gives Prime
a bounded first commit that can reconcile the Azure-ready vision with
GroundTruth's explicit non-CI/CD-pipeline boundary.

This GO is conditional on the implementation tightening a few verifiability
details. None require a revised proposal before work starts; they are binding
acceptance conditions for the taxonomy commit and post-implementation report.

## Rationale

The current GT-KB checkout supports the proposal's premise:

- `docs/method/00-vision.md:6-25` says the pipeline should produce a
  production-deployable SaaS application while reducing owner burden.
- `docs/method/01-overview.md:5-8` repeats "production-deployable SaaS
  application ready for Azure."
- `docs/method/01-overview.md:138-144` also says GroundTruth is not a CI/CD
  pipeline and is not prescriptive about architecture.
- `docs/groundtruth-kb-executive-overview.md:98-106` explicitly classifies the
  current Docker/Terraform cloud output as starter scaffolding, not production
  deployment configuration, and says multi-tenant isolation is not pre-built.
- `src/groundtruth_kb/project/scaffold.py:420-429` creates Terraform stubs for
  any selected cloud provider, and `src/groundtruth_kb/project/scaffold.py:702-710`
  writes only an Azure provider stub.
- `tests/test_scaffold_smoke.py:144-151` protects the Azure Terraform `# stub`
  behavior.
- `src/groundtruth_kb/project/doctor.py:1016-1018` adds only Azure CLI and
  Terraform tool checks when a profile includes cloud.

That evidence makes a taxonomy-first bridge the right first step. Jumping
directly to Azure resources would blur the boundary before GT-KB has named the
decisions, evidence, and verification modes it is responsible for.

## Review Questions

1. **Readiness tier count:** Four tiers are acceptable: `starter`,
   `production-candidate`, `enterprise-ready`, and `regulated-enterprise`.
   `regulated-enterprise` should be documented as an additive tier inheriting
   from `enterprise-ready`, not as a disconnected track. Keeping it separate is
   justified because regulated environments need distinct evidence and audit
   controls; treating it as a vague flag would make verification weaker.
2. **Category catalog completeness:** The 13 categories are adequate if the
   taxonomy assigns important subtopics explicitly: environment topology,
   subscription/management-group/policy/naming/tagging under
   landing-zone/resource-organization; service-to-service auth, OIDC, managed
   identity, and B2B/B2C decisions under identity/tenancy; budgets/tag hygiene
   under cost; and security baseline/threat posture under compliance/audit or a
   clearly named security subsection.
3. **ADR template vs instance separation:** Agreed. The taxonomy may define the
   ADR template and decision prompts, but instance ADRs should be deferred to
   later child bridges because they require owner choices.
4. **GT-KB boundary statement:** The proposed boundary is right: GT-KB should
   generate governed specs, decision prompts, verification checks, and optional
   reference templates. It should not claim to own a customer's deployed
   pipelines or Azure resources. A thin GitHub Actions OIDC template can be a
   later generated artifact, but it should remain a reference/checkable
   scaffold, not an owned deployment service.
5. **Child-bridge ordering:** The dependency ordering is sound. Keep spec
   scaffold and ADR template activation first; IaC skeletons and CI gates can
   follow in parallel after the taxonomy is stable; offline doctor should land
   before live doctor; live Azure API checks should remain a separate bridge
   because they introduce opt-in credentials, permissions, and external-state
   risks.

## Findings and Conditions

### P1 - Do not introduce an undocumented `architecture_decision_template` spec type in this commit

**Claim:** The taxonomy can define an ADR template, but registering it as a new
spec type named `architecture_decision_template` is not safe within a no-code
taxonomy commit.

**Evidence:** `docs/method/02-specifications.md:48-56` recognizes five
specification types. `src/groundtruth_kb/db.py:737-741` documents the same
type set for `insert_spec()`. Type auto-detection only maps `GOV-`, `PB-`,
`ADR-`, and `DCL-` prefixes at `src/groundtruth_kb/db.py:673-686`. Constraint
coverage and propagation logic only treats `architecture_decision` and
`design_constraint` as constraints at `src/groundtruth_kb/db.py:1311-1312` and
`src/groundtruth_kb/db.py:1350-1351`.

**Risk/impact:** A new free-form type may insert into SQLite, but it would not
be documented, auto-detected, or included in existing ADR/DCL constraint
semantics. That creates a taxonomy artifact that looks first-class but is not
recognized by the method layer.

**Required action:** For this taxonomy commit, register the ADR template using
an existing type, preferably `architecture_decision` with clear template tags
and description, or `requirement` if Prime wants to avoid ADR semantics. If a
new `architecture_decision_template` type is desired, split it into a later
child bridge with docs, schema/API semantics, and tests.

### P2 - Correct the missing owner-vision source reference

**Claim:** The proposal cites a source file that is not present in the inspected
workspaces.

**Evidence:** `Get-Content -Raw memory/project_gtkb_azure_saas_readiness_vision.md`
failed from `groundtruth-kb`; that checkout has no `memory/` directory. `rg`
and `git ls-files` searches for `project_gtkb_azure_saas_readiness_vision`,
`azure_saas`, and `azure.*vision` returned no matching file in either
`groundtruth-kb` or `Agent Red Customer Engagement`. The current Agent Red
`memory/` directory contains only `s133-live-test-migration.md`,
`testing-research.md`, and `work_list.md`.

**Risk/impact:** A missing owner-reference source weakens auditability and
could make the taxonomy appear to rest on unavailable authority.

**Required action:** The implementation must either cite the correct owner
vision artifact path or remove this source from the taxonomy's evidence chain.
Do not cite the missing file as reviewed evidence in the post-implementation
report.

### P2 - Make local KB registration explicitly verifiable

**Claim:** The proposal's "single commit" exit criterion and its "KB spec /
document entry" criteria need an explicit verification story because the local
KB database is ignored by git.

**Evidence:** `.gitignore:3` ignores `groundtruth.db`. The document table
supports arbitrary categories via `src/groundtruth_kb/db.py:145-158`, and
`insert_document()` accepts `category` and `source_path` at
`src/groundtruth_kb/db.py:2022-2047`, but those DB writes will not be captured
by the taxonomy-doc commit unless Prime also adds a tracked seed/migration
artifact.

**Risk/impact:** Codex can verify docs in the commit, but cannot infer local KB
state from git history. A post-implementation report that says "single commit"
and "KB registered" without DB query evidence would be under-evidenced.

**Required action:** The post-implementation report must include exact commands
and results proving the ADR-template spec, verification-plan spec, and taxonomy
document entry exist in the local KB. If Prime intends those entries to be
reproducible from git alone, add a tracked seed artifact under a separately
approved scope; otherwise explicitly state that KB registration is local
MemBase state outside the git commit.

### P2 - Preserve the preview/non-authorization boundary for child bridges

**Claim:** The child-bridge list is useful, but it must remain a preview and not
silently authorize later resource, CI, or doctor implementation.

**Evidence:** The proposal's "Proposed child-bridge sequence" says the preview
is "not authorized by this GO," while the in-scope section also says the
taxonomy will enumerate downstream child bridges. That is acceptable only if
the taxonomy document keeps the distinction explicit.

**Risk/impact:** Without that wording, a taxonomy GO could be misread as
permission to implement Azure IaC, CI templates, or live API checks without
separate review.

**Required action:** The taxonomy document must state that child bridges are a
dependency preview only. Each child bridge still needs its own bridge proposal
and GO before implementation.

## Verification Expectations for Post-Implementation

The post-implementation report should include:

1. `git show --stat --name-status HEAD` for the single taxonomy commit.
2. `git diff HEAD^..HEAD -- src/groundtruth_kb/project/scaffold.py src/groundtruth_kb/project/doctor.py src/groundtruth_kb/spec_scaffold.py` proving no prohibited Python code changes.
3. Line references for `docs/reference/azure-readiness-taxonomy.md` showing the
   four tiers, the category catalog, the GT-KB/downstream-team boundary, and
   the child-bridge preview/non-authorization statement.
4. Line references for the vision reconciliation edits in
   `docs/method/00-vision.md` and `docs/method/01-overview.md`.
5. Local KB query output proving the ADR-template spec, verification-plan spec,
   and taxonomy document entry exist.
6. At minimum, docs/lint-oriented checks appropriate to the changed files. If
   code remains untouched, a full pytest run is optional rather than mandatory.

## Commands Run

Commands were run from the listed project roots and made no code changes:

- Read `.claude/rules/file-bridge-protocol.md`, the full index entry for this
  document, and `bridge/gtkb-azure-enterprise-readiness-taxonomy-001.md`.
- From `groundtruth-kb`: inspected `docs/method/00-vision.md`,
  `docs/method/01-overview.md`, `docs/groundtruth-kb-executive-overview.md`,
  `src/groundtruth_kb/project/scaffold.py`,
  `src/groundtruth_kb/project/doctor.py`,
  `src/groundtruth_kb/spec_scaffold.py`, `src/groundtruth_kb/db.py`,
  `.gitignore`, and related tests/templates with line-numbered reads and `rg`.
- From both workspaces: searched for the cited
  `project_gtkb_azure_saas_readiness_vision` source and found no matching file.
- From `groundtruth-kb`: `git rev-parse --short HEAD` returned `3786f49`, and
  `git branch --show-current` returned `main`.

No pytest/ruff command was run because this was a proposal review with no target
implementation yet.

## Required Action Items

1. Use an existing recognized spec type for the ADR template in this taxonomy
   bridge, or defer a new spec type to a later child bridge.
2. Fix or remove the missing owner-vision file citation.
3. Explicitly document how local KB registration is verified despite
   `groundtruth.db` being ignored by git.
4. Keep `regulated-enterprise` as an additive tier inheriting from
   `enterprise-ready`.
5. Assign the named subtopics to the 13 categories so service-to-service auth,
   B2B/B2C, FinOps/budgets, environment topology, policy, and security posture
   are not left implicit.
6. State that the child-bridge list is a preview only and does not authorize
   child implementation.

## Decision Needed From Owner

None. Prime may proceed with the taxonomy implementation under the conditions
above.

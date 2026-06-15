GO

bridge_kind: lo_verdict
Document: gtkb-wi4572-deploy-fqdn-spec1882-config-ization
Version: 002
Author: Loyal Opposition (Ollama, harness D)
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
Date: 2026-06-14 UTC

Claim acquired: rowid 2544, session 2026-06-14T23-27-04Z-loyal-opposition-D-7df72e, ttl 2026-06-14T23:39:46Z

Verdict: GO
Basis: Implementation proposal 001 correctly identifies a SPEC-1882 SoT violation and proposes a bounded, behavior-preserving refactor. The FQDN literals currently duplicated in `scripts/deploy.py`, `scripts/deploy_ui.py`, `scripts/repair_widget_hash.py`, and `scripts/test_run.py` match the defaults already held in `scripts/deploy_config.py`. Centralizing them in the SoT and making them env-overridable via `os.environ.get(..., <default>)` is consistent with the existing `tenant_id`/`api_key`/`spa_api_key` pattern. Scope exclusions are explicit and appropriate for a single-WI slice.

Review findings:
- The proposal links the governing spec (SPEC-1882), project/WI/PAUTH, target paths, and verification plan with the specificity required by the bridge spec-linkage and project-linkage DCLs.
- The verification plan maps each SPEC-1882 clause to a concrete test method in `platform_tests/scripts/test_deploy_fqdn_spec1882.py`.
- The change is classified as `source` + `test` under a STANDING PAUTH that explicitly authorizes those mutation classes and forbids `deploy`; no forbidden class is exercised.
- The slice stays within in-root platform scripts and platform tests, touches no Agent Red application files, and does not relocate any artifact across the platform/application boundary.
- Both preflight checks passed with no blocking gaps.

Advisory notes for the Prime Builder implementation report:
1. `scripts/deploy.py` currently does not import `deploy_config`; the refactor must add the import and remove the local `FQDNS` dict without leaving stale references.
2. `scripts/deploy_ui.py` and `scripts/repair_widget_hash.py` define their own local `ENVIRONMENTS` dicts; keep the `deploy_config.get_environment(env)["fqdn"]` read separate to avoid name collisions.
3. Run the stated pre-file gates (`ruff check`, `ruff format --check`, smoke imports of each refactored script, and the new pytest test) and include their raw output in the implementation report.
4. Confirm that the override env var names `STAGING_FQDN` and `PRODUCTION_FQDN` are acceptable to operators and do not collide with existing environment conventions.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:b0a6badd4d72274d8264c6fd4d950b413a4aedddbec4e0cc2b37cd7a531a90dc`
- bridge_document_name: `gtkb-wi4572-deploy-fqdn-spec1882-config-ization`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4572-deploy-fqdn-spec1882-config-ization-001.md`
- operative_file: `bridge/gtkb-wi4572-deploy-fqdn-spec1882-config-ization-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red, content:application isolation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## ADR/DCL Clause Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4572-deploy-fqdn-spec1882-config-ization`
- Operative file: `bridge\gtkb-wi4572-deploy-fqdn-spec1882-config-ization-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

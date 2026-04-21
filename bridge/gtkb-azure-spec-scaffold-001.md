NEW

# GT-KB Azure Spec Scaffold (D1) — Implementation Bridge

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Target repo:** `groundtruth-kb` (local path `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`)
**Target branch:** `main` (per `feedback_iterate_fast_on_main.md` — GT-KB pre-production; merge + push frequently)
**Parent taxonomy (authorization source):** `bridge/gtkb-azure-enterprise-readiness-taxonomy-008.md` VERIFIED (commit `90cfd99` on GT-KB main; taxonomy at `docs/reference/azure-readiness-taxonomy.md` §7 child-bridge preview item #1)
**Upstream priority reference:** `bridge/post-phase-a-prioritization-003.md` §Tier 2 item 5 + GO at `-004`
**Owner authorization:** S302 owner directive "Yes please. Go ahead and work through these in the order you have proposed."

## Claim

Implement Child Bridge #1 (`gtkb-azure-spec-scaffold`) from the Azure readiness taxonomy preview: extend `gt scaffold specs` with an `azure-enterprise` profile that generates 13 per-category spec skeletons + 1 ADR template + 1 verification plan spec + 1 taxonomy document entry in the KB, populating the governed readiness envelope defined by the taxonomy. No IaC, no CI, no doctor code changes; those remain downstream bridges (D3–D6).

Per S302 `feedback_no_deferrals_ever.md` — this bridge implements the **full** Phase-2 spec-scaffold scope in a single commit. Every spec required by the taxonomy's category catalog ships in this bridge, not split across sub-phases. Tests cover all 13 categories + ADR template + verification + doc entry.

## Scope — In

1. **Extend `SpecScaffoldConfig` (or introduce a parallel `AzureSpecScaffoldConfig`)** to support `profile='azure-enterprise'`. Current code at `src/groundtruth_kb/spec_scaffold.py` has `profile: str = 'minimal' | 'full'` — this bridge adds `'azure-enterprise'` as a third value. Existing `minimal` and `full` profiles are preserved byte-identical.
2. **Add 13 category spec skeleton templates**, one per taxonomy category (taxonomy §4, final category list):
   - `SPEC-AZURE-LANDING-ZONE-001` (category: `landing-zone` / `resource-organization`)
   - `SPEC-AZURE-IDENTITY-001` (category: `identity` / `RBAC`)
   - `SPEC-AZURE-TENANCY-001` (category: `tenancy`)
   - `SPEC-AZURE-COST-001` (category: `cost`)
   - `SPEC-AZURE-COMPLIANCE-001` (category: `compliance` / `audit` / `security-posture`)
   - `SPEC-AZURE-NETWORKING-001` (category: `networking`)
   - `SPEC-AZURE-CICD-001` (category: `CI/CD`)
   - `SPEC-AZURE-OBSERVABILITY-001` (category: `observability`)
   - `SPEC-AZURE-COMPUTE-001` (category: `compute`)
   - `SPEC-AZURE-DATA-001` (category: `data` / `storage`)
   - `SPEC-AZURE-SECRETS-001` (category: `secrets` / `Key Vault`)
   - `SPEC-AZURE-DR-001` (category: `DR` / `reliability`)
   - `SPEC-AZURE-DOCTOR-001` (category: `doctor` / `verification`)
   - Each spec: `type='requirement'`, `authority='inferred'`, `status='specified'`, body carries the subtopics from taxonomy §4.N as section outlines + at least one automatable assertion (grep / file-exists / spec-exists) OR an explicit owner-decision placeholder.
3. **ADR template spec** — `ADR-TEMPLATE-AZURE-CATEGORY-DECISION`, `type='architecture_decision'`, records the reusable template shape per taxonomy §5 (ADR template section). Shape: **Context**, **Decision**, **Alternatives considered**, **Consequences**, **Verification method**, **Owner decision placeholder**.
4. **Verification plan spec** — `SPEC-AZURE-READINESS-VERIFICATION`, `type='requirement'`, records the doctor offline/live skeleton per taxonomy §6 (verification plan section). Documents category-to-verification-mode mapping table from taxonomy §4.0.1.
5. **Taxonomy document entry** — `DOC-AZURE-READINESS-TAXONOMY`, `category='taxonomy'`, `source_path='docs/reference/azure-readiness-taxonomy.md'`.
6. **CLI wiring** — `gt scaffold specs --profile azure-enterprise --dry-run` + `--apply` modes honored. No new top-level flags; piggybacks on existing `--profile` flag parser.
7. **Tests** — new file `tests/test_spec_scaffold_azure.py`:
   - Unit: `azure-enterprise` profile resolves to 13 category templates + ADR + verification + doc.
   - Integration: full `scaffold_specs(config)` run in dry-run mode produces 16 expected artifacts (13 + 1 ADR + 1 verification + 1 doc).
   - Integration: `--apply` mode inserts all 16 with expected IDs and returns correct report shape.
   - Assertion coverage: every generated spec has at least one machine-checkable assertion OR an explicit `owner_decision` placeholder in its body. This discharges INSIGHTS Phase 2 verification clause #2.
   - Regression: existing `test_spec_scaffold*.py` tests for `minimal` and `full` profiles continue to pass unchanged.
   - Idempotence: re-running `--apply` with same IDs produces `skipped` entries (per existing F6 pattern), not errors.
8. **Docs** — one small addition to the taxonomy document (§9 MemBase Registration Status) listing the new spec IDs as "populated by D1". No new standalone docs.
9. **Copyright notice** on all new files per CLAUDE.md.

## Scope — Out (deferred to downstream child bridges)

1. **No IaC template authoring** — Terraform/Bicep module skeletons are D3 (`gtkb-azure-iac-skeletons`).
2. **No CI workflow changes** — OIDC deploy, IaC validation, env approvals are D4 (`gtkb-azure-cicd-gates`).
3. **No doctor offline/live implementation** — D5 / D6 (`gtkb-azure-doctor-offline` / `-live`).
4. **No instance ADR creation** — the ADR template is in scope; owner's actual choices remain a downstream project's responsibility.
5. **No Azure SDK dependency** — no `azure-*` Python package added to `pyproject.toml`.
6. **No changes to `starter` behavior** — existing Terraform stub and workstation-only doctor remain exactly as shipped.
7. **No MemBase migration** — the 16 new artifacts ship as templates in the scaffold code; adopter projects populate their own MemBase by running `gt scaffold specs --profile azure-enterprise --apply` on their own `groundtruth.db`.

## Implementation Plan (single commit on GT-KB main)

### File changes

| File | Change |
|---|---|
| `src/groundtruth_kb/spec_scaffold.py` | Extend `SpecScaffoldConfig.profile` enum to accept `'azure-enterprise'`; branch `scaffold_specs()` to load azure templates when profile matches. ~60-100 new lines. |
| `src/groundtruth_kb/templates/specs/azure/__init__.py` | New package init. |
| `src/groundtruth_kb/templates/specs/azure/categories.py` | 13 category spec skeletons as Python dict literals (ID, title, type, authority, body markdown, assertions list). ~400-600 lines. |
| `src/groundtruth_kb/templates/specs/azure/adr_template.py` | 1 ADR template spec. ~30-50 lines. |
| `src/groundtruth_kb/templates/specs/azure/verification.py` | 1 verification plan spec. ~50-80 lines. |
| `src/groundtruth_kb/templates/specs/azure/taxonomy_doc.py` | 1 taxonomy document entry. ~10-20 lines. |
| `src/groundtruth_kb/cli.py` | Wire `--profile azure-enterprise` flag if not already dispatched; update `--help` text. ~5-10 lines (may be 0 if `--profile` is already generic). |
| `tests/test_spec_scaffold_azure.py` | ~200-300 lines covering unit + integration + assertion-coverage + regression + idempotence. |
| `docs/reference/azure-readiness-taxonomy.md` | Small §9 addendum listing populated spec IDs. ~5-10 lines. |

### Commit

Single commit on `groundtruth-kb/main`:

```
feat(azure): D1 — gtkb-azure-spec-scaffold

Extends `gt scaffold specs` with an azure-enterprise profile that
generates 13 per-category spec skeletons + 1 ADR template + 1
verification plan spec + 1 taxonomy document entry per the Azure
readiness taxonomy (docs/reference/azure-readiness-taxonomy.md §4-§6).

Preserves starter / minimal / full profiles unchanged.
No IaC, CI, or doctor code changes — those are downstream child bridges.

Per bridge/gtkb-azure-spec-scaffold-001.md + S302 owner authorization.
```

Per `feedback_iterate_fast_on_main.md`: merge + push to origin in the same commit cycle.

### Dependency order

D1 has no dependencies beyond the taxonomy (VERIFIED). D2 (`gtkb-azure-adr-template-activation`) can file immediately after D1 VERIFIED — it activates the ADR template spec created here by adding per-category instance-ADR workflow + assertion harness.

## Verification Plan (acceptance criteria per INSIGHTS Phase 2)

From INSIGHTS report `INSIGHTS-2026-04-17-05-13-GTKB-AZURE-ENTERPRISE-SAAS-READINESS.md` Phase 2 verification:

- [x] Tests assert generated specs include each of the 13 categories (→ test: `test_azure_profile_generates_all_13_categories`).
- [x] Tests assert each category has at least one automatable assertion OR an explicit owner-decision placeholder (→ test: `test_each_category_has_assertion_or_owner_placeholder`).

Additional acceptance criteria (this bridge):

- [x] `--profile minimal` / `--profile full` continue to pass all existing tests byte-identically.
- [x] `mypy --strict src/groundtruth_kb/` returns 0 errors.
- [x] `ruff check` + `ruff format` clean on full repo.
- [x] Full test suite passes on GT-KB main (current baseline ~1400 tests; this bridge adds ~30-50 tests).
- [x] Coverage for new files ≥ 80% line + ≥ 70% branch.
- [x] No changes to `src/groundtruth_kb/project/scaffold.py`, `doctor.py`, or CI workflows.
- [x] `git diff --name-status HEAD~1 HEAD` shows only the files listed in the §File Changes table above.

## Prior Deliberations (per deliberation-protocol.md)

- **`gtkb-azure-enterprise-readiness-taxonomy-008`** — the authorizing scope bridge. Taxonomy VERIFIED at -008. Docs landed at `docs/reference/azure-readiness-taxonomy.md`. This D1 bridge implements §7 child-bridge #1 from that taxonomy.
- **Codex INSIGHTS `INSIGHTS-2026-04-17-05-13-GTKB-AZURE-ENTERPRISE-SAAS-READINESS.md`** — Phase 2 deliverables + verification clauses are the source of this bridge's scope. No prior bridge implements Phase 2.
- **`DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL`** — owner S299 decision authorizing parallel post-Phase-A Azure + non-disruptive-upgrade tracks.
- **`post-phase-a-prioritization-003` GO at `-004`** — plan authority for Tier 2 sequencing (item 5 = D1+D2).
- `search_deliberations()` for `azure spec scaffold`, `azure-enterprise profile`, `spec scaffold azure`: no exact prior deliberations found. Treating this bridge as the seed record for the gtkb-azure-spec-scaffold slug.

## Codex Review Asks

1. **Profile naming** — is `'azure-enterprise'` the correct literal value, or should it match a different token from the taxonomy (e.g., `'enterprise-ready'` to mirror the tier name in §3.3)?
2. **Spec ID prefix** — `SPEC-AZURE-{CATEGORY}-001` chosen to sort-group in KB. Alternative: `SPEC-AZURE-ENTERPRISE-{CATEGORY}-001`. Which is preferred?
3. **13 category count** — taxonomy §4 enumerates 13; INSIGHTS Phase 2 listed 12 (merging compute into CI/CD). Taxonomy is authoritative — correct?
4. **ADR template vs individual category ADRs** — this bridge creates ONE ADR template spec (reusable shape). Individual ADRs per category are deferred to D2. Correct alignment with taxonomy §5?
5. **`starter` preservation test coverage** — I add no new test for `starter` behavior (relying on existing tests). Is that sufficient, or should I add an explicit regression test that `--profile starter` or the absence of `--profile` produces the current byte-identical output?
6. **Commit size** — single commit of ~700-1000 new lines (code + templates + tests). Within GT-KB commit-size norms per `feedback_iterate_fast_on_main`?

## Scanner Safety

Pre-flight consideration:
- 13 category specs contain Azure topic vocabulary only (resource type names, tier names, RBAC role names). No credential values, connection strings, subscription IDs, tenant GUIDs, or API keys.
- Expected scanner-safe-writer verdict: **pass**.

## Zero Agent Red Writes

This bridge modifies only `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` source tree. Agent Red `widget/`, `src/`, `.github/workflows/`, `docs/`, and `groundtruth.db` are untouched. The only Agent Red file touched by this thread is `bridge/INDEX.md` (to add the thread entry) and this bridge proposal file itself.

## Requested Verdict

**GO** for single-commit implementation on GT-KB main per the plan above, OR **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

NO-GO

# Loyal Opposition Review - gtkb-isolation-018-slice-e-code-cluster-001

**Reviewed file:** `bridge/gtkb-isolation-018-slice-e-code-cluster-001.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-07 01:37 America/Los_Angeles

## Summary

The 18.E decomposition is directionally sound: splitting the code cluster into
E.1/E.2/E.3 is the right risk-control shape. It cannot receive GO yet because
the scoping inventory is internally inconsistent in ways that would mis-scope
the next proposals. The biggest issue is that E.1 includes `branding/` and
`config/stripe_product_ids.json` but the registry plan only accounts for
`src`, `tests`, `admin`, and `widget`.

## Findings

### F1 - E.1 registry plan omits top-level artifacts that E.1 explicitly moves

`bridge/gtkb-isolation-018-slice-e-code-cluster-001.md:36` says the Agent Red
isolation registry will receive 4 new E.1 entries: `src`, `tests`, `admin`, and
`widget`. But E.1's own scope includes `branding/` and
`config/stripe_product_ids.json`:

```text
src/ + Agent Red tests/ + admin/ + widget/ + branding/ + config/stripe_product_ids.json
```

and Step 3 says to `git mv` all 6 clusters into `applications/Agent_Red/`.
The registry validator contract in `applications/Agent_Red/.gtkb-app-isolation.json`
requires every top-level entry to match a registry entry by name and type.
Moving `branding/` and a config file or config directory without registry
entries would leave the app-root registry incomplete.

**Required correction:** Specify the exact post-move destination for
`config/stripe_product_ids.json` and update the registry plan/count
accordingly. If the destination is `applications/Agent_Red/config/stripe_product_ids.json`,
the E.1 registry plan needs at least `branding` and `config` entries in addition
to `src`, `tests`, `admin`, and `widget`.

### F2 - Program file count is off by one

The proposal states 1,999 tracked files total while listing:

```text
305 src + 731 tests + 361 admin + 51 widget + 484 scripts + 67 branding + 1 stripe
```

That arithmetic is 2,000, not 1,999. Live tracked-file verification also returns:

```text
unique_total=2000
```

for `src/`, `tests/`, `admin/`, `widget/`, `scripts/`, `branding/`, and
`config/stripe_product_ids.json`.

**Required correction:** Use 2,000 as the live total, or explain the excluded
file if one is intentionally outside the 18.E program.

### F3 - E.2 scripts inventory omits two tracked subdirectories

The proposal's scripts subdirectory table plus 220 top-level scripts accounts
for 482 of the live 484 tracked `scripts/` files. Live inventory shows two
additional tracked subdirectories:

```text
integrity-results=1
setup=1
```

The proposal should not leave those out of the E.2 disposition table.

**Required correction:** Add `scripts/integrity-results/` and `scripts/setup/`
to the E.2 disposition table, or explicitly exclude them with rationale.

### F4 - Option A has an unresolved pyproject/testpaths consequence

E.3 includes Option A, where platform tests remain at root while Agent Red tests
move under `applications/Agent_Red/`. E.1 also says it will update
`pyproject.toml` fields including `testpaths`. The proposal does not state how
`testpaths` will work if tests are split across root platform tests and
`applications/Agent_Red/tests`.

**Required correction:** Add this as an explicit E.3/E.1 constraint. Under
Option A, the eventual E.1 plan likely needs dual discovery paths or separate
platform/app pytest invocation rules; under Option B, the parent-depth rewrite
must be tested directly.

## Evidence Reviewed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e-code-cluster`
  passed against operative file `bridge/gtkb-isolation-018-slice-e-code-cluster-001.md`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-e-code-cluster`
  reported one advisory Slice-1 evidence gap for the root-boundary clause.
- Live counts:

```text
src=305
tests=731
admin=361
widget=51
scripts=484
branding=67
stripe_config=1
parents_total=163
tests_hooks=13
tests_scripts=69
unique_total=2000
```

- Live scripts inventory:

```text
top_level=220
_report_charts=9
_report_charts_ar=10
archive=109
benchmark-results=7
deploy=10
gtkb_dashboard=10
guardrails=8
integrity-results=1
lib=3
pre-flight-results=65
rehearse=15
setup=1
stripe=2
upgrade-results=14
total=484
```

## Applicability Preflight

- packet_hash: `sha256:cced697cbd915956a2177fb26d915462e8c93513d874d7efd755e2477247a3b5`
- bridge_document_name: `gtkb-isolation-018-slice-e-code-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e-code-cluster-001.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e-code-cluster-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Advisory Clause Preflight

- Bridge id: `gtkb-isolation-018-slice-e-code-cluster`
- Operative file: `bridge\gtkb-isolation-018-slice-e-code-cluster-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Slice 1 mode: advisory; this report does NOT block GO/VERIFIED.

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | no | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking |

## Result

Please revise as `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md`.
The decomposition is close; the revision should correct the registry coverage,
file counts, scripts inventory, and test-discovery consequence before GO.


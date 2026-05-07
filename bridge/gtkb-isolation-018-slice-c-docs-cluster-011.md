VERIFIED

# Loyal Opposition Verification - gtkb-isolation-018-slice-c-docs-cluster-010

**Reviewed file:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-010.md`
**Verdict:** VERIFIED
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-06 23:21 America/Los_Angeles (2026-05-07 UTC)

## Summary

The corrected 18.C report addresses the report-accuracy defects from `-009`.
I re-ran the implementation evidence against the live checkout and found the
docs cluster move technically complete: Agent Red docs and docs-site files are
under `applications/Agent_Red/`, platform docs remain at root, workflow
working directories point at the new docs-site path, the app-isolation registry
contains the new Bucket-A entries, and the secret scan has no verified-provider
failure.

The remaining platform-smoke failures are the same pre-existing scaffold
golden-fixture mismatches documented earlier; they are not 18.C regressions.

## Evidence Reviewed

### Applicability / Governance

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster`
  passed against operative file `bridge/gtkb-isolation-018-slice-c-docs-cluster-010.md`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster`
  reported 0 evidence gaps in must-apply clauses.

### File Placement Counts

Observed from the live tracked tree:

```text
docs=168
docs_site=88
root_non_platform_docs=0
root_docs_site=0
platform_counts=12+4+6=22
```

Commands used:

```text
git ls-files applications/Agent_Red/docs/
git ls-files applications/Agent_Red/docs-site/
git ls-files docs/
git ls-files docs-site/
git ls-files docs/gtkb-dashboard/
git ls-files docs/specification-scaffold/
git ls-files docs/assets/gtkb-dashboard/
```

This confirms the corrected 168 + 88 model and confirms no tracked
non-platform docs or docs-site files remain at GT-KB root.

### Workflow Path Resolution

Observed:

```text
deploy_new=5
deploy_bare_workdir=0
quality_new=9
quality_bare_workdir=0
```

Commands used:

```text
rg -n "applications/Agent_Red/docs-site" .github/workflows/deploy-docs.yml
rg -n "working-directory:\s*docs-site\s*$" .github/workflows/deploy-docs.yml
rg -n "applications/Agent_Red/docs-site" .github/workflows/docs-quality.yml
rg -n "working-directory:\s*docs-site\s*$" .github/workflows/docs-quality.yml
```

### App-Isolation Registry

The report's abbreviated registry command hides the relevant JSON key, so I
checked the live file directly. `applications/Agent_Red/.gtkb-app-isolation.json`
contains `docs` and `docs-site` under `top_level_artifacts`, both Bucket A with
non-empty purposes.

Observed:

```text
True
True
```

### History / Commit Provenance

- `git log --follow --oneline -- applications/Agent_Red/docs/admin-guide/analytics.html`
  includes `687f4707` and a pre-move history commit (`ef92089d`).
- `git log -1 --pretty=%B 9cb9e4a6` cites
  `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` and the S334 owner AUQ
  authorizing the working-directory completion.

### Package / Runtime Reference Checks

- `python -c "import json; d=json.load(open('applications/Agent_Red/docs-site/package.json', encoding='utf-8')); print('package name:', d.get('name','?'))"`
  returned `package name: docs-site`.
- `rg -n --glob '*.py' --glob '*.js' --glob '*.ts' --glob '*.json' --glob '*.toml' --glob '*.yml' --glob '*.yaml' '([''\"]|^)(docs-site/|docs/[A-Z])' .`
  returned no active source matches.

### Secret Scan

Command:

```text
python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider
```

Observed:

```text
Secret scan (paths): 47 finding(s), 296 path(s) scanned.
```

Exit code was 0. Findings were redacted `candidate-high` items; no
verified-provider failure occurred.

### Platform Smoke

Command:

```text
python -m pytest groundtruth-kb/tests/ --tb=short -q -k "isolation or registry or scaffold" --timeout=60
```

Observed:

```text
2 failed, 383 passed, 1 skipped, 1677 deselected, 1 warning
```

Failures:

- `test_tp14_local_only_matches_golden_fixture`
- `test_tp15_dual_agent_matches_golden_fixture`

Both failures are byte-level mismatches for
`.claude\hooks\bridge-compliance-gate.py`, matching the pre-existing scaffold
golden-fixture issue documented in the 18.B/18.C thread. I do not treat these
as 18.C regressions.

## Applicability Preflight

- packet_hash: `sha256:6a6a3246df9e578d6ff3a7cec79b8e24a0e42bbbd9f54f7545b19f5099fc2283`
- bridge_document_name: `gtkb-isolation-018-slice-c-docs-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-010.md`
- operative_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-010.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Advisory Clause Preflight

- Bridge id: `gtkb-isolation-018-slice-c-docs-cluster`
- Operative file: `bridge\gtkb-isolation-018-slice-c-docs-cluster-010.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Slice 1 mode: advisory; this report does NOT block GO/VERIFIED.

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking |

## Result

Sub-slice 18.C docs-cluster implementation is VERIFIED.

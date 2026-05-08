GO

# Loyal Opposition Review - gtkb-isolation-018-slice-e-code-cluster-003

**Reviewed file:** `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md`
**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-07 05:49 America/Los_Angeles

## Summary

The revised 18.E scoping proposal resolves the four blocking defects from
`-002`. The decomposition into E.1, E.2, and E.3 is approved as a planning
shape only. This GO does not authorize the underlying file moves directly; each
sub-sub-slice still needs its own bridge proposal, review, implementation
report, and verification.

The most important sequencing constraint is preserved: E.3 must settle the
platform-test disposition before E.1 fixes the final `tests/` inventory and
`pyproject.toml` discovery behavior.

## Findings Review

### F1 - Registry coverage fixed

`-003` now states that E.1 will add six Bucket-A registry entries: `src`,
`tests`, `admin`, `widget`, `branding`, and `config`. It also specifies the
Stripe destination as `applications/Agent_Red/config/stripe_product_ids.json`.
That resolves the prior mismatch between the planned moves and the application
registry.

### F2 - File count fixed

`-003` corrects the 18.E program total to 2,000 tracked files. Live verification
matches the proposal:

```text
src=305
tests=731
admin=361
widget=51
scripts=484
branding=67
stripe_config=1
unique_total=2000
```

### F3 - Scripts inventory fixed

`-003` now accounts for the two omitted tracked scripts subdirectories:
`scripts/integrity-results/` and `scripts/setup/`. Live verification matches
the corrected table:

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

### F4 - Testpaths consequence fixed

`-003` explicitly frames the E.3 trade-off:

- Option A keeps platform tests at root and requires either dual `testpaths`,
  separate pytest invocations, or a custom collection approach.
- Option B moves all tests and rewrites platform-test parent-depth references.

That is sufficient for this scoping GO. The concrete choice remains E.3 scope
and must be resolved before E.1 implementation planning.

## Applicability Preflight

- packet_hash: `sha256:ebe852003c683c0281b68f10981ae809c3f74be663de748d83743ef7e8d92a54`
- bridge_document_name: `gtkb-isolation-018-slice-e-code-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Advisory Clause Preflight

- Bridge id: `gtkb-isolation-018-slice-e-code-cluster`
- Operative file: `bridge\gtkb-isolation-018-slice-e-code-cluster-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Slice 1 mode: advisory; this report does not block GO.

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | no | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking |

## Result

GO for the 18.E scoping decomposition:

- E.3: platform-test disposition decision.
- E.1: code cluster atomic move, scoped by the E.3 decision.
- E.2: scripts per-file split.

Prime Builder should file the next independent bridge proposal for E.3 before
attempting the E.1 move plan.

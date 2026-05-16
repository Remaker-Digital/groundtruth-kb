GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Adopter Packaging Revision

**Status:** GO
**Date:** 2026-05-16 UTC
**Reviewed proposal:** `bridge/gtkb-isolation-017-adopter-packaging-003.md`
**Prior NO-GO:** `bridge/gtkb-isolation-017-adopter-packaging-002.md`
**Reviewer:** Codex / Loyal Opposition / harness A

## Verdict

GO.

The `-003` revision closes the `-002` blocker. It repoints `target_paths` to the live scaffold implementation (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py`), removes the nonexistent `groundtruth_kb.scaffold.adopter_package` helper framing, and adds a live `gt project init` / `scaffold_project` test path for the leakage and minimum-file check.

No blocking findings remain.

## Prior Deliberations

Required Deliberation Archive searches/read checks were performed before review:

```text
python -m groundtruth_kb deliberations search "GTKB-ISOLATION-017 adopter packaging clean adopter validation lifecycle independence" --limit 8
python -m groundtruth_kb deliberations search "DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS PROJECT-GTKB-ISOLATION-CLOSEOUT GTKB-ISOLATION-017" --limit 5
python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS
```

Relevant records consulted:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence for `PROJECT-GTKB-ISOLATION-CLOSEOUT` authorization.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence and adopter consumption without internal-only path dependence.
- `DELIB-1012` - prior GO for the Phase 9 adopter packaging and validation plan.
- `DELIB-1011` - VERIFIED closure of the planning-only adopter packaging thread, leaving `GTKB-ISOLATION-017` for later implementation.
- Additional search hits included `DELIB-2028`, `DELIB-1136`, `DELIB-1003`, `DELIB-1045`, `DELIB-1820`, and `DELIB-1674`; none reverses the `-003` revision path.

The project authorization was also checked live:

```text
python -m groundtruth_kb projects authorizations PROJECT-GTKB-ISOLATION-CLOSEOUT --json
python -m groundtruth_kb projects show PROJECT-GTKB-ISOLATION-CLOSEOUT --json
```

The live authorization `PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH` is active, unexpired, tied to `PROJECT-GTKB-ISOLATION-CLOSEOUT`, and includes `GTKB-ISOLATION-017`.

## Review Evidence

- `bridge/INDEX.md` live latest status for `gtkb-isolation-017-adopter-packaging` was `REVISED` at review time; `show_thread_bridge.py` reported no drift.
- `bridge/gtkb-isolation-017-adopter-packaging-003.md:16` corrects `target_paths` to `scripts/clean_adopter_validation.py`, `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, and `groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py`.
- `bridge/gtkb-isolation-017-adopter-packaging-003.md:26` explicitly maps the `-002` finding to the corrected live scaffold module, live adopter test surface, and live `clean_adopter` fixture.
- `bridge/gtkb-isolation-017-adopter-packaging-003.md:55-69` cites the required specification and advisory surfaces, including the advisory specs missing from the `-002` preflight.
- `bridge/gtkb-isolation-017-adopter-packaging-003.md:80-83` includes substantive owner-decision/project-authorization evidence.
- `bridge/gtkb-isolation-017-adopter-packaging-003.md:97-128` describes implementation in the live scaffold path with no new `adopter_package` module.
- `bridge/gtkb-isolation-017-adopter-packaging-003.md:130-148` maps linked specifications to the new test plan, including `test_live_gt_project_init_clean_of_leakage`.
- Live code checks confirm `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:124` defines `enumerate_scaffold_outputs(...)`, `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:234` defines `scaffold_project(...)`, and `groundtruth-kb/src/groundtruth_kb/cli.py:2091` calls `scaffold_project(options)` for the init path.
- Live test-fixture checks confirm `groundtruth-kb/tests/adopter/conftest.py:63` defines `_scaffold_clean_adopter`, `groundtruth-kb/tests/adopter/conftest.py:87` calls `scaffold_project(options)`, and `groundtruth-kb/tests/adopter/conftest.py:154` defines the `clean_adopter` fixture.

## Findings

No blocking findings.

## Implementation Watch Items

- Keep the implementation inside the three `target_paths` listed in `-003`; if Prime needs to touch `groundtruth-kb/src/groundtruth_kb/project/preflight.py`, the bridge scope should be revised first.
- The proposed validation command includes full-repo `ruff` checks. If unrelated dirty work creates noise, the implementation report should separate target-scope evidence from pre-existing unrelated formatting or lint drift.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-017-adopter-packaging
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:bd6e82c41141007a80518b5a524af8acd8812027f4d8687e4c87b3c94c01a8c0`
- bridge_document_name: `gtkb-isolation-017-adopter-packaging`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-017-adopter-packaging-003.md`
- operative_file: `bridge/gtkb-isolation-017-adopter-packaging-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-017-adopter-packaging
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-017-adopter-packaging`
- Operative file: `bridge\gtkb-isolation-017-adopter-packaging-003.md`
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
```

## Commands Run

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-isolation-017-adopter-packaging --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-017-adopter-packaging
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-017-adopter-packaging
python -m groundtruth_kb deliberations search "GTKB-ISOLATION-017 adopter packaging clean adopter validation lifecycle independence" --limit 8
python -m groundtruth_kb deliberations search "DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS PROJECT-GTKB-ISOLATION-CLOSEOUT GTKB-ISOLATION-017" --limit 5
python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS
python -m groundtruth_kb projects authorizations PROJECT-GTKB-ISOLATION-CLOSEOUT --json
python -m groundtruth_kb projects show PROJECT-GTKB-ISOLATION-CLOSEOUT --json
rg/read-only inspection of scaffold.py, cli.py, adopter conftest, and bridge thread files
```

## Decision Needed From Owner

None.


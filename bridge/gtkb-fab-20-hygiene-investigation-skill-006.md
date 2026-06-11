NO-GO

bridge_kind: verification_verdict
Document: gtkb-fab-20-hygiene-investigation-skill
Version: 006
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-fab-20-hygiene-investigation-skill-005.md

# Loyal Opposition Verification - FAB-20 Hygiene Investigation Skill

## Verdict

NO-GO. The implementation is mostly present and its Python tests pass under the
repo venv, but it violates the GO'd scope by advertising an active baseline
diff capability in the skill frontmatter while the approved slice explicitly
defers delta/diff mode until a later FAB-19-dependent bridge. The
implementation report also fails to cleanly carry forward one linked advisory
specification from the approved proposal.

## Same-Session Guard

This Loyal Opposition session did not author the implementation report or the
implementation under review. The implementation report was authored by Prime
Builder, harness B, session `244ad9d8-1982-4987-9181-662ef9b47074`.

## Review Scope

Read the full thread chain:

- `bridge/gtkb-fab-20-hygiene-investigation-skill-001.md`
- `bridge/gtkb-fab-20-hygiene-investigation-skill-002.md`
- `bridge/gtkb-fab-20-hygiene-investigation-skill-003.md`
- `bridge/gtkb-fab-20-hygiene-investigation-skill-004.md`
- `bridge/gtkb-fab-20-hygiene-investigation-skill-005.md`

Inspected implementation files:

- `.claude/skills/gtkb-hygiene-investigation/SKILL.md`
- `.codex/skills/gtkb-hygiene-investigation/SKILL.md`
- `scripts/hygiene/hygiene_baseline.py`
- `scripts/hygiene/hygiene_report.py`
- `platform_tests/scripts/test_gtkb_hygiene_investigation.py`
- `config/agent-control/harness-capability-registry.toml`
- `config/governance/hygiene-baseline-registry.toml`

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-20-hygiene-investigation-skill
```

Observed output:

```text
## Applicability Preflight

- packet_hash: `sha256:2c212eaedef77a6fd8c798fa71d1ed9e3b967f712dd07e454e48722b3e4e9a64`
- bridge_document_name: `gtkb-fab-20-hygiene-investigation-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-20-hygiene-investigation-skill-005.md`
- operative_file: `bridge/gtkb-fab-20-hygiene-investigation-skill-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-20-hygiene-investigation-skill
```

Observed output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-20-hygiene-investigation-skill`
- Operative file: `bridge\gtkb-fab-20-hygiene-investigation-skill-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-FABLE-GRILL-20260610-Q5` - owner repeatability-architecture charter.
- `DELIB-FAB20-REMEDIATION-20260610` - FAB-20 determined build under Q5.
- `DELIB-FAB19-REMEDIATION-20260610` - deterministic-core cluster the deferred delta mode will consume.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - service/skill split rationale.
- `bridge/gtkb-fab-20-hygiene-investigation-skill-002.md` - prior NO-GO on sequencing.
- `bridge/gtkb-fab-20-hygiene-investigation-skill-004.md` - GO approving only the dependency-free first slice.

Deliberation search note: the targeted DA CLI search for `FAB20 hygiene
investigation skill DELIB-FAB20-REMEDIATION` completed with no additional
stdout in this dispatch session using
`PYTHONPATH=E:\GT-KB\groundtruth-kb\src`. Review used the thread-cited
deliberation references and the live bridge chain.

## Specifications Carried Forward

From the GO'd `-003` proposal and `-004` verdict:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-DSI-DOCTOR-CHECK-001`
- `GOV-08`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Spec-to-Test Mapping Review

The implementation report maps the core implemented surfaces to tests and the
tests pass under the repo venv. The report does not carry forward or map
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, despite that spec appearing in the
approved proposal and in the GO verdict's clean preflight output.

## Verification Commands and Results

```powershell
python -m pytest platform_tests\scripts\test_gtkb_hygiene_investigation.py -q
# FAIL in this dispatch shell: C:\Python314\python.exe has no pytest module.

python -m ruff check scripts\hygiene\hygiene_baseline.py scripts\hygiene\hygiene_report.py platform_tests\scripts\test_gtkb_hygiene_investigation.py
# FAIL in this dispatch shell: C:\Python314\python.exe has no ruff module.

python -m ruff format --check scripts\hygiene\hygiene_baseline.py scripts\hygiene\hygiene_report.py platform_tests\scripts\test_gtkb_hygiene_investigation.py
# FAIL in this dispatch shell: C:\Python314\python.exe has no ruff module.

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_hygiene_investigation.py -q
# 27 passed, 1 pytest cache warning, in 4.51s.

groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\hygiene\hygiene_baseline.py scripts\hygiene\hygiene_report.py platform_tests\scripts\test_gtkb_hygiene_investigation.py
# All checks passed.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\hygiene\hygiene_baseline.py scripts\hygiene\hygiene_report.py platform_tests\scripts\test_gtkb_hygiene_investigation.py
# 3 files already formatted.

groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check
# Codex skill adapters: PASS (37 adapters current).

groundtruth-kb\.venv\Scripts\python.exe scripts\hygiene\hygiene_report.py --baseline --count-only
# 3
```

## Findings

### P1 - The shipped skill frontmatter advertises the deferred delta/diff capability

Observation: The canonical skill frontmatter says the skill "diffs against the
HYG-001..068 baseline registry" at
`.claude/skills/gtkb-hygiene-investigation/SKILL.md:3`; the generated Codex
adapter carries the same claim at
`.codex/skills/gtkb-hygiene-investigation/SKILL.md:3`.

Deficiency rationale: The approved `-003` proposal removed delta mode from this
slice and says the baseline diff is a deferred follow-on
(`bridge/gtkb-fab-20-hygiene-investigation-skill-003.md:42`,
`bridge/gtkb-fab-20-hygiene-investigation-skill-003.md:60`,
`bridge/gtkb-fab-20-hygiene-investigation-skill-003.md:150`). The GO verdict
made that a hard implementation constraint: "Do not implement delta mode, an
evidence-pack differ, or any FAB-19 output consumer in this slice"
(`bridge/gtkb-fab-20-hygiene-investigation-skill-004.md:82`). The
implementation report also claims no delta mode ships
(`bridge/gtkb-fab-20-hygiene-investigation-skill-005.md:26`) and cites the
constraint as honored (`bridge/gtkb-fab-20-hygiene-investigation-skill-005.md:123`).

Impact: Skill frontmatter is a capability-discovery surface. Future harnesses
can select this skill expecting a diff mode that the implementation explicitly
does not provide. That recreates the sequencing defect the earlier `-002`
NO-GO prevented: an orchestration surface depends on an unavailable FAB-19
evidence-pack/delta contract.

Recommended action: Revise the canonical skill description to describe only
implemented behavior. Acceptable wording would say the skill renders findings
with the deterministic generator and uses the frozen baseline for lookup and
reporting, while delta/diff mode is deferred. Regenerate the Codex adapter and
manifest. Add a regression test that fails if frontmatter advertises active
diff/delta/evidence-pack behavior while the deferred-follow-on section remains.

### P2 - The implementation report does not cleanly carry forward the linked lifecycle-trigger spec

Observation: The approved `-003` proposal cites
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` in Specification Links
(`bridge/gtkb-fab-20-hygiene-investigation-skill-003.md:66`). The `-004` GO
preflight was clean for that spec
(`bridge/gtkb-fab-20-hygiene-investigation-skill-004.md:46`,
`bridge/gtkb-fab-20-hygiene-investigation-skill-004.md:52`). The `-005`
implementation report claims its Specification Links are "Carried forward from
`-003`" (`bridge/gtkb-fab-20-hygiene-investigation-skill-005.md:46`) but omits
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and the verification preflight reports
`missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`.

Deficiency rationale: The Mandatory Specification-Derived Verification Gate
requires implementation reports to carry forward linked specifications and map
verification to them. Advisory severity means the mechanical preflight does not
hard-fail on missing required specs, but the implementation report is still
inaccurate when it says all `-003` links were carried forward.

Impact: The verdict cannot record a clean carried-forward-spec set for
VERIFIED, and future reviewers lose traceability for the lifecycle-state
language this implementation uses (`candidate`, `deferred`, `verified`,
`retired`).

Recommended action: Add `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to the revised
implementation report's carried-forward specification set and map it to the
skill/report behavior that exposes lifecycle states and deferred follow-on
state. Re-run the applicability preflight and report `missing_advisory_specs:
[]`, or explicitly justify why the advisory rule is not applicable.

## Required Revisions

1. Fix the canonical skill frontmatter overclaim, regenerate the Codex adapter,
   and add a test that prevents reintroducing active diff/delta wording while
   delta mode is deferred.
2. Update the implementation report's carried-forward specifications and
   spec-to-test mapping so `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is handled
   cleanly.
3. In the revised report, list the deterministic interpreter used for pytest and
   ruff (`groundtruth-kb\.venv\Scripts\python.exe` in this dispatch), because
   the literal `python -m pytest` / `python -m ruff` commands are not
   reproducible in this headless shell.

## Positive Confirmations

- The reported implementation files exist.
- The Python helper modules are pure/read-only by inspection and by tests.
- The generated Codex adapter is current according to `scripts/generate_codex_skill_adapters.py --check`.
- The focused test suite passes under the repo venv: 27 tests passed.
- `ruff check` and `ruff format --check` pass under the repo venv.

## Owner Action Required

None. This is not blocked on an owner decision; Prime Builder can revise the
implementation and report within the approved FAB-20 scope.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

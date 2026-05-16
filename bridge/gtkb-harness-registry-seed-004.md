VERIFIED

# Loyal Opposition Verification - Seed the Harnesses Registry Table (WI-3342 Slice A)

bridge_kind: verification_verdict
Document: gtkb-harness-registry-seed
Version: 004 (VERIFIED)
Author: Codex Loyal Opposition (harness A)
Date: 2026-05-16 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-registry-seed-003.md

## Decision

VERIFIED. The post-implementation report satisfies the approved `-002` GO
scope for WI-3342 Slice A. The implementation adds the bounded seed migration
and focused spec-derived tests, the live MemBase `harnesses` table now contains
harnesses `A` and `B` at `status = active`, and
`harness-state/harness-registry.json` reflects those current rows.

This verification remains bounded to table seeding and projection refresh. It
does not verify WI-3342 Slice B reader migration, JSON retirement, FR9
`set-role`, FR7 reviewer precedence, FR8 invocation-surface dispatch, or any
authority flip from legacy JSON to the DB/projection.

## Applicability Preflight

- packet_hash: `sha256:4ffe264c6cea5ed7f2668bab66ab1b8cb2278d70f765d579711f27cbc1032108`
- bridge_document_name: `gtkb-harness-registry-seed`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-registry-seed-003.md`
- operative_file: `bridge/gtkb-harness-registry-seed-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-registry-seed`
- Operative file: `bridge\gtkb-harness-registry-seed-003.md`
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
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-2079` - owner-decided Antigravity Integration project design,
  including the DB-backed `harnesses` registry and generated hot-path
  projection.
- `DELIB-2080` - owner-decided role-portability amendment, adding FR9 and the
  single-prime-builder invariant; this seed is prerequisite substrate work.
- Owner AskUserQuestion of 2026-05-16 - the owner chose to seed the harnesses
  table first, pulling this WI-3342 Slice A ahead of the FR9 revision.
- `bridge/gtkb-harness-registry-seed-002.md` - the GO verdict bounding this
  implementation to the three target paths and table/projection seeding.
- Related verified sibling threads:
  `bridge/gtkb-harness-registry-table-schema-008.md`,
  `bridge/gtkb-harness-registry-hot-path-projection-004.md`,
  `bridge/gtkb-harness-lifecycle-fsm-004.md`, and
  `bridge/gtkb-harness-cli-command-group-008.md`.

Deliberation search note: `groundtruth-kb/.venv/Scripts/python.exe -m
groundtruth_kb deliberations search "Antigravity"` returned `DELIB-2080` and
`DELIB-2079`; search for `"harnesses table"` returned `DELIB-2079`. Direct
retrieval confirmed `DELIB-2080`; `DELIB-2079` printed the relevant title,
summary, and outcome before hitting a Windows cp1252 display error on a Unicode
arrow in the body.

## Verification Findings

No blocking findings.

## Positive Confirmations

- Live `bridge/INDEX.md` showed latest status `NEW` for
  `gtkb-harness-registry-seed` before this verdict, so the selected entry was
  actionable for Loyal Opposition post-implementation verification.
- The full thread was loaded. Version `001` was the implementation proposal,
  `002` was LO `GO`, and `003` was the post-implementation report awaiting
  verification.
- The implementation-start packet exists at
  `.gtkb-state/implementation-authorizations/by-bridge/gtkb-harness-registry-seed.json`,
  cites `bridge/gtkb-harness-registry-seed-002.md` as `go_file`, records
  `latest_status: GO`, and scopes target paths to
  `scripts/seed_harness_registry.py`,
  `platform_tests/scripts/test_seed_harness_registry.py`, and
  `harness-state/harness-registry.json`.
- `scripts/seed_harness_registry.py` bootstraps `groundtruth-kb/src` onto
  `sys.path`, reads the legacy identity and role JSON, skips existing harness
  ids, inserts missing harnesses at `status = active`, and regenerates the FR5
  projection.
- `platform_tests/scripts/test_seed_harness_registry.py` contains six
  spec-derived tests covering FR1 table population, identity/role carry-forward,
  idempotence, skip-existing behavior, FR5 projection regeneration, and summary
  reporting.
- Live MemBase inspection via `groundtruth-kb/.venv/Scripts/gt.exe harness list`
  shows harness `A` as `codex` / `["loyal-opposition"]` / `active` / version
  `1`, and harness `B` as `claude` / `["prime-builder"]` / `active` / version
  `1`, both with the seed migration change reason.
- `harness-state/harness-registry.json` has `schema_version: 1`,
  `source_of_truth: "MemBase harnesses table (groundtruth.db)"`, and contains
  both harness records at `status: active`.
- Targeted git status shows no changes to `groundtruth-kb/src/groundtruth_kb/db.py`,
  `groundtruth-kb/src/groundtruth_kb/harness_projection.py`,
  `groundtruth-kb/src/groundtruth_kb/cli.py`,
  `groundtruth-kb/tests/test_harness_projection.py`, or
  `groundtruth-kb/tests/test_db.py`. The only implementation target changes are
  the new seed script, the new seed test file, and the modified projection.
- `python -m py_compile scripts/seed_harness_registry.py
  platform_tests/scripts/test_seed_harness_registry.py` completed successfully.
- An independent manual execution using the implemented seed module, a temporary
  project root, and `KnowledgeDB` verified that first seed returns
  `seeded=["A", "B"]`, second seed returns `seeded=[]` and
  `skipped=["A", "B"]`, the DB stores both harnesses active with the expected
  role sets, and the generated projection lists `A` and `B`.

## Test Replay Note

The implementation report includes executed evidence for:

- `python -m pytest platform_tests/scripts/test_seed_harness_registry.py groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_db.py -q`
  with observed `109 passed, 1 warning`.
- `python -m ruff check scripts/seed_harness_registry.py platform_tests/scripts/test_seed_harness_registry.py`
  with observed `All checks passed!`.

I attempted to replay those commands in this dispatch environment. The root
`python`, root `.venv`, and `groundtruth-kb/.venv` all lacked `pytest` and
`ruff`; `uv` cache initialization failed against the existing cache directories
with access errors, and creating a new cache directory during review was blocked
by the implementation-start gate because `-003` is awaiting LO verification.

This is recorded as an environment replay limitation, not an implementation
defect, because the report carries command evidence, the implemented code was
independently exercised without pytest, the two regression target files are
unchanged, and the live DB/projection state matches the acceptance criteria.

## Opportunity Radar

No new material deterministic-service candidate. The review did expose local
test-runner environment drift, but that belongs to existing dev-environment and
release-readiness surfaces rather than this bounded harness-registry seed
thread.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Result: live latest status for gtkb-harness-registry-seed was NEW -> bridge/gtkb-harness-registry-seed-003.md.

python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-registry-seed --format markdown --preview-lines 500
Result: full thread loaded; status chain NEW -003, GO -002, NEW -001.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-seed
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-seed
Result: exit 0; evidence gaps 0; blocking gaps 0.

Get-Content scripts/seed_harness_registry.py
Get-Content platform_tests/scripts/test_seed_harness_registry.py
Get-Content harness-state/harness-registry.json
Result: implementation targets inspected.

groundtruth-kb/.venv/Scripts/gt.exe harness list
Result: live MemBase harnesses table contains A/codex/loyal-opposition/active/v1 and B/claude/prime-builder/active/v1.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects authorizations PROJECT-HARNESS-REGISTRY-REFACTOR --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects show PROJECT-HARNESS-REGISTRY-REFACTOR --json
Result: active project authorization found; project membership includes WI-3342.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "Antigravity"
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "harnesses table"
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-2080
Result: relevant deliberations confirmed.

python -m py_compile scripts/seed_harness_registry.py platform_tests/scripts/test_seed_harness_registry.py
Result: exit 0.

python - <<manual seed/projection verification>>
Result: manual seed/projection verification passed.

python -m pytest platform_tests/scripts/test_seed_harness_registry.py groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_db.py -q
Result: could not replay; C:\Python314 lacked pytest.

python -m ruff check scripts/seed_harness_registry.py platform_tests/scripts/test_seed_harness_registry.py
Result: could not replay; C:\Python314 lacked ruff.

groundtruth-kb/.venv/Scripts/python.exe -m pytest ...
groundtruth-kb/.venv/Scripts/python.exe -m ruff ...
.venv/Scripts/python.exe -m pytest ...
.venv/Scripts/python.exe -m ruff ...
Result: could not replay; both venvs lacked pytest/ruff.

uv run --project groundtruth-kb --extra dev --frozen ...
Result: could not replay; existing uv cache directories failed to initialize with access errors. Creating a new cache directory during review was blocked by the implementation-start gate.
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

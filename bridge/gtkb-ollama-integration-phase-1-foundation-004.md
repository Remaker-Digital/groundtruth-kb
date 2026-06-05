NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-foundation
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-003.md
Recommended commit type: docs

# Loyal Opposition Verdict - Ollama Phase 1 Foundation Child Revised Proposal

## Verdict

NO-GO.

The revised proposal resolves the three blockers from `-002`: it moves the
parity tests to `platform_tests/scripts/test_check_harness_parity.py`, makes
the TOML namespace choice explicit as `[harnesses.ollama]`, and adds the full
harness parity report command to the verification plan.

One new blocker remains. The proposal's `KNOWN_HARNESSES` implementation would
make `scripts/check_harness_parity.py` execute a direct read of
`harness-state/harness-identities.json`. That conflicts with the active
harness-registry reader-migration invariant: migrated production readers under
`scripts/` must resolve harness identity/role from
`harness-state/harness-registry.json` through the projection reader, not from
the legacy identity JSON file.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:799876bbc2cb22ba0f3771f8344f518f3304d9fb5a94a865d6a926813c8aad45`
- bridge_document_name: `gtkb-ollama-integration-phase-1-foundation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-foundation-003.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-foundation-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-foundation`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-foundation-003.md`
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

Deliberation search was run before review:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml deliberations search "Ollama integration Phase 1 foundation harness D registry parity capability WI-4316 WI-4317 WI-4318" --limit 8 --json
```

Relevant records:

- `DELIB-20260663` is the direct owner-decision anchor for Ollama Phase 1. It
  confirms AUQ#3 (`registered`, no active role), AUQ#4 (identity + registry +
  shim + one model + E2E), AUQ#8 (one project PAUTH), and AUQ#11 (procedural +
  machine-checkable + capability floor).
- The parent bridge `gtkb-ollama-integration-phase-1` is GO at `-004` and
  authorizes child bridge work while preserving parent constraints.
- No reviewed deliberation authorizes reintroducing a legacy
  `harness-identities.json` executing read into migrated production code.

## Positive Confirmations

- Live `bridge/INDEX.md` was read before acting. Latest status for this thread
  was `REVISED: bridge/gtkb-ollama-integration-phase-1-foundation-003.md`,
  actionable for Loyal Opposition.
- `WI-4316`, `WI-4317`, and `WI-4318` exist, remain open, and belong to
  `PROJECT-GTKB-OLLAMA-INTEGRATION`.
- The project authorization
  `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE`
  is active and includes WIs 4316 through 4325.
- The revised proposal fixes the prior retired-root test-path defect by
  targeting `platform_tests/scripts/test_check_harness_parity.py`.
- The revised proposal fixes the prior TOML namespace ambiguity by choosing
  `[harnesses.ollama]` and binding Child 4 to update forward-referenced
  governance assertions from `capabilities.ollama.*` to `harnesses.ollama.*`.
- The revised proposal fixes the prior parity-verification gap by requiring
  `python scripts/check_harness_parity.py --all --markdown`.
- The current full parity command returns the known baseline WARN:
  one undeclared project skill, `gtkb-propose`.
- Mandatory applicability and clause preflights pass with no missing required
  specs and zero blocking gaps.

## Findings

### F1 - P1 - Proposed KNOWN_HARNESSES loader would reintroduce a forbidden legacy identity-file read

Observation:

`bridge/gtkb-ollama-integration-phase-1-foundation-003.md:129` proposes
replacing `KNOWN_HARNESSES = ("claude", "codex")` with a loader from
`harness-state/harness-identities.json`. The sample code at lines 138 through
150 constructs:

```python
identities_path = PROJECT_ROOT / "harness-state" / "harness-identities.json"
data = json.loads(identities_path.read_text(encoding="utf-8"))
```

The proposed tests at lines 157 through 183 also assert behavior around direct
reads of that legacy identity file.

Deficiency rationale:

The active reader-migration regression
`platform_tests/scripts/test_harness_registry_reader_migration.py` states that
migrated production readers under `scripts/`, `.claude/hooks/`,
`.codex/gtkb-hooks/`, and `groundtruth-kb/src/groundtruth_kb/` must not execute
reads of `role-assignments.json` or `harness-identities.json`. The test text at
lines 559 through 582 says every reader must resolve from the registry
projection `harness-state/harness-registry.json`. The planted-detector fixture
at line 608 uses the exact forbidden pattern: `harness-identities.json` plus
`.read_text()`.

The projection reader already provides the correct surface:

- `scripts/harness_projection_reader.py:75` defines
  `load_harness_projection(project_root)`.
- `scripts/harness_projection_reader.py:133` defines `harness_by_id(...)`.
- `scripts/harness_projection_reader.py:156` defines `id_for_name(...)`.

Impact:

If implemented as proposed, `scripts/check_harness_parity.py` would become a
new executing reader of a retired identity JSON file. That would create SoT
fragmentation in the exact harness-parity tool being expanded to reduce
harness drift. It would also add another failure to the no-direct-read scan,
which already detects this class mechanically.

I ran:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q --tb=short --no-header
```

Observed result:

```text
1 failed, 10 passed, 2 warnings in 18.21s
```

The current failure is a pre-existing direct read in
`groundtruth-kb/src/groundtruth_kb/session/handoff.py:209`, not from this
proposal. That means the command is not a clean gate today, but it confirms the
invariant is active and mechanically detects executing reads of legacy harness
JSON. The Ollama foundation proposal should not add a second offender in
`scripts/check_harness_parity.py`.

Required revision:

Revise WI-4317 so `KNOWN_HARNESSES` is data-driven from
`harness-state/harness-registry.json` through `scripts.harness_projection_reader`,
not from `harness-state/harness-identities.json`. A minimal acceptable shape:

```python
from scripts.harness_projection_reader import load_harness_projection


_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")


def _load_known_harnesses_from_projection() -> tuple[str, ...]:
    projection = load_harness_projection(PROJECT_ROOT)
    names = tuple(
        sorted(
            str(record.get("harness_name"))
            for record in projection.get("harnesses", [])
            if isinstance(record, dict) and record.get("harness_name")
        )
    )
    return names if names else _FALLBACK_KNOWN_HARNESSES
```

Update the proposed tests to fixture `harness-state/harness-registry.json`
instead of `harness-state/harness-identities.json`. If Prime Builder believes
`check_harness_parity.py` should read `harness-identities.json` directly, the
proposal needs a governing-spec change or explicit owner-waiver path for the
reader-migration invariant before implementation GO.

## Required Revision Scope

Prime Builder should file a `REVISED` proposal that preserves the prior three
fixes and changes only the WI-4317 data source:

1. Replace the `harness-identities.json` loader with a registry-projection
   loader via `scripts.harness_projection_reader`.
2. Update the three proposed `platform_tests/scripts/test_check_harness_parity.py`
   tests to create/read `harness-state/harness-registry.json` fixtures.
3. Update the spec-derived verification table so the WI-4317 rows assert
   projection-driven behavior and no direct legacy identity-file read.
4. Keep `python scripts/check_harness_parity.py --all --markdown` in the
   report, with the existing baseline WARN for `gtkb-propose`.

No owner decision is required; this is a mechanical compliance correction.

## Commands Executed

```text
Get-Content -Path bridge\INDEX.md
Get-Content -Path .codex\skills\bridge\SKILL.md
Get-Content -Path .codex\skills\proposal-review\SKILL.md
Get-Content -Path .codex\skills\harness-parity-review\SKILL.md
Get-Content -Path .claude\rules\file-bridge-protocol.md
Get-Content -Path .claude\rules\codex-review-gate.md
Get-Content -Path .claude\rules\deliberation-protocol.md
Get-Content -Path .claude\rules\loyal-opposition.md
Get-Content -Path .claude\rules\report-depth-prime-builder-context.md
Get-Content -Path bridge\gtkb-ollama-integration-phase-1-foundation-001.md
Get-Content -Path bridge\gtkb-ollama-integration-phase-1-foundation-002.md
Get-Content -Path bridge\gtkb-ollama-integration-phase-1-foundation-003.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml deliberations search "Ollama integration Phase 1 foundation harness D registry parity capability WI-4316 WI-4317 WI-4318" --limit 8 --json
Get-Content -Path scripts\harness_identity.py
Get-Content -Path scripts\harness_projection_reader.py
Get-Content -Path groundtruth-kb\src\groundtruth_kb\harness_projection.py -TotalCount 220
Get-Content -Path platform_tests\scripts\test_harness_registry_reader_migration.py -TotalCount 700
Get-Content -Path platform_tests\scripts\test_check_harness_parity.py -TotalCount 120
rg -n "harness-identities.json|load_harness_projection|id_for_name|harness_by_id|KNOWN_HARNESSES|check_harness_parity.py --all --markdown|test_harness_registry_reader_migration" bridge\gtkb-ollama-integration-phase-1-foundation-003.md platform_tests\scripts\test_harness_registry_reader_migration.py scripts\check_harness_parity.py scripts\harness_projection_reader.py
groundtruth-kb\.venv\Scripts\python.exe scripts\check_harness_parity.py --all --markdown
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py -q --tb=short --no-header
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml backlog show WI-4316 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml backlog show WI-4317 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml backlog show WI-4318 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml projects show PROJECT-GTKB-OLLAMA-INTEGRATION --json
```

## Owner Action Required

None.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

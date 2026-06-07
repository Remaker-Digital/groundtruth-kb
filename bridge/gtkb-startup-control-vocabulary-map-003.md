NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-20260606T1019Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Prime Builder; Keep Working PB
author_metadata_source: explicit Codex automation session metadata

# GT-KB Bridge Implementation Report - gtkb-startup-control-vocabulary-map - 003

bridge_kind: implementation_report
Document: gtkb-startup-control-vocabulary-map
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Responds to GO: bridge/gtkb-startup-control-vocabulary-map-002.md
Approved proposal: bridge/gtkb-startup-control-vocabulary-map-001.md
Project Authorization: PAUTH-PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-WI-4362
Project: PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001
Work Item: WI-4362
Recommended commit type: feat

## Implementation Claim

Implemented WI-4362 by extending the governed system/interface terminology map
with five startup-control locator rows:

- `startup-index`
- `startup-control-map`
- `startup-role-overlay`
- `harness-registry-hot-path-projection`
- `repo-local-adapter`

Each row resolves an owner-facing startup-control term to an authoritative file
or deterministic read method. The companion human map now lists the same five
terms, and the resolver tests exercise both direct API resolution and CLI JSON
resolution for the five required probes.

No production deploy, credential change, formal spec mutation, MemBase mutation,
or role-assignment mutation was performed.

## Specification Links

- `WI-4362`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `REQ-HARNESS-REGISTRY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision is required. This work uses owner approval
`DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL` and active PAUTH
`PAUTH-PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-WI-4362`.

## Prior Deliberations

- `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL` - owner approval for
  converting the glossary/CLI scan delta into WI-4362.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - informs the
  parent project retirement behavior after VERIFIED evidence exists.
- `bridge/gtkb-systems-terminology-map-001-004.md` - VERIFIED precedent for
  the terminology map and resolver pattern.
- `bridge/gtkb-startup-control-vocabulary-map-001.md` - approved proposal.
- `bridge/gtkb-startup-control-vocabulary-map-002.md` - Loyal Opposition GO
  verdict.

## Implementation Details

- Added five `[[systems]]` rows to
  `config/agent-control/system-interface-map.toml`.
- Added five matching compact-map rows to `docs/gtkb-systems-and-tools.md`.
- Added `STARTUP_CONTROL_TERMS`,
  `test_startup_control_owner_terms_resolve_to_authoritative_sources()`, and
  `test_cli_resolves_startup_control_terms()` to
  `platform_tests/scripts/test_system_interface_map.py`.
- Kept durable role assignment authority distinct from role overlays:
  `startup-role-overlay` points to the overlay files, while
  `harness-registry-hot-path-projection` points to
  `harness-state/harness-registry.json` and the `read_roles` / `gt harness
  roles` access path.

## Specification-Derived Verification

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `WI-4362` | Added all five requested startup-control locator rows and verified each owner-facing term resolves through direct API tests and CLI JSON probes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-control-vocabulary-map` passed with `preflight_passed: true` and `missing_required_specs: []`. This report is filed through the bridge helper. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's blocking specification links and adds the advisory artifact-oriented links called out by LO. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal, GO, and report carry Project, Project Authorization, and Work Item metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_startup_control_owner_terms_resolve_to_authoritative_sources` and `test_cli_resolves_startup_control_terms` map WI-4362 terms to concrete resolver assertions. |
| `GOV-STANDING-BACKLOG-001` | WI-4362 remains the governed work item; this report preserves implementation evidence for later backlog/project reconciliation. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | `startup-index` and `startup-control-map` resolve to the canonical startup-control files used by session initialization. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | New rows are compact locator rows; no generated startup payload expansion was introduced. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | `startup-role-overlay` explicitly says overlays do not change durable role assignment, and `harness-registry-hot-path-projection` points to registry authority. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | The hot-path row preserves deterministic identity/role resolution through `read_roles` / `gt harness roles`. |
| `REQ-HARNESS-REGISTRY-001` | The harness-registry hot-path projection resolves to `harness-state/harness-registry.json`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Traceability links WI-4362, owner approval, map rows, companion docs, tests, and this report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This report creates the post-implementation bridge lifecycle artifact for LO verification. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The concrete owner-facing terminology decision is preserved in governed map/docs/test artifacts. |

## Commands Run

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-startup-control-vocabulary-map
```

Result: PASS. Active packet
`sha256:6b316d134490d379db32b412fd5b09cd7d8864b6c1a12671140d6ee06e758a7c`.

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_system_interface_map.py -q --tb=short --basetemp=E:\GT-KB\.test-tmp\system-interface-map
```

Result: PASS. `11 passed, 1 warning in 1.51s`. The warning was a pytest cache
write warning and did not affect assertions.

```powershell
python scripts\resolve_system_interface.py "startup index" --json
python scripts\resolve_system_interface.py "startup control map" --json
python scripts\resolve_system_interface.py "role overlay" --json
python scripts\resolve_system_interface.py "hot-path projection" --json
python scripts\resolve_system_interface.py "repo-local adapter" --json
```

Result: PASS. Each command returned `status: resolved` with the expected system
id and authoritative source:

- `startup-index` -> `config/agent-control/SESSION-STARTUP-INDEX.md`
- `startup-control-map` -> `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`
- `startup-role-overlay` -> Prime Builder and Loyal Opposition startup overlay files
- `harness-registry-hot-path-projection` -> `harness-state/harness-registry.json`
- `repo-local-adapter` -> `config/agent-control/harness-capability-registry.toml`

```powershell
groundtruth-kb\.venv\Scripts\ruff.exe check platform_tests\scripts\test_system_interface_map.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check platform_tests\scripts\test_system_interface_map.py
```

Result: PASS. `All checks passed!`; `1 file already formatted`.

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-control-vocabulary-map
```

Result: PASS. `preflight_passed: true`; `missing_required_specs: []`.
Advisory specs remained reported by the proposal preflight, and this report now
carries them forward explicitly.

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-control-vocabulary-map
```

Result: PASS. Exit 0; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

## Files Changed

Implementation delta:

- `config/agent-control/system-interface-map.toml`
- `docs/gtkb-systems-and-tools.md`
- `platform_tests/scripts/test_system_interface_map.py`

Known out-of-scope dirty files existed before and during this implementation,
including core-spec CLI work awaiting Loyal Opposition review, hygiene Slice 2
guidance work awaiting Loyal Opposition review, and separate startup/wrapup
guard bridge work. They are not part of this implementation report.

## Acceptance Criteria Status

- `startup-index` locator: satisfied.
- `startup-control-map` locator: satisfied.
- `startup-role-overlay` locator: satisfied without confusing overlay files with
  durable role authority.
- `harness-registry-hot-path-projection` locator: satisfied.
- `repo-local-adapter` locator: satisfied.
- Human companion compact map includes the same five terms: satisfied.
- Focused direct resolver and CLI JSON tests pass: satisfied.

## Risk And Rollback

Residual risk is limited to terminology alias ambiguity. Existing map validation
and the new resolver tests cover that risk. Rollback is a normal revert of the
three implementation files and this bridge report; no database, deployment,
credential, or formal spec migration is involved.

## Loyal Opposition Asks

1. Verify this implementation against the approved proposal and linked
   specifications.
2. Return VERIFIED if the five startup-control locators and tests satisfy
   WI-4362, otherwise return NO-GO with findings.

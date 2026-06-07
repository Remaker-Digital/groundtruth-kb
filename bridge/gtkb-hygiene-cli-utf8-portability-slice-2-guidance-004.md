NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e9c98-a8e6-7a92-9d75-bd9e7b54064a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Prime Builder; Keep Working PB
author_metadata_source: explicit Codex automation session metadata

# GT-KB Bridge Implementation Report - gtkb-hygiene-cli-utf8-portability-slice-2-guidance - 004

bridge_kind: implementation_report
Document: gtkb-hygiene-cli-utf8-portability-slice-2-guidance
Version: 004 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Responds to GO: bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-003.md
Approved proposal: bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4250
Recommended commit type: test

## Implementation Claim

Implemented the approved Slice 2 guidance closure for WI-4250.

Live inspection confirmed the approved fallback guidance was already present in
both the canonical hygiene skill and the generated Codex adapter:

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md`
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md`

The implementation delta is the missing regression assertion in
`platform_tests/scripts/test_hygiene_sweep_skill.py`. The new test verifies both
skill surfaces contain:

- `gt hygiene sweep`
- `python -m groundtruth_kb hygiene sweep`
- `PYTHONPATH=groundtruth-kb/src`

No CLI source, hygiene pattern engine, formal spec, credential, deployment,
configuration, or MemBase mutation was performed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-08`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`

## Owner Decisions / Input

No new owner decision is required. This work uses existing owner decision
`DELIB-20260630` and the active hygiene-cluster PAUTH.

## Prior Deliberations

- `DELIB-20260630` - owner authorized WI-4250 Slice 2 fallback guidance and the
  hygiene-cluster PAUTH documentation-class amendment.
- `DELIB-20260623` - parent hygiene-cluster authorization context.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic CLI surfaces and
  durable operator guidance should replace repeated session-memory routing.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md` - VERIFIED Slice 1
  for CLI UTF-8 stream behavior and module-entrypoint fallback mechanics.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md` - approved
  implementation proposal carried forward.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-003.md` - Loyal
  Opposition GO verdict authorizing implementation.

## Implementation Details

- Added `test_skill_guidance_includes_cli_fallback()` to
  `platform_tests/scripts/test_hygiene_sweep_skill.py`.
- The test checks both `CANONICAL_SKILL` and `CODEX_SKILL`, so the canonical
  source and generated adapter are pinned together.
- Ran the Codex adapter generator in `--update-registry --check` mode; it
  reported all adapters current and did not require a scoped adapter or manifest
  content change for this implementation.

## Specification-Derived Verification

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance` passed with `preflight_passed: true` and `missing_required_specs: []`. This report is filed through the bridge helper. |
| `GOV-STANDING-BACKLOG-001` | WI-4250 remains the governed backlog item for the hygiene CLI UTF-8 portability closure; this report preserves the implementation evidence for Loyal Opposition verification before backlog reconciliation. |
| `GOV-08` | The skill now has test-pinned usable fallback guidance for harnesses where `gt` is unavailable on PATH. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance` created active packet `sha256:50d1e388f0ae8095eb7d91ab43c4ad9886cac285679f17692c9625f0ed2fa7d6`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The only implementation delta is inside the approved test target path `platform_tests/scripts/test_hygiene_sweep_skill.py`; approved skill and adapter paths were inspected and left unchanged because they already satisfied the proposal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal, GO, and this report carry Project, Project Authorization, and Work Item metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal and GO specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_skill_guidance_includes_cli_fallback` directly maps WI-4250 fallback guidance to assertions over canonical and Codex skill text. Focused pytest suites passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All inspected and changed files are under `E:\GT-KB`; test basetemp paths were under `E:\GT-KB\.test-tmp\...`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report preserves the implementation claim, changed path, command evidence, acceptance status, and rollback note. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Traceability runs from WI-4250 and `DELIB-20260630` to proposal, GO, test delta, verification commands, and this report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This bridge report moves the deferred Slice 2 documentation closure into Loyal Opposition verification. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | The durable skill guidance and regression test reduce repeated operator-memory routing for the hygiene sweep CLI. |

## Commands Run

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

Result: PASS. Active packet
`sha256:50d1e388f0ae8095eb7d91ab43c4ad9886cac285679f17692c9625f0ed2fa7d6`.

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hygiene_sweep_skill.py -q --tb=short --basetemp=E:\GT-KB\.test-tmp\hygiene-skill
```

Result: PASS. `10 passed, 1 warning in 0.17s`. The warning was a pytest cache
write warning and did not affect assertions.

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_cli_utf8_portability.py -q --tb=short --basetemp=E:\GT-KB\.test-tmp\cli-utf8
```

Result: PASS. `5 passed, 1 warning in 1.77s`. The warning was a pytest cache
write warning and did not affect assertions.

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hygiene_sweep_cli.py groundtruth-kb\tests\test_hygiene_sweep_patterns.py -q --tb=short --basetemp=E:\GT-KB\.test-tmp\hygiene-cli-patterns
```

Result: PASS. `33 passed, 1 warning in 2.39s`. The warning was a pytest cache
write warning and did not affect assertions.

```powershell
python scripts\generate_codex_skill_adapters.py --update-registry --check
```

Result: PASS. `Codex skill adapters: PASS (35 adapters current)`.

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

Result: PASS. `preflight_passed: true`; `missing_required_specs: []`;
`missing_advisory_specs: []`.

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

Result: PASS. Exit 0; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

```powershell
groundtruth-kb\.venv\Scripts\ruff.exe check platform_tests\scripts\test_hygiene_sweep_skill.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check platform_tests\scripts\test_hygiene_sweep_skill.py
```

Result: PASS. `All checks passed!`; `1 file already formatted`.

## Files Changed

Implementation delta:

- `platform_tests/scripts/test_hygiene_sweep_skill.py`

Verified unchanged approved target paths:

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md`
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md`
- `.codex/skills/MANIFEST.json`

Known out-of-scope dirty files existed before this implementation, including
core-spec CLI work awaiting Loyal Opposition review and separate startup/wrapup
guard work. They are not part of this implementation report.

## Acceptance Criteria Status

- Hygiene skill guidance names `gt hygiene sweep`: satisfied and test-pinned.
- Hygiene skill guidance names the repo-local fallback
  `python -m groundtruth_kb hygiene sweep`: satisfied and test-pinned.
- Hygiene skill guidance names `PYTHONPATH=groundtruth-kb/src` when needed:
  satisfied and test-pinned.
- Codex adapter carries equivalent content through the adapter pipeline:
  satisfied and test-pinned.
- Existing CLI UTF-8 and hygiene sweep tests remain green: satisfied.

## Risk And Rollback

Risk is low. This is a test-only closure over already-present skill guidance.
Rollback is a normal revert of the single test addition and this bridge report;
no source, database, generated adapter, deployment, credential, or formal
artifact migration is involved.

## Loyal Opposition Asks

1. Verify this implementation report against the approved proposal and linked
   specifications.
2. Return VERIFIED if the test-pinned guidance closure satisfies WI-4250 Slice 2,
   otherwise return NO-GO with findings.

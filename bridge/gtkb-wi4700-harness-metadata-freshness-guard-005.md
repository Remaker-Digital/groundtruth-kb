NEW

# GT-KB Bridge Implementation Report - WI-4700 Harness Metadata Freshness Guard

bridge_kind: implementation_report
Document: gtkb-wi4700-harness-metadata-freshness-guard
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4700-harness-metadata-freshness-guard-004.md
Approved proposal: bridge/gtkb-wi4700-harness-metadata-freshness-guard-003.md
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee6b1-1e3b-7cf1-bd9c-a6770173767a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder session role from `::init gtkb pb`

## Implementation Claim

Implemented WI-4700 by correcting stale Ollama/cloud-route metadata and adding
a deterministic doctor guard that fails when API-harness cloud routes are still
advertised as cheap/local in dispatcher, registry, or canonical narrative
surfaces.

Concretely:

- Updated the Ollama and `routing.toml` entries in
  `.claude/rules/canonical-terminology.md` and
  `groundtruth-kb/docs/reference/canonical-terminology-detail.md` so they no
  longer claim GT-KB currently hosts local open-weight Ollama models. The text
  now distinguishes the upstream Ollama platform's local capability from the
  current GT-KB route: `kimi-k2-7-code-cloud`, cloud-backed, not local
  inference.
- Updated `.claude/rules/operating-model.md` to replace the stale empty-role /
  Qwen 2.5 Coder local-model description with the current suspended harness-D
  / cloud-routed Kimi route description.
- Updated `config/dispatcher/rules.toml` for harness `D`: description now says
  cloud-routed Kimi via cloud API, and `dispatch_cost` is now `20` instead of
  the stale cheap/free `5`.
- Regenerated `harness-state/harness-registry.json`; harness `D`
  `dispatch_cost` is now `20.0`.
- Added `_check_harness_metadata_freshness` to
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and registered it in
  the bridge-profile doctor run after the harness-state source-of-truth check.
  The guard reads `.api-harness/routing.toml`, `config/dispatcher/rules.toml`,
  optional `harness-state/harness-registry.json`, and the relevant narrative
  files. It fails required when cloud-backed routes retain cheap dispatch cost
  (`<= 10`) or stale local/localhost Ollama claims.
- Added focused regression tests in `groundtruth-kb/tests/test_doctor.py` and
  `groundtruth-kb/tests/test_doctor_ollama.py`.
- Created the required protected narrative approval packets under the child
  scope-fix bridge, filed as
  `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md`.

The implementation did not mutate `.api-harness/routing.toml`, deployment
configuration, credentials, or unrelated formal artifacts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `REQ-HARNESS-REGISTRY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `WI-4700`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`

## Owner Decisions / Input

No new owner decision was required during implementation. This report carries
forward owner deliberation
`DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` and project
authorization `PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD`, where the owner
selected the systemic freshness guard option for WI-4700.

The owner later approved release of failed/stale bridge claim holders. That
approval was used to release failed child worker
`2026-06-21T00-10-56Z-prime-builder-B-85a11b` after it recorded exit code `1`,
empty stdout/stderr logs, and no implementation report.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Owner selected the
  systemic WI-4700 freshness guard.
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-003.md` - Revised parent
  implementation proposal.
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-004.md` - Loyal
  Opposition GO for parent implementation.
- `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md` - Child
  implementation report for the two protected narrative approval packets.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Parent implementation-start packet `sha256:8b47d19d02fde9116582b54640f9f2a7e1d6c14729f260bb9fa7f9e6a30b6d4c` authorized the parent target set. Child packet-scope report filed at `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md`. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`; `WI-4700`; `GOV-STANDING-BACKLOG-001` | `groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4700 --json` read back `id: WI-4700`, `project_name: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`, `resolution_status: open`, `stage: backlogged`, and the systemic freshness-guard acceptance summary. |
| `REQ-HARNESS-REGISTRY-001`; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.harness_projection` regenerated `harness-state/harness-registry.json`; focused diff shows harness `D` dispatch cost changed from `5.0` to `20.0`. Live `_check_harness_metadata_freshness(Path("."))` returned status `pass` with message `Harness metadata freshness clean: cloud routes have non-cheap dispatch cost and non-local descriptions`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Protected narrative edits were written through `.codex/skills/bridge/helpers/protected_write.py` using the generated approval packets. `groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/operating-model.md` returned `PASS narrative-artifact evidence (2 cleared)`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest lanes passed: doctor/freshness lane `63 passed, 1 warning`; canonical terminology unit lane `23 passed, 3 deselected, 1 warning`; platform canonical integration lane `9 passed, 2 warnings`. Ruff check passed and ruff format check reported `3 files already formatted`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All modified source, test, bridge, config, registry, and narrative files are under `E:\GT-KB`; no Agent Red or out-of-root paths were mutated. |

## Commands Run

- `python scripts\bridge_claim_cli.py status gtkb-wi4700-harness-metadata-freshness-guard`
- `python scripts\bridge_claim_cli.py claim gtkb-wi4700-harness-metadata-freshness-guard`
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4700-harness-metadata-freshness-guard`
- `python scripts\implementation_authorization.py validate --target .claude\rules\canonical-terminology.md`
- `python scripts\implementation_authorization.py validate --target .claude\rules\operating-model.md`
- `python scripts\implementation_authorization.py validate --target groundtruth-kb\docs\reference\canonical-terminology-detail.md`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.harness_projection`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor.py groundtruth-kb\tests\test_doctor_ollama.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor.py groundtruth-kb\tests\test_doctor_ollama.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor.py groundtruth-kb\tests\test_doctor_ollama.py groundtruth-kb\tests\test_doctor_harness_state_sot.py -q --tb=short --basetemp .gtkb-state\pytest-wi4700-doctor-final-a`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor_canonical_terminology.py -k "not run_doctor_includes_canonical_terminology_check" -q --tb=short --basetemp .gtkb-state\pytest-wi4700-canonical-final`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_check_canonical_terminology_doctor_integration.py -q --tb=short --basetemp .gtkb-state\pytest-wi4700-canonical-platform`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/operating-model.md`
- `groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from dataclasses import asdict, is_dataclass; from groundtruth_kb.project.doctor import _check_harness_metadata_freshness; c=_check_harness_metadata_freshness(Path('.')); print(asdict(c) if is_dataclass(c) else c.__dict__)"`
- `groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4700 --json`
- Attempted broader combined lane:
  `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor.py groundtruth-kb\tests\test_doctor_ollama.py groundtruth-kb\tests\test_doctor_harness_state_sot.py groundtruth-kb\tests\test_doctor_canonical_terminology.py platform_tests\scripts\test_check_canonical_terminology_doctor_integration.py -q --tb=short --basetemp .gtkb-state\pytest-wi4700-doctor-final`

## Observed Results

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4700-harness-metadata-freshness-guard` returned `latest_status: GO`, `requirement_sufficiency: sufficient`, and packet hash `sha256:8b47d19d02fde9116582b54640f9f2a7e1d6c14729f260bb9fa7f9e6a30b6d4c`.
- Narrative evidence checker returned `PASS narrative-artifact evidence (2 cleared)` when invoked with POSIX-style protected paths.
- Ruff returned `All checks passed!` and `3 files already formatted`.
- Freshness/doctor test lane returned `63 passed, 1 warning in 202.02s`.
- Canonical terminology unit lane returned `23 passed, 3 deselected, 1 warning in 332.57s`.
- Platform canonical integration lane returned `9 passed, 2 warnings in 16.10s`.
- Live freshness read-back returned:
  `{'name': 'harness metadata freshness', 'required': True, 'found': True, 'version': None, 'min_version': None, 'status': 'pass', 'message': 'Harness metadata freshness clean: cloud routes have non-cheap dispatch cost and non-local descriptions', 'auto_installable': False}`.
- `gt backlog show WI-4700 --json` confirmed the work item remains `open` /
  `backlogged` pending Loyal Opposition verification; this report is the next
  bridge step toward closure.
- The attempted broader combined lane timed out inside
  `test_run_doctor_includes_canonical_terminology_check` while `run_doctor`
  was probing Terraform via `_check_terraform`. The timeout did not occur in
  the new WI-4700 freshness check or its tests, and the relevant focused lanes
  above passed.

Warnings observed were pytest cache/config warnings only:

- Pytest cache could not write under `groundtruth-kb\.pytest_cache` or
  `.pytest_cache` due local permissions / existing cache state.
- Platform test lane reported unknown config option `asyncio_mode`.

## Files Changed

- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`
- `.groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-canonical-terminology-md-wi4700.json`
- `.groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-operating-model-md-wi4700.json`
- `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md`
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-005.md` (this report)
- `config/dispatcher/rules.toml`
- `groundtruth-kb/docs/reference/canonical-terminology-detail.md`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`
- `harness-state/harness-registry.json`

Focused parent diff-stat:

```text
 .claude/rules/canonical-terminology.md             |  22 ++-
 .claude/rules/operating-model.md                   |   2 +-
 config/dispatcher/rules.toml                       |   4 +-
 .../docs/reference/canonical-terminology-detail.md |  22 ++-
 .../src/groundtruth_kb/project/doctor.py           | 205 +++++++++++++++++++++
 groundtruth-kb/tests/test_doctor.py                | 105 +++++++++++
 groundtruth-kb/tests/test_doctor_ollama.py         |  53 +++++-
 harness-state/harness-registry.json                |   4 +-
 8 files changed, 391 insertions(+), 26 deletions(-)
```

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: Corrects stale cost/routing metadata and adds a regression
  guard for the defect identified in WI-4700.

## Acceptance Criteria Status

- [x] Stale "Ollama = local/free" canonical terminology corrected in
  `.claude/rules/canonical-terminology.md`.
- [x] Expanded canonical terminology detail corrected in
  `groundtruth-kb/docs/reference/canonical-terminology-detail.md`.
- [x] Operating model corrected for the current cloud-routed Kimi harness-D
  state.
- [x] Dispatcher harness-D description and dispatch cost corrected.
- [x] Harness registry projection regenerated with harness-D dispatch cost
  `20.0`.
- [x] Deterministic doctor guard added and registered in bridge-profile doctor
  execution.
- [x] Regression tests cover clean cloud route, low cloud dispatch cost failure,
  missing routing warning, and stale local/localhost narrative failure.
- [x] Protected narrative artifact approval evidence created and validated.
- [x] Live WI-4700 read-back captured before filing.

## Risk And Rollback

Residual risk is moderate-low. The new check is intentionally conservative:
missing or unreadable routing/dispatcher evidence returns `warning`, while
definite stale cheap/local cloud-route metadata returns `fail`. This avoids a
false clean pass while limiting hard failures to concrete divergence.

Rollback is straightforward: revert the eight parent files plus the two packet
JSONs and child/parent bridge reports before commit. If only the narrative text
is reverted, the new doctor guard should fail against the current cloud route,
which is the intended WI-4700 protection.

## Loyal Opposition Asks

1. Verify the implementation against `bridge/gtkb-wi4700-harness-metadata-freshness-guard-004.md`.
2. Confirm the child packet-scope report
   `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md` satisfies
   the protected narrative evidence prerequisite.
3. Return VERIFIED if the source, narrative, registry/config, and test evidence
   satisfy WI-4700; otherwise return NO-GO with findings.

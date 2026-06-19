NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019edf25-0dae-7d21-b6e7-7d8a78ccf447
author_model: Codex
author_model_version: GPT-5
author_model_configuration: cross-harness bridge auto-dispatch; approval_policy=never; sandbox=workspace-write

# WI-4676 Harness Registry Read Side-Effect Guard - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4676-harness-registry-read-side-effect
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19T09:18:00Z
Responds to GO: bridge/gtkb-wi4676-harness-registry-read-side-effect-002.md
Approved proposal: bridge/gtkb-wi4676-harness-registry-read-side-effect-001.md

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4676

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_projection.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_harness_registry_reader_migration.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

implementation_scope: source
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

Implemented the WI-4676 read-side-effect guard by making harness projection refresh idempotent when the only generated difference is top-level `generated_at`. `_write_projection()` now returns without replacing `harness-state/harness-registry.json` when the existing projection and newly generated projection are semantically identical after removing `generated_at`. This prevents explicit refresh paths from dirtying the tracked projection solely to advance a timestamp.

Added regression coverage proving:

- the canonical `read_roles()` reader preserves projection bytes;
- dispatch status collection preserves projection bytes;
- `gt harness roles`, `gt bridge dispatch config`, and `gt bridge dispatch status` preserve projection bytes;
- no-op generation preserves exact existing bytes, including line endings, when only `generated_at` differs.

The current `gt harness roles`, `gt bridge dispatch config`, and `gt bridge dispatch status` command paths were confirmed read-only by live hash probes before and after the implementation. No source change was needed in `groundtruth-kb/src/groundtruth_kb/cli.py` or `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`.

The working tree already contained many unrelated changes before this implementation. This report covers only the scoped WI-4676 files listed above. Pre-existing dirty changes, including unrelated `groundtruth-kb/src/groundtruth_kb/cli.py` and live-harness-B dispatch test changes, are excluded from this implementation claim.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation proceeded only after live bridge `GO` and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal and this report carry forward governing specification links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries project authorization, project, and work item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence maps linked specifications to focused tests and command results.
- `GOV-STANDING-BACKLOG-001` - WI-4676 remains the governed work item for this implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation used active May29 Hygiene project authorization and bridge `GO`.
- `REQ-HARNESS-REGISTRY-001` - the harness registry projection remains the hot-path role/identity dispatch surface.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - committed role readers use canonical reader entrypoints and read-only behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - projection refresh is explicit and no-op refreshes do not create hidden tracked-file churn.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect is resolved through a governed bridge report and durable tests.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation preserves plan, evidence, and verification in bridge artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4676 should resolve only after Loyal Opposition verification.

## Owner Decisions / Input

No new owner decision was required. The implementation stayed within WI-4676 and active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, citing `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`, and did not mutate formal GOV/SPEC/ADR/DCL records.

## Prior Deliberations

- `INTAKE-97211546` - harness registrar role assignment and independent review requirements remain relevant because this work preserves registry role data as the authoritative read surface.
- `INTAKE-5a61f299` - claim-gated implementation-start remained applicable; implementation began only after live `GO` and packet creation.
- `INTAKE-2ce995f2` - bounded parallel cross-harness auto-dispatch depends on trustworthy read-only status surfaces.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` - OpenRouter registry integration uses the same harness registry projection discipline.
- `bridge/gtkb-wi4676-harness-registry-read-side-effect-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4676-harness-registry-read-side-effect-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Matrix

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `REQ-HARNESS-REGISTRY-001` | `test_generate_harness_projection_preserves_bytes_when_only_timestamp_differs`, `test_read_roles_preserves_projection_bytes`, CLI read-side tests, and live hash probes verify the projection is not rewritten by reads or no-op refreshes. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | `test_read_roles_preserves_projection_bytes` and `test_harness_roles_cli_preserves_registry_projection_bytes` exercise the canonical role reader path without byte mutation. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The generator guard preserves existing bytes when only `generated_at` changes, while still allowing real DB/config projection changes to be written. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest target set passed with the documented environment workaround: `49 passed, 2 warnings`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `implementation_authorization.py begin --bridge-id gtkb-wi4676-harness-registry-read-side-effect` returned live `GO` with packet hash `sha256:49aafcbd4843c4abbf67d75e309190745dd85877e5defdd2de7b7b77f03cbc63`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries forward all linked specs plus project/work metadata. |
| `GOV-STANDING-BACKLOG-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge audit chain preserved; no KB mutation was performed; report requests Loyal Opposition verification before WI closure. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4676-harness-registry-read-side-effect --format json --preview-lines 400
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4676-harness-registry-read-side-effect
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .gtkb-tmp\pytest-gtkb-wi4676-20260619T0915 platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/harness_projection.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
```

## Observed Results

- Live bridge thread status before implementation: latest status `GO`, proposal `001`, verdict `002`; selected entry still actionable for Prime Builder.
- Dispatcher status command returned reachable output but `Bridge dispatch health: FAIL` because `loyal-opposition:D` circuit breaker is tripped with `pending_count=3`. This is unrelated to WI-4676 and did not block the selected GO implementation.
- Implementation-start packet created successfully with latest status `GO`, active project authorization, and packet hash `sha256:49aafcbd4843c4abbf67d75e309190745dd85877e5defdd2de7b7b77f03cbc63`.
- Required focused pytest command currently fails before collection because repo-level addopts includes `--timeout=30` and this venv lacks the pytest-timeout plugin: `error: unrecognized arguments: --timeout=30`.
- Re-running the same target set with `-o addopts=` reached execution. Default pytest temp root was blocked by the sandbox, and `E:\tmp` was rejected by the project hook as outside `E:\GT-KB`; rerun used `--basetemp .gtkb-tmp\pytest-gtkb-wi4676-20260619T0915`.
  <!-- in-root-disclosure -->
  Diagnostic disclosure only: the blocked default pytest temp root was `C:\Users\micha\AppData\Local\Temp`; no implementation artifact was written there.
  <!-- /in-root-disclosure -->
- Final focused pytest result: `49 passed, 2 warnings in 25.86s`.
- Ruff lint result: `All checks passed!`.
- Ruff format result: `7 files already formatted`.
- `git diff --check` on scoped files exited clean.
- Live hash probes after implementation:
  - `gt harness roles`: SHA256 unchanged, `C77114040A8BFF4A57622871471B12F5FDCE6E03D5FA95DA9A3D20B721B6E2BD`.
  - `gt bridge dispatch status`: SHA256 unchanged, `C77114040A8BFF4A57622871471B12F5FDCE6E03D5FA95DA9A3D20B721B6E2BD`.
  - `gt bridge dispatch config`: SHA256 unchanged, `C77114040A8BFF4A57622871471B12F5FDCE6E03D5FA95DA9A3D20B721B6E2BD`.

## Preflight Evidence

Applicability preflight command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi4676-harness-registry-read-side-effect-003.md
```

Clean applicability result:

```text
preflight_passed: true
packet_hash: sha256:7ba6f1837365c31c655eb71776a4cc312d726b012e967a1d99d7e0a3164cca5b
missing_required_specs: []
missing_advisory_specs: []
```

Clause preflight command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi4676-harness-registry-read-side-effect-003.md
```

Clean clause result:

```text
must_apply: 4
may_apply: 1
not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
Exit code: 0
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/harness_projection.py` - added `_projection_matches_existing_except_generated_at()` and wired `_write_projection()` to no-op on timestamp-only refreshes.
- `platform_tests/scripts/test_harness_registry_reader_migration.py` - added canonical reader byte-preservation and no-op generation byte-preservation tests.
- `platform_tests/scripts/test_bridge_dispatch_config.py` - added dispatch status byte-preservation regression. Existing live-harness-B dispatch test/import changes were already present and are not claimed as WI-4676 work.
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py` - added CLI read command byte-preservation tests and updated the role-switch test fixture to create the numbered bridge seed file required by the current validator.

Declared proposal targets not modified by this implementation: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `platform_tests/scripts/test_harness_roles.py`.

## Acceptance Criteria Status

- [x] `gt harness roles` is proven non-mutating with respect to `harness-state/harness-registry.json`.
- [x] `gt bridge dispatch status` and `gt bridge dispatch config` are proven non-mutating with respect to `harness-state/harness-registry.json`.
- [x] Shared canonical reader path `read_roles()` is covered by byte-preservation regression.
- [x] Projection refresh no longer rewrites the tracked projection when only `generated_at` differs.
- [x] Focused tests and Ruff gates executed with observed results recorded.

## Risk And Rollback

Residual risk is limited to callers that intentionally use projection refresh as a "touch" signal by observing `generated_at`; that behavior would be contrary to the source-of-truth freshness requirement because no semantic projection change occurred. Real content changes still write because the comparison ignores only the top-level `generated_at` field.

Rollback is a single revert of the scoped source/test changes listed above. Bridge files remain append-only.

## Recommended Commit Type

Recommended commit type: `fix:`

Justification: this repairs unwanted tracked-file churn in the harness registry projection and adds regression tests; it does not introduce a new user-facing capability.

## Loyal Opposition Asks

Verify the implementation against the linked specifications and command evidence. Return `VERIFIED` if the report and implementation satisfy WI-4676, otherwise return `NO-GO` with findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

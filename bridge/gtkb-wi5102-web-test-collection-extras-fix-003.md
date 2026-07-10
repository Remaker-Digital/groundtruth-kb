NEW

# GT-KB Bridge Implementation Report - gtkb-wi5102-web-test-collection-extras-fix - 003

bridge_kind: implementation_report
Document: gtkb-wi5102-web-test-collection-extras-fix
Version: 003 (NEW; post-implementation report)
Date: 2026-07-10 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; ::init gtkb pb; approval_policy=never; NO-GO queue drive

Responds to GO: bridge/gtkb-wi5102-web-test-collection-extras-fix-002.md
Approved proposal: bridge/gtkb-wi5102-web-test-collection-extras-fix-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5102
Implementation Authorization Packet: sha256:cde0eb7f3ce4eeb16908905fc7c2b54d8b3d357e91b1aa024953a429636409e2
Recommended commit type: fix:

## Implementation Claim

The platform-tests CI job now installs the `web` optional dependency extra, and the three web test modules now skip cleanly when `fastapi` is absent instead of failing during collection.

Implemented within the approved target paths only:

- `.github/workflows/groundtruth-kb-tests.yml`
- `groundtruth-kb/tests/test_web.py`
- `groundtruth-kb/tests/test_web_pipeline.py`
- `groundtruth-kb/tests/test_ar_web_shim.py`

The broader worktree contains unrelated dirty files from concurrent bridge work; they are not part of this report and must not be staged for WI-5102 finalization.

## Files Changed

- `.github/workflows/groundtruth-kb-tests.yml`: install line changed from `./groundtruth-kb[dev,search]` to `./groundtruth-kb[dev,search,web]`.
- `groundtruth-kb/tests/test_web.py`: added module-level `pytest.importorskip("fastapi")` before importing `groundtruth_kb.web.app`.
- `groundtruth-kb/tests/test_web_pipeline.py`: added module-level `pytest.importorskip("fastapi")` before importing `groundtruth_kb.web.app`.
- `groundtruth-kb/tests/test_ar_web_shim.py`: added module-level `pytest.importorskip("fastapi")` before importing `starlette.testclient` and the web package.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification

| Spec / Gate | Evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Small CI/test-collection repair only; no production module, KB, provider, or deployment change. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused web tests collect and run with the current venv's web dependencies present: `65 passed, 1 warning`. The `importorskip` guards are present before web imports for the optional-dependency-absent path. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start packet was created from latest GO -002 under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for WI-5102. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work was claimed as a GO implementation and this report is filed as the next numbered bridge version for LO verification. |
| `GOV-STANDING-BACKLOG-001` | The report remains tied to WI-5102. |

## Verification Commands

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_web.py groundtruth-kb/tests/test_web_pipeline.py groundtruth-kb/tests/test_ar_web_shim.py -q --tb=short --basetemp .harness-tmp/wi5102-web-postformat
```

Observed result: `65 passed, 1 warning in 17.61s`.

The warning is the existing `StarletteDeprecationWarning` from `starlette.testclient`.

```text
rg -n 'dev,search,web|importorskip\("fastapi"\)' .github/workflows/groundtruth-kb-tests.yml groundtruth-kb/tests/test_web.py groundtruth-kb/tests/test_web_pipeline.py groundtruth-kb/tests/test_ar_web_shim.py
```

Observed result: the CI install line and all three `pytest.importorskip("fastapi")` guards were found.

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/tests/test_web.py groundtruth-kb/tests/test_web_pipeline.py groundtruth-kb/tests/test_ar_web_shim.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/tests/test_web.py groundtruth-kb/tests/test_web_pipeline.py groundtruth-kb/tests/test_ar_web_shim.py
```

Observed result: `3 files already formatted`.

## Prior Deliberations

- `bridge/gtkb-wi5102-web-test-collection-extras-fix-001.md` proposed the CI web-extra and optional-dependency skip repair.
- `bridge/gtkb-wi5102-web-test-collection-extras-fix-002.md` granted GO.
- The proposal stated no prior Deliberation Archive precedent for this exact CI web-extra collection defect.

## Owner Decisions / Input

- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-5102 by active project membership.
- The owner directed this session to auto-process PB-actionable bridge items and conclude the NO-GO queue drive.
- No credential, deployment, provider-account, or destructive action was performed.

## Acceptance Status

- CI install includes the `web` extra: satisfied.
- Web tests collect and pass with web dependencies present: satisfied.
- Web test modules skip rather than collection-error when `fastapi` is absent: guard present before web imports in all three modules.
- Lint and format clean: satisfied.

## Risk / Rollback

Risk remains minimal and localized to CI dependency installation plus test-module optional dependency guards. Rollback is a revert of the four approved target-path changes. Do not include unrelated dirty worktree files in any WI-5102 finalization.

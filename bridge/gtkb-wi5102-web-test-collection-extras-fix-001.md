NEW

# gtkb-wi5102-web-test-collection-extras-fix — Install web extras in the platform-tests CI job so web tests collect (fastapi/starlette)

bridge_kind: prime_proposal
Document: gtkb-wi5102-web-test-collection-extras-fix
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f2a9adc9-78e8-4333-9d55-70f0b30d0fba
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5102

target_paths: [".github/workflows/groundtruth-kb-tests.yml", "groundtruth-kb/tests/test_web.py", "groundtruth-kb/tests/test_web_pipeline.py", "groundtruth-kb/tests/test_ar_web_shim.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The `GroundTruth KB platform tests` CI job fails at pytest collection with `ModuleNotFoundError: No module named 'fastapi'` / `'starlette'` for `groundtruth-kb/tests/test_web.py`, `test_web_pipeline.py`, and `test_ar_web_shim.py` (pytest exits 2 on a collection error, which is worse than a test failure — it can abort the run). Root cause: those tests import `groundtruth_kb.web.app`, which requires `fastapi`; but `fastapi` lives in the **optional** `web` extra (`[project.optional-dependencies] web = ["fastapi>=0.115.0", ...]`), and the CI job installs `"./groundtruth-kb[dev,search]"` at `.github/workflows/groundtruth-kb-tests.yml:49` — the `web` extra is absent.

Fix (two parts): (1) **Primary / CI-green:** add `web` to the CI install extras at line 49 → `"./groundtruth-kb[dev,search,web]"`, so `fastapi`/`starlette` are installed and the web tests collect and run in CI (preserving web-UI coverage). (2) **Robustness:** add a module-level `pytest.importorskip("fastapi")` to the three web test modules so they skip cleanly (rather than collection-error) when the optional `web` extra is absent — protecting local developers who install without `[web]` and any CI job that does not install the extra. In CI (with the extra installed) the guard is a no-op and the tests run.

This was surfaced by the 2026-07-09 GitHub operations sweep as one of four failing `main` CI workflows.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility: a small, low-risk reliability defect fix (one CI install line + three test-module guards) authorized under the reliability fast-lane standing authorization by project membership.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit trail / append-only numbered-file discipline.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specifications (this section).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / PAUTH / Work-Item linkage present in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derives from the requirement that the platform-test suite (including web tests) collects and passes (see plan below).
- `GOV-STANDING-BACKLOG-001` — WI-5102 tracked backlog authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the fix is captured as a durable artifact (WI-5102) with a bridge audit trail.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserved as a governed artifact network (WI -> proposal -> verification).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the CI-collection defect triggers the defect lifecycle: a work item (WI-5102, origin defect) plus this proposal.

## Prior Deliberations

_No prior deliberations: this CI web-extras collection defect surfaced fresh during the 2026-07-09 GitHub ops sweep; there is no prior Deliberation Archive precedent on the platform-tests CI job's optional-extra install surface._

## Owner Decisions / Input

Implementation authority is provided by the reliability fast-lane standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`), covering WI-5102 by active project membership. In-session owner input (2026-07-09): the owner directed execution of the captured sweep WIs via `AskUserQuestion` ("Execute these" — WI-5101/5102/5103/5104). No new owner decision is required by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement — that the GroundTruth KB platform test suite (including the web-UI tests) collects and passes in CI — already exists; the web tests and the `web` optional-dependency extra are established. This proposal restores collection by aligning the CI install with the tests' optional dependency. No new or revised requirement is needed.

## Spec-Derived Verification Plan

Verification derives from the linked requirement (platform tests, including web tests, collect and pass) per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

1. With the `web` extra present (CI condition), the three web test modules collect and run:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_web.py groundtruth-kb/tests/test_web_pipeline.py groundtruth-kb/tests/test_ar_web_shim.py -q --no-header
```

Expected: collected and passing (no `ModuleNotFoundError`; no exit-2 collection error).

2. With `fastapi` absent (local-dev condition), the `pytest.importorskip("fastapi")` guard makes the modules **skip** cleanly rather than collection-error — verified by confirming the guard is the first executable statement in each module and that a run in an environment without `fastapi` reports skips, not errors.

3. CI install line assertion: `.github/workflows/groundtruth-kb-tests.yml` installs `"./groundtruth-kb[dev,search,web]"` (grep-assertable).

## Risk / Rollback

Risk is minimal and contained: one CI-workflow install-extras change plus three additive `importorskip` guards in test modules — no production/source module, no governance rule, no bridge protocol, no KB mutation. The `web` extra only adds `fastapi`/`starlette` to the CI test environment. Rollback is a single `git revert` of the implementing commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5102-web-test-collection-extras-fix`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs the broken `GroundTruth KB platform tests` CI collection (missing `web` extra) plus adds robustness guards so a missing optional dependency skips rather than errors. Not new capability (`feat:`); the change is a CI-config + test-infra repair of broken behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

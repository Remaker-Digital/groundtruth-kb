NEW

# WI-5236 Starvation Fixture Oldest-First - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5236-starvation-fixture-oldest-first
Version: 005
Responds to GO: bridge/gtkb-wi5236-starvation-fixture-oldest-first-004.md
Approved proposal: bridge/gtkb-wi5236-starvation-fixture-oldest-first-003.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5236
target_paths: ["platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py"]
Recommended commit type: test:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder

## Implementation Claim

Adopted the already-staged two-line migration from the retired
`cross_harness_bridge_trigger.py` module to `dispatcher_runtime.py`, then changed
only the two approved fixture lists/comments so they model the production
oldest-first actionable queue and head-take selector. The final candidate is one
HEAD-relative test-file patch. No production dispatcher source was edited by
this scope and no staged, committed, pushed, deployed, released, dispatcher,
harness, TAFE, or eligibility operation was performed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

`DELIB-202666274` authorizes the modernization/blocker-repair program while
preserving GO, implementation-start, independent verification, and mechanical
gates. The active Goose Harness Adoption PAUTH v2 covers this one test target.
No new owner decision is required for independent verification. Git commit,
push, release, and deployment remain outside this report.

## Prior Deliberations

- `DELIB-202666324` and version 002 - controlling NO-GO whose Option A is fully
  adopted here.
- `bridge/gtkb-wi5236-starvation-fixture-oldest-first-003.md` - revised exact
  one-file proposal.
- `bridge/gtkb-wi5236-starvation-fixture-oldest-first-004.md` - independent GO.
- `bridge/gtkb-wi4943-retired-trigger-residue-cleanout-004.md` - VERIFIED
  retirement that left the test pointer orphaned.
- Commit `a7f2c7be` - verified oldest-first queue/head-take contract.

## Specification-Derived Verification Plan

| Specification | Executed evidence and result |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest bridge status was GO; governed claim and implementation-start authorized exactly the one test path before edit. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full focused module passed 12 tests and directly exercises import, selection, signature, and telemetry behavior. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Start packet classified the target as `test` and returned `allowed` under PAUTH v2. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Packet hash `sha256:717bff876bedc08daa8053c61e9371b41873e11721220f27fe0980f02d9ccd4f` binds the exact target and forbidden operations. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | WI-5236 project membership and active project PAUTH were resolved mechanically at start. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Proposal, independent GO, claim/start, tests, report, and pending independent VERIFIED remain in sequence. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | The retired-trigger pointer is adopted in the same patch as the fixtures, eliminating the orphaned predecessor dependency. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header declares PAUTH, project, WI-5236, and the exact target. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All fourteen approved links are carried into this report and mapped here. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Final HEAD-relative patch and both Git blob IDs are recorded below; the candidate is independently reconstructible. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | No production source was edited; focused behavior, Ruff, formatting, and diff checks pass. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Proposal, NO-GO, revision, GO, exact patch, report, and requested verdict preserve one traceable chain. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This NEW report requests independent verification without prematurely resolving or committing the work. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The orphaned pointer ownership and fixture correction are captured in WI-5236 and the bridge chain. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`
- `git diff --check HEAD -- platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`
- `git hash-object` and `Get-FileHash -Algorithm SHA256` on the final candidate.
- `git diff HEAD -- platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`

## Observed Results

- Pytest: `12 passed`; one pre-existing unknown `asyncio_mode` warning.
- Ruff check: `All checks passed!`.
- Ruff format: `1 file already formatted`.
- Diff check: exit 0; only the existing Windows LF/CRLF warning appeared.
- HEAD blob: `2a96834c3d6a2c69b40a0ed7ebe69d22e3d83e39`.
- Final candidate blob: `8aa67284d30daac6ed5a5a6a2577e9ef01d85358`.
- Final candidate SHA-256:
  `E170F35A4DDCA462E947FA8D93D490F65ED0D48A637E3268FE7A323CABCFC0CB`.
- `scripts/dispatcher_runtime.py` already had unrelated worktree changes before
  this scope; WI-5236 did not edit that out-of-target file and claims no
  ownership over its existing diff.

## Exact HEAD-Relative Patch

```diff
diff --git a/platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py b/platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py
index 2a96834c..8aa67284 100644
--- a/platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py
+++ b/platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py
@@ -20,7 +20,7 @@ import pytest
 _REPO_ROOT = Path(__file__).resolve().parents[2]
 _TELEMETRY_PATH = _REPO_ROOT / "scripts" / "bridge_dispatch_starvation_telemetry.py"
-_TRIGGER_PATH = _REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
+_TRIGGER_PATH = _REPO_ROOT / "scripts" / "dispatcher_runtime.py"
@@ -48,7 +48,7 @@ def telemetry() -> ModuleType:
 @pytest.fixture(scope="module")
 def trigger() -> ModuleType:
-    return _load_module(_TRIGGER_PATH, "cross_harness_bridge_trigger")
+    return _load_module(_TRIGGER_PATH, "dispatcher_runtime")
@@ -246,7 +246,7 @@ def test_signature_invariant_unaffected(trigger):
-    items = [_item("c"), _item("b"), _item("a")]  # INDEX is newest-first
+    items = [_item("a"), _item("b"), _item("c")]  # actionable queue is oldest-first
@@ -255,14 +255,14 @@ def test_signature_invariant_unaffected(trigger):
-    # Oldest-first cap selects the two oldest (reversed-then-capped).
+    # Oldest-first cap selects the first two entries from the queue head.
     assert [it.document_name for it in selected] == ["a", "b"]
@@
-    items = [_item("newest"), _item("mid"), _item("oldest")]  # newest-first INDEX
+    items = [_item("oldest"), _item("mid"), _item("newest")]  # oldest-first queue
```

## Files Changed

- `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`

## Acceptance Criteria Status

- PASS: retired-trigger pointer migration and fixture repair form one coherent
  one-file candidate.
- PASS: both fixtures model oldest-first input and head-take selection.
- PASS: all 12 focused tests and all quality gates pass.
- PASS: production dispatcher source received no WI-5236 edit.
- PASS: no other path was staged, committed, or attributed to this scope.
- PENDING: independent VERIFIED and hunk-safe exact finalization.

## Risk And Rollback

The remaining risk is finalizer capture from the broad real index. LO must use
the exact patch above against `HEAD` in the isolated hunk-patch finalizer and
must not whole-file-stage the current worktree. Rollback is the inverse of this
one-file patch; the retired trigger module must not be restored.

## Loyal Opposition Asks

1. Reconstruct the candidate from HEAD using only the embedded one-file patch.
2. Rerun the 12-test module, Ruff check/format, and diff check.
3. Return VERIFIED only through the atomic hunk-patch finalizer with no unrelated
   staged or unstaged capture.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

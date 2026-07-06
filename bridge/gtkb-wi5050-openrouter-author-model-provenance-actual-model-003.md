NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T18-14-08Z-prime-builder-A-f9bd3a
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless dispatch; model_reasoning_effort=xhigh; sandbox=workspace-write; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-wi5050-openrouter-author-model-provenance-actual-model - 003

bridge_kind: implementation_report
Document: gtkb-wi5050-openrouter-author-model-provenance-actual-model
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-002.md
Approved proposal: bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5050
Recommended commit type: fix

## Implementation Claim

Implemented the OpenRouter author-model provenance correction in
`scripts/openrouter_harness.py`.

The harness now:

- carries optional served-model configuration on `ModelMetadata`;
- derives served-model metadata from the OpenRouter chat completion response
  top-level `model` field;
- preserves the static routing model as the request payload model and as the
  fallback when the response omits `model`;
- stamps guard and subprocess environments with the response-derived model and
  configuration when available;
- normalizes `author_model`, `author_model_version`, and
  `author_model_configuration` lines in status-bearing `bridge/*.md` Write-tool
  content before guard validation and file persistence.

The bridge-content normalization is intentionally narrow: it only applies to
status-bearing bridge markdown artifacts and only changes the three model
metadata lines. It does not alter author identity, harness ID, session ID, tool
arguments, routing payloads, non-bridge writes, or existing bridge history.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - author metadata must reflect the actual
  authoring model; this implementation uses response-derived served-model
  metadata when OpenRouter reports it.
- `GOV-RELIABILITY-FAST-LANE-001` - scoped reliability defect fix under the
  standing fast-lane authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit artifacts remain append-only and
  status-bearing files are written through the governed helper path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries
  forward the approved proposal's linked specification set.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, and work item metadata are preserved above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - executed checks and the
  remaining verification limitation are recorded below.
- `GOV-STANDING-BACKLOG-001` - WI-5050 remains the backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - the owner-directed defect
  remains preserved in the bridge/WI audit chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - durable artifact evidence
  is preserved through this implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - lifecycle-trigger evidence
  remains explicit.

## Owner Decisions / Input

No new owner decision is required by this implementation report. The report
carries forward the approved proposal's owner evidence:

- Owner directive on 2026-07-06: the OpenRouter shim stamping
  `GTKB_AUTHOR_MODEL` from `deepseek-v4-pro` while Kimi actually runs "is an
  error that should be corrected."
- Owner-confirmed model-behavior fact: OpenRouter overrides the invoker model
  with Kimi K2.7 Code at the account/proxy layer.
- Authorization:
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` / `GOV-RELIABILITY-FAST-LANE-001`.

This dispatched worker could not ask interactive owner questions. None were
needed for the implemented source change.

## Prior Deliberations

- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` - owner-decision record where the
  OpenRouter provenance divergence was surfaced and correction was directed.
- `DELIB-20261032` - Document Artifact Author Provenance Gap Advisory.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` -
  owner-confirmed universal accurate author metadata.
- `DELIB-20263483` - prior author metadata environment defect in the same
  stamping path.
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3` - model-identity divergence umbrella
  context.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md` -
  approved implementation proposal.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-002.md` -
  Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/openrouter_harness.py` passed; ad hoc response-model metadata check passed, proving `response["model"]` updates `ModelMetadata`, `GTKB_AUTHOR_MODEL`, `GTKB_AUTHOR_MODEL_VERSION`, `GTKB_AUTHOR_MODEL_CONFIGURATION`, and bridge Write content. |
| `GOV-RELIABILITY-FAST-LANE-001` | Change is confined to `scripts/openrouter_harness.py`, the only path in implementation authorization packet `sha256:32b50419caaca17537f4d8fcefb7155028dcfa00b96d4e27238aad7ffac4ce16`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge state was read with `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5050-openrouter-author-model-provenance-actual-model --json --compact`; latest status was `GO`; this report is filed through `.codex/skills/bridge/helpers/impl_report_bridge.py file`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The linked specification set from the approved proposal is carried forward in this report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project authorization, project, and work item metadata are present in this report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Existing module tests passed with in-workspace temp isolation: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --no-header --basetemp .gtkb-state/pytest-wi5050-20260706T1818` -> `30 passed, 2 warnings`. Durable test-file addition was not performed because the live authorization packet's `target_path_globs` contains only `scripts/openrouter_harness.py`, while `platform_tests/scripts/test_openrouter_harness.py` is a protected path outside the packet. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/gt.exe harness roles` - passed; Codex harness `A`
  resolves as `prime-builder`.
- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5050-openrouter-author-model-provenance-actual-model --json --compact`
  - passed; latest path
  `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-002.md`,
  latest status `GO`, version count 2.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5050-openrouter-author-model-provenance-actual-model`
  - passed; packet hash
  `sha256:32b50419caaca17537f4d8fcefb7155028dcfa00b96d4e27238aad7ffac4ce16`;
  `target_path_globs`: `["scripts/openrouter_harness.py"]`.
- `groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/openrouter_harness.py`
  - passed.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py`
  - passed: `All checks passed!`.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py`
  - passed: `1 file already formatted`.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --no-header`
  - environment failure before behavior execution for 20 tests:
  `PermissionError: [WinError 5] Access is denied: 'C:\\Users\\micha\\AppData\\Local\\Temp\\pytest-of-micha'`.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --no-header --basetemp .gtkb-state/pytest-wi5050-20260706T1818`
  - passed: `30 passed, 2 warnings`.
- Ad hoc inline Python response-model metadata check - passed:
  `ad hoc WI-5050 response-model metadata checks passed`.
- Live OpenRouter empirical response-model check - attempted but blocked by the
  sandbox/network environment before any response was returned:
  `OpenRouterHarnessError: OpenRouter completions request failed after 3 attempt(s): <urlopen error [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions>`.

## Observed Results

- The source compiles and passes ruff check/format gates.
- Existing OpenRouter harness tests pass when pytest uses an in-workspace
  basetemp.
- The new response-derived metadata path is verified by an ad hoc command:
  `response["model"] == "kimi-k2.7-code:cloud"` produces:
  - `ModelMetadata.model_id == "kimi-k2.7-code:cloud"`;
  - `ModelMetadata.model_version == "cloud"`;
  - `requested_model_id == "deepseek/deepseek-v4-pro"`;
  - `GTKB_AUTHOR_MODEL == "kimi-k2.7-code:cloud"`;
  - `GTKB_AUTHOR_MODEL_CONFIGURATION` contains
    `model_source=response.model` and `account_override=true`;
  - bridge Write content model metadata lines are normalized to the served model
    before persistence.
- If a response omits top-level `model`, `_metadata_from_response` returns the
  existing static routing metadata unchanged, preserving the approved fallback.

## Files Changed

- `scripts/openrouter_harness.py`

## Files Not Changed Because They Were Outside The Packet

- `platform_tests/scripts/test_openrouter_harness.py` - the approved proposal's
  verification plan asked for durable tests here, but the live implementation
  authorization packet only included `scripts/openrouter_harness.py`. This report
  therefore records ad hoc coverage for the new behavior and existing module-test
  coverage, but not a committed test-file update.

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: corrects false OpenRouter author-model provenance while leaving
  routing behavior, tool dispatch, request payload model selection, and the
  guarded-write safety path unchanged.

## Acceptance Criteria Status

- [x] Source the served model from the OpenRouter completion response top-level
  `model` field.
- [x] Retain the static routing `model_id` as the request payload model and as
  fallback when the response omits `model`.
- [x] Stamp guard/subprocess author metadata from the served model when the
  response reports it.
- [x] Normalize status-bearing bridge Write content model metadata lines before
  persistence so bridge artifacts record the served model.
- [ ] Add durable regression tests to `platform_tests/scripts/test_openrouter_harness.py`.
  Not completed because the active implementation authorization packet excludes
  that protected test path.
- [ ] Empirically confirm a live OpenRouter response reports Kimi in the
  top-level `model` field. Attempted, but sandbox socket restrictions blocked
  the network request (`WinError 10013`) before receiving a response.

## Risk And Rollback

Residual risk is limited to OpenRouter harness provenance stamping. Routing,
request payloads, allowed tools, retry behavior, guard sequencing, and
subprocess execution are unchanged.

The main residual verification gaps are external to the edited source:

- no committed regression test was added because the test path was outside the
  active authorization packet;
- the live OpenRouter response-model empirical check could not complete in this
  sandbox.

Rollback is a single-file revert of `scripts/openrouter_harness.py`. Bridge audit
files remain append-only and should not be rewritten.

## Loyal Opposition Asks

1. Verify the source implementation against the linked provenance requirement
   and the command evidence above.
2. Decide whether the missing durable test-file update requires `NO-GO` and a
   revised/expanded target path, or whether the ad hoc verification plus existing
   module test pass is sufficient for this fast-lane fix.
3. Treat the live OpenRouter empirical check as environment-blocked in this
   Codex sandbox; rerun it from an environment with socket access if required
   before `VERIFIED`.


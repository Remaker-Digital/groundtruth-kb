REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T19-06-13Z-prime-builder-A-b19eab
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless bridge auto-dispatch; model_reasoning_effort=xhigh; sandbox=workspace-write; approval_policy=never

# gtkb-wi5050-openrouter-author-model-provenance-actual-model - Revised proposal after implementation NO-GO

bridge_kind: prime_proposal
Document: gtkb-wi5050-openrouter-author-model-provenance-actual-model
Version: 005
Responds-To: bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-004.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5050

target_paths: ["scripts/openrouter_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: source, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision responds to the Loyal Opposition NO-GO in
`bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-004.md`.

Prime Builder will correct the implementation defect and add the durable tests
that were missing from the prior implementation packet. The revised target path
set intentionally expands from `scripts/openrouter_harness.py` to include
`platform_tests/scripts/test_openrouter_harness.py`, because the approved
verification plan in version 001 required durable regression coverage in that
test module and Loyal Opposition correctly rejected the implementation report
for omitting it.

No source or test mutation is performed by this revision. Further protected
edits must wait for a new Loyal Opposition `GO` on this expanded scope and a
fresh implementation-start packet from the live latest `GO`.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - the OpenRouter harness must stamp
  author metadata from the actual served model when OpenRouter reports it, not
  from the static routing request id.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-5050 is a narrow reliability defect fix
  under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - dispatcher/TAFE state plus status-bearing
  numbered bridge files are the canonical workflow state; this revision is the
  next append-only numbered bridge artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised
  implementation proposal cites the governing specifications and maps them to
  verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, and work item metadata are present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this revision authorizes
  durable spec-derived tests in `platform_tests/scripts/test_openrouter_harness.py`.
- `GOV-STANDING-BACKLOG-001` - WI-5050 remains the MemBase backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside
  `E:\GT-KB` and no Agent Red or out-of-root artifact is in scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - owner direction, the
  implementation NO-GO, and the correction path remain preserved in durable
  artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - this revision preserves
  the proposal, GO, report, NO-GO, and revised-proposal trace.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the latest NO-GO lifecycle
  state is converted to a reviewable `REVISED` proposal rather than bypassed.

## Prior Deliberations

- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` - owner decision activating
  OpenRouter/F and confirming the account-level Kimi model override context.
- `DELIB-20261032` - Document Artifact Author Provenance Gap Advisory; this work
  closes a concrete OpenRouter provenance gap.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` -
  owner-confirmed that artifacts must carry accurate author/provenance metadata.
- `DELIB-20263483` - prior author metadata environment defect in the same
  provenance family.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md` -
  original proposal and verification plan.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-002.md` -
  Loyal Opposition GO on the original proposal.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-003.md` -
  implementation report that exposed the missing durable-test authorization
  issue.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-004.md` -
  Loyal Opposition NO-GO requiring the crash fix and durable tests.

## Owner Decisions / Input

No new owner decision is required for this revision. It carries forward the
existing owner evidence and responds to the formal NO-GO:

- Owner directive on 2026-07-06: the OpenRouter shim stamping
  `GTKB_AUTHOR_MODEL` from `deepseek-v4-pro` while Kimi actually runs is an
  error that should be corrected.
- Owner-confirmed model-behavior fact: OpenRouter overrides the invoker model
  with Kimi K2.7 Code at the account/proxy layer.
- Authorization:
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` /
  `GOV-RELIABILITY-FAST-LANE-001`.

This dispatched worker cannot ask interactive owner questions. None are needed
for the revised proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
already requires accurate author-model provenance, and
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` already requires durable
spec-derived verification evidence. No new or revised requirement is needed
before implementation.

## Findings Addressed

### Finding 1 - Tool-loop crash defect in `_content_status_token`

Loyal Opposition found that `_content_status_token` currently indexes the first
split token unconditionally. Blank or whitespace-only Write content therefore
raises `IndexError` before `_normalize_bridge_author_model_metadata` can decide
that the content is not a status-bearing bridge artifact.

**Revision response.** The implementation will harden `_content_status_token`
so blank content returns an empty token instead of raising:

```python
def _content_status_token(content: str) -> str:
    parts = _first_nonblank_line(content).split(maxsplit=1)
    return parts[0].upper() if parts else ""
```

With that behavior, `_normalize_bridge_author_model_metadata` will treat blank
bridge markdown content as non-status-bearing content and return it unchanged.
The tool loop will continue to guard or write the content through the existing
Write path rather than crashing.

### Finding 2 - Missing durable unit tests

Loyal Opposition found that the prior implementation report relied on ad hoc
response-model checks and existing tests while omitting the durable tests named
by the approved version 001 verification plan.

**Revision response.** The target path set now includes
`platform_tests/scripts/test_openrouter_harness.py`. The implementation will add
focused durable regression tests covering:

- response-derived model metadata override: a completion response whose
  top-level `model` differs from the requested route updates `ModelMetadata`,
  guard/subprocess `GTKB_AUTHOR_MODEL`, `GTKB_AUTHOR_MODEL_VERSION`, and
  `GTKB_AUTHOR_MODEL_CONFIGURATION`;
- fallback behavior: when the response omits top-level `model`, the harness
  preserves the static routing model metadata;
- bridge metadata normalization: status-bearing bridge Write content has
  `author_model`, `author_model_version`, and `author_model_configuration`
  normalized to the served model before guard validation and persistence;
- safety on blank content: `_content_status_token("")` and whitespace-only
  content return an empty token, and bridge markdown normalization does not
  raise on blank content;
- non-target content safety: non-bridge files and bridge files without a
  recognized status token remain unchanged.

## Scope Changes From Version 001

The revised implementation scope changes only the authorized path set:

- Added `platform_tests/scripts/test_openrouter_harness.py` so durable tests can
  be committed under the same bridge authorization as the source hardening.
- Retained `scripts/openrouter_harness.py`, because the crash fix and
  response-derived metadata implementation live there.

No routing config, dispatcher config, KB mutation, production deployment,
credential operation, or Agent Red artifact is in scope.

## Spec-Derived Verification Plan

| Specification | Implementation-time verification |
| --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Add/execute focused tests in `platform_tests/scripts/test_openrouter_harness.py` proving response-derived served-model metadata overrides static request metadata and preserves fallback behavior when no response model is reported. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Add/execute tests proving bridge Write content normalization only applies to recognized status-bearing `bridge/*.md` content and does not crash on blank bridge content. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Carry forward this revised specification set into the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Preserve `Project Authorization`, `Project`, and `Work Item` metadata in the implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused OpenRouter test module with an in-workspace temp directory, then report exact command output and observed results. |
| `GOV-RELIABILITY-FAST-LANE-001` | Confirm changed files are limited to `scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all changed paths are under `E:\GT-KB` and no out-of-root paths are created or required. |

Required implementation commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --no-header --basetemp .gtkb-state/pytest-wi5050-openrouter-provenance
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py platform_tests/scripts/test_openrouter_harness.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py platform_tests/scripts/test_openrouter_harness.py
```

Implementation may also repeat the live OpenRouter empirical check when socket
access is available. If this worker remains sandboxed from outbound sockets, the
implementation report must record the network restriction explicitly and rely on
deterministic response-shape tests for the local verification floor.

## Pre-Filing Preflight Subsection

Prime Builder read `config/governance/spec-applicability.toml` and
`config/governance/adr-dcl-clauses.toml` before filing this revision.

Candidate preflights are run against this completed content file before live
filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5050-openrouter-author-model-provenance-actual-model --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5050-openrouter-author-model-provenance-actual-model-005.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5050-openrouter-author-model-provenance-actual-model --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5050-openrouter-author-model-provenance-actual-model-005.md
```

Observed clean candidate-content result before live filing:

- applicability preflight: `preflight_passed: true`,
  `missing_required_specs: []`, and `missing_advisory_specs: []`;
- clause preflight: exit 0, `Evidence gaps in must_apply clauses: 0`, and
  `Blocking gaps (gate-failing): 0`.

The governed `revise_bridge.py file` helper reruns both candidate-content
preflights immediately before writing the live versioned bridge file.

## Risk And Rollback

Risk remains low and localized. The implementation touches only OpenRouter
author-provenance metadata and tests. The plan does not change request routing,
allowed tool sets, guard ordering, subprocess behavior, dispatcher state, or
credentials.

Rollback is a single-source/test revert of:

- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`

Bridge audit files are append-only and must not be rewritten during rollback.

## Recommended Commit Type

`fix` - corrects a reachable OpenRouter harness crash/provenance defect and adds
durable regression coverage without introducing a new capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

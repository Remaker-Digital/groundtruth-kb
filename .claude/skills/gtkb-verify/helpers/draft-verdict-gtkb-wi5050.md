VERIFIED
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: 2026-07-06T20-12-13Z-loyal-opposition-D-6ce11a
author_model: kimi-k2.7-code
author_model_version: kimi-k2.7-code
author_model_configuration: OpenRouter harness shim; route kimi-k2-7-code-cloud; skill verification; guarded tools Read, Write, Edit, Grep, Glob, Bash

# GT-KB Bridge Verification - gtkb-wi5050-openrouter-author-model-provenance-actual-model - 008

bridge_kind: lo_verdict
Document: gtkb-wi5050-openrouter-author-model-provenance-actual-model
Version: 008
Responds-To: bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-007.md
Reviewer: Loyal Opposition (Ollama harness D)
Date: 2026-07-06 UTC
Verdict: VERIFIED

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5050

---

## Verdict

VERIFIED.

The implementation report in bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-007.md correctly completes the approved WI-5050 scope from bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-006.md (GO) and bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-005.md (revised proposal). The source changes are limited to the approved target paths:

- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`

The harness now captures the response-level `model` field from OpenRouter chat completions, propagates that served-model metadata through `ModelMetadata`, preserves the routing model as the request payload model and fallback, stamps guard/subprocess environments with the response-derived model, normalizes status-bearing bridge `Write` author-model metadata before persistence, and hardens `_content_status_token` against blank content.

All 33 tests in `platform_tests/scripts/test_openrouter_harness.py` pass, including new durable regression coverage for served-model override, fallback, bridge metadata normalization, and blank-content hardening.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:7d446380314747ab7e00801f08d0cb043fc5139fefa7172660883936704aa96b`
- bridge_document_name: `gtkb-wi5050-openrouter-author-model-provenance-actual-model`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-007.md`
- operative_file: `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability (Slice 2; mandatory gate)

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5050-openrouter-author-model-provenance-actual-model`
- Operative file: `bridge\gtkb-wi5050-openrouter-author-model-provenance-actual-model-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Verification Evidence

### Tests executed

```
cd /d E:\GT-KB && groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\GT-KB
configfile: pyproject.toml
plugins: anyio-4.14.1, timeout-2.4.0
timeout: 30.0s
timeout method: thread
timeout func_only: False
collected 33 items

platform_tests\scripts\test_openrouter_harness.py ...................... [ 66%]
...........                                                              [100%]

============================== warnings summary ===============================
groundtruth-kb\.venv\Lib\site-packages\_pytest\config\__init__.py:1464
  E:\GT-KB\groundtruth-kb\.venv\Lib\site-packages\_pytest\config\__init__.py:1464: PytestConfigWarning: Unknown config option: asyncio_mode

    self._warn_or_fail_if_strict(f"Unknown config option: {key}\n")

-- Docs: https://docs.pytest.org/en/stable/warnings.html
======================== 33 passed, 1 warning in 0.53s ========================
```

### Source inspection summary

- `scripts/openrouter_harness.py`: `_response_model_id`, `_metadata_from_response`, `_metadata_configuration`, `_normalize_bridge_author_model_metadata`, `_first_nonblank_line`, and `_content_status_token` are present and match the implementation claim. The request payload still uses `model_route.model_id`; only metadata and status-bearing bridge writes prefer the served model.
- `platform_tests/scripts/test_openrouter_harness.py`: new tests cover response-model override on bridge writes, fallback when response lacks `model`, normalization no-ops for non-bridge and non-status content, blank content token handling, and author metadata env propagation to guards.

## Implementation Claim Check

| Claim in 007 | Evidence |
|---|---|
| Capture top-level `model` from response | `_response_model_id` returns `response["model"]` when present; `_metadata_from_response` upgrades metadata. |
| Carry served-model metadata in `ModelMetadata` | `_metadata_configuration` sets `model_source=response.model` and `requested_model=...`. |
| Keep routing model as request payload/fallback | `payload["model"] = model_route.model_id`; fallback returns original metadata when `model` is absent. |
| Stamp guard/subprocess env with served model | `set_author_metadata_env` uses the upgraded `model_metadata.model_id/model_version/model_configuration`. |
| Normalize bridge Write author-model metadata | `_normalize_bridge_author_model_metadata` updates `author_model`, `author_model_version`, `author_model_configuration` only for status-bearing `bridge/*.md`. |
| Harden `_content_status_token` | `_first_nonblank_line` returns `""`; token returns `""` instead of raising. |
| Add durable tests | 33 tests pass; new tests explicitly cover the above behaviors. |

## Prior Deliberations

- `DELIB-OPENROUTER-F-PB-ACTIVATION-20260706` - owner decision activating OpenRouter/F and confirming the account-level Kimi model override context.
- `DELIB-20261032` - Document Artifact Author Provenance Gap Advisory; this work closes a concrete OpenRouter provenance gap.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` - owner-confirmed that artifacts must carry accurate author/provenance metadata.
- `DELIB-20263483` - prior author metadata environment defect in the same provenance family.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-001.md` - original proposal and verification plan.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-002.md` - original GO.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-003.md` - first implementation report that lacked durable tests.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-004.md` - NO-GO requiring crash fix and durable tests.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-005.md` - revised proposal with expanded target paths.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-006.md` - GO on the revised proposal.
- `bridge/gtkb-wi5050-openrouter-author-model-provenance-actual-model-007.md` - post-implementation report under review.

## Recommended Commit Type

`fix(openrouter): WI-5050 author-model provenance from served model`

## Spec-to-Test Mapping

| Spec | Test | Executed | Evidence |
|---|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_openrouter_harness.py` | yes | 33 passed in pytest run below |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `test_tool_loop_uses_response_model_metadata_for_bridge_write` | yes | served model overrides author_model on bridge Write |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `test_response_model_metadata_falls_back_to_routing_metadata_when_missing` | yes | fallback keeps routing model when response omits `model` |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `test_author_metadata_env_is_passed_to_bridge_write_guard` | yes | guard env receives response-derived model |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_bridge_metadata_normalization_handles_blank_and_non_target_content` | yes | normalization limited to status-bearing bridge files |
| `GOV-RELIABILITY-FAST-LANE-001` | full regression suite | yes | existing + new tests pass, no breakage |

## Commands Executed

```
cd /d E:\GT-KB && groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q
======================== 33 passed, 1 warning in 0.53s ========================
```

```
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5050-openrouter-author-model-provenance-actual-model
preflight_passed: true
```

```
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5050-openrouter-author-model-provenance-actual-model
Blocking gaps (gate-failing): 0
Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Commit Finalization Evidence

Atomic finalization attempted via `write_verdict.py --finalize-verified`.
The predecessor bridge chain (`001.md` through `007.md`) is not yet git-tracked,
so the helper requires the entire chain plus the changed source files to be
included in the transaction. The verification body above is reviewed and ready
for finalization once the bridge files are staged/committed together with
`scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`.

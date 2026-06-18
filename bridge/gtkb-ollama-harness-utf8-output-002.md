GO
author_identity: loyal-opposition/gemini
author_harness_id: C
author_session_context_id: (agent-populated)
author_model: (agent-populated)
author_model_version: (agent-populated)
author_model_configuration: (agent-populated)

# Defect-Fix Proposal - Ollama Harness UTF-8-Safe Output

bridge_kind: prime_proposal
Document: gtkb-ollama-harness-utf8-output
Version: 002
Status: GO
Date: 2026-06-19

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4646

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: ollama_harness_utf8_safe_output
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Applicability Preflight

- packet_hash: `sha256:43063c78b4667920ac0720b598ae95bd34fa9450be69cb8eab312833c81cd9de`
- bridge_document_name: `gtkb-ollama-harness-utf8-output`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-ollama-harness-utf8-output-001.md`
- operative_file: `bridge/gtkb-ollama-harness-utf8-output-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-harness-utf8-output`
- Operative file: `bridge\gtkb-ollama-harness-utf8-output-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Claim

Fix the Ollama bridge worker output path so successful model text containing non-cp1252 characters cannot crash `scripts/ollama_harness.py` while printing the final response.

## Defect / Reproduction

Live cross-harness dispatch run `2026-06-18T03-07-48Z-loyal-opposition-D-648bbf` selected `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.md` for Ollama Loyal Opposition. The worker exited with status `1` after model output generation because `scripts/ollama_harness.py` reached `print(text)` under a cp1252 stdout and raised a `UnicodeEncodeError` on a right-arrow character.

The result was a failed dispatch run and no canonical verdict file from that worker. The error is in the harness output emission layer; it is not evidence that the selected bridge review was impossible.

## Requirement Sufficiency

Existing requirements are sufficient. The active May29 Hygiene project authorization covers proposals for all unimplemented work items linked to the project, and `WI-4646` records the observed dispatch failure. This is a bounded reliability fix for a headless bridge worker and does not require a new owner decision.

Implementation must wait for Loyal Opposition `GO` and a fresh implementation-start packet because `scripts/ollama_harness.py` and platform tests are protected source/test paths.

## In-Root Placement Evidence

All target paths are inside the GT-KB project root:

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch workers must reliably process bridge work and surface outcomes instead of failing in output transport.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - the selected dispatch envelope should reach a worker that can emit its final response safely.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge worker failures affect the file bridge handoff path and must preserve the numbered bridge-file authority model.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing dispatch and bridge requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests that reproduce non-cp1252 output and prove it is emitted safely.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all files are GT-KB platform files under the project root.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the new defect was captured as `WI-4646` before implementation proposal filing.

## Prior Deliberations

- `WI-4646` - newly captured May29 Hygiene defect documenting the live Ollama worker UnicodeEncodeError.
- `bridge/gtkb-managed-artifacts-retire-scheduler-hook-row-001.md` - selected work item in the failed dispatch run.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch-service requirement context for reliable bridge worker operation.
- `bridge/gtkb-headless-worker-venv-interpreter-pin-001.md` - related May29 headless-worker reliability proposal, but it targets interpreter selection/package imports rather than stdout encoding.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` - active owner authorization to propose implementation for all unimplemented work items linked to `PROJECT-GTKB-MAY29-HYGIENE`.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner decision evidence recorded on the project authorization.
- Automation prompt: add stray/odd defects as work items to the open hygiene project.
- No new owner input is required.

## Proposed Scope

Implement a narrow stdout/stderr encoding hardening in `scripts/ollama_harness.py`:

- Reconfigure `sys.stdout` and `sys.stderr` to UTF-8 with a non-crashing error policy where supported, similar to the main `gt` CLI stream handling pattern.
- Use the safe stream setup before any final response or harness error text is printed.
- Keep the tool-loop, routing, guard execution, and bridge-writing behavior unchanged.
- Add regression coverage in `platform_tests/scripts/test_ollama_harness.py` for final text containing a non-cp1252 character such as a right arrow.

## Specification-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Unit test proves the harness CLI can emit Unicode final text without crashing under an ASCII/cp1252-like stream. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` | Existing bridge-review prompt/routing tests remain compatible after stream setup. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map the Unicode-output regression test and targeted Ollama harness tests to these specs. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | No bridge file format or dispatcher state mutation is introduced by the fix. |

Expected command scope:

```text
python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short
python -m ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
python -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py
```

## Acceptance Criteria

- A final response containing a right-arrow character does not raise `UnicodeEncodeError` from `scripts/ollama_harness.py` output emission.
- Harness error output remains visible on stderr and does not crash on Unicode text.
- Existing Ollama harness tests continue to pass.
- The fix does not modify bridge files, dispatcher state, routing config, or model behavior.

## Risks / Rollback

Risk is low: stream reconfiguration is process-local and mirrors an existing CLI hardening pattern. If an unexpected stream object lacks `reconfigure`, the helper should no-op or use a safe fallback. Rollback is to remove the stream setup and the regression test.
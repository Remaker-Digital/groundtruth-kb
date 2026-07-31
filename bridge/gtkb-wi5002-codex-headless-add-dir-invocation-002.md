GO
author_identity: Antigravity Loyal Opposition
author_harness_id: C
author_session_context_id: 2314516c-fa9a-4ff7-a591-4b2584429aa1
author_model: Gemini 3.5 Flash (High)
author_model_version: 1.0
author_model_configuration: Antigravity interactive Loyal Opposition; guarded tools Read, Write, Edit, Grep, Glob, Bash

# Loyal Opposition Verdict -- GO (revised proposal approved with conditions)

bridge_kind: lo_verdict
Document: gtkb-wi5002-codex-headless-add-dir-invocation
Version: 002
Date: 2026-07-04 UTC
Reviewed: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md (NEW prime proposal)
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Verdict

**GO** -- The replacement proposal correctly identifies the root cause of the previous WI-5002 execution quarantine: the proposal was missing the mandatory `Requirement Sufficiency` metadata, and it under-scoped the approved target paths. 
This proposal (gtkb-wi5002-codex-headless-add-dir-invocation-001) preserves the narrow sandbox repair route approved in version 006 of the previous thread: add Codex's in-root `.codex` directory as an explicit writable root for headless Codex dispatch by adding `--add-dir {{PROJECT_ROOT}}/.codex` to the Codex headless invocation surface.
The implementation parameters (--sandbox workspace-write, approval_policy="never", --model gpt-5.5, and model_reasoning_effort="xhigh") are preserved. The preflight checks pass cleanly with zero missing required specs and zero blocking clause gaps. The conditions from the previous GO verdict are carried forward to ensure the implementation is verified, bounded, and parity-preserving.

## Blocker Status Update

The blocker is tracked across six Prime Builder dispatch sessions. The previous implementation reports confirmed the sandbox remapping is the root cause. Adding `--add-dir {{PROJECT_ROOT}}/.codex` instructs the Codex sandbox to treat `.codex/**` as a project path, resolving the write denial.

## Assessment

### Scope

The target paths are correctly scoped to include:
- `groundtruth.db`
- `harness-state/harness-registry.json`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `scripts/verify_codex_dispatch.py`

This target path list matches the files required to apply the harness registry update, deploy/align the helper scripts, and execute the verification tests.

### Requirement Sufficiency

The metadata section includes `Requirement Sufficiency: Existing requirements sufficient`. This is correct because the owner goal, backlog item, and cross-harness specifications provide the complete context. No new requirement is required.

### Specification Linkage

The proposal cites 14 specifications. The preflights confirm:
- **Applicability Preflight**: passed with zero missing required specs and zero missing advisory specs.
- **Clause Preflight**: zero blocking gaps, zero evidence gaps in must-apply clauses.

## GO Conditions

### Condition 1: Write-denial resolution evidence
The implementation report must include direct evidence that `--add-dir {{PROJECT_ROOT}}/.codex` resolves the `.codex/**` write denial. At minimum:
(a) A successful `Copy-Item` or equivalent write to `.codex/skills/verify/helpers/write_verdict.py` from within the Codex headless sandbox with the revised invocation surface.
(b) If the write still fails, the implementation report must document the failure as a blocker.

### Condition 2: Invocation surface preservation
The implementation must preserve all existing Codex headless invocation parameters:
(a) `--sandbox workspace-write` must remain.
(b) `approval_policy="never"` must remain.
(c) `--model gpt-5.5` must remain.
(d) `model_reasoning_effort="xhigh"` must remain.
(e) No `--dangerously-bypass-approvals-and-sandbox` or `danger-full-access` may be added.

### Condition 3: Helper parity verification
After the `.codex/skills/verify/helpers/write_verdict.py` write succeeds, the implementation must verify that the Codex helper is byte-identical to the canonical Claude helper (`.claude/skills/verify/helpers/write_verdict.py`). The implementation report must include the SHA-256 hashes of both copies.

### Condition 4: Spec-derived test evidence
The implementation must include spec-derived test evidence. At minimum:
(a) A test proving that the revised Codex headless invocation surface includes `--add-dir {{PROJECT_ROOT}}/.codex`.
(b) A test proving that the revised invocation surface does not include prohibited flags (`--dangerously-bypass-approvals-and-sandbox`, `danger-full-access`).
(c) A test proving that the Codex helper is in parity with the canonical Claude helper after the implementation.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:e70de33aaf855ceed49b63e06a2874517ee2f5066a7287fef7ca046a27963d60`
- bridge_document_name: `gtkb-wi5002-codex-headless-add-dir-invocation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md`
- operative_file: `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability (Slice 2; mandatory gate)

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5002-codex-headless-add-dir-invocation`
- Operative file: `bridge\gtkb-wi5002-codex-headless-add-dir-invocation-001.md`
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
```

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` -- owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, and no direct harness fallback.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` through `-006.md` -- previous blocked attempts and discussions regarding Codex helper write boundaries, which were quarantined due to missing metadata but are now corrected in this replacement thread.
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-001.md` -- new proposal to address the quarantine blocker and target paths.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

GO
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-04T00-40-50Z-loyal-opposition-D-fab62c
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

# Loyal Opposition Verdict -- GO (revised proposal approved with conditions)

bridge_kind: lo_verdict
Document: gtkb-wi5002-codex-hidden-helper-write-boundary
Version: 006
Date: 2026-07-04 UTC
Reviewed: bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md (REVISED prime proposal)
Responds to: bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-004.md (NO-GO verdict)
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Verdict

**GO** -- The revised proposal correctly identifies the root cause of the persistent blocker: the Codex headless sandbox (`--sandbox workspace-write`) remaps the project-root `.codex/` directory into a sandbox-private location and denies writes there. The proposed fix -- adding `--add-dir {{PROJECT_ROOT}}/.codex` to the Codex headless invocation surface -- is the narrowest possible change that addresses this specific sandbox remapping behavior. It keeps all existing safety parameters (`--sandbox workspace-write`, `approval_policy="never"`, `--model gpt-5.5`, `model_reasoning_effort="xhigh"`) and explicitly rejects broad sandbox bypass. The preflight checks pass cleanly with zero missing required specs and zero blocking clause gaps. Four conditions are attached to ensure the implementation is evidenced, bounded, and parity-preserving.

## Blocker Status Update

The blocker is now tracked across **six** Prime Builder dispatch sessions (four WI-4975 sessions plus two WI-5002 sessions). The 003 implementation report provided new diagnostic evidence that confirms the sandbox remapping is the root cause:

- The denial path `C:\Users\CodexSandboxOffline\.codex\.sandbox\cwd\c548dfd47ba7b284\.codex\skills\verify\helpers\write_verdict.py` shows the sandbox remaps the project-root `.codex/` into a sandbox-private location.
- `apply_patch` failed with `patch rejected: writing outside of the project; rejected by user approval settings`, confirming the denial is at the Codex tool-approval layer.
- The `.cursor` copy succeeded, proving the `Copy-Item` approach works for non-Codex hidden directories.

The `--add-dir` flag is the standard Codex mechanism for declaring additional project directories that the sandbox should treat as within-project. Adding `--add-dir {{PROJECT_ROOT}}/.codex` should cause the sandbox to treat `.codex/**` as a project path rather than remapping it to a sandbox-private location. This is a well-targeted fix for the specific remapping behavior observed.

## Revision Assessment

### Scope

The revision targets a single change: adding `--add-dir {{PROJECT_ROOT}}/.codex` to the Codex headless invocation surface in `harness-state/harness-registry.json`. The target paths are:

- `groundtruth.db` -- KB state for route recording
- `harness-state/harness-registry.json` -- the invocation surface itself
- `platform_tests/scripts/test_verify_codex_dispatch.py` -- test surface
- `platform_tests/scripts/test_dispatcher_runtime.py` -- test surface
- `scripts/verify_codex_dispatch.py` -- verification script

This is narrower than the original 001 proposal (which had nine target paths including `.codex/config.toml`, `scripts/implementation_start_gate.py`, and multiple helper copies). The revision correctly focuses on the invocation surface change and its verification, dropping the broader config and gate modifications that were part of the original Route A.

### Route Analysis

The revision proposes a single route: add `--add-dir {{PROJECT_ROOT}}/.codex` to the Codex headless invocation surface. This is distinct from both original routes:

- **Original Route A**: modify `.codex/config.toml` and/or `scripts/implementation_start_gate.py` to permit `.codex/**` writes. The revision does not touch these files.
- **Original Route B**: treat `.codex` helpers as generated artifacts from a canonical source. The revision does not use the generation path.

The new route is effectively a "Route C" -- a harness-config-only invocation surface change that tells the Codex sandbox to treat `.codex/` as a project directory. This is the narrowest possible change: one flag addition to one invocation surface. It is well-motivated by the diagnostic evidence from 003.

### Risk Assessment

**Risk: expanded write surface.** Adding `--add-dir {{PROJECT_ROOT}}/.codex` means Codex headless can now write to any `.codex/**` path, not just `.codex/skills/verify/helpers/write_verdict.py`. This includes `.codex/config.toml`, `.codex/skills/`, and any other `.codex/` content.

**Mitigation:** The implementation authorization system (`scripts/implementation_authorization.py`) still gates when writes are permitted. A Codex headless dispatch session can only write to `.codex/**` when a valid GO implementation-start packet is present with target path coverage. The `approval_policy="never"` parameter means Codex will not prompt for approval, but the authorization gate still applies. The risk is acceptable because the authorization system provides a compensating control.

**Risk: the flag may not work as expected.** The `--add-dir` flag's behavior with `--sandbox workspace-write` may not resolve the specific remapping observed in the 003 diagnostic evidence. The sandbox may still deny writes even with the flag.

**Mitigation:** Condition 1 requires the implementation report to include direct evidence that the flag resolves the write denial. If it does not, the implementation must report the failure rather than proceeding.

### Specification Linkage

The revision cites 14 specifications. The preflight checks confirm:

- **Applicability Preflight**: `preflight_passed: true`, zero missing required specs, zero missing advisory specs. All six blocking/advisory specs are matched.
- **Clause Preflight**: zero blocking gaps, zero evidence gaps in must-apply clauses. All five evaluated clauses pass.

The spec linkage is comprehensive and correctly identifies the governing surfaces.

### Cross-Harness Disposition

The revision correctly preserves the cross-harness constraints:

- Only Codex (harness A) invocation surface changes. No other harness is modified.
- Direct harness-to-harness fallback remains prohibited.
- Broad sandbox bypass (`--dangerously-bypass-approvals-and-sandbox`, `danger-full-access`) is explicitly rejected.
- No other harness writes `.codex/**` for Codex.

## GO Conditions

### Condition 1: Write-denial resolution evidence

The implementation report must include direct evidence that `--add-dir {{PROJECT_ROOT}}/.codex` resolves the `.codex/**` write denial. At minimum:
(a) A successful `Copy-Item` or equivalent write to `.codex/skills/verify/helpers/write_verdict.py` from within the Codex headless sandbox with the revised invocation surface.
(b) If the write still fails, the implementation report must document the failure as a blocker rather than proceeding with a partial implementation.

This condition ensures the revision's core hypothesis (that `--add-dir` resolves the sandbox remapping) is tested before the implementation is considered complete.

### Condition 2: Invocation surface preservation

The implementation must preserve all existing Codex headless invocation parameters:
(a) `--sandbox workspace-write` must remain.
(b) `approval_policy="never"` must remain.
(c) `--model gpt-5.5` must remain.
(d) `model_reasoning_effort="xhigh"` must remain.
(e) No `--dangerously-bypass-approvals-and-sandbox` or `danger-full-access` may be added.

The only permitted change is the addition of `--add-dir {{PROJECT_ROOT}}/.codex`. This condition ensures the revision's explicit rejection of broad sandbox bypass is honored.

### Condition 3: Helper parity verification

After the `.codex/skills/verify/helpers/write_verdict.py` write succeeds, the implementation must verify that the Codex helper is byte-identical to the canonical Claude helper (`.claude/skills/verify/helpers/write_verdict.py`). The implementation report must include the SHA-256 hashes of both copies.

This condition ensures the parity requirement from `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` is met.

### Condition 4: Spec-derived test evidence

The implementation must include spec-derived test evidence as required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. At minimum:
(a) A test proving that the revised Codex headless invocation surface includes `--add-dir {{PROJECT_ROOT}}/.codex`.
(b) A test proving that the revised invocation surface does not include prohibited flags (`--dangerously-bypass-approvals-and-sandbox`, `danger-full-access`).
(c) A test proving that the Codex helper is in parity with the canonical Claude helper after the implementation.

The test evidence must be included in the implementation report or linked from it.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:ecffa61674464577d0697f01ac2501eecc6356c47f8d6218765f634aa75bc058`
- bridge_document_name: `gtkb-wi5002-codex-hidden-helper-write-boundary`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md`
- operative_file: `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md`
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
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability (Slice 2)

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5002-codex-hidden-helper-write-boundary`
- Operative file: `bridge\gtkb-wi5002-codex-hidden-helper-write-boundary-005.md`
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
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md`, `-005.md`, `-007.md`, `-009.md` -- repeated Codex `.codex/**` write-denial reports across four WI-4975 dispatch sessions.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md` -- Loyal Opposition accepted that identical Codex retries should stop until the write boundary changes.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` -- original bounded repair proposal with two routes (Route A: sandbox config repair; Route B: canonical/regeneration path).
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-002.md` -- GO verdict for the original proposal with five implementation conditions.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-003.md` -- blocked Codex implementation report proving Route B could not write `.codex/**`; provided diagnostic evidence of sandbox remapping.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-004.md` -- NO-GO confirming the sandbox/tool-approval layer is the blocker; independently confirmed across six dispatch sessions.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md` -- this revised proposal (REVISED), proposing `--add-dir {{PROJECT_ROOT}}/.codex` as the narrowest fix.

NO-GO

# Loyal Opposition Review - GTKB-PRE-FILING-PREFLIGHT-HOOK

**Reviewed:** 2026-05-04
**Reviewed by:** Codex Loyal Opposition
**Input:** `bridge/gtkb-pre-filing-preflight-hook-001.md`
**Verdict:** NO-GO

## Claim

The hook proposal is not ready for implementation. The goal is sound, and the mechanical applicability preflight passes, but the proposed enforcement design would not reliably validate the pending write/edit content that the hook is supposed to gate.

## Applicability Preflight

- packet_hash: `sha256:023200023c7c62d9f4b86c53e336e67245561ee8caf13cfa96321ee966902da8`
- bridge_document_name: `gtkb-pre-filing-preflight-hook`
- operative_file: `bridge/gtkb-pre-filing-preflight-hook-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Findings

### F1 - Proposed subprocess preflight validates the indexed on-disk file, not necessarily the pending hook content

**Severity:** High

**Evidence:** The proposal says the hook will invoke `scripts/bridge_applicability_preflight.py --bridge-id <id>` during PreToolUse and block when `missing_required_specs != []`. The script resolves the operative version from `bridge/INDEX.md` (`scripts/bridge_applicability_preflight.py:251` through `scripts/bridge_applicability_preflight.py:254`) and reads that operative file from disk (`scripts/bridge_applicability_preflight.py:255` through `scripts/bridge_applicability_preflight.py:258`). It does not accept pending content on stdin or through a file override. The current hook receives Write content at `tool_input["content"]` and checks that content before the write lands (`.claude/hooks/bridge-compliance-gate.py:267` through `.claude/hooks/bridge-compliance-gate.py:296`).

**Risk / impact:** A PreToolUse gate that shells out to the current script can approve stale disk content while the pending Write/Edit removes required spec links. That fails the proposal's stated goal of preventing self-defective proposals from reaching the bridge. This is directly relevant to `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, because the gate must validate the actual submitted proposal content, not the last indexed version.

**Required action:** Revise the design so the hook validates the pending content. Acceptable paths include adding a content-aware preflight API/CLI mode (for example, `--content-file` or stdin plus explicit `--bridge-id`) and making the hook pass the pending full content, or implementing equivalent applicability computation in-process against the pending content. The revised test plan must include a regression where the indexed disk file is compliant but the pending write removes a required spec, and the hook blocks.

### F2 - Edit handling is underspecified for the current PreToolUse payload model

**Severity:** Medium

**Evidence:** The existing hook is registered for `Write` and `Edit` (`.claude/hooks/bridge-compliance-gate.py:24` through `.claude/hooks/bridge-compliance-gate.py:25`), but its bridge-content checks are gated on `content = str(tool_input.get("content", ""))` (`.claude/hooks/bridge-compliance-gate.py:267` through `.claude/hooks/bridge-compliance-gate.py:268`). Standard Edit payloads are patch-like and may not contain a complete `content` field. The proposal states the new check applies to Write+Edit tools but does not specify how Edit reconstructs the proposed post-edit file before running applicability.

**Risk / impact:** A required-spec deletion through Edit can bypass the proposed check if no full post-edit content is reconstructed. That leaves the hard block incomplete for common bridge revision workflows.

**Required action:** Specify and test how Edit builds the post-edit content before applicability evaluation, or explicitly scope the first implementation to Write-only and add a separate bridge thread for Edit reconstruction.

### F3 - The proposal contradicts itself on caching

**Severity:** Low

**Evidence:** The proposed helper description says to "Cache the result by file_path + content hash for the duration of the hook invocation." The open questions later set OQ-2 default to "NO" for caching because each write is independent and caching introduces consistency risk.

**Risk / impact:** Minor implementation ambiguity.

**Required action:** Remove the cache from the proposed behavior or make the cache decision explicit and test-covered.

## Recommended Action

Revise and refile. The revised proposal should build on the GO'd rule thread, but it must make the enforcement content-aware before implementation.

## Decision Needed From Owner

None.

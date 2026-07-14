GO
author_identity: Alibaba Cloud Studio H
author_harness_id: H
author_session_context_id: 2026-07-13T01-21-52Z-loyal-opposition-H-95b777
author_model: deepseek-v4-pro
author_model_version: unversioned
author_model_configuration: Alibaba Cloud Studio endpoint=https://token-plan.ap-southeast-1.maas.aliyuncs.com/apps/anthropic; route=alibaba-deepseek-v4-pro; requested_model=deepseek-v4-pro; model_source=response.model; account_override=false

# Loyal Opposition Review — Antigravity Prompt Transport Correction (Harness H, alibaba-cloud-studio)

**Document:** `gtkb-wi5217-antigravity-prompt-transport`
**Reviewed version:** `bridge/gtkb-wi5217-antigravity-prompt-transport-001.md`
**Proposal author:** Prime Builder Codex/A (gpt-5.5)
**Reviewer:** Alibaba Cloud Studio Loyal Opposition, harness H
**Date:** 2026-07-13 UTC
**Verdict:** GO

## Decision

GO. The proposal is sound, bounded, and ready for Prime Builder implementation. The defect is real, the root cause is precisely identified, and the proposed correction is the minimal surgical change needed.

## Defect Confirmation

The existing production code path is confirmed broken:

1. `_dispatch_prompt` (line 3898) detects Antigravity C and injects the rules block.
2. The full prompt is written to `<dispatch_id>.stdin.log` sidecar (line 5088-5090).
3. `_dispatch_target_uses_stdin_prompt` (line 4056-4065) returns True for C because the harness registry declares `"stdin": true` and `"prompt_transport": "stdin"`.
4. `_command_without_prompt_payload` (line 4068-4086) removes the prompt value from argv, but its `prompt_value_flags` set is `{"-p", "--prompt"}` — it does **not** recognize `--print` as a value-taking flag. The prompt value is removed by literal match (line 4078), leaving `["agy", "--print", "--print-timeout", "30m", ...]`.
5. `agy --print` consumes the next token (`--print-timeout`) as its user prompt, making the actual assignment unreachable.

The existing unit test `test_antigravity_stdin_dispatch_removes_prompt_from_child_argv` (line 5167) encodes this broken shape as the expected behavior (lines 5249-5259), confirming the defect is in the production path and not a transient configuration issue.

## Proposal Assessment

| Criterion | Finding |
|---|---|
| **Root cause identification** | Correct. The `_command_without_prompt_payload` function was designed for `-p`/`--prompt` flags and does not account for `--print` as a value-taking option in `agy`. |
| **Fix approach** | Sound. Replace the full prompt in argv with a short pointer instructing C to read the sidecar. This preserves the sidecar as the authoritative assignment text, avoids giant argv payloads, and keeps `--print` from consuming `--print-timeout`. |
| **Scope control** | Bounded to `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` only. No harness registry, routing, role, model, or lifecycle changes. |
| **Non-C harness safety** | The proposal explicitly preserves every non-C harness command and prompt transport byte-for-byte unchanged. |
| **Sidecar integrity** | The full assignment sidecar remains the authoritative text; the short argv pointer is a navigation aid, not a replacement. |
| **Risk acknowledgement** | The risk that C treats the short pointer as the full task is explicitly noted and mitigated by the pointer being explicit and the file being in-root. |

## Applicability Preflight

- packet_hash: `sha256:f5595b9e20bb1e1fd4ed0fbab3e3df7a87d9fb13fc909d27b663c46863564af8`
- bridge_document_name: `gtkb-wi5217-antigravity-prompt-transport`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5217-antigravity-prompt-transport-001.md`
- operative_file: `bridge/gtkb-wi5217-antigravity-prompt-transport-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5217-antigravity-prompt-transport`
- Operative file: `bridge\gtkb-wi5217-antigravity-prompt-transport-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-202666173` — complete six-harness governed proof and correct every discovered defect.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — cross-harness parity implementation authority.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` — verified requirement that every selected document advances independently.

## Implementation Guidance

When implementing:

1. The `_command_without_prompt_payload` function (or an Antigravity-specific path before it) must replace the full prompt with a short pointer string like `"Read and execute the full dispatch assignment from <project-root>/.gtkb-state/bridge-poller/runs/<dispatch_id>.stdin.log"`. The `--print` option must receive this pointer as its value, not as a bare token.

2. The existing test `test_antigravity_stdin_dispatch_removes_prompt_from_child_argv` must be updated to assert the new argv shape where `--print` has an intentional short pointer value, and the full prompt is absent from argv.

3. Add a focused test that verifies `--print-timeout` is never adjacent to `--print` without a value between them.

4. The sidecar write path (lines 5087-5090) is unchanged; the full assignment continues to be written to `<dispatch_id>.stdin.log`.

## Verification Gate

Before VERIFIED can be issued, the implementation must satisfy:
- `--print` always has an intentional short prompt value; `--print-timeout` can never become the user prompt.
- The short pointer references an existing in-root assignment file.
- Missing/unwritable assignment sidecars fail closed before launch.
- Existing hidden-launch, status-wrapper, lease, per-document completion, and 29,400-second lifetime behavior remains green.
- A fresh genuine C dispatch reads the real assignment and publishes a substantive canonical verdict.
- All non-C harness command-composition tests remain green.
REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder session; runtime reasoning profile not exposed

# Implementation Proposal Revision - Direct harness launch guard

bridge_kind: prime_proposal
Document: gtkb-wi4988-direct-harness-launch-guard
Version: 003
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4988-direct-harness-launch-guard-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4988-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4988

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py", "platform_tests/scripts/test_gate_fp_corpus.py", "config/governance/gate-fp-corpus.toml", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder revises WI-4988 after the NO-GO at `-002`. The design is narrowed and strengthened: the interactive directive-enforcement gate must block direct shell/PowerShell commands that launch another harness, and dispatcher-owned launches must be preserved because they occur in `scripts/dispatcher_runtime.py` outside any interactive harness PreToolUse shell hook. No shell-forgeable exemption is required for allow/deny.

If implementation adds a marker for audit metadata, the guard must not trust it as an allow signal. An interactive command that tries to spoof any dispatcher marker, environment variable, flag, or marker-file convention and then launch a harness must still be denied.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-21c5b3` records the owner prohibition. `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` records the owner decision and authorization evidence. `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `.claude/rules/bridge-essential.md` establish that the dispatcher daemon/control plane is the only automated dispatch substrate.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`, `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`, `platform_tests/scripts/test_fab14_directive_hook_coverage.py`, `platform_tests/scripts/test_gate_fp_corpus.py`, `config/governance/gate-fp-corpus.toml`, `scripts/dispatcher_runtime.py`, and `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`.

## Specification Links

- `SPEC-INTAKE-21c5b3` - owner-stated governance requirement prohibiting direct harness-to-harness invocation and requiring mechanical enforcement.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner decision evidence authorizing this enforcement work.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher is a black-box service; harnesses must not trigger, command, or suspend one another.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - cross-harness work must flow through the centralized dispatch service.
- `.claude/rules/bridge-essential.md` - dispatcher daemon is the canonical bridge automation path; manual owner assignment/scanning is available when daemon is unhealthy and no other automated fallback substrate is valid.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - enforcement must apply across harness/tooling paths, with gaps tracked explicitly.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - classifier must be deterministic; no model/API classifier is allowed inside the gate.
- `SPEC-AUQ-POLICY-ENGINE-001` - gate precision and false-positive control are required for owner-decision/policy enforcement.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook surfaces are live interception boundaries on this Windows host class and must be covered.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, revision, implementation report, and verification must remain tied to live bridge state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner directive, spec intake, work item, proposal, tests, and verification remain traceable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve the artifact graph from owner decision through implementation and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal updates a NO-GO thread through REVISED and must preserve lifecycle state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete links are present and mapped to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must be verified by tests derived from this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation stays in the GT-KB platform root and outside adopter application scope.
- `GOV-STANDING-BACKLOG-001` - WI-4988 remains the MemBase work item authority for this enforcement change.

## Prior Deliberations

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner decision: no GT-KB harness may directly launch, trigger, command, supervise, or otherwise interact with another AI harness as a standby or backup path.
- `.claude/rules/bridge-essential.md` - dispatcher-only substrate rule: the dispatcher daemon is the canonical automation path; manual owner assignment/scanning is available when unhealthy; no other automated fallback substrate is valid.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher-owned black-box service and harness-isolation rationale after prior harness-triggered storm.
- `WI-4977` - resolved headless dispatch stability item; adjacent history for why dispatcher-mediated work must be stabilized rather than bypassed.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity/history for relying on the shared directive-enforcement surface in modern Codex on Windows.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - prior cross-harness enforcement matrix.
- Deliberation Archive search noted by LO for `"direct harness to harness invocation ban dispatcher only"` returned no direct matches beyond the new owner-decision record; the records above are adjacent/governing history.

## Owner Decisions / Input

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibition and mechanical-enforcement directive.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4988-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering WI-4988.

## Findings Addressed

### N1 - Prior Deliberations placeholder

Response: corrected. The revision replaces the placeholder with the owner decision, dispatcher-only substrate rule, dispatcher architecture ADR, WI-4977, Codex hook parity, and cross-harness enforcement matrix.

### N2 - Dispatcher-exemption forgery resistance

Response: corrected. The implementation must not rely on a shell-inheritable exemption for allow/deny. The guard will operate on interactive command text seen by shared directive-enforcement hooks. Dispatcher-owned worker launches in `scripts/dispatcher_runtime.py` use Python `subprocess.Popen` from the dispatcher process and do not traverse the interactive shell PreToolUse hook surface; preserving that path is the exemption.

If the implementation adds an audit marker to dispatcher-spawned child environments or metadata, the guard must ignore it when deciding whether an interactive command is allowed. The test suite must include adversarial spoof-denial cases such as `GTKB_DISPATCHER_MEDIATED=1 claude ...`, `$env:GTKB_DISPATCHER_MEDIATED=1; claude ...`, marker-file creation followed by `codex exec ...`, and any proposed flag/marker convention. All spoof attempts must still be denied.

### N3 - False-positive corpus and verification-plan filler

Response: corrected. The target paths now include `config/governance/gate-fp-corpus.toml` and `platform_tests/scripts/test_gate_fp_corpus.py`. The implementation must add mention-not-launch pass cases and launch-signature block cases, including PowerShell call operators and `Start-Process`.

## Revised Scope

- Add deterministic command classification to `groundtruth_kb.enforcement.check_bash_command` for direct harness launch signatures.
- Deny launch/trigger commands for Claude Code, Codex, Ollama, Cursor, OpenRouter, Antigravity/Gemini wrappers, and known script shims when invoked from interactive shell surfaces.
- Cover Bash/cmd-style command heads, Windows `.exe` suffixes, PowerShell call operator forms such as `& claude ...`, and `Start-Process claude`.
- Preserve non-launch mentions and status/read commands, including bridge slugs or filenames containing harness names, `gt bridge show ...`, `python scripts/verify_codex_dispatch.py`, and `rg claude bridge/`.
- Preserve dispatcher-owned launches by not applying the interactive shell guard to `dispatcher_runtime.py` subprocess calls. Add tests proving dispatcher command composition is still possible while spoofed interactive exemptions are denied.
- Return remediation text that names `SPEC-INTAKE-21c5b3` / the direct-harness ban and directs agents to bridge files, `gt bridge dispatch` control-plane status/config surfaces, or independent owner/manual harness operation.

## Pre-Filing Preflight Subsection

Candidate preflights will be run against this completed revision body before live filing through `.codex/skills/bridge/helpers/revise_bridge.py file`:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4988-direct-harness-launch-guard --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4988-direct-harness-launch-guard --content-file <candidate>`

Observed result before filing:

- Applicability preflight exit 0, `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:309da6bb6023dfbf704f0e549f867cecd2f8396294864cc87078ac1b25e5df75`.
- Clause preflight exit 0; must_apply 4, evidence gaps 0, blocking gaps 0.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-21c5b3` | Unit tests deny direct harness-launch commands and assert remediation text for Claude, Codex, Ollama, Cursor, OpenRouter, and Antigravity/Gemini signatures. |
| `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` | Implementation report cites the owner decision and demonstrates that direct fallback launches are denied. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Dispatcher-runtime tests prove automated launches remain inside dispatcher runtime/control-plane code and no interactive harness fallback path is added. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests confirm dispatcher-mediated command composition remains allowed because it is outside the interactive shell hook path. |
| `.claude/rules/bridge-essential.md` | Implementation report confirms no alternate automated bridge substrate is introduced. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Hook coverage tests confirm the shared directive-enforcement adapter reaches Claude, Codex, and Cursor command surfaces. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Static/unit tests show the classifier is deterministic pattern logic only, with no LLM/API call path. |
| `SPEC-AUQ-POLICY-ENGINE-001` | False-positive corpus passes for mention-not-launch commands and true-positive corpus blocks launch commands. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex hook coverage tests confirm the Bash PreToolUse batch still includes directive enforcement on this Windows Codex surface. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge preflights pass; implementation and verification stay in the numbered bridge chain. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report ties owner decision, spec intake, WI-4988, tests, and verification evidence together. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Changed-file/report evidence preserves the owner decision -> requirement -> WI -> tests -> verification artifact graph. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Revision uses the NO-GO -> REVISED lifecycle and implementation report preserves the state transition. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes with no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this spec-to-test map and executes the focused tests before requesting VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal metadata and target paths are present and pass bridge compliance. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and changed-file evidence stay under `E:\GT-KB` platform paths. |
| `GOV-STANDING-BACKLOG-001` | Implementation report references WI-4988 as the backlog authority and does not create duplicate work. |

## Acceptance Criteria

- Direct interactive shell/PowerShell commands for `claude`, `codex exec`, `ollama`, `cursor`, `openrouter`, `antigravity`, `agy`, `gemini`, and project harness shims are denied.
- Spoofed dispatcher exemptions from an interactive shell are denied.
- Mention-not-launch commands and read/status commands continue to pass, including names containing `claude`, `codex`, `cursor`, or `ollama`.
- Dispatcher-runtime tests prove dispatcher-owned subprocess command composition still works without passing through or trusting the interactive shell exemption path.
- Denial output names the direct-harness ban and points to governed bridge/dispatcher control surfaces.

## Risk And Rollback

Risk is moderate because overmatching could block legitimate status/read work and undermatching could leave the prohibited direct-launch path open. The false-positive corpus and adversarial spoof tests are therefore part of the implementation scope.

Rollback is a revert of the source/config/test changes. Bridge files, deliberations, work-item history, and PAUTH records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `platform_tests/scripts/test_gate_fp_corpus.py`
- `config/governance/gate-fp-corpus.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

## Recommended Commit Type

`feat`

NEW
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: 2026-06-13-codex-wi-4516-proposal
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder role; approval_policy=never
author_metadata_source: Codex session explicit metadata for WI-4516 proposal filing

bridge_kind: prime_proposal
Document: gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-WI-4516-BASH-BRIDGE-HARDENING
Project: PROJECT-GTKB-BRIDGE
Work Item: WI-4516
Related Work Item: WI-4468

target_paths: ["scripts/sdk_bridge_bash_guard.py", "scripts/openrouter_harness.py", "scripts/ollama_harness.py", "scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

implementation_scope: source
authorization_scope: source,test_addition,governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# Implementation Proposal - WI-4516 OpenRouter/Ollama Bash Bridge Hardening

## Summary

Implement WI-4516 by adding a shared SDK-harness Bash bridge-mutation denial helper, wiring it into both OpenRouter and Ollama `Bash` dispatch before guard subprocesses or shell execution, and extending parity/regression coverage so bridge file/index writes via Bash fail closed with no bridge mutation.

Step zero resolves the WI-4468 dependency question by inspecting the metadata path before implementation. Current evidence from the LO advisory and live code shows WI-4468 concerns the Codex implementation-report helper, while the OpenRouter/Ollama guarded `Write`/`Edit` paths already inject harness F/D author metadata into bridge-compliance guard environments. This slice therefore does not edit `scripts/impl_report_bridge.py` unless implementation inspection proves that SDK harness bridge writes depend on that helper. The PAUTH includes WI-4468 only as a bounded contingency for that step-zero dependency.

The implementation will keep bridge artifact mutation out of SDK `Bash` commands. Valid bridge artifact mutations must use the existing guarded SDK `Write`/`Edit` dispatch path or deterministic bridge helper/writer surfaces that run `ensure_author_metadata()` and serialized `bridge/INDEX.md` updates; raw shell redirection, copy/move/remove, PowerShell content cmdlets, inline Python/Node file writes, and similar shell-mediated writes to `bridge/*.md` or `bridge/INDEX.md` will be denied before subprocess execution.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files and `bridge/INDEX.md` are governed workflow authority; mutations must preserve author metadata, status-token, and index integrity.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - this implementation must not use PAUTH or SDK harness tooling to bypass bridge proposal/GO/verification controls.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the bridge bypass risk, not only happy-path harness tests.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal explicitly links the governing specs that drive implementation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal metadata links the work to `PROJECT-GTKB-BRIDGE`, `WI-4516`, and the active PAUTH.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - Ollama full-parity tool dispatch must be fail-closed through GT-KB guard semantics.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - guarded bridge writes from Ollama must preserve author metadata injection; the Bash denial must not regress this.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex/SDK harness hook parity requires Windows-compatible fallback behavior and parity tests rather than relying on a single harness path.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - OpenRouter/Ollama harness capabilities must satisfy the same safety floor expected of GT-KB coding harnesses.
- `GOV-STANDING-BACKLOG-001` - WI-4516 is the durable backlog authority for this bridge-integrity defect.

## Prior Deliberations

- `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` - owner directive and PAUTH evidence for bounded WI-4516 implementation, including WI-4468 only if needed for metadata dependency resolution.
- `DELIB-20263134` - compressed VERIFIED WI-4477 bridge thread; source incident where OpenRouter/Ollama readiness verification exposed bridge-provenance drift and invalid/unindexed bridge artifacts.
- `DELIB-20261845` - VERIFIED bridge-propose helper caller migration to validated bridge writer; prior decision that bridge mutation helpers should use validated writer paths instead of ad hoc file/index edits.
- `DELIB-20261406` - GO verdict for caller migration to validated bridge writer; supports routing bridge artifacts through writer/compliance paths.
- `DELIB-20263076` - ordered fallback routing GO context for SDK harness routing parity and provider behavior.
- Advisory report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-13-WI-4516-openrouter-bash-bridge-bypass.md` provides direct code evidence, temp-dir reproduction, and recommended fix shape.

## Owner Decisions / Input

Owner decision `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` captures Mike's 2026-06-13 instruction to implement WI-4516 from the LO advisory, resolve WI-4468 if needed as step zero, hard-deny OpenRouter/Ollama `Bash` bridge writes, route bridge mutations through guarded writer paths, add parity/regression tests, and verify harnesses no longer bypass bridge compliance.

No further owner input is needed before LO review. The active PAUTH is `PAUTH-PROJECT-GTKB-BRIDGE-WI-4516-BASH-BRIDGE-HARDENING`; it covers only WI-4516 plus WI-4468 as a dependency contingency, permits source/test/governance-evidence mutation, and forbids deploy, force-push, spec deletion, credential lifecycle work, and bridge-GO bypass.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and the Ollama/OpenRouter parity specs are enough to require a fail-closed SDK `Bash` denial for bridge artifact mutation. No new formal specification is needed because the acceptance criterion is a direct enforcement of existing bridge authority: shell-mediated writes must not be a weaker path than guarded `Write`/`Edit` dispatch.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use only synthetic bridge file names and no credential-like fixtures in tests or proposal text. | Bridge helper credential scan, focused pytest, and diff review. | |
| CQ-PATHS-001 | Yes | Mutate only the listed SDK harness source files and platform test modules under the project root. | Implementation-start target-path packet plus `git diff --name-only` review. | |
| CQ-COMPLEXITY-001 | Yes | Keep the detector as a small shared helper with focused regex predicates and simple call-site wiring. | Ruff plus direct unit tests for allowed reads and denied mutation shapes. | |
| CQ-CONSTANTS-001 | Yes | Centralize bridge Bash mutation patterns in `scripts/sdk_bridge_bash_guard.py`; do not duplicate command-pattern literals across harnesses. | Ruff and unit tests around the shared helper. | |
| CQ-SECURITY-001 | Yes | Fail closed before subprocess execution for bridge artifact mutations; preserve guarded Write/Edit metadata and guard sequences. | OpenRouter/Ollama harness tests assert no command runner invocation and unchanged bridge state on denial. | |
| CQ-DOCS-001 | N/A | Runtime harness hardening only; no user-facing documentation surface is changed in this slice. | Diff review. | No docs surface change. |
| CQ-TESTS-001 | Yes | Add direct helper tests, OpenRouter parity tests, Ollama regression tests, and verify-script coverage. | Focused pytest commands listed in the verification plan. | |
| CQ-LOGGING-001 | N/A | No new logging stream; denial uses existing harness error path with an actionable message. | Diff review and tests asserting error text. | No logging surface change. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped Ruff, Ruff format check, and harness parity before implementation report. | Commands and observed results recorded in the post-implementation report. | |

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_sdk_bridge_bash_guard.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py -q --tb=short`. Expected result: Bash attempts to write `bridge/*.md` and `bridge/INDEX.md` are denied before command runner/subprocess execution; bridge files are absent and index content is unchanged.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: inspect guard call records in the same focused tests. Expected result: denied Bash bridge mutations do not run only destructive/formal/start gates and then mutate; no bypass path remains.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: run Ollama harness regression tests and `platform_tests/scripts/test_verify_ollama_dispatch.py`. Expected result: Ollama dispatch exposes the bridge-Bash denial in its guard verification surface.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: run existing and new Ollama/OpenRouter guarded Write/Edit tests. Expected result: guarded bridge Write/Edit still pass author metadata env fields for harness D/F.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` and `GOV-HARNESS-ONBOARDING-CONTRACT-001`: run OpenRouter parity tests mirroring Ollama coverage. Expected result: OpenRouter has explicit parity coverage for guarded Write/Edit and Bash bridge-denial behavior.
- Formatting and lint floor: run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/sdk_bridge_bash_guard.py scripts/openrouter_harness.py scripts/ollama_harness.py scripts/verify_ollama_dispatch.py platform_tests/scripts/test_sdk_bridge_bash_guard.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_verify_ollama_dispatch.py` and matching `ruff format --check`. Expected result: target files are lint-clean and formatted.
- Harness parity: run `groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --markdown`. Expected result: harness parity checks pass or any unrelated pre-existing failure is documented in the implementation report.

## Risk / Rollback

Risk is concentrated in shell-command intent detection. Parsing arbitrary shell is inherently lossy, so the implementation deliberately denies common mutating forms when they mention `bridge/*.md` or `bridge/INDEX.md` instead of attempting to extract and validate shell-written bridge content. False positives are acceptable for bridge artifact writes because SDK harnesses have non-Bash guarded writer paths; read-only bridge inspection through Bash should remain allowed and covered by regression tests.

Rollback is a single-commit revert of the shared guard helper, OpenRouter/Ollama wiring, and focused test changes. No production deployment or credential lifecycle action is in scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted in `bridge/INDEX.md` through the Codex non-bypass bridge writer. No prior bridge file is rewritten or deleted. `bridge/INDEX.md` remains canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix`: the change closes a bridge-integrity defect in SDK harness command dispatch and adds regression coverage.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

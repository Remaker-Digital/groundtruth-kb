REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-auto-builder-20260619T2007Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop; proposal-only revision; no implementation mutation

bridge_kind: prime_proposal
Document: gtkb-lo-verified-commit-atomicity
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC
Responds-To: bridge/gtkb-lo-verified-commit-atomicity-002.md

Project Authorization: PAUTH-WI-4680-VERIFIED-COMMIT-ATOMICITY
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4680

target_paths: [".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-review-gate.md", ".claude/rules/loyal-opposition.md", ".claude/skills/verify/SKILL.md", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/verify/SKILL.md", ".agent/skills/MANIFEST.json", ".api-harness/skills/verify/SKILL.md", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: bridge lifecycle rule, LO verification helper, generated harness guidance, dispatch prompts, regression tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# Revised Implementation Proposal - Make LO VERIFIED verdict recording atomic with final commit

## Revision Claim

This revision responds to the Loyal Opposition `NO-GO` at `bridge/gtkb-lo-verified-commit-atomicity-002.md`.

Changes from version 001:

- The `Requirement Sufficiency` subsection now uses the exact operative state `Existing requirements sufficient`.
- The subsection explicitly states that this proposal preserves and augments the Requirement Sufficiency gate; it does not amend, weaken, bypass, or replace that gate even though `.claude/rules/file-bridge-protocol.md` is in target scope.
- The substantive WI-4680 scope, target paths, acceptance criteria, and verification plan are unchanged.

No source, test, configuration, formal artifact, MemBase, deployment, credential, or Git history mutation is performed by this revision.

## Findings Addressed

### Primary Finding: Missing Mandatory Requirement Sufficiency Subsection

Accepted for mechanical compliance. Version 001 did include a `## Requirement Sufficiency` heading and stated that requirements were sufficient, but it did not use the exact operative phrase requested in the NO-GO. This revision replaces that wording with `Existing requirements sufficient`.

### Secondary Observation: Circular Dependency on Target Rule File

Addressed. This proposal targets `.claude/rules/file-bridge-protocol.md` to add the new VERIFIED commit-finalization invariant. It does not amend or relax the existing implementation-proposal Requirement Sufficiency gate. The implementation must preserve that gate and may only augment bridge lifecycle language around VERIFIED finalization.

## Summary

This proposal fixes WI-4680, a P0 bridge lifecycle defect reported by the owner on 2026-06-19.

Today, Loyal Opposition can record a terminal `VERIFIED` verdict while the implementation report, verdict artifact, and verified source changes are still only dirty or staged worktree state. That makes the git commit a post-verification best-effort action. When the commit is blocked or skipped, the bridge thread is terminal but the repository does not contain the verified change as durable git history.

The implementation will make `VERIFIED` a commit-finalization outcome. A `VERIFIED` verdict is valid only when the verified work and the verdict artifact are committed by the same local git transaction. If that transaction cannot be created, the verifier must fail closed and must not leave the bridge thread in terminal `VERIFIED`.

## Defect / Reproduction

Observed defect class:

1. Prime Builder completes implementation and files a post-implementation report.
2. Loyal Opposition records `VERIFIED` as the latest bridge status.
3. The verified artifacts remain uncommitted, or commit finalization is attempted later.
4. A stale implementation-start packet, dirty overlap, shell-composition issue, hook failure, or unavailable git writer can block the later commit.
5. The bridge now claims terminal verification without the repository containing the verified change in a local commit.

The live trigger was the production-readiness cleanup flow around `gtkb-dispatch-runtime-health-readiness-repair`, where terminal `VERIFIED` state and stale packet behavior exposed that `VERIFIED` closure and git finalization were not one transaction.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Bridge files and dispatcher/TAFE state are governed workflow authority; terminal bridge state must correspond to durable repository state.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `VERIFIED` must remain evidence-backed and must now include commit finalization evidence, not only test evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The implementation remains under a bounded project authorization and does not bypass proposal, GO, implementation-start, or verification gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The owner-reported defect is preserved as a durable work item, project authorization, bridge proposal, and eventual verification record.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal links the governing specs, work item, target paths, acceptance criteria, and tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This implementation-targeting proposal carries project authorization, project, work item, and inline JSON `target_paths`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex, Antigravity, and API harness guidance generated from canonical skill content must stay in sync where the verification procedure changes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The owner directive is captured as a work item, authorization evidence, proposal, tests, and later verification evidence instead of transient chat memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The owner-reported defect triggers durable backlog, proposal, implementation report, and verification lifecycle artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target files are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4680 is the MemBase backlog source of truth for this defect.

## Prior Deliberations

- `DELIB-20265286` - Owner authorization for this WI-4680 lifecycle repair.
- `bridge/gtkb-protected-commit-authorization-gate-001.md` through `bridge/gtkb-protected-commit-authorization-gate-004.md` - Prior WI-4613 thread that enforced "VERIFIED before commit"; this proposal is the follow-on for "VERIFIED and commit are one finalization transaction."
- `WI-4613` - Resolved predecessor work item, "Enforce Loyal Opposition VERIFIED verdict before commit for all harnesses."
- `WI-3497` / `bridge/gtkb-commit-scope-bundling-detection-slice-1-001.md` - Adjacent commit-scope contamination defect; relevant because same-transaction verification must stage only the verified target paths plus the verdict artifact.
- `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-003.md` / `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-006.md` - Adjacent packet-clearing evidence showing why stale VERIFIED packets and terminal states must be handled by deterministic lifecycle machinery.

## Owner Decisions / Input

- `DELIB-20265286` records the owner directive from 2026-06-19: "We need to change the way LO handles VERIFIED verdicts to ensure that the VERIFIED work is committed at the same time the verdict is recorded. In essence: the commit should be the final step for VERIFICATION, not a post-verification, best-effort action."
- `PAUTH-WI-4680-VERIFIED-COMMIT-ATOMICITY` authorizes the bounded implementation for WI-4680. It forbids push, deployment, credential lifecycle changes, retired poller restoration, and formal artifact mutation without a separate approval packet.

No additional owner input is needed for this proposal.

## Requirement Sufficiency

Existing requirements sufficient.

The owner directive adds a lifecycle invariant but does not require a new formal GOV/DCL before implementation. The invariant is implementable under the existing bridge authority, mandatory verification, project authorization, generated-adapter parity, and commit-time gate requirements cited above.

This proposal preserves the existing Requirement Sufficiency gate. The requested implementation may augment `.claude/rules/file-bridge-protocol.md` with VERIFIED commit-finalization semantics, but it must not amend, weaken, bypass, or replace the implementation-proposal Requirement Sufficiency requirement itself. If implementation discovers that `VERIFIED` must carry a new formal schema field beyond bridge-file prose and commit evidence, Prime Builder will file that as a separate formal artifact change rather than smuggling it into this repair.

## Proposed Scope

Implement a deterministic `VERIFIED` finalization path with these semantics:

1. A `VERIFIED` verdict cannot be published as the latest bridge state unless the same verification transaction creates a local git commit.
2. The commit must include the verified implementation/report paths and the new `VERIFIED` verdict artifact.
3. The commit must not include unrelated dirty or staged paths. The helper must show and validate the final staged set before commit creation.
4. If commit creation fails, the verifier must fail closed: no terminal `VERIFIED` is published, and the failure is reported as a blocked verification or `NO-GO` path rather than leaving terminal bridge state behind.
5. The `VERIFIED` verdict should record commit-finalization evidence that is knowable before the commit, such as intended subject, staged path list, tree/diff fingerprint, and same-transaction statement. The final commit SHA can be reported by the helper after success; it cannot be self-embedded in the committed verdict file without changing the commit hash.
6. The helper must use a clean git finalization invocation, with no shell pipe, redirect, command chain, force flag, or other composition that disqualifies the git-finalization exemption in `scripts/implementation_start_gate.py`.
7. Generated harness guidance and dispatch prompts must tell LO workers that `VERIFIED` is a commit-finalization outcome, not a file-only verdict.

The implementation may either extend `.claude/skills/verify/helpers/write_verdict.py` or add a focused helper alongside it, provided the public LO procedure uses the atomic helper for `VERIFIED`.

## Explicitly Out Of Scope

- Pushing to any remote.
- Rewriting historical bridge verdict files.
- Restoring the retired OS poller or smart poller.
- Changing the meaning of `GO` or `NO-GO`.
- Weakening spec-derived verification requirements.
- Weakening or bypassing the Requirement Sufficiency gate.
- Broad cleanup of unrelated dirty worktree state.
- Formal GOV/DCL/ADR mutation without a separate approval packet.

## Acceptance Criteria

1. A positive `VERIFIED` path creates exactly one local commit containing the verified work and the `VERIFIED` verdict artifact.
2. A failing commit path does not leave the bridge thread latest status as `VERIFIED`.
3. A staged-set guard rejects unrelated staged paths before commit finalization.
4. The LO verification skill and all generated harness-facing verify guidance describe commit finalization as mandatory for `VERIFIED`.
5. Ollama and OpenRouter LO prompts no longer instruct workers to merely write a `VERIFIED` verdict for post-implementation reports; they must use or defer to the finalization helper.
6. Existing Prime implementation-start behavior remains intact: terminal `VERIFIED` still blocks new implementation packets, while the sanctioned plain `git commit` finalization path remains allowed.
7. The implementation report for this work includes the exact local commit SHA created by the new verification-finalization path when this fix is later verified.

## Specification-Derived Verification Plan

| Specification / governing surface | Test or verification command | Expected evidence |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; WI-4680 acceptance criteria | `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short` | Positive flow commits the verified target paths and `VERIFIED` verdict together; failure flow leaves no terminal `VERIFIED` bridge state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; WI-3497 adjacent risk | `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short -k staged` | Unrelated staged files are rejected before commit finalization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short -k spec_mapping` | `VERIFIED` finalization still requires executed spec-derived test evidence before commit. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short` | Existing terminal `VERIFIED`, post-GO `NO-GO`, and stale packet clearing behavior remains correct. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short` | LO dispatch prompts require the commit-finalization helper or fail-closed behavior for `VERIFIED`. |
| Generated adapter source-of-truth discipline | `python scripts/generate_codex_skill_adapters.py --check --update-registry`; `python scripts/generate_antigravity_skill_adapters.py --check --update-registry`; `python scripts/generate_api_skill_adapters.py --check` | Generated verify skill adapters and manifests are synchronized with canonical `.claude/skills/verify/SKILL.md`. |
| Python code quality | `python -m ruff check .claude/skills/verify/helpers/write_verdict.py scripts/implementation_start_gate.py scripts/implementation_authorization.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py` | Lint passes for changed Python files. |
| Python formatting | `python -m ruff format --check .claude/skills/verify/helpers/write_verdict.py scripts/implementation_start_gate.py scripts/implementation_authorization.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py` | Formatting check passes for changed Python files. |
| Bridge proposal/report compliance | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-verified-commit-atomicity`; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-verified-commit-atomicity` | No missing required specs or blocking clause gaps for the proposal and later implementation report. |

## Risk / Rollback

Risk: the self-referential nature of commit SHA evidence means the verdict file cannot contain its own final commit SHA while also being part of that commit. The implementation must avoid promising impossible self-reference. It should record pre-commit evidence in the verdict and report the final SHA after successful commit creation.

Risk: committing from LO changes the operational boundary between reviewer and repository finalizer. This is intentional per the owner directive, but the helper must keep the committed scope narrow and transparent.

Rollback: revert the implementation commit touching the listed target paths. Historical bridge files remain append-only; no bridge file deletion is needed.

## Recommended Commit Type

`fix`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

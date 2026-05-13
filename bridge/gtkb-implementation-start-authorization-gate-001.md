NEW

# Implementation Proposal - Implementation Start Authorization Gate

**Document:** `gtkb-implementation-start-authorization-gate`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Active workspace:** `E:\GT-KB`
**Recommended commit type:** `feat:`
**target_paths:** ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", ".claude/hooks/implementation-start-gate.py", ".codex/gtkb-hooks/implementation-start-gate.cmd", ".claude/settings.json", ".codex/hooks.json", ".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-review-gate.md", "config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_hook_registration_parity.py"]

## Claim

GT-KB already states the bridge rule in prose: no implementation may begin without an implementation proposal that has received Loyal Opposition `GO`, and proposals must cite every relevant governing specification. The current mechanical enforcement is narrower than that rule. It blocks malformed bridge proposal/report content and some formal-artifact mutations, but it does not reliably stop ordinary source, configuration, hook, test, or script implementation from starting before a `GO` authorization exists.

The owner has now identified the specific governance gap: implementation should be mechanically forced to start from an approved plan, and if existing requirements are insufficient for citation, implementation should first require approval of new or revised requirements. This proposal requests review for a focused implementation-start authorization gate that makes that behavior enforceable for both Claude Code and Codex.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is the authoritative bridge queue and latest status source.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite every relevant governing specification before approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implemented work must carry forward linked specifications and execute spec-derived verification before `VERIFIED`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner requirements, implementation plans, review findings, and lifecycle transitions should be preserved as durable artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all GT-KB live implementation and governance files remain inside `E:\GT-KB`; no Agent Red or archive path is live scope for this work.
- `.claude/rules/codex-review-gate.md` - active rule: no implementation without Loyal Opposition review when the bridge is active; implementation includes code changes, KB mutations, configuration changes, deployments, and state-changing repository operations.
- `.claude/rules/file-bridge-protocol.md` - active bridge lifecycle and mandatory specification-linkage protocol.
- `.claude/hooks/bridge-compliance-gate.py` - existing bridge document gate; currently validates bridge markdown and asks on target-path collisions but does not hard-block every implementation write without a GO authorization.
- `.claude/hooks/formal-artifact-approval-gate.py` - existing formal artifact mutation gate; this proposal must complement it rather than weaken it.
- `.claude/hooks/spec-classifier.py` - existing prompt-time specification-language reminder; this proposal adds a hard implementation-start boundary where reminder-only behavior is insufficient.
- `.claude/settings.json` and `.codex/hooks.json` - cross-harness hook registration surfaces that must both enforce the same policy.
- `DELIB-S321-IMPL-PROPOSAL-SPEC-LINKAGE` - owner directive that implementation proposals must be linked to any and all relevant specifications.
- `DELIB-S321-SPEC-CREATION-STANDING-AUTH` - owner directive that necessary specification creation is authorized and implementation must not be proposed when unspecified.
- `DELIB-1404` - candidate-specification backlog advisory identifying partial enforcement around proposal/spec/scope linkage, test-before-implementation, and chat-derived specification approval.
- `DELIB-1860` and `DELIB-1859` - prior Loyal Opposition NO-GOs explaining that non-empty spec citation is not enough and that enforcement must occur at bridge submission/implementation boundaries, not only later review or git commit.

## Prior Deliberations

Deliberation searches were run on 2026-05-12 for implementation proposal specification linkage, bridge mechanical enforcement, requirement sufficiency, and implementation-start approval. Relevant records:

- `DELIB-S321-IMPL-PROPOSAL-SPEC-LINKAGE` - direct owner decision: it must not be possible to submit an implementation proposal that is not linked to all relevant specifications.
- `DELIB-S321-SPEC-CREATION-STANDING-AUTH` - direct owner decision: necessary specification creation is authorized, and implementation must not be proposed when unspecified.
- `DELIB-1860` - Loyal Opposition NO-GO on the first spec-coverage architecture proposal; it found that enforcement must be at the bridge submission boundary and must close relevance gaps, not merely validate at commit time.
- `DELIB-1859` - Loyal Opposition NO-GO on the revised spec-coverage architecture proposal; it found that pending requirement/specification discipline and deterministic relevance closure were still under-specified.
- `DELIB-1714` - Loyal Opposition GO for the Owner Decisions / Input bridge gate, showing the accepted pattern for moving from a soft bridge rule to hook-enforced bridge behavior.
- `DELIB-1404` - candidate specification backlog advisory; it explicitly identifies proposal/spec/scope linkage and test-before-implementation as only partially mechanically enforced.
- `DELIB-1646` - harness parity baseline NO-GO; relevant because enforcement cannot be Claude-only when Codex may operate as Prime Builder.

## Owner Decisions / Input

The owner stated on 2026-05-12:

> The bridge protocol is important. I have observed that there is no mechanical enforcement or reliable behavior that forces all implementation to be planned, and all implementation to begin with approval of new requirements is existing requirements are not sufficient for citation.

Interpretation for this proposal: this is a requirement-level defect report and implementation request. It authorizes filing an implementation proposal for a mechanical enforcement gate. It is not treated as direct approval to bypass bridge review, mutate formal GOV/ADR/DCL/SPEC records, or begin source implementation before this proposal receives `GO`.

## Current-State Evidence

- `.claude/rules/codex-review-gate.md` already states the policy: before Prime Builder modifies source code, KB records, configuration files, deployment state, or repository state, a bridge proposal must have Loyal Opposition `GO`.
- `.claude/hooks/bridge-compliance-gate.py` is registered in `.claude/settings.json` for `Write|Edit`, but it is not registered in `.codex/hooks.json` and it primarily validates bridge markdown proposal/report content.
- The same hook only emits an `ask` decision when a pending/NO-GO proposal has `target_paths` matching a write target; it does not hard-deny all implementation paths lacking a `GO` authorization.
- `.claude/hooks/formal-artifact-approval-gate.py` and the Codex wrapper `.codex/gtkb-hooks/formal-artifact-approval.cmd` block some formal-artifact mutations, but they do not cover ordinary source/configuration implementation.
- `.claude/hooks/spec-classifier.py` is registered in both harnesses as a prompt-time reminder. Reminder behavior does not mechanically prevent implementation when requirements are missing or insufficient.
- Current Codex editing normally uses `apply_patch` and shell tools; current Claude Code editing normally uses `Write|Edit|MultiEdit` and shell tools. The proposed enforcement must cover the actual mutation tools, not only one vendor's write hook.

## Proposed Implementation

### IP-1 - Shared Implementation Authorization Model

Create a shared authorization model for implementation work, tentatively persisted under `.gtkb-state/implementation-authorizations/current.json` and produced by a small verifier command such as:

```powershell
python scripts/implementation_authorization.py begin --bridge-id <document-name>
```

The command must:

- read live `bridge/INDEX.md`;
- require the selected document's latest status to be `GO`;
- identify the operative approved proposal and GO verdict file;
- require concrete `Specification Links` in the approved proposal;
- require concrete implementation scope/target paths for the approved proposal;
- require a spec-derived test plan in the approved proposal;
- reject proposals with placeholder links, `pending:` requirements, unresolved requirement-gap markers, or an explicit statement that existing requirements are insufficient;
- emit a session-scoped authorization packet containing bridge id, proposal file, GO file, authorized path globs, linked specification IDs/paths, packet hash, creation time, and expiry.

The authorization packet is not a substitute for bridge `GO`; it is a local, machine-readable proof that the current implementation session is scoped to one GO'd bridge proposal.

### IP-2 - Requirement Sufficiency Gate

Extend bridge proposal requirements and hook checks so implementation cannot start from an unspecified requirement gap.

Implementation proposals that touch source, configuration, hooks, scripts, tests, deployment behavior, KB mutation behavior, or repository state must include a `Requirement Sufficiency` subsection with one of two states:

- `Existing requirements sufficient` - cites the existing governing specs/rules/ADRs/DCLs and explains why no new requirement is needed.
- `New or revised requirement required before implementation` - identifies the missing requirement and limits immediate work to requirement/specification capture through the governed approval path.

The implementation authorization command must deny source/config/test implementation when the approved proposal is in the second state, when any cited requirement is unresolved/pending, or when the proposal uses placeholders such as `TBD`, `pending`, `no relevant`, or `not applicable` in the specification-linkage surface.

This proposal does not directly create a new GOV/DCL/SPEC record. If Loyal Opposition decides the requirement-sufficiency rule needs a formal DCL before code implementation, the required revision should split this into a formal-artifact-only first slice and a code-enforcement second slice.

### IP-3 - Shared Hook: Implementation Start Gate

Add a shared hook implementation, tentatively `scripts/implementation_start_gate.py`, with thin harness wrappers only where needed.

The gate must hard-deny protected implementation mutations unless a valid authorization packet exists and the target path or mutation command is within the packet's authorized path globs.

Protected mutation classes:

- source code and scripts under `scripts/**`, `groundtruth-kb/src/**`, and relevant package/application source paths;
- tests under `tests/**`, `platform_tests/**`, and `groundtruth-kb/tests/**`;
- hook/config/runtime surfaces including `.claude/hooks/**`, `.claude/settings.json`, `.codex/hooks.json`, `.codex/gtkb-hooks/**`, `config/**`, `.github/**`, `pyproject.toml`, and `groundtruth.toml`;
- KB mutation commands and direct database writes not already blocked by the formal-artifact gate;
- deployment, git-history, release, packaging, and repository state-changing commands.

Allowed without implementation authorization:

- read-only exploration and status commands;
- running existing tests and linters without writing artifacts;
- filing bridge proposals/reviews/reports under `bridge/**`;
- writing additive Loyal Opposition reports under `independent-progress-assessments/**`;
- formal requirement/specification capture actions only when separately approved by the formal-artifact approval gate;
- emergency bridge-function repair under the existing bridge-essential authority, but only when the bridge is unusable and the repair path records an incident/report afterwards.

### IP-4 - Harness Coverage

Register the shared gate for both Claude Code and Codex.

Claude Code target registration:

- `.claude/settings.json` PreToolUse for `Write|Edit|MultiEdit|Bash` or the closest supported matcher set;
- direct Python command to the shared hook.

Codex target registration:

- `.codex/hooks.json` PreToolUse for shell/Bash mutation commands and `apply_patch` if supported by the Codex hook schema;
- `.codex/gtkb-hooks/implementation-start-gate.cmd` wrapper for Windows parity where needed;
- a parity test that fails if Claude and Codex do not both register the gate across their actual mutation surfaces.

If Codex PreToolUse cannot intercept `apply_patch`, the implementation report must say so explicitly and Loyal Opposition should not mark the guarantee complete until an equivalent enforceable Codex path exists.

### IP-5 - Parser And Decision Rules

The gate must be deterministic enough to test:

- Parse Claude Write/Edit/MultiEdit payloads for target file paths.
- Parse Codex `apply_patch` payloads for added/updated/deleted file paths.
- Parse shell/Bash commands conservatively: allow known read/test/status commands; deny or require authorization for commands that write files, mutate DB state, change git history, deploy, install hooks, or run project scripts known to mutate state.
- Normalize paths to the `E:\GT-KB` project root and deny paths outside the root for GT-KB work.
- Treat missing/invalid authorization packet as deny for protected mutation.
- Treat latest bridge status other than `GO` as deny.
- Treat target path mismatch as deny.
- Treat authorization packet expiry or bridge status drift after authorization as deny.
- Emit concise deny text naming the missing action: file a bridge proposal, wait for `GO`, run authorization begin, or capture/approve a missing requirement.

### IP-6 - Rule And Inventory Updates

Update only the rule/inventory surfaces needed to make the mechanic discoverable:

- `.claude/rules/codex-review-gate.md`: add mechanical implementation-start gate behavior and requirement-sufficiency rule.
- `.claude/rules/file-bridge-protocol.md`: add proposal metadata expectations for target paths and requirement sufficiency.
- `config/agent-control/system-interface-map.toml`: record the implementation-start gate as a cross-harness enforcement surface.

Do not replace the bridge protocol or invent an alternate queue.

## Out Of Scope

- Implementing source changes before this proposal receives `GO`.
- Creating a competing bridge queue, runtime, or poller.
- Restoring retired smart poller or retired OS poller behavior.
- Treating a non-empty but irrelevant spec citation as sufficient.
- Creating or mutating formal GOV/ADR/DCL/SPEC records without the required approval evidence.
- Requiring bridge review for read-only exploration or running existing tests.
- Production deployment, release packaging, or history rewriting.

## Specification-Derived Verification Plan

| Test ID | Requirement | Verification |
|---|---|---|
| T-no-auth-block | `.claude/rules/codex-review-gate.md`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Hook denies a protected source/config/test edit when no authorization packet exists. |
| T-go-auth-allows | `GOV-FILE-BRIDGE-AUTHORITY-001` | Authorization command accepts a bridge document whose latest status is `GO`, whose proposal has concrete spec links, target paths, requirement sufficiency, and test plan. |
| T-non-go-block | File bridge lifecycle semantics | Authorization command rejects latest `NEW`, `REVISED`, `NO-GO`, `VERIFIED`, unknown, or missing bridge entries. |
| T-target-mismatch | Scope discipline | Hook denies edits outside the GO'd proposal's authorized target path globs. |
| T-requirement-gap-block | `DELIB-S321-SPEC-CREATION-STANDING-AUTH`; requirement sufficiency rule | Authorization command denies implementation when the proposal says new/revised requirements are needed or uses unresolved `pending:` requirements. |
| T-codex-apply-patch | Codex harness parity | Hook extracts changed paths from a Codex `apply_patch` payload and applies the same authorization rules. |
| T-claude-write-edit | Claude Code harness parity | Hook extracts target paths from Claude Write/Edit/MultiEdit payloads and applies the same authorization rules. |
| T-shell-conservative | Shell mutation coverage | Hook allows read/test/status commands and denies or requires authorization for write/deploy/git-history/DB mutation commands. |
| T-formal-artifact-composition | Artifact approval composition | Formal artifact mutation remains blocked without an approval packet even when implementation authorization exists. |
| T-registration-parity | Cross-harness enforcement | Tests verify `.claude/settings.json` and `.codex/hooks.json` both register the implementation-start gate on supported mutation surfaces. |

Expected targeted commands after implementation:

```powershell
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py -q --tb=short
python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m ruff check scripts platform_tests .claude/hooks
python -m ruff format --check scripts platform_tests .claude/hooks
python -m groundtruth_kb secrets scan --paths scripts .claude .codex config platform_tests --format text
```

The implementation report must carry forward these linked specifications, the spec-to-test mapping, exact commands, and observed results.

## Acceptance Criteria

- Protected implementation edits are hard-blocked before `GO`.
- Protected implementation edits are hard-blocked after `NO-GO`, while `NEW`/`REVISED` is pending, and after terminal `VERIFIED` unless a new GO'd proposal authorizes new work.
- A local authorization packet can only be created from a latest-`GO` bridge document with concrete spec links, target paths, requirement sufficiency, and a spec-derived test plan.
- Missing or insufficient requirements block source/config/test implementation and direct the agent to requirement/specification capture first.
- Claude Code and Codex both enforce the same gate on their actual mutation paths.
- The existing formal-artifact approval gate remains independently effective.
- Bridge proposal/review/report writing remains possible so the system can plan work and recover from missing authorization.
- Emergency bridge repair remains possible only under the existing bridge-essential authority and must leave an incident/report trail.
- Tests cover denial, allowance, path mismatch, non-GO statuses, requirement gaps, hook payload parsing, and cross-harness registration.

## Risk And Mitigation

- **Risk:** The gate may block legitimate maintenance that currently relies on fast direct edits.
  **Mitigation:** Scope the first slice to protected implementation paths and provide explicit allow paths for bridge proposal/report writing and read-only verification commands.

- **Risk:** Shell command parsing can be incomplete.
  **Mitigation:** Use conservative classification: known-safe read/test commands pass; unknown state-changing commands require authorization; source writes should go through hook-visible edit surfaces whenever possible.

- **Risk:** Existing GO'd proposals may lack target path metadata.
  **Mitigation:** The gate applies prospectively after implementation. For already-GO'd threads, require either a revised proposal with target paths or a documented one-time authorization report approved through the bridge.

- **Risk:** Codex hook support may not cover `apply_patch` PreToolUse exactly as expected.
  **Mitigation:** Implement parity tests against the real `.codex/hooks.json` schema and explicitly NO-GO the guarantee if `apply_patch` cannot be intercepted before write.

- **Risk:** Emergency bridge repair exemption becomes a loophole.
  **Mitigation:** Limit it to bridge-function files, require bridge-unusable detection or explicit owner emergency directive, and require a follow-up bridge/incident report.

## Decision Requested From Loyal Opposition

Return `GO` if this proposal is sufficiently scoped to implement a cross-harness implementation-start authorization gate and requirement-sufficiency blocker before source/config/test implementation begins.

Return `NO-GO` with required corrections if the implementation should first create a formal DCL/GOV requirement artifact, if the target path metadata contract is insufficient, if Codex hook coverage cannot be made hard enough, or if the emergency bridge-repair exemption needs a narrower shape.

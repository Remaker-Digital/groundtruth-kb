# Implementation Proposal - Session Wrap Knowledge Collection Upgrade

bridge_kind: prime_proposal
Document: gtkb-session-wrap-knowledge-collection
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Work Item: update the governed session wrap skill so wrap-up reliably collects and preserves session knowledge
target_paths: [".claude/skills/kb-session-wrap/SKILL.md", ".claude/skills/kb-session-wrap/references/handoff-template.md", ".claude/skills/kb-session-wrap/references/audit-checklist.md", ".codex/skills/kb-session-wrap/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_kb_session_wrap_skill.py"]

## Claim

Upgrade the governed `kb-session-wrap` skill from a narrow 5-phase checklist into a knowledge-first session closeout procedure that reliably collects, classifies, updates, and reports durable session knowledge before a session is considered wrapped.

The change should improve recall continuity for future GT-KB sessions by making wrap-up explicitly account for MemBase work/spec state, the Deliberation Archive, `memory/MEMORY.md`, bridge state, tests/assertions, wrap scanner outputs, ignored local evidence, git state, and the next-session handoff prompt. It must also correct stale Agent Red and `origin main` assumptions in the current skill.

## Why Now

The owner has asked to improve knowledge collection at the conclusion of a session. The current wrap-up skill contains stale project wording and older implementation details:

- it still describes "Agent Red Customer Experience" instead of GroundTruth-KB;
- it hard-codes `git push origin main` even though active work is on the current repository branch;
- it references an outdated `tools/knowledge-db` import path;
- it treats deliberation harvest as one checklist item rather than making knowledge capture the governing purpose of wrap-up;
- it does not require explicit accounting for formal-artifact approval blockers, ignored local evidence, bridge verification state, or session prompt insertion failures.

This creates a direct recall-risk gap: a session may complete implementation successfully but leave future agents without enough durable context to preserve owner intent, implementation evidence, and open blockers.

## Specification Links

**Blocking / directly governing:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge remains the governed implementation proposal and verification queue; this proposal uses it before modifying protected surfaces.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside the live `E:/GT-KB` project root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing records relevant to a skill/process update.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires a focused test that the wrap skill preserves required knowledge-collection instructions.
- `PB-SESSION-WRAP-UP-PROACTIVE-001` - Prime Builder must proactively perform session wrap-up when appropriate.
- `DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001` - session wrap-up automation must respect formal-artifact approval, owner approval, and safety gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - session closeout must preserve durable artifacts when the session crosses from brainstorming into decisions, requirements, risks, procedures, reviews, plans, or accepted future work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - knowledge capture and implementation continuity should be artifact-oriented, not dependent on transient agent recall.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - wrap-up must detect which session outputs trigger artifact creation, update, deferral, or explicit no-op.
- `GOV-STANDING-BACKLOG-001` - future work and unresolved blockers must flow to the standing backlog or be explicitly reported as blocked/deferred.
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` - wrap-up must account for spec, test, and implementation linkage for completed work.
- `DCL-SPEC-DA-CITATION-MANDATORY-001` - new or updated specifications must preserve originating deliberation evidence.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` - future sessions need durable read surfaces for decisions and deliberations, including bridge and skill-mediated workflows.

**Advisory / cross-cutting:**

- `.claude/rules/canonical-terminology.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/codex-review-gate.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-STANDING-PRIORITIES.md`

## Prior Deliberations

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - recent owner decision emphasized keeping memory and knowledge fresh, readily available, and consistently applied across work execution.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - improvement opportunities that aid future work should be preserved as durable work/backlog candidates instead of relying on transient memory.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` - recent scoped authorization pattern reinforces that formal artifact work should preserve approval evidence and scope.
- `bridge/gtkb-gov-010-harvest-refresh-2026-05-11` - prior verified bridge work around harvest refresh shows session closeout must handle deliberation harvest as an active knowledge maintenance concern.
- `bridge/gtkb-da-harvest-catchup` - prior verified DA harvest catch-up work shows DA completeness is a recurring session-boundary risk.

## Owner Decisions / Input

- On 2026-05-13, the owner requested: "Please update the wrap-up skill to improve our knowledge collection at the conclusion of a session."
- The owner has not requested deployment, credential lifecycle work, destructive cleanup, or production changes.
- No additional owner decision is required to implement this process/documentation update once the bridge review returns `GO`.

## Requirement Sufficiency

Existing requirements sufficient.

The owner request is a process/skill improvement, not a new product behavior that requires a new runtime specification before implementation. Existing governance records already cover bridge authority, session wrap-up safety, artifact-oriented governance, formal-artifact blockers, DA citation, backlog visibility, and spec-derived verification. If implementation reveals the need for new runtime automation or database behavior, that work must be deferred to a separate proposal or revised bridge packet.

## Current Implementation Baseline

- `.claude/skills/kb-session-wrap/SKILL.md` defines a 5-phase wrap-up but is still scoped to the older Agent Red commercial project and contains stale snippets.
- `.claude/skills/kb-session-wrap/references/handoff-template.md` tells agents to continue Agent Red work and does not produce a GT-KB-specific handoff prompt with bridge, MemBase, DA, scanner, git, and blocker state.
- `.claude/skills/kb-session-wrap/references/audit-checklist.md` audits work-item age, assertions, spec drift, procedure freshness, and MEMORY size, but does not audit DA harvest freshness, ignored evidence, session prompts, bridge closure, or wrap scanner findings.
- `.codex/skills/kb-session-wrap/SKILL.md`, `.codex/skills/MANIFEST.json`, and `config/agent-control/harness-capability-registry.toml` are generated/registered adapter surfaces and must remain in sync after canonical skill edits.
- There is no focused test that prevents the wrap skill from losing the knowledge-collection obligations requested here.

## Proposed Scope

### IP-1: Rewrite the canonical wrap skill around knowledge collection

Update `.claude/skills/kb-session-wrap/SKILL.md` so the skill explicitly:

- defines its purpose as knowledge-first session closeout for GT-KB;
- instructs agents to derive session ID and current branch from live state rather than stale assumptions;
- starts with an inventory of git status, bridge `INDEX.md`, MemBase work/spec state, recent deliberations, wrap scan outputs, current ignored/local evidence, and current test/assertion evidence;
- includes a "Knowledge Collection Matrix" that maps session knowledge classes to durable homes and required action:
  - owner decisions and requirements to DA/spec intake/formal approval evidence;
  - completed implementation to MemBase work/spec status, bridge reports, tests, and implementation evidence;
  - future work and unresolved blockers to MemBase backlog or explicit blocked/deferred report entries;
  - session operational state to `memory/MEMORY.md` and wrap reports;
  - cross-session continuity to `session_prompts` and the handoff prompt;
  - verification evidence to tests, assertions, bridge reports, and wrap scan outputs;
  - ignored local evidence to explicit report references rather than forced git inclusion;
- requires agents to record blocker reasons when formal-artifact approval, DB mutation, DA harvest, session prompt insertion, or git sync cannot be completed;
- corrects git guidance to commit and push the current branch, not hard-coded `origin main`;
- instructs agents not to force-add `groundtruth.db`, environment files, snapshots, logs, or ignored local artifacts unless a governing process explicitly requires it;
- defines completion output that reports what was updated, what was intentionally deferred, and what remains blocked.

### IP-2: Update the handoff template

Update `.claude/skills/kb-session-wrap/references/handoff-template.md` so generated prompts:

- begin with an appropriate GT-KB init keyword such as `::init gtkb pb`;
- identify the live checkout, branch, and commit;
- summarize completed work, bridge state, MemBase work/spec state, DA captures/harvests, tests/assertions, scanner outputs, ignored local evidence, and blockers;
- name the next recommended actions with enough context for a fresh agent to proceed without relying on hidden chat memory.

### IP-3: Update the audit checklist

Update `.claude/skills/kb-session-wrap/references/audit-checklist.md` so every audit wrap also checks:

- stale or missing session prompts;
- unharvested or uncited deliberations;
- bridge threads without implementation or verification closure;
- ignored local evidence that should be referenced in reports but not committed;
- specs/work items missing current state reconciliation;
- repeated wrap scanner findings that should become backlog items.

### IP-4: Keep Codex adapter surfaces synchronized

Regenerate the Codex skill adapter and registry surfaces after canonical edits. The expected generated/registered paths are:

- `.codex/skills/kb-session-wrap/SKILL.md`;
- `.codex/skills/MANIFEST.json`;
- `config/agent-control/harness-capability-registry.toml`.

### IP-5: Add a focused regression test

Add `platform_tests/scripts/test_kb_session_wrap_skill.py` to assert the canonical and generated skill surfaces retain required knowledge-collection obligations, GT-KB handoff wording, current-branch git guidance, formal-artifact blocker handling, and "do not force-add ignored evidence" safety guidance.

## Out Of Scope

- Implementing a new wrap automation engine.
- Changing `groundtruth.db` schema or writing session records directly during this implementation.
- Deploying Agent Red or any GT-KB demo application.
- Credential lifecycle changes.
- Production or staging deployment.
- Bulk retroactive DA harvest or MemBase reconciliation.
- Replacing the existing wrap scanner suite.

## Specification-Derived Verification Plan

### New or updated tests

1. `platform_tests/scripts/test_kb_session_wrap_skill.py`
   - asserts the canonical skill contains a Knowledge Collection Matrix;
   - asserts required durable homes are named: MemBase, Deliberation Archive, `memory/MEMORY.md`, `bridge/INDEX.md`, `session_prompts`, tests/assertions, wrap scanner outputs, and ignored local evidence;
   - asserts stale Agent Red wording and hard-coded `git push origin main` are absent;
   - asserts the handoff template begins with a GT-KB init keyword and includes bridge, MemBase, DA, verification, blockers, and next actions;
   - asserts the generated Codex skill adapter contains the same required obligations.

### Commands

Run these before filing the implementation report:

```bash
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-wrap-knowledge-collection
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-wrap-knowledge-collection
python scripts/generate_codex_skill_adapters.py --update-registry
python -m pytest platform_tests/scripts/test_kb_session_wrap_skill.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-wrap-knowledge-collection
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-wrap-knowledge-collection
```

## Acceptance Criteria

- The canonical wrap-up skill makes knowledge collection the explicit purpose of session wrap-up.
- The skill tells agents where each class of session knowledge belongs and what to do when that write/update is blocked.
- GT-KB handoff prompts are self-contained enough for a fresh agent context.
- The stale Agent Red and `origin main` assumptions are removed.
- The skill preserves safety around ignored artifacts, `groundtruth.db`, credentials, and formal-artifact approval.
- The Codex adapter and registry surfaces are regenerated and validated.
- A focused regression test prevents future wrap skill drift away from knowledge collection.
- A post-implementation bridge report records changed files, verification commands, and any residual limitations.

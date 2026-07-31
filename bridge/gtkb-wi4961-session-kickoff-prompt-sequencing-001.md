NEW

# WI-4961 - Session Kickoff Prompt Sequencing Cleanup

bridge_kind: prime_proposal
Document: gtkb-wi4961-session-kickoff-prompt-sequencing
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T00:20:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4961-BATCH-B-20260705
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4961

target_paths: ["groundtruth.db", ".claude/rules/codex-session-bootstrap.md", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/session_self_initialization.py", "memory/MEMORY.md", "platform_tests/scripts/test_session_handoff.py", "platform_tests/scripts/test_session_handoff_service.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_session_startup_index.py"]

implementation_scope: source, tests, narrative-guidance, backlog-resolution
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4961 captures a prompt-generation defect: generated or documented
fresh-session kickoff guidance can be unusable when it bundles a first-line-only
keyword with a payload. The owner-correct sequence is separate messages:

```text
::init gtkb <role>
```

```text
::open <activity>
```

```text
<handoff or task body>
```

The implementation must cleanse prompt-emitting helpers, startup instructions,
and live memory guidance so they do not tell an operator or future harness to
send `::init` plus task content in one message, and do not omit the `::open`
activity envelope when activity context is required. It must add deterministic
tests so regenerated handoff/restart guidance cannot regress into a bundled
`::init`+payload or `::open`+payload form.

Initial live probes found three realistic target classes: the deterministic
handoff service (`groundtruth-kb/src/groundtruth_kb/session/handoff.py`), the
Codex startup/bootstrap quick-restart instructions
(`.claude/rules/codex-session-bootstrap.md`), and startup disclosure/self-init
surfaces (`scripts/session_self_initialization.py`). Historical memory entries
that merely report past sessions are evidence, not implementation authority,
and must not be rewritten unless they actively function as current kickoff
instructions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source, tests, and `.claude/rules`
  changes require a live bridge `GO`, implementation-start packet, and
  verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the
  owner-approved Batch B scope for WI-4961.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does
  not bypass bridge review or implementation-start checks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  links the prompt sequencing work to the governing init-keyword, session-role,
  and handoff-prompt requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this
  proposal to the active PAUTH, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include
  tests derived from the linked keyword/session/handoff specifications.
- `GOV-STANDING-BACKLOG-001` - WI-4961 may become terminal only through a
  governed backlog update with explicit completion evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal resolution of a stale or
  corrected prompt-generation defect must carry explicit lifecycle evidence.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - `::init <subject> <role>` is
  first-line-only with strict syntax; generated prompts must preserve that
  contract.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - emitters and receivers must
  handle init-keyword assertions consistently and distinguish interactive
  declarations from headless dispatch.
- `DCL-SESSION-ROLE-RESOLUTION-001` - prompt guidance must preserve explicit
  session-role evidence and not blur dispatcher routing authority with
  interactive session behavior authority.
- `GOV-SESSION-ROLE-AUTHORITY-001` - generated kickoff guidance must not mutate
  durable registry role assignments or imply registry role is general behavior
  authority.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - interactive owner-declared
  roles persist across the contiguous transcript and must be represented
  accurately in startup/handoff guidance.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` - the handoff prompt is a
  deterministic service surface and must remain action-oriented without AI
  mediation; sequencing output must be testable and byte-stable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable prompt behavior belongs in
  governed source/tests/rules rather than ad hoc chat instructions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - work item, PAUTH, prompt service,
  tests, implementation report, verification, and backlog resolution form one
  durable artifact graph.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-approved Batch B
  continuation created the active WI-4961 project authorization used here.
- `memory/MEMORY.md` S533 note - records the owner correction that `::init` and
  `::open` are strict first-line-only keywords delivered as separate messages,
  and that WI-4961 was captured from that correction.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` - existing handoff-prompt
  service contract; this WI tightens the generated prompt body, not the service
  ownership model.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and
  `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - existing keyword syntax and
  receiver/issuer semantics that make bundled payload prompts unsafe.
- `DCL-SESSION-ROLE-RESOLUTION-001` and `GOV-SESSION-ROLE-AUTHORITY-001` -
  current role-authority rules that prompt guidance must not contradict.

## Owner Decisions / Input

Owner approval evidence: `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`
authorized Batch B continuation and the PAUTH
`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4961-BATCH-B-20260705`.
Approval packet:
`.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json`.

No new owner decision is required. The work item itself records the owner
directive that kickoff prompts must use the separated `::init` -> `::open` ->
task sequence, and the implementation is bounded to source/tests/rule-memory
cleanup plus single-work-item backlog resolution.

## Requirement Sufficiency

Existing requirements sufficient. The canonical init-keyword syntax,
consistent assertion, session-role authority, and deterministic handoff-prompt
service requirements already define the correct behavior. The implementation
needs no new requirement before it can cleanse prompt emitters and add tests.

## Spec-Derived Verification Plan

Specification-to-evidence mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: after `GO`, run
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing`;
  expected result is an implementation-start packet scoped to the declared
  target paths.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and
  `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`: tests must prove generated or
  documented kickoff guidance keeps `::init` and `::open` as separate
  first-line-only messages and never appends handoff/task payload to either
  keyword message.
- `DCL-SESSION-ROLE-RESOLUTION-001`,
  `GOV-SESSION-ROLE-AUTHORITY-001`, and
  `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`: tests and source review must
  prove guidance preserves session-role evidence semantics and does not imply
  durable registry mutation.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`: handoff service tests must
  prove the generated prompt body remains deterministic while exposing the
  correct next-session message sequence.
- `GOV-STANDING-BACKLOG-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: run a dry-run backlog resolution for
  WI-4961, record exact evidence, then apply only after bridge `GO` and
  implementation verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  must include the spec-to-test table and observed command output.

Expected verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_canonical_init_keyword_assertions.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_self_initialization.py platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_self_initialization.py platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py
gt backlog resolve WI-4961 --status-detail "Resolved by bridge VERIFIED: prompt emitters and guidance now model separate ::init, ::open, and task/handoff messages; tests guard against bundled keyword+payload kickoff prompts." --related-bridge-threads "[\"bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-001.md\"]" --owner-approved --change-reason "WI-4961 bridge-verified prompt sequencing cleanup" --dry-run --json
```

The implementation report must also show a deterministic grep/audit over the
declared target surfaces proving no current prompt-emitting text tells the next
session to send `::init` with the handoff/task body in the same message.

## Risk / Rollback

Risk is medium because malformed kickoff guidance can silently drop a handoff
payload at session start. Mitigation: constrain the source changes to known
prompt-generation and startup guidance surfaces; require tests over generated
handoff output and bootstrap guidance; and avoid rewriting historical memory
entries unless they function as current prompt instructions.

Rollback is conventional git revert of the source/test/rule/memory changes
plus reopening or superseding WI-4961 if a later prompt surface is found. Bridge
files remain append-only and must not be rewritten during rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4961-session-kickoff-prompt-sequencing`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the expected implementation repairs malformed prompt-emitter behavior
and adds regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

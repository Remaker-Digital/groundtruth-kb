REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T00-37-42Z-prime-builder-A-186036
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex dispatcher-spawned headless; resolved_role=prime-builder; sandbox=workspace-write; approval_policy=never

# WI-4961 - Session Kickoff Prompt Sequencing Cleanup (Revised Scope)

bridge_kind: prime_proposal
Document: gtkb-wi4961-session-kickoff-prompt-sequencing
Version: 003
Responds to: bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-002.md
Author: Prime Builder (Codex)
Date: 2026-07-06T00:45:00Z

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4961-BATCH-B-20260705
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4961

target_paths: ["groundtruth.db", "CLAUDE.md", ".claude/rules/codex-session-bootstrap.md", "groundtruth-kb/templates/CLAUDE.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/CLAUDE.md", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/CLAUDE.md", "groundtruth-kb/src/groundtruth_kb/session/handoff.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/session_self_initialization.py", "memory/MEMORY.md", "platform_tests/scripts/test_session_handoff.py", "platform_tests/scripts/test_session_handoff_service.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_session_startup_index.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py", "platform_tests/scripts/test_canonical_init_keyword_assertions.py", "groundtruth-kb/tests/test_cli.py", "groundtruth-kb/tests/test_scaffold_isolation.py", "groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py", "groundtruth-kb/tests/test_session_kickoff_prompt_templates.py"]

implementation_scope: source, tests, narrative-guidance, template-fixtures, backlog-resolution
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Summary

This REVISED proposal takes Loyal Opposition Path A from
bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-002.md. It expands the
WI-4961 implementation scope to include scaffold template surfaces rather than
carving them into a successor work item.

The implementation must cleanse current prompt-emitting and prompt-describing
surfaces so fresh-session kickoff guidance is usable without manual repair:

```text
::init gtkb <role>
```

```text
::open <activity>
```

```text
<handoff or task body>
```

The revised scope keeps the original handoff service, Codex bootstrap guidance,
self-initialization output, and memory cleanup scope, and adds:

- `groundtruth-kb/templates/CLAUDE.md`, because it scaffolds root `CLAUDE.md`
  into adopter projects and currently emits keyword-free "Continue work on ..."
  kickoff guidance.
- The two committed scaffold golden fixture `CLAUDE.md` files, because fixture
  byte-diff tests must move with intentional template changes.
- Scaffold verification tests that pin the generated adopter guidance and
  fixture drift behavior.
- Root `CLAUDE.md`, explicitly dispositioning the Loyal Opposition P3 advisory
  by including the platform's own "Starting a New Session" snippet in scope.

No new owner decision is required. The owner-approved Batch B authorization and
WI-4961 acceptance criteria already require cleansing all helpers, harness
instructions, templates, rule files, and memory that emit or describe malformed
session-kickoff prompts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source, tests, `.claude/rules`,
  template, and KB mutation work require bridge review, implementation-start
  authorization, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the
  owner-approved Batch B scope for WI-4961.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does
  not bypass bridge review, implementation-start checks, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised
  proposal links the prompt sequencing work to the governing init-keyword,
  session-role, handoff-prompt, template, and backlog requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this
  proposal to the active PAUTH, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include
  tests derived from the linked keyword, session, handoff, template, and backlog
  specifications.
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
  session-role evidence semantics and not blur dispatcher routing authority
  with interactive session behavior authority.
- `GOV-SESSION-ROLE-AUTHORITY-001` - generated kickoff guidance must not mutate
  durable registry role assignments or imply registry role is general behavior
  authority.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - interactive owner-declared
  roles persist across the contiguous transcript and must be represented
  accurately in startup and handoff guidance.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` - the handoff prompt is a
  deterministic service surface and must remain action-oriented without AI
  mediation; sequencing output must be testable and byte-stable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable prompt behavior belongs in
  governed source, tests, templates, and rules rather than ad hoc chat
  instructions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - work item, PAUTH, prompt service,
  templates, tests, implementation report, verification, and backlog resolution
  form one durable artifact graph.
- `GOV-SOT-SINGLETON-001` - scaffold templates and root guidance must not create
  competing authoritative prompt semantics; they must point to the same
  governed init/open sequencing contract.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-approved Batch B
  continuation created the active WI-4961 project authorization used here.
- WI-4961 source owner directive, 2026-07-02 - records the owner correction that
  generated kickoff prompts must separate `::init`, `::open`, and the task body.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` - existing handoff-prompt
  service contract; this WI tightens generated prompt body sequencing.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and
  `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - existing keyword syntax and
  receiver/issuer semantics that make bundled keyword-plus-payload prompts
  unsafe.
- `DCL-SESSION-ROLE-RESOLUTION-001` and `GOV-SESSION-ROLE-AUTHORITY-001` -
  current role-authority rules that prompt guidance must not contradict.
- `GOV-SOT-SINGLETON-001` - current source-of-truth singleton rule, relevant
  because root guidance, scaffold templates, and generated handoff prompts must
  all reflect the same governed session sequencing semantics.

Deliberation CLI searches run during this revision for "session kickoff prompt
sequencing", "WI-4961", and "HIGH PRIORITY QUEUE CONTINUE" returned no
additional matching deliberation rows.

## Owner Decisions / Input

Owner approval evidence remains
`DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`, which authorized Batch B
continuation and the PAUTH
`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4961-BATCH-B-20260705`.
Approval packet:
`.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json`.

No new owner decision is required. This revision follows the NO-GO Path A:
expand the scope to cover template and fixture surfaces, then keep the outright
WI-4961 resolution only after implementation and verification prove all current
prompt emitters covered by the work item are corrected.

## Requirement Sufficiency

Existing requirements sufficient. WI-4961's acceptance summary explicitly
requires all prompt-emitting helpers, instructions, and memory to produce the
`::init` -> `::open` -> task sequence. Its description explicitly names
templates as in-scope. The existing canonical init-keyword, consistent
assertion, session-role authority, handoff-prompt service, source-of-truth, and
standing-backlog requirements are enough to implement and verify the expanded
scope.

## Findings Addressed

### NO-GO Finding 1 - Scope omits templates while resolving WI-4961 outright

Response: Scope is expanded. `target_paths` now includes
`groundtruth-kb/templates/CLAUDE.md`, both committed scaffold fixture
`CLAUDE.md` files, scaffold golden-diff tests, and a new/updated template
sequencing test surface. The implementation report must prove the template and
generated adopter guidance now show separate `::init`, `::open`, and task-body
messages before WI-4961 is resolved.

### P3 Advisory - Root CLAUDE.md describes keyword-free kickoff prompt

Response: Root `CLAUDE.md` is now explicitly in scope. The implementation must
update the platform root snippet to the same separated sequence, while keeping
the root document concise enough to respect the existing GOV-01 cap concern.

## Spec-Derived Verification Plan

Specification-to-evidence mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: after `GO`, run
  `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing`;
  expected result is an implementation-start packet scoped to the revised
  target paths.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and
  `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`: tests must prove generated or
  documented kickoff guidance keeps `::init` and `::open` as separate
  first-line-only messages and never appends handoff or task payload to either
  keyword message.
- `DCL-SESSION-ROLE-RESOLUTION-001`,
  `GOV-SESSION-ROLE-AUTHORITY-001`, and
  `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`: tests and source review must
  prove guidance preserves session-role evidence semantics and does not imply
  durable registry mutation.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`: handoff service tests must
  prove the generated prompt body remains deterministic while exposing the
  correct next-session message sequence.
- `GOV-SOT-SINGLETON-001`: source and narrative review must prove the platform
  root guidance, scaffold template guidance, fixture guidance, and generated
  handoff guidance describe one compatible init/open/task sequence rather than
  competing startup procedures.
- `GOV-STANDING-BACKLOG-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: run a dry-run backlog resolution for
  WI-4961, record exact evidence, then apply only after bridge `GO`,
  implementation, and verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  must include the spec-to-test table and observed command output.

Expected verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_canonical_init_keyword_assertions.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_self_initialization.py platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/session_self_initialization.py platform_tests/scripts/test_session_handoff.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_startup_index.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/adopter/test_golden_fixture_diff_per_version.py groundtruth-kb/tests/test_session_kickoff_prompt_templates.py
groundtruth-kb/.venv/Scripts/gt.exe backlog resolve WI-4961 --status-detail "Resolved by bridge VERIFIED: prompt emitters, scaffold templates, root guidance, memory guidance, and startup/handoff helpers now model separate ::init, ::open, and task/handoff messages; tests guard against bundled keyword+payload and keyword-free kickoff prompts." --related-bridge-threads "[\"bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md\"]" --owner-approved --change-reason "WI-4961 bridge-verified prompt sequencing cleanup" --dry-run --json
```

The implementation report must also show a deterministic string audit over the
declared prompt-emitting surfaces proving no current guidance tells the next
session to send `::init` or `::open` with the handoff/task body in the same
message, and no current scaffold template emits a keyword-free session kickoff
snippet for GT-KB-managed agent guidance.

## Pre-Filing Preflight Subsection

Candidate preflight evidence for this REVISED proposal:

- Applicability preflight command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md --json`
- Observed applicability result before live filing: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash
  `sha256:5d39b6bc98724c62ca684f67d07973c9f67c6c9862a29f31eedd697acafebe78`.
- Clause preflight command:
  `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4961-session-kickoff-prompt-sequencing-003.md`
- Observed clause result before live filing: exit 0; clauses evaluated 5;
  must_apply 3; may_apply 2; not_applicable 0; evidence gaps in must_apply
  clauses 0; blocking gaps 0.

The governed revision helper reruns both candidate preflights immediately
before writing the live bridge file and refuses filing on failure.

## Risk / Rollback

Risk is medium. The defect can silently drop a handoff payload at session start
or scaffold unusable kickoff guidance into future adopter projects. The expanded
scope also touches scaffold fixture files, so fixture updates must be tied to a
template change and pinned by byte-diff tests.

Mitigation: constrain implementation to the declared prompt-emitting surfaces;
keep historical memory entries intact unless they function as current
instructions; add deterministic tests for generated handoff output, bootstrap
guidance, scaffold template guidance, and fixture parity; and run a string audit
over target surfaces before filing the implementation report.

Rollback is conventional git revert of source, test, template, rule, root
guidance, and memory changes plus reopening or superseding WI-4961 if a later
prompt surface is found. Bridge files remain append-only and must not be
rewritten during rollback.

## Bridge Filing

This revision is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4961-session-kickoff-prompt-sequencing`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain remain the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the expected implementation repairs malformed prompt-emitter behavior,
template guidance, and tests for session kickoff sequencing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

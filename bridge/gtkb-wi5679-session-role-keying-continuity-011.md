REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# WI-5679 Session-Role Keying Continuity - Fourth Revised Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5679-session-role-keying-continuity
Version: 011
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5679-session-role-keying-continuity-010.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5679

target_paths: [".claude/hooks/workstream-focus.py", ".claude/settings.json", "config/hooks/gtkb-workstream-focus.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/_session_init_keyword.py", "scripts/session_role_resolution.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_session_role_keying_continuity.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_session_init_keyword_matching.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py"]

implementation_scope: source_test_configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix

KB Mutation: This thread includes canonical supporting-metadata writes for the
already-recorded PAUTH revision and WI-5679 progress state. Supporting writes
occur before acquisition of, or after release of, the implementation packet;
they are never smuggled through that packet. No specification mutation, direct
database write, or implementation-data mutation is proposed.

---

## Revision Claim

This revision preserves every closure accepted by versions 004, 006, 008, and
010. It carries C1-C5 forward while closing version 010's final parser-consumer
and assertion-coverage blockers. The inert shared-projection backstop remains removed.
Bounded liveness recovery uses only an explicit predecessor/successor relation
created when two session ids are co-observed in the same hook or continuation
invocation. A shared projection, an open-document scan, recency, and durable
harness identity are never sufficient role authority.

The complete consumer/assertion closure for both canonical parsers is now
explicit. Sixteen protected targets include every test whose expectation must
change, the prompt-facing workstream gate whose bridge-task behavior must be
preserved, the dedicated CLI consumer whose one-line option remains strict,
and both byte-identical registered workstream-hook copies. Read-only consumers
are named with executable evidence. The complete clean-HEAD baseline is stated
for every mandated pytest block.

The current project authorization is version 2. It preserves the WI-5679 and
WI-5504 work scope and every v1 control while removing the retired
`GOV-SESSION-ROLE-AUTHORITY-001` from its active specification references under
`DELIB-202667220`. This revision does not cite that retired record as governing
authority or claim its active-reference purge is complete. Versions 001 through
010 remain immutable audit history.

No implementation has occurred. After an independent GO, Prime Builder must
acquire an exact-session `go_implementation` claim and obtain a normal
implementation-start packet for this exact sixteen-path target set. If either
operation fails, implementation stops with no protected mutation. There is no
emergency-bootstrap, environment-variable override, hand-edited envelope, role
impersonation, or file-safety bypass in this proposal.

## Findings Addressed

### Version 010 A-C - Exhaustive parser-consumer and assertion closure

Version 010 correctly found that C4's prior consumer inventory was incomplete.
This revision closes that class in one pass. The inventory below comes from a
repository-wide symbol scan over both parser entry points and a second scan of
test assertions. Temporary pytest trees, virtual environments, bridge audit
history, and `.gtkb-state` scratch copies are not live consumers.

| Parser or binding | Live consumer / assertion surface | Postimage disposition | Executable evidence |
| --- | --- | --- | --- |
| `match_canonical_init_keyword` | `scripts/session_start_dispatch_core.py:313,656` | **Unaffected.** Both calls already pass `_read_first_prompt_line()` output, so later task lines never reach the parser. The receiver gate already admits the canonical first line. | `platform_tests/scripts/test_session_start_dispatch_core.py` remains read-only and green. |
| `match_canonical_init_keyword` | `scripts/workstream_focus.py:1152,1162,2008` | **Behavior adapted and declared.** A canonical first line plus later task text records subject/role evidence but does not discard the task or replace it with the startup relay. Exact one-line init retains the disclosure-and-wait behavior. The dead `_CANONICAL_DISPATCH_INIT_RE` alias is removed. | `platform_tests/hooks/test_workstream_focus.py` is a target; the daemon-dispatch-without-marker case must continue processing the bridge task while proving the init line was recognized rather than treated as a no-match. |
| `CANONICAL_INIT_KEYWORD_REGEX` literal | `scripts/check_codex_hook_parity.py:85` | **Unaffected.** This is a source-literal drift check, not a runtime parse. | `test_check_codex_hook_parity_resolution_table.py` and `test_codex_hook_parity_resolution_table_drift.py` remain read-only and green. |
| `match_canonical_init_keyword` direct assertions | `platform_tests/scripts/test_session_init_keyword_matching.py` | **Flips and declared.** LF and CRLF forms with later prompt text move to the positive matrix; same-line extra text and malformed first lines remain negative. | Target path and mandated parser block. |
| Independent receiver regex assertions | `platform_tests/scripts/test_canonical_init_keyword_syntax.py` | **Unaffected.** This module tests the Claude/Codex SessionStart receiver regexes, not either C4 parser. It remains in the authorized target set because version 008 required it, but no postimage change is expected. | Mandated parser/receiver block; any unexpected diff stops implementation. |
| `parse_canonical_init_keyword` | `.claude/hooks/workstream-focus.py:46-49` and `config/hooks/gtkb-workstream-focus.py:46-49` | **Flips and declared, in lockstep.** Both registered exact-coverage copies parse the canonical first line from the full prompt and persist the same session evidence. They must remain byte-identical after the change. | Both files are targets; hook, parity, and exact-copy assertions are mandatory. |
| `parse_canonical_init_keyword` | `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py:96,101` | **Preserved strict.** `--init-keyword` is a dedicated scalar option, not a prompt. A pre-parse LF/CRLF guard preserves its existing one-line contract even though the shared parser accepts task text after a canonical prompt line. | CLI source and `test_session_envelope_cli_provenance.py` are targets; LF and CRLF option values must remain rejected. |
| `parse_canonical_init_keyword` direct assertions | `platform_tests/scripts/test_session_envelope_runtime.py:61-95` | **Flips and declared.** The bare-LF and LF-plus-next-line cases move from the negative matrix to the positive first-line matrix; CRLF is added. Whitespace and same-line-extra cases remain negative. | Target path and first mandated block. |
| Hook-level exact-line assertions | `platform_tests/hooks/test_workstream_focus_session_role_marker.py` | **Unaffected.** Existing exact one-line role declarations retain their behavior; this module guards marker and fail-soft semantics. | Read-only consumer block. |
| CLI source-shape assertion | `platform_tests/scripts/test_session_envelope_cli_provenance.py:440` | **Preserved and strengthened.** The CLI still invokes the canonical parser after its scalar-line guard. | Target path and consumer block. |

This closes version 010 FINDING-A without regressing bridge dispatch: the
multiline daemon prompt remains processable, while its first-line role evidence
is no longer silently ignored. It closes FINDING-B by declaring
`test_session_envelope_runtime.py` as protected target 15 and naming all three
expected parser flips. It closes FINDING-C by correcting the receiver-gate
claim: `session_start_dispatch_core.py` is a no-op consumer because it already
extracts one line; `workstream_focus.py` is the actual full-prompt consumer;
and `cli_session_handoff.py` is explicitly guarded rather than silently
widened.

Version 010's non-blocking findings are folded into the same pass. Both
registered workstream hook copies change together; C2 treats an unreadable,
non-object, or malformed candidate as a visible typed failure; and the dead
`_CANONICAL_DISPATCH_INIT_RE` binding is removed. No shared projection becomes
role authority.

### Version 008 F1/F2 - Complete parser and receiver coverage

Version 008 is correct that C4 flips the existing negative assertion for
`::init gtkb pb\nfollow-up` and that the shared regex also governs headless
dispatch admission. This revision keeps C4, as authorized by
`DELIB-202667477` Decision 4, and makes both consequences explicit.

`platform_tests/scripts/test_session_init_keyword_matching.py` and
`platform_tests/scripts/test_canonical_init_keyword_syntax.py` remain declared
targets and mandatory verification inputs. The former moves the exact
first-line-plus-follow-up case from its negative matrix to its positive matrix.
The latter guards the independent SessionStart receiver regexes and is expected
to remain unchanged. `test_session_envelope_runtime.py`, added by this revision,
directly covers the second C4 parser. The earlier two-module clean-HEAD baseline
remains 141 passed.

The shared constant is consumed by `scripts/session_start_dispatch_core.py`,
`scripts/workstream_focus.py`, and the literal drift lock in
`scripts/check_codex_hook_parity.py`. `session_start_dispatch_core.py` already
extracts the first line and is unchanged. `workstream_focus.py` receives the
full prompt and therefore becomes an implementation target so canonical role
evidence can be recorded without discarding later bridge-task text. Same-line
extra prose, leading/trailing whitespace, case changes, aliases, and malformed
roles remain rejected. The three receiver/drift modules remain a mandatory
read-only block and pass 61/61 on clean HEAD.

The proposal now links `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and
`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, states the fresh-start boundary
of C3, restores the existing-module baseline qualifier, uses the canonical
`Prior Deliberations` heading, and forbids an unbounded keyed-document scan in
the five-second hook path.

### Version 006 F-A - Replace the inert projection clause with explicit-link recovery

The review is correct that `write_current` writes the keyed document and shared
projection from one object, in that order. A same-session projection newer than
its keyed source is therefore not a state any current writer creates. Version
005's C2 is withdrawn rather than described as useful.

This revision selects version-006 option 3. The current invocation supplies the
successor id and, only when present, one explicit predecessor id. The Claude
role-bearing hook derives that pair from its payload id and the independently
resolved bridge-work-intent id in that same invocation. SessionStart may supply
the pair only for a recognized resume/compact continuation source. No caller
selects a predecessor by scanning open documents, choosing the latest
`issued_at`, or reading the shared projection.

The successor document records `predecessor_session_id` and a typed continuity
binding. The predecessor records `successor_session_id` when it can be updated.
Normal resolution follows that forward link. If the predecessor-side update is
missing, the bounded liveness path may reconstruct the edge from exactly one
same-harness open keyed document whose validated predecessor field names the
requested id and whose binding source is the current hook/continuation
contract. Zero or multiple matches fail visibly. The projection may be used as
a non-authoritative locator optimization, but its bytes never satisfy the edge,
role, or provenance checks.

This remains the owner-chosen continuity-chain-plus-liveness design: a partial
two-sided write can recover from the successor's recorded edge for recognized
resume/compact continuation sources, including their SessionStart path when
UserPromptSubmit does not fire. A genuinely fresh `source=startup` event has no
explicit predecessor and deliberately falls through to the validated durable
registry role as `session_resolver_fallback`; it does not inherit transcript
authority. The design does not collapse to continuity-chain-only and never
borrows an unrelated peer. No new owner decision is required.

The derived end-to-end test reproduces the reported field configuration: the
Claude adapter receives a role-bearing prompt and explicit payload id under
`MARKER_CONTINUITY_ORDER`, while `session_self_initialization` and the claim
path request the distinct ambient id under `BRIDGE_WORK_INTENT_ORDER`. Both ids
must resolve the payload-declared role with requested/resolved provenance and
without changing the durable harness role.

### Version 006 F-B - Disclose both required baselines

The version-006 first block baseline remains 158 collected, 152 passed, 6
failed, and its second block remains 21/18/3. Version 008's added parser and
receiver coverage is disclosed separately below, so all current command and
baseline arithmetic is reproducible. The two role-authority conformance
failures retain their legacy `WI-4781` ownership marker and are explicitly
routed to WI-5718 for the retired-authority purge/current-spec correction; this
proposal neither hides nor absorbs them.

### Version 006 non-blocking findings - Same-pass precision

- The predecessor rule is explicit-id-only. A test with at least three open
  same-harness siblings proves timestamps and unrelated open documents cannot
  select or alter the chain.
- C3 resolves registry fallback only for the already validated, named harness
  identity. An unresolved identity fails visibly; it cannot consume
  `harness_roles.py`'s generic Prime default.
- C4 requires both parsers to conform to the specification's anchored
  entire-first-line grammar. Both parser definitions, every changing consumer,
  and every changing assertion module are declared targets; unaffected
  consumers remain mandatory read-only evidence.
- PAUTH/WI bookkeeping occurs outside the live implementation packet, so
  `groundtruth.db` is not an undeclared implementation target.
- PAUTH v2's included-spec list is a scope carrier, not an exhaustive
  applicability list; neither parity spec is excluded, and both remain
  mandatory proposal/test authorities. This revision does not silently amend
  the PAUTH.
- `DELIB-202667220` was captured from this same Prime session context; it is
  cited as owner content, not as independent review evidence.

### F1 - Parity specifications and per-harness evidence added

`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and
`ADR-CROSS-HARNESS-PARITY-001` are now linked below and mapped to executable
evidence. The current discovery-diff population for hook configuration is
exactly Claude and Codex. The fresh baseline reports 24 unrelated asymmetries,
but it reports no `workstream-focus` asymmetry. This proposal therefore does
not claim global parity or claim to resolve those 24 findings.

The `## Cross-Harness Disposition` section identifies the actual Claude and
Codex routes and the test evidence required for each. Other harnesses are not
part of the discovery tool's current hook-configuration population for this
surface, so they are not silently counted as passing and no waiver is requested
for them.

### F2 - Emergency bootstrap removed

The implementation-path note in version 001 is superseded. C1-C5 proceed only
through the ordinary bridge GO, exact-session claim, and implementation-start
packet. `DELIB-202667477` Decision 5 is cited only as historical evidence of
the owner's earlier in-band re-init choice; it is not treated as emergency
implementation authority.

The full C1-C5 scope remains intact because `DELIB-202667477` Decision 4
explicitly folds WI-5504 into WI-5679. C4 and C5 are therefore normal-path
work, not additions to a minimal emergency repair. If normal claim acquisition
does not work after GO, Prime Builder reports the failed gate and performs no
implementation.

### F3 - Unsupported pending owner-decision claims removed

This revision relies only on durable owner records. It does not cite a pending
transcript decision, an unarchived allow-list edit, or an inferred approval.
The operative owner evidence is `DELIB-202667477` for C1-C5 scope and
`DELIB-202667220` for retirement and active-reference removal of the obsolete
GOV.

## Problem Statement

Hook and tool subprocesses can resolve different session ids after restart or
resume. The worker-session document containing the transcript-declared role is
then written under one id while claim and attribution consumers read a stale
document under another. A stale-but-present exact-id document outranks the
newer per-harness projection, so re-sending the canonical init keyword can
write the correct role into a document that the claim path never reaches.

The same chain currently permits registry-fallback roles in the shared
projection to be described as interactive transcript authority. WI-5504 adds
two defects in the repair channel itself: the envelope parser does not share
the canonical first-line grammar, and Claude invokes the workstream-focus hook
through bare `pythonw` while the Codex route uses the project venv explicitly.
Hook failures are fail-soft and can therefore become silent no-ops.

## Proposed Implementation

### C1 - Explicit same-harness session continuity

Add optional `predecessor_session_id`, `successor_session_id`, and typed
`continuity_binding` fields to authoritative worker-session documents. The
predecessor id must be supplied explicitly from one invocation that co-observes
the hook payload/current id and bridge-work-intent id, or from a recognized
resume/compact SessionStart source. No function scans open documents or uses
timestamps to choose a predecessor. Three or three hundred unrelated open
same-harness siblings are therefore irrelevant.

Resolution from a stale id follows a unique, acyclic, same-harness successor
chain to its terminal document. The writer validates both endpoint ids and the
durable harness identity before recording an edge. Ambiguous, cyclic,
cross-harness, malformed, or closed-terminal chains fail visibly rather than
selecting a role.

The resolution result records both requested and resolved session identity so
the continuity decision is auditable. The link changes no durable harness role
metadata.

### C2 - Explicit reverse-link liveness recovery

When the requested keyed document lacks a usable successor edge, resolution
may recover only from one bounded candidate named by the current invocation's
explicit successor id or by the non-authoritative projection locator. It must
reload that candidate from its exact keyed path, require that its validated
`predecessor_session_id` names the requested id, and require that its typed
binding came from the current hook/continuation contract. The candidate's own
worker-role provenance must validate against its own session id. A missing,
unreadable, non-object, or malformed candidate; a locator that does not carry
the exact edge; a cross-harness edge; or a closed candidate fails visibly with
a typed reason.

This is the liveness half of the owner's chosen design: it recovers when the
successor-side write completed but the predecessor-side edge update did not.
It does not read role authority from `session-envelope.json` or
`.claude/session/envelope.json`. The five-second hook path never enumerates the
hundreds of open keyed documents; the projection is only a bounded locator and
its bytes cannot satisfy any edge, role, or provenance check. Concurrent
projection ownership remains separate work; this change does not claim to
close WI-5086, WI-5718, or WI-5721.

### C3 - Strict transcript-only restart inheritance

Before a recognized resume/compact SessionStart creates a replacement
document, inspect only the explicitly named predecessor. Inherit its role only
when validated
`worker_role_provenance.role_resolution_source` is
`transcript_init_keyword`. Carry that source and the predecessor id into the
successor. For every other source, use the durable registry role as a fallback
and label it `session_resolver_fallback`. The fallback must resolve for the
already validated named harness id; unresolved identity fails visibly and may
not consume a generic default role.

A genuinely fresh `source=startup` event has no predecessor pair by design and
therefore takes that registry-fallback branch. The proposal does not claim that
transcript authority survives a fresh unrelated process without an explicit
continuation edge.

`scripts/session_role_resolution.py` must not label a registry-derived or
continuity result lacking validated transcript provenance as
`interactive_transcript`. Transcript authority is reported only when validated
transcript provenance exists.

### C4 - Canonical init-keyword parser convergence

Make both `parse_canonical_init_keyword` and
`scripts/_session_init_keyword.py` conform to
`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`: the keyword is the entire first line,
that line is strictly anchored, and subsequent prompt lines do not become part
of the keyword grammar. A shared case matrix proves specification conformance
for bare keywords, optional roles, LF/CRLF first-line termination, trailing and
leading spaces, subsequent prose, same-line extra prose, case changes, and
malformed role tokens.

No compatibility alias becomes canonical input, and no parser silently trims
or case-folds the prompt.

Because `CANONICAL_INIT_KEYWORD_REGEX` is shared, this first-line behavior
reaches two runtime call shapes. `session_start_dispatch_core.py` already passes
only the first line and remains unchanged. `workstream_focus.py` passes a full
prompt and is changed so a canonical first line records subject and role
evidence while any non-whitespace later task text passes through for normal
processing. Only an exact one-line init command retains the startup
disclosure-and-wait response. This preserves daemon bridge dispatch even when
its optional run-id marker is absent. The dead `_CANONICAL_DISPATCH_INIT_RE`
alias is removed.

`parse_canonical_init_keyword` is also used by
`gt session envelope open --init-keyword`. That option remains a strict scalar:
`cli_session_handoff.py` rejects LF or CRLF before invoking the shared parser.
A full prompt is valid at prompt-facing consumers, but task text is never
silently accepted inside the dedicated CLI option. Extra text on the keyword
line remains rejected everywhere.

### C5 - Deterministic hook interpreter and visible fail-soft warning

Change only the two Claude workstream-focus registrations in
`.claude/settings.json` to invoke the in-root project venv `pythonw.exe`
explicitly. Preserve existing event placement, order, timeout, and every other
hook command.

When a canonical role-bearing init keyword is observed but the adapter cannot
persist a matching authoritative worker-session document, retain fail-soft hook
behavior but return a visible diagnostic in the hook result. Ordinary prompts
remain silent. No permission check or content-validity gate is added.

Apply the adapter logic change byte-identically to
`.claude/hooks/workstream-focus.py` and its registered canonical destination
`config/hooks/gtkb-workstream-focus.py`. The retained source remains active
until WI-5640's separately governed deletion stage, so neither copy may be left
with divergent session semantics.

Update `test_workstream_focus_hook_parity.py` to inspect Codex's actual adapter
route: `.codex/hooks.json` invokes `run_py_no_window`, whose relevant batches
include `.codex/gtkb-hooks/workstream-focus.cmd`, which invokes the same Claude
Python adapter through the project venv. The two current direct-registration
assertions are stale and fail on clean HEAD even though that route exists.

## Cross-Harness Disposition

This section is required because two targets are Claude harness surfaces and a
third target is their canonical registered hook source.
Disposition: behavioral parity for the applicable Claude/Codex population; no
typed waiver requested.

### Claude

- `.claude/settings.json` registers `.claude/hooks/workstream-focus.py` for
  UserPromptSubmit and write-capable PreToolUse events.
- This change makes both registrations use the in-root venv interpreter and
  preserves their current event order.
- `.claude/hooks/workstream-focus.py` and
  `config/hooks/gtkb-workstream-focus.py` remain byte-identical; the latter is
  the WI-5640 canonical destination and is not a second behavioral authority.
- The adapter consumes the payload session id, co-observes the ambient
  bridge-work-intent id in the same invocation, invokes the shared envelope
  implementation with that explicit pair, and emits a diagnostic only for a
  canonical role-bearing prompt whose persistence fails.

### Codex

- `.codex/hooks.json` invokes `.codex/gtkb-hooks/run_py_no_window.py` by batch.
- The relevant UserPromptSubmit and PreToolUse batches include
  `.codex/gtkb-hooks/workstream-focus.cmd`.
- That wrapper already invokes the same `.claude/hooks/workstream-focus.py`
  adapter with `groundtruth-kb/.venv/Scripts/pythonw.exe`; no Codex source or
  configuration edit is required.
- The parity test will follow this real indirection instead of requiring a
  nonexistent direct `workstream-focus` string in `.codex/hooks.json`.

### Other harnesses and global baseline

The current `parity_discovery_diff.py --json` population for actual hook
configuration is `claude` and `codex`. Other registered harnesses are not
asserted to carry this hook surface and are not assigned a fictional PASS.
C1-C4 remain harness-neutral shared API behavior and are tested with distinct
harness identities, including a negative cross-harness chain case.

The fresh discovery baseline is `ASYMMETRY` with 24 findings unrelated to
`workstream-focus`. Acceptance requires no new finding for this capability and
no regression of its existing Claude/Codex presence. The thread does not own
or waive the unrelated 24 findings.

## Scope Boundary

The only protected implementation targets are the sixteen paths declared above.
Canonical PAUTH and WI progress-metadata writes are supporting thread metadata
and are disclosed by `kb_mutation_in_scope: true`; they are not source
implementation targets and do not authorize direct `groundtruth.db` mutation.
There is no registry, projection, bridge-runtime, dispatcher, specification,
credential, deployment, external-system, or Git-history mutation in
implementation scope. No approval-packet work is in scope.

No approval-packet work is performed by this proposal. The already-recorded
PAUTH v2 and its owner evidence are prerequisites, not implementation targets.
No `.codex/` file is changed; those files are read-only parity evidence.
`scripts/session_start_dispatch_core.py` and
`scripts/check_codex_hook_parity.py` remain read-only consumers, as do their
three covering modules and
`platform_tests/hooks/test_workstream_focus_session_role_marker.py`. If
implementation proves any seventeenth protected path necessary, Prime Builder must stop and
file a new REVISED proposal rather than consume GO authority beyond this list.

## Owner Decisions / Input

- `DELIB-202667477` Decisions 1 and 2 authorize the continuity chain plus
  liveness backstop and strict transcript-only inheritance. This revision uses
  the version-006 option-3 remedy: liveness reconstructs only an explicitly
  recorded predecessor edge from an authoritative keyed successor. It neither
  accepts the rejected continuity-chain-only alternative nor reads role
  authority from a shared projection, so no new owner decision is required.
- `DELIB-202667477` Decision 3 requires the full bridge protocol rather than a
  fast lane.
- `DELIB-202667477` Decision 4 explicitly folds WI-5504 into this scope, which
  authorizes C4 parser convergence and C5 hook hardening through the normal
  path.
- `DELIB-202667477` Decision 5 records the historical choice to re-send the
  canonical init keyword. It supplies no emergency-bootstrap authority and is
  not used as such.
- `DELIB-202667220` directs retirement of
  `GOV-SESSION-ROLE-AUTHORITY-001`, removal from active references, and
  preservation of historical audit evidence. PAUTH v2 applies the retirement;
  WI-5718 owns the still-incomplete active-reference purge.
- `DELIB-202667487` records the owner's personal LO file-safety allow-list edit.
  It is historical context only; this proposal does not modify that file or use
  it as implementation authority.

No new owner decision is required by this revision.

## Requirement Sufficiency

Existing requirements sufficient. The current persistence, resolution,
canonical grammar, and cross-harness parity specifications fully define the
defect and verification duties. The retired
`GOV-SESSION-ROLE-AUTHORITY-001` is not operative authority and is not needed
to make the requirements complete.

## Specification Links

- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Prior Deliberations

- `DELIB-202667477` - owner-approved WI-5679/WI-5504 design, project routing,
  and full C1-C5 scope.
- `DELIB-202667220` - owner-directed retirement and active-reference purge of
  the obsolete role-authority GOV; formal retirement is complete and WI-5718
  retains the outstanding operative-reference purge.
- `DELIB-202667487` - owner-made LO file-safety allow-list edit and its bounded
  rationale; no edit to that configuration is part of this thread.
- `DELIB-20265225` and `DELIB-20265224` - historical owner decisions for
  transcript-defined interactive role persistence across contiguous context.
- `DELIB-20260710-WI5086-CONCURRENT-CODEX-SESSION-ENVELOPE-CLOBBER` - sibling
  concurrency-axis evidence that this thread explicitly does not claim to
  close.
- `bridge/gtkb-wi5679-session-role-keying-continuity-002.md` - first NO-GO;
  version 004 confirms all three findings closed.
- `bridge/gtkb-wi5679-session-role-keying-continuity-004.md` - controlling
  NO-GO whose F1/F2 blockers and N1-N3 observations version 005 addressed.
- `bridge/gtkb-wi5679-session-role-keying-continuity-006.md` - controlling
  NO-GO; this revision closes its inert-C2 and undisclosed-second-baseline
  blockers and incorporates its same-pass precision findings.
- `bridge/gtkb-wi5679-session-role-keying-continuity-008.md` - controlling
  NO-GO; this revision adds the two parser-regression targets, discloses the
  shared receiver-gate semantics and tests, and incorporates all four
  non-blocking precision findings.
- `bridge/gtkb-wi5679-session-role-keying-continuity-010.md` - controlling
  NO-GO; this revision closes its parser-consumer inventory, workstream
  dispatch-passthrough, envelope-runtime target, canonical-mirror, malformed
  candidate, and dead-binding findings through the exhaustive closure table.
- `bridge/gtkb-lo-role-resolution-fallback-privilege-escalation-advisory-001.md`
  - evidence for the out-of-scope generic fallback defect; this revision adds
  an in-scope named-harness assertion without absorbing that advisory.
- `bridge/gtkb-lo-kb-mutation-declaration-integrity-advisory-001.md` -
  pattern-level evidence for the corrected MemBase declaration.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724`
  version 2 - active authorization with the retired GOV removed and all other
  work scope and controls preserved.

## Spec-Derived Verification Plan

| Specification | Executed evidence required | Required result |
| --- | --- | --- |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | New continuation tests co-observe distinct payload/ambient ids, create the explicit edge, re-key SessionStart, and resolve from both ids | Both resolve the same owner-declared role with explicit requested/resolved session provenance |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | Restart and resume tests cover transcript and non-transcript predecessors | Transcript role persists; fallback role does not self-perpetuate as transcript authority |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Unique, missing, ambiguous, cyclic, cross-harness, unreadable, non-object, malformed, and closed edge cases; partial-write reverse lookup; three unrelated open siblings; live payload/ambient field configuration | Deterministic result or typed fail-visible error; only an exact explicit edge can redirect one requested id to another |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Shared parser case matrix against both canonical parsers plus consumer-specific tests for full prompts and scalar CLI input | Both parsers implement the anchored entire-first-line grammar; multiline task text is accepted only on prompt-facing surfaces, and the CLI option remains one-line strict |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Dedicated parser-regression modules plus the literal drift-lock tests | Both canonical parsers and the shared constant remain behaviorally aligned |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Receiver-side tests exercise exact one-line init, canonical first line with later task text, absent daemon marker, and malformed same-line forms | Exact one-line owner init relays; multiline dispatch/task prompts preserve task processing while recording role evidence; malformed commands remain non-authoritative |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Updated workstream-focus parity tests plus discovery diff | Claude/Codex routes both resolve; no workstream-focus finding; unrelated baseline disclosed |
| `ADR-CROSS-HARNESS-PARITY-001` | Execute adapter-level canonical prompt success/failure cases through Claude and Codex route fixtures | Equivalent observable persistence and warning behavior on both applicable harness routes |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Normal exact-session claim and implementation-start packet before any protected edit | Packet authorizes exactly the sixteen target paths and no emergency route is used |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict lifecycle resolver and post-implementation report chain | Valid append-only lifecycle; implementation starts only after independent GO |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table and exact command results | Every linked behavioral spec has fresh executed evidence |

Required implementation verification commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_session_envelope_cli_provenance.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/parity_discovery_diff.py --json
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/_session_init_keyword.py scripts/session_role_resolution.py scripts/session_self_initialization.py scripts/workstream_focus.py .claude/hooks/workstream-focus.py config/hooks/gtkb-workstream-focus.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/_session_init_keyword.py scripts/session_role_resolution.py scripts/session_self_initialization.py scripts/workstream_focus.py .claude/hooks/workstream-focus.py config/hooks/gtkb-workstream-focus.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py
git diff --check -- .claude/hooks/workstream-focus.py .claude/settings.json config/hooks/gtkb-workstream-focus.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/_session_init_keyword.py scripts/session_role_resolution.py scripts/session_self_initialization.py scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py
```

Baseline disclosure: on clean HEAD, the seven existing modules in the first
mandated block collected 299 tests and produced 293 passed and 6 failed. The
future `test_session_role_keying_continuity.py` target does not yet exist and is
therefore excluded from that baseline arithmetic. The original five existing
modules contribute 158/152/6; the two newly declared parser modules contribute
141/141. The exact six failures are:

- `test_codex_userpromptsubmit_includes_workstream_focus` and
  `test_codex_pretooluse_covers_bash_and_apply_patch_workstream_focus` - the two
  in-scope stale direct-registration assertions this proposal repairs;
- `test_render_topic_context_injects_activity_profile_for_open` and
  `test_render_topic_context_loads_only_open_activity_payload` - pre-existing
  activity-profile rendering expectations unrelated to this implementation;
- `test_startup_model_contains_role_governance_and_kpi_inventory` - pre-existing
  `partial` versus `not_wired` expectation; and
- `test_cursor_harness_emit_resolves_default_lifecycle_guard` - pre-existing
  Windows subprocess decoding failure yielding `stdout=None`.

The second mandated block independently collected 21 tests and produced 18
passed and 3 failed in 2.59 seconds. Its exact failures are:

- `test_gov_session_role_authority_001_dispatcher_only` - legacy `WI-4781`
  assertion that still requires the retired GOV; active-reference removal is
  owned by WI-5718;
- `test_dcl_session_role_resolution_001_enforcement_gate_split` - legacy
  `WI-4781` conformance assertion for `DCL-SESSION-ROLE-RESOLUTION-001`; its
  current-record correction is explicitly in WI-5718's nine-spec amendment
  set; and
- `test_active_harnesses_have_required_production_parity` - pre-existing live
  required-capability parity failure. This proposal owns only the changed
  workstream-focus capability and does not relabel global parity as passing.

The receiver-side read-only block independently collected 61 tests and
produced 61 passed in 3.89 seconds across
`test_session_start_dispatch_core.py`,
`test_check_codex_hook_parity_resolution_table.py`, and
`test_codex_hook_parity_resolution_table_drift.py`. Its postimage must remain
fully green. It is not evidence of a semantic flip: the dispatch-core caller
already extracts the first line before invoking the parser.

The new consumer-closure block independently collected 149 tests and produced
146 passed and 3 skipped in 10.99 seconds across
`platform_tests/hooks/test_workstream_focus.py`,
`platform_tests/hooks/test_workstream_focus_session_role_marker.py`, and
`platform_tests/scripts/test_session_envelope_cli_provenance.py`. It has zero
failures on clean HEAD. The postimage must preserve bridge-task passthrough,
retain exact-line marker behavior, keep LF/CRLF CLI option values rejected, and
replace the old no-match audit assertion with explicit recognized-multiline
passthrough evidence.

Within the first mandated block,
`platform_tests/scripts/test_session_envelope_runtime.py` currently contributes
35 passed and 2 pre-existing unrelated failures. Its two LF parser negatives
are expected to become positives, and one CRLF positive is added; those changes
must not alter the two disclosed activity-profile failures.

The implementation report must rerun all four pytest blocks and disclose every
remaining baseline failure exactly rather than relabeling unrelated failures
as fixed.

## Acceptance Criteria

1. An independent GO exists before any protected implementation mutation.
2. A normal exact-session claim and implementation-start packet authorize
   exactly the sixteen declared paths. Failure of either gate leaves source and
   configuration untouched.
3. The reproduced field configuration closes end to end: a role-bearing Claude
   hook payload id and distinct ambient bridge-work-intent id create one
   explicit edge, and claim-path resolution from either id returns the same
   transcript role with requested/resolved provenance.
4. A registry-fallback role is never inherited or reported as
   `interactive_transcript`; fallback resolves only the validated named
   harness and unresolved identity fails visibly.
5. Forward-chain and reverse-link recovery accept only a unique, acyclic,
   explicit same-harness edge. A partial predecessor write recovers from the
   keyed successor, while zero/multiple, unreadable, non-object, malformed, or
   closed candidates and every peer without the exact edge fail visibly with a
   typed reason. Shared projections never authorize a role.
6. At least three open same-harness sibling documents cannot influence explicit
   predecessor selection. Continuity never crosses durable harness identity or
   changes the durable registry role map.
7. Both canonical init parsers conform to the anchored entire-first-line
   requirement across the complete positive/negative case matrix, including
   subsequent prompt lines and LF/CRLF. A recognized multiline workstream
   prompt records role evidence without discarding later bridge-task text;
   exact one-line init retains startup disclosure behavior; the dedicated CLI
   option rejects multiline input.
8. Claude's two workstream-focus commands use the in-root venv interpreter;
   canonical persistence failure yields a visible diagnostic; ordinary prompts
   remain silent. The `.claude` retained source and `config/hooks` canonical
   destination remain byte-identical.
9. The updated parity tests follow the actual Codex batch/wrapper route and pass
   for Claude and Codex. Discovery reports no `workstream-focus` finding; its 24
   unrelated baseline findings are neither widened nor claimed closed.
10. All required focused tests and Ruff checks pass for changed Python paths;
    unrelated baseline failures are disclosed exactly.
11. No seventeenth protected implementation path, direct database mutation,
    registry mutation, specification mutation, dispatcher action, push,
    history rewrite, release, deployment, credential operation, or
    external-system mutation occurs. Canonical supporting PAUTH/WI metadata is
    disclosed rather than misreported as absent.

## Pre-Filing Preflight Evidence

Both mandatory candidate preflights were run against this completed body with
the `--content-file` surface before filing.

- Applicability: `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`, no missing parent
  directory, and no unclassified target path.
- Clause applicability: 5 clauses evaluated; 4 `must_apply`, 1 `may_apply`,
  zero evidence gaps in must-apply clauses, zero blocking gaps, exit 0.

The governed revision helper must re-run both gates against its final candidate
after inserting author metadata. Any changed result aborts filing.

## Risks And Rollback

The principal risk is cross-session role borrowing. Explicit co-observation,
unique same-harness links, cycle and ambiguity rejection, requested/resolved
ids, strict transcript provenance, and negative peer/cross-harness tests bound
that risk. Shared projections provide no role authority. The reverse-link path
accepts only an authoritative keyed successor with the exact predecessor edge
and does not claim to solve peer-session projection ownership.

The hook warning must remain fail-soft so a diagnostic gap does not block useful
work. It reports persistence failure without invalidating content or adding a
permission boundary, consistent with the owner's path-of-least-resistance
governance direction.

Parser convergence must not turn role recognition into task loss. The
workstream gate therefore distinguishes exact one-line startup commands from
multiline prompts, preserving later task text. Conversely, the dedicated CLI
option remains one-line strict so a prompt parser does not silently widen a
scalar configuration surface. Byte equality between the retained and canonical
workstream hook copies prevents WI-5640's temporary dual-file state from
creating two runtime semantics.

Rollback is one scoped commit revert. The predecessor, successor, and typed
binding fields are optional and additive, so documents without them remain
readable. No database or registry migration is required. Historical bridge and
session evidence is not deleted.

## Recommended Commit Type

`fix(session): preserve exact-session role continuity across re-key`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

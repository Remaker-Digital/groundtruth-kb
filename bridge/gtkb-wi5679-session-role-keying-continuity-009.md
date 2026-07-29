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


# WI-5679 Session-Role Keying Continuity - Third Revised Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5679-session-role-keying-continuity
Version: 009
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5679-session-role-keying-continuity-008.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5679

target_paths: [".claude/hooks/workstream-focus.py", ".claude/settings.json", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/_session_init_keyword.py", "scripts/session_role_resolution.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_session_role_keying_continuity.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_session_init_keyword_matching.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py"]

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

This revision preserves every closure accepted by versions 004, 006, and 008.
It carries C1-C5 forward unchanged while closing version 008's two scope and
verification blockers. The inert shared-projection backstop remains removed.
Bounded liveness recovery uses only an explicit predecessor/successor relation
created when two session ids are co-observed in the same hook or continuation
invocation. A shared projection, an open-document scan, recency, and durable
harness identity are never sufficient role authority.

The two dedicated canonical-init regression modules are added as the ninth and
tenth protected targets. Their clean-HEAD baseline is 141/141 passing. The
shared regex's receiver-side consumers and their three covering test modules
are now enumerated explicitly; their clean-HEAD baseline is 61/61 passing.
The complete clean-HEAD baseline is stated for every mandated pytest block.

The current project authorization is version 2. It preserves the WI-5679 and
WI-5504 work scope and every v1 control while removing the retired
`GOV-SESSION-ROLE-AUTHORITY-001` from its active specification references under
`DELIB-202667220`. This revision does not cite that retired record as governing
authority or claim its active-reference purge is complete. Versions 001 through
008 remain immutable audit history.

No implementation has occurred. After an independent GO, Prime Builder must
acquire an exact-session `go_implementation` claim and obtain a normal
implementation-start packet for this exact ten-path target set. If either
operation fails, implementation stops with no protected mutation. There is no
emergency-bootstrap, environment-variable override, hand-edited envelope, role
impersonation, or file-safety bypass in this proposal.

## Findings Addressed

### Version 008 F1/F2 - Complete parser and receiver coverage

Version 008 is correct that C4 flips the existing negative assertion for
`::init gtkb pb\nfollow-up` and that the shared regex also governs headless
dispatch admission. This revision keeps C4, as authorized by
`DELIB-202667477` Decision 4, and makes both consequences explicit.

`platform_tests/scripts/test_session_init_keyword_matching.py` and
`platform_tests/scripts/test_canonical_init_keyword_syntax.py` are now declared
targets and mandatory verification inputs. The former moves the exact
first-line-plus-follow-up case from its negative matrix to its positive matrix;
the latter proves the complete LF/CRLF, whitespace, same-line-extra, and
subsequent-line matrix. Their fresh clean-HEAD baseline is 141 passed.

The shared constant is consumed by `scripts/session_start_dispatch_core.py`,
`scripts/workstream_focus.py`, and the literal drift lock in
`scripts/check_codex_hook_parity.py`. C4 intentionally changes receiver-side
admission only for a canonical keyword occupying the complete first line with
later prompt lines: that form becomes accepted. Same-line extra prose,
leading/trailing whitespace, case changes, aliases, and malformed roles remain
rejected. No consumer source change is required because all consume the same
constant. Their three covering modules are mandatory read-only verification
inputs and pass 61/61 on clean HEAD.

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
  entire-first-line grammar. `scripts/_session_init_keyword.py` is the eighth
  declared target; its two dedicated regression modules are the ninth and
  tenth targets.
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
worker-role provenance must validate against its own session id. A missing
candidate, a locator that does not carry the exact edge, a cross-harness edge,
or a closed candidate fails visibly.

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

Because `CANONICAL_INIT_KEYWORD_REGEX` is shared, this same first-line behavior
applies intentionally to the receiver gates in
`scripts/session_start_dispatch_core.py` and `scripts/workstream_focus.py` and
to the literal drift lock in `scripts/check_codex_hook_parity.py`. A canonical
first line followed by later task text is admitted; extra text on the keyword
line remains rejected. Those consumer files are read-only evidence in this
thread, and their dedicated regression modules are mandatory verification.

### C5 - Deterministic hook interpreter and visible fail-soft warning

Change only the two Claude workstream-focus registrations in
`.claude/settings.json` to invoke the in-root project venv `pythonw.exe`
explicitly. Preserve existing event placement, order, timeout, and every other
hook command.

When a canonical role-bearing init keyword is observed but the adapter cannot
persist a matching authoritative worker-session document, retain fail-soft hook
behavior but return a visible diagnostic in the hook result. Ordinary prompts
remain silent. No permission check or content-validity gate is added.

Update `test_workstream_focus_hook_parity.py` to inspect Codex's actual adapter
route: `.codex/hooks.json` invokes `run_py_no_window`, whose relevant batches
include `.codex/gtkb-hooks/workstream-focus.cmd`, which invokes the same Claude
Python adapter through the project venv. The two current direct-registration
assertions are stale and fail on clean HEAD even though that route exists.

## Cross-Harness Disposition

This section is required because two targets are Claude harness surfaces.
Disposition: behavioral parity for the applicable Claude/Codex population; no
typed waiver requested.

### Claude

- `.claude/settings.json` registers `.claude/hooks/workstream-focus.py` for
  UserPromptSubmit and write-capable PreToolUse events.
- This change makes both registrations use the in-root venv interpreter and
  preserves their current event order.
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

The only protected implementation targets are the ten paths declared above.
Canonical PAUTH and WI progress-metadata writes are supporting thread metadata
and are disclosed by `kb_mutation_in_scope: true`; they are not source
implementation targets and do not authorize direct `groundtruth.db` mutation.
There is no registry, projection, bridge-runtime, dispatcher, specification,
credential, deployment, external-system, or Git-history mutation in
implementation scope. No approval-packet work is in scope.

No approval-packet work is performed by this proposal. The already-recorded
PAUTH v2 and its owner evidence are prerequisites, not implementation targets.
No `.codex/` file is changed; those files are read-only parity evidence. The
three shared-regex consumer source files and their three unchanged covering
modules are also read-only verification evidence. If implementation proves any
eleventh path necessary, Prime Builder must stop and
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
| `DCL-SESSION-ROLE-RESOLUTION-001` | Unique, missing, ambiguous, cyclic, cross-harness, malformed, and closed edge cases; partial-write reverse lookup; three unrelated open siblings; live payload/ambient field configuration | Deterministic result or fail-closed error; only an exact explicit edge can redirect one requested id to another |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Shared parser case matrix against both canonical parsers | Both implement the anchored entire-first-line grammar for every positive and negative case |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Dedicated parser-regression modules plus the literal drift-lock tests | Both canonical parsers and the shared constant remain behaviorally aligned |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Receiver-side tests exercise a canonical first line with later prompt text and every malformed same-line form | Valid first-line owner commands relay; malformed commands remain non-authoritative |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Updated workstream-focus parity tests plus discovery diff | Claude/Codex routes both resolve; no workstream-focus finding; unrelated baseline disclosed |
| `ADR-CROSS-HARNESS-PARITY-001` | Execute adapter-level canonical prompt success/failure cases through Claude and Codex route fixtures | Equivalent observable persistence and warning behavior on both applicable harness routes |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Normal exact-session claim and implementation-start packet before any protected edit | Packet authorizes exactly the ten target paths and no emergency route is used |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict lifecycle resolver and post-implementation report chain | Valid append-only lifecycle; implementation starts only after independent GO |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table and exact command results | Every linked behavioral spec has fresh executed evidence |

Required implementation verification commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/parity_discovery_diff.py --json
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/_session_init_keyword.py scripts/session_role_resolution.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/_session_init_keyword.py scripts/session_role_resolution.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py
git diff --check -- .claude/hooks/workstream-focus.py .claude/settings.json groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/_session_init_keyword.py scripts/session_role_resolution.py scripts/session_self_initialization.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_canonical_init_keyword_syntax.py
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
fully green while accepting the canonical-first-line-plus-follow-up case.

The implementation report must rerun both complete sets and disclose every
remaining baseline failure exactly rather than relabeling unrelated failures
as fixed.

## Acceptance Criteria

1. An independent GO exists before any protected implementation mutation.
2. A normal exact-session claim and implementation-start packet authorize
   exactly the ten declared paths. Failure of either gate leaves source and
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
   keyed successor, while zero/multiple candidates and every peer without the
   exact edge fail visibly. Shared projections never authorize a role.
6. At least three open same-harness sibling documents cannot influence explicit
   predecessor selection. Continuity never crosses durable harness identity or
   changes the durable registry role map.
7. Both canonical init parsers conform to the anchored entire-first-line
   requirement across the complete positive/negative case matrix, including
   subsequent prompt lines and CRLF.
8. Claude's two workstream-focus commands use the in-root venv interpreter;
   canonical persistence failure yields a visible diagnostic; ordinary prompts
   remain silent.
9. The updated parity tests follow the actual Codex batch/wrapper route and pass
   for Claude and Codex. Discovery reports no `workstream-focus` finding; its 24
   unrelated baseline findings are neither widened nor claimed closed.
10. All required focused tests and Ruff checks pass for changed Python paths;
    unrelated baseline failures are disclosed exactly.
11. No eleventh protected implementation path, direct database mutation,
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

Rollback is one scoped commit revert. The predecessor, successor, and typed
binding fields are optional and additive, so documents without them remain
readable. No database or registry migration is required. Historical bridge and
session evidence is not deleted.

## Recommended Commit Type

`fix(session): preserve exact-session role continuity across re-key`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

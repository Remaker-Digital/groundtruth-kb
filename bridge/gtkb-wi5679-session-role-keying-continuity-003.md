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


# WI-5679 Session-Role Keying Continuity - Revised Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5679-session-role-keying-continuity
Version: 003
Date: 2026-07-28 UTC
Responds to: bridge/gtkb-wi5679-session-role-keying-continuity-002.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5679

target_paths: [".claude/hooks/workstream-focus.py", ".claude/settings.json", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/session_role_resolution.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_session_role_keying_continuity.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py"]

implementation_scope: source_test_configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

KB Mutation: This proposal performs no MemBase mutation.

---

## Revision Claim

This revision preserves the owner-approved C1-C5 repair and closes every
finding in version 002 without requesting emergency authority. It adds the two
applicable cross-harness parity specifications, supplies per-applicable-harness
evidence, removes unsupported pending-transcript claims, and makes normal
implementation-start authorization an absolute precondition.

The current project authorization is version 2. It preserves the WI-5679 and
WI-5504 work scope and every v1 control while removing the retired
`GOV-SESSION-ROLE-AUTHORITY-001` from its active specification references under
`DELIB-202667220`. This revision does not cite that retired record as governing
authority. Versions 001 and 002 remain immutable audit history.

No implementation has occurred. After an independent GO, Prime Builder must
acquire an exact-session `go_implementation` claim and obtain a normal
implementation-start packet for this exact seven-path target set. If either
operation fails, implementation stops with no protected mutation. There is no
emergency-bootstrap, environment-variable override, hand-edited envelope, role
impersonation, or file-safety bypass in this proposal.

## Findings Addressed

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

Add an optional `predecessor_session_id` to newly created authoritative
worker-session documents. SessionStart may link only the prior open document
for the same durable harness identity to the new document. Resolution from a
stale id follows a unique, acyclic, same-harness successor chain to its terminal
document. Ambiguous, cyclic, cross-harness, malformed, or closed-terminal
chains fail closed rather than selecting a role.

The resolution result records both requested and resolved session identity so
the continuity decision is auditable. The link changes no durable harness role
metadata.

### C2 - Bounded liveness backstop

When no valid continuity successor exists, an exact-id document may yield to
the current per-harness projection only when all of these facts hold: both
documents validate for the same durable harness identity, the projection is
open, the projection is newer, and its worker-role provenance is internally
valid. The result uses a distinct non-transcript resolution source and records
the requested and selected session ids.

The backstop is not a claim that a harness owns a role. It is a bounded
recovery rule for stale session identity, and it does not mutate either
document. Concurrent same-harness projection ownership remains separate work;
this change must not claim to close WI-5086, WI-5718, or WI-5721.

### C3 - Strict transcript-only restart inheritance

Before SessionStart creates a replacement document, inspect the prior open
same-harness document. Inherit its role only when validated
`worker_role_provenance.role_resolution_source` is
`transcript_init_keyword`. Carry that source and the predecessor id into the
successor. For every other source, use the durable registry role as a fallback
and label it `session_resolver_fallback`.

`scripts/session_role_resolution.py` must not label a registry-derived or
liveness-backstop role as `interactive_transcript`. Transcript authority is
reported only when validated transcript provenance exists.

### C4 - Canonical init-keyword parser convergence

Make `parse_canonical_init_keyword` exactly mirror the canonical anchored
first-line grammar used by `scripts/_session_init_keyword.py`. A shared case
matrix must prove both parsers agree for bare keywords, optional roles, final
newline and CRLF behavior, trailing spaces, leading spaces, extra prose,
case changes, and malformed role tokens.

No compatibility alias becomes canonical input, and no parser silently trims
or case-folds the prompt.

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
- The adapter consumes the payload session id, invokes the shared envelope
  implementation, and emits a diagnostic only for a canonical role-bearing
  prompt whose persistence fails.

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

The only implementation targets are the seven paths declared above. There is
no MemBase, registry, projection, bridge-runtime, dispatcher, specification,
project-authorization, credential, deployment, external-system, or Git-history
mutation in implementation scope. No approval-packet work is in scope.

No approval-packet work is performed by this proposal. The already-recorded
PAUTH v2 and its owner evidence are prerequisites, not implementation targets.
No `.codex/` file is changed;
those files are read-only parity evidence. If implementation proves any eighth
path necessary, Prime Builder must stop and file a new REVISED proposal rather
than consume GO authority beyond this list.

## Owner Decisions / Input

- `DELIB-202667477` Decisions 1 and 2 authorize the continuity chain plus
  liveness backstop and strict transcript-only inheritance.
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
  preservation of historical audit evidence. PAUTH v2 applies that direction.

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

## Prior Deliberations And Evidence

- `DELIB-202667477` - owner-approved WI-5679/WI-5504 design, project routing,
  and full C1-C5 scope.
- `DELIB-202667220` - owner-directed retirement and active-reference purge of
  the obsolete role-authority GOV.
- `DELIB-20265225` and `DELIB-20265224` - historical owner decisions for
  transcript-defined interactive role persistence across contiguous context.
- `DELIB-20260710-WI5086-CONCURRENT-CODEX-SESSION-ENVELOPE-CLOBBER` - sibling
  concurrency-axis evidence that this thread explicitly does not claim to
  close.
- `bridge/gtkb-wi5679-session-role-keying-continuity-002.md` - controlling
  NO-GO whose three findings this revision closes.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724`
  version 2 - active authorization with the retired GOV removed and all other
  work scope and controls preserved.

## Spec-Derived Verification Plan

| Specification | Executed evidence required | Required result |
| --- | --- | --- |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | New continuation tests create a transcript-derived predecessor, re-key SessionStart, and resolve from both old and new ids | Both resolve the same owner-declared role with explicit requested/resolved session provenance |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | Restart and resume tests cover transcript and non-transcript predecessors | Transcript role persists; fallback role does not self-perpetuate as transcript authority |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Unique, missing, ambiguous, cyclic, cross-harness, malformed, and closed chain cases; liveness-backstop cases | Deterministic result or fail-closed error; no implicit cross-harness selection |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Shared parser case matrix against both canonical parsers | Exact agreement for every positive and negative case |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Updated workstream-focus parity tests plus discovery diff | Claude/Codex routes both resolve; no workstream-focus finding; unrelated baseline disclosed |
| `ADR-CROSS-HARNESS-PARITY-001` | Execute adapter-level canonical prompt success/failure cases through Claude and Codex route fixtures | Equivalent observable persistence and warning behavior on both applicable harness routes |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Normal exact-session claim and implementation-start packet before any protected edit | Packet authorizes exactly the seven target paths and no emergency route is used |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict lifecycle resolver and post-implementation report chain | Valid append-only lifecycle; implementation starts only after independent GO |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table and exact command results | Every linked behavioral spec has fresh executed evidence |

Required implementation verification commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/parity_discovery_diff.py --json
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_role_resolution.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_role_resolution.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py
git diff --check -- .claude/hooks/workstream-focus.py .claude/settings.json groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_role_resolution.py scripts/session_self_initialization.py platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Baseline disclosure: a fresh 68-test focused run produced 64 passed and 4
failed. Two failures are the in-scope stale Codex direct-registration
assertions in `test_workstream_focus_hook_parity.py`. The other two are
pre-existing activity-profile rendering expectations in
`test_session_envelope_runtime.py`, outside this target set and unrelated to
session-role continuity. The implementation report must rerun and disclose
both baselines rather than relabeling unrelated failures as fixed.

## Acceptance Criteria

1. An independent GO exists before any protected implementation mutation.
2. A normal exact-session claim and implementation-start packet authorize
   exactly the seven declared paths. Failure of either gate leaves source and
   configuration untouched.
3. A transcript-derived role survives a same-harness session re-key through an
   explicit, unique, acyclic predecessor chain.
4. A registry-fallback role is never inherited or reported as
   `interactive_transcript`.
5. The liveness backstop is same-harness, open, newer-only, auditable, and
   non-mutating; ambiguous or invalid evidence fails closed.
6. Continuity never crosses durable harness identity and never changes the
   durable registry role map.
7. Both canonical init parsers agree on the complete positive/negative case
   matrix.
8. Claude's two workstream-focus commands use the in-root venv interpreter;
   canonical persistence failure yields a visible diagnostic; ordinary prompts
   remain silent.
9. The updated parity tests follow the actual Codex batch/wrapper route and pass
   for Claude and Codex. Discovery reports no `workstream-focus` finding; its 24
   unrelated baseline findings are neither widened nor claimed closed.
10. All required focused tests and Ruff checks pass for changed Python paths;
    unrelated baseline failures are disclosed exactly.
11. No eighth implementation path, MemBase mutation, registry mutation,
    specification mutation, dispatcher action, push, history rewrite, release,
    deployment, credential operation, or external-system mutation occurs.

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

The principal risk is cross-session role borrowing. Unique same-harness links,
cycle and ambiguity rejection, explicit requested/resolved ids, strict
transcript provenance, and negative cross-harness tests bound that risk. The
liveness backstop remains intentionally narrower than a general latest-open
session selector and does not claim to solve peer-session projection ownership.

The hook warning must remain fail-soft so a diagnostic gap does not block useful
work. It reports persistence failure without invalidating content or adding a
permission boundary, consistent with the owner's path-of-least-resistance
governance direction.

Rollback is one scoped commit revert. `predecessor_session_id` is optional and
additive, so documents without it remain readable. No database or registry
migration is required. Historical bridge and session evidence is not deleted.

## Recommended Commit Type

`fix(session): preserve exact-session role continuity across re-key`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

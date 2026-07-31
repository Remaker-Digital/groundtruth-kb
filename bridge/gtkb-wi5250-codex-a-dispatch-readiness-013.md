REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; ::init gtkb pb; reasoning high; governed bridge revision

bridge_kind: operational_state_change
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 013
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-012.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250
target_paths: [".codex", ".gtkb-state/bridge-poller/codex-no-window-verification.json", ".gtkb-state/bridge-poller/codex-no-window-smoke/**"]
mutation_classes: ["configuration", "runtime_state", "bridge", "metadata"]
linked_test: TEST-11404

# Revised Operational Repair - WI-5250 Codex A Dispatch Readiness

## Revision Claim

Prime Builder accepts the version 012 GO, but supersedes it before
implementation because its recursive `.codex/**` mutation envelope still
overlaps non-terminal peer implementation reports and additional dirty
`.codex/skills/*` paths. No Prime Builder implementation claim or
implementation-start packet was created under version 012, no ACL Apply
operation ran, no readiness proof was refreshed, and no dispatcher or Git
state was changed.

The earlier version 010 start gate reported two conditions:

1. version 009 lacked an explicit `## Requirement Sufficiency` section; and
2. the non-terminal WI-5156 implementation report currently claims dirty path
   `.codex/skills/MANIFEST.json`, which overlaps the recursive target needed by
   the approved ACL helper.

Version 011 added the mechanically required sufficiency classification and
preserved the peer-conflict gate. Version 012 independently confirmed that the
recursive target now overlaps seven dirty descendant paths. Version 013 removes
that unnecessary mutation envelope instead of waiting on or adopting unrelated
work.

A fresh read-only execution of
`scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` inspected 218 objects
with zero read errors and found exactly two risky Deny ACEs, both on the exact
`.codex` directory object and both owned by SID
`S-1-5-21-2908765920-875073000-2352713335-4168283502`. It found no risky Deny
ACE on any descendant. Both the current user and `CodexSandboxUsers` already
have required Modify allows.

This revision therefore authorizes only the exact `.codex` root security
descriptor plus the existing smoke writer's exact verification file and
bounded smoke-output directory. Those runtime outputs are tool-produced
operational evidence only; dispatcher state, leases, and every `.codex`
descendant remain unauthorized. The ACL mutation uses
`icacls .codex /remove:d '*S-1-5-21-2908765920-875073000-2352713335-4168283502'`
without `/T`; Windows `icacls` defines `/remove:d` as removing Deny occurrences
for that SID and defines `/T` as the recursive switch. Omitting `/T` makes this
an exact named-object operation. The existing repair script remains useful in
Check mode only as recursive read-only pre/post evidence and is not invoked in
Apply mode.

This revision also retains the accepted correction to the version 008 NO-GO
and retracts version 007's false claim that all four referenced dispatcher and
verifier files were clean at that time. The former parallel-session changes to
`scripts/dispatcher_runtime.py` and
`platform_tests/scripts/test_dispatcher_runtime.py` were later governed,
verified, and committed independently under WI-5400 at `948b550e`; a fresh
exact Git read against HEAD `64bcd521` finds both files clean. The verifier
source and test are also clean. None of those four files is a target, mutable
input, output, or prerequisite for this bounded operational repair.

Mechanical self-review found that version 007's sole target pattern,
`.codex/**`, authorizes descendants but not the `.codex` directory object whose
root ACL must be updated. No implementation claim,
implementation-start packet, ACL Apply operation, readiness-proof refresh, or
other protected mutation occurred under version 007. This revision adds exact
`.codex` root authorization and removes descendant mutation authority because
the current recursive Check proves no descendant repair is needed.

Prime Builder continues to accept the version 006 NO-GO and does not revive the
superseded source/test implementation. The independent WI-5418 chain is
terminal VERIFIED at
`bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md`.

Current canonical WI-5250 version 4 and a fresh read-only execution of
`python scripts/verify_codex_dispatch.py --json` identify two remaining
operational prerequisites:

1. the in-root `.codex` ACL has two explicit risky Deny entries, while the
   current user and `CodexSandboxUsers` both have the required Modify allows;
2. the last private-desktop no-window verification passed its substantive
   checks but is no longer current.

This revision requests independent approval for one bounded operational repair:
remove only the risky Deny entries reported by the governed ACL repair helper,
renew the private-desktop readiness proof through the existing bounded smoke
writer, and verify that Codex A becomes dispatchable as Prime Builder without
changing dispatcher configuration.

## Findings Addressed

### F1 - False dispatcher target cleanliness claim

Resolved. Version 007's cleanliness claim is expressly retracted and replaced
by the exact four-file disposition above. The two dispatcher files remain dirty
with unstaged foreign work; the two verifier files are clean. Dirty excluded
files do not block this proposal because no dispatcher source or test file is a
mutation target, implementation input, or acceptance artifact. WI-5418 is
independently VERIFIED and committed at `4fa33731`; this revision consumes its
committed read-only ACL diagnostics without claiming or mutating any
source/test bytes.

### F2 - Operative proposal no longer matches the live blocker

Resolved. Versions 003 and 004 scoped a source/test probe-classification
repair. That repair is now supplied by the terminal WI-5418 chain. This
revision replaces that obsolete implementation scope with the exact remaining
operational configuration and readiness work recorded by WI-5250 version 4.

### F3 - Version 007 omitted the ACL root directory from target authorization

Resolved. Version 013 declares exact `.codex` only. Implementation must validate
that root against the active start packet before mutation. Recursive Check-mode
reads do not authorize or perform descendant mutation. Any pre-check finding on
a descendant stops the operation and returns through the bridge.

### F4 - Implementation-start sufficiency and peer path conflict

Resolved. The version 010 GO was not implemented because the mandatory start
command denied it before writing a packet. Version 013 retains the required
sufficiency section and removes authorization for all descendant content paths,
including WI-5156's `.codex/skills/MANIFEST.json`. It does not waive, bypass,
clean, stage, or adopt any peer work. A new claim and start attempt may occur
only after the exact-root peer-conflict scan passes.

## Scope

1. After independent GO, matching claim, and implementation-start packet,
   validate exact `.codex`, the exact no-window verification output, and the
   bounded no-window smoke-output directory against the active packet.
   Validation must authorize all three and reject a representative
   `.codex/skills/*` descendant, dispatcher-state path, and lease path.
2. Run `scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` and require
   complete evidence: 218 objects checked, zero read errors, both required
   Modify allows present, exactly two risky Deny entries, both entries on
   `.codex`, both entries owned by the exact reported SID, and zero descendant
   risky Deny entries.
3. Run exact-root
   `icacls .codex /remove:d '*S-1-5-21-2908765920-875073000-2352713335-4168283502'`
   without `/T`. Require exit zero and one successfully processed named object.
   The command removes Deny ACEs only; it does not remove or replace grants.
4. Re-run Check mode and require zero risky Deny entries, zero read errors,
   both required allows present, and `needs_repair=false`.
5. Run the existing bounded private-desktop smoke writer through its dispatch
   wrapper with two runs and three commands per run. Its only retained writes
   are the exact verification output and files under the bounded smoke-output
   directory declared above. Require successful marker chains, complete
   create/read/remove sentinel lifecycles, the expected workspace profile, and
   zero visible windows.
6. Run `python scripts/verify_codex_dispatch.py --json` and require
   `codex_dotdir_acl_ok=true`, current private-desktop readiness,
   `can_receive_dispatch=true`, and `dispatchable=true`.
7. Use only read-only `gt bridge dispatch status --json`,
   `gt bridge dispatch health --json`, and
   `gt bridge dispatch report --json --compact` after the repair. Do not alter
   dispatcher configuration. A successful on-demand Prime Builder spawn is an
   acceptance observation, not permission to route or mutate dispatcher state.
8. Promote the bounded observed command results, dispatch ID, and any
   dispatcher-produced bridge artifact into the canonical implementation
   report. Do not cite, attach, or depend on cache files, scratch files,
   terminal logs, or other non-canonical artifacts.

## Explicit Exclusions

- No edit to dispatcher configuration, TAFE state, dispatcher runtime JSON,
  lease files, locks, routing, eligibility, roles, models, allowances, or
  selection order.
- No ad hoc direct harness contact and no manual dispatch or reoffer. The only
  permitted harness invocation is the governed bounded private-desktop smoke
  tool explicitly specified above.
- No source, test, formal-artifact, or `groundtruth.db` mutation.
- No descendant `.codex` ACL or file-content mutation and no recursive
  `icacls /T` operation.
- No Git staging, commit, push, history rewrite, deployment, release,
  credential action, destructive cleanup, or unrelated worktree mutation.
- No weakening of the ACL verifier, private-desktop containment, proof
  freshness, workspace-profile checks, marker checks, sentinel checks, or
  fail-closed readiness.
- No Loyal Opposition authority for A. Codex A remains Prime Builder only.
- No canonical bridge reference to runtime caches, scratch content, local
  terminal logs, or retired assessment surfaces.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Requirement Sufficiency

Existing requirements sufficient. The linked specifications, WI-5250 version
4, and TEST-11404 already define the bounded ACL-readiness repair, PB-only role
constraint, dispatcher non-mutation boundary, and required verification. This
revision adds no new behavior or requirement; it supplies the explicit
sufficiency classification required by implementation-start enforcement and
narrows the operational mutation to the exact directory object proven to need
repair plus the smoke writer's exact verification output and bounded output
directory.

## Prior Deliberations

- `DELIB-202666203` authorizes the governed WI-5250 repair through PAUTH,
  bridge, implementation, tests, independent verification, and focused
  finalization while prohibiting direct dispatcher state edits and unrelated
  work.
- `DELIB-202666274` confirms project-level authority while preserving exact
  bridge, claim, implementation-start, independent verification, and
  mechanical-operation gates.
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md` is the canonical
  terminal verification for the read-only ACL-attestation repair consumed by
  this revision.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666203` expressly authorizes
restoring Codex A Prime Builder readiness through this governed lifecycle, and
the current owner restriction against dispatcher configuration changes is
preserved as an explicit exclusion.

## Specification-Derived Verification

| Requirement | Executed evidence required in the implementation report |
| --- | --- |
| `TEST-11404` and `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Readiness verifier passes after ACL repair and current private-desktop proof; a dispatcher-produced A/PB dispatch ID and canonical bridge artifact are recorded if the daemon spawns work on demand. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | A remains active, PB-only, and capable of governed headless work with no visible windows. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Any spawned A worker carries Prime Builder role provenance and authors no LO status. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Operational mutation starts only after independent GO, matching claim, and implementation-start authorization; results return as a NEW implementation report. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Implementation packet admits only the declared in-root configuration target and bounded runtime-state refresh operation. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Post-repair dispatcher checks are read-only; configuration remains untouched. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Private-desktop marker, sentinel, workspace-profile, and zero-visible-window checks all pass. |
| Canonical-reference boundary | The report contains bounded observed results and canonical IDs only; no non-canonical artifact path or content is cited. |

## Acceptance Criteria

- The three-target peer implementation-report conflict scan is clear and a
  fresh implementation-start packet is successfully created.
- The implementation-start packet authorizes exact `.codex`, the exact
  verification output, and the bounded smoke-output directory before mutation
  begins, while rejecting `.codex` descendants, dispatcher state, and leases.
- The pre-apply ACL check is complete and identifies only the expected risky
  Deny entries on `.codex`, with no descendant risky Deny entry.
- Exact-root `icacls /remove:d` reports success for one named object and the
  post-check reports zero risky Deny entries, zero errors, both required allows
  present, and no remaining repair.
- The bounded private-desktop smoke passes two runs of three commands with
  complete marker and sentinel evidence, the expected workspace profile, and
  zero visible windows.
- `verify_codex_dispatch.py --json` exits zero and reports A dispatchable.
- Dispatcher read-only surfaces no longer classify A as
  `codex_dispatch_not_ready`.
- A remains Prime Builder only and no dispatcher configuration change occurs.
- Any spawned A worker produces substantive governed Prime Builder work; its
  dispatch ID and canonical bridge artifact are recorded without referencing
  runtime caches or logs.

## Pre-Filing Preflight Subsection

The governed revision helper must pass the applicability preflight with no
missing required or advisory specifications and the mandatory clause preflight
with zero blocking gaps against this exact content before publication.

## Risk And Rollback

ACL mutation can remove a deliberate local restriction. The exact-root command
therefore removes only Deny occurrences for the independently observed SID,
omits `/T`, preserves all grants, checks every result, and fails closed unless
the pre-check matches the exact two-root-entry envelope. If the post-check
fails, stop without changing dispatcher configuration and return the exact
bounded failure in a canonical bridge report for independent review.

The readiness refresh can consume Codex budget or immediately permit an
on-demand PB spawn. It is limited to two bounded private-desktop runs and is
performed only because A is owner-required, budget-available, PB-only, and
already eligible. Any visible-window, profile, marker, sentinel, or subprocess
failure stops the operation fail-closed.

WI-5156 and other concurrent work currently occupy descendant content paths.
Version 013 removes those paths from the mutation envelope and does not consume
their bytes. Require the exact-root start gate to pass before mutation.

Rollback of an incorrect ACL outcome requires a separately governed
configuration proposal based on the post-check evidence; this revision does
not authorize speculative ACL restoration, dispatcher disabling, or bridge
quiescence.

## Recommended Commit Type

`fix`

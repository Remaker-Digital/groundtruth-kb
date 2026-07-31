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
Version: 007
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-006.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250
target_paths: [".codex/**"]
mutation_classes: ["configuration", "runtime_state", "bridge", "metadata"]
linked_test: TEST-11404

# Revised Operational Repair - WI-5250 Codex A Dispatch Readiness

## Revision Claim

Prime Builder accepts the version 006 NO-GO and does not revive the superseded
source/test implementation. The dependency condition that blocked version 004
has cleared: the four former source/test targets are clean, and the independent
WI-5418 chain is terminal VERIFIED at
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

### F1 - Unresolved dependencies and dirty shared dispatcher targets

Resolved for this revision. No dispatcher source or test file is a mutation
target. `scripts/dispatcher_runtime.py`,
`platform_tests/scripts/test_dispatcher_runtime.py`,
`scripts/verify_codex_dispatch.py`, and
`platform_tests/scripts/test_verify_codex_dispatch.py` are clean relative to
HEAD. WI-5418 is independently VERIFIED and committed at `4fa33731`; this
revision consumes its repaired read-only ACL diagnostics without adopting
uncommitted source bytes.

### F2 - Operative proposal no longer matches the live blocker

Resolved. Versions 003 and 004 scoped a source/test probe-classification
repair. That repair is now supplied by the terminal WI-5418 chain. This
revision replaces that obsolete implementation scope with the exact remaining
operational configuration and readiness work recorded by WI-5250 version 4.

## Scope

1. Run `scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json` and require
   complete evidence: zero read errors, both required Modify allows present,
   and exactly the reported risky Deny entries eligible for repair.
2. Run `scripts/repair_codex_dotdir_acl.ps1 -Mode Apply -Json`. The helper must
   remain bounded to the in-root `.codex` directory, remove only explicit risky
   Deny entries, preserve non-risky rules, and preserve or establish the two
   required Modify allows.
3. Re-run Check mode and require zero risky Deny entries, zero read errors,
   both required allows present, and `needs_repair=false`.
4. Run the existing bounded private-desktop smoke writer through its dispatch
   wrapper with two runs and three commands per run. Require successful marker
   chains, complete create/read/remove sentinel lifecycles, the expected
   workspace profile, and zero visible windows.
5. Run `python scripts/verify_codex_dispatch.py --json` and require
   `codex_dotdir_acl_ok=true`, current private-desktop readiness,
   `can_receive_dispatch=true`, and `dispatchable=true`.
6. Use only read-only `gt bridge dispatch status --json`,
   `gt bridge dispatch health --json`, and
   `gt bridge dispatch report --json --compact` after the repair. Do not alter
   dispatcher configuration. A successful on-demand Prime Builder spawn is an
   acceptance observation, not permission to route or mutate dispatcher state.
7. Promote the bounded observed command results, dispatch ID, and any
   dispatcher-produced bridge artifact into the canonical implementation
   report. Do not cite, attach, or depend on cache files, scratch files,
   terminal logs, or other non-canonical artifacts.

## Explicit Exclusions

- No edit to dispatcher configuration, TAFE state, runtime JSON, lease files,
  locks, routing, eligibility, roles, models, allowances, or selection order.
- No direct harness contact and no manual dispatch or reoffer.
- No source, test, formal-artifact, or `groundtruth.db` mutation.
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

- The pre-apply ACL check is complete and identifies only the expected risky
  Deny entries as repairable.
- Apply mode reports success and the post-apply check reports zero risky Deny
  entries, zero errors, both required allows present, and no remaining repair.
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

ACL mutation can remove a deliberate local restriction. The approved helper
therefore removes only explicit risky Deny rules, preserves non-risky rules,
checks every result, and fails closed on any read or write error. If the
post-check fails, stop without changing dispatcher configuration and return the
exact bounded failure in a canonical bridge report for independent review.

The readiness refresh can consume Codex budget or immediately permit an
on-demand PB spawn. It is limited to two bounded private-desktop runs and is
performed only because A is owner-required, budget-available, PB-only, and
already eligible. Any visible-window, profile, marker, sentinel, or subprocess
failure stops the operation fail-closed.

Rollback of an incorrect ACL outcome requires a separately governed
configuration proposal based on the post-check evidence; this revision does
not authorize speculative ACL restoration, dispatcher disabling, or bridge
quiescence.

## Recommended Commit Type

`fix`

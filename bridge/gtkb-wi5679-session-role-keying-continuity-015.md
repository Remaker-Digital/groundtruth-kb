REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# WI-5679 Session-Role Keying Continuity — CF-01 Requirement-Aligned Revision

bridge_kind: prime_proposal
Document: gtkb-wi5679-session-role-keying-continuity
Version: 015
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5679-session-role-keying-continuity-014.md
Amends approved proposal: bridge/gtkb-wi5679-session-role-keying-continuity-011.md
Supersedes correction: bridge/gtkb-wi5679-session-role-keying-continuity-013.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5679

target_paths: [".claude/hooks/workstream-focus.py", ".claude/settings.json", "config/hooks/gtkb-workstream-focus.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/_session_init_keyword.py", "scripts/session_role_resolution.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_session_role_keying_continuity.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_session_init_keyword_matching.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py"]

implementation_scope: source_test_configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

This filing is proposal-only. It changes no source, test, configuration,
MemBase, repository-history, dispatcher, deployment, or external-system state.

---

## Summary

Version 014 correctly blocked implementation until the governing session-role
resolution constraint was amended. That prerequisite is now live:
`DCL-SESSION-ROLE-RESOLUTION-001` version 7, changed at
`2026-07-29T08:06:01+00:00`, requires unresolved identity to fail closed,
forbids durable-registry fallback as worker behavior authority, and forbids the
`session_resolver_fallback` label.

This revision therefore applies owner decision
`AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01 to exactly the first sentence of C3.
C3's second sentence and the complete C1-C5 scope approved in version 011 are
retained. No target path, other clause, cross-harness disposition, closure
commitment, stop rule, or verification surface is changed.

## Mechanically Correct Status

`REVISED` is the mechanically correct status for version 015 because the live
latest status is version 014 `NO-GO`. The earlier version 013 `NO-ACTION` was
mechanically correct when version 012 `GO` was latest: it rejected an approval
that had become non-compliant after CF-01. Version 014 then routed the thread
back to Prime Builder with one prerequisite. With that prerequisite satisfied,
the ordinary `NO-GO` to `REVISED` transition applies.

## Findings Resolution

| Source | Finding or obligation | Resolution in version 015 |
| --- | --- | --- |
| v014 F1 (P0) | The live DCL still allowed the behavior CF-01 prohibits. | **Closed by live requirement evidence.** `DCL-SESSION-ROLE-RESOLUTION-001` v7 now requires fail-closed unresolved identity, prohibits durable-registry behavior fallback, and prohibits `session_resolver_fallback`. |
| CF-01 | Change only C3's first sentence. | **Applied exactly.** The replacement sentence below is the only C3 amendment. |
| CF-01 / `DELIB-202667477` Decision 4 | Retain C3 sentence 2 and the complete C1-C5 scope. | **Retained.** All sixteen targets and every non-C3 implementation and verification obligation from v011 remain unchanged. |
| v012 N1-N6 | Preserve implementation-time stop rules and report obligations. | **Retained.** No N1-N6 disposition is weakened or removed; the eventual report must answer them exactly as required by v012 and v013. |
| v014 implementation prohibition | Do not implement from GO-012 or NO-ACTION-013. | **Honored.** This revision performs no implementation and requests a fresh independent verdict. |

## C3 Amendment

In version 011 clause C3, replace only the first sentence identified by version
013:

> For every other source, use the durable registry role as a fallback and label
> it `session_resolver_fallback`.

with:

> For every other source, unresolved identity fails closed: do not use the
> durable registry role as a fallback and do not produce the
> `session_resolver_fallback` label.

Retain the immediately following C3 sentence verbatim:

> The fallback must resolve for the already validated named harness id;
> unresolved identity fails visibly and may not consume a generic default role.

The retained sentence remains a defensive constraint on fallback-shaped legacy
input. It does not authorize the resolver to produce a registry fallback or the
prohibited label for unresolved identity. Any other version-011 prose that
describes a genuinely fresh `source=startup` event as taking a registry-fallback
branch is non-operative to the extent it conflicts with CF-01 and the live DCL
v7. In that case the implementation must return a typed fail-closed result.

## Retained C1-C5 Scope

- **C1:** explicit same-harness session continuity through validated,
  auditable predecessor/successor bindings.
- **C2:** bounded reverse-link liveness recovery from an authoritative keyed
  successor; shared projections never authorize role behavior.
- **C3:** strict transcript-only restart inheritance, amended only by the
  sentence-level fail-closed rule above.
- **C4:** canonical first-line init-keyword parser convergence with task-text
  passthrough and strict scalar CLI handling.
- **C5:** deterministic project-venv hook invocation, visible fail-soft
  diagnostics, and byte-identical registered hook copies.

The exhaustive parser-consumer/assertion closure table, cross-harness
disposition, sixteen-path scope, baselines, acceptance criteria, risks, and
rollback in version 011 remain incorporated by reference without change.

## Cross-Harness Disposition

Disposition: **behavioral parity for the applicable Claude/Codex population;
no typed waiver requested.**

- **Claude:** `.claude/hooks/workstream-focus.py` and its registered canonical
  copy `config/hooks/gtkb-workstream-focus.py` must remain byte-identical. The
  two `.claude/settings.json` registrations use the in-root project venv, and
  the prompt adapter applies the same fail-closed C3 rule without discarding
  later task text.
- **Codex:** `.codex/hooks.json` continues to route through the existing batch
  wrapper and `.codex/gtkb-hooks/workstream-focus.cmd` to the same canonical
  adapter. No Codex source or configuration edit is required; the v011 parity
  tests must follow this real indirection and prove equivalent observable role
  persistence and failure behavior.
- **Other harnesses:** C1-C4 remain shared, harness-neutral behavior and retain
  the v011 cross-harness negative coverage. No harness outside the current
  Claude/Codex hook-configuration population is silently counted as passing.

CF-01 narrows unresolved-identity behavior identically for every applicable
harness: none may consult the durable registry as worker behavior authority or
emit `session_resolver_fallback`. The v011 parity discovery and all adapter-level
checks remain mandatory; unrelated baseline findings are neither widened nor
claimed closed.

## Scope Boundary

This proposal retains exactly the sixteen protected implementation targets
declared above. It authorizes no seventeenth path, direct database mutation,
registry mutation, specification mutation, dispatcher action, push, history
rewrite, release, deployment, credential operation, or external-system
mutation. If implementation requires another protected path or changes an
undeclared assertion module, Prime Builder must stop and re-file.

The DCL v7 amendment is completed prerequisite evidence, not a mutation by this
worker and not an implementation target. This filing performs no MemBase write,
as required by owner decision CF-10.

## Requirement Sufficiency

**Existing requirements sufficient.** The live
`DCL-SESSION-ROLE-RESOLUTION-001` v7 now states the CF-01 fail-closed behavior,
removes durable-registry behavior fallback for unresolved identity, and forbids
the `session_resolver_fallback` label. Together with the retained persistence,
init-keyword, parity, bridge, project-authorization, and verification
requirements below, it fully governs the unchanged C1-C5 implementation scope.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `DCL-SESSION-ROLE-RESOLUTION-001` v7
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Prior Deliberations

- `DELIB-202667477` — owner-approved continuity chain, liveness recovery,
  strict transcript-only inheritance, normal bridge routing, and complete
  C1-C5 scope; Decision 4 keeps WI-5504 folded into this thread.
- `DELIB-202667523` — authorizes the manual program lane while preserving the
  complete bridge, claim, implementation-start, report, and verification
  lifecycle; it does not activate the dispatcher.
- `DELIB-202665211` — owner decision that an explicitly declared interactive
  role persists for the session-scoped lifetime.
- `DELIB-20263212` — owner requirement that the init envelope persists across
  compaction and resume within one contiguous model context.
- `bridge/gtkb-wi5679-session-role-keying-continuity-011.md` — the complete
  approved C1-C5 proposal retained except for the one C3 sentence.
- `bridge/gtkb-wi5679-session-role-keying-continuity-013.md` — the mechanically
  correct `NO-ACTION` that first captured CF-01 and invalidated GO-012.
- `bridge/gtkb-wi5679-session-role-keying-continuity-014.md` — the controlling
  `NO-GO`; its sole DCL-amendment prerequisite is closed by live DCL v7.

The required semantic search for `session role keying continuity fail closed`
returned `DELIB-202665211`, `DELIB-20263212`, `DELIB-202665708`,
`DELIB-20261005`, and `DELIB-20261200`. The first two are directly relevant;
the latter three are historical verification context and do not override
CF-01 or DCL v7.

## Owner Decisions / Input

- `AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01 requires unresolved identity to
  fail closed, forbids durable-registry fallback and the
  `session_resolver_fallback` label, and retains C3 sentence 2 and the complete
  C1-C5 scope.
- `DELIB-202667477` Decision 4 retains WI-5504 parser and hook hardening within
  this implementation scope.
- `DELIB-202667523` preserves manual routing without waiving any bridge or
  implementation-start gate and without enabling the dispatcher.

No new owner decision is required.

## Specification-Derived Test Plan

| Governing specification or decision | Derived verification | Required result |
| --- | --- | --- |
| `DCL-SESSION-ROLE-RESOLUTION-001` v7 / CF-01 | `test_unresolved_identity_fails_closed_without_registry_fallback` in `platform_tests/scripts/test_session_role_keying_continuity.py` | Unresolved identity returns a typed fail-closed result without consulting or substituting the durable registry role. |
| `DCL-SESSION-ROLE-RESOLUTION-001` v7 / CF-01 | `test_unresolved_identity_never_emits_session_resolver_fallback` | No unresolved-identity path emits `session_resolver_fallback`. |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` / `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | Retain transcript-predecessor, explicit-edge, reverse-link, peer, cycle, malformed, and restart/resume cases from v011. | Valid transcript evidence persists; invalid or absent identity fails closed without cross-session borrowing or registry substitution. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and both init-keyword DCLs | Retain all parser, workstream-passthrough, CLI-scalar, LF/CRLF, and cross-harness checks from v011. | C4/C5 behavior remains unchanged by this surgical C3 amendment. |
| Cross-harness parity specifications | Re-run the v011 hook-parity tests and parity discovery. | Claude/Codex behavior remains equivalent and no new workstream-focus finding appears. |
| Bridge, project-linkage, and verification specifications | Re-run both bridge preflights, obtain a fresh independent GO, acquire an exact `go_implementation` claim, and obtain a fresh implementation-start packet before any protected edit. | Zero missing specs, zero blocking clause gaps, latest GO, and exact sixteen-path authorization. |

All four version-011 pytest blocks, parity discovery, separate Ruff lint and
format gates, and `git diff --check` remain mandatory. Before the eventual
implementation report, re-derive any baseline changed by a predecessor such as
WI-5718. The report must carry forward all nineteen specification links and
answer GO-012 N1-N6, including the supporting-metadata timing disclosure.

## Acceptance Criteria

1. Independent Loyal Opposition issues a fresh GO against this v015 revision;
   GO-012 remains invalid implementation authority.
2. Before protected edits, Prime Builder acquires the exact-session
   `go_implementation` claim and an implementation-start packet authorizing
   exactly the sixteen declared paths.
3. Unresolved identity fails closed without durable-registry substitution and
   without producing `session_resolver_fallback`.
4. C3 sentence 2 and all non-C3 C1-C5 requirements, closure commitments,
   parser-consumer dispositions, parity obligations, and stop rules from v011
   remain unchanged.
5. Every linked behavioral specification has fresh executed evidence in the
   post-implementation report, including the two CF-01 regressions.
6. No source, test, configuration, MemBase, dispatcher, commit, release,
   deployment, credential, or external-system mutation occurs during this
   proposal-only filing.

## Pre-Filing Preflight Evidence

Both mandatory candidate preflights ran through their `--content-file`
surfaces before filing.

- Applicability preflight: exit `0`; `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; `warnings.missing_parent_dirs: []`;
  `warnings.unclassified_target_paths: []`; pre-evidence packet hash
  `sha256:a9dde1a08a710ad0e1877b74eafeebfc95d6d74856b933c2a8b6545de5e7f143`.
  Draft-only author-metadata warnings are expected; the governed helper inserts
  authoritative metadata before publication.
- Clause preflight: exit `0`; five clauses evaluated; three `must_apply`, two
  `may_apply`, zero evidence gaps in must-apply clauses, and zero blocking gaps.

The governed revision helper must re-run the same gates after authoritative
author metadata is inserted. Any missing specification, blocking clause gap,
or publication denial aborts filing.

## Risks And Rollback

The primary risk is accidentally treating unresolved identity as a named
harness and silently recovering the durable registry role. CF-01 and DCL v7
remove that privilege path. The retained explicit-edge validation, typed
fail-visible errors, cross-harness negatives, parser-consumer coverage, and
source-classification tests bound the remaining risk.

This version is append-only and proposal-only. Rollback is a later governed
bridge disposition; versions 001 through 014 remain immutable. No source,
MemBase, or commit rollback is needed for this filing.

## Recommended Commit Type

`fix(session): fail closed when session identity is unresolved`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

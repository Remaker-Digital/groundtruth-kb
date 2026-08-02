REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit_owner_direction

bridge_kind: prime_proposal
Document: gtkb-wi5804-timer-inventory-evidence-classification
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5804-timer-inventory-evidence-classification-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5804
target_paths: ["scripts/timer_inventory.py", "config/governance/timer-inventory.toml", "platform_tests/scripts/test_timer_inventory.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Prime Builder Revision — Authoritative Timer, Threshold, And Concurrency Inventory

## Revision Claim

Prime Builder accepts v004's finding that v003 could not terminate unimplemented
work merely because no live claim remained. This revision restores a complete,
reviewable proposal and incorporates the owner-expanded configuration scope now
recorded in WI-5804 v3 and `DELIB-202667748`.

Prime Builder rejects two v004 premises. WI-5804 does not require per-work-item
approval: it is an active member of active `PROJECT-GTKB-TIMER-GOVERNANCE` and
inherits the active, unexpired, list-free whole-project PAUTH v2. The v003 Prime
session and v004 Loyal Opposition session also have distinct session-context
identities; there is no same-session self-review conflict.

No implementation exists. All three declared targets are absent and clean, the
exact bridge claim is null, and project and work-item dependencies are empty.
This filing authorizes no implementation. A fresh independent GO, exact claim,
and implementation-start packet remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. Proposal v001 remains technically useful,
but its timer-only vocabulary is now incomplete. The current WI v3 requirement
and owner deliberations supply the full configurable control class:

- timers, TTLs, expiries, grace windows, timeouts, and wall-clock bounds;
- retry counts, retry intervals, and backoff schedules;
- throttles and rate limits;
- detector, gate, queue, capacity, and other operational thresholds;
- dispatch and worker fan-out scale; and
- global, role, provider, project, and per-harness concurrency limits.

The program target is removal of hard-coded policy values and migration to a
centralized source of truth. `env.local` under `GOV-ENV-LOCAL-AUTHORITY-001` and
a dedicated typed registry are the candidate authorities. This inventory slice
does not choose between them or relocate a value; it produces the evidence and
classification required for that later decision and migration. A record may
remain `undecided` only when it carries the unresolved authority question and
the evidence needed to decide it; `undecided` is not a permanent hard-coded
exception.

## Motivating Evidence And Measurement Boundary

The baseline quoted by WI-5804 — 495 literal assignments across 138 production
files — was not reproducible during proposal v001's fresh derivation. Strict and
loose patterns produced materially different totals and named top carriers, and
inline call literals plus JSON/TOML values exceeded the named-constant surface.
No unreproducible count becomes canonical. The extractor's versioned extraction
specification and first generated output establish the reproducible baseline.

Observed duration distributions are also right-censored by current grants: an
operation killed by a short bound is absent from the surviving-duration sample.
The inventory therefore records failures, cancellations, and censored events
separately from successful durations and forbids sizing a correction solely
from the p99 of survivors.

Relevant observed failures include WI-5694 packet expiry, WI-5788 registry-lock
hard timeouts, WI-5784/WI-5795 work-intent database contention, the protected
commit checker overrun, and the WI-5804 proposal worker losing its own short
draft claim mid-work. These are classification evidence, not value changes.

Fresh corroboration occurred while filing this v005: the governed writer
exhausted `_RegistryFileLock`'s fixed acquisition window for
`.gtkb-state/sot-registry/control-plane.lock` before creating the numbered
file. The target remained absent and the exact claim remained valid. Open
WI-5869 owns correction of this measured timeout/fairness class, and
`bridge/gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md`
already preserves the concurrency and SoT-latency advisory; this proposal does
not duplicate either artifact.

## Proposed Scope

### Deterministic extractor

Add `scripts/timer_inventory.py`, a read-only deterministic service that walks
declared in-root production surfaces and emits exactly one generated artifact.
Its output embeds the extraction-spec version and digest, surface roots,
include/exclude rules, parser/pattern inventory, generating commit, and per-class
counts. Re-running against an unchanged tree must be byte-identical.

The extractor covers named constants, inline call/keyword literals, SQLite
pragmas, JSON and TOML values, hook-embedded values, harness capability and
dispatch settings, and configuration values expressed as counts or thresholds
rather than durations. Test and fixture surfaces are reported separately from
production so they cannot inflate the operational migration population.

### Generated authoritative inventory

Emit `config/governance/timer-inventory.toml` with one stable record per control
value. Each record carries at least:

- stable identity; file; line; symbol/key; current value; unit;
- `control_class`: timer, ttl, expiry, grace, timeout, wall_clock, retry_count,
  retry_interval, backoff, throttle, rate_limit, threshold, fan_out, or
  concurrency_limit;
- category and scope: claim, packet, lock, poll, deploy, watchdog, session,
  dispatcher, queue, provider, global, role, project, or harness;
- value form: named constant, inline literal, environment read, JSON/TOML
  configuration, database/registry field, or derived value;
- current authority and `hard_coded` classification;
- invariant coupling to related values, including packet TTL versus claim
  maximum hold where applicable;
- observed failure evidence, measurement provenance, success/censor counts,
  and right-censoring warning;
- relaxed-first candidate value or policy, with rationale and units; and
- centralized-authority candidate (`env.local`, typed registry, or explicitly
  reasoned `undecided`), migration priority, and owning downstream work item
  when known.

The artifact records an explicit divergence note for the prior census. It also
identifies unclassified or ambiguous values instead of silently dropping them.

### Specification-derived tests

Add `platform_tests/scripts/test_timer_inventory.py` covering deterministic
byte output, stable ordering and identities, all control classes and value
forms, production/test separation, schema conformance, right-censor fields,
unclassified-value visibility, exact output-path confinement, and zero runtime
value mutation.

## Explicitly Out Of Scope

This slice inventories and classifies only. It does not change, relax, tighten,
externalize, delete, or re-home any runtime value. It does not select the final
central configuration authority and does not modify `env.local`, the SoT
registry, dispatcher/TAFE state, harness concurrency, or provider settings.

- WI-5805 owns registry visibility for artifacts bearing these controls.
- WI-5806 owns externalization and coordinated migration from hard-coded values.
- WI-5807 owns recurring evidence-driven tuning.
- Evidence-specific correction WIs own concrete mis-set values already found.

## Cross-Harness Disposition

V003 was authored by a Prime Builder session and v004 by a distinct Loyal
Opposition session. This Codex Prime Builder session is also distinct from both.
No artifact is self-reviewed. Loyal Opposition should review this complete v005
against the current WI v3 scope; it should not rely on legacy per-WI approval
metadata or treat distinct session contexts as a role conflict.

## Governance And Start Boundary

- The numbered bridge chain is append-only; no earlier version is rewritten.
- Harness A is currently Prime Builder and is eligible to author REVISED.
- The active PAUTH permits source, configuration, test-addition, test, and
  bridge classes for active project members, but does not substitute for GO.
- Filing does not create an implementation-start packet or permit target writes.
- After GO, Prime Builder must acquire a fresh exact-session claim and run the
  operation-time authorization gate for exactly the three declared paths.
- After implementation, the first report is a new `NEW` implementation report;
  it is not a `REVISED` proposal or a terminal verdict.
- No commit, push, deployment, release, credential, external-system, destructive,
  or dispatcher/TAFE operation is proposed.
- `.claude/rules/backlog-approval-state.md` makes `approval_state` compatibility
  metadata; current project membership and PAUTH govern implementation approval.

## In-Root And Worktree Evidence

All targets resolve within `E:\GT-KB` and outside adopter/application scope:
`scripts/timer_inventory.py`, `config/governance/timer-inventory.toml`, and
`platform_tests/scripts/test_timer_inventory.py`. Their parent directories
exist; each target is currently absent and has no dirty or untracked bytes.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`

## Prior Deliberations

- `DELIB-202667722` — timer/throttle governance, relaxed-first bias, registry
  visibility, no hard-coded values, and recurring tuning.
- `DELIB-202667725` — list-free whole-project authorization.
- `DELIB-202667734` — PAUTH v2 mutation-class schema repair.
- `DELIB-202667748` / `OWNER-TRANSCRIPT-20260801-TIMER-CONCURRENCY-SOT` —
  widened centralized-control scope, evidence-triggered WI capture, ongoing
  data-driven tuning, and right-censoring hazard.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE` — corroborating
  current-session capture of the same standing directive, not a second approval
  requirement.
- `DELIB-202667719` — list-free project authority inheritance.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — legacy per-WI
  approval metadata is noncontrolling.

## Owner Decisions / Input

The active project PAUTH and the current WI v3 requirement are sufficient for
this inventory implementation proposal. No new owner decision is requested.
The final choice between `env.local` and a dedicated typed registry remains a
later program design decision and is not required to produce this inventory.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Project authorization | Re-read project, active membership, and PAUTH v2 at start; require allowed source/configuration/test-addition/test/bridge operations for exactly three targets. |
| Determinism and freshness | Run the extractor twice on an unchanged tree; require byte-identical output, stable ordering, generating commit, extraction-spec version and digest. |
| Full control-class coverage | Fixture-test every listed `control_class` and value form, including thresholds, fan-out, and per-harness concurrency. |
| Hard-coded-value visibility | Assert every discovered record reports current authority and `hard_coded`; ambiguous cases remain visible as unclassified. |
| Centralization classification | Assert hard-coded policy records carry an `env.local` or typed-registry candidate plus rationale and migration owner without performing migration. |
| Evidence and censoring | Assert failure/success/censor fields exist and censored operations are not omitted from measurement evidence. |
| Invariant coupling | Fixture-test coupled records and stable references between both sides of a coupled policy. |
| Production boundary | Assert tests/fixtures are separated from operational totals and no adopter or out-of-root path is read as authority. |
| Write confinement | Run in a fixture tree and assert the extractor writes only the requested inventory output; inspect exact target diff afterward. |
| No runtime mutation | Compare all discovered source/config inputs before and after extraction; require no changed timer, threshold, throttle, fan-out, or concurrency value. |
| Bridge and spec linkage | Run applicability and mandatory clause preflights with zero missing required/advisory specs and zero blocking gaps. |

WI-5804 has no direct formal TEST ID and this proposal invents none. The new
owned verification module is the mapped test artifact. Existing program tests
`TEST-11795`, `TEST-11797`, `TEST-11798`, `TEST-11799`, `TEST-11800`,
`TEST-11801`, `TEST-11802`, `TEST-11803`, `TEST-11804`, and `TEST-11806` are
evidence anchors for already-observed control classes, not substitutes for the
new inventory suite.

Required execution evidence after implementation includes focused pytest for
`platform_tests/scripts/test_timer_inventory.py`, Ruff check and format-check on
the two Python targets, two real-tree extractor runs with matching hashes, the
generated artifact schema/count summary, and an exact three-path Git diff.

## Acceptance Criteria

- The extractor is deterministic, read-only over inputs, and re-runnable.
- The generated artifact covers the entire current WI v3 control class, not
  only duration-shaped timers or named constants.
- Every record has provenance, current-authority, hard-coded, evidence,
  censoring, coupling, relaxed-first, and centralization-classification fields.
- Production, test, and ambiguous populations are explicitly separated.
- No runtime value or file outside the three declared targets changes.
- All mapped tests and preflights pass and are reported with actual counts and
  hashes in a subsequent `NEW` implementation report.

## Risk, Rollback, And Scope Boundary

Primary risk is false completeness. Stable extraction metadata, class fixtures,
unclassified-value visibility, and reproducible counts make omissions
detectable. Secondary risk is treating survivor-only latency as evidence for a
short bound; explicit censor fields prevent that inference. Scope-creep risk is
controlled by the three-path target set and no-migration assertions.

Rollback removes only the three new targets under separate authority. Because
this slice changes no runtime control value, rollback has no timing or
concurrency behavior consequence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

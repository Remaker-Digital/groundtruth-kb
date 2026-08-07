NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 345fab55-33fc-40c1-933b-d2413de27158
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; activity build

bridge_kind: prime_proposal
Document: gtkb-inactive-harness-requirement-deferral
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5422
related_work_items: ["WI-5628", "WI-5897", "WI-5812"]

target_paths: ["config/governance/inactive-harness-deferrals.toml", "platform_tests/scripts/test_inactive_harness_deferrals.py"]
implementation_scope: governance_registry_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none. Work-item stage changes for WI-5628/WI-5897 are routed, not performed here.
dispatcher_or_tafe_mutation_in_scope: false

# Inactive-harness requirement deferral registry

## Summary

Two registered harnesses will not be activated. Several governed requirements
are satisfiable **only** by those harnesses, so those requirements are now
permanently unmeetable and are silently blocking otherwise-complete work.

This thread creates a small, machine-readable registry recording which
requirements are deferred because their only satisfying harness is inactive,
plus a test that keeps the registry honest. It is the durable form of the owner
directive quoted below, so future sessions resolve the deferral from an artifact
instead of re-deriving it from chat.

The highest-value consequence: `WI-5422` is blocked solely by a clause that
requires an Alibaba-H dispatch. Recording that deferral unblocks `WI-5422`,
which in turn releases `scripts/gtkb_bridge_writer.py` and therefore two
already-GO'd threads currently frozen behind it.

## The blocking chain (measured this session)

1. `bridge/gtkb-wi5422-provider-verdict-model-provenance-normalization-004.md`
   is `NO-GO` on exactly one blocking finding: TEST-11533's `expected_outcome`
   ends "**a fresh substantive Alibaba H dispatch publishes one governed
   verdict**", and `TEST-11533.last_result` is `None`. That verdict states
   plainly: "No code change is requested ... independently verified correct and
   low-risk."
2. Because that thread carries a non-terminal implementation report declaring
   `scripts/gtkb_bridge_writer.py`, the peer-conflict gate in
   `scripts/implementation_authorization.py` denies any other thread that
   declares the same path while it is dirty. Observed verbatim this session:
   "Peer implementation report conflict: bridge
   'gtkb-wi5422-provider-verdict-model-provenance-normalization' has a
   non-terminal implementation report that claims dirty path
   'scripts/gtkb_bridge_writer.py' ... (PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001)".
3. Two GO'd threads declare that path and are therefore blocked:
   `gtkb-w0-worker-enablement-plumbing` (GO at -004) and
   `gtkb-w0-executable-go-pre-verdict-validation` (GO at -002).

The clause cannot be satisfied by effort. Harness H will not be activated, so
no amount of retry produces the required dispatch. Without a recorded deferral
the chain stays blocked permanently.

## Proposed Change

1. **Create `config/governance/inactive-harness-deferrals.toml`** — a registry
   whose rows each record: the inactive harness, the deferred requirement
   (spec/test id and the specific clause), the owner directive that authorizes
   the deferral, the affected work items, and an explicit
   `reactivation_condition` stating that the deferral lapses if the harness is
   ever activated. Initial rows:

   - `alibaba-cloud-studio` (H) — `GOV-HARNESS-ONBOARDING-CONTRACT-001` /
     `TEST-11533` black-box dispatch clause; affects `WI-5422`.
   - `ollama` (D) — harness-D route reconciliation; affects `WI-5628`.
   - `ollama` (D) — local-tag-membership readiness probe; affects `WI-5897`
     (flagged `confirm_scope = true`; see Open Question).

2. **Create `platform_tests/scripts/test_inactive_harness_deferrals.py`**
   asserting: the registry parses; every row names a harness that is actually
   non-active in `harness-state/harness-registry.json`; every row carries a
   non-empty owner-directive citation and a `reactivation_condition`; and no row
   defers a requirement whose harness is active (the anti-abuse assertion —
   this registry must never become a way to waive requirements for live
   harnesses).

3. **No stage transition and no KB write is performed here.** Deferring
   `WI-5628`/`WI-5897` and filing WI-5422's REVISED report are routed as
   follow-on work so the reviewing role sees the registry before anything
   depends on it.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the contract whose black-box clause is
  deferred for H; the deferral is scoped to the clause, not the contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
  — an owner decision that changes what is required must become a durable
  artifact with an explicit lifecycle state, not remain chat context.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the registry is validated against a
  fresh read of the harness registry rather than restating harness status.
- `GOV-STANDING-BACKLOG-001` — affected work items are enumerated so the
  deferral is visible from the backlog side.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the registry ships with the
  test that enforces it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` /
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — links and project
  linkage are explicit above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets are in-root.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the numbered-file chain is canonical and
  append-only. This thread cites bridge files as evidence and edits none; the
  routed WI-5422 REVISED report will append a new version rather than mutate the
  existing `-004` verdict.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` and
  `ADR-OLLAMA-HARNESS-ADOPTION-001` — the adoption decisions this deferral
  supersedes in effect; the registry records the supersession rather than
  editing them.

## Prior Deliberations

- `bridge/gtkb-wi5422-provider-verdict-model-provenance-normalization-004.md` —
  the NO-GO that isolates the Alibaba-H clause as the single blocker and
  explicitly offers "an explicit, documented owner waiver" as remedy option 2.
  This thread supplies exactly that, in durable form.
- `DELIB-202666274` — general blocker-repair authorization; the -004 verdict
  correctly notes it does **not** waive this clause, which is why a specific
  recorded deferral is required.
- `DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO` — the dispatcher is
  deliberately stopped; nothing here activates or configures it.
- `DELIB-202667095` / `DELIB-202667098` / `DELIB-202668114` — goose and
  harness-parity lineage; goose remains active and is untouched by this
  deferral.

## Owner Decisions / Input

- **Owner directive, 2026-08-06 (this session, verbatim):** "the Alibaba and
  Ollama harnesses will not be activated and all requirements that are unique to
  those two harnesses should be deferred." This is the authorizing decision for
  every row in the registry.
- **Owner directive, 2026-08-06 (this session, verbatim):** "The legacy
  TAFE/dispatcher should remain disabled because it doesn't function and there
  are no harnesses for it to dispatch to (only Claude Code and Goose are
  currently available)." Establishes the live-harness set and forbids
  dispatcher activation; this thread performs none.
- **Owner instruction, 2026-08-06:** "Proceed." — authorizes filing this thread.
- **Standing authority:** `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`
  (active; `forbidden_operations` includes `dispatcher_mutation` and
  `external_system_mutation`, neither of which this thread performs).

## Requirement Sufficiency

Existing requirements sufficient. The owner directive supplies the deferral
decision; `GOV-HARNESS-ONBOARDING-CONTRACT-001` and TEST-11533 already define
what is being deferred. No requirement text is rewritten — the registry records
that a named clause is unmeetable while its harness is inactive, and lapses if
that changes.

## Specification-Derived Verification Plan

| Linked spec / requirement | Test / command | Required observed behavior |
|---|---|---|
| Registry parses and is well-formed | `python -m pytest platform_tests/scripts/test_inactive_harness_deferrals.py -q` | All rows parse; each has harness, requirement, clause, owner directive, affected work items, `reactivation_condition` |
| Anti-abuse: no active harness may be deferred | same module, dedicated case | A synthetic row naming an active harness (e.g. claude/goose) FAILS the test |
| Rows match live harness state | same module, validated against `harness-state/harness-registry.json` | Every deferred harness is non-active per a fresh registry read |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` scope containment | inspection asserted in test | Only the named TEST-11533 clause is deferred; the rest of the contract still applies to active harnesses |
| Dispatcher non-impairment | `git status --short -- scripts/dispatcher_runtime.py config/dispatcher/rules.toml harness-state/` | Unchanged; no dispatcher/TAFE mutation |
| Code quality (both gates, separately) | `ruff check` and `ruff format --check` on the new test module | Both pass |

## Acceptance Criteria

1. `config/governance/inactive-harness-deferrals.toml` exists with the three
   initial rows, each citing the verbatim owner directive and a
   `reactivation_condition`.
2. `platform_tests/scripts/test_inactive_harness_deferrals.py` passes, including
   the anti-abuse case proving an active-harness row is rejected.
3. No requirement is deferred for `claude` (B) or `goose` (G).
4. No KB row, dispatcher state, TAFE state, or harness registry entry is
   mutated by this thread.
5. `ruff check` and `ruff format --check` both pass on the new test module.
6. WI-5422's REVISED report and the WI-5628/WI-5897 stage changes are **not**
   performed here; they are named as follow-on work.
7. No commit is created by Prime Builder; finalization remains the Loyal
   Opposition atomic step.

## Open Question For The Reviewing Role

`WI-5897` ("Readiness probe reports not-ready for on-demand cloud models by
asserting local tag membership") is *probably* Ollama-unique — "local tag
membership" is an Ollama concept and the probe sits on the ollama routing
surface — but this was inferred from the title and surrounding routing config,
not proven from the probe's source. Its row is therefore marked
`confirm_scope = true`. If the reviewer finds the probe also governs a live
harness, that row must be dropped rather than deferred; the other two rows stand
independently.

## Backlog Visibility and Deferred Decisions

This is not a bulk operation: two new files, no MemBase write. Inventory of
work deliberately not performed here:

| # | Item | Disposition |
|---|---|---|
| 1 | File WI-5422's REVISED implementation report citing this registry | **DECISION DEFERRED** — follow-on; unblocks `gtkb_bridge_writer.py` and the two frozen W0 GOs |
| 2 | Move WI-5628 / WI-5897 to a deferred stage in MemBase | **DECISION DEFERRED** — follow-on; needs the registry to land first |
| 3 | Correct WI-5617 `status_detail` (falsified blockers) | **DECISION DEFERRED** — separate thread; not harness-related |
| 4 | Teach the authorization classifier to classify dependency manifests | **DECISION DEFERRED** — standing backlog item; platform defect found this session |

## Risk / Rollback

- **Primary risk: a deferral registry becomes a requirement-waiver loophole.**
  Mitigated structurally — the test fails any row naming an active harness, and
  every row carries a `reactivation_condition` that lapses the deferral on
  activation. The registry can only ever weaken requirements for harnesses that
  do not run.
- **Risk: WI-5897 mis-scoped.** Mitigated by `confirm_scope = true` and the Open
  Question above; the reviewer decides rather than inheriting my inference.
- **Risk: deferral read as cancellation.** The registry defers named clauses; it
  does not retire `GOV-HARNESS-ONBOARDING-CONTRACT-001`, the ADRs, or the work
  items themselves.
- Rollback is deletion of two new files. No data migration, no KB rows, no
  dispatcher state, no bridge-chain bytes.

## Cross-Harness Disposition

- **claude (B) / goose (G)**: active; explicitly excluded from every row and
  protected by the anti-abuse test.
- **alibaba-cloud-studio (H) / ollama (D)**: subjects of the deferral; not
  activated, not configured, not removed from the registry by this thread.
- **codex (A) / antigravity (C) / cursor (E) / openrouter (F)**: unaffected; no
  rows reference them and no harness-local surface changes.
- No typed waiver requested; no hook, skill, or projection regenerated.

## Recommended Commit Type

`feat` — adds a new governance registry surface and its enforcing test. Though
its effect is to defer requirements, the change itself introduces a new
machine-checkable artifact rather than repairing existing behavior.

## DISARM — Implementation

This file requests review only. It grants no protected-edit, claim, start, or
finalization authority. Implementation requires a Loyal Opposition GO from a
session context distinct from `345fab55-33fc-40c1-933b-d2413de27158`, a fresh
work-intent claim, and an implementation-start packet created from that GO.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.

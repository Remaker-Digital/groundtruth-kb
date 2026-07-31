NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5839-capability-ttl-sizing
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5839

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/timer_config.py", "config/governance/protected-commit-timers.toml", "platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py"]
implementation_scope: capability_ttl_configuration_sourcing_and_mint_time_admission_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5839 Implementation Proposal — Size the Bridge-Publication Capability TTL Against Measured Transaction Cost and Refuse Under-Sized Mints

## Summary

The bridge-publication capability that authorizes writing one bridge file is minted with a hard-coded 120-second default TTL and validated against a hard-coded 300-second ceiling. Both values are literals inside `mint_bridge_publication_capability`. The 2026-07-31 keystone diagnosis measured the protected-commit pre-commit gate at roughly 720 seconds wall clock on a 12-path finalization set, so the ceiling is structurally below the cost of the transaction the capability must survive: no legal TTL value can cover the gate.

This proposal does three things, exactly matching the work item's three scope clauses. It sources **both** the default and the ceiling from configuration instead of literals per DELIB-202667722. It derives the ceiling from measured transaction cost with explicit headroom rather than from a chosen round number. And it adds a **mint-time admission guard** that refuses to mint a capability whose lifetime cannot plausibly cover the pending transaction, with actionable text, instead of minting a capability that is already doomed.

The work composes with WI-5742 (GO'd at `-002`) rather than duplicating it. WI-5742 bounds the gate's **duration** and owns the coupled accessor that rejects an incoherent configuration at read time. WI-5839 owns the capability's **lifetime constants** and rejects an incoherent pending transaction at mint time. The ownership split and the coupling mechanism are stated explicitly in the Coordination Note, which is the section a reviewer should read first.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5839-capability-ttl-sizing-001.md`, continuing the append-only versioned bridge file chain. No prior version is deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads and measurements, 2026-07-31)

Every claim below was derived this session against the live worktree and the live control-plane store at `groundtruth.db`. Line numbers are current-worktree references at HEAD `8a35eabc8`.

### 1. The two literals

`mint_bridge_publication_capability` (`registry_control_plane.py` line 2641) declares `ttl_seconds: int = 120` (line 2655) and validates:

```text
if ttl_seconds <= 0 or ttl_seconds > 300:
    raise RegistryAuthorizationError("bridge publication capability TTL must be 1-300 seconds")
```

(lines 2663-2664). Expiry is stamped once at mint time as `created + timedelta(seconds=ttl_seconds)` (line 2711). Neither value is sourced from configuration; neither is tunable without a code change.

### 2. The default is what is actually in play

The sole production caller is `scripts/gtkb_bridge_writer.py` line 1206, which calls `mint_bridge_publication_capability(...)` **without passing `ttl_seconds`**. Every production mint therefore takes the 120-second default. This is confirmed empirically below: across 674 recorded consumptions the set of distinct granted TTL windows is exactly `{120.0}`.

### 3. Measured lifetime distribution of capabilities that survived

Measured this session against `sot_registry_bridge_publication_capabilities`, computing `consumed_at - created_at` for every row in state `consumed`:

```text
n = 674          distinct granted TTL windows = {120s}
min = 22s   median = 32s   p90 = 64s   p95 = 79s   p99 = 112s   max = 274s
```

The p99 of the surviving population is **112 seconds against a 120-second grant**. A distribution pressed that hard against its own grant boundary is the signature of **right-censoring**, not of comfortable headroom.

### 4. The censored tail — what the distribution above cannot show

State census of the same table, this session:

```text
consumed          672 rows
compensated        20 rows   (12 distinct threads)
recovery_required  20 rows   (17 distinct threads)
expired             3 rows   ( 3 distinct threads)
minted              1 row
```

Additionally, **29 capabilities carrying `status = 'VERIFIED'` never reached `consumed`** — each one a stranded terminal verdict. The most recent, by `created_at`, include `gtkb-wi5826-finalizer-evidence-hash-restamp` v4, `gtkb-wi5824-protected-commit-checker-null-safety-ordering` v8/v6/v4, and `gtkb-wi5827-post-nogo-refiling-protocol-reconciliation` v4. Every poisoned row shows a `created_at`/`expires_at` gap of exactly 120 seconds, and the recorded `failure_reason` values are `bridge publication aggregate preimage cannot be restored exactly` and `another bridge aggregate revision followed the publication`.

**This is the analytically load-bearing point of the proposal.** A transaction that needs 720 seconds *cannot appear* in the consumed distribution of §3, because it expires long before it can be consumed; it appears instead in the 43-row failed tail of §4. Sizing the ceiling from the surviving distribution alone would therefore be textbook survivorship bias — it would conclude that 120 seconds is nearly always sufficient, which is precisely the inference that produced the current constants. The uncensored evidence is the keystone diagnosis' measured ~720-second gate together with this censored tail.

### 5. The wi5827 incident named in the work item

`gtkb-wi5827-post-nogo-refiling-protocol-reconciliation` v4, status `VERIFIED`, was minted at `2026-07-31T07:34:56Z` with `expires_at = 2026-07-31T07:36:56Z` — a 120-second window — and is now in `recovery_required` with `failure_reason = bridge publication aggregate preimage cannot be restored exactly`. A second row for the same thread and version sits in `compensated` from `2026-07-31T07:12:55Z`. The terminal VERIFIED was stranded and the row poisoned, exactly as the work item records.

### 6. Five recorded consumptions exceed the granted window

Five rows record `consumed_at` more than 120 seconds after `created_at`: 129s, 151s, 156s, 185s, and 274s. Two mechanisms can produce this and **the table alone cannot distinguish them**:

- post-check overrun on the normal path, since `consume_bridge_publication_capability` checks expiry at line 2828 but stamps `consumed_at` at line 2899, after the exclusive-lock snapshot load, aggregate resolution, and revision append; or
- governed recovery re-consumption through `recover_bridge_publication` (line 2931), whose UPDATE at lines 3158-3162 sets `capability_state = 'consumed'` and explicitly sets `failure_reason = NULL`, erasing the marker that would have separated the two populations.

This proposal does not claim one mechanism over the other. Both readings support the same conclusion and the same remedy: **the granted lifetime is a bound on when the transaction may start, not a bound on when it completes**, so a mint-time admission decision must be made against the expected cost of the whole pending transaction rather than against a fixed constant.

### 7. The ceiling is a latent clamp on WI-5742's own configuration surface

WI-5742 externalizes the gate bound and its paired capability TTL into `config/governance/protected-commit-timers.toml` via `timer_config.py`. But the literal at line 2663 rejects any `ttl_seconds` above 300 **regardless of what that configuration says**. If WI-5742's relaxed-first paired TTL is set above 300 seconds, every mint raises `RegistryAuthorizationError`. Externalizing the ceiling is therefore a prerequisite for WI-5742's own surface to be tunable at all — which is why this work item exists as a separate, sequenced thread rather than as a footnote to the keystone.

## Proposed Design

Three changes, in the order they are implemented.

### Change 1 — Source both constants from configuration

`ttl_seconds` loses its literal default and its literal ceiling. Both resolve through the single resolution path WI-5742 establishes at `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`, reading `config/governance/protected-commit-timers.toml`, with the same precedence WI-5742 defines: env-local override per GOV-ENV-LOCAL-AUTHORITY-001, then config file, then a documented relaxed fallback constant used only when the config surface is absent.

Two new capability-side keys join the existing gate-side keys in the same config surface:

- the capability TTL default that mint applies when no caller override is supplied; and
- the capability TTL ceiling that mint validates against.

No new resolution path, no second config file, and no duplicated precedence logic is introduced. `timer_config.py` gains capability-side accessors alongside WI-5742's gate-side accessor; the module's resolution machinery is reused, not reimplemented.

### Change 2 — Derive the ceiling from measured cost with explicit headroom

The ceiling stops being a chosen round number and becomes a derived quantity, documented inline in the config file:

```text
ceiling  >=  paired_gate_bound  +  measured_publish_and_commit_overhead  +  headroom
```

where `paired_gate_bound` is read from WI-5742's gate-side key rather than restated here, and the headroom factor is itself a configured value rather than a literal. Per DELIB-202667722 the starting posture is relaxed-first: the initial ceiling is set comfortably above the derived minimum, not at it, with the derivation and its measurement provenance recorded as a comment in the config file so a future tuning session does not have to re-derive it.

The default TTL is derived the same way and is, by construction, less than or equal to the ceiling.

Note the direction of the derivation. It is deliberately **not** taken from the p99 of §3, for the survivorship reason given there; it is taken from the bound on the transaction the capability must survive.

### Change 3 — Mint-time admission guard

`mint_bridge_publication_capability` gains an optional keyword parameter carrying the expected cost of the pending transaction, defaulting to the paired gate bound read from WI-5742's accessor. At mint, after resolving the effective TTL and the configured ceiling, the function refuses when the effective TTL cannot plausibly cover that expected cost:

- if the effective TTL exceeds the configured ceiling, refuse (the existing check, now config-sourced);
- **if the effective TTL is below the expected transaction cost scaled by the configured headroom factor, refuse** with actionable text naming the requested TTL, the expected transaction cost, the configured ceiling, the resolved configuration source, and the remediation.

The guard is fail-closed in both directions: if configuration resolution degrades to the documented fallback, the guard still runs against the fallback values and says so in its message; it never silently skips because a value was unresolvable.

**Blast radius, stated precisely.** Because WI-5742's accessor already refuses to return a gate bound greater than its paired TTL, a coherent configuration cannot trip this guard. The guard therefore fires in exactly two situations: a caller passes an explicit under-sized `ttl_seconds` argument, or configuration resolution degraded. That is the intended narrow surface — and the first situation is precisely the case WI-5742's config-read-time accessor structurally cannot see, because `ttl_seconds` is a public parameter that bypasses configuration entirely.

### Why WI-5742's Layer C does not make this work redundant

WI-5742's Layer C-ii moves the mint to after the gates pass, so the capability spans only publish-and-commit rather than the full gate. That shortens the span the capability must cover; it does not remove the requirement that the capability cover whatever span remains, and it does not address either literal. Three reasons this work item survives Layer C intact:

1. The 300-second ceiling literal clamps WI-5742's own externalized TTL (§7). It must be externalized for the keystone's config surface to function.
2. The `ttl_seconds` parameter is public API. A caller passing an explicit value bypasses every configuration-time check; only mint time observes the actual requested lifetime.
3. The guard is parameterized on the pending transaction's declared cost, not hard-wired to the gate bound, so it holds correctly under either transaction ordering — pre-Layer-C (capability spans the gate) or post-Layer-C (capability spans publish-and-commit).

### Rejected alternatives

- **Raise the ceiling literal to cover 720 seconds.** Treats the symptom, leaves both values untunable, and bakes in a number that Layer B is about to invalidate by two orders of magnitude. Rejected.
- **Duplicate WI-5742's coupling comparison inside mint.** Would create a second authority for the same invariant and guarantee divergence the first time either side is tuned. Rejected in favour of consuming the keystone's accessor.
- **Put the capability constants in a separate config surface.** Splits an invariant-coupled pair across two files, which is the exact failure mode WI-5806 and DELIB-202667722 exist to prevent. Rejected.
- **Size the ceiling from the observed p99 of consumed capabilities.** Survivorship bias; the surviving distribution is censored at the grant boundary and cannot represent the transactions that failed. Rejected explicitly, and this rejection is itself tested.
- **Add a renewal or heartbeat instead of an admission check.** WI-5742 considered and rejected renewal as its Layer C-i; re-proposing it here would contradict a GO'd sibling. Rejected.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — the WI-5839 source specification; append-only numbered bridge chain and bridge audit-trail authority. The stranded terminal verdicts in the evidence section are chain-versus-commit divergences this work prevents; no chain file is rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation; the derived tests below map back to these citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the mapping below is the derivation record the verifier executes against.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain; the PAUTH triple in the header proceeds under it.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — required (blocking) — authorization bounds enforced at every operation; a capability expiring mid-operation is exactly that property failing, and the mint-time guard is an operation-time enforcement point.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — required (blocking) — governed Git lifecycle; this work restores the ability of a governed finalization to produce a backing commit.
- `GOV-WORK-TREE-HYGIENE-001` — required (blocking) — worktree hygiene; the 29 stranded VERIFIED terminals are the hygiene failure being cleared.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is mutated by this implementation; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root; no application subtree and no out-of-root dependency is touched.
- `GOV-ENV-LOCAL-AUTHORITY-001` — required (blocking) — scopes the env-local layer of the timer resolution precedence this work consumes.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the two-layer defense-in-depth posture is the direct justification for enforcing the coupling at both configuration-read time (WI-5742) and mint time (this work).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence derives from fresh canonical reads and measurements taken this session.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — a derived, configured ceiling with an actionable refusal message replaces per-incident manual diagnosis of stranded terminals.
- `SPEC-1662` — advisory — assertion quality: the tests assert behavioral outcomes (refusal, message content, absence of stranding), not structural presence of constants.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the config surface and its recorded derivation are durable artifacts rather than transient session knowledge.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability across work item, config, tests, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions for WI-5839 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5839 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667722`, `DELIB-202667721`, `DELIB-202667734`, `DELIB-202667723`, `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667722** — Timer and throttle governance as a first-class concern with relaxed-first defaults: the direct authority for sourcing both the default and the ceiling from configuration rather than literals, and for the relaxed-first starting posture of the derived ceiling.
- **DELIB-202667721** — Owner authorization of the list-free whole-project PAUTH for PROJECT-GTKB-HOUSEKEEPING-HARDENING, recorded as the authorization cited in this proposal's header.
- **DELIB-202667734** — Owner decision repairing inert whole-project PAUTH envelopes by removing the unregistered mutation-class token; this is why the cited authorization is currently operative rather than deny-everything.
- **DELIB-202667723** — Terminal-evidence sufficiency for expired implementation-start packets: the adjacent expiry-versus-evidence question, and the reason an expiry-driven refusal must carry actionable text rather than a bare error.
- **DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS** — Exact recovery of stranded WI-5670 and WI-5588 terminal transactions: the recovery discipline this proposal is designed to stop needing.
- All deliberation, specification, work-item, and test IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase; bridge chain states were verified by direct first-line status-token reads of the numbered files, and control-plane figures by direct read-only query of `sot_registry_bridge_publication_capabilities`.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5839. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667721 / DELIB-202667734** — the owner's list-free whole-project grant recorded as PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 covers WI-5839 as a member work item. Verified fresh this session: the envelope is `active` at version 2, carries a null `expires_at`, has a null `included_work_item_ids` (list-free), and its `allowed_mutation_classes` are `source`, `test`, `test_addition`, `configuration`, `documentation`, `metadata`, `governance_evidence`, `bridge` — correctly excluding the unregistered `git_commit` token repaired under DELIB-202667734. Per the PAUTH scope summary, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO carrying complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. **DELIB-202667722** — the owner's timer-governance decision constrains Changes 1 and 2 to configuration-sourced, relaxed-first values. No additional owner decision is required to review this proposal, and this proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5839 title, description, and `source_test_id` (fresh-read verified via `gt backlog show WI-5839 --json`), the TEST-11790 `expected_outcome` (fresh-read verified via `gt tests show TEST-11790 --json`), together with GOV-FILE-BRIDGE-AUTHORITY-001, DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001, GOV-ENV-LOCAL-AUTHORITY-001, and the DELIB-202667722 timer-governance decision, fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

The spec-derived test anchor is MemBase record **TEST-11790**, created with WI-5839 per GOV-12, whose `expected_outcome` reads: *"A finalize-verified transaction whose gate duration approaches the configured bound either completes with its capability still valid, or the capability mint refuses up front with actionable text; no path produces an expired-mid-transaction capability that strands a terminal VERIFIED file."* That outcome has two acceptance arms and one prohibition; the mapping below covers all three.

All new tests land in `platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py`.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11790 arm 1 / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_transaction_near_bound_keeps_capability_valid` | A finalize-verified transaction whose duration approaches the configured bound completes with its capability still valid; the verdict and its verified paths land in one commit |
| TEST-11790 arm 2 / DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 | `test_mint_refuses_ttl_below_expected_transaction_cost` | When the effective TTL cannot cover the expected transaction cost with headroom, mint refuses up front and raises before any capability row is written |
| TEST-11790 arm 2 (actionability) / DELIB-202667723 | `test_refusal_message_is_actionable` | The refusal names the requested TTL, the expected transaction cost, the configured ceiling, the resolved configuration source, and the remediation — actionable text, not a bare error or stack trace |
| TEST-11790 prohibition / REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001 | `test_no_expired_mid_transaction_capability_strands_verified` | **Required regression.** No path produces an expired-mid-transaction capability that strands a terminal VERIFIED file: on every refusal and failure branch there is no orphan terminal file, no minted row left behind, and no `recovery_required` row created |
| WI-5839 clause 2 / DELIB-202667722 | `test_ttl_default_is_configuration_sourced` | The mint default resolves through the timer-config path with the documented precedence; no production literal remains for the default |
| WI-5839 clause 1 / DELIB-202667722 | `test_ceiling_is_configuration_sourced` | The ceiling resolves through the same path; a configured value above the former 300-second literal is accepted, proving the clamp of §7 is gone |
| WI-5839 clause 1 (derivation) | `test_ceiling_covers_paired_bound_with_headroom` | The resolved ceiling is at least the paired gate bound plus publish-and-commit overhead scaled by the configured headroom factor |
| WI-5839 clause 3 (public-API bypass) / GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 | `test_explicit_undersized_ttl_argument_is_refused` | An explicit under-sized `ttl_seconds` argument — the case configuration-time checks structurally cannot see — is refused at mint |
| WI-5742 coupling (non-duplication) | `test_guard_consumes_paired_accessor_without_duplicating_it` | The guard obtains the paired gate bound from the WI-5742 accessor; no second comparison of bound against TTL exists in the control plane |
| WI-5839 (fail-closed) / GOV-ENV-LOCAL-AUTHORITY-001 | `test_degraded_config_resolution_stays_fail_closed` | With the config surface absent, resolution falls back to the documented relaxed constant, the guard still evaluates, and the message names the fallback source; the guard is never silently skipped |
| SPEC-1662 / DELIB-202667722 | `test_no_new_timer_literals_introduced` | The diff introduces no new hard-coded timer, interval, retry, or throttle literal outside the documented relaxed fallback constant |
| WI-5839 (anti-survivorship) | `test_ceiling_is_not_derived_from_consumed_distribution` | The derivation is anchored to the transaction bound, not to the censored percentile of surviving consumptions; a fixture whose surviving p99 is far below the bound still yields a bound-sized ceiling |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py -q --tb=short` passes green, and the existing control-plane and finalization suites remain green.
3. Neither `120` nor `300` survives as a capability-TTL literal in `mint_bridge_publication_capability`; both resolve through the timer-config path.
4. A configured ceiling above 300 seconds is accepted by mint, demonstrating that the clamp on WI-5742's configuration surface is removed.
5. The mint-time guard refuses an under-sized capability with actionable text naming requested TTL, expected transaction cost, configured ceiling, resolved configuration source, and remediation.
6. On every refusal and failure branch: no orphan terminal file, no capability row left in `minted`, and no new `recovery_required` row.
7. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals outside the documented relaxed fallback constant.
8. Exactly one comparison of gate bound against capability TTL exists across WI-5742 and WI-5839 surfaces; the guard consumes it rather than restating it.

## Risk And Rollback

- **Guard too aggressive, locking out all minting.** The highest-consequence risk: if the guard activated while the paired gate bound were still ~720 seconds and the ceiling still 300, every mint would refuse and bridge publication would stop entirely. Mitigated by the sequencing constraint below — WI-5839 lands only after WI-5742's Layer A bound and Layer B reductions are in place, so the paired bound is already small when the guard activates — and by the structural property that a coherent configuration cannot trip the guard, since WI-5742's accessor already refuses a bound exceeding its paired TTL. `test_transaction_near_bound_keeps_capability_valid` is the positive-path lock against over-refusal.
- **Ceiling set too low after derivation.** Mitigated by relaxed-first defaults per DELIB-202667722, by anchoring the derivation to the transaction bound rather than the censored p99, and by recording the derivation and its measurement provenance inline in the config file.
- **Divergence between the two enforcement points.** Mitigated by consuming WI-5742's accessor rather than duplicating the comparison, and asserted by `test_guard_consumes_paired_accessor_without_duplicating_it`.
- **Rebase risk on a shared, currently-dirty file.** `registry_control_plane.py` carries uncommitted staged work right now; see the Coordination Note for the baseline and the re-baselining obligation.
- **Rollback** is the exact revert of the changed source files, the capability-side config keys, and the new test module. No MemBase mutation, no dispatcher/TAFE state change, and no bridge chain file rewrite is involved.

## Coordination Note (sequencing and ownership, not scope)

### WI-5742 — GO'd keystone; the ownership split this proposal composes with

WI-5742 (`bridge/gtkb-wi5742-bound-protected-commit-evaluation`) is **GO'd at `-002`** with no required revisions, verified this session by first-line status-token reads (`-001` NEW, `-002` GO). It bounds gate **duration**; WI-5839 sizes capability **lifetime**. The two threads share `registry_control_plane.py`, `timer_config.py`, and `config/governance/protected-commit-timers.toml`, so the split must be explicit:

| Constant or mechanism | Owner | Surface |
|---|---|---|
| Gate wall-clock bound | **WI-5742** | `timer_config.py` gate-side accessor plus config key |
| Coupling enforcement at configuration-read time (bound must not exceed paired TTL) | **WI-5742** | the validated accessor |
| Transaction ordering (late mint, Layer C-ii) and compensation robustness (C-iii) | **WI-5742** | publication path |
| Gate cost reductions (Layer B) | **WI-5742** | gate internals |
| Capability TTL default (literal at line 2655) | **WI-5839** | config-sourced |
| Capability TTL ceiling (literal at line 2663) | **WI-5839** | config-sourced, derived with headroom |
| Mint-time admission guard | **WI-5839** | `mint_bridge_publication_capability` |

**How the coupling is enforced without duplicating WI-5742's accessor.** WI-5839 does not re-implement the bound-versus-TTL comparison. It *calls* WI-5742's accessor to obtain the paired gate bound and uses that value as the default expected transaction cost for the guard. The two enforcement points are at different times and see different inputs: WI-5742 enforces at configuration-read time and rejects an incoherent configuration; WI-5839 enforces at mint time and rejects an incoherent pending transaction even under a coherent configuration — including the explicit-argument case that configuration-time checks structurally cannot observe. This is the two-layer defense in depth GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 requires, and it answers WI-5742's own Loyal Opposition Review Question 2 ("configuration time or mint time?") with *both, at different points* rather than choosing one.

**Sequencing is mandatory, not advisory.** WI-5839 implementation MUST be sequenced after WI-5742 lands, for three reasons: WI-5742 creates `timer_config.py` and the config file that WI-5839 extends; WI-5742's Layer B reductions must be in place before the guard activates, per the lockout risk above; and both threads modify `mint_bridge_publication_capability` and its surrounding module, so the diffs must not interleave.

**Rebase baseline.** HEAD is `8a35eabc8`. `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` and `scripts/gtkb_bridge_writer.py` are both currently **staged-modified** in the worktree (`git --no-optional-locks status --short` reports `M ` for each). All line references in this proposal are against that current worktree state. The correct implementation baseline is the post-WI-5742 landed worktree; if the landed WI-5742 diff moves or renames `mint_bridge_publication_capability` or the surrounding validation block, the implementing session re-baselines line references before editing and records the re-baseline in the implementation report.

### WI-5825 — complementary, disjoint

WI-5825 (`bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill`, **GO'd at `-002`**, verified this session) clears **already-poisoned** `recovery_required` and compensated rows and back-fills receipts. WI-5839 prevents the expiry that poisons them. The two are complementary and their target paths are disjoint: this proposal touches no recovery, cleanup, or receipt back-fill surface, and creates no MemBase row. The 20 `recovery_required` and 20 `compensated` rows measured above are WI-5825's inventory, cited here only as evidence of the failure rate. Running WI-5825's cleanup after both WI-5742 and WI-5839 land avoids re-poisoning rows that were just cleared.

### WI-5806 — the generic home for timer constants; how this registers

WI-5806 (P1, open) owns externalizing hard-coded timers to the canonical config surface with relaxed-first defaults, a single resolution path, and invariant-coupled pairs externalized together. WI-5839 registers with it in three ways: the two capability constants are added to the **same** config surface and the **same** resolution path WI-5742 establishes as WI-5806's first slice, not to a new one; they are externalized **together with** their coupled gate-side partner, satisfying WI-5806's invariant-coupled-pair requirement; and the derivation rule is recorded inline so WI-5806 can adopt and generalize it rather than rediscover it. WI-5839 does not block on WI-5806, which has no bridge thread yet.

### WI-5838 — shares the incident, not the surface

WI-5838 (P1, open) reaps orphaned pre-commit hook processes when the parent dies. It shares the 2026-07-31 finalization incident with WI-5839 but touches a disjoint surface: process lifecycle rather than capability lifetime. No coordination beyond awareness is required.

### WI-5791 — publication linearizability

The cross-process generation race is WI-5791 scope. The mint-time guard is a local admission decision and does not pre-empt that work; the `another bridge aggregate revision followed the publication` failure reason seen in two rows above is WI-5791 territory, not this proposal's.

## DISARM — KB Mechanics

This work performs no MemBase mutation. This proposal creates and modifies source, configuration, and test files only. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work; no `groundtruth.db` write, insert, or mutation occurs. The `kb_mutation_in_scope: false` flag accurately reflects a pure source, configuration, and test change. Citations of DELIB, spec, work-item, and test IDs in this proposal are read-only references, not mutations, and the control-plane figures reported in the evidence section were obtained through a strictly read-only connection.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5839-capability-ttl-sizing`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs a defect (a capability lifetime whose hard ceiling is structurally below the cost of the transaction it must survive, stranding terminal publications and poisoning control-plane rows) with regression coverage. The configuration keys and accessors are remediation plumbing required to source the values without literals, not a new capability surface.

## Loyal Opposition Review Questions

1. Is the ownership split in the Coordination Note correct — WI-5742 owning gate duration and the configuration-read-time coupling, WI-5839 owning the capability constants and the mint-time guard — or should the capability constants move into WI-5742 so one thread owns the whole coupled pair?
2. Is consuming WI-5742's accessor for the paired bound the right non-duplication mechanism, or should the guard take the expected transaction cost strictly from its caller so the control plane has no dependency on the gate's configuration?
3. Is the anti-survivorship derivation argument sound — that the ceiling must be anchored to the transaction bound rather than the censored p99 of surviving consumptions — and is `test_ceiling_is_not_derived_from_consumed_distribution` an adequate mechanical guard against that reasoning error recurring?
4. Is the mandatory sequencing after WI-5742 sufficient mitigation for the guard-lockout risk, or should the guard ship in a report-only mode first and be promoted to refusing in a follow-on slice?
5. Given that §6 cannot distinguish post-check overrun from governed recovery re-consumption, should this work item also require that `recover_bridge_publication` stop nulling `failure_reason` so the two populations remain separable — or is that properly WI-5825 scope?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

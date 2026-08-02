REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5839-capability-ttl-sizing
Version: 005
Responds to: bridge/gtkb-wi5839-capability-ttl-sizing-004.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5839
related_work_items: ["WI-5715", "WI-5742", "WI-5806", "WI-5812", "WI-5825"]

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/timer_config.py", "config/governance/protected-commit-timers.toml", "platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py"]
implementation_scope: centralized_capability_ttl_configuration_and_mint_admission_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# WI-5839 Revised Implementation Proposal — Centralize Capability TTL Sizing and Fail Closed on Under-Sized Mints

## Revision Claim

Version 004 correctly rejects version 003's attempted stale-GO closure. No implementation report exists, so this revision does not fabricate one. Current source still carries a 120-second mint default, a 300-second maximum, and in-code 90/120 fallback values; the dedicated WI-5839 test module is absent. This is therefore a refreshed implementation proposal, not an implementation report.

The revision preserves the previously approved capability-lifetime and mint-admission intent while incorporating the owner's newer timer/concurrency SoT directive. It removes the original proposal's allowance for any production in-code fallback, corrects the false claim that WI-5825 is target-disjoint, rebases onto the already-landed WI-5742 Layers A/B, and makes dependency/dirty-byte ordering explicit. Implementation remains disabled until the exact current dependencies and receipt evidence are clear.

## Findings Response

1. **No configuration, guard, or test outcome evidence exists — accepted.** The present bytes prove the approved implementation did not occur. V005 requests review only.
2. **No active claim is not a terminal result — accepted.** Claim absence is concurrency state, not completion evidence.
3. **NO-ACTION is not closure — accepted.** WI-5839 remains open and version 003 is preserved as historical invalid-disposition evidence.

## Current Evidence and Preimages

- `registry_control_plane.py` is tracked but foreign-dirty under WI-5715 at SHA-256 `A063E0CB057FACFC86D077360B02EB9805A1EB516C7CE16CCED0B472D06C3006`, worktree blob `bd0c0aebc68660063c1c77f07dfd8710d0d7c7dc`, versus HEAD/index blob `eacfa072116b3696c9877ba27f7ddb883ab35d83`. It still defaults capability TTL to 120 seconds and rejects values above 300 seconds.
- `timer_config.py` is tracked and clean at SHA-256 `4F3C678C01ADD235940D88135194B52DD96DAC9C20CBBC050E726974E2A3785F`; it still contains production fallback values 90/120 and a 300-second ceiling.
- `protected-commit-timers.toml` is tracked and clean at SHA-256 `3180FC08CDE78A4714733CED1F892093ACC39A715CABBFA45A3709F69658820F`; it records the current 110-second gate bound and 120-second capability TTL while comments retain the former 300-second constraint.
- `platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py` is absent.
- Current right-censored evidence remains material: successful capability consumptions cluster against the old 120-second grant, while failed/recovery rows and the measured long finalization path prove survivor percentiles alone understate required lifetime. Recent governed writers have also taken roughly 60–82 seconds under ordinary contention.
- The project is active; WI-5839 has active membership and inherits active list-free Housekeeping Hardening PAUTH v2. Legacy WI approval metadata is noncontrolling.

## Centralized Design

### Slice A — One typed timer/concurrency SoT, no production fallbacks

Use `config/governance/protected-commit-timers.toml` through the single typed `timer_config.py` resolver as the authoritative surface for this invariant-coupled group:

- capability TTL default;
- capability TTL ceiling;
- capability minimum headroom / sizing policy inputs; and
- the already-centralized paired protected-commit gate bound.

Environment overrides may enter only through the canonical resolver and must be documented with units and provenance. `registry_control_plane.py` must not declare default, ceiling, or headroom values. `timer_config.py` must not silently return hard-coded timer values. Missing, malformed, non-positive, incoherent, or incomplete configuration fails closed with an actionable typed error naming the key, source, units, and remediation.

The initial configured posture must be generous and supported by fresh, right-censor-aware evidence. The implementation report must record the observed gate/publish distributions, the censored failure population, the selected configured values, the derivation and headroom, and why the values are tolerable. Ongoing tuning changes the SoT, not production code.

### Slice B — Configuration coherence

The resolver returns one immutable typed snapshot containing every coupled value and its source. It rejects any snapshot in which:

- default TTL exceeds ceiling;
- TTL cannot cover the declared transaction cost plus configured headroom;
- gate bound and capability lifetime are incoherent for the active transaction ordering; or
- units or provenance are missing.

No second resolver, configuration file, per-caller environment read, or duplicated comparison is introduced.

### Slice C — Mint-time admission

`mint_bridge_publication_capability` obtains the typed snapshot and evaluates the actual requested TTL against the pending transaction cost. It refuses before inserting a capability row when the requested or configured lifetime is under-sized. The error must name requested TTL, required minimum, configured default and ceiling, transaction-cost evidence, resolved configuration source, and remediation.

An explicit caller-supplied TTL remains supported only within the configured envelope; it cannot bypass the paired-invariant check. Every refusal is side-effect free: no capability row, terminal file, receipt, or recovery-required residue is created.

### Slice D — Dedicated verification

Add the declared test module to prove:

- default, ceiling, headroom and paired bound all resolve from the single SoT;
- no production capability default/ceiling/headroom or silent fallback literal remains;
- missing/malformed/incoherent configuration fails closed actionably;
- configured values above the former 300-second clamp are accepted when coherent;
- explicit under-sized caller values are refused before row insertion;
- sizing uses right-censor-aware transaction evidence rather than the survivor-only percentile;
- near-bound valid work remains admitted; and
- no refusal or expiry path strands a terminal bridge file or creates new poisoned capability state.

## Mandatory Ordering and Collision Ledger

1. **WI-5715 first.** It owns the current foreign dirty bytes in `registry_control_plane.py`. Preserve them unchanged until its governed finalization produces a clean exact baseline. V005's dirty hash is evidence only, never an implementation preimage.
2. **WI-5839 prevention second.** Re-read every target and update the implementation-start packet only after WI-5715 is terminal and the source is clean. Obtain a fresh independent GO, exact claim and schema-v3 start packet; no claim transfers byte ownership.
3. **WI-5825 recovery third, after WI-5812.** WI-5825's current GO overlaps `registry_control_plane.py`; it is not disjoint. Its historical/unreceipted recovery must follow WI-5812 and the prevention slice so cleanup is not immediately re-poisoned.

WI-5742 Layers A/B are already committed and independently verified; V005 extends their timer surface. WI-5742 Layer C remains unresolved and is not claimed complete. WI-5806 v2 is the generic centralized timer/concurrency program; this is its capability-lifetime child slice rather than a parallel configuration authority.

The existing zero-byte `.git/index.lock` is foreign and outside this proposal. It must not be removed, replaced, adopted, or interpreted as WI-5839 authority. TAFE/dispatcher activation or mutation is forbidden and out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; append-only numbered bridge authority and WI-5839 / TEST-11790 source requirement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; requires complete governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; implementation verification derives from the mapping below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — blocking; current project PAUTH controls target classes and operations.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — blocking; capability admission is an operation-time enforcement point.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — blocking; the capability must remain valid through governed publication/finalization.
- `GOV-WORK-TREE-HYGIENE-001` — blocking; foreign dirty bytes and the index lock remain fail-closed boundaries.
- `GOV-ENV-LOCAL-AUTHORITY-001` — blocking; any environment override enters only through the canonical typed resolver.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; every artifact and dependency is in-root under `E:/GT-KB`.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory; configuration-time coherence and mint-time admission are distinct mechanical layers.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory; implementation must refresh censored and uncensored measurements before selecting configured values.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory; one resolver and typed failures replace incident-specific guesses.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory traceability and lifecycle evidence.

## Prior Deliberations

- `DELIB-202667748` / `OWNER-TRANSCRIPT-20260801-TIMER-CONCURRENCY-SOT` — controlling owner direction: centralize timers, TTLs, expiries, retries, throttles, thresholds, fan-out and concurrency limits; use generous evidence-derived values and tune through one SoT.
- `DELIB-202667722` — timer/throttle governance and relaxed-first defaults; still applicable where consistent with the broader v2 directive.
- `DELIB-202667721` and `DELIB-202667734` — active Housekeeping Hardening project authority and repaired PAUTH envelope.
- `DELIB-202667723` — expiry-related evidence must fail actionably rather than strand terminal work.
- Version 004's search found no owner disposition closing WI-5839 without implementation; this revision preserves that conclusion.

## Owner Decisions / Input

No new owner decision is required. The owner already approved the project PAUTH and the centralized timer/concurrency direction. This proposal does not select a new project, create a formal artifact, or weaken any current GO/claim/start/verification gate.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5839 / TEST-11790 define the capability-lifetime outcomes, and the owner timer/concurrency deliberations define the configuration posture. No new specification or timer WI is created.

## Specification-Derived Verification Plan

| Requirement | Test | Required observed behavior |
|---|---|---|
| `TEST-11790` admission obligation | `test_mint_refuses_ttl_below_required_transaction_cost` | Refusal occurs before any capability row or bridge side effect and reports every sizing input/source. |
| `TEST-11790` positive obligation | `test_near_bound_transaction_remains_admitted` | Coherent generously configured work near the measured bound remains valid through publication. |
| Central SoT directive | `test_capability_timer_group_resolves_from_one_typed_snapshot` | Default, ceiling, headroom and paired bound come from one resolver with units and provenance. |
| No literal/fallback directive | `test_no_production_capability_timer_literal_or_silent_fallback_remains` | No production default, ceiling, headroom or absent-config fallback value remains outside the SoT. |
| Fail-closed configuration | malformed/missing/incoherent configuration cases | Every invalid state raises a typed actionable error before mint; no silent 120/300 substitution occurs. |
| Former clamp removal | `test_configured_ceiling_above_former_clamp_is_accepted` | A coherent configured ceiling above 300 seconds is accepted without a code change. |
| Explicit caller bypass | `test_explicit_undersized_ttl_cannot_bypass_guard` | Public API override remains inside the configured invariant and is refused when under-sized. |
| Right-censor awareness | `test_sizing_does_not_use_survivor_percentile_as_worst_case` | A fixture with low survivor p99 but censored long failures still selects a lifetime covering transaction evidence. |
| Non-stranding | `test_refusal_and_expiry_paths_leave_no_terminal_or_poisoned_residue` | No orphan terminal file, minted row, or new recovery-required row remains on every failure branch. |

## Acceptance Criteria

1. Only the four declared targets change, after WI-5715 finalizes and exact clean preimages are re-read.
2. Default, ceiling, headroom and paired-bound resolution use one typed canonical SoT; missing or malformed configuration fails closed.
3. No production capability timer/default/ceiling/headroom/fallback literal remains in `registry_control_plane.py` or `timer_config.py`.
4. The implementation report records fresh right-censor-aware measurements and the evidence-derived generous starting configuration.
5. The focused WI-5839 module, existing timer-config/control-plane suites, Ruff lint and Ruff format checks execute with observed results.
6. Under-sized explicit or configured TTLs refuse before any database/file side effect; coherent near-bound work remains admitted.
7. No implementation starts while WI-5715 owns dirty bytes, while a conflicting active claim exists, or before the WI-5825/WI-5812 ordering is restated in the fresh start evidence.
8. No formal artifact, MemBase row, `groundtruth.db`, TAFE/dispatcher state, Git state, foreign index lock, deployment, release, credential, or external system is mutated by this proposal.

## Risk and Rollback

The highest risk is globally refusing bridge publication because the configuration is incoherent. The positive-path test, generous evidence-derived initial posture, atomic typed snapshot and dependency order bound that risk. A second risk is adopting WI-5715's foreign dirty source; exact clean rebaseline after its finalization is mandatory. Rollback is the exact source/config hunks and deletion of the new test module through the governed lifecycle; no data migration is involved.

## DISARM — Implementation

This file requests review only. It grants no protected edit, claim, start, finalization, receipt repair, or cleanup authority. Implementation requires canonical independent GO, exact current claim, fresh schema-v3 start packet, clean post-WI-5715 preimages, and a valid governed receipt path for the unreceipted v004 predecessor.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# Bridge Proposal — GT-KB Isolation Completion Plan: REVISED-2 Architectural Clarification Addendum (2026-04-28)

**Status:** REVISED (version 005 — addendum recording owner architectural clarification on lifecycle independence and single-application cardinality)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-completion-plan-2026-04-28`
**Builds on:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md` (NEW; comprehensive scoping)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md` (NEW; owner decisions addendum)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-003.md` (NO-GO; Loyal Opposition findings)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md` (REVISED-1; addresses -003 findings)

This addendum strengthens the design assumption captured in -004 §1 with an architectural clarification provided by the owner during S319 bridge-scan response. It does NOT supersede -004; it amends it with a sharper statement of intent. Codex review should treat the combined `-001 + -002 + -004 + -005` as the proposed final state.

---

## 1. Architectural Clarification (Owner, S319 2026-04-28)

> *"We want GT-KB and the applications that are built using it to be isolated for lifecycle reasons (the platform should be able to evolve independently of the applications, on its own release cadence). We do not expect to have more than one application under development in a GT-KB host directory at any one time. The GT-KB platform supports only one developed application at a time."*

This statement upgrades the design assumption recorded in -004 §1 from an *expectation* to a *platform contract*, and adds the *why*.

### 1.1 Strengthened wording

The relevant text in -004 §1 currently reads:

> "Design assumption recorded by owner (S319, 2026-04-28): *'The poller and bridge are GT-KB infrastructure. We do not expect to have more than one application under development in a GT-KB host directory at any one time. There will not be conflicts.'*"

**Replace** with:

> **Design contract (owner-asserted, S319, 2026-04-28):** *"The GT-KB platform supports only one developed application at a time."* This is not an operational expectation — it is the platform's cardinality contract. The motivation is **lifecycle independence**: GT-KB and adopter applications must be able to evolve on independent release cadences, with the platform consumed as a stable dependency by the shorter-cycle application work. Coupling them via shared in-tree state (as Agent Red and GT-KB are coupled today) defeats this purpose; isolating them and enforcing single-application cardinality preserves it.

### 1.2 Why lifecycle independence requires this constraint

| Coupling failure mode (without isolation) | What it causes |
|---|---|
| Application work modifying platform code in-tree | Platform release cadence is held hostage by application stability — the platform can't release until the application's work is shippable. |
| Application-specific tests / fixtures / scripts living at platform root | Platform release acceptance must include application-domain regression checks, expanding the platform's release surface to whatever applications happen to be present. |
| Application-specific bridge / KB / governance entries inside platform tables without `application_id` tags | Cross-cutting governance changes (specs, deliberations, hooks) require analyzing which artifacts belong to which subject — slows platform changes and risks application-specific work being affected by platform sweeps. |
| Multiple applications in one GT-KB host with shared coordination state | Platform must mediate between application priorities — the platform becomes a multi-tenant coordination service, which is a fundamentally different design problem than "platform consumed by one application." |

The single-application cardinality, combined with the platform/application physical isolation in -001 §2, lets the platform be released independently because its acceptance surface is bounded.

### 1.3 What stays consistent with -004 / earlier statements

- Option A bridge centralization (-004 §1 / §2.2) is **strengthened** by this clarification, not weakened. With one application at a time, there is no per-app bridge contention by construction; the centralized bridge is the right answer not because we've deferred multi-app concerns but because multi-app **isn't a roadmap target**.
- The smart-poller "enable when functional" stance (-002 §2.2 + owner S319 reaffirmation) is unaffected. The poller is platform infrastructure, runs on the platform's release cadence, and serves whichever single application is currently in development.
- Existing formal records (`DELIB-0834`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`) describing Agent Red as "a well-behaved, fully-conformant application supported and sustained by GroundTruth-KB" are consistent. This addendum sharpens the cardinality side that those records did not explicitly state.

## 2. Implementation Implications

### 2.1 Phase 3 — Application registration cardinality enforcement

**-001 Section 7.3 (Phase 3) addition:** Phase 3 step 3 currently reads "Implement `gt application register <name>` and `gt application unregister <name>`."

**Add the following sub-requirement** (insert after step 3, renumber subsequent):

> 3a. **Cardinality enforcement.** `gt application register <name>` MUST refuse registration if any application is already registered (i.e., if `applications/` contains any registered application with a valid `application.toml`). The error path must:
>
>    - Identify the currently-registered application by name and slot path.
>    - Direct the user to `gt application unregister <existing-name>` if a swap-out is desired.
>    - Exit non-zero so install scripts and CI pipelines fail loudly rather than silently producing a multi-app state.
>
>    Rationale: per platform design contract (-005 §1), the platform supports only one developed application at a time. Cardinality enforcement at the registration command makes the contract mechanically active rather than convention-only.

**Test contract for Phase 3 cardinality:** Add `tests/framework/test_application_register_cardinality.py` covering: (a) first registration succeeds; (b) second registration with different name fails with the swap-out message; (c) re-registration of the same name is idempotent OR explicitly fails with "already registered" — owner decision needed at Phase 3 design time, not now.

### 2.2 Phase 5 — Application install slot precondition

**-001 Section 7.5 (Phase 5) precondition:** Phase 5 application install must include a precondition step:

> 0. **Verify slot is empty (or current application is the same as the one being installed).** Before any Phase 5 file moves, check `applications/registry.toml` (or equivalent). If a different application is already registered, abort with the cardinality error from §2.1 above. The user must `gt application unregister <existing>` before installing a new application.

This is the symmetric application-install gate to the Phase 3 framework-side cardinality check.

### 2.3 Phase 4 — `gt platform doctor` cardinality check

**Augment -004 §2.3 Phase 4 doctor checks** with:

> (h) **Application cardinality check.** `gt platform doctor` reports green only when zero or one applications are registered. Two-or-more registered applications report a P0 violation with a remediation pointer (`gt application unregister <name>`).

This makes the cardinality contract observable at platform-health time, not only at registration time.

## 3. What Does NOT Change in This Addendum

- **-001 Section 2.2 platform layout.** The `applications/<app-name>/` slot directory structure stays as designed. The "applications" plural in the directory name is appropriate: the slot is reusable across the platform's lifetime, supporting at-most-one-at-a-time but allowing for swap-out (uninstall Agent_Red, later install Some_Other_App). The cardinality constraint is on simultaneous registration, not on lifetime occupancy of the slot directory name.
- **-001 Section 2.4 platform-application boundary.** All ownership stamps remain correct; the cardinality constraint is consistent with the boundary as drawn.
- **-001 Sections 3, 4, 5, 6 install behaviors.** No changes beyond the Phase 3 / 4 / 5 augmentations in §2 above.
- **-002 owner decisions.** All 7 confirmed decisions remain in force; the smart-poller stance is unaffected.
- **-004 finding closures.** All four NO-GO finding closures (independent-progress-assessments disposition, Option A bridge centralization, doctor phase relocation, root-file inventory appendix) remain as written in -004.

## 4. Codex Re-Review Request

In addition to the five verification asks in -004 §4, please verify:

6. **Lifecycle-independence rationale captured durably.** Confirm §1 above states the design contract clearly enough that future sessions reading the bridge thread (or a session-wrap deliberation harvest) can re-derive Option A and the cardinality constraint without owner re-explanation.

7. **Cardinality enforcement is mechanical.** Confirm the §2.1 (Phase 3 register), §2.2 (Phase 5 install precondition), and §2.3 (Phase 4 doctor check) augmentations together make the single-application contract enforced by code, not by convention or AI behavior. Flag any path where multi-app state could silently arise.

8. **No conflicts with existing GT-KB governance.** Confirm the cardinality contract does not contradict `DELIB-0834`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, or other prior formal records. (These describe Agent Red as a conformant adopter, which is consistent with single-application cardinality; explicit verification appreciated.)

9. **Session-wrap harvest candidate.** This addendum's §1 contains a substantive owner architectural assertion suitable for harvesting into the Deliberation Archive at session wrap. Confirm the bridge file content is sufficient as a near-term capture (i.e., no immediate KB insertion is required mid-stream).

## 5. Reversibility (No Change)

This addendum does not directly mutate any artifact. It records an owner architectural clarification and proposal augmentations for the contract. Subsequent phase proposals execute the contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

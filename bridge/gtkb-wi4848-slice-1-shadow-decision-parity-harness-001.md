NEW

# gtkb-wi4848-slice-1-shadow-decision-parity-harness — Inert parity harness: prove the daemon's shadow decision matches the trigger's dispatch selection (pre-cutover evidence)

bridge_kind: prime_proposal
Document: gtkb-wi4848-slice-1-shadow-decision-parity-harness
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4848

target_paths: ["scripts/ops/dispatch_parity.py", "platform_tests/scripts/test_dispatch_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4848 (the dispatcher cutover) says the flip to live spawn "must be gated on shadow-decision parity evidence." This slice builds that evidence — and nothing else. It adds a **read-only parity harness** that, for a given bridge state, computes both (a) the daemon's shadow dispatch decision and (b) the trigger's canonical dispatch selection, and reports per-role whether they match field-for-field (role, recipient harness, selected documents, signature). It **spawns nothing, mutates nothing, and re-enables no dispatch** — dispatch stays quiesced; this is pure measurement. The harness converts "the daemon reuses the trigger's logic, so it should dispatch identically" from an assumption into VERIFIED, regression-guarded evidence the owner can weigh before authorizing the go-live (slice 2).

## Motivation — this is not tautological

The daemon's `compute_shadow_decisions` (`scripts/gtkb_dispatcher_daemon.py` L147-207) and the trigger's live loop (`scripts/cross_harness_bridge_trigger.py` `run_trigger` L4223-4264) both compute dispatch via the same functions (`_compute_actionable`, `_resolve_dispatch_targets`, `_target_selected_signature`). But they are **not** byte-identical wrappers: the trigger feeds `_target_selected_signature` a per-target-shrinking `remaining_items` (L4264), while the daemon feeds the full `items` (L194). For the single-target-per-role case (the norm) these coincide; for a **multi-target role** they can diverge. A blind cutover would silently change dispatch behavior in exactly that case. The parity harness exists to surface this class of divergence as evidence, before the flip — not after a storm.

## Design (for LO review)

New `scripts/ops/dispatch_parity.py` (read-only; pure-function core):

- `trigger_canonical_decisions(project_root, *, max_items)` — replicates the trigger's `run_trigger` dispatch-selection sequence (compute actionable -> per-role resolve targets -> per-target `_target_selected_signature` with the trigger's `remaining_items` consumption) **without spawning**, returning per-role `(recipient, harness_id, signature, selected_docs)`.
- `daemon_shadow_decisions(project_root, *, max_items)` — invokes the daemon's `compute_shadow_decisions` (loaded via the daemon's existing importlib pattern) and normalizes its records to the same shape.
- `compute_parity(project_root, *, max_items)` — compares the two per role; returns a `ParityReport` (`per_role: {match, trigger, daemon, divergences}`, `overall_match`, `roles_compared`). Pure given its two decision inputs.
- `main()` — prints the parity report (JSON) for the current bridge state; read-only CLI.

New `platform_tests/scripts/test_dispatch_parity.py` — deterministic over synthetic bridge states (reusing the `_make_project` / `_write_bridge` fixture style of `test_gtkb_dispatcher_daemon.py`):

- single-target GO thread -> `overall_match` True; per-role trigger == daemon.
- multi-role (prime GO + LO NEW) -> per-role comparison present and correct.
- a forced-divergence construction (two decision inputs that differ) -> `compute_parity` reports `match: False` with the diff (proves the harness DETECTS divergence, not just agreement).
- no-actionable state -> both empty, match True.

## Inertness / Risk Containment

- The harness only **reads** bridge state and **computes** decisions; it never calls the trigger's spawn path (`subprocess.Popen`), never writes dispatch state, never re-enables dispatchability. Running it leaves the quiesced posture unchanged.
- If the harness reports a real divergence (e.g., the multi-target `items` vs `remaining_items` difference), that is *evidence for the owner + a scoped follow-on*, not a behavior change made here. Reconciling any divergence in the daemon is explicitly out of scope for this slice.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the cutover must be gated on shadow-decision parity evidence; this builds that gate's evidence source.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the dispatch service whose shadow/live decision-equivalence is measured.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — parity is computed from the fresh live bridge state, not cached decisions.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4848-slice-1-shadow-decision-parity-harness-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4848 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision (WI-4790 -> WI-4788 -> WI-4848); authorizes building the cutover up to the owner-gated flip.
- `DELIB-20266084` — WI-4787 daemon foundation (the shadow decision path this measures).
- WI-4790 slices 1-3 VERIFIED (the daemon brain); WI-4788 slice 2 activation report filed (the guard).

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`) — authorizes the WI-4790 -> WI-4788 -> WI-4848 path under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`, building autonomously up to the go-live. This slice is inert (no spawn, no dispatch re-enable), so it stays within the autonomous build mandate.
- The go-live flip (daemon live + trigger inert + dispatch re-enable) is the separate **owner-gated** WI-4848 slice 2, which I will bring as an AUQ **with this harness's parity evidence in hand**. No owner decision is required for this slice.

## Requirement Sufficiency

Existing requirements sufficient — WI-4848 + `ADR-DISPATCHER-ARCHITECTURE-001` require parity evidence to gate the flip; this builds the evidence source. No new or revised requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (parity evidence) | `test_parity_single_target_matches` | single GO thread -> `overall_match` True; trigger decision == daemon decision per role. |
| ADR-DISPATCHER-ARCHITECTURE-001 (multi-role) | `test_parity_multi_role` | prime GO + LO NEW -> per-role comparison present and correct. |
| ADR-DISPATCHER-ARCHITECTURE-001 (detects divergence) | `test_parity_reports_divergence` | mismatched decision inputs -> `match: False` with diff (the harness catches divergence). |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (read-only/inert) | `test_parity_is_read_only` | running `compute_parity` spawns no subprocess (patched `subprocess.Popen` not called) and writes no dispatch state. |
| No-regression | `ruff check` + `ruff format --check` on both files | green. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_dispatch_parity.py -q --tb=short`; `ruff check`/`ruff format --check` on both files; plus a real-state smoke `python scripts/ops/dispatch_parity.py` to emit the current parity report.

## Risk / Rollback

- Risk: very low. New read-only module + test, both in-root under `E:\GT-KB`. No existing file changed; the daemon and trigger are imported read-only and never driven to spawn; dispatch remains quiesced.
- Rollback: delete the two new files. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: the go-live flip (daemon live-spawn, trigger inert, dispatch re-enable — owner-gated WI-4848 slice 2); reconciling any divergence the harness surfaces (a scoped follow-on); WI-4852 watchdog-dormancy remediation (post-live-daemon).

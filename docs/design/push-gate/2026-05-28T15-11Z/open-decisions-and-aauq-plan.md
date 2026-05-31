# Open Decisions and AUQ Plan

**Status:** CENTRAL Slice 0 deliverable per Codex GO-004 P2-002 reframing.
**Authority:** `bridge/gtkb-push-gate-design-governance-review-004.md`
**Purpose:** Structured AUQ-ready packets for the 5 deferred owner decisions. Each packet contains everything needed for the owner to answer via AskUserQuestion in a follow-on session.

Per the P2-002 reframing, these decisions are Slice 0 OUTPUTS, not Slice 0 prerequisites. They become Slice 0 PREREQUISITES for the follow-on `gtkb-push-gate-design-contract-final` thread that locks the binding design.

Each packet uses the canonical AUQ structure: decision statement, 2-4 option labels (suitable for `header` chips in AskUserQuestion), trade-off analysis per option, spec-coherence check, recommendation + rationale.

---

## Q1. Cleanup Sequencing

**Decision Statement:** Should the push gate become a mechanical blocker AFTER the existing debt inventory is cleaned (clean-then-enable), or should it become a mechanical blocker IMMEDIATELY and freeze development until the debt is cleaned (enable-then-freeze)?

**Options:**

| Header | Label | Description |
|---|---|---|
| `Clean-Enable` | Option A: Clean-then-enable (Recommended) | Inventory debt (Slice 1.5) → clean debt (Slice 3) → enable gate as blocker (Slice 5). Normal cadence preserved during cleanup. |
| `Enable-Freeze` | Option B: Enable-then-freeze-until-clean | Enable gate as blocker immediately (Slice 3). All pushes block until debt cleaned. Honors no-amnesty directive instantly. |

**Trade-Off Analysis:**

Option A preserves development continuity during cleanup. Owner's "no amnesty" requirement is still honored (just deferred to Slice 5). Cleanup volume is measured before the freeze risk is accepted. Codex agreed at NO-GO-002 final note.

Option B honors mechanical-blocker semantics from Slice 3 forward. Forces prioritization of cleanup. But introduces a development freeze that S365 did not explicitly authorize; risk to hotfix paths if Q2 (override path) is not resolved in parallel.

**Spec-Coherence Check:**

Both options preserve `SPEC-DSI-CI-GATE-001` (CI-time enforcement), `SPEC-SEC-HOOK-PORTABILITY-001` (tracked hooks), and `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` (governed test evidence). They differ in timing of gate activation, not in coverage.

**Recommendation:** Option A. Detailed analysis in `cleanup-sequencing-analysis.md`. Mitigated risk profile + Codex agreement + preserved development cadence + measured-then-acted-on volume.

**Rationale:** "It takes as long as it takes" (S365) appears to refer to the gate's runtime, not to a development-blocking freeze. Cleanup volume is unknown until Slice 1.5 lands; committing to a freeze before knowing volume is unbounded risk. If the inventory turns out small (< ~50 findings), owner may revise toward Option B at the final-contract thread.

---

## Q2. Owner-Override Path Scope

**Decision Statement:** Should the push gate provide an owner-override path that allows a specific push to bypass the gate (e.g., emergency hotfix), or should bypasses be fully forbidden (no override surface exists)?

**Options:**

| Header | Label | Description |
|---|---|---|
| `Bridge-Auth` | Option A: `bridge_kind: gate_bypass_authorization` (Recommended) | Bypass requires a bridge proposal with owner approval. Audit-logged via append-only bridge files. Per-push scope. |
| `No-Override` | Option B: Fully forbidden | No override surface exists. Any failing check blocks push permanently until check passes. Maximum mechanical-blocker integrity. |
| `Env-Var` | Option C: Environment-variable escape hatch | Set `GTKB_PUSH_GATE_BYPASS=<owner-token>` to bypass. Lightweight. Not audited via bridge. |

**Trade-Off Analysis:**

Option A integrates with existing bridge governance. Each bypass leaves a versioned audit trail. Owner's approval is explicit per bypass. Slight friction (file a bridge), but consistent with owner-decision-via-bridge precedent.

Option B is the maximum-integrity stance. No edge cases for the gate to handle. But hotfix paths during the Slice 3 cleanup freeze (if Option B chosen for Q1) become unreachable; production-critical fixes might require freeze suspension or other ad-hoc workaround.

Option C is fastest but breaks audit-trail integrity. The owner-token mechanism has its own risks (secret management, rotation, accidental commit). Not recommended.

**Spec-Coherence Check:**

Option A coheres with `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge is canonical workflow state) and the AUQ-only owner-decision enforcement stack — bypasses become a kind of owner-decision routed through the existing bridge/AUQ machinery.

Option B coheres with the strictest reading of `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — no escape hatches in deterministic services.

Option C does not cohere with `GOV-FILE-BRIDGE-AUTHORITY-001` or the AUQ-only stack; it adds an out-of-band owner-decision surface.

**Recommendation:** Option A (`bridge_kind: gate_bypass_authorization`). Preserves bridge-as-canonical-state. Integrates with existing AUQ enforcement. Audit-friendly.

**Rationale:** GT-KB's existing governance is bridge-mediated; introducing a non-bridge override surface fragments the governance model. The friction of "file a bridge to override" is acceptable because emergency hotfixes already involve owner attention; routing through the bridge adds proper audit + a forcing function for explicit owner involvement.

---

## Q3. Multi-Platform CI

**Decision Statement:** Should the GitHub Actions workflow run on Windows only (parity with the local `E:\GT-KB` developer environment), or on Windows + ubuntu-latest (broader coverage)?

**Options:**

| Header | Label | Description |
|---|---|---|
| `Win-Only` | Option A: Windows-only | Run only on `windows-latest`. Mirrors developer environment. Minimal CI cost. |
| `Win-Linux` | Option B: Windows + ubuntu-latest (Recommended) | Run on both. Catches platform-divergence defects (path separators, PATHEXT, line endings). |
| `Linux-Only` | Option C: ubuntu-latest only | Run only on `ubuntu-latest`. Cheaper. But CI environment diverges from developer environment. |

**Trade-Off Analysis:**

Option A is the minimum-risk choice for parity. CI doesn't catch platform-divergence defects, but the dev environment IS Windows, so most defects surface locally before CI.

Option B catches a class of defects that Option A misses. Codex's recent WI-3349 (Gemini PATHEXT) and several historical Windows-specific findings show platform-divergence defects are a real category. Adds ~50% CI cost.

Option C is cheaper than B but breaks dev-env parity. Defects could land green in CI and break locally on Windows.

**Spec-Coherence Check:**

`SPEC-DSI-CI-GATE-001` requires the CI gate; does not specify platform. `SPEC-DSI-DOCTOR-CHECK-001` requires doctor invariant coverage; does not specify platform.

All three options cohere with the specs. The decision is operational, not spec-bound.

**Recommendation:** Option B (Windows + ubuntu-latest).

**Rationale:** Platform-divergence defect class is real (WI-3349 evidence). CI cost is bounded (~50% more); benefit is catching defects pre-merge. Aligns with GT-KB's "no amnesty" directive — defects are found, not deferred.

---

## Q4. PR-vs-Push Gating Scope

**Decision Statement:** Should the GitHub Actions workflow trigger on both `push` and `pull_request` events to develop/main, or on `pull_request` only?

**Options:**

| Header | Label | Description |
|---|---|---|
| `Both-Events` | Option A: Both `push` + `pull_request` (Recommended) | Workflow fires on every push to develop/main AND on PRs. Maximum coverage. |
| `PR-Only` | Option B: `pull_request` only | Workflow fires only on PRs. Direct pushes to develop/main bypass the gate. |
| `Push-Only` | Option C: `push` only | Workflow fires only on pushes. PRs are not gated (only the final push merge is). |

**Trade-Off Analysis:**

Option A is the maximum-coverage choice. Branch protection's "require status check to pass" works on both event types. Direct pushes (rare in normal workflow, but possible for hotfixes) are gated.

Option B leaves direct pushes ungated. Hotfix pushes bypass the gate. Normal PR workflow is fully gated. Cost: half the CI runs.

Option C inverts B: PRs are not gated until the merge push, which means PR reviewers see ungated state. Wastes the value of pre-merge review.

**Spec-Coherence Check:**

`SPEC-DSI-CI-GATE-001` says "GitHub Actions job on every pull request and push" — explicitly both. `SPEC-SEC-GITHUB-POSTURE-001` branch-protection invariants require the workflow to gate before merge.

Option A is the closest match to `SPEC-DSI-CI-GATE-001` literal text. Options B and C require the spec to be reinterpreted as "either/or."

**Recommendation:** Option A (both events).

**Rationale:** SPEC-DSI-CI-GATE-001 literal text already calls for both. Maximum coverage. Bounded cost (CI cycles are cheap relative to defects). Aligns with Option A in Q1 (clean-then-enable) — once enabled, gate is comprehensive.

---

## Q5. Test Impact Analysis Dependency

**Decision Statement:** Should the gate's Layer 3 (test suites) use `pytest-testmon` for coverage-traced test selection, or a pure-stdlib per-file SHA cache for changed-test-set computation?

**Options:**

| Header | Label | Description |
|---|---|---|
| `testmon` | Option A: pytest-testmon | Coverage-traced selection. Mature library. Integrates with pytest's own cache. |
| `SHA-Cache` | Option B: Pure-stdlib SHA cache (Recommended) | Compute per-file SHAs; map to test impact via import graph + collection cache. No external dependency. |
| `Both` | Option C: pytest-testmon for speed, SHA-cache as fallback | Use testmon when available; fall back to SHA-cache. |

**Trade-Off Analysis:**

Option A is the easiest path. pytest-testmon is well-maintained, has coverage-traced precision, and integrates with pytest's collection cache. Adds one Python dependency.

Option B keeps the deterministic-services-principle minimal-dependency stance. The SHA cache is simpler to reason about (one input → one output). May have lower precision than testmon (imports captured but runtime-only dependencies missed). No external dependency.

Option C is the safety-belt choice. Code complexity doubles (two implementations) for marginal benefit.

**Spec-Coherence Check:**

`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` favors minimal-dependency deterministic services. Option B aligns most closely.

`SPEC-DSI-CI-GATE-001` requires the CI gate but does not specify the test-selection mechanism.

Both A and B cohere with all relevant specs.

**Recommendation:** Option B (pure-stdlib SHA cache).

**Rationale:** Aligns with the deterministic-services-principle minimalism. One less dependency to manage. Lower precision than testmon is acceptable because the cache is a SPEEDUP, not a correctness boundary — if the cache returns "no changed tests," the next layer (Layer 6 governance integrity) still runs full coverage in audit-mode periodically (Slice 7 hardening). If owner prefers testmon's coverage precision over minimalism, Option A is fine; the design contract documents both.

---

## AUQ Filing Path

After Slice 0 reaches VERIFIED, Prime Builder files 5 AskUserQuestion calls in a follow-on session — ideally one-by-one per `feedback_present_decisions_one_by_one.md`. Each call uses the corresponding option labels from above with header chips set to the `Header` column.

Each owner answer becomes a Deliberation Archive record with `source_type='owner_conversation'` and `outcome='owner_decision'`. The records are cited in the `gtkb-push-gate-design-contract-final` thread's `## Owner Decisions / Input` section.

## Decision-Ready Checklist

For each of the 5 questions above:

- [ ] Decision statement is precise and unambiguous.
- [ ] Options are mutually exclusive.
- [ ] 2-4 options (AskUserQuestion constraint; all 5 questions satisfy this).
- [ ] Trade-off analysis cites concrete evidence (specs, bridge precedents, feedback memory).
- [ ] Spec-coherence check confirms which specs the decision affects.
- [ ] Recommendation is explicit; rationale grounds the recommendation.

All 5 packets satisfy the checklist.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

# Cleanup-Sequencing Analysis (Deferred Decision Q1)

**Companion to:** `open-decisions-and-aauq-plan.md` § Q1
**Authority:** `bridge/gtkb-push-gate-design-governance-review-004.md` (Codex GO on REVISED-3)
**Owner directive locked at S365:** *"First: no amnesty — all errors must be found and fixed."*

## The Question

When the deterministic push gate becomes the mechanical blocker, what should the sequencing look like relative to the existing debt inventory the gate would surface?

Option A — **Clean-then-enable**: produce the debt inventory (Slice 1.5), clean the debt (Slice 3), THEN enable the gate as the mechanical blocker (Slice 4+).

Option B — **Enable-then-freeze-until-clean**: enable the gate immediately, accept that all pushes are blocked until the debt is cleaned, work toward zero-debt under the freeze.

Both honor the no-amnesty directive; they differ in development continuity during the cleanup phase.

## Option A — Clean-then-Enable (RECOMMENDED)

### Sequencing

1. **Slice 1** — Canonical `gt push-gate` CLI scaffold + content-addressed cache substrate.
2. **Slice 1.5** — Audit-only mode produces initial debt inventory (`.gtkb-state/push-gate/audits/initial-YYYY-MM-DD/debt-inventory.json`).
3. **Slice 2** — Layer 2 AST checkers (hardcoded-externals, hardcoded SHA, magic-number, import topology). Inventory exposed; not blocking.
4. **Slice 3** — **Debt cleanup phase.** All inventoried defects fixed under normal development cadence. Gate runs in audit-only mode; not blocking.
5. **Slice 4** — Layer 1-7 wired into local pre-push hook. Initially in audit mode.
6. **Slice 5** — Gate flipped from audit-only to mechanical blocker at pre-push.
7. **Slice 6** — GitHub Actions workflow added. Branch protection requires the workflow.
8. **Slice 7** — Final hardening (cache lifecycle, owner-override path, edge cases).

### Risk / Blast Radius

- **Development continuity during cleanup:** Normal cadence preserved. Pushes succeed because gate is audit-only until Slice 5.
- **New debt accumulation risk:** Without a blocking gate during Slice 3 cleanup, a developer could introduce new debt while cleaning old debt. *Mitigation:* Slice 3's cleanup workflow includes audit-mode regression check; any new defect introduced during cleanup is caught by the audit before commit.
- **Slice 3 sizing uncertainty:** Cleanup volume unknowable until Slice 1.5 inventory lands. *Mitigation:* Slice 1.5's inventory schema includes per-rule-code and per-file aggregation enabling prioritized triage; cleanup can ship incrementally.
- **Slice 4 transition risk:** Wiring the gate to pre-push could surprise developers if debt remains in any layer. *Mitigation:* Slice 4 ships in audit mode; Slice 5 flips the switch only after verification that audit reports zero findings.

### Mechanical-Blocker Preservation

The owner's "mechanical blocker" requirement is preserved at Slice 5. The audit-only phase (Slice 1.5 → Slice 5) is **inventory and remediation**, not gate operation. Once Slice 5 lands, no push proceeds without all checks PASS.

### Why Recommended

- Preserves normal development cadence during cleanup.
- Cleanup volume can be measured and scoped before the freeze risk is taken on.
- Mechanical blocker activates at a known-clean baseline, not against an uninventoried surface.
- Codex agreed at `bridge/gtkb-push-gate-design-governance-review-002.md` final notes: *"Clean-then-enable remains the safer sequencing because it preserves the owner's 'mechanical blocker' requirement without freezing all development behind unknown current debt before the debt inventory exists."*

## Option B — Enable-then-Freeze-Until-Clean

### Sequencing

1. **Slice 1** — Canonical `gt push-gate` CLI scaffold + content-addressed cache substrate.
2. **Slice 1.5** — Audit-only mode runs; inventory captured.
3. **Slice 2** — Layer 2 AST checkers.
4. **Slice 3** — Gate flipped to mechanical blocker IMMEDIATELY. All pushes block until corresponding debt is cleaned.
5. **Slice 4** — Debt cleanup under the freeze. Push restrictions force prioritization.
6. **Slice 5** — Once inventory drained to zero, pushes resume normally.
7. **Slice 6** — GitHub Actions workflow + branch protection.

### Risk / Blast Radius

- **Development continuity during cleanup:** Major disruption. All work must be cleanup-related or held until the freeze lifts.
- **New debt accumulation risk:** Minimal. Gate is blocking from Slice 3; nothing new can land without passing.
- **Slice 3 sizing uncertainty:** Same as Option A; inventory determines cleanup volume.
- **Owner expectations:** S365 didn't specify a development freeze. Option B introduces one.
- **Operational risk:** If a critical hotfix arises during the freeze, no clean path exists to ship it (unless the owner-override path Q2 is resolved before Slice 3).

### Mechanical-Blocker Preservation

The mechanical blocker is preserved from Slice 3 onward. The owner's directive is satisfied immediately.

### When Option B Could Be Right

- If owner's S365 *"It takes as long as it takes"* is interpreted as accepting a development freeze.
- If the debt inventory turns out to be small (say, < 50 violations) so the freeze is short.
- If owner separately resolves Q2 (owner-override path) before Slice 3 to provide an emergency hotfix exemption.

## Decision Anchors for the Owner

1. **Tolerance for development freeze:** Does S365's "time-irrelevant execution" extend to a development-blocking phase, or just to the gate's own runtime?
2. **Override-path coupling:** Is Q2 (owner-override) acceptable as a freeze-safety-valve? If yes, Option B becomes safer.
3. **Hotfix risk during freeze:** Are there active production-impacting hotfix paths that must remain available during cleanup?
4. **Debt inventory sizing:** When Slice 1.5 produces the inventory, will the volume justify a freeze or a phased cleanup?

## Recommendation

**Option A (clean-then-enable).** Codex agrees. The mechanical-blocker requirement is preserved (just deferred to Slice 5), development continuity is preserved during cleanup, and the cleanup volume is measured before the freeze risk is taken on.

If the debt inventory from Slice 1.5 reveals a small enough volume (heuristic: < 50 cross-tool findings) that a brief freeze would close it within a week, the owner may revise the decision toward Option B at the `gtkb-push-gate-design-contract-final` thread.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

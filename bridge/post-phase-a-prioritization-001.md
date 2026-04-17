# Post-Phase-A Work Prioritization Plan

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (wrap-plan)
**Scope:** Enumerate all open GT-KB + Agent Red work + propose dependency-informed ordering.
**Owner directive:** Owner asked Prime to propose prioritization + submit to Codex for review.

## Purpose

S299 closed Phase A (v0.6.0 on PyPI) and both post-Phase-A scope
bridges (Azure taxonomy VERIFIED, non-disruptive upgrade
investigation VERIFIED). The forward work surface has expanded
materially — 8 + 7 child bridges previewed + multiple other tracks
in parallel. This plan proposes an ordering + priority tier
assignment.

This is a **plan proposal**, not an implementation bridge. No code
changes flow from Codex's GO here; individual work items each
require their own bridge cycle per
`.claude/rules/codex-review-gate.md`.

## Prior Deliberations

- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (S299 owner decision —
  non-disruptive upgrade + Azure taxonomy run in parallel
  post-Phase-A)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md`
  (VERIFIED — investigation report at `67197ed` with 8 child-bridge
  preview)
- `bridge/gtkb-azure-enterprise-readiness-taxonomy-004.md` +
  `-008.md` (VERIFIED taxonomy at `90cfd99` with 7 child-bridge
  preview; incident cleanly remediated)
- `bridge/gtkb-v060-release-006.md` (v0.6.0 VERIFIED on PyPI)
- `memory/project_gtkb_non_disruptive_upgrade_priority.md` (owner
  S298 directive — CTO adopter cannot be disrupted)

## Complete open-work inventory

### Track A — Bridge infrastructure (sole item)

**A1. Bridge dispatcher latest-status-only fix** — the S299 Azure
incident demonstrated that the OS-poller dispatcher hands stale GO
pointers to spawns without checking whether later VERIFIED has
closed the thread. Flagged in
`bridge/gtkb-azure-enterprise-readiness-taxonomy-007.md` as
`gtkb-bridge-dispatcher-latest-status-only` but not yet proposed.

### Track B — Agent Red CTO readiness cleanup

**B1. Push + CI green on Agent Red develop** — local develop has 16+
commits ahead of `origin/develop`, CI failing at GitHub on the last
pushed state, dirty worktree with 19 modified files (AGENTS.md,
bridge/, memory/, groundtruth.db, widget/, Codex artifacts, etc.)
plus untracked `.githooks/` and `archive/` directories. The
production path (develop → merge main → production) is degraded
while this sits.

**B2. Deferred provisioning display-name rewrite** — 3 files
(`src/integrations/provisioning.py` + 2 test files) split from SMS
OTP hardening bridge due to tenant-isolation risk flagged by Codex
`agent-red-sms-otp-hardening-002`.

**B3. Wiki currency review** — Codex previously flagged wiki as
stale relative to current April work. Content audit + refresh.

### Track C — GT-KB non-disruptive upgrade child bridges (8 bridges)

Investigation report at `docs/reports/non-disruptive-upgrade-audit.md`
enumerated these in dependency order. Registry is the precondition;
the other 7 can follow (some in parallel).

**C1. `gtkb-managed-artifact-registry`** — PRECONDITION.
Single declarative registry consumed by scaffold/upgrade/doctor.
Closes live defect **Gap 2.8** (rule templates copied but not in
`_MANAGED_RULES`).

**C2–C8.** `gtkb-upgrade-pre-flight-checks`, `-rollback`,
`-settings-merge`, `-changelog-integration`, `-interactive-mode`,
`-managed-workflows`, `-toml-migration`.

### Track D — GT-KB Azure enterprise readiness child bridges (7 bridges)

Taxonomy at `docs/reference/azure-readiness-taxonomy.md`
enumerated these with ordering.

**D1. `gtkb-azure-spec-scaffold`** + **D2. `gtkb-azure-adr-template-activation`**
— first pair (parallel).

**D3. `gtkb-azure-iac-skeletons`** + **D4. `gtkb-azure-cicd-gates`**
— second pair (parallel, after D1+D2).

**D5. `gtkb-azure-doctor-offline`** → **D6. `gtkb-azure-doctor-live`**
— sequential.

**D7. `gtkb-azure-operational-docs`** — docs wrap, last.

### Track E — GT-KB Tier A adoption to Agent Red

**E1. `gtkb-skills-tier-a-adoption-001`** — port Tier A skills/hooks
into Agent Red's live tooling (not just GT-KB scaffolder). Flagged
in `memory/work_list.md` as a post-v0.6.0 follow-up.

### Track F — Agent Red product

**F1. POR Step 14 — E2E phone OTP smoke test** — BLOCKED on
toll-free carrier approval (Application 346df3eb). Not proceed-able
until carrier returns.

**F2. POR Step 16.D — orphan test rationalization** — ~10,440
orphan tests, largest sub-phase.

**F3. POR Step 16.E — exit verification** — untested-spec count ≤ 6
+ orphan-test count ≤ 100. Depends on 16.D.

**F4. Commercial Readiness SPEC-1831/1832/1833 → verified** —
currently at `implemented`; need test-plan execution and status
promotion. Small scope each.

**F5. WI-3156 — `deploy.py` scaling enforcement** — separate from
POR; small scope.

**F6. Zero-Knowledge Architecture (Phase 4, long-term)** — 4 specs
(SPEC-1843/1844/1644/1840), 5 implementation phases. Prerequisite
per work_list: POR Step 16 substantially complete.

## Proposed prioritization

### Tier 1 — Immediate (visible to CTO; blocks downstream work)

**1. A1 — Bridge dispatcher latest-status-only fix.** Small scope
(~1-2 days). Prevents future incidents of the S299 Azure-thread
variety. Independent of everything else; can start immediately.

**2. B1 — Agent Red CTO cleanup.** Gets origin/develop current,
restores CI green, makes emergency-fix path usable. Critical for
any production change. Scope: classify 19 dirty-worktree files,
commit/discard appropriately, push, fix CI failures, confirm
green.

**3. C1 — `gtkb-managed-artifact-registry`.** Closes the live
defect (Gap 2.8) the investigation surfaced. Precondition for all
7 other non-disruptive upgrade child bridges. Every adopter of
v0.7.x+ benefits. No child bridge in Tracks C/D can land safely
without this first — a second parallel manifest would make the
split-manifest problem worse.

### Tier 2 — High priority (parallelizable after Tier 1)

**4. C2 — `gtkb-upgrade-pre-flight-checks`.** First child bridge
after the registry. Most immediate adopter-quality-of-life win
(`--dry-run` catches problems before anything is modified).
Independent of Azure track.

**5. D1 + D2 — Azure spec scaffold + ADR template activation.**
The Azure child-bridge entry points. Both can run in parallel once
taxonomy is VERIFIED (which it now is). Parallel with C2.

**6. E1 — Tier A skills adoption in Agent Red.** Brings the
decision-capture / bridge-propose / spec-intake skills into Agent
Red's live tooling (not just adopter scaffolds). Independent of C
and D tracks. Modest scope.

### Tier 3 — Medium priority (dependency-gated)

**7. C3 + C4 — Upgrade rollback + settings-merge.** After C1+C2
settle. These two can parallel each other.

**8. D3 + D4 — Azure IaC skeletons + CI/CD gates.** After D1+D2
settle. Parallel with each other.

**9. F2 — POR Step 16.D orphan test rationalization.** Large scope
(~10,440 tests). Does not block other tracks but closes a hygiene
debt that increases with time.

**10. F4 — Commercial Readiness SPEC-1831/1832/1833 → verified.**
Small scope each. Can pick up in background between other bridges.

### Tier 4 — Planned / deferred

**11. F1 — POR Step 14 E2E OTP smoke test.** BLOCKED on toll-free
carrier approval. Passive monitor already running. No action until
carrier returns.

**12. C5 + C6 + C7 + C8 — Remaining non-disruptive upgrade child
bridges** (changelog integration, interactive mode, managed
workflows, TOML migration). After earlier C-track children settle.

**13. D5 + D6 + D7 — Azure doctor offline + live + operational
docs.** After D3+D4 settle. D5 before D6 (offline before live).

**14. F3 — POR Step 16.E exit verification.** After 16.D.

**15. B2 — Provisioning display-name rewrite.** Needs
tenant-isolation design review first. Can happen alongside any
other track but not critical path.

**16. B3 — Wiki currency review.** Paper-over content debt; no
downstream dependencies.

**17. F5 — WI-3156 deploy.py scaling.** Separate from POR; small
scope.

### Tier 5 — Long-term (prerequisites gated)

**18. F6 — Zero-Knowledge Architecture (Phase 4).** 4 specs, 5
phases, multi-session. Work list says "POR Step 16 substantially
complete" as prerequisite. Probably a multi-month arc.

## Critical path recommendation

**Days 1-3**: A1 (dispatcher fix) + B1 (Agent Red cleanup) + C1
(registry). These three unblock everything else and have
independent scopes.

**Days 4-10**: Tier 2 (C2 + D1+D2 + E1) in parallel.

**Days 11+**: Tier 3 follows as its dependencies settle.

## Dependencies matrix

```
A1 → nothing (fully independent)
B1 → nothing (fully independent within Agent Red tree)
C1 → blocks C2-C8 (registry is precondition)
C2 → requires C1
C3 + C4 → require C1; parallel to each other
C5-C8 → require at minimum C1; can parallel after C2
D1 + D2 → require Azure taxonomy VERIFIED ✅; parallel to each other
D3 + D4 → require D1+D2 settled; parallel to each other
D5 → requires D3+D4
D6 → requires D5
D7 → last, after D5+D6
E1 → requires v0.6.0 on PyPI ✅; independent of C+D tracks
F1 → BLOCKED externally; passive monitor in place
F2 → independent; can happen in parallel with anything
F3 → requires F2
F4 → independent; 3 sub-items, small scope
F5 → independent; small scope
F6 → requires F2+F3 "substantially complete"
```

## Owner override invitation

This plan is the Prime Builder's recommendation. The owner may
override any specific ordering decision per
`.claude/rules/codex-review-gate.md` owner-pre-approval semantics.
Specific invitations:

1. **A1 vs C1 ordering.** A1 is the safer fix-first move (prevents
   future incidents). C1 is the bigger adopter-quality-of-life win.
   Could parallel them; recommended sequential (A1 first) to keep
   dispatcher reliable while C1 is in flight.
2. **B1 effort estimate.** 19 dirty-worktree files may need owner
   input on which to commit vs. discard. Could be half-a-day or
   two days depending on how much is stale.
3. **E1 scope ordering.** Could run before C1 (Tier A adoption is
   small and Agent-Red-only), but then E1 benefits from later
   non-disruptive upgrade work reaching Agent Red.
4. **Azure vs non-disruptive priority**: Option C was parallel.
   This plan puts C1 (registry) ahead of Azure D1+D2, because the
   registry closes a live defect while Azure work is additive. If
   the CTO trial emphasizes Azure specifically, owner may want to
   flip D1+D2 earlier.

## Scope constraints for this proposal

This is a **plan proposal only**. No code changes. No KB mutations.
No commits flow from approval of this plan. Each numbered item
still requires its own bridge cycle (proposal → Codex review → GO
→ implement → post-impl → VERIFIED) per
`.claude/rules/codex-review-gate.md`.

## GO Request

Codex: please review this prioritization for:

1. **Ordering logic** — is C1 correctly positioned as precondition
   for C2-C8? Is the A1 → B1 → C1 day-1-to-3 critical path right?
2. **Dependency matrix accuracy** — any missed dependencies? Any
   claimed dependencies that aren't real?
3. **Tier 2 parallelism** — are C2 + D1+D2 + E1 genuinely
   independent (disjoint files, no hidden coupling)?
4. **Deferred items** — is it right to defer F2/F3 (POR 16.D/E) to
   Tier 3 despite their size? Or should they be pulled earlier?
5. **Azure-vs-non-disruptive balance** — is putting C1 ahead of
   D1+D2 the right call, given owner Option C said parallel?
6. **Missing tracks** — any open work not captured in the
   inventory?

If approved: this plan becomes the forward-work ordering
reference. Each item still requires its own bridge proposal
before implementation. Disagreements or NO-GO-level revisions
welcome.

## Scanner Safety

Pre-flight scan: plan prose contains track names, bridge names,
SPEC IDs, file paths. No literal credential values. Expected hook
verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

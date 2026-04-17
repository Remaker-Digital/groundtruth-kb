# Post-Phase-A Work Prioritization Plan (REVISED-1)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (wrap-plan)
**NO-GO reference:** `bridge/post-phase-a-prioritization-002.md`
**Supersedes:** `bridge/post-phase-a-prioritization-001.md`

## Summary of Revision

All 3 Codex P1 findings addressed. All other content retained
(inventory shape, tier structure, owner-override invitation, scope
constraints) per Codex's positive verification on B1, C1 ordering
within Track C, D1/D2 ordering within Track D, POR 16.D/E sourcing,
and Tier A adoption sourcing.

**Three specific fixes:**

1. **P1-F1 (C1 overstated as blocking Tracks C+D)** — Corrected C1
   to block Track C only. D1/D2 require only Azure taxonomy
   VERIFIED state (already satisfied). Added owner-override
   language if Mike wants C1 before D1/D2 as a priority choice
   (not a technical dependency).
2. **P1-F2 (F5 stale)** — Removed WI-3156 / deploy.py scaling. The
   `deploy-scaling-full-coverage-006` bridge VERIFIED that work;
   it is not open. Replaced with the actual remaining non-blocking
   follow-up: `wiki/Scaling-Analysis.md` hygiene update (the
   genuine leftover from that VERIFIED bridge).
3. **P1-F3 (A1 needs current-code reconciliation)** — Re-scoped A1
   against current scanner code. The filter-by-latest-status logic
   is already correct; the actual remaining defect is **spawn-time
   revalidation** — the spawn receives a pointer at scan time but
   does not re-check the INDEX at execution time, so a
   VERIFIED that lands between scan and spawn-run goes unseen.
   A1 is re-named `gtkb-bridge-spawn-revalidation` with a specific
   scope.

## Prior Deliberations

- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (owner S299 decision —
  Option C parallel workstreams)
- `bridge/post-phase-a-prioritization-001.md` (NEW, superseded)
- `bridge/post-phase-a-prioritization-002.md` (Codex NO-GO — 3 P1
  findings)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md`
  (VERIFIED)
- `bridge/gtkb-azure-enterprise-readiness-taxonomy-004.md` +
  `-008.md` (VERIFIED + remediation VERIFIED)
- `bridge/deploy-scaling-full-coverage-006.md` (VERIFIED — settled
  WI-3171; no open scaling-enforcement work remains)
- `bridge/gtkb-azure-enterprise-readiness-taxonomy-007.md`
  (remediation report; flagged the spawn-time-revalidation defect)

## Complete open-work inventory (corrected)

### Track A — Bridge infrastructure

**A1. `gtkb-bridge-spawn-revalidation`** — current scanners
(`codex-file-bridge-scan.ps1:125-136`,
`claude-file-bridge-scan.ps1:173-191`) correctly filter to latest
`Versions[0].Status == NEW|REVISED` (Codex) or `GO|NO-GO` (Prime).
**That part is already correct.**

The remaining defect is spawn-time: when the dispatcher hands a
spawn an entry-to-process snapshot at time T0, the spawn may not
run until T0+Δ (typically 2-10 min). If a later status lands in
the INDEX during [T0, T0+Δ] — e.g., a VERIFIED closing the thread —
the spawn acts on the stale snapshot. The S299 Azure incident was
an instance of this: a GO at `-002` was handed to a spawn; by the
time the spawn ran, `-004` had closed the thread VERIFIED, but
the spawn never re-checked.

**Scope**: add a spawn-time pre-execution guard. Before implementing
the work, the spawn re-reads the entry's current `Versions[0]` and
aborts if (a) it no longer matches the snapshot status, or (b) it
is now a terminal status (VERIFIED / NO-GO). Targeted code paths:
whatever invokes `claude.exe` or `codex.exe` with the entry-info
payload. Verification: an integration test that mutates INDEX
between snapshot and spawn start and asserts the spawn aborts.

### Track B — Agent Red CTO readiness cleanup

**B1. Push + CI green on Agent Red develop.** Codex empirically
confirmed: `git status -sb` reports `develop...origin/develop
[ahead 20]`, 19 modified files, many untracked. Last 5 develop
runs on GitHub are `completed failure` on SonarCloud (2026-04-15).

**B2. Deferred provisioning display-name rewrite** (3 files,
tenant-isolation review required per
`agent-red-sms-otp-hardening-002`).

**B3. Wiki currency review** (Codex previously flagged wiki as
stale).

**B4. `wiki/Scaling-Analysis.md` follow-up** (from
`deploy-scaling-full-coverage-006.md` as the remaining non-blocking
follow-up from that VERIFIED bridge). **This replaces the stale F5
entry from `-001`.**

### Track C — GT-KB non-disruptive upgrade child bridges (8 bridges)

**C1. `gtkb-managed-artifact-registry`** — **PRECONDITION for
C2-C8 within Track C.** Not a precondition for any Azure bridge.
Closes live defect Gap 2.8 (rule templates in `scaffold.py:273-274`
not in `_MANAGED_RULES` at `upgrade.py:45-51`; doctor required at
`doctor.py:483-486` but upgrade cannot restore).

**C2-C8.** Upgrade pre-flight checks, rollback, settings-merge,
changelog integration, interactive mode, managed workflows, TOML
migration. Each requires C1.

### Track D — GT-KB Azure enterprise readiness child bridges (7 bridges)

**D1. `gtkb-azure-spec-scaffold`** + **D2.
`gtkb-azure-adr-template-activation`** — first pair. Require only
Azure taxonomy VERIFIED (✅ satisfied). **Do NOT require C1.**

**D3 + D4 + D5 + D6 + D7** — ordering from taxonomy doc
(docs/reference/azure-readiness-taxonomy.md:508-529).

### Track E — Tier A skills adoption in Agent Red

**E1. `gtkb-skills-tier-a-adoption-001`** — Flagged in
`memory/work_list.md:40`.

### Track F — Agent Red product

**F1. POR Step 14 E2E phone OTP smoke test** (BLOCKED on carrier;
passive monitor in place).

**F2. POR Step 16.D orphan test rationalization** (~10,440 tests;
independent).

**F3. POR Step 16.E exit verification** (depends on F2).

**F4. Commercial Readiness SPEC-1831/1832/1833 → verified**
(currently `implemented`; small scope each).

**F5** — **REMOVED** (was stale; WI-3156/WI-3171 scaling
enforcement already VERIFIED at
`deploy-scaling-full-coverage-006`).

**F6. Zero-Knowledge Architecture (Phase 4)** (long-term; prereq
POR 16 substantially complete).

## Revised prioritization

### Tier 1 — Immediate (visible to CTO; blocks downstream work)

**1. A1 — `gtkb-bridge-spawn-revalidation`.** Small scope, now with
specific technical target (spawn pre-execution guard). Prevents
future S299-Azure-incident-class races.

**2. B1 — Agent Red CTO cleanup.** 20 commits ahead / CI red / 19
dirty-file classification. Critical for production path integrity.

**3. C1 — `gtkb-managed-artifact-registry`.** Closes live defect
Gap 2.8. **Blocks C2-C8 only.** Does NOT block Azure D1/D2.

### Tier 2 — High priority (parallelizable after Tier 1)

**4. C2 — `gtkb-upgrade-pre-flight-checks`.** First adopter-quality
win after registry.

**5. D1 + D2 — Azure spec scaffold + ADR template activation.**
Entry points for Track D. **Can run parallel with Tier 1 items
C1 (genuinely independent) or held in Tier 2 as a priority
choice.** See owner invitation below.

**6. E1 — Tier A skills adoption in Agent Red.** Modest scope;
independent of C/D tracks.

### Tier 3 — Medium priority (dependency-gated)

**7. C3 + C4** — upgrade rollback + settings-merge (parallel; both
require C1).

**8. D3 + D4** — Azure IaC skeletons + CI/CD gates (parallel; both
require D1+D2).

**9. F2 — POR 16.D orphan test rationalization** (large; independent).

**10. F4 — Commercial Readiness SPEC verification** (3 small
items).

**11. B4 — `wiki/Scaling-Analysis.md` update** (small follow-up
from VERIFIED `deploy-scaling-full-coverage-006`).

### Tier 4 — Planned / deferred

**12. F1 — POR 14** (BLOCKED externally).

**13. C5-C8 — Remaining non-disruptive upgrade children** (after
earlier Track C children settle).

**14. D5 + D6 + D7 — Azure doctor offline + live + operational
docs** (sequential; D5 before D6; D7 last).

**15. F3 — POR 16.E exit verification** (after F2).

**16. B2 — Provisioning display-name rewrite** (tenant-isolation
design review required).

**17. B3 — Wiki currency review** (paper-over content debt).

### Tier 5 — Long-term

**18. F6 — Zero-Knowledge Architecture Phase 4** (4 specs, 5
phases; prereq POR 16 substantially complete).

## Corrected dependency matrix

```
A1 → independent
B1 → independent (scoped to Agent Red repo)
C1 → blocks C2-C8 (within Track C only)
C2 → requires C1
C3 + C4 → require C1; parallel to each other
C5-C8 → require at minimum C1; can parallel after C2
D1 + D2 → require Azure taxonomy VERIFIED ✅; parallel to each other;
         INDEPENDENT of C1 (technical — see P1-F1 correction)
D3 + D4 → require D1+D2 settled; parallel to each other
D5 → requires D3+D4
D6 → requires D5
D7 → last, after D5+D6
E1 → requires v0.6.0 on PyPI ✅; independent of C+D
F1 → BLOCKED externally
F2 → independent
F3 → requires F2
F4 → independent; 3 sub-items
F6 → prereq "POR 16 substantially complete" (F2 mostly done)
B2 → prereq tenant-isolation design review
B3 → independent
B4 → independent; small follow-up from settled bridge
```

## Owner override invitation (revised)

The P1-F1 correction means C1 and D1/D2 are technically independent.
Mike may still choose to sequence them (e.g., C1 first for
registry-priority reasons, or D1/D2 first for CTO-Azure-demonstration
reasons), but that is a **priority choice**, not a dependency
constraint. This plan recommends starting C1, D1, and D2
concurrently in Tier 2, but lists C1 as Tier 1 to reflect its
Gap-2.8 defect-closing property.

Specific invitations:

1. **Absolute Tier-1 trio vs. other orderings**: A1 + B1 + C1.
   Mike may want to include D1+D2 in Tier 1 if Azure demo is
   imminent.
2. **B1 effort estimate**: unknown until 19 dirty files are
   classified. Could be half-day or 2-3 days.
3. **Registry vs pre-flight ordering within Track C**: C1 is
   registry; C2 is pre-flight. C2 could alternately precede C1 if
   Mike prefers, but the investigation explicitly recommends
   registry-first.
4. **POR 16.D timing**: the 10,440 orphan test sub-phase will be
   the largest single body of work in 2026-Q2. Could be pulled to
   Tier 1 if orphan-test debt is owner's Q2 priority.

## Addressed Codex findings

- **P1-F1 (C1 overstated)**: §"Tier 1" + §"Corrected dependency
  matrix" now explicitly say "C1 blocks C2-C8 only". The text "No
  child bridge in Tracks C/D can land safely without this first"
  is removed. D1/D2 are noted as technically independent of C1.
- **P1-F2 (F5 stale)**: F5 removed from inventory. `B4 wiki
  Scaling-Analysis.md follow-up` added in Track B as the genuine
  remaining non-blocking work from the already-VERIFIED
  `deploy-scaling-full-coverage-006`.
- **P1-F3 (A1 needs current-code reconciliation)**: A1 re-scoped
  to `gtkb-bridge-spawn-revalidation`. Explicitly acknowledges
  scanner filter logic is already correct; identifies the
  remaining defect as spawn-time revalidation (snapshot vs.
  execution-time state divergence). Includes a concrete
  verification idea (integration test that mutates INDEX between
  snapshot and spawn start and asserts abort).

## Scope constraints (unchanged)

Plan proposal only. No code changes, no KB mutations, no commits
flow from Codex approval of this plan. Each numbered item still
requires its own bridge cycle per `.claude/rules/codex-review-gate.md`.

## GO Request

Codex: please confirm the 3 P1 findings are addressed. Specific
review targets:

1. **P1-F1 fix**: is the C1→C2-C8-only claim now correctly
   scoped? Is the owner-override language sufficiently separating
   technical dependency from priority choice?
2. **P1-F2 fix**: is `wiki/Scaling-Analysis.md` the correct
   replacement for the stale F5, or should I remove it entirely?
3. **P1-F3 fix**: is "spawn-time revalidation" the correct
   framing? Should A1 include a concrete test design beyond the
   "integration test that mutates INDEX" sketch?
4. **Dependency matrix**: any still-inaccurate dependencies?

If approved: this plan becomes the forward-work ordering reference.
Each item still requires its own bridge proposal before
implementation.

## Scanner Safety

Pre-flight scan: revised plan contains track names, bridge names,
line references, and prose. No literal credential values. Expected
hook verdict: **pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

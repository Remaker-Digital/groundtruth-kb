NEW

# GT-KB Tier A Adoption — Agent Red Retroactive-Adopter Scope Proposal (E1)

**Status:** NEW (scope proposal)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Authorizing chain:**
- `bridge/post-phase-a-prioritization-004.md` (GO'd plan, Tier 2 item E1)
- `bridge/gtkb-operational-skills-tier-a-005.md` (Tier A scope closure noting "Follow-up bridge after v0.6.0 ships: `gtkb-skills-tier-a-adoption-001` (Agent Red adoption of the five deliverables).")
- `bridge/gtkb-rollback-receipts-016.md` (VERIFIED — payload-branch-and-merge + receipt flow landed)
- `bridge/gtkb-upgrade-pre-flight-checks-implementation-004.md` (VERIFIED — C2 pre-flight checks landed)
- `bridge/gtkb-da-governance-completeness-implementation-020.md` (VERIFIED — governance hooks operational)

## Summary

**Scope proposal for E1.** The prioritization-plan shorthand "Agent Red
adopts the six Tier A deliverables" undersells the actual scope: Agent Red
is not a GT-KB adopter today. It predates `gt project init` and has no
`groundtruth.toml` manifest, so `gt project upgrade` cannot run against it.
This bridge scopes a **broadened retroactive adoption** — making Agent Red
a formal GT-KB adopter for the first time, then running the full upgrade
pipeline (pre-flight + payload-branch-and-merge + rollback receipt) in a
real production-adjacent context, then wiring the Tier A deliverables into
Agent Red's existing governance.

This is a scope bridge, not an implementation bridge. No Agent Red or GT-KB
source writes are authorized until Codex GO + an implementation bridge.

## Prior Deliberations

- **DELIB-0317** — GroundTruth GitHub-installability contract comparison
  (relevant to how Agent Red would receive future GT-KB releases).
- **DELIB-0501** — Agent Red Large-Scale Commercial Production Plan
  (broader Agent Red trajectory; Tier A adoption is one subphase).
- **DELIB-0706** — **"Spec pipeline features are GT-KB product features,
  not Agent Red specific"** — directly relevant. Captures the recent
  realization that governance/hooks/templates/vocabulary belong in GT-KB
  product with Agent Red as adopter. E1 is the first real exercise of
  that separation.
- No prior `gtkb-skills-tier-a-adoption` deliberations found. This is the
  first scope proposal in the thread.

## Source: Current State of Agent Red vs. GT-KB Registry

Inspected 2026-04-18:

| Surface | Agent Red current | GT-KB registry (`dual-agent`) |
|---------|-------------------|-------------------------------|
| `groundtruth.toml` manifest | **Absent** | Required for upgrade |
| `.claude/hooks/*.py` | 6 files: `assertion-check`, `credential-scan`, `destructive-gate`, `poller-freshness`, `scheduler`, `spec-classifier` | 14 files per `artifacts_for_scaffold("dual-agent", class_="hook")` |
| `.claude/rules/*.md` | 6 rules: `bridge-essential`, `codex-review-gate`, `deliberation-protocol`, `file-bridge-protocol`, `loyal-opposition`, `report-depth-prime-builder-context` | 8 rules per registry |
| `.claude/skills/` | Many project-specific (`arch-audit`, `deploy`, `kb-*`, etc.) | 3 Tier A skills: `decision-capture`, `bridge-propose`, `spec-intake` + helpers |
| `.claude/settings.json` | Hand-rolled | 11 registry-managed hook registrations |
| `scanner-safe-writer.py` hook | **Absent** | Required by registry (PreToolUse) |
| Tier A canonical credential-patterns module | **Absent** | Ships in `groundtruth_kb` pip package |
| Tier A metrics collector | **Absent** | Ships in GT-KB repo as `scripts/collect_phase_a_metrics.py` |

**Gaps:** ~8 registry hooks absent from Agent Red; scanner-safe-writer
missing entirely; no Tier A skills; no manifest; no settings registry
alignment.

**Extras in Agent Red not managed by the registry:** `poller-freshness.py`
(bridge-automation-specific), `scheduler.py` (Agent Red automation), most
of the `.claude/skills/` set (project-specific governance skills).

## Proposed Scope — Six Phases

### Phase α — Retroactive Manifest

- Decide profile: `dual-agent` vs `dual-agent-webapp`. Agent Red is a
  webapp deployed to Azure Container Apps. `dual-agent-webapp` writes
  `Dockerfile`/`docker-compose.yml`/`.env.example`, which may not align
  with Agent Red's existing Azure-native deployment.
- Decide `scaffold_version`: released PyPI (`0.6.1`) vs. current GT-KB
  main HEAD (`70773f4`, has rollback-receipts + C2 pre-flight + gov-
  completeness).
- Hand-write `groundtruth.toml` (or run a dry-run `gt project init`
  variant that writes just the manifest without scaffold files).
- Zero other Agent Red writes in Phase α.

### Phase β — Dry-Run and Classification

- `gt project upgrade --dry-run` on Agent Red.
- Expected output surface (using C2 machinery):
  - Many `[WARNING]` rows for in-flight bridge entries (Agent Red's
    `bridge/INDEX.md` has ~5–10 currently active documents).
  - Many `[INFORMATIONAL]` rows for scaffold-coverage delta (Agent Red
    has ~100+ files the scaffold doesn't write).
  - `[ADD]` rows for missing registry-managed hooks, rules, skills.
  - Possibly `[MERGE-EVENT-HOOKS]` if `.claude/settings.json` differs
    from registry shape.
- Classify every `[ADD]` and `[MERGE-EVENT-HOOKS]` row as:
  - **A1-adopt**: apply as-is (Tier A deliverables expected here).
  - **A2-conflict**: registry file collides with Agent-Red-specific
    shape; requires reconciliation.
  - **A3-reject**: managed file should not land in Agent Red; registry
    row should be scoped profile-differently or become adopter-opt-in.

### Phase γ — Reconciliation

- For each A2/A3: document decision with Codex review.
- For A1: no action needed at this phase.
- Possible outcomes:
  - Some registry rows may need profile refinement (e.g., `scheduler.py`
    might move out of `dual-agent` if it's truly Agent-Red-specific —
    but that's a GT-KB change, outside E1 scope).
  - Agent Red extras (`poller-freshness.py`, `scheduler.py`, project-
    specific skills) are accepted as adopter-authored, not registry-
    managed. Coverage-delta will flag them as informational forever.
- Produce a "reconciliation plan" document (Agent Red side) that
  documents each adoption decision.

### Phase δ — Apply

- **Clean-tree precondition.** Agent Red currently has 16+ unpushed
  commits + ~100+ untracked files (the bridge backlog). The rollback-
  receipts-landed `_require_clean_tree` gate will refuse. Resolution
  options (to decide in Phase γ):
  - (δ1) Gate E1 on **B1 (`agent-red-cto-cleanup`) execution first** —
    cleanest path, but blocks E1 on separate work.
  - (δ2) Do a staged cleanup as part of E1 Phase δ setup: commit all
    the bridge artifacts, stash any genuine uncommitted work, then
    proceed.
  - (δ3) Run the upgrade on a **side branch** (`e1-adoption`) where
    the tree can be made clean; merge back manually when verified.
- Run `gt project upgrade --apply`. Should produce:
  - Payload branch `gt-upgrade-payload-<id>`
  - Payload commit with registry-managed files
  - `git merge --no-ff` → real merge commit
  - Post-merge receipt in `.claude/upgrade-receipts/active/<id>.json`
- **Validate:** `git revert -m 1 <merge_commit> --no-commit` shows
  only payload files; receipt survives. This is the first real-
  adopter validation of the rollback primitive landed in rollback-
  receipts Phase 3.

### Phase ε — Wire Into Governance

- For each newly-landed hook: verify it fires on the expected event
  (e.g., `scanner-safe-writer.py` runs on `PreToolUse` Write calls and
  correctly scans / redacts per its helper).
- For each newly-landed skill: invoke manually and confirm the
  confirm-before-mutate contract (for `spec-intake`) and the overlap-
  safe redact contract (for `bridge-propose`).
- Update Agent Red's `CLAUDE.md` / operational docs to reference the
  new skills where they supersede project-specific alternatives.
- **Out of scope for the first tranche**: removing superseded Agent-
  Red-specific skills (e.g., if the Tier A `bridge-propose` should
  retire an Agent-Red-specific alternative, that's a follow-up
  bridge).

### Phase ζ — Metrics Collection (Optional / Deferrable)

- Install the Tier A metrics collector (`scripts/collect_phase_a_metrics.py`
  from GT-KB) or its packaged equivalent.
- Configure scanner-safe-writer to emit JSONL to
  `.claude/hooks/scanner-safe-writer.log`.
- Run collector over ~1–2 sessions to generate first real-world
  deny-record dataset.
- **Can be deferred to a follow-up bridge** if Phases α–ε land first
  and need a merge-and-validate cycle before adding metrics surface.

## Explicit Boundaries

**In scope for this scope bridge:**
- Framing the six phases + dependencies.
- Naming the open design questions for Codex.
- Identifying the B1 interaction.
- Requesting Codex GO on scope.

**Out of scope for this bridge entirely:**
- Any Agent Red or GT-KB source writes.
- Decisions that should be Codex's to make (profile choice, version
  target, clean-tree strategy) — flagged as open questions below.
- The Phase ζ metrics surface if it becomes contentious (can be its
  own follow-up bridge).

**Out of scope until a future phase bridge:**
- Removing superseded Agent-Red-specific skills (CLAUDE.md
  documentation refresh only).
- Promoting `poller-freshness.py` or `scheduler.py` into the GT-KB
  registry (that's a GT-KB-side bridge, not Agent Red adoption).
- Teaching `dual-agent-webapp` profile to skip Docker files on Azure-
  native adopters (a GT-KB-side registry/profile change).

## Open Design Questions for Codex

1. **Profile choice.** Recommend `dual-agent` (not `-webapp`) for Agent
   Red because the webapp-variant writes Docker/Terraform templates
   Agent Red doesn't use. Downside: Agent Red IS a webapp, so the
   manifest would lose that classification. Alternatives: teach the
   registry an `azure-webapp` variant (larger scope); accept the
   Docker rows as informational-only via C2 coverage-delta (messy but
   zero GT-KB change). Codex preference?

2. **`scaffold_version`.** Recommend PyPI `0.6.1` as the stable
   anchor. Newer work (rollback-receipts + C2 + gov-completeness) is on
   GT-KB main HEAD but not yet released — adopting from main would
   require source-install and couple Agent Red to GT-KB commit SHAs.
   Codex preference?

3. **Clean-tree strategy for Phase δ.** Three options (δ1 / δ2 / δ3
   above). δ1 (gate on B1) is cleanest but introduces a cross-bridge
   dependency. δ2 (staged cleanup) is pragmatic but mixes scopes.
   δ3 (side-branch) avoids blocking but produces unusual history.
   Codex preference?

4. **Reconciliation rigor.** Phase γ classifies each drift action as
   A1/A2/A3. How formal should this be — a brief list in the
   implementation bridge, or a dedicated reconciliation document
   pinned to specific commits on both sides?

5. **Phase boundaries — single impl bridge vs split.** Six phases is
   a lot for one implementation bridge. Options: (a) single impl
   bridge covering α–ζ with phase-gated commits; (b) split into
   two impl bridges (α+β+γ = "prepare", δ+ε = "apply"); (c) split
   into four (α, β+γ, δ, ε+ζ). Codex preference on session count and
   review rhythm.

6. **Phase ζ scope.** Include metrics collection in E1 or defer to a
   follow-up?

## Estimated Impact

- **Agent Red writes:** ~14 new managed hook files, ~2 new managed rule
  files, ~6 new managed skill files (decision-capture + bridge-propose
  + spec-intake with helpers), `.claude/settings.json` merged to
  registry shape, `groundtruth.toml` created, `.claude/upgrade-
  receipts/active/<id>.json` receipt, CLAUDE.md adjustments.
- **Agent Red test impact:** no production source changes expected; new
  CI gates possible if Agent Red's existing CI should lint the new
  files.
- **GT-KB writes:** **zero**, unless Phase γ reconciliation surfaces a
  registry bug that must be fixed before adoption can proceed. If so,
  that fix is a separate GT-KB bridge.
- **Session count:** likely 1–2 sessions. Could extend if Phase γ
  reconciliation surfaces extensive conflicts.

## Zero GT-KB Writes

Unchanged from the GO. E1 is primarily Agent Red writes. GT-KB only
ever writes as a **dependency**: GT-KB publishes v0.6.1 (already done
on PyPI), Agent Red adopts.

## Requested Verdict

**GO on scope + open-question resolutions**, OR **NO-GO with specific
findings** I can address in a REVISED scope bridge.

## Next Step After Codex GO

File `bridge/gtkb-skills-tier-a-adoption-implementation-001.md` (or
phase-specific bridge names, per Codex's answer to open question 5)
with concrete file lists, profile choice, scaffold_version pin,
clean-tree strategy, reconciliation plan, and commit sequencing.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

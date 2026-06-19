---
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 842c2b3d-f449-4faa-afb7-24b24f78546a
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI (explanatory output style)
---

# Session Handoff — GT-KB Production-Readiness Roadmap (2026-06-19)

> Operational notepad (not canonical). The fresh session's first message should be
> the **Handoff Prompt** block below (or: "Read memory/SESSION-HANDOFF-2026-06-19-production-readiness-roadmap.md and execute it as a loop").

---

## Handoff Prompt (paste as the first owner message of the fresh session)

```text
::init gtkb pb

# Mission: drive the GT-KB production-readiness roadmap to VERIFIED conclusion, in a loop.

You are Prime Builder (harness B). Work in a LOOP: each iteration, (1) re-read live
bridge/lock state, (2) take the highest-priority ACTIONABLE task, (3) drive it through
the bridge cycle (propose -> LO GO -> implement -> report -> VERIFIED) to its VERIFIED
conclusion or to a clean blocked state, (4) move to the next task. Do not stop after one
task — iterate until every task is VERIFIED or genuinely blocked, surfacing owner
decisions via AskUserQuestion only when a decision truly blocks progress. Never bypass a
governance gate.

## State at handoff (2026-06-19)
- GT-KB is NOT production-ready. Root cause: leaky release-evidence/persistence machinery
  (VERIFIED work not git-committed; tree perpetually dirty; `gt project doctor` = FAIL;
  v1.0 gate unbuilt).
- Banked: 2 clean commits cut the dirty tree 184 -> 85.
  - df0ed79d9  chore(bridge): 99 terminal-thread bridge audit files
  - 355bdbc13  feat(agent-disposition): post_action_receipt module + tests
- BLOCKED at handoff: the impl-start gate (PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001)
  globally locks protected mutations while a concurrent Antigravity/C post-impl report
  (gtkb-show-thread-bridge-windows-unicode-003, NEW) awaits LO review. Do NOT bypass. CAUTION:
  the LO dispatch pipeline is DEGRADED (WI-4679 — see P0.1), so this lock may NOT auto-clear —
  the blocking report needs a working LO (only D/ollama may be functional; C cannot self-review,
  F sticky-backoff). Repairing LO dispatch (P0.1) is what actually unblocks.

## Roadmap (drive each to VERIFIED)

### Phase 0 — Reliability foundation (prerequisite; START HERE)
- P0.1  Repair the DEGRADED LO DISPATCH PIPELINE (most acute; this is why locks don't clear).
        WI-4679 (PROJECT-GTKB-RELIABILITY-FIXES, P1, harness-dispatch, raised by Antigravity/C):
        the gemini CLI throws IneligibleTierError (deprecated "individuals" tier) so
        loyal-opposition:C exits 1 on every auto-dispatch and trips the circuit breaker; AND the
        dispatcher state reset skips clearing last_dispatched_signature for F (OpenRouter) on
        max-turn exhaustion -> sticky backoff. Net: 2 of 3 LO harnesses (C, F) cannot be
        auto-dispatched; only D (ollama) may be functional, so NEW/REVISED reports sit
        unreviewed and impl-start locks don't clear. Verify the F signature-reset claim in the
        dispatch substrate, fix it, and resolve/route around the gemini tier error for C.
- P0.2  Fix the commit-after-VERIFIED cadence (the other half of the root cause). Tracked:
        WI-4545 (+ cluster WI-4369 / WI-3497 / WI-3498 / WI-4630 / WI-4305). Design a fix so
        VERIFIED bridge work auto-commits, drive to VERIFIED.
- P0.3  Clear the 5 doctor FAILs (`python -m groundtruth_kb project doctor` for live list):
        (a) config/registry/sot-artifacts.toml duplicate id 'bridge-versioned-files'
            (lines 207-218 glob vs 220-231 dir — disambiguate the id, don't just delete);
        (b) standing-backlog health 8-fail (project_name inconsistency WI-3500/WI-3503);
        (c) 15 VERIFIED bridges missing Owner-Decisions section (likely doctor-check
            grandfather, not retro-edit of append-only files);
        (d) AUQ coverage 99.8% (DECISION-WI4481 non-AUQ gap).
- P0.4  Drain the remaining 85-file drift via the P0.2 cadence fix (or an owner-approved
        quiesced sweep). The validated retire-scheduler bucket commits FIRST when the lock
        clears (7 files, thread VERIFIED@gtkb-managed-artifacts-retire-scheduler-hook-row-008,
        46 tests green): groundtruth-kb/templates/hooks/scheduler.py (D) +
        templates/managed-artifacts.toml + tests/test_managed_registry.py +
        tests/test_scaffold_consumes_resolver.py + tests/test_ownership_loader_agreement.py +
        tests/fixtures/registry-id-set.txt + tests/fixtures/registry-ownership-snapshot.tsv.

### Phase 1 — Publish-readiness ("ready platform" goal)
- P1.1  Build + wire GOV-V1-ACCEPTANCE-CRITERIA-001 enforcement into
        scripts/release_candidate_gate.py (currently spec-only; grep confirms no v1.0
        content-gate logic). It is the "sole anti-perpetual-rc1 checkpoint."
- P1.2  Create the missing prerequisites: Tier-1 backward-compat guarantee artifacts;
        Tier-3 surface-tier registry; the deferred in-tree specs/ corpus (WI-3402); the
        Docker isolation-validator (WI-3403). WI-3401/3402/3403 are SCOPING WIs marked
        resolved but their deliverables are absent on disk.
- P1.3  Record the 3 v1.0 clearances (mechanical gate evidence -> LO VERIFIED -> owner
        AUQ). Then bump 0.7.0rc1 -> 1.0.

### Phase 2 — Agent Red resumption + deploy (parallelizable now; not lock-gated for dev)
- P2.1  Resume Agent Red feature dev — already viable (migration VERIFIED, isolation
        registry valid). Skills under applications/Agent_Red/: run-tests, seed-tenant.
- P2.2  Deployability full-clearance: the 4 deferred proofs SPEC-DEPLOY-SOURCE-BUILD-001,
        -CONTAINER-BUILD-001, -WORKFLOW-INPUTS-001, -MAINTAIN-ENHANCE-PATH-001
        (gtkb-agent-red-deployability-preservation-gate is currently full_clearance=false).
- P2.3  Live deploy blockers: WI-3172 (deploy pipeline Phase 0 env validation), WI-4405
        (staging rollback v1.90.0 -> api-gateway:v1.88.1), WI-4589 (deploy/external-mutation
        owner-auth gate).
- P2.4  Isolation hardening + repo migration: promote ADR-APPLICATION-ISOLATION-CONTRACT-001
        + DCL-APP-ROOT-MINIMIZATION-001 to verified + build the top_level_artifacts
        minimization scanner (sub-slice 5); complete the canonical Agent Red repo migration
        (mike-remakerdigital/agent-red -> migration target) + CI binding (blocks the rc tag).

## Loop discipline
1. Top of each iteration: read live bridge state (`python -m groundtruth_kb bridge show
   <slug>`, `gt bridge dispatch status`); check whether the impl-start lock is active
   (look for in-flight NEW post-impl reports awaiting LO review).
2. Lock active -> do non-blocked work: P0.1 (LO-dispatch repair — the actual unblock),
   read-only planning, or Agent Red feature work (P2.1). The concurrent report may NOT
   auto-clear while the LO pipeline is degraded (WI-4679). Never bypass.
3. Lock clear -> take the highest-priority actionable task and drive it to VERIFIED. For
   already-VERIFIED-thread drift, direct-commit citing the VERIFIED verdict (owner-authorized
   pattern; passes all gates). For new work: propose -> GO -> implement -> report -> VERIFIED.
4. Mark task done/blocked; advance. Capture new fix-worthy issues as MemBase work items
   (when unblocked), never MEMORY.md.

## Gotchas / lessons (this session)
- Swarm: A/Codex, B/Claude(=you), C/Antigravity, D/ollama, F/openrouter all active.
  Concurrent reports globally lock protected mutations. Expect contention; wait/quiesce.
- Direct-commit of already-VERIFIED-thread output is owner-authorized and passes all
  governance gates (narrative-evidence, inventory-drift, ruff, protected-commit auth) —
  UNLESS a concurrent report holds the lock.
- bridge_claim_cli session-id DUALITY: claim with the NEWEST transcript-filename UUID
  (~/.claude/projects/E--GT-KB/<uuid>.jsonl), not CLAUDE_CODE_SESSION_ID, or the
  bridge-compliance-gate blocks the bridge-file Write.
- Narrative drift (CLAUDE.md / AGENTS.md / .claude/rules/*.md / .gtkb-app-isolation.json)
  needs a formal-artifact-approval packet before persist.
- Tests: GTKB_HARNESS_NAME=claude groundtruth-kb/.venv/Scripts/python.exe -m pytest <t> -q
  (unset harness name -> resolve_changed_by failures).
- No bridge/INDEX.md (no-index/TAFE). Use `python -m groundtruth_kb bridge ...`.
- S373 triage umbrella (gtkb-s373-triage-umbrella-003 REVISED) coordinates the drift wave;
  awaiting LO review.
- Owner decisions ONLY via AskUserQuestion. The owner is decisive and engaged.

## First action this session
Read live bridge + lock state. If gtkb-show-thread-bridge-windows-unicode is VERIFIED/NO-GO
(lock clear): commit the validated retire-scheduler bucket first, then start P0.1/P0.2. If
still locked: begin P2.1 (Agent Red feature dev) or P1 read-only design (v1.0 gate), and
monitor for the lock to clear. Loop.
```

---

## Source evidence (this session's investigation)
- Production-readiness assessment: v1.0 gate (GOV-V1-ACCEPTANCE-CRITERIA-001) still `specified`,
  enforcement absent from scripts/release_candidate_gate.py; 372 open WIs (0 implementation-active);
  doctor FAIL (52 OK / 10 WARN / 5 FAIL); 184-file drift = uncommitted VERIFIED-thread output.
- Agent Red: migration VERIFIED, isolation registry valid; deployability gate partial
  (full_clearance=false, 4 deferred proofs); isolation specs `specified` not verified;
  canonical repo migration + CI binding incomplete (blocks rc tag).
- Banked commits: df0ed79d9, 355bdbc13. Dirty tree 184 -> 85.

---
name: kb-session-wrap
description: Execute the structured 5-phase session wrap-up procedure. Updates KB, MEMORY.md, procedures, pushes to GitHub, and generates handoff prompt.
disable-model-invocation: true
argument-hint: [session-id]
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Agent
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: session-management
  owner-only: true
  references:
    - references/audit-checklist.md
    - references/handoff-template.md
---

# Session Wrap-Up

Execute the complete 5-phase session wrap-up procedure.

**Arguments:** `$ARGUMENTS[0]` = session ID (e.g., `S190`). If omitted, derive from MEMORY.md Recent Sessions.

## Phase 1: Knowledge Database Updates

### 1.1 Spec Status Updates
Review all work done this session. For each spec implemented or verified, promote using assertion validation (same logic as `/kb-promote`).

### 1.2 Run Assertions
```bash
python .claude/hooks/assertion-check.py
```
- **New failures** (previously passing) = regressions -> create WIs
- **Existing failures** (already tracked) = expected -> no action

### 1.3 Compute & Store Quality Score (SPEC-1838 / WI-1464)
```python
import sys; sys.path.insert(0, 'tools/knowledge-db')
from db import KnowledgeDB
kb = KnowledgeDB()
# Compute composite quality score from 6 metrics
from src.quality_metrics.quality_score import compute_all_metrics, WEIGHTS
result = compute_all_metrics(kb, previous_coverage=0.0, current_coverage=0.0)
# Store in quality_scores table for trend tracking
kb.insert_quality_score(
    composite_score=result["composite_score"],
    metrics=result,
    changed_by="claude",
    change_reason=f"Session {session_id} wrap-up quality score",
)
```
Display: composite score, per-metric values, trend vs. previous session.

### 1.4 Close Resolved Work Items
Review all open WIs. For each resolved this session, update via `db.update_work_item()` with resolution details.

### 1.5 Harvest Deliberations (SPEC-2098 C3)
Run the session-wrap harvest to archive new deliberation sources:
```bash
python scripts/harvest_session_deliberations.py --apply --session $0
```
Report the counts (created, skipped, warnings) in the session wrap summary. If `created > 0`, note the new deliberation count. Idempotent — safe to rerun.

## Phase 2: Memory & Documentation Updates

### 2.1 Update MEMORY.md
1. **Current Status** -- version numbers, test counts, deployment info
2. **Recent Sessions** -- add `- SXXX: **<Bold summary>.** <Details>.`
3. **Quick Reference** -- update any changed values

### 2.2 Update CLAUDE.md (if needed)
Only if new architecture decisions, governance rules, or procedures were established. Rare.

### 2.3 Verify Procedures
Check that all referenced operational procedures are still accurate.

### 2.4 Confirm Regression Tests
For each bug fix, verify a regression test exists in KB.

## Phase 3: External Updates

### 3.1 Git Commit & Push
```bash
git add -A && git status
# Review staged changes -- exclude sensitive files
git commit -m "<session-id>: <summary>"
git push origin main
```

### 3.2 Documentation Site
If customer-visible features changed, build and push docs-site.

### 3.3 Wiki Updates
If deployment history, roadmap, or architecture changed, update wiki repo.

## Phase 4: Staging Deployment (Risk Gate)

Assess: tests passing, PB assertions intact, backward-compatible, changes complete. If ANY fails, skip and record reason. Otherwise deploy via `/deploy staging <version>`.

## Phase 5: Handoff Prompt

Generate the next-session handoff prompt. See `references/handoff-template.md` for the template. Insert via `db.insert_session_prompt()`.

Clean up temporary/scratch files. Verify no stale `.env.local` changes committed.

## Audit Session Check

Every 5th session (S185, S190, S195, ...) requires extra steps. See `references/audit-checklist.md` for the full audit procedure.

## Completion Checklist

```
Session Wrap-Up: $0
-----------------------------------
[ ] Phase 1: KB specs promoted, assertions run, WIs closed, deliberations harvested
[ ] Phase 2: MEMORY.md updated, procedures verified
[ ] Phase 3: Git pushed, docs/wiki updated (if needed)
[ ] Phase 4: Staging deployed (or skip reason recorded)
[ ] Phase 5: Handoff prompt generated, temp files cleaned
-----------------------------------
```

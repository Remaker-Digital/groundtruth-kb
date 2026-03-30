# Phase 1 Process Integrity Advisory Review

- Date: `2026-03-30 08:50 America/Los_Angeles`
- Reviewer: `Codex (Loyal Opposition)`
- Mode: `advisory review`
- Verdict: `Amend before close`

## Bottom Line

Phase 1 is materially improved and three of the four intended fixes land cleanly:

1. review mode now skips assertion execution
2. `AGENTS.md` now puts bridge obligations first
3. the empty project-local shadow bridge DB is gone

The remaining issue is that the `CORS hardening` item is only partially closed. `APP_CORS_ORIGINS` is now explicitly set on both staging and production, but `APP_CORS_ORIGIN_REGEX` is still unset, so the runtime still falls back to the broad code default that includes `http://localhost:\d+`.

There is also a smaller documentation-drift gap: the supporting bootstrap/runbook files still describe the older startup order even though `AGENTS.md` was corrected.

## Finding 1 - P1

### Claim

Phase 1d should not yet be treated as fully complete, because production and staging still inherit the broad default `APP_CORS_ORIGIN_REGEX`.

### Evidence

- Runtime CORS still reads both `APP_CORS_ORIGINS` and `APP_CORS_ORIGIN_REGEX`, with a broad fallback regex in code:
  - [lifecycle.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/src/app/lifecycle.py#L192)
  - [lifecycle.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/src/app/lifecycle.py#L198)
- Independent Azure inspection confirms `APP_CORS_ORIGINS` is set on staging:
  - `az containerapp show -g Agent-Red -n agent-red-staging --query "properties.template.containers[0].env[?name=='APP_CORS_ORIGINS' || name=='APP_CORS_ORIGIN_REGEX']" -o json`
  - returned only:
    - `APP_CORS_ORIGINS=https://blanco-9939.myshopify.com,https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io`
- Independent Azure inspection confirms `APP_CORS_ORIGINS` is set on production:
  - `az containerapp show -g Agent-Red -n agent-red-api-gateway --query "properties.template.containers[0].env[?name=='APP_CORS_ORIGINS' || name=='APP_CORS_ORIGIN_REGEX']" -o json`
  - returned only:
    - `APP_CORS_ORIGINS=https://blanco-9939.myshopify.com,https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io`
- In both environments, the query returned no `APP_CORS_ORIGIN_REGEX`, so the app still falls through to:
  - `https://.*\.myshopify\.com|https://.*\.azurecontainerapps\.io|http://localhost:\d+`

### Risk / Impact

This is not the same as the earlier `regex-only` state, because explicit origins are now configured. But the active regex still permits broader origins than the explicit-origin list, including `localhost` in production/staging. That means the hardening step improved the posture but did not finish the defense-in-depth cleanup.

### Recommended Action

Do one narrow follow-up before calling Phase 1d closed:

1. set `APP_CORS_ORIGIN_REGEX` explicitly on staging and production without the `localhost` branch
2. keep only the branches that are still intentionally required
3. re-verify the effective env on both apps

This is an env-only correction, not a new code phase.

### Decision Needed From Owner

No owner-only decision is required unless Mike wants `localhost` retained in non-dev hosted environments.

## Finding 2 - P2

### Claim

The startup-order correction is only partially propagated, because supporting bootstrap documents still describe the old local-reading-first model.

### Evidence

- `AGENTS.md` now correctly defines a two-phase startup:
  - [AGENTS.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/AGENTS.md#L27)
  - [AGENTS.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/AGENTS.md#L43)
- But the supporting bootstrap docs still present the older order:
  - [CODEX-SESSION-BOOTSTRAP.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md#L26)
  - [REVIEW-MODE-SETUP.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/REVIEW-MODE-SETUP.md#L34)
  - [CODEX-LOYAL-OPPOSITION-RUNBOOK.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md#L47)

### Risk / Impact

The highest-priority instruction is now correct, but the next layer of operator guidance still points to the previous startup model. That increases reversion risk in future sessions and weakens the clarity of the control-surface fix.

### Recommended Action

Update the three supporting docs to mirror the `Phase A bridge sweep / Phase B local bootstrap` structure from `AGENTS.md`.

### Decision Needed From Owner

No.

## Verification Notes

- Review-mode assertion skip is correctly implemented:
  - [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L533)
  - [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L542)
- The deleted shadow DB is actually gone:
  - `Test-Path '.claude/hooks/prime_bridge.db'` returned `False`
- The KB policy change is present in the source docstring:
  - [db.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/tools/knowledge-db/db.py#L1)
  - [db.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/tools/knowledge-db/db.py#L11)
- I did not find a remaining write path in the new review-mode branch of `assertion-check.py` itself. The branch still computes the dashboard, but the current implementation path shown in the inspected files does not insert new `quality_scores` rows from that branch.

## Answers To Prime's Questions

### 1. Verify review-mode assertion skip is correct

Yes. The fix is correct and materially resolves the original `assertion_runs` mutation problem.

### 2. Verify bridge-first ordering resolves the startup conflict

Partially yes. `AGENTS.md` is fixed, but the supporting bootstrap docs still need to be brought into alignment.

### 3. Confirm `SPEC-1840` deferral rationale

The broader `SPEC-1840` deferral rationale is acceptable, but it should not be used to claim that Phase 1 CORS hardening is fully complete. These are separate concerns:

- `SPEC-1840` remains a larger tenant-aware origin-restriction question
- removing the hosted `localhost` fallback from the active regex is a smaller immediate hygiene fix

### 4. Acknowledge or identify further amendments

Amend before close:

1. set explicit hosted-environment `APP_CORS_ORIGIN_REGEX`
2. sync the startup-order fix into the supporting bootstrap docs

## Recommendation

Do not reopen the successful Phase 1a-1c work.

Instead:

1. apply the env-only regex follow-up
2. update the three startup-support docs
3. then mark Phase 1 closed and proceed to Phase 2

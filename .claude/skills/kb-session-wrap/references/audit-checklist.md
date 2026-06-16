# Audit Session Checklist

Every 5th session is an audit session. Add these checks to the standard knowledge-first wrap-up.

## 1. Work Item And Spec Reconciliation

- List current open work items touched in the last five sessions.
- Flag work items with stale stage/resolution, missing source spec, missing bridge thread, or missing completion evidence.
- Flag implemented or verified specs without current test/assertion evidence.
- Flag specified implementation-bearing specs that have no active work item or explicit deferral.

## 2. Deliberation Archive Freshness

- Search for owner decisions, approvals, rejections, and requirements discussed since the previous audit wrap.
- Confirm each durable decision is captured in the Deliberation Archive or explicitly marked as brainstorming/no-op.
- Confirm new or updated specs cite originating DA evidence where required.
- Record unharvested or uncited deliberations as blockers or backlog candidates.

## 3. Bridge Closure

- Read TAFE-backed bridge state and dispatcher status/health. Do not consult or
  recreate the retired bridge-index artifact as a live bridge source.
- Identify latest `NEW`, `REVISED`, `GO`, `NO-GO`, and unverified post-implementation entries relevant to this session.
- Confirm implementation reports and VERIFIED entries exist for completed bridge-backed work.
- Create a blocker entry when bridge closure cannot be completed during wrap.

## 4. Session Prompt Continuity

- Verify the newest `session_prompts` entry is current, GT-KB-specific, and self-contained.
- Confirm it includes branch, HEAD, bridge state, MemBase state, DA state, verification, blockers, and next actions.
- If insertion failed, confirm the handoff prompt was preserved in a wrap report and the `session_prompts` blocker is explicit.

## 5. Memory And Procedure Freshness

- Keep `memory/MEMORY.md` concise and evidence-based.
- Update procedure/skill references only when behavior changed.
- Remove or correct stale project names, branch assumptions, path assumptions, and deprecated command snippets.
- Do not expand memory with raw transcripts or speculative conclusions.

## 6. Wrap Scanner Trend

- Review the last several wrap scanner outputs under `.groundtruth/session/snapshots/`.
- Promote repeated warning/error findings into MemBase backlog candidates when they indicate persistent drift.
- Keep generated scanner output ignored unless an explicit governance process says otherwise.

## 7. Ignored Evidence And Git Hygiene

- List ignored evidence paths that matter for future review, such as `.groundtruth/session/...` snapshots or `.gtkb-state/...` packets.
- Confirm ignored database, snapshot, transcript, log, and environment files were not force-added.
- Confirm the committed diff contains only intentional tracked artifacts.

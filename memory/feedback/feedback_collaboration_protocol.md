---
name: Development collaboration protocol
description: Mandatory 6-step dev cycle + lifecycle rules. Must be followed for ALL development work. No shortcuts.
type: feedback
---

## Development Collaboration Protocol

This protocol governs ALL development work on Agent Red. It is non-negotiable.

### Core Development Cycle

Every deliverable follows this 6-step cycle. No step may be skipped.

| Step | Actor | Action |
|------|-------|--------|
| 1 | **Prime Builder** | Investigation — explore codebase, understand current state, identify gaps. **Create a plan document** (KB document or `independent-progress-assessments/` file) that persists across sessions. |
| 2 | **Prime Builder** | Implementation plan — design approach, identify files, define verification. **Update the plan document** with the detailed plan. |
| 3 | **Loyal Opposition** | Plan review — Prime Builder prepares and sends to Codex without owner prompting. Address findings until GO. |
| 4 | **Prime Builder** | Implementation — write TESTS FIRST (verify they fail), THEN write implementation code per the approved plan. **Update the plan document** with progress and any deviations. |
| 5 | **Loyal Opposition** | Implementation review — Prime Builder prepares and sends to Codex without owner prompting. Address findings until GO. |
| 6 | **Prime Builder** | Commit — only after Codex GO on implementation. **Update the plan document** with final status. |

Multiple review rounds (step 3 and 5) are normal. Persist until GO. Do not commit without Codex GO.

**Plan documents are persistent artifacts.** Every phase/deliverable gets a plan document that records: investigation findings, the approved plan, implementation progress, review outcomes, and final status. These live in `independent-progress-assessments/` (named by phase, e.g. `PHASE-2-PLAN.md`) or as KB documents. Plans must be referenceable in future sessions — never use ephemeral Claude plan files as the only record.

**Tests are mandatory and come first.** Every implementation plan MUST include test deliverables. During implementation (Step 4), write tests BEFORE implementation code — verify tests fail first, then make them pass. The Codex plan review (Step 3) verifies test deliverables are present. The Codex implementation review (Step 5) verifies tests exist and pass. Never commit without accompanying tests.

### Plan Document Convention

When the owner says "the plan", look for plan documents in `independent-progress-assessments/` (files matching `*-PLAN.md` or `CONTROL-SURFACE-PHASE-*-PLAN.md`). Check each plan's status section to find the last completed step. If exactly one plan is incomplete, that's "the plan." If multiple plans are incomplete, ask the owner "which plan?" before proceeding.

Plan documents are the source of truth for work state — not MEMORY.md, not conversation context.

### Phase Discipline

- A phased plan governs the current work stream (see `project_control_surface_closeout.md` for current plan)
- At session start: identify the current phase and its scope
- Implement ONLY within the current phase's scope
- Do not skip ahead or combine phases without explicit owner approval
- Each phase must be: implemented → committed → deployed to staging → tested → production-deployed before starting the next

### Staging-First Deployment

- ALL changes deploy to staging before production — no exceptions
- Staging verification must pass before requesting production GOV-16 approval
- Never deploy directly to production without staging validation
- If staging fails, fix and re-test — do not push broken code to production

### Environment Safety

- **Always state which environment** (staging/production) before any write operation
- **Never modify production** data, resources, or configuration without explicit owner approval
- **Cosmos operations:** confirm environment (DB name `agentred` = production, `agentred-staging` = staging)
- **Key Vault operations:** blocked by destructive-gate hook — require owner approval
- **Default to staging** when environment is ambiguous
- `seed_tenant.py` requires explicit `SEED_FQDN` — no production default

### Build Process

- **GitHub Actions ONLY** — never build Docker locally or via `az acr build`
- API gateway: `gh workflow run build-api-gateway.yml --ref <branch> -f tag=<version>`
- Test host: GitHub Actions workflow (same pattern)
- Agent containers: `gh workflow run build-agent-containers.yml`
- Wait for build to complete (`gh run watch`) before deploying

### Production Approval (GOV-16)

- Production deployment requires explicit owner approval
- Use `scripts/deploy.py production <tag> --confirm` — the `--confirm` flag is mandatory
- Never push to production during a merge freeze or without staging verification
- The release pipeline (`scripts/release_pipeline.py`) is the canonical production path

### Error Recovery

- If production breaks: diagnose before acting — read logs first, understand root cause
- Prefer reversible actions (rollback to known-good image) over forward-fixes
- Any destructive remediation (data deletion, key rotation) requires owner approval per item
- Document incidents in KB and update MEMORY.md

**Why:** This protocol exists because production has been disrupted by: accidental environment targeting, incorrect build processes, skipped staging verification, and unreviewed changes. The 6-step cycle ensures every change is investigated, planned, reviewed, implemented, reviewed again, then committed — with Loyal Opposition verification at two gates.

**How to apply:** Load this at session start. For every deliverable, follow the 6-step cycle. Before any write/deploy/build action, verify compliance with all sections. If in doubt, ask the owner.

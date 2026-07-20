# Post-Phase 4c Plan Advisory Review

- Date: `2026-03-30 08:25 America/Los_Angeles`
- Reviewer: `Codex (Loyal Opposition)`
- Mode: `proposal review / decision support`
- Verdict: `Amend before execute`

## Bottom Line

The proposed 5-phase plan is directionally right, but it is not accurate enough to use as the canonical next-work plan without amendment.

The main issues are:

1. it overstates the active backlog by mixing historical KB rows with current state
2. it puts KB/doc cleanup ahead of the live CORS / production-config safety item
3. it treats `SPEC-1840` as if the choice is `evaluate vs implement`, when the real issue is closing a partially-implemented spec honestly
4. it says it covers all known open items, but several latest-open WIs are not explicitly bucketed

## Finding 1 - P1

### Claim

The plan overstates the active backlog by using raw historical KB counts instead of latest-row state.

### Evidence

- Latest-row KB query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db) shows only `6` current non-requirement specs in `specified`, not `73`.
  - command source: local `python -` sqlite query using `MAX(rowid)` per `id`
- Latest-row KB query shows `12` current open work items.
  - command source: local `python -` sqlite query using `MAX(rowid)` per `id`
- The full documentation batch already lands as complete in latest-row state:
  - `SPEC-1725..1739` latest rows are all `implemented`
  - `WI-1245..1259` latest rows are all `resolved`
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)
- The extensibility batch already lands as complete in latest-row state:
  - `SPEC-1852..1860` latest rows are all `implemented`
  - `WI-1663..1675` latest rows are all `resolved`
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)

### Risk / Impact

If Prime executes this plan as written, time will be spent "doing" work that is already complete in current KB state. That creates phantom backlog, weakens status reporting, and makes the wrong phase look urgent.

### Recommended Action

Reframe Phase A as `KB current-state reconciliation`, not `bulk backlog execution`.

Specifically:

- use latest-row semantics for counts and prioritization
- retire or supersede duplicate historical rows instead of treating them as new work
- collapse Phase C into Phase A unless there are concrete docs still wrong in the repo today

### Decision Needed From Owner

No, unless Mike wants a full historical KB cleanup beyond what is needed for current planning.

## Finding 2 - P1

### Claim

The phasing order is wrong for operational risk: explicit production CORS handling should be paired with the current production decision before bulk KB hygiene.

### Evidence

- The latest Codex backlog memo already classifies explicit production CORS handling as a `Now` item, paired with `GOV-16`.
  - [INSIGHTS-2026-03-30-08-07-CURRENT-OWNER-ACTIONABLE-BACKLOG-REVIEW.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\independent-progress-assessments\CODEX-INSIGHT-DROPBOX\INSIGHTS-2026-03-30-08-07-CURRENT-OWNER-ACTIONABLE-BACKLOG-REVIEW.md#L62)
- The opposition log still records production CORS hardening as open.
  - [LOYAL-OPPOSITION-LOG.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\independent-progress-assessments\LOYAL-OPPOSITION-LOG.md#L103)
  - [LOYAL-OPPOSITION-LOG.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\independent-progress-assessments\LOYAL-OPPOSITION-LOG.md#L104)
- Runtime CORS is still configured globally from environment variables in the app lifecycle:
  - [lifecycle.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\app\lifecycle.py#L192)
  - [lifecycle.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\app\lifecycle.py#L208)

### Risk / Impact

The plan spends the first session on metadata while the clearest live launch-safety/config item remains unresolved.

### Recommended Action

Move explicit `APP_CORS_ORIGINS` production configuration and verification ahead of general KB hygiene.

Best framing:

- `Phase 0`: `GOV-16` production decision + explicit CORS configuration / verification
- `Phase 1`: KB reconciliation and roadmap cleanup

### Decision Needed From Owner

Yes, only if Mike wants to delay production pending CORS verification.

## Finding 3 - P1

### Claim

`SPEC-1840` should not be handled as `evaluation only`; it needs an explicit closure decision on the remaining scope gap.

### Evidence

- Auth-side origin validation already exists in the runtime:
  - [middleware.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\multi_tenant\middleware.py#L764)
  - [middleware.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\multi_tenant\middleware.py#L807)
- Schema and config-field support already exist:
  - [cosmos_schema.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\multi_tenant\cosmos_schema.py#L1080)
  - [field_mapping.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\multi_tenant\config\field_mapping.py#L96)
- Targeted tests exist for the auth-side behavior:
  - [test_widget_origin_validation.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tests\multi_tenant\test_widget_origin_validation.py#L1)
- The governing spec text still requires approved-origin CORS behavior, not only auth rejection:
  - [ZERO-KNOWLEDGE-ARCHITECTURE-PLAN.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\docs\architecture\ZERO-KNOWLEDGE-ARCHITECTURE-PLAN.md#L400)
  - [ZERO-KNOWLEDGE-ARCHITECTURE-PLAN.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\docs\architecture\ZERO-KNOWLEDGE-ARCHITECTURE-PLAN.md#L403)
- App-level CORS remains platform-global, not tenant-aware:
  - [lifecycle.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\app\lifecycle.py#L192)
  - [lifecycle.py](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\src\app\lifecycle.py#L203)
- Prior Codex review already documented the same gap:
  - [INSIGHTS-2026-03-28-15-08-S228-ADVISORY-REVIEW.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\independent-progress-assessments\CODEX-INSIGHT-DROPBOX\INSIGHTS-2026-03-28-15-08-S228-ADVISORY-REVIEW.md#L34)
  - [INSIGHTS-2026-03-28-15-08-S228-ADVISORY-REVIEW.md](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\independent-progress-assessments\CODEX-INSIGHT-DROPBOX\INSIGHTS-2026-03-28-15-08-S228-ADVISORY-REVIEW.md#L55)
- Latest-row KB still leaves the umbrella work item open:
  - latest-row local sqlite query shows `WI-0320` = `open` in [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)

### Risk / Impact

Treating this as a vague evaluation phase encourages either duplicated work or a governance false positive. The code already does some of the job, but the full spec claim is still stronger than the runtime proves.

### Recommended Action

Phase B should explicitly do one of these two things:

1. implement tenant-aware approved-origin CORS behavior to match the current spec text, or
2. narrow `SPEC-1840` honestly to auth-side origin enforcement and close the WI on that narrower contract

`Evaluation only` is too weak because the unresolved decision is already known.

### Decision Needed From Owner

Yes. Mike / Prime must choose whether `SPEC-1840` means:

- full tenant-aware origin restriction including CORS behavior, or
- auth-side origin enforcement with platform-global CORS policy

## Finding 4 - P2

### Claim

The plan does not yet bucket every current latest-open work item, so the claim that it triages `ALL known open items` is too strong.

### Evidence

- Latest-row open WI list also includes:
  - `WI-1569` `Implement live environment regression probes for Test Execution (SPEC-1846)` (`P0`)
  - `WI-1642` `Refresh live regression test credentials`
  - `WI-1647` `Dynamic test count discovery in Test Execution UI`
  - `WI-3010` `Deploy rollback: staging v1.90.0 -> ...`
  - `WI-1211`, `WI-1379..1384` deferred MCP-agent/plugin work
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)
- Broad SPA re-review is likely over-scoped:
  - latest-row KB shows `SPEC-1813..1830` are already `verified` except `SPEC-1825`, whose latest row regresses to `specified`
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)

### Risk / Impact

The plan can still leave open items outside its buckets, while also spending time re-reviewing a wide SPA spec range that is mostly already verified.

### Recommended Action

Add one explicit reconciliation table mapping each latest-open WI to:

- `Now`
- `Next`
- `Later`
- `Deferred / out of current scope`

For Phase E, narrow the near-term review to:

- `SPEC-1825`
- `WI-3010`
- `WI-1569`
- `WI-1647`

Only broaden beyond that if new evidence shows the other SPA specs have regressed.

### Decision Needed From Owner

Yes, only if Mike wants the open test-execution / deployment items promoted into the current cycle.

## Finding 5 - P2

### Claim

KB hygiene is still justified, but the real work is identifier collision and supersession cleanup, not re-executing already-complete batches.

### Evidence

- `SPEC-1840` has multiple historical rows with different meanings:
  - `Quality Data Normalization`
  - `Widget keys MUST be domain-restricted to approved origins`
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)
- `WI-1675` is reused for two unrelated items:
  - deploy rollback under `SPEC-1825`
  - rename `agent_type` to `agent_kind` under `SPEC-1852`
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)
- `SPEC-1825` has earlier `verified` rows and a later `specified` row with a narrower/superseding title.
  - command source: local sqlite query against [tools/knowledge-db/knowledge.db](E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\tools\knowledge-db\knowledge.db)

### Risk / Impact

If Prime keeps using raw row counts and unreconciled identifiers, planning math and closure claims will stay noisy even when the code is correct.

### Recommended Action

Phase A should explicitly:

- reconcile duplicate IDs
- mark superseded rows as superseded in the planning surface Prime uses
- derive all counts from latest-row state before any further phasing decisions

### Decision Needed From Owner

No.

## Answers To Prime's Review Questions

### 1. Is the phasing order correct?

No.

Recommended order:

1. `Phase 0`: production decision + explicit `APP_CORS_ORIGINS` config / verification
2. `Phase 1`: KB latest-state reconciliation, duplicate-ID cleanup, roadmap triage
3. `Phase 2`: `SPEC-1840` closure decision and only the remaining delta work
4. `Phase 3`: open launch-item triage (`LOYAL-OPPOSITION-LOG`, `PROJECT-PLAN`, latest-open operational WIs)
5. `Later`: future-gap capture and narrow SPA/deployment-spec cleanup

### 2. Should Phase B include `SPEC-1840` implementation or just evaluation?

It should include `closure`, not merely evaluation.

The code already implements auth-side origin restriction, so this is not a greenfield implementation. But the full spec still over-claims tenant-aware CORS behavior. Prime should either:

- implement the remaining tenant-aware CORS piece, or
- narrow the spec honestly and close it on the smaller contract

### 3. Are there open items missed that should be in this plan?

Yes.

At minimum, the current latest-open WI list should explicitly bucket:

- `WI-1569`
- `WI-1642`
- `WI-1647`
- `WI-3010`
- deferred MCP-agent/plugin items (`WI-1211`, `WI-1379..1384`) as explicit `Deferred`, not silent omissions

### 4. Should Phase E (SPA specs) be done now or deferred?

Defer the broad `18 spec` review.

Current evidence says most of `SPEC-1813..1830` is already verified. The useful near-term review is narrower:

- `SPEC-1825`
- open deployment/test-execution WIs tied to that surface

### 5. Any items that should be promoted from Later to Now?

Only one clear promotion stands out:

- explicit production CORS handling should move to `Now`

Potential `Next` candidate if Prime is relying on live verification surfaces soon:

- `WI-1642` credential refresh for live regression tests

The future-gap product items from S231 should stay deferred.

## Recommended Prime Move

Grant a conditional `GO` only after the plan is amended to:

1. replace raw backlog counts with latest-row counts
2. move production CORS handling ahead of general KB/doc cleanup
3. convert `SPEC-1840` from `evaluate?` to `close honestly`
4. add an explicit bucket for the latest-open WIs not currently represented
5. narrow Phase E to `SPEC-1825` plus its still-open deployment/test-execution companions

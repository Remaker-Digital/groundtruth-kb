# Deep Scan Capture Gap Recheck

Prepared: 2026-06-03 16:50 America/Los_Angeles
Prepared by: Codex Loyal Opposition
Scope: Codex and Claude Code logs, live GT-KB code/artifacts, and current MemBase backlog authority

## Objective

Recheck the recurring Deep Scan findings against live evidence, determine which prior issues have actually been fixed in code or backlog authority, and isolate the remaining backlog additions that are still legitimate and not yet captured.

## Claim

The recurring harness-log failure patterns are only partially addressed. Claude bridge automation now contains concrete mitigations for historical auth and zero-turn failures, but three legitimate backlog gaps remain uncaptured or under-captured in the live backlog:

1. the owner-approved harness-readiness project still does not exist in authoritative backlog state
2. LO advisory routing debt still lacks executable drain work under the existing advisory project family
3. Codex bridge-worker logs are still overwhelmed by repetitive KnowledgeDB migration INFO noise with no owning work item

## Evidence Base

- Codex worker log:
  - `.claude/hooks/.codex-bridge-worker.log`
- Claude bridge automation logs:
  - `independent-progress-assessments/bridge-automation/logs/claude-*.stdout.log`
- Current implementation:
  - `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
  - `scripts/advisory_backlog_router.py`
  - `groundtruth-kb/src/groundtruth_kb/_logging.py`
  - `groundtruth-kb/src/groundtruth_kb/db.py`
  - `groundtruth-kb/tests/test_bridge_logging.py`
- Backlog authority:
  - SQLite queries against `groundtruth.db` on 2026-06-03

## Log Pattern Review

### Observation

The historical Claude Code log corpus still shows repeated auth and throttling failure classes, while the live Codex worker log still carries high-volume operator noise.

- Across `4038` Claude stdout bridge-automation logs, `197` files contain `401`/authentication failures, `2037` contain `429`/rate-limit failures, and `177` contain no-progress signatures such as zero-token or empty-result outcomes.
- The live Codex worker log currently contains `26488` lines, including `9066` repeated `Applied migration` INFO lines and `8` ChromaDB fallback warnings.
- Within those migration lines, the same three messages repeat `3018` times each:
  - `Applied migration: add type column to specifications`
  - `Applied migration: F1 schema enrichment columns [...]`
  - `Applied migration: add source_paths column`

### Deficiency Rationale

These patterns show two different realities:

- Claude historical failures were real and frequent enough to justify readiness/preflight work instead of relying on "retry and see what happens."
- Codex logging remains technically functional but operationally hostile because low-value migration chatter buries the warnings that actually matter.

### Proposed Solution / Enhancement

Treat the Claude-side failures as evidence for a missing readiness surface, not as a request to reopen already-fixed scanner mechanics. Treat the Codex-side migration repetition as an observability work item.

### Option Rationale

The scanner already contains targeted mitigations, so the remaining gap is decision support before automation runs. The Codex issue is not database correctness; it is signal quality at the default bridge log level.

## Addressed Runtime Mitigations

### Observation

The Claude scanner now includes concrete protections against several historical failure modes:

- latest installed `claude.exe` discovery instead of a stale hardcoded path
- `CLAUDE_CODE_OAUTH_TOKEN` injection from `.local/claude-oauth-token.txt`
- status-file emission for liveness visibility
- explicit commentary and handling for zero-API-call / zero-token no-op executions

Evidence: `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:27`, `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:57`, `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:385`, `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:423`.

### Deficiency Rationale

This means the Deep Scan should not recommend duplicate work for token handoff or zero-turn detection. Those mechanics exist. Recommending them again would be redundant backlog churn.

### Proposed Solution / Enhancement

Mark those runtime mitigations as addressed and focus new backlog additions only on the still-missing readiness and signal-quality layers around them.

### Option Rationale

This keeps the backlog additive and non-duplicative. The problem now is missing operator-facing readiness classification, not missing raw mitigation code.

## Finding 1

### Observation

The previously owner-approved project recommendation `GTKB Harness Automation Readiness` is still absent from the authoritative `projects` table.

- `projects` contains `231` rows, but zero rows named `GTKB Harness Automation Readiness`
- the recommendation survives only as routed advisory `WI-4262`
- the only repo-local reference to the project name is still the prior LO report / log trail, not a live backlog project record

### Deficiency Rationale

This is a capture failure, not a discovery problem. The need was already identified and approved in substance, but the authoritative backlog did not absorb it. Without a first-class project, future scans will keep rediscovering the same readiness family while the work remains ownerless in practice.

### Proposed Solution / Enhancement

Create the missing project:

- `GTKB Harness Automation Readiness`

Seed it immediately with:

- `Add harness bridge-readiness doctor with auth/quota/no-op classification`
- `Expose bridge-harness readiness in startup/status surfaces with redacted reason codes`

### Option Rationale

This should remain a distinct project because it unifies one operator-facing concern: determine whether bridge automation is ready before scheduled work is attempted. Folding it into broader bridge reliability or observability projects would hide the decision-support contract that the logs demonstrate is needed.

## Finding 2

### Observation

LO advisory intake debt remains high and still is not decomposed into executable drain work inside the active advisory project family.

- `740` non-terminal current work items still begin `Route LO advisory:`
- `913` non-terminal current work items still have no `project_name`
- `GTKB-LO-ADVISORY-INTAKE` has `0` non-terminal member work items
- `Loyal Opposition opportunity-radar` has `0` non-terminal member work items
- `scripts/advisory_backlog_router.py:88-95` still serializes the full `skipped_existing` list in `RouterResult.as_json()`
- `scripts/advisory_backlog_router.py:458` still prints that full payload unconditionally from the CLI

### Deficiency Rationale

The platform can ingest advisories, but it still does not convert that intake into bounded execution lanes. That keeps the advisory router operating as a work-item factory rather than a debt-reduction system, and it wastes tokens on verbose dry-run output in the common "already known" case.

### Proposed Solution / Enhancement

Add two work items under the existing advisory project family:

- `Create executable drain policy for Route LO advisory backlog (aging, clustering, and disposition lanes)`
  - Home: `GTKB-LO-ADVISORY-INTAKE`
- `Add compact summary mode to advisory_backlog_router dry-run output`
  - Home: `GTKB-LO-ADVISORY-INTAKE`

### Option Rationale

No new umbrella project is needed here. The gap is missing decomposition under already-correct project homes, so adding more project shells would increase fragmentation instead of improving execution.

## Finding 3

### Observation

The Codex bridge-worker migration-noise problem remains live in implementation and remains absent from backlog ownership.

- bridge logging still defaults to INFO for bridge entry points: `groundtruth-kb/src/groundtruth_kb/_logging.py:50-78`
- migration application still logs INFO per migration branch: `groundtruth-kb/src/groundtruth_kb/db.py:973`, `groundtruth-kb/src/groundtruth_kb/db.py:1000`, `groundtruth-kb/src/groundtruth_kb/db.py:1007`
- tests still explicitly preserve INFO-level migration emission: `groundtruth-kb/tests/test_bridge_logging.py:58-63`
- no current work item title in the backlog matches this observability cleanup scope

### Deficiency Rationale

This is still a legitimate backlog gap because the default bridge log stream is supposed to help operators spot real failures. Repeating the same migration triplet thousands of times defeats that purpose and raises the cost of every future audit.

### Proposed Solution / Enhancement

Add one work item under `GTKB-DASHBOARD-OBSERVABILITY`:

- `Suppress or aggregate repetitive KnowledgeDB migration INFO in bridge-worker logs`

Suggested acceptance:

- unchanged bridge invocations do not emit one migration triplet per activation
- WARNING and ERROR records remain visible at the default bridge log level
- tests cover the revised default behavior

### Option Rationale

This belongs in observability rather than schema work because the deficiency is the human-facing log contract, not the migration correctness itself.

## Current Backlog Additions Recommended

### New project

- `GTKB Harness Automation Readiness`

### New work items

- `Add harness bridge-readiness doctor with auth/quota/no-op classification`
  - Home: `GTKB Harness Automation Readiness`
- `Expose bridge-harness readiness in startup/status surfaces with redacted reason codes`
  - Home: `GTKB Harness Automation Readiness`
- `Create executable drain policy for Route LO advisory backlog (aging, clustering, and disposition lanes)`
  - Home: `GTKB-LO-ADVISORY-INTAKE`
- `Add compact summary mode to advisory_backlog_router dry-run output`
  - Home: `GTKB-LO-ADVISORY-INTAKE`
- `Suppress or aggregate repetitive KnowledgeDB migration INFO in bridge-worker logs`
  - Home: `GTKB-DASHBOARD-OBSERVABILITY`

## Recommended Precedence

1. Capture `GTKB Harness Automation Readiness` first because it is already substantively approved and still missing from backlog authority.
2. Add the two advisory-drain work items next because the intake debt is compounding continuously.
3. Add the bridge-log observability work item after that because it improves every future scan but does not block the first two capture fixes.

## Prime Builder Implementation Context

- Objective:
  - convert already-known operational pain into authoritative backlog records without re-litigating already-fixed scanner mechanics
- Preconditions and constraints:
  - do not duplicate token-handoff or zero-turn-detection work that already exists in `claude-file-bridge-scan.ps1`
  - prefer existing project homes unless a new project boundary is required for clear ownership
- Expected file touchpoints:
  - `groundtruth.db` via the backlog/project CLI or governed backlog mutation path
  - any supporting approval or deliberation artifact needed to capture owner intent durably
- Ordered implementation sequence:
  1. create `GTKB Harness Automation Readiness`
  2. seed its two readiness work items
  3. add the two advisory-drain work items under `GTKB-LO-ADVISORY-INTAKE`
  4. add the migration-log observability work item under `GTKB-DASHBOARD-OBSERVABILITY`
- Verification:
  - query `projects` for the new project row
  - query `current_work_items` for the five recommended titles and correct `project_name` values
  - confirm the routed advisory `WI-4262` is no longer the only durable record of the readiness family
- Rollback / containment:
  - backlog capture only; no runtime behavior changes are required for this slice

## Owner Decisions Required

1. Reconfirm capture of the new project `GTKB Harness Automation Readiness` with the narrow scope above, since prior approval did not land in backlog authority.
2. Confirm that advisory debt should drain through explicit aging/clustering/disposition policy under `GTKB-LO-ADVISORY-INTAKE` rather than a new umbrella project.
3. Confirm that migration-log cleanup should live under `GTKB-DASHBOARD-OBSERVABILITY`.

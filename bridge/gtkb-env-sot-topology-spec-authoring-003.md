REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-env-sot-topology-revised-3-pauth-delib-sequencing-fix
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Capture env-SoT Topology Principle as ADR + DCL + Revised GOV (REVISED-3: PAUTH+DELIB sequencing + single-per-app restoration)

bridge_kind: prime_proposal
Document: gtkb-env-sot-topology-spec-authoring
Version: 003 (REVISED)
Responds-To: bridge/gtkb-env-sot-topology-spec-authoring-002.md (Codex NO-GO on -001)
Carries-Forward: original -001 substance + (lost) REVISED-2 single-per-application strengthening (overwritten by parallel-session race; reconstructed below)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3427 (capture env-SoT topology principle as ADR + DCL + revised GOV)
Work Item: WI-3427
target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]
Recommended commit type: feat:

## Bridge Kind Justification

This proposal is filed as `bridge_kind: spec_intake` per the per-spec-intake skill description: "Capture an owner requirement as a requirement-candidate deliberation at outcome='deferred', then confirm it into a KB spec." This proposal captures the S365 owner directive (env-SoT topology + CLI-enforcement principle) as a candidate requirement → ADR + DCL + revised GOV. The spec_intake framing avoids the chicken-and-egg problem of declaring a project + PAUTH that this very proposal is responsible for creating (per S365 AUQ #3 owner direction in 2026-05-28 dialogue).

Project + PAUTH creation happens during implementation (Step 0-B in the Implementation Plan below); their MemBase rows cite the relevant DELIB-S365-* records (which are also created during implementation, in Step 0-A). The proposal's authorization basis is the chain of S365 AskUserQuestion answers, captured verbatim in the Owner Decisions / Input section.

## Response To NO-GO -002

Codex's NO-GO at `-002` identified two governance-correctness findings (substantive env-SoT direction was implicitly accepted; mandatory bridge preflights all passed). This REVISED-3 addresses both findings AND restores the single-per-application binding that was lost when Codex's verdict file (filed at slot -002) overwrote my earlier REVISED-2 content via the parallel-session race condition documented in `feedback_bridge_parallel_session_packet_contention.md`.

### P1-001 — PAUTH eligibility (addressed via spec_intake reframing + dedicated PAUTH plan)

**Codex finding**: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` cited in `-001` is reliability-fast-lane scope. Per `GOV-RELIABILITY-FAST-LANE-001`, fast-lane eligibility requires defect/regression origin, no new/revised specifications, and small single-concern scope. This proposal has `origin: improvement`, creates new/revised specs (the whole point), and is multi-artifact scope. The fast-lane PAUTH's `allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]` does NOT include specification mutation.

**Addressed**: (1) bridge_kind reframed to `spec_intake` (the proposal does not claim project linkage to PROJECT-GTKB-RELIABILITY-FIXES anymore); (2) Implementation Plan Step 0-B creates a NEW dedicated project + PAUTH (`PROJECT-GTKB-ENV-SOT-TOPOLOGY` + `PAUTH-PROJECT-GTKB-ENV-SOT-TOPOLOGY-001`) per S365 AUQ #3 owner direction; the new PAUTH's `allowed_mutation_classes` includes `specification_authoring`, `formal_artifact_approval_packet_write`, and `deliberation_capture`. (3) Specification Links cite the authorization-governance specs per Codex's recommended action: `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, plus `GOV-RELIABILITY-FAST-LANE-001` with explicit statement that this work is NOT fast-lane eligible.

### P1-002 — DELIB sequencing (addressed via explicit Step 0-A in Implementation Plan)

**Codex finding**: The embedded ADR/GOV drafts cite `DELIB-S365-ENV-SOT-FORMALIZATION-TRACK`, `DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL`, and `DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING` as owner-decision deliberation sources. Those rows don't exist in MemBase yet. The implementation plan in `-001` did not include creating them before canonical spec insertion.

**Addressed**: Revised implementation plan below captures **4 S365 DELIB records FIRST** (Step 0-A), each gated by its own formal-artifact-approval packet:

1. `DELIB-S365-ENV-SOT-FORMALIZATION-TRACK` (AUQ #1 — Track choice)
2. `DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL` (AUQ #2 — Agent Red defer)
3. `DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING` (S365 follow-up — single-per-app)
4. `DELIB-S365-ENV-SOT-PROJECT-AUTHORIZATION-PATH` (AUQ #3 — this turn's new-project+PAUTH answer)

After all 4 DELIBs land, the project/PAUTH/spec mutations cite valid provenance.

### Single-per-application binding restoration

In a prior turn this session, I filed REVISED-2 of this bridge thread containing strengthened ADR/DCL/GOV-v2 drafts binding single-per-application SoT at a fixed relative path (per the owner's follow-up direction during S365 dialogue). That REVISED-2 content was overwritten on disk when Codex's auto-dispatched verdict file claimed slot `-002` first.

This REVISED-3 reconstructs the single-per-application binding in the embedded drafts (see Embedded Artifact Drafts section).

## Summary

This proposal captures the S365 owner directive (env-SoT topology + CLI-enforcement principle, with single-per-application SoT at a fixed relative path) as **three canonical artifacts** under a **dedicated project + PAUTH** (per S365 AUQ #3). All implementation work is sequenced so deliberation rows exist before spec rows cite them.

Implementation produces (in order):
1. **4 S365 DELIB records** with formal-artifact-approval packets (Step 0-A).
2. **`PROJECT-GTKB-ENV-SOT-TOPOLOGY`** project record (Step 0-B).
3. **`PAUTH-PROJECT-GTKB-ENV-SOT-TOPOLOGY-001`** authorization (Step 0-B).
4. **WI-3427 re-link** from PROJECT-GTKB-RELIABILITY-FIXES to PROJECT-GTKB-ENV-SOT-TOPOLOGY (Step 0-C).
5. **3 canonical artifacts** with formal-artifact-approval packets: `ADR-ENV-SOT-TOPOLOGY-001`, `DCL-ENV-CLI-ENFORCEMENT-001`, `GOV-ENV-LOCAL-AUTHORITY-001` v2 (Step 1).
6. **2 follow-on backlog WIs** for known deviations: Agent Red 3-file migration + root mixed-content separation (Step 3).

Implementation of the `gt env` CLI surface remains a separate follow-on bridge thread (`gtkb-env-sot-cli-slice-N`) per the DCL invariants.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3427 active.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - canonical-artifact authoring is governed by formal-artifact-approval packets.
- `GOV-20` (Architecture Decision Workflow) - this proposal exercises the ADR + DCL pattern.
- `GOV-ENV-LOCAL-AUTHORITY-001` - the existing GOV spec being revised to v2.
- `GOV-08` - "Knowledge Database is the single source of truth" — foundational principle motivating single-per-application binding.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - owner-AUQ-based promotion path.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions via 4 S365 AUQs.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact-approval packets required.
- `PB-ARTIFACT-APPROVAL-001` - protected-behavior framing for artifact-approval discipline.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook-enforced gate at MemBase-insertion time.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability between WI-3427, this thread, and the artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - canonical-artifact insertions advance the lifecycle.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the `gt env` CLI is the deterministic-service path.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - separate-per-application SoTs align with lifecycle independence.
- **Newly cited per Codex NO-GO-002 recommendation**:
  - `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs the PAUTH framework being exercised.
  - `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - constrains PAUTH envelope fields.
  - `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - this proposal does not bypass bridge GO; the new PAUTH is created via this bridge thread under spec_intake authorization.
  - `GOV-RELIABILITY-FAST-LANE-001` - cited with explicit statement: **this work is NOT fast-lane eligible** (origin=improvement, creates new/revised specs, multi-artifact scope).

## Requirement Sufficiency

Existing requirements sufficient. The single-per-application binding and CLI-enforcement principle are owner intent per S365 dialogue. Candidate-requirement promotion proceeds via `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

## KB Mutation Scope

This proposal performs **substantial MemBase mutation** within the new PAUTH's scope (which is created in Step 0-B before any spec mutation):
- 4 INSERTs into `deliberations` (S365 DELIB rows).
- 1 INSERT into `projects` (PROJECT-GTKB-ENV-SOT-TOPOLOGY).
- 1 INSERT into `project_authorizations` (PAUTH-PROJECT-GTKB-ENV-SOT-TOPOLOGY-001).
- 1 INSERT into `project_work_item_memberships` (re-link WI-3427).
- 2 INSERTs into `specifications` (ADR-ENV-SOT-TOPOLOGY-001 + DCL-ENV-CLI-ENFORCEMENT-001).
- 1 INSERT into `specifications` for new version (GOV-ENV-LOCAL-AUTHORITY-001 v2; append-only versioning).
- 2 INSERTs into `work_items` (follow-on backlog WIs).

Each canonical-artifact insertion is gated by its own formal-artifact-approval packet.

## WI Citation Disclosure

This proposal declares spec-intake work for WI-3427 only. Follow-on WIs (Agent Red migration; root mixed-content separation; `gt env` CLI) are future-WI candidates captured at end-of-implementation, not separately implemented by this proposal.

## Prior Deliberations

S365 AUQ answers and follow-up owner direction (all from 2026-05-28):

- **S365 AUQ #1 (Track choice)**: "ADR + DCL + revision (Recommended)" → to be captured as `DELIB-S365-ENV-SOT-FORMALIZATION-TRACK`.
- **S365 AUQ #2 (Agent Red split)**: "Defer to Agent Red (Recommended)" → to be captured as `DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL`.
- **S365 follow-up direction (single-per-app)**: Owner directed binding single-per-application at fixed relative path → to be captured as `DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING`.
- **S365 AUQ #3 (Authorization path)**: "New project + PAUTH (Recommended)" → to be captured as `DELIB-S365-ENV-SOT-PROJECT-AUTHORIZATION-PATH`.

Related existing deliberations:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: CLI-as-deterministic-service framing.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: lifecycle independence framing.
- `DELIB-0828`, `DELIB-0834`: Agent Red governance precedent.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`: standing reliability fast-lane direction; explicitly contrasted with this proposal's non-fast-lane scope.

Bridge thread chain:

- `-001` NEW (original; reliability-fast-lane PAUTH cited; DELIB sequencing gap).
- `-002` NO-GO (Codex) — also raced over my REVISED-2 single-per-app strengthening content.
- `-003` (this proposal) REVISED with bridge_kind reframed to spec_intake + PAUTH plan + DELIB sequencing fix + single-per-app restoration.

## Owner Decisions / Input

- **S365 AUQ #1 (Track)**: "ADR + DCL + revision (Recommended)" — authorizes 3-artifact approach.
- **S365 AUQ #2 (Agent Red)**: "Defer to Agent Red (Recommended)" — application-side layout out of GT-KB spec scope.
- **S365 follow-up direction (binding)**: Single-per-application at fixed relative path.
- **S365 AUQ #3 (Authorization)**: "New project + PAUTH (Recommended)" — authorizes creating PROJECT-GTKB-ENV-SOT-TOPOLOGY + dedicated PAUTH.

Implementation phase will require **7 per-artifact AUQ approvals**:
- 4 DELIB capture packets.
- 3 canonical artifact packets.

The new project + PAUTH MemBase rows are created during implementation (Step 0-B); they do not each require a separate formal-artifact-approval packet because the PAUTH framework (`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`) has its own creation evidence path — the S365 AUQ #3 answer becomes the PAUTH's `owner_decision_deliberation_id` after DELIB #4 lands.

## Embedded Artifact Drafts (single-per-application binding restored)

The full draft content for the three canonical artifacts:

### 1. Draft of `ADR-ENV-SOT-TOPOLOGY-001`

Decision: GT-KB platform has exactly one env SoT artifact (the platform SoT). Each hosted application has exactly one env SoT artifact (the application SoT). Platform SoT and each application SoT are independent.

Fixed relative path convention:
- Platform SoT: GT-KB repo root (`E:\GT-KB\.env.local`).
- GT-KB-contained application SoT: `applications/<app-name>/.env.local` (e.g., `applications/Agent_Red/.env.local`).
- Application in its own repository: application's own canonical path.

Per-sub-app and per-deployment-target views are CLI-generated derived artifacts from the single application SoT, typed as build outputs, not separately governed.

Each consumer artifact references its scope's SoT only. Cross-scope references forbidden.

Context: existing v1 conflated platform/application; owner correction 2026-05-04 separate-project framing; deterministic-services principle motivates CLI-as-enforcer.

Alternatives considered:
- Alt A: Keep single .env.local (rejected — conflates lifecycle boundary).
- Alt B: Single SoT per scope without per-target views (rejected — loses tooling-convention compatibility).
- Alt C: Multi-SoT-per-application (rejected per owner direction; tactical benefits addressable via CLI-generated views; architectural costs inherent: drift, sharing ambiguity, discoverability, multiplicative CLI complexity, ambiguous "one app or N?" boundary).
- Alt D: ENV vars only (rejected — owner principle presumes env.local artifact; loses audit trail).

Consequences:
- Existing `E:\GT-KB\.env.local` stays as platform SoT; pruning needed (downstream WI).
- Agent Red eventual SoT: `applications/Agent_Red/.env.local`. Current 3-file layout is known deviation requiring migration (downstream WI).
- `gt env` CLI (follow-on slice) generates per-sub-app/per-target views at process-start.
- DCL-ENV-CLI-ENFORCEMENT-001 captures machine-checkable invariants including A6 single-per-scope.

Migration cost (honest trade-off): Agent Red migration includes consolidating 3 files into 1; updating deploy scripts; updating dev-loop conventions. Owner accepted this cost in S365 dialogue as worth paying for durable architectural correctness over indefinite drift risk.

Source citations: DELIB-S365-ENV-SOT-FORMALIZATION-TRACK + DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL + DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING.

### 2. Draft of `DCL-ENV-CLI-ENFORCEMENT-001`

Constraint: A canonical CLI (working name: `gt env`) is sole governed interface for reading/updating env SoT artifacts. Enforced mechanically; violations fail closed.

Assertions:
- **A1**: All env-value reads from platform or hosted application must go through `gt env` CLI. Direct file reads of SoT permitted only for runtime-environment loading at process-start.
- **A2**: All writes to env SoT artifacts must go through `gt env` CLI. PreToolUse Write/Edit hook blocks direct edits outside CLI subprocess context.
- **A3**: Consumer artifacts must not embed literal live env values. Placeholders/variable names/fake examples/public URLs permitted.
- **A4**: Cross-scope env references forbidden. CLI knows which scope each consumer belongs to.
- **A5**: `gt env` is canonical authority over SoT schema. Schema-add operations create versioned records; schema-rename operations include consumer-reference migration.
- **A6 (RESTORED from REVISED-2)**: Each scope has exactly one SoT artifact at the fixed relative path declared by ADR-ENV-SOT-TOPOLOGY-001. Per-sub-app and per-deployment-target views are CLI-generated derived artifacts treated as build outputs; not separately governed. Multi-SoT-per-scope explicitly forbidden: CLI refuses operations that would create or recognize a second SoT artifact in the same scope. Verification: at `gt env init` time, CLI fails if a second `.env.local` exists in the scope's path tree below the canonical location (unless registered as a known derived view). Doctor check enumerates scope SoT counts; > 1 SoT per scope is doctor FAIL.

Implementation note: This DCL specifies the CLI's behavioral contract. The CLI itself lands in `gtkb-env-sot-cli-slice-N` (separate bridge thread).

Source citations: DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING + DELIB-S365-ENV-SOT-FORMALIZATION-TRACK.

### 3. Draft of `GOV-ENV-LOCAL-AUTHORITY-001` (v2)

Description: GT-KB platform has exactly one env SoT artifact (the platform SoT). Each hosted application has exactly one env SoT artifact (the application SoT). Each SoT is authoritative for credentials, secrets, keys, runtime service URLs, hard path prefixes, CLI configuration choices, environment-specific variable values, and equivalent configuration visible to its scope.

Fixed relative path convention:
- Platform SoT: GT-KB repo root (`E:\GT-KB\.env.local`).
- GT-KB-contained application SoT: `applications/<app-name>/.env.local`.
- Application in own repo: application's own canonical path.

Per-sub-app and per-deployment-target views are CLI-generated derived artifacts; not separately governed.

Live credentials, secrets, keys, tokens, runtime service URLs, tenant/deployment-specific URLs must not appear outside the appropriate SoT.

Operationalized by ADR-ENV-SOT-TOPOLOGY-001 + DCL-ENV-CLI-ENFORCEMENT-001.

Assertions (revised):
- **A1 (revised)**: GT-KB platform has one env SoT artifact at platform fixed relative path. Each hosted application has one env SoT artifact at application fixed relative path. GT-KB-side SoT topology is independent of any hosted application's. Verification: doctor enumerates SoT counts per scope (> 1 per scope = FAIL); governance review confirms cross-scope references.
- **A2 (carryforward)**: No artifact under `E:\GT-KB` may contain live credentials/secrets/keys/tokens/URLs outside the appropriate SoT. Verification: repository redaction scans + commit gates fail closed.
- **A3 (carryforward)**: Other artifacts may contain only placeholders/variable names/fake examples/public URLs.
- **A4 (NEW)**: `gt env` CLI is mechanical enforcement boundary per DCL-ENV-CLI-ENFORCEMENT-001. CLI generates per-sub-app/per-target views; derived views not separately governed.

Known deviations under v2 (downstream migration scope):
- Agent Red currently has 3 SoT-class files at `applications/Agent_Red/admin/{shopify,standalone,provider}/.env.local`. Per A1, this is a deviation; migration to single Agent Red SoT + CLI-generated per-sub-app views required.
- `E:\GT-KB\.env.local` currently mixes platform values with Agent Red application values. Per A1, application values migrate to `applications/Agent_Red/.env.local`; platform values stay at root.

Both deviations tracked as separate follow-on WIs (Step 3 of Implementation Plan).

Supersedes: GOV-ENV-LOCAL-AUTHORITY-001 v1.

Source citations: all 4 S365 DELIBs.

## Implementation Plan

### Step 0-A — Capture 4 S365 DELIB records

For each S365 DELIB (in order):
1. Author formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-DELIB-S365-<name>.json`.
2. Owner approves packet via AskUserQuestion.
3. Insert DELIB row into MemBase `deliberations` table.

Order: DELIB-S365-ENV-SOT-FORMALIZATION-TRACK → DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL → DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING → DELIB-S365-ENV-SOT-PROJECT-AUTHORIZATION-PATH.

### Step 0-B — Create new project + PAUTH

1. Insert `PROJECT-GTKB-ENV-SOT-TOPOLOGY` into `projects` table.
2. Insert `PAUTH-PROJECT-GTKB-ENV-SOT-TOPOLOGY-001` into `project_authorizations` with:
   - `project_id = PROJECT-GTKB-ENV-SOT-TOPOLOGY`
   - `status = active`
   - `owner_decision_deliberation_id = DELIB-S365-ENV-SOT-PROJECT-AUTHORIZATION-PATH`
   - `allowed_mutation_classes = ["specification_authoring", "formal_artifact_approval_packet_write", "deliberation_capture"]`
   - `included_work_item_ids = ["WI-3427"]`
   - `scope_summary = "Capture env-SoT topology principle as ADR + DCL + revised GOV per S365 AUQs"`

### Step 0-C — Re-link WI-3427

`python -m groundtruth_kb projects add-item PROJECT-GTKB-ENV-SOT-TOPOLOGY WI-3427 --change-reason "Re-link to new dedicated env-SoT project per S365 AUQ #3"`.

### Step 1 — Author 3 canonical artifacts

For each (ADR → DCL → GOV-v2):
1. Author formal-artifact-approval packet.
2. Owner approves packet via AskUserQuestion.
3. Insert/update spec row in `specifications`; cite the relevant DELIB-S365-* IDs (now valid per Step 0-A).

### Step 2 — Post-implementation report

File post-impl with all 12 mutation evidence + AUQ-acceptance count + final preflights.

### Step 3 — Capture follow-on WIs

After VERIFIED, capture two backlog WIs under PROJECT-GTKB-ENV-SOT-TOPOLOGY:
- "Migrate Agent Red from 3-file SoT layout to single SoT + CLI-generated per-sub-app views."
- "Separate platform-level values from application-level values in `E:\GT-KB\.env.local`."

### Step 4 — Follow-on bridge thread (out of this proposal's scope)

`gt env` CLI implementation lands in `gtkb-env-sot-cli-slice-N` separate bridge thread.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-3 filed at bridge path; INDEX updated. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight run after Write. | PASS expected. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping; post-impl records observed results per mutation. | PASS - mapping present. |
| `GOV-STANDING-BACKLOG-001` | WI-3427 active; re-link tracked in Step 0-C. | PASS. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | New PAUTH satisfies framework per Step 0-B. | PASS at post-impl. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | New PAUTH includes all required envelope fields. | PASS at post-impl. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | New PAUTH created through this bridge thread under spec_intake authorization (not bypassing GO). | PASS. |
| `GOV-RELIABILITY-FAST-LANE-001` | Explicit non-eligibility statement above. | PASS - non-eligibility documented. |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | 7 packets (4 DELIBs + 3 specs) per implementation plan. | PASS at post-impl (per-packet evidence). |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Canonical artifacts inserted with full provenance citing 4 S365 DELIBs (which exist before spec insertion). | PASS at post-impl. |
| `GOV-20` | ADR + DCL + revised GOV exercise architecture-decision pattern. | PASS at post-impl. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | v2 supersedes v1 via append-only versioning. | PASS at post-impl. |
| `GOV-08` | Single SoT per scope honors single-source-of-truth principle. | PASS. |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | Each S365 DELIB capture goes through AUQ approval per chat-derived-spec-approval workflow. | PASS at post-impl. |
| `SPEC-AUQ-POLICY-ENGINE-001` | 4 S365 AUQs + 7 per-packet approval AUQs are owner-decision evidence. | PASS. |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-3.
- [ ] 4 S365 DELIB rows exist in `current_deliberations` before any spec insertion (Step 0-A).
- [ ] `PROJECT-GTKB-ENV-SOT-TOPOLOGY` active (Step 0-B).
- [ ] `PAUTH-PROJECT-GTKB-ENV-SOT-TOPOLOGY-001` active with `specification_authoring` in allowed_mutation_classes (Step 0-B).
- [ ] WI-3427 active under new project (Step 0-C).
- [ ] `ADR-ENV-SOT-TOPOLOGY-001` exists with single-per-application binding (Step 1).
- [ ] `DCL-ENV-CLI-ENFORCEMENT-001` exists with A6 multi-SoT-forbidden assertion (Step 1).
- [ ] `GOV-ENV-LOCAL-AUTHORITY-001` v2 exists with revised A1 + new A4 + known-deviations (Step 1).
- [ ] 7 formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/`.
- [ ] 2 follow-on backlog WIs captured (Step 3).
- [ ] Codex returns VERIFIED on post-impl.

## Risk and Rollback

Risk: moderate. Multiple MemBase mutations with append-only versioning; each gated by per-artifact owner-approval packet.

Risks:
- **Per-packet AUQ count (7 approvals)**: Mitigation: per `feedback_present_decisions_one_by_one.md`, one-at-a-time pattern honored.
- **Implementation sequencing**: DELIBs must land before specs cite them. Mitigation: Step 0-A → 0-B → 0-C → 1 → 2 → 3 explicit ordering.
- **Parallel-session race**: same risk that overwrote REVISED-2. Mitigation: re-read INDEX aggressively before each Write; if -003 gets overwritten, file -004 and continue. Opportunity-radar candidate: atomic-bridge-file-claim mechanism.

Rollback: pre-MemBase-mutation rollback discards packets; post-MemBase-mutation rollback inserts append-only revert version rows.

## Verification Limitations Anticipated

- This proposal's review confirms artifact drafts are well-formed; CLI implementing DCL assertions (incl. A6) is follow-on slice.
- A6's strict single-per-scope guarantee is forward-looking; existing deviations are documented as known deviations requiring downstream migration, not retroactively cured.

## Files Touched (target_paths recap)

- `.groundtruth/formal-artifact-approvals/**` — 7 packets.
- `groundtruth.db` — 4 DELIB INSERTs + 1 project INSERT + 1 PAUTH INSERT + 1 membership INSERT + 2 spec INSERTs + 1 spec version-INSERT + 2 backlog WI INSERTs.

Bridge filing artifacts:
- `bridge/gtkb-env-sot-topology-spec-authoring-003.md` (this file)
- `bridge/INDEX.md` (entry update)
- Next post-impl report (at `-NNN`)

## Loyal Opposition Asks

1. Confirm the bridge_kind reframing to `spec_intake` is appropriate for this work (which captures owner directive as new specs), or recommend reverting to `implementation_proposal` with a different scope adjustment.
2. Confirm the new project + PAUTH path (per S365 AUQ #3) closes Codex NO-GO-002 P1-001 cleanly, with appropriate authorization-governance specs cited, or NO-GO with specific PAUTH-scope concerns.
3. Confirm the DELIB sequencing plan (Step 0-A captures all 4 DELIBs BEFORE any spec insertion) closes Codex NO-GO-002 P1-002, or recommend alternative sequencing.
4. Verify the restored single-per-application binding in the embedded ADR/DCL/GOV-v2 drafts is consistent with the owner direction during S365 dialogue.
5. Confirm `target_paths: [".groundtruth/formal-artifact-approvals/**", "groundtruth.db"]` correctly covers the implementation surface.
6. Note any remaining authorization-governance specs that should be added beyond `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` + `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` + `GOV-RELIABILITY-FAST-LANE-001`.
7. Acknowledge the parallel-session-race observation (second instance this session of races overwriting Prime REVISED content; opportunity-radar candidate for atomic-bridge-file-claim mechanism).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

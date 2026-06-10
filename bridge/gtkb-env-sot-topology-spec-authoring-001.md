NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-env-sot-topology-spec-authoring
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Capture env-SoT Topology Principle as ADR + DCL + Revised GOV (per S365 owner AUQs)

bridge_kind: prime_proposal
Document: gtkb-env-sot-topology-spec-authoring
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3427 (capture env-SoT topology principle as ADR + DCL + revised GOV)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3427
target_paths: [".groundtruth/formal-artifact-approvals/**", "groundtruth.db"]
Recommended commit type: feat:

## Summary

This proposal scopes the authoring of three canonical artifacts capturing the owner's env-SoT topology and CLI-enforcement principle (S365 owner statement, 2026-05-28):

1. **`ADR-ENV-SOT-TOPOLOGY-001`** — Architecture decision: GT-KB platform and the hosted application each have **independent** env source-of-truth artifacts (separate from each other; one each), rather than a single shared `.env.local` serving both.
2. **`DCL-ENV-CLI-ENFORCEMENT-001`** — Machine-checkable design constraint: the CLI used to read/update env SoTs is the mechanical enforcement boundary for SoT-consumer alignment; consumer artifacts (source code, tests, docs) must reference the SoT through the CLI rather than embed literal values.
3. **`GOV-ENV-LOCAL-AUTHORITY-001` (v2)** — Revision of the existing GOV spec: switch its framing from "single root `.env.local` serves both platform and hosted application" to "separate platform + application SoTs"; reference the new ADR/DCL; preserve A2/A3 (no live values in other artifacts; only placeholders permitted).

Per Codex's GO-20 advisory pilot, the ADR captures decision + context + alternatives + consequences; the DCL captures machine-checkable invariants; the revised GOV is the operating governance rule referencing both. Implementation (the `gt env` CLI surface) is a follow-on bridge per the DCL invariants and is OUT OF SCOPE for this proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; INDEX entry tracked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target paths within `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + PAUTH declared above.
- `GOV-STANDING-BACKLOG-001` - WI-3427 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - canonical-artifact authoring is governed by formal-artifact-approval packets per artifact.
- `GOV-20` (Architecture Decision Workflow / ADR-DCL-IPR-CVR advisory pilot) - this proposal exercises the ADR + DCL pattern.
- `GOV-ENV-LOCAL-AUTHORITY-001` - the existing GOV spec being revised; A1 framing changes; A2/A3 preserved.
- `GOV-08` - "Knowledge Database is the single source of truth" — foundational SoT principle.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - owner-AUQ-based promotion of chat-derived candidate requirements to formal specs.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions captured via AskUserQuestion S365 (two questions, both answered).
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact-approval packets required for canonical-artifact mutation.
- `PB-ARTIFACT-APPROVAL-001` - protected-behavior framing for artifact-approval discipline.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook-enforced gate at MemBase-insertion time.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability between WI-3427, this thread, the 3 artifacts, and the formal-artifact-approval packets.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - canonical-artifact insertions advance the lifecycle.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the `gt env` CLI (follow-on scope) is the deterministic-service path; this proposal captures the principle that establishes its need.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - the separate-SoTs topology aligns with platform/application lifecycle independence.

## Requirement Sufficiency

`Existing requirements sufficient` for the proposal-side spec-authoring deliverable. The owner-stated principle is being captured through the formal artifact channel (ADR + DCL + revised GOV); no new SPEC is being created beyond what this proposal scopes. The candidate requirement from the S365 owner statement is being promoted via the formal-artifact channel per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

## KB Mutation Scope

This proposal will require MemBase mutation in the implementation phase (NOT this proposal phase). At implementation:

- One INSERT into `specifications` for `ADR-ENV-SOT-TOPOLOGY-001` (`type=architecture_decision`).
- One INSERT into `specifications` for `DCL-ENV-CLI-ENFORCEMENT-001` (`type=design_constraint`; assertions field populated).
- One UPDATE (new version row) of `GOV-ENV-LOCAL-AUTHORITY-001` (`type=governance`) reflecting the revised description + assertions.

Each canonical mutation is gated by a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`. The packets will be authored after Codex GO on this proposal and require explicit owner approval before MemBase insertion.

## WI Citation Disclosure

This proposal declares implementation work for WI-3427 only. No other WI is implicated.

## Prior Deliberations

- **S365 AskUserQuestion answer #1 (2026-05-28)**: Track choice — Owner selected "ADR + DCL + revision" from four formalization options. To be captured as `DELIB-S365-ENV-SOT-FORMALIZATION-TRACK`.
- **S365 AskUserQuestion answer #2 (2026-05-28)**: Agent Red split — Owner selected "Defer to Agent Red" from four scope-clarification options. To be captured as `DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL`.
- **S365 originating owner statement (2026-05-28)**: The env-SoT topology and CLI-enforcement principle being formalized.
- `GOV-ENV-LOCAL-AUTHORITY-001` (existing spec): the current single-env.local model being refined.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: the lifecycle-independence framing that motivates separate SoTs.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: the deterministic-services principle that motivates CLI-as-enforcer.
- `DELIB-0828`, `DELIB-0834`: prior Agent Red governance framing (separate-project status).
- 2026-05-04 owner correction: Agent Red is a separate project, not part of GT-KB.

## Owner Decisions / Input

- **S365 AskUserQuestion answer #1 (Track)**: "ADR + DCL + revision (Recommended)" — authorizes authoring three canonical artifacts.
- **S365 AskUserQuestion answer #2 (Agent Red)**: "Defer to Agent Red (Recommended)" — the ADR/DCL/revised-GOV specify the platform-side topology principle only; Agent Red's specific SoT layout is Agent Red's own decision in Agent Red's scope.
- **S365 originating principle statement** (verbatim, 2026-05-28): *"GT-KB and the hosted/contained application should each have independent artifacts which are the source-of-truth for environment variables, such as hard path prefixes, credentials, CLI configuration choices and variable values or other information which should not be in other artifacts, such as source code or files. I have presumed that this artifact is an env.local document. The GT-KB artifacts should refer to the GT-KB source-of-truth. The application artifacts should refer to the application's source-of-truth. Keeping these sources-of-truth aligned must be mechanical, enforced by the CLI used to read/update the sources-of-truth."*

No additional owner decisions required for THIS proposal phase. Implementation phase will require:
- One formal-artifact-approval packet per artifact (3 packets, 3 owner approvals via AskUserQuestion).

## Embedded Artifact Drafts

The following artifact drafts are provided so Codex can evaluate the substantive content before implementation. Each draft will be inserted (or version-incremented) into MemBase only after Codex GO + per-artifact formal-artifact-approval packet.

### 1. Draft of `ADR-ENV-SOT-TOPOLOGY-001`

```
ID: ADR-ENV-SOT-TOPOLOGY-001
Type: architecture_decision
Title: Separate env source-of-truth artifacts for GT-KB platform and hosted application

Status: proposed

Decision:
The GT-KB platform and each hosted application have independent env source-of-truth (SoT)
artifacts. The platform SoT artifact governs platform-level configuration (hard paths,
credentials, CLI configuration choices, variable values) visible to GT-KB platform code,
tests, scripts, hooks, and docs. The application SoT artifact governs application-level
configuration visible to the application's own code, tests, scripts, and docs.

The two SoT artifacts are independent: changes to one do not require changes to the other;
each evolves on its application's/platform's own lifecycle cadence per
DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT.

Each consumer artifact (source code, tests, scripts, hooks, docs) references its scope's
SoT only. GT-KB platform artifacts reference the platform SoT. Application artifacts
reference the application SoT. Cross-scope references (e.g., platform code reading the
application's SoT) are explicitly forbidden as a topology invariant.

Context:
- The existing GOV-ENV-LOCAL-AUTHORITY-001 v1 declared a single root .env.local at
  E:\GT-KB\.env.local serving both platform and hosted application; this conflated
  the lifecycle-independence boundary between GT-KB and its hosted applications.
- Owner correction 2026-05-04: Agent Red is a separate project, not part of GT-KB.
  The single-env.local model is inconsistent with that framing — Agent Red's env
  values logically belong to Agent Red, not to GT-KB.
- Per DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE, repetitive plumbing belongs in
  services. The CLI managing env SoTs is the natural deterministic-service shape.

Alternatives considered:
- Alternative A: Keep single .env.local (rejected — conflates lifecycle boundary).
- Alternative B: Single SoT with deployment-target views (rejected — owner principle
  specifies INDEPENDENT artifacts, not derived views).
- Alternative C: ENV vars only, no SoT artifact (rejected — owner principle presumes
  an env.local document; ENV-only loses durable history and audit trail).

Consequences:
- The existing GT-KB .env.local stays in place as the GT-KB platform SoT (its content
  may need pruning to remove application-only values that migrate to the application SoT).
- Hosted applications get their own SoT artifacts in their own scope. Agent Red's specific
  SoT layout is deferred to Agent Red per S365 owner AUQ #2.
- The gt env CLI (follow-on scope) gates SoT read/update operations and enforces
  topology invariants (no cross-scope references; no literal values in consumer artifacts).
- DCL-ENV-CLI-ENFORCEMENT-001 captures the machine-checkable invariants this ADR establishes.

Rejected approaches:
- Alternative A (above): rejected because it conflates lifecycle boundaries.
- Alternative B (above): rejected because the principle specifies INDEPENDENT artifacts.
- Alternative C (above): rejected because ENV-only loses durable history.

Source: S365 owner statement (2026-05-28); S365 AUQ #1 + #2 owner decisions.
Owner-decision deliberation IDs: DELIB-S365-ENV-SOT-FORMALIZATION-TRACK,
DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL.
```

### 2. Draft of `DCL-ENV-CLI-ENFORCEMENT-001`

```
ID: DCL-ENV-CLI-ENFORCEMENT-001
Type: design_constraint
Title: The CLI managing env SoTs is the mechanical enforcement boundary for SoT-consumer alignment

Status: proposed

Constraint:
A canonical CLI (working name: gt env) is the sole governed interface for reading and
updating env source-of-truth artifacts. The CLI enforces these invariants mechanically;
violations fail closed at CLI invocation or commit time.

Derived from: ADR-ENV-SOT-TOPOLOGY-001.

Assertions (machine-checkable):
- DCL-ENV-CLI-ENFORCEMENT-001-A1: All reads of env values from the platform or any
  hosted application must go through the gt env CLI (or an equivalent governed
  read surface). Direct file reads of .env.local files by consumer code are
  permitted only when the consumer is loading the SoT into the runtime
  environment at process-start; subsequent value lookups go through the env
  namespace, not direct file reads.
  Verification: Source/test/doc scans for direct file-path references to env.local
  files outside the loader path (e.g., python-dotenv invocations) fail closed when
  found.

- DCL-ENV-CLI-ENFORCEMENT-001-A2: All writes to env SoT artifacts must go through
  the gt env CLI (or governed write surface). Direct hand-edits of .env.local
  files are prohibited; the gt env CLI is the sole writer.
  Verification: PreToolUse Write/Edit hook (extension of scanner-safe-writer)
  blocks direct edits to env.local files outside the CLI's own subprocess context.

- DCL-ENV-CLI-ENFORCEMENT-001-A3: Consumer artifacts (source code, tests, scripts,
  hooks, docs) must not embed literal live env values. Variable names (e.g.,
  os.environ.get("GT_FOO")), placeholders (e.g., {{GT_FOO}}), explicitly fake
  examples (e.g., "sk-test-FAKE"), and public documentation/source-control URLs
  are permitted.
  Verification: Repository-wide scan compares literal values in consumer artifacts
  against the SoT registry; matches outside the SoT registry fail closed.

- DCL-ENV-CLI-ENFORCEMENT-001-A4: Cross-scope env references are forbidden.
  GT-KB platform code/tests/docs must not read values from the application SoT;
  application code/tests/docs must not read values from the platform SoT.
  Verification: gt env scoped reads (e.g., gt env get --scope platform KEY) refuse
  cross-scope lookups; the CLI knows which scope each consumer belongs to.

- DCL-ENV-CLI-ENFORCEMENT-001-A5: The gt env CLI is the canonical authority over
  the SoT schema. Adding a new env key or renaming an existing key goes through
  gt env, which mechanically updates dependent consumer-reference scans.
  Verification: Schema-add operations create a versioned record; schema-rename
  operations include a migration step that updates consumer references via
  the CLI.

Implementation note: This DCL specifies the CLI's behavioral contract. The
gt env CLI implementation itself is follow-on bridge scope (gtkb-env-sot-cli-slice-N).
```

### 3. Draft of `GOV-ENV-LOCAL-AUTHORITY-001` (v2 revision)

```
ID: GOV-ENV-LOCAL-AUTHORITY-001
Version: 2
Type: governance
Title: env source-of-truth artifacts are the authoritative configuration and credential
       sources for the GT-KB platform and each hosted application

Status: specified

Description (revised):
The GT-KB platform and each hosted application have independent env source-of-truth
(SoT) artifacts (typically .env.local files; collectively "env SoTs"). Each SoT is the
authoritative source for credentials, secrets, keys, runtime service URLs, hard path
prefixes, CLI configuration choices, environment-specific variable values, and equivalent
configuration visible to its scope.

Live credentials, secrets, keys, tokens, runtime service URLs, tenant- or deployment-
specific URLs, and equivalent environment-specific configuration values must not appear
in any other artifact under E:\GT-KB; other artifacts may use variable names,
placeholders, explicitly fake examples, or public documentation/source-control URLs
that are not runtime configuration.

This spec is operationalized by ADR-ENV-SOT-TOPOLOGY-001 (the architectural decision
establishing the separate-SoTs topology) and DCL-ENV-CLI-ENFORCEMENT-001 (the
machine-checkable invariants enforced by the gt env CLI).

Assertions (revised):
- GOV-ENV-LOCAL-AUTHORITY-001-A1: The GT-KB platform has one env SoT artifact (the
  platform SoT). Each hosted application has one or more env SoT artifacts at the
  application's own discretion. The GT-KB-side SoT topology is independent of any
  hosted application's SoT topology.
  Verification: Governance review confirms platform code/tests/docs reference only
  the platform SoT; application code/tests/docs reference only the application's
  own SoT.

- GOV-ENV-LOCAL-AUTHORITY-001-A2: No artifact under E:\GT-KB may contain live
  credentials, secrets, keys, tokens, runtime service URLs, tenant- or deployment-
  specific URLs, or equivalent environment-specific configuration values outside
  the appropriate env SoT for its scope.
  Verification: Repository redaction scans and commit gates fail closed on literal
  live values outside the appropriate SoT.

- GOV-ENV-LOCAL-AUTHORITY-001-A3: Other artifacts may contain only non-sensitive
  placeholders, variable names, explicitly fake examples, or public documentation/
  source-control URLs that are not runtime configuration.
  Verification: Allowlists must be value+path scoped and must not permit live values.

- GOV-ENV-LOCAL-AUTHORITY-001-A4: The gt env CLI (or governed equivalent) is the
  mechanical enforcement boundary for SoT-consumer alignment, per
  DCL-ENV-CLI-ENFORCEMENT-001.
  Verification: DCL-ENV-CLI-ENFORCEMENT-001 assertions enumerate the specific
  invariants the CLI enforces; this assertion incorporates them by reference.

Supersedes: GOV-ENV-LOCAL-AUTHORITY-001 v1 (which declared a single root .env.local
for both platform and hosted application).

Source: S365 owner statement (2026-05-28); S365 AUQ #1 + #2 owner decisions.
Owner-decision deliberation IDs: DELIB-S365-ENV-SOT-FORMALIZATION-TRACK,
DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL.
```

## Implementation Plan

After Codex GO on this proposal:

1. **Author 3 formal-artifact-approval packets** at:
   - `.groundtruth/formal-artifact-approvals/2026-05-28-ADR-ENV-SOT-TOPOLOGY-001.json`
   - `.groundtruth/formal-artifact-approvals/2026-05-28-DCL-ENV-CLI-ENFORCEMENT-001.json`
   - `.groundtruth/formal-artifact-approvals/2026-05-28-GOV-ENV-LOCAL-AUTHORITY-001-v2.json`

   Each packet contains the full artifact content above, the SHA256 of the body, owner-approval evidence (per-artifact AskUserQuestion confirmation), and the required formal-artifact-approval fields.

2. **Owner approves each packet via AskUserQuestion** (one packet at a time per `feedback_present_decisions_one_by_one.md`). 3 owner-AUQ confirmations expected.

3. **MemBase mutations** (one per artifact):
   - `db.insert_spec(...)` for ADR-ENV-SOT-TOPOLOGY-001.
   - `db.insert_spec(...)` for DCL-ENV-CLI-ENFORCEMENT-001 (with assertions field populated per the draft).
   - `db.update_spec(...)` for GOV-ENV-LOCAL-AUTHORITY-001 (new version with revised description + assertions).

   Each mutation triggers the `formal-artifact-approval-gate` hook, which validates that the inserted/updated content matches the corresponding approval packet's body_sha256.

4. **Post-implementation report** documents the 3 insertions/updates, the formal-artifact-approval packets created, and the owner-approval evidence.

5. **Follow-on bridge thread** (separate scope, not this proposal): `gtkb-env-sot-cli-slice-N` proposes and implements the `gt env` CLI per DCL-ENV-CLI-ENFORCEMENT-001 invariants. That scope includes:
   - `gt env get` / `gt env set` / `gt env check` / `gt env migrate` subcommands.
   - Schema versioning and per-scope (platform / application) namespacing.
   - Consumer-reference scan hook extension (extending scanner-safe-writer).
   - Migration of the existing `E:\GT-KB\.env.local` to split platform-only content from any application-only content currently mixed in.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal at `bridge/gtkb-env-sot-topology-spec-authoring-001.md`; INDEX entry created. | PASS — bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root under `E:\GT-KB`. | PASS — formal-artifact-approval packets + groundtruth.db are in-root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-env-sot-topology-spec-authoring`. | PASS expected. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping with observed results at post-impl report time. | PASS — mapping present. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES`: WI-3427 active member. | PASS — verified at WI capture time. |
| `GOV-20` (advisory pilot) | Three artifacts authored: ADR (architecture_decision), DCL (design_constraint with assertions), revised GOV (governance). | PASS at post-impl review. |
| `GOV-ENV-LOCAL-AUTHORITY-001` (revision) | New version row in `specifications` table with revised description + 4 assertions. | PASS at post-impl review. |
| `GOV-08` | KB is single SoT for project knowledge; the 3 artifacts are inserted into MemBase (canonical store). | PASS at post-impl review. |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | Owner-AUQ confirmation per artifact before MemBase insertion. | PASS at post-impl review (3 owner-AUQ approvals expected). |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner decisions captured via S365 AUQ #1 + #2 + 3 per-packet AUQs. | PASS — AUQ-only path observed. |
| `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | 3 formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/`; hook gates the inserts. | PASS at post-impl review. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Traceability: WI-3427 → this thread → 3 packets → 3 MemBase mutations → post-impl report. | PASS at post-impl review. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | 3 spec insertions/updates advance the lifecycle. | PASS at post-impl review. |

## Acceptance Criteria

- [ ] Codex returns GO on this proposal.
- [ ] 3 formal-artifact-approval packets authored.
- [ ] Owner approves each packet via AskUserQuestion (3 owner-AUQ confirmations).
- [ ] `ADR-ENV-SOT-TOPOLOGY-001` inserted into `specifications` (type=architecture_decision).
- [ ] `DCL-ENV-CLI-ENFORCEMENT-001` inserted into `specifications` (type=design_constraint) with the 5 assertions populated.
- [ ] `GOV-ENV-LOCAL-AUTHORITY-001` updated to v2 with revised description + 4 assertions.
- [ ] Post-implementation report enumerates the 3 mutations + the 3 packets + per-artifact verification.
- [ ] Codex returns VERIFIED.

## Risk and Rollback

Risk: low. The 3 artifacts are documentation-class canonical records. No source/test/script changes; no runtime behavior changes. The `gt env` CLI implementation (follow-on scope) is separately gated.

Risks identified:
- **Cross-scope reference exposure**: The revised GOV's A1 declares that platform code references only platform SoT and vice versa. The existing GT-KB codebase may have cases where platform tests reference Agent Red env values (or vice versa) that violate the new invariant. Mitigation: this is captured as Slice-N (the `gt env` CLI's consumer-reference scan); current `GOV-ENV-LOCAL-AUTHORITY-001` v2 spec is forward-looking; existing violations get triaged in the CLI-scan slice.
- **GOV-ENV-LOCAL-AUTHORITY-001 v1 supersession ambiguity**: v2 is a version increment, not a separate spec. Supersession is implicit through append-only versioning. Mitigation: revised description explicitly cites v1 framing as the prior state.
- **Agent Red SoT layout deferral**: Owner's S365 AUQ #2 deferred Agent Red layout to Agent Red. The current `E:\GT-KB\applications\Agent_Red\admin\{shopify,standalone,provider}\.env.local` files remain in place; their disposition is Agent Red's call. Mitigation: explicitly out of scope for this proposal.

Rollback: 
- Pre-MemBase-mutation: discard the formal-artifact-approval packets; no DB state changed.
- Post-MemBase-mutation: insert another version row reverting GOV-ENV-LOCAL-AUTHORITY-001 to v1 framing; insert "deprecated" status on ADR/DCL (append-only; original rows preserved).

## Verification Limitations Anticipated

- The DCL's assertions specify machine-checkable invariants the `gt env` CLI will enforce; this proposal's verification confirms the assertions are well-formed and machine-readable, NOT that the CLI implementing them exists yet (that's the follow-on slice).
- The revised GOV's A1 declares the topology principle; existing cross-scope reference violations in the codebase are NOT remediated by this proposal — that remediation is the `gt env` CLI's consumer-reference scan slice.

## Files Touched (target_paths recap)

- `.groundtruth/formal-artifact-approvals/2026-05-28-ADR-ENV-SOT-TOPOLOGY-001.json` (new at impl)
- `.groundtruth/formal-artifact-approvals/2026-05-28-DCL-ENV-CLI-ENFORCEMENT-001.json` (new at impl)
- `.groundtruth/formal-artifact-approvals/2026-05-28-GOV-ENV-LOCAL-AUTHORITY-001-v2.json` (new at impl)
- `groundtruth.db` (mutating: 2 INSERT + 1 UPDATE/new-version at impl)

Bridge filing artifacts:
- `bridge/gtkb-env-sot-topology-spec-authoring-001.md` (this file)
- `bridge/INDEX.md` (entry update)
- Future post-impl report.

## Loyal Opposition Asks

1. Verify the embedded ADR draft captures the architecture decision precisely (decision, context, alternatives, consequences), or NO-GO with specific gaps.
2. Verify the embedded DCL draft's 5 assertions are machine-checkable, internally consistent, and forward-compatible with the future `gt env` CLI implementation, or recommend refinements.
3. Verify the revised GOV-ENV-LOCAL-AUTHORITY-001 v2 draft preserves the spec's substantive force while updating the topology framing, or surface unintended weakening.
4. Confirm the GOV-20 ADR + DCL pattern is correctly exercised (architecture decision + machine-checkable constraint + revised governance rule), or recommend an alternative artifact split.
5. Confirm the formal-artifact-approval packet workflow (3 packets, 3 owner-AUQ approvals, 3 MemBase mutations) is correctly scoped, or recommend a different implementation sequence.
6. Verify the Agent Red deferral is correctly handled (platform-side principle declared; Agent Red layout out of scope), or recommend explicit Agent Red scope inclusion/exclusion language.
7. Note any cross-cutting governance specs that should be added to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

NEW

# Prime Disposition - LO Hygiene Assessment Skill Advisory (WI-3303)

bridge_kind: implementation_proposal
Document: gtkb-lo-hygiene-assessment-skill-advisory-disposition
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3303 (advisory-backlog-router routed advisory `INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY.md`)
Recommended commit type: `docs:`
target_paths: ["bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-14-wi-3303-disposition-*.json"]

## Summary

Prime Builder classifies LO advisory `INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY.md` (routed as WI-3303) as **`adapt`** under the Peer-Solution-Advisory-Loop classification vocabulary (`.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary). Disposition rationale: the advisory's core pattern (a new LO-owned orchestration skill that synthesizes hygiene checks into a phase-indexed, severity-ranked, read-only Prime-action plan and preserves the Prime Builder / Loyal Opposition role split) is correct and worth implementing. Prime adapts the surface to GT-KB native conventions: canonical `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md`, capability-registry entry in `config/agent-control/harness-capability-registry.toml`, Codex adapter generated via `scripts/generate_codex_skill_adapters.py`, and a v1 scope limited to manual invocation (deferring startup-pulse, scheduling, and command-surface invocation per F4 of the advisory). This disposition is the routing decision; the substantive implementation will be filed under a separate `gtkb-lo-hygiene-assessment-skill-build` bridge thread post-Codex-GO.

## Advisory Source

- Advisory file: `E:\GT-KB\independent-progress-assessments\CODEX-INSIGHT-DROPBOX\INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY.md`
- Routed work item: WI-3303 (rowid 4579; `origin='hygiene'`; `source_spec_id='GOV-STANDING-BACKLOG-001'`; `changed_by='advisory-backlog-router/1.0'`; `changed_at='2026-05-14T02:59:42+00:00'`).
- Source advisory `Disposition` field self-declared: "Advisory report; implementation recommended". Severity P1 across F1 (fragmented hygiene authority) and F2 (LO read-only advisory boundary); P2 across F3 (cross-harness skill pattern) and F4 (lightweight startup/scheduling).
- Note: advisory recommends a GT-KB-native skill build (not adoption of an external peer system). The Peer-Solution-Advisory-Loop classification vocabulary still applies because the LO advisory is the input pattern; `adapt` is the appropriate state because Prime accepts the core pattern (LO orchestration skill) but tailors the surface to GT-KB native conventions and a narrower v1 scope.

## Classification

**`adapt`** per `.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary.

### Evidence supporting `adapt` over `adopt`/`reject`/`defer`/`monitor`

- **`adopt` rejected:** would require accepting the advisory's recommendation AS-IS, including the full v1 contract (overview / phase / verify / startup-pulse modes; 9-phase registry; report-format with 11 required fields). Prime adapts by narrowing v1 to manual `overview` + `phase <id>` modes only, deferring `startup-pulse` and command surfaces (`::hygiene`, `gt hygiene scan`) per the advisory's own F4 phased-rollout guidance. Prime also adapts capability-registry attribution (`parity_class = "baseline"` initially, per F3) rather than `required` from day one.
- **`adapt` selected:** Prime accepts the CORE PATTERN — a single LO-owned orchestration skill that calls existing narrower hygiene skills (`structural-hygiene-review`, `check-deliberations`, `kb-session-wrap-scan`, `harness-parity-review`), synthesizes a Prime-facing action plan, and stays read-only by default — and ADAPTS the surface to GT-KB native conventions: canonical `.claude/skills/` source + capability-registry entry + Codex-adapter pipeline (rather than ad-hoc invocation), v1 manual mode only, and explicit `prime-action` / `peer-prime-candidate` / `lo-verification` ownership classification per finding.
- **`reject` rejected:** the advisory recommendation does not conflict with GT-KB governance; it strengthens the Prime Builder / Loyal Opposition role split by giving LO a structured advisory surface and keeping mutation authority with Prime Builder. Rejection would discard durable hygiene-assessment repeatability.
- **`defer` rejected:** no future GT-KB milestone needs to land before this skill is useful; the existing hygiene checks (F1 references `structural-hygiene-review`, `check-deliberations`, `kb-session-wrap-scan`, `harness-parity-review`) are already in place. The advisory's own F4 staging is internal to the skill scope, not a defer trigger.
- **`monitor` rejected:** the recommendation requires active implementation work (a new SKILL.md + capability-registry entry + adapter regeneration); passive monitoring would leave the advisory in scrollback indefinitely.

### Adapt scope vs advisory surface

| Advisory surface | Prime adaptation |
|---|---|
| Skill canonical name `loyal-opposition-hygiene-assessment` | Adopt as-is. |
| Modes: `overview` + `phase <id>` + `verify <report-or-phase>` + `startup-pulse` | v1: `overview` + `phase <id>` only. Defer `verify` and `startup-pulse` to follow-on slice after first 1-2 reports calibrate signal/noise. |
| 9-phase hygiene registry (DA / branches / bridge / structure / terminology / specs / gitignore / naming / poller-residual) | Adopt as-is in skill body; mark all 9 phases available in v1 but expect first 2-3 manual runs to cover one phase each, not all nine. |
| Report format: 11 required fields (claim / scope / evidence / severity / phase / Prime sequence / peer-Prime / LO verification / do-not-touch / owner decisions / residual risk) | Adopt as-is. |
| Capability-registry entry `parity_class = "baseline"` initially, promote to `required` later | Adopt as-is. |
| Codex adapter via `scripts/generate_codex_skill_adapters.py --update-registry` | Adopt as-is (canonical mechanism). |
| Verification commands: `--update-registry --check`, `check_harness_parity.py --all --markdown`, `rg` discovery scan | Adopt as-is for the follow-on build thread. |
| Out-of-scope action list (branch deletion, formal artifact mutation, spec merge/retire, script deletion, broad rename, role/bridge mutation) | Adopt as-is verbatim in skill body — these are LO read-only-advisory boundary guardrails. |
| Command surfaces `::hygiene` / `gt hygiene scan` | DEFER to a separate follow-on bridge thread; not in v1 build scope. |
| Startup-pulse hygiene-age reporting | DEFER to a separate follow-on bridge thread; not in v1 build scope. |
| Scheduling (weekly / pre-release / post-churn) | DEFER to a separate follow-on bridge thread; not in v1 build scope. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `.claude/rules/peer-solution-advisory-loop.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/project-root-boundary.md`

## Prior Deliberations

- `INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY.md` — the source LO advisory routed into WI-3303 (cited verbatim as the advisory input).
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` — Slice-0 Codex GO that authorized the Peer-Solution-Advisory-Loop classification vocabulary used here.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` through `-004.md` — durable rule capture for the procedure now codified at `.claude/rules/peer-solution-advisory-loop.md`.
- `bridge/gtkb-mcp-stable-harness-surface-advisory-disposition-001.md` (NEW; S350 2026-05-14) — sibling advisory-disposition proposal authored under the same owner-direction batch; precedent for the disposition format used here.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md` (referenced by the canonical glossary `benchmark` entry) — adjacent LO read-only measurement pattern that informs the advisory's read-only-default boundary (F2).
- _No prior deliberations specifically classifying a `loyal-opposition-hygiene-assessment` skill: this is the first disposition for WI-3303 and the first Prime response to the cited advisory._

## Owner Decisions / Input

- **Owner direction 2026-05-14 S350**: "Please parallelize work and start as many priority backlog projects as possible" — authorizes batch filing of priority backlog proposals; per-proposal Codex GO required before implementation.
- The advisory itself records at § Open Owner Decisions: "No blocking owner decision is required. The owner has already expressed preference for an LO standards/enforcement hygiene skill and asked to implement it." Prime carries that statement forward as supporting owner input but does NOT substitute it for the AUQ-required approvals that the follow-on implementation proposal will need for capability-registry mutation and formal-artifact packets.
- No AUQ-required owner decision is required to record `adapt` classification: the disposition itself is a routing decision under Prime authority (per `.claude/rules/peer-solution-advisory-loop.md` § Owner-Dialogue Workflow step 4: `adapt` → NEW bridge proposal; owner reviews substantive `adapt` proposals through standard bridge review, which is the follow-on build thread, not this disposition).
- The follow-on build proposal will require AUQ-required owner approval for: (a) capability-registry mutation per `GOV-ARTIFACT-APPROVAL-001`, (b) any formal-artifact packets the build creates, (c) the eventual `parity_class` promotion from `baseline` to `required`.

## Clause Scope Clarification (Not a Bulk Operation)

This disposition proposal is a single-thread inventory and routing record. It is NOT a bulk-ops operation against the standing backlog: it touches exactly one work item (WI-3303) by resolution-status update post-GO, and one formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-wi-3303-disposition-*.json` when the disposition is recorded. No `inventory` sweep of multiple work items, no batch MemBase mutation, no bulk spec-status promotion. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause does not gate this proposal because the proposal performs single-item routing under the advisory-loop procedure; `formal-artifact-approval` packet evidence for the per-WI resolution remains required per `GOV-ARTIFACT-APPROVAL-001`.

## Requirement Sufficiency

Existing requirements sufficient. Governing requirements: `.claude/rules/peer-solution-advisory-loop.md` defines the 5-state vocabulary; `GOV-FILE-BRIDGE-AUTHORITY-001` defines the bridge transport; `GOV-STANDING-BACKLOG-001` defines work-item resolution authority; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` defines verification-evidence scope for the (no-source-impl) disposition; `.claude/rules/loyal-opposition.md` defines the read-only-advisory boundary that the adapted skill enforces; `GOV-ARTIFACT-APPROVAL-001` defines the formal-artifact-approval packet requirement carried into the follow-on build thread. No new requirements or specifications are required for this disposition.

## Follow-On Artifact Plan

Post-Codex GO, Prime Builder will:

1. **File a Deliberation Archive record** capturing the `adapt` disposition. Required fields:
   - `source_type='advisory_disposition'`
   - `outcome='adapt'`
   - `title='WI-3303 disposition: adapt (LO hygiene assessment skill — adopt core pattern; adapt to GT-KB native conventions; defer scheduling/startup-pulse/command-surface to follow-on slice)'`
   - `summary` quoting this proposal's § Classification with the adapt-scope-vs-advisory-surface table.
   - `related_deliberation_ids` citing the source advisory's harvested DELIB-ID once known and the procedure thread `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md`.
   - `related_spec_ids='GOV-FILE-BRIDGE-AUTHORITY-001,GOV-ARTIFACT-APPROVAL-001'`.

2. **File the follow-on implementation proposal** at `bridge/gtkb-lo-hygiene-assessment-skill-build-001.md` (NEW). That thread is the substantive implementation work scope:
   - Author canonical `.claude/skills/loyal-opposition-hygiene-assessment/SKILL.md` per the advisory's § Recommended Skill Contract (name + description + required-inputs + modes + 9-phase registry + report-format + out-of-scope action list).
   - Add `skill.loyal-opposition-hygiene-assessment` capability-registry entry with `required_for_roles = ["loyal-opposition"]` and `parity_class = "baseline"`.
   - Generate Codex adapter at `.codex/skills/loyal-opposition-hygiene-assessment/SKILL.md` via `python scripts/generate_codex_skill_adapters.py --update-registry`.
   - Update `.codex/skills/MANIFEST.json` if the adapter generator updates it.
   - Verify with `python scripts/generate_codex_skill_adapters.py --update-registry --check` and `python scripts/check_harness_parity.py --all --markdown`.
   - v1 scope: manual `overview` + `phase <id>` modes only; defer `verify`, `startup-pulse`, `::hygiene`/`gt hygiene scan` command surfaces, scheduling, and `parity_class` promotion to a separate follow-on slice.

3. **Resolve WI-3303** post-Codex GO via standard MemBase work-item resolution path under a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-wi-3303-disposition.json`. Change reason: `'advisory disposition: adapt — LO hygiene assessment skill recommendation accepted; v1 build deferred to follow-on bridge gtkb-lo-hygiene-assessment-skill-build'`.

4. **File post-implementation report** at `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-NNN.md` carrying forward the DA insert evidence, the WI-3303 resolution evidence, and a pointer to the follow-on build thread for Codex VERIFIED.

No source code, no test changes, no harness configuration changes, no plugin packaging, no skill file authoring in this disposition. The DA insert, the WI-3303 resolution, and the follow-on build proposal filing are the only artifacts produced by this disposition.

## Risk and Rollback

- **Risk: misclassification (`adapt` vs `adopt`).** If Codex assesses that the v1 narrowing (manual modes only; defer scheduling/startup-pulse/command-surface) misreads the advisory's core pattern, Codex should issue NO-GO with the disagreement evidence. Prime will revise to `adopt` (full v1 scope as advisory describes) or to a tighter `adapt` (further narrowing).
- **Risk: misclassification (`adapt` vs `reject`).** If Codex assesses that the GT-KB hygiene authority is sufficiently covered by the existing skills (`structural-hygiene-review`, `check-deliberations`, `kb-session-wrap-scan`, `harness-parity-review`) and a new orchestration skill is redundant, Codex should issue NO-GO. Prime will revise to `reject` with DA-preservation rationale.
- **Risk: scope drift in the follow-on build proposal.** The follow-on `gtkb-lo-hygiene-assessment-skill-build-001.md` proposal will be subject to standard Codex review and may itself be NO-GO'd on scope or quality grounds. This disposition does not pre-authorize the build; it only routes the advisory to the build thread.
- **Rollback:** the disposition is reversible. DA inserts are append-only but additive; the `adapt` classification can be superseded by a future `reject` or `monitor` proposal under the same advisory if the build proposal fails review and Prime concludes no implementation path is acceptable. The WI-3303 resolution is reversible via standard work-item reopen procedure. No source code, registry, or adapter mutation is performed by this disposition, so no source-side rollback is required.

## Acceptance Criteria

1. Codex confirms `adapt` is the correct Peer-Solution-Advisory-Loop classification for this advisory.
2. Codex confirms the adapt-scope-vs-advisory-surface table accurately represents what Prime accepts AS-IS vs adapts vs defers.
3. Codex confirms the Follow-On Artifact Plan is sufficient (DA insert + WI resolution + separate build-thread filing, with no source/test/registry mutation in this disposition).
4. Applicability and clause preflights PASS against this proposal file (content-file mode; INDEX entry deferred).
5. The Prior Deliberations section cites the source advisory file, the Peer-Solution-Advisory-Loop conversion thread, and the sibling MCP-advisory-disposition precedent.
6. The Owner Decisions / Input section enumerates the owner direction authorizing batch filing.

## Verification Plan

Spec-to-test mapping for this no-source-implementation disposition:

| Linked specification / rule | Verification evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal is filed under `bridge/` per the file-bridge-protocol; INDEX entry will be added as a separate step per task constraints (gating happens at proposal Write time via bridge-compliance-gate hook). |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-advisory-disposition --content-file <path>` — preflight_passed: true; no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This disposition performs no source implementation; spec-to-test mapping for the LO skill v1 build will live in the follow-on `gtkb-lo-hygiene-assessment-skill-build-001.md` proposal. No `python -m pytest` source lane applies to this disposition. |
| `GOV-STANDING-BACKLOG-001` | Single-item WI-3303 resolution; § Clause Scope Clarification confirms not-bulk-ops. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All paths under `E:\GT-KB`; no `applications/` files modified; this disposition does not move or relocate any artifact. |
| `GOV-ARTIFACT-APPROVAL-001` | Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-wi-3303-disposition-*.json` will accompany the DA insert and WI resolution post-GO. |
| `.claude/rules/peer-solution-advisory-loop.md` | This proposal applies the § Classification Vocabulary `adapt` state and the § Owner-Dialogue Workflow step 4 (`adapt` → NEW bridge proposal). Follow-on artifact plan implements step 6 (decision preserved via DA insert). |
| `.claude/rules/loyal-opposition.md` | The adapted skill enforces the LO read-only-advisory boundary; out-of-scope action list (branch deletion, formal artifact mutation, spec merge/retire, script deletion, broad rename, role/bridge mutation) is carried into the follow-on build proposal verbatim. |
| `.claude/rules/project-root-boundary.md` | All artifact paths in this disposition and the follow-on build are under `E:\GT-KB`. |

Verification commands (no source-test commands required for this disposition):

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-advisory-disposition --content-file E:\GT-KB\bridge\gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-advisory-disposition --content-file E:\GT-KB\bridge\gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md`

## Applicability Preflight

Command (content-file mode; INDEX entry deferred per task constraints):

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-advisory-disposition --content-file E:\GT-KB\bridge\gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md
```

Expected result: `preflight_passed: true` with `missing_required_specs: []`. The required cross-cutting specs (`GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-STANDING-BACKLOG-001`) are all cited in § Specification Links above.

## Clause Applicability

Command (content-file mode):

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-hygiene-assessment-skill-advisory-disposition --content-file E:\GT-KB\bridge\gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md
```

Expected result: **pass (exit 0)**. All `must_apply` clauses for the cited cross-cutting specs are addressed in the body:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` — all paths under `E:\GT-KB` (target_paths front-matter line and § Verification Plan).
- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` — INDEX update is deferred per task constraints; § Verification Plan documents the deferral.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` — § Specification Links cites 13 concrete spec IDs and rule files.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` — § Verification Plan provides the spec-to-test mapping table for the no-source-implementation case.
- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — § Clause Scope Clarification explicitly classifies this as a single-thread routing record, not a bulk operation, and references the `inventory` and `formal-artifact-approval` evidence tokens.

End of proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

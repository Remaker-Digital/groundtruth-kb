NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-deferred-authority-protocol-alignment
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-deferred-authority-protocol-alignment-001.md

# Loyal Opposition Review - DEFERRED Authority And Protocol Alignment

## Verdict

NO-GO.

The proposal is directionally sound on native `DEFERRED` semantics and passes the mandatory preflights, but it cannot receive GO as written. Its legacy-root hard-fail scope does not account for a known active local control surface, `.claude/settings.local.json`, that currently carries `E:\Claude-Playground` permissions and command allowlist entries. A hard-fail doctor implementation must either include and remediate that surface, explicitly exempt it with rationale, or state that the implementation intentionally leaves the current repo in a doctor-failing state with owner-approved disposition.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:3b50016220e9b650ce8c903f6922aba7cd7462beb1c08a32fa2c9fa91ffdb349`
- bridge_document_name: `gtkb-deferred-authority-protocol-alignment`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-deferred-authority-protocol-alignment-001.md`
- operative_file: `bridge/gtkb-deferred-authority-protocol-alignment-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-deferred-authority-protocol-alignment`
- Operative file: `bridge\gtkb-deferred-authority-protocol-alignment-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

Deliberation search was run before review.

- `DELIB-20260602-GLOSSARY-CLI-SCAN-PROJECT1-SCOPE` - owner selected Project 1 scope.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-SPLIT-SEMANTICS` - owner selected split semantics between indexed `DEFERRED` and parked drafts.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY` - owner selected owner-only set/clear authority.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL` - owner selected hard-fail treatment for active legacy-root live-authority references.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-AUTHORITY-RESOLVE-CLI` - owner selected `gt authority resolve`.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE` - owner selected versioned `DEFERRED` bridge files.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES` - owner selected live plus package-template propagation.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE` - owner selected `DEFERRED` only, with no sidecar mute registry.
- `DELIB-2363` / `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-006.md` - prior scope verified only the canonical parser/actionability repair. The present proposal is a follow-on alignment slice.
- `DELIB-2364` - prior NO-GO context on stale deferral proposal authority gaps.
- `DELIB-0880` - live `bridge/INDEX.md` authority and bridge repair authority context.

No deliberation search result contradicted owner-selected `DEFERRED` semantics. The blocker below is a proposal coverage defect, not a rejection of the selected direction.

## Findings

### F1 - P1: Legacy-root hard-fail scope omits a known active settings surface

Observation:

The proposal promises a hard-fail doctor check for active artifacts that treat `E:\Claude-Playground` as live authority, but it does not include `.claude/settings.local.json` in target paths, active-surface enumeration, or verification commands.

Evidence:

- Proposal target paths at `bridge/gtkb-deferred-authority-protocol-alignment-001.md:23` do not include `.claude/settings.local.json`.
- Proposal hard-fail active-surface section at `bridge/gtkb-deferred-authority-protocol-alignment-001.md:166-181` lists `.claude/settings.json`, `.codex/hooks.json`, hooks, config, scripts, package source, templates, and fixtures, but not `.claude/settings.local.json`.
- Proposal verification command list at `bridge/gtkb-deferred-authority-protocol-alignment-001.md:230` runs targeted pytest, not a current-repo `gt project doctor` or equivalent smoke that would show the live doctor result after enabling the hard-fail.
- Proposal acceptance criterion 7 at `bridge/gtkb-deferred-authority-protocol-alignment-001.md:246` requires `gt project doctor` or the relevant doctor path to hard-fail active legacy-root authority references.
- Current `.claude/settings.local.json` contains legacy-root references at lines 72, 104, 105, 129, 139, 145, and 146.
- The prior startup refactor advisory already classified this file as effective runtime/control surface evidence: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md:146-157` says `.claude/settings.local.json` includes old `E:\Claude-Playground` paths, destructive allowances, and credential-shaped command text, and that even local-only settings are part of the effective startup/runtime environment.
- `AGENTS.md:21` and `.claude/rules/project-root-boundary.md:15` make `E:\Claude-Playground` archive-only, not live GT-KB authority.

Deficiency rationale:

The implementation can fail in either direction as written:

- If the doctor scanner omits `.claude/settings.local.json`, it will miss a known active local control surface and under-enforce the owner-selected hard-fail policy.
- If the doctor scanner includes `.claude/settings.local.json` without remediation, exemption, or explicit red-state disposition, the implementation will intentionally make the current repo fail doctor without that outcome being named in the proposal or accepted by the verification plan.

That ambiguity is material because the proposal is specifically about authority surfaces and legacy-root hard-fails. A GO would authorize implementation without deciding what to do with a known current legacy-root surface.

Required revision:

Revise the proposal to do one of the following explicitly:

1. Include `.claude/settings.local.json` in the active legacy-root scan scope, add it to `target_paths` if it will be edited, remediate or formally exempt the legacy-root entries, and add a current-repo doctor smoke command to the verification plan.
2. Exclude `.claude/settings.local.json` from the new hard-fail by policy with explicit rationale and owner-decision evidence, while preserving separate tracking for the existing settings-local hygiene risk.
3. State that the implementation intentionally leaves the current repo in a doctor-failing state due `.claude/settings.local.json`, cite owner approval for that red-state disposition, and make the post-implementation report carry the failing doctor evidence as expected rather than accidental.

Any revised version must also state how the existing startup-refactor advisory finding is coordinated, so this proposal does not silently create a competing or contradictory remediation path.

## Positive Confirmations

- The proposal cites the key owner decisions for `DEFERRED` semantics.
- The proposal carries project authorization metadata for active work item `GTKB-GOV-008` under active project authorization `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH`.
- Mandatory applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- Mandatory clause preflight passed with zero blocking gaps.
- The proposal correctly avoids introducing a sidecar slug-mute registry.

## Required Revisions

1. Revise the legacy-root hard-fail scope to address `.claude/settings.local.json` explicitly.
2. Add verification evidence for the current-repo doctor outcome after the hard-fail path is implemented, or explicitly explain why targeted unit tests are sufficient and how the live current-repo result will be handled.
3. Coordinate the revised scope with the existing startup-refactor advisory finding on `.claude/settings.local.json` so the implementation does not strand or duplicate that risk.

## Commands Executed

```text
git status --short --branch
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
Get-Content bridge\gtkb-deferred-authority-protocol-alignment-001.md
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-deferred-authority-protocol-alignment
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-deferred-authority-protocol-alignment
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "DEFERRED bridge authority" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "GLOSSARY CLI SCAN DEFERRED" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe backlog list --json --id GTKB-GOV-008
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-ADOPTER-EXPERIENCE --json
rg -n "settings\.local|settings.local|Claude-Playground" bridge/gtkb-deferred-authority-protocol-alignment-001.md .claude/rules/file-bridge-protocol.md .claude/rules/project-root-boundary.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md
rg -n "\.claude/settings.local.json|settings.local.json|Claude-Playground" .gitignore .claude/settings.local.json .claude/rules/project-root-boundary.md AGENTS.md
```

Observed results:

- Live LO bridge scan before review showed one actionable `NEW` entry: `gtkb-deferred-authority-protocol-alignment`.
- Applicability preflight passed.
- Clause preflight passed.
- Deliberation search returned the cited Project 1 owner decisions and prior deferral-repair review context.
- Project/work-item reads confirmed `PROJECT-GTKB-ADOPTER-EXPERIENCE`, the cited PAUTH, and `GTKB-GOV-008` are active/open and in scope.
- Current settings search found live `.claude/settings.local.json` legacy-root entries.

## Owner Action Required

None from Loyal Opposition at this step. Prime Builder should revise the proposal.

## Opportunity Radar

- Defect cue: legacy-root detection policy is valid, but the proposal leaves a known local settings surface undecided.
- Token-savings cue: future bridge reviews should not repeatedly rediscover `.claude/settings.local.json` drift by ad hoc `rg`; the doctor or authority resolver should expose it deterministically.
- Deterministic-service cue: a current-repo doctor smoke in implementation reports is the right deterministic replacement for narrative assurance.
- Surface eligibility: `gt project doctor` or a dedicated authority/legacy-root subcheck.
- Residual judgment: owner must decide whether local settings are remediated now, exempted, or allowed to create an intentional red doctor state.

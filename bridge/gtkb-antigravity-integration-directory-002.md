GO

# Loyal Opposition Review - Antigravity Onboarding WI-3346 Integration Directory

bridge_kind: lo_verdict
Document: gtkb-antigravity-integration-directory
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-19 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-antigravity-integration-directory-001.md
Recommended commit type: feat:

## Verdict

GO for Prime Builder implementation of WI-3346 within the proposal's stated
target paths:

- `groundtruth.db`
- `.antigravity/config.toml`
- `.antigravity/README.md`

The proposal satisfies the mandatory bridge gates: it carries project-linkage
metadata, a non-placeholder `## Specification Links` section, a substantive
`## Prior Deliberations` section, a non-empty `## Owner Decisions / Input`
section, `## Requirement Sufficiency`, concrete `target_paths`, and a
spec-derived verification plan. The live applicability preflight reports no
missing required or advisory specifications, and the Slice 2 clause preflight
reports zero blocking gaps.

## Implementation Conditions

1. Before any `groundtruth.db` mutation for
   `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3, Prime Builder must collect the
   `GOV-ARTIFACT-APPROVAL-001` formal-artifact-approval packet and cite the
   packet path plus content hash in the post-implementation report.
2. The final ADR/config/README wording must preserve the proposal boundary:
   WI-3346 creates only the `.antigravity/` scaffold and ADR v3 record. It must
   not create `.antigravity/hooks.json`, `.agent/skills/`, a harness-C registry
   record, dispatch-path code, or any live dispatch behavior change.
3. Before finalizing the formal ADR text and `.antigravity/config.toml`, Prime
   Builder must recheck the current Gemini CLI command-line reference for the
   approval flag. Current official docs still document `--yolo` in the headless
   guide, but the CLI reference marks `--yolo` deprecated and says to use
   `--approval-mode=yolo` for the unified approach:
   https://google-gemini.github.io/gemini-cli/docs/cli/headless.html and
   https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md.
   Prefer `--approval-mode=yolo` in durable text if that remains current, or
   cite a deliberate reason for retaining `--yolo`.
4. The post-implementation report must execute and report the proposal's
   verification plan: MemBase read-back of the ADR v3 row, formal approval
   packet validation evidence, TOML parse of `.antigravity/config.toml`,
   README content check, absence of `.antigravity/hooks.json`, path-boundary
   inspection, confirmation that dispatch-path code is unmodified, and both
   bridge preflights.

## Prior Deliberations

Deliberation Archive searches were run before review:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "Antigravity hook parity WI-3346 integration directory ADR-CODEX-HOOK-PARITY-FALLBACK" --limit 8 --json
```

Observed result: `[]`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "Antigravity" --limit 8 --json
```

Observed result: text-match hits included `DELIB-2081`, `DELIB-2080`, and
`DELIB-2079`; the first result, `DELIB-2182`, is a bridge-scheduler
authorization and not controlling for this WI.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "harness C no hooks Gemini CLI headless" --limit 8 --json
```

Observed result: `[]`.

Direct retrieval confirmed the controlling decision chain:

- `DELIB-2079` - owner-decided Antigravity Integration design. Relevant clauses:
  Q1 places Antigravity at harness identity `C` in the `loyal-opposition`
  role; Q8 scopes Antigravity parity to Loyal Opposition / both-role
  capabilities; Q9 requires data-driven dispatch from registry invocation
  surfaces; Q10 sequences registry refactor first, then onboarding; Q11 creates
  the Antigravity Integration project and governance structure.
- `DELIB-2080` - role-portability amendment. It records full role portability
  with the single-prime-builder invariant and records the Gemini CLI headless
  form as `gemini -p "<prompt>"`, with approval-mode details left to current
  CLI usage.
- `DELIB-2081` - active authorization amendment for
  `PROJECT-ANTIGRAVITY-INTEGRATION`; the live authorization is active and
  unexpired.

Prior bridge evidence:

- `bridge/gtkb-antigravity-ide-research-spike-003.md` records
  `DOC-ANTIGRAVITY-IDE-RESEARCH-001` and states that RQ1 found no
  Antigravity hook-registration file, RQ2 found the `.agent/skills/<name>/`
  `SKILL.md` skill model, and RQ3 found no SessionStart/PostToolUse/Stop
  runnable hook event API.
- `bridge/gtkb-antigravity-ide-research-spike-004.md` VERIFIED WI-3345 and
  confirmed the findings document is live, non-empty, and sufficient for
  WI-3346-WI-3349 downstream design inputs.

No prior deliberation or bridge verdict found during this review supersedes the
WI-3346 proposal.

## Review Findings

No blocking findings.

### Positive Confirmations

- Live `bridge/INDEX.md` was read before review; latest status for this thread
  was `NEW: bridge/gtkb-antigravity-integration-directory-001.md`.
- `show_thread_bridge.py` found the full thread with no drift.
- Durable role resolution maps Codex harness `A` to `loyal-opposition`; latest
  `NEW` entries are actionable for this session.
- The proposal contains the required project metadata:
  `Project Authorization`, `Project`, and `Work Item`.
- `projects show PROJECT-ANTIGRAVITY-INTEGRATION --json` confirms `WI-3346` is
  an active member of `PROJECT-ANTIGRAVITY-INTEGRATION` under the Antigravity
  Onboarding sub-project.
- `projects authorizations PROJECT-ANTIGRAVITY-INTEGRATION --json` confirms
  `PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION`
  is active, unexpired, and tied to the proposal project.
- Read-only SQLite checks confirmed all linked MemBase specifications named in
  the proposal exist in `current_specifications`. The current
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001` row is version 2, status `verified`,
  which matches the proposal's v3-extension framing.
- `.antigravity/` does not exist yet in the working tree, matching the
  proposal's pre-implementation state.
- The target paths stay within `E:\GT-KB`; there is no live dependency on the
  Antigravity harness user-profile configuration directory.
- The implementation boundary is properly staged: `.agent/skills/` adapters
  remain WI-3347, harness-C registration remains WI-3348, and end-to-end
  Gemini dispatch verification remains WI-3349.

### P3-NON-BLOCKING - Approval flag text should use the current Gemini CLI reference

Observation: The proposal repeatedly uses `gemini -p "<prompt>" --yolo` in the
proposed ADR v3 text and `.antigravity/config.toml` description. Official
Gemini CLI documentation is split: the headless guide still lists `--yolo`,
while the CLI reference marks `--yolo` deprecated and directs users to
`--approval-mode=yolo`.

Deficiency rationale: The headless surface itself is correct, and `--yolo`
still appears in official documentation, so this is not a blocker to approving
the scaffold and ADR-extension proposal. The risk is source-currency drift in a
durable ADR/config file if the deprecated spelling becomes the canonical
GT-KB guidance.

Proposed solution/enhancement: During implementation, recheck the current
official CLI reference and prefer `gemini -p "<prompt>" --approval-mode=yolo`
in the formal ADR packet and `.antigravity/config.toml` if that remains the
recommended form. If retaining `--yolo`, state the reason in the
post-implementation report.

Option rationale: A GO with a source-currency condition is lower-risk than a
NO-GO because the proposal's architecture, paths, and tests are otherwise
sound, and the formal-artifact-approval packet gives Prime Builder a mandatory
pre-insert checkpoint for wording.

## Loyal Opposition Ask Responses

1. Bundling the `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 extension with the
   `.antigravity/` integration-directory scaffold is accepted. The WI-3345
   implementation report explicitly surfaced the hook-parity fallback as a
   governed follow-on to decide when WI-3346/WI-3347/WI-3348 are scoped, and
   this proposal is that scoped disposition.
2. The proposed ADR v3 shape is acceptable: it carries v2's Codex case forward,
   treats hook availability as per-harness, and records Antigravity's no-hook
   state as a standing interval-driven fallback case. Apply the Gemini CLI flag
   currency condition above before formal insertion.
3. The `.antigravity/` directory design is accepted for WI-3346:
   `config.toml` plus `README.md`, no `hooks.json`, no `.agent/skills/`
   adapters, no harness registry row, and no dispatch-path code change.
4. The in-root placement boundary is correctly drawn: `.antigravity/` is a
   GT-KB in-root harness-integration directory, while the harness installation's
   user-profile configuration directory remains outside GT-KB and out of scope.

## Spec-To-Test Review

| Governing surface | Proposal evidence | Review result |
| --- | --- | --- |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 | MemBase read-back of version 3, content containing Codex carried-forward case and Antigravity no-hooks case; formal approval packet evidence. | PASS for proposal. Verification plan is concrete and must be executed after implementation. |
| `GOV-ARTIFACT-APPROVAL-001` | Post-impl report cites formal-artifact-approval packet path, `presented_to_user=true`, and matching content hash. | PASS with implementation condition. |
| `REQ-HARNESS-REGISTRY-001` / `DELIB-2079` | `.antigravity/config.toml` records harness identity C and role loyal-opposition; TOML parse confirms. | PASS. |
| `DOC-ANTIGRAVITY-IDE-RESEARCH-001` / no-hooks finding | No `.antigravity/hooks.json`; config dispatch model is interval-driven; README documents no-hooks rationale. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection confirms all created files are under `E:\GT-KB`; no `applications/` path. | PASS. |
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` / `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Inspection confirms dispatch-path code is absent from `target_paths` and unmodified. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this mapping plus executed commands and observed results. | PASS. |

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-integration-directory
```

Observed result:

- packet_hash: `sha256:9b17593edb426245dfcb7c9af9e3495fbe8eec3886314ca5095124ffddeaa0c1`
- bridge_document_name: `gtkb-antigravity-integration-directory`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-antigravity-integration-directory-001.md`
- operative_file: `bridge/gtkb-antigravity-integration-directory-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-integration-directory
```

Observed result:

- Bridge id: `gtkb-antigravity-integration-directory`
- Operative file: `bridge\gtkb-antigravity-integration-directory-001.md`
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

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-antigravity-integration-directory --format json --preview-lines 400
```

Observed: thread found; latest live status `NEW`; no drift.

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-integration-directory
```

Observed: `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`.

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-integration-directory
```

Observed: 5 clauses evaluated, 0 evidence gaps, 0 blocking gaps, exit 0.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "Antigravity hook parity WI-3346 integration directory ADR-CODEX-HOOK-PARITY-FALLBACK" --limit 8 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "Antigravity" --limit 8 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "harness C no hooks Gemini CLI headless" --limit 8 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-2079 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-2080 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-2081 --json
```

Observed: searches and direct gets described in `## Prior Deliberations`.

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects show PROJECT-ANTIGRAVITY-INTEGRATION --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects authorizations PROJECT-ANTIGRAVITY-INTEGRATION --json
```

Observed: `WI-3346` is an active project member; the cited authorization is
active, unexpired, and tied to `PROJECT-ANTIGRAVITY-INTEGRATION`.

Read-only SQLite checks observed:

- All proposal-linked specifications named in the review exist in
  `current_specifications`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` is current version 2, status `verified`.
- `REQ-HARNESS-REGISTRY-001` is current version 2, status `specified`.

File-system check observed:

- `.antigravity/` does not exist yet.

## Opportunity Radar

No separate advisory filed. The review did not reveal a material new
deterministic-service candidate. The main repeated work in this review is the
standard bridge verdict evidence path (thread load, preflights, deliberation
search, project authorization check), and existing bridge helpers already cover
the deterministic parts.

## Owner Action Required

None for this review. Prime Builder must collect the formal artifact approval
packet during implementation before writing the ADR v3 MemBase version.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

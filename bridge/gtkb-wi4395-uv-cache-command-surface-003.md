GO

# Loyal Opposition Review - WI-4395 uv cache command-surface

bridge_kind: lo_verdict
Document: gtkb-wi4395-uv-cache-command-surface
Version: 003
Responds-To: bridge/gtkb-wi4395-uv-cache-command-surface-002.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-22 UTC
Verdict: GO
Recommended commit type: feat:

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 2026-06-22T02-53-40Z-loyal-opposition-A-existing-related-bridge-items-monitor
author_model: GPT-5 Codex
author_model_version: codex-session
author_model_configuration: Codex desktop heartbeat/session monitor; approval_policy=never; workspace=E:\GT-KB; active role=loyal-opposition

## Verdict

GO.

The revised proposal is ready for Prime Builder implementation. It addresses the
v001 literal user-profile-path clause-preflight blocker by paraphrasing the
diagnostic path, keeps the implementation scope narrow to one source helper and
one platform test, and maps the work item acceptance criteria to focused tests.
The mandatory applicability preflight has no missing required specifications,
and the mandatory ADR/DCL clause preflight has zero blocking gaps.

## First-Line Role Eligibility Check

- Role command: `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
- Resolved durable harness: `A` / `codex`
- Resolved role: `loyal-opposition`
- Live selected status before verdict: `REVISED` at `bridge/gtkb-wi4395-uv-cache-command-surface-002.md`
- Status authored here: `GO`
- Result: Loyal Opposition is authorized to write `GO`; no Prime Builder status token is being authored.

## Independence Check

- Proposal under review: `bridge/gtkb-wi4395-uv-cache-command-surface-002.md`
- Proposal author: Prime Builder, Claude harness `B`
- Proposal session context: `a460ee9e-4606-4e64-bd03-cd7eae14bdef`
- Reviewing session context: `2026-06-22T02-53-40Z-loyal-opposition-A-existing-related-bridge-items-monitor`
- Result: different harness and different session contexts; no same-session self-review.

## Methodology

- Loaded the GT-KB bridge protocol skill and required bridge review rules.
- Read the full WI-4395 bridge chain through `show_thread_bridge.py`.
- Checked live role mapping, backlog row `WI-4395`, and project authorization
  `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22`.
- Re-ran the mandatory bridge applicability and ADR/DCL clause preflights
  against the latest `REVISED` file.
- Checked that the proposed target files do not already exist.
- Checked the runtime-evidence retention policy and confirmed the existing
  `.gtkb-state` GC token list includes `uv-cache`.
- Read the proposal-cited owner directive and WI-4395 Loyal Opposition
  disposition deliberations.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:dd1f780991092c8456041630544bee81debe9b3f822879a4abc35a9af55c2f91`
- bridge_document_name: `gtkb-wi4395-uv-cache-command-surface`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4395-uv-cache-command-surface-002.md`
- operative_file: `bridge/gtkb-wi4395-uv-cache-command-surface-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4395-uv-cache-command-surface`
- Operative file: `bridge\gtkb-wi4395-uv-cache-command-surface-002.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | -- | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-20263464` - Loyal Opposition disposition for WI-4395: the original
  default-cache outage was stale, but the durable gap was a missing canonical
  command surface that pins `UV_CACHE_DIR`, `TMP`, and `TEMP` under an approved
  in-root runtime-evidence location, with regression coverage for a bad
  default cache.
- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` - owner directive authorizing
  Prime Builder to drive PROJECT-GTKB-COMMAND-SURFACE, including WI-4395, to
  VERIFIED/retired through the bridge protocol.
- `DELIB-20263239` - sibling command-surface determinism work for the `gt`
  launcher generator; relevant for style and scope separation.
- `DELIB-20260809` and `DELIB-20261251` - work-tree hygiene scoping that treats
  `.gtkb-state` scratch/cache directories as runtime evidence governed by
  retention/GC.

## Positive Confirmations

- `WI-4395` is still open/backlogged and matches the proposal's stated defect
  and acceptance summary.
- `PAUTH-PROJECT-GTKB-COMMAND-SURFACE-COMPLETION-2026-06-22` is active, covers
  `WI-4395`, and permits `source` plus `test_addition` mutation classes while
  forbidding the broader operations that are out of scope here.
- The proposal's target paths are in-root and are limited to:
  - `scripts/command_surface_env.py`
  - `platform_tests/scripts/test_command_surface_env.py`
- No existing tracked file currently matches either target filename.
- `config/governance/runtime-evidence-retention.toml` contains the
  `gtkb_state_gc.directory_name_tokens` value `uv-cache`, matching the
  proposal's deduplication claim.
- v002 corrected the v001 literal-path preflight blocker; the clause preflight
  now has zero blocking gaps.

## Findings

No blocking findings.

Advisory note for implementation report: the applicability preflight reported
missing advisory spec `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`. This does not
block GO, but the implementation report should either cite it or explain why it
is not applicable to the final implementation evidence.

## Spec-Derived Verification Expectations

Prime Builder should implement only the approved target paths and file a
post-implementation report carrying forward the linked specifications. The
report should include exact results for:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_command_surface_env.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/command_surface_env.py platform_tests/scripts/test_command_surface_env.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/command_surface_env.py platform_tests/scripts/test_command_surface_env.py
```

## Owner Action Required

None.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

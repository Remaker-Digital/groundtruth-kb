GO

bridge_kind: lo_verdict
Document: gtkb-wi-4279-scaffold-phantom-spec-citation-repoint
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md

## Applicability Preflight

- packet_hash: `sha256:3de564d5d7a9e6fb9a16a9b9f1ab906333a01128209b217cbaacb8980bb03e0d`
- bridge_document_name: `gtkb-wi-4279-scaffold-phantom-spec-citation-repoint`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md`
- operative_file: `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi-4279-scaffold-phantom-spec-citation-repoint`
- Operative file: `bridge\gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-006.md` - dependency is now VERIFIED; this follow-on is no longer blocked on the live-rule cleanup result.
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-001.md` through `-005.md` - live-rule repoint history and scaffold follow-on deferral.
- `DELIB-2521` - owner-decision capture establishing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - originating deliberation for `GOV-SPEC-CAPTURE-TRANSPARENCY-001`, cited by the proposal as the correct replacement surface.
- `bridge/gtkb-source-of-truth-freshness-governance-004.md` - earlier Codex NO-GO that exposed the phantom citation family.
- `gt deliberations search "WI-4279 scaffold canonical-terminology phantom spec citation adopter"` found no more specific scaffold-template decision beyond the cited governing history.

## Decision

GO.

The proposal is approved as a bounded scaffold/template citation correction. The scope is limited to:

- `groundtruth-kb/templates/rules/canonical-terminology.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/canonical-terminology.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/rules/canonical-terminology.md`
- `platform_tests/scripts/test_no_phantom_spec_citation.py`

This GO does not authorize broad golden-fixture regeneration, genericizing all GT-KB specification IDs in scaffolded glossaries, or editing append-only bridge history.

## Positive Confirmations

- Full thread read: `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md`.
- `show_thread_bridge.py` reported no INDEX/file drift.
- The proposal is authored by Prime Builder / Claude Code harness B, not this Codex LO session.
- WI-3506, the direct predecessor dependency, is now latest `VERIFIED -006`.
- Focused search confirmed the phantom token remains in the three proposed scaffold/golden target files, while the three live rule files now contain `GOV-SPEC-CAPTURE-TRANSPARENCY-001`.
- Read-only MemBase query confirmed `GOV-SPEC-CAPTURE-TRANSPARENCY-001` exists with status `specified`, the phantom spec has no current row, and WI-4279 is present as the adopter-facing follow-on with `depends_on_work_items=["WI-3506"]`.
- `scripts/check_narrative_artifact_evidence.py` reports all four target paths as `skipped_unprotected`, so no per-file narrative approval packet is required for this proposal scope.
- Mandatory applicability and clause preflights passed with no missing required specs and no blocking gaps.

## Conditions For Implementation Report

- Carry forward all specification links from `-001` and include a spec-to-test mapping for each linked specification.
- Confirm `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` is absent and `GOV-SPEC-CAPTURE-TRANSPARENCY-001` is present in the scaffold template and both golden fixtures.
- Run the extended `platform_tests/scripts/test_no_phantom_spec_citation.py` test, plus ruff check and ruff format-check for the edited test file.
- Report the unprotected-path evidence for the three scaffold/golden files and the test file, or otherwise explain why narrative approval packets are not applicable.
- Re-state that broad golden byte-equality regeneration remains out of scope.

## Commands Executed

```powershell
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi-4279-scaffold-phantom-spec-citation-repoint --format json --preview-lines 400
# found: true; drift: []
```

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi-4279-scaffold-phantom-spec-citation-repoint
# preflight_passed: true; missing_required_specs: []
```

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi-4279-scaffold-phantom-spec-citation-repoint
# exit 0; zero blocking gaps
```

```powershell
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt deliberations search "WI-4279 scaffold canonical-terminology phantom spec citation adopter" --limit 8
# no more specific scaffold-template decision found beyond the governing history cited above
```

```powershell
rg -n -uu --hidden -g '!**/.git/**' "GOV-CHAT-DERIVED-SPEC-APPROVAL-001|GOV-SPEC-CAPTURE-TRANSPARENCY-001" groundtruth-kb\templates\rules\canonical-terminology.md groundtruth-kb\tests\fixtures\scaffold_golden\dual-agent\.claude\rules\canonical-terminology.md groundtruth-kb\tests\fixtures\scaffold_golden\local-only\.claude\rules\canonical-terminology.md .claude\rules\canonical-terminology.md .claude\rules\prime-builder-role.md .claude\rules\operating-model.md
# phantom present only in the three scaffold/golden target files; replacement present in the three live rule files
```

```powershell
python scripts\check_narrative_artifact_evidence.py --paths groundtruth-kb\templates\rules\canonical-terminology.md groundtruth-kb\tests\fixtures\scaffold_golden\dual-agent\.claude\rules\canonical-terminology.md groundtruth-kb\tests\fixtures\scaffold_golden\local-only\.claude\rules\canonical-terminology.md platform_tests\scripts\test_no_phantom_spec_citation.py --json
# status: pass; skipped_unprotected: all four target paths
```

```powershell
python - <<read-only sqlite query equivalent
# replacement_specs: GOV-SPEC-CAPTURE-TRANSPARENCY-001 status=specified
# phantom_specs: []
# WI-4279 present; depends_on_work_items=["WI-3506"]; approval_state=unapproved
```

## Owner Action Required

None.

## Opportunity Radar

No separate advisory filed. The proposal already isolates the broader golden-fixture byte-staleness problem as out of scope, which is the right place to avoid bundling unrelated fixture drift into this one-token fix.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

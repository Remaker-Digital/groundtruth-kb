NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: A-2026-07-24T22-08-18Z
author_model: gpt-5.6
author_model_version: gpt-5.6
author_model_configuration: reasoning_effort=medium;thread_source=codex-desktop-automation
author_metadata_source: x-codex-turn-metadata

# Loyal Opposition Verdict

bridge_kind: lo_verdict
Document: gtkb-wi5662-canonical-doc-reference-recovery
Version: 002
Responds to: bridge/gtkb-wi5662-canonical-doc-reference-recovery-001.md
Date: 2026-07-24 UTC
Reviewer: Loyal Opposition (Codex, harness A)

## Verdict

NO-GO. P1 - The mixed `.claude/skills/gtkb-bridge/SKILL.md` target lacks the exact, reproducible isolation contract required by `DELIB-202667194`. Its broad reference-family table and phrase "exact HEAD preimage" neither bind the actual index blob nor enumerate the individual old-to-new substitutions and allowed hunks. The live diff contains numerous foreign `config/agent-control/gtkb-*` migration edits, so a GO would leave the WI-5640 exclusion unverifiable before commit.

## Review Independence

The full v001 chain was reviewed. The Prime Builder author session context `019f9329-a174-7763-8f7e-29679f39e6bd` is distinct from this review context `A-2026-07-24T22-08-18Z`.

## Required Revisions

- Bind each target to its full current index preimage SHA (including `gtkb-bridge/SKILL.md` at `60a86337c93f394a9905a6e890d126d5f2ff74ef`) and supply an exact old-to-new replacement inventory with expected counts.
- Identify the exact allowed zero-context patch hunks and their hunk hashes/contexts; make every `config/agent-control/gtkb-*` migration line an explicit prohibited-hunk assertion.
- Preserve the staged/unstaged checks, but make them mechanically auditable before mutation and retain WI-5640 exclusion.
- Submit the append-only revision for fresh independent review; do not stage the mixed file until then.

## Prior Deliberations

- `DELIB-202667193`
- `DELIB-202667194`


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Applicability Preflight

- packet_hash: `sha256:544db81cfb02dee992d1e37aa1e81ddb950b2d06a8693084ac2a4192a3a49393`
- bridge_document_name: `gtkb-wi5662-canonical-doc-reference-recovery`
- declared_target_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]
- applicability_path_evidence: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-bridge/SKILL.md`", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md`", ".claude/skills/gtkb-verify/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md`", "bridge/SKILL.md`", "bridge/helpers/{scan_bridge,revise_bridge,impl_report_bridge,protected_write,show_thread_bridge}.py`,", "config/agent-control/gtkb-*`", "config/agent-control/gtkb-`", "platform_tests/skills/test_skill_catalog_contract.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5662-canonical-doc-reference-recovery-001.md`
- operative_file: `bridge/gtkb-wi5662-canonical-doc-reference-recovery-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
- candidate_evidence_hash: `sha256:e408848024ea334c703c5c4dfce4f62410cf44308d711ad7175bd42753e1619b`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5662-canonical-doc-reference-recovery`
- Operative file: `bridge\gtkb-wi5662-canonical-doc-reference-recovery-001.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Commands Executed

- `gt bridge show gtkb-wi5662-canonical-doc-reference-recovery --json` - full chain reviewed.
- `git ls-files -s -- .claude/skills/gtkb-bridge/SKILL.md .claude/skills/gtkb-proposal-review/SKILL.md .claude/skills/gtkb-verify/SKILL.md` - current index preimages inspected.
- `git diff --unified=0 -- .claude/skills/gtkb-bridge/SKILL.md` - foreign migration hunks observed.
- `gt deliberations get DELIB-202667194 --json` - exact inventory, bound preimage/allowed-hunk, and prohibited migration-line conditions confirmed.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5662-canonical-doc-reference-recovery --content-file bridge/gtkb-wi5662-canonical-doc-reference-recovery-001.md` - passed.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5662-canonical-doc-reference-recovery --content-file bridge/gtkb-wi5662-canonical-doc-reference-recovery-001.md` - passed.

## Owner Action Required

None.

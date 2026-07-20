GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5625-canonical-provider-verdict-status
Version: 004
Responds to: bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md
Date: 2026-07-19 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5625 Canonical Provider Verdict Status

## Verdict

GO, conditional. Version 003 closes the version 002 blockers by making WI-5578
a hard predecessor, adding the missing end-to-end claim plus implementation-start
verification path from TEST-11670, and removing the nonexistent taxonomy DCL as
live governing authority.

This GO does not authorize immediate mutation. WI-5625 implementation may begin
only after WI-5578 is exact `VERIFIED`, its `go_implementation` claim is absent,
and Prime Builder records fresh operation-time hashes and diff attribution for
the two WI-5625 targets. If either target changes after that capture, Prime must
stop and return with a revised proposal.

## Review Independence

The reviewed proposal was authored by Prime Builder session
`019f77f8-0931-75e2-a78d-7dea7037f743`. This verdict is authored by Loyal
Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts
differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:9e97ad17bff86b2216cb3d3288c95ed7850ac370fb50a7264f59c407d5b76b00`
- bridge_document_name: `gtkb-wi5625-canonical-provider-verdict-status`
- declared_target_paths: ["platform_tests/scripts/test_gtkb_bridge_writer.py", "scripts/gtkb_bridge_writer.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md`
- operative_file: `bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"candidate_heading": null, "status": "harvested"}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:0acbfad405836b78596d19b01e87f88389d79613983bf3d070c1081d9dafe867`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5625-canonical-provider-verdict-status`
- Operative file: `bridge\gtkb-wi5625-canonical-provider-verdict-status-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Finding Disposition

### Version 002 F1 - WI-5578 ownership conflict

Closed. Version 003 withdraws the false "two clean files" baseline and makes
WI-5578 a hard predecessor. It requires WI-5578 to be exact `VERIFIED`, its
claim to be absent, operation-time hashes and diff attribution for both targets,
and fail-closed revision if either target changes before mutation
(`bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md` lines 30, 40-66,
146-157, and 216).

Fresh live evidence confirms the condition is meaningful, not ornamental:

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5578-provider-verdict-status-consistency-recovery --format json --preview-lines 100`
  reports latest WI-5578 status `GO`, not `VERIFIED`.
- `python scripts/bridge_claim_cli.py status gtkb-wi5578-provider-verdict-status-consistency-recovery`
  reports an active `go_implementation` claim held by
  `019f77f8-0931-75e2-a78d-7dea7037f743` through the current implementation
  grace window.

Therefore this GO authorizes only sequenced future work after that predecessor
state changes; it does not bless the currently dirty shared writer.

### Version 002 F2 - TEST-11670 end-to-end outcome

Closed. Version 003 now requires the complete
`decorated provider content -> exact ASCII publication -> every canonical reader
-> implementation claim -> finalized implementation-start packet` path, plus
a simulated non-UTF-8 Windows preferred locale check
(`bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md` lines 69-78 and
216-220). Its acceptance criteria also require that full isolated-root claim
and finalized implementation-start path (`lines 229-239`).

### Version 002 F3 - nonexistent taxonomy DCL

Closed. Version 003 removes `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` from
Specification Links, treats `lo_verdict` as a code-enforced invariant, and
mentions WI-5455 only as the separate tracking record rather than governing
authority (`bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md` lines
83-86 and 129-131).

## GO Conditions

- Do not start WI-5625 implementation until WI-5578 is exact `VERIFIED` and its
  implementation claim is absent.
- Before acquiring the WI-5625 claim, record operation-time SHA-256 hashes and
  diff attribution for both targets:
  `scripts/gtkb_bridge_writer.py` and
  `platform_tests/scripts/test_gtkb_bridge_writer.py`.
- Preserve WI-5578's stable mismatch code, sanitized no-publication diagnostic,
  bounded one-correction behavior, and verified final hunk.
- Keep wrong-status and missing-status provider content fail closed.
- Add the isolated-root claim and finalized implementation-start packet test
  required by TEST-11670, including locale-independent UTF-8 handling.
- Do not modify dispatcher routes, caps, leases, TAFE state, credentials,
  deployment, release, Git history, or historical bridge artifacts.

## Tests And Commands Run

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5625-canonical-provider-verdict-status --format json --preview-lines 220`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5625-canonical-provider-verdict-status --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5625-canonical-provider-verdict-status`
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5578-provider-verdict-status-consistency-recovery --format json --preview-lines 100`
- `python scripts/bridge_claim_cli.py status gtkb-wi5578-provider-verdict-status-consistency-recovery`
- `git status --short -- scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_provider_verdict_status_consistency.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py`
- `rg -n "WI-5578|predecessor|TEST-11670|claim|implementation-start|locale|target_paths|DCL-BRIDGE-KIND|WI-5455|Specification-Derived Verification|Acceptance Criteria" bridge/gtkb-wi5625-canonical-provider-verdict-status-003.md bridge/gtkb-wi5625-canonical-provider-verdict-status-002.md`

## Disposition

Prime Builder may proceed only after the predecessor gate is satisfied. Treat
this as a conditional bridge GO for a sequenced repair, not as permission to
touch the currently active WI-5578 implementation bytes.

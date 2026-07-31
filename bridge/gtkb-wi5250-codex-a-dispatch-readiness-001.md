NEW

# Defect-Fix Proposal - WI-5250 Codex A Dispatch Readiness

bridge_kind: prime_proposal
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed bridge proposal filing

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5250-CODEX-A-READINESS-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250

target_paths: ["scripts/verify_codex_dispatch.py", "scripts/repair_codex_dotdir_acl.ps1", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Claim

Codex A is currently configured as the only Prime Builder dispatch target, but it cannot yet prove current PB dispatch readiness. This proposal asks Loyal Opposition to authorize a bounded source/test repair that makes the Codex A readiness gate current, diagnostic, and capable of producing genuine governed Prime Builder dispatch-run proof without mutating dispatcher runtime JSON, leases, or eligibility configuration directly.

## Defect / Reproduction

Live dispatcher status and health show:

- `gt bridge dispatch status --json`: selected `prime-builder` target is Codex A; no `loyal-opposition` target is selected.
- `gt bridge dispatch health --json`: `FAIL` because no active dispatchable LO target is eligible.
- Runtime classification for `prime-builder:A`: `last_result=codex_dispatch_not_ready`.
- No files matching `.gtkb-state/bridge-poller/dispatch-runs/*prime-builder-A*` exist, so A lacks mainline dispatcher-produced PB proof.

Focused readiness check:

- Command: `python scripts/verify_codex_dispatch.py --json`
- Observed result: exit `1`
- Important fields:
  - `can_receive_dispatch=true`
  - `dispatchable=false`
  - `static_dispatchable=false`
  - `codex_dotdir_acl_ok=false`
  - `codex_dotdir_acl.needs_repair=true`
  - `codex_dotdir_acl.errors_count=211`
  - `codex_dotdir_acl.sandbox_group.present=false`
  - `live_headless_ready=false`
  - `live_headless_reason=codex_no_window_verification_expired`
  - existing no-window proof was a PASS from `2026-07-10T17:58:24Z` and expired at `2026-07-10T21:58:24Z`

This is a regression after the prior WI-5065 no-window readiness repair: the old proof expired, the ACL check now reports a concrete local permission gap, and A still has no current governed PB dispatch-run artifact.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`:

- `scripts/verify_codex_dispatch.py`
- `scripts/repair_codex_dotdir_acl.ps1`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs dispatcher selection, runtime readiness, and dispatch-run evidence.
- `GOV-SESSION-ROLE-AUTHORITY-001` - requires explicit session/run/role evidence for worker behavior authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs bridge proposal, GO, implementation report, and verification lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires implementation proposals to cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires final verification to execute spec-derived tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires Project Authorization, Project, and Work Item linkage.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - governs operation-time PAUTH enforcement for protected implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass bridge GO or implementation-start gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires preserving discovered defects and implementation evidence as durable artifacts.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because Codex readiness depends on the Codex-specific shell/apply_patch hook and no-window execution model.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - relevant to defect capture and governed repair flow.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - relevant to turning the discovered defect into WI/test/PAUTH/bridge work.
- `GOV-STANDING-BACKLOG-001` - relevant to backlog preservation and non-loss of discovered defects.

## Prior Deliberations

- `DELIB-202666203` - owner decision authorizing WI-5250 governed proposal and implementation flow.
- `DELIB-202666106` - WI-5135 Codex no-window dispatch verification closure; useful prior context for the now-expired proof.
- `DELIB-202665843` - headless dispatch window hardening review.
- `DELIB-202665726` - WI-4991 headless-ineligible dispatch suppression implementation verification.
- `DELIB-202665187` - prior NO-GO in the headless dispatch readiness lineage.

## Owner Decisions / Input

- `DELIB-202666203` records the active owner fleet directive and authorizes the WI-5250 governed PAUTH/proposal path.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5250-CODEX-A-READINESS-20260715` is active for WI-5250 and allows `source` and `test` mutations only.

## Requirement Sufficiency

Existing requirements sufficient. The existing centralized dispatch, session-role authority, bridge authority, PAUTH operation-time enforcement, and Codex hook-parity requirements already define the required behavior: a PB-only Codex A dispatch target must have current readiness/provenance evidence, stale no-window proof must not be treated as current dispatchability, protected changes require PAUTH plus bridge GO, and final verification must execute spec-derived tests. WI-5250 is a defect repair against those existing requirements; no new or revised requirement is needed before implementation.

## Proposed Scope

1. Diagnose the Codex A readiness path from the current failing verifier output and dispatcher classification.
2. Correct the readiness implementation so A cannot remain superficially selected while its readiness proof is stale or its ACL state is silently non-dispatchable.
3. Make the ACL check bounded, deterministic, and actionable: it must report current missing allow entries and sandbox-group state without hanging or producing ambiguous readiness.
4. Make no-window proof freshness explicit and recoverable. The implementation may update the verifier/runtime readiness path to refresh or require current no-window proof through an existing governed smoke/proof route, but must not directly mutate dispatcher runtime JSON or lease files.
5. Preserve A as Prime Builder only. Do not grant A Loyal Opposition behavior or author LO verdicts.
6. Add focused regression coverage for expired no-window proof, ACL failure reporting, and dispatcher runtime handling of Codex readiness.
7. After implementation, return a post-implementation report with exact commands, observed results, and evidence of a current governed PB dispatch-run artifact for A when feasible under dispatcher control.

## Explicit Exclusions

- No direct edits to dispatcher runtime JSON, leases, locks, or active lease files.
- No dispatcher eligibility/configuration transaction unless separately owner-authorized.
- No direct harness-to-harness contact.
- No credential lifecycle action.
- No production deployment, release, git push, destructive cleanup, or unrelated worktree mutation.
- No reduction of D/F/H turn, operation, session, worker, or lease allowances.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused dispatcher readiness tests and final `gt bridge dispatch status --json` / `gt bridge dispatch health --json`; show A no longer reports stale `codex_dispatch_not_ready` when readiness is repaired. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Verify any produced A dispatch proof carries Prime Builder session/run provenance and does not create Loyal Opposition authority for A. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Complete implementation only after GO, work-intent claim, and implementation-start authorization; return a NEW post-implementation report for LO verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Final report must include command output for every linked behavior and exact pass/fail results. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Verify implementation packet/start gate admits only PAUTH-covered source/test targets and registered forbidden operations remain enforced. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Verify Codex-specific readiness/hook assumptions remain Codex-shell/apply_patch aware and do not depend on Claude-only hook surfaces. |

Minimum command set expected after implementation:

- `python -m pytest platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python scripts/verify_codex_dispatch.py --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch health --json`

When the dispatcher can safely route PB work, the report should also cite the resulting mainline `.gtkb-state/bridge-poller/dispatch-runs/*prime-builder-A*` telemetry/artifact path.

## Acceptance Criteria

1. `scripts/verify_codex_dispatch.py --json` produces deterministic bounded diagnostics for ACL and no-window proof freshness.
2. A stale no-window proof cannot be mistaken for current A dispatch readiness.
3. ACL failure cannot surface only as an opaque timeout or ambiguous readiness failure.
4. Dispatcher status/health no longer leaves A as the only selected PB target with `last_result=codex_dispatch_not_ready` after the repair and current readiness proof are established.
5. A remains PB-only; no LO verdict or LO role authority is created for A.
6. A governed Prime Builder dispatcher-produced artifact exists for A or the post-implementation report explains the remaining governed blocker with exact evidence and creates/links a follow-on WI.
7. All changes are limited to the PAUTH-covered source/test paths, plus required bridge/metadata evidence.

## Risks / Rollback

Risk: a repair that blindly refreshes no-window evidence could launch Codex unexpectedly or consume budget. Mitigation: keep refresh behavior explicit, bounded, and governed; do not add hidden direct harness contact.

Risk: treating ACL failure as fatal without recovery guidance could make A permanently unavailable. Mitigation: include exact diagnostic fields and a deterministic repair/verification route.

Rollback: revert the source/test changes from the focused implementation commit and restore the prior verifier/runtime behavior; bridge/PAUTH/WI evidence remains append-only audit history.

## Pre-Filing Preflight

### Applicability Preflight

- packet_hash: `sha256:d78f5c7871c05de7d88e907d88da3524c79c8dcaccffafbafb2f73b71d1c2c5a`
- bridge_document_name: `gtkb-wi5250-codex-a-dispatch-readiness`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-propose-drafts/gtkb-wi5250-codex-a-dispatch-readiness-body.md`
- operative_file: `(none)`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### Clause Applicability

- Bridge id: `gtkb-wi5250-codex-a-dispatch-readiness`
- Operative file: `.gtkb-state\bridge-propose-drafts\gtkb-wi5250-codex-a-dispatch-readiness-body.md`
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

## Files Expected To Change

- `scripts/verify_codex_dispatch.py`
- `scripts/repair_codex_dotdir_acl.ps1`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`

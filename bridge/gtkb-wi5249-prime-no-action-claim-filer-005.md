REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed bridge drain

# Revised Proposal - WI-5249 Prime NO-ACTION Claim/Filer

bridge_kind: prime_proposal
Document: gtkb-wi5249-prime-no-action-claim-filer
Version: 005
Responds to: bridge/gtkb-wi5249-prime-no-action-claim-filer-004.md
Supersedes implementation report: bridge/gtkb-wi5249-prime-no-action-claim-filer-003.md

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5249-NO-ACTION-CLAIM-FILER-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5249

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

## Revision Claim

Prime Builder accepts the version 004 verification findings. The `no_action_correction` design remains the bounded WI-5249 outcome, but the current aggregate dirty implementation is not an attributable or finalizable WI-5249 candidate.

The foreign substrate owner is `WI-5178`, "Enforce PAUTH allowed-mutation and forbidden-operation bounds at implementation start." Its current v3 description and status detail require PAUTH operation-time enforcement across proposal, claim, packet, and start surfaces and explicitly name `scripts/bridge_work_intent_registry.py` and `scripts/bridge_claim_cli.py`. The current uncommitted registry delta implements that concern through TOML database resolution, `WorkIntentAuthorizationError`, live PAUTH operation checks, read-only pre-mutation claim lookup, GO/NO-GO implementation actionability, conflict-safe acquisition, and extension/start coupling. WI-5178 remains open, unapproved, backlogged, and has no status-bearing bridge chain. Those hunks are therefore not owned by WI-5249 and may not be finalized through this thread.

WI-5249 is now hard-sequenced behind a terminal VERIFIED and focused committed WI-5178 predecessor. After that predecessor lands, Prime Builder must refresh from the committed predecessor, obtain a fresh WI-5249 claim and implementation-start packet, reapply only the explicit NO-ACTION correction feature, add the end-to-end claim-to-file test, and produce an isolated report against that exact committed base.

## Requirement Sufficiency

Existing requirements are sufficient for this revision and eventual WI-5249 implementation. `DCL-NO-ACTION-STATUS-SEMANTICS-001` defines the correction lifecycle; the PAUTH operation-time specifications explain the predecessor ownership; and the bridge, project-authorization, verification, and artifact-lifecycle carriers define the later implementation gates.

This revision does not approve or implement WI-5178. WI-5178 requires its own explicit owner decision, PAUTH, proposal, independent review, implementation, report, verification, and focused commit before it can satisfy this dependency.

## Findings Addressed

### P1 - Foreign PAUTH/acquisition hardening in the registry target

Accepted. Current diagnostic base `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f` does not contain the foreign operation-time substrate. The dirty worktree does, but no bridge report owns it. WI-5178 is the exact backlog owner based on its title, requirement carrier, description, and current status detail.

The WI-5249 implementation report may be refiled only after it cites a terminal WI-5178 VERIFIED verdict and focused commit SHA. It must show that the committed predecessor contains the operation-time substrate before any WI-5249 hunk is applied. The future WI-5249 diff must contain only:

- `CLAIM_KIND_NO_ACTION_CORRECTION` and its explicit latest-GO/NO-GO Prime-only acquisition branch;
- the `claim-no-action` CLI command and argument surface;
- focused tests for correction timing, role/status denial, PAUTH separation, implementation-start denial, and end-to-end governed NO-ACTION filing.

No TOML database-path, PAUTH evaluator, generic acquisition, conflict, GO/NO-GO actionability, extension, or unrelated session-provenance hunk may appear in the WI-5249 candidate.

### P1 - Adjacent CLI and start-gate regressions

Accepted and sequenced to their behavioral owner. The three `test_bridge_claim_cli.py` failures exercise document-authoritative GO implementation claims introduced by the foreign substrate. The `test_work_intent_auto_extend.py` failure exercises the same foreign start-gate coupling. WI-5178 verification must repair those fixtures or otherwise produce a clean exact substrate candidate before WI-5249 begins.

After the predecessor commit, WI-5249 must rerun the complete adjacent command from version 004 and require zero failures. A green focused WI-5249 module is not sufficient by itself.

### P2 - Missing claim-to-NO-ACTION filing proof

Accepted. `platform_tests/scripts/test_bridge_work_intent_registry.py` will add one end-to-end test that:

1. creates a latest GO or NO-GO fixture with valid Prime worker provenance;
2. acquires `no_action_correction` through the canonical CLI;
3. invokes the governed bridge writer/filer path to append the next Prime-authored `NO-ACTION` entry;
4. confirms the numbered chain is append-only and the new entry carries valid author/session metadata;
5. confirms canonical scanning classifies the latest NO-ACTION as Loyal-Opposition-actionable and not Prime-implementation-actionable;
6. confirms implementation authorization still rejects the correction claim.

The test may call existing governed writer/scanner services, but WI-5249 will not modify those services.

## In-Root Placement Evidence

The eventual three implementation targets remain inside `E:\GT-KB`. The predecessor, bridge evidence, tests, and exact-candidate artifacts must also remain in-root. No Agent Red or out-of-root dependency is introduced.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - defines Prime correction and Loyal Opposition review routing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct append-only status authority and the governed filer.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - requires attributable session metadata in the filed NO-ACTION entry.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - assigns the foreign PAUTH/acquisition substrate to WI-5178 and preserves operation-time checks.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - defines the current authorization envelope consumed by the predecessor.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - correction claims cannot authorize implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries complete concrete links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - final verification requires exact-candidate and end-to-end executed evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI, and target paths remain explicit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - WI-5178 and WI-5249 remain separate durable work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - ownership, implementation, tests, report, verdict, and commit remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this thread remains blocked until the predecessor reaches the required state.
- `GOV-STANDING-BACKLOG-001` - the foreign WI-5178 work remains visible and cannot be absorbed silently.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets and evidence remain within GT-KB.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex continues through governed deterministic bridge helpers.

## Prior Deliberations

- `DELIB-202666202` - owner authorization for the bounded WI-5249 repair.
- `DELIB-HARNESS-NO-ACTION-LO-RESPONSE-SET-20260702` - Loyal Opposition handling of Prime NO-ACTION entries.
- `DELIB-202666082` - owner-approved operation-time enforcement requirement without implementation authority.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-004.md` - exact-candidate and adjacent-regression findings addressed here.
- `WI-5178` v3 - current backlog owner of the foreign operation-time substrate; no implementation approval is inferred.

## Owner Decisions / Input

- `DELIB-202666202` continues to authorize only the bounded WI-5249 lifecycle.
- No new owner decision is required to file this sequencing revision.
- Separate owner approval is required before WI-5178 can be proposed or implemented; this revision does not supply it.

## Pre-Filing Preflight

Candidate applicability preflight passed on this exact completed revision:

- packet_hash: `sha256:b82c00872fdd187e08a7eb8f1d11e04d6aebd15cc0a1348c99e4a04ddd4bd68c`
- content_source: `pending_content`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

Mandatory clause preflight also passed: five clauses evaluated, four `must_apply`, one `may_apply`, zero evidence gaps in must-apply clauses, and zero blocking gaps.

## Specification-Derived Verification Plan

| Requirement | Exact future evidence |
| --- | --- |
| WI-5178 predecessor ownership | Cite terminal VERIFIED verdict and focused commit; show the operation-time substrate is committed before WI-5249 begins. |
| Exact WI-5249 candidate | `git diff <WI-5178-commit> --` shows only the three approved targets and only the explicit correction feature/test hunks listed above. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Focused positive and negative claim tests plus the end-to-end canonical claim-to-file-to-LO-scan test pass. |
| PAUTH and implementation-start non-bypass | Normal malformed-PAUTH implementation claim remains denied; correction claim succeeds only for filing and cannot authorize implementation start. |
| Adjacent regression safety | The exact version 004 adjacent suite reruns with zero failures after WI-5178 and WI-5249 changes. |
| Static quality | Ruff check, Ruff format-check, and `git diff --check` pass on the three WI-5249 targets. |
| Governance | Applicability and clause preflights pass on the operative revision and implementation report. |

Required command set after the predecessor commit:

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_no_action_prior_verdict.py platform_tests/scripts/test_scan_bridge.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_go_impl_claim_timebox.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py platform_tests/scripts/test_bridge_work_intent_registry.py
python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py platform_tests/scripts/test_bridge_work_intent_registry.py
git diff --check
```

## Acceptance Criteria

- WI-5178 is independently VERIFIED and committed before WI-5249 source/test mutation begins.
- The future WI-5249 diff contains only the explicit correction feature and focused tests in the three declared targets.
- All focused and adjacent suites pass against the exact post-predecessor candidate.
- The end-to-end test proves canonical acquisition, governed NO-ACTION filing, LO actionability, and implementation-start denial in one workflow.
- The report cites the predecessor commit, exact candidate hash/diff, executed tests, Ruff gates, and passing preflights.
- No foreign operation-time, dispatcher, runtime, lease, role, eligibility, credential, external-system, deployment, release, push, or unrelated worktree mutation is attributed to WI-5249.

## Risk And Rollback

The primary risk is that WI-5178 changes the registry interfaces before it lands. The fresh post-predecessor claim, start packet, baseline hash, focused diff, and full adjacent suite contain that risk. A second risk is accidentally making correction claims implementation-capable; explicit start-gate denial remains mandatory.

Rollback is a focused revert of the eventual WI-5249-only hunks from the three declared targets. The WI-5178 predecessor commit and append-only bridge evidence remain intact.

## Recommended Commit Type

`feat`

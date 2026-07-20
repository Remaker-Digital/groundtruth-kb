GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5250 Codex A Dispatch Readiness

bridge_kind: lo_verdict
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 018
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250
Recommended commit type: none

## Verdict

GO. Version 017 is approved only as a bounded exact-root `.codex` ACL repair proposal. It correctly accepts the version 016 NO-GO, withdraws the disproven raw-SID `icacls /remove:d` mechanism, and replaces it with exact `Get-Acl` enumeration plus `RemoveAccessRuleSpecific` removal of the two non-inherited Deny rule objects for SID `S-1-5-21-2908765920-875073000-2352713335-4168283502`, followed by one `Set-Acl` write against exact `.codex`.

This is not a terminal readiness approval and not permission to overstate Codex A dispatchability. Fresh live evidence during this review still shows two independent readiness facts: `.codex` ACL readiness is false because exactly two risky root Deny ACEs are present, and the separate no-window proof is expired. The v017 implementation may repair the first fact. It must report the second fact honestly unless the separately governed no-window proof is current by implementation-report time.

The GO therefore unlocks the exact ACL operation and post-operation evidence collection. A later VERIFIED for WI-5250 still requires the canonical readiness verifier to support the terminal claim actually made. If `verify_codex_dispatch.py --json` still reports `codex_no_window_verification_expired`, the implementation report must not claim full `dispatchable=true` restoration under this revision.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is operating as Loyal Opposition by direct owner instruction in the current chat. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and v017 is latest `REVISED`, which is Loyal-Opposition-actionable.

PASS. Version 017 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

The v017 artifact-head envelope line `::init gtkb lo` is correct for a Prime-authored `REVISED` proposal because the envelope addresses the LO responder. `bridge_proposal_pattern_lint.py --file bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md --strict` reported zero findings.

## Applicability Preflight

- packet_hash: `sha256:0642f5bc47b3d82e94ca5ef546cd7c932cee55219f01281b32385552da69b5e6`
- bridge_document_name: `gtkb-wi5250-codex-a-dispatch-readiness`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md`
- operative_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`.codex`]
- candidate_evidence_hash: `sha256:91bfd18143a0298be4d6e4625d7deb0bb81700508eb3365df9889cb5d58952bc`

## Clause Applicability

- Bridge id: `gtkb-wi5250-codex-a-dispatch-readiness`
- Operative file: `bridge\gtkb-wi5250-codex-a-dispatch-readiness-017.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory Slice 2 gate

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Evidence Reviewed

- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge state-report --json`: fresh scan reported 45 LO-actionable latest entries; dispatcher health `WARN`; selected LO targets `D` and `F`; selected PB target `A`.
- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5250-codex-a-dispatch-readiness --compact --json`: latest status `REVISED`, latest path `bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md`, version count 17.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md --json`: PASS; packet hash shown above; declared target path only `.codex`; missing required and advisory specs empty.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md`: PASS; must-apply gaps 0.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --json`: FAIL as expected; `codex_dotdir_acl_ok=false`, `risky_deny_count=2`, `errors_count=0`, `live_headless_ready=false`, `live_headless_reason=codex_no_window_verification_expired`, `dispatchable=false`, `static_dispatchable=false`.
- `powershell -File scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json`: FAIL as expected; `checked_count=218`, `risky_deny_count=2`, `needs_repair=true`, both risky Deny rules on exact `.codex` for the stated SID; both required Modify allows present.
- `Get-Acl -LiteralPath .codex`: confirms the two explicit Deny ACEs are on exact `.codex`.
- `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5250 --json`: status detail remains stale and still describes a prior clean readiness interval and latest NO-GO v016, not the current regressed ACL plus expired no-window state.
- `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5571 --json`: WI-5571 is open and owns the separate recurrence/provenance investigation, linked to TEST-11622.

## Findings

### F1 - The corrected ACL mechanism is necessary and sufficiently bounded

The current live state matches v017's precondition: exactly two risky explicit Deny entries on the exact `.codex` root, zero read errors, and required Modify allows present. Version 016 required replacing the failed raw-SID `icacls /remove:d` path with exact ACE-object removal if the state regressed. Version 017 does that and fails closed if the selection is anything other than the two target Deny rule objects.

The proposal's mutation surface is appropriately narrow: exact `.codex` root only, no recursion, no descendant writes, no source or test changes, no dispatcher configuration, no TAFE state, no lease/runtime mutation, no harness invocation, no proof renewal, and no Git operation.

### F2 - Full dispatchability remains blocked by no-window expiry

The live verifier currently reports `live_headless_reason=codex_no_window_verification_expired`. Version 017 correctly refuses to renew that proof and requires honest classification if it remains expired. That is acceptable for this GO because this proposal is an ACL repair, but it means the implementation evidence cannot be treated as full Codex A readiness unless the separate no-window proof is current and accepted at report time.

The related no-window work should be handled under its own governed bridge thread, not silently absorbed into this exact-ACL proposal.

### F3 - WI-5250 backlog status detail is stale and must not be cited as current truth

`gt backlog show WI-5250 --json` still reports a clean readiness interval and latest NO-GO v016, while the live verifier and v017 show the state has regressed and v017 is latest REVISED. This does not block the ACL repair GO, but it does block any final readiness narrative that cites `status_detail` without correction. Prime Builder should correct the backlog status detail through an authorized path after the repair evidence is available, or clearly state in the report that live bridge and verifier state supersede that stale row.

## Required Implementation Constraints

1. Acquire a matching work-intent claim and current implementation-start authorization for v017 before any `.codex` ACL write.
2. Admit only exact `.codex`; representative descendants, dispatcher state, leases, source, tests, and database paths must be rejected by the operation-time gate.
3. Before the write, prove exactly two target root Deny ACEs for the stated SID, zero descendant risky Deny ACEs, zero read errors, and both required Modify allows.
4. Remove only the two selected non-inherited Deny rule objects with `RemoveAccessRuleSpecific` and apply one `Set-Acl -LiteralPath .codex` write.
5. Prove every non-target root ACE, owner, inheritance-protection property, and required Modify allow is unchanged after the write.
6. Re-run `repair_codex_dotdir_acl.ps1 -Mode Check -Json` and require `risky_deny_count=0`, `needs_repair=false`, `errors_count=0`, and both required allows present.
7. Re-run `verify_codex_dispatch.py --json` and report the canonical readiness classification exactly. Do not claim `dispatchable=true` if the only remaining red fact is an expired no-window proof.
8. Use dispatcher status/health/report commands read-only only. Do not mutate dispatcher config, TAFE state, harness registry, leases, locks, routing, roles, models, caps, selection order, or runtime JSON.
9. Do not stage, commit, push, rewrite history, adopt unrelated worktree changes, touch `groundtruth.db`, or perform credential, deployment, release, cleanup, or external-system actions under this GO.

## Prior Deliberations And Related Artifacts

- `DELIB-202666203` - owner authorization for WI-5250 governed Codex A dispatch readiness repair while preserving bridge and dispatcher boundaries.
- `DELIB-202666274` - active project authorization with implementation-start and forbidden-operation constraints.
- `DELIB-202666254` and `DELIB-202666929` - prior WI-5250 GO lineage and cautionary precedent around conditional readiness claims.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md` - records the failed approved raw-SID `icacls` attempt.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-016.md` - required exact ACE-object repair if the ACL state regressed.
- `WI-5571` / `TEST-11622` - owns the separate recurrence/provenance and durable non-reintroduction investigation.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge state-report --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5250-codex-a-dispatch-readiness --compact --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --json
powershell -File scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json
Get-Acl -LiteralPath .codex
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5250 --json
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5571 --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_proposal_pattern_lint.py --file bridge/gtkb-wi5250-codex-a-dispatch-readiness-017.md --strict
```

## Scope Of This Verdict

Verdict-file only. I did not mutate `.codex`, source, tests, dispatcher configuration, TAFE state, runtime JSON, leases, harness registry, `groundtruth.db`, credentials, deployment state, release state, Git state, or external systems.

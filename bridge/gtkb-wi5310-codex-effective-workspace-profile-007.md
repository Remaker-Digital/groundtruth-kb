NO-ACTION
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

# WI-5310 Prime Builder Verification And Dispatch-Gate Disposition

bridge_kind: operational_state_change
Document: gtkb-wi5310-codex-effective-workspace-profile
Version: 007
Responds to: bridge/gtkb-wi5310-codex-effective-workspace-profile-006.md
Date: 2026-07-16 UTC
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5310-CODEX-PERMISSION-PROFILE-V2-20260716
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5310
target_paths: []

## First-Line Role Eligibility Check

PASS. Canonical open session `A-2026-07-16T12-17-36Z` resolves to Prime
Builder for harness A through transcript-defined role provenance. Prime Builder
holds the exact `no_action_correction` claim for this thread, row `31635`,
acquired at `2026-07-16T20:23:54Z`. `NO-ACTION` is authorized by
`GOV-FILE-BRIDGE-AUTHORITY-001` and
`DCL-NO-ACTION-STATUS-SEMANTICS-001` because the version-006 GO cannot satisfy
its mandatory verification and real-dispatch conditions without unauthorized
out-of-scope mutations.

## Disposition

The authorized five-target candidate is technically functional but the GO is
not verification-ready or finalization-ready. Prime Builder therefore fails
closed instead of filing a false-complete implementation report.

The V2 PAUTH, GO, claim, and implementation-start gates passed. The canonical
writer changed A's headless invocation from legacy `--sandbox workspace-write`
to `-c default_permissions=":workspace"`, preserving model `gpt-5.5`, approval
`never`, reasoning `xhigh`, project-root selection, `.codex` add-dir, PB-only
role, and canonical max-items `1`. The scripts and focused tests now require
schema-v3 effective-profile and create/read/remove sentinel evidence. The real
two-run private-desktop smoke passed.

Four independent mandatory gates remain unsatisfied:

1. `python scripts/verify_codex_dispatch.py --json` exits `1`. Its selector and
   live-proof checks pass, including `permissions_profile_ok=true`,
   `live_headless_ready=true`, and current schema-v3 evidence. The separate
   `.codex` ACL gate reports `codex_dotdir_acl_ok=false`, `errors_count=217`,
   `needs_repair=true`, no recognized `CodexSandboxUsers` group, and therefore
   `static_ok=false` / `dispatchable=false`. `--repair-acl` would mutate hundreds
   of paths outside WI-5310's exact five-target PAUTH and was not run.
2. Read-only dispatcher status and health expose a cap-authority mismatch. The
   canonical `gt harness show --harness A` record and generated registry keep
   `dispatch_max_items=1`, while dispatcher selection reports A with
   `dispatch_max_items=4`. WI-5310 explicitly forbids changing dispatcher
   config, routing, caps, or TAFE state, so this session did not reconcile it.
3. No fresh dispatcher-produced substantive A/PB bridge artifact exists after
   the canonical A version-61 mutation at `2026-07-16T20:11:56Z`. Dispatcher
   runtime evidence remains the stale pre-fix `codex_dispatch_not_ready` result
   from `2026-07-15T21-48-32Z-prime-builder-A-aff7b2`, with no current A
   selection. Triggering unrelated bridge work while the full verifier is red
   would bypass the GO and this worker's WI-5310-only scope.
4. Harness parity Phase 1 exits `1` with overall `FAIL` (`52` DEGRADED, `69`
   MISSING, `308` PASS, `145` UNSUPPORTED). Phase 2 exits `0` with no unwaived
   release-blocking gap, and Phase 3 exits `0` with `PASS`, but the GO requires
   all three parity phases and no parity regression.

## Authenticated Partial Candidate Evidence

The partial candidate remains in the worktree for a governed successor; it is
not staged, committed, pushed, released, or deployed.

| Target | SHA-256 after authorized implementation |
| --- | --- |
| `harness-state/harness-registry.json` | `c735cd1130c4850e07f0e2982900c6049c5866b635174b4bc1e1824aefade9b5` |
| `scripts/codex_no_window_smoke_probe.py` | `576d3030bdd2ba053916fdeb218f621b44b4ada08cdc9c1d44b2ba2358369515` |
| `scripts/verify_codex_dispatch.py` | `188b231cc6d158697f20ea3dce4f7f495fdb91e00ff9c51a53496295ce38ade6` |
| `platform_tests/scripts/test_codex_no_window_smoke_probe.py` | `13f9c859c2006990b686d1c0b2071f8e1f6094e698a46e99eb7e57e2b5dd5f8f` |
| `platform_tests/scripts/test_verify_codex_dispatch.py` | `319dace31700e2cc680d5f08c3f4300921a2cbf36f91f5fc4994226222df269c` |

The registry was mutated only through
`gt harness set-invocation-surface --harness A --surface headless`. The writer
advanced canonical A from version `60` to `61` and refreshed the shared
generated projection from MemBase. Pre-existing and concurrently generated
foreign projection deltas remain unstaged and are not attributed to WI-5310.

## Verification Evidence

| Check | Observed result |
| --- | --- |
| V2 PAUTH | Active; exact five targets and `runtime_state`, `source`, and `test` coverage confirmed. |
| Mandatory bridge preflights before implementation | Applicability PASS; clause preflight exit `0`, no blocking gaps. |
| Work-intent claim | `go_implementation`, row `31635`, session `A-2026-07-16T12-17-36Z`, acquired `2026-07-16T20:06:44Z`. |
| Implementation start | PASS; packet `sha256:aa96fcd5b88abe79874863c2cbeb36bdacc854c3fd4ece4142ac33c447fdf007`, exact five targets. |
| Focused tests | `python -m pytest platform_tests/scripts/test_codex_no_window_smoke_probe.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short` -> `27 passed`. |
| Ruff | Four changed Python files: check PASS; format-check PASS. |
| Diff check | `git diff --check` PASS for the four changed Python files. |
| Private-desktop smoke | Exit `0`; two runs; `:workspace` requested; `workspace-write` observed; all six markers attributable with occurrence count `3`; both create/read/remove chains PASS; wrapper exits `0`; four zero-window observations; no residue. |
| Full Codex verifier | Exit `1`; live proof PASS, ACL gate FAIL with 217 errors; `dispatchable=false`. |
| Dispatcher health/status/report | Read-only; daemon/supervisor/watchdog healthy, aggregate WARN due unrelated E backoff; A selected as PB but dispatcher cap view is `4`, not canonical `1`; no fresh A artifact. |
| Harness parity Phase 1 | Exit `1`, overall FAIL. |
| Harness parity Phase 2 | Exit `0`; 0 unwaived release-blocking gaps. |
| Harness parity Phase 3 | Exit `0`, PASS. |

## Correction Required From Loyal Opposition

Issue a corrected `NO-GO` that preserves the authenticated five-target
candidate and requires dependency closure before another implementation GO:

- route `.codex` ACL diagnosis/repair through separate exact-path authority;
- reconcile canonical max-items `1` with the dispatcher-selected cap without
  assigning that dispatcher/config mutation to WI-5310;
- resolve or explicitly baseline the failing Phase 1 parity population; and
- after the full verifier is green, provide an independently approved
  substantive carrier that the dispatcher may route to A for the required
  governed artifact proof.

Do not require WI-5310 to mutate credentials, dispatcher/TAFE configuration,
unrelated bridge threads, external systems, or Git history to satisfy those
dependencies.

## Requirement Sufficiency

Existing requirements remain sufficient. The selector, smoke, and verifier
design is implemented and tested; the blockers are independently governed ACL,
dispatcher-cap, parity-baseline, and real-dispatch dependencies. No owner
decision is invented by this disposition.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202665713` - WI-4985 Codex headless write-boundary VERIFIED lineage.
- `DELIB-202665293` - nominal workspace-write may differ from effective runtime identity.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded WI-5310 repair authority.
- Versions 001 through 006 are the complete proposal, prior rejection,
  corrected V2 authorization, revision, and fresh GO chain.

## Owner Decisions / Input

No owner decision is required to fail closed on the observed mandatory gates.
Any ACL, dispatcher-cap, parity-baseline, or separate acceptance-carrier work
must use its own existing or newly governed authority; none is inferred here.

## Pre-Filing Preflight Subsection

The mandatory applicability preflight ran against this completed version-007
content and passed with `missing_required_specs: []`,
`missing_advisory_specs: []`, and no blocking errors. The mandatory ADR/DCL
clause preflight evaluated five clauses, classified three as `must_apply`,
found zero evidence gaps and zero blocking gaps, and exited `0`.

## Authority Boundary

This entry authorizes no further source, test, runtime-state, ACL, dispatcher,
TAFE, credential, Git, release, deployment, or external-system mutation. It
preserves but does not finalize the authenticated five-target candidate.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

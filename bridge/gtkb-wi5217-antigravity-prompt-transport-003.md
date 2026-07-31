NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; resumed GT-KB fleet goal; A is PB-only
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - WI-5217 Antigravity Prompt Transport

bridge_kind: implementation_report
Document: gtkb-wi5217-antigravity-prompt-transport
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5217-antigravity-prompt-transport-002.md
Approved proposal: bridge/gtkb-wi5217-antigravity-prompt-transport-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5217
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
Recommended commit type: fix(dispatcher):

## Implementation Claim

WI-5217 is implemented in the Antigravity command-composition path.

The dispatcher already writes the complete selected assignment to the per-dispatch stdin sidecar. This implementation makes the argv scrubber explicitly treat `--print` as a value-taking prompt flag, so Antigravity receives a short pointer prompt as the `--print` value instead of allowing `--print-timeout` to become the prompt. The focused regression test now asserts the child argv contains `--print`, the sidecar pointer, and then `--print-timeout`, with the full dispatcher assignment absent from argv and present in the in-root sidecar.

## Governance And Authorization Evidence

- Latest bridge status before implementation: `GO` at `bridge/gtkb-wi5217-antigravity-prompt-transport-002.md`.
- PB work-intent claim acquired: rowid `31194`, session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, `claim_kind=go_implementation`, `ttl_expires_at=2026-07-15T04:41:50Z`.
- Implementation-start authorization succeeded at `2026-07-15T04:01:59Z`.
- Implementation authorization packet hash: `sha256:95d126b96596e08ed602820a46a7e27b52227f71b92670efd4080e7143ca155e`.
- PAUTH version: `2`.
- PAUTH classified target mutation classes as `source` and `test`; both requested target classes were allowed.
- Owner decision carried forward: `DELIB-202666173`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected work must reach the chosen harness unchanged.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - eligibility remains controlled only through canonical transactions.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - C must perform genuine assigned-role work and produce governed evidence.
- `ADR-CROSS-HARNESS-PARITY-001` - C requires equivalent actionable prompt delivery.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - successful process launch is not functional proof when the selected assignment is lost.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the worker lifetime and hidden process envelope remain intact.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the pointer assignment directs C back to authoritative selected bridge files and normal LO verdict rules.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - the dispatch/session context remains the author authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requirements are linked before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes mapped unit and genuine C checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, work item, PAUTH, and targets are declared.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live C failure has a durable defect lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dispatch, test, proposal, report, and verdict evidence remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - live misrouting triggers governed correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this is in-root GT-KB dispatcher work.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect found during genuine six-harness proof.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712` forbids credential lifecycle, destructive cleanup, dispatcher mutation, external system mutation, git history rewrite, git push, production deployment, and release operations.
- No new owner decision is required for this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5217-antigravity-prompt-transport-001.md` - approved Prime Builder proposal.
- `bridge/gtkb-wi5217-antigravity-prompt-transport-002.md` - H-authored Loyal Opposition GO verdict.
- `DELIB-202666173` - complete six-harness governed proof and correct every discovered defect.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - cross-harness parity implementation authority.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` - verified requirement that every selected document advances independently.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused tests prove the full selected assignment remains in the stdin sidecar and the child argv contains a pointer prompt rather than the full assignment. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | No dispatcher eligibility, rules, routing, runtime JSON, lease, model, or role configuration was mutated. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Code/test evidence is present; a fresh genuine C dispatch is still required before terminal confidence. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Focused tests assert Antigravity-specific prompt transport without changing non-C command construction. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Focused tests include the existing worker-lifetime assertion for C (`4200`, current harness default in this checkout); no lifetime logic was changed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Work advanced through GO, claim, implementation-start, and this NEW report; no Prime-authored VERIFIED or LO status was created. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries forward the proposal, GO, PAUTH, project, work item, target paths, and linked specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, and ruff format check are recorded below; the broad dispatcher-runtime suite failure is disclosed and mapped to existing WI-5236/WI-5240. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Work remains linked through WI-5217, DELIB-202666173, PAUTH, bridge proposal, GO, tests, and this report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed WI-5217 paths are in-root GT-KB dispatcher source/test paths; no `applications/Agent_Red/` path changed. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py::test_antigravity_stdin_dispatch_replaces_prompt_with_sidecar_pointer platform_tests\scripts\test_dispatcher_runtime.py::test_antigravity_print_prompt_scrub_keeps_timeout_from_becoming_prompt platform_tests\scripts\test_dispatcher_runtime.py::test_worker_lifetime_profile_uses_opus_floor_for_unprofiled_lo -q --tb=short`
- `python -m ruff check scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py`
- `python -m ruff format --check scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py`
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5217-antigravity-prompt-transport`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5217-antigravity-prompt-transport`

## Observed Results

- Focused WI-5217 pytest: `3 passed in 0.82s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `2 files already formatted`.
- Broad dispatcher-runtime pytest: `194 passed, 3 failed`. The remaining failures are `test_prime_spawn_creates_dispatch_authorization_packet_and_env`, `test_issue_dispatch_auth_uses_go_items_from_mixed_list`, and `test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy`; this is the current-HEAD fixture drift already tracked by `WI-5236` and the PAUTH repair thread `WI-5240`.
- Applicability preflight on the operative bridge proposal: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:f5595b9e20bb1e1fd4ed0fbab3e3df7a87d9fb13fc909d27b663c46863564af8`.
- Clause preflight: exit `0`, `Blocking gaps (gate-failing): 0`.

## Files Changed For WI-5217

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `bridge/gtkb-wi5217-antigravity-prompt-transport-003.md` (this report, when filed)

Implementation-scope stat for the WI-5217 unstaged delta:

```text
platform_tests/scripts/test_dispatcher_runtime.py | 24 ++++++++++++++++++++++-
scripts/dispatcher_runtime.py                     |  2 +-
2 files changed, 24 insertions(+), 2 deletions(-)
```

## Dirty Worktree And Staging Boundary

The repository was already extremely dirty before this implementation. The two WI-5217 target files had no staged or unstaged changes immediately before this implementation began. This implementation did not run `git add`, `git commit`, `git push`, deployment, credential mutation, dispatcher eligibility/routing mutation, or direct runtime/lease edits.

## Acceptance Criteria Status

- PASS - C's `--print` option has an intentional short prompt value in the focused test path.
- PASS - `--print-timeout` is no longer adjacent to `--print` without a value between them.
- PASS - The short prompt points to the existing in-root assignment sidecar path.
- PASS - The full dispatcher assignment is not placed in child argv and remains in the sidecar.
- PASS - Missing/unwritable sidecars still fail closed before launch through the existing `prompt_sidecar_write_failed` path; no launch occurs before the write succeeds.
- PASS - Existing wrapper, hidden-launch, status-file, and worker-lifetime assertions covered by the focused selected test continue to pass.
- NOT RUN - A fresh genuine C dispatch was not launched by Prime Builder during this implementation. C is currently budget-constrained and disabled for general LO dispatch; prior owner authorization for C reroute was scoped to WI-5138, WI-5139, and WI-5233, not WI-5217.
- PENDING LO - Independent LO verification and any fresh C proof must be performed through TAFE/bridge only when an eligible LO lane is available.

## Risk And Rollback

Residual risk is concentrated in live Antigravity behavior: C must actually open and execute the pointed sidecar rather than treating the pointer text as the whole task. The implementation is intentionally narrow and leaves non-C harness command construction, dispatcher routing, registry eligibility, runtime JSON, leases, and worker lifetime logic unchanged.

Rollback is a source/test revert of the two WI-5217 implementation target files if Loyal Opposition finds a defect. Bridge files, work item/test records, PAUTH rows, and deliberation records are append-only audit artifacts and must not be deleted by rollback.

## Loyal Opposition Asks

1. Verify the source/test implementation against the linked specifications and observed command evidence.
2. Treat the disclosed broad-suite failures as existing WI-5236/WI-5240 fixture drift unless inspection shows this implementation introduced a new failure.
3. Determine whether the report can be VERIFIED with the focused evidence plus later fleet proof, or return NO-GO requiring a fresh genuine C dispatch before terminal verification.

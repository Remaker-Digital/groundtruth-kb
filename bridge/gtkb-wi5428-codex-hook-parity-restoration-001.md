NEW
::init gtkb pb
::open build

# Defect-Fix Proposal - Restore missing WI-5364 Codex hook parity implementation after false closure

bridge_kind: prime_proposal
Document: gtkb-wi5428-codex-hook-parity-restoration
Version: 001
Date: 2026-07-30 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb387-6f1b-7cb3-bb04-fca3330f512f
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; transcript role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5428

target_paths: [".codex/config.toml", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: configuration,source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## First-Line Role Eligibility Check

PASS. Interactive session `019fb387-6f1b-7cb3-bb04-fca3330f512f` resolves to
Prime Builder from the owner-declared `::init gtkb pb` transcript authority.
Prime Builder is authorized to file the `NEW` status on this implementation
proposal. The exact live draft claim for
`gtkb-wi5428-codex-hook-parity-restoration` is held by that same session; it
must remain current through the canonical helper write and is released only
after the numbered file and latest status are verified.

## Claim

Restore the still-missing Codex hook parity implementation through the active,
project-member successor `WI-5428`. Enable the supported live Windows hook
surface, make the deterministic parity checker understand the repository's
existing no-window batch fan-out without requiring duplicate registrations,
and stop the wrap-up trigger from forcing a role profile.

The repair is bounded to four currently clean targets. It does not amend,
delete, replace, or rely on the invalidly closed `WI-5364` bridge/backlog chain.
That chain remains append-only audit evidence, while this NEW thread obtains its
own independent GO, implementation-start packet, report, and VERIFIED verdict.

## Defect / Reproduction

At current HEAD `8a35eabc8cae297cbd295223d6ec904aa15212b8`, the exact focused command

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short --timeout=300
```

collects 14 tests and returns **5 failed, 9 passed, 1 warning in 0.65s**.
The failing tests are:

1. `test_codex_hook_parity_passes_for_repository_configuration`
2. `test_codex_userpromptsubmit_wrapup_hook_has_headroom_timeout`
3. `test_codex_hook_parity_requires_session_lifecycle_hook_intent`
4. `test_codex_hook_commands_avoid_shell_specific_command_substitution`
5. `test_codex_parity_repository_configuration_wires_bridge_compliance`

The exact checker command

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py
```

returns FAIL with exactly eight findings:

1. `.codex/config.toml` does not set `[features].hooks = true`.
2. The checker does not recognize the formal-artifact approval `PreToolUse` surface.
3. The checker does not recognize the workstream-focus `PreToolUse` surface.
4. The checker does not recognize the workstream-focus `Bash` matcher route.
5. The checker does not recognize the workstream-focus `apply_patch` matcher route.
6. The checker does not recognize the workstream-focus `UserPromptSubmit` surface.
7. The checker does not recognize the `UserPromptSubmit` session-lifecycle surface.
8. The wrap-up trigger dispatcher forces a role instead of discovering it.

The registration document already routes `UserPromptSubmit`, `PreToolUse Bash`,
and `PreToolUse apply_patch` through `run_py_no_window --batch`. The committed
batch table reaches the workstream-focus, formal-artifact, bridge-compliance,
and wrap-up handlers. Adding literal registrations on top of those batches would
double-run governance and lifecycle behavior. The defect is the disabled
feature flag, stale parity interpretation/tests that inspect only the outer
batch command, and the explicit wrap-up `--role-profile` extension.

The four target paths are clean in both worktree and index. Their pre-proposal
blob hashes are:

| Target | Blob hash |
|---|---|
| `.codex/config.toml` | `7deb13bee852276a44b15c23700637bf060f0480` |
| `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | `dde84f254eaeeaa6a62b58836d4930371a37ccdc` |
| `scripts/check_codex_hook_parity.py` | `a471fc7bfbc75c8ff9cf6033437fb31fc77655f1` |
| `platform_tests/scripts/test_codex_hook_parity.py` | `1cd59cfa2e608ed2312e287ad3502e11a1599da7` |

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.codex/config.toml`,
`.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`,
`scripts/check_codex_hook_parity.py`, and
`platform_tests/scripts/test_codex_hook_parity.py`. No Agent Red, adopter,
external-repository, or harness-local scratch artifact is an implementation
dependency.

## Authoritative Carrier and Audit-Trail Preservation

`WI-5428` is open, P0, and an active member of active project
`PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`. The current project-scoped
PAUTH is active at version 3, is list-free, covers bridge/configuration/source/
test work, and names `DELIB-202666274` as owner-decision evidence. Under the
project-only implementation-approval model, the work item inherits that project
authorization; the legacy per-WI `approval_state: unapproved` field is not an
implementation-authority gate.

The prior physical-repair carrier is preserved exactly as evidence:

- `bridge/gtkb-wi5364-codex-hook-batch-parity-001.md` is the original NEW proposal.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-002.md` is its historical GO.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-003.md` records NO-ACTION after the implementation-start packet failed to materialize.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-004.md` begins with `NO-GO` but its startup line declares `::init gtkb pb` while its author/session metadata and `bridge_kind` identify Loyal Opposition. It is therefore retained as role-envelope defect evidence, not silently repaired or treated as implementation authority.
- The MemBase `WI-5364` record says it was resolved by the VERIFIED backlog reconciler even though the numbered chain contains no terminal VERIFIED and the latest numbered file is the defective NO-GO carrier. This false-closure evidence remains untouched.

This proposal does not reopen, supersede, rewrite, or normalize those records.
It gives the still-required physical repair one unambiguous current carrier and
requires its implementation report to cite the preserved false-closure trail.

The former packet-start blocker is no longer systemic: the independent verdict
`bridge/gtkb-wi5382-implementation-start-packet-contract-004.md` is terminal
VERIFIED. That repair does not revive WI-5364's old GO and does not authorize
implementation here. After a fresh LO GO on this WI-5428 thread, Prime Builder
must acquire a matching `go_implementation` claim and produce/validate the
named implementation-start packet for this exact slug and target set.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - WI-5428's source requirement requires the detected parity failure to be corrected with mechanical evidence.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 - supported Codex Windows hooks are live; fallback is retained only if empirical availability regresses.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - the enabled Codex surface must cover active governance gates, including formal-artifact and bridge compliance.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity discovery evaluates actual configured surfaces, including declarative batch fan-out, without requiring duplicate registrations.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - current session authority determines role; a wrap-up adapter must not force a harness-local role profile.
- `DCL-SESSION-ROLE-RESOLUTION-001` - wrap-up generation discovers the current session role through canonical resolution.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - hook activation preserves no-window containment, single execution, role correctness, and fail-closed governance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - the governed Python lane cannot be release-ready while its mandatory Codex parity checker fails.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation authority comes from the active parent-project PAUTH and the work item's active membership.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - PAUTH status and scope must be revalidated when implementation starts.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - only the four declared paths and allowed configuration/source/test classes are in scope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - this proposal links the project and work item to the governing requirements.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass independent bridge GO, claim/start, report, or VERIFIED gates.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - exact-target cleanliness and concurrent-work isolation are rechecked before implementation and finalization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - defect, successor carrier, implementation evidence, and independent verdict remain durably linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5428 remains open until implementation and independent verification complete.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the false-closure residue is preserved as an origin=hygiene work item rather than hidden in chat or scratch state.
- `GOV-STANDING-BACKLOG-001` - WI-5428 is the durable current owner of the bounded repair.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - all four protected targets require independent GO, a matching claim/start packet, report, and independent VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the machine-readable PAUTH/project/work-item headers bind this proposal to an approved project member.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - each target and acceptance path is linked to its governing carrier.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification derives tests from live hook, batch, role, no-window, and release-readiness requirements.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - exact target hashes, commands, outputs, and preserved audit evidence make the change independently evaluable.
- `SPEC-AUQ-POLICY-ENGINE-001` - no AUQ is needed because active project authorization and membership already establish implementation approval; any new scope or owner choice fails closed to a one-question AUQ.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets are platform paths under the mandatory project root and do not mix Agent Red/application lifecycle authority into the repair.

## Prior Deliberations

- `DELIB-0836` - established the original Codex hook fallback stance later superseded in part by the live-Windows-hook ADR revisions.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` - approved mechanical Codex governance parity.
- `DELIB-202666274` - authorizes the Assurance project at project scope while preserving independent GO, claim/start, VERIFIED, exact-target, and forbidden-operation boundaries.
- `DELIB-202666774` - preserves the WI-5370/WI-5364 sprawl-reconciliation findings relevant to retaining, rather than erasing, malformed historical carriers.
- `DELIB-202667009` - records the corrected missing-targets-repair disposition and reinforces that a superseded or malformed carrier remains evidence rather than implementation authority.

## Owner Decisions / Input

No new owner decision is required. Active PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
version 3 covers this active project member and the exact bridge,
configuration, source, and test classes. Its owner-decision evidence is
`DELIB-202666274`.

This proposal does not authorize credential lifecycle, destructive cleanup,
dispatcher/TAFE mutation, external-system mutation, Git commit/history/push,
production deployment, or release. It also does not authorize bridge-history
rewrites, WI-5364 lifecycle repair, harness eligibility changes, manual routing,
or database mutation.

This proposal performs no KB or MemBase mutation.

## Requirement Sufficiency

Existing requirements sufficient. The live-Windows hook ADR, parity spec,
role-resolution requirements, nonimpairment contract, and active project PAUTH
fully determine the bounded correction. The observed defect is implementation
residue after a false closure, not a missing policy decision.

## Proposed Scope

1. Replace the obsolete disabled-hooks comment with the current live-Windows/no-window-batch stance and set `[features].hooks = true` in `.codex/config.toml`.
2. Preserve every unrelated config byte and fail closed if any of the four pre-proposal target hashes changes before implementation-start validation.
3. Remove the wrap-up adapter's role-profile helper/command extension; retain session-envelope latching and let `session_self_initialization.py` discover current role authority.
4. Import and reuse the existing public batch-aware surface enumerator in the parity checker rather than building a second parser.
5. Evaluate required surfaces per event group and matcher after expanding `run_py_no_window --batch`, while continuing to accept valid direct no-space wrapper routes.
6. Treat unreadable, malformed, missing, or incomplete batch definitions as parity failures.
7. Validate the outer batch hook as a command-substitution-free no-window invocation; keep child timeout enforcement with the existing batch runner/runtime-containment checks instead of imposing a direct-handler timeout on the aggregate hook.
8. Update focused repository assertions to inspect expanded event-group surfaces rather than literal command fragments in `.codex/hooks.json`.
9. Add or update focused fixtures proving a valid batch route passes, a missing/malformed batch surface fails closed, and direct-wrapper compatibility remains accepted.
10. Leave `.codex/hooks.json`, `.codex/gtkb-hooks/run_py_no_window.py`, every batch definition, Claude/Cursor/Antigravity configuration, dispatcher/TAFE state, harness registry, and the complete WI-5364 audit trail unchanged.

## Cross-Harness Disposition

No typed waiver is requested.

- Codex: enable the existing no-window batch topology and correct parity evaluation plus dynamic wrap-up role behavior. Each handler continues to execute once.
- Claude: no hook/settings mutation; existing direct registrations remain a reference behavior.
- Cursor: no hook mutation; shared workstream, role, and governance semantics remain regression inputs.
- Antigravity: no hook mutation; its absence of native hook events remains an architectural surface difference, not a target for registration cloning.
- Ollama, OpenRouter, Goose, and Alibaba Cloud Studio: no interactive hook configuration, eligibility, or routing change.

## Intuitiveness / Nonimpairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5428 fresh reproduction under DELIB-202666274 with WI-5364 false-closure trail preserved",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py",
  "before_behavior": "Codex hooks are disabled, the parity checker reports eight gaps because it does not expand existing no-window batches, five of fourteen focused tests fail, and wrap-up passes an explicit role profile.",
  "after_behavior": "Codex hooks are enabled through existing no-window batches, parity resolves each batch to its actual handlers exactly once, all fourteen focused tests pass, and wrap-up discovers session role canonically.",
  "self_descriptive_naming": "The checker distinguishes outer batch commands from expanded handler surfaces and names event-group and matcher evidence explicitly while preserving direct-wrapper compatibility.",
  "obsolete_guidance_disposition": "Remove the stale disabled-hooks comment and explicit role-profile override while retaining fallback only for an empirically demonstrated regression.",
  "history_preservation": "Do not mutate WI-5364 bridge files or backlog state; cite their invalid/false-closure evidence from the new WI-5428 implementation report.",
  "essential_context_preservation": "Keep live-hook availability, exact batch fan-out, single-execution behavior, no-window containment, canonical role resolution, fallback conditions, and the complete WI-5364 false-closure audit trail visible in code, tests, and governed reports.",
  "baseline": {
    "focused_parity_passed": 9,
    "focused_parity_failed": 5,
    "checker_findings": 8,
    "hooks_enabled": false,
    "target_paths_clean": 4
  },
  "expected_result": {
    "focused_parity_passed": 14,
    "focused_parity_failed": 0,
    "checker_findings": 0,
    "hooks_enabled": true,
    "duplicate_handler_registrations_added": 0
  },
  "rollback": "Through a separately governed transaction, revert only the four WI-5428 hunks to their recorded pre-implementation blobs; preserve existing batch registrations and all WI-5364/WI-5428 bridge history.",
  "hard_invariants": [
    "no governance or lifecycle handler executes twice because of this repair",
    "all hook subprocesses remain under the existing no-window runner",
    "missing or malformed batch evidence fails parity closed",
    "interactive session role is not forced by the wrap-up adapter",
    "no harness is disabled, deprioritized, rerouted, or made ineligible",
    "no dispatcher, TAFE, registry, hook registration, or historical WI-5364 artifact is mutated"
  ],
  "fail_closed_conditions": [
    "a fresh independent GO or matching implementation-start packet is absent",
    "any target is concurrently modified before start or finalization",
    "hooks remain disabled on the supported runtime",
    "a required batch surface cannot be parsed or is absent",
    "a hook command bypasses the no-window runner",
    "the explicit role-profile override remains",
    "focused parity, runtime containment, or cross-harness regression tests fail"
  ]
}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Live Codex hook activation | Parse `.codex/config.toml`; run `groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py` | `[features].hooks = true`; checker exits 0 with PASS and zero findings. |
| Batch-aware parity | Run focused valid/missing/malformed batch fixtures in `platform_tests/scripts/test_codex_hook_parity.py` | Valid event/matcher batches pass; missing, unreadable, or incomplete required surfaces fail deterministically. |
| No duplicate registration | Compare `.codex/hooks.json` and `.codex/gtkb-hooks/run_py_no_window.py` hashes before/after; enumerate expanded surfaces | Both non-target files are unchanged and each required handler has exactly one route per event/matcher. |
| Governance coverage | Check formal approval, bridge compliance, workstream Bash/apply_patch/UserPromptSubmit, and lifecycle SessionStart/UserPromptSubmit surfaces after expansion | Every required surface is recognized with the correct event and matcher. |
| Dynamic role authority | Run `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`; inspect command construction | No `--role-profile` argument is passed and canonical session role discovery remains green. |
| No-window containment | Run `platform_tests/scripts/test_codex_hook_runtime_containment.py`, `test_codex_hook_batch_output.py`, `test_codex_no_window_timeout_alignment.py`, and `test_codex_shell_no_window_wrapper.py` | No visible-console, wrapper, timeout, or aggregate-batch regression. |
| Focused parity | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short --timeout=300` | 14 passed, 0 failed. |
| Checker regressions | Run `platform_tests/scripts/test_check_codex_hook_parity.py`, `test_check_codex_hook_parity_resolution_table.py`, and `test_codex_hook_parity_resolution_table_drift.py` | Parser/direct-wrapper/batch resolution remains deterministic and the resolution table does not drift. |
| Exact-scope isolation | Revalidate PAUTH, claim/start packet, four target hashes, `git diff --check`, and scoped staged/unstaged paths | Only the four approved target hunks change; no dispatcher/TAFE, registration, registry, backlog, or historical bridge artifact changes. |
| Audit preservation | Compare WI-5364 files/records before and after; cite them in the implementation report | Original files and false-closure evidence remain byte-identical and visible to independent review. |

## Acceptance Criteria

1. Codex hooks are enabled for the supported live Windows runtime.
2. The deterministic parity checker exits 0 with PASS and zero findings.
3. All 14 focused parity tests pass, including valid, omitted, and malformed batch fixtures.
4. Required governance/lifecycle surfaces are reached through exactly one direct or batch route per event/matcher.
5. `.codex/hooks.json`, the no-window runner, and its batch definitions are unchanged.
6. The wrap-up adapter no longer passes or contains `--role-profile`; canonical role tests pass.
7. No-window containment, timeout, checker-resolution, and cross-harness regressions pass.
8. Only the four approved target paths change; concurrent or foreign bytes are preserved.
9. The WI-5364 bridge/backlog false-closure and invalid-role-envelope evidence remains unchanged and is cited in the implementation report.
10. A fresh WI-5428 LO GO, matching implementation-start authority, implementation report, and independent VERIFIED verdict exist before completion is claimed.

## Risks / Rollback

The highest implementation risk is double-running blocking or mutating handlers
by adding literal registrations on top of batch fan-out. This proposal forbids
that approach and verifies actual expanded topology. A second risk is a batch
parser that silently accepts incomplete evidence; unreadable, malformed,
missing, or incomplete batch definitions must fail closed. A third risk is
erasing or laundering the false-closure trail; historical WI-5364 bridge files
and backlog evidence are explicit non-targets.

Rollback requires a separately governed transaction and restores only the four
WI-5428 implementation hunks to their recorded pre-start blobs. It does not
rewrite hook registrations, batch definitions, dispatcher/TAFE or harness
state, database records, Git history, or WI-5364/WI-5428 bridge history.

## Files Expected To Change

- `.codex/config.toml`
- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

## Files Explicitly Excluded

- `.codex/hooks.json`
- `.codex/gtkb-hooks/run_py_no_window.py`
- `bridge/gtkb-wi5364-codex-hook-batch-parity-001.md` through `-004.md`
- all MemBase backlog/project/authorization records
- all dispatcher/TAFE, harness-registry, credential, Git, deployment, and release surfaces

## Bridge Filing

This NEW version 001 is filed through the governed bridge-propose helper for
`gtkb-wi5428-codex-hook-parity-restoration` under the exact current-session
claim. The helper-mediated filing preserves credential scanning, compliance
validation, append-only numbered-file creation, and governed current-status
publication; it does not authorize implementation before independent GO and a
matching implementation-start packet.

## Recommended Commit Type

`fix` - restores active Codex hook parity after false closure while preserving the audit trail.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

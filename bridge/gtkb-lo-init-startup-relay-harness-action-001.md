NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T07-30Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; Prime Builder

# Defect-Fix Proposal - LO Init Relay Must Continue To Harness-Only Startup Action

bridge_kind: prime_proposal
Document: gtkb-lo-init-startup-relay-harness-action
Version: 001
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4440

target_paths: ["scripts/workstream_focus.py", "scripts/session_self_initialization.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: lo_init_relay_harness_only_startup_action
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Fix the residual Loyal Opposition init-keyword startup relay defect captured in `WI-4440`: after a fresh `init gtkb` / `::init gtkb lo` match relays the cached startup disclosure, the LO path must also reach the harness-only startup action that verifies live bridge state and processes LO-actionable `NEW` / `REVISED` entries by default. The current relay instruction in `scripts/workstream_focus.py` tells the model to relay the disclosure, then stop and wait for the next owner message, which can prevent the required LO startup conclusion.

The implementation must preserve Prime Builder startup behavior: PB still presents the disclosure/session-focus choices and waits for the owner to choose or provide a concrete task. The change is LO-specific and must keep advisory mode opt-in behavior intact.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4440` has owner-requested hygiene capture, and the May29 Hygiene project authorization covers proposal work for all unimplemented work items linked to `PROJECT-GTKB-MAY29-HYGIENE`. The governing startup contract already requires role-specific LO behavior after disclosure: live bridge verification and auto-processing of actionable review/verification entries unless advisory mode is explicitly selected.

No new owner decision is required for proposal review. Implementation must wait for Loyal Opposition `GO` and a fresh implementation-start packet because `scripts/` and `platform_tests/` are protected source/test paths.

## In-Root Placement Evidence

All target paths are root-relative GT-KB paths:

- `scripts/workstream_focus.py`
- `scripts/session_self_initialization.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## Specification Links

- `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` - init-keyword match semantics govern startup relay behavior.
- `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` - startup action is selected by init-keyword matching.
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` - LO startup defaults to live bridge scan and auto-processing instead of asking Mike whether to process.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge state and numbered bridge files remain the authority for LO startup actionability.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal maps the implementation scope to concrete governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the LO init relay cannot stop after disclosure alone.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files must remain under the GT-KB project root.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect is already represented by `WI-4440` before proposal filing.

## Prior Deliberations

- `WI-4440` - owner-requested hygiene item describing the relay-stop defect and acceptance criteria.
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-010.md` - VERIFIED older startup-symmetry work; relevant prior baseline, but it does not close this residual relay-stop behavior because live `scripts/workstream_focus.py` still instructs the relay turn to stop and wait after disclosure.
- `bridge/gtkb-startup-relay-pretooluse-read-exemption-005.md` and `bridge/gtkb-startup-relay-truncation-fix-refile-012.md` - prior relay-cache mechanics that must remain intact.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1536` — seed=search; bridge_thread; Loyal Opposition Review - SessionStart Formalization (Init-Keyword Contract with
- DA: `DELIB-20264942` — seed=search; bridge_thread; Loyal Opposition Verification - Startup Relay Truncation Fix Refile
- DA: `DELIB-20262428` — seed=search; bridge_thread; Bridge thread: gtkb-startup-relay-truncation-fix-refile (12 versions, ORPHAN)
- DA: `DELIB-20264940` — seed=search; bridge_thread; Loyal Opposition Review - Startup Relay Truncation Fix Refile REVISED
- DA: `DELIB-2205` — seed=search; bridge_thread; Bridge thread: gtkb-startup-relay-pretooluse-read-exemption (5 versions, VERIFIE

## Proposed Implementation

1. Split startup relay follow-through by role/mode in `scripts/workstream_focus.py` so the LO default init path no longer emits an unconditional `stop and wait for the next owner message` instruction after disclosure relay.
2. Preserve the cache-read-only guard and pending-startup-response protections for the disclosure read itself.
3. Ensure LO default mode instructs the harness to continue with the harness-only startup action after relaying the disclosure: fresh live bridge/TAFE state read, report current LO-actionable queue state, and process latest `NEW` / `REVISED` entries oldest-to-newest when dispatchable.
4. Preserve `init gtkb advisory` as the opt-in advisory mode that reports the scan and asks Mike whether to switch to auto-process.
5. Preserve PB behavior that waits for session focus or a concrete mapped task after the startup disclosure.
6. Align `scripts/session_self_initialization.py` generated startup context text if it still contradicts the corrected LO follow-through contract.

## Spec-Derived Verification Plan

| Spec / governing surface | Required verification |
| --- | --- |
| `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` and `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` | Add or update tests that exercise a fresh LO init-keyword match and assert the generated relay instructions include LO follow-through rather than only disclosure relay plus wait. |
| `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` | Add or update tests that prove LO default startup reaches an auditable bridge-scan / auto-process instruction path after disclosure, while advisory mode remains opt-in. |
| PB startup contract | Existing or new regression tests must prove PB relay still waits for owner session focus / concrete task after disclosure. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests or source assertions must keep live bridge/TAFE state and versioned bridge files as the only queue authority; no cached startup reports or aggregate queue artifacts may be used. |

Suggested focused commands after implementation:

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_init_keyword_matching.py -q --tb=short -k "startup_response_pending or loyal_opposition_startup or init_keyword or startup_relay"
python -m ruff check scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_self_initialization.py
python -m ruff format --check scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_self_initialization.py
```

## Out Of Scope

- Do not change bridge dispatcher selection, provider routing, or thread automation registrations.
- Do not create new bridge automation.
- Do not mutate `bridge/INDEX.md` directly.
- Do not perform formal DA, GOV, SPEC, PB, ADR, or DCL mutations under this proposal.
- Do not alter Agent Red or other adopter application behavior.

## Risk / Impact

The main risk is over-correcting the relay path and making PB startup continue into tool use without owner focus. Keep the implementation role-specific and test PB separately. A second risk is bypassing the relay cache-read guard; the proposal intentionally preserves that guard and changes only what the LO path instructs after the disclosure has been relayed.

## Review Request

Loyal Opposition should review whether this scope is sufficient, non-duplicative with the VERIFIED startup-symmetry baseline, and narrow enough to implement without a new owner decision.
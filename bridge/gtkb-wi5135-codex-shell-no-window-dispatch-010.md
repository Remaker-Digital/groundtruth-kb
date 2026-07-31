VERIFIED
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T18-11-47Z-loyal-opposition-B-8066d7
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge-dispatch worker; resolved role loyal-opposition; auto-dispatch

# Loyal Opposition Verdict — VERIFIED — gtkb-wi5135-codex-shell-no-window-dispatch

bridge_kind: lo_verdict
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 010
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-009.md (NEW; implementation report; prime-builder/codex, harness A)
Date: 2026-07-10 UTC

## Verdict

VERIFIED. The `-009` implementation report satisfies the `-008` GO scope for WI-5135.
Codex headless shell containment is implemented as a per-dispatch Windows private
desktop (`CreateDesktopW` + `STARTUPINFO.lpDesktop`) applied to the Codex worker
launch, paired with a schema-v2 efficacy gate that requires positive marker-chain
proof of multi-command Codex shell activity AND zero visible pwsh/PowerShell
windows. I confirmed the implementation against the ten approved target paths by
direct diff inspection, re-ran the code-quality gates and the focused test suite
independently, and verified the load-bearing safety property against canonical
state: Codex-A stays quiesced. All evidence is reproduced below from my own runs,
not accepted from the report's self-assertion.

## Specification Links

Carried forward from the operative proposal (`-007`) and implementation report (`-009`):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered bridge chain authored role-correctly (PB report, LO verdict).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable implementation + verification evidence captured in this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — report carries forward concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping plus executed tests provided below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — report header carries PAUTH, Project, Work Item, and target_paths.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — containment implemented in dispatcher-owned command spawning.
- `ADR-DISPATCHER-ARCHITECTURE-001` — daemon-owned dispatch preserved; no poller/harness-trigger restored.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — live marker-chain proof exercises Codex behavior, not assumed hook parity.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — fail-closed readiness while Codex-A remains quiesced.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — protected mutation gated by the live PAUTH plus begin packet.
- `GOV-WORK-TREE-HYGIENE-001` — scope limited to the ten approved target paths; groundtruth.db and harness registry not staged.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — changes remain in GT-KB platform dispatcher/test scope.
- `GOV-STANDING-BACKLOG-001` — WI-5135 governed backlog continuation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable artifacts and lifecycle transitions.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — prior `-005` NO-ACTION / `-006` NO-GO lifecycle correction preserved.

## Spec-to-Test Mapping

| Specification | Test / evidence exercising it | Executed | Result |
| --- | --- | --- | --- |
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 | test_spawn_harness_uses_private_desktop_for_windows_codex_wrapper (dispatcher owns containment selection + env) | yes | pass |
| ADR-DISPATCHER-ARCHITECTURE-001 | test_dispatcher_runtime.py suite (daemon-owned spawn path; no poller/harness-trigger restored) | yes | pass |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | test_run_probe_writes_schema_v2_multi_command_marker_evidence (proves Codex shell activity by marker chain, not assumed hook parity) | yes | pass |
| SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 | test_codex_windows_dispatch_rejects_legacy_clean_false_green_verification + test_evaluate_readiness_rejects_legacy_clean_false_green_proof (fail-closed readiness; Codex-A quiesced) | yes | pass |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | test_run_probe_fails_when_marker_chain_is_missing + test_run_probe_fails_when_visible_window_is_observed (efficacy gate rejects both false-green modes) | yes | pass |
| GOV-FILE-BRIDGE-AUTHORITY-001 | numbered bridge chain -001..-010 authored role-correctly; PB report, LO verdict | yes | pass |

Governance/process specs in the report's Specification Links
(GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001,
PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, GOV-WORK-TREE-HYGIENE-001,
ADR-ISOLATION-APPLICATION-PLACEMENT-001, GOV-STANDING-BACKLOG-001,
ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001,
DCL-NO-ACTION-STATUS-SEMANTICS-001) are verified by bridge-protocol compliance:
correct authorship, live implementation-scoped PAUTH, target-path scoping, and the
two mandatory preflights passing on the operative file.

## Commands Executed

All commands run by the reviewer (harness B) from the project venv:

```
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <10 target paths>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <10 target paths>
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_subprocess.py platform_tests/scripts/test_codex_shell_no_window_wrapper.py platform_tests/scripts/test_codex_no_window_smoke_probe.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp/wi5135-lo-verify
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch
git --no-pager diff HEAD -- scripts/dispatcher_runtime.py scripts/verify_codex_dispatch.py scripts/windows_subprocess.py
```

Observed results:

- ruff check: `All checks passed!` on all ten target paths.
- ruff format --check: `10 files already formatted`.
- Focused pytest: `204 passed, 1 warning in 20.82s`. The single warning is the
  pre-existing `asyncio_mode` config warning, unrelated to this change.
- Applicability preflight: reproduced independently (see Applicability Preflight
  section) with an empty missing-required-specs list.
- Clause preflight: exit 0, zero blocking gaps across five clauses.
- Diff inspection: the modified source (dispatcher_runtime.py, verify_codex_dispatch.py,
  windows_subprocess.py) carries only WI-5135 content; the four new scripts are
  WI-5135-exclusive.

## Canonical-State Safety Verification (re-arm hazard)

The load-bearing risk in this slice is the WI-5080 verification-refresh re-trigger:
writing a current no-window proof can re-enable Codex-A dispatch and produce a pwsh
window storm. I confirmed this is contained against canonical state, not the report:

- The dispatcher's actual gate (`_evaluate_harness_dispatch_readiness`) requires a
  valid schema-v2 proof and rejects the legacy schema-v1 false-green format
  (asserted by test_codex_windows_dispatch_rejects_legacy_clean_false_green_verification).
- `harness-state/harness-registry.json` records harness A (Codex) with
  `can_receive_dispatch: false` and `role: ["prime-builder"]`. That persistent
  eligibility switch keeps Codex-A non-dispatchable regardless of no-window
  readiness. Harness B (this reviewer) is `loyal-opposition` and dispatchable,
  consistent with this dispatch.
- The change adds containment to the spawn path and tightens the readiness gate;
  it does not mutate dispatcher eligibility, so landing it cannot re-arm Codex-A.

## Non-Blocking Observations (implementation-phase notes; not verdict conditions)

1. [P3] Window observation is sampled before/after each blocking Codex run, not
   during it. A transient pwsh window that opens and closes entirely within one
   run could be missed by the observer. This is mitigated because the primary
   containment (CREATE_NO_WINDOW at process creation plus private-desktop
   inheritance) is deterministic rather than probabilistic, and the marker-chain
   proof confirms the multi-command shell activity actually occurred. Worth a
   follow-on during-run sampler if the mechanism is ever weakened.
2. [P3] scripts/codex_no_window_smoke_probe.py hard-codes `--model gpt-5.5` for
   the Codex exec. If that model id becomes unavailable the probe fails closed
   (non-zero return breaks the marker chain), so this is a brittleness note, not
   a correctness gap.
3. [P3] The standing recommendation from the -006/-008 thread — add
   mutation-class-versus-implementation-scope validation to the
   implementation_authorization.py / implementation_start_gate.py chain — remains
   an open Prime-Builder backlog-capture item, unaffected by this VERIFIED.

## Applicability Preflight

Command: `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch`.
Operative file resolved: `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-009.md` (NEW). Result summary:

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:e281bf4fb699707829ca19f78034c34f969b318137910c90d177abc3e608c225`

## Clause Applicability

Command: `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch` (mandatory mode; exit 0).

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0).
- Evidence gaps in must_apply clauses: 0.
- Blocking gaps (gate-failing): 0.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING: evidence found.

No blocking gaps; no owner-waiver line required.

## Methodology trail

- Read the full thread chain (-001 NEW, -002 NO-GO, -003 REVISED, -004 GO, -005
  NO-ACTION, -006 NO-GO, -007 REVISED, -008 GO, -009 report) before verdict.
- Review independence: reviewer session `2026-07-10T18-11-47Z-loyal-opposition-B-8066d7`
  (harness B, loyal-opposition) differs from the `-009` author session
  `019f4ace-e667-7030-b632-1cf002c1a0f7` (harness A, Codex). The implementation
  under review is Codex's work; the reviewer did not author it.
- Verified all ten target paths present (6 modified, 4 untracked) and cleanly
  WI-5135-scoped by `git diff --stat` and full-diff inspection.
- Inspected the containment mechanism in scripts/windows_subprocess.py
  (create_private_desktop_name, ensure_private_desktop, private_desktop_popen_kwargs)
  and its use in scripts/dispatcher_runtime.py _spawn_harness.
- Confirmed the smoke-probe pass logic requires marker_chain_ok AND not
  visible_window_detected, and that main() spawns real Codex and rewrites the live
  proof by default; therefore did NOT run the smoke-probe CLI in this headless
  session (WI-5080 re-arm hazard).
- Confirmed tests are hermetic (injected command_runner/window_observer,
  monkeypatched Popen/os.name/ensure_private_desktop) and genuinely exercise the
  fail-closed paths.
- Both mandatory preflights re-run independently on the operative file.

## Prior Deliberations

- `DELIB-202666064` — owner decision (AUQ): fix WI-5135 for the headless Prime path;
  backs the implementation-scoped WI-5135 PAUTH.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — owner directive: no visible console
  windows may spawn; dispatcher may remain quiesced until proof exists.
- `DELIB-202665909` — VERIFIED for the parent-level dispatcher no-window containment
  (WI-5052) that this grandchild-shell follow-on supersedes.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — governs the -005 NO-ACTION / -006 NO-GO
  lifecycle correction closed by the -008 GO.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-008.md` — the GO whose scope
  this report fulfills.

## Recommended Commit Type

Recommended commit type: `fix`. The slice remediates the Codex no-window dispatch
window-storm defect with focused source and platform-test coverage; two new helper
scripts are supporting surface for that fix, consistent with the declared type.

## Summary

The implementation delivers efficacy-gated Codex headless shell containment
(Windows private desktop) with schema-v2 fail-closed readiness that rejects the
prior false-green format, backed by hermetic tests covering both false-green modes.
Reviewer re-ran ruff check, ruff format --check, and the focused 204-test suite
(all green), re-ran both mandatory preflights (clean), and verified against
canonical registry state that Codex-A remains quiesced (`can_receive_dispatch:
false`), so the re-arm hazard is contained. Review independence is confirmed; no
blocking defect remains. VERIFIED, with three P3 implementation-phase notes carried
forward as non-blocking follow-ups.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(dispatcher): WI-5135 Codex shell no-window private-desktop containment + schema-v2 dispatch gate VERIFIED`
- Same-transaction path set:
- `scripts/dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `scripts/codex_no_window_smoke_probe.py`
- `scripts/windows_subprocess.py`
- `scripts/codex_shell_no_window_wrapper.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_windows_subprocess.py`
- `platform_tests/scripts/test_codex_shell_no_window_wrapper.py`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-001.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-002.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-003.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-004.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-005.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-006.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-007.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-008.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-009.md`
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-010.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.

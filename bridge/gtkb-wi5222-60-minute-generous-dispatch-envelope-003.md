NEW

# WI-5222 - 60-Minute Generous Dispatch Envelope Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5222-60-minute-generous-dispatch-envelope
Version: 003
Date: 2026-07-13 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: interactive Prime Builder; governed implementation; hunk-scoped index reconstruction

Responds to GO: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-002.md
Approved proposal: bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5222
Linked Test: TEST-11376
Phase: PHASE-015
Implementation claim: row 31278, session 2026-07-13T16-56-00Z-prime-builder-A-wi5222-impl, deadline 2026-07-13T17:19:12Z
Implementation authorization packet: sha256:16840fa76ce01b0f7c967f2e9766d0c3571b61358e3105f4d0dedc1b45b82cb0
Recommended commit type: fix
Recommended commit: `fix(dispatcher): calibrate generous execution envelope to 60 minutes`

## Implementation Claim

Implemented the owner-calibrated generous allowance from
`DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE`:

- D/F/H retain exactly 900 seconds per operation and 600 turns.
- D/F/H provider model sessions now receive exactly 3,600 seconds.
- A/B/C/D/F/H default dispatcher workers receive 4,200 seconds, preserving the
  600-second provider completion/reconciliation margin.
- Canonical document-lease and reset-straggler derivation now resolves to 4,500
  seconds without any direct runtime-state or lease-file edit.
- Models, skill routes, roles, eligibility, ranking, credentials, and cleanup
  algorithms are unchanged.

The implementation is staged as an asserted `HEAD`-based index patch. This
keeps every foreign routing-formatting, Goose, WI-5217, WI-5220, generated
adapter, and other dirty-worktree hunk outside the WI-5222 patch.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs worker lifetime, timeout classification, lease ordering, and dispatcher execution.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires the effective timer policy to remain observable through canonical dispatcher reporting.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires provider harness limits to support genuine governed PB/LO work.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - governs the shared F/H provider runtime and routing configuration.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - requires H to consume the shared timing contract truthfully.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - requires D timing changes to preserve governed tool-loop behavior and parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the append-only proposal, verdict, report, and verification chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH, project, and work-item linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent execution of mapped acceptance tests.
- `GOV-STANDING-BACKLOG-001` - `WI-5222` and `TEST-11376` are the governed work carriers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the owner policy decision and implementation evidence to remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs the decision-to-work-item-to-bridge lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires implementation and independent verification artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires all implementation and evidence to remain inside `E:\GT-KB`.

## Owner Decisions / Input

`DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` is controlling. It
supersedes the prior eight-hour numeric allowance while preserving 600 turns
and 900-second operations. The owner explicitly accepts the two longer
historical successful runs as outliers under the new policy.

## Prior Deliberations

- `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE` - controlling numeric policy.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - predecessor generous-first policy.
- `DELIB-20260703-DISPATCH-OPUS-FLOOR-20RUN-REFINEMENT` - predecessor refinement rule superseded for this calibration.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` - predecessor 28,800/29,400 allowance.

## Specification-Derived Verification

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `TEST-11376` | Dispatcher runtime and daemon suites, including role defaults, routed D lifetime, lease, reset, and telemetry assertions | PASS: worker 4,200; lease/reset 4,500; routed D remains model window plus 600 |
| `ADR-CLOUD-HARNESS-TEMPLATE-001`, `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Shared cloud, Alibaba H, and OpenRouter F modules | PASS: each consumes 900/3,600/600 |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Ollama D harness module plus dispatcher lifetime profile coverage | PASS: D consumes 900/3,600/600 and receives a 4,200-second worker |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Exact cross-provider turn-budget assertions | PASS: D/F/H remain at 600 turns with unchanged role/model routing |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All approved test modules, Ruff lint/format, and staged patch whitespace check | PASS |
| Hunk-only guard | `git diff --cached --name-status`, `--stat`, full patch inspection, and `git diff --cached --check` | PASS: exactly nine approved source/config/test paths; no foreign hunks |

## Commands Run

- `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py -q --tb=short`
- `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py`
- `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_lo_harness_turn_budget.py`
- `git diff --cached --check`
- `git diff --cached --name-status`

## Observed Results

- Pytest: `473 passed, 1 warning in 53.14s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `8 files already formatted`.
- Staged whitespace check: exit 0 with no findings.
- Staged paths: exactly the nine approved target paths listed below.

The full dirty-worktree `git diff --check` remains noisy because unrelated
owner/other-session files contain pre-existing CRLF and whitespace changes.
That broad signal is not attributed to WI-5222; the exact staged patch is clean.

## Authorization Recovery Evidence

PAUTH v1/v2 failed closed on noncanonical operation taxonomy. PAUTH v3 corrected
only the authorization metadata and then allowed the implementation packet.
When the original interactive context ID was later found in multiple harness
session envelopes, packet renewal again failed closed. No envelope or runtime
JSON was hand-edited. A canonical, session-keyed Codex-A Prime Builder worker
envelope was created through `ensure_worker_session`, the stale overlapping
claims were released through the work-intent API, and claim row 31278 plus the
packet above were issued normally. The cross-harness interactive session-ID
collision is a separate discovered defect and is excluded from this timer patch.

## Scope Notes

- Two additional 3,600-second Ollama assertions are correct in the worktree but
  live inside a foreign, newly added test function absent from `HEAD`; they are
  intentionally excluded from this commit. Four `HEAD`-based Ollama assertions
  still cover route parsing and runtime propagation.
- The WI-5220 fixture corrections that made the full dispatcher/daemon suites
  green remain unstaged and require separate finalization.
- No dispatcher runtime JSON, lease, lock, credential, role, model, route,
  eligibility, or foreign generated-adapter hunk is included.

## Files Changed

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`

## Risks / Rollback

The accepted risk is that a legitimate run resembling the two historical
outliers will now time out at 60 minutes. An ordering regression could also
preempt provider cleanup, but the explicit model/worker/lease/reset assertions
guard that boundary. Rollback is the exact restoration of 28,800 provider
sessions, the 29,400 worker constant, and their owned assertions; runtime state
and lease files remain under canonical reconciliation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

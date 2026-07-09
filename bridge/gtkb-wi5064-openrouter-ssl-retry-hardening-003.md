NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# GT-KB Bridge Implementation Report - gtkb-wi5064-openrouter-ssl-retry-hardening - 003

bridge_kind: implementation_report
Document: gtkb-wi5064-openrouter-ssl-retry-hardening
Version: 003 (NEW; post-implementation report)
Date: 2026-07-07 UTC
Responds to GO: bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-002.md
Approved proposal: bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5064

## Implementation Claim

Prime Builder implemented the approved WI-5064 reliability repair for OpenRouter/F provider transport failures.

The OpenRouter harness now treats selected provider-transport failures as retryable inside the existing bounded chat-completion retry loop. The narrow SSL retry trigger covers `ssl.SSLError` text containing `SSLV3_ALERT_BAD_RECORD_MAC` or `bad record mac`, while preserving the existing attempt cap, backoff budget, and session timeout behavior. If the SSL failure exhausts retries or is not a recognized retryable provider-transport error, the harness now raises a concise `OpenRouterHarnessError` headed `OpenRouter provider transport failure after ... attempt(s)` without including the API key, request headers, or raw request payload.

The dispatcher runtime now recognizes both the new concise OpenRouter transport failure text and the legacy traceback marker text as `provider_failure`, so exhausted provider/TLS failures do not collapse into undifferentiated subprocess failures.

Implementation-start authorization was created from the live latest-`GO` bridge state before protected source/test edits:

- implementation packet hash: `sha256:171cc42c2d7dece833170a5bd91f2f9f1b8fe0409e57ee5f4283d65e7d161c71`
- implementation claim session: `019f3ddf-359c-7fa3-8885-2d1f9179d884`
- implementation claim status: `go_implementation`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this source/test/config repair to be bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires a live project authorization for source/test changes.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not replace LO GO or the implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - authorizes small single-concern reliability defects under `PROJECT-GTKB-RELIABILITY-FIXES` by active membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the recurrence to be preserved as durable work item and bridge evidence rather than chat-only memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - supports creating WI-5064 and a follow-on proposal when a verified closure premise is contradicted by fresh evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the defect, proposal, verification, and eventual report linked.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to map focused tests to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH/project/work-item metadata above.
- `GOV-ENV-LOCAL-AUTHORITY-001` - forbids credential disclosure or credential lifecycle changes while testing provider connectivity.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs provider-backed dispatch workers and the requirement that they process work headlessly.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher health/status evidence and failure classification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because Codex must self-enforce bridge gates when native hook coverage is incomplete.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms the target paths are GT-KB platform files, not external application files.
- `GOV-STANDING-BACKLOG-001` - covers WI-5064 as the active backlog record for the recurrence.

## Owner Decisions / Input

- Owner updated the active goal on 2026-07-07: OpenRouter should be LO-default, and Codex plus OpenRouter must be able to work headlessly.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active for small reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES`.
- No new owner decision, credential lifecycle change, provider-account change, production deployment, force-push, or broad cleanup is requested or consumed by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-202665819` - WI-5048 OpenRouter/F dispatchability NO-GO context.
- `DELIB-202665850`, `DELIB-202665849`, `DELIB-202665847`, and `DELIB-202665840` - prior OpenRouter retry/readiness verdict context for bounded provider retry handling.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction.

## Files Changed

- `scripts/openrouter_harness.py`
  - Added `ssl` import and `RETRYABLE_PROVIDER_TRANSPORT_MARKERS`.
  - Added narrow provider transport helpers for retryable marker detection and concise error summaries.
  - Extended `call_openrouter_chat` to catch `ssl.SSLError`, retry recognized bad-record-MAC provider failures within the existing attempt/backoff/session-timeout budget, and fail closed with credential-safe `OpenRouterHarnessError` text when exhausted.
- `scripts/dispatcher_runtime.py`
  - Added fatal worker-output markers for the new concise OpenRouter transport failure text and the legacy `SSLV3_ALERT_BAD_RECORD_MAC` traceback text, classified as `provider_failure`.
- `platform_tests/scripts/test_openrouter_harness.py`
  - Added WI-5064 focused tests for SSL bad-record-MAC retry recovery and exhausted credential-safe failure behavior.
- `platform_tests/scripts/test_dispatcher_runtime.py`
  - Added WI-5064 focused dispatcher classification coverage for legacy OpenRouter SSL bad-record-MAC stderr.

Note: these four approved target files already contained unrelated in-flight changes from prior work. This report claims only the WI-5064 behavior above.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge thread had latest status `GO` at `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-002.md` before implementation; implementation-start packet hash `sha256:171cc42c2d7dece833170a5bd91f2f9f1b8fe0409e57ee5f4283d65e7d161c71` was created before source/test edits. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | The implementation-start packet was created under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, `PROJECT-GTKB-RELIABILITY-FIXES`, and WI-5064. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Bridge proposal `001`, LO GO `002`, and implementation-start packet evidence are all cited; PAUTH was not treated as a bridge bypass. |
| `GOV-RELIABILITY-FAST-LANE-001` | Scope remained a single reliability repair for OpenRouter/F provider transport failure handling under WI-5064. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The recurrence is preserved as WI-5064 plus this append-only bridge implementation report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The live recurrence after WI-5051 closure is documented in proposal `001`; this report records the follow-on implementation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Proposal, GO verdict, implementation packet, code/test changes, verification evidence, and this report are linked in one bridge thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked specification surfaces. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Direct WI-5064 behavior checks invoked the new test functions and passed; lint/format gates passed; pytest runner caveat is documented below. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project authorization, project, and work-item metadata are present in the proposal and carried forward here. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Exhaustion behavior check asserted fake key `secret-openrouter-key` was absent from the raised error text; no credential file was edited. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Direct behavior check confirmed a simulated first-attempt OpenRouter SSL bad-record-MAC failure recovers on bounded retry and returns final assistant content. Live OpenRouter smoke returned the expected sentinel and exit code `0`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Direct behavior check confirmed legacy SSL bad-record-MAC stderr is detected as `fatal_worker_output_marker` with label/class `provider_failure`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | This interactive PB session self-enforced the bridge GO and implementation-start packet before protected edits. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths are inside `E:\GT-KB` and are GT-KB platform files, not Agent Red lifecycle-independent repository files. |
| `GOV-STANDING-BACKLOG-001` | WI-5064 is the active work item grounding this reliability repair. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\openrouter_harness.py scripts\dispatcher_runtime.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py
```

Observed result:

```text
All checks passed!
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\openrouter_harness.py scripts\dispatcher_runtime.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py
```

Observed result:

```text
4 files already formatted
```

```text
<direct Python harness invoking test_wi5064_openrouter_ssl_bad_record_mac_retry_then_success,
test_wi5064_openrouter_ssl_bad_record_mac_exhaustion_is_credential_safe, and
test_wi5064_openrouter_legacy_ssl_bad_record_mac_marker_is_provider_failure>
```

Observed result:

```text
direct WI-5064 behavior checks passed
```

```text
groundtruth-kb\.venv\Scripts\python.exe -c "import scripts.openrouter_harness as h; rc=h.main(['-p','Reply exactly: OPENROUTER_SSL_RETRY_PATCH_SMOKE_OK','--model','deepseek-v4-pro','--max-turns','1','--timeout','45','--session-timeout','90']); print('main_rc', rc)"
```

Observed result:

```text
OPENROUTER_SSL_RETRY_PATCH_SMOKE_OK
main_rc 0
```

Attempted focused pytest runner command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short
```

Observed result:

```text
pytest_exit_code=15
```

Additional diagnostic attempt with plugin autoload disabled and addopts cleared reached collection, then exited `15` before producing a test report:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0 -- E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\GT-KB
configfile: pyproject.toml
collecting ... pytest_single_no_plugins_exit_code=15
```

The pytest runner result is not claimed as passing evidence. The direct behavior checks above exercised the WI-5064 assertions outside the failing collection path.

## Observed Results

- Simulated `ssl.SSLError("[SSL: SSLV3_ALERT_BAD_RECORD_MAC] sslv3 alert bad record mac")` followed by a successful response retried once and returned final assistant content.
- Repeated simulated bad-record-MAC failures raised `OpenRouterHarnessError` with `OpenRouter provider transport failure` and `SSLV3_ALERT_BAD_RECORD_MAC` in the message, while excluding the fake API key value.
- Legacy OpenRouter SSL bad-record-MAC traceback text is now classified by dispatcher failure detection as `provider_failure`.
- Live OpenRouter `deepseek-v4-pro` smoke returned the exact sentinel and `main_rc 0`.
- Ruff lint and format checks passed on the approved target files.
- The repo pytest collection path for these target files exited `15` without a report; this remains a verification caveat for Loyal Opposition review.

## Acceptance Criteria Status

- OpenRouter/F no longer crashes with an unhandled `ssl.SSLError` for simulated `SSLV3_ALERT_BAD_RECORD_MAC`: satisfied by direct behavior check.
- A transient first-attempt TLS/provider failure can recover through bounded retry and return final assistant text: satisfied by direct behavior check.
- An exhausted TLS/provider failure exits with concise credential-safe stderr and is classified as a provider failure: satisfied by direct behavior check and dispatcher classification check.
- The post-implementation report includes focused tests and a controlled smoke plan for OpenRouter/F without relaunch loops: satisfied, with pytest runner caveat disclosed.

## Residual Blockers / Non-Scope

- This patch hardens OpenRouter/F against the recurrent SSL bad-record-MAC provider failure, but it does not restart or re-enable guarded dispatcher/watchdog automation.
- Codex/A headless dispatch remains separately blocked by the Codex Windows no-window/sandbox launch issue and the dispatcher disable guard.
- LO lane health may still show recent hold state until the sliding failure window clears or a separately authorized state reset is performed.
- The pytest runner collection exit `15` appears broader than WI-5064 because direct imports and direct WI-5064 behavior checks succeed; no pytest-infrastructure repair is claimed here.

## Risk And Rollback

Risk: retrying too broadly could mask non-transient provider defects. Mitigation: retry remains narrow, marker-driven for SSL bad-record-MAC, bounded by the existing attempt/backoff/session timeout controls, and still reports a provider failure when exhausted.

Rollback: revert the WI-5064 hunks in the four approved target files:

- `scripts/openrouter_harness.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

Bridge audit files remain append-only and are not rollback targets.

## Recommended Commit Type

Recommended commit type: `fix:`

`fix:` - this is a bounded reliability repair to existing OpenRouter/F dispatch behavior and dispatcher failure classification.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Treat the pytest runner exit `15` as an explicit verification caveat; return `VERIFIED` if the direct behavior evidence and live smoke are sufficient, otherwise return `NO-GO` with the scoped pytest-runner finding.

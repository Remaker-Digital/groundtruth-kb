GO
author_identity: OpenRouter F
author_harness_id: F
author_session_context_id: 2026-07-08T01-40-00Z-loyal-opposition-F-onshot
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter endpoint=https://openrouter.ai/api/v1; route=deepseek-v4-pro; requested_model=deepseek/deepseek-v4-pro; one-shot direct verdict body

## Applicability Preflight

- packet_hash: `sha256:2c541792348015ca3dd4d0da4af9caecf508ee73f4271dfe1fb34f89ba226de5`
- bridge_document_name: `gtkb-wi5064-openrouter-ssl-retry-hardening`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-001.md`
- operative_file: `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
## Decision

GO

## Prior Deliberations

- DELIB-202665819: Loyal Opposition Review – WI-5048 Activate OpenRouter/F for dispatchable Prime Builder work (NO-GO). The OpenRouter/F target was not ready at that time; subsequent work led to the LO-default headless processing goal.
- DELIB-202665850: Loyal Opposition Review – OpenRouter direct timeout retry (WI-5060). This informed the existing bounded retry infrastructure in the harness.
- DELIB-202665840: Verdict for `gtkb-wi5060-harness-readiness-repair`. The harness readiness repair laid groundwork for reliability improvements.
- DELIB-202665849: Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060). Approved a smaller retry expansion, confirming the retry pattern is acceptable.
- DELIB-202665847: Loyal Opposition Verdict: OpenRouter connection reset retry. Another retry addition, reinforcing the bounded retry approach.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: Owner-approved standing reliability fast-lane authorization, which applies to this defect.
- WI-5051 closure-only report: That report concluded the SSL bad record MAC failure was transient, but its recurrence today proves the need for code-level resilience.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Findings

1. The proposal is narrow: it adds retry handling for selected SSL/TLS transport exceptions (specifically `SSLV3_ALERT_BAD_RECORD_MAC` and similar transient network wrappers) within the existing bounded retry loop of `scripts/openrouter_harness.py`. The retry count, backoff budget, and session timeout are preserved, preventing unbounded loops.

2. The proposed error message when retries are exhausted is credential-safe: it names the provider transport class without dumping credentials, request headers, or raw payloads. This aligns with `GOV-ENV-LOCAL-AUTHORITY-001`.

3. Dispatcher failure classification in `scripts/dispatcher_runtime.py` will be updated to recognize both the hardened error texts and legacy traceback patterns, correctly categorizing them as provider failures rather than generic subprocess failures. This is consistent with `SPEC-DISPATCHER-CONTROL-SURFACE-001`.

4. The test plan covers retry success, retry exhaustion, credential-safe error text, and dispatcher classification. The tests are focused and will be executed under the project's verification requirements.

5. The proposal does not expand scope beyond the source files listed. No credential rotation, provider-account changes, or production deployment are authorized. It stays within the `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` authorization.

6. The recurrence of `SSLV3_ALERT_BAD_RECORD_MAC` after the closure of WI-5051 demonstrates that the previous assumption of transience was incorrect; a code-level fix is necessary for reliable headless dispatch. The bounded retry approach is a proportional response.

7. All referenced specifications are satisfied, and the preflight passed with no missing required specs.

## Conditions

- Prime Builder must run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5064-openrouter-ssl-retry-hardening` before source edits.
- The post-implementation report must include the execution of the focused tests (as specified in the verification plan) and the results, confirming that the harness retries correctly, failures are classified properly, and no credentials are leaked in error output.
- The smoke plan must be executed on OpenRouter/F without relaunch loops, and the outcome must be captured in the implementation report.
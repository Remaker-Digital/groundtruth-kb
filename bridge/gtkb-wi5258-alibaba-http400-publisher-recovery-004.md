NO-GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f65fb-4219-7150-ac09-26f12b650337
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Loyal Opposition; transcript override ::init gtkb lo; reasoning xhigh

# Loyal Opposition NO-GO Verdict - WI-5258 Alibaba H HTTP 400 Publisher Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5258-alibaba-http400-publisher-recovery
Version: 004
Responds to: bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-003.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5258-H-HTTP400-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5258

## First-Line Role Eligibility Check

PASS. Active role is transcript-defined Loyal Opposition (`::init gtkb lo`), harness A, session `019f65fb-4219-7150-ac09-26f12b650337`; NO-GO is authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. Report author session `A-2026-07-15T05-27-23Z` is independent from this review session.

## Verdict

NO-GO. The bounded JSON diagnostic, credential redaction, publisher-only forced-any behavior, and focused tests are otherwise sound, but malformed/incomplete HTTP response streams can escape the diagnostic helper and replace the prior governed terminal error.

## Finding

### P1 - Incomplete HTTP error streams bypass the generic fail-closed fallback

`_bounded_http_error_diagnostic` catches `AttributeError`, `OSError`, `TypeError`, and `ValueError` around `exc.read(MAX_HTTP_ERROR_BODY_BYTES)`. Python's `http.client.IncompleteRead` derives from `HTTPException`, not `OSError`, so a prematurely terminated HTTP 400 response propagates out of the helper.

Independent probe:

`groundtruth-kb/.venv/Scripts/python.exe -c "<HTTPError body read raises http.client.IncompleteRead; call _bounded_http_error_diagnostic>"`

Observed result: exit 1 with `http.client.IncompleteRead: IncompleteRead(1 bytes read, 10 more expected)` from `scripts/cloud_harness_base.py` at the bounded read. This violates the report's claim that unsafe or unrecognized bodies preserve the generic status-only `CloudHarnessError` and can misclassify a genuine H provider rejection as an unrelated harness failure.

Required correction:

1. Treat incomplete/malformed response-stream read failures as no diagnostic and preserve the existing generic HTTP status error. Catch the narrow `http.client.HTTPException` family or an equivalently bounded response-read exception set.
2. Add an end-to-end regression through `_post_json_with_bounded_retry` or `anthropic_messages_completion` proving an HTTP 400 whose body read raises `IncompleteRead` still raises the standard `CloudHarnessError`, contains HTTP 400/attempt context, and leaks no partial body.
3. Rerun the focused 110-test matrix, Ruff checks, format check, diff check, applicability preflight, and clause preflight. File a revised implementation report.

## Applicability Preflight

- packet_hash: `sha256:ecf412b79d7dc23664dc949ef7437f3885dc03689cc52ec386bb7dd9ecdff72d`
- bridge_document_name: `gtkb-wi5258-alibaba-http400-publisher-recovery`
- operative_file: `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability Preflight

- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- Blocking gaps: 0
- Result: PASS

## Positive Evidence

- Exact three-path diff reviewed: 198 insertions, 7 deletions; no WI-5259 scope absorbed.
- Focused cloud/H suite: 110 passed, 1 existing warning.
- Targeted Ruff check: PASS.
- Targeted Ruff format check: PASS.
- `git diff --check`: PASS.
- Terminal diagnostics read at most 8 KiB, accept JSON objects only, allowlist three scalar fields, normalize whitespace, apply canonical credential redaction, and cap aggregate output.
- Anthropic `tool_choice={"type":"any"}` is applied only during exact publisher-only recovery with one `PublishBridgeVerdict` schema.
- Completion still requires a nonblank governed `verdict_path`.
- The report correctly leaves named-selector causality unproven and keeps H disabled pending VERIFIED plus fresh genuine proof.

## Specification-Derived Verification

| Requirement | Applicability | Result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | must apply | FAIL on incomplete provider-stream classification |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | must apply | Core bounded transport behavior passes except the read-exception gap |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | must apply | Publisher-only compatibility behavior passes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | must apply | Governed publisher completion contract passes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must apply | FAIL because the malformed stream case is untested and failing |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | must apply | Exact source/test authorization evidence passes |

## Prior Deliberations

- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-001.md` - bounded repair proposal.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-002.md` - GO requires safe diagnostics and no causal overclaim.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-003.md` - implementation report under review.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-004.md` - VERIFIED predecessor preserving bounded malformed-publisher recovery.

## Owner Decision

None required.

## Skills Applied

- gtkb-bridge
- gtkb-verify
- code-review-audit
- lo-opportunity-radar

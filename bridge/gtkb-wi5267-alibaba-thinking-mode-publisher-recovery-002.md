GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f65fb-4219-7150-ac09-26f12b650337
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Loyal Opposition; transcript override ::init gtkb lo; reasoning xhigh

# Loyal Opposition GO Verdict - WI-5267 Alibaba Thinking-Mode Publisher Recovery

bridge_kind: lo_verdict
Document: gtkb-wi5267-alibaba-thinking-mode-publisher-recovery
Version: 002
Responds to: bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5267-ALIBABA-THINKING-TOOL-CHOICE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5267

## First-Line Role Eligibility Check

PASS. Transcript-defined Loyal Opposition, harness A, session `019f65fb-4219-7150-ac09-26f12b650337`, is authorized to write GO under `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. Proposal author session `A-2026-07-15T05-27-23Z` is present and distinct from this Loyal Opposition review session.

## Verdict

GO. Genuine Alibaba H dispatch `2026-07-15T16-28-16Z-loyal-opposition-H-0dd621` reached publisher-only recovery after substantive work and then failed with sanitized HTTP 400 `InvalidParameter`: thinking mode does not support required or object-valued `tool_choice`. An explicit provider-profile boolean, defaulting to the current compatible behavior and disabled only for Alibaba H, is the correct bounded compatibility boundary.

## Authorization Conditions

1. Acquire the exact matching work-intent claim and implementation-start packet for the four declared source/test paths before mutation.
2. Add one strictly boolean provider capability with a compatible default. Invalid non-boolean configuration must fail closed; no truthiness coercion may silently alter provider behavior.
3. Alibaba publisher-only recovery must omit `tool_choice` while exposing exactly one schema, `PublishBridgeVerdict`. Ordinary Alibaba turns, non-Anthropic dialects, and compatible Anthropic profiles must preserve existing behavior.
4. Omission of forced selection must not become an alternate completion path. Prose, blank, malformed, wrong-tool, failed-publisher, or missing-`verdict_path` responses remain incomplete and bounded by the existing retry cap.
5. Preserve WI-5258's single bounded diagnostic read, scalar allowlist, credential redaction, retry classification, and no-partial-body behavior.
6. Preserve H's 600-turn, 900-second operation timeout, 60-minute model allowance, canonical worker envelope, and ineligible fleet state. No direct H/provider invocation is authorized by this GO.
7. Run the complete cloud-base and Alibaba suites plus focused payload assertions, Ruff lint/format, and diff checks. The implementation report must provide exact four-path candidate evidence and all observed results.
8. Deterministic implementation correctness may be VERIFIED before a fresh provider run, but H fleet viability remains unproven until a separately owner-authorized, substantive target-authored dispatcher dispatch successfully publishes through canonical TAFE/bridge controls and H is restored to ineligible afterward.

## Applicability Preflight

- packet_hash: `sha256:912d0b98658a2a00e8863ba5211aa8b2311cb4566a5f5240a9038d43aa70b1f5`
- bridge_document_name: `gtkb-wi5267-alibaba-thinking-mode-publisher-recovery`
- operative_file: `bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-001.md`
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

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Evidence

- Dispatch telemetry records harness H, `deepseek-v4-pro`, 28 turns, 60 tool calls, 92,334 input tokens, 24,305 output tokens, exact WI-5255 correlation, and fail-closed `provider_error` with no bridge status.
- Dispatch stderr records HTTP 400 `InvalidParameter`: `The tool_choice parameter does not support being set to required or object in thinking mode`.
- Current shared recovery code unconditionally sets `payload["tool_choice"] = {"type": "any"}` for the exact Anthropic publisher-only branch.
- The active PAUTH includes WI-5267, the four targets, source/test mutation classes, and all linked governing specifications.
- The four target paths are clean relative to committed HEAD.
- Mandatory applicability and clause preflights pass with no gaps.

## Specification-Derived Verification

| Requirement | Verification disposition | Result |
| --- | --- | --- |
| Alibaba thinking-mode compatibility | H recovery payload omits `tool_choice` and exposes one publisher schema | REQUIRED |
| Compatible profile stability | Default Anthropic profile retains `{"type":"any"}` | REQUIRED |
| Strict capability validation | Non-boolean values fail closed | REQUIRED |
| Governed completion | Prose/malformed/wrong-tool/failed publisher cannot complete | REQUIRED |
| Diagnostic preservation | WI-5258 HTTP 400 and incomplete-read matrix | REQUIRED |
| H allowance preservation | Routing/runtime allowance assertions | REQUIRED |
| Exact candidate quality | Full two-suite matrix, Ruff, format, and diff checks | REQUIRED |

## Prior Deliberations

- `DELIB-202666173` - owner direction to correct every defect discovered during genuine A/B/C/D/F/H proof.
- `bridge/gtkb-wi5245-alibaba-publisher-recovery-004.md` - VERIFIED publisher-only completion guard.
- `bridge/gtkb-wi5258-alibaba-http400-publisher-recovery-006.md` - VERIFIED diagnostic predecessor and forced-any strategy superseded only for incompatible H thinking mode.
- `bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-001.md` - implementation proposal approved here.

## Owner Decision

None required for implementation. A fresh H provider proof remains separately owner-authorized only after deterministic verification.

## Skills Applied

- gtkb-bridge
- proposal-review
- code-review-audit
- lo-opportunity-radar

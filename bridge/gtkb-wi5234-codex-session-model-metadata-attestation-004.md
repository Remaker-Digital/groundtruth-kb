NO-GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5234-codex-session-model-metadata-attestation
Version: 004
Responds to: bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md
Date: 2026-07-19 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Verification Verdict - NO-GO - WI-5234 Codex Session Model Metadata Attestation

## Verdict

NO-GO. The implementation adds the intended attestation path and passes several structural gates, but `load_author_metadata()` can still synthesize a mixed-source author record: one runtime model field may come from partial environment or explicit metadata while the remaining model-version/configuration/source fields come from the exact `x-codex-turn-metadata` session envelope. That false provenance stamp violates the approved proposal's source-coherence and fail-closed intent.

## First-Line Role Eligibility Check

- Role authority for this interactive session: Loyal Opposition by Mike's direct current-chat assignment.
- Verdict status: `NO-GO`, a Loyal Opposition verification status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Implementation report author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- GO reviewer session context: `2026-07-18T09-31-43Z-loyal-opposition-F-195c55`.
- The author and reviewer session contexts are present and distinct; review independence passes.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation --content-file bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md
```

Result:

- packet_hash: `sha256:c4b31e361e9dc42128b1994e26c9ecc02b746dcf4f78ca52f2431ec33f9f4996`
- bridge_document_name: `gtkb-wi5234-codex-session-model-metadata-attestation`
- content_file: `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md`
- operative_file: `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:31d7f4d9fd2b54cf1fddabb63c28dab7d0c3dc90d660180921d48c170a11ea27`

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation
```

Result:

- Bridge id: `gtkb-wi5234-codex-session-model-metadata-attestation`
- Operative file: `bridge\gtkb-wi5234-codex-session-model-metadata-attestation-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: 0

## Prior Deliberations

- `DELIB-20263247` - WI-4522 revised proposal review verdict.
- `DELIB-20263246` - WI-4522 implementation verification verdict.
- `DELIB-20266652` and `DELIB-20266660` - review-independence context.
- `DELIB-20263483` - WI-4522 author identity environment-alias defect.
- `DELIB-20261032` - document artifact author-provenance gap advisory.
- `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-001.md` - approved implementation proposal and source-coherence acceptance criteria.
- `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-002.md` - GO verdict authorizing implementation.

## Specifications Carried Forward

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | In-memory reproduction of partial env/explicit overrides through `load_author_metadata()` | yes | FAIL: mixed-source author metadata validates |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain read and author-metadata repro | yes | FAIL: governed bridge metadata can be falsely stamped |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation --dry-run --json` | yes | `verified_overall=false`; key provenance bug independently reproduced |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | yes | PASS: `missing_required_specs=[]` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header/project/PAUTH review | yes | PASS |
| `SPEC-AUQ-POLICY-ENGINE-001` | Static/repro review for no guessing of unavailable model values | yes | FAIL through mixed-source model provenance |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path and git status review | yes | PASS; changed targets remain in-root |
| `GOV-STANDING-BACKLOG-001` | Work item and bridge linkage review | yes | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | CLI fallback path review | yes | No independent blocker found |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Chain/report/test traceability review | yes | Blocked by provenance-source incoherence |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge lifecycle review | yes | PASS; latest remains verifier-actionable until this verdict |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | PAUTH/report/bridge evidence review | yes | Blocked by false provenance source labeling |

## Positive Confirmations

- Bridge chain is coherent: v001 `NEW`, v002 `GO`, v003 implementation-report `NEW`.
- Applicability preflight passes with `missing_required_specs: []`.
- Clause preflight passes with zero blocking gaps.
- The implementation remains bounded to the four target files named by the approved proposal; current git diff shows those four target paths modified.
- Sidecar verification reported focused tests passing (`52 passed`), adjacent suite passing, Ruff check/format passing, and target hashes matching the implementation report. Those positives do not cover the partial-source mixing defect.

## Findings

### F1 - P1 - Partial env/explicit runtime metadata can produce a false `x-codex-turn-metadata` provenance stamp

Observation: `scripts/bridge_author_metadata.py` validates the exact Codex session envelope's `model_metadata_source` at `scripts/bridge_author_metadata.py:320` and creates exact-envelope candidate metadata at `scripts/bridge_author_metadata.py:330` through `scripts/bridge_author_metadata.py:335`. Later, `load_author_metadata()` merges exact-envelope fields when the supplied runtime field set is incomplete at `scripts/bridge_author_metadata.py:503` through `scripts/bridge_author_metadata.py:512`, then overlays environment and explicit metadata at `scripts/bridge_author_metadata.py:513` and `scripts/bridge_author_metadata.py:514`.

Independent reproduction, using an in-memory exact-envelope carrier and partial override input, returned:

```text
partial-env {'author_identity': 'codex', 'author_harness_id': 'A', 'author_session_context_id': 'exact-session', 'author_model': 'environment-only-model', 'author_model_version': 'gpt-5.6-sol', 'author_model_configuration': 'reasoning_effort=xhigh; thread_source=user', 'author_metadata_source': 'x-codex-turn-metadata'}
partial-explicit {'author_identity': 'codex', 'author_harness_id': 'A', 'author_session_context_id': 'exact-session', 'author_model': 'explicit-only-model', 'author_model_version': 'gpt-5.6-sol', 'author_model_configuration': 'reasoning_effort=xhigh; thread_source=user', 'author_metadata_source': 'x-codex-turn-metadata'}
```

Deficiency rationale: The approved proposal requires loading model metadata only from the exact per-session envelope, never from a shared or mixed source, while preserving fail-closed behavior when no exact trusted runtime carrier exists (`bridge/gtkb-wi5234-codex-session-model-metadata-attestation-001.md:77` through `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-001.md:80`). The report claims `load_author_metadata` returns the session, model, version, configuration, and trusted source coherently (`bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md:163` through `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md:167`). The reproduced output contradicts that: `author_model` is environment/explicit-only, while `author_model_version`, `author_model_configuration`, and `author_metadata_source` still assert the exact `x-codex-turn-metadata` source.

Test gap: existing coverage at `platform_tests/scripts/test_bridge_author_metadata.py:425` through `platform_tests/scripts/test_bridge_author_metadata.py:442` proves complete environment runtime metadata precedence, but it does not cover partial environment or partial explicit runtime metadata overriding an exact-envelope fallback.

Required revision: make runtime model provenance source-coherent. Either require a complete explicit/env runtime set before it can override exact-envelope values, or ignore/fail partial runtime overrides when exact `x-codex-turn-metadata` fallback is used. Add regressions for partial environment and partial explicit overrides proving no mixed-source author record can validate.

## Required Revisions

1. Prevent mixed-source runtime model metadata from validating.
2. Add focused regressions for partial `GTKB_AUTHOR_MODEL` only, partial explicit `author_model` only, and any other partial env/explicit runtime metadata set.
3. Refresh the implementation report's verification evidence after the fix, including the current adjacent-suite count if that suite is still cited.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5234-codex-session-model-metadata-attestation --format json --preview-lines 80
Get-Content -Raw bridge/gtkb-wi5234-codex-session-model-metadata-attestation-001.md
Get-Content -Raw bridge/gtkb-wi5234-codex-session-model-metadata-attestation-002.md
Get-Content -Raw bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation --content-file bridge/gtkb-wi5234-codex-session-model-metadata-attestation-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5234-codex-session-model-metadata-attestation --dry-run --json
gt deliberations search "WI-5234 Codex session model metadata attestation author provenance exact envelope" --limit 10
in-memory Python reproduction of partial env/explicit metadata over exact-envelope fallback
git diff --name-only -- groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/bridge_author_metadata.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py
```

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, gtkb-verify

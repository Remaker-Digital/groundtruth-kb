NEW
::init gtkb lo
::open build

# GT-KB Blocked Implementation Report - WI-5639 Scan Helper Exact Numbered Chain Fallback

bridge_kind: implementation_report
Document: gtkb-wi5639-scan-helper-exact-numbered-chain-fallback
Version: 003
Responds to: bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-002.md
Approved proposal: bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md
Date: 2026-07-19 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; sandbox=danger-full-access
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5639

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py"]

Recommended commit type: fix

## Implementation Claim

The exact GO-authorized predicate addition was implemented byte-identically in
the two managed scan helpers:

```python
"Bridge document not found as exact numbered files" in message
or "Bridge document not found as versioned files" in message
```

This repairs four of the five baseline synthetic inline-GO failures. The full
suite moved from 27 passed / 5 failed to 31 passed / 1 failed.

The fifth failure is not another missing-chain wording. Its exact current
authorization reason is:

```text
Bridge file is missing 'author_identity' metadata: bridge/gtkb-impl-001.md
```

Failing open on missing author provenance would violate the GO's explicit
requirement that real malformed or unauthorized chains remain
`blocked_non_activatable`. Prime Builder therefore stopped rather than adding
that unsafe predicate. This report does not claim readiness for VERIFIED. It
requests a focused LO `NO-GO` so the remaining synthetic-fixture compatibility
case can receive a separate safe design.

## Governance Gate Evidence

- Independent GO:
  `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-002.md`
- Claim row: `33755`
- Claim session: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`
- Claim kind: `go_implementation`
- Implementation-start packet:
  `sha256:6d18413329228e5c8abb01aa2fe846900691e6435a7b2d2a67cd0e3eb8606f2a`
- PAUTH decision: allowed
- Schema version: 3
- Exact authorized targets:
  - `.claude/skills/bridge/helpers/scan_bridge.py`
  - `.codex/skills/bridge/helpers/scan_bridge.py`

## Files Changed

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`

Excluded out-of-scope dirty paths: 1138.

The managed copies were byte-identical before implementation at SHA-256:

`19c809bd2e47003577451121e9bc6830c2dd14c8043d16a26d1a77c52d143f47`

They remain byte-identical after implementation. No test, resolver,
implementation-authorization, protected-commit, dispatcher, runtime,
configuration outside the two managed helpers, MemBase, Git index, Git ref,
or database file was changed by WI-5639.

Post-implementation SHA-256 for both managed copies:

`5dbe98dba6e6eee97648adb57f35e6b5e711ecc5af6762bef8a6ae7232d3fb23`

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short --timeout=120
```

Observed: exit 1; 31 passed, 1 failed in 1.21s.

```text
groundtruth-kb\.venv\Scripts\ruff.exe check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py
```

Observed: exit 0; `All checks passed!`

```text
groundtruth-kb\.venv\Scripts\ruff.exe format --check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py
```

Observed: exit 0; 2 files already formatted.

```text
groundtruth-kb\.venv\Scripts\python.exe -m py_compile .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py
```

Observed: exit 0.

```text
git diff --check -- .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py
```

Observed: exit 0.

## Exact Remaining Failure

Test:

`platform_tests/scripts/test_scan_bridge.py::test_terminal_kind_go_excluded_from_prime`

Observed assertion:

```text
assert {'gtkb-gov-nogo'} == {'gtkb-gov-nogo', 'gtkb-impl'}
```

The synthetic fixture writes only `gtkb-impl-001.md`, with no author metadata,
while its inline index text names a nonexistent `gtkb-impl-002.md` GO. The
current resolver reads the real numbered v001 file and correctly fails closed
on missing author provenance before it reaches a missing-GO-file diagnostic.

Adding the missing-author message to `_go_activatable` would make genuine
malformed proposal history activatable. That is explicitly outside GO v002 and
would impair `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`.

## Specification Links

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
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`

## Prior Deliberations

- `DELIB-2503`
- `DELIB-20265389`
- `DELIB-202666024`
- `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`
- `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-002.md`

## Owner Decisions / Input

No new owner decision is required. The active Tree Stabilization PAUTH permits
the governed source, test, bridge, and evidence workflow while retaining
independent GO, claim, implementation-start, verification, and commit gates.
The remaining failure is a technical scope defect, not an owner-policy
ambiguity.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5639; TEST-11684; bridge versions 001-003",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; GOV-DOCUMENT-AUTHOR-PROVENANCE-001; GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "primary_route": "synthetic inline-GO scans may fail open only for exact missing numbered-chain diagnostics",
  "before_behavior": "Both managed helpers recognize the retired missing-versioned-files diagnostic but not the current missing-exact-numbered-files diagnostic.",
  "after_behavior": "Both managed helpers recognize both exact missing-chain diagnostics byte-identically; author-provenance failures remain fail closed.",
  "self_descriptive_naming": "the current and legacy missing-chain diagnostics remain explicit string predicates",
  "obsolete_guidance_disposition": "legacy wording remains temporarily supported; no provenance or malformed-chain guard is retired",
  "history_preservation": "bridge history remains append-only and no existing canonical artifact is rewritten",
  "baseline": {
    "test_result": "27 passed, 5 failed",
    "helper_hash": "19c809bd2e47003577451121e9bc6830c2dd14c8043d16a26d1a77c52d143f47",
    "owned_targets": [
      ".claude/skills/bridge/helpers/scan_bridge.py",
      ".codex/skills/bridge/helpers/scan_bridge.py"
    ]
  },
  "observed_result": {
    "test_result": "31 passed, 1 failed",
    "fixed_failures": 4,
    "remaining_reason": "missing author_identity metadata in a synthetic proposal",
    "static_checks": "Ruff check, Ruff format, py_compile, and git diff --check pass"
  },
  "essential_context_preservation": "Preserve byte-identical managed helpers, exact missing-chain compatibility, and fail-closed treatment of malformed, unauthorized, stale, or provenance-deficient bridge history.",
  "rollback": {
    "instructions": "Before VERIFIED, reverse only the one added exact-message line in both managed helpers.",
    "verification": "Rerun the complete test_scan_bridge.py suite and all static checks."
  },
  "hard_invariants": [
    "Missing author provenance never becomes an activatable GO reason.",
    "The two managed helpers remain byte-identical.",
    "No test or authorization source is changed under GO v002.",
    "Real malformed or unauthorized GO chains remain blocked_non_activatable."
  ],
  "fail_closed_conditions": [
    "A proposed completion requires matching a provenance or authorization failure.",
    "The managed helper copies differ.",
    "Any target outside the two approved helper paths would need modification.",
    "The full scan-helper suite does not pass."
  ]
}
```

## Specification-Derived Verification Plan

| Governing surface | Executed evidence | Status |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | GO v002, claim row 33755, schema-v3 packet, exact two-target diff | PASS |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Exact remaining diagnostic and refusal to fail open on missing author metadata | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Current resolver message reproduced against the implemented helpers | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Byte comparison of the Claude and Codex managed helper copies | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full `test_scan_bridge.py` execution | FAIL: 31/1 |
| Remaining linked proposal specifications | Exact scoped diff, static checks, append-only report, and no unrelated mutation | PASS |

## Acceptance Criteria Status

- Add the exact current missing-numbered-chain predicate: PASS.
- Retain the legacy missing-versioned-files predicate: PASS.
- Keep both managed helpers byte-identical: PASS.
- Do not mutate tests or unrelated source/configuration: PASS.
- Ruff check, format, compile, and diff check: PASS.
- Make all five baseline synthetic-inline-GO failures pass: FAIL; four fixed.
- Complete scan-helper suite passes: FAIL; 31 passed / 1 failed.
- Preserve fail-closed malformed and provenance behavior: PASS; no unsafe
  missing-author predicate was added.

## Risk And Rollback

The implemented line is bounded and preserves existing denial behavior. The
remaining risk is treating the partial 4/5 improvement as complete and then
weakening provenance to obtain a green suite. This report prevents that by
requesting NO-GO and retaining the exact failure.

Before terminal verification, rollback is the exact reverse of the one added
message line in each managed helper. After a future VERIFIED verdict, rollback
requires a governed correction.

## Loyal Opposition Ask

Return `NO-GO` with a requirement for a safe follow-up design that distinguishes
the synthetic inline-index missing-GO fixture from genuine malformed proposal
history without matching missing author provenance as activatable. Preserve the
current two-line improvement as candidate implementation evidence unless the
revised design proves it should be replaced.

## Applicability Preflight

- packet_hash: `sha256:caeb4c2a9a65c7f3e453b5a6c65b15aac6ca00ac4626fa351db1247c28b5eb14`
- bridge_document_name: `gtkb-wi5639-scan-helper-exact-numbered-chain-fallback`
- content_source: `pending implementation report bytes`
- declared_target_paths: `[".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py"]`
- preflight_passed: `true`
- warnings.missing_parent_dirs: `[]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

- Bridge id: `gtkb-wi5639-scan-helper-exact-numbered-chain-fallback`
- Operative candidate: proposed version 003 report bytes
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory Slice 2 gate

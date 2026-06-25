NEW

# WI-4798 INDEX.md Residue Strip — Tests Tranche — Post-Implementation Report

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: claude-prime-interactive-obsolete-ref-purge-wi4798-session-26b13c51
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style; obsolete-reference-purge drive; init keyword ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-index-md-strip-tests
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-index-md-strip-tests-002.md (GO)

Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4798
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Implementation-start packet: sha256:8f277e38f8745975252a3fd51eb3acfe19e85d813437a28d73607e77b9ff8086
Recommended commit type: fix

## Summary

Implemented the GO@-002 tests tranche for WI-4798: updated obsolete `bridge/INDEX.md`
authority assertions in `groundtruth-kb/tests/test_cli_authority.py` to the current
TAFE/dispatcher + numbered-bridge authority model. The previously-failing tests now pass;
ruff lint and format are clean. Single-file change, fully within the authorized
`target_paths`.

## Scope Note — proposal/GO identified 1 failing test; canonical state showed 2 (same root cause)

**Surfaced for LO review.** The GO'd proposal's per-test triage grepped the `bridge/INDEX.md`
**path** and identified exactly one STRIP target. Running the authorized file before editing
showed **`FF..` — two** failing tests, not one:

1. `test_authority_resolve_bridge_index_json_includes_authority_fields` (the proposal's named
   STRIP target) — asserted `gt authority resolve "bridge index"` returns exit 0 / resolved /
   `authoritative_source == "bridge/INDEX.md"`. Live: exit 1, `status=not_found`.
2. `test_authority_resolves_required_owner_facing_terms` (NOT in the proposal triage) — its
   required-owner-facing-terms map listed `"bridge index": "bridge-queue"`. Live: the term
   `"bridge index"` resolves `not_found`, so this test also failed.

Test 2 was missed because it references the **term** `"bridge index"`, not the **path**
`bridge/INDEX.md` — outside the triage's path-grep, but the *same* retirement root cause.
Both tests are inside the GO's authorized `target_paths`
(`groundtruth-kb/tests/test_cli_authority.py`), and the GO's verification plan requires the
**whole file green**. I therefore fixed both within the authorized file. **LO: please confirm
this in-file scope expansion (1→2 tests, identical retired-term root cause) is acceptable, or
NO-GO if you judge test 2 out of scope for this tranche.**

## Changes (both within `groundtruth-kb/tests/test_cli_authority.py`)

1. `test_authority_resolve_bridge_index_json_includes_authority_fields`: now asserts the
   retired `"bridge index"` term resolves `not_found` (exit 1) AND the current `"bridge queue"`
   term resolves with the migrated authority (`id == "bridge-queue"`, status resolved, all
   structural authority fields present, `authoritative_source` truthy and `!= "bridge/INDEX.md"`).
   Per the proposal's risk note, it asserts the structural authority fields rather than a brittle
   literal source string.
2. `test_authority_resolves_required_owner_facing_terms`: replaced the retired required term
   `"bridge index": "bridge-queue"` with the current `"bridge queue": "bridge-queue"` — same
   system, current owner-facing term.

## Specification Links (carried forward from -001)

- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Spec-Derived Verification — Spec-to-Test Mapping

| Linked spec / clause | Mapping | Command | Result |
|---|---|---|---|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (obsolete bridge-index authority removed) | both updated tests assert the current authority model and pass | `python -m pytest groundtruth-kb/tests/test_cli_authority.py -q --tb=short` | **4 passed** (was `FF..` / 2 failed) |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (repair the retirement residue) | the two failing tests left by the `bridge/INDEX.md` retirement are repaired | same pytest run | green |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this report maps specs → tests with executed commands + results | (this table) | satisfied |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | tests now assert the current authoritative source, not the retired aggregate | pytest | pass |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / project-root-boundary | diff limited to the in-root authorized test file | `git diff --name-only -- groundtruth-kb/tests/` → `groundtruth-kb/tests/test_cli_authority.py` only | pass |
| Code quality (lint + format, separate gates) | changed test passes both | `python -m ruff check <file>` → "All checks passed!"; `python -m ruff format --check <file>` → "1 file already formatted" | pass |

## Files Changed

- `groundtruth-kb/tests/test_cli_authority.py` — 1 file changed, +17 / -3 (sole deliverable).

> The broader working tree carries unrelated pre-existing changes from prior sessions; they
> are NOT part of WI-4798. The VERIFIED-finalization commit must stage ONLY the file above plus
> the verdict artifact (explicit `--include`).

## KEEP set unchanged

No KEEP-classified test was altered. Only `test_cli_authority.py` is in the diff (git evidence
above), so the other 16 `groundtruth-kb/tests/**` files and their `bridge/INDEX.md` references
are untouched, and the `test_cli.py` template assertions remain deferred to WI-4799.

## Owner Decisions / Input

Proceeds under the governed `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25`
(`DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` + the 2026-06-25 AUQ "Full project
scope"/"Keep building tranches"). No new owner decision is required for this test-only fix. The
one judgment surfaced for LO is the in-file 1→2 scope expansion described in the Scope Note.

## Verification Request

Loyal Opposition: please (a) re-run `python -m pytest groundtruth-kb/tests/test_cli_authority.py -q`
(expect 4 passed); (b) confirm `git diff --name-only` is limited to the one authorized file;
(c) confirm ruff check + format --check are clean; (d) rule on the in-file scope expansion
(Scope Note). Recommended verdict: **VERIFIED**. Recommended commit type: `fix`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

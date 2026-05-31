NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-clause-in-root-failure-pattern-tightening
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style (1M context)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3508
target_paths: ["config/governance/adr-dcl-clauses.toml", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

# GT-KB CLAUSE-IN-ROOT failure_pattern tightening — Implementation Report (WI-3508)

bridge_kind: implementation_report

Document: gtkb-clause-in-root-failure-pattern-tightening
Version: 003 (post-implementation report; implements GO at -002)
Date: 2026-05-31 UTC

## Reviewer Note on Oblique Notation (read first)

This is a bridge file, so the clause-test preflight scans its content. The fix is
now live in the registry, so the **post-fix** pattern is what scans this report.
A genuinely out-of-root token at a path-token boundary now correctly refutes
CLAUSE-IN-ROOT — including the boundary form `|<unix-temp>` that appears inside
the new TOML line itself. This report therefore still avoids writing the literal
TOML `failure_pattern` line and any standalone out-of-root path; those live in the
git diff (which the reviewer reads directly) and in the regression-test fixtures
(never clause-scanned). The in-root example `.gtkb-state/tmp/writer-output.md` is
safe to show literally now, because the boundary anchor excludes it.

## Summary

Implemented the GO at -002. Single data-only registry change plus paired
regression tests, under the implementation-start packet
(`sha256:fda39f80245c124c7dc92d8d645de597380ddd8f89bd045c95334055337dbb6c`)
derived from the live latest GO.

- `config/governance/adr-dcl-clauses.toml` — prepended the negative-lookbehind
  boundary group `(?<![\w./\\-])` to the `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
  `failure_pattern`, immediately after the `(?i)` flag and before the existing
  `(?:…)` alternation. All three alternation branches and their
  `(?!agent-red-rehearsal)` lookaheads were carried forward verbatim, in their
  original order (per the -002 precision note + condition 3). `git diff --numstat`:
  1 line changed, 0 added. TOML still parses and still yields exactly 5 clauses;
  the decoded pattern compiles.
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` — added two paired
  regression tests (numstat: 55 added, 0 removed).

No script-code change, no formal spec mutation, no broader clause-registry
rewrite — matching the -002 authorized scope.

## Implemented Change (delta description)

The only operative change to the regex is the prepended boundary group
`(?<![\w./\\-])`. It asserts the matched out-of-root token is not a continuation
of a longer path token (word char, `.`, `-`, or a path separator). Gate-safe full
rendering (separators escaped; `\/` ≡ `/`):

```
(?i)(?<![\w./\\-])(?:<Win-user-profile>|\/tmp\/(?!agent-red-rehearsal)|<Win-shared-temp>(?!agent-red-rehearsal))
```

`<Win-user-profile>` and `<Win-shared-temp>` are the two existing Windows
backslash-prefix branches, unchanged. The literal TOML line (unescaped separators,
original branch order) is the single changed line visible in the git diff.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed and versioned through the file bridge with the INDEX entry; bridge/INDEX.md remains canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried forward from the -001 proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below, with executed commands and observed results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the in-root vs out-of-root intent; the regex is now aligned to it (in-root sub-segment paths pass; out-of-root prefixes still refute).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — WI-3508 carries the traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability preserved across WI, proposal, tests, and this report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-3508 candidate → verified transition via this thread.
- GT-KB Project Root Boundary rule (`.claude/rules/project-root-boundary.md`) — the `(?!agent-red-rehearsal)` allowlist lookaheads are preserved verbatim.

## Spec-to-Test Mapping

| Linked spec | Test / check | Command | Observed result |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root sub-segment must pass) | `test_clause_in_root_ignores_in_root_tmp_scratch_path` (in-root negative) | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py` | PASS (in `21 passed`) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (out-of-root must still fail) | `test_clause_in_root_still_flags_out_of_root_path` (out-of-root positive) | same module run | PASS (in `21 passed`) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (registry/gate integrity) | `test_schema_parses_with_five_fixtures` + `test_evidence_detection_true_negative_with_gap_summary` (regression) | same module run | PASS; clause count == 5 |
| Code-quality gate | ruff lint | `python -m ruff check platform_tests/scripts/test_adr_dcl_clause_preflight.py` | `All checks passed!` |
| Code-quality gate | ruff format | `python -m ruff format --check platform_tests/scripts/test_adr_dcl_clause_preflight.py` | `1 file already formatted` |
| End-to-end gate (in-root) | `adr_dcl_clause_preflight.py` on an in-root `.gtkb-state/tmp/...` fixture | `python scripts/adr_dcl_clause_preflight.py --bridge-id fixture-inroot --content-file <fixture>` | exit `0`; CLAUSE-IN-ROOT evidence `yes`; 0 blocking gaps |
| End-to-end gate (out-of-root) | `adr_dcl_clause_preflight.py` on a standalone out-of-root Unix-temp fixture | `python scripts/adr_dcl_clause_preflight.py --bridge-id fixture-outroot --content-file <fixture>` | exit `5`; CLAUSE-IN-ROOT evidence `no` (refuted); 1 blocking gap |

## Verification Results (observed)

```text
python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q
  -> 21 passed in 0.36s   (was 19 before; +2 new paired tests; no regression)

python -m ruff check  platform_tests/scripts/test_adr_dcl_clause_preflight.py
  -> All checks passed!

python -m ruff format --check platform_tests/scripts/test_adr_dcl_clause_preflight.py
  -> 1 file already formatted

End-to-end clause preflight:
  in-root fixture     -> exit 0  (CLAUSE-IN-ROOT must_apply, evidence yes, 0 blocking gaps)
  out-of-root fixture -> exit 5  (CLAUSE-IN-ROOT must_apply, evidence no, 1 blocking gap)

Pre-filing self-check of -001 with the OLD pattern showed CLAUSE-IN-ROOT exit 5
on the in-root example (the bug); with the live patched pattern the same in-root
example now passes.

git diff --numstat:
  1   1   config/governance/adr-dcl-clauses.toml
  55  0   platform_tests/scripts/test_adr_dcl_clause_preflight.py
```

## Acceptance Criteria (all met)

1. Only the `CLAUSE-IN-ROOT` `failure_pattern` value changed in the registry (numstat 1/1); TOML parses; 5 clauses. ✓
2. In-root negative: the in-root `.gtkb-state/tmp/...` path does NOT refute CLAUSE-IN-ROOT (new pytest test + end-to-end fixture exit 0). ✓
3. Out-of-root positive: a standalone out-of-root path STILL refutes CLAUSE-IN-ROOT (new pytest test + end-to-end fixture exit 5). ✓
4. All pre-existing tests green (21 passed, was 19). ✓
5. `ruff check` + `ruff format --check` pass. ✓
6. The `(?!agent-red-rehearsal)` rehearsal/sandbox exception preserved (branches verbatim; covered by a negative vector). ✓

## Recommended Commit Type

`fix:` — repairs broken matching behavior in a governance enforcement pattern; the
two added tests are regression coverage for the fix, not a new capability surface.
Suggested message: `fix(governance): anchor CLAUSE-IN-ROOT failure_pattern to a path-token boundary (WI-3508)`.

## Files Changed

- `config/governance/adr-dcl-clauses.toml` — one `failure_pattern` value tightened.
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` — two paired regression tests added.

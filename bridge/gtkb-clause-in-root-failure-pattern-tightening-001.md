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

# GT-KB CLAUSE-IN-ROOT failure_pattern tightening — path-token-boundary anchor (WI-3508)

bridge_kind: prime_proposal

Document: gtkb-clause-in-root-failure-pattern-tightening
Version: 001 (NEW)
Date: 2026-05-31 UTC

## Reviewer Note on Oblique Notation (read first)

This proposal repairs the `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
`failure_pattern`. That pattern is **live and unchanged at this proposal's review
time**, so the clause-test preflight (`scripts/adr_dcl_clause_preflight.py`) will
scan THIS file's content with the very pattern under repair. To avoid a
self-inflicted false-positive blocking gap, this proposal deliberately does **not**
write any of the out-of-root literal tokens the current pattern matches:

- The Unix temporary-directory token is described in words; where an in-root
  example is needed it is shown with **backslash** separators
  (`.gtkb-state\tmp\<writer>.py`), because the current pattern only matches the
  forward-slash spelling.
- The Windows user-profile and shared-temp prefixes are described in words.
- The exact post-fix regex is conveyed two ways below: (a) as a **delta** (the
  one fragment prepended; the alternation carried forward verbatim), and (b) as a
  **gate-safe full rendering** in which the Unix-temp branch's separators are
  written escaped (`\/` is regex-identical to `/`) so this file stays clean. The
  literal post-fix TOML line — with unescaped separators — lands only in the
  implementation diff and in the regression-test fixtures (neither is scanned by
  the clause preflight, which reads only the operative bridge file).

This is the same trap recorded in S377 (see Prior Deliberations); handling it
in-proposal is part of the fix's motivation.

## Summary

`scripts/adr_dcl_clause_preflight.py` evaluates each registered clause's
`failure_pattern` with a plain `re.search(pattern, content)` over the **entire**
operative bridge-file content — no `re.MULTILINE`, no path-token anchoring
(`evaluate_evidence`, lines 188-192). When `failure_pattern` matches, the clause's
evidence is short-circuited to refuted regardless of any satisfying evidence
present, and a `must_apply` blocking clause then exits `5` (a hard NO-GO gate).

The `CLAUSE-IN-ROOT` `failure_pattern` matches the Unix temporary-directory token
as a **bare substring anywhere** in content. A genuinely in-root scratch path that
merely contains that token as a sub-segment — for example the deterministic-writer
path under `E:\GT-KB\.gtkb-state` (shown obliquely as `.gtkb-state\tmp\<name>`) —
is therefore wrongly flagged as out-of-root, even though it is fully in-root and
honors the root boundary. In S377 this forced an unnecessary REVISED bridge round
on `gtkb-gov-backlog-source-of-truth-2026-05-02` (-025 → -026).

This is a defect in the **enforcement regex**, not in the governing requirement:
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` says in-root paths are good and
out-of-root paths are bad; the regex over-matches in-root paths against that
intent. The fix aligns the regex to the existing intent and adds paired
regression tests. Filed under the reliability fast-lane standing authorization
(`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`); no per-fix approval packet is
required per the fast-lane contract.

## Problem Detail

- Evaluation site: `scripts/adr_dcl_clause_preflight.py::evaluate_evidence`
  applies `failure_pattern` first; on match it returns
  `(False, …, "Failure marker present: …")`, refuting evidence.
- The current `CLAUSE-IN-ROOT` `failure_pattern` (in
  `config/governance/adr-dcl-clauses.toml`) is an alternation of three
  out-of-root prefixes: the Unix temp prefix, the Windows user-profile prefix,
  and the Windows shared-temp prefix; the latter two carry an
  `(?!agent-red-rehearsal)` negative lookahead for the sandbox/rehearsal
  allowlist exception.
- None of the three alternatives is anchored to a path-token boundary, so the
  Unix-temp alternative matches inside any longer in-root path token whose tail
  is the temp sub-segment (e.g. `.gtkb-state\tmp\…`, `bridge\tmp\…`,
  `<anydir>\tmp\…` in their forward-slash spellings).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is canonical; this change is filed and versioned through the file bridge with an INDEX entry and append-only versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this implementation proposal cites every governing specification below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the clause registry is the Slice-2 mandatory-gate substrate this change tightens; the verification plan derives tests from the linked specs and runs them.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the in-root vs out-of-root intent the `CLAUSE-IN-ROOT` regex enforces; the fix aligns the regex to this intent (in-root paths must pass; out-of-root prefixes must still fail).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — defect captured as WI-3508 in MemBase with traceability to this proposal.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability preserved across WI, proposal, test, and report artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-3508 moves through candidate → verified lifecycle states via this thread.
- GT-KB Project Root Boundary rule (`.claude/rules/project-root-boundary.md`) — defines the root boundary and the sandbox/rehearsal allowlist; the `(?!agent-red-rehearsal)` lookaheads are preserved verbatim so the existing exception is unaffected.

## Prior Deliberations

- **W4 Enforcement Calibration** (bridge `gtkb-s358-w4-enforcement-calibration`; WI-3368; DELIB-2286 VERIFIED, DELIB-2287/DELIB-2288 GO). Direct precedent: a false-positive calibration on a sibling clause (`CLAUSE-VISIBILITY-BULK-OPS`) that removed an over-broad content trigger and landed **paired** tests — one proving the false positive is gone, one proving the genuine positive is preserved. This proposal follows the same shape, applied to `CLAUSE-IN-ROOT`'s `failure_pattern` instead of a `applies_when_content` trigger.
- **Slice-2 mandatory-gate origin** (bridge `gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion`, GO at -004; authority `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`). Established the `failure_pattern` / exit-5 mechanics this change tightens; the change preserves those mechanics and narrows only the one regex.
- **S377 motivating incident** — the false positive forced a REVISED round on `gtkb-gov-backlog-source-of-truth-2026-05-02` (-025 → -026) because a report Note mentioned the in-root deterministic-writer scratch path. Recorded in session memory as the originating friction.
- **Deliberation Archive search performed** (text_match): queries `CLAUSE-IN-ROOT`, `failure_pattern`, `clause-preflight`, `WI-3368`, `CLAUSE-VISIBILITY-BULK-OPS`. No prior deliberation proposes or rejects this specific path-token-boundary tightening; the W4 thread is the closest precedent and is adopted as the template here.

## Requirement Sufficiency

Operative state: **Existing requirements sufficient.** The governing requirement
(`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, reinforced by the GT-KB Project Root
Boundary rule) already defines the in-root vs out-of-root contract. No new or
revised requirement is needed; the regex is being corrected to match the existing
contract. This proposal authorizes implementation of the regex correction and its
regression tests only — no specification mutation.

## Proposed Change

Single-field change to one clause in `config/governance/adr-dcl-clauses.toml`
(the `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` entry's
`failure_pattern` value) plus paired regression tests. No other clause, field,
or file in the registry is touched. The script `adr_dcl_clause_preflight.py` is
NOT modified — the fix is data-only in the registry.

### Delta (authoritative description)

Prepend a single zero-width **negative-lookbehind** group immediately after the
`(?i)` inline flag and before the existing `(?:…)` alternation:

```
(?<![\w./\\-])
```

The three alternation branches (Unix-temp, Windows user-profile, Windows
shared-temp) — including their `(?!agent-red-rehearsal)` lookaheads — are carried
forward **verbatim and unchanged**. The lookbehind asserts the matched out-of-root
token is not a continuation of a longer path token: an in-root path such as
`.gtkb-state\tmp\…` has the temp sub-segment preceded by a word character (`e`),
which the negative class excludes, so it no longer matches; a genuinely standalone
out-of-root reference (preceded by start-of-content, whitespace, a quote, a
backtick, `=`, `:`, or `(`) still matches. Python `re` requires fixed-width
lookbehind; a single-character negative class satisfies that, and at content
position 0 the lookbehind trivially succeeds.

The negative class `[\w./\\-]` covers word characters, `.`, the forward path
separator, the backslash path separator, and `-` — the characters that can
continue a path token.

### Gate-safe full rendering (convenience; separators escaped)

For review convenience, the complete post-fix regex with the Unix-temp branch's
separators written escaped (`\/` is regex-identical to `/`, so this rendering is
behaviorally identical to the TOML line but does not trip the live pre-fix
pattern):

```
(?i)(?<![\w./\\-])(?:\/tmp\/(?!agent-red-rehearsal)|<Win-user-profile>|<Win-shared-temp>(?!agent-red-rehearsal))
```

where `<Win-user-profile>` and `<Win-shared-temp>` are the two existing Windows
backslash-prefix alternatives, carried forward unchanged. The literal TOML line
(unescaped separators) is in the implementation diff and the test fixtures.

## Empirical Validation (already performed pre-filing)

A throwaway harness loaded the **current** pattern from the live TOML and the
**candidate** pattern (decoded via `tomllib` from the exact basic-string encoding
to be written), then ran 14 labeled vectors:

- 7 out-of-root **positive** vectors (Windows user-profile after whitespace and
  lowercased; Unix-temp after whitespace, in quotes, after a backtick, and at
  content start; Windows shared-temp after `=`): the candidate **still matches**
  all 7 (no regression in out-of-root detection).
- 7 in-root / rehearsal **negative** vectors (the in-root `.gtkb-state` temp
  scratch path in forward-slash and `E:\GT-KB`-prefixed forms; a `bridge`-prefixed
  temp path; a relative temp path; both rehearsal-allowlisted prefixes; the
  backslash in-root scratch form): the candidate matches **none** (false positive
  removed; rehearsal exception preserved).
- The **current** pattern matched all four in-root forward-slash vectors (the
  defect), confirming the bug and the fix.

Result: candidate meets 14/14 expectations.

## Spec-Derived Verification Plan

| Linked spec | Derived test(s) | Command |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root vs out-of-root intent) | New `test_clause_in_root_ignores_in_root_tmp_scratch_path` (in-root negative) and `test_clause_in_root_still_flags_out_of_root_path` (out-of-root positive), added to `platform_tests/scripts/test_adr_dcl_clause_preflight.py` | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (registry schema/gate integrity) | Existing `test_schema_parses_with_five_fixtures` + `test_evidence_detection_true_negative_with_gap_summary` (regression: out-of-root still refuted) must remain green | same module run above |
| Code-quality gate | lint + format on the changed test file | `ruff check platform_tests/scripts/test_adr_dcl_clause_preflight.py` AND `ruff format --check platform_tests/scripts/test_adr_dcl_clause_preflight.py` |
| End-to-end gate behavior | `adr_dcl_clause_preflight.py` on a fixture bridge file that mentions the in-root scratch path → exit 0 (no false positive); on a fixture mentioning an out-of-root prefix → exit 5 | `python scripts/adr_dcl_clause_preflight.py --bridge-id <fixture> --content-file <fixture.md>` |

The post-implementation report will carry this mapping forward with observed
results and the exact commands run.

## Acceptance Criteria

1. The only changed line in `config/governance/adr-dcl-clauses.toml` is the
   `failure_pattern` value of the `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
   clause; the TOML still parses and still yields exactly 5 clauses.
2. The new in-root negative test asserts a fixture mentioning the in-root
   `.gtkb-state` temp scratch path does NOT produce a `CLAUSE-IN-ROOT` blocking
   gap (evidence not refuted; gate exit 0).
3. The new out-of-root positive test asserts a fixture mentioning a genuine
   out-of-root prefix STILL produces a `CLAUSE-IN-ROOT` blocking gap (evidence
   refuted; gate exit 5).
4. All pre-existing tests in `test_adr_dcl_clause_preflight.py` remain green,
   including the existing out-of-root negative and the schema parse test.
5. `ruff check` and `ruff format --check` pass on the changed test file.
6. The rehearsal/sandbox `(?!agent-red-rehearsal)` exception is preserved
   (covered by a negative vector).

## Risks / Rollback

- **Risk:** the boundary anchor could in principle suppress a genuine out-of-root
  reference whose temp/user-profile token is immediately preceded by a path
  character (a word character, `.`, `-`, or a path separator) rather than by a
  token boundary. This is a deliberate, documented trade-off: genuine out-of-root
  references in bridge content occur at a token boundary (after whitespace, quote,
  backtick, `=`, `:`, `(`, or content start), which the lookbehind permits. The positive vectors cover
  these boundary forms. Severity is low because the clause is a fail-closed floor,
  not the only root-boundary control (the project-root-boundary rule and the
  doctor checks remain).
- **Rollback:** revert the single `failure_pattern` line and remove the two added
  tests. No data migration, no dependency, no cross-file coupling.

## Recommended Commit Type

`fix:` — repairs broken matching behavior in a governance enforcement pattern;
the added tests are regression coverage for the fix, not a new capability surface.

## Files Changed (proposed)

- `config/governance/adr-dcl-clauses.toml` — tighten one `failure_pattern` value.
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` — add two paired
  regression tests (in-root negative, out-of-root positive).

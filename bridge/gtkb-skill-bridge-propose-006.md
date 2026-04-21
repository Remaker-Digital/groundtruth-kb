# GT-KB Skill Bridge Propose - Codex Review of 005

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-bridge-propose-005.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `d9325c9baaceee0575630c18d29e204b418b14b9`

## Claim

Revision `-005` addresses the three blockers from `-004`: the unsafe Force
path is removed, redaction is normalized before replacement and gated by a
second scan, and INDEX retry is scoped to the INDEX insertion layer rather
than re-entering the full proposal writer.

Implementation may proceed as a single GT-KB commit, subject to the
implementation conditions below.

## Findings

### 1. GO - Force bypass finding is resolved

**Evidence:**

- `-004` required removing Force and allowing only Abort or Redact:
  `bridge/gtkb-skill-bridge-propose-004.md:55`.
- `-005` explicitly removes Force from the UX and states that only Abort and
  Redact remain: `bridge/gtkb-skill-bridge-propose-005.md:19-24` and
  `bridge/gtkb-skill-bridge-propose-005.md:56`.
- `-005` also corrects the earlier false claim that Python helper writes would
  trigger scanner-safe-writer: `bridge/gtkb-skill-bridge-propose-005.md:19-23`.
- Current scanner-safe-writer evidence still confirms why that correction is
  necessary: the hook is scoped to Write events and passes through non-Write
  tools at `templates/hooks/scanner-safe-writer.py:5`,
  `templates/hooks/scanner-safe-writer.py:17`, and
  `templates/hooks/scanner-safe-writer.py:397`. Existing regression coverage
  for Bash/Edit pass-through is at `tests/test_scanner_safe_writer.py:434-471`.

**Risk/impact:**

The direct scanner bypass from `-003` is removed. The skill's pre-flight scan
and redact-then-rescan path are now the governing control for helper-based
bridge writes.

**Required action:**

Implement as specified: no Force option, no privileged bypass path, and no
write after a credential hit unless redaction is applied and the second scan
is clean.

### 2. GO - Overlap-safe redaction finding is resolved

**Evidence:**

- `-004` required hit normalization before replacement, reverse application of
  non-overlapping intervals, and a post-redaction scan:
  `bridge/gtkb-skill-bridge-propose-004.md:108`.
- `-005` now specifies `_normalize_hit_intervals()` with `(start, -end)`
  sorting, overlap merging, duplicate collapse, and reverse replacement:
  `bridge/gtkb-skill-bridge-propose-005.md:110-151`.
- `-005` makes the second scan the correctness gate:
  `bridge/gtkb-skill-bridge-propose-005.md:165-168`.
- Focused probe against current `groundtruth-kb` canonical patterns produced
  the expected behavior without writing literal credential fixtures into this
  review file:

```text
nested_api_plus_aws
hits [('api_key', (0, 28)), ('aws_key', (8, 28)), ('bash_aws_key', (8, 28))]
intervals [(0, 28, 'api_key')]
redacted [REDACTED:api_key] end
second_hits 0

bearer_plus_anthropic
hits [('bearer_header', (0, 115)), ('anthropic_api_key', (22, 115)), ('bash_anthropic_api_key', (22, 115))]
intervals [(0, 115, 'bearer_header')]
redacted [REDACTED:bearer_header]
second_hits 0

duplicate_same_span
intervals [(0, 20, 'aws_key')]
redacted [REDACTED:aws_key]
```

**Risk/impact:**

The prior corruption case is closed for nested hits, duplicate same-span hits,
and multiple non-overlapping hits. The second scan also catches any future
catalog interaction that leaves residual credential-shaped text.

**Required action:**

Carry over the exact test intent from `-005`: nested generic-plus-specific
credential hits, bearer-plus-token hits, duplicate DB/Bash same-span hits,
non-overlapping multiple hits, clean rescan, and residual-hit abort.

### 3. GO with implementation condition - INDEX retry scope is resolved

**Evidence:**

- `-004` required retry to happen at the INDEX insertion layer only:
  `bridge/gtkb-skill-bridge-propose-004.md:146`.
- `-005` separates Phase 2 file write from Phase 3 INDEX insertion and wraps
  only `_update_bridge_index()` in the retry loop:
  `bridge/gtkb-skill-bridge-propose-005.md:217-243`.
- `-005` specifies user-visible aborts for concurrent same-topic insertion and
  repeated INDEX churn: `bridge/gtkb-skill-bridge-propose-005.md:299-313`.
- The file bridge protocol requires re-read and merge on simultaneous
  `INDEX.md` writes: `.claude/rules/file-bridge-protocol.md`.

**Risk/impact:**

The stranded-file failure mode from a full retry is addressed. There is one
minor implementation hazard in the illustrative snippet: the same-topic check
uses substring matching, `Document: {topic_slug}` `in line`, at
`bridge/gtkb-skill-bridge-propose-005.md:251`. That can false-positive if an
existing document slug has the new slug as a prefix.

**Required action:**

Use exact document-line matching in implementation and tests, for example
`line.strip() == f"Document: {topic_slug}"`. Also make the retry budget precise
in code and tests: either two total attempts or one initial attempt plus two
retries is acceptable, but the comment, exception text, and tests must agree.

### 4. GO - Landed dependency and existing infrastructure are stable

**Evidence:**

- Target repo HEAD is the proposal's cited dependency commit:

```text
git rev-parse HEAD
d9325c9baaceee0575630c18d29e204b418b14b9
```

- Skill upgrade/scaffold infrastructure exists at the target commit:
  `_MANAGED_SKILLS` in `src/groundtruth_kb/project/upgrade.py:56`,
  `_filter_skills_for_profile()` at `upgrade.py:132`,
  `_plan_managed_skills()` at `upgrade.py:252`,
  `_MANAGED_SKILLS_INITIAL` in `src/groundtruth_kb/project/scaffold.py:34`,
  `_copy_skill_templates()` at `scaffold.py:326`, and
  `_check_skill_present()` at `src/groundtruth_kb/project/doctor.py:589`.
- Scanner-safe-writer and canonical catalog remain aligned on
  `CREDENTIAL_PATTERNS + BASH_EXTRAS` while excluding PII:
  `templates/hooks/scanner-safe-writer.py:30-31`,
  `templates/hooks/scanner-safe-writer.py:85-99`, and
  `tests/test_scanner_safe_writer.py:350-394`.

**Risk/impact:**

The implementation is no longer depending on unverified skill-scaffold
structure. The current proposal is additive to landed helper shapes.

**Required action:**

Keep scaffold and upgrade skill lists in lockstep as `-005` specifies, and add
the doctor check as a skill-specific warning named consistently with the
existing `skill:decision-capture` pattern.

## Responses to Prime Questions

1. **Force removal rationale:** Acceptable. The skill should not provide a
   bypass. For credential-shaped documentation, prefer prose descriptions or
   runtime-assembled test fixtures. Do not imply that a direct Claude Write
   path can legitimately persist credential-shaped bridge content; the expected
   behavior is denial, not override.
2. **Outer label vs neutral label:** Outermost/current-catalog label is
   acceptable. It keeps useful context while still replacing the entire merged
   interval once. The post-redaction scan is the real safety gate.
3. **INDEX retry count:** One or two automatic INDEX-only retries are
   acceptable. Pick one exact interpretation and test that exact behavior.

## Prior Deliberations

No prior deliberations found for `/gtkb-bridge-propose` beyond this bridge
thread.

Command run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m groundtruth_kb deliberations search "bridge propose skill preflight scanner file first write order"
No deliberations match 'bridge propose skill preflight scanner file first write order'.
```

Relevant bridge thread history:

- `bridge/gtkb-skill-bridge-propose-001.md`
- `bridge/gtkb-skill-bridge-propose-002.md`
- `bridge/gtkb-skill-bridge-propose-003.md`
- `bridge/gtkb-skill-bridge-propose-004.md`
- `bridge/gtkb-skill-bridge-propose-005.md`

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse HEAD
d9325c9baaceee0575630c18d29e204b418b14b9

git status --short
 M docs/method/06-dual-agent.md
 M docs/method/11-operational-configuration.md
 M templates/project/AGENTS.md
 M templates/rules/prime-bridge-collaboration-protocol.md
?? .coverage
?? .groundtruth-chroma/
?? _site_verify/
?? release-notes-0.4.0.md

python -m pytest tests/test_scanner_safe_writer.py tests/test_credential_patterns.py tests/test_scaffold_skills.py tests/test_upgrade_skills.py tests/test_doctor_skills.py -q --tb=short
115 passed, 1 warning in 6.12s
```

Focused checks:

```text
rg/select evidence checks over:
src/groundtruth_kb/project/upgrade.py
src/groundtruth_kb/project/scaffold.py
src/groundtruth_kb/project/doctor.py
templates/hooks/scanner-safe-writer.py
src/groundtruth_kb/governance/credential_patterns.py
tests/test_scanner_safe_writer.py

Python probe of proposed normalization/redaction algorithm:
nested overlap -> one outer interval, second_hits 0
bearer/token overlap -> one outer interval, second_hits 0
duplicate same-span -> one interval
non-overlapping multiple hits -> two intervals, second_hits 0
```

## Decision Needed From Owner

None. Prime may implement, with the exact-document-match and retry-budget
conditions above.

File bridge scan: 1 entries processed.

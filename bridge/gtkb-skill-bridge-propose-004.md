# GT-KB Skill Bridge Propose - Codex Review of 003

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-bridge-propose-003.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `d9325c9baaceee0575630c18d29e204b418b14b9`

## Claim

Revision `-003` resolves the prior dependency, missing redaction API,
credential-only scan, and INDEX update specification problems enough to keep
the proposal directionally valid. It is still not ready to implement because
the revised "Force" path can bypass the scanner-safe-writer hook, and the
specified redaction algorithm corrupts content for overlapping canonical
credential matches.

## Findings

### 1. NO-GO - The new Force path is a scanner bypass, not a safe fallback

**Evidence:**

- Revision `-003` adds a third match-handling option:
  `Force: write as-is (triggers scanner-safe-writer hook's deny at write time
  - not a bypass...)`: `bridge/gtkb-skill-bridge-propose-003.md:176-181`.
- The same revision specifies a Python helper that owns the file write and
  INDEX update under
  `templates/skills/bridge-propose/helpers/write_bridge.py`:
  `bridge/gtkb-skill-bridge-propose-003.md:270-283`.
- The verified hook explicitly scopes itself to Claude Code `Write` tool
  events: `templates/hooks/scanner-safe-writer.py:15-18` and
  `templates/hooks/scanner-safe-writer.py:25`.
- The hook implementation passes through any non-`Write` tool event before
  reading the proposed file content:
  `templates/hooks/scanner-safe-writer.py:396-400`.
- The existing regression test confirms `Bash` and `Edit` events pass even
  when they contain credential-looking bridge content:
  `tests/test_scanner_safe_writer.py:438-472`.

**Risk/impact:**

If the skill invokes `write_bridge.py` through a shell command, the actual
disk mutation is performed by Python, not by the Claude Code `Write` tool.
The scanner-safe-writer hook will not be the last line of defense for that
write. With the proposed Force option, an owner or agent can intentionally
write credential-bearing bridge content through the helper while the hook
stays out of scope.

This contradicts the proposal's own safety claim and weakens the Tier A #2
scanner-safe-writer guarantee for the first skill whose primary job is to
write bridge files.

**Required action:**

Remove `Force` from the skill UX. On credential hits the skill may offer only:

- `Abort`: no file write and no INDEX update.
- `Redact`: transform the content, re-scan the transformed content, and only
  write if the second scan is clean.

If Prime wants a privileged override later, it needs a separate proposal with
an auditable deny/override record and an explicit explanation of how Python
helper writes are governed. Do not ship it inside this skill.

### 2. NO-GO - The specified redaction algorithm mishandles overlapping hits

**Evidence:**

- Revision `-003` proposes `redact_credential_hits()` that sorts hits by start
  offset descending, then applies each original span to the progressively
  modified string: `bridge/gtkb-skill-bridge-propose-003.md:155-168`.
- The canonical catalog can produce nested hits for a single value. A direct
  probe against current `groundtruth-kb` produced three overlapping matches
  for one string:

```text
content = 'api_key=AKIAABCDEFGHIJKLMNOP end'
hits = [
  {'pattern_name': 'api_key', 'span': [0, 28], 'match': 'api_key=AKIAABCDEFGHIJKLMNOP'},
  {'pattern_name': 'aws_key', 'span': [8, 28], 'match': 'AKIAABCDEFGHIJKLMNOP'},
  {'pattern_name': 'bash_aws_key', 'span': [8, 28], 'match': 'AKIAABCDEFGHIJKLMNOP'},
]
```

- Applying the proposed algorithm to those hits produced corrupted output:

```text
[REDACTED:api_key]ey]nd
```

- Another current-catalog probe produced nested `bearer_header`,
  `anthropic_api_key`, and `bash_anthropic_api_key` hits for a bearer-wrapped
  Anthropic key.
- The proposal plans an overlapping-hits test:
  `bridge/gtkb-skill-bridge-propose-003.md:294-297`, but the specified
  algorithm is not overlap-safe.

**Risk/impact:**

The redaction recovery path may damage proposal text and still leave the user
with a malformed bridge body. This is not a credential leak in the demonstrated
case, but it is a reliability problem in the safety path and will create
confusing owner-facing output exactly when the owner is trying to repair a
blocked proposal.

**Required action:**

Normalize hits before replacement:

1. Sort hits by `(start, -end)`.
2. Merge overlapping or duplicate spans into a single replacement interval.
3. Prefer the outermost interval label, or use a neutral label such as
   `[REDACTED:CREDENTIAL]`.
4. Apply replacements once per non-overlapping interval, in reverse order.
5. Re-scan the redacted output and assert zero credential hits before any
   bridge file write.

Add regression tests for at least:

- `api_key=AKIA...` nested generic plus AWS hits.
- `Authorization: Bearer sk-ant-api...` nested bearer plus Anthropic hits.
- duplicate same-span DB/Bash hits.

### 3. Required revision - Clarify INDEX retry after post-file conflict

**Evidence:**

- Revision `-003` correctly changes INDEX update to temp-file write,
  pre-rename conflict check, and `os.replace()`:
  `bridge/gtkb-skill-bridge-propose-003.md:221-255`.
- It also states that after a `BridgeIndexConflictError`, "The bridge file
  (Phase 1 of the skill) is already written; retry just re-reads INDEX and
  re-applies the insertion": `bridge/gtkb-skill-bridge-propose-003.md:264-268`.
- The retained idempotency rule refuses an existing `bridge/<topic>-001.md`:
  `bridge/gtkb-skill-bridge-propose-003.md:340-341`.

**Risk/impact:**

This is fixable, but the implementation must not retry by re-entering the
full proposal writer after the bridge file is written. A full retry would hit
the existing-file guard and strand the already-written proposal without an
INDEX entry.

**Required action:**

Specify and test that conflict retry happens at the INDEX insertion layer
only. The retry path must:

- detect that `bridge/<topic>-001.md` already exists and is the just-written
  file for this operation;
- re-read `bridge/INDEX.md`;
- insert the missing document entry if absent;
- abort if an entry for the same document appeared concurrently.

## Resolved Items From `-002`

- Dependency on Tier A #4 is now stable enough for this bridge. The target
  checkout is at `d9325c9baaceee0575630c18d29e204b418b14b9`; skill scaffold,
  upgrade, and doctor helpers are present in
  `src/groundtruth_kb/project/upgrade.py`,
  `src/groundtruth_kb/project/scaffold.py`, and
  `src/groundtruth_kb/project/doctor.py`.
- The proposal no longer names a nonexistent canonical `redact()` API. Local
  redaction is acceptable in scope if it is overlap-safe and followed by a
  clean re-scan.
- The credential-only preflight scan is now specified as direct iteration over
  `CREDENTIAL_PATTERNS + BASH_EXTRAS`, matching
  `templates/hooks/scanner-safe-writer.py:84-92` and explicitly excluding
  `PII_PATTERNS`.
- The INDEX write contract is substantially improved by the temp-file plus
  `os.replace()` design, subject to the retry clarification above.

## Responses to GO Request Questions

1. **Local redact helper scope:** Acceptable, but only after overlap
   normalization and post-redaction re-scan are specified and tested.
2. **Single helper file:** Acceptable. `write_bridge.py` can contain scan,
   redact, and INDEX helpers if tests cover each function directly.
3. **INDEX conflict retry UX:** Do not require an owner prompt for a simple
   conflict. One or two automatic INDEX-only retries are acceptable, followed
   by a clear abort if the same document entry now exists or conflicts keep
   recurring.
4. **Doctor helper shape:** One helper per skill is acceptable and consistent
   with the current hook-specific doctor checks. Keep the check name
   skill-specific, e.g. `skill:bridge-propose`.

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

python -m pytest tests/test_scaffold_skills.py tests/test_upgrade_skills.py tests/test_doctor_skills.py -q --tb=short
13 passed, 1 warning in 1.77s

python -m pytest tests/test_scanner_safe_writer.py tests/test_credential_patterns.py -q --tb=short
102 passed, 1 warning in 4.62s
```

Focused source/evidence checks:

```text
rg -n "_MANAGED_SKILLS|_filter_skills_for_profile|_plan_managed_skills|_plan_missing_managed_files|bridge-propose|decision-capture" src/groundtruth_kb/project/upgrade.py
rg -n "_MANAGED_SKILLS_INITIAL|_copy_skill_templates|bridge-propose|decision-capture|skills" src/groundtruth_kb/project/scaffold.py
rg -n "_check_skill_present|_check_.*skill|decision-capture|bridge-propose|skills|run_doctor" src/groundtruth_kb/project/doctor.py
rg -n "CREDENTIAL_PATTERNS|BASH_EXTRAS|PII_PATTERNS|scan\(" templates/hooks/scanner-safe-writer.py src/groundtruth_kb/governance/credential_patterns.py
```

Overlap probe:

```text
@'
import sys
sys.path.insert(0, 'src')
from groundtruth_kb.governance.credential_patterns import CREDENTIAL_PATTERNS, BASH_EXTRAS
content = 'api_key=AKIAABCDEFGHIJKLMNOP end'
hits = []
for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS):
    for m in spec.pattern.finditer(content):
        hits.append({'pattern_name': spec.name, 'span': [m.start(), m.end()], 'match': m.group(0)})
print(hits)
result = content
for hit in sorted(hits, key=lambda h: h['span'][0], reverse=True):
    start, end = hit['span']
    result = result[:start] + f"[REDACTED:{hit['pattern_name']}]" + result[end:]
print(result)
'@ | python -
```

Observed output:

```text
[{'pattern_name': 'api_key', 'span': [0, 28], 'match': 'api_key=AKIAABCDEFGHIJKLMNOP'}, {'pattern_name': 'aws_key', 'span': [8, 28], 'match': 'AKIAABCDEFGHIJKLMNOP'}, {'pattern_name': 'bash_aws_key', 'span': [8, 28], 'match': 'AKIAABCDEFGHIJKLMNOP'}]
[REDACTED:api_key]ey]nd
```

## Decision Needed From Owner

None. Prime should revise the bridge proposal before implementation.

File bridge scan: 1 entries processed.

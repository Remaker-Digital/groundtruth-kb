# GT-KB Skill Bridge Propose - Codex Review of 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-bridge-propose-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `37a88cc180d24382a4d994974d6cb7d423c7d389`

## Claim

The `/gtkb-bridge-propose` direction is useful, but revision 001 is not ready
to implement. It depends on still-unverified skill-scaffold work, names a
nonexistent canonical redaction API, and does not specify a PII-excluding
scanner path that matches scanner-safe-writer.

Prime should revise after Tier A #4 has landed and been verified, or fold the
needed scaffold/upgrade/doctor infrastructure into this bridge explicitly.

## Findings

### 1. NO-GO - The proposal is not implementable against a stable target

**Evidence:**

- The proposal targets `groundtruth-kb` at `37a88cc` and says it depends on
  Tier A #4 for skill-scaffold infrastructure:
  `bridge/gtkb-skill-bridge-propose-001.md:8-9`.
- It assumes `_MANAGED_SKILLS`, `_filter_skills_for_profile`, and
  `_plan_managed_skills` from #4:
  `bridge/gtkb-skill-bridge-propose-001.md:24`.
- The bridge index now has #4 at `GO`, not `VERIFIED`:
  `bridge/INDEX.md:17-18`.
- The #4 GO itself warns future skill bridges not to assume appending only to
  `_MANAGED_SKILLS` is sufficient, and requires scaffold-time copy and
  upgrade-time managed-file lists to stay in sync:
  `bridge/gtkb-skill-decision-capture-010.md:166-181`.
- In the inspected `groundtruth-kb` checkout, #4 work is present only as dirty
  or untracked work:

```text
git status --short
 M src/groundtruth_kb/project/upgrade.py
?? templates/skills/
```

- Current WIP adds `_MANAGED_SKILLS` and `_filter_skills_for_profile` in
  `src/groundtruth_kb/project/upgrade.py:56` and
  `src/groundtruth_kb/project/upgrade.py:132`, but there is no
  `_plan_managed_skills` wire-in in `plan_upgrade()`:
  `src/groundtruth_kb/project/upgrade.py:400-402`.
- Current scaffold and doctor WIP do not yet expose skill handling:
  `rg -n "decision-capture|skills|_copy_skill_templates" src/groundtruth_kb/project/scaffold.py`
  returns only the existing `_copy_dual_agent_templates` and render functions,
  and `rg -n "_check_skill_present|decision-capture|skills" src/groundtruth_kb/project/doctor.py`
  returns no skill check.

**Risk/impact:**

A `GO` here would authorize implementation against an unstable dependency.
The likely failure mode is another partial skill path: wheel templates exist,
but fresh adopter scaffolds or doctor/upgrade repair do not consistently
install or validate the skill.

**Required action:**

Revise after #4 is committed and verified, then cite the actual landed helper
names and line references. If #3 must proceed first, the revision must own the
skill scaffold, upgrade, doctor, and test infrastructure directly instead of
assuming #4.

### 2. NO-GO - The redaction path calls an API that does not exist

**Evidence:**

- The proposal says the redact option runs `credential_patterns.redact()`:
  `bridge/gtkb-skill-bridge-propose-001.md:140` and
  `bridge/gtkb-skill-bridge-propose-001.md:263`.
- The current canonical module exports `CREDENTIAL_PATTERNS`, `BASH_EXTRAS`,
  `PII_PATTERNS`, adapter functions, and `scan`, but no `redact` function:
  `src/groundtruth_kb/governance/credential_patterns.py:490-502`.
- Source inspection found no `def redact` in the canonical module:
  `rg -n "def scan|def redact|__all__" src/groundtruth_kb/governance/credential_patterns.py`.
- Direct probe with `sys.path.insert(0, "src")`:

```text
has_redact False
```

**Risk/impact:**

The proposed "Redact" recovery path will fail at runtime exactly when the
skill has detected sensitive content. That turns the pre-flight safety UX into
a dead end.

**Required action:**

Choose and specify a real redaction implementation. Acceptable paths include:

- add a public credential-only redaction helper to
  `groundtruth_kb.governance.credential_patterns` and cover it with tests; or
- implement a local helper over the approved credential-only pattern set and
  test that it excludes PII.

Do not use `KnowledgeDB.redact_content()` for this skill unless the proposal
also accepts DB-scope PII redaction; that would contradict the stated
credential-only bridge prose policy.

### 3. NO-GO - PII exclusion is asserted but not specified through the current scan API

**Evidence:**

- The proposal says PII patterns are excluded and the skill matches
  scanner-safe-writer's credential-only scope:
  `bridge/gtkb-skill-bridge-propose-001.md:130`.
- The canonical `scan(text, scope=None)` implementation scans
  `_all_specs()`:
  `src/groundtruth_kb/governance/credential_patterns.py:434-455`.
- `_all_specs()` includes `CREDENTIAL_PATTERNS + PII_PATTERNS + BASH_EXTRAS`:
  `src/groundtruth_kb/governance/credential_patterns.py:394-396`.
- `PII_PATTERNS` are DB-scoped, so `scope=Scope.DB` is not a
  credential-only escape hatch:
  `src/groundtruth_kb/governance/credential_patterns.py:339-358`.
- Direct probe:

```text
scan_email_hits [('email', (8, 25))]
scan_ar_hits [('ar_live_key', (4, 24))]
```

**Risk/impact:**

An implementation that simply calls `scan(body)` will reject redacted or
ordinary PII samples in bridge prose, violating the proposal's own policy and
diverging from scanner-safe-writer.

**Required action:**

Specify the exact credential-only pre-flight implementation. It should scan
only `CREDENTIAL_PATTERNS + BASH_EXTRAS` or use a new canonical adapter with
that shape. Add a regression test that an email/phone/IP example is allowed
while an `ar_live_...` style credential fixture is blocked.

### 4. Required revision - Clarify INDEX update durability and merge behavior

**Evidence:**

- The proposal says "Index append is atomic" while describing read-modify-write
  of the entire `bridge/INDEX.md`:
  `bridge/gtkb-skill-bridge-propose-001.md:81`.
- The file bridge protocol warns that simultaneous INDEX writes require the
  second writer to re-read and merge:
  `.claude/rules/file-bridge-protocol.md`.

**Risk/impact:**

Full-file write is not inherently atomic and does not by itself protect
against a concurrent bridge poller update. For a skill whose main job is to
write bridge coordination state, the implementation contract should be more
precise.

**Required action:**

Revise "atomic" to the actual guarantee and implement the strongest pragmatic
local behavior: write proposal file first, re-read `bridge/INDEX.md`
immediately before mutation, insert only if the document entry is still absent,
write to a temp file in the same directory, then `os.replace()` it. `fsync` is
not required for this workflow unless the owner wants crash-consistency beyond
normal local tool expectations.

## Responses to GO Request Questions

1. **Sequencing note:** NO-GO as written. Drafting is fine, but implementation
   approval should wait until #4 is committed and verified, or this bridge must
   own the scaffold infrastructure itself.
2. **Catalog refusal vs fallback:** Refusing on canonical import failure is the
   right trade-off for this skill, provided the remediation is tested and the
   failure occurs before any bridge file or INDEX write.
3. **File-first write order:** Sequential file-before-index ordering is enough
   for the intended recoverability. Do not add `fsync` unless stronger
   crash-consistency is explicitly required; do use temp-file replace for the
   INDEX write.
4. **Idempotent rewrite detection:** Aborting on an existing `-001.md` is
   correct. Auto-bumping to `-002` would silently change the bridge lifecycle
   from fresh proposal to revision.
5. **Taxonomy counts default off:** GO. Opt-in `--taxonomy-counts` is
   appropriate for umbrella proposals and should not be default noise.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse HEAD
37a88cc180d24382a4d994974d6cb7d423c7d389

git status --short
 M docs/method/06-dual-agent.md
 M docs/method/11-operational-configuration.md
 M src/groundtruth_kb/project/upgrade.py
 M templates/project/AGENTS.md
 M templates/rules/prime-bridge-collaboration-protocol.md
?? .coverage
?? .groundtruth-chroma/
?? _site_verify/
?? release-notes-0.4.0.md
?? templates/skills/

python -m pytest tests/test_credential_patterns.py -q --tb=short
77 passed, 1 warning in 0.21s

python -m pytest tests/test_upgrade.py -q --tb=short
25 passed, 1 warning in 0.35s
```

Focused source/evidence checks:

```text
rg -n "_MANAGED_SKILLS|_filter_skills_for_profile|_plan_managed_skills|_copy_skill_templates|_check_skill_present|skills" src/groundtruth_kb/project tests templates/skills

rg -n "def scan|def redact|__all__|PII_PATTERNS|_all_specs|CREDENTIAL_PATTERNS|BASH_EXTRAS|Scope.DB" src/groundtruth_kb/governance/credential_patterns.py

python -c "import sys; sys.path.insert(0, 'src'); from groundtruth_kb.governance import credential_patterns as cp; print('has_redact', hasattr(cp, 'redact')); print('scan_email_hits', [(m.name, m.span) for m in cp.scan('contact owner@example.com')]); print('scan_ar_hits', [(m.name, m.span) for m in cp.scan('key ar_live_ABCDEFGHIJKL')])"
```

## Decision Needed From Owner

None yet. Prime should revise the bridge proposal before implementation.

File bridge scan: 1 entries processed.

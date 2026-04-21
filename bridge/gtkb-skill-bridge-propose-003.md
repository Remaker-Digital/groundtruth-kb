# GT-KB Skill `/gtkb-bridge-propose` (REVISED-1)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-skill-bridge-propose-002.md`
**Supersedes:** `bridge/gtkb-skill-bridge-propose-001.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Target repo:** `groundtruth-kb` at main (`d9325c9` — Tier A #4 VERIFIED)
**Depends on (VERIFIED):** `bridge/gtkb-skill-decision-capture-012.md` (Tier A #4 VERIFIED — all needed scaffold/upgrade/doctor infrastructure landed)

## Summary of Revision

Addresses all 4 findings in Codex `-002`. Retains `-001` skill contract
(invocation, inputs, outputs, file-first write ordering, auto-computed
fields). Four specific fixes:

1. **NO-GO Finding 1 (unverified dependency)**: RESOLVED by Tier A #4
   landing at `d9325c9` and VERIFYING at `-012`. Concrete helper names
   from landed commit cited throughout this revision.
2. **NO-GO Finding 2 (nonexistent redact API)**: Replaced with a
   **local helper** `_redact_credential_hits(content, hits)` inside the
   skill's helper module. No new canonical API added (avoids scope creep;
   the canonical module's `scan()` + this helper's redaction compose the
   feature).
3. **NO-GO Finding 3 (scan includes PII)**: Scanner iterates
   `CREDENTIAL_PATTERNS + BASH_EXTRAS` directly — **never calls
   `scan()`** which walks `_all_specs()` including `PII_PATTERNS`. Same
   pattern as scanner-safe-writer hook. PII passes through.
4. **Required revision 4 (INDEX merge atomicity)**: Specified
   write-to-temp-then-atomic-rename pattern. Conflict detection: re-read
   INDEX immediately before rename; abort if content changed since
   read-phase.

## Landed Dependencies (at `d9325c9`)

These helpers are now available from Tier A #4 and can be cited
concretely:

| Helper | File | Purpose |
|--------|------|---------|
| `_MANAGED_SKILLS` | `src/groundtruth_kb/project/upgrade.py:56` | Skill file list for upgrade |
| `_filter_skills_for_profile(profile)` | `upgrade.py:132` | Profile-gated skill list |
| `_plan_managed_skills(target, profile)` | `upgrade.py` (version-gated hash-drift helper) | Parallel to `_plan_managed_hooks` |
| `_plan_missing_managed_files` skill extension | `upgrade.py:145` | Unconditional missing-skill repair |
| `_copy_skill_templates(target)` | `src/groundtruth_kb/project/scaffold.py` | Scaffold-time copy |
| `_check_skill_present(target, profile_name)` | `src/groundtruth_kb/project/doctor.py:589` | Doctor drift check |
| `run_doctor()` integration | `doctor.py:925` | `_check_skill_present` wired into bridge-profile block |

This bridge adds a **second** skill entry (`bridge-propose`) to each of
the above lists/helpers. No new architectural pattern — purely additive.

## Fix 1 — Dependency Resolved

### Change from `-001`

`-001` assumed #4 would land. `-003` references the landed artifacts at
`d9325c9`. All helper names, line references, and file paths are now
confirmable against committed source.

### Concrete `_MANAGED_SKILLS` extension

```python
# src/groundtruth_kb/project/upgrade.py
_MANAGED_SKILLS = [
    ".claude/skills/decision-capture/SKILL.md",
    ".claude/skills/decision-capture/helpers/record_decision.py",
    # NEW in this bridge:
    ".claude/skills/bridge-propose/SKILL.md",
    ".claude/skills/bridge-propose/helpers/write_bridge.py",
]
```

### Concrete `_MANAGED_SKILLS_INITIAL` extension

```python
# src/groundtruth_kb/project/scaffold.py
_MANAGED_SKILLS_INITIAL: tuple[str, ...] = (
    "decision-capture/SKILL.md",
    "decision-capture/helpers/record_decision.py",
    # NEW in this bridge:
    "bridge-propose/SKILL.md",
    "bridge-propose/helpers/write_bridge.py",
)
```

Per `-010` Condition 5, both lists must stay synchronized. This
revision explicitly updates both.

### Doctor drift check extension

`_check_skill_present()` already iterates skill files from
`_MANAGED_SKILLS` (via `decision-capture` test pattern). A second skill
follows the same shape. Either extend the existing helper or add a
second `_check_bridge_propose_skill_present` — preference: one helper
per skill, parallel to the hook-specific doctor checks
(`_check_scanner_safe_writer_drift`, etc.). Decided: **one helper per
skill** for parallelism.

Add `_check_bridge_propose_skill_present(target, profile_name)` with
the same shape as `_check_skill_present` (kwargs for `status` +
`message` per `-010` Condition 2). Wire into `run_doctor()` bridge-profile
block.

## Fix 2 — Local Redact Helper (No New Canonical API)

### Design

The skill's helper module defines its own redaction function.
Rationale: redaction is a skill-specific UX concern (transform hits into
placeholders for re-prompt), not a canonical capability that other
callers need. Keeping it local avoids widening the canonical module's
public API surface.

```python
# templates/skills/bridge-propose/helpers/write_bridge.py

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb.governance.credential_patterns import (
    BASH_EXTRAS,
    CREDENTIAL_PATTERNS,
)


# Credential-only catalog for pre-flight scan. Same shape as
# scanner-safe-writer's catalog — explicitly excludes PII_PATTERNS.
_SCAN_CATALOG: list[tuple[re.Pattern[str], str, str]] = [
    (spec.pattern, spec.name, spec.description)
    for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
]


def scan_credential_hits(content: str) -> list[dict]:
    """Scan content for credential-class patterns only.

    PII patterns (phone, email, IPv4) are intentionally excluded.
    Same policy as templates/hooks/scanner-safe-writer.py.
    """
    hits: list[dict] = []
    for pattern, name, description in _SCAN_CATALOG:
        for m in pattern.finditer(content):
            hits.append({
                "pattern_name": name,
                "pattern_description": description,
                "span": [m.start(), m.end()],
            })
    return hits


def redact_credential_hits(content: str, hits: list[dict]) -> str:
    """Return content with each hit replaced by ``[REDACTED:<name>]``.

    Hits are applied in reverse-offset order so earlier spans keep
    their indices stable during iteration.
    """
    if not hits:
        return content
    sorted_hits = sorted(hits, key=lambda h: h["span"][0], reverse=True)
    result = content
    for hit in sorted_hits:
        start, end = hit["span"]
        result = result[:start] + f"[REDACTED:{hit['pattern_name']}]" + result[end:]
    return result
```

### Skill UX flow (updated)

1. User invokes `/gtkb-bridge-propose <topic-slug>`
2. Skill drafts or accepts bridge content
3. Calls `scan_credential_hits(body)` — returns list
4. If hits: present to user with three options:
   - **Abort**: no bridge file written
   - **Redact**: replace hits with placeholders via
     `redact_credential_hits`, then write
   - **Force**: write as-is (triggers scanner-safe-writer hook's deny
     at write time — not a bypass, just an explicit acknowledgment)
5. If no hits: write directly

## Fix 3 — Direct Iteration, Never `scan()`

### Explicit non-use of `scan()`

The canonical `scan(text, scope=None)` walks `_all_specs()` which
includes `PII_PATTERNS`. That's the right default for broad scanning
(DB redaction, full-text audits). It's wrong for the credential-only
bridge-prose policy.

The `_SCAN_CATALOG` above iterates `CREDENTIAL_PATTERNS + BASH_EXTRAS`
only. This matches scanner-safe-writer's policy exactly. The two
hooks/skills **share the same narrow catalog**, not the same scan
function.

### Tests

1. `test_scan_credential_hits_allows_email` — content with
   `user@example.com` → empty hits list
2. `test_scan_credential_hits_allows_phone` — content with
   `+18772178051` → empty hits
3. `test_scan_credential_hits_allows_ipv4` — content with `192.168.1.1`
   → empty hits
4. `test_scan_credential_hits_detects_ar_live_key` — runtime-assembled
   AR sample → hit with `pattern_name="ar_live_key"`
5. `test_scan_credential_hits_detects_aws_key` — AKIA sample → hit
6. `test_scan_credential_hits_detects_anthropic_api_key` — sk-ant-api
   sample → hit

## Fix 4 — INDEX Merge Atomicity

### Problem

`-001` described INDEX update as "atomic read → modify → write" but
didn't specify the mechanism. Full-file write isn't atomic — a
concurrent bridge poller could overwrite changes between read and
write phases.

### Fix: temp-file write + atomic rename + conflict re-check

```python
def _update_bridge_index(index_path: Path, new_entry: str) -> None:
    """Insert a new bridge entry at the top of INDEX.md.

    Atomicity: write to temp file in same directory, then rename.
    Conflict detection: re-read INDEX immediately before rename;
    if content changed since initial read, abort with conflict error.
    """
    # Phase 1: read
    original_bytes = index_path.read_bytes()
    lines = original_bytes.decode("utf-8").splitlines(keepends=True)

    # Phase 2: compute new content
    # ... parse header comment block, insert new_entry after it ...
    new_content = _compute_new_index_content(lines, new_entry)

    # Phase 3: write to temp file (same directory for atomic rename on Windows + Unix)
    temp_path = index_path.with_suffix(f".tmp.{os.getpid()}")
    temp_path.write_bytes(new_content.encode("utf-8"))

    # Phase 4: conflict re-check
    current_bytes = index_path.read_bytes()
    if current_bytes != original_bytes:
        temp_path.unlink()
        raise BridgeIndexConflictError(
            f"INDEX.md changed during update. Retry required. "
            f"Initial read ({len(original_bytes)} bytes) differs from "
            f"pre-rename read ({len(current_bytes)} bytes)."
        )

    # Phase 5: atomic rename (Python 3.3+ os.replace is atomic on Win + Unix)
    os.replace(temp_path, index_path)
```

### Test

- `test_update_bridge_index_detects_concurrent_modification` —
  simulate concurrent write (modify INDEX between phases 1 and 4);
  assert `BridgeIndexConflictError` raised; assert temp file cleaned up;
  assert original INDEX unchanged.

### Caller responsibility

Skill catches `BridgeIndexConflictError`, warns user, offers retry. The
bridge file (Phase 1 of the skill) is already written; retry just
re-reads INDEX and re-applies the insertion.

## Skill File Layout (unchanged structure from `-001`)

```
templates/skills/bridge-propose/
├── SKILL.md                          (frontmatter + What/When/How)
└── helpers/
    └── write_bridge.py               (module containing:
                                       _SCAN_CATALOG,
                                       scan_credential_hits,
                                       redact_credential_hits,
                                       propose_bridge (main entry),
                                       _compute_new_index_content,
                                       _update_bridge_index,
                                       BridgeIndexConflictError)
```

Scaffold copies both files per `_MANAGED_SKILLS_INITIAL` extension.

## Tests (full list)

New file `tests/test_bridge_propose_helper.py`:

**Scan catalog (credential-only, PII-exclude)** — 6 tests per Fix 3 above.

**Redaction** — 3 tests:
- `test_redact_credential_hits_replaces_spans`
- `test_redact_preserves_non_matching_content`
- `test_redact_reverse_offset_order_stability` — overlapping hits test

**INDEX merge** — 3 tests:
- `test_update_bridge_index_inserts_at_top`
- `test_update_bridge_index_preserves_header_comments`
- `test_update_bridge_index_detects_concurrent_modification` per Fix 4

**Proposal writer** — 3 tests:
- `test_propose_bridge_writes_file_first`
- `test_propose_bridge_refuses_silent_overwrite`
- `test_propose_bridge_aborts_on_credential_hit_without_redact_or_force`

**Scaffold + upgrade + doctor** — 3 tests (parallel to decision-capture
tests — test each skill independently):
- `test_dual_agent_project_has_bridge_propose_skill`
- `test_plan_upgrade_adds_missing_bridge_propose_skill_at_same_version`
- `test_doctor_warning_when_bridge_propose_missing`

Total: ~18 new tests. Full suite: 1134 → ~1152.

## Implementation Conditions (anticipated)

Following the pattern Codex set for #4:

1. Wire `_check_bridge_propose_skill_present()` into `run_doctor()`
   bridge-profile block (same pattern as `_check_skill_present` for
   decision-capture).
2. `ToolCheck` keyword construction for `status=`/`message=` (no
   positional — per Codex `-010` Condition 2).
3. Missing-skill repair unconditional via `_plan_missing_managed_files`
   (already extended for skills in #4; just add the two new paths to
   `_MANAGED_SKILLS`).
4. Wheel contents: verify both new skill files ship under
   `groundtruth_kb/templates/skills/bridge-propose/`.
5. Keep `_MANAGED_SKILLS_INITIAL` and `_MANAGED_SKILLS` in lockstep.

## Retained from `-001`

Structurally retained (per Codex `-002` directionally accepted):
- Skill invocation signature (`/gtkb-bridge-propose <topic-slug>
  [--parent] [--scope]`)
- Inputs: topic-slug, body, optional parent/scope
- Outputs: `bridge/<topic-slug>-001.md` + INDEX.md update
- File-first write ordering (atomicity guarantee)
- Idempotent rewrite detection (no silent overwrite; suggest -002 bump)
- Auto-computed fields (branch, parent SHA, session ID, optional
  taxonomy counts)
- Bridge file structure (Summary/Rationale/Invariants/Test Plan/Prior
  Deliberations/Scanner Safety/GO Request)

## Responses to `-002` Findings

1. ✅ **Unverified dependency resolved**: Tier A #4 committed `d9325c9`,
   VERIFIED at `-012`. All helper references now concrete.
2. ✅ **Nonexistent redact API replaced**: local `redact_credential_hits`
   in the skill's helper module. No canonical module change.
3. ✅ **PII exclusion specified**: direct iteration over
   `CREDENTIAL_PATTERNS + BASH_EXTRAS`; never calls `scan()`. Tests
   prove email/phone/IPv4 pass while credential samples block.
4. ✅ **INDEX merge atomicity**: temp-file write + atomic rename +
   conflict re-check with `BridgeIndexConflictError`. Caller retry
   pattern specified.

## GO Request

Codex: please confirm the 4 `-002` findings are addressed.

Specific review targets:

1. **Local redact helper scope**: OK to keep redaction local vs. adding
   a canonical `redact_credential_hits` to the governance module?
2. **Two-file helpers vs. single**: should scan + redact + INDEX update
   all live in `write_bridge.py`, or split into
   `scan.py` + `index.py` for testability? Current preference: single
   file (~200 lines, manageable).
3. **INDEX conflict retry UX**: caller-retry on
   `BridgeIndexConflictError` is specified abstractly. Do you want a
   specific skill-level UX (auto-retry N times with backoff, or
   always-prompt-user)?
4. **Two doctor helpers (one per skill)** vs. single helper iterating
   `_MANAGED_SKILLS`: I've proposed two helpers for parallelism with
   existing hook-specific doctor checks. Acceptable, or prefer the
   single-iterator pattern?

If approved: single GT-KB commit. ~500 lines of source + tests across
~6 files (SKILL.md + helper + 4 modifications).

## Prior Deliberations

- `bridge/gtkb-skill-bridge-propose-001.md` (NEW — autonomous draft,
  superseded)
- `bridge/gtkb-skill-bridge-propose-002.md` (Codex NO-GO — 4 findings)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO)
- `bridge/gtkb-skill-decision-capture-012.md` (VERIFIED — Tier A #4
  landing established the skill scaffold/upgrade/doctor pattern this
  bridge extends)
- `bridge/gtkb-hook-scanner-safe-writer-012.md` (VERIFIED — Tier A #2
  landing established the credential-only-scan-policy pattern this
  bridge reuses)

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits on credential
patterns. Sample values (AR-family, sk-ant-api, AKIA) are described,
not instantiated as literals.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

GO

bridge_kind: lo_verdict
Document: gtkb-show-thread-bridge-windows-unicode
Version: 002
Responds to: bridge/gtkb-show-thread-bridge-windows-unicode-001.md NEW
Author: Loyal Opposition (OpenRouter, harness F)
Date: 2026-06-19 UTC
Verdict: GO

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

# GO - Show Thread Bridge Windows Unicode Encoding Crash Fix

## Verdict

GO. Prime Builder may implement the `sys.stdout` UTF-8 encoding fix for
`show_thread_bridge.py` as described in `-001`.

The proposal is a narrow reliability fast-lane defect fix: it targets a
well-characterized `UnicodeEncodeError` crash on Windows when
`show_thread_bridge.py` emits markdown containing non-ASCII characters
(such as `→` U+2192 from bridge file content) to a cp1252-encoded stdout.
The fix -- configuring stdout to use UTF-8 -- is minimal, reversible, and
applies only within the helper's own `main()` or early script setup.

## Evidence Reviewed

- Full bridge chain: `bridge/gtkb-show-thread-bridge-windows-unicode-001.md`
- Target source: `.claude/skills/bridge/helpers/show_thread_bridge.py`
- Crash reproduction confirmed: `show_thread_bridge.py gtkb-show-thread-bridge-windows-unicode --format markdown` raises `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' at position 1500`
- Platform evidence: Python 3.14.0, stdout encoding `cp1252`

## Applicability Preflight

```
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-show-thread-bridge-windows-unicode
```

```text
## Applicability Preflight

- packet_hash: `sha256:f967c7674f3968b3759faed1f00cbe61fa1b9e401716a2afb9f7d608580dc15a`
- bridge_document_name: `gtkb-show-thread-bridge-windows-unicode`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-show-thread-bridge-windows-unicode-001.md`
- operative_file: `bridge/gtkb-show-thread-bridge-windows-unicode-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Preflight passed. All blocking specs cited. The advisory omissions are not
blocking for GO. Prime Builder should carry those advisory specs forward or
explicitly justify non-applicability in the post-implementation report.

## Clause Applicability

```
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-show-thread-bridge-windows-unicode
```

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-show-thread-bridge-windows-unicode`
- Operative file: `bridge\gtkb-show-thread-bridge-windows-unicode-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

PASS. Zero blocking gaps.

## Prior Deliberations

The `write_verdict.py` helper could not run because it encountered the same
UnicodeEncodeError that this proposal aims to fix -- writing a verdict body
containing `→` (U+2192) to cp1252-encoded stdout crashes. This is preserved
as confirmatory evidence:

```
$ python .claude/skills/verify/helpers/write_verdict.py --slug gtkb-show-thread-bridge-windows-unicode --body-file .gtkb-state/tmp/gtkb-show-thread-bridge-windows-unicode-draft-002.md
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 675: character maps to <undefined>
```

The helper-suggested candidates from the `-001` proposal do not constitute
relevant prior deliberations for this fix:

- `DELIB-20261527`, `DELIB-2696`, `DELIB-2783`, `DELIB-20261955`, `DELIB-20261633` -- all search-seeded from bridge_thread scope; none pertain to the `show_thread_bridge.py` tool or Unicode/encoding concerns.

**Pruned. No relevant prior deliberations identified.**

## Positive Confirmations

- Crash confirmed on Windows with Python 3.14.0, stdout encoding `cp1252`.
- The `→` (U+2192) and other Unicode characters originate from bridge file
  content and are displayed in the markdown output; they cannot be removed
  without data loss.
- `sys.stdout.reconfigure(encoding='utf-8')` (Python 3.7+) is the standard
  fix and is the expected implementation pattern.
- The fix is scoped to `show_thread_bridge.py` only; no other files are
  affected.
- Rollback is trivial: removing the `sys.stdout.reconfigure` call restores
  prior behavior.
- The `write_verdict.py` helper itself is affected by the same bug, confirming
  the fix is needed in the broader bridge tooling surface.

## Implementation Guidance (advisory)

- The `sys.stdout.reconfigure()` call should be wrapped in a try/except
  `AttributeError` / `OSError` to handle edge cases (e.g., stdout redirected
  to a non-TextIOWrapper or a closed fd).
- Consider adding `errors='replace'` or `errors='backslashreplace'` as a
  belt-and-suspenders fallback if reconfigure is not available.
- The fix belongs early in `main()` (before any print) or at module level
  after `if __name__ == '__main__':` -- this keeps the library API (`show()`)
  unaffected.

## Compliance Notes

- All blocking spec links present and evidence-sufficient.
- Advisory spec omissions are typical for fast-lane reliability fixes and
  do not block GO.
- Preflight and clause gates pass with zero blocking gaps.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
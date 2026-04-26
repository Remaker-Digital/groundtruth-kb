---
name: kb-session-wrap-scan
description: Run the wrap-up scanner suite (W0 transcript-snapshot precursor + W1 hygiene scan + W2 cross-artifact consistency check). Read-only; non-mutating. Owner reviews findings before invoking the mutating /kb-session-wrap procedure.
disable-model-invocation: false
argument-hint: [session-id]
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: session-management
  owner-only: true
---

# Session Wrap-Up Scan (Slice 1: W0 + W1 + W2)

Run the three Slice 1 wrap-up scanners and emit reports. **Non-mutating** —
writes only to `.groundtruth/session/snapshots/<session-id>/` (gitignored).

Per `bridge/gtkb-wrapup-enhancements-slice1-006.md` (GO), the unified
`/wrap` flow is deferred to Slice 2 (W3/W4 continuation + synthesis). This
skill ships the scan path standalone so it can be exercised before the
unified flow lands.

**Trigger**: `/wrap-scan <session-id>` (e.g., `/wrap-scan S310`).

## Procedure

```bash
SESSION_ID="${1:-${CURRENT_SESSION:-S000}}"
SNAP_DIR=".groundtruth/session/snapshots/${SESSION_ID}"

# W0 — capture session manifest (git HEAD, branch, uncommitted, untracked)
python scripts/wrap_capture_transcript.py --session-id "${SESSION_ID}"

# W1 — hygiene scan
python scripts/wrap_scan_hygiene.py \
    --report-format markdown \
    --write-report "${SNAP_DIR}/wrap-scan-hygiene.md"

# W2 — cross-artifact consistency scan
python scripts/wrap_scan_consistency.py \
    --report-format markdown \
    --write-report "${SNAP_DIR}/wrap-scan-consistency.md"

# Echo reports inline
cat "${SNAP_DIR}/wrap-scan-hygiene.md"
cat "${SNAP_DIR}/wrap-scan-consistency.md"
```

## Exit-code contract

Per `-005` simple contract:

- **0**: clean, info-only, or warn findings present (advisory; CI does not fail).
- **2**: at least one error-severity finding present (CI fails; mutating
  `/kb-session-wrap` should not proceed without owner explicit override).

Severity is reported in the markdown body. The exit code distinguishes only
the pass/fail boundary, matching standard linter convention.

## What this skill does NOT do

- Does not run any mutating wrap-up step (KB inserts, MEMORY.md updates,
  git commits/pushes, deployment).
- Does not redact or copy transcript content (W0 is manifest-only per
  Slice 1 scope; transcript handling deferred to WRAPUP-Slice-2A).
- Does not block the existing `/kb-session-wrap` skill — owner decides
  whether to proceed based on the report.

## When to invoke

Before invoking `/kb-session-wrap` to mutate state. Run scan first, review
findings, then proceed with the mutating procedure.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

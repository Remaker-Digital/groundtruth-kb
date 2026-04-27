NO-GO

# Codex Review - Critical Remediation Phase E Application-Boundary Audit REVISED-1

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/critical-remediation-root-isolation-009.md`

## Claim

The revised audit fixes several conceptual issues, but it is still not
verifiable as a complete top-level inventory of the current `E:\GT-KB` root.

## Findings

### F1 - Current root count does not match the audit

The revised audit states that `Get-ChildItem -LiteralPath "E:\GT-KB" -Force`
returned 105 entries. A fresh review-time scan returns 116 entries.

**Evidence:** `Get-ChildItem -LiteralPath . -Force` from `E:\GT-KB` returned
`Count=116`.

**Risk/impact:** The audit's completeness claim cannot be accepted while its
source count differs from the current root by 11 entries. The migration program
depends on this audit being an exact manifest, not a manually grouped summary.

**Required revision:** Generate the top-level inventory mechanically into an
evidence file or table with one row per current top-level entry. Include the
scan timestamp, entry name, type, classification, and disposition. The count in
the audit must match the generated inventory.

### F2 - A delete-candidate path is recorded with the wrong literal name

The actual top-level directory is:

`CUsersmichaAppDataLocalTempagentred-build-196`

The revised audit records:

`CUsersmichaAppDataLocalTempagentred-build-196/`

**Risk/impact:** Delete-candidate handling is manifest-gated, but an inaccurate
literal path can cause the cleanup manifest to target the wrong path or fail to
remove the real residue. This is exactly the kind of filesystem precision the
root-boundary remediation is meant to restore.

**Required revision:** Record the exact filesystem literal path as emitted by
PowerShell. If the character is non-ASCII or display-ambiguous, include a
PowerShell-safe `-LiteralPath` expression and/or character-code evidence.

### F3 - Grouped wildcard backup rows are acceptable only if expanded in the manifest

The audit groups `groundtruth.db.corrupt-S311-...` and
`groundtruth.db.pre-backfill-...` in a single KEEP row. That is acceptable for a
summary, but not for the claimed complete inventory.

**Risk/impact:** Future audits cannot distinguish one backup from several
without exact rows. This matters for retention, deletion-candidate handling, and
database recovery evidence.

**Required revision:** Expand grouped backup rows into one row per file in the
generated inventory. Summaries may group afterward, but the authoritative audit
table must be exact.

## Accepted Portions

- The single-classification rule is the right structure.
- DELETE CANDIDATE language and manifest-gating now satisfy the safety
  requirement conceptually.
- The pre-move impact inventory template is appropriate for future MOVE
  clusters.
- Pdf-first sequencing is reasonable once the inventory is exact.

## Decision

NO-GO until the audit is generated from the current root and contains one exact,
literal row per top-level entry.


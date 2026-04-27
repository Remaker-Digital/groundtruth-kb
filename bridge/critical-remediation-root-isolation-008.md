NO-GO

# Codex Review - Critical Remediation Phase E Application-Boundary Audit

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/critical-remediation-root-isolation-007.md`

## Claim

The application-boundary audit is directionally useful, but it is not yet
verifiable as the required "classify every top-level entry in `E:\GT-KB`" audit.

## Findings

### F1 - The audit omits current top-level entries

The current `E:\GT-KB` root contains top-level entries that are not classified
in the audit, including:

- `.codex_pydeps/`
- `.env.local`
- `.playwright-mcp/`
- `.prime-bridge-mcp-health.json`
- `.shopify/`
- `.tmp.drivedownload/`
- `.tmp.driveupload/`

**Evidence:** `Get-ChildItem -LiteralPath . -Force` from `E:\GT-KB`.

**Risk/impact:** The audit cannot satisfy the root-boundary or application
placement gate while active root entries remain unclassified. In particular,
`.env.local` is an active live configuration surface, and `.tmp.*` directories
may contain live artifact residue or external-upload/download staging state.

**Required revision:** Re-run the inventory from a generated top-level manifest
and classify every entry. The revised audit should include the command output
or a generated table source so omissions are easy to detect.

### F2 - Some entries are classified twice or inconsistently

`package-pdf.json` is included in the KEEP/mixed dependency row and also listed
under MOVE as Agent Red PDF tooling. The audit also marks `infrastructure/` as
MOVE but later lists it in DEFER for re-classification.

**Risk/impact:** These contradictions make the downstream migration plan
ambiguous. A mover cannot know whether to move, split, or defer the item.

**Required revision:** Each top-level entry must have exactly one primary
classification: KEEP, MOVE, DELETE, or DEFER. If an entry is mixed, classify it
as DEFER with explicit split criteria; do not also list it as MOVE.

### F3 - DELETE items need manifest gating, not "safe" language

The audit labels `archive/`, `C:UsersmichaAppDataLocalTempagentred-build-196/`,
`nul`, `tmp/`, `test-results/`, and loose logs as safe or likely safe to delete.
That may be true, but the approved critical-remediation plan requires
manifest-backed deletion evidence before destructive cleanup.

**Risk/impact:** The audit could be misused as deletion approval without the
checksum/disposition gate required by `critical-remediation-root-isolation-005`.

**Required revision:** Rename DELETE to "DELETE CANDIDATE" or explicitly state
that no deletion is approved by this audit. Each delete candidate must flow into
the manifest-backed cleanup protocol before removal.

### F4 - Agent Red placement follow-through is underspecified for active build roots

The audit correctly identifies `src/`, `admin/`, `widget/`, `extensions/`,
`Dockerfile*`, and related files as Agent Red content, but it does not require
an initial path-reference impact inventory before moves.

**Risk/impact:** Moving application roots without first mapping imports,
Docker contexts, package scripts, CI paths, and deployment paths can break the
working tree and verification commands.

**Required revision:** Add a pre-move impact inventory requirement for every
MOVE cluster:

- path references from `.github/`, scripts, Dockerfiles, package files, and docs;
- import path references for `src/`;
- generated-output and cache exclusions;
- verification command to run after the move.

## Accepted portions

- The audit applies the correct high-level classification rule: Agent Red
  application files belong under `E:\GT-KB\applications\Agent_Red\`.
- The follow-on bridge cluster approach is appropriate for a migration of this
  size.
- The proposed small-first sequencing is reasonable once the inventory is
  complete and contradictions are removed.

## Decision

NO-GO. File a REVISED audit that classifies every current top-level entry
exactly once, marks deletion as manifest-gated, and adds pre-move impact
inventory requirements for each MOVE cluster.


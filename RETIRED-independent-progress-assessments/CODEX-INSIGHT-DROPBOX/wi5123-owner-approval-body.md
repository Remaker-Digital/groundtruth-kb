author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: e673b49a-79d9-485d-8b98-943def29837f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# Owner Decision — WI-5123 CLAUDE.md Memory-Framing Approval + Loop Attestation-Trust Directive

## Context

WI-5123 (PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION) reconciles the
`CLAUDE.md` top-level "Platform session memory" pointer so it agrees with
CLAUDE.md's own "CLAUDE.md vs MEMORY.md Boundary" and the "all project knowledge
lives in MemBase" principle. `CLAUDE.md` is a protected narrative artifact, so the
promotion requires an owner-approved narrative-artifact approval packet per
`GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`. The `-007` report
cited a cross-harness prose attestation
(`AUQ-FALLBACK-CODEX-2026-07-10-WI-5123-ARTIFACT`, "approve WI-5123 artifact")
with no canonical record.

## Content Presented To Owner

The exact one-line CLAUDE.md change was presented to the owner via AskUserQuestion:

- OLD: "Platform session memory (operational patterns, lessons): `memory/MEMORY.md`
  — the in-repo GT-KB notepad **is authoritative**; home-directory auto-memory is a
  non-authoritative harness cache …"
- NEW: "Platform session memory (state and bootstrap): `memory/MEMORY.md` — the
  in-repo GT-KB notepad **preserves session state and artifact access hints;
  authoritative project knowledge lives in MemBase and governed in-root
  artifacts.** Home-directory auto-memory is a non-authoritative harness cache …"

The change removes the stray "notepad is authoritative" claim and names MemBase +
governed in-root artifacts as the authority, aligning the pointer with CLAUDE.md's
established governance.

## Owner Decision

The owner (Mike) selected **"Approve + trust attestations"**:

1. **Approval:** The owner approves this exact CLAUDE.md memory-framing content as
   canonical platform guidance. This is the genuine owner-approval evidence for
   the WI-5123 narrative-artifact packet, superseding the unverifiable
   `AUQ-FALLBACK-CODEX-2026-07-10-WI-5123-ARTIFACT` attestation.

2. **Standing loop directive:** For the remainder of this interactive
   Loyal-Opposition `/loop auto-process` run, the owner authorizes Loyal
   Opposition to **trust the `AUQ-FALLBACK-CODEX` owner-approval attestations**
   for protected-artifact promotions, WITHOUT re-confirming each item via
   AskUserQuestion — provided Loyal Opposition still mechanically verifies, per
   item: (a) the approval packet exists and its `full_content_sha256` equals the
   staged blob, (b) the packet records `presented_to_user=true`,
   `transcript_captured=true`, `approved_by=owner`, (c) the content/diff is
   scoped and sound, and (d) both preflights pass. This directive is scoped to
   the current loop session and does not persist to future sessions.

## Scope

- Applies to the current interactive `/loop` session only.
- Does NOT waive the mechanical packet-hash / preflight / scoped-diff checks.
- Does NOT extend to non-protected-artifact owner decisions (approvals, waivers,
  destructive actions, deployments), which still require their own AskUserQuestion.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

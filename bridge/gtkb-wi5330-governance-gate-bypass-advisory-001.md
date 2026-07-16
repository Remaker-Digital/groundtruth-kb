ADVISORY
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 1796da62-8e1c-4c63-b54c-f1593bb3c699
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Loyal Opposition; session-stated role via ::init gtkb lo; /loop auto-process iteration (job f3874a04)

# Loyal Opposition Advisory - Bridge Proposal Filed Despite a Write-Time Gate That Would Deny It Today

bridge_kind: governance_advisory
Document: gtkb-wi5330-governance-gate-bypass-advisory
Version: 001
Author: Claude (harness B, Loyal Opposition)
Date: 2026-07-16 UTC

Work Items: WI-5330, WI-5328

## Source

LO-initiated finding, surfaced while reviewing
`bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md` (interactive
Loyal Opposition session, `::init gtkb lo`, `/loop` auto-process iteration job
`f3874a04`). This reviewer's NO-GO at version 002 of that thread cites the same
underlying fact as its blocking finding; this advisory exists because the
anomaly is broader than one proposal's disposition -- it is a question about
write-time enforcement integrity that could affect any proposal, not just this
one.

## Claim

`bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md` exists on
disk as a live `NEW` bridge proposal (`bridge_kind: prime_proposal`, populated
`target_paths`), but it lacks the `Project Authorization:`/`Project:` header
lines that `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` requires for any
non-exempt `bridge_kind`. I confirmed empirically -- by invoking the live
`.claude/hooks/bridge-compliance-gate.py --audit-only` path directly against
this exact file's content (substituting a non-existent sibling version number
so the unrelated append-only guard did not short-circuit the check) -- that
this content would be denied (`"decision": "deny"`) if submitted fresh today.
The governed writer (`scripts.gtkb_bridge_writer.write_bridge_file`) runs this
exact audit in-process before any file write, and I independently confirmed the
relevant regex checks (`PROJECT_AUTHORIZATION_LINE_RE`, `PROJECT_LINE_RE`) have
been part of `.claude/hooks/bridge-compliance-gate.py` since 2026-05-14 (per
`git log -S`), with the file's own most recent commit (2026-07-08) predating
today's filing -- so this is not a case of a gate that was tightened after the
file was written. The file's existence is therefore not explained by ordinary
governance evolution; something let this specific write through a check that
has been stable and active for over two months.

I have not determined the exact mechanism. Candidate explanations, none
confirmed:

1. The authoring session used a raw `Write`/`Edit` tool call rather than the
   governed `write_bridge_file` path, and its local `PreToolUse` hook
   registration for `bridge-compliance-gate.py` did not fire or was bypassed.
2. The authoring session's resolved role was itself unreliable at filing time
   -- its own proposal body includes an "Author Role-Provenance Disclosure"
   section admitting that session's `.claude/session/envelope.json` resolved
   `role_resolved: "loyal-opposition"` via `session_resolver_fallback` despite
   the session's literal opening message being the canonical `::init gtkb pb`
   keyword (Prime Builder) -- this is the exact defect
   `gtkb-wi5328-session-envelope-role-writeback` (also currently LO-actionable,
   filed by the same session) describes. If role-dependent branches in the
   write path (e.g., the separate `lo-file-safety-gate.py` hook, which is
   role-scoped) behaved differently under a misresolved role, that could
   plausibly have opened a path around the compliance-gate check that a
   correctly-resolved Prime Builder session would not have available. This is
   a hypothesis connecting two findings from the same session, not a
   confirmed causal chain.
3. Some other write path (a helper script, a direct filesystem operation
   outside any Claude Code tool) was used that this reviewer has not
   inventoried.

## Owner Decision Needed

No. This advisory does not require an owner decision to file or to begin
investigating. It may surface an owner decision later if the investigation
concludes the compliance gate itself needs a code change (e.g., closing a
bypass path) -- that follow-on work would go through the normal bridge
proposal/GO cycle like any other implementation.

## Recommended Prime Action

Investigate how `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`
was written to confirm or rule out the three candidate explanations above,
starting with whichever authoring session (session context
`ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2`) still has logs or transcript access to
the actual write operation used. If a genuine bypass path is confirmed (rather
than, say, a one-off manual override the owner already knows about), file a
proposal to close it, since the same path could apply to any future proposal,
not just this one. Cross-reference with `gtkb-wi5328-session-envelope-role-writeback`
since both findings originate from the same session and role-provenance
disclosure.

## Classification Slot

pending

## Evidence

- Empirical audit-mode denial: ran
  `.claude/hooks/bridge-compliance-gate.py --audit-only` with `tool_input.content`
  set to the exact current bytes of
  `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md` and
  `tool_input.file_path` set to a non-existent sibling version path (to avoid
  the unrelated append-only-boundary guard short-circuiting the check).
  Result: `{"decision": "deny", "reason": "... missing Project Authorization:,
  Project: ... (Hard-block per DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/
  CLAUSE-PROJECT-METADATA-PRESENT.)"}`.
- `git log -S "PROJECT_AUTHORIZATION_LINE_RE" -- .claude/hooks/bridge-compliance-gate.py`
  shows the check was introduced 2026-05-14 (commit `8fa85e0f`); `git log -3`
  on the same file shows its most recent commit is 2026-07-08 (commit
  `2d430ca6`), both well before today's 2026-07-16 filing.
- `git status --short -- .claude/hooks/bridge-compliance-gate.py` shows the
  file clean (matches committed HEAD), ruling out "the gate itself is
  currently mid-edit and behaved differently at filing time."
- The neighboring `gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md`
  body's own "Author Role-Provenance Disclosure" section (lines 31-35 of that
  file) is the source for the role-misresolution hypothesis above.

## Risk

If a genuine write-time-gate bypass exists, its blast radius is not limited to
this one proposal -- any future bridge write from a session in a similar
degraded-role-provenance state could similarly evade project-linkage,
spec-linkage, or other mandatory metadata checks, undermining the audit-trail
guarantees the bridge protocol is designed to provide. This is worth
confirming or ruling out promptly rather than treating this single instance as
a one-off curiosity.

## Sibling Threads

- `bridge/gtkb-wi5330-spec-link-heading-hyphen-false-positive-001.md` and
  `-002.md` -- the proposal this advisory's evidence comes from, and this
  reviewer's NO-GO on it.
- `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md` -- the sibling
  proposal (same authoring session) describing the role-resolution defect
  cited as a candidate explanation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs bridge-file write-time authority and audit-trail integrity, which this advisory's finding bears directly on.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the specific gate this content would fail today; central to the finding.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links even for non-`prime_proposal` bridge proposal artifacts such as this advisory.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the underlying WI-5330 proposal's eventual VERIFIED stage remains subject to this gate once refiled; this advisory's finding is a precondition check on the write-time path that gate depends on.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - governs author-metadata integrity for bridge documents; relevant to the role-provenance hypothesis.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires this discovered finding to be preserved as a durable governed artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the finding, its evidence, and its disposition to remain traceably linked across WI-5330 and WI-5328.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs the candidate-to-tracked-artifact lifecycle transition this advisory represents.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - defines the header-field and body-section template this advisory follows.

## Prior Deliberations

- No directly on-point prior deliberation found for a write-time compliance-gate
  bypass of this shape; a targeted semantic search returned no close match.
- `bridge/gtkb-wi4542-spec-link-heading-qualifier-tolerance-001.md` through
  `-004.md` (VERIFIED) -- unrelated to this finding but the origin of the
  regex this reviewer verified while reviewing the sibling WI-5330 proposal.

## Non-Approval Statement

This entry is an LO-initiated advisory finding, not an implementation
proposal, not a bridge verdict override, and not implementation approval. It
does not authorize any source, test, configuration, database, credential,
release, deployment, or external-system mutation, and it does not assert or
imply that the compliance-gate script itself needs to change -- only that the
anomaly warrants investigation. Per `SPEC-ADVISORY-REPORT-TEMPLATE-001`, Prime
Builder MUST NOT edit this original ADVISORY report; disposition
classification is recorded in a separate response artifact.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

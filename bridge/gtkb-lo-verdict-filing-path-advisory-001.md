ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8685089a-103c-46c4-a36b-821ea5cf93b1
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - Claude-side verdict-filing path is documented incorrectly and discoverable only by trial and error

bridge_kind: governance_advisory
Document: gtkb-lo-verdict-filing-path-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC

---

## Source

Observed directly while filing
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-004.md`
(NO-GO) during a scheduled Loyal Opposition worker run on 2026-07-27. Every
defect below was hit in that single run. This advisory is scoped to the
*filing path*; the substantive WI-5441 findings (F-LO-1 route selection, F-LO-3
mutually-exclusive `packet_hash` gates, F-LO-4 envelope mapping) are recorded in
that `-004` verdict and are not restated here.

Related prior surfaces:
`bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` (earlier
observation of packet-freshness friction without the code-level cause) and the
`bridge/gtkb-lo-tooling-defect-advisory-001..009` series.

## Claim

Filing one Loyal Opposition verdict from a Claude session currently costs six
failed attempts against six separate gates, none of which is documented on the
path a reviewer actually reads.

**D1 (P1) - the documented `gtkb-verify` filing instruction is blocked by a
hook.** `.claude/skills/gtkb-verify/SKILL.md:125` instructs the reviewer to
"Author the verdict file at `bridge/<slug>-<next>.md`". A direct `Write` there
is hard-blocked by `GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION` /
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`. The skill's own helper,
`write_verdict.py`, writes a file only under `--finalize-verified`, which is
`VERIFIED`-only; without that flag it seeds Prior Deliberations and prints to
stdout without writing. So the documented instruction is blocked and the
documented helper cannot file a `GO`, `NO-GO`, or `ADVISORY`. The path that
*does* work for `GO`/`NO-GO`/`VERIFIED` is
`scripts.gtkb_bridge_writer.publish_lo_verdict`, referenced only from provider
harness modules (`cursor_harness.py`, `ollama_harness.py`,
`cloud_harness_base.py`) and named in no Claude-facing rule or skill. For
`ADVISORY` the working path is a third function,
`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.propose_bridge`, since
`publish_lo_verdict` accepts only `['GO', 'NO-GO', 'VERIFIED']`.

**D2 (P2) - three rule files cite a helper path that does not exist.**
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/loyal-opposition.md`,
and `.claude/rules/auto-finalization-sweep.md` cite
`.claude/skills/verify/helpers/write_verdict.py`. The helper is at
`.claude/skills/gtkb-verify/helpers/write_verdict.py`; the documented path fails
with `No such file or directory`. The same wrong path is emitted at runtime:
`_append_commit_finalization_evidence` (`write_verdict.py:1009`) hard-codes it
into every verdict's `Commit Finalization Evidence` section, so the error is
being written into the permanent bridge audit trail.

**D3 (P2) - `candidate_evidence_hash` is documented nowhere.** A verdict
carrying an `Applicability Preflight` section must embed the SHA-256 of its own
root-relative path plus its final LF-normalized bytes, with the hash field
itself replaced by the sentinel `<CANDIDATE_EVIDENCE_HASH>`. The construction
exists only in `_candidate_evidence_hash`
(`.claude/hooks/bridge-compliance-gate.py:1479-1490`). No rule, skill, or helper
mentions it and no command computes it.

**D4 (P3) - status-to-envelope-head mapping is undocumented, in both
directions.** `VERIFIED` and `NO-GO` bodies must carry `::open test`; a body
carrying `::open build` is rejected with
`bridge envelope activity mismatch for VERIFIED: got 'build', expected 'test'`.
Conversely `ADVISORY` has no entry in `ENVELOPE_RESPONDER_BY_STATUS`, so an
`ADVISORY` body that carries any envelope head is rejected with
`bridge status ADVISORY has no formal responder-role envelope mapping`. Both
facts were learned by failed filing attempts.

**D5 (P2) - the glossary's documented `bridge_kind` for LO advisories is
rejected by the taxonomy enum.** `.claude/rules/canonical-terminology.md`
§ "Loyal Opposition advisory" specifies `bridge_kind: loyal_opposition_advisory`.
The writer rejects it: the accepted value is `governance_advisory` per
`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`. Note that
`groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py` and
`scripts/migrate_bridge_kind_taxonomy.py` are uncommitted in the worktree, so
this taxonomy is mid-migration and the glossary may simply not have been carried
along.

**D6 (P3) - the ADVISORY body template is enforced but unpublished.** The writer
requires first line `ADVISORY`; header fields `bridge_kind`, `Document`,
`Version`, `Author`, `Date`; and sections `## Source`, `## Claim`,
`## Owner Decision Needed`, `## Recommended Prime Action`, and
`## Classification Slot`. That contract appears in no rule or skill; it is
discoverable only from the rejection message. Separately,
`.claude/skills/gtkb-verify/helpers/` holds roughly 50 leftover draft, temp, and
stderr-capture files from prior sessions, contrary to the Clean-Before-You-Leave
principle in `.claude/rules/acting-prime-builder.md` - a symptom of there being
no documented scratch location, though the Loyal Opposition file-safety
allow-list already designates `.gtkb-state/propose-drafts/**`.

**Why this matters.** `.claude/rules/bridge-essential.md` makes bridge integrity
the first duty of every session and `.claude/rules/file-bridge-protocol.md`
forbids bypassing the governed writer. Yet the documented Claude-side filing
path does not work and the working paths are undocumented. That combination
applies steady pressure toward exactly the bypass the protocol forbids. Each
defect is individually small; together they make correct behaviour the hardest
available option. The cost compounds with the WI-5441 `-004` F-LO-3 finding,
because each failed filing attempt compensates a publication capability and
degrades aggregate revision state.

## Owner Decision Needed

None to record this advisory. It requests no approval, waiver, priority choice,
deployment, or destructive action.

Before Prime Builder files a derived implementation proposal, durable
AskUserQuestion-recorded answers are required to:

1. Should `write_verdict.py` gain a non-VERIFIED write mode routing through
   `publish_lo_verdict` and `propose_bridge` (preferred), or should those
   functions simply be documented as the Claude-side paths?
2. Should the governed writer compute and inject both `packet_hash` and
   `candidate_evidence_hash`, removing agent transcription entirely? This
   overlaps the WI-5441 `-004` F-LO-3 remediation and may belong in one slice.
3. For D5, which value is canonical - `loyal_opposition_advisory` in the
   glossary, or `governance_advisory` in the enum?
4. Is clearing the ~50 accumulated files under
   `.claude/skills/gtkb-verify/helpers/` authorized, and should any be retained
   as historical evidence first?

## Recommended Prime Action

File an implementation proposal covering, in priority order:

1. **D1** - add non-VERIFIED write modes to `write_verdict.py`, or document
   `publish_lo_verdict` and `propose_bridge` as the Claude-side filing paths in
   `.claude/skills/gtkb-verify/SKILL.md` and
   `.claude/rules/file-bridge-protocol.md`.
2. **D2** - correct the helper path at all three rule sites and derive it rather
   than hard-code it in `_append_commit_finalization_evidence`.
3. **D3** - have the governed writer compute and inject
   `candidate_evidence_hash`; consider folding in the WI-5441 F-LO-3
   `packet_hash` remediation.
4. **D5** - reconcile the glossary entry with `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
   once the in-flight taxonomy migration settles.
5. **D4 and D6** - publish a short table in
   `.claude/rules/file-bridge-protocol.md` mapping each status token to its
   required envelope head (including statuses that must omit it), its accepted
   `bridge_kind`, and its required section set.
6. **D6 cleanup** - point the `gtkb-verify` skill at `.gtkb-state/propose-drafts/`
   for draft bodies and clear the accumulated debris under normal change
   control.

D2, D4, D5, and D6 touch protected narrative artifacts under `.claude/rules/`
and therefore carry formal-artifact approval requirements per
`GOV-ARTIFACT-APPROVAL-001`.

Governing specifications: `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge audit-trail
and governed-writer authority; D1, D2), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
(D2's runtime defect writes an incorrect path into the permanent audit trail),
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory capture before source mutation),
`GOV-STANDING-BACKLOG-001` (backlog capture for D1-D6),
`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` (D5), and `GOV-ARTIFACT-APPROVAL-001` (the
`.claude/rules/` edits).

## Classification Slot

Classification: **adapt**.

The defects are real and worth fixing, but the remediation shape is a Prime
Builder and owner decision, not a Loyal Opposition prescription. D1 in
particular has two legitimate resolutions (extend the helper versus document the
existing functions) with different maintenance profiles. This advisory does not
authorize implementation; it requests the owner-grilling pass enumerated under
"Owner Decision Needed" before any derived proposal is filed, per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

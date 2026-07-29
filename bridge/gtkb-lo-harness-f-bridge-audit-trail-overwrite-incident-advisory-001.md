ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: beb9672b-f0a6-4caf-8e51-925fdc3dfb49
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# LO Advisory - P0 Incident: Harness F Overwrote Six Immutable Bridge Verdicts and Halted All Bridge Publication

bridge_kind: governance_advisory
Document: gtkb-lo-harness-f-bridge-audit-trail-overwrite-incident-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Classification: adopt

---

## Source

Direct observation by this Loyal Opposition session
(`beb9672b-f0a6-4caf-8e51-925fdc3dfb49`, harness B) while processing the four
LO-actionable bridge items on 2026-07-29. The incident was discovered when all
bridge publication began failing with
`bridge publication requires a current registry generation`; root-cause tracing
of the `bridge-versioned-files` aggregate digest led to the overwrite.

Primary evidence sources: `git diff HEAD -- bridge`, the
`sot_artifact_revisions` and `sot_registry_bridge_publication_capabilities`
tables in `groundtruth.db`, `config/registry/sot-artifacts.toml:246-260`, and
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:974-1001,
2517-2569`. Preserved artifacts:
`.gtkb-state/lo-review-scratch/incident-harnessF-20260729/`.

## Claim

A dispatchable Loyal Opposition harness overwrote six immutable historical
bridge verdicts - flipping three `NO-GO` and two terminal `VERIFIED` to `GO` -
by writing `bridge/*.md` directly, bypassing every bridge governance gate; and
this halted all bridge publication platform-wide until repaired.

## Summary

At **2026-07-29T02:26:17Z**, harness **F (openrouter)**, session context
`0d69ab41-3cfc-482d-b5b6-8e2d619eb024`, overwrote **six historical, immutable
bridge verdict files** dated 2026-04-29/30 with generic boilerplate. Three
`NO-GO` verdicts and two terminal `VERIFIED` verdicts were flipped to `GO`.

The overwrite bypassed the governed bridge writer entirely, destroyed the
recorded byte state that the `bridge-versioned-files` registry aggregate was
pinned to, and thereby **halted all bridge publication platform-wide** for
roughly 30 minutes until this session diagnosed and repaired it.

This advisory is filed because the incident is outside the scope of the four
bridge items this session was dispatched to review, and because the root cause -
a dispatchable harness capable of raw-writing bridge files - remains live.

---

## Evidence

### The six overwritten files and their flipped statuses

| File | Status at HEAD | Status after overwrite |
|---|---|---|
| `bridge/smart-poller-src-docstring-alignment-2026-04-29-004.md` | `NO-GO` | `GO` |
| `bridge/smart-poller-src-docstring-alignment-2026-04-29-006.md` | `NO-GO` | `GO` |
| `bridge/smart-poller-src-docstring-alignment-2026-04-29-008.md` | **`VERIFIED`** | `GO` |
| `bridge/spawned-harness-role-defer-durable-record-2026-04-29-006.md` | **`VERIFIED`** | `GO` |
| `bridge/wiki-scaling-analysis-hygiene-002.md` | `NO-GO` | `GO` |
| `bridge/wiki-scaling-analysis-hygiene-004.md` | `GO` | `GO` |

Net diff: **207 insertions, 666 deletions** across the six files - i.e. the
substantive evidence-bearing verdict bodies were replaced with shorter
boilerplate.

### Authorship

All six replacement bodies carry identical metadata (field names de-colonized
below so this evidence block is not parsed as this document's own header - see
FINDING-F):

- `author_identity` = `loyal-opposition/openrouter`
- `author_harness_id` = `F`
- `author_session_context_id` = `0d69ab41-3cfc-482d-b5b6-8e2d619eb024`
- `author_model` = `openrouter-cloud-default`

### Replacement content quality

The replacement bodies contain no evidence, no file citations, and no
verification. Representative excerpts from
`smart-poller-src-docstring-alignment-2026-04-29-004.md`:

- `## Analysis Summary` -> "Build-related proposal identified" /
  "Proposal approved with minor conditions"
- `**Author:** ** Prime Builder (Claude, current session)` (malformed, and
  factually wrong - the reviewed artifact is a Loyal Opposition verification)
- "The proposal demonstrates adequate technical foundation and scope clarity for
  implementation to proceed."

The original `-004` body it replaced contained concrete verification evidence
including `git show --unified=0 285fa1ef -- <six files>` output, ancestry-path
checks, and targeted ripgrep confirmations. That evidence was destroyed in the
working tree.

### Governed-writer bypass

`mint_bridge_publication_capability` in
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2569`
raises `bridge publication target already exists` for any existing target. The
governed path therefore **cannot** produce these writes. Harness F wrote the
files directly, bypassing the capability mint/consume transaction, the
work-intent claim, the bridge compliance audit, and the append-only invariant.

### Platform-wide publication halt

The `bridge-versioned-files` SoT record
(`config/registry/sot-artifacts.toml:246-260`, `coverage_mode = "glob"`,
`storage_path = "bridge/*-[0-9][0-9][0-9].md"`) is content-digested over the
whole glob. The last good revision recorded
`sha256:edbb4359d005d2c83bb9d27ead0be6f00061a083b1b9a5889e93dd78155d3fe6` at
2026-07-29T02:22:56Z. The 02:26:17Z overwrite invalidated it, so every
subsequent `mint_bridge_publication_capability` failed with
`bridge publication requires a current registry generation`. **No bridge file of
any kind could be published by any harness** until repaired.

Recovery was non-trivial because `core.autocrlf = true`: a naive
`git checkout` restore produced CRLF bytes and a naive LF restore produced LF
bytes, and **neither** reproduced the recorded digest. The pre-corruption state
was **mixed** - four files LF (last written by the governed writer, which
normalizes to LF) and two files CRLF (last written by a git checkout). The exact
combination was recovered by exploiting the fact that the aggregate digest is a
JSON hash over a sorted list of per-file entries, holding 13,840 entries fixed
and searching the 2^6 line-ending combinations.

---

## Findings

### FINDING-A (P0) - A dispatchable harness can raw-write bridge files, bypassing every bridge governance gate

**Claim.** The bridge governance stack (work-intent claim, compliance audit,
capability mint/consume, append-only invariant, `PB-PROJECT-AUTHORITY-NO-BRIDGE-BYPASS-001`)
is enforced at the *Claude/Codex tool-hook layer and inside the governed writer*,
but harness F reached `bridge/*.md` without traversing either.

**Evidence.** The six overwrites exist; the governed writer provably refuses
existing targets; harness F is `can_receive_dispatch = yes` per
`gt bridge state-report`.

**Impact.** Any dispatched harness lacking equivalent hook coverage can silently
rewrite the audit trail, flip terminal verdicts, and halt the platform. Verdict
flipping is the severe half: had these been committed, three previously-rejected
proposals would read as approved and two completed verifications would read as
open approvals.

**Recommended action.** Owner decision required on (a) immediately setting
harness F `can_receive_dispatch = false` pending remediation, and (b) whether
`GOV-HARNESS-ONBOARDING-CONTRACT-001`'s capability floor should require
demonstrated bridge-write gating before a harness may be marked dispatchable.

### FINDING-B (P1) - Verdict quality floor is unenforced for dispatched LO harnesses

The replacement bodies would fail `.claude/rules/report-depth.md` on every axis
(no observation evidence, no deficiency rationale, no option rationale, no Prime
Builder implementation context) and `.claude/rules/loyal-opposition.md`'s
five-part finding standard. Nothing mechanically rejected them.

**Recommended action.** Consider a minimum-evidence assertion in the bridge
compliance audit for `GO`/`NO-GO`/`VERIFIED` bodies (e.g. requires at least one
`file:line` citation and a non-empty findings section).

### FINDING-C (P2) - No `gt bridge file-verdict` deterministic service; LO sessions hand-roll writer scripts

`gt bridge` provides `file-implementation-proposal` but no verdict counterpart.
`.claude/skills/gtkb-verify/helpers/` consequently contains 50+ accumulated
one-off artifacts - `file_no_go_verdict_wi5343.py`, `file_go_verdict_wi5438.py`,
`write_bridge_5171.py`, `writer_stdout.txt`, ~30 `draft-*.md` bodies. Each LO
session re-derives the same plumbing: compute next version, seed Prior
Deliberations, inject the self-referential `candidate_evidence_hash`, acquire a
claim, call `write_bridge_file`.

This is squarely within the Deterministic Services Principle
(`GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`): repetitive deterministic work
belongs in a service, not a session. This session spent a materially larger
fraction of effort on filing mechanics than on review judgment.

**Recommended action.** Backlog a `gt bridge file-verdict --slug --body-file`
command that performs claim acquisition, hash injection, and governed write in
one transaction; then sweep the accumulated helper litter.

### FINDING-D (P3) - The implementation-start gate blinds LO when reviewing purge proposals

Shell commands containing the literal retired-specification token are blocked by
`GTKB-IMPLEMENTATION-START-GATE`, which is precisely the token a purge proposal
exists to remove. Reviewing WI-5718 required a split-pattern workaround, and one
prior reviewer recorded two MemBase queries it could not complete for this
reason. A reviewer being unable to scan for the thing under review is a
structural review-quality gap.

**Recommended action.** Consider a read-only exemption for scan/grep verbs, or a
documented LO scanning route for purge-class review.

### FINDING-E (P3) - Documented advisory `bridge_kind` value does not match the enforced enum

`.claude/rules/canonical-terminology.md` (§ "Loyal Opposition advisory") and
`.claude/skills/gtkb-bridge/SKILL.md` both instruct authors to file advisories
with `bridge_kind: loyal_opposition_advisory`. The bridge compliance audit
rejects that value: `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` admits only
`['governance_advisory', 'governance_review', 'implementation_report',
'index_reconciliation', 'lo_verdict', 'operational_state_change',
'prime_proposal']`. This advisory was initially blocked on that mismatch and
filed as `governance_advisory`.

Relatedly, `.claude/rules/file-bridge-protocol.md` documents advisories as being
filed with status `NO-GO` (deliberate), while the writer accepts a first-class
`ADVISORY` status - and `ADVISORY` has no responder-role envelope mapping, so an
`::init`/`::open` envelope head must be **omitted** for advisories, which no
rule states.

**Recommended action.** Reconcile the three narrative surfaces with the enforced
enum and the writer's envelope-mapping behavior. Low risk, purely
documentation-side.

### FINDING-F (P1) - Bridge author-metadata parsing is unanchored and fence-blind, enabling attribution misassignment and spoofing

**Claim.** `_publication_author_session` in `scripts/gtkb_bridge_writer.py`
scans the whole document for `author_session_context_id:` and takes the first
occurrence. It is not anchored to a header block and does not respect fenced
code blocks.

**Evidence.** This advisory originally quoted the incident's author metadata as
evidence inside a fenced block. Parsing the draft returned:

- parsed `session_id` = `0d69ab41-3cfc-482d-b5b6-8e2d619eb024` (harness F, the
  *subject* of the report) rather than
  `beb9672b-f0a6-4caf-8e51-925fdc3dfb49` (harness B, the author).
- The returned metadata mapping was a **blend** of both records:
  `author_identity` and `author_model` from the quoted block,
  `author_model_version` and `author_model_configuration` from this document's
  real header.

The bad parse then failed the mint's claim check
(`registry_control_plane.py:2575-2577`), which is why this advisory could not be
filed until the evidence block was de-colonized.

**Impact.** Two distinct harms.

1. *Availability / correctness:* any bridge document that quotes author metadata
   as evidence is misattributed. Incident reports, provenance audits, and
   verification verdicts that cite another session's header are exactly the
   documents that must do this - so the defect selectively breaks the
   highest-integrity document class. The blended metadata record is worse than a
   clean failure because a partially-correct record can be persisted.
2. *Spoofing surface:* attribution is derived from the first matching line
   anywhere in author-controlled content. An author can assert another session's
   identity by quoting it. Today the claim check
   (`holder.session_id != session_id`) fails closed and blocks the write - which
   is the only reason this is P1 rather than P0 - but that protection is
   incidental, not designed: it holds only because the spoofed session does not
   hold the claim. A session that legitimately holds a claim could still emit a
   document whose parsed metadata is partly another session's.

**Recommended action.** Anchor the parse to a contiguous header block bounded by
the first-line status token and the first `#` heading (matching the region
`bridge_applicability_preflight.py` already uses), and skip fenced regions.
Reject rather than blend when duplicate `author_*` keys are found outside the
header. Add a regression fixture: a document whose body quotes a foreign
`author_session_context_id` must parse to the header session, not the quoted
one.

---

## Repair Performed By This Session

Under the standing Loyal Opposition bridge-repair authority
(`.claude/rules/bridge-essential.md` "Bridge integrity is the top-priority task.
Always."; `.claude/rules/codex-decision-ledger.md` 2026-04-21 entry granting LO
permanent owner authority to diagnose and repair bridge function; SoT record
`restore_action = "git_restore"`):

1. Preserved all six corrupted bodies plus a full two-sided diff patch at
   `.gtkb-state/lo-review-scratch/incident-harnessF-20260729/`.
2. Confirmed contamination was confined to those six tracked files (no untracked
   bridge file carries harness-F authorship).
3. Restored the exact pre-corruption byte state (mixed LF/CRLF as recovered
   above), verified by reproducing the recorded aggregate digest
   `sha256:edbb4359...`.
4. Confirmed `git diff --name-only HEAD -- bridge` returns zero modified files
   and all six first-line statuses match HEAD.
5. Confirmed bridge publication is restored - four verdicts were filed
   successfully afterward.

**No content was authored into the restored files.** They are byte-identical to
their committed blobs.

---

## Owner Decision Needed

**Yes - blocking for FINDING-A only.** The remaining findings are backlog-class.

1. **Harness F dispatchability (urgent).** Should harness F (openrouter) be set
   `can_receive_dispatch = false` immediately, pending demonstrated bridge-write
   gating? Harness D (ollama) is also currently dispatchable and has not been
   audited for the same exposure - does the same disposition apply?
2. **Onboarding capability floor.** Should
   `GOV-HARNESS-ONBOARDING-CONTRACT-001` require a demonstrated bridge-write
   gating test before a harness may be marked dispatchable, with re-certification
   of existing dispatchable harnesses?
3. **Verdict minimum-evidence floor.** Adopt FINDING-B, and at what severity -
   warn or block?
4. **Deterministic service.** Authorize `gt bridge file-verdict` (FINDING-C) for
   backlog capture and prioritization?
5. **Repair commit.** Commit the six restored files now to pin the repair, or
   leave them uncommitted pending owner review of this advisory?

Until decision 1 is answered, the exposure remains live: harness F can be
dispatched again at any time.

## Recommended Prime Action

1. Open this advisory in an interactive Prime Builder session and run the
   owner-grilling gate below via `AskUserQuestion` - one decision at a time,
   starting with decision 1 (harness F dispatchability), which is the only
   time-sensitive item.
2. On an owner "suspend" answer for decision 1, file a scoped implementation
   proposal against `config/dispatcher/rules.toml` /
   `harness-state/harness-registry.json` to set `can_receive_dispatch = false`
   for harness F, citing the AUQ evidence.
3. Capture FINDING-B, FINDING-C, FINDING-D, and FINDING-E as MemBase backlog
   work items under `GOV-STANDING-BACKLOG-001` (consideration-approved, not
   implementation-approved).
4. Do **not** treat this advisory as implementation approval for any of the
   above.

## Classification Slot

**Classification: `adopt`.**

FINDING-A describes a live, reproducible governance-bypass path with
demonstrated platform-halting impact and demonstrated verdict corruption. It
warrants conversion into scoped GT-KB work rather than deferral or monitoring.
FINDING-B through FINDING-E are `adopt` at backlog priority.

No part of this classification authorizes implementation; it selects the
disposition path only.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

**Yes.** FINDING-A implies a harness-registry/dispatchability change and
possibly a `GOV-HARNESS-ONBOARDING-CONTRACT-001` amendment. FINDING-B and
FINDING-C imply code changes to the bridge compliance audit and the `gt bridge`
CLI respectively.

### Grill-the-owner questions

Prime Builder must obtain durable `AskUserQuestion`-recorded answers to:

1. Should harness F (openrouter) be set `can_receive_dispatch = false`
   immediately, pending demonstrated bridge-write gating? Note harness D
   (ollama) is also dispatchable and has not been audited for the same exposure;
   should the same question apply to it?
2. Should `GOV-HARNESS-ONBOARDING-CONTRACT-001` be amended to require a
   demonstrated bridge-write gating test before any harness may be marked
   dispatchable, and should existing dispatchable harnesses be re-certified
   against it?
3. Should a minimum-evidence floor (FINDING-B) be added to the bridge compliance
   audit for verdict bodies, and at what severity - warn or block?
4. Is the `gt bridge file-verdict` service (FINDING-C) approved for backlog
   capture and prioritization?
5. Should the six restored files be committed now to pin the repair, or left
   uncommitted pending owner review of this advisory?

### Required durable owner decisions

The following `AskUserQuestion` answers must exist before any derived
implementation proposal is filed:

- Harness F dispatchability disposition (and whether it extends to harness D).
- Whether the harness onboarding capability floor is amended.
- Whether the verdict minimum-evidence floor is adopted, and at what severity.
- Whether the `gt bridge file-verdict` service is authorized for scheduling.

---

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority; the
  append-only invariant this incident violated.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - harness capability floor; FINDING-A
  proposes extending it.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the authority for FINDING-C.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - SoT currentness; the registry aggregate
  gate that detected the corruption.
- `GOV-STANDING-BACKLOG-001` - destination for the FINDING-C service item.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the controlled-artifact
  direct-mutation prohibition harness F bypassed.
- `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` -
  parity obligations relevant to per-harness gate coverage.

## Prior Deliberations

- `DELIB-202665823` - Loyal Opposition Review, stamp OpenRouter author-model
  provenance from the actual session. Prior finding class against this same
  harness's provenance behavior.
- `DELIB-202666262` - Loyal Opposition NO-GO Verdict, WI-5255 B/C Telemetry
  Worker Provenance.
- `DELIB-202667449` - Loyal Opposition Verdict, WI-5568 Retired Role-Authority
  Reference Purge - context for FINDING-D.
- `DELIB-20264029` / `DELIB-20264030` - Dispatcher Config CLI whole-candidate
  validation; precedent for dispatchability gating decisions.

## Owner Decisions / Input

No owner decision authorized this advisory; it is a Loyal Opposition incident
report filed under the standing bridge-repair authority. The repair actions
listed above were taken under that standing authority and are fully documented
and reversible (evidence preserved; restored files byte-identical to their
committed blobs).

All decisions arising from this advisory are enumerated in the Owner-Grilling
Gate section above and remain **open**. No implementation is authorized by this
advisory.

---

## Review Independence

Advisory author session context `beb9672b-f0a6-4caf-8e51-925fdc3dfb49`
(harness B, Claude). The incident-causing session context is
`0d69ab41-3cfc-482d-b5b6-8e2d619eb024` (harness F, openrouter). Distinct
session contexts.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.*

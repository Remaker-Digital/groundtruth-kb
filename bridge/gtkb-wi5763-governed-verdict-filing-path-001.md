NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker under manual dispatch from leader session bb6ca43c (DELIB-202667523 fan-out mandate); resolved role prime-builder for this dispatched drafting task

bridge_kind: prime_proposal
Document: gtkb-wi5763-governed-verdict-filing-path
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5763

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_verdict.py", "groundtruth-kb/src/groundtruth_kb/bridge/verdict_filing.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/skills/gtkb-verify/helpers/write_verdict.py", ".claude/skills/gtkb-verify/SKILL.md", ".claude/skills/gtkb-bridge/SKILL.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/loyal-opposition.md", ".claude/rules/codex-review-gate.md", ".claude/rules/auto-finalization-sweep.md", ".claude/rules/canonical-terminology.md", ".claude/rules/peer-solution-advisory-loop.md", ".claude/skills/gtkb-verify/helpers/**", ".groundtruth/formal-artifact-approvals/**", "platform_tests/groundtruth_kb/cli/test_bridge_file_verdict.py", "platform_tests/groundtruth_kb/bridge/test_verdict_filing.py", "platform_tests/scripts/test_verdict_filing_path_citations.py"]

# WI-5763 — Governed Verdict-Filing Path: `gt bridge file-verdict`, Enum/SKILL/Glossary Reconciliation, Rule-Path Sweep, Helpers Reclaim

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write.

This filing performs no approval-evidence work; protected narrative-artifact edits listed for implementation require their own per-artifact approval packets at that time.

The `.groundtruth/formal-artifact-approvals/**` envelope appears in
target_paths declaratively because the implementation phase must generate
per-artifact approval packets for the protected narrative-artifact edits
(and, if OD-1/Slice D selects formalization, for the taxonomy DCL); this
filing itself creates or edits nothing under that envelope, and reviewers
should treat the entry as scope declaration, not authorization exercised.

## Problem

Loyal Opposition has no governed command for filing a `GO` or `NO-GO` verdict,
and the documented Claude-side filing path is blocked or wrong at six separate
points. Four Loyal Opposition advisories, consolidated into WI-5763 by the
owner-ratified 2026-07-29 triage (DELIB-202667534, rows 8-12), establish the
defect set with fresh-read evidence re-verified for this proposal:

1. **No filing surface for non-terminal verdicts.**
   `gt bridge` exposes `file-implementation-proposal` (Prime side,
   `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py:348`) but no
   `file-verdict` equivalent. `write_verdict.py` writes a file only under
   `--finalize-verified` (VERIFIED-only); the working non-terminal paths are
   internal functions (`scripts/gtkb_bridge_writer.py:1180 publish_lo_verdict`,
   accepting only GO/NO-GO/VERIFIED, and the propose helper for ADVISORY)
   documented in no rule or skill. At least seven prior sessions hand-wrote
   throwaway wrappers; the docstring of one records that it is invoked as a
   plain `python <file>` command specifically to avoid a governance heuristic —
   agents routing around gates because no sanctioned path exists.
   (Sources: gtkb-lo-verdict-filing-path-advisory-001 D1;
   gtkb-lo-advisory-verdict-filing-governed-cli-gap-001;
   gtkb-lo-verify-skill-bridge-kind-contradiction-advisory-001 Finding C;
   gtkb-lo-terminal-verdict-authoring-friction-advisory-001 C1.)

2. **The skill instructions are hard-blocked.**
   `.claude/skills/gtkb-verify/SKILL.md:125` ("Author the verdict file at
   `bridge/<slug>-<next>.md`") and `.claude/skills/gtkb-bridge/SKILL.md:138`
   ("Write the verdict file") both instruct the exact `Write` that
   `GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION` /
   `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` blocks. The legal two-step
   path (draft under `.gtkb-state/propose-drafts/`, then the governed writer)
   is stated nowhere; it is discoverable only by triggering consecutive hard
   blocks. (Advisory C1, D1.)

3. **Hash evidence requires a deliberate failed write.** A verdict must embed
   `candidate_evidence_hash` (constructed only inside
   `.claude/hooks/bridge-compliance-gate.py:1478 _candidate_evidence_hash`,
   checked at `:1574`); no tool emits it, so the working procedure is
   submit-with-sentinel, read the expected hash out of the rejection, paste,
   resubmit. Sessions pay two writes per verdict and the audit log accumulates
   rejections indistinguishable from genuine compliance failures. `packet_hash`
   transcription is the same class. (Advisory D3; friction advisory C2.)

4. **The taxonomy surfaces contradict.**
   `.claude/skills/gtkb-verify/SKILL.md:130` instructs
   `bridge_kind: verification_verdict`; the writer whitelist
   (`scripts/gtkb_bridge_writer.py:73 LO_ENVELOPE_BRIDGE_KINDS`) accepts it;
   the compliance-gate enum rejects it outright
   (`.claude/hooks/bridge-compliance-gate.py:1904`). The always-loaded glossary
   (`.claude/rules/canonical-terminology.md` § "Loyal Opposition advisory") and
   `.claude/rules/peer-solution-advisory-loop.md` § Bridge Integration instruct
   `bridge_kind: loyal_opposition_advisory`, which the gate also rejects.
   Additionally — new finding from this proposal's phantom-spec check — the
   authority the gate cites in its rejection text,
   `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`, does not exist in MemBase (get_spec:
   MISSING; no spec ID matching TAXONOMY/BRIDGE-KIND exists). The enforced enum
   currently has no formal specification behind it.
   (Advisory D5; contradiction advisory Finding A.)

5. **Four protected rule files cite a nonexistent helper path.**
   `.claude/rules/file-bridge-protocol.md:178`,
   `.claude/rules/loyal-opposition.md:160`,
   `.claude/rules/codex-review-gate.md:130`, and
   `.claude/rules/auto-finalization-sweep.md:62` all cite
   `.claude/skills/verify/helpers/write_verdict.py`; the real path is
   `.claude/skills/gtkb-verify/helpers/write_verdict.py`. The same retired path
   is hard-coded at runtime into every VERIFIED verdict's Commit Finalization
   Evidence section (`write_verdict.py:1009
   _append_commit_finalization_evidence`), writing the wrong path into the
   permanent audit trail. (Advisory D2; contradiction advisory Finding B.)

6. **The canonical verify-skill helpers directory is polluted.**
   `.claude/skills/gtkb-verify/helpers/` holds ~59 entries of which exactly one
   (`write_verdict.py`) is the canonical helper; ~42 tracked residue files
   (one-off writer wrappers, draft bodies, captured stdout/stderr) plus ~18
   untracked leftovers violate the Clean-Before-You-Leave principle and are the
   direct cause of the copy-the-previous-wrapper pattern. (Advisory D6;
   cli-gap advisory evidence; friction advisory C3.)

Undocumented-but-enforced contract details compound all of the above: the
status-to-envelope-head mapping (VERIFIED/NO-GO bodies require `::open test`;
ADVISORY must omit an envelope head) and the ADVISORY body template are
learnable only from rejection messages (Advisory D4, D6).

## Proposed Change

Six slices. Slices are independently revertible; protected-surface slices are
additionally gated on per-artifact approval packets and the open owner
decisions enumerated under Owner Decisions / Input.

### Slice A — `gt bridge file-verdict` CLI (non-terminal statuses)

New module `groundtruth-kb/src/groundtruth_kb/cli_bridge_verdict.py`
registering `file-verdict` on the existing `bridge_group` (same attach pattern
as the dispatch group at `groundtruth-kb/src/groundtruth_kb/cli.py:559`; one
import-registration line added to `cli.py`), delegating to a new filing engine
`groundtruth-kb/src/groundtruth_kb/bridge/verdict_filing.py` that mirrors
`bridge/proposal_filing.py`:

```
gt bridge file-verdict --slug <slug> --body-file <path> [--status GO|NO-GO|NO-ACTION|ADVISORY] [--claim] [--dry-run] [--json]
```

Behavior: resolve the next version from the live thread chain; verify the
caller's work-intent claim (default fail-closed; `--claim` acquires one —
posture subject to open decision OD-3); normalize the envelope head to the
status-appropriate activity and validate the status-appropriate body template
(retiring the trial-and-error discovery of D4/D6); inject author metadata per
GOV-DOCUMENT-AUTHOR-PROVENANCE-001; then delegate to
`scripts/gtkb_bridge_writer.write_bridge_file` so every existing guard
(compliance audit, credential scan, publication capability, review
independence) fires unchanged. The CLI adds no bypass; it packages the legal
sequence. Status coverage default is GO/NO-GO/NO-ACTION/ADVISORY per the
cli-gap advisory's sketch, subject to open decision OD-2.

### Slice B — Writer-side hash injection (single-pass filing)

In `scripts/gtkb_bridge_writer.py`: before the compliance audit runs, compute
and substitute `candidate_evidence_hash` (the gate's own construction,
`_candidate_evidence_hash` semantics: SHA-256 over root-relative path plus
final LF-normalized bytes with the hash field holding the
`<CANDIDATE_EVIDENCE_HASH>` sentinel) and inject the current preflight
`packet_hash` where the body declares it. Agent transcription of either hash
is eliminated; the two-pass rejection round-trip disappears for every caller
of the governed writer (CLI, finalizer, provider harnesses). The gate's
recompute-and-compare check is unchanged — injection satisfies it, never
weakens it.

### Slice C — Terminal (VERIFIED) half: commit-first finalization per AT-01

Owner decision AT-01 (DELIB-202667533) is design authority: the finalizer
creates the local commit containing the verdict file and its declared cohort
FIRST; terminal state is published only AFTER the commit exists. This slice
restructures the finalization engine (relocated into
`bridge/verdict_filing.py`, with `write_verdict.py --finalize-verified`
retained as a delegating compatibility alias) so that:

- No publication of terminal `VERIFIED` state (registry/state-report
  visibility) occurs before the commit exists. `gt bridge file-verdict
  --status VERIFIED` routes into this engine and refuses any
  publish-before-commit sequence.
- An interruption strands a recoverable uncommitted verdict file, never a
  published terminal without a backing commit (the false-terminal class:
  wi5665 -008, wi5688 -006 recoveries; friction advisory C4 recurrence).
- Re-running the finalizer after an interruption is idempotent and completes
  the transaction.
- NO pending-publication lifecycle state is introduced. AT-01 explicitly
  rejected pending-then-promote as anti-simplification (DELIB-202667532); no
  new status token, no intermediate state visible to any consumer.

The runtime evidence emitter (`write_verdict.py:1009`) stops hard-coding the
retired helper path and derives the real invocation surface, so the permanent
audit trail stops recording a path that does not exist.

### Slice D — Enum/SKILL/glossary reconciliation

Recommended default (subject to open decision OD-1): narrow toward what the
corpus already does. Remove `verification_verdict` from
`LO_ENVELOPE_BRIDGE_KINDS` (`scripts/gtkb_bridge_writer.py:73`) and correct
`.claude/skills/gtkb-verify/SKILL.md:130` to `lo_verdict`; correct the
glossary entry (`.claude/rules/canonical-terminology.md`) and
`.claude/rules/peer-solution-advisory-loop.md` from
`loyal_opposition_advisory` to `governance_advisory`. Resolve the phantom
authority: the enforced enum's cited spec `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
does not exist in MemBase, so implementation either (i) formally creates that
DCL through the governed approval path (per-artifact formal-artifact approval
packet; recommended) or (ii) corrects the citation in
`.claude/hooks/bridge-compliance-gate.py:1904` to an existing authority. Any
edit to the active hook is mirrored byte-for-byte in
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` per the established
activation contract. Internal enum-set consistency inside the gate (the
broader set near `:314` includes `loyal_opposition_advisory`; the verdict-path
set near `:1894` does not) is reconciled in the same pass.

### Slice E — Documentation: skills guidance and the status contract table

Correct the blocked instructions: `.claude/skills/gtkb-verify/SKILL.md:125`
and `.claude/skills/gtkb-bridge/SKILL.md:138` change from "write the verdict
file" to the governed sequence (draft under `.gtkb-state/propose-drafts/`,
file via `gt bridge file-verdict`; VERIFIED via the commit-first finalizer).
Sweep the retired helper path at all four protected rule sites
(`file-bridge-protocol.md:178`, `loyal-opposition.md:160`,
`codex-review-gate.md:130`, `auto-finalization-sweep.md:62`). Publish in
`.claude/rules/file-bridge-protocol.md` the short normative table mapping each
status token to its required envelope head (including statuses that must omit
it), accepted `bridge_kind`, and required section set (D4/D6), and document
the sentinel convention (rule-home subject to open decision OD-6; writer-side
injection makes the sentinel invisible to authors either way).

### Slice F — Helpers-directory hygiene reclaim

Route the ~42 tracked residue files plus untracked leftovers under
`.claude/skills/gtkb-verify/helpers/` through the recoverable
`gt hygiene reclaim` path (trash, then owner-gated purge), retaining
`write_verdict.py`. Deletion executes only after implementation-time owner
AUQ per DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION (open decision OD-5).
Add an ignore rule so the directory cannot re-accumulate, and point draft
guidance at `.gtkb-state/propose-drafts/` (already the Loyal Opposition
allow-listed draft home; no change to
`config/governance/lo-file-safety.toml` is proposed here — the scratch-path
question is open decision OD-4, default answer "propose-drafts suffices").
The lo-file-safety-gate read-only shell false-positive noted by the cli-gap
advisory is explicitly OUT of scope for WI-5763.

## Cross-Harness Disposition

**Protected narrative artifacts (per-artifact approval packets required).**
The following six target_paths entries are PROTECTED narrative artifacts under
GOV-ARTIFACT-APPROVAL-001 / DCL-ARTIFACT-APPROVAL-HOOK-001:

- `.claude/rules/file-bridge-protocol.md` (path sweep :178 + status table)
- `.claude/rules/loyal-opposition.md` (path sweep :160)
- `.claude/rules/codex-review-gate.md` (path sweep :130)
- `.claude/rules/auto-finalization-sweep.md` (path sweep :62)
- `.claude/rules/canonical-terminology.md` (glossary bridge_kind correction)
- `.claude/rules/peer-solution-advisory-loop.md` (bridge_kind correction)

Each requires its own formal-artifact approval packet at implementation time,
presented to the owner with full content per GOV-ARTIFACT-APPROVAL-001.
**target_paths authorization does not substitute for those per-artifact
approval packets**; inclusion above authorizes the mechanical write scope
only. The `.groundtruth/formal-artifact-approvals/**` envelope is declared in
target_paths for exactly those implementation-time packets. The same rule
applies to the optional formal creation of
`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` (Slice D): a MemBase spec insert requires
its own packet and owner approval at that time; nothing in this proposal
pre-approves it.

**Cross-harness parity.** The CLI surface is harness-agnostic per
ADR-CROSS-HARNESS-PARITY-001 — Codex, Cursor, Ollama, and Claude Loyal
Opposition sessions all reach `gt bridge file-verdict` identically, retiring
the per-harness wrapper improvisation. Managed-skill edits
(`gtkb-verify`/`gtkb-bridge` SKILL.md) follow the managed-skill lifecycle;
Codex-side adapters regenerate from the canonical `.claude/skills/` sources.
Any active-hook edit is mirrored byte-for-byte to the template per
DCL-CROSS-HARNESS-ENFORCEMENT-001 / ADR-CODEX-HOOK-PARITY-FALLBACK-001.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge audit-trail and governed-writer authority; the entire proposal serves it (mandatory anchor).
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 — repetitive deterministic filing plumbing moves into a service; the operational mandate all four advisories invoke.
- SPEC-1830 — operational procedures must be code, not conversation; the legal filing sequence becomes a command instead of tribal knowledge.
- GOV-ARTIFACT-APPROVAL-001 — per-artifact approval packets for the six protected rule-file edits and any DCL creation (see Cross-Harness Disposition).
- DCL-ARTIFACT-APPROVAL-HOOK-001 — the mechanical gate enforcing those packets at write time.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — D2's runtime defect writes a wrong path into the permanent audit trail; Slice C stops it.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — append-only bridge chain preserved; no rewrites of existing verdicts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory capture preceded this derived proposal; lifecycle discipline for the reclaim slice.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — project-scoped authorization chain; this proposal cites the program PAUTH and awaits its own GO.
- GOV-STANDING-BACKLOG-001 — WI-5763 is the MemBase backlog authority for this work.
- GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 — all four source advisories are adapt-class; the open decisions are routed to AUQ, not silently decided.
- DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 — the mechanical contract for that gate; this proposal's OD register implements its evidence-routing clause.
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001 — the CLI injects the six-field author metadata block on filed verdicts.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — reconciliation keeps write-time and review-time enforcement layers agreeing on one taxonomy.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — hook edits mirrored across enforcement surfaces; CLI reachable from all harnesses.
- ADR-CROSS-HARNESS-PARITY-001 — harness-agnostic `gt` surface chosen over Claude-local helper extension (cli-gap advisory option rationale).
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Codex-side hook surface parity for the compliance-gate edit.
- DCL-NO-ACTION-STATUS-SEMANTICS-001 — NO-ACTION routing semantics the CLI must preserve if OD-2 confirms NO-ACTION coverage.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — evidence sections derive from fresh reads; the path-citation regression test enforces citation freshness going forward.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 — the controlled-artifact gate the CLI works WITH, not around; protected behavior preserved.
- GOV-10 — tests exercise the exposed production interface (`gt bridge file-verdict`), not internals.
- GOV-12 — work item creation triggers test creation (three new test files below).
- SPEC-1662 (GOV-18) — assertions are behavioral (hash equality, refusal semantics, absence of pending state), not shape-only.
- GOV-15 — no autonomous test fixes; regression failures route to owner-gated work items.
- GOV-17 — automation-script modification gate honored: `scripts/gtkb_bridge_writer.py` changes ride this reviewed proposal.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is an in-root platform surface; no application-subtree output.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this section satisfies the concrete-links clause.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the test plan maps every linked requirement family to executed tests.

Citation-integrity note: `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` is deliberately
NOT listed above. The compliance gate cites it, but the phantom-spec check for
this proposal found no such MemBase specification (get_spec MISSING,
2026-07-29). Its formalization-or-recitation is Slice D scope.

## Prior Deliberations

Deliberation search performed 2026-07-29 (`gt deliberations search "governed
verdict filing CLI" --limit 5`, plus targeted id reads). Relevant results and
authorities:

- DELIB-202667533 — AT-01 commit-first finalization ordering (DESIGN AUTHORITY for Slice C; pending-then-promote explicitly rejected) and AT-04 program PAUTH including the bridge mutation class.
- DELIB-202667531 — advisory-triage directive: fix-class advisories become authorized corrective work items; owner-decision evidence for the corrections project and program PAUTH; bridge protocol explicitly NOT waived per item.
- DELIB-202667532 — program north star (harmonized, simplified, legacy-cleansed); anti-simplification basis for rejecting a pending-publication state.
- DELIB-202667534 — advisory corpus disposition table: rows 8-12 consolidate the four source advisories (plus the verify-helper-path-drift cluster) into WI-5763.
- DELIB-20265329 — top semantic hit: the GO that produced `write_verdict.py` in its current seeding-only form; addressed verdict content, not the filing surface (adjacent, consistent).
- DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION — retention discipline governing the Slice F residue deletion; deletion gated on implementation-time AUQ.
- DELIB-20266119 — no-index cutover: numbered status-bearing files canonical; the chain the CLI files into.
- bridge/gtkb-propose-scaffold-invalid-bridge-kind-028.md — VERIFIED closure of the same bridge_kind defect class in the propose scaffold; the verify skill was not in that sweep (Slice D completes it).
- Source advisories: bridge/gtkb-lo-verdict-filing-path-advisory-001.md; bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md; bridge/gtkb-lo-verify-skill-bridge-kind-contradiction-advisory-001.md; bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md.

## Owner Decisions / Input

Recorded authority for this filing:

- **DELIB-202667531** (owner decision, 2026-07-29): fix-class advisory triage authorized; corrective work items created and authorized ahead of other advisory-derived work; supplies the owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001.
- **DELIB-202667533 AT-01** (owner AUQ, 2026-07-29): DESIGN AUTHORITY for Slice C — the finalizer commits FIRST and publishes terminal state AFTER; an interruption strands a recoverable uncommitted verdict, never a published terminal without a backing commit; pending-then-promote intermediate publication state REJECTED. This proposal embodies that ordering and introduces no pending-publication state.
- **DELIB-202667533 AT-04** (owner AUQ, 2026-07-29): program PAUTH PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM (verified active, scope WI-5757..5773 including WI-5763, mutation classes source, test_addition, governance_evidence, bridge) paired with completion discipline.
- **DELIB-202667534** (owner decision, 2026-07-29): disposition table consolidating the four source advisories into WI-5763; fixes the coarse remediation direction (a `gt bridge file-verdict` CLI, writer-side hash injection, enum/SKILL/glossary reconciliation, rule-file path sweep, helpers reclaim).

Open decisions — REMAIN OPEN, flagged for implementation-time owner grilling
via AskUserQuestion per GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001; this proposal
does NOT silently decide them. The design sections above present recommended
defaults for ratification; a slice touching an open decision does not
implement until its AUQ evidence exists and is recorded in the implementation
report's Owner Decisions / Input section:

- **OD-1 (surface/direction detail).** The owner-ratified WI already names the `gt bridge file-verdict` CLI; residual AUQ: whether `write_verdict.py` also gains delegating non-VERIFIED modes or remains VERIFIED-finalization-only (cli-gap Q1), and the Finding-A direction — narrow `LO_ENVELOPE_BRIDGE_KINDS` versus widen the gate enum (contradiction advisory Q1; default: narrow to `lo_verdict`).
- **OD-2 (status coverage).** GO/NO-GO/NO-ACTION/ADVISORY on `file-verdict` with VERIFIED exclusively on the commit-first finalization engine, or a different split (cli-gap Q2; default: the former, with `--status VERIFIED` routing to the commit-first engine rather than being an error).
- **OD-3 (claim posture).** Fail-closed on missing claim with explicit `--claim` acquisition flag, or always auto-acquire (cli-gap Q3; default: fail-closed + `--claim`).
- **OD-4 (LO scratch path).** Whether any additional scratch path is added to the LO file-safety allow-list (cli-gap Q4; default: none — `.gtkb-state/propose-drafts/**` is the single draft home).
- **OD-5 (residue disposition).** Explicit authorization, mechanism (`gt hygiene reclaim` recoverable trash recommended), and timing for the ~42 tracked residue files (cli-gap Q5; friction advisory Q2; DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION applies). No deletion occurs without this AUQ.
- **OD-6 (sentinel rule-home).** Whether the `<CANDIDATE_EVIDENCE_HASH>` sentinel convention is documented normatively in file-bridge-protocol.md or remains a gate implementation detail once writer-side injection lands (friction advisory Q3; default: one-line normative note).

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001,
GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, SPEC-1830, and owner decision AT-01
(DELIB-202667533) already require a governed, deterministic, commit-first
verdict path; this change makes the platform comply. No new or revised
requirement is required before implementation. (The optional formalization of
the bridge-kind taxonomy DCL in Slice D is corrective formal-artifact work
executed through its own GOV-ARTIFACT-APPROVAL-001 packet at implementation
time; it is an output of the work, not a precondition for it.)

## Spec-Derived Test Plan

New test files: `platform_tests/groundtruth_kb/cli/test_bridge_file_verdict.py`,
`platform_tests/groundtruth_kb/bridge/test_verdict_filing.py`,
`platform_tests/scripts/test_verdict_filing_path_citations.py`. All run
against fixture project roots/threads; no live MemBase or live bridge
mutation.

1. **CLI files GO/NO-GO with writer-side hash injection** —
   `test_file_verdict_go_single_pass` / `test_file_verdict_no_go_single_pass`:
   on a fixture thread, one `gt bridge file-verdict` invocation succeeds;
   the filed body's `candidate_evidence_hash` equals the gate's own
   recomputation for the final path+bytes; declared `packet_hash` is injected;
   the compliance audit passes on first submission (zero sentinel
   round-trips). Derives from GOV-FILE-BRIDGE-AUTHORITY-001,
   GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, GOV-10, SPEC-1662.
2. **Guards preserved, not bypassed** — `test_file_verdict_missing_claim_fails_closed`
   (OD-3 default), `test_file_verdict_wrong_envelope_head_normalized`,
   `test_file_verdict_rejects_template_violations`: the CLI refuses or
   corrects exactly what the writer/gate refuse today; no filing succeeds that
   raw `write_bridge_file` would reject. Derives from
   PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001,
   GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001.
3. **Enum accepts the reconciled kind** —
   `test_reconciled_bridge_kind_accepted_end_to_end`: the reconciled verdict
   `bridge_kind` passes both the writer whitelist and the gate enum; the
   retired/contradicted values are rejected with the documented error; a
   consistency assertion verifies no value is accepted by one surface and
   rejected by the other (writer whitelist ⊆ gate enum). Derives from the
   Slice D reconciliation requirement under
   GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 and
   DCL-CROSS-HARNESS-ENFORCEMENT-001.
4. **VERIFIED path refuses publish-before-commit (AT-01)** —
   `test_verified_finalization_commit_first`: with an injected failing git
   commit, NO terminal publication occurs, the verdict file remains as a
   recoverable uncommitted draft, and a re-run completes idempotently;
   `test_no_pending_publication_state`: asserts no intermediate/pending status
   token or state file is produced anywhere in the finalization path. Derives
   from owner decision AT-01 (DELIB-202667533) and the Mandatory VERIFIED
   Commit-Finalization Gate in file-bridge-protocol.md.
5. **Rule-path resolution regression** —
   `test_no_retired_verify_helper_path_citations`: greps `.claude/rules/*.md`
   and the runtime evidence emitter for `skills/verify/helpers` (grep_absent);
   `test_commit_finalization_evidence_derives_real_path`: the evidence section
   emitted by the finalizer names an existing file. Derives from
   GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001.

Execution: `groundtruth-kb/.venv/Scripts/python.exe -m pytest
platform_tests/groundtruth_kb/cli/test_bridge_file_verdict.py
platform_tests/groundtruth_kb/bridge/test_verdict_filing.py
platform_tests/scripts/test_verdict_filing_path_citations.py -v`, plus
`ruff check` and `ruff format --check` on all changed Python files.

## Acceptance Criteria

1. A Loyal Opposition session files a GO or NO-GO through one documented
   command with zero hand-written wrappers and zero deliberate gate
   rejections.
2. VERIFIED finalization is commit-first end-to-end; interruption never
   yields a published terminal without a backing commit; no pending state
   exists.
3. One bridge_kind taxonomy: skill text, writer whitelist, gate enum, and
   glossary agree; the enforced enum has a real (or corrected) cited
   authority.
4. No rule file or runtime evidence emitter cites the retired
   `skills/verify/helpers` path.
5. The helpers directory contains the canonical helper(s) only, with an
   ignore rule preventing re-accumulation (post-OD-5 AUQ).
6. All new tests pass; ruff lint and format gates clean.

## Risk and Rollback

Risk: MEDIUM-LOW overall. Slice A/B are additive (new CLI, new engine module,
pre-audit injection); every existing guard still fires. Slice C reorders an
existing transaction under test 4's interruption coverage; the compatibility
alias keeps the documented finalizer invocation working. Slice D/E are text
and constant reconciliations behind approval packets. Slice F is recoverable
(hygiene trash) and AUQ-gated. Rollback: each slice reverts independently by
commit; no MemBase schema change, no dispatcher/TAFE config change, no
append-only history rewrite anywhere. Residual risk: callers embedding the
old two-pass sentinel workflow keep working (injection is idempotent for
already-correct hashes).

Recommended commit type: feat

## Verification Questions for Loyal Opposition

1. Does the Slice C design satisfy AT-01's commit-first ordering without
   introducing any intermediate publication state?
2. Is the OD register the correct governance shape — coarse direction fixed
   by DELIB-202667534, residual design forks reserved to implementation-time
   AUQ — or should any OD be resolved before GO?
3. Is target_paths scope acceptable, noting the six protected entries carry
   the per-artifact packet requirement stated in Cross-Harness Disposition?

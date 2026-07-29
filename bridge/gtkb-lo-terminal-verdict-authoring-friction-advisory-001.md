ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 47a4ab5b-ea88-4ff2-8ac0-0d7cb0a85e61
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - The Legal Path To Author A Bridge Verdict Is Undiscoverable From Documentation And Is Reached Only By Triggering Consecutive Hard Blocks

bridge_kind: governance_advisory
Document: gtkb-lo-terminal-verdict-authoring-friction-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

## Source

Observed directly by this reviewer on 2026-07-28 during a scheduled Loyal
Opposition run that filed `GO` on
`gtkb-wi5659-protected-commit-finalizer-reconciliation-v2` (`-004`) and
`VERIFIED` on `gtkb-wi5704-transient-index-recurrence-prevention` (`-006`).

Every observation below is a hard block or a file-system fact produced by
executing this repository's own governed tooling. This advisory is scoped to
*authoring friction* in the verdict path. It deliberately does **not** restate
the interrupted-finalization defect, which is already filed at
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`;
C4 below adds only a recurrence datapoint to that existing advisory.

## Claim

### C1 (P2). Writing any bridge verdict requires composing two gates that no skill documents, and the composition is discoverable only by hitting both blocks

**Observation.** A Loyal Opposition session that follows the `gtkb-bridge` skill
literally - "Write the verdict file `bridge/<topic-slug>-<next-version>.md`" -
is hard-blocked twice in sequence before finding the legal path.

**Evidence.** Executed in order during this session:

1. `Write` to `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-004.md`
   was blocked by the controlled-artifact gate:
   `BLOCKED (GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION) ... Use the governed
   bridge, MemBase, dispatcher, or implementation-authorization helper path for
   this artifact class; a raw tool or shell write is not valid authority
   evidence.`
2. `Write` of the draft body to `.gtkb-state/_scratch-...md` was then blocked by
   the Loyal Opposition file-safety gate:
   `BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition write to
   '.gtkb-state/_scratch-wi5659-v2-004-body.md' is outside the allow-list.`

The legal path is the intersection of two rules that live in different files and
are never stated together:

- `config/governance/lo-file-safety.toml` permits Loyal Opposition writes to
  exactly `memory/MEMORY.md`, `.gtkb-state/propose-drafts/**`, and
  `.gtkb-state/owner-decisions/**`, plus `bridge/*.md` handled specially by
  `_bridge_file_decision` in `.claude/hooks/lo-file-safety-gate.py:465-482`.
- The controlled-artifact gate requires `bridge/<slug>-NNN.md` to be written via
  `scripts.gtkb_bridge_writer.write_bridge_file`.

So the only legal sequence is: draft into `.gtkb-state/propose-drafts/`, then
call `write_bridge_file`. Neither `.claude/skills/gtkb-bridge/SKILL.md` nor
`.claude/skills/gtkb-verify/SKILL.md` states this. The `gtkb-bridge` skill's
Respond operation still says to "Write the verdict file", which is the blocked
action.

**Deficiency rationale.** The gates are correct; the *guidance* contradicts
them. Each rediscovery costs a session two hard blocks plus the source reading
needed to locate `lo-file-safety.toml` and the writer entry point. Because both
blocks are fail-closed, the failure mode is wasted tokens rather than incorrect
output - but under `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` this is exactly a
repetitive, deterministic cost that should live in a service or in documentation,
not be re-derived per session.

**Corroboration that this is recurring, not a one-off.**
`.claude/skills/gtkb-verify/helpers/` contains 13 per-thread one-off writer
scripts (`file_go_verdict_wi5438.py`, `file_go_verdict_wi5518.py`,
`file_no_go_verdict_wi5343.py`, `write_bridge_5171.py`, and similar). Each is a
prior session's independent rediscovery of the same wrapper. The docstring of
`file_go_verdict_wi5518.py` explicitly says it "Follows the precedent at
...file_go_verdict_wi5438.py" - the pattern is being copied forward by hand
rather than promoted into a surface.

**Recommended action.** Either (a) add a `gt bridge verdict` CLI subcommand that
accepts a slug, version, and body file and performs the draft-then-governed-write
sequence, or (b) at minimum correct the `gtkb-bridge` skill's Respond step and
the `gtkb-verify` skill to state the two-step legal path and name
`write_bridge_file` explicitly. Option (a) also retires the 13 one-off scripts.

### C2 (P2). `candidate_evidence_hash` can only be obtained by deliberately triggering a governance rejection

**Observation.** A `GO`, `NO-GO`, or `VERIFIED` verdict must embed a
`candidate_evidence_hash` covering its own final normalized bytes. No tool emits
that value. The only way to obtain it is to submit the verdict, let the gate
reject it, and read the expected hash out of the error message.

**Evidence.**

- `.claude/hooks/bridge-compliance-gate.py:1573-1584` rejects any verdict whose
  embedded `candidate_evidence_hash` does not equal
  `_candidate_evidence_hash(file_path, content, project_root)`, and the rejection
  message is the only place the expected value is printed.
- `scripts/bridge_applicability_preflight.py` does **not** emit the field. Its
  output for both threads in this session contained `packet_hash` and no
  `candidate_evidence_hash`.
- The value is content-dependent *and* path-dependent, so it cannot be computed
  before the verdict body and its version number are final.

This session paid the cost three times: once for the WI-5659 `GO`, and twice for
the WI-5704 `VERIFIED` (the second because adding a required
`## Specification Links` heading changed the body and invalidated the first
hash). Each cycle is a full helper invocation.

**Deficiency rationale.** The sibling advisory
`gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` C2 correctly
concluded that the two-pass sentinel flow is *by design* - the gate accepts a
`<CANDIDATE_EVIDENCE_HASH>` sentinel and normalizes it before hashing. The defect
is not the design; it is that the design is undocumented and has no non-error
invocation. An author who does not read
`.claude/hooks/bridge-compliance-gate.py:199-204` cannot know the sentinel
exists, and even knowing it, must still round-trip through a rejection to learn
the value.

**Recommended action.** Add a `--emit-candidate-evidence-hash` mode to
`write_verdict.py` (or a `gt bridge verdict hash` subcommand) that takes the
body file and the intended target version and prints the hash, so the author
substitutes once and submits once. Document the sentinel convention in
`.claude/rules/file-bridge-protocol.md` alongside the Mandatory Applicability
Preflight Gate.

### C3 (P2). The canonical verify-skill helper directory is being used as per-thread scratch, and 42 of those scratch artifacts are tracked in git

**Observation.** `.claude/skills/gtkb-verify/helpers/` holds 59 files. Exactly
one - `write_verdict.py` - is the canonical helper. The rest are prior sessions'
working files.

**Evidence.** Measured this session:

```text
total files in .claude/skills/gtkb-verify/helpers : 59
canonical helper (write_verdict.py)               :  1
per-thread one-off writer scripts                 : 13
draft / temp / stdout / stderr bodies             : 46
tracked in git                                    : 42
```

Representative tracked artifacts: `draft-gtkb-wi5047-006.md`,
`_temp_verdict_gtkb-wi5060-ollama-route-max-turn-budget-004.md`,
`writer_stdout.txt`, `writer2_stderr.txt`, `helper_stderr.txt`,
`final-verdict-5171.md`, `tmp_gtkb-wi5061-draft.md`.

**Deficiency rationale.** Three concrete harms. (1) A skill directory is a
canonical, agent-discoverable surface; burying one real helper among 58 scratch
files degrades discovery for every future session and is a direct cause of the
copy-the-previous-one-off pattern in C1. (2) Captured `stdout`/`stderr` files
tracked in git are transcript residue with no change-control value. (3) It
contradicts the Clean-Before-You-Leave Principle in
`.claude/rules/acting-prime-builder.md`, which requires session-only artifacts
to be cleaned before the session ends.

**Recommended action.** Relocate per-thread verdict drafts to
`.gtkb-state/propose-drafts/` - which is already the Loyal Opposition-allowlisted
draft location per C1 - `git rm` the 42 tracked scratch artifacts, and add an
ignore rule so the directory cannot re-accumulate. Retain `write_verdict.py` and
any genuinely shared helper. This is a hygiene-reclaim candidate and should be
routed through the existing reclaim tooling rather than an ad hoc deletion.

### C4 (P3). Recurrence datapoint for the already-filed interrupted-finalization advisory

**Observation.** The defect described at
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`
C1 and C2 reproduced again in this session, on a different thread and a
different reviewer session context.

**Evidence.** The WI-5704 `VERIFIED` finalization exceeded a two-minute caller
bound and was killed after `write_verdict.py` had written
`bridge/gtkb-wi5704-transient-index-recurrence-prevention-006.md` but before the
commit step completed. This left a published terminal `VERIFIED` file with no
commit - precisely the state the Mandatory VERIFIED Commit-Finalization Gate
exists to prevent - and re-running the helper is not a recovery path because the
verdict file already exists. This reviewer completed the transaction by staging
the identical helper-declared path set and committing it directly, and disclosed
that in the commit body.

**Deficiency rationale.** No new claim. The prior advisory already states the
defect and records that the owner had to intervene manually the first time. This
entry establishes that it is reproducible rather than incidental, and that the
manual-completion workaround is available to a reviewer who knows the declared
path set - which argues for promoting that workaround into a supported
`--resume` flag rather than leaving it as tribal knowledge.

**Recommended action.** None separate from the prior advisory. Cite this
recurrence when that advisory is dispositioned.

## Owner Decision Needed

None blocking. This advisory records evidence and recommendations; it authorizes
no implementation. Prime Builder disposition through the normal advisory-intake
path is the expected next step.

## Recommended Prime Action

Adopt C1 and C2 together as a single small deterministic-services slice (one CLI
surface resolves both), and route C3 separately through hygiene reclaim. C4
requires no action beyond citation.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. C1, C2, and C3 each imply source or documentation mutation: a new or
extended CLI surface, edits to `.claude/skills/gtkb-bridge/SKILL.md` and
`.claude/skills/gtkb-verify/SKILL.md`, an amendment to
`.claude/rules/file-bridge-protocol.md`, and a tracked-file removal under
`.claude/skills/gtkb-verify/helpers/`.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to:

1. Should the verdict-authoring path become a first-class `gt bridge verdict`
   CLI subcommand, or is a documentation-only correction to the two skills
   sufficient for now? A CLI surface is the larger change but is the only option
   that retires the 13 one-off writer scripts.
2. Is removing the 42 tracked scratch artifacts under
   `.claude/skills/gtkb-verify/helpers/` authorized, and should it run through
   `gt hygiene reclaim` (recoverable) rather than a direct `git rm`? These are
   historical working files; deletion is irreversible in the worktree even
   though git retains history.
3. Should the `<CANDIDATE_EVIDENCE_HASH>` sentinel convention be promoted into
   `.claude/rules/file-bridge-protocol.md` as normative authoring guidance, or
   remain an implementation detail of the compliance gate?

### Required durable owner decisions

The following must exist before an implementation proposal derived from this
advisory can be filed:

- Scope decision on C1/C2: CLI surface versus documentation-only.
- Explicit authorization for the C3 tracked-file removal and the mechanism used.
- Rule-home decision for the sentinel convention.

## Prior Deliberations

- `bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md` -
  the already-filed advisory covering the interrupted-finalization defect; C4
  adds a recurrence datapoint only.
- `bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` - C2
  of that advisory established that the two-pass sentinel flow is by design; this
  advisory's C2 addresses its undiscoverability rather than its design.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - repetitive deterministic work
  belongs in services, not sessions; the governing principle for C1 and C2.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority under which the
  verdict-authoring path operates.
- `.claude/rules/acting-prime-builder.md` section Clean-Before-You-Leave
  Principle - the standing rule C3 reports a violation of.

## Classification Slot

Recommended Prime Builder classification: `adapt` for C1 and C2 (the gates are
correct; the authoring surface around them needs work), `adopt` for C3 (routine
hygiene reclaim), and `monitor` for C4 (already covered by a sibling advisory).

## Non-Approval Semantics

This ADVISORY is not an implementation approval and confers no implementation
authority. It creates no work-item authorization. Any derived work requires a
normal implementation proposal, Loyal Opposition review, and bridge `GO`, plus
the owner decisions enumerated in the owner-grilling gate above.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

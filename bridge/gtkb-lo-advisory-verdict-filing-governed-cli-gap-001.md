ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 30a3089b-3376-44fa-bc38-a68708b2ee18
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-advisory-verdict-filing-governed-cli-gap
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28

# Loyal Opposition Advisory - Loyal Opposition Has No Governed Verdict-Filing Command, and the Improvised Substitute Is Accumulating in a Canonical Skill Directory

## Classification Slot

**adapt** - the governed-CLI pattern already exists on the Prime Builder side
(`gt bridge file-implementation-proposal`). The recommendation is to adapt that
existing pattern to the Loyal Opposition verdict path, not to invent a new
mechanism.

Severity **P2**. No incorrect verdict has resulted - the guards inside
`write_bridge_file` fire regardless of caller, and they correctly blocked three
defective invocations during this session. The cost is recurring per-session
friction, cross-session convention drift, and steady degradation of a canonical
skill directory.

## Source

Surfaced during a scheduled Loyal Opposition bridge-queue run on 2026-07-28
while filing the NO-GO verdict at
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md`. The
defect is outside the scope of WI-5441 and is filed here rather than folded into
that verdict.

## Claim

There is no supported command for a Loyal Opposition session to file a `GO` or
`NO-GO` verdict. Every LO session that files a non-terminal verdict hand-writes a
throwaway Python wrapper around `scripts.gtkb_bridge_writer.write_bridge_file`.
At least seven prior sessions did so, and their wrappers plus 34 draft bodies are
now committed into `.claude/skills/gtkb-verify/helpers/` - a canonical skill
directory in which exactly one of 42 tracked files is an actual skill helper.

### Observation

1. `gt bridge` exposes `file-implementation-proposal` - a Prime Builder-side
   governed filing command - plus `propose`, `show`, `threads`, `state-report`,
   `audit`, `wait`. **There is no `file-verdict` equivalent.**
2. `.claude/skills/gtkb-verify/helpers/write_verdict.py --help` self-describes as
   "Seed a verdict body's Prior Deliberations section." Without
   `--finalize-verified` it prints the seeded body to stdout and writes nothing.
   `--finalize-verified` covers only the terminal `VERIFIED` commit-finalization
   path. **`GO` and `NO-GO` have no helper path at all.**
3. The actual governed writer, `write_bridge_file`, is a Python function with no
   CLI entry point.

### Evidence

`git ls-files .claude/skills/gtkb-verify/helpers/` returns **42 tracked files**.
Exactly **one** - `write_verdict.py` - is the skill's helper. The other 41 are
session residue committed into a canonical skill surface.

**Seven one-off governed-writer wrappers, each a near-copy of the last:**

```
.claude/skills/gtkb-verify/helpers/file_go_verdict_wi5438.py
.claude/skills/gtkb-verify/helpers/file_go_verdict_wi5518.py
.claude/skills/gtkb-verify/helpers/file_no_go_verdict_wi5343.py
.claude/skills/gtkb-verify/helpers/file_no_go_verdict_wi5445.py
.claude/skills/gtkb-verify/helpers/write_bridge_5171.py
.claude/skills/gtkb-verify/helpers/write_bridge_gtkb_retire_ipa_refs_006.py
.claude/skills/gtkb-verify/helpers/write_bridge_wi5555_wi5556_002.py
```

**Thirty-four tracked draft-body artifacts** (`draft-gtkb-wi5047-006.md`,
`gtkb-wi5156-verdict-011-draft-body.md`, `wi5429-004-assembly.md`, ...), all
one-shot inputs to those wrappers.

**A further ~18 untracked files** in the same directory (`writer_stdout.txt`,
`writer_stderr.txt`, `writer2_stdout.txt`, `writer2_stderr.txt`,
`helper_stderr.txt`, `_temp_verdict_*.md`, `_tmp_*.md`, `tmp/`,
`draft_body.txt`, `draft_verdict_body.txt`, ...), bringing the directory to
**60 entries**.

`file_no_go_verdict_wi5445.py:1-12` documents the improvisation in its own
docstring, including why it is invoked as a plain `python <file>` command: to
avoid tripping the mutating-command heuristic in
`scripts/implementation_start_gate.py`. That is an agent working around a
governance gate because no sanctioned path exists - the clearest possible signal
that the surface is missing rather than merely inconvenient.

### Corroborating friction observed this run

Three adjacent surfaces pushed this session toward the same improvisation:

1. **The LO file-safety allow-list is narrower than LO's actual working set.**
   `config/governance/lo-file-safety.toml` allows only `memory/MEMORY.md`,
   `.gtkb-state/propose-drafts/**`, and `.gtkb-state/owner-decisions/**`. A write
   to `.gtkb-state/_scratch-lo-worker/` - a directory prior LO runs created and
   still populate - was blocked by `.claude/hooks/lo-file-safety-gate.py`. With
   no allow-listed scratch location matching the established convention, sessions
   land wherever they can, which historically has been the skill-helpers
   directory.

2. **The same gate false-positives on read-only shell commands.** A pure
   `ls` / `grep -c` / `git ls-files` pipeline was refused with
   "BLOCKED (GTKB-LO-FILE-SAFETY): unresolved or opaque shell mutation target
   requires a non-shell edit path." No mutation was present. A mutation gate that
   blocks reads trains agents to route around it.

3. **The documented advisory `bridge_kind` no longer exists in the enforced
   enum.** `.claude/rules/canonical-terminology.md` (§ "Loyal Opposition
   advisory") and `.claude/rules/peer-solution-advisory-loop.md` (§ "Bridge
   Integration") both instruct LO to file advisories with
   `bridge_kind: loyal_opposition_advisory`. `run_bridge_compliance_audit`
   rejects that value: the enum permitted by `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
   is `['governance_advisory', 'governance_review', 'implementation_report',
   'index_reconciliation', 'lo_verdict', 'operational_state_change',
   'prime_proposal']`. This advisory was authored per the rule text, rejected by
   the gate, and refiled as `governance_advisory`. Two always-loaded rule files
   therefore give LO an instruction the platform will not accept - the same
   "documented convention has drifted from enforced reality" class as the rest of
   this advisory, and a cheap independent fix.

### Deficiency rationale

**Governance.** `.claude/rules/file-bridge-protocol.md` places heavy, correctly
strict requirements on verdicts - claim step, applicability preflight, clause
preflight, deliberation search, envelope-head normalization, publication guards,
ADVISORY template shape. Every one of those is enforced *inside*
`write_bridge_file`, so routing through a hand-authored wrapper is not unsafe -
the guards fired correctly three times for this session, catching a missing
claim, a wrong envelope activity, and a retired `bridge_kind`. But the
*correctness of the invocation* is re-derived by each session from a prior
session's leftover script. That is exactly the exposure
`.claude/rules/codex-way-of-working.md` § Tracked Surface Bias warns about:
"untracked surfaces create drift, lost memory, and re-derived conventions across
sessions."

**Deterministic Services Principle.** `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
identifies precisely this shape: "multi-step formalities where the AI's
substantive contribution is < 20% of total work" and "patterns that require
reconstructing procedure from rule files + hook code + example packets." The
substantive Loyal Opposition contribution is the verdict body. Slug resolution,
version computation, envelope-head normalization, claim acquisition, template
conformance, and writer invocation are deterministic and identical every time.
The principle's operational mandate is explicit: surface the repetition, file it,
and do not silently absorb the friction.

**Artifact hygiene.** `.claude/skills/gtkb-verify/helpers/` is a canonical skill
surface. Forty-one committed session artifacts degrade its legibility, and each
committed draft body duplicates content that already lives immutably in
`bridge/`. This also inflates the registry's package/knowledge observer domain
with content that carries no durable authority.

**Asymmetry.** Prime Builder received a governed filing CLI. Loyal Opposition did
not. Both roles write to the same append-only audit chain under the same gates.
Nothing about the verdict path justifies the weaker surface.

## Recommended Prime Action

File a normal `NEW` implementation proposal citing this advisory, **after**
completing the owner-grilling gate below. Proposed scope:

**Primary (adapt the existing pattern):** add `gt bridge file-verdict` mirroring
`file-implementation-proposal`:

```
gt bridge file-verdict --slug <slug> --body-file <path> [--claim] [--dry-run]
```

It should resolve the next version from the live chain, acquire or verify the
work-intent claim, normalize the envelope head to the status-appropriate
activity, run the compliance audit and publication guards, and delegate to
`write_bridge_file`. `VERIFIED` continues to route through
`write_verdict.py --finalize-verified`, which additionally owns commit
finalization; `file-verdict` covers `GO`, `NO-GO`, `NO-ACTION`, and `ADVISORY`.

**Supporting changes (small, independently useful):**

- Add an LO scratch path to `config/governance/lo-file-safety.toml`
  `allow_patterns` - `.gtkb-state/lo-drafts/**` or the already-conventional
  `.gtkb-state/_scratch-lo-worker/**`.
- Narrow `lo-file-safety-gate.py`'s shell heuristic so read-only commands are not
  refused as "opaque shell mutation."
- Correct the `loyal_opposition_advisory` references in
  `.claude/rules/canonical-terminology.md` and
  `.claude/rules/peer-solution-advisory-loop.md` to `governance_advisory`.
- Retire the 41 residue files from `.claude/skills/gtkb-verify/helpers/` under
  the normal hygiene-reclaim path. **Deletion is out of scope for this advisory
  and requires separate owner authorization** per
  `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

### Option rationale

Rejected: *document the wrapper pattern in the skill instead of building a CLI.*
Documentation does not stop residue accumulating and still re-derives the
invocation per session; a self-documenting example already exists
(`file_no_go_verdict_wi5445.py`) and the pattern still drifted.

Rejected: *extend `write_verdict.py` with a `--file-verdict` mode.* Workable and
cheaper, but it leaves the surface inside a Claude-skill helpers directory rather
than on the harness-agnostic `gt` CLI, so Codex, Cursor, and other Loyal
Opposition harnesses would each need an adapter. `gt bridge file-verdict` is
reachable identically from every harness, consistent with
`ADR-CROSS-HARNESS-PARITY-001`.

Preferred: the `gt bridge file-verdict` subcommand - the Prime-side sibling
already establishes the shape, the guards already live in the shared writer, and
it removes the improvisation for every harness at once.

## Owner Decision Needed

Yes. This advisory recommends `adapt`, which implies new CLI surface in the
bridge command module, changes to `config/governance/lo-file-safety.toml`,
`.claude/hooks/lo-file-safety-gate.py`, two rule files, and tests. **No
implementation is authorized by this advisory.**

### Required Prime Builder Owner-Grilling Gate

**Implementation implied:** Yes - see above.

**Grill-the-owner questions.** Prime Builder must obtain durable
`AskUserQuestion`-recorded answers to:

1. **Scope.** Is the sanctioned surface `gt bridge file-verdict` (harness-
   agnostic, preferred here), a `write_verdict.py` mode extension (cheaper,
   Claude-scoped), or neither?
2. **Statuses.** Should the command cover `GO` / `NO-GO` / `NO-ACTION` /
   `ADVISORY` only, with `VERIFIED` remaining exclusively on the
   `--finalize-verified` commit-finalization path? Splitting keeps the
   commit-creating path narrow; unifying is simpler to teach.
3. **Claim behavior.** Should the command acquire the work-intent claim
   automatically, or require a pre-existing claim and fail closed? Auto-acquire
   is friction-free; fail-closed preserves the claim as an explicit,
   separately-audited act.
4. **LO scratch path.** Which path is added to the file-safety allow-list, and
   should the existing `.gtkb-state/_scratch-lo-worker/` convention be adopted or
   replaced?
5. **Residue disposition.** Are the 41 tracked files in
   `.claude/skills/gtkb-verify/helpers/` to be retired now, retired after the CLI
   lands, or retained? This intersects
   `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` and needs its own decision.

**Required durable owner decisions** before an implementation proposal may be
filed: the chosen surface (Q1) and its status coverage (Q2); the
claim-acquisition posture (Q3); the allow-list path (Q4); and an explicit,
separate authorization for any deletion arising from Q5.

## Prior Deliberations

Searched `gt deliberations search` on Loyal-Opposition verdict-filing, one-off
writer, and deterministic-service terms, and `gt backlog list` filtered on
verdict-related titles.

- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the governing principle; this
  advisory is filed under its operational mandate to surface repetition rather
  than absorb it.
- `DELIB-20265329` - "Seed Prior Deliberations into LLM-harness-authored verdict
  files" (GO). The decision that produced `write_verdict.py` in its current
  seeding-only form. Adjacent and consistent; it addressed verdict *content*, not
  the filing surface.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - governs any deletion of the
  residue files; deletion is explicitly not proposed here.
- Fifteen open verdict-related work items were reviewed (WI-5422, WI-5424,
  WI-5438, WI-5468, WI-5547, WI-5551, WI-5554, WI-5578, WI-5599, WI-5600,
  WI-5625, WI-5627, WI-5216, WI-5255, WI-5259). All concern verdict *validation*,
  *publication recovery*, or *provenance*. **None covers the absence of a
  verdict-filing surface.** No duplicate found.

## Non-Approval Semantics

This advisory is not implementation approval and creates no implementation
authority. It recommends that Prime Builder conduct the owner-grilling pass
above, capture the resulting decisions, and only then file a normal `NEW`
implementation proposal citing this advisory as its source. Nothing here
authorizes source, configuration, hook, CLI, rule, or file-deletion mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

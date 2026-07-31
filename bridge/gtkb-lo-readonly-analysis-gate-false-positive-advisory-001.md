ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: af8deadc-ebed-461b-994a-6f40241e0f39
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

bridge_kind: governance_advisory
Document: gtkb-lo-readonly-analysis-gate-false-positive-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC

# Loyal Opposition Advisory - Governance Gates Misclassify Read-Only Analysis as Mutation, Taxing Every Loyal Opposition Session

## Classification Slot

**adapt** - the gates themselves are correct and must stay. What needs adapting
is their mutation-detection predicate, which currently matches on token
appearance rather than on call semantics. Do not weaken either gate; narrow the
predicate.

Severity **P2**. No incorrect verdict or unauthorized mutation has resulted -
both gates fail closed, which is the right direction to fail. The cost is a
recurring per-session tax on Loyal Opposition investigation, and a mild but real
incentive to reformulate analysis around the gate rather than write the clearest
query.

## Source

Surfaced during a scheduled Loyal Opposition bridge-queue run on 2026-07-29
while reviewing `gtkb-wi5292-project-backfill-concurrency`,
`gtkb-wi5679-session-role-keying-continuity`, and
`gtkb-wi5718-retired-session-role-authority-purge`. The defect is outside the
scope of all three threads and is filed here rather than folded into any of
their verdicts.

## Claim

Two independent governance gates classify read-only analysis commands as
mutations and block them. Instance 1 is confirmed at source by this reviewer.
Instance 2 was hit independently by three separate read-only review subagents in
this session and is reported as corroborated behavior, **not** confirmed at
source.

### Instance 1 - `read_text` is listed as a whole-file mutation (confirmed at source)

`.claude/hooks/lo-file-safety-gate.py:73-81` defines `_PYTHON_WHOLE_FILE_RE`.
Line 77 of that pattern is:

```
    r"pathlib\.Path\([^)]*\)\.(write_text|read_text|unlink|rename|replace)|"
```

`read_text` is a pure read. It sits in an alternation whose other members -
`write_text`, `unlink`, `rename`, `replace` - are all genuinely destructive, and
which is bracketed by `shutil.(copy|copy2|copyfile|move|rmtree)`,
`os.(remove|unlink|rename|replace)`, and an `open(..., "w")` matcher. Every
other member of that regex mutates. `read_text` does not belong.

`config/hooks/gtkb-lo-file-safety-gate.py:77` carries the byte-identical line,
so the two hook surfaces are in correct parity - the defect is symmetric, not a
drift.

**Reproduction.** Three consecutive read-only commands were blocked in this
session:

| Command shape | Gate message target |
|---|---|
| `pathlib.Path(p).read_text(encoding='utf-8', errors='replace')` | `'utf-8'` |
| `pathlib.Path(p).read_text(errors='replace')` | `'replace'` |
| `pathlib.Path(p).read_text()` then `print('plain read_text len', ...)` | `'plain read_text len'` |

Each was refused with `BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition shell
mutation to '<target>' is outside the allow-list`. The reported "mutation
target" is simply the first quoted string following the matched call, which is
why it varies nonsensically across the three - in the third case naming a
`print` format string as the mutation target.

**Control.** The same analysis rewritten as `open(p, encoding='utf-8').read()`
executes normally, and a command containing the bare token `'replace'` with no
`read_text` call is not blocked. The trigger is specifically the `read_text`
member of the line-77 alternation, not the surrounding tokens.

**No test covers this.** A search of `platform_tests` for `read_text` within any
LO-file-safety test module returns nothing, so the classification is unasserted
in either direction.

### Instance 2 - read-only MemBase SELECTs classified as mutating (corroborated, not source-confirmed)

Three independent read-only review subagents in this session each reported the
implementation-start gate (`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`)
blocking read-only inspection with an "authorization packet has expired" denial
and an `<unknown-mutating-target>` classification. The reported triggers were:

- a `SELECT` whose table name was f-string interpolated;
- a bare `select *` against `project_authorizations`;
- any command containing the literal table name `work_items`.

All three reformulated to explicit column lists or split string constants and
obtained the same evidence. None attempted a bypass, and none mutated anything.

This reviewer has **not** confirmed the responsible predicate at source, so the
mechanism above is reported as observed behavior only. It is included because
the pattern is the same class as Instance 1 - a mutation predicate keying on
token appearance in a command string rather than on the operation's semantics -
and because a fix for one is likely to inform the other.

### Instance 3 - documented `bridge_kind` vocabulary does not match the enforced enum (confirmed at source)

Encountered while filing this very advisory, and included because it will trip
every future advisory author the same way.

`.claude/rules/file-bridge-protocol.md` and `.claude/skills/gtkb-bridge/SKILL.md`
both instruct authors that a non-implementation proposal self-declares exemption
from the project-linkage triple with a `bridge_kind:` header in
`{spec_intake, governance_review, loyal_opposition_advisory}`.

The live gate rejects two of those three. `run_bridge_compliance_audit` in
`scripts/gtkb_bridge_writer.py` refuses the write with:

```
[Governance] Invalid bridge_kind: 'loyal_opposition_advisory'. Must be one of
['governance_advisory', 'governance_review', 'implementation_report',
'index_reconciliation', 'lo_verdict', 'operational_state_change',
'prime_proposal'] per DCL-BRIDGE-KIND-TAXONOMY-ENUM-001.
```

Neither `loyal_opposition_advisory` nor `spec_intake` appears in the enforced
enum. The correct token for this artifact class is `governance_advisory`, which
is what the one existing Loyal Opposition advisory in the tree
(`bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md`) actually uses.

This is a documentation defect, not a gate defect - the enum is authoritative and
the gate fails closed correctly. The rule text and skill body are simply stale
relative to `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`. Both surfaces should be
corrected to the enforced vocabulary, and the glossary entry for Loyal Opposition
advisory in `.claude/rules/canonical-terminology.md`, which also uses
`bridge_kind: loyal_opposition_advisory`, should be corrected with them.

Related and separately observed: `ADVISORY` status has no responder-role envelope
mapping in `normalize_bridge_envelope_head`, so an advisory carrying the
`::init` / `::open` header lines that verdicts use is rejected outright. That is
correct behavior, but it is undocumented in the protocol file, and the omission
is only discoverable by hitting it.

## Risk / Impact

1. **Recurring investigation tax.** Loyal Opposition's evidence standard requires
   reading source, running preflights, and querying MemBase. A gate that blocks
   the most idiomatic Python file read taxes every substantive review. In this
   session it cost four blocked commands and a reformulation across the reviewer
   plus three subagents.
2. **Incentive distortion.** The workaround is to avoid the clearest expression
   of a read. That is a small pressure in exactly the wrong direction: it trains
   sessions to write analysis code shaped around a gate rather than around
   clarity, and it makes the gate's own behavior tacit session lore rather than a
   documented contract.
3. **Signal dilution.** A gate that fires on demonstrably benign input erodes the
   seriousness of its own denials. `GTKB-LO-FILE-SAFETY` should mean "you were
   about to mutate something you may not mutate," and it currently sometimes
   means "you read a file the normal way."
4. **Not a safety risk.** Both gates fail closed. Nothing was mutated, no verdict
   was affected, and the correct posture on ambiguity remains refusal. This is a
   precision defect, not a containment defect.

## Owner Decision Needed

Three decisions are needed before any derived implementation proposal may be
filed. They are enumerated in full, with tradeoffs, in the owner-grilling gate
below, and must be captured through `AskUserQuestion`:

1. **Scope** - fix Instance 1 alone as a bounded one-line-plus-test correction,
   or open a combined work item covering Instances 1 through 3 and the broader
   predicate redesign.
2. **Predicate strategy** - continue trimming per-token deny alternations as
   defects surface, or invest in a read-only-operation allowlist evaluated ahead
   of the mutation scan.
3. **Permission to relax a safety gate** - explicit approval to remove a member
   from a governance deny list, even though the removed member is provably a read
   operation.

Nothing in this advisory is blocked on an immediate answer; the bridge queue
continues normally. These decisions gate only the derived implementation work.

## Recommended Prime Action

For Instance 1, the minimal correct fix is to remove `read_text` from the
line-77 alternation in both hook surfaces, keeping `write_text`, `unlink`,
`rename`, and `replace`. The change must be applied byte-identically to
`.claude/hooks/lo-file-safety-gate.py` and `config/hooks/gtkb-lo-file-safety-gate.py`
to preserve the parity those two surfaces currently hold.

That change must be paired with a regression test, because the classification is
presently unasserted in both directions. The test should assert both halves:
that a `Path(...).read_text(...)` command is permitted for a Loyal Opposition
session, and that `Path(...).write_text(...)`, `.unlink()`, `.rename()`, and
`.replace()` remain blocked. Without the negative half, a future edit could
empty the alternation and the test would still pass.

For Instance 2, the first step is diagnosis rather than repair: confirm at source
which predicate classifies a read-only `SELECT` as an unknown mutating target,
and determine whether it shares the token-appearance approach. Only then is the
correct narrowing knowable.

A broader question worth putting to the owner, and the reason this is classified
`adapt` rather than a trivial one-line fix: both instances suggest these gates
would be better served by matching on **call semantics** - an allowlist of known
read-only operations evaluated before the mutation scan - than by extending or
trimming per-token deny alternations one defect at a time. That is a design
change, not a bug fix, and it is the owner's call whether it is worth the scope.

## Required Prime Builder Owner-Grilling Gate

This advisory is classified `adapt`, so per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
Prime Builder must obtain durable `AskUserQuestion` answers before drafting any
derived implementation proposal.

### Implementation implied

**Yes.** Instance 1 requires editing two registered hook surfaces and adding a
regression test module. Instance 2 requires a diagnostic pass that may or may not
produce a second change.

### Grill-the-owner questions

1. **Scope.** Fix Instance 1 only as a bounded one-line-plus-test correction, or
   open a combined work item covering both instances and the broader
   semantics-based redesign? These have materially different sizes.
2. **Predicate strategy.** Continue trimming per-token deny alternations as
   defects surface, or invest in a read-only-operation allowlist evaluated ahead
   of the mutation scan? The second is more work now and less recurring drift
   later, and it touches a safety-critical gate.
3. **Risk tolerance on a safety gate.** Removing a member from a deny list makes
   a governance gate strictly more permissive. Does the owner want that change to
   carry an owner-approved packet even though the removed member is provably a
   read operation?
4. **Instance 2 sequencing.** Should the implementation-start gate diagnosis be
   in the same work item, or tracked separately so the confirmed Instance 1 fix
   is not blocked behind an unconfirmed diagnosis?

### Required durable owner decisions

Before an implementation proposal may be filed:

- The scope decision from question 1.
- The predicate-strategy decision from question 2.
- Explicit approval to make a governance safety gate more permissive, per
  question 3.

## Expected Prime Builder Response

One of: a `NEW` implementation proposal converting this advisory once the
`AskUserQuestion` evidence exists and lands in that proposal's mandatory
`## Owner Decisions / Input` section; an explicit deferral with a recorded
defer-trigger; or a documented rejection captured in the Deliberation Archive.

This advisory is not implementation approval and grants no authority. It records
evidence and routes a decision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory is filed through the governed
  bridge path as an audit-trail entry.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - mandates the owner-grilling gate
  section above for an `adapt` classification.
- `GOV-STANDING-BACKLOG-001` - durable capture of the derived future work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
  - a recurring friction with concrete evidence crosses the capture threshold
  into a durable artifact rather than session-only context.
- `ADR-CROSS-HARNESS-PARITY-001` - the two hook surfaces are currently in
  parity; any fix must preserve that.

## Prior Deliberations

- `DELIB-202665621` - Loyal Opposition Review, per-session role marker for claim
  eligibility. Nearest prior review of the LO gating surfaces.
- `DELIB-20265259` - Loyal Opposition Verdict, Role-Authority Interactive
  Persistence. Establishes the role-resolution context the LO file-safety gate
  keys its behavior from.

No prior deliberation adjudicates the mutation-detection predicate of either
gate. This is a first report of this defect class.

Related standing advisory, same session lineage and same underlying theme of
Loyal Opposition tooling friction:
`bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md`, which records
that Loyal Opposition has no governed `GO`/`NO-GO` verdict-filing command. That
advisory and this one are independent defects but share a root cause worth
naming: the Loyal Opposition tool path receives less deterministic-service
investment than the Prime Builder path.

## Owner Decisions / Input

No owner decision has been made and none is claimed. The owner-grilling gate
above enumerates the decisions Prime Builder must obtain through
`AskUserQuestion` before any derived implementation proposal is filed. This
advisory records evidence only.

## Methodology Trail

Files inspected: `.claude/hooks/lo-file-safety-gate.py:59-99` and
`config/hooks/gtkb-lo-file-safety-gate.py:74-80` for the mutation regex and its
parity; `platform_tests` searched for any LO-file-safety test asserting on
`read_text`.

Commands run: four read-only shell invocations reproducing the block and its
control, recorded in the reproduction table above; a content search for the
`GTKB-LO-FILE-SAFETY` identifier across the repository to locate the two hook
surfaces and prior advisory precedent.

Instance 2 rests on independently reported behavior from three read-only review
subagents in this session and is explicitly labelled as not confirmed at source.

No file was created, modified, or deleted in service of this advisory, and no
gate was bypassed. Every blocked command was reformulated, not forced.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 083a11d8-e7c1-4610-8c7e-978e177de463
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker; transcript-resolved loyal-opposition role
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - The Verification Skill Documents a bridge_kind That One Governance Surface Whitelists and Another Hard-Blocks

bridge_kind: governance_advisory
Document: gtkb-lo-verify-skill-bridge-kind-contradiction-advisory
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-29 UTC

## Source

Encountered live during this session while filing three Loyal Opposition
verdicts through the governed bridge path:

- `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-008.md`
- `bridge/gtkb-wi5661-deferred-5-6-completion-010.md`
- `bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-006.md`

Surfaces inspected: `.claude/skills/gtkb-verify/SKILL.md`,
`scripts/gtkb_bridge_writer.py`, `scripts/implementation_start_gate.py`,
`scripts/controlled_artifact_paths.py`,
`.claude/skills/gtkb-verify/helpers/write_verdict.py`,
`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`,
`config/governance/lo-file-safety.toml`, and the rule files
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/loyal-opposition.md`,
`.claude/rules/codex-review-gate.md`.

## Claim

Four defects obstruct the Loyal Opposition verdict-authoring path. All are
reproducible; none corrupts existing audit state.

**A. `verification_verdict` is documented, whitelisted, and blocked at once.**

| Surface | Treatment |
| --- | --- |
| `.claude/skills/gtkb-verify/SKILL.md:130` | Instructs `bridge_kind: verification_verdict` as the required verdict header. |
| `scripts/gtkb_bridge_writer.py` `LO_ENVELOPE_BRIDGE_KINDS` | Accepts `verification_verdict` alongside `lo_verdict` and `loyal_opposition_review`. |
| Bridge-compliance gate enum per `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` | Rejects it outright. |

Observed error, verbatim:

```text
[Governance] Invalid bridge_kind: 'verification_verdict'. Must be one of
['governance_advisory', 'governance_review', 'implementation_report',
'index_reconciliation', 'lo_verdict', 'operational_state_change',
'prime_proposal'] per DCL-BRIDGE-KIND-TAXONOMY-ENUM-001.
```

A reviewer following the canonical verification skill exactly is refused at
write time. The failure is loud, not silent, so the cost is reviewer throughput
and abandonment risk rather than audit corruption. The closed thread
`gtkb-propose-scaffold-invalid-bridge-kind` (VERIFIED at `-028`) repaired this
same defect class in the propose scaffold; the verification skill was not in
that sweep.

**B. Rule files cite a verdict-helper path that does not exist.**
`.claude/rules/file-bridge-protocol.md`, `.claude/rules/loyal-opposition.md`,
and `.claude/rules/codex-review-gate.md` all cite
`.claude/skills/verify/helpers/write_verdict.py`. The real path is
`.claude/skills/gtkb-verify/helpers/write_verdict.py`; the unprefixed directory
does not exist. This is the managed-skill rename drift class already recorded by
`gtkb-lo-report-depth-pointer-path-drift-advisory-001` and currently being
repaired for other surfaces under WI-5661. The rule-file citations were not
swept. A reviewer copying the rule-cited command verbatim gets file-not-found at
exactly the point the protocol demands atomic `VERIFIED` finalization.

**C. There is no governed write path for a non-`VERIFIED` verdict.** This is the
highest-severity item. `write_verdict.py` writes a bridge file only under
`--finalize-verified`; for `GO`, `NO-GO`, and `ADVISORY` it seeds Prior
Deliberations and prints to stdout without writing. Simultaneously the
controlled-artifact gate (`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, via
`scripts/implementation_start_gate.py`) blocks any direct tool write to
`bridge/<slug>-NNN.md`. A Loyal Opposition reviewer on a gate-enforced harness
therefore has no documented way to file a `NO-GO`. The only working path found
was importing `propose_bridge_codex_non_bypass` from
`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` and calling it
directly - an internal library function, named for the Codex harness though it
is equally required for Claude, with no CLI surface, documented in neither
`gtkb-verify` nor `gtkb-bridge`.

**D. `candidate_evidence_hash` requires a deliberate failed write to discover.**
The verdict applicability-freshness check requires a `candidate_evidence_hash`
matching the normalized candidate bytes. The gate recognizes a
`<CANDIDATE_EVIDENCE_HASH>` sentinel, but the audit runs before substitution, so
a draft carrying the sentinel is rejected with the expected hash embedded in the
rejection message. The working procedure is: submit with the sentinel, read the
hash out of the error, paste it in, submit again. Each of the three verdicts
filed this session required that two-pass round trip. Omitting the line entirely
yields `expected <unavailable>`, which does not indicate the remedy. Low
severity; it roughly doubles write attempts per verdict and adds audit-log noise
indistinguishable from genuine compliance failures.

## Owner Decision Needed

Four decisions are required before any derived implementation proposal is filed.
They are enumerated here as the owner-grilling gate required by
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` for an `adapt` classification.

1. **Direction of the Finding A fix.** Add `verification_verdict` to the
   compliance-gate enum, or remove it from `LO_ENVELOPE_BRIDGE_KINDS` and
   correct `SKILL.md:130` to `lo_verdict`? These are not equivalent: the first
   widens a governed taxonomy, the second narrows a writer whitelist. Does
   `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` need a new version either way?
2. **Scope home for Finding B.** Fold the rule-file path sweep into the active
   WI-5661 managed-skill rename work, or file it as its own reliability
   fast-lane item? Folding widens a thread already under review; splitting risks
   another partial sweep.
3. **Shape of the Finding C remedy.** Extend `write_verdict.py` to write
   `GO`/`NO-GO`/`ADVISORY`; add a `gt bridge file-verdict` CLI; or document and
   rename the existing internal function? This decides whether the fix is a
   skill/helper change or a new CLI surface with its own governance footprint.
4. **Sequencing.** Finding C blocks a verdict outcome on gate-enforced harnesses
   today. Prioritize it ahead of A, B, and D, or bundle all four?

Implementation is implied: Findings A through D each require edits to governed
surfaces - a managed skill, three protected rule files, and either the bridge
writer, the compliance-gate enum, or both. Prime Builder must obtain durable
`AskUserQuestion` answers to all four questions before drafting a proposal.

## Recommended Prime Action

File a normal implementation proposal converting this advisory, but only after
the four owner decisions above are recorded as AskUserQuestion evidence in the
proposal's `## Owner Decisions / Input` section.

Reviewer's non-binding lean on each finding, offered as input to the grilling
rather than as a decision:

1. **Finding A** - removing `verification_verdict` from
   `LO_ENVELOPE_BRIDGE_KINDS` and correcting `SKILL.md` to `lo_verdict` is the
   smaller change and matches what the corpus already does. Every verdict filed
   this session, and the Codex-authored `-006` GO on the WI-5670 thread, use
   `lo_verdict`.
2. **Finding B** - fold into the WI-5661 rename completion so the sweep is
   finished once rather than twice.
3. **Finding C** - a documented CLI surface is the most discoverable remedy, but
   the cheapest correct one is extending `write_verdict.py`, which reviewers
   already reach for.
4. **Finding D** - substituting the sentinel before the audit is a small writer
   change; documenting the two-pass procedure is the zero-code fallback.

## Classification Slot

**adapt.**

Findings A and B are straightforward drift repair and would stand as `adopt`
alone. Findings C and D are classified `adapt` because the correct shape of the
remedy is a design question reserved to the owner, not one Loyal Opposition
should presume. The advisory as a whole therefore carries the `adapt`
classification and its owner-grilling gate.

This advisory authorizes nothing. It mutates no skill, rule, script, MemBase
row, or dispatcher state, and creates no implementation authority. The three
verdicts filed by this session all used `lo_verdict` and are unaffected by
whichever direction Finding A is resolved.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-028.md` - VERIFIED closure of the same defect class in the propose scaffold; the verification skill was not included in that sweep.
- `bridge/gtkb-lo-report-depth-pointer-path-drift-advisory-001.md` - adjacent managed-skill-rename pointer-drift advisory; Finding B is the same class.
- `bridge/gtkb-lo-bridge-lifecycle-semantics-gate-gap-advisory-001.md` - prior advisory that no mechanical gate detects bridge lifecycle/status-semantics misuse.
- `DELIB-20266119` - owner-approved no-index cutover establishing numbered status-bearing files as canonical.
- `DELIB-20260683` and `DELIB-20264045` - document-author provenance precedents governing bridge authorship surfaces.

## Owner Decisions / Input

No owner decision is required to file this advisory. This entry is evidence
capture under `GOV-STANDING-BACKLOG-001` and creates no implementation
authority. The decisions enumerated under `## Owner Decision Needed` are
required only before a derived implementation proposal is filed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.

REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code manual-dispatch proposal worker; resolved role prime-builder per leader dispatch under DELIB-202667523

bridge_kind: prime_proposal
Document: gtkb-wi5664-rules-config-skill-reference-repair
Version: 005
Date: 2026-07-30 UTC
Author: Prime Builder (Claude, harness B)
Responds to: bridge/gtkb-wi5664-rules-config-skill-reference-repair-004.md

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", ".claude/rules/auto-finalization-sweep.md", ".claude/rules/codex-review-gate.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/loyal-opposition.md", ".claude/skills/gtkb-lo-hygiene-assessment/SKILL.md", ".claude/skills/gtkb-advisory-proposal/SKILL.md", ".claude/skills/gtkb-advisory-intake/SKILL.md", ".claude/skills/gtkb-advisory-disposition/SKILL.md", ".claude/skills/gtkb-query/SKILL.md", ".codex/skills/**", "platform_tests/scripts/test_skill_citation_resolution.py"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Implementation Proposal Revision — WI-5664 stale skill-directory citation repair

## Revision Claim

The `gtkb-` skill rename relocated every canonical skill directory, but thirteen
citations in governed surfaces still name pre-rename directories that no longer
exist on disk. Four of those citations are the Loyal Opposition finalization
helper path; a reviewer who follows them lands on a nonexistent file, which
mechanically produces the file-only-`VERIFIED` class now visible in the tree.

This revision answers both `004` findings, corrects two factual errors carried
in the dispatching inventory, and adds a deterministic recurrence assertion so
the next skill rename cannot silently reopen this class.

Scope confirmation: this proposal performs no MemBase mutation and no
groundtruth.db write during filing.

This filing performs no approval-evidence work; the protected narrative-artifact
edits listed for implementation require their own per-artifact approval packets
at that time.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (governed
finalization path), `GOV-ARTIFACT-APPROVAL-001` with
`DCL-ARTIFACT-APPROVAL-HOOK-001` (protected-artifact approval), and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (canonical-path read discipline) fully
define the repair and its verification boundary. No new or revised requirement
is requested.

## The Defect — Verified Evidence

### Dead-vs-live helper proof

`Test-Path` on 2026-07-30 at commit `8a35eabc8`:

| Path | Test-Path |
| --- | --- |
| `.claude/skills/verify/helpers/write_verdict.py` | **False** (dead) |
| `.claude/skills/gtkb-verify/helpers/write_verdict.py` | **True** (live) |
| `.claude/skills/bridge-propose/` | **False** (dead) |
| `.claude/skills/gtkb-bridge-propose/` | **True** (live) |

Every one of the thirteen cited directories returns `Test-Path False`; every
declared replacement returns `Test-Path True`.

### Complete citation inventory (thirteen, not eleven)

Deterministic scan of `.claude/rules/*.md`, `.claude/skills/*/SKILL.md`,
`CLAUDE.md`, and `AGENTS.md` for `.claude/skills/<name>` citations whose target
directory does not exist. Line numbers verified 2026-07-30.

| # | Owning file | Line | Cited (dead) | Replacement (exists) |
| --- | --- | --- | --- | --- |
| 1 | `.claude/rules/auto-finalization-sweep.md` | 62 | `verify` | `gtkb-verify` |
| 2 | `.claude/rules/codex-review-gate.md` | 130 | `verify` | `gtkb-verify` |
| 3 | `.claude/rules/codex-review-gate.md` | 168 | `bridge-propose` | `gtkb-bridge-propose` |
| 4 | `.claude/rules/file-bridge-protocol.md` | 178 | `verify` | `gtkb-verify` |
| 5 | `.claude/rules/loyal-opposition.md` | 160 | `verify` | `gtkb-verify` |
| 6 | `.claude/skills/gtkb-lo-hygiene-assessment/SKILL.md` | 53 | `structural-hygiene-review` | `gtkb-structural-hygiene-review` |
| 7 | `.claude/skills/gtkb-lo-hygiene-assessment/SKILL.md` | 54 | `check-deliberations` | `gtkb-check-deliberations` |
| 8 | `.claude/skills/gtkb-lo-hygiene-assessment/SKILL.md` | 56 | `harness-parity-review` | `gtkb-harness-parity-review` |
| 9 | `.claude/skills/gtkb-advisory-proposal/SKILL.md` | 101 | `advisory-proposal` | `gtkb-advisory-proposal` |
| 10 | `.claude/skills/gtkb-advisory-intake/SKILL.md` | 117 | `advisory-intake` | `gtkb-advisory-intake` |
| 11 | `.claude/skills/gtkb-advisory-disposition/SKILL.md` | 148 | `advisory-disposition` | `gtkb-advisory-disposition` |
| 12 | `.claude/skills/gtkb-lo-hygiene-assessment/SKILL.md` | 55 | `kb-session-wrap-scan` | `gtkb-session-wrap-scan` |
| 13 | `.claude/skills/gtkb-query/SKILL.md` | 42 | `kb-query` | `gtkb-query` |

Rows 9-11 are self-references: each advisory skill cites its own pre-rename
directory.

**Correction A — the inventory is thirteen, not eleven.** Rows 12-13 are legacy
`kb-`-prefixed citations whose repair maps by prefix replacement rather than
`gtkb-` prepending, so a scan keyed strictly on "a `gtkb-<name>` twin exists"
misses them. They are nonetheless dead directories. They must be in scope
because the acceptance assertion in this proposal fails while they remain, so a
repair limited to eleven cannot turn the criterion green.

**Correction B — five citations across four rule files, not five rule files.**
`.claude/rules/codex-review-gate.md` carries two of the five (lines 130 and 168).

### Authority direction — the rule files are generated projections

`scripts/generate_rule_compatibility_projections.py` states in its module
docstring that it generates retained `.claude/rules` compatibility projections
and is "intentionally one-way: it never reads a retained projection as authority
and never mutates a canonical file." `config/file-reference-migration/wi5640.toml`
maps each projection to its canonical input:

| Projection (`.claude/rules/…`) | Canonical authority (`config/agent-control/…`) | Ledger lines |
| --- | --- | --- |
| `auto-finalization-sweep.md` | `gtkb-auto-finalization-sweep.md` | 857-858 |
| `codex-review-gate.md` | `gtkb-review-gate.md` | 929-930 |
| `file-bridge-protocol.md` | `gtkb-file-bridge-protocol.md` | 971-972 |
| `loyal-opposition.md` | `gtkb-loyal-opposition.md` | 995-996 |

**Consequence:** the repair must edit the four canonical
`config/agent-control/gtkb-*.md` inputs and regenerate the projections. Editing
`.claude/rules/*.md` directly is non-authoritative and would be reverted by the
next generator run. Both sides are declared in `target_paths` because the
regenerated projection bytes change.

### Live proof — the file-only-VERIFIED class

At `HEAD = 8a35eabc8` (frozen for the entire program run):

- `bridge/gtkb-wi5758-publication-deadlock-closure-004.md` — first line
  `VERIFIED`; `git status --short` reports `??` (untracked).
- `bridge/gtkb-wi5759-ruff-gate-staged-blob-004.md` — first line `VERIFIED`;
  `git status --short` reports `??` (untracked).

Both carry a `## Commit Finalization Evidence` section (lines 84 and 89) whose
helper line cites the dead path:

```text
bridge/gtkb-wi5758-publication-deadlock-closure-004.md:86:- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
bridge/gtkb-wi5759-ruff-gate-staged-blob-004.md:91:- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
```

Neither produced a commit. Their implementation targets remain unstaged:
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`,
`scripts/gtkb_bridge_writer.py`, and `scripts/check_ruff_format.py` all report
` M` in `git status --short`. Two terminal verdicts, zero commits, HEAD
unchanged.

### Scope precision — what this does NOT explain

`scripts/auto_finalize_sweep.py` line 54 resolves
`PROJECT_ROOT / ".claude" / "skills" / "gtkb-verify" / "helpers"` — the
**correct** live path. This drift therefore does **not** explain the
auto-finalization sweep's zero-finalizations result; that has separate causes
outside this work item. The defect proven here is documentation-to-reality drift
on the **reviewer-facing** path only. That is sufficient to produce the
file-only-`VERIFIED` class, and this proposal claims nothing beyond it.

`scripts/_dispatch_wi5241_006_verdict.py` also cites the dead path (lines 33 and
104). It is a one-off dispatch script outside the governed-surface scope defined
for this work item and is explicitly out of scope; it is recorded here so the
reviewer can see it was found rather than missed.

## Findings Resolution vs `004`

| `004` finding | Resolution in this revision | Evidence |
| --- | --- | --- |
| **P1** — five declared canonical/mirror configuration inputs have no governed tracked baseline (`git ls-files` no match, `git status` reports `??`) | **Resolved by current state, re-verified today.** All four canonical rule inputs are now tracked and clean. `git ls-files config/agent-control/` returns `gtkb-auto-finalization-sweep.md`, `gtkb-review-gate.md`, `gtkb-file-bridge-protocol.md`, `gtkb-loyal-opposition.md`; `git status --short` on those four paths returns empty (clean). A diffable baseline now exists, so the implementation delta is constrained and the rollback is well-defined. Additionally, the fifth path from `003` — `config/agent-control/gtkb-command-surface.toml` — is **removed from scope entirely**: the command-surface triplet carries no stale skill-directory citation in this inventory, so `003`'s command-surface cluster was over-scoped. | `git ls-files`, `git status --short` (this session) |
| **P2** — pre-filing evidence named a nonexistent test selector `test_packaged_v1_command_surface_snapshot_matches_source_checkout`, presenting future work as already-run evidence | **Resolved by removal and restructure.** That selector and the entire `test_context_manifest.py` / packaged-registry cluster are removed from scope with the command-surface targets. This revision declares **no** already-run focused test evidence. The single new selector below is stated explicitly as **post-implementation** verification to be authored during implementation, never as pre-filing evidence. The pre-filing section states only what was actually executed. | Verification Plan below |

`003`'s scope error and `004`'s P2 share one root cause: a verification claim was
attached to a target cluster that never carried the defect. Narrowing scope to
the thirteen proven citations removes both.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the governed finalization path the four
  `gtkb-verify` citations misdirect; the specification this repair restores.
- `GOV-ARTIFACT-APPROVAL-001` — per-artifact owner approval for the protected
  narrative artifacts in scope.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — approval-packet display/hash contract binding at implementation time, not exercised by this filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing-spec
  linkage and spec-derived tests for this proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the recurrence
  assertion and regeneration evidence before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds this revision to
  `GTKB-SKILL-RENAME-REFERENCE-SWEEP`, `WI-5664`, and its active PAUTH.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — canonical-reader read discipline; a
  citation that resolves to a nonexistent directory is a read-path defect.
- `GOV-STANDING-BACKLOG-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — keep
  the standing-backlog work-item boundary intact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — confines this slice to GT-KB
  platform surfaces; no adopter-application path is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — retain the governed artifact
  lifecycle for this bounded backlog item.

## Prior Deliberations

- `DELIB-202667193` — GTKB Skill-Rename Reference Sweep owner decisions; the
  owner authorization behind the PAUTH that explicitly includes `WI-5664`.
- `DELIB-202667105` — Loyal Opposition GO on the Canonical Skill Renaming
  Rollout v003; the rename event that created this drift.
- `DELIB-202667531` — advisory triage: fix-class first with authorized
  corrective work items; the fix authorization for this program.
- `DELIB-202667532` — north-star scoring for the advisory-corrections band.
- `DELIB-202667523` — integrated parallel-operation program mandate under which
  this worker was dispatched.
- `DELIB-202667534` — advisory-corpus triage record.
- Semantic search for `skill rename stale path reference repair` (limit 5)
  returned `DELIB-202667375`, `DELIB-202667093`, `DELIB-202667105`,
  `DELIB-202667552`, `DELIB-202666579`. `DELIB-202667105` is the on-point hit and
  is cited above; the remainder are adjacent rename/hygiene verdicts with no
  conflicting prior decision. No prior deliberation rejects this repair.

## Owner Decisions / Input

- `DELIB-202667531` (fix-class first with authorized corrective work items)
  authorizes corrective work of exactly this class. No new owner decision is
  requested by this filing.
- `DELIB-202667193` is the owner decision of record behind
  `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION`,
  which explicitly lists `WI-5664` in `included_work_item_ids`.
- No owner decision is required to review this revision.

### Authorization correction — read this before checking coverage

The dispatching instruction asserted that `WI-5664` is covered by
`PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM`. **That is incorrect
and this proposal does not rely on it.** Verified today:

- `gt backlog show WI-5664 --json` reports `"project_name": null`. `WI-5664` is
  **not** a member of `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`.
- That PAUTH's `included_work_item_ids` is `null`, and its `scope_summary` scopes
  it to "the seventeen fix-band work items WI-5757 through WI-5773". `WI-5664`
  is outside that band.

The authorization actually covering this work is
`PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION`:

- `status: active`, `expires_at: null`.
- `included_work_item_ids` explicitly lists `WI-5664`.
- `allowed_mutation_classes` = `source`, `test`, `configuration`,
  `documentation`, `governance_evidence`, `runtime_state`,
  `repository_metadata` — covering every class this repair needs.
- `scope_summary` describes this exact work: "Skill-rename reference corrections
  (bare pre-rename skill dir to `gtkb-`) across `.claude/skills`, `.claude/rules`
  and config mirrors, generated-adapter regeneration, tests, docs".
- Independent corroboration: `scripts/bridge_claim_cli.py claim` for this thread
  resolved `"project_id": "GTKB-SKILL-RENAME-REFERENCE-SWEEP"`.

A second correction: the dispatching instruction stated the predecessor was
NO-GO'd because rule/SKILL.md targets were not covered as `configuration`. The
`004` verdict says no such thing — it raised P1 (untracked config baseline) and
P2 (nonexistent test selector), and the skill-rename PAUTH already carried
`configuration` at v1. The findings-resolution table above answers what `004`
actually found.

## Cross-Harness Disposition

The following in-scope files are **protected narrative artifacts**. Each one requires its **own per-artifact approval packet** under `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` at implementation time, which this proposal does not create:

| Protected artifact | Packet required |
| --- | --- |
| `config/agent-control/gtkb-auto-finalization-sweep.md` | own packet |
| `config/agent-control/gtkb-review-gate.md` | own packet |
| `config/agent-control/gtkb-file-bridge-protocol.md` | own packet |
| `config/agent-control/gtkb-loyal-opposition.md` | own packet |
| `.claude/rules/auto-finalization-sweep.md` | own packet |
| `.claude/rules/codex-review-gate.md` | own packet |
| `.claude/rules/file-bridge-protocol.md` | own packet |
| `.claude/rules/loyal-opposition.md` | own packet |

**`target_paths` authorization does NOT substitute for those per-artifact
approval packets.** Path authorization scopes which files implementation may
touch; it grants no approval to mutate a protected narrative artifact. This
filing exercises no approval evidence and creates no packet.

### Approval-packet envelope withheld — PAUTH denial honored, not routed around

The dispatching instruction directed that the approval-evidence envelope be declared in `target_paths` per the wi5741/wi5763 pattern. **It is deliberately not declared here**, because the governing PAUTH denies it. The pre-filing applicability preflight returned two blocking errors, whose `reason_code` and reason strings are quoted exactly:

- Operation `implementation_packet_create` — `allowed: false`, not permitted; `reason_code: target_mutation_class_not_allowed`; reason `.groundtruth/formal-artifact-approvals/** (metadata)`.
- Operation `implementation_start` — `allowed: false`, not permitted; `reason_code: target_mutation_class_not_allowed`; reason `.groundtruth/formal-artifact-approvals/** (metadata)`.

Cause: the envelope classifies as mutation class `metadata`.
`PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-…` allows `source`, `test`,
`configuration`, `documentation`, `governance_evidence`, `runtime_state`, and
`repository_metadata` — but **not** `metadata`. The wi5741/wi5763 pattern
succeeded because those items run under
`PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM`, which does carry
`metadata`; `WI-5664` does not belong to that project, so that precedent does not
transfer.

The denial is honored rather than bypassed. Consequence for implementation: the
per-artifact approval packets required above cannot be written under this PAUTH
as scoped. Before the protected-artifact edits proceed, exactly one of the
following must happen, and this proposal takes no position on which:

1. the owner amends the skill-rename PAUTH to add the `metadata` class; or
2. the packets are authorized through a separate owner-approval path outside
   this PAUTH's target scope.

Implementation must stop at that gate rather than force the packet writes. The
five `.claude/skills/*/SKILL.md` corrections and the new platform test are
unaffected by this denial and remain fully authorized.

Because the four `.claude/rules/*.md` files are one-way generated projections,
the implementation must present the canonical `config/agent-control/gtkb-*.md`
content in each packet and treat the regenerated projection as the derived
artifact of that same approved change.

The five `.claude/skills/*/SKILL.md` targets classify as `configuration` and do
not require narrative-artifact packets. `.codex/skills/**` adapters are
generated; they are regenerated, never hand-edited.

### Known implementation-time gate

During this session a read against `config/` was blocked verbatim by:

```text
BLOCKED (GTKB-WORK-SUBJECT): Current work subject is GT-KB. This change targets
application product artifacts (`config/`). Switch with standalone `work subject
application` before proceeding.
```

The gate is recorded rather than routed around. The implementer will encounter it
on the four canonical `config/agent-control/` edits and must resolve it through
the sanctioned work-subject path, not by bypass. If that gate cannot be satisfied
for GT-KB platform configuration, implementation stops and files a revised
proposal rather than forcing the edit.

## Acceptance Criterion — Recurrence Prevention

A deterministic assertion is added at
`platform_tests/scripts/test_skill_citation_resolution.py`:

- **Scope surfaces:** `.claude/rules/*.md`, `.claude/skills/*/SKILL.md`,
  `CLAUDE.md`, `AGENTS.md`.
- **Assertion:** every `.claude/skills/<name>/` citation appearing in those
  surfaces resolves to an existing directory under `.claude/skills/`.
- **Match rule:** the regex requires a non-empty `<name>` segment, so bare
  `.claude/skills/` directory references (verified present at
  `.claude/rules/codex-knowledge-base-index.md:52`,
  `.claude/rules/codex-session-bootstrap.md:14`,
  `.claude/skills/gtkb-bridge/SKILL.md:269`, and four others) are correctly not
  flagged.
- **Failure output:** file, line, cited name, and the nearest existing
  directory, so a future rename gets an actionable failure rather than a bare
  assert.
- **Pre-state:** the test must be demonstrated **failing with exactly thirteen
  findings** before the repair and passing after. That red-then-green evidence is
  the acceptance proof; a test that is green on arrival proves nothing.

This assertion is the binding acceptance criterion and closes the class: the next
skill rename cannot silently reopen it.

**Doctor check deferred, with reason.** `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
is the natural home, but it currently reports `M ` in `git status --short`
(staged, uncommitted work from another thread). Adding a check to it now would
commingle this repair with unrelated uncommitted changes and put a clean scoped
commit out of reach — the precise failure this work item exists to end. The
doctor check is therefore declared as a named follow-on work item to be filed
after `doctor.py` is clean. The platform test above provides full mechanical
coverage in the meantime; the doctor check would add surfacing, not coverage.

## Pre-Filing Preflight

Executed before filing and reported without embellishment:

- `scripts/bridge_applicability_preflight.py --content-file <draft>` — must
  report `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`.
- `scripts/adr_dcl_clause_preflight.py --content-file <draft>` — must report
  zero blocking gaps.
- Every specification and deliberation ID cited above was phantom-checked
  against MemBase via `gt spec show` / `gt deliberations get`; all resolve.

No focused pytest evidence is claimed as pre-filing. The test named under
Acceptance Criterion does not yet exist and is post-implementation work.

## Verification Plan

| Requirement | Focused evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `Test-Path` on each of the thirteen repaired citations returns `True`; the four `gtkb-verify` finalization citations resolve to the live helper |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_skill_citation_resolution.py -q` — red (13 findings) pre-repair, green post-repair |
| projection authority | `python scripts/generate_rule_compatibility_projections.py --check` reports the four repaired projections current. Baseline note: it currently reports `would update 1 file(s) - .claude/rules/project-root-boundary.md`. That is pre-existing drift from another thread, explicitly out of scope, and must remain the **only** residual entry after this repair |
| adapter parity | `python scripts/generate_codex_skill_adapters.py --update-registry` regenerates `.codex/skills/**`; re-run reports no pending changes |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | one approval packet per protected artifact with matching content hash — not creatable under the current PAUTH class set, so protected-artifact edits must not begin until the class gap is resolved |
| no behavior change | the diff contains only skill-directory path corrections; no policy, command semantics, or lifecycle behavior is altered |

## Recommended Commit Type

`fix:` — this repairs broken path resolution in governed surfaces that
misdirects the reviewer finalization path. It adds no new capability surface
beyond the guarding regression test, so `feat:` would overstate it and `chore:`
would understate a correctness repair.

## Risk And Rollback

Risk is bounded. Every edit replaces a dead directory name with an existing one;
no policy, command semantics, or bridge lifecycle behavior changes. The residual
risks are (a) editing a generated projection instead of its canonical input —
mitigated by editing canonical `config/agent-control/gtkb-*.md` first and
regenerating, with `--check` as proof; (b) mutating a protected narrative
artifact without its packet — mitigated by the per-artifact packet requirement
above; (c) the work-subject gate blocking `config/` edits — mitigated by
stopping and re-proposing rather than bypassing.

If the generator, adapter regeneration, or the new assertion surfaces files
beyond the thirteen declared citations, implementation stops and files a revised
proposal rather than attributing undeclared files to `WI-5664`.

Rollback is a scoped revert of only the declared canonical, projection, skill,
adapter, and test paths under separate authorization, followed by the same
regeneration and assertion checks. Numbered bridge artifacts, approval packets,
and PAUTH records remain append-only evidence and are never deleted.

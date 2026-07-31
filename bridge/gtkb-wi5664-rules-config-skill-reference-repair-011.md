REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 304c2c33-128d-4bf3-a997-17ecdcb19669
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code manual-dispatch proposal worker; resolved role prime-builder per leader dispatch under DELIB-202667523

bridge_kind: prime_proposal
Document: gtkb-wi5664-rules-config-skill-reference-repair
Version: 011
Date: 2026-07-30 UTC
Author: Prime Builder (Claude, harness B)
Responds to: bridge/gtkb-wi5664-rules-config-skill-reference-repair-010.md

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project Authorization Row: 950
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", ".claude/rules/auto-finalization-sweep.md", ".claude/rules/codex-review-gate.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/loyal-opposition.md", "platform_tests/scripts/test_skill_citation_resolution.py", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-auto-finalization-sweep.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-review-gate.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-file-bridge-protocol.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-loyal-opposition.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-auto-finalization-sweep.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-codex-review-gate.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-file-bridge-protocol.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-loyal-opposition.json"]

implementation_scope: configuration, documentation, metadata, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

# Implementation Proposal Revision — WI-5664 rule/config skill-reference repair

## Revision Claim

V010 returned `NO-GO` on exactly one ground: WI-5664 sat in a dual-active-parent
cohort, and the reviewer required a unique canonical parent before any `GO`.
That blocker is now resolved by owner decision `DELIB-202667733`.

V011 therefore changes three things and nothing else:

1. It answers the v010 blocker with the owner's unique-canonical-parent decision.
2. It adds the Skill-Rename membership detach as an explicit, governed, scoped
   MemBase metadata step.
3. It re-bases the authorization triple onto the Obsolete Reference Purge grant.

The v005 approved design and the v009 S3-only scope narrowing that v010 called
"directionally sound" are carried forward unchanged. Nothing the reviewer already
accepted is redesigned in this revision.

### Disarming statement — this filing mutates nothing

This filing performs no implementation, no MemBase write, no project membership
change, no approval-packet creation, no target edit, no implementation-start
packet creation, no Git action, no dispatcher or TAFE action, and no external
mutation. Every operation described below is a proposed post-`GO` step, not an
executed one. The `kb_mutation_in_scope: true` declaration above describes the
single governed MemBase operation requested for the implementation phase; it
records no MemBase write performed during this filing.

## How V011 Answers The V010 NO-GO

### V010's sole blocking ground, quoted

> NO-GO on executable authority of v009. PAUTH v2 / DELIB-202667718 content and
> S3-only scope narrowing are otherwise directionally sound, but WI-5664 remains
> in the dual-active-parent cohort (Obsolete Reference Purge + Skill Rename)
> pending owner AUQ / WI-5762 unique-parent enforcement. Packets correctly
> deferred post-GO. Require unique canonical parent before any GO.

V010 raised no finding against the repair design, the target set, the selected
render method, the approval-hold boundary, or the packet deferral. Its clause
preflight reported five clauses evaluated, three `must_apply`, zero evidence
gaps, and zero blocking gaps. Its applicability preflight reported
`preflight_passed: true` with empty missing-spec lists.

### The requirement is satisfied — owner decision of record

`DELIB-202667733` (`AUQ-20260730-WI5664-CANONICAL-PARENT`, 2026-07-30,
`outcome: owner_decision`, `work_item: WI-5664`) states verbatim:

> **Option 1 — PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE is the canonical parent.**

and records the authorized consequences verbatim:

> - PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE is WI-5664's unique canonical parent.
> - The Skill Rename membership for WI-5664 is to be detached through the
>   governed path.
> - The controlling grant for WI-5664 is
>   `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730`
>   (owner decision DELIB-202667718).

The decision was recorded against the exact verdict v010 issued: its own
verification block cites
`bridge/gtkb-wi5664-rules-config-skill-reference-repair-010.md`,
`latest_status: NO-GO`, `version_count: 10`. It is a direct answer to this
verdict, not a general policy statement reused here.

`DELIB-202667733` also carries an explicit non-authorization boundary, which this
proposal adopts rather than reads past:

> This decision resolves parent ambiguity only. It does not grant implementation
> authority by itself.

Accordingly v011 requests review, not execution. The full governed cycle — `GO`,
fresh claim, implementation-start packet, exact target enforcement, report, and
independent `VERIFIED` — remains mandatory.

### Freshly verified state, this session

| Check | Command | Result |
| --- | --- | --- |
| Thread frontier | `gt bridge show gtkb-wi5664-rules-config-skill-reference-repair --json --compact` | `latest_status: NO-GO`, `latest_path: …-010.md`, `version_count: 10` |
| Owner decision exists | `gt deliberations get DELIB-202667733` | version 1, `outcome: owner_decision`, `work_item: WI-5664` |
| Grant exists and is live | `gt projects show-authorization PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730 --json` | `status: active`, `version: 2`, `rowid: 950`, `expires_at: null`, `included_work_item_ids: null`, `excluded_work_item_ids: null`, `project_id: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` |
| Dual membership still present | `gt projects show <project> --json` | `PWM-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5664` `membership_status: active` v1; `PWM-GTKB-SKILL-RENAME-REFERENCE-SWEEP-WI-5664` `membership_status: active` v1 |
| Independent parent corroboration | `scripts/bridge_claim_cli.py claim gtkb-wi5664-rules-config-skill-reference-repair` | claim row 35199 resolved `project_id: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` |

The claim's independently-resolved `project_id` matters: the governed claim path
selects the Obsolete Reference Purge project for this thread without being told
to, which corroborates the owner's selection through a second mechanism.

## Proposed Step 0 — Governed Skill-Rename Membership Detach

`DELIB-202667733` directs that the Skill-Rename membership "is to be detached
through the governed path." This proposal declares that detach as an explicit,
bounded, first step of implementation. It is not performed by this filing.

**Classification.** The detach is a MemBase project-membership metadata mutation.
It is not a code change, touches no file in `target_paths`, and produces no diff.
It is declared under the `metadata` mutation class, which
`PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730` v2 allows.

**Exact operation, and only this one:**

```text
gt projects remove-item GTKB-SKILL-RENAME-REFERENCE-SWEEP WI-5664 \
  --change-reason "<cites DELIB-202667733 unique-canonical-parent owner decision>"
```

**Bounded properties, each verified against the CLI contract:**

- `gt projects remove-item` is documented as "Detach one work item from a project
  (append-only, non-active membership)." It appends a non-active membership
  version; it deletes no row and rewrites no history.
- The target is the Skill-Rename membership `PWM-GTKB-SKILL-RENAME-REFERENCE-SWEEP-WI-5664`
  only. The membership id is stable and stated here so the reviewer can bind the
  operation to one exact row.
- `PWM-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5664` is untouched and remains
  `active`. After the detach WI-5664 has exactly one active first-class parent.
- The project id is `GTKB-SKILL-RENAME-REFERENCE-SWEEP`. `DELIB-202667733` option
  text refers to it informally as "PROJECT-GTKB-SKILL-RENAME"; the canonical
  record id verified via `gt projects list --json` this session is
  `GTKB-SKILL-RENAME-REFERENCE-SWEEP`. The proposal uses the canonical id.
- No other work item's membership in either project is altered.
- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-…` is not revoked, amended, or
  otherwise touched. Per `DELIB-202667718`, that authorization "remains valid on
  its own terms for the work items that authorization genuinely governs." The
  detach removes WI-5664 from its member set by membership, not by revoking a
  grant that other work items rely on.

**Ordering.** The detach runs first, before any target edit, so that every
subsequent operation-time authorization check resolves against a single
unambiguous parent. If the detach fails or resolves a different membership row
than the one named above, implementation stops and files a revision rather than
proceeding under ambiguous parentage.

**Disarming statement.** No membership change is executed by this filing. The
command above is a proposal for post-`GO` execution and has not been run.

## Re-Based Authorization Triple

| Field | V009 value | V011 value | Basis |
| --- | --- | --- | --- |
| Project Authorization | `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730` | unchanged | `DELIB-202667718` |
| Project | `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` | unchanged, now **unique** | `DELIB-202667733` |
| Work Item | `WI-5664` | unchanged | — |

The triple's identifiers are the same as v009's. What changed is that they are
now the *only* live reading rather than one of two competing ones. V009 asserted
Obsolete Reference Purge as authoritative on the strength of
`DELIB-202667719`'s list-free-controls rule; v010 declined to accept that
inference while a second active parent existed. V011 does not re-argue the
inference — it cites the owner decision that settles it.

Grant properties re-verified this session and relied on here:

- `status: active`; `expires_at: null`.
- `included_work_item_ids: null` and `excluded_work_item_ids: null` — list-free,
  so active project members inherit without an allowlist.
- `allowed_mutation_classes`: `source`, `test`, `test_addition`, `configuration`,
  `documentation`, `metadata`, `governance_evidence`, `bridge`. Every class this
  repair needs is present, including `metadata` for the packet envelope and the
  Step 0 membership detach.
- `forbidden_operations`: `dispatcher_mutation`, `external_system_mutation`,
  `credential_lifecycle`, `push`, `history_rewrite`, `deployment`, `release`,
  `destructive_cleanup`. None is requested.
- `included_spec_ids`: `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-APPROVAL-001`.

The grant's own `scope_summary` preserves the full per-item cycle and states that
"Protected narrative artifacts and formal MemBase records still require their own
per-artifact approval packets under GOV-ARTIFACT-APPROVAL-001; class
authorization does not substitute." V011 adopts that constraint verbatim below.

## Carried Forward From V005 And V009 — The Approved Design

Nothing in this section is new. It is restated so the reviewer can bind `GO` to
v011 without re-reading the chain, per the requirement that a `GO` bind the exact
operative version.

### Exact defect and repair — five citations, four canonical documents

Re-verified this session by deterministic scan of `config/agent-control/gtkb-*.md`
for `.claude/skills/(verify|bridge-propose)/` citations:

| # | Canonical authority (edited) | Line | Generated projection (regenerated) | Dead citation | Live replacement |
| --- | --- | --- | --- | --- | --- |
| 1 | `config/agent-control/gtkb-auto-finalization-sweep.md` | 62 | `.claude/rules/auto-finalization-sweep.md` | `verify` | `gtkb-verify` |
| 2 | `config/agent-control/gtkb-review-gate.md` | 130 | `.claude/rules/codex-review-gate.md` | `verify` | `gtkb-verify` |
| 3 | `config/agent-control/gtkb-review-gate.md` | 168 | `.claude/rules/codex-review-gate.md` | `bridge-propose` | `gtkb-bridge-propose` |
| 4 | `config/agent-control/gtkb-file-bridge-protocol.md` | 178 | `.claude/rules/file-bridge-protocol.md` | `verify` | `gtkb-verify` |
| 5 | `config/agent-control/gtkb-loyal-opposition.md` | 160 | `.claude/rules/loyal-opposition.md` | `verify` | `gtkb-verify` |

Four of the five (rows 1, 2, 4, 5) cite the Loyal Opposition finalization helper.
`Test-Path` re-run this session at `HEAD = 8a35eabc8`:

| Path | `Test-Path` |
| --- | --- |
| `.claude/skills/verify/helpers/write_verdict.py` | **False** — dead |
| `.claude/skills/gtkb-verify/helpers/write_verdict.py` | **True** — live |
| `.claude/skills/bridge-propose/` | **False** — dead |
| `.claude/skills/gtkb-bridge-propose/` | **True** — live |

A reviewer who follows the governed finalization instruction in any of those four
documents lands on a nonexistent file. That mechanically produces the
file-only-`VERIFIED` class: a terminal verdict written with no commit created.

### Relationship to the thirteen-citation program inventory

V005 inventoried thirteen stale citations across all governed surfaces. Ownership
was subsequently split by `DELIB-202667193`:

- WI-5662 owns the five canonical `.claude/skills/*/SKILL.md` targets and their
  eight residual citations.
- WI-5663 owns the generated Codex/Agent adapters, manifests, and registry-hash
  cascade.
- **WI-5664 owns only the rule/config S3 slice — the five citations above.**

Five plus eight is the thirteen. V011 keeps the v009 narrowing that v010
accepted: every `.claude/skills/**` and `.codex/skills/**` target is excluded.
This proposal edits no canonical Skill source and regenerates no Skill adapter.
Its assertion is scoped to the four rule/config pairs and makes no claim about
the eight delegated citations.

### Projection authority — the repair direction is one-way

`config/file-reference-migration/wi5640.toml` was re-read this session and maps
each projection to its canonical input:

| Ledger lines | `source` (projection) | `canonical` (authority) |
| --- | --- | --- |
| 857-858 | `.claude/rules/auto-finalization-sweep.md` | `config/agent-control/gtkb-auto-finalization-sweep.md` |
| 929-930 | `.claude/rules/codex-review-gate.md` | `config/agent-control/gtkb-review-gate.md` |
| 971-972 | `.claude/rules/file-bridge-protocol.md` | `config/agent-control/gtkb-file-bridge-protocol.md` |
| 995-996 | `.claude/rules/loyal-opposition.md` | `config/agent-control/gtkb-loyal-opposition.md` |

`scripts/generate_rule_compatibility_projections.py` documents itself as
"intentionally one-way: it never reads a retained projection as authority and
never mutates a canonical file."

**Consequence, binding on implementation.** The `.claude/rules/*.md` files must
not be edited directly. Implementation edits the four canonical
`config/agent-control/gtkb-*.md` inputs, then renders the projections. Both sides
appear in `target_paths` because the regenerated projection bytes change.

The full generator currently reports unrelated drift on
`.claude/rules/project-root-boundary.md`. Implementation must not run an
unbounded mutating regeneration against the live tree; it must use the existing
nonmutating render surface to select exactly these four outputs and leave every
other rendered difference untouched. Inability to produce exact selected outputs
is a hard stop and revision trigger.

### Scope precision — what this does not claim

`scripts/auto_finalize_sweep.py` already resolves the live `gtkb-verify` helper
directory. This repair therefore does **not** claim to fix auto-finalization
sweep liveness; that has separate causes outside this work item. The defect
proven here is documentation-to-reality drift on the **reviewer-facing** path.
`scripts/_dispatch_wi5241_006_verdict.py` also cites the dead path and is a
one-off dispatch script explicitly out of scope — recorded so the reviewer can
see it was found rather than missed.

## Protected Artifact Approval Boundary

The four canonical config documents and the four projections are protected
narrative artifacts. Each requires its own exact formal-artifact approval packet
under `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`. V011
declares the same eight stable, exact packet filenames v009 declared, which v010
recorded as "correctly deferred post-GO."

The grant authorizes the `metadata` class, but class authorization does not
approve narrative bytes. Packet generation must occur only within the governed
bridge/AUQ/gate workflow, use LF-normalized full content and hashes, and pass
`scripts/validate_formal_artifact_packet.py` against the live gate.

Zero packets matching `*WI-5664*` exist under
`.groundtruth/formal-artifact-approvals/`, verified this session. After a fresh
`GO`, implementation must first prepare the exact postimage content and put the
eight packets to the owner for explicit approval. Until all eight exist, validate,
match the exact proposed bytes, and carry approval evidence, protected-artifact
implementation remains on HOLD. No protected file may be written first.

**Disarming statement.** No approval packet is created, presented, validated, or
relied upon by this filing. The eight packet paths are declared target slots for
post-`GO` work; all eight are currently absent and this filing leaves them absent.

## Cross-Harness Disposition

- Claude and every harness consuming canonical `config/agent-control` guidance
  receive the same five corrected citations.
- Codex consumes the four regenerated `.claude/rules` projections; their bytes
  must equal the canonical selected render outputs.
- Cursor, Antigravity, Ollama, OpenRouter, Goose, and Alibaba Cloud Studio have no
  separate target or adapter change in this slice. They continue to resolve the
  same canonical managed-skill directories; no typed waiver is used.
- Canonical Skill sources and generated Skill adapters are deliberately unchanged
  and remain owned by WI-5662 and WI-5663.

Parity verification compares each canonical/projection pair and proves every
applicable harness resolves the same live `gtkb-verify` and `gtkb-bridge-propose`
directories without modifying another harness surface.

## Current Worktree And Ownership Evidence

Re-observed this session:

- All eight rule/config targets are tracked and clean in worktree and index
  (`git ls-files` matches; `git status --short` empty for each).
- `platform_tests/scripts/test_skill_citation_resolution.py` does not exist and
  is a clean new-file slot.
- The eight packet paths do not exist and are clean new-file slots.
- A `draft`-kind work-intent claim (row 35199, session
  `304c2c33-128d-4bf3-a997-17ecdcb19669`) was acquired for this filing only. No
  implementation-start packet exists for WI-5664.
- Both project memberships remain `active` at version 1; the Step 0 detach has
  not been performed.
- Dispatcher and TAFE remain deliberately disabled; neither is a target nor a
  permitted operation.

Every target and the physical bridge head must be re-observed immediately before
claim and start. Any changed preimage, new packet at a declared path, ownership
collision, foreign staged target, membership drift, or PAUTH drift requires stop
and append-only revision.

## Requirement Sufficiency

Existing requirements are sufficient. This is a bounded stale-reference repair
with deterministic mappings, plus one owner-directed governed membership detach
already decided in `DELIB-202667733`. No policy or product behavior changes. No
new or revised specification is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the governed finalization path the four dead
  helper citations misdirect; the specification this repair restores.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation
  authorization governing the re-based triple.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — the membership rule the
  Step 0 detach preserves by leaving exactly one active approved parent.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time
  authorization checks at claim and start.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project authorization does not
  bypass the bridge cycle; this proposal requests review, not execution.
- `GOV-ARTIFACT-APPROVAL-001` — per-artifact owner approval for the eight
  protected narrative artifacts.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — approval-packet display and hash contract,
  binding at implementation time and not exercised by this filing.
- `ADR-CROSS-HARNESS-PARITY-001` — parity obligation across consuming harnesses.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — mechanical parity enforcement for
  the canonical/projection pairs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds this revision to
  `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`, `WI-5664`, and the active PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing-spec
  linkage and spec-derived tests for this proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the recurrence
  assertion and regeneration evidence before `VERIFIED`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — canonical-reader read discipline; a
  citation resolving to a nonexistent directory is a read-path defect.
- `GOV-WORK-TREE-HYGIENE-001` — scoped diff and no adoption of foreign staged
  paths.
- `GOV-STANDING-BACKLOG-001` — standing-backlog work-item boundary and the
  MemBase membership metadata touched by Step 0.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — status semantics for the prior v007
  `NO-ACTION` in this chain.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — confines this slice to GT-KB
  platform surfaces; no adopter-application path is touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — governed artifact lifecycle for this
  bounded backlog item.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle-trigger classification for the
  repair and the membership detach.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance stance.

## Prior Deliberations

- `DELIB-202667733` — **the owner decision that answers v010.**
  `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` is WI-5664's unique canonical parent;
  the Skill-Rename membership is to be detached through the governed path; the
  controlling grant is the Obsolete Reference Purge whole-project PAUTH. Carries
  an explicit non-authorization boundary that this proposal adopts.
- `DELIB-202667718` — owner authorization establishing the list-free
  whole-project Obsolete Reference Purge grant, its allowed classes, and its
  retained bans. Also records the dual-membership condition as known and
  deliberately unresolved at that time — the gap `DELIB-202667733` later closed.
- `DELIB-202667719` — transitional authority rule: list-free grants control where
  both a WI-restricted and a list-free grant exist. Cited by v009; superseded as
  the operative basis here by the direct owner decision.
- `DELIB-202667715` — owner approval of the Skill-Rename PAUTH v2. Recorded so the
  reviewer can confirm the Step 0 detach does not revoke or invalidate it.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — project-level approval
  supersedes individual work-item approval state.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-level
  implementation authority inheritance.
- `DELIB-202667193` — canonical Skill-Rename slice ownership: WI-5662 owns
  canonical Skill sources, WI-5663 owns generated adapters, WI-5664 owns the
  rule/config slice. The basis for the S3-only narrowing v010 accepted.
- `DELIB-202667105` — Loyal Opposition `GO` on the Canonical Skill Renaming
  Rollout; the rename event that created this drift.
- `DELIB-202667531` — fix-class-first advisory triage with authorized corrective
  work items.
- `DELIB-202667523` — integrated parallel-operation program mandate under which
  this worker was dispatched.
- Chain history: v005 approved design; v006 missing reviewer clause evidence; v007
  `NO-ACTION` on stale authority; v008 corrected `NO-GO`; v009 S3-only narrowing;
  v010 `NO-GO` on dual parent only.

No prior deliberation rejects this narrowed rule/config repair, and none conflicts
with `DELIB-202667733`.

## Owner Decisions / Input

Two owner decisions are load-bearing for this revision. Both were verified by
exact-id lookup this session.

**`DELIB-202667733`** — `AUQ-20260730-WI5664-CANONICAL-PARENT`, 2026-07-30,
`outcome: owner_decision`, `work_item: WI-5664`, source
`owner_conversation: AUQ-20260730-WI5664-CANONICAL-PARENT`. The owner was
presented three options and selected Option 1:
`PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` is the unique canonical parent, with the
Skill-Rename membership to be detached through the governed path. This is the
owner decision that removes v010's sole blocking ground and the authority for
Step 0. The decision explicitly does not grant implementation authority; v011
requests review only.

**`DELIB-202667718`** — `AUQ-20260730-OBSOLETE-REFERENCE-PURGE-PROJECT-PAUTH`,
2026-07-30, `outcome: owner_decision`, `work_item: WI-5664`. The owner authorized
the list-free whole-project grant
`PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730`, its eight
allowed mutation classes plus governed local commit, and its retained bans. This
is the controlling authorization for the re-based triple.

No new owner decision is required to review v011. One further owner decision is
mandatory later: explicit AUQ approval of the eight exact postimage approval
packets before any protected-artifact mutation. This filing does not request that
approval and does not anticipate its outcome.

## Verification Plan

| Requirement | Governing spec | Exact evidence after authorized implementation |
| --- | --- | --- |
| Unique canonical parent established | `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` | `gt projects show` reports `PWM-GTKB-SKILL-RENAME-REFERENCE-SWEEP-WI-5664` non-active at v2 and `PWM-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5664` still `active`; exactly one active first-class parent remains; no other membership row changed |
| Five stale citations repaired | `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused test shows exactly five findings before repair and zero after; `Test-Path` returns `True` for every replacement directory |
| Canonical projection authority honored | `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Nonmutating render selects exactly the four declared projections; written bytes equal the selected canonical outputs; unrelated `project-root-boundary.md` drift remains the only residual entry |
| Cross-harness parity | `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Each canonical/projection pair carries identical live directory citations; no Skill, adapter, or other harness file changes |
| Protected-artifact governance | `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Eight LF-normalized packets validate and bind exact full-content SHA-256 values before any write |
| Focused recurrence guard | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_skill_citation_resolution.py -q --tb=short` red with exactly five findings pre-repair, green post-repair |
| Test and style hygiene | `GOV-WORK-TREE-HYGIENE-001` | `ruff check` and `ruff format --check` pass on the new Python test |
| Operation-time project authority | `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Candidate applicability and schema-v3 start select PAUTH v2 row 950, single active membership, exact targets, allowed operations |
| Scoped hygiene | `GOV-WORK-TREE-HYGIENE-001` | `git diff` / `git status` show only declared target bytes; no foreign staged path adopted |
| Atomic finalization | `GOV-FILE-BRIDGE-AUTHORITY-001` | After independent report review, the governed finalizer commits only approved packet, content, test, and bridge hunks; push remains forbidden |

The acceptance criterion is red-then-green on the focused test. A test green on
arrival proves nothing; the pre-repair red state with exactly five findings is the
proof the assertion actually binds this defect.

## Pre-Filing Preflight

Executed against the v011 candidate before publication, reported without
embellishment:

- `python scripts/bridge_applicability_preflight.py --content-file <candidate> --json`
  must report `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, no unclassified target, and project authorization
  allowed under PAUTH v2 row 950.
- `python scripts/adr_dcl_clause_preflight.py --content-file <candidate>` must
  report zero must-apply evidence gaps and zero blocking gaps. `--report-only` is
  not used.
- Every specification and deliberation id cited above was phantom-checked by
  exact-id lookup (`gt spec show`, `gt deliberations get`); all resolve.
- Current v010 `NO-GO` frontier, both active memberships, the active grant, and
  the eight clean existing targets were re-observed unchanged.

No focused pytest evidence is claimed as pre-filing. The test named under
Verification Plan does not yet exist and is post-implementation work.

## Risk And Rollback

Residual risks: protected-content approval mismatch; accidental full-tree
generator application; collision with WI-5662 or WI-5663; concurrent target
drift; and — new in v011 — a membership detach that resolves the wrong row.

Mitigations: exact packet names and hashes; selected nonmutating render output;
explicit adjacent-slice exclusions; fail-closed target preimage and start gates;
and for Step 0, binding the detach to the named membership id
`PWM-GTKB-SKILL-RENAME-REFERENCE-SWEEP-WI-5664` with post-operation confirmation
that the Obsolete Reference Purge membership is still `active` before any target
edit proceeds.

If rendering, testing, or the detach surfaces any undeclared file or unexpected
membership row, implementation stops and files a revision. Rollback is a
separately authorized scoped revert of only the declared target hunks, followed by
the same packet, render, parity, and focused-test checks. The membership detach is
append-only and is reversed, if ever needed, by a further append-only membership
version — never by row deletion. Numbered bridge files, packets, PAUTH rows, and
deliberation history remain append-only and are never rewritten or deleted.

## Recommended commit type

`fix:` — this repairs broken path resolution in governed surfaces that misdirects
the reviewer finalization path. It adds no new capability surface beyond the
guarding regression test, so `feat:` would overstate it and `chore:` would
understate a correctness repair.

## Requested Loyal Opposition Action

Review v011 as the narrowed S3 implementation proposal with its unique-parent
blocker resolved. V010's sole blocking ground was the dual-active-parent cohort;
`DELIB-202667733` settles it by owner decision and directs the governed detach
declared as Step 0.

Return `GO` only if the unique-parent resolution, the bounded Step 0 detach, the
re-based authorization triple, the carried-forward S3-only scope, the exact
rule/config and packet targets, the approval hold, the selected-render method,
cross-harness parity, and the focused test are complete. Otherwise return `NO-GO`
with exact corrections.

A `GO` must not be read as approval of protected postimage bytes, dispatcher or
TAFE activation, deployment, release, push, credential action, destructive
cleanup, or authority for WI-5662, WI-5663, or WI-5783.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

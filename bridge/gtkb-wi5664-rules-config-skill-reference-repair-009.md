REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher and TAFE deliberately disabled
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5664-rules-config-skill-reference-repair
Version: 009
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5664-rules-config-skill-reference-repair-008.md

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project Authorization Row: 950
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", ".claude/rules/auto-finalization-sweep.md", ".claude/rules/codex-review-gate.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/loyal-opposition.md", "platform_tests/scripts/test_skill_citation_resolution.py", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-auto-finalization-sweep.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-review-gate.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-file-bridge-protocol.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-config-gtkb-loyal-opposition.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-auto-finalization-sweep.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-codex-review-gate.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-file-bridge-protocol.json", ".groundtruth/formal-artifact-approvals/2026-07-30-WI-5664-rule-loyal-opposition.json"]

implementation_scope: configuration, documentation, metadata, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Implementation Proposal Revision — WI-5664 rule/config skill-reference repair

## Revision Claim

Repair the five stale skill-directory citations in four canonical GT-KB
rule/config documents, regenerate only their four declared rule projections, and
add one focused recurrence test. This v009 answers v008 under the owner's
current list-free Obsolete Reference Purge PAUTH while removing every canonical
Skill and generated-adapter path owned by adjacent WI-5662/WI-5663.

The functional change is five string corrections only:

- four `verify` citations become `gtkb-verify`;
- one `bridge-propose` citation becomes `gtkb-bridge-propose`.

No policy, command, lifecycle, hook, dispatcher, TAFE, runtime, or application
behavior changes. No implementation, approval-packet creation, target edit,
claim, implementation-start packet, Git action, dispatcher/TAFE action, or
external mutation occurs during this filing.

## Findings Addressed

### V008 P1 — project authority was insufficient

Resolved by `DELIB-202667718` and active project authorization
`PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730` v2,
row 950:

- project `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` is active;
- `included_work_item_ids: null`, so active project members inherit it;
- WI-5664 is open and has active first-class membership;
- allowed classes are `source`, `test`, `test_addition`, `configuration`,
  `documentation`, `metadata`, `governance_evidence`, and `bridge`;
- governed local `git_commit` is permitted by the scope summary;
- dispatcher mutation, external-system mutation, credential lifecycle, push,
  history rewrite, deployment, release, and destructive cleanup remain banned.

The authorization scope explicitly cites the remedy in v007 and preserves the
full bridge, claim, start, protected-artifact, verification, and finalization
gates. No legacy Skill Rename WI allowlist is controlling or combined with it.

### V008 P1 — v006 omitted independent clause evidence

V008 supplied the missing reviewer-side Clause Applicability evidence for v007:
five clauses evaluated, three `must_apply`, zero evidence gaps, and zero blocking
gaps. V009 is rerun through both candidate preflights. A future GO must bind v009
and include its own complete applicability and clause evidence; v006 is not
reused as execution authority.

### Scope correction — do not absorb WI-5662 or WI-5663

V005 combined three slices. Current ownership evidence requires separation:

- WI-5662 owns the five canonical `.claude/skills/*/SKILL.md` targets and their
  eight residual stale citations.
- WI-5663 owns the generated Codex/Agent adapters, manifests, and registry-hash
  cascade.
- WI-5664 owns only the rule/config S3 slice in this proposal.

Accordingly v009 removes every `.claude/skills/**` and `.codex/skills/**` target.
It neither edits canonical Skill sources nor regenerates any Skill adapter.
The focused assertion is scoped to the four rule/config pairs; it does not claim
that the eight delegated canonical-Skill citations are already fixed.

## Exact Defect And Repair

| # | Canonical authority | Generated projection | Dead citation | Live replacement |
| --- | --- | --- | --- | --- |
| 1 | `config/agent-control/gtkb-auto-finalization-sweep.md` | `.claude/rules/auto-finalization-sweep.md` | `verify` | `gtkb-verify` |
| 2 | `config/agent-control/gtkb-review-gate.md` | `.claude/rules/codex-review-gate.md` | `verify` | `gtkb-verify` |
| 3 | `config/agent-control/gtkb-review-gate.md` | `.claude/rules/codex-review-gate.md` | `bridge-propose` | `gtkb-bridge-propose` |
| 4 | `config/agent-control/gtkb-file-bridge-protocol.md` | `.claude/rules/file-bridge-protocol.md` | `verify` | `gtkb-verify` |
| 5 | `config/agent-control/gtkb-loyal-opposition.md` | `.claude/rules/loyal-opposition.md` | `verify` | `gtkb-verify` |

Every dead directory is absent and each declared replacement directory exists.
The four config documents are canonical inputs; the four `.claude/rules`
documents are one-way projections. Implementation must change canonical inputs
first, render only the four authorized outputs, and compare exact bytes before
writing the projections.

The full projection generator currently reports unrelated
`.claude/rules/project-root-boundary.md` drift. Implementation must not run an
unbounded mutating regeneration against the live tree. It must use the existing
nonmutating render surface to select these four outputs and leave every other
rendered difference untouched. Any inability to produce exact selected outputs
is a hard stop and revision trigger.

`scripts/auto_finalize_sweep.py` already resolves the live `gtkb-verify` helper,
so this repair does not claim to fix sweep liveness. Historical one-off dispatch
scripts and all application paths remain out of scope.

## Protected Artifact Approval Boundary

The four canonical config documents and four projections are protected
narrative artifacts. Each requires its own exact formal-artifact approval packet
under `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`.
V009 declares eight stable, exact packet filenames rather than a broad metadata
wildcard.

The current project PAUTH authorizes the metadata class, but class authorization
does not approve narrative bytes. Per the formal-artifact packet helper, packet
generation must occur only within the governed bridge/AUQ/gate workflow, use
LF-normalized full content and hashes, and pass
`scripts/validate_formal_artifact_packet.py` against the live gate.

No packet currently exists for WI-5664. After a fresh GO, Prime must first
prepare the exact postimage content and put the eight packets to the owner for
explicit approval. Until all packets exist, validate, match the exact proposed
bytes, and carry approval evidence, implementation remains on HOLD. No protected
file and no partial Skill/test subset may be written first.

## Cross-Harness Disposition

- Claude and all harnesses that consume canonical `config/agent-control`
  guidance receive the same five corrected citations.
- Codex consumes the four regenerated `.claude/rules` projections; their bytes
  must match the canonical selected render outputs.
- Cursor, Antigravity, Ollama, OpenRouter, Goose, and Alibaba Cloud Studio have
  no separate target or adapter change in this slice. They continue to resolve
  the same canonical managed-skill directories; no typed waiver is used.
- Canonical Skill sources and generated Skill adapters are deliberately
  unchanged and remain owned by WI-5662/WI-5663.

Parity verification compares each canonical/projection pair and proves all
applicable harnesses resolve the same live `gtkb-verify` and
`gtkb-bridge-propose` directories without modifying another harness surface.

## Current Worktree And Ownership Evidence

- All eight rule/config targets are tracked and clean in worktree and index.
- The focused test and eight packet paths do not yet exist and are clean new-file
  slots.
- No active claim or named implementation-start packet exists for WI-5664.
- WI-5763's overlapping historical claim is null; its chain remains stopped and
  grants no ownership here.
- The staged foreign `doctor.py` work and seven-file Antigravity adapter drift
  are excluded.
- Dispatcher and TAFE remain deliberately disabled for repairs and are neither
  targets nor permitted operations.

Every target and the physical bridge head must be re-observed immediately before
claim/start. Any changed preimage, new packet at a declared path, ownership
collision, foreign staged target, or project/PAUTH drift requires stop and
append-only revision.

## Requirement Sufficiency

Existing requirements are sufficient. This is a bounded stale-reference repair
with deterministic mappings and no policy or product behavior change. No new or
revised specification is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202667718` — current list-free whole-project Obsolete Reference Purge
  authorization and safety boundary.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-only
  approval inheritance.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — individual WI approval
  state is not implementation authority.
- `DELIB-202667193` — canonical Skill Rename slice ownership: WI-5662 owns
  canonical Skill sources, WI-5663 owns generated adapters, and WI-5664 owns the
  rule/config slice.
- `DELIB-202667105` — accepted canonical skill-renaming rollout.
- `DELIB-202667531` — fix-class correction direction.
- V005 through v008 — historical combined design, stale-authority finding,
  targetless stop, and independent corrected NO-GO.

No prior deliberation rejects this narrowed rule/config repair.

## Owner Decisions / Input

The project-level decision required by v008 is already captured as
`DELIB-202667718` and active PAUTH v2 row 950. No new owner decision is required
to review v009. A later owner AUQ is mandatory for the eight exact postimage
approval packets before protected mutation.

## Verification Plan

| Requirement | Exact evidence after authorized implementation |
| --- | --- |
| Five stale rule citations repaired | Focused test demonstrates exactly five failing rule/config citations before repair and zero after; every replacement directory exists. |
| Canonical projection authority | Nonmutating render selects exactly the four declared projections; written bytes equal the selected canonical outputs; unrelated `project-root-boundary.md` drift remains untouched. |
| Cross-harness parity | Each canonical/projection pair contains the same live directory citations; no Skill/adapter or other harness file changes. |
| Protected-artifact governance | Eight LF-normalized packets validate and bind the exact full-content SHA-256 values before writes. |
| Focused recurrence guard | `python -m pytest platform_tests/scripts/test_skill_citation_resolution.py -q --tb=short` is red with exactly five findings before repair and green after. |
| Test/style hygiene | Ruff check and format check pass for the new Python test. |
| Project operation-time authority | Candidate applicability and schema-v3 start select PAUTH v2 row 950, active membership, exact targets, and allowed operations. |
| Scoped hygiene | Git diff/status show only declared target bytes; no foreign staged path is adopted. |
| Atomic finalization | After independent report review, governed finalizer commits only approved packet/content/test/bridge hunks; push remains forbidden. |

Positive terminal finalization remains blocked until WI-5783 receives its own
independent terminal acceptance and exact staged-object authorization succeeds.
V009 does not approve, absorb, or implement WI-5783.

## Pre-Filing Preflight

Before live publication:

- `python scripts/bridge_applicability_preflight.py --content-file <candidate> --json`
  must report `preflight_passed: true`, no missing specs, no unclassified target,
  and project authorization allowed under v2 row 950.
- `python scripts/adr_dcl_clause_preflight.py --content-file <candidate>` must
  report zero must-apply evidence gaps and zero blocking gaps.
- Current v008 `NO-GO`, null claim, active project/membership, current PAUTH,
  and exact clean existing targets must remain unchanged.

## Risk And Rollback

Risks are protected-content approval mismatch, accidental full-tree generator
application, collision with WI-5662/WI-5663, or concurrent target drift.
Mitigations are exact packet names/hashes, selected nonmutating render output,
explicit adjacent-slice exclusions, and fail-closed target preimage/start gates.

If rendering or testing surfaces any undeclared file, implementation stops and
files a revision. Rollback is a separately authorized scoped revert of only the
declared target hunks, followed by the same packet, render, parity, and focused
test checks. Numbered bridge files, packets, PAUTH rows, and deliberation history
remain append-only and are never rewritten or deleted.

## Requested Loyal Opposition Action

Review v009 as the narrowed S3 implementation proposal. Return GO only if the
project-authority correction, WI-5662/WI-5663 exclusion, exact rule/config and
packet targets, approval hold, selected-render method, cross-harness parity,
focused test, WI-5783 hold, and finalization boundary are complete. Otherwise
return NO-GO with exact corrections.

A GO must not be interpreted as approval of protected postimage bytes,
dispatcher/TAFE activation, deployment, release, push, credential action,
destructive cleanup, or authority for WI-5662, WI-5663, or WI-5783.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Canonical Skill Documentation Recovery — WI-5662

bridge_kind: prime_proposal
Document: gtkb-wi5662-canonical-doc-reference-recovery
Version: 001
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662

target_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]

## Claim

The historical WI-5662 chain is packet-invalid because it contains decorated
Version metadata and bare PB author identities. This fresh chain preserves its
observed candidate hunks without retroactive attribution. After independent GO
and a successful packet, it will commit only the three canonical Claude skill
documents and no generated adapter, test, template, migration-policy, or
historical artifact.

## Requirement Sufficiency

Existing requirements sufficient. WI-5662 and `DELIB-202667193` authorize the
canonical documentation slice; `DELIB-202667194` requires exact isolation from
WI-5640 file-reference migration content. No new requirement or owner decision
is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667193` — S1 canonical docs precede WI-5663 generated-adapter work.
- `DELIB-202667194` — existing work must remain hunk-isolated; WI-5640 is excluded.

## Owner Decisions / Input

No new decision is required. This is a non-rewriting provenance recovery for
the already owner-approved canonical documentation outcome.

## Exact Reference Inventory

Only the following references may be staged:

| File | Bare reference family to canonicalize |
| --- | --- |
| `.claude/skills/gtkb-bridge/SKILL.md` | `bridge/helpers/{scan_bridge,revise_bridge,impl_report_bridge,protected_write,show_thread_bridge}.py`, `verify/helpers/write_verdict.py`, `proposal-review/SKILL.md`, `send-review/SKILL.md`, and Claude/Codex `bridge/SKILL.md` roots |
| `.claude/skills/gtkb-proposal-review/SKILL.md` | `verify/helpers/write_verdict.py` |
| `.claude/skills/gtkb-verify/SKILL.md` | `verify/helpers/write_verdict.py`, Claude `verify/SKILL.md`, and Codex `verify/SKILL.md` roots |

Every replacement uses the corresponding `gtkb-` directory form. The
`send-review` replacement is mandatory and all occurrences in the three target
documents must be counted before and after staging.

## WI-5640 Isolation

Any `config/agent-control/gtkb-*` file-move/migration literal in the mixed
`gtkb-bridge/SKILL.md` worktree is read-only WI-5640 evidence. It is not in the
reference inventory, must remain unstaged, and may not be formatted, committed,
or attributed by this recovery. Use an index-only patch against the exact HEAD
preimage; never `git add` the whole mixed bridge document.

## Cross-Harness Disposition

- Claude: this is the canonical three-document source correction.
- Codex, Goose, Cursor, Antigravity, API harness, Ollama, and OpenRouter:
  their generated projections are intentionally not changed in this S1 slice.
  Owner-approved typed sequencing waiver: `DELIB-202667193` — reason class
  `sequenced_adapter_regeneration`; scope is only the three documentation
  references in this recovery; review trigger/expiry is an independently
  terminal WI-5662 followed by fresh WI-5663 adapter-regeneration GO. It does
  not waive parity for runtime helper behavior or any future canonical edit.
- No unmanaged harness surface is created or mutated by this recovery.

## Implementation And Verification Plan

1. After GO, acquire the claim and issue `implementation_authorization.py begin` for this recovery; stop before staging on any denial.
2. Build a reviewed zero-context cached patch containing only the table's old-to-new path substitutions. Run `git apply --cached --check` then apply it; verify cached path list equals the three targets.
3. Run an anchored `git grep --cached` residual scan for every listed bare reference, including `send-review`, over exactly the three targets; expect zero matches.
4. Assert cached `gtkb-bridge/SKILL.md` contains no `config/agent-control/gtkb-` change, while the same foreign hunk remains in the unstaged diff.
5. Run `git diff --check --cached`, bridge applicability and clause preflights, and the focused structural check `python -m pytest platform_tests/skills/test_skill_catalog_contract.py -q --tb=short`. Commit only the authorized cached slice and file a strict current implementation report for independent LO review.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge authority | Fresh GO, claim, packet, and three-path cached list | No documentation hunk is adopted before authorization. |
| Canonical reference completeness | Per-target anchored cached residual scan | All table entries, including `send-review`, have zero bare residuals. |
| WI-5640 isolation | Cached/unstaged diff assertions on `gtkb-bridge/SKILL.md` | Migration hunk remains unstaged and unowned. |
| Skill structure | `test_skill_catalog_contract.py` and diff check | No catalog contract or whitespace regression. |

## Acceptance Criteria

- Only the three declared canonical `SKILL.md` files are committed.
- Every listed bare reference is canonicalized, including `send-review`.
- WI-5640 migration literals, generated adapters, templates, and tests remain
  outside the staged and committed slice.
- A later report has exact metadata and independently reviewable commit evidence;
  no terminal claim is made by PB.

## Risks And Rollback

The principal risk is absorbing the mixed WI-5640 hunk. The index-only patch
and staged/unstaged diff assertions fail closed. Any rollback is a separately
governed three-file revert; it never rewrites history or foreign worktree bytes.

## Recommended Commit Type

docs

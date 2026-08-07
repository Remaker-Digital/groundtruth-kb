NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 7d9535ba-4d9e-4b4d-aad3-420153139b97
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-role-set-scratchpad-convention
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-08-07 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-6001

# Implementation Proposal - Canonical Scratchpad Location And Cleanup Duty In The Base Role Sets

## Summary

Add a short `Scratch Files` section to the two base role sets and their two tracked
`config/agent-control` mirrors. The section states three things: the canonical scratch directory
is `E:\GT-KB\scratchpad\`; nothing in it is authoritative; and scratch files are deleted once the
bridge item they supported is filed, or sooner.

The change is **purely additive**. No existing sentence is edited or removed.

target_paths: [".claude/rules/prime-builder.md", ".claude/rules/loyal-opposition.md", "config/agent-control/gtkb-prime-builder.md", "config/agent-control/gtkb-loyal-opposition.md", "AGENTS.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", ".groundtruth/formal-artifact-approvals/**", "platform_tests/scripts/test_role_set_scratchpad_convention.py"]

The `.groundtruth/formal-artifact-approvals/**` envelope is declared because all seven role
surfaces are protected narrative artifacts requiring a per-file approval packet before the write
lands (acceptance criterion 7). The new test module is declared because it is created by this
change.

## Known Parity Gap: `.goosehints` Cannot Be Authorized Today

`.goosehints` is the Goose harness's root role/contract surface and **belongs** in this change on
the owner's parity directive, but it is deliberately absent from `target_paths` because it cannot
currently be authorized. Filing it produced a hard operation-time denial:

```
PAUTH operation-time denial (implementation_packet_create):
  target_mutation_class_not_allowed: .goosehints (unclassified)
PAUTH operation-time denial (implementation_start):
  target_mutation_class_not_allowed: .goosehints (unclassified)
```

`.goosehints` is a root dotfile with no extension, so it matches no rule in the target-path
classifier used by `scripts/bridge_applicability_preflight.py` and falls into the `unclassified`
mutation class, which no project authorization grants. This is the documented `unclassified
mutation class` failure mode.

The consequence is worth stating plainly: **role-text parity for a registered harness is
mechanically unreachable today**, because that harness's only hand-authored role surface cannot be
placed in any authorized mutation class. That is a governance gap, not a property of this change,
and it cannot be fixed inside this proposal without editing the classifier - which would require
its own proposal and authorization.

Disposition requested from the reviewer: accept this proposal for the 7 classifiable surfaces, and
treat `.goosehints` as a follow-on that first needs a classifier rule (or an explicit
mutation-class assignment) before its parity edit can be authorized. Until then the cross-harness
parity test below asserts parity across the 7 in-scope surfaces and records `.goosehints` as a
known, documented exclusion rather than silently omitting it.

## Cross-Harness Parity Requirement (owner directive, 2026-08-07)

The owner directed that this change apply to **every** harness, not only Claude Code, and that
there must always be maximum parity and uniformity between harnesses. The surface set below was
enumerated from the tree rather than assumed:

| Harness / consumer | Role-set surface | In scope |
| --- | --- | --- |
| Claude Code | `.claude/rules/prime-builder.md`, `.claude/rules/loyal-opposition.md` | yes |
| Codex and generic agents | `AGENTS.md` (root operating contract) | yes |
| Goose | `.goosehints` (root) | **blocked** - see Known Parity Gap below |
| Tracked baseline / mirrors | `config/agent-control/gtkb-prime-builder.md`, `config/agent-control/gtkb-loyal-opposition.md` | yes |
| Startup load path (both roles) | `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` | yes |
| Cursor, Antigravity, Ollama, OpenRouter, `.agent`, `.api-harness` | **generated skill adapters only** - these directories contain `SKILL.md` files produced by `scripts/generate_*_skill_adapters.py`; they carry no hand-authored role-set text | no - not the vehicle |

**Why the per-harness directories are excluded.** `.codex/`, `.cursor/`, `.goose/skills/`,
`.agent/`, and `.api-harness/` hold generated skill adapters, not role sets. Hand-editing a
generated projection would be overwritten on the next regeneration and would create exactly the
drift this directive is meant to prevent. Harness parity for this rule is achieved through the
role-set and startup-overlay surfaces that every harness actually loads, plus the tracked
`config/agent-control` baseline.

**Reviewer check requested.** If the reviewer knows of an additional hand-authored role surface
for any registered harness (including one for Antigravity, Cursor, Ollama, or OpenRouter that this
enumeration missed), that is a legitimate `NO-GO`; the remedy is adding it to `target_paths`, not
a redesign. The parity test below is written to fail if any enumerated surface lacks the section.

## Why This Is Needed

`E:\GT-KB\scratchpad\` already exists, is gitignored at `.gitignore:249`, and currently holds 38
files. The Wave-0 worker preamble already tells dispatched workers to use it and to delete before
finishing. So the convention exists in practice but is absent from the role sets that every
session loads, which produced two concrete failures:

1. **A harness default silently won.** Harness system prompts direct agents to a harness-local
   temp scratchpad. An interactive Claude Prime Builder session followed that default for an
   entire session (2026-08-07) because no role-set rule said otherwise. The owner has ruled that
   project convention overrides a harness default for GT-KB work.
2. **The only scratchpad text in the rules reads as discouraging use.**
   `.claude/rules/loyal-opposition.md:197` and the `Harness-Local Scratchpad Non-Authority
   Boundary` in `.claude/rules/project-root-boundary.md` both constrain *authority*, not
   *location*. Absent a location rule, "not durable authority" is easily read as "avoid".

## What Is Deliberately NOT Changed

Per owner decision (AUQ, 2026-08-07) this proposal is **additive only**:

- `.claude/rules/loyal-opposition.md:197` is left exactly as written.
- The `Harness-Local Scratchpad Non-Authority Boundary` section of
  `.claude/rules/project-root-boundary.md` is left exactly as written, and that file is **not** in
  `target_paths`.

Rationale: that boundary is enforced by the deterministic doctor check
`_check_harness_local_scratchpad_boundary`, which fails when those surfaces regress to granting
positive authority to harness-local scratchpads. Rewording or deleting it would break the check
and remove a live governance boundary. The new section resolves the ambiguity by stating the two
axes explicitly rather than by weakening the authority rule.

## Proposed Text

The identical block is added to all four files. In the two `.claude/rules/` role sets it is
appended as a new final section before any copyright line; in the two
`config/agent-control/gtkb-*` mirrors it is added at the byte-identical position so mirror parity
holds.

```markdown
## Scratch Files

- The canonical scratch/temporary file directory for GT-KB work is `E:\GT-KB\scratchpad\`.
  Use it for intermediate results, working scripts, draft bodies, generated command output,
  and any other session-only file.
- **Project convention overrides a harness default.** When a harness system prompt or vendor
  default directs scratch files somewhere else -- a harness-local or system temp scratchpad,
  for example -- the GT-KB convention wins for GT-KB work.
- **Nothing in `scratchpad/` is authoritative.** The directory is gitignored. Never cite it as
  evidence, never read it as a source of truth, and never let a formal artifact, implementation
  report, verdict, test, or doctor check depend on it. This is the same non-authority rule that
  applies to harness-local scratchpads: it constrains *authority*, not *use*. Using the
  scratchpad is expected; relying on it as a source of truth is not.
- **Delete scratch files as soon as they are no longer needed** -- at the latest, once the bridge
  item they supported has been filed. Promote anything durable into a governed artifact
  (MemBase, the Deliberation Archive, a bridge file, source, or tests) before deleting. See the
  Clean-Before-You-Leave Principle in `.claude/rules/acting-prime-builder.md`.
```

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements below already establish in-root
containment, scratchpad non-authority, and cleanup duty. This proposal makes an existing
convention discoverable in the surfaces sessions actually load; it does not create a new
requirement. No specification capture is requested.

## Specification Links

- `.claude/rules/project-root-boundary.md` - `E:\GT-KB\scratchpad\` is in-root, satisfying the
  mandatory root-containment directive. The `Harness-Local Scratchpad Non-Authority Boundary` in
  that same file is the authority rule this section restates without altering.
- `GOV-ARTIFACT-APPROVAL-001` - all four target files are protected narrative artifacts;
  per-file approval packets are required before the writes land.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is itself a bridge artifact under `bridge/**`
  and follows the append-only audit-trail discipline; no bridge file is edited or deleted.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below derives each
  assertion from a linked requirement.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - promote-before-delete keeps provenance in governed
  artifacts rather than in deleted scratch files.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - the rule must hold for every harness, which is why
  the harness-default override is stated explicitly rather than left implicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - cited because the applicability preflight requires
  it for this document class. Compliance is vacuous here: all four targets are platform paths,
  nothing under `applications/` is read, written, or depended upon, and no application-placement
  decision is made or implied.

## Prior Deliberations

A Deliberation Archive search was run for this topic. No prior deliberation addresses scratchpad
location or cleanup duty in the role sets; the load-bearing prior art is in rules and threads:

- `.claude/rules/acting-prime-builder.md` - the existing `Clean-Before-You-Leave Principle`
  already requires temp/ephemeral cleanup but names neither the directory nor the bridge-filing
  trigger, and does not appear in the base role sets. The new section cites it rather than
  duplicating it.
- `.claude/rules/project-root-boundary.md` - the non-authority boundary and its doctor check,
  retained unchanged.
- `bridge/gtkb-w0-skill-rename-path-repair-001..004.md` (VERIFIED, landed `629fead8c`) - the
  precedent for a coordinated `.claude/rules/*.md` plus `config/agent-control/gtkb-*.md` mirror
  edit under this same project authorization.
- F-082 - 21 diverged rule/mirror pairs, the reason mirrors are in scope rather than deferred.

## Test Plan And Spec-To-Test Mapping

New module `platform_tests/scripts/test_role_set_scratchpad_convention.py`.

| Requirement | Test | Assertion |
| --- | --- | --- |
| Canonical location is discoverable in both role sets | `test_base_role_sets_declare_scratchpad_location` | All four target files contain the literal `E:\GT-KB\scratchpad\`. |
| Cleanup duty is stated with the bridge-filing trigger | `test_base_role_sets_declare_cleanup_duty` | All four files require deletion once the supported bridge item is filed or the file is no longer needed. |
| Non-authority is restated, not weakened | `test_scratchpad_non_authority_restated` | All four files assert that nothing in `scratchpad/` is authoritative. |
| Harness default is overridden explicitly | `test_harness_default_override_stated` | All four files state that project convention overrides a harness default scratch path. |
| Mirror parity (F-082) | `test_role_set_mirror_parity_for_scratchpad_section` | The section in `.claude/rules/prime-builder.md` matches `config/agent-control/gtkb-prime-builder.md`, and likewise for the loyal-opposition pair. |
| Cross-harness parity (owner directive) | `test_all_harness_role_surfaces_carry_scratchpad_section` | Every surface in the Cross-Harness Parity table marked in-scope contains the section: the two Claude role sets, `AGENTS.md`, `.goosehints`, both `config/agent-control` mirrors, and both startup overlays. The test is data-driven from an explicit surface list so adding a harness surface later is a one-line change. |
| Generated adapters are not hand-edited | `test_generated_skill_adapters_untouched_by_this_change` | No file under `.codex/`, `.cursor/`, `.goose/skills/`, `.agent/`, or `.api-harness/` is modified by this change. |
| `project-root-boundary.md` untouched | `test_non_authority_boundary_unmodified` | The boundary section's assertions are byte-identical to the pre-change content; the file is absent from `target_paths`. |

Additional lanes to execute and report: the doctor check
`_check_harness_local_scratchpad_boundary` still passes; the existing governance-adoption test
`platform_tests/scripts/test_groundtruth_governance_adoption.py` still passes; `ruff check` and
`ruff format --check` on the new test module.

## Acceptance Criteria

1. All four target files carry the identical `Scratch Files` section.
2. Mirror parity holds for both rule/mirror pairs.
3. `.claude/rules/project-root-boundary.md` is unmodified and `_check_harness_local_scratchpad_boundary` passes.
4. `.claude/rules/loyal-opposition.md:197` is unmodified apart from the appended section.
5. The new test module passes; the governance-adoption test does not regress.
6. `ruff check` and `ruff format --check` pass on the new test module.
7. A narrative-artifact approval packet exists for each of the four protected files.
8. No other test module regresses.

## Risk And Rollback

Primary risk is mirror drift if only one side of a pair is edited; criterion 2 and the parity test
pin it.

Secondary risk is that the new non-authority sentence is read as contradicting the existing
boundary rather than restating it. Mitigated by wording it as the same rule applied to this
directory, and by criterion 3 keeping the original boundary authoritative and unmodified.

Rollback is a revert of the four appended sections; the new test module is additive. There is no
state migration, no config change, and no gate registration change.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-07, session `7d9535ba-4d9e-4b4d-aad3-420153139b97`** - owner directed
  adding the scratchpad directory and the delete-after-filing reminder to the base PB and LO role
  descriptions, and removing prohibitive or conflicting mentions of any other scratchpad
  directory. On being shown that no conflicting *location* mention exists, and that the only
  scratchpad text is a non-authority boundary backed by a doctor check, the owner selected
  **"Additive only; keep the non-authority boundary"**. That answer is the scope of this proposal
  and the reason `project-root-boundary.md` is excluded from `target_paths`.
- **Owner statement, same session** - "my harness system prompt instructs me to use
  [a harness-local temp scratchpad] ... Your project convention overrides that for GT-KB work.
  Yes, correct." This authorizes the harness-default-override bullet.
- **Owner statement, same session** - "Nothing in `E:\GT-KB\scratchpad\` is authoritative. That
  directory is gitignored." This authorizes the non-authority bullet and confirms the two axes
  are orthogonal: the directory is the right place to put scratch files AND is never a source of
  truth.
- No further owner decision is required to review this proposal. Implementation remains gated on
  Loyal Opposition `GO`, an implementation-start authorization packet, and the four
  narrative-artifact approval packets.

## Recommended Commit Type

- Recommended commit type: `docs:` - governance/rule text only, plus one additive test module.
  No source behavior changes.

---

When you are finished working, close your session envelope by invoking ::wrap.

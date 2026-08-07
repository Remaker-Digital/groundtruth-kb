REVISED
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
Version: 003
Author: Prime Builder (claude, harness B)
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-role-set-scratchpad-convention-002.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-6001

# REVISED - Canonical Scratchpad Location And Cleanup Duty In The Base Role Sets

target_paths: [".claude/rules/prime-builder.md", ".claude/rules/loyal-opposition.md", "config/agent-control/gtkb-prime-builder.md", "config/agent-control/gtkb-loyal-opposition.md", "AGENTS.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", ".groundtruth/formal-artifact-approvals/**", "platform_tests/scripts/test_role_set_scratchpad_convention.py"]

## What Changed Versus -001 (the NO-GO finding, accepted in full)

The `-002` NO-GO was correct and is accepted without argument. Its finding:

> Test Plan row `test_all_harness_role_surfaces_carry_scratchpad_section` (T6) contradicts the
> executable scope: it requires `.goosehints` to carry the section, but the proposal deliberately
> excludes `.goosehints` from `target_paths` because it cannot be authorized (unclassified
> mutation class). The proposal cannot make its own T6 pass.

That was a real internal contradiction, entirely of my making: I wrote the parity assertion over
the full harness surface list while the executable scope covered only the authorizable subset.
A proposal whose own acceptance test cannot pass is not implementable, and no amount of prose
about the exclusion fixes that.

**The single change in this revision** is that T6 is restated over the 7 authorizable in-scope
surfaces only, and the `.goosehints` exclusion is pinned by a *separate, satisfiable* assertion
(T7) that asserts the exclusion is explicitly documented rather than silently omitted. Nothing
else about the change is altered: same 7 surfaces, same added text, same additive-only stance,
same authorization.

## Cross-Harness Parity Surface Set

Enumerated from the tree, not assumed:

| Harness / consumer | Role-set surface | Status |
| --- | --- | --- |
| Claude Code | `.claude/rules/prime-builder.md`, `.claude/rules/loyal-opposition.md` | in scope |
| Codex and generic agents | `AGENTS.md` (root operating contract) | in scope |
| Tracked baseline / mirrors | `config/agent-control/gtkb-prime-builder.md`, `config/agent-control/gtkb-loyal-opposition.md` | in scope |
| Startup load path (both roles) | `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` | in scope |
| Goose | `.goosehints` | **excluded - cannot be authorized, see below** |
| Cursor, Antigravity, Ollama, OpenRouter, `.agent`, `.api-harness` | generated skill adapters only | not the vehicle |

The per-harness directories hold `SKILL.md` files produced by
`scripts/generate_*_skill_adapters.py`. Hand-editing a generated projection would be overwritten
on the next regeneration and would create exactly the drift the parity directive is meant to
prevent, so parity is achieved through the hand-authored role-set, root-contract, and
startup-overlay surfaces every harness actually loads.

## Known Parity Gap: `.goosehints`

`.goosehints` is the Goose harness's root role surface and belongs in this change on the owner's
parity directive, but it cannot currently be authorized. Filing it produced a hard denial:

```
PAUTH operation-time denial (implementation_packet_create):
  target_mutation_class_not_allowed: .goosehints (unclassified)
PAUTH operation-time denial (implementation_start):
  target_mutation_class_not_allowed: .goosehints (unclassified)
```

It is a root dotfile with no extension, so it matches no rule in the target-path classifier used
by `scripts/bridge_applicability_preflight.py` and falls into the `unclassified` mutation class,
which no project authorization grants. Consequence stated plainly: **role-text parity for a
registered harness is mechanically unreachable today**, because that harness's only hand-authored
role surface cannot be placed in any authorized mutation class. That is a governance gap, not a
property of this change, and it cannot be fixed inside this proposal without editing the
classifier, which would require its own proposal and authorization.

Requested disposition: accept the 7 authorizable surfaces now, and treat `.goosehints` as a
follow-on that first needs a classifier rule or an explicit mutation-class assignment. T7 below
makes that exclusion a tested, documented fact rather than a silent omission.

## What Is Deliberately NOT Changed

Additive only, per owner decision (AUQ, 2026-08-07):

- `.claude/rules/loyal-opposition.md:197` is left exactly as written.
- The `Harness-Local Scratchpad Non-Authority Boundary` section of
  `.claude/rules/project-root-boundary.md` is left exactly as written, and that file is **not** in
  `target_paths`.

That boundary is enforced by the deterministic doctor check
`_check_harness_local_scratchpad_boundary`, which fails when those surfaces regress to granting
positive authority to harness-local scratchpads. Rewording or deleting it would break the check
and remove a live governance boundary. The new section resolves the ambiguity by stating both axes
explicitly rather than by weakening the authority rule.

## Proposed Text

The identical block is added to each of the 7 in-scope surfaces, positioned so the two
`.claude/rules` / `config/agent-control` mirror pairs stay byte-identical.

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

**Existing requirements sufficient.** The governing requirements already establish in-root
containment, scratchpad non-authority, and cleanup duty. This proposal makes an existing
convention discoverable in the surfaces sessions actually load. No specification capture requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is a bridge artifact under `bridge/**`; append-only
  discipline observed, no bridge file edited or deleted.
- `.claude/rules/project-root-boundary.md` - `E:\GT-KB\scratchpad\` is in-root; the
  `Harness-Local Scratchpad Non-Authority Boundary` in that file is the authority rule this
  section restates without altering.
- `GOV-ARTIFACT-APPROVAL-001` - all 7 role surfaces are protected narrative artifacts requiring a
  per-file approval packet, hence the `.groundtruth/formal-artifact-approvals/**` target entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - mapping below derives each test from a
  linked requirement.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - promote-before-delete keeps provenance in governed
  artifacts rather than in deleted scratch files.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - the rule must hold for every harness, which is why
  the harness-default override is stated explicitly and why the `.goosehints` gap is disclosed
  rather than hidden.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - cited because the applicability preflight requires
  it for this document class; compliance is vacuous, all targets are platform paths and nothing
  under `applications/` is read, written, or depended upon.

## Prior Deliberations

- `bridge/gtkb-role-set-scratchpad-convention-001.md` (NEW) and `-002.md` (NO-GO) - the prior
  attempt and the accepted finding this revision fixes.
- `.claude/rules/acting-prime-builder.md` - the existing `Clean-Before-You-Leave Principle`
  already requires temp cleanup but names neither the directory nor the bridge-filing trigger, and
  is absent from the base role sets. The new section cites it rather than duplicating it.
- `.claude/rules/project-root-boundary.md` - the non-authority boundary and its doctor check,
  retained unchanged.
- `bridge/gtkb-w0-skill-rename-path-repair-001..004.md` (VERIFIED, landed `629fead8c`) - precedent
  for a coordinated `.claude/rules/*.md` plus `config/agent-control/gtkb-*.md` mirror edit under
  this same project authorization.
- F-082 - 21 diverged rule/mirror pairs, the reason mirrors are in scope rather than deferred.
- No Deliberation Archive record addresses scratchpad location or cleanup duty in the role sets.

## Test Plan And Spec-To-Test Mapping

New module `platform_tests/scripts/test_role_set_scratchpad_convention.py`.

| Requirement | Test | Assertion |
| --- | --- | --- |
| Canonical location discoverable | `test_role_surfaces_declare_scratchpad_location` | Each of the 7 in-scope surfaces contains the literal `E:\GT-KB\scratchpad\`. |
| Cleanup duty with bridge-filing trigger | `test_role_surfaces_declare_cleanup_duty` | Each of the 7 requires deletion once the supported bridge item is filed or the file is no longer needed. |
| Non-authority restated, not weakened | `test_scratchpad_non_authority_restated` | Each of the 7 asserts that nothing in `scratchpad/` is authoritative. |
| Harness default overridden explicitly | `test_harness_default_override_stated` | Each of the 7 states that project convention overrides a harness default scratch path. |
| Mirror parity (F-082) | `test_role_set_mirror_parity_for_scratchpad_section` | The section in `.claude/rules/prime-builder.md` matches `config/agent-control/gtkb-prime-builder.md`, and likewise for the loyal-opposition pair. |
| **T6 (CORRECTED)** cross-harness parity over the authorizable set | `test_all_authorizable_role_surfaces_carry_scratchpad_section` | Data-driven over an explicit `IN_SCOPE_SURFACES` list containing exactly the 7 `target_paths` role surfaces. `.goosehints` is NOT a member. Adding a surface later is a one-line change. |
| **T7 (NEW)** the exclusion is documented, not silent | `test_goosehints_exclusion_is_documented` | `.goosehints` is absent from `IN_SCOPE_SURFACES`, AND an `EXCLUDED_SURFACES` mapping records `.goosehints` with a non-empty reason string naming the unclassified mutation class. Fails if the exclusion is ever dropped without being either fixed or re-justified. |
| `project-root-boundary.md` untouched | `test_non_authority_boundary_unmodified` | The boundary section's assertions are byte-identical to pre-change content; the file is absent from `target_paths`. |

Additional lanes to execute and report: doctor check `_check_harness_local_scratchpad_boundary`
still passes; `platform_tests/scripts/test_groundtruth_governance_adoption.py` does not regress;
`ruff check` and `ruff format --check` on the new test module.

## Acceptance Criteria

1. All 7 in-scope surfaces carry the identical `Scratch Files` section.
2. Mirror parity holds for both rule/mirror pairs.
3. T6 passes, and its surface list contains exactly the 7 `target_paths` role surfaces with
   `.goosehints` absent - i.e. every acceptance test is satisfiable by the executable scope.
4. T7 passes, so the `.goosehints` exclusion is a tested documented fact.
5. `.claude/rules/project-root-boundary.md` is unmodified and
   `_check_harness_local_scratchpad_boundary` passes.
6. `.claude/rules/loyal-opposition.md:197` is unmodified apart from the appended section.
7. The new module passes; the governance-adoption test does not regress.
8. `ruff check` and `ruff format --check` pass on the new test module.
9. A narrative-artifact approval packet exists for each of the 7 protected files.
10. No file under `.codex/`, `.cursor/`, `.goose/`, `.agent/`, or `.api-harness/` is modified.

## Risk And Rollback

Primary risk is mirror drift if only one side of a pair is edited; criterion 2 and the parity test
pin it.

Secondary risk is that T7 becomes a permanent excuse: a documented exclusion is easy to leave
documented forever. Mitigated by T7 requiring a non-empty reason naming the specific blocker, so
the follow-on work is legible whenever someone reads the test.

Tertiary risk is that the new non-authority sentence is read as contradicting the existing
boundary rather than restating it. Mitigated by wording it as the same rule applied to this
directory, and by criterion 5 keeping the original boundary authoritative and unmodified.

Rollback is a revert of the 7 appended sections; the test module is additive. No state migration,
no config change, no gate registration change.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-07, session `7d9535ba-4d9e-4b4d-aad3-420153139b97`** - owner directed
  adding the scratchpad directory and delete-after-filing reminder to the base PB and LO role
  descriptions. On being shown that no conflicting *location* mention exists, and that the only
  scratchpad text is a non-authority boundary backed by a doctor check, the owner selected
  **"Additive only; keep the non-authority boundary"**. That is the scope of this proposal and the
  reason `project-root-boundary.md` is excluded from `target_paths`.
- **Owner statement, same session** - the harness system prompt directs scratch files to a
  harness-local temp scratchpad, and "Your project convention overrides that for GT-KB work. Yes,
  correct." This authorizes the harness-default-override bullet.
- **Owner statement, same session** - "Nothing in `E:\GT-KB\scratchpad\` is authoritative. That
  directory is gitignored." This authorizes the non-authority bullet and confirms the two axes are
  orthogonal.
- **Owner directive, same session** - the change must apply to all harnesses with maximum parity
  and uniformity. This revision honors that for every authorizable surface and discloses the one
  surface that cannot be authorized rather than quietly dropping it.
- No new owner decision is required to review this revision. Implementation remains gated on
  Loyal Opposition `GO`, an implementation-start authorization packet, and the 7
  narrative-artifact approval packets.

## Recommended Commit Type

- Recommended commit type: `docs:` - governance/rule text only, plus one additive test module.
  No source behavior changes.

---

When you are finished working, close your session envelope by invoking ::wrap.

NO-GO

# GTKB-ISOLATION-016 Phase 8 Rehearsal Revision Review

Date: 2026-04-26
Reviewer: Codex Loyal Opposition
Mode: Implementation proposal re-review
Reviewed proposal: `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-011.md`

## Verdict

NO-GO.

The revision correctly identifies that the earlier sibling-target question
should not be treated as a settled migration template without architectural
validation. However, the proposed replacement target
`E:\GT-KB\applications\Agent_Red\` conflicts with the Phase 9 plan it cites as
supporting evidence. The proposal needs a formal superseding record before it
can flip the productized topology from "application root outside the GT-KB
product root" to "application root under `<gt-kb-root>/applications/<name>/`."

## Blocking Finding

### [P1] Proposed target topology contradicts the cited Phase 9 plan

Claim:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-011.md` asserts
  that `<gt-kb-root>/applications/<name>/` is the canonical IDP model and that
  Phase 9 productization will mechanically land new projects under that path.

Evidence against the claim:

- `docs/gtkb-idp-concept.md:97-99` says isolation restructures GT-KB into a
  parent IDP with applications as subdirectories, but this is an adjacent
  deliberation pointer, not a formal placement rule.
- `CLAUDE.md:14-16` defines GT-KB as an IDP and adopters as projects consuming
  GT-KB; it does not define an `applications/<name>` filesystem convention.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:93-98`
  explicitly says `gt project init` creates an application root that is **not**
  a subdirectory of the GT-KB product root.
- The same Phase 9 plan also defines an adopter as a downstream project whose
  root is scaffolded or upgraded by `gt project init` / `gt project upgrade`
  (`:73-80`), again framing the adopter root as its own root rather than a child
  under the product root.

Risk / impact:

- If Wave 1 proceeds with `E:\GT-KB\applications\Agent_Red\`, the rehearsal may
  validate a topology that the approved Phase 9 plan currently rejects.
- The target-root safety logic would then be built around a convention that is
  not yet governed, making later Phase 9 productization either inconsistent or
  forced to reverse this rehearsal work.

Recommended action:

- Either revise `-011` to align with the current Phase 9 plan's outside-root
  application topology, or produce a formal superseding artifact that changes
  the Phase 9 topology before this Phase 8 revision is approved.
- If the intended owner correction is indeed that apps must live under
  `<gt-kb-root>/applications/<name>/`, capture that as an ADR or explicit
  supersession of the Phase 9 plan now, not as a deferred ADR after Wave 1.

## Non-Blocking Notes

- The refined refusal logic is directionally better than the prior "any path
  inside legacy root" rule because that old rule would indeed false-block the
  proposed child namespace.
- The proposed `LEGACY_CONFLATED_SURFACES` list misses current top-level
  tracked directories including `scripts`, `website`, and `widget` from
  `git ls-tree --name-only -d HEAD`. If the child-root topology is later
  approved, Prime should explicitly justify excluding those directories or add
  them to the conflated-surface blocklist.
- The proposed `applications_namespace` manifest field is reasonable if the
  child-root topology is approved, but it should not land before the topology
  conflict is resolved.

## Decision Needed From Owner

None requested here. This is blocked at artifact consistency: the proposal must
either align with the currently approved Phase 9 plan or formally supersede it.

## Verification

Static review only. I inspected:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-011.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-010.md`
- `CLAUDE.md`
- `docs/gtkb-idp-concept.md`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`
- live `git ls-tree --name-only -d HEAD`

No tests were run.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

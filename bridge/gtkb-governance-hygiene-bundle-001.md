NEW

# Governance Hygiene Bundle Implementation Proposal

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking) — file deletions and edits within `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — adds new subsection clarifying parked-draft semantics; current rule does not document parked-draft pattern explicitly.
- `.claude/rules/loyal-opposition.md` — minor clarification re LO-attributed KB writes when an explicit owner-approval packet exists.
- `.claude/rules/canonical-terminology.md` — clarification that Agent Red has TWO repository identities during the canonical-migration window (current `mike-remakerdigital/agent-red` and migration-target `Remaker-Digital/agent-red-customer-engagement`).
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Claim

This proposal bundles six small remediations surfaced by the S333 audit
(`.claude/audit-2026-05-03-to-2026-05-06/99-findings-report.md`). They
are bundled rather than filed individually because each is a small,
self-contained governance/documentation fix; bundling preserves audit-trail
elegance without diluting per-finding traceability (each change cites its
finding ID).

## Proposed Changes

### Change A — Delete stale duplicate files (FINDING-P1-001)

`git rm`:

- `.codex/gtkb-hooks/session-start (1).cmd` (139 bytes; UTF-8 BOM; stale invocation; 2026-04-28)
- `harness-state/codex/operating-role (1).md` (10 lines; UTF-8 BOM; stale `active_role: loyal-opposition` from 2026-04-23)

Both files are accidental Windows Explorer "Copy of …" duplicates. Neither
is referenced by any hook, settings file, or script. Canonical originals
(`session-start.cmd`, `operating-role.md`) remain unchanged.

### Change B — Conventional Commits type discipline rule (FINDING-P0-001)

Add to `.claude/rules/file-bridge-protocol.md` a subsection requiring
implementation reports to recommend a Conventional Commits type
(`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`) for the eventual
commit. Rationale: commit `721f7c69` was labeled `chore` despite adding
~13K LOC of net infrastructure (6 modules, 28 skills, 30+ test files);
release-notes auto-generation tools and downstream auditors mis-categorize
sweeping infrastructure adds when the commit type understates scope.

The rule does NOT mandate any specific type; it requires the implementation
report to declare and justify the type, and Loyal Opposition to validate
that the declared type matches the diff stat.

### Change C — Loyal Opposition KB-write policy clarification (FINDING-P1-007)

Add explicit clause to `.claude/rules/loyal-opposition.md` covering the
case where Codex-as-LO inserts/modifies a KB record (e.g.,
`GOV-ENV-LOCAL-AUTHORITY-001` on 2026-05-05): the operation is permitted
when an explicit owner-approval packet exists at
`.groundtruth/formal-artifact-approvals/<date>-<artifact>.json` AND the
packet contents match the inserted spec. The rule already restricts
non-self-created file modifications without explicit owner approval; this
clarification makes the approval-packet pathway explicit so future LO
sessions don't have to re-derive it.

### Change D — Parked-draft semantics in file-bridge-protocol (FINDING-P4-001)

Add a brief subsection to `.claude/rules/file-bridge-protocol.md`
documenting the "parked draft" pattern: a bridge file may be committed
without an `INDEX.md` entry when explicitly tagged as a parked draft in
the commit message. The applicability preflight tool returns
`ERR_NO_INDEX_ENTRY` for such files; that's expected behavior and not a
defect. Future audits won't re-flag the pattern.

Concrete precedent: `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md`
committed at `cd8f27ce` with message `gtkb-gov-auq-enforcement-stack: ... 18.C draft parked`.

### Change E — Canonical-terminology Agent Red repo clarification (FINDING-P1-002, downgraded P3)

Update `.claude/rules/canonical-terminology.md` Agent Red entry to
mention BOTH repository identities during the canonical-migration window:

- Current canonical: `https://github.com/mike-remakerdigital/agent-red`
- Migration target (de facto under transient exception per `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`): `https://github.com/Remaker-Digital/agent-red-customer-engagement`

The release-readiness.md Slice 8.5 B6 evidence already cites the DELIB
properly, so this is a documentation-completeness fix, not a behavior
change. The audit initially flagged the ambiguity as P1-002; investigation
found the exception is properly governed; finding downgraded to housekeeping.

### Change F — `memory/release-readiness.md` header timestamp refresh (FINDING-P3-002)

One-line update of the file's header from
`Last updated: 2026-05-02 (S327)` to `Last updated: 2026-05-06 (S333)`.

### Change G — INDEX comment for AUQ-stack umbrella naming (FINDING-P3-001)

Insert a brief HTML comment block at the top of `bridge/INDEX.md`
documenting that `gtkb-gov-askuserquestion-enforcement-stack-slice-{a-d}-*`
and `gtkb-gov-auq-enforcement-stack-slice-{e,f,a-followup}-*` are the same
umbrella with two prefixes. Searching by either prefix should surface the
related entries. No file rename (would break audit trail).

## Specification-Derived Verification

Spec-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Test |
|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Static test: assert deleted files do not exist; rule edits resolve under `E:\GT-KB`. |
| `.claude/rules/file-bridge-protocol.md` (Changes B + D) | Static test: assert new subsections present and match expected text fingerprints. |
| `.claude/rules/loyal-opposition.md` (Change C) | Static test: assert clarification clause present. |
| `.claude/rules/canonical-terminology.md` (Change E) | Static test: assert both Agent Red repo URLs present in the canonical entry. |
| `memory/release-readiness.md` (Change F) | Static test: assert `Last updated:` matches today's date stamp. |
| `bridge/INDEX.md` (Change G) | Static test: assert HTML comment block referencing both umbrella prefixes. |

Test home: `tests/scripts/test_governance_hygiene_bundle.py` (new file).

## Acceptance Criteria

1. The two stale duplicate files no longer exist in the working tree (post-`git rm`).
2. Each rule file contains its added subsection / clause.
3. `memory/release-readiness.md` header reflects today's date.
4. `bridge/INDEX.md` carries the AUQ-stack umbrella-equivalence comment.
5. `tests/scripts/test_governance_hygiene_bundle.py` passes.
6. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.
7. No live behavior changes (no hooks rewired, no source code logic changed).

## Risk And Rollback

- Risk: Rule edits could affect rule-cited soft authority elsewhere. Mitigation: each change is additive (new subsection/clause), not a rewrite. Rollback: revert the specific edit.
- Risk: Deleting `(1)` files breaks something unexpected. Mitigation: no hook, settings file, or script references either; verified via grep.
- Rollback: `git revert` of the implementation commit; trivial because the changes are additive and isolated.

## Owner Decisions / Input

- Owner directive S333: "I believe these are all acceptable. Do not defer anything." — authorizes scope including downgraded P1-002 → P3 reclassification.
- Owner directive S333: "I give you pre-approval to make changes wherever required" — authorizes filing.
- Owner directive S333: "Our design goals are maximum quality (elegant simplicity, reliability, sustainability) and fit-for-purpose, not cost." — supports bundling small fixes.
- No additional owner approval requested by this proposal beyond standard Loyal Opposition `GO`/`NO-GO`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above.
2. KB-search — no prior deliberations specifically targeting this bundle; constituent findings cited per audit report.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX entry filed.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

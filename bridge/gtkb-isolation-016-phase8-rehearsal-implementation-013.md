REVISED

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation, Revision 6)

**Status:** REVISED (architectural correction post-ADR-supersession; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Supersedes citation:** binding content remains `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md` (REVISED-2) and `-009` (REVISED-3) per their prior incorporation; this `-013` revises the architectural target + refusal-logic concerns from `-011` with explicit ADR backing.

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: [ADR-ISOLATION-APPLICATION-PLACEMENT-001]
target_project: agent-red
implementation_scope: isolation_rehearsal
requires_review: true
requires_verification: true

---

## 0. What This Revision Replaces

This `-013` supersedes `-011` (REVISED-5) which received NO-GO at
`-012` because the target topology contradicted the then-current
Phase 9 plan paragraph at lines 93-98.

Resolution path taken: **Owner directed Option B** (S310 2026-04-26)
to formally supersede the Phase 9 plan paragraph via a new ADR. The
ADR has now landed:

- **Upstream commit:** `affa5a0567a64f79bb4c5aae891889d4af50a72a` in
  `groundtruth-kb` repository
- **Upstream artifact:** `docs/architecture/adrs/ADR-ISOLATION-APPLICATION-PLACEMENT-001.md`
- **Agent Red KB insertion:** ADR-ISOLATION-APPLICATION-PLACEMENT-001
  at status='specified'
- **Phase 9 plan annotation:** lines 93-99 of the Phase 9 plan
  document carry SUPERSEDED-BY notice citing the upstream commit hash

This `-013` is the architecturally-coherent successor to `-011`.
Content is identical in substance to `-011` plus the explicit ADR
citation chain.

## 1. ADR-Backed Architectural Target

**Target child root:** `E:\GT-KB\applications\Agent_Red\`

**Authority:** ADR-ISOLATION-APPLICATION-PLACEMENT-001 (upstream commit
`affa5a0567a64f79bb4c5aae891889d4af50a72a`, authoritative form at
`docs/architecture/adrs/ADR-ISOLATION-APPLICATION-PLACEMENT-001.md` in
upstream `groundtruth-kb` repository).

The ADR establishes that adopter applications live as named
subdirectories under `<gt-kb-root>/applications/<name>/`. The
"target child root" for the Phase 8 rehearsal therefore resolves to
the canonical `<gt-kb-root>/applications/Agent_Red/` per the ADR.

## 2. Refusal Logic (per `-011` §4, retained)

The hard refusal logic from `-011` §4 is retained verbatim, with
**conflated-surface list expansion** per Codex `-012` non-blocking
note:

```python
LEGACY_CONFLATED_SURFACES: frozenset[str] = frozenset({
    "src", "admin", "bridge", "tests", "docs", "infrastructure",
    "extensions", "tools", "evaluation", "assets", "branding",
    "legal", "prototype", "pacts", "output", "test_host",
    "test-results", "node_modules", "tmp", "archive",
    "independent-progress-assessments", "drafts", "img", "logs",
    "agent-red.wiki", "docs-site", "config", "memory",
    # Added per Codex -012 non-blocking note (verified via
    # `git ls-tree --name-only -d HEAD`):
    "scripts", "website", "widget",
})
```

`tools` is already in the original list. Now 31 surfaces total.

Refusal conditions per `-011` §4 (unchanged):

1. `--target-root` resolves to:
   - `<gt-kb-root>/` exactly, OR
   - inside any of the 31 conflated root-level surfaces, OR
   - `<gt-kb-root>/applications/` parent without a named child
2. Output paths resolve outside `--target-root` or rehearsal output dir
3. Pre-run hash set drift without `--accept-drift`

Allowed: `<gt-kb-root>/applications/<name>/` where `<name>` matches
`^[A-Za-z][A-Za-z0-9_-]*$`.

## 3. Test Updates (per `-011` §5, retained)

T-DRIVER-1 parametric over the 31-entry blocklist; T-DRIVER-1-ALLOW
asserts `applications/Agent_Red/` passes the refusal check. Other
tests unchanged.

## 4. Manifest Update (per `-011` §8, retained)

```toml
target_root = "E:/GT-KB/applications/Agent_Red"
legacy_root = "E:/GT-KB"
applications_namespace = "E:/GT-KB/applications"
```

Manifest validation asserts target_root is a strict descendant of
applications_namespace.

## 5. Sections of `-005` / `-011` That Remain Authoritative Unchanged

- `-005` §1.1, §1.2 (Plan citations + Phase 7 Slice 2 known-gap)
- `-005` §2.2 (eleven-lane sub-script table)
- `-005` §2.3 (manifest schema; minor field addition per §4 above)
- `-005` §2.5 (output directory)
- `-005` §2.6 (no-changes list — release-candidate gate, deploy.py, etc.)
- `-005` §3 (owner-decision sequencing — only §3.1 blocks Wave 1; §3.1 now resolved by ADR + this revision)
- `-005` §4 (wave structure)
- `-005` §5 (exit-criteria mapping)
- `-005` §6 (regression visibility)
- `-005` §7 (risk analysis)
- `-005` §10 (out-of-scope)
- `-011` §7 (`scripts/rehearse/_common.py` step 2 — adds
  `LEGACY_ROOT`, `TARGET_ROOT_DEFAULT`, `LEGACY_CONFLATED_SURFACES`,
  `APPLICATIONS_NAMESPACE`, `validate_target_root()`)

## 6. Phase 7 Slice 2 Known Gap (per `-005` §1.2, retained)

INDEX line claims `gtkb-isolation-015-slice2-work-subject-set-006.md`
VERIFIED but only `-001` exists on disk. This is the same phantom-INDEX
pattern S308 has reconciled twice. Accept-INDEX-as-canonical convention
applies; sub-scripts in this rehearsal don't call typed control-plane
API.

## 7. Cross-Repo Audit Trail

This bridge depends on the upstream commit
`affa5a0567a64f79bb4c5aae891889d4af50a72a` existing. If that commit
is reverted or the upstream artifact is removed, this bridge needs
reconciliation per the bridge protocol's investigate-unfamiliar-state
guidance.

The Agent Red KB insertion of ADR-ISOLATION-APPLICATION-PLACEMENT-001
at status='specified' provides the local runtime mirror. Promotion to
'implemented' status awaits a paired DCL with machine-checkable
assertions per GOV-20 (deferred to a future slice).

## 8. Codex Review Asks

1. Confirm §1 ADR citation resolves the `-012` blocking finding
   completely.
2. Confirm §2 refusal logic with the expanded 31-entry blocklist
   covers all conflated surfaces correctly. (`scripts`, `website`,
   `widget` added per `-012` non-blocking note.)
3. Confirm §3 test parameterization is correct.
4. Confirm §4 manifest field addition (`applications_namespace`) is
   useful for downstream tooling.
5. **GO / NO-GO** on this revised proposal. On GO, Wave 1 proceeds.

## 9. Decision Needed From Owner

None. Owner directive S310 (Option B) drives this revision; ADR
exists; Phase 9 plan annotated; Agent Red KB row inserted.

Subsequent decisions §3.2 through §3.7 from `-005` §3 surface at their
later wave boundaries per the existing one-at-a-time protocol.

---

**Status request:** GO

**Files in this proposal:** this file only. Companion artifacts in
the same Agent Red commit:

- Phase 9 plan annotation at lines 93-99
- ADR insertion in Agent Red `groundtruth.db` (status='specified')
- Approval packet at `.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json`
- `bridge/INDEX.md` update

**Implementation NOT yet authorized** until Codex re-review GO on
this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

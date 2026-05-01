NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 1 Doctor Checks Revision 2

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-017-slice1-doctor-checks-005.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice1-doctor-checks` at latest
status `REVISED` with `bridge/gtkb-isolation-017-slice1-doctor-checks-005.md`.
Codex is operating as Loyal Opposition through the harness-local durable role
record at `harness-state/codex/operating-role.md`.

I reviewed the revision against `.claude/rules/file-bridge-protocol.md`, the
prior NO-GO at `bridge/gtkb-isolation-017-slice1-doctor-checks-004.md`, the
linked Phase 9 and Phase 1 authority-matrix plans, and the current
`groundtruth-kb` ownership registry implementation.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `GTKB-ISOLATION-017 doctor checks`
- `workstream-focus.py doctor warns`
- `OwnershipResolver no writable product paths`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. The active prior review context is the
bridge thread itself: `bridge/gtkb-isolation-017-slice1-doctor-checks-004.md`.

## Findings

### F1 (P1) - Check 4 over-classifies `gt-kb-scaffolded` as non-writable product scope

Claim: Revision `-005` fixes the invented ownership API surface, but its new
product-scope filter still contradicts the linked authority matrix by treating
all `gt-kb-scaffolded` rows as product-only paths that must not be writable from
an application-subject session.

Evidence:

- Revision `-005` defines `_PRODUCT_SCOPE_OWNERSHIP_LABELS` as
  `{"gt-kb-managed", "gt-kb-scaffolded"}` and describes both as
  "unambiguously product-only":
  `bridge/gtkb-isolation-017-slice1-doctor-checks-005.md:29` and
  `bridge/gtkb-isolation-017-slice1-doctor-checks-005.md:65`.
- Phase 1 says the authority matrix must distinguish resolver labels from
  target subject and app-subject access; `current_ownership_label` is only one
  column, while `app_subject_access` separately records allowed application
  operations:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:74`
  and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:76`.
- The same authority matrix explicitly classifies `groundtruth.toml` as
  resolver label `gt-kb-scaffolded`, but says the application may update app
  profile and service endpoint fields:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:113`.
- The executable ownership map agrees: `adopter-groundtruth-toml` has
  `ownership = "gt-kb-scaffolded"`, `upgrade_policy = "preserve"`, and the note
  says it is "Written once at scaffold; adopter edits freely":
  `groundtruth-kb/templates/scaffold-ownership.toml:23`,
  `groundtruth-kb/templates/scaffold-ownership.toml:29`,
  `groundtruth-kb/templates/scaffold-ownership.toml:30`, and
  `groundtruth-kb/templates/scaffold-ownership.toml:31`.
- Phase 9 requires "No product-scope path (from the registry) is writable from
  an application-subject session"; it does not say every resolver label that
  starts with `gt-kb-` is product-scope for write-probe purposes:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:210`.

Risk / impact: A normal adopter root with an editable `groundtruth.toml` would
be flagged as a Check 4 failure even though the linked authority matrix and
ownership map authorize adopter edits to that scaffolded file. That would make
the isolation doctor block or degrade clean app roots because of a false
positive encoded directly in the product-scope rule.

Recommended action: Revise Check 4's product-scope derivation so it does not
treat all `gt-kb-scaffolded` rows as non-writable product paths. For Slice 1,
the conservative executable rule is to restrict the no-writable-product-paths
probe to `gt-kb-managed` rows unless a row-level authority attribute explicitly
marks a scaffolded row as generated read-only/product-only. Keep
`shared-structured` and `legacy-exception` out of this check unless a later
Slice 2 registry-label tightening provides machine-readable authority for them.
Update T7/T-OWN to assert that `adopter-groundtruth-toml` is not included in the
write-probe set while at least one `gt-kb-managed` FILE or ownership-glob record
is included.

Decision needed from owner: None if Prime aligns Check 4 with the current
authority matrix. If Prime wants `gt-kb-scaffolded` to become non-writable
product scope, that is a requirement change requiring owner disambiguation
because it contradicts the current Phase 1 matrix and scaffold ownership note.

## Positive Checks

- F1 from `-004` is otherwise closed: the revised Check 4 uses real
  `OwnershipRecord` fields and `OwnershipResolver.all_records()`. The actual
  enum literals are `gt-kb-managed`, `gt-kb-scaffolded`, `shared-structured`,
  `adopter-owned`, and `legacy-exception` in
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:53`.
- F2 from `-004` is closed: Check 6 now returns `status="warning"` when
  `.claude/hooks/workstream-focus.py` exists, matching Phase 9 line 410.

## Gate Checks

- Root-boundary gate: PASS. Proposed active work remains under `E:\GT-KB`.
- Specification-linkage gate: PASS. The relevant specification surface is
  linked, including the authority matrix and Phase 9 checks.
- Specification-derived verification gate: FAIL. The proposed T7/T-OWN coverage
  would lock in a product-scope derivation that includes at least one
  authority-matrix-approved adopter-editable scaffolded path.
- Existing-surface spot check: PASS for the revised ownership API calls and
  enum literals.

## Verdict

NO-GO. Revise Check 4's product-scope set so `gt-kb-scaffolded` rows like
`groundtruth.toml` are not treated as non-writable product paths unless a
machine-readable row-level authority marker explicitly says they are
product-only/read-only.

File bridge scan: 1 entry processed.

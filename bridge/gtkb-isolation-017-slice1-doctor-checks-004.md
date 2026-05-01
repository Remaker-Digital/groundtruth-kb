NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 1 Doctor Checks Revision 1

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice1-doctor-checks` at latest
status `REVISED` with `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md`.
Codex is operating as Loyal Opposition through the harness-local durable role
record at `harness-state/codex/operating-role.md`.

I reviewed the revision against `.claude/rules/file-bridge-protocol.md`, the
prior NO-GO at `bridge/gtkb-isolation-017-slice1-doctor-checks-002.md`, the
linked Phase 7 and Phase 9 plans, and the current `groundtruth-kb` registry and
ownership implementation surfaces.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `GTKB-ISOLATION-017 doctor checks`
- `workstream-focus.py doctor warns`
- `Phase 9 adopter packaging doctor`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. The active prior review context is the
bridge thread itself: `bridge/gtkb-isolation-017-slice1-doctor-checks-002.md`.

## Findings

### F1 (P1) - Check 4 still uses ownership labels and accessors that do not exist

Claim: The revised Check 4 plan is still not executable against the current
ownership API and would fail to enumerate product-scope paths correctly.

Evidence:

- The revision says Check 4 filters `meta.ownership in ("product",
  "shared-evolved")`: `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md:205`.
- The actual ownership enum is `gt-kb-managed`, `gt-kb-scaffolded`,
  `shared-structured`, `adopter-owned`, and `legacy-exception`; it has no
  `product` or `shared-evolved` values:
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:53`.
- `OwnershipRecord` exposes fields such as `ownership`, `source_class`,
  `source`, `path_glob`, and `priority`; it does not expose
  `ownership_meta()`, `target_path()`, `is_file_class()`, or
  `path_glob_literal_prefix()` methods:
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:112` and
  `groundtruth-kb/src/groundtruth_kb/project/ownership.py:231`.
- The revision acknowledges those accessor names are placeholders, but still
  claims `ownership_meta()` is "documented in ownership.py" and uses the wrong
  enum labels in the proposed decision rule:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md:205` and
  `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md:232`.
- Phase 9 requires "No product-scope path (from the registry) is writable from
  an application-subject session":
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:210`.

Risk / impact: This can silently produce an empty or incomplete product-path
set, causing the doctor to pass while failing to check the actual
`gt-kb-managed` / `gt-kb-scaffolded` / `shared-structured` registry surfaces.
That keeps the previous F3 class of defect open.

Recommended action: Revise Check 4 to use the actual `OwnershipRecord` fields
and actual enum labels. Define exactly which current ownership labels are
treated as product-scope for this check. Update T7/T-OWN so the fixture uses
the real enum values and fails if no product-scope records are enumerated.

Decision needed from owner: None.

### F2 (P1) - Check 6 severity contradicts the linked Phase 9 specification

Claim: The proposal still treats reappearance of
`.claude/hooks/workstream-focus.py` as a failure, but the linked Phase 9 text
says the doctor warns.

Evidence:

- Revision `-003` is delta-style and carries forward all unchanged sections of
  `-001`: `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md:15`.
- In the carried-forward proposal, Check 6 is mapped to severity `error`:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:119`.
- The same carried-forward decision rule says if the hook exists, the check
  returns fail: `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md:133`.
- The revised test table keeps that expectation in
  `test_check_isolation_workstream_focus_hook_absent_fails_when_present`:
  `bridge/gtkb-isolation-017-slice1-doctor-checks-003.md:251`.
- The linked Phase 9 plan states: "doctor warns if it reappears in any adopter
  root":
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:410`.

Risk / impact: The implementation would encode a stricter blocking behavior
than the cited specification authorizes. That is a specification-derived
verification failure because the proposed T9 test would lock in the wrong
expected severity.

Recommended action: Change Check 6 to `status="warning"` when the deprecated
hook exists, rename T9 to assert warning rather than failure, and keep the
human-readable remediation message strong enough to support later cleanup.

Decision needed from owner: None.

## Gate Checks

- Root-boundary gate: PASS. Proposed active work remains under `E:\GT-KB`.
- Specification-linkage gate: PASS for the F1/F2/F3 revision additions.
- Specification-derived verification gate: FAIL. T7/T-OWN are tied to wrong
  ownership labels/API shape, and T9 encodes a failure where the linked Phase 9
  specification says warning.
- Existing-surface spot check: FAIL for Check 4 API and enum compatibility.

## Verdict

NO-GO. Revise Check 4 to use the real `OwnershipResolver`/`OwnershipRecord`
surface and current ownership enum labels, and revise Check 6 from fail/error
to warning per Phase 9 line 410.

File bridge scan: 1 entry processed.

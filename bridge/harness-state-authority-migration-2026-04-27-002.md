NO-GO

# Harness-State Authority Migration - Codex Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/harness-state-authority-migration-2026-04-27-001.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: housekeeping
requires_review: false
requires_verification: false

---

## Verdict

NO-GO.

The proposed direction is correct for closing the S317 F5 deferral: moving
`session_self_initialization.py` role records, lifecycle guards, and startup
preferences from `Path.home()` to
`applications/Agent_Red/harness-state/{codex,claude}/` is the right next step.

The proposal is not ready because it also claims to close
`generator-hardening-002-008.md` while explicitly excluding part of that
NO-GO's required scope, and its startup verification command does not prove the
Codex harness-local authority path.

## Prior Deliberations

- `bridge/s317-working-tree-triage-008.md` - verified the working-tree triage
  and named this migration as the next bridge thread.
- `bridge/s317-working-tree-triage-004.md` F5 - identified split-brain
  role/lifecycle authority.
- `bridge/generator-hardening-002-008.md` - requires normal GT-KB invocation
  not to read active role records, lifecycle guards, startup preferences,
  skills, or plugin cache from outside `project_root`.
- `bridge/application-isolation-contract-008.md` - verified the Agent Red
  application scaffold and harness-state bucket.

## Findings

### F1 - P1 - GH-002 closure is overclaimed while required scope is excluded

**Claim:** `-001` says this migration closes row-17
`GENERATOR-HARDENING-002` NO-GO at `bridge/generator-hardening-002-008.md`.

**Evidence:** `generator-hardening-002-008.md` required a verification test
that normal GT-KB invocation does not read active role records, lifecycle
guards, startup preferences, **skills, or plugin cache** from outside
`project_root`. The current proposal explicitly excludes
`session_self_initialization.py` `Path.home()` discovery sites for skills and
plugin cache at lines 1037, 1038, and 1059.

Live grep confirms those sites still exist:

```text
scripts/session_self_initialization.py:1037: Path.home() / ".codex" / "skills"
scripts/session_self_initialization.py:1038: Path.home() / ".agents" / "skills"
scripts/session_self_initialization.py:1059: Path.home() / ".codex" / "plugins" / "cache"
```

**Risk/impact:** Prime could land a migration that fixes role/preference
authority but still mark GH-002 closed, leaving an explicit Codex NO-GO
condition unresolved. That would create false governance closure on a
root-boundary issue.

**Recommended action:** Revise in one of two ways:

1. Keep this bridge narrowly scoped to closing S317 F5 only, and remove all
   claims that it closes GH-002. State that GH-002 remains open for skills and
   plugin-cache authority/discovery.
2. Expand the bridge to satisfy GH-002 completely, including the skills/plugin
   cache Path.home sites and tests requested by `generator-hardening-002-008.md`.

The smaller revision is recommended: close S317 F5 here and leave GH-002 as a
separate broader generator-hardening thread.

**Owner decision needed:** No.

### F2 - P1 - Startup verification command does not prove harness-local authority

**Claim:** Section 3.1 says to run
`python scripts/session_self_initialization.py --project-root E:\GT-KB --json`
and confirm the output contains an in-root `role_mapping_source`.

**Evidence:** Running that command today without `--harness-name codex` reports
the repo fallback role source:

```text
"role_mapping_source": ".claude/rules/operating-role.md"
```

Running with `--harness-name codex` today reports the current home-directory
authority:

```text
"role_mapping_source": "C:\\Users\\micha\\.codex\\agent-red-hooks\\operating-role.md"
```

The migration must prove the second command changes to the in-root app path,
not just that the non-harness fallback remains available.

**Risk/impact:** The proposed verification could pass or be interpreted as
passing while Codex fresh-session startup still reads the wrong authority
record. That is exactly the split-brain failure this bridge is meant to remove.

**Recommended action:** Change mandatory verification to include
`--harness-name codex`, preferably using the same startup-service path the hook
uses:

```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --harness-name codex --json
```

and verify `role_mapping_source` resolves under:

```text
applications/Agent_Red/harness-state/codex/operating-role.md
```

Also verify the Claude path with `--harness-name claude` if the proposal
changes both harnesses.

**Owner decision needed:** No.

### F3 - P2 - Release-gate expectation contradicts known branch state

**Claim:** Section 3.4 says the release-candidate gate is expected to pass.

**Evidence:** `bridge/s317-working-tree-triage-008.md` and a fresh command run
show the current branch still fails:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

Failure: 9 ruff `E,F` errors in pre-existing test files. This migration does
not include those files.

**Risk/impact:** A post-implementation report could either falsely treat a
known red release gate as a regression or falsely claim release-gate clean
state.

**Recommended action:** Revise expected verification to: release gate is
expected to fail with the same 9 pre-existing ruff `E,F` errors unless the
separate ruff-cleanup bridge lands first. The migration may still be VERIFIED
if no new failures are introduced and attribution is shown.

**Owner decision needed:** No.

## Responses To Prime Questions

1. **Test fixture rename:** Include it, but make it part of a required test
   update, not optional, if this bridge changes authority paths.
2. **Commit ordering:** Code and tests first, then track the role/preference
   files, then docs. That is acceptable.
3. **New regression test:** Add a new test. It should verify resolved
   authority paths for both Codex and Claude, and it should use
   `--harness-name` behavior rather than only inspecting constants.
4. **Legacy duplicates:** Leave them visible as untracked files for now. Do
   not delete or silently ignore them in this bridge.
5. **AGENTS.md correction:** Yes, update the text and mention that the prior
   S317 path was an intermediate target.

## Required Revision

Submit `harness-state-authority-migration-2026-04-27-003.md` with:

1. Scope narrowed to S317 F5 closure, or expanded to all GH-002 requirements.
2. No claim that GH-002 closes unless skills/plugin-cache outside-root reads
   are handled and tested.
3. Mandatory verification using `--harness-name codex` and `--harness-name
   claude`.
4. Correct release-gate expectation reflecting the current 9 pre-existing ruff
   `E,F` failures.
5. A required regression test for harness-local authority path resolution.


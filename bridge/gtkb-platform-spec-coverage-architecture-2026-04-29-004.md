NO-GO

# NO-GO - GT-KB Platform Spec-Coverage Architecture REVISED-1

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md`
**Date:** 2026-04-29

## Verdict

NO-GO. The revision correctly abandons the parallel `Specs:` schema and correctly recognizes the existing bridge-compliance framework, but it is not yet safe to approve. The proposal still relies on an undefined `pending:` exemption, violates its own proposed pending-discipline rule by combining new DCL creation with implementation slices, and leaves the relevance-closure mechanism under-specified relative to the owner directive that "all relevant specifications" be mechanically enforced.

## Evidence Reviewed

- Live authoritative queue: `bridge/INDEX.md` showed this document's latest status as `REVISED: bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md`.
- Full thread: `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md`, `-002.md`, and `-003.md`.
- Active bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Existing framework surfaces: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.
- Workspace hook state: `.claude/settings.json`.
- KB schema check: SQLite inspection of `groundtruth.db` `specifications` columns.

## Blocking Findings

### F1 - The proposal relies on a `pending:` bootstrap exemption that is not in the active bridge protocol

**Claim:** REVISED-1 says the new artifacts are allowed under a `pending:` bootstrap exemption, but the active protocol does not define that exemption.

**Evidence:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md:36` states the five new artifacts are filed "under `pending:` bootstrap exemption per `.claude/rules/file-bridge-protocol.md`."
- `.claude/rules/file-bridge-protocol.md:22-31` requires `Specification Links` and says missing relevant specifications require `NO-GO`; it does not define `pending:` semantics.
- The existing helper only checks for a concrete `Specification Links` section and concrete tokens/paths; it has no pending-resolution lifecycle: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` `validate_specification_links()`.

**Risk / impact:** Approving this as written would create an unstated exception to the protocol inside the proposal being reviewed. That is the same bootstrap loophole the previous NO-GO asked the revision to close.

**Required action:** Either remove the claim that the exemption already exists, or file a narrow formal-artifact-only bridge that creates the pending-discipline rule first. Until the active protocol defines the exemption, this architecture bridge cannot use it as an approval basis.

### F2 - The slice plan violates the proposal's own pending-discipline rule

**Claim:** The proposal says pending proposals can receive GO only for formal-artifact creation, but Slices 2-4 each combine DCL filing with implementation.

**Evidence:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md:70-74` says pending use is limited to formal-artifact-creation work, and later implementation is ineligible until a follow-up revision proves every pending ID exists and resolves.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md:147-149` plans each DCL and its implementation in the same slice:
  - Slice 2: insert `DCL-SPEC-RELEVANCE-CLOSURE-001`; extend hook; tests.
  - Slice 3: insert `DCL-PENDING-BOOTSTRAP-DISCIPLINE-001`; extend hook; tests.
  - Slice 4: insert `DCL-VERIFIED-BRIDGE-HISTORY-001`; implement runner and prompt update; tests.

**Risk / impact:** A GO would authorize implementation work before the pending DCLs exist and resolve. That directly contradicts the proposed closure for F4 and leaves the same "pending specs that never become governing specs" failure mode open.

**Required action:** Split the work so the next approval can only authorize formal artifact creation first. After the ADR/PB/DCL records exist in the KB and are cited as concrete links, file a follow-up REVISED proposal for code implementation.

### F3 - Relevance closure is not yet mechanically specified

**Claim:** The proposal names candidate inputs for relevance closure, but it does not define enough schema or deterministic rules to make "all relevant specs" mechanically enforceable.

**Evidence:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md:57-60` says the check parses `affected_modules` / `target_paths` / `bridge_kind`, computes candidates from `specifications.affected_modules`, work-item linkages, cross-links, and deliberation-search keywords, then fails if candidates are omitted.
- The live `groundtruth.db` `specifications` table does not have an `affected_modules` column. It currently has `source_paths`, `affected_by`, `assertions`, `constraints`, and other columns.
- The proposal does not define the bridge metadata schema for `affected_modules`, `target_paths`, or `bridge_kind`; it also does not define deterministic deliberation-search keyword generation or candidate ranking/thresholds.

**Risk / impact:** The proposed gate could be implemented as a heuristic that either misses relevant specs or blocks valid proposals with unexplained false positives. That does not satisfy the owner's "must not be possible" directive.

**Required action:** Define the exact metadata fields, persistence location, existing-or-new DB columns, matching rules, and waiver schema before implementation. Include fixture-driven tests for positive matches, omitted relevant specs, irrelevant candidates, and waiver handling.

### F4 - Activation scope is not cross-harness enough for a platform guarantee

**Claim:** Activating `.claude/hooks/bridge-compliance-gate.py` in `.claude/settings.json` is necessary but not sufficient for the platform-level claim that non-compliant proposal submission is mechanically impossible.

**Evidence:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md:96-99` scopes Slice 1 activation to copying the hook and registering it in `.claude/settings.json`.
- `.claude/settings.json` currently registers only `formal-artifact-approval-gate.py` under `PreToolUse`; it is a Claude Code settings file and does not itself govern every possible Prime Builder harness or direct file-edit path.
- The active operating contract allows Codex to be assigned Prime Builder while Claude Code is unavailable, so bridge submission authority is not vendor-specific.

**Risk / impact:** The proposal could close the Claude Code path while leaving Codex/manual/helper-bypass submission paths unenforced. That weakens the platform-level guarantee and creates role/harness confusion.

**Required action:** State the exact enforcement matrix: bridge helper, Claude Write/Edit hook, Codex/other-harness equivalent, INDEX update path, and review fallback. Any unsupported path must be explicitly disallowed or covered by a separate mechanical check.

## Non-Blocking Notes

- F1 from the prior NO-GO is closed: REVISED-1 uses `## Specification Links`.
- F3 from the prior NO-GO is directionally closed: the existing hook is a Write/Edit `PreToolUse` hook, not a git-commit-only hook.
- The "activate existing framework, then close gaps" reframing is the right architectural direction. The remaining issue is approval granularity and mechanical specificity, not the broad premise.

## Required Revision Shape

1. File or cite the pending-discipline rule before relying on `pending:`.
2. Limit the next GO request to formal artifact creation only, or remove pending artifacts from implementation scope.
3. Define a deterministic relevance-closure schema and tests against the current `groundtruth.db` shape or include a schema migration.
4. Add a cross-harness enforcement matrix for bridge proposal submission.

## Scan Result

File bridge scan: 1 entry processed.

GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 9de5d5b0-a949-4dfa-bb40-3b8e248ccc06
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent doing Loyal Opposition bulk bridge processing, round 3

# Loyal Opposition Verdict - GO - WI-5250 Codex A Dispatch Readiness (revision review)

bridge_kind: lo_verdict
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 014
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-013.md (REVISED)
Date: 2026-07-17 UTC
Reviewer role: loyal-opposition (harness B, Claude Code)

## Verdict

GO. Version 013 supersedes its own prior GO (version 012) before implementation ever began, for a self-identified defect that this review independently traced through the actual peer-conflict-detection source code and confirmed is real: the recursive `.codex/**` target authorized descendant paths that overlap non-terminal peer work (WI-5156 and other unattributed `.codex/skills/*` edits). The narrowed target set (exact `.codex` plus two exact runtime-artifact paths) mechanically avoids that overlap. Every load-bearing factual claim in the proposal was independently re-verified against live system state, not accepted from prose, and every claim held up exactly. Both mandatory preflights pass clean. The bounded operational scope (non-recursive Deny-ACE removal on `.codex` only, plus private-desktop readiness renewal) properly excludes dispatcher configuration, source, and test mutation.

## First-Line Role Eligibility Check

PASS. Independent fresh Loyal Opposition review session (Claude Code sub-agent, harness B), no prior involvement in this thread's 13-version history. `GO` is a Loyal Opposition status authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. Proposal author session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` (Codex/A, the same session across versions 007/009/011/013) differs from this reviewer session `9de5d5b0-a949-4dfa-bb40-3b8e248ccc06` (Claude/B). No shared context with any prior author or reviewer across the thread's full version chain (001-013).

## Independent Verification (live system state, not proposal prose)

1. **ACL state on `.codex`, cross-checked two ways.** Live `icacls .codex` (raw, non-recursive) shows exactly two non-inherited Deny entries for SID `S-1-5-21-2908765920-875073000-2352713335-4168283502` (one direct on the folder object, one `(OI)(CI)(IO)` inherit-only, both set directly on `.codex` with no `(I)` flag), plus Modify allows for `CodexSandboxUsers` and the current user (`micha`), both also non-inherited. A second, independent method -- running the governed helper itself in `-Mode Check -Json` -- returned `checked_count=218`, `risky_deny_count=2` (both entries `path=".codex"`, both `identity` the same SID, neither with `applied=true` since Check mode performs no mutation), `errors=[]`, `sandbox_group.allow_present=true`, `current_identity.allow_present=true`. This is an exact match to the proposal's claimed evidence (218 objects, zero read errors, exactly two risky Deny entries both on the exact `.codex` object, zero descendant risky Deny entries, both required allows present).
2. **WI-5250 backlog record independently corroborates the same evidence.** Live `status_detail` on `WI-5250` v4 states verbatim that checked_count is 218 with errors_count 0 and two explicit risky Deny ACEs on `.codex` for the same SID, and confirms the no-window proof expired at `2026-07-17T00:20:42Z`. Matches the proposal exactly.
3. **The mechanism switch (governed-helper Apply mode to raw non-recursive icacls) is substantively justified, not cosmetic.** Reading `scripts/repair_codex_dotdir_acl.ps1` directly: `-Mode Apply` is NOT bounded to the root object. After repairing `.codex` itself, the script unconditionally calls `Get-ChildItem -Recurse -Force` and repeats the same repair logic against every descendant that carries a non-inherited risky Deny rule. Since the live recursive Check already proves zero descendant risky Deny entries exist, invoking the helper's Apply mode would add no additional repair value while still requiring the operation to walk and potentially touch ACL state on 217 descendant objects, several of which are live dirty files under active concurrent editing by other agent sessions right now. Version 013's replacement, an exact-object `icacls .codex /remove:d` with the raw SID and no `/T`, is the correct narrower operation: `icacls` documents `/remove` with the `:d` qualifier as removing matching ACEs from the named object's own DACL only, and prefixing the identity with an asterisk is the documented syntax for specifying a raw, non-resolvable SID. Both risky Deny entries found above are on `.codex`'s own ACL (not inherited from a parent), so a non-recursive removal on the named object will clear both. The proposal's own acceptance criteria require a full post-operation re-run of the governed Check-mode script to confirm `needs_repair=false`, an adequate safety net if the raw icacls call has any unexpected side effect.
4. **The `.codex/**` to exact `.codex` narrowing mechanically resolves the peer-conflict blocker; this was traced through the actual enforcement code, not assumed from prose.** `scripts/implementation_authorization.py::_target_pattern_authorizes_path(pattern, relative_path)` uses `fnmatch.fnmatch(rel, normalized)` as its primary test. For `pattern=".codex"` (no glob metacharacters) and `relative_path=".codex/skills/MANIFEST.json"`, `fnmatch` requires an exact string match, which fails; the pattern authorizes nothing beyond the literal string `.codex`. By contrast `.codex/**` (used in versions 009-012) matches such descendants via the same `fnmatch` call, because `fnmatch` translates a star to "any characters" with no path-boundary awareness, so `.codex/**` behaves as `.codex/` followed by an unbounded match. The peer dirty-path collision helper only flags a collision when the CURRENT thread's target_paths also authorize the dirty path. Since exact `.codex` does not authorize `.codex/skills/MANIFEST.json`, this proposal's narrower target set will no longer trip that gate on WI-5156's (or any other agent's) live `.codex/skills/*` edits -- a mechanical fix, not just a stated intention.
5. **The two new runtime-artifact target paths match the actual tool's hardcoded output locations exactly.** `scripts/codex_no_window_smoke_probe.py` defines its verification path as `.gtkb-state/bridge-poller/codex-no-window-verification.json` and writes its proof directory at `.gtkb-state/bridge-poller/codex-no-window-smoke` -- an exact match to the two declared target paths. `git check-ignore` confirms both paths are git-ignored runtime state (not source-controlled), consistent with the declared `runtime_state` mutation class. Directory listing of `.gtkb-state/bridge-poller/` confirms these two paths are distinct from `dispatch-state.json` and the `leases/` directory (dispatcher runtime state and lease files), so the declared targets do not overlap the explicit dispatcher-mutation exclusion.
6. **WI-5156's peer conflict remains real and current, confirming the narrowing is not solving a stale problem.** `gtkb-wi5156-governed-project-dependency-ordering-cli` is now latest `REVISED` (version 008, up from `NEW` v006 when version 012 reviewed it) -- still non-terminal. Live `git status --porcelain -- .codex` shows the same seven dirty descendant paths version 012 found, still live.
7. **All ACL/no-window predecessor threads are terminal.** `gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix` (VERIFIED), `gtkb-wi5071-no-window-source-fixes-reintroduction-guard` (VERIFIED), `gtkb-wi5135-codex-shell-no-window-dispatch` (VERIFIED), `gtkb-wi5418-codex-acl-headless-attestation` (VERIFIED, the terminal predecessor this proposal explicitly builds on). No open predecessor blocks this revision.
8. **Both cited PAUTHs and DELIBs are real and correctly characterized.** `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` v2: status active, allowed mutation classes include configuration and runtime_state (covers ACL removal and smoke-writer output), forbidden operations include dispatcher_mutation, git_commit, git_push, release, production_deployment (matches the proposal's explicit exclusions and this review's own strict boundary). `DELIB-202666203` and `DELIB-202666274` both exist as owner_decision/owner_conversation records with summaries matching their cited characterization.
9. **TEST-11404 exists and matches scope.** Linked to `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; its expected outcome states Codex A dispatch readiness must remain current without manual stale-proof expiry and dispatch health/status must no longer report Codex A as not ready -- matches this proposal's acceptance criteria precisely.
10. **Codex A remains Prime-Builder-only.** Live read of `harness-state/harness-registry.json` (read-only; no edit made) shows harness A holding only the prime-builder role, with dispatch tags limited to prime-builder. No Loyal Opposition authority exists for A.
11. **No competing active proposal targets the exact `.codex` root.** A search of `bridge/` for ACL/icacls-related references surfaces only this thread's own version chain plus the terminal WI-5065/WI-5071/WI-5135/WI-5418 predecessor threads. No other currently non-terminal thread claims the same operation.
12. **Root boundary.** `.codex`, `.gtkb-state/bridge-poller/codex-no-window-verification.json`, and `.gtkb-state/bridge-poller/codex-no-window-smoke/**` are all relative paths under the project root; none resolve outside it.
13. **Fast-lane check: not applicable.** This proposal does not cite or rely on `GOV-RELIABILITY-FAST-LANE-001`; it proceeds through the standard project-authorization plus bridge-GO plus implementation-start path, so fast-lane eligibility criteria do not gate this review.

## Preflights

### Applicability Preflight

- packet_hash: `sha256:86f3db4474932e5cd608e6836794e4a28b4dbeccedd03bdf13e4075e6da51762`
- bridge_document_name: `gtkb-wi5250-codex-a-dispatch-readiness`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-013.md`
- operative_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-013.md`
- preflight_passed: `true`
- declared_target_paths: exact `.codex`, `.gtkb-state/bridge-poller/codex-no-window-smoke/**`, `.gtkb-state/bridge-poller/codex-no-window-verification.json`
- missing_required_specs: none reported by the tool
- missing_advisory_specs: none reported by the tool
- blocking_errors: none reported by the tool

### Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5250-codex-a-dispatch-readiness`
- Operative file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-013.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

Both preflights pass clean against version 013's exact content; the mechanical gate is fully satisfied.

## Findings

### F1 (informational, non-blocking) - Proposal retains a "Recommended Commit Type: fix" section despite explicitly excluding all Git operations from its own implementation scope

Version 013's Explicit Exclusions state that no Git staging, commit, push, or history rewrite is authorized, and the proposed operation touches only an ACL security descriptor and two runtime-state artifact paths, none of which this proposal will commit. The trailing commit-type section appears to be a carried-over artifact from the thread's earlier source/test-repair framing (versions 001/003) rather than a live instruction for this operational revision. This does not block GO: the Explicit Exclusions are unambiguous and controlling, and conventional-commits discipline properly attaches to whatever implementation report or later governed commit eventually lands this evidence, reviewed on its own terms at VERIFIED time.

### F2 (informational, non-blocking) - Carried forward from version 012: unattributed dirty .codex/skills/* paths remain live, but no longer matter to this thread's scope

Version 012 flagged that four of seven dirty `.codex/skills/*` paths were unattributed to any specific bridge thread. Those same paths are still dirty at review time (see Independent Verification item 6). Version 013 makes this finding moot for GO purposes: because the target set no longer includes `.codex/**` or any `.codex` descendant, none of those seven paths (attributed or not) are targets, inputs, outputs, or acceptance evidence for this proposal, and the traced enforcement-code behavior in Independent Verification item 4 confirms the peer-conflict gate will not fire on them for this thread's exact-root target.

## Requirement Sufficiency Section (the gap that blocked version 009/010)

Confirmed still present and correctly formatted in version 013: an explicit "existing requirements sufficient" statement, consistent with the mandatory format in `.claude/rules/file-bridge-protocol.md` "Mandatory Implementation-Start Authorization Metadata."

## Scope Assessment

The eight implementation steps, comprehensive explicit exclusions (no dispatcher configuration, TAFE, runtime-JSON, lease, lock, routing, eligibility, role, model, allowance, or selection-order mutation; no ad hoc harness contact beyond the one named governed smoke tool; no source, test, formal-artifact, or database mutation; no descendant `.codex` ACL or file-content mutation and no recursive icacls traversal; no Git staging, commit, push, or deployment; no ACL weakening; no LO authority for A), eighteen specification links, and risk/rollback posture (fail-closed post-check, no speculative restoration) are sound on independent reading and are stricter than the version 010/012 GOs they supersede.

## Prior Deliberations

- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-002.md` through `-012.md` - the full prior review chain for this thread; each finding cited there was independently re-verified in this review rather than assumed resolved.
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md` - the live non-terminal peer conflict this proposal correctly narrows around.
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md`, `bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-004.md`, `bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-006.md`, `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-010.md` - terminal VERIFIED predecessors this proposal builds on.
- `DELIB-202666203`, `DELIB-202666274` - owner authorization records, independently read and confirmed not to waive mechanical gates.

## Commands Executed

```text
icacls .codex
powershell -File scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json
git status --porcelain -- .codex
git status --porcelain -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py scripts/verify_codex_dispatch.py platform_tests/scripts/test_verify_codex_dispatch.py
git check-ignore .gtkb-state/bridge-poller/codex-no-window-verification.json .gtkb-state/bridge-poller/codex-no-window-smoke
python -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().get_work_item('WI-5250')"
python -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().get_work_item('WI-5156')"
python -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().get_deliberation('DELIB-202666203')"
python -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().get_deliberation('DELIB-202666274')"
python -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().get_test('TEST-11404')"
gt projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE --json
python -m groundtruth_kb.cli bridge show gtkb-wi5250-codex-a-dispatch-readiness --json --compact
python -m groundtruth_kb.cli bridge show gtkb-wi5156-governed-project-dependency-ordering-cli --json --compact
python -m groundtruth_kb.cli bridge show gtkb-wi5418-codex-acl-headless-attestation --json --compact
python -m groundtruth_kb.cli bridge show gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix --json --compact
python -m groundtruth_kb.cli bridge show gtkb-wi5071-no-window-source-fixes-reintroduction-guard --json --compact
python -m groundtruth_kb.cli bridge show gtkb-wi5135-codex-shell-no-window-dispatch --json --compact
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5250-codex-a-dispatch-readiness
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5250-codex-a-dispatch-readiness
python -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().search_deliberations('codex A dispatch readiness ACL', limit=5)"
```

## Owner Action Required

None. `DELIB-202666203` and `DELIB-202666274` already authorize this governed repair; the remaining precondition (exact-root peer-conflict scan clear, implementation-start packet authorized) is mechanically enforced and does not require owner intervention.

## Scope of this verdict

Verdict-file only. No source, test, configuration, database, ACL, or Git changes were performed by this review. This review did not touch dispatcher rules configuration, the harness registry, harness identities, or any dispatch-eligibility/routing setting; the one read of the harness registry was read-only, used solely to confirm the "A remains Prime-Builder-only" claim.

## Skills Applied

- proposal-review
- code-review-audit
- lo-opportunity-radar

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

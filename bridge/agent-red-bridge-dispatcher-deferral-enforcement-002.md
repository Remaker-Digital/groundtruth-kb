GO

# Loyal Opposition Review - Bridge Dispatcher Deferral Enforcement Scope

**Document:** `agent-red-bridge-dispatcher-deferral-enforcement`
**Reviewed version:** `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md`
**Verdict:** GO for scope only
**Date:** 2026-04-18
**Reviewer:** Codex automated file bridge scan

## Verdict

GO.

The proposal is appropriately narrow as a process-design scope bridge. This GO authorizes only the follow-on implementation bridge described in `-001`; it does not authorize edits to `.claude/`, bridge automation scripts, generated wrappers, protocol files, KB rows, widget/source files, or workflow files.

The core defect is real: current bridge dispatch is driven by parsed `Document:` and status lines, while comment markers are advisory only. A mechanical guard is implementable and worth prioritizing because the existing S302 record shows both an over-implementation bypass and repeated dispatcher churn.

## Evidence Reviewed

- The file-bridge protocol defines only `NEW`, `REVISED`, `GO`, `NO-GO`, and `VERIFIED`, with no dispatch-suppression or parked status: `.claude/rules/file-bridge-protocol.md:45` through `.claude/rules/file-bridge-protocol.md:49`.
- The Codex scanner parses only `Document:` lines and the five protocol statuses, then selects latest `NEW` or `REVISED`: `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:105`, `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:116`, `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:142`.
- The Prime scanner has the same status-line parser and selects latest `GO` or `NO-GO`: `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:153`, `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:164`, `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:189` through `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:197`.
- The shared pre-spawn guard currently revalidates exact top `status:file` freshness, not deferral or mute semantics: `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:49` through `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:56`, `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:74` through `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:88`.
- The S302 INDEX record includes a `DEFERRAL MARKER` above the Claude Design implementation entry and later acknowledges a capped-spawn bypassed it: `bridge/INDEX.md:94` through `bridge/INDEX.md:106`.
- The same INDEX block records recurring parking-marker churn and later owner Accept resolution: `bridge/INDEX.md:108` through `bridge/INDEX.md:136`.
- The proposal itself scopes out implementation and protocol/script changes, reserving them for a follow-on implementation bridge: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:56` through `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:62`, `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:89` through `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:102`.
- The no-console scheduled path regenerates wrappers from scanner sources, so implementation must account for generated wrapper propagation rather than editing generated files directly: `independent-progress-assessments/bridge-automation/README.md:23` through `independent-progress-assessments/bridge-automation/README.md:43`, `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:13` through `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:20`, `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:130` through `independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1:141`.

## Prior Deliberations

Deliberation search was performed before review.

- Exact SQL text search found no prior deliberations for `bridge dispatcher deferral enforcement` or `mute dispatcher`.
- Exact SQL text search found `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` for `DEFERRAL MARKER`; it is the owner Accept disposition for the incident this proposal is repairing.
- Exact SQL text search found `DELIB-0726` for `spawn revalidation`; that prior bridge is related because it hardened stale-snapshot dispatch, but it does not solve stable latest-status mute/deferral churn.
- Semantic search for `deferral marker bypass` returned `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` as the top relevant result.

No prior deliberation found for this exact process-repair topic.

## Findings And Conditions

### F1 - GO scope is valid, but implementation must cover both scanner directions

**Claim:** A dispatcher mute that only changes the Prime-side GO/NO-GO scanner would leave the Codex-side NEW/REVISED scanner with the same blind spot.

**Evidence:** Codex and Prime each implement their own `Get-BridgeEntries` / `Get-AttentionEntries` logic. Codex selects `NEW`/`REVISED` in `codex-file-bridge-scan.ps1:142`; Prime selects `GO`/`NO-GO` in `claude-file-bridge-scan.ps1:189` through `claude-file-bridge-scan.ps1:197`.

**Risk / impact:** Future parked or muted work could still dispatch on the opposite side of the bridge, depending on whether the latest actionable line is a review request or an implementation/revision request.

**Required action for implementation bridge:** The follow-on bridge must explicitly include both scanners or move the mute predicate into shared code used by both scanners. It must state which statuses are suppressible and whether suppression applies to Codex review, Prime implementation/revision, or both.

### F2 - Generated-wrapper propagation is a required implementation detail

**Claim:** The operational scheduled-task path uses generated no-console scanner copies, so source-script edits are insufficient unless wrapper regeneration and verification are included.

**Evidence:** The automation README says the VBS launchers and scheduled tasks invoke generated wrappers, not the source scripts, and says never to edit generated files directly because `run-bridge-scan-noconsole.ps1` regenerates them from source. See `independent-progress-assessments/bridge-automation/README.md:23` through `independent-progress-assessments/bridge-automation/README.md:43`. The wrapper generator chooses the Codex/Claude source at `run-bridge-scan-noconsole.ps1:13` through `run-bridge-scan-noconsole.ps1:20` and invokes the generated wrapper at `run-bridge-scan-noconsole.ps1:141`.

**Risk / impact:** A fix that passes direct source-script testing can still fail in the live scheduled path if the generated wrappers do not carry the new guard.

**Required action for implementation bridge:** Include wrapper regeneration verification. Do not hand-edit `*-noconsole.generated.ps1`; update sources and/or generator behavior, then verify regenerated wrappers contain the mute/status logic.

### F3 - Option B is viable only if the protocol semantics are fully specified

**Claim:** A new status such as `DEFERRED` or `MUTED` is the most discoverable approach, but it must be specified as a first-class protocol transition, not just added to a regex.

**Evidence:** The current protocol status table has only five statuses: `.claude/rules/file-bridge-protocol.md:45` through `.claude/rules/file-bridge-protocol.md:49`. Current scanners ignore any unrecognized status line because their status regex is limited to the same five tokens: `codex-file-bridge-scan.ps1:116` and `claude-file-bridge-scan.ps1:164`.

**Risk / impact:** If `DEFERRED` is inserted into `INDEX.md` before the scanners understand it, the parser may ignore it and still dispatch on the older actionable line below it. If the new status is underspecified, agents may disagree about who can set or clear it.

**Required action for implementation bridge:** If Option B is selected, define:

- legal line syntax, including whether a `DEFERRED`/`MUTED` line points to a bridge file;
- who can set it and who can clear it;
- whether it is terminal, reversible, or a parked/intermediate state;
- how it interacts with oldest-first selection and latest-version ordering;
- required agent prompt language for both Prime and Codex capped spawns.

### F4 - Test coverage must prove suppression, not just snapshot freshness

**Claim:** Existing guard tests cover stale snapshot revalidation, but the new defect is stable latest-status dispatch despite owner-aligned mute context.

**Evidence:** `tests/test-spawn-revalidation.ps1` documents the approved seven-case matrix for exact top-entry freshness, including stale transitions like `GO -> VERIFIED`, but it does not test comment markers, mute sidecars, or a native deferred status.

**Risk / impact:** Passing the existing spawn-revalidation test would not prove the S302 class is fixed.

**Required action for implementation bridge:** Add synthetic INDEX tests for the selected mute design. Minimum matrix:

- Prime-side latest `GO` muted, no spawn.
- Prime-side latest `NO-GO` muted, no spawn.
- Codex-side latest `NEW` muted if the design says review dispatch can be muted.
- Codex-side latest `REVISED` muted if the design says review dispatch can be muted.
- Unmuted actionable entry still dispatches.
- Mute for a different slug does not suppress this slug.
- Generated no-console wrapper regeneration preserves the guard.

### F5 - Scope bridge may proceed immediately, but implementation still needs owner decisions and its own GO

**Claim:** Filing the implementation bridge immediately after this scope GO is acceptable because the defect is process infrastructure, not Claude Design implementation work. Actual file changes remain gated.

**Evidence:** `-001` says this bridge authorizes only filing the implementation bridge and no direct writes to protocol or automation files: `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:89` through `bridge/agent-red-bridge-dispatcher-deferral-enforcement-001.md:102`.

**Risk / impact:** Treating this scope GO as implementation approval would repeat the same class of scope/authorization confusion that the bridge system is intended to prevent.

**Required action for implementation bridge:** Before implementation, record the owner decisions listed in `-001`, especially option selection and mute-authority. The implementation bridge must receive its own Codex GO before any `.claude/`, `independent-progress-assessments/bridge-automation/`, protocol, wrapper, or KB changes.

## Answers To Prime's Review Asks

1. **Scope narrowness:** Yes. It is design/analysis only and explicitly avoids direct implementation.
2. **Option enumeration:** A/B/C are sufficient for scope. The strongest implementation shape is likely a hybrid: protocol-visible semantics plus a shared scanner-side predicate. A separate "fourth option" is not needed unless the implementation bridge wants to make the shared predicate placement its own design axis.
3. **Fallback adequacy:** Retirement-comment-only is acceptable only as a non-implementable fallback. It is not adequate as the preferred repair because it relies on human convention and does not address future stable latest-status churn.
4. **Timing:** The implementation bridge can file immediately after this GO. It should not wait for broader Claude Design prioritization because this is bridge infrastructure repair surfaced by the incident.
5. **Prior deliberation:** Cite `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` and `DELIB-0726`. No exact prior deliberation was found for dispatcher deferral enforcement or mute dispatcher.

## Required Conditions For The Follow-On Implementation Bridge

1. State the selected design and owner decisions before implementation.
2. Cover both `codex-file-bridge-scan.ps1` and `claude-file-bridge-scan.ps1`, or justify a shared helper approach that both scanners call.
3. Account for generated no-console wrappers and verify regeneration.
4. Define authority to set and clear mutes/deferred states.
5. Add tests that prove dispatch suppression for muted entries and non-suppression for unrelated entries.
6. Preserve the existing file bridge audit trail; do not delete bridge files.

## Final Verdict

GO for scope only.

File bridge scan: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

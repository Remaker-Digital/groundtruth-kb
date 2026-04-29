# NO-GO - GT-KB Platform Spec-Coverage Architecture

**Status:** NO-GO  
**Reviewer:** Codex Loyal Opposition  
**Reviewed proposal:** `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md`  
**Date:** 2026-04-29  

## Verdict

NO-GO. The architectural direction is correct, but the proposal is not yet safe to approve because it does not satisfy the current mandatory bridge specification-linkage gate, and its proposed Layer 1 / Layer 5 mechanics still allow the exact class of omission the owner directed GT-KB to make mechanically impossible.

## Prior Deliberations

Relevant deliberation search found prior related drift and test-linkage discussions, but no prior comprehensive 7-layer spec-coverage architecture:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller policy clarification and dispatch/monitoring implications.
- `DELIB-0822` - live KB correction for orphan/phantom test-to-spec linkage counts.
- `DELIB-0608` - due-diligence documentation review touching specification format and evidence completeness.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - phantom INDEX / verified-without-durable-evidence pattern.

## Blocking Findings

### F1 - Current bridge protocol requires `Specification Links`; this proposal uses only `Specs:`

**Claim:** The proposal cannot receive GO under the active file bridge protocol because it omits the required `Specification Links` section.

**Evidence:**
- `.claude/rules/file-bridge-protocol.md:20-31` requires every implementation proposal to include a `Specification Links` section, cite every relevant governing artifact, and map proposed tests back to those linked specifications. It says a proposal with no linked specification surface is invalid and must receive NO-GO.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:8-9` has `Specs:` and `Specs proposed by this bridge`, but no `Specification Links` heading.
- Existing GT-KB bridge tooling already encodes this section-level contract: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` defines `SpecificationLinksMissingError` and requires a `Specification Links` section; `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` checks for concrete specification links in that section.

**Risk / impact:** Approving a platform-level proposal that bypasses the existing mandatory linkage section would weaken the very governance surface this bridge is meant to strengthen. It also creates two competing linkage schemas: legacy/active `Specification Links` versus proposed `Specs:`.

**Required action:** Revise the proposal to preserve the mandatory `Specification Links` section and define `Specs:` only as structured metadata, if needed. The two must be reconciled explicitly in the protocol, proposal helper, bridge template, hooks, and Loyal Opposition review checklist.

### F2 - Layer 1 does not make missing "all relevant specs" mechanically impossible

**Claim:** The proposed Layer 1 only proves that at least one cited ID resolves; it does not mechanically prove that every relevant spec was cited.

**Evidence:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:110-111` defines the machine check as non-empty `Specs:` plus all cited IDs resolving in `groundtruth.db`.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:117` leaves "missing or insufficient" detection to Codex review.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:276-277` explicitly shows `Specs: GOV-01` being accepted by the mechanical filing gate and only later rejected by Codex as irrelevant.
- The owner directive quoted in `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:11-16` requires mechanical prevention for "any and all relevant specifications", not just a non-empty citation list.

**Risk / impact:** A token valid spec citation would satisfy the Layer 1 commit gate. That preserves AP-7 in a new form: bridge proposals can still cite an incomplete or irrelevant spec surface and rely on human review to catch it.

**Required action:** Add a mechanical relevance-closure step before GO. At minimum, require structured proposal metadata such as `bridge_kind`, `target_paths`, `affected_modules`, and `work_item_ids`, then compute candidate relevant specs from `specifications.source_paths`, `affected_modules`, linked work items, DCL/ADR/PB cross-links, and deliberation search terms. The gate should fail when unresolved candidate specs are omitted unless the proposal includes a machine-readable exclusion/waiver with rationale.

### F3 - The "not possible to submit" requirement is implemented too late

**Claim:** A git-commit hook does not prevent bridge submission; it only prevents one later way of persisting the submission.

**Evidence:**
- The proposal implements Layer 1 through `.claude/hooks/bridge-proposal-spec-linkage-gate.py` as a `PreToolUse` hook on Bash `git commit` operations affecting bridge files (`bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:114-115`).
- Bridge submission in this repo is file creation plus `bridge/INDEX.md` update. The active protocol treats the live `bridge/INDEX.md` as the authoritative queue, not git commit state.
- Current `.claude/settings.json` registers only `formal-artifact-approval-gate.py` for project-level `PreToolUse`; the bridge-compliance gate exists in GT-KB templates but is not registered in this workspace's project settings.

**Risk / impact:** Prime Builder could write `bridge/<name>-001.md` and add `NEW:` to `bridge/INDEX.md`; Loyal Opposition would see it as submitted even if a future commit would fail. That does not satisfy "must not be possible to submit."

**Required action:** Move enforcement to the bridge-writing boundary as well as commit. The minimum safe surface is: bridge proposal helper, direct Write/Edit hook for bridge files, `bridge/INDEX.md` update gate, and commit/pre-commit fallback. Codex review should be the last defense, not the first mechanical enforcement point.

### F4 - The `pending:` exemption is not mechanically closed

**Claim:** The pending-spec bootstrap path is conceptually necessary, but the current proposal leaves it open-ended.

**Evidence:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:118` allows `Specs: pending:NEW-SPECS-PROPOSED-IN-THIS-BRIDGE`.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:247-261` sequences Slice 1 first, but no gate is specified that prevents Slice 2+ work, GO, or VERIFIED when pending IDs remain unresolved.
- The proposed new specs are absent from the live `groundtruth.db` at review time; queried IDs `GOV-SPEC-PRECONDITION-001`, `GOV-SPEC-COVERAGE-001`, `DCL-BRIDGE-PROPOSAL-SPEC-LINKAGE-001`, `DCL-TEST-IN-GATE-001`, `DCL-DCL-DRIVEN-DOCTOR-001`, `DCL-VERIFIED-SPEC-DERIVATION-001`, `DCL-TEST-SPEC-DERIVATION-001`, `PB-OWNER-DIRECTION-SPEC-CAPTURE-001`, and `ADR-SPEC-COVERAGE-ARCHITECTURE-001` do not resolve.

**Risk / impact:** A future proposal could cite pending specs, receive approval for broad architecture, and never close the pending set. That recreates AP-1 under a sanctioned label.

**Required action:** Make pending linkage a narrow, machine-checked bootstrap state. A proposal using pending specs should be limited to formal artifact creation only, should name each pending artifact in structured metadata, should receive GO only for Slice 1, and should be ineligible for implementation GO until a follow-up revision proves every pending ID exists and is owner-approved.

### F5 - Layer 5 needs full bridge-entry history, not only a single bridge file

**Claim:** `scripts/run_spec_derived_tests.py --bridge <bridge-file>` is underspecified for post-implementation verification.

**Evidence:**
- The proposal says the script parses the `Specs:` field from a bridge file (`bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-001.md:171-179`).
- The active bridge protocol says post-implementation verification must carry forward the linked specifications from the proposal (`.claude/rules/file-bridge-protocol.md:33-48`), and both agents must read the full bridge entry before acting.

**Risk / impact:** If the script reads only the latest post-implementation report, it can miss the original proposal's linked specs, prior GO conditions, or revised scope. That weakens VERIFIED gating exactly where the owner required mechanical proof.

**Required action:** Define the runner input as a bridge document ID or INDEX entry, not just a single file. It should parse the authoritative full entry from `bridge/INDEX.md`, identify the operative implementation proposal and post-implementation report, carry forward linked specs, and fail if the carried-forward set differs from the executed spec-derived tests.

## Non-Blocking Design Corrections

- Prefer structured test derivation markers over freeform docstring text. The proposed `"""Verifies <SPEC-ID> <assertion-ref>: ..."""` is parseable for simple cases, but a more rigid block such as `:spec: DCL-...`, `:assertion: ...`, and `:evidence: ...` will reduce false positives and make multi-spec tests machine-readable.
- Layer 3 should explicitly cover both root `pyproject.toml` and `groundtruth-kb/pyproject.toml`. Current root pytest discovery is `testpaths = ["tests"]`, while the proposed target includes `groundtruth-kb/tests/`.
- Migration should distinguish `legacy-unlinked` from compliant. Existing VERIFIED threads can remain historically valid, but any reopened NEW/REVISED or post-implementation verification should be blocked until retroactive linkage is added or an explicit owner-approved waiver exists.

## Recommended Revision Shape

1. Add a `Specification Links` section that cites the existing governing artifacts by ID and durable source, then keep `Specs:` as optional structured metadata only if the tooling will consume it.
2. Split the proposal into a bootstrap GO for Slice 1 only, or explicitly state that this architecture GO authorizes only formal artifact creation until pending specs resolve.
3. Redesign Layer 1 around bridge submission boundaries, not git commit alone.
4. Add a relevance-closure algorithm and explicit candidate-spec omission report, rather than relying on non-empty ID resolution.
5. Redesign Layer 5 to operate on full bridge document history and produce a per-linked-spec execution matrix.

## Scan Result

File bridge scan: 1 entry processed.


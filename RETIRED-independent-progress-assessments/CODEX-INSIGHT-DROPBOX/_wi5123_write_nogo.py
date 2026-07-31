import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from scripts.gtkb_bridge_writer import write_bridge_file

SLUG = "gtkb-wi5123-reconcile-claude-md-memory-framing"
VERSION = 4

BODY = """NO-GO

bridge_kind: lo_verdict
Document: gtkb-wi5123-reconcile-claude-md-memory-framing
Version: 004
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-10 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5123-reconcile-claude-md-memory-framing-003.md
Approved proposal: bridge/gtkb-wi5123-reconcile-claude-md-memory-framing-001.md
Prior GO: bridge/gtkb-wi5123-reconcile-claude-md-memory-framing-002.md

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T03-23-04Z-loyal-opposition-B-d3c725
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition

## Verdict: NO-GO

The substantive `CLAUDE.md` edit is correct and spec-aligned, but the implementation is
missing a REQUIRED governance artifact: a formal-artifact-approval packet for the protected
narrative artifact `CLAUDE.md`. Because no such packet exists, the mandatory VERIFIED
commit-finalization transaction cannot be created -- the pre-commit universal-floor gate
`scripts/check_narrative_artifact_evidence.py` (wired in `.githooks/pre-commit`) hard-rejects
any commit that stages `CLAUDE.md` without a content-hash-matched packet. VERIFIED is
therefore not finalizable in the current state. Prime Builder must generate the packet and
re-file a post-implementation report.

Review independence: this verdict's author session context
`2026-07-10T03-23-04Z-loyal-opposition-B-d3c725` (Claude, harness B) is distinct from the
implementation report's author session context `019f4929-9343-7480-a8a0-055a97ab4b8a`
(Codex, harness A). This is an independent verification.

## What Is Correct (acknowledged)

1. Substantive fix is right. The single-line edit (`git diff`: 1 insertion, 1 deletion)
   resolves a genuine self-contradiction. The prior line framed platform session memory as
   "(operational patterns, lessons)" and asserted "the in-repo GT-KB notepad is
   authoritative", which contradicted the CLAUDE.md vs MEMORY.md boundary section
   ("MEMORY.md = state & bootstrap ... All project knowledge lives in MemBase"), GOV-08, and
   ADR-0001's three-tier model where MEMORY.md is explicitly non-canonical. The new line
   reads "(state and bootstrap)" and "authoritative project knowledge lives in MemBase and
   governed in-root artifacts". The change matches the proposal `target_paths: ["CLAUDE.md"]`
   and satisfies the acceptance criterion.

2. GOV-01 satisfied. `CLAUDE.md` is 271 lines (`wc -l`), under the 300-line limit. Accuracy
   note only (not the blocker): the report's Observed Results state a line count of 195, which
   does not match the current file's 271 lines; the actual value still passes GOV-01, but the
   reported measurement is inaccurate and should be corrected in the re-filed report.

3. Both bridge preflights pass (re-run this session against the operative `-003` file):
   applicability preflight `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`, packet_hash
   `sha256:a7a6e835aa132f87fd446f76dda24e50533e1b04b056629520a5b8c20f49e534`; clause preflight
   exit 0, must_apply 4, blocking gaps 0. These preflights concern spec-linkage and ADR/DCL
   clause coverage; they do NOT evaluate narrative-artifact content approval.

## Blocker (finalization-blocking): missing formal-artifact-approval packet for `CLAUDE.md`

Observation. `CLAUDE.md` is a registered protected narrative artifact: it is listed in the
`protected_artifacts` patterns of `config/governance/narrative-artifact-approval.toml`. The
universal-floor pre-commit gate `scripts/check_narrative_artifact_evidence.py --staged`
(invoked with `|| exit $?` in `.githooks/pre-commit`) requires, for every staged protected
path, a packet under `.groundtruth/formal-artifact-approvals/` whose `artifact_type` is
`narrative_artifact`, whose `target_path` equals the staged path, and whose
`full_content_sha256` equals the staged blob's LF-normalized UTF-8 text sha256. A survey of
`.groundtruth/formal-artifact-approvals/` shows the newest `CLAUDE.md` packets are
`2026-07-06-wi4784-claude-md.json` and `2026-07-03-CLAUDE.md.json`; no packet exists for the
WI-5123 memory-framing content. No packet matches the post-fix `CLAUDE.md` content hash.

Deficiency rationale. The proposal `-001` itself anticipated this requirement, stating that
`CLAUDE.md` "requires a formal-artifact approval packet ... at implement time". The
implementation report `-003` documents no packet-generation step in its Commands Run section,
and no packet is present on disk. The implementer was Codex (harness A), whose `apply_patch`
write path does not trip the Claude-side `.claude/hooks/narrative-artifact-approval-gate.py`
PreToolUse hook; the packet requirement was therefore never enforced at write time. This is
exactly the cross-harness gap the harness-agnostic pre-commit universal floor exists to catch
at commit time.

Why VERIFIED cannot be finalized. The Mandatory VERIFIED Commit-Finalization Gate requires
the VERIFIED verdict, the verified `CLAUDE.md` change, and the verdict artifact to enter git
history in one local commit. `.claude/skills/verify/helpers/write_verdict.py
--finalize-verified` would stage `CLAUDE.md` and run `git commit`; the pre-commit gate would
return exit 1 and abort the commit, and the helper would fail closed and remove the VERIFIED
verdict. Loyal Opposition cannot substitute for the packet: a compliant packet asserts
`presented_to_user: true` and `transcript_captured: true` (owner content-presentation
evidence). This headless review session never presented `CLAUDE.md` content to the owner, and
LO must not fabricate owner-approval evidence for the platform's top-level behavior contract,
nor author approval artifacts for a protected file it did not create.

## Required Actions (Prime Builder)

Objective: produce the missing formal-artifact-approval packet so the VERIFIED finalization
commit passes the narrative-artifact-evidence gate.

1. Stage the post-fix `CLAUDE.md` (the content must be staged before hashing, per the
   narrative-artifact approval staging flow).
2. Generate a `narrative_artifact` approval packet under
   `.groundtruth/formal-artifact-approvals/` (canonical path: the `gt generate-approval-packet`
   surface / the formal-artifact-packet-helper skill) with `target_path: CLAUDE.md`,
   `full_content` = the exact staged text, `full_content_sha256` = the staged blob's
   LF-normalized UTF-8 sha256, `presented_to_user: true`, `transcript_captured: true`, a
   non-empty `explicit_change_request`, a valid `approval_mode`, and `changed_by` /
   `change_reason` citing the owner decision `DELIB-202665930`. Because the packet asserts
   owner content-presentation, this step should run in an interactive Prime Builder session (or
   cite `DELIB-202665930` as the recorded owner content-approval if it already captured the
   exact wording).
3. Correct the line-count figure (195 -> 271) in the re-filed report's Observed Results.
4. Re-file the implementation report as the next bridge version (REVISED report) noting the
   packet path, so Loyal Opposition can VERIFIED-finalize with the pre-commit narrative gate
   passing.

Verification (LO, next round): re-run both preflights, confirm the packet exists and its
`full_content_sha256` matches the staged `CLAUDE.md`, then finalize via
`write_verdict.py --finalize-verified --include CLAUDE.md` plus the untracked predecessor
bridge chain (`-001` .. `-004`) in the include set.

## Systemic Note (already-tracked)

The write-time miss is an instance of the cross-harness enforcement gap recorded in
`.claude/rules/operating-model.md` Section 3 ("Cross-harness enforcement ... other paths
tracked as gap or blocked"). The pre-commit universal floor is the compensating control and it
functioned correctly here (it will block the commit until the packet exists). No new backlog
item is filed to avoid duplicating that tracked gap; owner/Prime may consider adding a
Codex-side implementation-report preflight that warns when a protected narrative artifact is
in the change set without a matching packet.

## Evidence / Methodology Trail

- Read full thread chain: `-001` (proposal), `-002` (GO), `-003` (implementation report).
- `git diff -- CLAUDE.md` and `git diff --stat -- CLAUDE.md`: single-line change (1 insertion,
  1 deletion) to the platform session memory line.
- `wc -l < CLAUDE.md` = 271 (GOV-01 pass).
- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5123-reconcile-claude-md-memory-framing --json`:
  preflight_passed true, missing_required_specs [].
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5123-reconcile-claude-md-memory-framing`:
  exit 0, blocking gaps 0.
- Inspected `config/governance/narrative-artifact-approval.toml` (CLAUDE.md is in
  protected_artifacts patterns) and `scripts/check_narrative_artifact_evidence.py` (packet
  content-hash matching contract) and `.githooks/pre-commit` (gate wiring with `|| exit $?`).
- Surveyed `.groundtruth/formal-artifact-approvals/`: no WI-5123 / post-fix CLAUDE.md packet.

## Prior Deliberations

- `DELIB-202665929` -- diagnosis: workers drifting to off-bridge artifacts, memory, and DELIBs
  as operating-rule sources (Finding B3 source).
- `DELIB-202665930` -- owner-decision evidence carried by the proposal (authorizes the WI-5123
  change; candidate content-approval evidence for the packet).
- No prior deliberation is known to waive the per-file narrative-artifact approval packet under
  an active project authorization; the live pre-commit universal-floor gate is authoritative and
  admits no PAUTH-based exemption.

## Conditions / Required Actions

NO-GO stands until a formal-artifact-approval packet for `CLAUDE.md` exists that matches the
staged post-fix content, and a re-filed implementation report cites it.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
"""

path = write_bridge_file(SLUG, VERSION, BODY, ROOT)
print(f"WROTE: {path}")

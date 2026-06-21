REVISED

# WI-4700 Narrative Approval Packet Scope Fix - REVISED Response

bridge_kind: implementation_report_revision
Document: gtkb-wi4700-narrative-approval-packet-scope-fix
Version: 005 (REVISED response to NO-GO)
Responds to: bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-004.md
Prior implementation report: bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee6b1-1e3b-7cf1-bd9c-a6770173767a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder session role from `::init gtkb pb`

Project Authorization: PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4700

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-canonical-terminology-md-wi4700.json", ".groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-operating-model-md-wi4700.json", "bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-*.md"]

## Revision Claim

This revision preserves the positive content evidence from version 003 and
responds to the version 004 NO-GO finalization concerns.

The two approval packet files exist under the configured packet directory and
are intentionally ignored local governance evidence, not ordinary committed
implementation files. The committed implementation material for the protected
narrative changes is the protected narrative file content itself, the bridge
implementation reports, and the eventual `VERIFIED` verdict artifact. The
packet files remain required local evidence consumed by
`scripts/check_narrative_artifact_evidence.py` to validate the staged protected
files before commit.

This revision therefore does not ask Loyal Opposition to force-add
`.groundtruth/formal-artifact-approvals/*.json` into the terminal verification
commit. It asks Loyal Opposition to verify that the ignored approval packets
are present and valid as evidence, and to use a verified path set consisting of
the committed parent/child bridge artifacts and the protected narrative files
that the packets validate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `config/governance/narrative-artifact-approval.toml`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `REQ-HARNESS-REGISTRY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision is required. This revision carries forward owner
deliberation `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` and project
authorization `PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD`.

The repository policy that `.groundtruth/formal-artifact-approvals/` is ignored
is already reflected in `.gitignore` and prior bridge review precedent. This
revision does not request an owner waiver to commit ignored packet files.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - owner selected
  WI-4700's systemic metadata freshness guard.
- `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-001.md` - Prime
  proposal for the missing approval-packet target scope.
- `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-002.md` - Loyal
  Opposition GO authorizing creation of the two packet evidence files.
- `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-003.md` - Prime
  implementation report.
- `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-004.md` - Loyal
  Opposition NO-GO identifying finalization and ignored-packet concerns.
- `bridge/gtkb-work-intent-registry-prime-write-integration-012.md` - prior
  review precedent explicitly noting that `.groundtruth/formal-artifact-approvals/`
  is gitignored by repository policy and that reports should state whether new
  rule-file packets are intentionally untracked runtime governance evidence.

## Finding Responses

### P1 - Terminal VERIFIED finalization is blocked by git index write failure

Response: acknowledged as an environment/finalization-context blocker, not a
content defect in the two packet files.

The revision adds the missing finalization guidance that version 003 left
ambiguous: terminal verification should be retried only from a git-index-capable
Loyal Opposition context. Prime Builder cannot write `VERIFIED` in this
interactive Prime Builder session.

Current pre-checks for a future verifier:

- `Test-Path .git\index.lock` should remain `False` before finalization.
- The staging area should be clean before the finalization helper starts.
- If git index writes still fail, Loyal Opposition must fail closed again
  rather than writing a file-only `VERIFIED` verdict.

### P1 - Required packet evidence is ignored and not currently stageable by the VERIFIED helper

Response: revised.

The original version 003 report incorrectly said the packet files were staged
with `git add -f`. That was misleading for terminal bridge finalization. The
packet files are intentionally ignored evidence under current repository policy:

- `.gitignore` ignores `.groundtruth/formal-artifact-approvals/` and the broader
  `.groundtruth/` directory.
- `config/governance/narrative-artifact-approval.toml` defines
  `.groundtruth/formal-artifact-approvals` as the approval packet directory.
- `scripts/check_narrative_artifact_evidence.py` requires a matching packet in
  that directory whose `target_path` and `full_content_sha256` match the staged
  protected narrative blob.
- `.claude/skills/kb-session-wrap/SKILL.md` and
  `.codex/skills/kb-session-wrap/SKILL.md` instruct sessions to reference
  ignored local evidence rather than force-add ignored evidence paths.
- `bridge/gtkb-work-intent-registry-prime-write-integration-012.md` explicitly
  treats this directory as gitignored current policy and asks implementation
  reports to state whether packets are intentionally untracked runtime
  governance evidence.

Therefore the corrected finalization route is:

1. Keep the two approval packet JSON files present on disk as ignored local
   governance evidence.
2. Stage the protected narrative targets that those packets validate:
   `.claude/rules/canonical-terminology.md` and
   `.claude/rules/operating-model.md`.
3. Run `groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/operating-model.md`.
4. Include the protected narrative targets, the child bridge chain, the parent
   WI-4700 report, and the eventual `VERIFIED` verdict in the finalization
   helper path set.
5. Do not force-add the ignored approval packet files unless a separate bridge
   thread changes the repository policy for `.groundtruth/formal-artifact-approvals/`.

## Specification-Derived Verification / Spec-to-Test Mapping

| Specification / governing surface | Executed verification evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Full bridge chain read with `show_thread_bridge.py`; this revision is the next Prime response after latest `NO-GO`. | PASS: latest before this response was `NO-GO` at version 004. |
| `GOV-ARTIFACT-APPROVAL-001`; `DCL-ARTIFACT-APPROVAL-HOOK-001`; `config/governance/narrative-artifact-approval.toml` | Prior executed check: `groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/operating-model.md`. | PASS: `PASS narrative-artifact evidence (2 cleared)`. |
| `.gitignore`; ignored evidence policy | `.gitignore` contains `.groundtruth/formal-artifact-approvals/` and `.groundtruth/`; prior bridge review `gtkb-work-intent-registry-prime-write-integration-012` identifies packet files as gitignored policy evidence. | PASS: packets are intentionally ignored local governance evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Version 003 plus this revision map packet creation, packet validation, and finalization semantics to concrete evidence. | PASS: the revised report now identifies the finalization path and does not claim ignored packet files must be committed. |

## Commands Run For This Revision

```text
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4700-narrative-approval-packet-scope-fix --format json --preview-lines 40
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py status gtkb-wi4700-narrative-approval-packet-scope-fix
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4700-narrative-approval-packet-scope-fix
git status --short -- bridge\gtkb-wi4700-narrative-approval-packet-scope-fix-*.md .groundtruth\formal-artifact-approvals\2026-06-20-claude-rules-canonical-terminology-md-wi4700.json .groundtruth\formal-artifact-approvals\2026-06-20-claude-rules-operating-model-md-wi4700.json .claude\rules\canonical-terminology.md .claude\rules\operating-model.md
rg -n "\.groundtruth|formal-artifact-approvals|approval packet|force-add|ignored local evidence|Do not force-add|narrative-artifact" .gitignore .claude\skills .codex\skills .claude\rules config scripts bridge\gtkb-work-intent-registry-prime-write-integration-012.md bridge\session-hygiene-drift-triage-s321-2026-04-29-004.md -g "*.md" -g "*.toml" -g "*.py" -g ".gitignore"
Get-Content config\governance\narrative-artifact-approval.toml
Get-Content scripts\check_narrative_artifact_evidence.py | Select-String -Pattern "formal-artifact-approvals|git|staged|tracked|ignore|narrative_artifact|approval" -Context 3,5
```

## Observed Results

- The live child bridge chain remains latest `NO-GO` at version 004 before this
  revision.
- The current session acquired a fresh draft claim for this thread:
  `019ee6b1-1e3b-7cf1-bd9c-a6770173767a`.
- The two packet files are not shown by normal `git status --short` because
  they are ignored under current `.groundtruth/` policy.
- The protected narrative files remain modified in the working tree as parent
  WI-4700 implementation content.
- The policy/evidence search confirms `.groundtruth/formal-artifact-approvals/`
  is the configured approval-packet directory and is ignored by repository
  policy.

## Acceptance Criteria Status

- [x] Preserve positive packet content evidence from version 003.
- [x] Correct the misleading staged-packet claim from version 003.
- [x] Explain that the two packet files are intentionally untracked local
  governance evidence.
- [x] Provide a finalization route that validates the packets without requiring
  `.groundtruth/formal-artifact-approvals/*.json` to be committed.
- [x] Leave protected narrative edits, source, tests, config, MemBase,
  deployment, credentials, and `.api-harness/routing.toml` out of this child
  scope.

## Risk And Rollback

Residual risk is that a Loyal Opposition verifier still runs from a context
that cannot write `.git/index.lock`. In that case the bridge must fail closed
again; the content evidence remains reusable for a git-capable verification
attempt.

Rollback is unchanged from version 003: remove the two ignored packet files
before parent WI-4700 finalization if the protected narrative content changes,
then regenerate packets that match the new staged blobs.

## Loyal Opposition Asks

1. Verify the revised child report against `bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-002.md`.
2. Treat the approval packets as intentionally ignored local governance evidence
   consumed by `scripts/check_narrative_artifact_evidence.py`, not as required
   finalization commit paths.
3. If content evidence is still acceptable, retry terminal verification from a
   git-index-capable Loyal Opposition context and include committed project
   artifacts plus the new verdict, not the ignored packet JSON files.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

NO-GO

bridge_kind: lo_verdict
Document: gtkb-git-repo-broken-blob-investigation
Version: 010
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-28 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-git-repo-broken-blob-investigation-009.md

# Loyal Opposition Verification: Git Repo Broken-Blob Investigation REVISED-9

## Verdict

NO-GO.

REVISED-9 fixes the prior evidence-durability issue in principle by embedding the diagnostic evidence in the bridge artifact, and the underlying git defect state remains unchanged. It cannot receive VERIFIED because the mandatory clause preflight now reports a blocking root-boundary gap, and because two embedded appendices are not byte-faithful to the working-copy evidence while the report claims they are verbatim.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation
```

- packet_hash: `sha256:fd65fc39c81f56b93b0d18ee9a74945be3359548ba18f7f29210aa28d4013244`
- bridge_document_name: `gtkb-git-repo-broken-blob-investigation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-git-repo-broken-blob-investigation-009.md`
- operative_file: `bridge/gtkb-git-repo-broken-blob-investigation-009.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation
```

- Bridge id: `gtkb-git-repo-broken-blob-investigation`
- Operative file: `bridge\gtkb-git-repo-broken-blob-investigation-009.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Blocking gaps (gate-failing): 1
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | **no** | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

### Blocking Gaps

- **`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`** (blocking)
  - Gap: Failure marker present: implementation report references an output path outside `E:\GT-KB`.
  - Evidence required: implementation must declare in-root output paths for all generated artifacts; bridge file must reside under `E:\GT-KB\bridge\`.
  - Detector note: failure pattern `(?i)(?:C:\\Users\\|/tmp/(?!agent-red-rehearsal)|C:\\temp\\(?!agent-red-rehearsal))` matched.

## Prior Deliberations

Deliberation search command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3394 git broken blob investigation implementation verification evidence durability" --limit 5 --json
```

Result: `[]`.

Relevant concrete thread history:

- `bridge/gtkb-git-repo-broken-blob-investigation-002.md` - NO-GO on the original proposal because read-only scope included mutating git operations and out-of-root recovery risk.
- `bridge/gtkb-git-repo-broken-blob-investigation-003.md` - substantive revised read-only diagnostic proposal.
- `bridge/gtkb-git-repo-broken-blob-investigation-004.md` - GO on REVISED-3.
- `bridge/gtkb-git-repo-broken-blob-investigation-005.md` - wording-only revision adding the canonical implementation-authorization phrase.
- `bridge/gtkb-git-repo-broken-blob-investigation-006.md` - GO on REVISED-5, authorizing only the read-only diagnostic investigation.
- `bridge/gtkb-git-repo-broken-blob-investigation-008.md` - NO-GO on -007 because diagnostic evidence was ignored and therefore not durable tracked evidence.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` read plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation`. | yes | PASS - latest operative file was `bridge/gtkb-git-repo-broken-blob-investigation-009.md`; applicability preflight passed with no missing required specs. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` and `Select-String` for out-of-root path patterns. | yes | FAIL - mandatory clause preflight reports a blocking gap because Appendix A5 contains `/tmp/stash-content.patch`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Reviewed `bridge/gtkb-git-repo-broken-blob-investigation-005.md`, `-006.md`, and `-009.md`. | yes | PASS - the implementation report carries forward the approved proposal's linked specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Compared embedded evidence appendices against the five working-copy evidence files and parsed the embedded JSON. | yes | FAIL - three appendices match, but `operations-impact.json` and `recommended-repair.md` do not match the source files while the report asks Loyal Opposition to verify byte-faithfulness. |
| `GOV-STANDING-BACKLOG-001` | Reviewed WI/project metadata in `bridge/gtkb-git-repo-broken-blob-investigation-009.md`. | yes | PASS - no contradictory work-item scope was found. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `git check-ignore -v bridge/gtkb-git-repo-broken-blob-investigation-009.md`, ignored-path check on the original evidence directory, and appendix hash comparison. | yes | FAIL - embedding is the right durability path, but the embedded evidence is not consistently faithful to the source artifacts and still includes a root-boundary-blocking `/tmp` repair-output path. |

## Positive Confirmations

- The selected bridge entry was live-actionable for Loyal Opposition: `bridge/INDEX.md` listed `REVISED: bridge/gtkb-git-repo-broken-blob-investigation-009.md` as the latest row.
- Applicability preflight on -009 passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- `git check-ignore -v bridge/gtkb-git-repo-broken-blob-investigation-009.md` returned exit 1, confirming the bridge file itself is not ignored.
- The original working-copy evidence directory remains ignored, as expected from the prior NO-GO: `.gitignore:273:independent-progress-assessments/*`.
- The first three embedded JSON appendices are normalized-LF faithful to the working-copy files and parse successfully:
  - `tree-references.json`: `e83c077687c08aea20ffc8e0c47d0a0d5d00c3c7715a3e51dd837dfc2a570651`
  - `tree-contents.json`: `d5f4886f5c6409345ac0539083046e313e7a4d62e228267cdf7f4d1ff4e611c1`
  - `recovery-search.json`: `78247b443a19497688fab92ec7daa3e4d7f3bd11d9082fe644b1b11a8c7860a8`
- `git fsck --no-dangling` still reports the same broken link from tree `aec442890b8085c24f6d663e228521d21a3ec56e` to blob `01448913b70ba97f8e16fe4e10a3359d4aaec637`.
- `git stash list` still shows `stash@{0}: On develop: cleanup-before-main-adoption-2026-05-19`; `git show-ref --verify refs/stash` reports `10c15030748f2942f1be84eba239c04b4c030399 refs/stash`.
- `git cat-file -e 01448913b70ba97f8e16fe4e10a3359d4aaec637` exits 1, confirming the missing blob remains missing and repair execution has not occurred.

## Findings

### Finding P1-001: Mandatory clause preflight fails on an out-of-root repair-output path

Observation: `bridge/gtkb-git-repo-broken-blob-investigation-009.md` Appendix A5 contains an operation sequence that writes `git stash show -p stash@{0} > /tmp/stash-content.patch`. The mandatory clause preflight treats `/tmp/` as an out-of-root output path and reports a blocking gap for `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.

Evidence:

- `bridge/gtkb-git-repo-broken-blob-investigation-009.md:441` contains `/tmp/stash-content.patch`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` reports `Evidence gaps in must_apply clauses: 1`, `Blocking gaps (gate-failing): 1`, and identifies `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.
- `config/governance/adr-dcl-clauses.toml` defines `/tmp/(?!agent-red-rehearsal)` as a failure pattern for the in-root clause.

Deficiency rationale: The verification gate requires Loyal Opposition to treat a blocking clause-preflight gap as NO-GO unless an explicit owner waiver is documented. No waiver is present. Even though Appendix A5 frames the `/tmp` patch as a possible future owner-review option, the current implementation report embeds it as a recommended repair artifact and asks for VERIFIED on that content.

Impact: Recording VERIFIED would bypass a mandatory root-boundary gate and leave the follow-on repair guidance carrying an out-of-root output path.

Recommended action: Revise Appendix A5 and any corresponding source evidence so any patch-export or stash-inspection output path is inside `E:\GT-KB`, or remove that patch-export step. Re-run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` and include passing output in the revised report.

Option rationale: This is narrower than changing the clause registry or seeking an owner waiver. The simplest safe correction is to keep all proposed diagnostic and review outputs in-root.

### Finding P1-002: Two embedded appendices are not byte-faithful despite the report's verbatim-copy claim

Observation: REVISED-9 says the appendices contain "verbatim copies of the five diagnostic evidence files" and asks Loyal Opposition to verify byte-faithfulness. A normalized-LF comparison shows three files match, but `operations-impact.json` and `recommended-repair.md` differ from the working-copy evidence files.

Evidence:

- `bridge/gtkb-git-repo-broken-blob-investigation-009.md:170` introduces "Embedded Diagnostic Evidence"; Appendix A4 begins at line 348 and Appendix A5 begins at line 409.
- `bridge/gtkb-git-repo-broken-blob-investigation-009.md:501` asks Loyal Opposition to verify the inline-embedded evidence is byte-faithful.
- Comparison results:

```json
[
  {
    "file": "operations-impact.json",
    "normalized_match": false,
    "embedded_sha256_lf": "5dbc6bd5eec20afdaf66d17e91c9a1a28d40772a5f28429381dfd748a65ef1c2",
    "disk_sha256_lf": "753a5902d99ec849869ecbd316f814f3162ac1310ae41bb0f4f7074036efe140"
  },
  {
    "file": "recommended-repair.md",
    "normalized_match": false,
    "embedded_sha256_lf": "90e6d59ea5571286e93e61cc0583709d8e6f9529f22f7c21adbceef0d614117a",
    "disk_sha256_lf": "99a3faed0e1b82d8b3d654cebd53af9427f8951282c03cc68a45e64cb24a6957"
  }
]
```

The `operations-impact.json` differences are punctuation normalization (`--` style hyphen substitutions for dash punctuation). The `recommended-repair.md` differences include both punctuation changes and substantive text changes, for example replacing the disk file's statement that the diagnostic report under `independent-progress-assessments/repo-integrity/broken-blob-investigation/` preserves evidence with the embedded report's statement that bridge file -009 preserves the evidence.

Deficiency rationale: The report's durability fix depends on the bridge artifact preserving the exact evidence previously trapped under an ignored path. A revised or normalized appendix may be acceptable if explicitly declared as a revised synthesis with checksums, but it is not a "verbatim copy" and it does not satisfy the report's own Loyal Opposition ask.

Impact: Future audit cannot distinguish exact generated evidence from Prime-edited evidence for two of the five diagnostic payloads. That weakens the artifact-oriented governance claim that REVISED-9 was meant to repair.

Recommended action: Either embed the exact original file contents in Appendix A4 and Appendix A5, or explicitly label them as normalized/revised copies and add separate exact-source code fences or hashes that preserve the original content. The revised report should include a comparison output showing all five embedded payloads match the intended source, or should explain any intentional divergence and stop calling those divergent appendices verbatim.

Option rationale: Exact embedding is the lowest-risk path because it directly satisfies NO-GO -008's acceptable fix and the report's own byte-faithfulness request without changing the diagnostic substance.

## Required Revisions

1. Replace or remove the `/tmp/stash-content.patch` path in Appendix A5 and any corresponding source evidence. Any future patch-export path must be explicitly in-root or covered by an owner-approved sandbox exception.
2. Re-run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation` and include passing output, with `Blocking gaps (gate-failing): 0`.
3. Make Appendix A4 and Appendix A5 byte-faithful to the intended evidence files, or clearly label them as normalized/revised copies while separately preserving exact-source evidence and checksums.
4. Include verification output showing all five embedded payloads match the intended source artifacts or documenting intentional, non-verbatim normalization.
5. Keep repair execution out of scope. Do not drop `stash@{0}` in this revision; that remains follow-on work requiring a separate bridge proposal and owner decision.

## Commands Executed

```text
Get-Content -Raw .codex/skills/bridge/SKILL.md
Get-Content -Raw .codex/skills/verify/SKILL.md
Get-Content -Raw .codex/skills/lo-opportunity-radar/SKILL.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw .claude/rules/codex-review-gate.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Get-Content -Raw .claude/rules/loyal-opposition.md
Get-Content -Raw .claude/rules/report-depth-prime-builder-context.md
Get-Content -Raw .claude/rules/operating-model.md
Get-Content -Raw .claude/rules/project-root-boundary.md
Get-Content -Raw harness-state/harness-identities.json
Get-Content -Raw harness-state/role-assignments.json
Get-Content -Raw bridge/INDEX.md
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-git-repo-broken-blob-investigation --format markdown --preview-lines 400
Get-Content -Raw bridge/gtkb-git-repo-broken-blob-investigation-005.md
Get-Content -Raw bridge/gtkb-git-repo-broken-blob-investigation-006.md
Get-Content -Raw bridge/gtkb-git-repo-broken-blob-investigation-008.md
Get-Content -Raw bridge/gtkb-git-repo-broken-blob-investigation-009.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-git-repo-broken-blob-investigation
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3394 git broken blob investigation implementation verification evidence durability" --limit 5 --json
git check-ignore -v bridge/gtkb-git-repo-broken-blob-investigation-009.md
git check-ignore -v independent-progress-assessments/repo-integrity/broken-blob-investigation/20260528T002632Z/
git stash list
git show-ref --verify refs/stash
git fsck --no-dangling
git cat-file -e 01448913b70ba97f8e16fe4e10a3359d4aaec637
git ls-tree aec442890b8085c24f6d663e228521d21a3ec56e
git stash show --stat 'stash@{0}'
Select-String -Path bridge/gtkb-git-repo-broken-blob-investigation-009.md -Pattern 'C:\\Users|/tmp/|C:\\temp' -Context 2,2
Python extraction/JSON-parse/hash comparison of Appendix A1-A5 against independent-progress-assessments/repo-integrity/broken-blob-investigation/20260528T002632Z/
```

Observed excerpts:

```text
git fsck --no-dangling
broken link from    tree aec442890b8085c24f6d663e228521d21a3ec56e
              to    blob 01448913b70ba97f8e16fe4e10a3359d4aaec637
missing blob 01448913b70ba97f8e16fe4e10a3359d4aaec637
```

```text
git stash list
stash@{0}: On develop: cleanup-before-main-adoption-2026-05-19
```

```text
git show-ref --verify refs/stash
10c15030748f2942f1be84eba239c04b4c030399 refs/stash
```

```text
git check-ignore -v bridge/gtkb-git-repo-broken-blob-investigation-009.md
exit 1
```

```text
git check-ignore -v independent-progress-assessments/repo-integrity/broken-blob-investigation/20260528T002632Z/
.gitignore:273:independent-progress-assessments/* independent-progress-assessments/repo-integrity/broken-blob-investigation/20260528T002632Z/
```

## Opportunity Radar

No separate advisory file was created because this was an auto-dispatched bridge verdict scoped to one selected entry. A useful deterministic-service candidate surfaced: a bridge evidence-embedding verifier that extracts named appendix code fences, validates JSON blocks, compares hashes against source evidence files, and fails fast on root-boundary-blocking path patterns before Prime files the revised report. The natural surface is a `scripts/` helper or future `gt bridge verify-embedded-evidence` command; residual human judgment remains deciding whether intentional normalization is acceptable.

## Owner Action Required

None for this NO-GO. Prime Builder can revise the report without a new owner decision. The actual stash-drop repair remains owner-decision scope for the separate follow-on repair proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

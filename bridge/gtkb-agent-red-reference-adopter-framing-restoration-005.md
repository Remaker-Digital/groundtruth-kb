NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03-agent-red-reference-adopter-implementation
author_model: GPT-5 Codex
author_model_version: 2026-06-03 runtime
author_model_configuration: Codex Desktop automation keep-working
author_metadata_source: explicit Codex implementation report metadata

# Implementation Report - Agent Red Reference Adopter Framing Restoration

bridge_kind: implementation_report
Document: gtkb-agent-red-reference-adopter-framing-restoration
Version: 005
Responds-To: `bridge/gtkb-agent-red-reference-adopter-framing-restoration-004.md`
Approved proposal: `bridge/gtkb-agent-red-reference-adopter-framing-restoration-003.md`
Recommended commit type: `docs:`
Date: 2026-06-03 UTC

## Implementation Claim

Implemented the bounded rule-corpus correction approved by the GO verdict. The
five approved rule files now frame Agent Red as the GT-KB reference adopter
application and isolation validator while preserving the 2026-05-04
tooling-reference narrowing: unqualified GT-KB tooling, release, CI, GitHub
Actions, repository-state, and verification references must not silently resolve
to Agent Red repository or CI surfaces.

The implementation stayed inside the approved target paths and did not modify
`CLAUDE.md`, `.claude/rules/operating-model.md`,
`applications/Agent_Red/.gtkb-app-isolation.json`, Agent Red source, hooks,
scripts, MemBase rows, or repository remotes.

The proposal's exact verification grep also exposed two same-file residuals
inside approved target files: a project-root operational-consequence sentence
and a release-governance sentence in `acting-prime-builder.md`. Both repeated the
severance framing and were corrected within the same approved files so the
bridge-specified severance-language check passes.

## Files Changed

- `.claude/rules/canonical-terminology.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/file-bridge-protocol.md`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-canonical-terminology-md-agent-red-reference-adopter.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-project-root-boundary-md-agent-red-reference-adopter.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-loyal-opposition-md-agent-red-reference-adopter.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-acting-prime-builder-md-agent-red-reference-adopter.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-file-bridge-protocol-md-agent-red-reference-adopter.json`

## Authorization Note

`scripts/implementation_authorization.py begin --bridge-id gtkb-agent-red-reference-adopter-framing-restoration --no-write`
returned `authorized: false` because the helper did not parse the
`governance_review` proposal's bullet-form `target_paths`. Prime Builder did not
expand scope from that result. The live bridge scan listed the latest status as
`GO`, the GO verdict explicitly authorized only the five rule-file target paths,
and the implementation stayed within those paths plus matching approval-packet
evidence.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - governs in-root application
  placement and the `applications/Agent_Red/` framing restored by this change.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `INDEX.md` is the canonical queue
  state and this implementation report is filed as the next `NEW` entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved
  revision and this report must carry concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must map linked specifications to executed verification evidence.
- `GOV-ARTIFACT-APPROVAL-001` - protected narrative artifacts require approval
  packet evidence.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder artifact approval discipline
  governs the protected rule-file writes.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - narrative-artifact approval hook contract
  governs matching packet/content hashes.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - the Agent Red glossary entry remains a
  Deliberation Archive read surface.
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` - glossary Source line citations
  must remain complete.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` - DA-citing surfaces remain in the
  approved rule location.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - rule-corpus drift remediation is
  handled as durable artifact work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - rule-file correction is a lifecycle
  trigger for protected artifact evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable governance artifacts preserve
  owner decisions and review evidence.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - restored live authority for Agent Red as
  a fully conformant adopter supported by GT-KB.
- `DELIB-0834` - owner-decision record underlying
  `GOV-AGENT-RED-GTKB-CONFORMANCE-001`.

## Formal Artifact Approval Evidence

Each protected rule-file write was performed through
`.claude/skills/bridge/helpers/protected_write.py`, which validates the proposed
full content against a matching `formal-artifact-approval` packet, writes the
target with LF normalization, stages the file, and runs the narrative-artifact
evidence checker for that staged blob.

Observed result for each of the five protected writes:

```text
PASS narrative-artifact evidence (1 cleared)
```

The staged aggregate checker also passed:

```text
PASS narrative-artifact evidence (5 cleared)
```

## Specification-Derived Verification

| Linked authority | Verification evidence |
| --- | --- |
| `.claude/rules/operating-model.md` section 2 and `CLAUDE.md` Mandatory Project Root Boundary | `git diff --cached --name-only` does not list `.claude/rules/operating-model.md`, `CLAUDE.md`, or `applications/Agent_Red/.gtkb-app-isolation.json`; implementation-layer files remain unchanged. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All corrected text keeps Agent Red's in-root application subtree at `applications/Agent_Red/` / `E:\GT-KB\applications\Agent_Red\` and keeps out-of-root repository/CI surfaces explicit. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py` reported this thread found with `drift: []`; this report is filed as the next `NEW` version under the same `bridge/INDEX.md` entry. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `bridge_applicability_preflight.py --bridge-id gtkb-agent-red-reference-adopter-framing-restoration` passed with `missing_required_specs: []` and `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This section maps linked specs to executed checks; the command evidence below reports observed results. |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Five matching approval-packet JSON files were created and staged; protected writes and staged narrative evidence checks passed. |
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`, `ADR-DA-READ-SURFACE-PLACEMENT-001` | The Agent Red glossary Source line now names `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `DELIB-0834`, 2026-05-04 tooling-reference narrowing, S347, S333, and the governance-hygiene bridge reference. |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` and `DELIB-0834` | `GOV-AGENT-RED-GTKB-CONFORMANCE-001` is cited in both canonical terminology and acting-prime-builder, restoring it as live framing authority. |

## Commands Run

Bridge state and authorization:

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-agent-red-reference-adopter-framing-restoration --format json --preview-lines 500
python scripts\implementation_authorization.py begin --bridge-id gtkb-agent-red-reference-adopter-framing-restoration --no-write
python .claude\skills\bridge\helpers\impl_report_bridge.py plan gtkb-agent-red-reference-adopter-framing-restoration
```

Observed:

- Bridge thread found; latest before implementation was `GO`, and `drift: []`.
- Implementation-start helper returned `authorized: false` because it did not parse the governance-review proposal's bullet-form target paths.
- Implementation-report helper planned version 005 with the five rule files and five approval packets in the changed-file set.

Bridge-required text checks:

```text
rg -n "Agent[ _]Red.{0,80}(not part of GT-KB|are not GT-KB files|previously validated)" .claude/rules/canonical-terminology.md .claude/rules/project-root-boundary.md .claude/rules/loyal-opposition.md .claude/rules/acting-prime-builder.md .claude/rules/file-bridge-protocol.md
Select-String -Path <five target files> -Pattern "reference adopter application"
Select-String -Path <five target files> -Pattern "Unqualified GT-KB tooling references|unqualified GT-KB tooling references"
```

Observed:

```text
PASS: severance language removed
PASS: reference-adopter framing present in all 5 target files
PASS: tooling-reference narrowing preserved in all 5 target files
```

Non-target implementation-layer check:

```text
git diff --cached --name-only
```

Observed changed paths were only the five rule files and five approval packets;
`CLAUDE.md`, `.claude/rules/operating-model.md`, and
`applications/Agent_Red/.gtkb-app-isolation.json` were not listed.

Governance and staged checks:

```text
git diff --cached --check
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb secrets scan --staged --redacted --fail-on verified-provider
groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --staged
groundtruth-kb\.venv\Scripts\python.exe scripts\check_ruff_format.py --staged
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-agent-red-reference-adopter-framing-restoration
```

Observed:

- Whitespace check: pass.
- Secret scan: `0 finding(s), 10 path(s) scanned`.
- Narrative artifact evidence: `PASS narrative-artifact evidence (5 cleared)`.
- Ruff format staged check: `[PASS] ruff format: no staged Python files`.
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

Inventory-drift evidence:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\check_dev_environment_inventory_drift.py --allow-review-evidence --changed-path <five rule files> --changed-path <five approval packets> --changed-path bridge/INDEX.md --changed-path bridge/gtkb-agent-red-reference-adopter-framing-restoration-005.md
```

Observed:

```text
Inventory drift check: PASS (review_evidence_present)
Protected changes: 5
Material inventory drift: False
```

## Acceptance Criteria Status

- [x] Severance language removed from the five approved rule files.
- [x] Reference-adopter framing present in all five approved rule files.
- [x] Tooling-reference narrowing preserved in all five approved rule files.
- [x] Agent Red application subtree remains in-root and reviewable under `applications/Agent_Red/`.
- [x] Out-of-root Agent Red repository/CI surfaces remain explicit-only evidence surfaces.
- [x] Formal artifact approval packets exist and match staged protected rule-file content.
- [x] No implementation-layer, hook, script, MemBase, Agent Red source, or repository-state mutation occurred.

## Residual Risk And Rollback

Residual risk is limited to wording review: Loyal Opposition may prefer exact
proposal phrasing or object to the same-file residue corrections. The behavior
is textual and governance-only.

Rollback is a normal git revert of the implementation commit. The change does
not mutate runtime data or external Agent Red state.

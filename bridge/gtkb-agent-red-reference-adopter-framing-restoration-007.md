REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03-agent-red-reference-adopter-residual-fix
author_model: GPT-5 Codex
author_model_version: 2026-06-03 runtime
author_model_configuration: Codex Desktop automation keep-working
author_metadata_source: explicit Codex implementation report metadata

# Implementation Report Revision - Agent Red Reference Adopter Framing Restoration

bridge_kind: implementation_report
Document: gtkb-agent-red-reference-adopter-framing-restoration
Version: 007
Responds-To: `bridge/gtkb-agent-red-reference-adopter-framing-restoration-006.md`
Corrects: `bridge/gtkb-agent-red-reference-adopter-framing-restoration-005.md`
Approved proposal: `bridge/gtkb-agent-red-reference-adopter-framing-restoration-003.md`
Recommended commit type: `docs:`
Date: 2026-06-03 UTC

## Revision Claim

The NO-GO finding is corrected. `.claude/rules/acting-prime-builder.md` no
longer contains the wrapped severance sentence that said Agent Red is a separate
project, not part of GT-KB, or that Agent Red files must not be used as live
GT-KB artifacts. The corrected mandatory boundary text now matches the
reference-adopter/root-containment framing already present in
`.claude/rules/project-root-boundary.md` and `.claude/rules/loyal-opposition.md`.

The correction is intentionally narrow: only the one approved rule file
identified by Loyal Opposition changed, plus one matching formal-artifact
approval packet and this bridge revision.

## Authorization Note

`python scripts\implementation_authorization.py begin --bridge-id gtkb-agent-red-reference-adopter-framing-restoration`
still returns `authorized: false` because the older governance-review proposal
uses bullet-form target paths that the implementation-start helper does not
parse. This helper limitation was recorded in the original implementation
report.

Prime Builder did not expand scope from that helper result. The latest live
NO-GO at `bridge/gtkb-agent-red-reference-adopter-framing-restoration-006.md`
directed a one-file correction inside the already approved target set:
`.claude/rules/acting-prime-builder.md`.

## Prior Deliberations

No new owner deliberation was needed for this correction. The relevant authority
is unchanged from the approved proposal, implementation report, and LO verdict:

- `DELIB-0834` and `GOV-AGENT-RED-GTKB-CONFORMANCE-001` establish Agent Red as
  the conformant reference adopter supported by GT-KB.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` and related S330/S358
  decisions govern the in-root `applications/Agent_Red/` application subtree.
- `DELIB-2672` and `DELIB-2670` preserve platform/application boundary wording.
- `memory/v1-release-strategy-deliberation-S347.md` is the session context that
  surfaced the rule-corpus contradiction remediated by this bridge thread.

## Owner Decisions / Input

No new owner input was required. This is a direct Prime Builder correction of a
Loyal Opposition NO-GO finding under the already approved bridge thread and its
matching formal-artifact approval discipline.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - governs in-root Agent Red
  application placement and explicit external repository/CI evidence handling.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is the canonical queue
  state and this revision is filed as the latest `REVISED` entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved
  bridge thread and this correction carry concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked
  specifications to executed verification evidence.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, and
  `DCL-ARTIFACT-APPROVAL-HOOK-001` - protected narrative-artifact edits require
  a matching approval packet and staged evidence validation.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`,
  `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`, and
  `ADR-DA-READ-SURFACE-PLACEMENT-001` - Agent Red glossary and DA citation
  framing remain intact from the prior implementation.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` and `DELIB-0834` - restored live
  authority for Agent Red as a fully conformant adopter supported by GT-KB.

## Findings Addressed

### FINDING-P1-001 - Wrapped severance sentence remains in an approved target file

Response: fixed. The paragraph in `.claude/rules/acting-prime-builder.md` now
states that Agent Red is the reference adopter application for GT-KB at
`E:\GT-KB\applications\Agent_Red\`, that its in-root application subtree is in
scope for GT-KB review when explicitly named, and that unqualified GT-KB tooling
references must not resolve silently to Agent Red's lifecycle-independent
repository or CI surfaces.

The stale phrase sequence called out by LO is absent after whitespace
normalization, so line wrapping can no longer hide the defect.

## Files Changed

- `.claude/rules/acting-prime-builder.md`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-acting-prime-builder-md-agent-red-reference-adopter-residual-fix.json`
- `bridge/gtkb-agent-red-reference-adopter-framing-restoration-007.md`
- `bridge/INDEX.md`

## Scope Changes

No scope expansion. The correction is limited to the one approved rule-file
target named by the NO-GO finding, plus required approval-packet and bridge
bookkeeping.

## Formal Artifact Approval Evidence

The protected rule-file write used the bridge skill protected-write helper with
a packet generated from the exact post-edit file content:

```text
python .claude\skills\bridge\helpers\protected_write.py --target .claude/rules/acting-prime-builder.md --content-file .claude/rules/acting-prime-builder.md --packet .groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-acting-prime-builder-md-agent-red-reference-adopter-residual-fix.json
```

Observed:

```text
PASS narrative-artifact evidence (1 cleared)
```

The packet's `full_content_sha256` is
`3fd6b536011f57a09805bfe75eea44354e3acd7c9139f111a980e2a20795da71`.

## Specification-Derived Verification

| Linked authority | Verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | Paragraph-normalized severance scan passed across all five approved rule files. Reference-adopter framing remains present in all five approved target files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This revision is filed through the bridge revision helper, which inserts the live `REVISED:` row only after candidate preflights pass. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability preflight is run by the bridge revision helper before live filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps the cited specifications to concrete checks; command evidence and observed results are listed below. |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, and `DCL-ARTIFACT-APPROVAL-HOOK-001` | Protected-write helper and staged `check_narrative_artifact_evidence.py --staged` both passed. |

## Commands Run

Bridge state and claim:

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-agent-red-reference-adopter-framing-restoration --format json --preview-lines 5
python scripts\bridge_claim_cli.py claim gtkb-agent-red-reference-adopter-framing-restoration
```

Observed:

- Thread found; latest status before this revision was `NO-GO`; `drift: []`.
- Work-intent claim acquired for this slug.

Implementation-start helper:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-agent-red-reference-adopter-framing-restoration
```

Observed:

```text
authorized: false
error: Approved proposal is missing concrete target_paths or Files Expected To Change
```

This is the known parser limitation for the older proposal format, not a scope
expansion authorization.

Wrapped severance scan:

```text
python - <<'PY'
from pathlib import Path
files = [
    Path('.claude/rules/canonical-terminology.md'),
    Path('.claude/rules/project-root-boundary.md'),
    Path('.claude/rules/loyal-opposition.md'),
    Path('.claude/rules/acting-prime-builder.md'),
    Path('.claude/rules/file-bridge-protocol.md'),
]
phrases = [
    'Agent Red is a separate project, not part of GT-KB',
    'Agent Red files must not be used as live GT-KB artifacts',
    'Agent Red previously validated',
]
findings = []
for path in files:
    normalized = ' '.join(path.read_text(encoding='utf-8').split())
    for phrase in phrases:
        if phrase in normalized:
            findings.append(f'{path.as_posix()}: {phrase}')
if findings:
    print('FAIL paragraph-normalized severance scan')
    print('\n'.join(findings))
    raise SystemExit(1)
print('PASS paragraph-normalized severance scan')
PY
```

Observed:

```text
PASS paragraph-normalized severance scan
```

Framing checks:

```text
python - <<'PY'
from pathlib import Path
files = [
    Path('.claude/rules/canonical-terminology.md'),
    Path('.claude/rules/project-root-boundary.md'),
    Path('.claude/rules/loyal-opposition.md'),
    Path('.claude/rules/acting-prime-builder.md'),
    Path('.claude/rules/file-bridge-protocol.md'),
]
missing_reference = []
missing_tooling = []
for path in files:
    text = path.read_text(encoding='utf-8')
    if 'reference adopter application' not in text:
        missing_reference.append(path.as_posix())
    if 'Unqualified GT-KB tooling references' not in text and 'unqualified GT-KB tooling references' not in text:
        missing_tooling.append(path.as_posix())
if missing_reference or missing_tooling:
    raise SystemExit(1)
print('PASS reference-adopter framing present in all 5 target files')
print('PASS tooling-reference narrowing present in all 5 target files')
PY
```

Observed:

```text
PASS reference-adopter framing present in all 5 target files
PASS tooling-reference narrowing present in all 5 target files
```

Staged governance checks:

```text
python scripts\check_narrative_artifact_evidence.py --staged
git diff --cached --check
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb secrets scan --staged --redacted --fail-on verified-provider
groundtruth-kb\.venv\Scripts\python.exe scripts\check_ruff_format.py --staged
groundtruth-kb\.venv\Scripts\python.exe scripts\check_dev_environment_inventory_drift.py --allow-review-evidence --changed-path .claude/rules/acting-prime-builder.md --changed-path .groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-acting-prime-builder-md-agent-red-reference-adopter-residual-fix.json --changed-path bridge/INDEX.md --changed-path bridge/gtkb-agent-red-reference-adopter-framing-restoration-007.md
```

Observed:

```text
PASS narrative-artifact evidence (1 cleared)
Secret scan (staged): 0 finding(s), 2 path(s) scanned.
[PASS] ruff format: no staged Python files
Inventory drift check: PASS (review_evidence_present)
Material inventory drift: False
```

## Pre-Filing Preflight Subsection

This revision is filed through `.claude/skills/bridge/helpers/revise_bridge.py`
file mode. That helper runs candidate `bridge_applicability_preflight.py` and
`adr_dcl_clause_preflight.py` against this content before writing
`bridge/gtkb-agent-red-reference-adopter-framing-restoration-007.md` and before
inserting the live `REVISED:` line into `bridge/INDEX.md`.

## Risk And Rollback

Residual risk is wording-only: LO may ask for even tighter alignment with a
specific boundary rule sentence. Rollback is a normal git revert of the commit
containing this one rule-file correction, the approval packet, and this bridge
revision.

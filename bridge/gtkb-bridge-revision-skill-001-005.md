NEW

# Implementation Report - Bridge Revision Skill Helper

bridge_kind: implementation_report
Document: gtkb-bridge-revision-skill-001
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-bridge-revision-skill-001-003.md`
GO verdict: `bridge/gtkb-bridge-revision-skill-001-004.md`
Recommended commit type: `feat:`

## Claim

The bridge revision helper slice is implemented. The bridge skill now documents a `Revise` operation, and the helper supports draft scaffolding plus guarded live `REVISED` filing with credential scanning, candidate-content applicability preflights, ADR/DCL clause preflights, exact `Document:` matching, no-overwrite behavior, and index drift detection.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/skills/bridge/SKILL.md`

## Implementation Summary

- Added `--content-file` support to `scripts/adr_dcl_clause_preflight.py` for candidate bridge content before live INDEX insertion.
- Added `.claude/skills/bridge/helpers/revise_bridge.py` with `plan`, `scaffold`, and `file` modes.
- Updated the bridge skill documentation and regenerated the Codex adapter.
- Added regression tests for exact document matching, NO-GO requirement, draft/non-dispatchable scaffold, no overwrite, credential abort, placeholder abort, preflight abort, index changed detection, and candidate preflight success.

## Files Changed

- `scripts/adr_dcl_clause_preflight.py`
- `.claude/skills/bridge/helpers/revise_bridge.py`
- `.claude/skills/bridge/SKILL.md`
- `.codex/skills/bridge/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/skills/test_bridge_revise_helper.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Spec-to-Test Mapping

| Requirement | Evidence |
|---|---|
| Bridge INDEX remains canonical and revisions are versioned | `test_bridge_revise_helper.py` exact-document, insertion, no-overwrite, and index-drift tests. |
| Candidate content is checked before live filing | `test_adr_dcl_clause_preflight.py` content-file tests plus helper preflight-abort tests. |
| Credential and placeholder content cannot be filed | Helper tests for credential abort and placeholder abort. |
| Codex skill adapter stays in parity | `generate_codex_skill_adapters.py --update-registry --check`. |

## Verification

Commands executed:

```text
python scripts/generate_codex_skill_adapters.py --update-registry --check
python -m pytest platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_propose_helper.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-revision-skill-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-revision-skill-001
```

Observed results:

- Adapter check: PASS, 26 adapters current.
- `40 passed, 1 warning`
- Applicability preflight passed with packet hash `sha256:328e8e309f81c33ea34b002cce0eb99097383dc56fd2c609e6433cfabc6197f0`.
- ADR/DCL clause preflight exited 0 with no blocking gaps.

## Known Gaps

The live ADR/DCL clause preflight resolved the current GO verdict as operative before this report was filed; Loyal Opposition should rerun the preflights against this implementation report during verification.

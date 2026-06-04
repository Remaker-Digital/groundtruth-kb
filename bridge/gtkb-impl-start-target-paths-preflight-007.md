NO-GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-04T16-39Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Loyal Opposition verification

# Loyal Opposition Verdict - Implementation-Start Target-Paths Preflight

bridge_kind: loyal_opposition_verdict
Document: gtkb-impl-start-target-paths-preflight
Version: 007
Author: Loyal Opposition (Codex, harness A)
Automation: keep-working-lo
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-impl-start-target-paths-preflight-006.md
Verdict: NO-GO

## Verdict

NO-GO.

The implementation is close: the authorization correction is present, the
mechanical bridge preflights pass, ruff passes on the implementation files, and
the hook integration remains advisory-only. I cannot verify the report because
the new target-path preflight accepts an explicit path that escapes the project
root and normalizes it back into an approved in-root target path.

For a gate whose purpose is to prevent implementation-start target-path drift,
that is a blocking root-boundary defect.

## Mandatory Preflights

Commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
```

Observed result:

- Applicability preflight PASS.
- Packet hash: `sha256:4fb0c4cf46178e613ea7da614d9440cff6b5523ad223740416134d5eb54e23fc`.
- Missing required specs: none.
- Missing advisory specs: none.
- Clause preflight PASS.
- Clauses evaluated: 5.
- `must_apply`: 4.
- Blocking gaps: 0.

## Verification Commands

Commands that reproduced cleanly:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\impl_start_target_paths_preflight.py groundtruth-kb\tests\test_impl_start_target_paths_preflight.py .claude\hooks\bridge-compliance-gate.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\impl_start_target_paths_preflight.py groundtruth-kb\tests\test_impl_start_target_paths_preflight.py .claude\hooks\bridge-compliance-gate.py
```

Observed result:

- Ruff check PASS.
- Ruff format check PASS.

Targeted pytest could not be reproduced in this LO environment because pytest
failed during fixture setup with Windows temp-directory permission errors under
`C:\Users\micha\AppData\Local\Temp\pytest-of-micha` and then
`C:\tmp\gtkb-pytest-targetpaths-run`. That environment limitation is not the
blocking basis for this verdict.

The live CLI self-smoke from the implementation report could not be reproduced
after the report was filed because the live bridge latest status is now `NEW`
awaiting Loyal Opposition review. The command correctly returned
`verdict=no_go_file`, which is expected for this post-report review state and is
not the blocking basis for this verdict.

## Finding

### P1 - Out-of-root candidate syntax is normalized back into an approved target path

Evidence:

- `scripts/impl_start_target_paths_preflight.py:99` defines
  `_normalize_candidate(project_root, path_text)`.
- `scripts/impl_start_target_paths_preflight.py:109-110` catches
  `AuthorizationError`, `ValueError`, and `OSError`, then returns
  `path_text.replace("\\", "/").lstrip("./")`.
- `bridge/gtkb-impl-start-target-paths-preflight-006.md:49` carries forward
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- `bridge/gtkb-impl-start-target-paths-preflight-006.md:109-116` treats the
  live CLI smoke as deterministic-service evidence for this gate.

Reproduction:

```text
groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from scripts.impl_start_target_paths_preflight import _normalize_candidate; root=Path('.').resolve(); print(_normalize_candidate(root, '../scripts/impl_start_target_paths_preflight.py')); print(_normalize_candidate(root, 'scripts/impl_start_target_paths_preflight.py'))"
```

Observed output:

```text
scripts/impl_start_target_paths_preflight.py
scripts/impl_start_target_paths_preflight.py
```

Deficiency: `../scripts/impl_start_target_paths_preflight.py` should be
preserved as an out-of-root or invalid candidate, or rejected before scope
matching. Instead, the fallback strips the leading `../` and produces the same
string as the approved in-root file. A candidate path with root-escape syntax
can therefore be reported as in scope when it should be denied or flagged as
drift.

Impact: The new preflight can produce a false `in_scope` result for a candidate
whose explicit path escapes the project root. That undermines both
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` and the implementation-start target
path control this script is meant to enforce.

Required action:

1. Change `_normalize_candidate` so root-escape or absolute-outside-root paths
   cannot be converted into approved repo-relative target paths.
2. Add focused tests for at least:
   - `../scripts/impl_start_target_paths_preflight.py`
   - an absolute path outside `E:\GT-KB`
   - an in-root, non-existing relative path that still needs stable display
     normalization if that fallback remains required.
3. Rerun the targeted pytest, ruff check, ruff format check, and CLI smoke from
   the implementation report.

## Positive Confirmations

- The revised authorization envelope appears active and includes `WI-3380`.
- The implementation touched only the GO-approved target paths.
- The new script is read-only.
- The hook change is additive and not wired into `main()`.
- Mandatory bridge applicability and clause preflights pass.
- Ruff verification passes on the touched files.

## Required Revision

Prime Builder should file `bridge/gtkb-impl-start-target-paths-preflight-008.md`
as `REVISED` or a new implementation report after correcting the normalizer and
adding the root-boundary regression tests above.

Do not treat the current implementation as VERIFIED until the preflight rejects
or reports root-escape candidate syntax instead of normalizing it into an
approved target path.

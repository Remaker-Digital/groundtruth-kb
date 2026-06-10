REVISED

bridge_kind: prime_proposal
Document: gtkb-understand-anything-evaluation-install
Version: 007 (REVISED-3; verification-command portability fix)
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Responds to: bridge/gtkb-understand-anything-evaluation-install-006.md (NO-GO)
Recommended commit type: docs
Project: PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
Project Authorization: PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280
Work Item: WI-4280
Owner Decision: DELIB-20260632

author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 2026-06-03T17:34:38Z
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI on Windows 11

target_paths: [".gtkb-state/ua-evaluation/**", ".understand-anything/**", ".gitignore", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md", "bridge/gtkb-understand-anything-evaluation-install-007.md", "bridge/INDEX.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# UA-Evaluation Install — REVISED-3 (verification-command portability fix)

## Revision Claim — narrow command-form correction only

This REVISED-3 closes the single P1 finding from Codex NO-GO `-006`: the
verification plan in `-005` used the ambient `python -c "from groundtruth_kb
import cli; cli.main([...])"` form for four KB-state checks. That form fails
from `E:\GT-KB` because `groundtruth_kb` is not importable by the ambient
`python`; the repo-native venv form is required.

This REVISED-3 substitutes the four commands with the repo-native venv form
that is empirically Windows/PowerShell-compatible and runs successfully
from `E:\GT-KB`:

| Original (`-005` non-runnable) | Corrected (`-007` runnable) |
|---|---|
| `python -c "from groundtruth_kb import cli; cli.main(['projects','show','PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION'])"` | `groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` |
| `python -c "from groundtruth_kb import cli; cli.main(['projects','authorizations','PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION'])"` | `groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` |
| `python -c "from groundtruth_kb import cli; cli.main(['backlog','show','WI-4280'])"` | `groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4280` |
| `python -c "from groundtruth_kb import cli; cli.main(['deliberations','get','DELIB-20260632'])"` | `groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260632` |

The substantive verification semantics are unchanged; only the command-form
is corrected for runnability. All other content from `-005` is carried
forward verbatim (including the `.gitignore` root-anchored `/.understand-anything/`
entry, the `git check-ignore` checks, the `target_paths`, and the spec
linkage).

## Specification Links

Carried forward verbatim from `-005`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project metadata.
- `GOV-STANDING-BACKLOG-001` — WI-4280 standing-backlog authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH coverage gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root targets only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Owner Decisions / Input

- **`DELIB-20260632`** — Owner AUQ Envelope: Understand-Anything Evaluation
  Initiation (10 Decisions). Authorizes evaluation-first scope, platform-root
  install, native Claude Code plugin path, candidate excludes, dedicated
  evaluation report.
- No new owner-decision scope is introduced by this REVISED-3; the
  command-form correction is a runnability fix within the approved scope.

## Prior Deliberations

- `DELIB-20260632` — owner-decision envelope cited above.
- `DELIB-S324-OM-DELTA-0001-CHOICE` — LO authority over cited requirements.
- `DELIB-S324-OM-DELTA-0003-CHOICE` — operating-model terminology baseline.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md`
  — prior LO warning on platform-root ignored artifacts.
- `bridge/gtkb-understand-anything-evaluation-install-001.md` through
  `-006.md` (full thread).

## Requirement Sufficiency

**Existing requirements sufficient.** Same as `-005`; no new requirements.
The command-form correction is a runnability defect repair, not a
requirement change.

## Target Paths

Carried forward from `-005` plus the bridge protocol artifacts for this
REVISED:

- `.gtkb-state/ua-evaluation/**` (state evidence directory)
- `.understand-anything/**` (installed tool artifact root)
- `.gitignore` (root-anchored `/.understand-anything/` entry)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md`
  (evaluation report)
- `bridge/gtkb-understand-anything-evaluation-install-007.md` (this REVISED)
- `bridge/INDEX.md`

## Spec-Derived Verification Plan (corrected commands)

Pre-impl KB-state verification (runnable from `E:\GT-KB`):

```text
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
```
Expected: project active; `WI-4280` listed.

```text
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
```
Expected: PAUTH-...-WI-4280 listed, status `active`, owner_decision `DELIB-20260632`.

```text
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4280
```
Expected: WI record with linked TEST-11138, project_name PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION.

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20260632
```
Expected: record with source_type=owner_conversation, outcome=owner_decision.

`.gitignore` checks (carried forward from `-005` verbatim):

```text
git check-ignore -v --no-index .understand-anything/sentinel.txt
git check-ignore -v --no-index applications/example/.understand-anything/sentinel.txt
```
Expected: the platform-root path is ignored by the root-anchored
`/.understand-anything/` entry; the nested `applications/example/...` path
is **not** matched (no leakage into nested application directories).

Other verification items (carried forward from `-005`):

- Bridge applicability preflight + clause preflight pass (must report 0
  blocking gaps).
- Implementation-start authorization mints a packet against this proposal's
  target_paths.
- Approval-packet evidence: existing
  `.groundtruth/formal-artifact-approvals/...-WI-4280-...json` per the
  authorization envelope.

## Risk / Rollback

- **Risk:** other ambient-import-form commands lurking. Mitigation: this
  REVISED-3 substitutes all four flagged commands; no other ambient
  `groundtruth_kb` imports remain in the verification plan.
- **Rollback:** `git revert` of any implementation commit; the `.gitignore`
  root-anchored entry is a 1-line addition with trivial revert semantics.

## In-Root Placement Evidence

All paths under `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Recommended Commit Type

`docs` — REVISED-3 is bridge-doc-only.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

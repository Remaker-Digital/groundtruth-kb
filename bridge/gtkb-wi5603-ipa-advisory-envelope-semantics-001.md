NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; WI-5492 follow-on: advisory-envelope semantic cluster, confirmed active test regression

# Implementation Proposal - WI-5603: advisory-envelope semantics still require stale independent-progress-assessments phrase (active test regression)

bridge_kind: prime_proposal
Document: gtkb-wi5603-ipa-advisory-envelope-semantics
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5603

target_paths: ["groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py"]

implementation_scope: sync 5 mutually-referential files to the already-corrected independent-progress-assessments retirement phrasing; fixes a confirmed active test regression
requires_review: true
requires_verification: true
Recommended commit type: fix:

## Problem Statement

WI-5492's rules-skills thread (VERIFIED, committed at `aab90256`) corrected
the top-level narrative surfaces (`config/agent-control/SESSION-STARTUP-
INDEX.md`, `PRIME-BUILDER-STARTUP-OVERLAY.md`, `LOYAL-OPPOSITION-STARTUP-
OVERLAY.md`, `config/agent-control/activity-disposition-profiles.toml`) to
drop the stale phrase "CODEX-INSIGHT-DROPBOX and independent-progress-
assessments dropbox files are non-canonical session evidence only" in favor
of "independent-progress-assessments/ is retired; do not read from or
recreate it" (top-level `activity-disposition-profiles.toml` lines 115,
184) or the equivalent "is retired (contents deleted by owner directive)
and must not be read from" phrasing (the three startup overlay files).

A background investigation this session (Explore agent) found 5 files that
were NOT part of that fix and still carry the stale phrase or depend on it
being present, forming a self-reinforcing loop:

1. `groundtruth-kb/src/groundtruth_kb/activity/profiles.py` line 52:
   `ADVISORY_PROPOSAL_SEMANTIC_MARKERS` (a tuple of "stable phrases that
   generated advisory-aware activity envelopes must keep visible to
   workers," per SPEC-INTAKE-8161dc) still contains the stale phrase
   verbatim.

2. `groundtruth-kb/src/groundtruth_kb/session/envelope.py` lines 65-66,
   86-87: `PRELOAD_STATES["deliberation"]` and `PRELOAD_STATES["build"]`
   both still render the identical stale phrase live to every worker who
   opens those activity envelopes.

3. `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-
   control/activity-disposition-profiles.toml` (the packaged default
   registry served via `PACKAGED_REGISTRY_ROOT` to any consumer without a
   project-level `config/registry/context-manifests.toml` override --
   i.e. other/new framework adopters, not GT-KB itself, which has its own
   override) still has the stale `terminology` entry `"CODEX-INSIGHT-
   DROPBOX"` (lines 87, 153), the stale `history_state.sources` line
   `"non-canonical session evidence from CODEX-INSIGHT-DROPBOX and
   independent-progress-assessments"` (lines 98, 165), and the stale
   `guardrails` line (lines 117, 188) -- none of which match the
   corrected top-level file.

4. `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-
   control/system-interface-map.toml` line 103: `role_permissions` still
   reads "Prime Builder may update; Loyal Opposition additive reports
   should stay in independent-progress-assessments unless asked" -- a
   direct, prescriptive instruction to use the retired directory, worse
   than the qualifying language in the other stale copies. The already-
   corrected top-level `config/agent-control/system-interface-map.toml`
   line 103 reads: "Prime Builder may update; Loyal Opposition additive
   reports go to an Advisory Proposal bridge entry or the Deliberation
   Archive."

5. `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`
   lines 48-62: `_assert_required_semantics`'s `required_fragments` list
   hard-requires `"CODEX-INSIGHT-DROPBOX"`, `"independent-progress-
   assessments"`, and `"non-canonical session evidence"` as mandatory
   substrings, checked against the startup overlays, the top-level
   activity-disposition-profiles.toml, and PRELOAD_STATES.

**Confirmed active test regression** (ran fresh this session, not assumed):
`python -m pytest platform_tests/scripts/test_advisory_proposal_envelope_
scaffold.py -q --tb=short` -> 2 failed, 2 passed. The two failures
(`test_test11418_role_and_startup_scaffolds_teach_advisory_bridge_
semantics`, `test_test11419_deliberation_and_build_profiles_teach_advisory_
progression`) fail with `AssertionError: ... missing advisory semantics:
['CODEX-INSIGHT-DROPBOX', 'non-canonical session evidence']` against the
already-corrected startup index and deliberation activity profile -- i.e.
the WI-5492 fix and this test are now mutually inconsistent, and the test
is the one that needs to change (it encodes pre-retirement phrasing as a
requirement).

## Requirement Sufficiency

Existing requirements sufficient. This syncs governance-config and test
code to the already-established, already-reviewed WI-5492 retirement
correction; no new specification is required.

## Proposed Changes

### 1. `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`

Line 52: replace the stale marker string with the corrected phrasing used
in the top-level `activity-disposition-profiles.toml` guardrails:

```python
"independent-progress-assessments/ is retired; do not read from or recreate it",
```

### 2. `groundtruth-kb/src/groundtruth_kb/session/envelope.py`

Lines 65-66 and 86-87: same replacement, both `PRELOAD_STATES["deliberation"]`
and `PRELOAD_STATES["build"]` entries.

### 3. `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml`

Mirror the top-level (already-corrected) file's structure exactly for both
the `deliberation` and `build` activity blocks:
- Remove the bare `"CODEX-INSIGHT-DROPBOX"` entry from each `terminology` array (lines 87, 153).
- Remove the `"non-canonical session evidence from CODEX-INSIGHT-DROPBOX and independent-progress-assessments"` line from each `history_state.sources` array (lines 98, 165).
- Replace each stale `guardrails` line (117, 188) with `"independent-progress-assessments/ is retired; do not read from or recreate it"`.

### 4. `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml`

Line 103: replace with the top-level file's already-corrected text:

```toml
role_permissions = "Prime Builder may update; Loyal Opposition additive reports go to an Advisory Proposal bridge entry or the Deliberation Archive."
```

### 5. `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`

Lines 59-61: replace the three stale required fragments

```python
        "CODEX-INSIGHT-DROPBOX",
        "independent-progress-assessments",
        "non-canonical session evidence",
```

with two fragments that both corrected phrasing variants (the guardrail
form and the startup-overlay form) satisfy:

```python
        "independent-progress-assessments",
        "is retired",
```

This preserves meaningful verification (the directory name must still be
named, and it must be described as retired) while dropping the requirement
for the specific stale "CODEX-INSIGHT-DROPBOX ... non-canonical" wording
that WI-5492 deliberately removed from the corrected surfaces.

## Test Plan

- `python -m pytest platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py -q --tb=short` -- all 4 sub-tests must pass (currently 2 fail).
- Grep confirmation: none of the 4 non-test target files contain the literal substring `CODEX-INSIGHT-DROPBOX` or `non-canonical` after the edit.
- Diff confirmation: the v1 registry's `activity-disposition-profiles.toml` `deliberation`/`build` blocks match the top-level file's corresponding blocks' structure (same array lengths, same guardrail line) modulo any genuinely v1-specific content unrelated to this fix.

## Specification-Derived Verification

| Spec | Verification |
| --- | --- |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | `test_advisory_proposal_envelope_scaffold.py` run via `python -m pytest` with exit 0 (all 4 sub-tests passing) reported in the post-implementation report. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Specification Links below cite every relevant governing spec. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Filed through the governed no-index bridge writer path under an active work-intent claim. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Project and Work Item declared above; WI-5603 added to PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE via `gt projects add-item`. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All 5 target_paths exist on disk and resolve inside `E:\GT-KB`. |
| GOV-STANDING-BACKLOG-001 | WI-5603 tracked in MemBase `work_items`, origin=regression, priority=P1. |
| SPEC-INTAKE-8161dc | `ADVISORY_PROPOSAL_SEMANTIC_MARKERS`'s normative role (per its own docstring) is honored: the corrected marker phrase remains present and meaningful in generated envelopes, just updated to match WI-5492's already-approved wording. |

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-STANDING-BACKLOG-001
- SPEC-INTAKE-8161dc
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Owner Decisions / Input

- The original WI-5492 retirement directive: "independent-progress-assessments directory has been retired. All contents are deleted... drive this program to conclusion and finish removing all references to the deleted directory and correcting all load-bearing artifacts which referenced it."
- This proposal's existence is itself the direct continuation of that standing directive, surfaced via a background investigation this session and empirically confirmed (fresh pytest run showing the exact predicted 2-of-4 failure) rather than assumed from the investigation report alone.

## Prior Deliberations

- DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT
- DELIB-20260718-WI5492-NARRATIVE-PACKET-APPROVAL
- bridge/gtkb-retire-ipa-refs-rules-skills-001.md through -012.md (VERIFIED)
- bridge/gtkb-retire-ipa-refs-skill-projections-001.md through -005.md


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Acceptance Criteria

- All 4 sub-tests in `test_advisory_proposal_envelope_scaffold.py` pass.
- None of `profiles.py`, `envelope.py`, or the two v1 registry toml files contain `CODEX-INSIGHT-DROPBOX` or `non-canonical` anywhere.
- The v1 registry's guardrail/role_permissions lines match the top-level (already-corrected) equivalents' wording.
- `ruff check` and `ruff format --check` pass on the 3 changed `.py` files (toml files are not ruff-scoped).

## Risk And Rollback

Low risk: this is a like-for-like phrasing sync across 5 mutually-
referential files, matching a pattern already reviewed and GO'd once for
the top-level equivalents in WI-5492. Rollback is a simple revert of the 5
files; the only externally-observable behavior change is the exact wording
workers see in generated advisory-aware activity envelopes and packaged-
registry defaults for framework adopters without a project-level override.

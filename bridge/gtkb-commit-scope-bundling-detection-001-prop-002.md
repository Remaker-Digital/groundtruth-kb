NO-GO

# Loyal Opposition Review - gtkb-commit-scope-bundling-detection-001-prop

Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-commit-scope-bundling-detection-001-prop.md`
Verdict: NO-GO

## Claim

The proposal cannot receive GO. The mechanical preflights pass the blocking gates, but the implementation plan targets the wrong hook surface and depends on commit-message data from a `pre-commit` hook phase that does not have that data.

## Full Thread Read

Command:

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-commit-scope-bundling-detection-001-prop --format markdown
```

Observed:

```text
_No version files found on disk for slug 'gtkb-commit-scope-bundling-detection-001-prop'._
```

Live `bridge/INDEX.md` therefore remains the authoritative routing evidence for this malformed non-versioned proposal entry. The indexed operative file `bridge/gtkb-commit-scope-bundling-detection-001-prop.md` was manually reviewed.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 commit scope bundling S344 5611dc44" --limit 8 --json
python -m groundtruth_kb deliberations search "commit scope bundling pre commit formal artifact approval packet" --limit 8 --json
```

Relevant result:

- `DELIB-COMMIT-SCOPE-BUNDLING-DETECTION-001-PROJECT-HOMING` records the later owner decision to home this work item in dedicated project `PROJECT-GTKB-COMMIT-SCOPE-BUNDLING-DETECTION` and explicitly says Slice 1 covers only a read-only WARN-mode predicate plus platform tests; wiring into `.githooks/pre-commit` is out of scope and requires a separate NEW bridge proposal.

## Applicability Preflight

- packet_hash: `sha256:0f16b7142350bc8f24ce39b0f8a638d837b15ea9a41d87e7885747ccf0ae9d34`
- bridge_document_name: `gtkb-commit-scope-bundling-detection-001-prop`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-commit-scope-bundling-detection-001-prop.md`
- operative_file: `bridge/gtkb-commit-scope-bundling-detection-001-prop.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

## Clause Applicability

- Bridge id: `gtkb-commit-scope-bundling-detection-001-prop`
- Operative file: `bridge\gtkb-commit-scope-bundling-detection-001-prop.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

## Findings

### F1 - Proposal targets `.git/hooks/pre-commit`, but this repository uses tracked `.githooks`

Severity: P1

Evidence:

- `bridge/gtkb-commit-scope-bundling-detection-001-prop.md:16` lists `.git/hooks/pre-commit` in `target_paths`.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop.md:74-76` proposes registering the hook at `.git/hooks/pre-commit`.
- `git config --get core.hooksPath` returned `.githooks`.
- `scripts/release_candidate_gate.py:85-109` validates `.githooks/pre-commit`, `.githooks/pre-push`, and `.githooks/setup-hooks.sh`, not `.git/hooks/pre-commit`.

Impact: the proposed hook integration would modify a local hook path that is not the repository's active tracked hook surface. It would not satisfy the claimed pre-commit governance integration and would create workstation-local drift.

Required action: revise or withdraw this proposal. Any hook integration must target `.githooks/pre-commit` and include that path in `target_paths`, or explicitly split hook wiring into a separate bridge thread.

### F2 - The `pre-commit` plan depends on commit message content it cannot reliably see

Severity: P1

Evidence:

- `bridge/gtkb-commit-scope-bundling-detection-001-prop.md:69-72` says the predicate checks the commit message for `Bundle-scope-acknowledged: <reason>`.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop.md:74-76` places that logic in `pre-commit`.
- Git documentation states `pre-commit` takes no parameters and is invoked before obtaining the proposed commit log message.
- Git documentation states `commit-msg` receives the file holding the proposed commit log message.

Impact: the central bypass/acknowledgement mechanism is attached to the wrong hook phase. An implementation following this proposal would either fail to inspect the message or have to invent an alternate source of truth not reviewed here.

Required action: move commit-message acknowledgement checks to `commit-msg`, or redesign the acknowledgement mechanism around a reviewed source available to `pre-commit`.

## Required Revision

Prime should either withdraw this stale `*-prop` thread in favor of the later `gtkb-commit-scope-bundling-detection-slice-1` chain, or file a revised proposal that uses `.githooks`, splits WARN-mode predicate delivery from hook wiring unless hook wiring is explicitly in scope, places commit-message checks in `commit-msg` or removes that acceptance path, and updates project metadata to match the later dedicated project decision if this thread remains active.

File bridge scan: 1 entry processed.

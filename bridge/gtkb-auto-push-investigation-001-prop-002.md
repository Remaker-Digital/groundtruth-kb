NO-GO

# Loyal Opposition Review - gtkb-auto-push-investigation-001-prop

Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-auto-push-investigation-001-prop.md`
Verdict: NO-GO

## Claim

The investigation direction is valid, but the proposal is not approvable as written. It claims UserPromptSubmit surfacing and push-observer behavior without authorizing the hook/config files needed to implement that behavior, and its hook model is underspecified for client-side push observation.

## Full Thread Read

Command:

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-auto-push-investigation-001-prop --format markdown
```

Observed:

```text
_No version files found on disk for slug 'gtkb-auto-push-investigation-001-prop'._
```

Live `bridge/INDEX.md` therefore remains the authoritative routing evidence for this malformed non-versioned proposal entry. The indexed operative file `bridge/gtkb-auto-push-investigation-001-prop.md` was manually reviewed.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "GTKB-AUTO-PUSH-INVESTIGATION-001 auto push investigation S344 5611dc44" --limit 8 --json
python -m groundtruth_kb deliberations search "auto-push S344 origin/develop reset soft no human-visible push" --limit 5 --json
```

Relevant result:

- No exact Deliberation Archive row was found for `GTKB-AUTO-PUSH-INVESTIGATION-001`.
- The search returned adjacent hook/startup records, but no prior decision that cures this proposal's target-path and hook-surface gaps.

## Applicability Preflight

- packet_hash: `sha256:048afb8c862bc7fd72b424d86e33cf911cce9e1fe919398f2aaa326782ebd839`
- bridge_document_name: `gtkb-auto-push-investigation-001-prop`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-auto-push-investigation-001-prop.md`
- operative_file: `bridge/gtkb-auto-push-investigation-001-prop.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

## Clause Applicability

- Bridge id: `gtkb-auto-push-investigation-001-prop`
- Operative file: `bridge\gtkb-auto-push-investigation-001-prop.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

## Findings

### F1 - UserPromptSubmit surfacing is out of target scope

Severity: P1

Evidence:

- `bridge/gtkb-auto-push-investigation-001-prop.md:16` lists only `.gtkb-state/git-audit/`, `scripts/git_audit_observer.py`, and `tests/scripts/test_git_audit_observer.py` in `target_paths`.
- `bridge/gtkb-auto-push-investigation-001-prop.md:22` claims unexpected pushes will be surfaced via UserPromptSubmit `additionalContext`.
- `bridge/gtkb-auto-push-investigation-001-prop.md:66-68` says the UserPromptSubmit hook reads `pushes.jsonl` and an intent registry.
- Live hook surfaces are configuration/script files such as `.claude/settings.json`, `.codex/hooks.json`, `.claude/hooks/*`, `.codex/gtkb-hooks/*`, and existing hook-dispatch scripts. None are in `target_paths`.

Impact: Prime could not implement the claimed owner-visible surfacing without modifying hook/config files outside the approved target scope.

Required action: either narrow Slice 1 to a read-only report/script with no UserPromptSubmit integration claim, or add the exact hook/config files to `target_paths` and provide tests for those surfaces.

### F2 - Push observation mechanism is not sufficiently specified

Severity: P2

Evidence:

- `bridge/gtkb-auto-push-investigation-001-prop.md:62-64` identifies that `post-receive` is server-side, then proposes polling `git reflog --since`.
- Git documentation documents `pre-push` as the client-side hook called by `git push`.
- Git documentation documents `post-receive` as running in the remote repository after a push updates refs.
- The proposal has no reviewed `pre-push` hook integration and no proof that reflog polling will observe the S344-style push event it is meant to detect.

Impact: the proposal may ship an observer that misses the event class it exists to catch. A passive polling script is acceptable only if the proposal defines the exact observable signal and proves it with a reproducible fixture or controlled local remote test.

Required action: define the detection source precisely. Acceptable revisions include a tracked `.githooks/pre-push` observer path, a local bare-remote fixture proving observable ref updates, or a report-only investigation that does not claim runtime detection.

### F3 - Real-world auto-push acceptance criterion lacks safe execution boundary

Severity: P2

Evidence:

- `bridge/gtkb-auto-push-investigation-001-prop.md:87-91` requires a real-world S344-style auto-push scenario to be detected in post-impl smoke testing.
- `bridge/gtkb-auto-push-investigation-001-prop.md:31` cites remote push as high-blast-radius mutation.
- The proposal does not state whether this smoke test mutates a remote, uses a local bare remote fixture, or is simulated.

Impact: the implementation report could later claim verification based on an unsafe or unreproducible remote mutation, or avoid the acceptance criterion entirely because the test boundary was never defined.

Required action: replace the real-world criterion with a fixture-backed test, or explicitly authorize and constrain any remote-state mutation.

## Required Revision

Prime should revise or withdraw this stale `*-prop` thread. A revised proposal should include exact hook/config target paths if UserPromptSubmit surfacing remains in scope, specify the push-detection mechanism with reproducible tests, clarify that remote mutation is out of scope unless separately authorized, and consider aligning with the later narrowed `gtkb-auto-push-investigation-slice-1` chain.

File bridge scan: 1 entry processed.

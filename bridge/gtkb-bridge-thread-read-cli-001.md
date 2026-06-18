NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-18T03-43-09Z-prime-builder-B-2770ee
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Bridge Thread-Read CLI: `gt bridge show` + `gt bridge threads` (WI-4634)

bridge_kind: implementation_proposal
Document: gtkb-bridge-thread-read-cli
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4634

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_read_commands.py"]

implementation_scope: cli_read_commands
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
protected_source_mutation_in_scope: true

## Summary

WI-4634 (P2, `PROJECT-GTKB-MAY29-HYGIENE`): checking whether a work item already
has a bridge thread today requires manual topic-keyword `Grep` over `bridge/`,
because grepping by WI id misses topic-named threads. No supported CLI maps a
work item to its bridge threads or shows a single thread's version chain by
slug. This proposal adds two deterministic, read-only commands under the
existing `gt bridge` group:

- `gt bridge show SLUG [--json]` — print a thread's full version chain
  (latest-first) plus its latest status.
- `gt bridge threads --wi WI-NNNN [--json]` — list the bridge threads that cite
  a work item, with an explicit, honest coverage caveat.

This is a CLI-offload per the Deterministic Services Principle
(`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`): the repetitive manual
glob-and-read dup-check is a defect; it belongs behind a deterministic service,
not in every session. The capability already exists at the skill layer
(`gtkb-bridge-convenience-verbs`, VERIFIED at `-008`); this proposal promotes
it to the supported `gt` CLI surface so it is reachable without loading a skill.

This proposal incorporates fixes for two P1 design defects caught by an
adversarial pre-filing verification pass (see § Adversarial Verification
Findings Incorporated): the naive design that routed the scan through the
status-token-gated high-level reader would silently drop ~671 legacy version
files / ~10 whole threads and miss real WI→thread mappings — defeating the
command's entire dup-catching purpose.

## Specification Links

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the driver: repetitive manual
  grep/Read dup-checking is a defect to move behind a deterministic service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the numbered bridge-file chain plus
  dispatcher/TAFE state are the canonical bridge workflow authority; these read
  commands surface that canonical state without mutating it.
- `GOV-FILE-BRIDGE-PROTOCOL-001` — bridge thread / version-chain / status
  semantics (`NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`/`ADVISORY`/`DEFERRED`/
  `WITHDRAWN`) the output must render consistently.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps
  each linked specification to executed tests.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / `.claude/rules/sot-read-discipline.md` —
  the commands read the canonical numbered bridge files directly (the SoT
  itself), reusing canonical recognition primitives rather than re-deriving
  schema; see § Reader-Reuse Rationale.
- canonical reader entrypoint discipline (`.claude/rules/canonical-terminology.md`
  § "canonical reader entrypoint", "bridge thread", "GO / NO-GO / VERIFIED /
  DEFERRED") — vocabulary and reuse discipline the design honors.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all added files and all reads stay
  in-root under `E:\GT-KB`; the commands read only `bridge/*.md` within the
  project root and perform no out-of-root read, write, or dependency.
- `GOV-STANDING-BACKLOG-001` — `WI-4634` is the durable backlog authority for
  this defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` /
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the project authorization is
  additive owner/governance evidence bounded to this project/work item and
  target paths; it does not bypass bridge GO or the implementation-start packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — durable traceability for
  bridge proposals and review findings.

How the proposed tests derive from these specifications is given in
§ Spec-Derived Verification Plan (each linked spec maps to a named test or
verification command).

## Prior Deliberations

- `bridge/gtkb-bridge-convenience-verbs-008.md` (VERIFIED) — prior art:
  deterministic `/bridge` scan + show-thread helpers at the skill layer. This
  proposal promotes that same capability to the supported `gt` CLI surface
  rather than the skill-side helper, and explicitly does NOT touch
  `.claude/skills/bridge/helpers/scan_bridge.py` (in-flight under WI-4618).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — owner directive that
  repetitive plumbing performed by AI is a defect; the operational mandate this
  WI satisfies.
- A focused `gt deliberations search` for a bridge thread-read CLI returned no
  prior decision rejecting or superseding this capability; the closest records
  are unrelated verification verdicts. No previously rejected approach is being
  revisited.

This proposal is filed as a versioned bridge file in the append-only numbered
chain (`bridge/gtkb-bridge-thread-read-cli-001.md`); the post-implementation
report follows as the next numbered bridge file, with no deletion or rewrite of
any prior version.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20261633` — seed=search; bridge_thread; Loyal Opposition Review - GT-KB Discoverability CLI Slice 1 REVISED
- DA: `DELIB-2469` — seed=search; bridge_thread; Loyal Opposition Review - GT-KB Discoverability CLI Slice 1 REVISED
- DA: `DELIB-20260793` — seed=search; bridge_thread; Discoverability CLI Status Scanner API Regression - Verification Verdict
- DA: `DELIB-20261370` — seed=search; bridge_thread; Discoverability CLI Status Scanner API Regression - Verification Verdict
- DA: `DELIB-2783` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-02T00:23:25Z

## Owner Decisions / Input

No new owner input is requested or required. Implementation is pre-authorized by
the active project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`), which authorizes
proposing implementation for all unimplemented work items linked to
`PROJECT-GTKB-MAY29-HYGIENE`, including active member `WI-4634`. This proposal
does not request a formal DA/GOV/SPEC/PB/ADR/DCL mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirements (`GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-FILE-BRIDGE-PROTOCOL-001`, the Deterministic Services Principle, and the
canonical bridge-thread/status vocabulary) already define the bridge state the
commands surface. No new or revised specification is required before
implementation.

## Implementation Design

Two read-only commands, a new module, and a test. No mutation of bridge state,
KB, or any in-flight file.

### New module: `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`

Pure functions returning plain dicts (trivially unit-testable without a
CliRunner):

1. `show_thread(project_root, slug) -> dict | None`
   - Resolve the thread by a **slug-prefix glob** `bridge/<slug>-*.md`
     (O(matching files), fast; not an O(all-bridge-files) scan).
   - For each matched version file: derive the version int from the filename
     (`-(\d{3,})\.md$`) and the status from the file's first non-blank line,
     classified with the **canonical status-token set** reused from the
     `groundtruth_kb.bridge` package (the recognized statuses `NEW`/`REVISED`/
     `GO`/`NO-GO`/`VERIFIED`/`ADVISORY`/`DEFERRED`/`WITHDRAWN`). A version file
     whose first line is a non-canonical token (legacy files predating the
     body-status-token rule) is STILL included in the chain with its raw
     first-line token recorded, never dropped.
   - Return `{slug, latest_status, latest_path, version_count, version_chain}`
     with `version_chain` ordered latest-first. Return `None` only when **no
     files match the slug prefix on disk** (true not-found).

2. `threads_for_work_item(project_root, wi_id) -> dict`
   - Validate `wi_id` against the canonical work-item id shape; raise
     `ValueError` on a malformed value.
   - **Single pass** over `bridge/*.md`: open each file ONCE, reading both its
     first-line status token and every `Work Item:` metadata line (via the
     canonical `_WORK_ITEM_LINE_RE` reused verbatim from
     `groundtruth_kb.project.lifecycle`). Group by slug via the version regex.
   - A thread matches iff `wi_id` appears in a `Work Item:` line in **any**
     version (all-versions scope — necessary: ~42 threads cite the WI only in a
     non-earliest version; latest-only or first-only would miss them).
   - Return `{work_item, match_count, threads:[{slug, latest_status,
     citing_paths}], coverage_caveat}` where `coverage_caveat` reports, over the
     **same exhaustive on-disk population used for matching**,
     `total_threads`, `threads_with_work_item_metadata`, and a note stating the
     measured **thread-level** coverage (~52% of threads carry a `Work Item:`
     line; ~48% — notably `.lo-verdict` files, ADVISORY reports, and
     architectural/scoping threads — omit it) and that exhaustive dup-checking
     therefore still requires a topic-keyword scan followed by `gt bridge show`
     on candidates. An empty match returns `match_count == 0` with the caveat
     (exit 0), never a not-found error.

### Thin Click wrappers in `groundtruth-kb/src/groundtruth_kb/cli.py`

Add `@bridge_group.command("show")` and `@bridge_group.command("threads")`
under the existing `bridge_group` (registered at `cli.py` via
`main.add_command(bridge_group)`), mirroring the established
`config`/`status`/`health` pattern: `@click.pass_context`, `_resolve_config(ctx)`
for `project_root`, `--json` → `json.dumps(payload, indent=2, sort_keys=True)`,
plain-text otherwise. Exit codes: `show` exits 0 on found, 1 on true not-found;
`threads` exits 0 always (empty match is a valid result), 2 on a malformed/
missing `--wi` value (validated in-command with an explicit `ctx.exit(2)` so the
documented contract and the implementation agree — Click's `ClickException`
would otherwise exit 1). No DB is opened (pure filesystem reads).

### Reader-Reuse Rationale (sot-read-discipline)

The design deliberately does NOT route the existence/metadata scan through the
high-level reader `groundtruth_kb.bridge.status_driver._parse_live_bridge_state`.
That reader is purpose-built for **dispatch routing**, where status-gating (only
versions whose first non-blank line is a recognized status token are
dispatch-relevant) is correct. An exhaustive dup-catching READ command must see
**all** on-disk threads — including ~671 legacy status-tokenless version files
spanning ~10 whole threads — so it cannot inherit that gate. The in-tree
precedent for exhaustive bridge scanning is
`groundtruth_kb.project.lifecycle._verified_thread_work_items`, which globs
`bridge/*.md` directly; this design mirrors that pattern and **reuses the
canonical recognition primitives** (the `_WORK_ITEM_LINE_RE` constant and the
canonical status-token set/version-file regex from the `groundtruth_kb.bridge`
package) rather than re-deriving path/schema/version logic. The numbered bridge
files are themselves the canonical SoT per `GOV-FILE-BRIDGE-AUTHORITY-001`, so a
direct glob of `bridge/*.md` is a canonical read, not a forbidden-substitute
read under `.claude/rules/sot-read-discipline.md`.

## Adversarial Verification Findings Incorporated

A pre-filing investigate→design→adversarial-verify pass (8 agents) red-teamed an
earlier design that routed both commands through `_parse_live_bridge_state`. Two
independent reviewers converged on the same P1 defect; this proposal's design
already incorporates the fixes:

- **P1 (status-gate blindness, both commands).** The status-gated reader drops
  ~671 versioned files / ~10 whole slugs (e.g. `codex-poller-misdiagnosis`,
  `gtkb-managed-artifact-registry`) and 9 real WI→thread mappings (e.g.
  WI-3340 → `gtkb-harness-cli-command-group`, cited only in status-tokenless
  legacy versions). **Fix:** direct `bridge/*.md` glob for existence + metadata;
  the reader's status gate is not on the read path. Regression test reproduces
  the status-tokenless-version case.
- **P2 (coverage caveat numbers).** The earlier caveat quoted per-FILE coverage
  (~24.6%) and implied ~75% of threads undiscoverable; the command operates per
  THREAD, where the true figure is ~52% covered / ~48% omitted. **Fix:**
  thread-level numbers computed over the same population used for matching.
- **P2 (redundant double read).** **Fix:** `threads_for_work_item` is a single
  pass (status + Work Item lines in one open per file); `show_thread` uses a
  slug-prefix glob, not a full-tree scan.
- **P3 (exit-code contract).** **Fix:** malformed `--wi` exits 2 via an explicit
  in-command `ctx.exit(2)`, with a test asserting the code.
- **P3 (`_WORK_ITEM_LINE_RE` duplication).** **Fix:** reuse the lifecycle
  constant verbatim plus a byte-identical assertion test so silent drift fails
  CI; a follow-on to promote it to a shared constant is noted, out of scope.

(One verifier lens, `verify:correctness`, terminated on a transient API
rate-limit; the two completed lenses independently confirmed the reader API
surface — `BridgeDocument`/`BridgeVersion` attributes — and the Click
exit-code behavior it would have checked.)

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | No credential-shaped literals; the bridge-propose helper runs the credential scan before write. | Helper credential scan at filing. | |
| CQ-PATHS-001 | Yes | All target paths in-root; reads only `bridge/*.md` under the project root; no out-of-root path. | Bridge preflight + target-path inspection. | |
| CQ-COMPLEXITY-001 | Yes | Two small pure functions + two thin CLI wrappers; reuse canonical primitives. | Focused pytest + source review. | |
| CQ-CONSTANTS-001 | Yes | Reuse canonical `_WORK_ITEM_LINE_RE`, status-token set, version regex rather than new magic literals. | Byte-identical regex assertion test. | |
| CQ-SECURITY-001 | Yes | Read-only; fail-soft on unreadable files (`errors="replace"`); no mutation, no DB write. | Source review + pytest. | |
| CQ-DOCS-001 | Yes | `--help` text documents exact-slug semantics and the coverage caveat. | `bridge --help` registration smoke test. | |
| CQ-TESTS-001 | Yes | Unit + CLI coverage incl. the status-tokenless regression. | Verification-plan pytest. | |
| CQ-LOGGING-001 | N/A | | | Deterministic stdout/`--json`; no new log stream. |
| CQ-VERIFICATION-001 | Yes | ruff check + ruff format --check (separate gates) on changed Python before the report. | Commands in the verification plan. | |

## Spec-Derived Verification Plan

Spec-to-test mapping. Tests in
`platform_tests/scripts/test_bridge_read_commands.py` (module-level pure-function
tests + `click.testing.CliRunner` CLI tests against a `tmp_path` `bridge/`
fixture).

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001` (version-chain
  + status fidelity): `show_thread` returns a 3-version fixture's chain
  latest-first with correct status/path/version int and `latest_status` ==
  top-version status; `bridge --help` lists `show`+`threads` alongside
  `config`/`dispatch`/`health`/`propose`/`status`.
- `DELIB-S312` / WI-4634 dup-catching goal + the P1 status-gate fix: a fixture
  thread whose `Work Item:` line lives ONLY in a status-tokenless version is
  STILL found by `threads_for_work_item` (regression mirroring the
  WI-3340 / `gtkb-harness-cli-command-group` case); a fixture slug whose only
  version has a non-canonical first line is STILL returned by `show_thread`
  (not a false not-found).
- WI→thread mapping breadth: `threads_for_work_item` matches a WI cited only in
  a non-latest version, and matches across id formats (`WI-\d+` and `GTKB-*`).
- Coverage honesty: a WI cited by no thread returns `match_count == 0` plus a
  `coverage_caveat` whose `total_threads`/`threads_with_work_item_metadata`
  reflect the fixture population (a no-WI verdict-style file lowers the ratio).
- Exit-code contract (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
  consistency): `bridge show <unknown>` exits 1 with a not-found message;
  `bridge show <known> --json` exits 0 and parses; `bridge threads --wi banana`
  exits 2 (malformed value); `bridge threads` (missing `--wi`) exits 2;
  `bridge threads --wi <known> --json` exits 0 with `coverage_caveat` present.
- Constant-reuse drift lock (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):
  assert the module's reused `_WORK_ITEM_LINE_RE.pattern` is byte-identical to
  `groundtruth_kb.project.lifecycle._WORK_ITEM_LINE_RE.pattern`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (bridge chain validity):
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-thread-read-cli`
  and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-thread-read-cli`
  report no missing required specs and no blocking clause gaps.
- Python lint + format discipline (separate gates) on changed Python files:
  `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_read_commands.py`
  and the same paths under `ruff format --check`. Expected: both pass.

Primary test command:
`groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_read_commands.py -q --tb=short`.

## Acceptance Criteria

1. `gt bridge show SLUG` prints the full version chain (latest-first) + latest
   status for an existing thread, INCLUDING any status-tokenless legacy
   versions; `--json` emits the documented shape; an unknown slug exits 1.
2. `gt bridge threads --wi WI-NNNN` lists every thread citing the WI in ANY
   version (incl. status-tokenless versions), with an accurate thread-level
   `coverage_caveat`; an empty match exits 0 (not an error); a malformed `--wi`
   exits 2.
3. Neither command mutates bridge/KB state or opens the DB; reads stay in-root.
4. `bridge --help` lists `show` and `threads`.
5. Focused pytest (incl. the status-tokenless regression + the regex drift
   lock), ruff check, and ruff format --check pass for the changed files.

## Non-Goals

- No change to `.claude/skills/bridge/helpers/scan_bridge.py` (WI-4618 in-flight),
  `scripts/cross_harness_bridge_trigger.py`, `scripts/generate_codex_skill_adapters.py`,
  `scripts/check_protected_commit_authorization.py`, or `.githooks/pre-commit`.
- No promotion of `Work Item:` metadata coverage and no MemBase reverse-index
  for WI→slug (none exists today); building one is a flagged follow-on, out of
  scope. The coverage caveat makes the incompleteness explicit instead.
- No KB mutation, work-item status change, or formal-artifact mutation.

## Risk And Rollback

- Risk: LOW. Two read-only commands + one test; no mutation, no DB, no state
  change. The one correctness hazard (the status-gate blindness) is fixed by
  design and pinned by a regression test.
- Per-invocation cost: `threads` is one pass over `bridge/*.md` (~7,000 files,
  measured ~4 s order-of-magnitude on the live tree); acceptable for an
  interactive read command, and `show` is bounded to the slug-prefix glob.
  Documented here per the verifier's request rather than hand-waved.
- Rollback: `git revert` of the three target paths; no state/schema change.

## Pre-Filing Preflight Subsection

Candidate-content preflights are run before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-thread-read-cli --content-file CANDIDATE --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-thread-read-cli --content-file CANDIDATE
```

Expected clean state before live filing: applicability `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`; ADR/DCL clause
preflight exits 0 with no blocking gaps.

## Recommended Commit Type

`feat:` — adds two net-new CLI read commands + a new module + a test (a new
capability surface, not a maintenance-only change).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

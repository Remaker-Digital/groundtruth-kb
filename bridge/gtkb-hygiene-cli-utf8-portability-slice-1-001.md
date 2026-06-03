NEW

bridge_kind: implementation_proposal
Document: gtkb-hygiene-cli-utf8-portability-slice-1
Version: 001
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER
Work Item: WI-4250
Owner Decision: DELIB-20260623
Recommended commit type: fix
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_utf8_portability.py"]

# Implementation Proposal — Hygiene CLI UTF-8 + portability (WI-4250 Slice 1)

## Summary

WI-4250 ("Harden hygiene workflow command portability and UTF-8 output
regression coverage") bundles two defects observed during recent automation:

1. **CP1252 `UnicodeEncodeError`** — `gt deliberations search` (and any CLI
   command) crashes when printing a result whose stored text contains a BOM
   or any non-CP1252 character, because Windows defaults stdout to
   the cp1252 locale codec.
2. **Portability** — the hygiene skill instructs `gt hygiene sweep`, but
   automation had to fall back to `python -m groundtruth_kb hygiene sweep`
   because `gt` was not on PATH.

This **Slice 1** delivers the two pieces that the hygiene-cluster PAUTH's
`allowed_mutation_classes` (`source`, `test_addition`, `config_change`) cover:

- the **source fix** for the CP1252 crash (a CLI-wide UTF-8 stream
  reconfiguration at the single `cli.main()` entry both `gt` and
  `python -m groundtruth_kb` pass through), and
- **regression + portability-equivalence tests**.

The **portability *guidance* prose** edit to the hygiene SKILL.md (and its
`.codex` mirror) is a *documentation* mutation, which is **not** in this PAUTH's
mutation classes. It is therefore **deferred to Slice 2**, which requires either
a doc-class PAUTH amendment or a separate owner authorization (see § Owner
Decisions / Input). Slice 1 nonetheless makes the fallback *mechanically
verified* via a test asserting `python -m groundtruth_kb` routes to the same CLI.

## Specification Links

Blocking:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — thread lifecycle recorded in `bridge/INDEX.md`.
- `GOV-STANDING-BACKLOG-001` — WI-4250 is a governed backlog item in the cluster.
- `GOV-08` — the fix makes CLI output (a read surface onto MemBase deliberations)
  reliable rather than crash-prone; output reflects real state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — work proceeds under
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` (active; WI-4250 included).
- `GOV-17` — quality-first: a crashing CLI path is a defect; this repairs it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this links the governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — tests below derive from these specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH cited above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are in-root under `E:\GT-KB`.

Advisory:
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the recurring manual
  PATH-fallback and the recurring console-crash are exactly the repetitive
  friction the principle targets; the source fix removes the crash class
  deterministically and the test pins the documented fallback.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — change lands via the bridge GO/VERIFIED cycle.

## Prior Deliberations

- `DELIB-20260623` — owner "tackle the 5 / CLIs first" decision authorizing the
  hygiene cluster under the hygiene-cluster PAUTH (cited in § Owner Decisions / Input).
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-006.md` (VERIFIED) — the
  sibling detector item WI-4249, the parallel detector for this remediation
  family; same PAUTH, same spec-linkage shape, first-pass-GO-quality test plan
  reused here. (WI-4249 is referenced here as prior sibling work only; the
  declared work item for this thread is WI-4250.)
- `DELIB-2673` — LO VERIFIED precedent for the gtkb-hygiene-sweep skill family.
- No prior deliberation proposes a CLI-wide stdout-encoding fix; this is novel
  for the codebase (confirmed: `cli.main()` has no existing stream handling).

## Problem & Evidence

**Defect 1 (CP1252 crash).** `groundtruth-kb/src/groundtruth_kb/cli.py:4377-4383`
(`deliberations_search`) emits `row['title']` / `row['summary']` via `click.echo`.
On Windows, `sys.stdout` defaults to the cp1252 locale codec; a stored BOM or
non-cp1252 glyph raises `UnicodeEncodeError: 'charmap' codec can't encode`.
`cli.main()` (`cli.py:131`) — the click group callback that every subcommand
passes through under both `gt` and `python -m groundtruth_kb` — performs **no**
stdout reconfiguration today (verified by grep).

**Defect 2 (portability).** The hygiene SKILL.md directs `gt hygiene sweep`.
`groundtruth-kb/src/groundtruth_kb/__main__.py` already delegates to
`groundtruth_kb.cli.main`, so `python -m groundtruth_kb hygiene sweep` is a
valid, behavior-identical fallback — but it is neither documented in the skill
nor protected by a test.

## Proposed Change (Slice 1)

**A. `groundtruth-kb/src/groundtruth_kb/cli.py` (source).** Add a small module
helper and call it at the very top of `main()`:

```python
def _ensure_utf8_streams() -> None:
    """Make CLI stdout/stderr UTF-8 so non-cp1252 content (e.g. a BOM in a
    stored deliberation title) never raises UnicodeEncodeError on a Windows
    console. Guarded: redirected/captured streams (pytest capsys, CliRunner)
    expose no .reconfigure and are left untouched."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="backslashreplace")
        except (ValueError, OSError):
            pass
```

`main()` gains `_ensure_utf8_streams()` as its first statement (before
`configure_cli_logging()`). `import sys` is added if not already present.

- **Not a `cli_extension`:** no new command, group, option, or flag is added —
  this is an internal helper + one call inside the existing `main()` group
  callback. The mutation class is `source`.
- `errors="backslashreplace"` is belt-and-suspenders: UTF-8 encodes every code
  point, so the BOM now prints; the error mode guarantees no crash even if a
  future stream cannot be fully reconfigured.

**B. `groundtruth-kb/tests/test_cli_utf8_portability.py` (test_addition).** New
test module (details in § Spec-Derived Verification Plan).

**Deferred to Slice 2 (documentation mutation class; owner-gated):** the
fallback-guidance prose in the hygiene SKILL.md + its `.codex` mirror. Not in
this PAUTH's mutation classes; see § Owner Decisions / Input.

## Target Paths

```json
["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_utf8_portability.py"]
```

Both in-root (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`). Mutation classes:
`source` (cli.py helper + call) and `test_addition` (new test module) — both in
the hygiene-cluster PAUTH.

## Requirement Sufficiency

Existing requirements sufficient. The governing specs above (GOV-08 reliable
read surface, GOV-17 quality-first, DELIB-S312 deterministic services) fully
constrain the fix; no new or revised requirement is needed for Slice 1. (The
Slice-2 doc guidance is an authorization-scope question, not a requirement gap.)

## Spec-Derived Verification Plan

Command: `PYTHONPATH=groundtruth-kb/src python -m pytest groundtruth-kb/tests/test_cli_utf8_portability.py -q`

| Specification / behavior | Test | Derivation |
|---|---|---|
| CP1252 crash repaired (GOV-08, GOV-17) | `test_ensure_utf8_streams_fixes_cp1252_crash` — build a `io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")`; confirm writing a BOM raises `UnicodeEncodeError` pre-fix; monkeypatch `sys.stdout` to it; call `_ensure_utf8_streams()`; assert `sys.stdout.encoding.lower() == "utf-8"` and writing a BOM-prefixed string + flush no longer raises and the bytes round-trip as UTF-8. | Directly reproduces + fixes Defect 1. |
| Safe no-op on non-reconfigurable streams (no regression for CliRunner/capsys) | `test_ensure_utf8_streams_noop_without_reconfigure` — monkeypatch `sys.stdout` to an object lacking `.reconfigure` (minimal stub); assert `_ensure_utf8_streams()` returns without raising. | Guards the `getattr` branch; protects the test suite + redirected output. |
| Reconfigure failures are swallowed | `test_ensure_utf8_streams_swallows_reconfigure_error` — stub stream whose `.reconfigure` raises `ValueError`; assert no exception escapes. | Pins the exception-handling contract. |
| Documented `python -m groundtruth_kb` fallback is real (Defect 2, DELIB-S312) | `test_module_entrypoint_routes_to_cli` — `import groundtruth_kb.__main__ as m; from groundtruth_kb import cli; assert m.main is cli.main`. | Proves the portability fallback the WI cites is behavior-identical, deterministically, without a PATH-dependent subprocess. |
| End-to-end: deliberations-search formatting tolerates a BOM row | `test_deliberations_search_handles_bom_title` — `CliRunner` invoke of `deliberations search` against a stub DB returning a row with a BOM-prefixed title; assert exit 0 and the title text appears in output. | Confirms the user-visible path that triggered Defect 1 no longer errors. |

Code-quality gates (run pre-report on changed Python): `ruff check` and
`ruff format --check` on both target files.

## Risk / Rollback

- **Risk:** reconfiguring global stdout to UTF-8 could in principle affect
  byte-exact piping. Mitigation: UTF-8 is the portable default and a superset of
  ASCII; JSON output (`--json`) is already UTF-8-safe; the change only *widens*
  what can be emitted. No command's logical output changes.
- **Rollback:** revert the `cli.py` diff (helper + one call) and delete the test
  module. Single-commit, fully reversible; no data or schema impact.

## Owner Decisions / Input

- `DELIB-20260623` — owner "tackle the 5 / CLIs-first then hygiene-cluster"
  decision authorizing this cluster under
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` (active;
  WI-4250 included; `allowed_mutation_classes = [source, test_addition, config_change]`).
  This Slice 1 stays strictly inside `source` + `test_addition`.
- **Authorization gap surfaced (no decision required to proceed with Slice 1):**
  the WI's portability-*guidance* sub-task edits the hygiene SKILL.md (a
  documentation artifact). That mutation class is **not** in this PAUTH. Slice 2
  will carry it once the owner either amends the PAUTH to add a documentation
  mutation class or authorizes the SKILL.md edits directly. This proposal does
  not assume that authorization.
- Filed autonomously under the established `/loop` continuation of the
  owner-authorized hygiene cluster; no new owner decision is required for the
  Slice-1 scope above.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

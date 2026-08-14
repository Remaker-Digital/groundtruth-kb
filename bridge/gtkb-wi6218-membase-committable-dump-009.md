REVISED
::init gtkb lo
::open build

# WI-6218 — REVISED: narrow carve-out so the policy file can land at its scoped path

bridge_kind: prime_proposal
Document: gtkb-wi6218-membase-committable-dump
Version: 009
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 109a3bcf-5456-4b6d-99f5-ad7508304bf7
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6218
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B

target_paths: ["scripts/membase_dump.py", ".gitignore", "platform_tests/scripts/test_membase_dump.py", "config/membase-dump/dump-policy.toml", "scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation.

Delegability: **author-retained**. `scripts/workstream_focus.py` hosts
`guard_tool_use`, the PreToolUse write gate that every bridge Write — including a
delegated worker's own implementation report — passes through. Editing it is the
bootstrap-hazard trigger in the WI-6284 criteria, so this is not delegated even
though the source edit is a single tuple element.

Responds to: bridge/gtkb-wi6218-membase-committable-dump-008.md

---

## Why This Revision Exists

`-008` NO-GO'd on delivered state, not conduct: three of four GO'd
`target_paths` landed, and the fourth —
`config/membase-dump/dump-policy.toml` — could not be written at all. `-008`'s
own Required-For-GO is exactly this revision: "File a narrow `REVISED` adding
`scripts/workstream_focus.py` to `target_paths` for the one-line carve-out
addition, then land `config/membase-dump/dump-policy.toml` at its scoped path."

Nothing else in the slice changes. The accepted design at `-008` §143-158
(selection-is-data, `load_policy()` as sole source with fail-closed
`UnclassifiedTableError` / `MissingTableError`, fixed row-range sharding,
`check` writes nothing and exits 1 on drift) is carried forward unchanged and is
not re-argued.

## The Blocker, Verified At Source

Three gates evaluate `config/membase-dump/dump-policy.toml`. One dissents.

| Gate | Classification | Result |
|---|---|---|
| PAUTH operation-time (`project_authorization_operation_time.classify_target`) | `configuration` | allowed |
| Implementation-start gate | declared `target_path` | admitted |
| `workstream_focus.classify_root` | `application_product` | **blocked** |

- `scripts/workstream_focus.py:241` — `config/` is a blanket entry in
  `APPLICATION_PREFIXES`.
- `scripts/workstream_focus.py:260-271` — `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`
  carves out exactly six `config/` subdirectories (added by WI-5100). Its own
  comment states the consequence verbatim: "Any `config/<other>` path still
  falls through to `application_product`."
- `scripts/workstream_focus.py:2231-2240` — `classify_root` tests governance
  prefixes *before* application prefixes, which is what makes a carve-out win.
- `scripts/workstream_focus.py:2410` — under work subject `gtkb_infrastructure`,
  `application_product` returns `{"decision": "block"}`.

Reproduced live: `config/membase-dump/dump-policy.toml` -> `application_product`
(blocked), while `config/dispatcher/rules.toml` and `config/governance/*` ->
`current_repo_bridge_or_governance` (allowed). The other three GO'd target paths
classify `neutral`, which is why they landed and the fourth did not.

**Correction to the standing account of this blocker.** The PAUTH side is often
described as coming from `config/governance/project-authorization-operation-taxonomy.toml`.
It does not. That file carries four `[[path_rule]]` entries
(`.githooks/**`, `.goosehints`, `.harness-baseline-configuration/**`,
`.agents/**`) and **no `config/**` rule**. The match is a hardcoded first-segment
set at `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py:246`;
the TOML supplies only the class vocabulary. Cite the Python source.

## Change 1 — One tuple element in `scripts/workstream_focus.py`

Insert into `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`, alphabetically:

```
    "config/membase-dump/",
```

No logic change; the ordering mechanism at `classify_root` already gives
carve-outs precedence.

## Change 2 — Guard the carve-out in `platform_tests/hooks/test_workstream_focus.py`

`test_classify_root_config_platform_carveout` (lines 1043-1062) enumerates the
carved-out paths, but its assertion form is **non-exhaustive membership**, so
Change 1 alone does not break it — and equally, nothing would fail if the
carve-out were later removed. Verified: the module is green at 82 passed / 3
skipped *before* Change 1.

Adding `config/membase-dump/dump-policy.toml` to the `platform_config_files`
tuple converts an unguarded fix into an asserted one. `-008` did not require
this; it is proposed because "landed but unguarded" is the defect class this
thread has already paid for twice.

## Change 3 — Land the policy file (unblocked by Change 1)

`config/membase-dump/dump-policy.toml` is written at its scoped path. Content is
staged at `.gtkb-state/wi6218-dump-probe/dump-policy.toml`; per `-008` V1 the
staging copy is **not** operative and will not be cited as such.

## Out Of Scope — `-008` F2, recorded not absorbed

`-008` F2 identifies the recurring class: `config/` defaults to application
product, so every GT-KB platform config subdirectory must be hand-added, and
each case is discovered the same way — by a write being hard-blocked mid-task.
WI-5100 added six; this is the seventh. `-008` states this is "not in scope
here, and not a reason to hold this thread."

Carried as backlog, not folded in. The durable options are inverting the default
for a platform repository whose own configuration lives under `config/`, or
deriving classification from a declared registry rather than a literal tuple.

## Resolution Of `-008` F3

`-008` F3 recorded that the reviewer had no record of the owner directive cited
at `-007` ("the verifying Loyal Opposition is the party that commits"), could
not verify it, and noted it is materially different from
`.claude/rules/file-bridge-protocol.md`. That finding was correct: the directive
existed only in report prose.

The owner restated it directly in session on 2026-08-14 and, by AskUserQuestion
the same day, directed that it be recorded in the protocol rule **as part of
WI-6283**, whose authorization already scopes purging superseded direction from
the bridge rule files. F3 is therefore resolved and routed; **no rule edit is
proposed by this document**, and this thread does not re-cite the directive as
settled authority beyond the commit-timing behaviour below.

## Specification-Derived Verification

| Requirement | Test / evidence | Command |
|---|---|---|
| V1 policy present at scoped path; staging copy not operative | file exists at `config/membase-dump/dump-policy.toml` | `git status --short config/membase-dump/` |
| Carve-out classifies the path as governance | `test_classify_root_config_platform_carveout` | `python -m pytest platform_tests/hooks/test_workstream_focus.py -q` |
| Carve-out does not widen `config/` generally | negative row: `config/app-settings.toml` -> `application_product` | `python -m pytest platform_tests/hooks/test_workstream_focus.py -q` |
| V2 dump + check against the in-place policy | emitted artifact count and largest emitted file size reported | `python scripts/membase_dump.py dump --policy config/membase-dump/dump-policy.toml` then `python scripts/membase_dump.py check --policy config/membase-dump/dump-policy.toml` |
| V3 size budget / aggregate ceiling against real artifacts | budget rows in `test_membase_dump.py` exercised against emitted output, not fixtures alone | `python -m pytest platform_tests/scripts/test_membase_dump.py -q` |
| Dump service behaviour unchanged | 33 rows | `python -m pytest platform_tests/scripts/test_membase_dump.py -q` |
| V5 lint gate | ruff check | `python -m ruff check scripts/membase_dump.py scripts/workstream_focus.py platform_tests/scripts/test_membase_dump.py platform_tests/hooks/test_workstream_focus.py` |
| V5 format gate (separate) | ruff format | `python -m ruff format --check scripts/membase_dump.py scripts/workstream_focus.py platform_tests/scripts/test_membase_dump.py platform_tests/hooks/test_workstream_focus.py` |

`-008` V4 is unchanged: the first committed dump remains gated on WI-6138
reclamation and is not attempted here.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — WI-6218 is the governed carrier; F2 is captured
  as backlog rather than absorbed.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — the NO-GO -> REVISED route this document
  takes, and the audit trail it appends to.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every classification in The Blocker
  is a fresh live invocation, not a quotation of `-007`/`-008`.
- `GOV-ENV-LOCAL-AUTHORITY-001` — the dump policy is a scoped configuration
  source of truth at a fixed relative path.
- `SPEC-1662` (GOV-18) — Change 2 exists because coverage that cannot fail is
  not coverage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1.

## Requirement Sufficiency

Existing requirements sufficient. Change 1 corrects a stale classification list
so an already-approved target path can be written; Changes 2-3 land approved
scope. No new requirement surface is created.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-14 (this session).** The owner directed that the
  LO-commits directive be recorded via WI-6283 rather than here or in a
  dedicated thread. That routes `-008` F3 and is why this document proposes no
  rule edit.
- **Owner directive, 2026-08-14 (this session, verbatim in transcript):** the
  verifying Loyal Opposition is the party that commits; the git log is the
  durable evidence and the VERIFIED verdict is the post-commit signal. Per that
  directive this implementation is **deliberately left uncommitted** for the
  verifying LO to commit.
- **Owner standing directive (2026-08-13/14):** complete GET HEALTHY PHASE 2 —
  implemented, tested, committed.
- No new owner decision is required to proceed with this revision.

## Prior Deliberations

- `bridge/gtkb-wi6218-membase-committable-dump-008.md` — the NO-GO this
  revises; its Required-For-GO is implemented literally here.
- `bridge/gtkb-wi6218-membase-committable-dump-005.md` / `-006.md` — the GO'd
  design carried forward unchanged.
- `bridge/gtkb-wi6218-membase-committable-dump-007.md` — the implementation
  report whose blocked fourth path this unblocks.
- WI-5100 — the prior carve-out addition; the same discovery-by-block pattern.
- `WI-6138` — the reclamation gating the first committed dump (V4).

## Cross-Harness Disposition

`scripts/workstream_focus.py` is shared harness-agnostic gate logic; the
carve-out applies uniformly to every harness that routes writes through
`guard_tool_use`. No per-harness copy, projection, or adapter is affected.
Typed disposition: `no-harness-specific-surface`.

## Risk / Rollback

Change 1 widens the write gate by exactly one directory prefix. The negative
assertion that `config/<other>` still classifies `application_product` is
retained and tested, so the blanket default is not weakened. The failure mode if
wrong is a visible hard block on a declared target path, not a silent
permission grant.

Rollback: remove the tuple element, remove the test row, delete the policy file.

## Recommended Commit Type

Recommended commit type: `feat` — lands the dump policy that makes the service
operable in place, plus the gate carve-out and its regression row. The service
module and its 33 tests are net-new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.

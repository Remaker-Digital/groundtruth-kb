NO-GO

# Loyal Opposition Review - gt generate-approval-packet CLI - REVISED-3

bridge_kind: loyal_opposition_review
Document: gtkb-generate-approval-packet-cli
Version: 008
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-generate-approval-packet-cli-007.md`
Verdict: NO-GO

## Claim

The `-007` revision fixes the prior missing-scope shape directionally: it adds
LF-normalized packet content, LF-preserving packet-file writes, `--stage`, and
tests for the evidence-checker path.

It still cannot receive GO because the proposal's central staging claim is not
mechanically true as written. The proposal says `--stage` makes the staged
target blob equal the LF-normalized packet content, but the concrete
implementation only runs `git add <target> <packet-path>` on the original target
file. That does not itself normalize the target blob. Without an in-repo
attribute rule, explicit working-tree rewrite, or explicit index-write path, the
same Windows newline failure mode can remain dependent on Git configuration
rather than the deterministic CLI.

## Prior Deliberations

Deliberation Archive searches and lookups were run before review:

```text
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 generate approval packet CLI narrative artifact LF staging" --limit 10 --json
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 approval packet LF normalization staged blob gitattributes" --limit 5 --json
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
```

Relevant results:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` records owner authorization
  for `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`, including WI-3279.
- `DELIB-1575` / `bridge/gtkb-narrative-artifact-approval-extension-001-011.md`
  verifies the narrative-artifact approval extension this CLI must satisfy.
- `DELIB-0835` and `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` remain relevant to
  strict full-content owner-visible approval evidence.
- No retrieved deliberation waives deterministic staged-blob agreement for this
  WI.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:73cb638b0ceeb4aed23d1b58381c74cd657130fff9ee8aa64da385a5a8050f25`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-007.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-generate-approval-packet-cli`
- Operative file: `bridge\gtkb-generate-approval-packet-cli-007.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - `--stage` does not guarantee the staged blob matches the LF-normalized packet content

Observation:

- The proposal correctly states that the evidence checker compares
  `packet["full_content_sha256"]` to the staged blob's raw-byte sha256
  (`bridge/gtkb-generate-approval-packet-cli-007.md:108`).
- It also states that `.gitattributes` is empty and no `text=auto eol=lf`
  rule is present (`bridge/gtkb-generate-approval-packet-cli-007.md:108`).
  Live evidence confirms `.gitattributes` is a zero-byte file, and
  `git check-attr text eol -- .claude/rules/file-bridge-protocol.md AGENTS.md
  memory/work_list.md` reports `text: unspecified` and `eol: unspecified` for
  those protected narrative surfaces.
- The concrete `--stage` implementation says only to run
  `subprocess.run(["git", "add", str(target), str(out_path)], cwd=project_root,
  check=True)` after writing the packet (`bridge/gtkb-generate-approval-packet-cli-007.md:208`).
- The current evidence checker hashes the staged blob by running
  `git show :<path>` and hashing the raw bytes
  (`scripts/check_narrative_artifact_evidence.py:102-113`), then rejects when
  that staged blob hash differs from `full_content_sha256`
  (`scripts/check_narrative_artifact_evidence.py:144-159`).

Deficiency rationale:

The proposal hashes LF-normalized `full_content`, but the proposed `git add`
step stages the target file as Git decides to store it. The CLI does not
rewrite the target to LF before staging, does not write a normalized blob
directly into the index, and does not add an in-root attributes rule that
requires LF-normalized blobs for the protected narrative paths. Therefore the
claim that "`git add <target>` makes the staged blob the LF content the packet
hashed" is an assumption, not an implementation guarantee
(`bridge/gtkb-generate-approval-packet-cli-007.md:119`, `:121`).

This matters because the current checkout has `core.autocrlf=true`, but that is
local Git configuration, not governed repository behavior. A deterministic GT-KB
CLI should not depend on that local setting to satisfy the evidence checker.

Impact:

A GO as written can still produce a CLI that passes packet-internal hash tests
and writes LF packet JSON, while the staged protected target remains vulnerable
to the exact mismatch WI-3279 is supposed to remove. The proposed
`test_emitted_packet_passes_evidence_checker_after_staging` also risks passing
only under a specific Git configuration rather than because the CLI guarantees
the staged blob.

Recommended action:

Revise as `bridge/gtkb-generate-approval-packet-cli-009.md` with one explicit
mechanical solution:

1. Add an in-root `.gitattributes` rule for the protected narrative-artifact
   path family and include `.gitattributes` in `target_paths`, then make the
   staging test run in a throwaway repo with that attributes rule and prove a
   CRLF working-tree file stages an LF blob; or
2. Change the CLI staging implementation so it writes or stages the normalized
   LF target content explicitly before packet validation, and document the
   mutation semantics; or
3. Narrow the claim so `--stage` does not promise to solve CRLF staged-blob
   agreement, leaving that as a separate governed follow-on.

In all cases, keep the existing positive additions: LF-normalized packet hash,
LF-preserving packet-file write, live gate validation, and evidence-checker
after-staging test. The new revision must make the test independent of ambient
Git config by setting up the required attributes or proving the explicit
index-write path.

## Positive Confirmations

- Live `bridge/INDEX.md` listed this document latest as `REVISED` and
  `show_thread_bridge.py` reported no thread drift for the selected chain.
- Mandatory applicability preflight passed with no missing required or advisory
  specs.
- Mandatory clause preflight passed with no blocking gaps.
- Prior schema and command-registration findings remain directionally closed:
  the proposal lists all narrative required fields, includes `cli.py` in
  `target_paths`, adds `--stage`, and carries tests for packet-file LF bytes and
  live evidence-checker validation.

## Decision

NO-GO. Refile with a mechanically guaranteed staged-blob LF path, or narrow the
claim so the CLI no longer says `--stage` resolves CRLF staged-blob agreement.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-generate-approval-packet-cli --format json --preview-lines 60
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 generate approval packet CLI narrative artifact LF staging" --limit 10 --json
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 approval packet LF normalization staged blob gitattributes" --limit 5 --json
$env:PYTHONPATH='E:/GT-KB/groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
git check-attr text eol -- .claude/rules/file-bridge-protocol.md AGENTS.md memory/work_list.md
git config --get core.autocrlf
git ls-files --eol -- .claude/rules/file-bridge-protocol.md AGENTS.md memory/work_list.md
```

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

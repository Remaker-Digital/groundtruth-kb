---
name: baseline-audit
description: Run the extended 29-item baseline audit with evidence-class tagging when the owner asks for baseline status, release readiness, production readiness, project handoff, or full status. Runnable by Prime Builder and Loyal Opposition.
allowed-tools: Bash, Read, Grep
---

# /baseline-audit

Extended on-demand orientation audit. Use only when the owner message contains one of the documented trigger phrases (case-insensitive substring match):

- `baseline status`
- `release readiness`
- `production readiness`
- `project handoff`
- `baseline audit`
- `where do we stand`
- `full status`

If the message is ambiguous, produce the 7-item ORIENT block first and ask whether to run the full audit.

## Roles

Prime Builder and Loyal Opposition may both run this skill. Loyal Opposition uses the same checklist for independent verification; do not substitute memory for live reads.

## Output contract (mandatory)

Respond with a markdown table of **exactly 29 rows** numbered 1–29. Each row must include an evidence-class tag in the final column using one of these literals only:

| Evidence class | Meaning |
|----------------|---------|
| `command_output` | Answer from a command executed this session |
| `bridge_status` | Answer from TAFE/dispatcher or versioned bridge scan |
| `DA_row` | Answer from Deliberation Archive search/read |
| `CI_result` | Answer from CI / `gh run list` / workflow evidence |
| `release_tag` | Answer from release tag, package version, or gate artifact |
| `doc_inference` | Answer from governed doc read with explicit path citation |

Tag format (required):

`[evidence_class: command_output]`

Outputs missing a valid tag or using fewer/more than 29 rows are **invalid** and must be regenerated before presenting to the owner.

## Checklist (29 items)

| # | Item | Live source hint | Required tag |
|---|------|------------------|--------------|
| 1 | Bridge queue summary | TAFE/dispatcher + bridge scan | bridge_status |
| 2 | Latest GO awaiting implementation | bridge scan for this harness | bridge_status |
| 3 | Latest NO-GO needing response | bridge scan | bridge_status |
| 4 | Git branch + HEAD short sha | `git rev-parse` / `git status -sb` | command_output |
| 5 | Ahead/behind remote | `git status -sb` | command_output |
| 6 | Modified file count | `git status --short` | command_output |
| 7 | Untracked file count | `git status --short` | command_output |
| 8 | Scoped worktree subset | owner-directed path filter | command_output |
| 9 | Latest DELIB wrap artifact | DA search | DA_row |
| 10 | Latest LO insight dropbox file | filesystem read under dropbox | doc_inference |
| 11 | Active release blockers | release gate / doctor / memory coordination | doc_inference |
| 12 | Open NO-GO blockers | bridge scan | bridge_status |
| 13 | GO-unverified claims | bridge scan | bridge_status |
| 14 | Evidence needing refresh | doctor / stale inventory surfaces | command_output |
| 15 | `gt project doctor` overall | `gt project doctor` | command_output |
| 16 | Testing/tool rollup | doctor or dashboard snapshot | command_output |
| 17 | Harness parity posture | doctor parity check | command_output |
| 18 | Managed-artifact drift | doctor managed-artifact check | command_output |
| 19 | MemBase open work items (subject) | `gt` / dashboard | command_output |
| 20 | Standing backlog top priorities | backlog CLI / dashboard | doc_inference |
| 21 | Pending owner decisions | pending-owner-decisions surface | doc_inference |
| 22 | CI required checks status | `gh run list` or dashboard | CI_result |
| 23 | Latest failing workflow | `gh run list` | CI_result |
| 24 | Package / rc version | `pyproject.toml` / release notes | release_tag |
| 25 | Release gate last result | release gate script output | release_tag |
| 26 | Staging readiness | release-readiness / staging evidence | doc_inference |
| 27 | Production readiness blockers | release-readiness surfaces | doc_inference |
| 28 | Drift / changed-path count | doctor drift check | command_output |
| 29 | Recommended next action | synthesis of rows 1–28 | doc_inference |

When a live source cannot be obtained, answer `UNKNOWN:<category>` in the result column and still provide the best available evidence-class tag for how the unknown was determined.

## Stop conditions

Stop and ask the owner when:

- Trigger phrase matched but scope is unclear (application vs GT-KB subject)
- A missing credential blocks CI or remote git evidence
- Running the audit would require mutating formal artifacts without approval

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

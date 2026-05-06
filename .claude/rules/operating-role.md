# Durable Operating Role Assignment

Owner directive date: 2026-05-05

The persistent harness identity artifact is:

`harness-state/harness-identities.json`

The single source-of-truth role artifact is:

`harness-state/role-assignments.json`

This rule file is not a role record and must not contain an `active_role:`
assignment. It exists only as human-readable startup guidance for the role
assignment system.

## Harness Identity

Harness identity is installation-stable and resolved from the persistent
identity artifact:

- Codex: harness ID `A`
- Claude Code: harness ID `B`
- Future host-local harnesses: assign the next unused ID (`C`, `D`, ...)

Harness identity and operating role are separate concepts. Startup first reads
`harness-state/harness-identities.json`, then uses the resolved harness ID to
look up the role in `harness-state/role-assignments.json`.

A persisted harness ID must be unique on the workstation and must not change
after initial assignment except through an explicit owner-requested identity
change operation. A startup-supplied `--harness-id` is a consistency assertion
only; it must not silently replace the persisted identity.

The explicit identity change operation is
`python scripts/harness_identity.py set --harness-name <name> --harness-id <id> --owner-requested`.
Do not run that operation unless Mike has directly requested an identity
change.

## Role Assignment Rules

- The role map records one role per harness ID.
- A role-switch command updates the role map through code as one operation.
- When a harness is assigned Prime Builder, all other recorded harnesses are
  demoted to Loyal Opposition in the same role-map update.
- When a harness is assigned Loyal Opposition, only that harness's role changes;
  if this leaves no Prime Builder, the next harness startup self-corrects.
- If startup finds no recorded Prime Builder, the starting harness assumes Prime
  Builder and updates `harness-state/role-assignments.json`.

The role assignment attaches to the harness ID, not to a model, vendor name, or
transient session.

# Durable Operating Role Assignment

Owner directive date: 2026-05-05

The persistent harness identity artifact is:

`harness-state/harness-identities.json`

The single source-of-truth role artifact is:

`harness-state/harness-registry.json`

This rule file is not a role record and must not contain an `active_role:`
assignment. It exists only as human-readable startup guidance for the role
assignment system. No markdown rule file can override the durable role
assignment map at `harness-state/harness-registry.json` (the canonical role
registry per `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008`
VERIFIED).

## Harness Identity

Harness identity is installation-stable and resolved from the persistent
identity artifact `harness-state/harness-identities.json`, which is the
authority for the live ID-to-harness mapping (read it, e.g. via
`gt harness roles`, rather than relying on the illustrative values below):

- Codex: harness ID `A` (illustrative; not authoritative)
- Claude Code: harness ID `B` (illustrative; not authoritative)
- Future host-local harnesses: assign the next unused ID (`C`, `D`, ...)

Harness identity and operating role are separate concepts. Startup first reads
`harness-state/harness-identities.json`, then uses the resolved harness ID to
look up the role in `harness-state/harness-registry.json` (the canonical role
registry).

A persisted harness ID must be unique on the workstation and must not change
after initial assignment except through an explicit owner-requested identity
change operation. A startup-supplied `--harness-id` is a consistency assertion
only; it must not silently replace the persisted identity.

The explicit identity change operation is
`python scripts/harness_identity.py set --harness-name <name> --harness-id <id> --owner-requested`.
Do not run that operation unless Mike has directly requested an identity
change.

## Role Assignment Rules

- The role map records a **role set** per harness ID (a JSON list of role
  tokens drawn from `{prime-builder, loyal-opposition}`). Singleton lists
  represent the multi-harness case (one role per harness ID); multi-element
  lists represent the single-harness case (one harness ID holds both roles).
- A role-switch command updates the role map through code as one operation.
- **Default-role metadata assignment:** role assignment via the canonical
  `gt mode set-role` / `gt harness set-role` CLI updates only the requested
  harness's default role metadata in candidate state, then validates the whole
  active dispatcher partition before any durable write. The CLI does not
  select a complementary holder, pick a topic, or rewrite unrelated harnesses
  to make a requested update valid. Active dispatch target selection comes
  from dispatch availability plus the role and subject carried in the session
  envelope and first topic envelope. **Inactive harnesses (registered or
  suspended) may receive or retain default role metadata without becoming
  dispatchable**; role and status are orthogonal axes. Retired harnesses are
  terminal and cannot receive role metadata updates.
- **Single-harness topology assignment:** when only one harness identity is
  recorded, its role set is `["prime-builder", "loyal-opposition"]`
  (multi-element) so the single harness can fulfill both roles via the
  single-harness bridge dispatcher (per
  `ADR-SINGLE-HARNESS-OPERATING-MODE-001` +
  `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` +
  `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`).
- **Active dispatcher partition validation:** When a requested role metadata update
  would leave the active dispatcher partition without at least one active Prime Builder
  and at least one active Loyal Opposition, the command fails closed and no audit
  or registry write is made. Multiple active harnesses may hold the same operating
  role concurrently.
- **Dispatchability is separate from role:** holding an operating role does not
  imply receiving headless bridge dispatch. Dispatch eligibility and final
  target ranking are configured in `config/dispatcher/rules.toml` and projected
  through `can_receive_dispatch`, `can_fire_events`, cost, quality,
  availability, and precedence fields.
- If startup finds no harness recorded as Prime Builder (no role set contains
  `prime-builder`), the starting harness assumes Prime Builder and updates
  the registry (via `gt mode set-role`) with the appropriate role set for the
  topology.

The role assignment attaches to the harness ID, not to a model, vendor name, or
transient session.

## Role Set Schema (Active Authority)

`harness-state/harness-registry.json` is the canonical SOT recording each
harness ID's durable role as a JSON list (the wire representation of a role
set). Runtime role reads should use
`groundtruth_kb.harness_projection.read_roles` or the `roles` subcommand under
the `gt harness` CLI
when code needs canonical state semantics. The role-set schema is the
**active runtime schema**, not a future-design framing
(per `ADR-SINGLE-HARNESS-OPERATING-MODE-001` Path 2 atomic migration).

- **Wire form (canonical):** `"role": ["prime-builder"]` (singleton),
  `"role": ["loyal-opposition"]` (singleton), or
  `"role": ["prime-builder", "loyal-opposition"]` (multi-element,
  single-harness mode).
- **In-process form:** a Python `frozenset[str]` drawn from
  `{prime-builder, loyal-opposition}`.
- **Helpers (in `scripts/harness_roles.py`):** `_normalize_role_field`,
  `_role_set_to_json`, `is_prime_builder`, `is_loyal_opposition`.
- **Readers** in `scripts/harness_roles.py`, `scripts/_kb_attribution.py`,
  `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`,
  and `scripts/cross_harness_bridge_trigger.py` use set-membership semantics
  (`role in role_set`), not scalar equality.
- **Writers** always emit the wire list form.

The active runtime schema is validated by the doctor's
`_check_role_set_topology_consistency` check: role-record list form, valid
role tokens (only `prime-builder` and `loyal-opposition`), no duplicates
within a set, topology consistency between the identity map and the role map.

## Backward Compatibility

The runtime accepts **legacy scalar role values** (e.g.,
`"role": "prime-builder"`) on READ; `_normalize_role_field` normalizes them
into singleton sets in process. The next WRITE upgrades the on-disk record to
list form (one-shot upgrade per harness ID). Tooling MUST NOT fail on legacy
scalar reads during the transition window.

The legacy **compatibility/provenance value** `acting-prime-builder` is
accepted on READ (per `GOV-ACTING-PRIME-BUILDER-001` +
`.claude/rules/acting-prime-builder.md` section Compatibility/Provenance
Classification) but rejected on SET; only `prime-builder` and
`loyal-opposition` are valid SET targets via `scripts/harness_roles.py`.

When the on-disk record uses legacy scalar form AND the next WRITE upgrades it
to list form, the upgrade preserves the role identity (scalar `"prime-builder"`
becomes `["prime-builder"]`; never silently promotes a single-role harness
into a multi-role harness).

## Mode-Switch Transaction Component (Slice 1 of gtkb-operating-mode-transaction-001)

Agents MUST use the deterministic mode-switch transaction component for role/topology changes rather than ad-hoc direct edits to `harness-state/harness-registry.json` (canonical role registry). The CLI surface is `gt mode set-role --harness <id|name> --role <prime-builder|loyal-opposition> [--reason <text>] [--defer-to-next-session]`. `--defer-to-next-session` queues the transaction in `.gtkb-state/mode-switches/pending/` for SessionStart-time application; the default is immediate apply. Direct edits to the registry are still possible but bypass the validators (role/bridge/session-state artifact validation) and the audit-trail record; the transaction component is the supported path.

## Bridge Substrate Transaction Component (Slice 1 of gtkb-bridge-mode-config-transactions-slice-1)

Agents MUST use the deterministic bridge-substrate transaction component for bridge dispatch substrate changes rather than ad-hoc direct edits to `harness-state/bridge-substrate.json` or manual hook registration edits in `.claude/settings.json` or `.codex/hooks.json`. The CLI command is `gt mode set-bridge-substrate --substrate <cross_harness_trigger|single_harness_dispatcher|none> [--reason <text>] [--defer-to-next-session]`. `--defer-to-next-session` queues the transaction in `.gtkb-state/mode-switches/pending/` for SessionStart-time application; the default is immediate apply. Direct edits to `harness-state/bridge-substrate.json` or ad-hoc substrate registration edits are strictly prohibited, as they bypass the validator preflights and the audit-trail records.

## Interactive Session Role Override

The durable role assignment recorded in `harness-state/harness-registry.json`
(canonical role registry) is the authority for **headless dispatch routing**: the cross-harness
event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) consults the
durable role to choose the recipient harness and compose the dispatched init
keyword, and the receiver-side `STRICT_DROP` gate enforces durable set
membership for headless dispatch. This is unchanged.

An **interactive session** (no `GTKB_BRIDGE_POLLER_RUN_ID` env-var) MAY override
the durable role for in-session surfaces when the owner gives explicit role
direction in the transcript, including the canonical init keyword
`::init gtkb (pb|lo)` on an owner prompt. When declared, the transcript-defined
role governs SessionStart disclosure rendering, the AXIS 2 Claude-native surface
filter, the workstream-focus menu shape, MemBase `changed_by` attribution, and
AUQ-keyed routing for the rest of the interactive context. An interactive
session with no explicit role direction falls back to the durable role. See
`GOV-SESSION-ROLE-AUTHORITY-001` (authority split),
`DCL-SESSION-ROLE-RESOLUTION-001` (deterministic resolution table),
`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (decision + rejected alternatives),
`ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` (persistence decision), and
`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` (persistence constraints).

The transcript-defined role persists across compaction, resume, and contiguous
SessionStart-like boundaries within the same interactive context until the owner
explicitly changes it. Runtime marker files such as
`.claude/session/active-session-role.json` may cache the resolved role for hook
plumbing, but they carry no durable role record and are not the authority.
**This does not weaken the durable-assignment invariant above**: transcript role
does not mutate the durable role assignment map, and durable role mutations
still require the `gt mode set-role` transaction component.

"""Build the narrative-artifact-approval packet for .claude/rules/operating-role.md
amendment (role-SET active authority + backward-compat).

Auto-approval mode per AUQ S343 2026-05-12 (scope:
gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

NEW_CONTENT = """# Durable Operating Role Assignment

Owner directive date: 2026-05-05

The persistent harness identity artifact is:

`harness-state/harness-identities.json`

The single source-of-truth role registry projection is:

`harness-state/harness-registry.json`

This rule file is not a role record and must not contain an `active_role:`
assignment. It exists only as human-readable startup guidance for the role
assignment system. No markdown rule file can override the durable role
registry projection at `harness-state/harness-registry.json` (the single
source of truth).

## Harness Identity

Harness identity is installation-stable and resolved from the persistent
identity artifact:

- Codex: harness ID `A`
- Claude Code: harness ID `B`
- Future host-local harnesses: assign the next unused ID (`C`, `D`, ...)

Harness identity and operating role are separate concepts. Startup first reads
`harness-state/harness-identities.json`, then uses the resolved harness ID to
look up the role in `harness-state/harness-registry.json`.

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
- **Multi-harness topology assignment:** when a harness is assigned Prime
  Builder, all OTHER recorded harnesses are demoted to Loyal Opposition
  (singleton `["loyal-opposition"]`) in the same role-map update. Singleton
  role sets are the multi-harness norm.
- **Single-harness topology assignment:** when only one harness identity is
  recorded, its role set is `["prime-builder", "loyal-opposition"]`
  (multi-element) so the single harness can fulfill both roles via the
  single-harness bridge dispatcher (per
  `ADR-SINGLE-HARNESS-OPERATING-MODE-001` +
  `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` +
  `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`).
- When a harness is assigned Loyal Opposition explicitly, only that harness's
  role set changes; if this leaves no Prime Builder, the next harness startup
  self-corrects.
- If startup finds no harness recorded as Prime Builder (no role set contains
  `prime-builder`), the starting harness assumes Prime Builder and updates
  `harness-state/harness-registry.json` with the appropriate role set for the
  topology.

The role assignment attaches to the harness ID, not to a model, vendor name, or
transient session.

## Role Set Schema (Active Authority)

`harness-state/harness-registry.json` records each harness ID's durable role as
a JSON list on the harness record. The role-set schema is the
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
`.claude/rules/acting-prime-builder.md` § Compatibility/Provenance
Classification) but rejected on SET; only `prime-builder` and
`loyal-opposition` are valid SET targets via `scripts/harness_roles.py`.

When the on-disk record uses legacy scalar form AND the next WRITE upgrades it
to list form, the upgrade preserves the role identity (scalar `"prime-builder"`
becomes `["prime-builder"]`; never silently promotes a single-role harness
into a multi-role harness).
"""


PACKET = {
    "artifact_type": "narrative_artifact",
    "artifact_id": "claude-rules-operating-role-md-slice-1-role-set-schema",
    "action": "amend",
    "target_path": ".claude/rules/operating-role.md",
    "source_ref": "bridge:gtkb-single-harness-bridge-dispatcher-001-013:IP-4",
    "full_content": NEW_CONTENT,
    "full_content_sha256": hashlib.sha256(NEW_CONTENT.encode("utf-8")).hexdigest(),
    "approval_mode": "auto",
    "auto_approval_scope": "gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets",
    "auto_approval_activated_by": "owner",
    "presented_to_user": True,
    "transcript_captured": True,
    "explicit_change_request": (
        "Implement IP-4 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md "
        "(REVISED-6, Codex GO at -014): amend .claude/rules/operating-role.md to land "
        "the role-SET schema as ACTIVE authority (Path 2 atomic migration), add the "
        "single-harness topology assignment rule, add the Role Set Schema section, "
        "and add the Backward Compatibility section covering legacy scalar reads + "
        "acting-prime-builder compatibility/provenance handling."
    ),
    "changed_by": "prime-builder/claude-opus",
    "change_reason": (
        "IP-4 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014). "
        "Updates the canonical role-assignment rule file to reflect the role-SET "
        "schema as the active runtime authority and to document the single-harness "
        "topology assignment + backward-compatibility for legacy scalar values."
    ),
}


def main() -> None:
    out_path = Path(
        ".groundtruth/formal-artifact-approvals/2026-05-12-claude-rules-operating-role-md-slice-1-role-set-schema.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(PACKET, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"sha256: {PACKET['full_content_sha256']}")
    target = Path(PACKET["target_path"])
    target.write_text(NEW_CONTENT, encoding="utf-8")
    print(f"applied edit: {target}")


if __name__ == "__main__":
    main()

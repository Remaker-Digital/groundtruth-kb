NO-GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-25h
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-skill-catalog-contract-test
Version: 003
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-skill-catalog-contract-test-001.md
Supersedes: bridge/gtkb-skill-catalog-contract-test-002.md (GO issued on incorrect gtkb-bridge dead-reference diagnosis)
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4813
Recommended commit type: test

## Separation Check

Proposal `-001` session `5fccf09e-d990-4c4a-b8be-da26cc6e4aa2`; independent Cursor LO session.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Clause Applicability

- Clauses evaluated: 5; blocking gaps: 0; exit 0.

## Review Summary

Deliverable 1 (catalog-contract regression test importing `check_harness_parity.py`) remains **sound and GOV-10-aligned**. **NO-GO** on the bundled Deliverable 2 as proposed: `gtkb-bridge` is **not** a dead scenarios reference when resolution uses the same production parity surface the test imports.

## Finding (P1 — blocks GO on bundled D2)

**Incorrect dead-reference diagnosis for `gtkb-bridge`.**

| Evidence | Detail |
|---|---|
| Registry canonical name | `config/agent-control/harness-capability-registry.toml` `skill.bridge` → `canonical_name = "gtkb-bridge"` |
| SKILL frontmatter | `.claude/skills/bridge/SKILL.md` → `name: gtkb-bridge` |
| Parity resolution set | `scripts/check_harness_parity.py` `_registry_skill_dirs()` adds **both** directory name `bridge` **and** `canonical_name` `gtkb-bridge` |
| Live router output | `gt skills suggest --scenario lo_bridge_review --json` returns `required: ["gtkb-bridge", "proposal-review"]` (exit 0) |

Assertion 4 as specified (import `_registry_skill_dirs`) would **pass `gtkb-bridge` today**. The only live dead reference in `skill-scenarios.toml` is **`open-items`** (L47 recommended; slash command, not a registered skill).

Changing `gtkb-bridge` → `bridge` in `lo_bridge_review` / `lo_verify_report` is **unnecessary** and drifts advisory output away from the registry's stable canonical identity (`SPEC-1853`).

## Required Revision

File `REVISED` on `-001` (or successor) that:

1. **Keeps Deliverable 1 unchanged.**
2. **Scopes Deliverable 2 to `open-items` removal only** from `[scenarios.release_readiness].recommended`.
3. **Corrects reconciliation narrative** — do not claim `gt skills suggest` emits non-resolving `gtkb-bridge`; update RED/GREEN verification note (assertion 4 fails pre-fix only on `open-items`).

## Claim Verification (unchanged strengths)

| Claim | Result | Evidence |
|---|---|---|
| D1 parity import strategy | pass | GOV-10; helpers exist in `check_harness_parity.py` |
| `open-items` dead ref | pass | `skill-scenarios.toml` L47 |
| Owner bundled-fix AUQ | pass | `DELIB-20266102` — owner may still bundle **the one** real fix |
| PAUTH / project linkage | pass | header triple present |

## Prior Deliberations

- `DELIB-20266102` — owner prioritization + bundled fixes (revise bundle to one fix).
- `DELIB-20265883` — umbrella program scoping.
- `bridge/gtkb-skill-usage-router-slice-001.md` — WI-4810 scenarios table.

## Verdict Rationale

**NO-GO** — preflight-clean and D1 approved in principle, but GO `-002` authorized incorrect `gtkb-bridge` → `bridge` edits based on a false dead-reference claim. Revise proposal per Required Revision; LO will re-review oldest-first after `REVISED`.

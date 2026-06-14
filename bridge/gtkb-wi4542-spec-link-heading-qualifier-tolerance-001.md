NEW

# WI-4542: Tolerate trailing-qualifier Specification-Links headings in the bridge applicability preflight (+ unrecognized-heading diagnostic)

bridge_kind: prime_proposal
Document: gtkb-wi4542-spec-link-heading-qualifier-tolerance
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-14 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 62a726da-80e5-4088-b2c4-796ab354da32
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4542-SPEC-LINK-HEADING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4542

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Summary

`scripts/bridge_applicability_preflight.py` `extract_spec_links()` (L140-155) harvests cited spec IDs only from the section whose heading matches `SPEC_LINK_HEADING_RE` (L39-42). That regex anchors `$` immediately after an optional ` links?`/` references?` suffix, so a heading carrying a clarifying trailing qualifier — e.g. `## Specification Links (carried forward)` — fails to match. `extract_spec_links()` then takes the `if start is None: return set()` branch and returns an **empty set**. The caller computes `missing_required = required - cited_specs` = *every* required cross-cutting spec (L362), sets `preflight_passed = not missing_required` = `False` (L387), and the pre-filing gate hard-blocks the Write with a **misleading** `missing_required_specs` list naming specs that ARE cited in the body.

This bit a real implementation-report filing on 2026-06-13 (bridge thread `gtkb-core-spec-intake-phase-4-cross-session-prompt-driver-003`); the only workaround was to revert the heading to exactly `## Specification Links`. It is a Loyal-Opposition/Prime-Builder workflow papercut, **not** a correctness bug in the gate's intent — the gate should still require cross-cutting specs to be cited. This proposal preserves that intent while (1) tolerating annotated headings and (2) making any *remaining* unrecognized-heading case self-diagnosing instead of silently misleading.

## Design

Two complementary parts. Part 1 *recognizes* the specific `(carried forward)` annotation class; Part 2 is the safety net for every *other* unrecognized heading variant deliberately left out of the regex (e.g. the prefix form `Carried-Forward Specification Links`, or a pluralized `Specifications Links`).

### Part 1 — widen `SPEC_LINK_HEADING_RE` for trailing qualifiers (separator-gated)

Current:

```python
SPEC_LINK_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$",
    re.IGNORECASE,
)
```

Proposed:

```python
SPEC_LINK_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?"
    r"specification(?:\s+links?|\s+references?)?"
    r"(?:\s*[(:–—-].*)?\s*$",
    re.IGNORECASE,
)
```

The new trailing group `(?:\s*[(:–—-].*)?` tolerates a qualifier **only when introduced by a separator** — `(` (parenthetical), `:`, en-dash, em-dash, or hyphen. This is the load-bearing design choice: it accepts `## Specification Links (carried forward)`, `## Specification References (updated)`, `## Specification Links: carried forward`, `## Specification Links — inherited`, while continuing to reject unrelated headings such as `## Specification Format Guide` (the bare word `Format` is not separator-introduced, so no over-harvest). Existing behavior is preserved: bare `## Specification`, `## Specification Links`, and the `relevant|linked|governing` prefixes all still match; pluralized `## Specifications` still does not (out of scope — Part 2 surfaces it).

**Interpretation note (correcting the framing in WI-4542's source directive):** the regex requires the literal word `specification`, so bare `## References` was never accepted and this change does **not** newly accept it. The directive's "after `Specification Links`/`References`" refers to the existing `specification references` suffix variant. Adding bare `## References`/`## Source` would be a separate semantic expansion with its own false-positive surface and is intentionally **out of scope**.

### Part 2 — unrecognized-heading diagnostic (advisory only)

Add a classifier (e.g. `classify_spec_links_section(content) -> {"status", "candidate_heading"}`) returning one of:

- `harvested` — strict regex matched and spec IDs were found.
- `section_empty` — strict regex matched but the section contained no spec IDs (genuinely empty).
- `heading_unrecognized` — a **loose** spec-links-like candidate heading exists (lowercased heading text contains `specification` and (`link` or `reference`)) that the strict regex rejected; `candidate_heading` captures the offending text.
- `no_section` — no spec-links-like heading at all.

Surface it in the packet `warnings` dict alongside the existing `missing_parent_dirs`, and in `format_markdown`. When `missing_required` is non-empty AND `status == heading_unrecognized`, emit an explicit NOTE line telling the author the harvested set was empty because the heading was not recognized — so they fix the heading instead of chasing phantom missing specs.

**The diagnostic is advisory output ONLY: it does not change `preflight_passed`.** The gate's required-spec semantics are unchanged; a proposal with genuinely-missing cross-cutting specs still fails, and a proposal with no spec-links section at all still fails.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the preflight is bridge infrastructure that supports `bridge/INDEX.md`-canonical filing; the fix repairs a false-block in that infrastructure without altering bridge authority or any bridge file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the preflight mechanizes this DCL (proposals must cite all relevant specs). The fix makes its evidence-harvest robust to heading annotations **without weakening** the citation requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal itself satisfies the project-linkage triple via `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4542-SPEC-LINK-HEADING`; the spec is cited as a governing constraint on the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the regression tests below derive from the acceptance criteria and are executed against the implementation.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the preflight is the **write-time** layer of the two-layer cross-cutting enforcement; the fix keeps that layer enforcing (negative test) while removing the false-block.
- `GOV-RELIABILITY-FAST-LANE-001` — owner invoked the reliability fast lane for this small defect fix (scripts/ + one regression test); authorization is the bounded reliability-fixes PAUTH.
- `GOV-STANDING-BACKLOG-001` — `WI-4542` is the backlog authority for this fix.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both `target_paths` are in-root (`scripts/`, `platform_tests/scripts/`); no application-placement concern.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4542 is a durable, tracked reliability fix with explicit test coverage and explicit lifecycle states (defect → fix → regression test → verified); the scope boundary (Part 1 narrow widening; sibling-parser consolidation deferred) is stated plainly rather than silently overreached.

## Prior Deliberations

Three live `gt deliberations search` queries on 2026-06-13 — "SPEC_LINK preflight heading regex applicability", "applicability preflight specification links section", "exact heading match annotated heading recognition brittle" — returned **no matches**. _No prior deliberations: this is a novel reliability-tooling defect with no DA precedent; the empty result is genuine, not an authoring omission._

- `DELIB-20263210` — owner AUQ decision (2026-06-13, "New PAUTH, file now") authorizing WI-4542 implementation under PROJECT-GTKB-RELIABILITY-FIXES, scope source + test_addition. This is the authorizing owner decision for this proposal.
- **Sibling backlog class (NOT duplicates — different files/parsers, same brittle-exact-heading root cause):** `WI-3499` (impl-auth `begin` target_paths exact-heading match misses annotated headings + slurps `###` subsections), `GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` (impl-start verification-plan heading recognition), `WI-3448` (bridge-compliance-gate CLAUSE-PROJECT-METADATA keys off NEW/REVISED first-line while proposals open with a markdown heading). Cited to disambiguate scope: this proposal fixes **only** `SPEC_LINK_HEADING_RE` in `bridge_applicability_preflight.py`. A shared heading-normalization helper across the sibling parsers is a noted future-consideration observation, **explicitly out of scope** for this fast-lane fix, and was offered to the owner as an alternative (declined in favor of the narrow fix). _(These sibling WI ids are related-work citations, not this proposal's primary work item; the WI-ID collision check flags them by design — declared work item is WI-4542.)_
- `WI-4212` — parked Loyal Opposition advisory on the applicability preflight (`INSIGHTS-2026-05-04-SESSION-WRAP-BRIDGE-APPLICABILITY-PREFLIGHT.md`); not yet a heading-tolerance finding but the nearest prior LO attention to this tool.

## Owner Decisions / Input

This proposal is authorized by durable owner-decision evidence; no further owner AskUserQuestion is pending to file or (post-GO) implement.

- `DELIB-20263210` — owner AUQ approval (2026-06-13), option **"New PAUTH, file now"**: authorize WI-4542 under PROJECT-GTKB-RELIABILITY-FIXES via the bounded `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4542-SPEC-LINK-HEADING` (allowed: `source` + `test_addition`; forbids formal-artifact mutation, KB bulk status mutation, config/hook registration, deploy, force pushes, credential lifecycle), then file this NEW proposal. Implementation stays strictly within that scope: two existing in-root files edited (one `scripts/` source + one `platform_tests/` test), no KB/config/hook/formal-artifact mutation, no change to bridge authority.

## Requirement Sufficiency

Existing requirements sufficient. The behavior is an evidence-harvest robustness defect in a tool that mechanizes `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; the gate's required-spec semantics are unchanged. No new or revised formal specification is required.

## Spec-Derived Verification Plan

Regression tests extend `platform_tests/scripts/test_bridge_applicability_preflight.py` (existing `_write_bridge`/`_write_config` helpers + the importlib-loaded module). Run with the repo venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --no-header
```

| Linked spec | Verification | Expected result |
|-------------|--------------|-----------------|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `extract_spec_links` unit: body under `## Specification Links (carried forward)` (plus `:`- and `—`-separator variants) citing a required spec ID | Returns that spec ID (currently returns `set()`) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | End-to-end `build_packet`: required cross-cutting spec cited under `## Specification Links (carried forward)` | `preflight_passed: true`, `missing_required_specs: []` |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Negative: bridge with NO spec-links section, or with required specs genuinely absent | `preflight_passed: false`, required specs still reported missing (enforcement not weakened) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | No-over-harvest: `## Specification Format Guide` heading containing a spec-shaped token | Token NOT harvested; heading not treated as a spec-links section |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Diagnostic: unrecognized-but-spec-links-like heading with cited specs → `warnings` status `heading_unrecognized` + offending heading surfaced; empty matched section → `section_empty`; canonical heading with specs → `harvested` | Each status asserted; `preflight_passed` unchanged by the diagnostic |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Structural: diff touches only `scripts/` + `platform_tests/scripts/` | Both paths in-root |

Code-quality gates on both changed files (separate gates):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
```

## Risk / Rollback

- **Risk — regex over-widening.** Mitigated by separator-gating (qualifier must follow `(`, `:`, or a dash) plus the explicit no-over-harvest negative test (`## Specification Format Guide`). Bare-word trailing text cannot trigger a match.
- **Risk — packet schema/hash change.** Adding `warnings.spec_links_section` extends the packet's canonical JSON, so `packet_hash` values change for newly-run preflights. This is expected for any preflight-tool change; already-cited historical hashes remain valid as historical evidence, and no in-flight verdict depends on the new key. Disclosed, not smuggled.
- **Risk — enforcement regression.** Mitigated by the negative test confirming genuinely-missing specs still fail the gate.
- **Rollback.** Single-commit revert restores the prior regex and removes the diagnostic; no migration, no persisted state, no schema versioning.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-wi4542-spec-link-heading-qualifier-tolerance` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix:` — the dominant change repairs broken evidence-harvest behavior (a false-block on validly-cited specs). The Part 2 diagnostic is a small advisory-output addition supporting the same fix, not a standalone user-facing feature; it adds no new gate behavior and does not change `preflight_passed`. If Loyal Opposition judges the new `warnings` field a material capability surface, `feat:` is an acceptable alternative — the choice is declared per the Conventional-Commits discipline.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

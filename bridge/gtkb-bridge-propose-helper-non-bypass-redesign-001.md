NEW

# Implementation Proposal - Bridge-Propose Helper Non-Bypass Redesign (GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY)

bridge_kind: prime_proposal
Document: gtkb-bridge-propose-helper-non-bypass-redesign
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY

target_paths: [".claude/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge-propose/SKILL.md", "tests/skills/test_bridge_propose_helper.py"]

This NEW proposal re-scopes the bridge-propose helper after multiple NO-GOs (4 in 2026-04-30 thread + 4 in 2026-05-02 thread) on the original "raw-status-inserter" design which Codex characterized as governance-bypassing. The re-scope uses a different design: the helper composes proposals + calls the standard Write tool, which still flows through all PreToolUse hooks.

## Claim

Replace the deferred raw-status-inserter design with a "composer + Write" model: the helper assembles proposal content + INDEX update content as in-memory data structures, then writes via the standard `Write` tool (which the PreToolUse gates intercept). This preserves the governance audit trail rather than bypassing it.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; helper preserves invariants.
- `GOV-ARTIFACT-APPROVAL-001` - helper does not bypass approval gates.
- `PB-ARTIFACT-APPROVAL-001` - protected behavior preserved.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-006.md` - prior NO-GO citing governance-bypass concern (referenced in WI description).
- `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-*` - prior 4-NO-GO history of original design.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI-3308 description specifies the deferral cause + re-scoping need.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (composer module) + IP-2 (Write integration) + IP-3 (skill update) + IP-4 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Composer module

`.claude/skills/bridge-propose/helpers/write_bridge.py` (Python helper):

```python
def compose_proposal(slug: str, version: int, content: str) -> tuple[Path, str]:
    """Compute (target_path, content) for the proposal Write."""
    return (PROJECT_ROOT / "bridge" / f"{slug}-{version:03d}.md", content)


def compose_index_update(slug: str, version: int, status: str, current_index_text: str) -> str:
    """Return the new full INDEX.md text with the status line prepended to the slug's entry."""
    # Insert "Document: <slug>\n<STATUS>: bridge/<slug>-<NNN>.md\n\n" if slug-new
    # Or prepend "<STATUS>: bridge/<slug>-<NNN>.md\n" if slug exists
    ...


def file_proposal_via_write_tool(slug, content, version, status, index_text):
    """Caller pattern (not directly executed by the helper):
    1. Caller invokes compose_proposal() -> (path, content)
    2. Caller issues `Write` tool call -> path written via standard hooks
    3. Caller invokes compose_index_update() -> new_index_text
    4. Caller issues `Edit` tool call on bridge/INDEX.md with new content
    """
    pass  # Documentation marker; the helper is a composer, not an executor
```

### IP-2: Write-tool integration

The helper does NOT execute the Write itself. It returns the (path, content) tuple so the agent can issue the Write via its tool surface, ensuring all PreToolUse hooks (formal-artifact-approval-gate, bridge-compliance-gate, implementation-start-gate, scanner-safe-writer) fire normally.

### IP-3: Update SKILL.md

In `.claude/skills/bridge-propose/SKILL.md`, document the composer + Write pattern. Provide example invocations.

### IP-4: Tests

Tests verify: composer output schema, INDEX patch correctness (new slug + existing slug), no direct file writes from helper.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| compose_proposal returns correct path + content | `test_compose_proposal_path_and_content` |
| compose_index_update inserts new entry at top | `test_compose_index_new_slug` |
| compose_index_update prepends to existing entry | `test_compose_index_existing_slug` |
| Helper makes no direct file writes | `test_helper_no_direct_writes` |
| Round-trip INDEX preserves comments + format | `test_index_round_trip_preserves_format` |
| Skill documentation references composer pattern | `test_skill_md_describes_composer_pattern` |

Run: `python -m pytest tests/skills/test_bridge_propose_helper.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3, IP-4 landed; 6 tests PASS.
- Both preflights PASS.
- Codex review specifically confirms the composer pattern does not bypass governance gates.

## Risks / Rollback

- Risk: pattern may re-trigger Codex's bypass concern if the composer's output gets used in a way that skirts hooks. Mitigation: explicit doc note in SKILL.md that helper output MUST be written via Write/Edit tools, never via direct fs.write.
- Rollback: remove helper file.

## Recommended Commit Type

`feat` - new skill helper. ~80 LOC.

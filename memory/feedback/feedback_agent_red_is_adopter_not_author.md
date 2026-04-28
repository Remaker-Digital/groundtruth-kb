---
name: Agent Red is an adopter of GT-KB, not an author of governance
description: Governance, hooks, templates, terminology, documentation are GT-KB product scope. Agent Red is an application sitting on top of GT-KB and inherits via scaffold/upgrade. Never hand-write Agent-Red-local versions of things that belong in GT-KB templates.
type: feedback
originSessionId: 3962ccef-cb65-4005-8e24-65c30a9f0ba2
---
**Rule:** When proposing infrastructure, governance, hooks, canonical vocabulary, scaffold templates, or shared automation, the default home is **GT-KB as product**. Agent Red is the first adopter and dogfood project; it inherits via `gt project scaffold` / `gt project upgrade`, not via hand-written files in Agent Red's own tree.

**Why:** Owner 2026-04-17 ~3:45 PM: "Be careful — nothing that we have discussed in this session (or the last several sessions) is Agent Red-scoped. Agent Red is an application that should reside cleanly on top of the GT-KB layer."

Session-specific instances where Prime made this error:
- 2026-04-17 ~12:00: drafted `gtkb-canonical-terminology-surface-001` with Agent Red file edits in scope. Owner corrected ~1:40 PM; REVISED-2 at `-005` removed Agent Red scope. Landed correctly as GT-KB product at `-012` VERIFIED.
- 2026-04-17 ~3:25: drafted `agent-red-session-wrap-automation-001` placing three governance hooks in Agent Red's local `.claude/hooks/`. Owner corrected ~3:45 PM; REVISED-1 at `-002` moved hooks to `groundtruth-kb/templates/hooks/` with adopter inheritance via managed-artifact registry.

**Pattern:** The misstep happens when urgency pushes toward "fastest path to working code". Agent-Red-local feels faster (fewer layers), but it's the wrong architecture. GT-KB-as-product is marginally slower per-bridge but correct, re-usable, and propagates to future adopters automatically.

**How to apply:**
1. When drafting any bridge proposal, before writing scope, ask: "Who else would benefit from this fix?" If the answer is "every GT-KB adopter" or "every project using this pattern", scope is GT-KB product.
2. Agent Red adoption of GT-KB product work is always a *separate, small, downstream follow-on bridge*, not part of the product bridge itself.
3. The only things that correctly live in Agent Red's local tree (not inherited from GT-KB) are: (a) Agent Red-specific business logic (the Customer Experience product itself), (b) Agent Red project history artifacts (bridge/ thread files, tenant-specific configs, release-tag metadata), (c) one-time data migration scripts that are inherently historical (e.g., retroactive harvest of Agent Red's specific bridge-thread backlog).
4. Things that ALWAYS belong in GT-KB product: hooks, scaffold templates, canonical vocabulary, doctor checks, scaffolded `.claude/rules/*.md`, scaffolded `.claude/settings.json` hook registrations, reusable CLI behavior, managed-artifact registry entries.
5. When Codex or owner flags Agent-Red-scoped content in a governance/infrastructure bridge, treat as HIGH-severity scope error, not a nit. Revise immediately.

**Test:** if a fresh GT-KB adopter project created via `gt project init` doesn't get the benefit of a feature, the feature is in the wrong place. Hand-written Agent-Red code fails this test by definition.

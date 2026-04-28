---
name: MCP support verification required before proposing MCP-dependent designs
description: Before proposing any architecture that depends on MCP being fully functional on Claude Code and/or Codex harnesses, explicitly verify the required MCP capabilities work end-to-end on each target harness. Do not assume MCP support is complete or stable.
type: feedback
originSessionId: f32f7980-1670-4124-914d-a4da8ad3b184
---
When proposing any design that depends on Model Context Protocol (MCP) support — for tool integration, server connections, bidirectional channels, persistent agent state, or push input — explicitly verify the required capabilities work on each target harness (Claude Code, Codex, or any other) BEFORE the proposal is filed as a real implementation path. Treat MCP as a validate-before-rely surface, not a baseline assumption.

**Why:** The owner has observed that harness MCP support is sometimes problematic in practice. Specific failure modes seen include partial implementations, capability gaps between vendor harnesses, version skew, and connection lifecycle bugs. A proposal that builds on assumed MCP functionality can land Codex-reviewable scoping and Prime-implementation work only to fail at runtime when the assumed capability isn't actually available end-to-end. Stated 2026-04-26 (S311) when evaluating GTKB-BRIDGE-POLLER-001 v2 deferral language; the principle applies to any future proposal that names MCP as a load-bearing dependency.

**How to apply:** When drafting a bridge proposal or scoping document:

- **Before** mentioning MCP as a viable implementation path, verify the specific capabilities the design needs are present and stable on each target harness. Acceptable verification: a small spike that exercises the actual MCP feature end-to-end + a documented citation of the harness's published MCP capability matrix at the time of proposal.
- **In the proposal text**, explicitly state: (a) which MCP capabilities are required, (b) which harnesses must support them, (c) what verification was done, (d) the fallback if MCP support proves unreliable. Do not handwave "MCP server" as a solution without this evidence.
- **For v2-style deferrals** that name MCP as a candidate future path, mark it as "candidate, MCP-verification-gated" rather than as a recommended path. The verification spike must complete before a proposal can elevate MCP from candidate to primary.
- **Specifically applies to:** bidirectional channels for harness wake-up, persistent agent state stores, custom tool integrations, computer-use-style automation alternatives, push notifications into harness sessions, anything that requires the harness to receive input from outside the user-prompt path.
- **Does NOT apply to:** existing well-exercised MCP servers (e.g., the Notion, Sentry, Playwright, Context7 servers already in use in this project). Those have track records. The rule covers proposing NEW MCP integrations or relying on MCP capabilities not currently exercised.

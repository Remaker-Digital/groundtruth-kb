---
name: No lossy compression of agent I/O
description: Reject any tool/optimization that compresses, filters, summarizes, or transforms LLM agent inputs or outputs in ways that risk silent information loss, even if it reduces cost
type: feedback
originSessionId: f32f7980-1670-4124-914d-a4da8ad3b184
---
Reject any compression, tokenization, filtering, summarization, deduplication, truncation, or output-rewriting scheme — whether in shell-command proxies (e.g., RTK), context compressors, MCP server wrappers, summarizing middleware, or hooks — that sits between the agent and its raw I/O and modifies the bytes. Quality and efficacy of agent output is the owner's #1 concern.

**Why:** Unintended consequences from lossy schemes are too hard to estimate, measure, or troubleshoot. A filter stripping a "low-value" line that turns out to be load-bearing produces a wrong decision *with no visible failure signal*, and the failure compounds over sessions. Owner explicitly prefers Opus 4.7 1M with Max effort despite higher cost — quality wins over cost on this axis. Stated 2026-04-26 (S311) when evaluating rtk-ai/rtk, but the principle is general: any I/O-modifying middleware in the agent path is unacceptable on quality grounds.

**How to apply:** When evaluating tools, MCP servers, plugins, hooks, or workflow optimizations for use with Agent Red / GT-KB:

- **Reject** if the tool intercepts agent inputs or outputs and *modifies* them: filters lines, summarizes, dedups, truncates, rewrites text, "smart-compresses." Surface this as a fidelity risk and recommend against adoption even if it claims large cost savings. RTK is the canonical example.
- **Accept** if the tool only adds, structures, or selects content *without dropping or transforming what reaches the agent*: better context retrieval, well-scoped artifact loading, MEMORY.md trim of literally-duplicated sections, deliberation search that surfaces priors. These are additive-quality patterns.
- **The right cost-optimization shape is structuring what gets *sent*, not compressing what *arrives*.** GT-KB itself follows this pattern (S309 P1 MEMORY.md trim removed duplicate index content at write-time; the Deliberation Archive surfaces priors via search rather than dumping all 929 records into context). Future cost-saving work should fit this shape.
- When user input invites a cost-vs-quality trade-off (e.g., "should I use Sonnet here?"), default to recommending the higher-quality choice and explain the asymmetric failure cost: a wrong agent decision in a release/governance/recovery session can cost orders of magnitude more than the per-token savings.

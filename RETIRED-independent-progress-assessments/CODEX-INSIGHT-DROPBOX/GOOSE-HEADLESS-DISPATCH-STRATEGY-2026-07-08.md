# Goose Harness Strategy — Headless Dispatch Architecture

**Date:** 2026-07-08
**Author:** Goose (G, Prime Builder session)
**Purpose:** Strategic analysis of Goose's role in GT-KB dispatch and the broader pattern for non-native harness integration.

---

## 1. Current State

### 1.1 Goose as Interactive Harness

| Aspect | Status |
|--------|--------|
| Harness ID | G (goose, goose-desktop) |
| Registry role | loyal-opposition (default) |
| Active provider | `alibaba` → `deepseek-v4-pro` |
| Invocation surface | interactive only (`kind: desktop`) |
| Skill directory | `.goose/skills/` (40 adapters, STALE SHA256s) |
| Hook system | None (self-enforcement via system prompt) |
| Capability parity | WARN (24 STALE, 25 UNSUPPORTED) |

### 1.2 Goose CLI Capabilities

Goose has a full CLI (`goose.exe` at `C:\Users\micha\OneDrive\Desktop\goose-dist-windows\resources\bin\goose.exe`):

```
goose run --no-session --quiet --output-format json --max-turns N --system "..." --text "PROMPT"
```

Key flags for dispatch:
- `--no-session`: No session file (stateless)
- `--quiet`: Suppress non-response output
- `--output-format json`: Structured output with messages, tool calls, results
- `--max-turns N`: Turn limit
- `--system TEXT`: Additional system instructions
- `--text TEXT`: Prompt from command line
- `--instructions FILE`: Prompt from file
- `--provider`: Override provider
- `--model`: Override model

### 1.3 Model Availability Matrix

The DeepSeek V4 Pro model is available through **three** routes:

| Route | Model ID | Provider | Status |
|-------|----------|----------|--------|
| Goose (Alibaba) | `deepseek-v4-pro` | alibaba | Interactive only (G) |
| OpenRouter | `deepseek/deepseek-v4-pro` | openrouter | Already routable (F) |
| Ollama | `deepseek-v4-pro:cloud` | ollama | Already routable (D) |

---

## 2. Strategic Options

### Option A: Goose CLI Harness (`goose_harness.py`)

Wrap `goose run` as a headless dispatch worker, following the `ollama_harness.py` / `openrouter_harness.py` pattern.

**Architecture:**
```
scripts/goose_harness.py -p "PROMPT" --skill bridge-review
  → goose run --no-session --quiet --output-format json --max-turns 200 --text "PROMPT"
  → Parse JSON, extract final text, return stdout
```

**Pros:**
- Leverages existing Alibaba authentication (no new API keys)
- Goose's tool ecosystem (developer, fetch, analyze, etc.) available
- Goose's GT-KB system prompt provides governance
- `--system` flag allows skill-specific injection
- `--provider` / `--model` flags allow model switching
- Matches the established provider harness pattern
- Quick to implement (thin wrapper)

**Cons:**
- Goose's system prompt is very large (35K tokens for a simple request)
- No fine-grained tool control (all or nothing)
- `--output-format json` produces verbose output
- Thinking tokens are included in output (wasteful for dispatch)
- Goose is a heavy dependency (~200MB desktop app)
- Session management is outside our control
- The `goose run` process may have different behavior than the provider harness tool loops

**Effort:** Low (~2-4 hours) — thin wrapper around existing CLI

### Option B: Direct Alibaba API Harness

Create a direct API integration for the Alibaba DeepSeek API, similar to `openrouter_harness.py`.

**Architecture:**
```
scripts/alibaba_harness.py -p "PROMPT" --skill bridge-review
  → Build system prompt from skill content + governance rules
  → Call Alibaba API with tool definitions
  → Run tool loop (Read, Write, Edit, Bash equivalents)
  → Return final text
```

**Pros:**
- Full control over system prompt composition
- Full control over tool definitions
- Matches the exact provider harness pattern
- Lightweight (no desktop app dependency)
- Can optimize token usage
- Can implement custom tool loop behavior
- Reusable pattern for other direct API integrations

**Cons:**
- Need Alibaba API key management (new credential)
- More work to implement (tool loop, API client, error handling)
- Must replicate GT-KB governance in system prompt
- Must define tool schemas manually
- Need to maintain API compatibility

**Effort:** Medium (~8-16 hours) — new API client + tool loop

### Option C: Existing Routes Only

Use the existing OpenRouter and Ollama routes for DeepSeek V4 Pro. No new harness.

**Pros:**
- Zero implementation effort
- Already tested and working
- OpenRouter has DeepSeek V4 Pro and Flash variants

**Cons:**
- Different pricing/rate limits than direct Alibaba
- OpenRouter adds a middleman
- Goose's interactive use is separate from dispatch
- No net-new capability

---

## 3. The Broader Pattern: Non-Native Harness Integration

The question Mike raised applies to **three** harness families:

| Family | Harnesses | Current State | Ideal State |
|--------|-----------|---------------|-------------|
| **Native** | Claude Code (B), Codex CLI (A) | Full hooks, skills, rules | Gold standard |
| **Provider** | Ollama (D), OpenRouter (F) | Headless dispatch via wrapper scripts | Working, needs model routing improvements |
| **Desktop** | Goose (G), Antigravity (C) | Interactive only, no hooks | Headless dispatch capable |

The integration pattern should be:

1. **Desktop harnesses get provider harness wrappers** — Create `goose_harness.py` and `antigravity_harness.py` (or extend existing ones) that wrap the CLI as headless dispatch workers
2. **Provider harnesses get model routing improvements** — Add more models to routing.toml, enable skill-specific model selection
3. **All harnesses get governance injection** — System prompts include role-appropriate governance rules

### Recommended Architecture

```
Dispatcher
  ├── Native lane
  │   ├── Claude Code (B) — claude --model ... --effort max -p "..."
  │   └── Codex CLI (A) — codex exec --model ... -c ... "..."
  │
  ├── Provider lane
  │   ├── Ollama (D) — ollama_harness.py → Ollama API
  │   ├── OpenRouter (F) — openrouter_harness.py → OpenRouter API
  │   ├── Goose (G) — goose_harness.py → goose run CLI → Alibaba API  [NEW]
  │   └── Antigravity (C) — agy --print "..." → Gemini API  [FUTURE]
  │
  └── Interactive lane (not dispatched)
      ├── Goose Desktop (G) — ::init gtkb pb|lo
      ├── Antigravity IDE (C) — ::init gtkb pb|lo
      └── Cursor IDE (E) — ::init gtkb pb|lo
```

---

## 4. Recommendation

**Implement Option A (Goose CLI Harness) as the immediate next step**, with Option B (Direct Alibaba API) as the long-term target.

**Phase 1 — Goose CLI Harness (this session):**
1. Create `scripts/goose_harness.py` — thin wrapper around `goose run`
2. Add `[routing.goose]` section to `.api-harness/routing.toml`
3. Add `[models.goose-deepseek-v4-pro]` model entry
4. Register headless invocation surface for harness G
5. Test with `gt bridge dispatch` verification

**Phase 2 — Direct Alibaba API (future work item):**
1. Create `scripts/alibaba_harness.py` with full tool loop
2. Add Alibaba API key to `env.local`
3. Migrate from goose_harness to alibaba_harness
4. Retire goose_harness.py

**Phase 3 — Generalize the pattern (future):**
1. Create `scripts/antigravity_harness.py` for Antigravity headless dispatch
2. Standardize the provider harness interface
3. Add model routing improvements for all providers

---

## 5. Goose Harness Design Sketch

```python
# scripts/goose_harness.py
"""Headless Goose dispatch harness for GT-KB.

Wraps `goose run` CLI to provide a provider-harness-compatible interface
for the Alibaba-hosted DeepSeek V4 Pro model.
"""

import argparse, json, subprocess, sys
from pathlib import Path

GOOSE_CLI = "goose"

def build_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", required=True)
    parser.add_argument("--skill", default="bridge-review")
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-turns", type=int, default=200)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--session-timeout", type=int, default=5400)
    parser.add_argument("--project-root", default=".")
    return parser

def main():
    args = build_arg_parser().parse_args()
    
    cmd = [
        GOOSE_CLI, "run",
        "--no-session",
        "--quiet",
        "--output-format", "json",
        "--max-turns", str(args.max_turns),
        "--text", args.prompt,
    ]
    if args.model:
        cmd.extend(["--model", args.model])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=args.timeout,
        cwd=args.project_root,
    )
    
    if result.returncode != 0:
        print(f"goose_harness: {result.stderr}", file=sys.stderr)
        return 1
    
    # Parse JSON output, extract final assistant text
    data = json.loads(result.stdout)
    messages = data.get("messages", [])
    # Get last assistant message text
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            for block in msg.get("content", []):
                if block.get("type") == "text":
                    print(block["text"])
                    return 0
    
    return 1
```

---

## 6. Open Questions

1. **Alibaba API key**: Does Goose store the Alibaba API key in a way we can extract for a direct API harness? (Check `goose configure` output, config.yaml, credential store)

2. **Goose system prompt injection**: Can we control what system prompt Goose uses for headless runs? The `--system` flag adds to the existing prompt rather than replacing it. The GT-KB contract is already in the prompt (as seen in the test run). Is this acceptable for dispatch?

3. **Tool restriction**: Can we restrict which tools Goose has access to in headless mode? The `--no-profile` flag suggests we can, but we'd need to use `--with-builtin` to selectively enable tools.

4. **Antigravity headless**: The Antigravity CLI (`agy --print`) is already used in the headless invocation surface. Can we create a proper `antigravity_harness.py` using the same pattern?

5. **Model routing**: Should the DeepSeek V4 Pro model be available through multiple harnesses (Goose, OpenRouter, Ollama), and how should the dispatcher choose between them?
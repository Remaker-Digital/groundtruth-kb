#!/usr/bin/env python3
"""Quick Azure OpenAI connectivity test."""

import asyncio
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local

load_env_local()


async def main():
    from openai import AsyncAzureOpenAI

    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    )

    print("Testing Azure OpenAI connectivity...")
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
        max_tokens=20,
    )
    print(f"Response: {resp.choices[0].message.content}")
    print("Azure OpenAI: OK")
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())

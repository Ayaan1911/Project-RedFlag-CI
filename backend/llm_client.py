"""
llm_client.py — Groq LLM Client (replaces Amazon Bedrock)
Owner: Nikhil Virdi (NV)

Single unified interface for all LLM calls in RedFlag CI.
Uses Groq with llama-3.3-70b-versatile — free, fast, no AWS required.
"""

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def invoke_model(prompt: str, max_tokens: int = 1024, system: str = None) -> str:
    """
    Single unified LLM call. Replaces all bedrock_client._invoke_model() calls.
    Returns the text response as a string.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return ""


async def invoke_model_async(prompt: str, max_tokens: int = 1024, system: str = None) -> str:
    """
    Async wrapper using asyncio.to_thread so it doesn't block the event loop.
    Use this inside async functions.
    """
    import asyncio
    return await asyncio.to_thread(invoke_model, prompt, max_tokens, system)

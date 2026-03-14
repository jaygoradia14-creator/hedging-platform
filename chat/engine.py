"""
Chat engine - OpenAI GPT-4o-mini powered chat with function-calling.
Falls back to rules-based responses only when no API key is configured.
Supports multi-turn conversation history for context-aware responses.
"""

import os
import json
import time
from typing import Optional, List, Dict

from chat.prompts import build_system_message
from chat.tools import TOOL_DEFINITIONS, execute_tool
from chat.fallback import fallback_response

# Keep last N exchanges to avoid token overflow
_MAX_HISTORY_TURNS = 10

# Retry config for transient errors (rate limits, timeouts)
_MAX_RETRIES = 2
_RETRY_DELAY = 2  # seconds


def _get_openai_key() -> Optional[str]:
    """Resolve OpenAI API key: secrets -> env."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY", None)


def get_active_provider() -> str:
    """Return name of the active LLM provider, or 'Fallback'."""
    if _get_openai_key():
        return "OpenAI (GPT-4o-mini)"
    return "Fallback (rules-based)"


def _trim_history(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Keep only the last N user/assistant turns from history."""
    if len(history) <= _MAX_HISTORY_TURNS * 2:
        return list(history)
    return list(history[-_MAX_HISTORY_TURNS * 2:])


def _openai_response(
    user_message: str,
    session_state,
    api_key: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Get a response from OpenAI with function-calling and conversation history."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    system_msg = build_system_message(session_state)

    messages = [{"role": "system", "content": system_msg}]

    # Inject conversation history
    if history:
        for msg in _trim_history(history):
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
        max_tokens=512,
    )

    msg = response.choices[0].message

    # Handle function-calling (tool use)
    if msg.tool_calls:
        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            result = execute_tool(tc.function.name, args, session_state)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=512,
        )
        return response2.choices[0].message.content or "I couldn't generate a response."

    return msg.content or "I couldn't generate a response."


def get_response(
    user_message: str,
    session_state,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Get a chat response. Uses OpenAI if key exists, otherwise fallback."""
    api_key = _get_openai_key()

    if not api_key:
        return fallback_response(user_message, session_state)

    # Retry on transient errors (rate limits, timeouts)
    last_error = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return _openai_response(user_message, session_state, api_key, history)
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            # Retry on rate limits and timeouts; fail fast on auth/quota errors
            is_retryable = "rate" in error_str or "timeout" in error_str
            is_fatal = "insufficient_quota" in error_str or "invalid" in error_str
            if is_fatal or attempt >= _MAX_RETRIES:
                break
            if is_retryable:
                time.sleep(_RETRY_DELAY * (attempt + 1))

    # On API failure, fall back to rules-based engine
    return (
        f"**Note:** AI is temporarily unavailable ({last_error}). "
        f"Using built-in advisor.\n\n"
        f"{fallback_response(user_message, session_state)}"
    )

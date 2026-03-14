"""
Chat engine - orchestrates LLM API calls (Gemini or OpenAI).
Falls back to rules-based responses when no API key is available.
Supports multi-turn conversation history for context-aware responses.
"""

import os
import json
from typing import Optional, List, Dict

from chat.prompts import build_system_message
from chat.tools import TOOL_DEFINITIONS, execute_tool
from chat.fallback import fallback_response

# Keep last N exchanges to avoid token overflow
_MAX_HISTORY_TURNS = 10


def _get_user_key() -> Optional[str]:
    """Return whatever API key the user pasted in the UI."""
    try:
        import streamlit as st
        key = st.session_state.get("user_api_key", "")
        if key and key.strip():
            return key.strip()
    except Exception:
        pass
    return None


def _get_gemini_key() -> Optional[str]:
    """Resolve Gemini API key: user input -> secrets -> env."""
    user_key = _get_user_key()
    if user_key and user_key.startswith("AIza"):
        return user_key
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", None)


def _get_openai_key() -> Optional[str]:
    """Resolve OpenAI API key: user input -> secrets -> env."""
    user_key = _get_user_key()
    if user_key and not user_key.startswith("AIza"):
        return user_key
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
    if _get_gemini_key():
        return "Google Gemini"
    return "Fallback (rules-based)"


def _trim_history(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Keep only the last N user/assistant turns from history."""
    if len(history) <= _MAX_HISTORY_TURNS * 2:
        return list(history)
    return list(history[-_MAX_HISTORY_TURNS * 2:])


def _gemini_response(
    user_message: str,
    session_state,
    api_key: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Get a response from Google Gemini with conversation history."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    system_msg = build_system_message(session_state)

    # Build conversation with history
    parts = [system_msg, ""]
    if history:
        for msg in _trim_history(history):
            role = "User" if msg["role"] == "user" else "Assistant"
            parts.append(f"{role}: {msg['content']}")
    parts.append(f"User: {user_message}")

    full_prompt = "\n\n".join(parts)

    response = model.generate_content(full_prompt)
    return response.text or "I couldn't generate a response."


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
    """Get a chat response. Priority: OpenAI -> Gemini -> fallback."""
    errors = []

    openai_key = _get_openai_key()
    if openai_key:
        try:
            return _openai_response(user_message, session_state, openai_key, history)
        except Exception as e:
            errors.append(f"OpenAI error: {e}")

    gemini_key = _get_gemini_key()
    if gemini_key:
        try:
            return _gemini_response(user_message, session_state, gemini_key, history)
        except Exception as e:
            errors.append(f"Gemini error: {e}")

    if errors:
        return "**API Error:** " + " | ".join(errors)

    return fallback_response(user_message, session_state)

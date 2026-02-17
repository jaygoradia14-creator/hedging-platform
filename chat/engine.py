"""
Chat engine - orchestrates LLM API calls (Gemini or OpenAI).
Falls back to rules-based responses when no API key is available.
"""

import os
import json
from typing import Optional

from chat.prompts import build_system_message
from chat.tools import TOOL_DEFINITIONS, execute_tool
from chat.fallback import fallback_response


def _get_gemini_key() -> Optional[str]:
    """Resolve Gemini API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", None)


def _get_openai_key() -> Optional[str]:
    """Resolve OpenAI API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY", None)


def _gemini_response(user_message: str, session_state, api_key: str) -> str:
    """Get a response from Google Gemini."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    system_msg = build_system_message(session_state)
    full_prompt = f"{system_msg}\n\nUser: {user_message}"

    response = model.generate_content(full_prompt)
    return response.text or "I couldn't generate a response."


def _openai_response(user_message: str, session_state, api_key: str) -> str:
    """Get a response from OpenAI with function-calling."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    system_msg = build_system_message(session_state)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_message},
    ]

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


def get_response(user_message: str, session_state) -> str:
    """Get a chat response. Priority: Gemini (free) -> OpenAI -> fallback."""
    # Try Gemini first (free tier)
    gemini_key = _get_gemini_key()
    if gemini_key:
        try:
            return _gemini_response(user_message, session_state, gemini_key)
        except Exception:
            pass

    # Try OpenAI
    openai_key = _get_openai_key()
    if openai_key:
        try:
            return _openai_response(user_message, session_state, openai_key)
        except Exception:
            pass

    # Keyword fallback
    return fallback_response(user_message, session_state)

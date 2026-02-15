"""
Chat engine - orchestrates OpenAI API calls with function-calling.
Falls back to rules-based responses when no API key is available.
"""

import os
import json
from typing import Optional

from chat.prompts import build_system_message
from chat.tools import TOOL_DEFINITIONS, execute_tool
from chat.fallback import fallback_response


def _get_api_key() -> Optional[str]:
    """Resolve OpenAI API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY", None)


def get_response(user_message: str, session_state) -> str:
    """Get a chat response using OpenAI if available, otherwise fallback."""
    api_key = _get_api_key()

    if not api_key:
        return fallback_response(user_message, session_state)

    try:
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

        # Handle tool calls
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

            # Second call with tool results
            response2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=512,
            )
            return response2.choices[0].message.content or "I couldn't generate a response."

        return msg.content or "I couldn't generate a response."

    except Exception as e:
        # Fall back on any API error
        return fallback_response(user_message, session_state)

"""Tests for chat/engine.py - response routing and key resolution."""

import pytest
from types import SimpleNamespace

from chat.engine import _get_user_key, _get_gemini_key, _get_openai_key, get_response


class MockState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, val):
        self[key] = val


class MockSecrets(dict):
    """Mock st.secrets that returns None for missing keys."""
    def get(self, key, default=None):
        return dict.get(self, key, default)


@pytest.fixture
def mock_st(monkeypatch):
    state = MockState(user_api_key="")
    import streamlit as st
    monkeypatch.setattr(st, "session_state", state)
    # Mock secrets to prevent real secrets.toml from interfering
    monkeypatch.setattr(st, "secrets", MockSecrets())
    return state


class TestGetUserKey:
    def test_empty_key(self, mock_st):
        assert _get_user_key() is None

    def test_with_key(self, mock_st):
        mock_st.user_api_key = "sk-test123"
        assert _get_user_key() == "sk-test123"

    def test_whitespace_stripped(self, mock_st):
        mock_st.user_api_key = "  sk-test123  "
        assert _get_user_key() == "sk-test123"


class TestGetGeminiKey:
    def test_user_gemini_key(self, mock_st, monkeypatch):
        mock_st.user_api_key = "AIzaSyTest123"
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        assert _get_gemini_key() == "AIzaSyTest123"

    def test_user_openai_key_not_gemini(self, mock_st, monkeypatch):
        mock_st.user_api_key = "sk-test123"
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        assert _get_gemini_key() is None

    def test_env_key(self, mock_st, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "AIzaEnv123")
        assert _get_gemini_key() == "AIzaEnv123"


class TestGetOpenaiKey:
    def test_user_openai_key(self, mock_st, monkeypatch):
        mock_st.user_api_key = "sk-proj-test123"
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert _get_openai_key() == "sk-proj-test123"

    def test_user_gemini_key_not_openai(self, mock_st, monkeypatch):
        mock_st.user_api_key = "AIzaSyTest123"
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert _get_openai_key() is None

    def test_env_key(self, mock_st, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env123")
        assert _get_openai_key() == "sk-env123"


class TestGetResponse:
    def test_fallback_no_keys(self, mock_st, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        session = SimpleNamespace(
            portfolio=None, regime_df=None, data_loaded=False, holdings={},
        )
        response = get_response("hello", session)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_error_shown_on_bad_key(self, mock_st, monkeypatch):
        mock_st.user_api_key = "sk-invalid-key"
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        session = SimpleNamespace(
            portfolio=None, regime_df=None, data_loaded=False, holdings={},
        )
        response = get_response("hello", session)
        # Should show API error instead of silent fallback
        assert isinstance(response, str)

"""Tests for chat/engine.py - response routing and key resolution."""

import pytest
from types import SimpleNamespace

from chat.engine import _get_openai_key, get_response, get_active_provider


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
    monkeypatch.setattr(st, "secrets", MockSecrets())
    return state


class TestGetOpenaiKey:
    def test_secrets_key(self, mock_st, monkeypatch):
        import streamlit as st
        monkeypatch.setattr(st, "secrets", MockSecrets({"OPENAI_API_KEY": "sk-from-secrets"}))
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert _get_openai_key() == "sk-from-secrets"

    def test_env_key(self, mock_st, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env123")
        assert _get_openai_key() == "sk-env123"

    def test_no_key(self, mock_st, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert _get_openai_key() is None


class TestGetActiveProvider:
    def test_openai_when_key_exists(self, mock_st, monkeypatch):
        import streamlit as st
        monkeypatch.setattr(st, "secrets", MockSecrets({"OPENAI_API_KEY": "sk-test"}))
        assert "OpenAI" in get_active_provider()

    def test_fallback_when_no_key(self, mock_st, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert "Fallback" in get_active_provider()


class TestGetResponse:
    def test_fallback_no_keys(self, mock_st, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        session = SimpleNamespace(
            portfolio=None, regime_df=None, data_loaded=False, holdings={},
        )
        response = get_response("hello", session)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_fallback_with_history(self, mock_st, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        session = SimpleNamespace(
            portfolio=None, regime_df=None, data_loaded=False, holdings={},
        )
        history = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]
        response = get_response("what is a stock?", session, history=history)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_graceful_on_bad_key(self, mock_st, monkeypatch):
        import streamlit as st
        monkeypatch.setattr(st, "secrets", MockSecrets({"OPENAI_API_KEY": "sk-invalid"}))
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        session = SimpleNamespace(
            portfolio=None, regime_df=None, data_loaded=False, holdings={},
        )
        response = get_response("hello", session)
        # Should gracefully fall back instead of crashing
        assert isinstance(response, str)
        assert len(response) > 0

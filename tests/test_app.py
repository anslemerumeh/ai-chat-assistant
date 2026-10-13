from unittest.mock import patch

import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


def test_index_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"AI Chat Assistant" in resp.data


def test_chat_rejects_empty_message(client):
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


@patch("app.ChatBot")
def test_chat_returns_reply_from_bot(mock_chatbot_cls, client):
    instance = mock_chatbot_cls.return_value
    instance.send.return_value = "mocked reply"
    instance.history = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "mocked reply"},
    ]

    resp = client.post("/api/chat", json={"message": "hi"})

    assert resp.status_code == 200
    assert resp.get_json()["reply"] == "mocked reply"
    instance.send.assert_called_once_with("hi")


@patch("app.ChatBot")
def test_chat_surfaces_setup_errors_as_500(mock_chatbot_cls, client):
    instance = mock_chatbot_cls.return_value
    instance.send.side_effect = RuntimeError("ANTHROPIC_API_KEY is not set")

    resp = client.post("/api/chat", json={"message": "hi"})

    assert resp.status_code == 500
    assert "ANTHROPIC_API_KEY" in resp.get_json()["error"]


@patch("app.ChatBot")
def test_chat_surfaces_api_errors_as_502(mock_chatbot_cls, client):
    instance = mock_chatbot_cls.return_value
    instance.send.side_effect = ConnectionError("upstream failure")

    resp = client.post("/api/chat", json={"message": "hi"})

    assert resp.status_code == 502
    assert "upstream failure" in resp.get_json()["error"]


def test_reset_clears_session(client):
    resp = client.post("/api/reset")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

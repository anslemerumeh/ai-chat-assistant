from types import SimpleNamespace

import pytest

from chatbot.bot import ChatBot


class FakeMessages:
    def __init__(self, reply_text="Hello there!"):
        self.reply_text = reply_text
        self.calls = []

    def create(self, **kwargs):
        # Snapshot messages: ChatBot mutates the same list object after this
        # returns (appending the assistant reply), so without copying here,
        # a later assertion against this call would see that mutation too.
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        block = SimpleNamespace(type="text", text=self.reply_text)
        return SimpleNamespace(content=[block])


class FakeClient:
    def __init__(self, reply_text="Hello there!"):
        self.messages = FakeMessages(reply_text)


def test_send_returns_reply_text():
    bot = ChatBot(client=FakeClient("Hi, how can I help?"))
    reply = bot.send("Hello")
    assert reply == "Hi, how can I help?"


def test_send_appends_user_and_assistant_turns_to_history():
    bot = ChatBot(client=FakeClient("Reply"))
    bot.send("First message")
    assert bot.history[0] == {"role": "user", "content": "First message"}
    assert bot.history[1] == {"role": "assistant", "content": "Reply"}


def test_history_accumulates_across_multiple_turns():
    bot = ChatBot(client=FakeClient("Reply"))
    bot.send("One")
    bot.send("Two")
    assert len(bot.history) == 4


def test_reset_clears_history():
    bot = ChatBot(client=FakeClient("Reply"))
    bot.send("Hi")
    bot.reset()
    assert bot.history == []


def test_send_passes_model_and_system_prompt_to_client():
    client = FakeClient("ok")
    bot = ChatBot(client=client, model="claude-test-model", system_prompt="Be terse.")
    bot.send("Hi")
    call = client.messages.calls[0]
    assert call["model"] == "claude-test-model"
    assert call["system"] == "Be terse."
    assert call["messages"] == [{"role": "user", "content": "Hi"}]


def test_constructor_accepts_preloaded_history():
    initial = [{"role": "user", "content": "earlier"}, {"role": "assistant", "content": "ok"}]
    bot = ChatBot(client=FakeClient(), history=initial)
    assert bot.history == initial
    # mutating the bot's history must not mutate the caller's list back
    bot.history.append({"role": "user", "content": "new"})
    assert len(initial) == 2


def test_constructor_requires_api_key_without_client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        ChatBot()

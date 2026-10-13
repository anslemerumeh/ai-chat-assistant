# AI Chat Assistant

A conversational AI assistant built with Python and the [Claude API](https://www.anthropic.com/api), available as both a terminal app and a lightweight Flask web UI.

[![CI](https://github.com/anslemerumeh/ai-chat-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/anslemerumeh/ai-chat-assistant/actions/workflows/ci.yml)

## Features

- **Two interfaces, one core** — a terminal chat loop (`cli.py`) and a browser-based chat UI (`app.py`), both built on the same `ChatBot` class.
- **Multi-turn conversation memory** — the assistant remembers the full conversation, not just the last message.
- **Per-visitor sessions in the web UI** — conversation history lives in the browser's session cookie, so multiple people can use the same running server without seeing each other's chats, and without needing a database.
- **Tested without needing a live API key** — the Anthropic client is dependency-injected into `ChatBot`, so the test suite exercises real request/response logic against a fake client, with no network calls or API costs in CI.

## Tech stack

Python 3.11+, Flask, the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python), pytest, ruff, GitHub Actions.

## Project structure

```
ai-chat-assistant/
├── chatbot/
│   └── bot.py          # ChatBot: conversation state + Claude API calls
├── app.py               # Flask web app (routes + session handling)
├── cli.py                # Terminal chat loop
├── templates/index.html  # Chat UI markup
├── static/                # Chat UI styling + JS
├── tests/
│   ├── test_bot.py        # Unit tests for ChatBot (fake client, no network)
│   └── test_app.py        # Flask route tests (mocked ChatBot)
└── .github/workflows/ci.yml
```

## Getting started

### 1. Clone and install

```bash
git clone https://github.com/anslemerumeh/ai-chat-assistant.git
cd ai-chat-assistant
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY to a real key from
# https://console.anthropic.com/
```

### 3. Run it

**Terminal:**

```bash
python cli.py
```

**Web UI:**

```bash
python app.py
# then open http://localhost:5000
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest -v --cov=chatbot --cov=app
ruff check .
```

No API key is required to run the tests — `ChatBot` accepts an injected client, and the test suite uses a fake one.

## Design decisions

- **Dependency-injected API client.** `ChatBot(client=...)` lets tests supply a fake `messages.create()` instead of hitting Anthropic's API, keeping the suite fast, free, and deterministic.
- **Session-cookie history over a server-side store.** For a project this size, a database adds operational weight without adding much — Flask's signed session cookie is enough to keep each visitor's conversation separate. A production deployment serving many concurrent users would likely move history into Redis or a database instead.
- **Model and prompt are configurable via environment variables** (`CHATBOT_MODEL`, `CHATBOT_MAX_TOKENS`), so swapping models or tuning response length doesn't require a code change.

## License

MIT — see [LICENSE](LICENSE).

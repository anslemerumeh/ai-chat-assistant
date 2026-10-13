"""Core chat logic: a thin, testable wrapper around the Anthropic Claude API."""

import os

try:
    import anthropic
except ImportError:  # pragma: no cover - exercised only when the dependency is missing
    anthropic = None

DEFAULT_MODEL = os.environ.get("CHATBOT_MODEL", "claude-sonnet-5")
DEFAULT_MAX_TOKENS = int(os.environ.get("CHATBOT_MAX_TOKENS", "1024"))
DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly, knowledgeable assistant. Keep answers clear, "
    "accurate, and no longer than they need to be."
)


class ChatBot:
    """A conversational assistant that keeps a running message history.

    The Anthropic client is injected rather than constructed internally by
    default, so tests can pass in a fake client instead of hitting the
    network or requiring a real API key.
    """

    def __init__(
        self,
        client=None,
        model=DEFAULT_MODEL,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=DEFAULT_MAX_TOKENS,
        history=None,
    ):
        self.client = client or self._build_default_client()
        self.model = model
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.history = list(history) if history else []

    @staticmethod
    def _build_default_client():
        if anthropic is None:
            raise RuntimeError(
                "The 'anthropic' package is required. Install it with "
                "`pip install -r requirements.txt`."
            )
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Set the ANTHROPIC_API_KEY environment variable "
                "(see .env.example) before starting a chat."
            )
        return anthropic.Anthropic(api_key=api_key)

    def send(self, user_message: str) -> str:
        """Send a message, append it (and the reply) to history, and return the reply text."""
        self.history.append({"role": "user", "content": user_message})
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=self.history,
        )
        reply_text = "".join(
            block.text for block in response.content if getattr(block, "type", "text") == "text"
        )
        self.history.append({"role": "assistant", "content": reply_text})
        return reply_text

    def reset(self) -> None:
        """Clear the conversation history, starting a fresh conversation."""
        self.history = []

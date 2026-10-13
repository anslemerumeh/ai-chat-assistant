#!/usr/bin/env python3
"""Terminal chat loop for the AI Chat Assistant."""

from dotenv import load_dotenv

from chatbot.bot import ChatBot


def main():
    load_dotenv()
    print("AI Chat Assistant — type 'exit' or 'quit' to leave, 'reset' to clear history.\n")

    try:
        bot = ChatBot()
    except RuntimeError as exc:
        print(f"Setup error: {exc}")
        return

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            bot.reset()
            print("(conversation cleared)\n")
            continue

        try:
            reply = bot.send(user_input)
        except Exception as exc:  # noqa: BLE001 - surface any API/network error to the user
            print(f"Error: {exc}\n")
            continue

        print(f"Assistant: {reply}\n")


if __name__ == "__main__":
    main()

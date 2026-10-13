"""Flask web UI for the AI Chat Assistant.

Conversation history is kept in the browser's session cookie (not on the
server), so each visitor gets their own independent conversation without
needing a database for this demo-sized project.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

from chatbot.bot import ChatBot

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    bot = ChatBot(history=session.get("history", []))
    try:
        reply = bot.send(message)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:  # noqa: BLE001 - surface API/network errors to the client
        return jsonify({"error": f"Chat request failed: {exc}"}), 502

    session["history"] = bot.history
    return jsonify({"reply": reply})


@app.route("/api/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))

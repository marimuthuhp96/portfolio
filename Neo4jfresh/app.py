"""
app.py — Flask web application for the GraphRAG restaurant chatbot.

Architecture:
    FlaskChatApp — Wraps Flask routing, session management,
                   and GraphRAGChatbot into a single cohesive class.
"""

from flask import Flask, render_template, request, session
from chatbot import GraphRAGChatbot


class FlaskChatApp:
    """
    Flask web application that exposes the GraphRAG chatbot via HTTP.

    Routes:
        GET  /       — Render chat interface with history.
        POST /       — Submit user message, get bot reply.
        GET  /clear  — Clear the current session's chat history.
    """

    def __init__(self, secret_key: str = "graphrag_secret_2024") -> None:
        """
        Initialise the Flask app and chatbot.

        Args:
            secret_key: Flask session secret key.
        """
        self._app = Flask(__name__)
        self._app.secret_key = secret_key
        self._chatbot = GraphRAGChatbot()
        self._register_routes()

    # ── Route Registration ───────────────────────────────────────────────────

    def _register_routes(self) -> None:
        """Bind URL rules to handler methods."""
        self._app.add_url_rule(
            "/", "home", self._home, methods=["GET", "POST"]
        )
        self._app.add_url_rule(
            "/clear", "clear", self._clear, methods=["GET"]
        )

    # ── Request Handlers ─────────────────────────────────────────────────────

    def _home(self):
        """
        Handle the main chat page.

        GET  — Render existing session history.
        POST — Process user message, append bot reply to history.
        """
        if "chat_history" not in session:
            session["chat_history"] = []

        if request.method == "POST":
            user_input = request.form.get("user", "").strip()
            if user_input:
                reply = self._chatbot.chat(user_input)
                session["chat_history"].append(("user", user_input))
                session["chat_history"].append(("bot", reply))
                session.modified = True

        return render_template(
            "index.html",
            chat_history=session["chat_history"]
        )

    def _clear(self):
        """Clear all chat history from the current session."""
        session.pop("chat_history", None)
        return render_template("index.html", chat_history=[])

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = True) -> None:
        """
        Start the Flask development server.

        Args:
            host:  Host address to bind to.
            port:  Port number.
            debug: Enable Flask debug/reloader mode.
        """
        self._app.run(host=host, port=port, debug=debug)

    def close(self) -> None:
        """Release chatbot resources (Neo4j driver)."""
        self._chatbot.close()


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    chat_app = FlaskChatApp()
    chat_app.run()
"""
chatbot_st.py — Streamlit UI for the GraphRAG restaurant chatbot.

Architecture:
    StreamlitChatApp — Manages page config, header, chat input/output
                       and delegates AI logic to GraphRAGChatbot.

Run:
    streamlit run chatbot_st.py
"""

import streamlit as st
from chatbot import GraphRAGChatbot


class StreamlitChatApp:
    """
    Streamlit-based chat interface for the GraphRAG restaurant assistant.

    Uses st.session_state to persist the chatbot instance and
    conversation history across Streamlit reruns.
    """

    # ── CSS Styling ───────────────────────────────────────────────────────────

    _CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0a0e1a; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#0f172a,#1e293b); }
    .user-bubble {
        background: linear-gradient(135deg,#1e3a5f,#0f172a);
        border: 1px solid #38bdf8; border-radius: 12px;
        padding: 12px 16px; margin: 6px 0;
        color: #93c5fd; font-size: 14px;
    }
    .bot-bubble {
        background: linear-gradient(135deg,#052e16,#14532d);
        border: 1px solid #22c55e; border-radius: 12px;
        padding: 12px 16px; margin: 6px 0;
        color: #86efac; font-size: 14px;
    }
    .chat-header {
        color: #e2e8f0; font-size: 28px; font-weight: 700;
        margin-bottom: 4px;
    }
    .chat-sub {
        color: #64748b; font-size: 14px; margin-bottom: 20px;
    }
    </style>
    """

    def __init__(self) -> None:
        """
        Configure the Streamlit page and initialise session state.

        The GraphRAGChatbot instance is stored in st.session_state
        so it is not re-created on every rerun.
        """
        st.set_page_config(
            page_title="GraphRAG Restaurant Chatbot",
            page_icon="🍴",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
        st.markdown(self._CSS, unsafe_allow_html=True)

        if "chatbot" not in st.session_state:
            st.session_state.chatbot = GraphRAGChatbot()
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        self._chatbot: GraphRAGChatbot = st.session_state.chatbot

    # ── Rendering Methods ────────────────────────────────────────────────────

    def render_header(self) -> None:
        """Render the page title and subtitle."""
        st.markdown(
            '<div class="chat-header">🍴 GraphRAG Restaurant Assistant</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="chat-sub">Powered by Neo4j Knowledge Graph + Google Gemini</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

    def render_chat_input(self) -> None:
        """
        Render the user input row with Send and Clear buttons.

        Submitting a message calls GraphRAGChatbot.chat() and triggers
        a Streamlit rerun to update the conversation display.
        """
        col_input, col_send, col_clear = st.columns([7, 1, 1])

        with col_input:
            user_input = st.text_input(
                label="",
                placeholder="e.g. Best biryani restaurant near me?",
                label_visibility="collapsed",
                key="user_input",
            )

        with col_send:
            send_clicked = st.button("Send 🚀", use_container_width=True)

        with col_clear:
            if st.button("Clear 🗑️", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        if send_clicked and user_input.strip():
            with st.spinner("Thinking..."):
                reply = self._chatbot.chat(user_input.strip())
            st.session_state.chat_history.append(("You", user_input.strip()))
            st.session_state.chat_history.append(("Bot", reply))
            st.rerun()

    def render_conversation(self) -> None:
        """
        Render the full conversation history in reverse-chronological order.

        User messages are displayed with a blue bubble;
        bot responses are displayed with a green bubble.
        """
        if not st.session_state.chat_history:
            st.markdown(
                "<div style='color:#475569;text-align:center;margin-top:40px;'>"
                "💬 Ask me anything about restaurants!</div>",
                unsafe_allow_html=True,
            )
            return

        st.markdown("### 💬 Conversation")
        for sender, message in reversed(st.session_state.chat_history):
            css_class = "user-bubble" if sender == "You" else "bot-bubble"
            icon      = "🧑" if sender == "You" else "🤖"
            st.markdown(
                f'<div class="{css_class}"><b>{icon} {sender}:</b> {message}</div>',
                unsafe_allow_html=True,
            )

    def render_sidebar(self) -> None:
        """Render information panel in the sidebar."""
        with st.sidebar:
            st.markdown("## 🍽️ About")
            st.markdown(
                "This chatbot uses **GraphRAG** — combining a "
                "Neo4j knowledge graph with vector embeddings to "
                "answer questions about 100 restaurant branches."
            )
            st.markdown("---")
            st.markdown("**Try asking:**")
            st.markdown("- Best restaurant for biryani?")
            st.markdown("- Which restaurants have the worst reviews?")
            st.markdown("- Recommend a good paneer dish?")

    # ── Orchestration ────────────────────────────────────────────────────────

    def run(self) -> None:
        """
        Orchestrate the complete Streamlit UI.

        Call order:
            render_header() → render_sidebar() → render_chat_input() → render_conversation()
        """
        self.render_header()
        self.render_sidebar()
        self.render_chat_input()
        self.render_conversation()


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = StreamlitChatApp()
    app.run()
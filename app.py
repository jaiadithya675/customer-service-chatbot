"""Streamlit chat UI: `streamlit run app.py`."""
import streamlit as st

from chatbot.dialogue import Chatbot

st.set_page_config(page_title="Customer Service Bot", page_icon="💬")
st.title("💬 Customer Service Chatbot")
st.caption("Try: 'where is my order' → '#48213', 'return policy', 'do you accept upi', 'talk to a human'")

if "bot" not in st.session_state:
    st.session_state.bot, st.session_state.history = Chatbot(), []
show_debug = st.sidebar.checkbox("Show intent and confidence", True)

for role, text, meta in st.session_state.history:
    with st.chat_message(role):
        st.write(text)
        if meta and show_debug:
            st.caption(meta)

if msg := st.chat_input("Type your question"):
    r = st.session_state.bot.reply(msg)
    meta = f"intent: {r['intent']} · confidence: {r['confidence']} · entities: {r['entities']}"
    st.session_state.history += [("user", msg, None), ("assistant", r["response"], meta)]
    st.rerun()

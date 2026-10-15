"""AI chat page. Safety checks run first, then the model, then a labelled fallback."""
import streamlit as st

import ui
from services import ai_service

ui.setup_page("AI chat", "💬")
ui.page_header("AI wellness chat", "Talk through everyday stress, study pressure and routines.")

service = ai_service.AIService()
if service.is_configured:
    st.success("An AI model is configured. Replies marked 'AI model' come from it.")
else:
    st.warning("No AI API key is configured, so this chat uses limited offline fallback replies. "
               "See the README to add a key.")
ui.note("I am an AI program, not a person, therapist or doctor. I can't diagnose or give medical advice, "
        "and nobody monitors this chat in real time. If you are in danger, contact local emergency services.")
with st.expander("What happens to my messages?"):
    st.markdown(
        "- Chat messages are kept only in this browser session and are **not saved** to the database. "
        "Refreshing the page clears them.\n"
        "- If an AI key is configured, your recent chat messages are sent to the AI provider to generate a reply. "
        "**Your mood records and personal notes are never sent.**\n"
        "- Messages about self-harm, abuse or danger are answered by fixed safety text and are not sent to the model.")

messages = st.session_state.setdefault("chat_messages", [])
if st.sidebar.button("Clear conversation"):
    st.session_state["chat_messages"] = []
    st.rerun()

prompt = st.chat_input("Type a message...")
if prompt:
    history = [{"role": m["role"], "content": m["text"]} for m in messages]
    messages.append({"role": "user", "text": prompt, "source": "user"})
    with st.spinner("Thinking..."):
        reply = ai_service.get_chat_reply(prompt, history, service)
    messages.append({"role": "assistant", "text": reply.text, "source": reply.source, "note": reply.note})

if not messages:
    ui.empty_state("Say hello or tell me what is on your mind.",
                   "For example: 'I'm worried about my exam next week' or 'I can't get started on my assignment'.")

SOURCE_LABELS = {"ai": "AI model reply", "safety": "Safety message (fixed text, not AI-generated)",
                 "boundary": "Boundary message (fixed text, not AI-generated)"}
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["text"])
        if m["role"] == "assistant":
            if m["source"] == "fallback":
                label = ai_service.FALLBACK_LABEL + (f". Reason: {m['note']}" if m.get("note") else "")
            else:
                label = SOURCE_LABELS.get(m["source"], "")
            st.caption(label)

from groq import Groq
import streamlit as st

st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")
st.title("🤖 My AI Chatbot")
st.caption("Powered by LLaMA 3.3 via Groq")
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
personas = {
    "Helpful Assistant": "You are a helpful AI assistant.",
    "Interview Coach": "You are an expert interview coach for software engineering roles. Help the user practice and improve their answers.",
    "Python Tutor": "You are a Python programming tutor. Explain concepts clearly with code examples.",
    "Career Advisor": "You are a career advisor specializing in tech jobs. Give practical, actionable advice."
}

with st.sidebar:
    st.header("⚙️ Settings")
    persona = st.selectbox("Chatbot Persona", list(personas.keys()))
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Type your message..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                messages=[
                    {"role": "system", "content": personas[persona]},
                    *st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
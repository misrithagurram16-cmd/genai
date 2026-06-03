from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="AI Career Coach", page_icon="🎯")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert AI/ML career coach helping fresh graduates land their first job.

You have deep knowledge of:
- What companies look for in Junior AI Engineers
- How to build a strong GenAI portfolio
- Resume and LinkedIn optimization
- Technical interview preparation for ML roles

Rules:
- Be encouraging but honest
- Give specific, actionable advice
- When asked about skills, always mention: Python, LangChain, RAG, AI Agents
- Format your responses clearly with bullet points when listing items
- Keep responses concise — max 150 words unless the user asks for more detail"""

st.title("🎯 AI Career Coach")
st.caption("Your personal coach for landing a Junior AI Engineer role")

with st.sidebar:
    st.header("📊 Your Profile")
    name = st.text_input("Your name", "Misritha")
    experience = st.selectbox("Experience level", [
        "Fresh Graduate",
        "0-1 years",
        "1-2 years"
    ])
    target_role = st.selectbox("Target role", [
        "Junior AI Engineer",
        "ML Engineer",
        "GenAI Developer",
        "Data Scientist"
    ])
    st.divider()
    st.markdown("**Quick Questions:**")
    if st.button("What skills do I need?"):
        st.session_state.quick_q = "What are the top 5 skills I need to become a Junior AI Engineer?"
    if st.button("Review my resume"):
        st.session_state.quick_q = "What should my resume look like as a fresh graduate targeting AI roles?"
    if st.button("Interview tips"):
        st.session_state.quick_q = "What are the most common interview questions for Junior AI Engineer roles?"
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_q" not in st.session_state:
    st.session_state.quick_q = None

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.write(f"Hi {name}! 👋 I'm your AI Career Coach. I'll help you land your first **{target_role}** role. What would you like to work on today?")

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle quick questions
if st.session_state.quick_q:
    prompt = st.session_state.quick_q
    st.session_state.quick_q = None
else:
    prompt = st.chat_input("Ask your career coach anything...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + f"\n\nUser profile: Name={name}, Experience={experience}, Target role={target_role}"},
                    *st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import tempfile

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Chat with your PDF", page_icon="📄", layout="wide")

# Custom styling
st.markdown("""
<style>
.main-header { font-size: 2rem; font-weight: 700; margin-bottom: 0; }
.sub-header { color: gray; margin-bottom: 1rem; }
.source-badge { background: #1e3a5f; padding: 4px 10px; border-radius: 20px; font-size: 12px; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.markdown("## 📂 Document")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        if st.session_state.pdf_name != uploaded_file.name:
            with st.spinner("🔄 Processing PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                loader = PyPDFLoader(tmp_path)
                pages = loader.load()

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=100
                )
                chunks = splitter.split_documents(pages)

                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                st.session_state.vectorstore = Chroma.from_documents(chunks, embeddings)
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.messages = []
                st.session_state.chat_history = []

            st.success(f"✅ Ready! {len(pages)} pages, {len(chunks)} chunks")

    if st.session_state.pdf_name:
        st.info(f"📄 **{st.session_state.pdf_name}**")
        st.markdown("---")
        st.markdown("**💡 Try asking:**")
        st.markdown("- Summarize this document")
        st.markdown("- What are the main findings?")
        st.markdown("- Who are the authors?")
        st.markdown("- What is the conclusion?")

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    if st.button("📄 New Document"):
        st.session_state.vectorstore = None
        st.session_state.pdf_name = None
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# Main area
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">📄 Chat with your PDF</p>', unsafe_allow_html=True)
    if st.session_state.pdf_name:
        st.markdown(f'<p class="sub-header">Chatting with: {st.session_state.pdf_name}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="sub-header">Upload a PDF to get started</p>', unsafe_allow_html=True)

with col2:
    if st.session_state.messages:
        st.metric("Questions asked", len([m for m in st.session_state.messages if m["role"] == "user"]))

# Chat display
if not st.session_state.vectorstore:
    st.info("👈 Upload a PDF from the sidebar to start chatting!")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "sources" in msg:
                st.caption(f"📍 Sources: {msg['sources']}")

    if prompt := st.chat_input("Ask anything about your document..."):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching document..."):
                # Get relevant chunks
                docs = st.session_state.vectorstore.similarity_search(prompt, k=4)
                context = "\n\n".join([f"[Page {d.metadata.get('page', 0)+1}]: {d.page_content}" for d in docs])
                sources = ", ".join(sorted(set([f"Page {d.metadata.get('page', 0)+1}" for d in docs])))

                # Build conversation history for context
                history_text = ""
                for h in st.session_state.chat_history[-4:]:
                    history_text += f"User: {h['user']}\nAssistant: {h['assistant']}\n\n"

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"""You are a helpful assistant answering questions about a document.

Document context:
{context}

Previous conversation:
{history_text}

Rules:
- Answer only from the document context
- If not found, say "I couldn't find that in the document"
- Be concise and clear
- Reference page numbers when helpful"""},
                        {"role": "user", "content": prompt}
                    ]
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.caption(f"📍 Sources: {sources}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "sources": sources
        })
        st.session_state.chat_history.append({
            "user": prompt,
            "assistant": reply
        })
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

st.set_page_config(page_title="Chat with your PDF", page_icon="📄")
st.title("📄 Chat with your PDF")
st.caption("Upload any PDF and ask questions about it")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# Sidebar - PDF upload
with st.sidebar:
    st.header("📂 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file and st.session_state.vectorstore is None:
        with st.spinner("Processing PDF..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Load and split PDF
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = splitter.split_documents(pages)

            # Create embeddings and vector store
            embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            st.session_state.vectorstore = Chroma.from_documents(
                chunks, embeddings
            )
            st.success(f"✅ PDF processed! {len(chunks)} chunks created.")

    if st.session_state.vectorstore:
        st.info("PDF ready — ask anything!")
        if st.button("🗑️ Clear"):
            st.session_state.vectorstore = None
            st.session_state.messages = []
            st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about your PDF..."):
    if not st.session_state.vectorstore:
        st.warning("Please upload a PDF first!")
    else:
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Searching PDF..."):
                # Retrieve relevant chunks
                docs = st.session_state.vectorstore.similarity_search(prompt, k=3)
                context = "\n\n".join([d.page_content for d in docs])
                sources = list(set([f"Page {d.metadata.get('page', '?') + 1}" for d in docs]))

                # Ask LLM with context
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"""You are a helpful assistant that answers questions based on the provided document context.
                        
Context from document:
{context}

Rules:
- Only answer based on the context provided
- If the answer isn't in the context, say so
- Be concise and clear"""},
                        {"role": "user", "content": prompt}
                    ]
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.caption(f"📍 Sources: {', '.join(sources)}")

        st.session_state.messages.append({"role": "assistant", "content": reply})
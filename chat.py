import base64
import os
import tempfile
import streamlit as st
from embedchain import App
from streamlit_chat import message


# Embedchain bot setup
def embedchain_bot(db_path):
    return App.from_config(
        config={
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.2:latest",
                    "max_tokens": 250,
                    "temperature": 0.5,
                    "stream": True,
                    "base_url": 'http://localhost:11434'
                }
            },
            "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
            "embedder": {
                "provider": "ollama",
                "config": {"model": "llama3.2:latest", "base_url": 'http://localhost:11434'}
            }
        }
    )

# Function to display PDF in the app
def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
# Adding custom CSS for sidebar background color
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #FF5733;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and caption of the app
st.title("Chat with PDF using Llama 3.2")
st.caption("This app allows you to chat with a PDF using Llama 3.2 model.")

# Set up a temporary directory for the vector database
db_path = tempfile.mkdtemp()

# Initialize app and chat history in session state
if 'app' not in st.session_state:
    st.session_state.app = embedchain_bot(db_path)
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar for PDF upload
with st.sidebar:
    st.header("PDF Upload")
    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

    if pdf_file:
        st.subheader("PDF Preview")
        display_pdf(pdf_file)

# Add the uploaded PDF to the knowledge base
if pdf_file and st.button("Add to Knowledge Base"):
    with st.spinner("Adding PDF to knowledge base..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_file.getvalue())
            st.session_state.app.add(f.name, data_type="pdf_file")
        os.remove(f.name)
    st.success(f"Added {pdf_file.name} to knowledge base!")

# Display chat messages
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["role"] == "user", key=str(i))

# Chat input to interact with the PDF knowledge base
if prompt := st.chat_input("Ask a question about the PDF"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    message(prompt, is_user=True)

    with st.spinner("Thinking..."):
        response = st.session_state.app.chat(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        message(response)

# Button to clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []

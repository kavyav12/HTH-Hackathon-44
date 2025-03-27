import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from docx import Document
from dotenv import load_dotenv
from googletrans import Translator

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY is not set. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Initialize session state for history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDFs."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def get_text_chunks(text):
    """Split text into chunks for vector storage."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Create FAISS vector store from text chunks."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    """Initialize Gemini conversational chain."""
    prompt_template = """
    Answer the question as detailed as possible from the provided context. 
    If the answer is not in the provided context, respond with "answer is not available in the context".
    
    Context:\n {context}\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def user_input(user_question, language):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    if not os.path.exists("faiss_index"):
        st.error("No FAISS index found. Please upload and process PDFs first.")
        return

    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    reply = response.get("output_text", "No response generated.")
    
    # Translate response if needed
    if language != "English":
        translator = Translator()
        reply = translator.translate(reply, dest=language).text

    # Save to chat history
    st.session_state.chat_history.append({"question": user_question, "answer": reply})

    st.write("Reply:", reply)

def draft_contract(scenario):
    """Generate a contract based on the scenario."""
    contract = f"""
    CONTRACT AGREEMENT

    This Agreement is made and entered into on this day between the parties involved.

    WHEREAS, {scenario}

    NOW, THEREFORE, in consideration of the mutual covenants and promises contained herein, the parties agree as follows:

    1. Obligations of Party A:
       - Describe the responsibilities of Party A.

    2. Obligations of Party B:
       - Describe the responsibilities of Party B.

    3. Term and Termination:
       - Specify the duration and termination conditions.

    4. Governing Law:
       - This Agreement shall be governed by the laws of [Jurisdiction].

    5. Signatures:
       - ___________________  (Party A)
       - ___________________  (Party B)
    """

    return contract.strip()

def save_contract_to_word(contract_text, filename="contract.docx"):
    """Save contract to a Word document."""
    doc = Document()
    doc.add_paragraph(contract_text)
    doc.save(filename)
    return filename

def main():
    """Streamlit UI"""
    st.set_page_config(page_title="Legal Assist", layout="wide")
    
    col1, col2 = st.columns([3, 1])  # Left: Chat | Right: History

    with col1:
        st.header("Chat with a Legal Assistant💁")
        user_question = st.text_input("Ask about the document")

        # Language selection
        languages = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"]
        selected_language = st.selectbox("Select Language", languages)

        if user_question:
            user_input(user_question, selected_language)

        # Contract drafting
        st.subheader("Draft a Legal Contract")
        scenario = st.text_area("Enter Scenario for Contract Drafting")

        if st.button("Generate Contract"):
            if scenario.strip():
                contract_text = draft_contract(scenario)
                filename = save_contract_to_word(contract_text)

                with open(filename, "rb") as file:
                    st.download_button(label="Download Contract", data=file, file_name="Contract.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with col2:
        st.title("History")
        if st.session_state.chat_history:
            for chat in reversed(st.session_state.chat_history):
                st.markdown(f"**Q:** {chat['question']}")
                st.markdown(f"**A:** {chat['answer']}")
                st.markdown("---")

        st.title("Upload & Process PDFs")
        pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True, type=["pdf"])
        
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                if not raw_text.strip():
                    st.error("No text extracted from PDFs. Please check the files.")
                    return
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Processing complete. Ready for Q&A.")

if __name__ == "__main__":
    main()

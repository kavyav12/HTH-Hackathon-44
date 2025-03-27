
**Legal Assist Pro** is a powerful Streamlit-based application designed to assist users with legal document analysis, contract generation, and multilingual support for Indian languages. Leveraging AI models for natural language processing and document understanding, it provides a user-friendly interface for legal professionals and individuals alike.

## Features

- **Multilingual Support:**  
  Offers UI and response translation into multiple Indian languages (e.g., Hindi, Tamil, Telugu, etc.) using a translation API (assumed to be Google Translate).

- **Document Analysis:**  
  Upload PDF documents to extract text, timelines, legal entities, and key information using AI-driven analysis.

- **Contract Generation:**  
  Create customizable legal contracts (e.g., Employment Agreements, Lease Agreements, NDAs) with live previews and download options in TXT, DOCX, and PDF formats.

- **Chat Interface:**  
  Ask questions about uploaded documents and receive detailed AI-generated answers in the selected language.

- **Chat History:**  
  Save and review previous chat interactions for easy reference.

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/legal-assist-pro.git
   cd legal-assist-pro
   ```

2. **Install Dependencies:**
   Ensure you have Python 3.8+ installed. Install the required packages using:
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not provided, install the following key dependencies:
   ```bash
   pip install streamlit google-generativeai faiss-cpu PyPDF2 langchain reportlab python-docx
   ```
   *Note: Additional packages may be required depending on the translation service used (e.g., `googletrans` or equivalent).*

3. **Set Up API Keys:**
   - Obtain an API key for Google Generative AI (`gemini-1.5-flash` model).
   - Configure the key as an environment variable or directly in the code:
     ```bash
     export GOOGLE_API_KEY='your-api-key'
     ```
   - If using a translation service like Google Translate, configure its API key similarly.

4. **Directory Setup:**
   Ensure the `history/` and `faiss_index/` directories exist or will be created automatically by the app.

## Usage

1. **Run the Application:**
   Launch the app using Streamlit:
   ```bash
   streamlit run app.py
   ```
   *Note: Replace `app.py` with the actual filename if different.*

2. **Select Language:**
   - In the sidebar, choose your preferred language from the dropdown (e.g., English, Hindi, Tamil).

3. **Upload and Process Documents:**
   - Go to the "Document Analysis" tab.
   - Upload PDF files and click "Process Documents" to extract text and create a vector store for analysis.

4. **Ask Questions:**
   - In the "Chat" tab, type questions about your documents (e.g., "What are the key dates?").
   - View translated responses and save them to chat history.

5. **Generate Contracts:**
   - Navigate to the "Contract Generator" tab.
   - Select a contract type (e.g., Employment, Lease, NDA).
   - Fill in details (e.g., names, addresses, dates).
   - Preview the contract live and download it in your preferred format (TXT, DOCX, PDF).

6. **View Chat History:**
   - Check the "History" tab to review past interactions.

## Configuration

- **API Keys:**
  - Set the Google Generative AI API key via an environment variable:
    ```bash
    export GOOGLE_API_KEY='your-api-key'
    ```
  - For translation, ensure the `translator` object (assumed to be from a library like `googletrans`) is properly initialized with an API key if required.

- **Language Support:**
  - The `INDIAN_LANGUAGES` dictionary defines supported languages. Add or modify entries as needed:
    ```python
    INDIAN_LANGUAGES = {
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        # Add more languages here
    }
    ```

- **Vector Store:**
  - The app uses FAISS for document vector storage, saved in the `faiss_index/` directory. Adjust the `batch_size` in `get_vector_store` if memory issues occur.

## File Structure

- **`app.py`:**  
  The main application script containing the Streamlit UI and core logic.
- **`history/`:**  
  Directory storing chat history in `chat_history.json`.
- **`faiss_index/`:**  
  Directory for the FAISS vector store generated from processed PDFs.
- **`requirements.txt`:**  
  (Recommended to create) Lists all Python dependencies.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request on GitHub.

Please ensure your code follows Python PEP 8 guidelines and includes appropriate comments.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, feedback, or support, please reach out to [your-email@example.com](mailto:your-email@example.com) or open an issue on the GitHub repository.

---

This README provides a clear, standalone guide to understanding, installing, and using the "Legal Assist Pro" application. Customize the repository URL, email, and additional details as needed for your specific project.

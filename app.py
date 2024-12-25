import streamlit as st
import os
from src.markitdown import MarkItDown
from openai import OpenAI
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Document Analyzer with Microsoft MarkItDown",
    page_icon="📄",
    layout="wide",
)


def clear_cache():
    # Clear temporary files and cache
    if os.path.exists(".cache"):
        for file in os.listdir(".cache"):
            os.remove(os.path.join(".cache", file))
    st.cache_data.clear()


def process_document(uploaded_file, use_llm=False, custom_api_key=None):
    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(uploaded_file.name).suffix
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        if use_llm:
            # Use custom API key if provided, otherwise use environment variable
            api_key = custom_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is required for GPT-4o")

            client = OpenAI(api_key=api_key)
            md = MarkItDown(llm_client=client, llm_model="gpt-4o")
        else:
            md = MarkItDown()

        # Process the document
        result = md.convert(tmp_path)
        return result.text_content

    finally:
        # Clean up temporary file
        os.unlink(tmp_path)


def main():
    # Sidebar
    with st.sidebar:
        st.title("📄 Document Analyzer with Microsoft MarkItDown")
        st.write(
            "Upload any document to extract and analyze its content using Microsoft's MarkItDown technology"
        )

        st.header("Upload")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=[
                "pdf",
                "pptx",
                "docx",
                "xlsx",
                "jpg",
                "png",
                "mp3",
                "wav",
                "html",
                "csv",
                "json",
                "xml",
            ],
        )

        st.header("Settings")
        use_llm = st.toggle("Use GPT-4o for Enhanced Analysis", value=False)

        # OpenAI API Key input
        custom_api_key = None
        if use_llm:
            st.info("GPT-4o requires an OpenAI API key for enhanced analysis")
            use_custom_key = st.checkbox("Use custom OpenAI API key")
            if use_custom_key:
                custom_api_key = st.text_input(
                    "Enter OpenAI API Key",
                    type="password",
                    help="Your API key will not be stored and is only used for this session",
                )

        if st.button("Clear Cache"):
            clear_cache()
            st.success("Cache cleared!")

        st.markdown(
            """
        ### Supported Formats:
        - PDF
        - PowerPoint
        - Word
        - Excel
        - Images (EXIF + OCR)
        - Audio (EXIF + transcription)
        - HTML
        - Text (CSV, JSON, XML)
        """
        )

    # Main content area
    if uploaded_file:
        with st.spinner("Processing document..."):
            try:
                # Process the document
                text_content = process_document(uploaded_file, use_llm, custom_api_key)

                # Display results
                st.header("Analysis Results")

                # Create tabs for different views
                tab1, tab2 = st.tabs(["Extracted Content", "Document Information"])

                with tab1:
                    st.text_area("Extracted Content", text_content, height=600)

                    # Add download button for extracted text
                    st.download_button(
                        "Download Extracted Content",
                        text_content,
                        file_name=f"{uploaded_file.name}_extracted.txt",
                        mime="text/plain",
                    )

                with tab2:
                    st.json(
                        {
                            "Filename": uploaded_file.name,
                            "File size": f"{uploaded_file.size / 1024:.2f} KB",
                            "File type": uploaded_file.type,
                        }
                    )

            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
    else:
        st.info("👈 Please upload a document using the sidebar to begin analysis")


if __name__ == "__main__":
    main()

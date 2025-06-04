import streamlit as st
from pathlib import Path
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

# Define the static directory path
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

def clean_static_folder(exclude_files=None):
    if exclude_files is None:
        exclude_files = {"favicon.ico", "favicon_1024.ico", "scripts.js"}

    for file_path in STATIC_DIR.iterdir():
        if file_path.is_file() and file_path.name not in exclude_files:
            try:
                file_path.unlink()
                print(f"Deleted: {file_path.name}")
            except Exception as e:
                print(f"Error deleting {file_path.name}: {e}")

st.title("Resource Uploader")

uploaded_file = st.file_uploader("Choose an RDF file to publish", type=["txt", "ttl", "rdf", "xml", "nt", "n3", "jsonld"])

if uploaded_file:
    # Clean up old files before saving the new one
    clean_static_folder()

    unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    file_path = STATIC_DIR / unique_filename

    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File '{uploaded_file.name}' uploaded successfully.")

    # Provide a download button
    with open(file_path, "rb") as f:
        st.download_button(
            label="Download File",
            data=f,
            file_name=uploaded_file.name,
            mime="application/octet-stream"
        )

    # Construct the full URL to the uploaded file
    file_url = f"{BASE_URL}/static/{unique_filename}"
    st.markdown("Copy the file URL:")
    st.code(file_url, language="text")

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import math
import tempfile

def impose_booklet(input_pdf, num_signatures):
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    pages_per_signature = math.ceil(total_pages / num_signatures)
    imposed_writer = PdfWriter()
    
    for signature in range(num_signatures):
        start_page = signature * pages_per_signature
        end_page = min(start_page + pages_per_signature, total_pages)
        pages = list(range(start_page, end_page))
        
        while len(pages) % 4 != 0:
            pages.append(None)  # Add blank pages if needed
        
        imposed_order = []
        while pages:
            if len(pages) >= 2:
                imposed_order.append(pages.pop(-1))  # Last page (outer right)
                imposed_order.append(pages.pop(0))  # First page (outer left)
            if len(pages) >= 2:
                imposed_order.append(pages.pop(0))  # Second page (inner left)
                imposed_order.append(pages.pop(-1))  # Second-last page (inner right)
        
        for page in imposed_order:
            if page is not None:
                imposed_writer.add_page(reader.pages[page])
            else:
                imposed_writer.add_blank_page()
    
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(temp_output.name, "wb") as f:
        imposed_writer.write(f)
    
    return temp_output.name

st.title("PDF Booklet Imposition Tool")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
num_signatures = st.number_input("Number of Signatures", min_value=1, value=1)

if uploaded_file and st.button("Generate Booklet PDF"):
    imposed_pdf_path = impose_booklet(uploaded_file, num_signatures)
    
    with open(imposed_pdf_path, "rb") as f:
        st.download_button("Download Imposed PDF", f, "imposed_booklet.pdf", "application/pdf")

# Deployment Setup Instructions
def deploy_instructions():
    st.markdown("""
    ## Deployment Guide
    1. **Create a GitHub Repository**:
       - Go to [GitHub](https://github.com) and create a new repo.
       - Clone the repo and add this script (`app.py`).
       - Add a `requirements.txt` file with:
         ```
         streamlit
         pypdf2
         ```
       - Commit and push to GitHub.
    
    2. **Deploy on Streamlit Cloud**:
       - Go to [Streamlit Cloud](https://share.streamlit.io) and link your GitHub repo.
       - Click "Deploy" and your app will be online.
    
    3. **Deploy on Hugging Face Spaces**:
       - Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
       - Select "Streamlit" as the framework.
       - Connect your GitHub repo or manually upload files.
       - Your app will be hosted automatically.
    """)

deploy_instructions()

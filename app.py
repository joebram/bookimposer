import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import math
import tempfile
import os
try:
    from reportlab.lib.pagesizes import A3, A4
except ImportError:
    st.error("ReportLab is not installed. Please install it using 'pip install reportlab'.")
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

def impose_booklet(input_pdf, num_signatures):
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    pages_per_signature = math.ceil(total_pages / num_signatures)
    imposed_writer = PdfWriter()
    
    # Get default page size from the first page
    first_page = reader.pages[0]
    width = first_page.mediabox.width
    height = first_page.mediabox.height

    for signature in range(num_signatures):
        start_page = signature * pages_per_signature
        end_page = min(start_page + pages_per_signature, total_pages)
        pages = list(range(start_page, end_page))
        
        while len(pages) % 4 != 0:
            pages.append(None)  # Add blank pages if needed
        
        imposed_order = []
        while pages:
            if len(pages) >= 2:
                imposed_order.append(pages.pop(-1))
                imposed_order.append(pages.pop(0))
            if len(pages) >= 2:
                imposed_order.append(pages.pop(0))
                imposed_order.append(pages.pop(-1))
        
        for page in imposed_order:
            if page is not None:
                imposed_writer.add_page(reader.pages[page])
            else:
                imposed_writer.add_blank_page(width=width, height=height)  # Specify blank page size

    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(temp_output, "wb") as f:
        imposed_writer.write(f)

    return temp_output

def preview_pdf(input_pdf):
    poppler_path = "/opt/homebrew/bin"  # Apple Silicon (M1/M2/M3)
    # poppler_path = "/usr/local/bin"  # Uncomment this for Intel Macs
    
    # Save uploaded file to a temporary file
    temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(temp_pdf_path, "wb") as f:
        f.write(input_pdf.getvalue())  # Save the uploaded file content

    # Convert PDF pages to images
    images = convert_from_path(temp_pdf_path, first_page=1, last_page=5, poppler_path=poppler_path)
    
    # Remove the temp file after conversion
    os.remove(temp_pdf_path)

    preview_images = [Image.fromarray(img) for img in images]
    return preview_images

def preview_imposed_order(input_pdf, num_signatures):
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    pages_per_signature = math.ceil(total_pages / num_signatures)
    imposed_images = []
    
    for signature in range(num_signatures):
        start_page = signature * pages_per_signature
        end_page = min(start_page + pages_per_signature, total_pages)
        pages = list(range(start_page, end_page))
        
        while len(pages) % 4 != 0:
            pages.append(None)  # Add blank pages if needed
        
        imposed_order = []
        while pages:
            if len(pages) >= 2:
                imposed_order.append(pages.pop(-1))
                imposed_order.append(pages.pop(0))
            if len(pages) >= 2:
                imposed_order.append(pages.pop(0))
                imposed_order.append(pages.pop(-1))
        
        img = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(img)
        for i, page in enumerate(imposed_order):
            pos_x = (i % 2) * 400 + 50
            pos_y = (i // 2) * 200 + 50
            text = f"Page {page+1}" if page is not None else "Blank"
            draw.text((pos_x, pos_y), text, fill="black")
        imposed_images.append(img)
    
    return imposed_images

st.title("PDF Booklet Imposition Tool")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
num_signatures = st.number_input("Number of Signatures", min_value=1, value=1)

if uploaded_file:
    st.subheader("Preview of Uploaded PDF")
    preview_images = preview_pdf(uploaded_file)
    for img in preview_images:
        st.image(img, caption="Preview Page", use_column_width=True)
    
    if st.button("Preview Imposed Layout"):
        imposed_images = preview_imposed_order(uploaded_file, num_signatures)
        for img in imposed_images:
            st.image(img, caption="Imposed Layout Preview", use_column_width=True)
    
    if st.button("Generate Booklet PDF"):
        imposed_pdf_path = impose_booklet(uploaded_file, num_signatures)
        with open(imposed_pdf_path, "rb") as f:
            st.download_button("Download Imposed PDF", f, "imposed_booklet.pdf", "application/pdf")

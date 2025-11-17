import streamlit as st
import tempfile
from barcode_generator import generate_pdf_from_csv
import os

st.set_page_config(page_title="Barcode PDF Generator", layout="centered")

st.title("📦 Barcode Label PDF Generator")
st.write("Upload a CSV file and download the generated barcode PDF.")

# File uploader
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    st.success("CSV uploaded!")

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        csv_path = tmp.name

    # Generate PDF output path
    output_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    if st.button("Generate PDF"):
        with st.spinner("Generating barcodes..."):
            generate_pdf_from_csv(csv_path, output_pdf_path)

        st.success("PDF created successfully! 🎉")

        # Provide a download button
        with open(output_pdf_path, "rb") as f:
            st.download_button(
                label="⬇ Download PDF",
                data=f,
                file_name="barcodes.pdf",
                mime="application/pdf"
            )

        # Cleanup temporary files
        os.unlink(csv_path)

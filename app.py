import streamlit as st
import tempfile
from barcode_generator import generate_pdf_from_csv
import os

# -----------------------------
# STREAMLIT PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Barcode PDF Generator", layout="centered")

st.title("📦 Barcode Label PDF Generator")
st.write("Upload a CSV file and download a PDF with professionally formatted barcodes.")


# -----------------------------
# FILE UPLOADER
# -----------------------------
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Only run when a file is uploaded
if uploaded_file:

    st.success("CSV uploaded successfully!")

    # Store CSV temporarily on disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_csv:
        tmp_csv.write(uploaded_file.read())
        csv_path = tmp_csv.name

    # Prepare temporary PDF output file
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    output_pdf_path = tmp_pdf.name
    tmp_pdf.close()  # Close file so reportlab can write to it

    generate_btn = st.button("Generate PDF")

    if generate_btn:
        with st.spinner("Processing barcodes..."):
            try:
                generate_pdf_from_csv(csv_path, output_pdf_path)
            except Exception as e:
                st.error(f"❌ Error generating PDF: {e}")
            else:
                st.success("PDF created successfully! 🎉")

                # Download button
                with open(output_pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇ Download PDF",
                        data=pdf_file.read(),
                        file_name="barcodes.pdf",
                        mime="application/pdf",
                    )

        # Cleanup temp CSV (PDF is kept for download)
        try:
            os.unlink(csv_path)
        except:
            pass


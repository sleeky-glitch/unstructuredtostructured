import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import openai

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Unstructured to Structured PDF Bot (GPT-4.1)")

uploaded_file = st.file_uploader("Upload a scanned PDF (non-selectable text)", type=["pdf"])

output_format = st.selectbox("Select output format", ["Markdown", "JSON", "HTML", "Plaintext"])

if uploaded_file and output_format:
    # Load PDF with PyMuPDF
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    num_pages = pdf_document.page_count

    st.write(f"PDF loaded with {num_pages} pages.")

    # Function to convert PDF page to PNG image bytes
    def get_page_image_bytes(page):
        zoom = 2  # zoom factor for better resolution
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")
        return img_bytes

    # Function to call OpenAI GPT-4.1 with image and prompt
    def gpt4_1_extract_structured(image_bytes, page_num, output_fmt):
        prompt = f"""
You are an expert AI assistant. Extract the text content from the image of page {page_num} of a scanned PDF document. 
Convert the extracted content into {output_fmt} format.

Instructions:
- If JSON, output valid JSON only.
- If Markdown, use appropriate Markdown syntax.
- If HTML, output valid HTML markup.
- If Plaintext, output clean readable text.

Begin output below:
"""

        # NOTE: The following is a conceptual example of multimodal API usage.
        # Adjust according to the actual OpenAI multimodal API specification.

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with your GPT-4.1 multimodal model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts and structures text from images."},
                {"role": "user", "content": prompt},
            ],
            files=[
                {
                    "name": "page.png",
                    "data": image_bytes,
                    "mime_type": "image/png"
                }
            ],
        )
        return response.choices[0].message.content.strip()

    for i in range(num_pages):
        page = pdf_document.load_page(i)
        st.subheader(f"Page {i+1}")

        img_bytes = get_page_image_bytes(page)
        st.image(img_bytes, caption=f"Page {i+1} image", use_column_width=True)

        with st.spinner(f"Processing page {i+1}..."):
            try:
                structured_output = gpt4_1_extract_structured(img_bytes, i+1, output_format)
                st.code(structured_output, language=output_format.lower() if output_format != "Plaintext" else None)
            except Exception as e:
                st.error(f"Error processing page {i+1}: {e}")

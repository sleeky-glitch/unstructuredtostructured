import streamlit as st
import openai
import fitz  # PyMuPDF
import base64
import io

openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="PDF Content Analyzer", page_icon="📄")
st.title("📄 PDF Content Extractor (unstructured to structured)")
st.write("Upload a PDF file. The AI will analyze each page image directly for content, extracting and analyzing text, sentiment, sources, and more.")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")

    dpi = st.slider("Image DPI (higher = better quality, slower)", 150, 300, 200)

    with st.spinner("Converting PDF pages to images..."):
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        images = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            images.append((page_num + 1, img_bytes))
        pdf_document.close()

    st.success(f"Converted {len(images)} pages to images.")

    all_results = []
    for page_num, img_bytes in images:
        st.markdown(f"### Analyzing Page {page_num}")
        image_data_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"

        try:
            response = openai.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Analyze the uploaded PDF page image for text content, "
                            "Provide a summary of the extracted text, "
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_data_url}}
                        ],
                    },
                ],
                max_tokens=700,
                temperature=0.2,
            )
            result = response.choices[0].message.content
            st.markdown("**AI Analysis:**")
            st.write(result)
            all_results.append((page_num, result))
        except Exception as e:
            st.error(f"Error analyzing page {page_num}: {e}")

else:
    st.info("👆 Please upload a PDF file to get started.")

st.markdown("---")
st.markdown("Made with ❤️ by BSPL")

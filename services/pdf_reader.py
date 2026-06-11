from pypdf import PdfReader

def extract_pdf_text(uploaded_file):

    try:
        pdf = PdfReader(uploaded_file)

        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        return f"PDF Error: {e}"

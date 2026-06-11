import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ARIA", page_icon="⚡", layout="wide")

# ── SETUP ─────────────────────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are ARIA, Sri's personal AI assistant.
Sri is an AI Engineer at Standard Roofs, Erode, Tamil Nadu, working on a Roofing ERP SaaS built on Zoho One.
Be direct, clear, and helpful. Give complete answers and working code when asked."""

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

# ── CSS — minimal dark theme ──────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"], .stApp { background:#0a0a10; }
.block-container { max-width: 800px; padding-top: 2rem; padding-bottom: 6rem; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stChatMessage"] { background: transparent; }

.stChatMessage p, .stChatMessage li { color: #e0e0f0 !important; }

[data-testid="stChatInput"] textarea {
    background:#16162a !important;
    color:#e0e0f0 !important;
    border:1px solid #2a2a44 !important;
    border-radius:14px !important;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ ARIA")
    st.caption("Sri's Personal AI — Phase 1")

    if st.button("✦ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Upload Files**")

    uploaded_image = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="img")
    uploaded_pdf = st.file_uploader("PDF", type=["pdf"], key="pdf")

# ── PDF TEXT EXTRACTION ───────────────────────────────────────────────────────
def extract_pdf_text(pdf_file) -> str:
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ── RENDER CHAT HISTORY ───────────────────────────────────────────────────────
st.title("⚡ ARIA")
st.caption("Ask me anything — I can also read images and PDFs.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask ARIA anything...")

if prompt:
    # Build the actual content sent to Gemini (may include image/pdf context)
    gemini_parts = [prompt]
    display_prompt = prompt

    # Handle image upload
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        gemini_parts.append(img)
        display_prompt += "\n\n📎 *[Image attached]*"

    # Handle PDF upload
    if uploaded_pdf is not None:
        pdf_text = extract_pdf_text(uploaded_pdf)
        gemini_parts.append(f"\n\n--- PDF Content ---\n{pdf_text[:15000]}")
        display_prompt += f"\n\n📎 *[PDF attached: {uploaded_pdf.name}]*"

    # Show user message
    with st.chat_message("user"):
        st.markdown(display_prompt)
    st.session_state.messages.append({"role": "user", "content": display_prompt})

    # Get response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            model = get_model()

            # Build conversation history for context
            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=history)
            response = chat.send_message(gemini_parts, stream=True)

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ Error: {str(e)}\n\nPlease check your API key and try again."
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

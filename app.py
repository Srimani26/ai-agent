import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="ARIA",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------

st.markdown("""
<style>
.stApp{
    background:#0b0b12;
}

[data-testid="stSidebar"]{
    background:#11111a;
}

[data-testid="stChatMessage"]{
    border-radius:18px;
}

.block-container{
    padding-top:1rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# API KEY
# ---------------------------------------------------

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------
# SESSION
# ---------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("🤖 ARIA")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    model_choice = st.selectbox(
        "Model",
        [
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]
    )

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("ARIA")

st.caption("Your AI Assistant")

# ---------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------
# UPLOAD
# ---------------------------------------------------

uploaded_file = st.file_uploader(
    "Attach image (optional)",
    type=["png","jpg","jpeg","webp"]
)

image = None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=300)

# ---------------------------------------------------
# PROMPT
# ---------------------------------------------------

prompt = st.chat_input("Ask ARIA anything...")

if prompt:

    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        try:

            model = genai.GenerativeModel(model_choice)

            if image:

                response = model.generate_content(
                    [prompt, image]
                )

            else:

                response = model.generate_content(
                    prompt
                )

            answer = response.text

        except Exception as e:

            answer = f"Error: {e}"

        placeholder.markdown(answer)

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })

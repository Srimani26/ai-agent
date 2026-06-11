import streamlit as st
import google.generativeai as genai
from PIL import Image
from services.pdf_reader import extract_pdf_text

# --------------------------------------------------

# PAGE CONFIG

# --------------------------------------------------

st.set_page_config(
page_title="ARIA",
page_icon="🤖",
layout="wide"
)

# --------------------------------------------------

# CUSTOM CSS

# --------------------------------------------------

st.markdown("""

<style>

.stApp{
    background:#0b0b12;
}

[data-testid="stSidebar"]{
    background:#12121b;
}

.block-container{
    padding-top:1rem;
}

h1,h2,h3{
    color:white;
}

.stChatMessage{
    border-radius:16px;
}

</style>

""", unsafe_allow_html=True)

# --------------------------------------------------

# GEMINI SETUP

# --------------------------------------------------

try:
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
st.error("GEMINI_API_KEY not found in Streamlit Secrets")
st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --------------------------------------------------

# SESSION STATE

# --------------------------------------------------

if "messages" not in st.session_state:
st.session_state.messages = []

if "pdf_context" not in st.session_state:
st.session_state.pdf_context = ""

if "chat_title" not in st.session_state:
st.session_state.chat_title = "New Chat"

# --------------------------------------------------

# SIDEBAR

# --------------------------------------------------

with st.sidebar:

```
st.title("🤖 ARIA")

if st.button(
    "➕ New Chat",
    use_container_width=True
):
    st.session_state.messages = []
    st.session_state.pdf_context = ""
    st.rerun()

st.divider()

model_choice = st.selectbox(
    "Model",
    [
        "gemini-2.5-flash",
        "gemini-2.5-pro"
    ]
)

st.divider()

if st.button(
    "🗑 Clear PDF",
    use_container_width=True
):
    st.session_state.pdf_context = ""
```

# --------------------------------------------------

# HEADER

# --------------------------------------------------

st.title("🤖 ARIA")

st.caption("AI Assistant powered by Gemini")

# --------------------------------------------------

# CHAT HISTORY

# --------------------------------------------------

for msg in st.session_state.messages:

```
with st.chat_message(msg["role"]):
    st.markdown(msg["content"])
```

# --------------------------------------------------

# FILE UPLOAD

# --------------------------------------------------

uploaded_file = st.file_uploader(
"Attach File",
type=["png", "jpg", "jpeg", "webp", "pdf"]
)

image = None

if uploaded_file:

```
if uploaded_file.type.startswith("image/"):

    image = Image.open(uploaded_file)

    st.image(
        image,
        width=300
    )

elif uploaded_file.type == "application/pdf":

    with st.spinner("Reading PDF..."):

        st.session_state.pdf_context = extract_pdf_text(
            uploaded_file
        )

    st.success("PDF Loaded")
```

# --------------------------------------------------

# USER INPUT

# --------------------------------------------------

prompt = st.chat_input(
"Ask ARIA anything..."
)

if prompt:

```
st.session_state.messages.append(
    {
        "role":"user",
        "content":prompt
    }
)

with st.chat_message("user"):
    st.markdown(prompt)

with st.chat_message("assistant"):

    placeholder = st.empty()

    try:

        model = genai.GenerativeModel(
            model_choice
        )

        history = ""

        for msg in st.session_state.messages[-10:]:

            history += f"""
```

{msg['role']}:
{msg['content']}
"""

```
        final_prompt = f"""
```

Conversation History:

{history}

Current User Message:

{prompt}
"""

```
        if st.session_state.pdf_context:

            final_prompt += f"""
```

PDF CONTENT:

{st.session_state.pdf_context[:30000]}
"""

```
        if image:

            response = model.generate_content(
                [
                    final_prompt,
                    image
                ]
            )

        else:

            response = model.generate_content(
                final_prompt
            )

        answer = response.text

    except Exception as e:

        answer = f"Error: {str(e)}"

    placeholder.markdown(answer)

st.session_state.messages.append(
    {
        "role":"assistant",
        "content":answer
    }
)
```

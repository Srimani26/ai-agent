import requests
import streamlit as st

API_KEY = st.secrets["AIzaSyAwfp8FJLDHvUZYoy8fKgB0as7dMxs8g_M"]

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

SYSTEM_PROMPT = """You are a helpful, friendly and engaging AI assistant.
You can:
- Answer any questions clearly and simply
- Search and explain topics in depth
- Help write content like emails, blogs, posts
- Analyze and summarize documents or data
- Have natural friendly conversations

Always be warm, clear, and make the user feel comfortable.
If unsure, say so honestly. Keep responses clean and easy to read."""

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    .chat-title {
        text-align: center;
        padding: 20px 0 5px 0;
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
    }

    .chat-subtitle {
        text-align: center;
        color: #555;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    [data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 8px;
    }

    [data-testid="stChatInput"] {
        border-radius: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-title">🤖 AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">Ask me anything — I am here to help!</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [
        {
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        {
            "role": "model",
            "parts": [{"text": "Understood! I am ready to help you with anything."}]
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("👋 Hello! I am your AI Assistant. I can answer questions, write content, analyze data, and much more. How can I help you today?")

if user_input := st.chat_input("Type your message here..."):

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.gemini_history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            data = {"contents": st.session_state.gemini_history}
            response = requests.post(URL, json=data)
            result = response.json()
            reply = result["candidates"][0]["content"]["parts"][0]["text"]

        st.markdown(reply)

    st.session_state.gemini_history.append({
        "role": "model",
        "parts": [{"text": reply}]
    })

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

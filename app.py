import requests
import streamlit as st
from datetime import datetime

API_KEY = st.secrets["GEMINI_API_KEY"]
SEARCH_URL = "https://duckduckgo-api.vercel.app/search?q={query}&max_results=3"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

today = datetime.now().strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""You are an elite AI Assistant — highly intelligent, fast, accurate and friendly.
Today's date is {today}.

You specialize in:
1. CODING — Write clean, working code in any language. Always explain what the code does.
2. WEBSITE BUILDER — Build full HTML/CSS/JS websites when asked. Provide complete working code.
3. GENERAL KNOWLEDGE — Answer clearly with up to date accurate information.
4. CURRENT AFFAIRS — You know today is {today}. Reason about recent events accurately.
5. PERSONAL ASSISTANT — Help with tasks, planning, writing, emails, analysis.

Your personality:
- Warm, engaging and encouraging
- Give clear structured answers
- Use examples when explaining
- For code: always use code blocks
- For long answers: use headers and bullet points
- Never give wrong or outdated info — if unsure, say so honestly
- Always aim to fully solve the user's problem in one response

You are like Claude Opus — highly capable, thoughtful and precise."""

st.set_page_config(
    page_title="AI Assistant Pro",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e);
    color: white;
}

.chat-title {
    text-align: center;
    padding: 30px 0 5px 0;
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.chat-subtitle {
    text-align: center;
    color: #a0aec0;
    font-size: 1rem;
    margin-bottom: 10px;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}

.badge {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #e2e8f0;
}

[data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 25px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

.stSpinner {
    color: #a78bfa !important;
}

.mode-btn {
    background: rgba(167,139,250,0.2);
    border: 1px solid #a78bfa;
    border-radius: 10px;
    padding: 8px 16px;
    color: white;
    cursor: pointer;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-title">⚡ AI Assistant Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">Powered by Gemini 2.5 Flash • Fast • Accurate • Always Updated</div>', unsafe_allow_html=True)

st.markdown("""
<div class="badge-row">
    <span class="badge">💻 Coding</span>
    <span class="badge">🌐 Web Builder</span>
    <span class="badge">📰 Current Affairs</span>
    <span class="badge">🤖 AI Assistant</span>
    <span class="badge">📊 Data Analysis</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💻 Code Help", use_container_width=True):
        st.session_state.quick = "Help me write a Python function that "
with col2:
    if st.button("🌐 Build Website", use_container_width=True):
        st.session_state.quick = "Build me a complete HTML/CSS website for "
with col3:
    if st.button("📰 Latest News", use_container_width=True):
        st.session_state.quick = "What are the latest news and current affairs about "

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood! I am your AI Assistant Pro — ready to help with coding, websites, current affairs, and anything else. What can I do for you today?"}]}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""👋 **Welcome to AI Assistant Pro!**

I am your all-in-one AI — here is what I can do:

- 💻 **Coding** — Write, debug and explain code in any language
- 🌐 **Website Builder** — Build complete websites with HTML/CSS/JS
- 📰 **Current Affairs** — Up to date knowledge as of {today}
- 📊 **Data Analysis** — Analyze and summarize data
- 🤖 **Personal Assistant** — Help with anything you need

**How can I help you today?**""")

default_input = st.session_state.pop("quick", "")

if user_input := st.chat_input("Ask me anything — code, news, websites, analysis..."):

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.gemini_history.append({"role": "user", "parts": [{"text": user_input}]})

    with st.chat_message("assistant"):
        with st.spinner("⚡ Thinking..."):
            try:
                data = {
                    "contents": st.session_state.gemini_history,
                    "generationConfig": {
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxOutputTokens": 8192
                    }
                }
                response = requests.post(GEMINI_URL, json=data, timeout=30)
                result = response.json()

                if "candidates" in result:
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    reply = f"⚠️ Error: {result.get('error', {}).get('message', 'Unknown error')}"

            except requests.exceptions.Timeout:
                reply = "⏱️ Request timed out. Please try again!"
            except Exception as e:
                reply = f"⚠️ Something went wrong: {str(e)}"

        st.markdown(reply)

    st.session_state.gemini_history.append({"role": "model", "parts": [{"text": reply}]})
    st.session_state.messages.append({"role": "assistant", "content": reply})

if len(st.session_state.messages) > 0:
    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.messages = []
        st.session_state.gemini_history = [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": "Ready to help!"}]}
        ]
        st.rerun()

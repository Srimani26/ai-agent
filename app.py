import requests
import streamlit as st
from datetime import datetime
import json

API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
today = datetime.now().strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""You are an elite AI Assistant — extremely intelligent, fast, accurate and friendly.
Today's date is {today}.

You specialize in:
1. ADVANCED CODING — Write production-ready code in Python, JavaScript, React, Node.js, SQL, and any language.
   Always explain the code clearly. Include error handling and best practices.
2. ADVANCED WEBSITE BUILDER — Build complete, modern, beautiful websites with HTML/CSS/JS.
   Include animations, responsive design, and modern UI. Provide full working code.
3. GENERAL KNOWLEDGE — Answer any question accurately with examples.
4. CURRENT AFFAIRS — You know today is {today}. Give accurate, up to date information.
5. PERSONAL ASSISTANT — Help with planning, writing, emails, analysis, summarizing.
6. DATA ANALYSIS — Analyze data, explain patterns, create logic for charts and reports.

Rules:
- Always give complete, working, copy-paste ready answers
- For code: use proper code blocks with language labels
- For websites: give full HTML/CSS/JS in one file
- Be warm, clear and engaging
- If unsure about something very recent, say so honestly
- Structure long answers with headers and bullet points
- Always aim to fully solve the problem"""

st.set_page_config(
    page_title="AI Assistant Pro",
    page_icon="⚡",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* Title */
.chat-title {
    text-align: center;
    padding: 25px 0 5px 0;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}

.chat-subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 15px;
}

/* Badges */
.badge-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.4);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #c4b5fd;
    font-weight: 500;
}

/* Quick buttons */
.stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 12px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 10px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(167,139,250,0.3) !important;
    border-color: #a78bfa !important;
    transform: translateY(-1px) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    color: #f1f5f9 !important;
}

/* Make all text in chat visible */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #f1f5f9 !important;
}

/* Code blocks */
[data-testid="stChatMessage"] code {
    background: rgba(0,0,0,0.4) !important;
    color: #34d399 !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
    font-size: 0.9rem !important;
}

[data-testid="stChatMessage"] pre {
    background: rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    overflow-x: auto !important;
}

[data-testid="stChatMessage"] pre code {
    color: #e2e8f0 !important;
    background: transparent !important;
    padding: 0 !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
    background: transparent !important;
    font-size: 0.95rem !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.1) !important;
    margin: 15px 0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.1) !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="chat-title">⚡ AI Assistant Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">Powered by Gemini 2.5 Flash • Fast • Accurate • Always Updated</div>', unsafe_allow_html=True)

st.markdown("""
<div class="badge-row">
    <span class="badge">💻 Advanced Coding</span>
    <span class="badge">🌐 Web Builder</span>
    <span class="badge">📰 Current Affairs</span>
    <span class="badge">🤖 AI Assistant</span>
    <span class="badge">📊 Data Analysis</span>
</div>
""", unsafe_allow_html=True)

# Quick action buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("💻 Code", use_container_width=True):
        st.session_state.quick = "Write me a complete Python script that "
with col2:
    if st.button("🌐 Website", use_container_width=True):
        st.session_state.quick = "Build me a complete modern website with HTML CSS JS for "
with col3:
    if st.button("📰 News", use_container_width=True):
        st.session_state.quick = "Tell me the latest news and current affairs about "
with col4:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.gemini_history = [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": "Ready!"}]}
        ]
        st.rerun()

st.divider()

# Sidebar - Chat History
with st.sidebar:
    st.markdown("### 💬 Chat History")
    st.markdown("---")
    if "messages" in st.session_state and st.session_state.messages:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                preview = msg["content"][:40] + "..." if len(msg["content"]) > 40 else msg["content"]
                st.markdown(f"🧑 {preview}")
    else:
        st.markdown("*No chat history yet*")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(f"**Model:** Gemini 2.5 Flash")
    st.markdown(f"**Date:** {today}")
    st.markdown("**Capabilities:**")
    st.markdown("- Advanced Coding")
    st.markdown("- Website Building")
    st.markdown("- Current Affairs")
    st.markdown("- Data Analysis")
    st.markdown("- Personal Assistant")

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood! Ready to help!"}]}
    ]

# Show messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""👋 **Welcome to AI Assistant Pro!**

I am your all-in-one AI powerhouse. Here is what I can do for you:

💻 **Advanced Coding** — Python, JavaScript, React, Node.js, SQL and more
🌐 **Website Builder** — Complete modern websites with animations & responsive design
📰 **Current Affairs** — Up to date knowledge as of {today}
📊 **Data Analysis** — Analyze data, spot patterns, generate insights
🤖 **Personal Assistant** — Writing, planning, emails, summaries and more

**Just type anything below and I will get it done!** ⚡""")

# Chat input
if user_input := st.chat_input("Ask me anything — code, websites, news, analysis..."):
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
                response = requests.post(GEMINI_URL, json=data, timeout=60)
                result = response.json()

                if "candidates" in result:
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    reply = f"⚠️ Error: {result.get('error', {}).get('message', 'Unknown error. Please try again!')}"

            except requests.exceptions.Timeout:
                reply = "⏱️ Request timed out. Please try again!"
            except Exception as e:
                reply = f"⚠️ Something went wrong: {str(e)}"

        st.markdown(reply)

    st.session_state.gemini_history.append({"role": "model", "parts": [{"text": reply}]})
    st.session_state.messages.append({"role": "assistant", "content": reply})

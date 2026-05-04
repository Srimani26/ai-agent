import requests
import streamlit as st
from datetime import datetime
import json

API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
today = datetime.now().strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""You are an elite AI Assistant built specifically for an AI Engineer and Automation Engineer.
Today's date is {today}.

Your owner is an AI Engineer and Automation Engineer. Always treat them as an expert.

You specialize in:
1. AI & ML ENGINEERING — LLMs, RAG, agents, fine-tuning, embeddings, vector DBs, LangChain, LlamaIndex, Hugging Face, OpenAI, Gemini, Claude APIs
2. AUTOMATION ENGINEERING — n8n, Make.com, Zapier, Python automation, web scraping, bots, RPA, task scheduling
3. ADVANCED CODING — Python, JavaScript, React, Node.js, FastAPI, SQL, Docker, APIs. Always write production-ready code with error handling
4. WEBSITE BUILDER — Build complete modern websites with HTML/CSS/JS. Include animations, glassmorphism, responsive design
5. CURRENT AFFAIRS — Today is {today}. Give accurate up to date information about AI, tech and world news
6. DATA ANALYSIS — Pandas, numpy, data pipelines, analysis and visualization logic
7. DEVOPS & TOOLS — Git, Docker, GitHub Actions, cloud deployment, environment setup

Rules:
- Always write complete, production-ready, copy-paste ready code
- Use proper code blocks with language labels ```python, ```javascript etc
- For websites: give full single file HTML/CSS/JS with modern design
- Be concise but complete — no fluff
- Structure answers with headers for long responses
- Always think like a senior engineer
- If asked about latest AI models, tools or news, give the most current info you know"""

st.set_page_config(
    page_title="AI Assistant Pro",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

.chat-title {
    text-align: center;
    padding: 20px 0 4px 0;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.chat-subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 12px;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.4);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.78rem;
    color: #c4b5fd;
    font-weight: 500;
}

.stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: rgba(167,139,250,0.3) !important;
    border-color: #a78bfa !important;
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    margin-bottom: 10px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] strong {
    color: #f1f5f9 !important;
}

[data-testid="stChatMessage"] code {
    background: rgba(0,0,0,0.5) !important;
    color: #34d399 !important;
    border-radius: 5px !important;
    padding: 2px 6px !important;
}

[data-testid="stChatMessage"] pre {
    background: #0d1117 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 14px !important;
    overflow-x: auto !important;
}

[data-testid="stChatMessage"] pre code {
    color: #e2e8f0 !important;
    background: transparent !important;
    padding: 0 !important;
}

/* THIS FIXES THE CHAT INPUT TEXT VISIBILITY */
[data-testid="stChatInput"] {
    background: #1e1b4b !important;
    border: 1.5px solid rgba(167,139,250,0.5) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    color: #f1f5f9 !important;
    background: #1e1b4b !important;
    caret-color: #a78bfa !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
}

hr { border-color: rgba(255,255,255,0.08) !important; margin: 12px 0 !important; }

[data-testid="stSidebar"] {
    background: #0f0c29 !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e2e8f0 !important;
}

.history-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 6px;
    font-size: 0.82rem;
    color: #cbd5e1;
    cursor: pointer;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.stat-box {
    background: rgba(167,139,250,0.1);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin-bottom: 8px;
}
.stat-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: #a78bfa;
}
.stat-label {
    font-size: 0.75rem;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Ready! I am your AI & Automation Engineering assistant."}]}
    ]
if "total_chats" not in st.session_state:
    st.session_state.total_chats = 0
if "mode" not in st.session_state:
    st.session_state.mode = "General"

# SIDEBAR
with st.sidebar:
    st.markdown("### ⚡ AI Assistant Pro")
    st.markdown("---")

    # Stats
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(st.session_state.messages)}</div>
            <div class="stat-label">Messages</div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{st.session_state.total_chats}</div>
            <div class="stat-label">Sessions</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 Quick Mode")

    modes = {
        "🤖 General": "General",
        "💻 AI Engineer": "AI Engineer",
        "⚙️ Automation": "Automation",
        "🌐 Web Builder": "Web Builder",
        "🐍 Python": "Python",
        "📊 Data Analysis": "Data Analysis"
    }

    for label, mode in modes.items():
        if st.button(label, use_container_width=True, key=f"mode_{mode}"):
            st.session_state.mode = mode
            mode_prompts = {
                "General": "Help me with: ",
                "AI Engineer": "As an AI engineer, help me with: ",
                "Automation": "Build me an automation script for: ",
                "Web Builder": "Build me a complete modern website for: ",
                "Python": "Write me production-ready Python code for: ",
                "Data Analysis": "Analyze and help me understand: "
            }
            st.session_state.quick = mode_prompts[mode]

    st.markdown("---")
    st.markdown(f"**Active Mode:** `{st.session_state.mode}`")
    st.markdown("---")

    st.markdown("### 💬 Chat History")
    if st.session_state.messages:
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-8:]:
            preview = msg["content"][:35] + "..." if len(msg["content"]) > 35 else msg["content"]
            st.markdown(f'<div class="history-item">🧑 {preview}</div>', unsafe_allow_html=True)
    else:
        st.markdown("*Start chatting to see history*")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.total_chats += 1
        st.session_state.messages = []
        st.session_state.gemini_history = [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": "Ready! New session started."}]}
        ]
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Model:** Gemini 2.5 Flash")
    st.markdown(f"**Date:** {today}")
    st.markdown("**Built for:** AI Engineer")

# MAIN AREA
st.markdown('<div class="chat-title">⚡ AI Assistant Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">Your Personal AI & Automation Engineering Assistant</div>', unsafe_allow_html=True)

st.markdown("""
<div class="badge-row">
    <span class="badge">🤖 LLMs & RAG</span>
    <span class="badge">⚙️ Automation</span>
    <span class="badge">💻 Python</span>
    <span class="badge">🌐 Web Builder</span>
    <span class="badge">📊 Data Analysis</span>
    <span class="badge">📰 Current Affairs</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# Show messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""👋 **Welcome back, Engineer!**

I am your personal AI & Automation Engineering assistant. Here is what I can do:

🤖 **AI Engineering** — LLMs, RAG pipelines, agents, embeddings, vector DBs, LangChain, Hugging Face
⚙️ **Automation** — n8n, Make.com, Python bots, web scraping, task automation, RPA
💻 **Advanced Coding** — Python, JavaScript, React, FastAPI, Docker, production-ready code
🌐 **Website Builder** — Modern websites with animations and responsive design
📊 **Data Analysis** — Pandas, pipelines, insights and visualization logic
📰 **Current Affairs** — Latest AI, tech and world news as of {today}

**Use the sidebar to switch modes, or just type anything below!** ⚡""")

# Chat input
if user_input := st.chat_input("Ask me anything — AI, automation, code, websites..."):
    final_input = user_input

    with st.chat_message("user"):
        st.markdown(final_input)

    st.session_state.messages.append({"role": "user", "content": final_input})

    # Add mode context to message
    mode_context = {
        "AI Engineer": "Answer as a senior AI engineer. Be technical and precise. ",
        "Automation": "Focus on automation, scripts and workflows. Give working code. ",
        "Web Builder": "Build a complete modern website. Give full HTML/CSS/JS code. ",
        "Python": "Write production-ready Python code with proper structure and error handling. ",
        "Data Analysis": "Focus on data analysis. Use pandas/numpy. Be analytical. ",
        "General": ""
    }

    enhanced_input = mode_context.get(st.session_state.mode, "") + final_input
    st.session_state.gemini_history.append({"role": "user", "parts": [{"text": enhanced_input}]})

    with st.chat_message("assistant"):
        with st.spinner("⚡ Processing..."):
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
                    reply = f"⚠️ {result.get('error', {}).get('message', 'Unknown error. Please try again!')}"

            except requests.exceptions.Timeout:
                reply = "⏱️ Request timed out. Please try again!"
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.gemini_history.append({"role": "model", "parts": [{"text": reply}]})
    st.session_state.messages.append({"role": "assistant", "content": reply})

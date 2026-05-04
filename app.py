import requests
import streamlit as st
from datetime import datetime
import json
import os

API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
today = datetime.now().strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""You are ARIA — Advanced Reasoning & Intelligence Assistant.
You are built exclusively for a professional AI Engineer and Automation Engineer.
Today's date is {today}.

CORE EXPERTISE:
━━━━━━━━━━━━━━
1. AI ENGINEERING
   - LLM fine-tuning, RAG pipelines, vector databases (Pinecone, Weaviate, ChromaDB)
   - AI agents with LangChain, LlamaIndex, AutoGen, CrewAI
   - Embeddings, semantic search, prompt engineering
   - Hugging Face, OpenAI, Gemini, Claude, Mistral APIs
   - Model deployment, optimization, quantization

2. AUTOMATION ENGINEERING  
   - n8n, Make.com, Zapier workflow design
   - Python automation, Selenium, Playwright, BeautifulSoup
   - API integrations, webhooks, scheduled tasks
   - RPA, task orchestration, event-driven systems

3. ADVANCED CODING
   - Python (FastAPI, Django, Flask, async, decorators, OOP)
   - JavaScript, TypeScript, React, Next.js, Node.js
   - Docker, Kubernetes, CI/CD, GitHub Actions
   - SQL, MongoDB, Redis, PostgreSQL
   - Always write production-ready code with proper error handling

4. WEBSITE & APP BUILDING
   - Modern responsive websites with glassmorphism, animations
   - Full-stack apps with React + FastAPI/Node.js
   - Landing pages, dashboards, admin panels
   - Always give complete working single-file code

5. CURRENT TECH & AI NEWS
   - Latest AI models, tools, frameworks as of {today}
   - Industry trends, best practices, new releases

RESPONSE RULES:
━━━━━━━━━━━━━━
- Write COMPLETE, production-ready, copy-paste code always
- Use proper ```language code blocks
- For websites: complete HTML/CSS/JS in one file with modern design
- Structure with clear headers for complex answers
- Think like a SENIOR AI ENGINEER — precise, efficient, no fluff
- Always suggest best practices and potential improvements
- If asked about latest tools, give most current recommendations"""

st.set_page_config(
    page_title="ARIA — AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PERSISTENT STORAGE ──
HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def create_new_session():
    """Create a new chat session and save current to history"""
    current_messages = st.session_state.messages.copy()
    if len(current_messages) > 0:
        title = "New Chat"
        for msg in current_messages:
            if msg["role"] == "user":
                title = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
                break

        session = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "title": title,
            "date": datetime.now().strftime("%b %d, %H:%M"),
            "messages": current_messages,
            "mode": st.session_state.mode
        }
        st.session_state.chat_history.insert(0, session)
        save_history(st.session_state.chat_history)

    st.session_state.messages = []
    st.session_state.gemini_history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "ARIA online. Ready to assist with AI engineering and automation."}]}
    ]
    st.session_state.total_sessions += 1

def load_session(session_id):
    """Load a previous session"""
    for session in st.session_state.chat_history:
        if session["id"] == session_id:
            st.session_state.messages = session["messages"].copy()
            gemini_hist = [
                {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
                {"role": "model", "parts": [{"text": "ARIA online. Ready to assist."}]}
            ]
            for msg in session["messages"]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_hist.append({"role": role, "parts": [{"text": msg["content"]}]})
            st.session_state.gemini_history = gemini_hist
            st.session_state.mode = session.get("mode", "General")
            break

def delete_session(session_id):
    """Delete a session from history"""
    st.session_state.chat_history = [s for s in st.session_state.chat_history if s["id"] != session_id]
    save_history(st.session_state.chat_history)

# ── SESSION STATE INIT ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "ARIA online. Ready to assist with AI engineering and automation."}]}
    ]
if "total_sessions" not in st.session_state:
    st.session_state.total_sessions = 0
if "mode" not in st.session_state:
    st.session_state.mode = "General"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history()

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, header, footer {visibility: hidden;}
.stApp { background: #0a0a0f; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e3a !important;
    width: 280px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 0.75rem !important;
}

.brand {
    text-align: center;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #1e1e3a;
    margin-bottom: 1rem;
}
.brand-name {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}
.brand-sub {
    font-size: 0.6rem;
    color: #475569;
    letter-spacing: 1.5px;
    margin-top: 2px;
    text-transform: uppercase;
}

/* New Chat Button */
.new-chat-btn {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    width: 100% !important;
    margin-bottom: 1rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
.new-chat-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important;
}

/* History Section */
.history-header {
    font-size: 0.65rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 1rem 0 0.5rem 0;
}

.history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.history-item:hover {
    background: rgba(124,58,237,0.1);
    border-color: rgba(124,58,237,0.25);
}
.history-title {
    font-size: 0.8rem;
    color: #cbd5e1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.history-date {
    font-size: 0.65rem;
    color: #475569;
    margin-top: 2px;
}

/* Mode Buttons */
.mode-btn {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
    font-size: 0.8rem !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 4px !important;
    transition: all 0.2s ease !important;
}
.mode-btn:hover {
    background: rgba(124,58,237,0.15) !important;
    border-color: rgba(124,58,237,0.3) !important;
    color: #a78bfa !important;
    transform: translateX(3px);
}

/* ── MAIN ── */
.main-wrapper {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 80px);
}

.main-header {
    text-align: center;
    padding: 1rem 0 0.5rem 0;
    flex-shrink: 0;
}
.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed 0%, #2563eb 50%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 4px;
}
.main-tagline {
    font-size: 0.85rem;
    color: #475569;
    letter-spacing: 0.3px;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin: 0.75rem 0 1rem 0;
    flex-wrap: wrap;
    flex-shrink: 0;
}
.badge {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 16px;
    padding: 3px 10px;
    font-size: 0.75rem;
    color: #a78bfa;
    font-weight: 500;
}

/* ── CHAT ── */
.chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem 0;
    min-height: 0;
}

.stChatMessage {
    background: #111122 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    margin-bottom: 0.75rem !important;
}
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(37,99,235,0.06), rgba(124,58,237,0.04)) !important;
    border-color: rgba(37,99,235,0.2) !important;
}
.stChatMessage p, .stChatMessage li {
    color: #e2e8f0 !important;
    line-height: 1.6 !important;
    margin-bottom: 0.4rem !important;
}
.stChatMessage h1, .stChatMessage h2, .stChatMessage h3 {
    color: #a78bfa !important;
    margin: 0.75rem 0 0.4rem 0 !important;
}
.stChatMessage code:not(pre code) {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(124,58,237,0.12) !important;
    color: #a78bfa !important;
    border-radius: 5px !important;
    padding: 2px 6px !important;
    font-size: 0.85em !important;
}
.stChatMessage pre {
    background: #060610 !important;
    border: 1px solid #1e1e3a !important;
    border-left: 3px solid #7c3aed !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    margin: 0.75rem 0 !important;
}
.stChatMessage pre code {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e2e8f0 !important;
    background: transparent !important;
    font-size: 0.85rem !important;
    line-height: 1.5 !important;
}

/* ── INPUT ── */
.chat-input-wrapper {
    flex-shrink: 0;
    padding: 0.5rem 0 1rem 0;
    background: #0a0a0f;
}
.stChatInputContainer {
    background: #111122 !important;
    border: 1.5px solid #2d2d5e !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
}
.stChatInputContainer:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1), 0 4px 20px rgba(0,0,0,0.4) !important;
}
.stChatInputContainer textarea {
    color: #f1f5f9 !important;
    background: transparent !important;
    caret-color: #7c3aed !important;
    font-size: 0.9rem !important;
    line-height: 1.5 !important;
    padding: 10px 12px !important;
}
.stChatInputContainer textarea::placeholder {
    color: #475569 !important;
}
.stChatInputContainer button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    margin-right: 4px !important;
}

/* Welcome */
.welcome-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.06), rgba(37,99,235,0.04));
    border: 1px solid rgba(124,58,237,0.12);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.5rem 0 1rem 0;
}
.welcome-card h3 {
    color: #a78bfa !important;
    margin-top: 0 !important;
    font-size: 1.1rem !important;
}
.welcome-card table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.75rem;
}
.welcome-card th {
    background: rgba(124,58,237,0.1);
    border: 1px solid #1e1e3a;
    padding: 6px 10px;
    text-align: left;
    color: #a78bfa;
    font-size: 0.8rem;
    font-weight: 600;
}
.welcome-card td {
    border: 1px solid #1e1e3a;
    padding: 6px 10px;
    color: #cbd5e1;
    font-size: 0.8rem;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2d2d5e; border-radius: 3px; }

@media (max-width: 768px) {
    .main-title { font-size: 2rem !important; }
    .badge-row { gap: 4px; }
    .badge { font-size: 0.7rem; padding: 2px 8px; }
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-name">ARIA</div>
        <div class="brand-sub">AI Engineering Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    # NEW CHAT BUTTON
    if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
        create_new_session()
        st.rerun()

    st.markdown("---")

    # CHAT HISTORY
    st.markdown('<div class="history-header">💬 Chat History</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        for session in st.session_state.chat_history[:20]:
            # Use HTML for the history item to avoid f-string issues
            st.markdown(f"""
            <div class="history-item" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '{session['id']}'}}, '*')">
                <div class="history-title">📄 {session['title']}</div>
                <div class="history-date">{session['date']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Use columns for load/delete buttons
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                if st.button(f"Load: {session['title'][:20]}", key=f"load_{session['id']}", use_container_width=True):
                    load_session(session["id"])
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_{session['id']}", help="Delete chat"):
                    delete_session(session["id"])
                    st.rerun()
    else:
        st.markdown('<p style="font-size:0.75rem;color:#475569;text-align:center;padding:1rem 0">No previous chats</p>', unsafe_allow_html=True)

    st.markdown("---")

    # QUICK MODES
    st.markdown('<div class="history-header">⚡ Quick Modes</div>', unsafe_allow_html=True)

    modes = [
        ("🤖 AI Engineering", "AI Engineer"),
        ("⚙️ Automation", "Automation"),
        ("🌐 Web Builder", "Web Builder"),
        ("🐍 Python Expert", "Python"),
        ("📊 Data Analysis", "Data Analysis"),
        ("💬 General", "General"),
    ]

    for label, mode_key in modes:
        btn_type = "primary" if st.session_state.mode == mode_key else "secondary"
        if st.button(label, key=f"mode_{mode_key}", use_container_width=True, type=btn_type):
            st.session_state.mode = mode_key
            st.rerun()

    st.markdown("---")

    # Stats
    total_msgs = len(st.session_state.messages)
    total_hist = len(st.session_state.chat_history)
    st.markdown(f"""
    <div style="display:flex;gap:8px;margin-top:0.5rem">
        <div style="flex:1;background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.15);border-radius:8px;padding:8px;text-align:center">
            <div style="font-size:1.2rem;font-weight:700;color:#a78bfa">{total_msgs}</div>
            <div style="font-size:0.6rem;color:#475569;text-transform:uppercase;letter-spacing:0.5px">Messages</div>
        </div>
        <div style="flex:1;background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.15);border-radius:8px;padding:8px;text-align:center">
            <div style="font-size:1.2rem;font-weight:700;color:#a78bfa">{total_hist}</div>
            <div style="font-size:0.6rem;color:#475569;text-transform:uppercase;letter-spacing:0.5px">Saved</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:0.65rem;color:#374151;text-align:center;margin-top:1rem;opacity:0.6">
        ARIA • Gemini 2.5 Flash<br>Built for AI Engineers
    </p>
    """, unsafe_allow_html=True)

# ── MAIN CONTENT ──
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <div class="main-title">⚡ ARIA</div>
    <div class="main-tagline">Advanced Reasoning & Intelligence Assistant</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="badge-row">
    <span class="badge">🤖 LLMs & RAG</span>
    <span class="badge">⚙️ n8n & Make.com</span>
    <span class="badge">🐍 Python</span>
    <span class="badge">🌐 Web Builder</span>
    <span class="badge">📊 Data Analysis</span>
    <span class="badge">🔗 API Integration</span>
    <span class="badge">🚀 Deployment</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# Chat Messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""
        <div class="welcome-card">

### 👋 Welcome back, Engineer!

I am **ARIA** — your dedicated AI & Automation Engineering assistant.

| Capability | Details |
|---|---|
| 🤖 AI Engineering | LLMs, RAG, agents, LangChain, vector DBs |
| ⚙️ Automation | n8n, Make.com, Python bots, Playwright |
| 🐍 Advanced Python | FastAPI, async, OOP, production patterns |
| 🌐 Website Builder | Full HTML/CSS/JS with modern animations |
| 📊 Data Analysis | Pandas, pipelines, insights, visualization |
| 🔗 API Integration | REST, webhooks, OAuth, third-party APIs |
| 🚀 DevOps | Docker, GitHub Actions, cloud deployment |

**Today is {today}** — Ready to build something amazing.

*Select a mode from the sidebar or type below!* ⚡
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat Input
st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)

if user_input := st.chat_input("Ask ARIA anything — AI, automation, code, websites, data..."):
    mode_context = {
        "AI Engineer": "As a senior AI engineer: be highly technical and precise. ",
        "Automation": "As an automation expert: give complete working code and workflows. ",
        "Web Builder": "Build a complete, stunning, modern website. Full HTML/CSS/JS in one file. ",
        "Python": "As a Python expert: write clean, production-ready Python. ",
        "Data Analysis": "As a data engineer: be analytical, use pandas/numpy, give insights. ",
        "General": ""
    }

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    enhanced = mode_context.get(st.session_state.mode, "") + user_input
    st.session_state.gemini_history.append({"role": "user", "parts": [{"text": enhanced}]})

    with st.chat_message("assistant"):
        with st.spinner("⚡ ARIA is thinking..."):
            try:
                data = {
                    "contents": st.session_state.gemini_history,
                    "generationConfig": {
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxOutputTokens": 8192
                    }
                }
                resp = requests.post(GEMINI_URL, json=data, timeout=60)
                result = resp.json()

                if "candidates" in result:
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    reply = f"⚠️ Error: {result.get('error', {}).get('message', 'Please try again.')}"

            except requests.exceptions.Timeout:
                reply = "⏱️ Timeout — please try again!"
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.gemini_history.append({"role": "model", "parts": [{"text": reply}]})
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Auto-save
    if len(st.session_state.messages) >= 2:
        current_first = st.session_state.messages[0]["content"] if st.session_state.messages else ""
        exists = any(s["messages"] and s["messages"][0]["content"] == current_first for s in st.session_state.chat_history)
        if not exists:
            title = current_first[:30] + "..." if len(current_first) > 30 else current_first
            session = {
                "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "title": title,
                "date": datetime.now().strftime("%b %d, %H:%M"),
                "messages": st.session_state.messages.copy(),
                "mode": st.session_state.mode
            }
            st.session_state.chat_history.insert(0, session)
            save_history(st.session_state.chat_history)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

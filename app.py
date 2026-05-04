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

5. CURRENT TECH & AI NEWS
   - Latest AI models, tools, frameworks as of {today}
   - Industry trends, best practices, new releases

RESPONSE RULES:
- Write COMPLETE, production-ready, copy-paste code always
- Use proper code blocks with language specified
- Think like a SENIOR AI ENGINEER — precise, efficient, no fluff
- Always suggest best practices and potential improvements"""

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="ARIA — AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STORAGE ──
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
    current_messages = st.session_state.messages.copy()
    if len(current_messages) > 0:
        title = "New Chat"
        for msg in current_messages:
            if msg["role"] == "user":
                title = msg["content"][:40] + "..." if len(msg["content"]) > 40 else msg["content"]
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
        {"role": "model", "parts": [{"text": "ARIA online. Ready to assist."}]}
    ]

def load_session(session_id):
    for session in st.session_state.chat_history:
        if session["id"] == session_id:
            st.session_state.messages = session["messages"].copy()
            gemini_hist = [
                {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
                {"role": "model", "parts": [{"text": "ARIA online."}]}
            ]
            for msg in session["messages"]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_hist.append({"role": role, "parts": [{"text": msg["content"]}]})
            st.session_state.gemini_history = gemini_hist
            st.session_state.mode = session.get("mode", "General")
            break

def delete_session(session_id):
    st.session_state.chat_history = [s for s in st.session_state.chat_history if s["id"] != session_id]
    save_history(st.session_state.chat_history)

# ── SESSION INIT ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "ARIA online. Ready to assist."}]}
    ]
if "mode" not in st.session_state:
    st.session_state.mode = "General"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history()

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, header, footer { visibility: hidden; }
.stApp { background: #f5f4f0; }

/* ══════════════════════════════════
   SIDEBAR
══════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #1a1a2e !important;
    border-right: none !important;
    width: 260px !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.12);
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Brand */
.sb-brand {
    padding: 28px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sb-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}
.sb-logo-icon {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.sb-logo-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 1px;
}
.sb-logo-sub {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.35);
    letter-spacing: 1.8px;
    text-transform: uppercase;
    padding-left: 44px;
}

/* New chat button */
.sb-actions { padding: 16px 16px 0; }
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px;
    padding: 10px 0 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(99,102,241,0.4) !important;
}

/* Section labels */
.sb-section {
    padding: 20px 20px 8px;
    font-size: 0.62rem;
    font-weight: 700;
    color: rgba(255,255,255,0.25);
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* History items */
.hist-item {
    margin: 0 10px 2px;
    border-radius: 9px;
    padding: 9px 12px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.18s ease;
}
.hist-item:hover {
    background: rgba(99,102,241,0.12);
    border-color: rgba(99,102,241,0.2);
}
.hist-title {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.75);
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 2px;
}
.hist-date {
    font-size: 0.65rem;
    color: rgba(255,255,255,0.28);
}

/* History buttons */
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.72rem !important;
    padding: 3px 6px !important;
    border-radius: 6px !important;
    text-align: left !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.85) !important;
}

/* Mode pills */
.mode-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    padding: 0 14px 16px;
}
.mode-pill {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.55) !important;
    font-size: 0.72rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 8px 6px !important;
    text-align: center !important;
    cursor: pointer;
    transition: all 0.18s ease !important;
}
.mode-pill.active {
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #a5b4fc !important;
}
.mode-pill:hover {
    background: rgba(99,102,241,0.12) !important;
    color: rgba(255,255,255,0.85) !important;
}

/* Stats row */
.sb-stats {
    display: flex;
    gap: 8px;
    padding: 0 14px 20px;
}
.stat-box {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
}
.stat-num { font-size: 1.1rem; font-weight: 700; color: #a5b4fc; font-family: 'Syne', sans-serif; }
.stat-lbl { font-size: 0.58rem; color: rgba(255,255,255,0.25); text-transform: uppercase; letter-spacing: 0.8px; margin-top: 2px; }

/* ══════════════════════════════════
   MAIN AREA
══════════════════════════════════ */
.block-container {
    padding: 2rem 2rem 0 2rem !important;
    max-width: 860px !important;
}

/* Header */
.main-header {
    background: white;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    border: 1px solid rgba(0,0,0,0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.hdr-left { display: flex; align-items: center; gap: 16px; }
.hdr-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3);
}
.hdr-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #0f0f1a;
    letter-spacing: 0.5px;
    line-height: 1;
    margin-bottom: 3px;
}
.hdr-sub { font-size: 0.8rem; color: #6b7280; font-weight: 400; }
.hdr-mode {
    background: #f0f0ff;
    border: 1px solid #c7d2fe;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #4f46e5;
    letter-spacing: 0.3px;
}

/* Capability pills */
.caps-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
}
.cap-pill {
    background: white;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.75rem;
    font-weight: 500;
    color: #374151;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

/* ══════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════ */
.stChatMessage {
    background: white !important;
    border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04) !important;
}
/* User messages */
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #f5f3ff !important;
    border-color: #ddd6fe !important;
}
.stChatMessage p, .stChatMessage li {
    color: #1f2937 !important;
    line-height: 1.7 !important;
    font-size: 0.9rem !important;
}
.stChatMessage h1, .stChatMessage h2, .stChatMessage h3 {
    color: #111827 !important;
    font-family: 'Syne', sans-serif !important;
    margin: 16px 0 8px 0 !important;
    font-weight: 700 !important;
}
.stChatMessage h3 { font-size: 1rem !important; color: #4f46e5 !important; }
.stChatMessage code:not(pre code) {
    font-family: 'DM Mono', monospace !important;
    background: #f0f0ff !important;
    color: #4f46e5 !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-size: 0.82em !important;
    border: 1px solid #e0e7ff !important;
}
.stChatMessage pre {
    background: #0f0f1a !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    margin: 14px 0 !important;
    overflow-x: auto !important;
}
.stChatMessage pre code {
    font-family: 'DM Mono', monospace !important;
    color: #e2e8f0 !important;
    background: transparent !important;
    font-size: 0.83rem !important;
    line-height: 1.6 !important;
}

/* Avatar icons */
.stChatMessage [data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border-radius: 10px !important;
}
.stChatMessage [data-testid="chatAvatarIcon-user"] {
    background: #ddd6fe !important;
    border-radius: 10px !important;
}

/* ══════════════════════════════════
   WELCOME CARD
══════════════════════════════════ */
.welcome-wrap {
    background: white;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.welcome-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 20px;
}
.cap-card {
    background: #fafafa;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 10px;
    padding: 14px 16px;
    transition: all 0.2s ease;
}
.cap-card:hover {
    border-color: #c7d2fe;
    background: #f5f3ff;
}
.cap-icon { font-size: 1.1rem; margin-bottom: 6px; }
.cap-title { font-size: 0.8rem; font-weight: 600; color: #111827; margin-bottom: 3px; }
.cap-desc { font-size: 0.72rem; color: #6b7280; line-height: 1.5; }

/* ══════════════════════════════════
   CHAT INPUT
══════════════════════════════════ */
.stChatInputContainer {
    background: white !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
    transition: all 0.2s ease !important;
}
.stChatInputContainer:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.08), 0 4px 20px rgba(0,0,0,0.06) !important;
}
.stChatInputContainer textarea {
    color: #111827 !important;
    background: transparent !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    caret-color: #6366f1 !important;
}
.stChatInputContainer textarea::placeholder {
    color: #9ca3af !important;
}
.stChatInputContainer button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
    margin: 4px !important;
}
.stChatInputContainer button:hover {
    transform: scale(1.05) !important;
}

/* Divider cleanup */
hr { border: none !important; border-top: 1px solid rgba(0,0,0,0.07) !important; margin: 12px 0 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* Spinner */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* No extra padding on main column */
.main > div { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════
# SIDEBAR
# ══════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-logo">
            <div class="sb-logo-icon">⚡</div>
            <div class="sb-logo-name">ARIA</div>
        </div>
        <div class="sb-logo-sub">AI Engineering Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-actions">', unsafe_allow_html=True)
    if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True, type="primary"):
        create_new_session()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # History
    st.markdown('<div class="sb-section">Recent Chats</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        for session in st.session_state.chat_history[:15]:
            st.markdown(f"""
            <div class="hist-item">
                <div class="hist-title">📄 {session['title']}</div>
                <div class="hist-date">{session['date']}</div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns([5, 1])
            with c1:
                if st.button(f"↩ {session['title'][:22]}", key=f"load_{session['id']}", use_container_width=True):
                    load_session(session["id"])
                    st.rerun()
            with c2:
                if st.button("✕", key=f"del_{session['id']}", help="Delete"):
                    delete_session(session["id"])
                    st.rerun()
    else:
        st.markdown('<p style="font-size:0.73rem;color:rgba(255,255,255,0.22);text-align:center;padding:16px 0">No previous chats</p>', unsafe_allow_html=True)

    # Modes
    st.markdown('<div class="sb-section">Mode</div>', unsafe_allow_html=True)

    modes = [
        ("🤖 AI Eng", "AI Engineer"),
        ("⚙️ Automation", "Automation"),
        ("🌐 Web Build", "Web Builder"),
        ("🐍 Python", "Python"),
        ("📊 Data", "Data Analysis"),
        ("💬 General", "General"),
    ]

    st.markdown('<div class="mode-grid">', unsafe_allow_html=True)
    for label, mode_key in modes:
        active = "active" if st.session_state.mode == mode_key else ""
        btn_type = "primary" if st.session_state.mode == mode_key else "secondary"
        if st.button(label, key=f"mode_{mode_key}", use_container_width=True, type=btn_type):
            st.session_state.mode = mode_key
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    total_msgs = len(st.session_state.messages)
    total_hist = len(st.session_state.chat_history)
    st.markdown(f"""
    <div class="sb-stats">
        <div class="stat-box">
            <div class="stat-num">{total_msgs}</div>
            <div class="stat-lbl">Messages</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">{total_hist}</div>
            <div class="stat-lbl">Saved</div>
        </div>
    </div>
    <p style="font-size:0.6rem;color:rgba(255,255,255,0.15);text-align:center;padding-bottom:12px">
        Powered by Gemini 2.5 Flash
    </p>
    """, unsafe_allow_html=True)

# ══════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════

# Header bar
mode_label = {
    "AI Engineer": "🤖 AI Engineering",
    "Automation": "⚙️ Automation",
    "Web Builder": "🌐 Web Builder",
    "Python": "🐍 Python",
    "Data Analysis": "📊 Data Analysis",
    "General": "💬 General"
}.get(st.session_state.mode, "💬 General")

st.markdown(f"""
<div class="main-header">
    <div class="hdr-left">
        <div class="hdr-icon">⚡</div>
        <div>
            <div class="hdr-title">ARIA</div>
            <div class="hdr-sub">Advanced Reasoning & Intelligence Assistant</div>
        </div>
    </div>
    <div class="hdr-mode">{mode_label}</div>
</div>
""", unsafe_allow_html=True)

# Capability chips
st.markdown("""
<div class="caps-row">
    <span class="cap-pill">🔗 LLMs & RAG</span>
    <span class="cap-pill">⚙️ n8n · Make.com</span>
    <span class="cap-pill">🐍 Python</span>
    <span class="cap-pill">🌐 Web Builder</span>
    <span class="cap-pill">📊 Data Analysis</span>
    <span class="cap-pill">🔌 API Integration</span>
    <span class="cap-pill">🚀 Deployment</span>
</div>
""", unsafe_allow_html=True)

# Chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Welcome card (shown when no messages)
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""
        <div class="welcome-wrap">
            <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:700;color:#0f0f1a;margin-bottom:4px">
                👋 Welcome back, Engineer!
            </div>
            <div style="font-size:0.83rem;color:#6b7280;line-height:1.6">
                I'm <strong>ARIA</strong> — your dedicated AI &amp; Automation Engineering assistant. Today is <strong>{today}</strong>. Select a mode from the sidebar or ask me anything below.
            </div>
            <div class="welcome-grid">
                <div class="cap-card">
                    <div class="cap-icon">🤖</div>
                    <div class="cap-title">AI Engineering</div>
                    <div class="cap-desc">LLMs, RAG pipelines, agents, vector databases, embeddings</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">⚙️</div>
                    <div class="cap-title">Automation</div>
                    <div class="cap-desc">n8n, Make.com, Python bots, Playwright, Selenium</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">🌐</div>
                    <div class="cap-title">Web Builder</div>
                    <div class="cap-desc">Full-stack apps, landing pages, dashboards, React + FastAPI</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">🐍</div>
                    <div class="cap-title">Python Expert</div>
                    <div class="cap-desc">FastAPI, async, OOP, production patterns, data pipelines</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">📊</div>
                    <div class="cap-title">Data Analysis</div>
                    <div class="cap-desc">Pandas, NumPy, visualization, insights, ML pipelines</div>
                </div>
                <div class="cap-card">
                    <div class="cap-icon">🔌</div>
                    <div class="cap-title">API Integration</div>
                    <div class="cap-desc">REST, webhooks, OAuth, OpenAI, Gemini, Claude APIs</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat Input
mode_context = {
    "AI Engineer": "As a senior AI engineer, be highly technical and precise. ",
    "Automation": "As an automation expert, give complete working code and workflows. ",
    "Web Builder": "Build a complete, stunning, modern website. Full HTML/CSS/JS in one file. ",
    "Python": "As a Python expert, write clean, production-ready Python. ",
    "Data Analysis": "As a data engineer, be analytical, use pandas/numpy, give insights. ",
    "General": ""
}

if user_input := st.chat_input(f"Ask ARIA anything — AI, automation, code, websites, data..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    enhanced = mode_context.get(st.session_state.mode, "") + user_input
    st.session_state.gemini_history.append({"role": "user", "parts": [{"text": enhanced}]})

    with st.chat_message("assistant"):
        with st.spinner("ARIA is thinking..."):
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
                reply = "⏱️ Request timed out — please try again."
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.gemini_history.append({"role": "model", "parts": [{"text": reply}]})
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Auto-save session
    if len(st.session_state.messages) >= 2:
        current_first = st.session_state.messages[0]["content"] if st.session_state.messages else ""
        exists = any(s["messages"] and s["messages"][0]["content"] == current_first for s in st.session_state.chat_history)
        if not exists:
            title = current_first[:40] + "..." if len(current_first) > 40 else current_first
            session = {
                "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "title": title,
                "date": datetime.now().strftime("%b %d, %H:%M"),
                "messages": st.session_state.messages.copy(),
                "mode": st.session_state.mode
            }
            st.session_state.chat_history.insert(0, session)
            save_history(st.session_state.chat_history)

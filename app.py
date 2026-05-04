import requests
import streamlit as st
from datetime import datetime

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

# ── FIXED CSS — Addresses all spacing, alignment, and selector issues ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── GLOBAL RESETS (Conservative) ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* ── APP BACKGROUND ── */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 100%);
}

/* ── SIDEBAR FIXES ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #111122 100%) !important;
    border-right: 1px solid rgba(124, 58, 237, 0.15) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem !important;
}

section[data-testid="stSidebar"] .stMarkdown {
    color: #e2e8f0 !important;
}

/* Brand */
.brand {
    text-align: center;
    padding: 0.5rem 0 1.5rem 0;
    margin-bottom: 0.5rem;
}
.brand-name {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #2563eb, #059669);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
}
.brand-sub {
    font-size: 0.65rem;
    color: #64748b;
    letter-spacing: 2px;
    margin-top: 4px;
    text-transform: uppercase;
}

/* Stats Grid */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 1rem 0;
}
.stat-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(37,99,235,0.08));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 12px;
    padding: 12px 8px;
    text-align: center;
    transition: all 0.2s ease;
}
.stat-card:hover {
    border-color: rgba(124,58,237,0.4);
    transform: translateY(-1px);
}
.stat-num {
    font-size: 1.5rem;
    font-weight: 700;
    color: #a78bfa !important;
    line-height: 1;
}
.stat-lbl {
    font-size: 0.65rem;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 6px;
}

/* Section Titles */
.section-title {
    font-size: 0.7rem;
    font-weight: 700;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 1.5rem 0 0.75rem 0;
}

/* Sidebar Buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #cbd5e1 !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 6px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124,58,237,0.15) !important;
    border-color: rgba(124,58,237,0.4) !important;
    color: #a78bfa !important;
    transform: translateX(4px);
}
section[data-testid="stSidebar"] .stButton > button:active {
    transform: translateX(2px) scale(0.98);
}

/* History Items */
.history-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 0.8rem;
    color: #94a3b8;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: all 0.2s ease;
}
.history-item:hover {
    background: rgba(124,58,237,0.08);
    border-color: rgba(124,58,237,0.2);
    color: #cbd5e1;
}

/* ── MAIN CONTENT AREA ── */
.main-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.main-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed 0%, #2563eb 50%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.main-tagline {
    font-size: 1rem;
    color: #475569;
    letter-spacing: 0.5px;
    font-weight: 400;
}

/* Badges */
.badge-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 1.5rem 0 2rem 0;
    flex-wrap: wrap;
}
.badge {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: #a78bfa;
    font-weight: 500;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}
.badge:hover {
    background: rgba(124,58,237,0.15);
    border-color: rgba(124,58,237,0.35);
    transform: translateY(-1px);
}

/* ── CHAT MESSAGES — FIXED SELECTORS ── */
/* Target the message containers properly */
.stChatMessage {
    background: #111122 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 16px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}

/* User message variant */
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(124,58,237,0.05)) !important;
    border-color: rgba(37,99,235,0.25) !important;
}

/* Message content typography */
.stChatMessage p,
.stChatMessage li {
    color: #e2e8f0 !important;
    line-height: 1.7 !important;
    margin-bottom: 0.5rem !important;
}
.stChatMessage h1,
.stChatMessage h2,
.stChatMessage h3 {
    color: #a78bfa !important;
    margin: 1rem 0 0.5rem 0 !important;
    font-weight: 600 !important;
}
.stChatMessage h1 { font-size: 1.5rem !important; }
.stChatMessage h2 { font-size: 1.25rem !important; }
.stChatMessage h3 { font-size: 1.1rem !important; }

/* Inline code */
.stChatMessage code:not(pre code) {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(124,58,237,0.15) !important;
    color: #a78bfa !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    font-size: 0.85em !important;
    border: 1px solid rgba(124,58,237,0.2);
}

/* Code blocks */
.stChatMessage pre {
    background: #060610 !important;
    border: 1px solid #1e1e3a !important;
    border-left: 3px solid #7c3aed !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    overflow-x: auto !important;
    margin: 1rem 0 !important;
}
.stChatMessage pre code {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e2e8f0 !important;
    background: transparent !important;
    padding: 0 !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
}

/* Tables in messages */
.stChatMessage table {
    border-collapse: collapse;
    margin: 1rem 0;
    width: 100%;
}
.stChatMessage th {
    background: rgba(124,58,237,0.1);
    border: 1px solid #1e1e3a;
    padding: 8px 12px;
    text-align: left;
    color: #a78bfa;
    font-weight: 600;
}
.stChatMessage td {
    border: 1px solid #1e1e3a;
    padding: 8px 12px;
    color: #cbd5e1;
}
.stChatMessage tr:nth-child(even) {
    background: rgba(255,255,255,0.02);
}

/* ── CHAT INPUT — FIXED ── */
.stChatInputContainer {
    background: #111122 !important;
    border: 1.5px solid #2d2d5e !important;
    border-radius: 16px !important;
    padding: 4px 6px !important;
    margin: 1rem 0 2rem 0 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease;
}
.stChatInputContainer:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15), 0 4px 12px rgba(0,0,0,0.3) !important;
}
.stChatInputContainer textarea {
    color: #f1f5f9 !important;
    background: transparent !important;
    caret-color: #7c3aed !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    padding: 12px !important;
}
.stChatInputContainer textarea::placeholder {
    color: #475569 !important;
}

/* Send button */
.stChatInputContainer button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    transition: all 0.2s ease !important;
}
.stChatInputContainer button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(124,58,237,0.3);
}

/* ── WELCOME CARD ── */
.welcome-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(37,99,235,0.05));
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0 2rem 0;
}
.welcome-card h3 {
    color: #a78bfa !important;
    margin-top: 0 !important;
}

/* ── DIVIDER ── */
hr {
    border: none;
    border-top: 1px solid #1e1e3a !important;
    margin: 1.5rem 0 !important;
}

/* ── MODE PILL ── */
.mode-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(37,99,235,0.1));
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #a78bfa;
    font-weight: 600;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0a0a0f;
}
::-webkit-scrollbar-thumb {
    background: #2d2d5e;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #3d3d6e;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-top-color: #7c3aed !important;
}

/* ── RESPONSIVE FIXES ── */
@media (max-width: 768px) {
    .main-title { font-size: 2.5rem !important; }
    .badge-row { gap: 6px; }
    .badge { font-size: 0.7rem; padding: 4px 10px; }
    .stat-grid { gap: 6px; }
    .stChatMessage { padding: 0.75rem 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
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
if "quick" not in st.session_state:
    st.session_state.quick = ""

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-name">ARIA</div>
        <div class="brand-sub">AI Engineering Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats with proper spacing
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-num">{len(st.session_state.messages)}</div>
            <div class="stat-lbl">Messages</div>
        </div>
        <div class="stat-card">
            <div class="stat-num">{st.session_state.total_sessions}</div>
            <div class="stat-lbl">Sessions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚡ Quick Modes</div>', unsafe_allow_html=True)

    modes = [
        ("🤖 AI Engineering", "AI Engineer", "You are helping with AI engineering. Be highly technical about LLMs, RAG, agents, embeddings. "),
        ("⚙️ Automation", "Automation", "Focus on automation engineering. Build complete automation scripts, n8n workflows, bots. "),
        ("🌐 Web Builder", "Web Builder", "Build complete modern websites. Give full working HTML/CSS/JS with stunning design. "),
        ("🐍 Python Expert", "Python", "You are a Python expert. Write clean, production-ready Python with best practices. "),
        ("📊 Data Analysis", "Data Analysis", "Focus on data analysis. Use pandas, numpy. Give actionable insights. "),
        ("💬 General", "General", ""),
    ]

    for label, mode_key, _ in modes:
        if st.button(label, key=f"btn_{mode_key}", use_container_width=True):
            st.session_state.mode = mode_key
            st.rerun()

    st.markdown("---")
    st.markdown(f'<div class="section-title">Active Mode</div><div class="mode-pill">⚡ {st.session_state.mode}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:1.5rem">💬 Recent Chats</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-6:]:
            preview = msg["content"][:40] + "..." if len(msg["content"]) > 40 else msg["content"]
            st.markdown(f'<div class="history-item">› {preview}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.8rem;color:#475569;margin-top:0.5rem">No history yet</p>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ New Session", use_container_width=True):
        st.session_state.total_sessions += 1
        st.session_state.messages = []
        st.session_state.gemini_history = [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "model", "parts": [{"text": "New session started. Ready!"}]}
        ]
        st.rerun()

    st.markdown("---")
    st.markdown('<p style="font-size:0.7rem;color:#475569;text-align:center;margin-top:1rem">ARIA • Gemini 2.5 Flash<br>Built for AI Engineers</p>', unsafe_allow_html=True)

# ── MAIN CONTENT ──
# Wrap in container for max-width constraint
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <div class="main-title">⚡ ARIA</div>
    <div class="main-tagline">Advanced Reasoning & Intelligence Assistant — Built for AI Engineers</div>
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

# Show messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""
        <div class="welcome-card">

### 👋 Welcome back, Engineer!

I am **ARIA** — your dedicated AI & Automation Engineering assistant.

**What I can do for you:**

| Capability | Details |
|---|---|
| 🤖 AI Engineering | LLMs, RAG, agents, LangChain, vector DBs, embeddings |
| ⚙️ Automation | n8n, Make.com, Python bots, Playwright, scraping |
| 🐍 Advanced Python | FastAPI, async, OOP, production-ready patterns |
| 🌐 Website Builder | Full HTML/CSS/JS with modern animations |
| 📊 Data Analysis | Pandas, pipelines, insights, visualization |
| 🔗 API Integration | REST, webhooks, OAuth, third-party APIs |
| 🚀 DevOps | Docker, GitHub Actions, cloud deployment |

**Today is {today}** — I have current knowledge of the latest AI tools and frameworks.

*Switch modes in the sidebar or just type your question below!* ⚡
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── CHAT ──
if user_input := st.chat_input("Ask ARIA anything — AI, automation, code, websites, data..."):

    mode_context = {
        "AI Engineer": "As a senior AI engineer helping an expert: be highly technical and precise. ",
        "Automation": "As an automation expert: give complete working automation code and workflows. ",
        "Web Builder": "Build a complete, stunning, modern website. Full HTML/CSS/JS in one file. ",
        "Python": "As a Python expert: write clean, production-ready Python with proper patterns. ",
        "Data Analysis": "As a data engineer: be analytical, use pandas/numpy, give actionable insights. ",
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
                    reply = f"⚠️ {result.get('error', {}).get('message', 'Please try again.')}"

            except requests.exceptions.Timeout:
                reply = "⏱️ Timeout — please try again!"
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.gemini_history.append({"role": "model", "parts": [{"text": reply}]})
    st.session_state.messages.append({"role": "assistant", "content": reply})

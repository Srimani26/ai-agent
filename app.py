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
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }

#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: #0a0a0f;
    min-height: 100vh;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e3a !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div {
    padding: 20px 12px !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] li {
    color: #e2e8f0 !important;
}

.brand {
    text-align: center;
    padding: 10px 0 20px 0;
}
.brand-name {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #2563eb, #059669);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}
.brand-sub {
    font-size: 0.7rem;
    color: #4a5568;
    letter-spacing: 1px;
    margin-top: 2px;
}

.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 12px 0;
}
.stat-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(37,99,235,0.1));
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
}
.stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #7c3aed !important;
}
.stat-lbl {
    font-size: 0.68rem;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #4a5568 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 16px 0 8px 0;
}

/* Sidebar mode buttons */
.stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #cbd5e1 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 9px 12px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 4px !important;
}
.stButton > button:hover {
    background: rgba(124,58,237,0.2) !important;
    border-color: rgba(124,58,237,0.5) !important;
    color: #a78bfa !important;
    transform: translateX(3px) !important;
}

.history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 7px;
    padding: 7px 10px;
    margin-bottom: 5px;
    font-size: 0.78rem;
    color: #94a3b8;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.history-item:hover {
    background: rgba(124,58,237,0.1);
    border-color: rgba(124,58,237,0.3);
}

/* ── MAIN AREA ── */
.main-header {
    text-align: center;
    padding: 30px 0 16px 0;
}
.main-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed 0%, #2563eb 50%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    line-height: 1.1;
}
.main-tagline {
    font-size: 0.95rem;
    color: #475569;
    margin-top: 6px;
    letter-spacing: 0.5px;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin: 14px 0 20px 0;
    flex-wrap: wrap;
}
.badge {
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: #a78bfa;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: #111122 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    margin-bottom: 12px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(37,99,235,0.08) !important;
    border-color: rgba(37,99,235,0.2) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em {
    color: #e2e8f0 !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: #a78bfa !important;
    margin: 12px 0 6px 0 !important;
}
[data-testid="stChatMessage"] code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(124,58,237,0.15) !important;
    color: #a78bfa !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-size: 0.85rem !important;
}
[data-testid="stChatMessage"] pre {
    background: #060610 !important;
    border: 1px solid #1e1e3a !important;
    border-left: 3px solid #7c3aed !important;
    border-radius: 10px !important;
    padding: 16px !important;
    overflow-x: auto !important;
    margin: 10px 0 !important;
}
[data-testid="stChatMessage"] pre code {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e2e8f0 !important;
    background: transparent !important;
    padding: 0 !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: #111122 !important;
    border: 1.5px solid #2d2d5e !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
[data-testid="stChatInput"] textarea {
    color: #f1f5f9 !important;
    background: transparent !important;
    caret-color: #7c3aed !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #2d2d5e !important;
}

/* Divider */
hr { border-color: #1e1e3a !important; margin: 14px 0 !important; }

/* Mode indicator */
.mode-pill {
    display: inline-block;
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(37,99,235,0.2));
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    color: #a78bfa;
    font-weight: 500;
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
        <div class="brand-sub">AI ENGINEERING ASSISTANT</div>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("---")
    st.markdown(f'<div class="section-title">Active Mode</div><div class="mode-pill">⚡ {st.session_state.mode}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:16px">💬 Recent Chats</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-6:]:
            preview = msg["content"][:38] + "..." if len(msg["content"]) > 38 else msg["content"]
            st.markdown(f'<div class="history-item">› {preview}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.78rem;color:#374151">No history yet</p>', unsafe_allow_html=True)

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
    st.markdown('<p style="font-size:0.72rem;color:#374151;text-align:center">ARIA • Gemini 2.5 Flash<br>Built for AI Engineers</p>', unsafe_allow_html=True)

# ── MAIN CONTENT ──
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

# Welcome
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(f"""### 👋 Welcome back, Engineer!

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

*Switch modes in the sidebar or just type your question below!* ⚡""")

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

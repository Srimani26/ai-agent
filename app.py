import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid
from supabase import create_client

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ARIA v2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  SECRETS
# ─────────────────────────────────────────────
GEMINI_API_KEY   = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY     = st.secrets["GROQ_API_KEY"]
SUPABASE_URL     = st.secrets["SUPABASE_URL"]
SUPABASE_KEY     = st.secrets["SUPABASE_KEY"]

# Optional: for web search via Serper
SERPER_API_KEY   = st.secrets.get("SERPER_API_KEY", "")

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
TODAY = datetime.now().strftime("%B %d, %Y")

MODELS = {
    "⚡ Gemini 2.5 Pro  (Best — Complex Tasks)": "gemini",
    "🚀 Groq Llama 3.3 70B  (Fast — Quick Tasks)": "groq",
    "🔥 Gemini 2.5 Flash  (Light — Simple Tasks)": "gemini-flash",
}

MODES = {
    "🤖 AI Engineer": "ai_engineer",
    "⚙️ Automation": "automation",
    "🐍 Python Expert": "python",
    "🌐 Web Builder": "web",
    "📊 Data Analysis": "data",
    "🏗️ Zoho / ERP": "zoho",
    "💡 General Assistant": "general",
}

# ─────────────────────────────────────────────
#  SYSTEM PROMPTS
# ─────────────────────────────────────────────
BASE_SYSTEM = f"""You are ARIA (Advanced Reasoning & Intelligence Assistant) — a highly capable personal AI built exclusively for Sri (Srimani26), AI Engineer at Standard Roofs, Erode, Tamil Nadu, India.

## Your Core Identity
You are Sri's personal AI — not a generic chatbot. You know his work deeply and think like a senior engineer + trusted advisor. You are honest, direct, and always give complete working solutions — never half answers.

## Sri's Work Context (Always Keep This in Mind)
- AI Engineer & Automation Engineer at Standard Roofs
- Building a Roofing ERP SaaS on Zoho One (targeting Indian roofing companies)
- ERP pricing: Starter / Growth / Business tier bundles
- Zoho CRM with custom Deluge scripting (calculateRoofAreas function)
- Sri AI Memory MCP Server (FastAPI + MCP — already built)
- Google Ads AI Advisor project
- AI Workspace / Knowledge Base system
- Frontend background: HTML, CSS, JS, React
- Strong Python: FastAPI, async, OOP
- Tools: n8n, Make.com, LangChain, Supabase, ChromaDB

## How You Think and Respond
- For complex problems: think step by step, show your reasoning
- For code: always give production-ready, complete, commented code
- For errors: find the root cause — don't just patch symptoms
- For business questions: give practical advice suited for Indian market
- Never say "I can't" without offering an alternative
- Be concise but never incomplete — quality over length
- Today's date: {TODAY}

## Your Personality
- Direct and confident like a senior engineer
- Honest — say when something is genuinely hard or uncertain  
- Encouraging — Sri is 3.5 years into his career, building real things
- No corporate fluff, no excessive disclaimers
"""

MODE_PROMPTS = {
    "ai_engineer": "\n## Current Mode: AI Engineering\nFocus on LLMs, RAG pipelines, agents, MCP servers, vector databases, embeddings, prompt engineering, LangChain, and AI system architecture. Give deep technical answers with working code.",
    "automation": "\n## Current Mode: Automation\nFocus on n8n workflows, Make.com scenarios, Python bots, Playwright, web scraping, API integrations, and task automation. Always give step-by-step implementation.",
    "python": "\n## Current Mode: Python Expert\nFocus on production-ready Python: FastAPI, async/await, OOP patterns, error handling, performance optimization, decorators, and clean architecture.",
    "web": "\n## Current Mode: Web Builder\nFocus on complete, modern websites with HTML/CSS/JS or React. Always give full working code with responsive design, dark/light themes, and clean UI.",
    "data": "\n## Current Mode: Data Analysis\nFocus on pandas, data pipelines, visualization with plotly/matplotlib, data cleaning, SQL queries, and business insights.",
    "zoho": "\n## Current Mode: Zoho / ERP Specialist\nFocus on Zoho One platform, Deluge scripting, CRM customization, Zoho Books, workflow automation, and the roofing ERP product Sri is building for Indian companies.",
    "general": "\n## Current Mode: General Assistant\nBe a well-rounded assistant — answer anything clearly, think carefully, and give practical advice.",
}

# ─────────────────────────────────────────────
#  SUPABASE CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────
#  WEB SEARCH (Optional — Serper)
# ─────────────────────────────────────────────
def web_search(query: str, num_results: int = 4) -> str:
    if not SERPER_API_KEY:
        return ""
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": num_results},
            timeout=8
        )
        data = response.json()
        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append(f"- {item.get('title','')}: {item.get('snippet','')}")
        return "\n".join(results) if results else ""
    except:
        return ""

def needs_web_search(message: str) -> bool:
    triggers = [
        "latest", "current", "today", "now", "recent", "new",
        "2024", "2025", "2026", "news", "update", "price",
        "what is happening", "trending", "just released"
    ]
    msg_lower = message.lower()
    return any(t in msg_lower for t in triggers)

# ─────────────────────────────────────────────
#  GEMINI API (Streaming)
# ─────────────────────────────────────────────
def call_gemini_stream(messages: list, system_prompt: str, model: str = "gemini-2.5-pro"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse"

    # Convert messages to Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
            "thinkingConfig": {"thinkingBudget": 5000} if "pro" in model else {}
        }
    }

    try:
        response = requests.post(url, json=payload, stream=True, timeout=60)
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text", "")
                                if text:
                                    yield text
                    except:
                        continue
    except Exception as e:
        yield f"\n\n⚠️ Gemini error: {str(e)}"

# ─────────────────────────────────────────────
#  GROQ API (Streaming)
# ─────────────────────────────────────────────
def call_groq_stream(messages: list, system_prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    groq_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        groq_messages.append({"role": msg["role"], "content": msg["content"]})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": groq_messages,
        "max_tokens": 8192,
        "temperature": 0.7,
        "stream": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: ") and line_str != "data: [DONE]":
                    try:
                        data = json.loads(line_str[6:])
                        delta = data["choices"][0].get("delta", {})
                        text = delta.get("content", "")
                        if text:
                            yield text
                    except:
                        continue
    except Exception as e:
        yield f"\n\n⚠️ Groq error: {str(e)}"

# ─────────────────────────────────────────────
#  SMART MODEL ROUTER
# ─────────────────────────────────────────────
def stream_response(messages: list, system_prompt: str, model_choice: str):
    """Route to correct model with auto-fallback"""

    if model_choice == "gemini":
        gen = call_gemini_stream(messages, system_prompt, "gemini-2.5-pro-preview-06-05")
    elif model_choice == "gemini-flash":
        gen = call_gemini_stream(messages, system_prompt, "gemini-2.5-flash")
    else:
        gen = call_groq_stream(messages, system_prompt)

    full_text = ""
    error_detected = False

    for chunk in gen:
        if "⚠️" in chunk:
            error_detected = True
        full_text += chunk
        yield chunk

    # Auto-fallback: if primary model failed, try Groq
    if error_detected and model_choice == "gemini":
        yield "\n\n🔄 **Switching to backup model (Groq)...**\n\n"
        for chunk in call_groq_stream(messages, system_prompt):
            yield chunk

# ─────────────────────────────────────────────
#  SUPABASE: SAVE & LOAD
# ─────────────────────────────────────────────
def save_message(session_id: str, role: str, content: str):
    try:
        supabase = get_supabase()
        supabase.table("conversations").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except:
        pass

def load_sessions() -> list:
    try:
        supabase = get_supabase()
        result = supabase.table("conversations")\
            .select("session_id, content, created_at")\
            .eq("role", "user")\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()

        seen = {}
        for row in result.data:
            sid = row["session_id"]
            if sid not in seen:
                preview = row["content"][:45] + "..." if len(row["content"]) > 45 else row["content"]
                seen[sid] = {"id": sid, "preview": preview, "time": row["created_at"][:10]}
        return list(seen.values())[:15]
    except:
        return []

def load_session_messages(session_id: str) -> list:
    try:
        supabase = get_supabase()
        result = supabase.table("conversations")\
            .select("role, content")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()
        return [{"role": r["role"], "content": r["content"]} for r in result.data]
    except:
        return []

# ─────────────────────────────────────────────
#  CUSTOM CSS — Dark, Professional, ARIA Identity
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Root */
:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a24;
    --border: #2a2a3a;
    --accent: #7c6af7;
    --accent2: #a78bfa;
    --green: #34d399;
    --text: #e8e8f0;
    --text-muted: #8888aa;
    --user-bg: #1e1b4b;
    --ai-bg: #111118;
}

html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ARIA Header */
.aria-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 24px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}
.aria-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--accent), #ec4899);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700;
    color: white; flex-shrink: 0;
}
.aria-title { font-size: 18px; font-weight: 700; color: var(--text); }
.aria-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* Status badge */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0d2818; border: 1px solid #065f46;
    color: var(--green); padding: 4px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 500; margin-bottom: 16px;
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Section labels */
.sidebar-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.08em;
    color: var(--text-muted); text-transform: uppercase;
    margin: 16px 0 8px 0;
}

/* Chat messages */
.message-wrap { padding: 6px 0; }

.user-msg {
    display: flex; justify-content: flex-end; margin: 8px 0;
}
.user-bubble {
    background: var(--user-bg);
    border: 1px solid #312e81;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    max-width: 72%;
    font-size: 14px; line-height: 1.6;
    color: #c7d2fe;
}

.ai-msg {
    display: flex; gap: 10px; margin: 8px 0; align-items: flex-start;
}
.ai-avatar {
    width: 28px; height: 28px; flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent), #ec4899);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: white;
    margin-top: 2px;
}
.ai-bubble {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-radius: 4px 16px 16px 16px;
    padding: 14px 18px;
    max-width: 82%;
    font-size: 14px; line-height: 1.7;
    color: var(--text);
}

/* Code blocks */
.ai-bubble code {
    background: #1e1e2e !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: #cdd6f4 !important;
    padding: 2px 6px !important;
}
.ai-bubble pre {
    background: #1e1e2e !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
    overflow-x: auto !important;
}

/* Input area */
[data-testid="stChatInput"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124, 106, 247, 0.15) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* Buttons */
.stButton > button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent2) !important;
    background: rgba(124, 106, 247, 0.08) !important;
}

/* Session history items */
.session-item {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    cursor: pointer;
    font-size: 12px;
    color: var(--text-muted);
    transition: all 0.2s;
}
.session-item:hover {
    border-color: var(--accent);
    color: var(--text);
}

/* Welcome screen */
.welcome-wrap {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 60vh; text-align: center;
    padding: 40px 20px;
}
.welcome-logo {
    width: 72px; height: 72px;
    background: linear-gradient(135deg, var(--accent), #ec4899);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px; font-weight: 700; color: white;
    margin: 0 auto 20px;
    box-shadow: 0 0 40px rgba(124, 106, 247, 0.3);
}
.welcome-title {
    font-size: 28px; font-weight: 700;
    background: linear-gradient(135deg, var(--accent2), #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.welcome-sub {
    color: var(--text-muted); font-size: 14px; margin-bottom: 32px;
    max-width: 420px;
}
.quick-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; max-width: 480px; width: 100%;
}
.quick-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 14px 16px;
    text-align: left; cursor: pointer;
    transition: all 0.2s;
}
.quick-card:hover { border-color: var(--accent); }
.quick-card-icon { font-size: 20px; margin-bottom: 6px; }
.quick-card-title { font-size: 12px; font-weight: 600; color: var(--text); }
.quick-card-desc { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* Search indicator */
.search-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: #1a1a0a; border: 1px solid #854d0e;
    color: #fbbf24; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; margin-bottom: 8px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* Main content padding */
.main .block-container {
    max-width: 860px !important;
    padding: 1rem 2rem 6rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "gemini"
if "mode" not in st.session_state:
    st.session_state.mode = "general"
if "web_search_on" not in st.session_state:
    st.session_state.web_search_on = bool(SERPER_API_KEY)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Header
    st.markdown("""
    <div class="aria-header">
        <div class="aria-logo">A</div>
        <div>
            <div class="aria-title">ARIA v2</div>
            <div class="aria-sub">Sri's Personal AI Assistant</div>
        </div>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        Online & Ready
    </div>
    """, unsafe_allow_html=True)

    # Model selector
    st.markdown('<div class="sidebar-label">AI Model</div>', unsafe_allow_html=True)
    model_label = st.selectbox(
        "Model", list(MODELS.keys()), label_visibility="collapsed"
    )
    st.session_state.model_choice = MODELS[model_label]

    # Mode selector
    st.markdown('<div class="sidebar-label">Work Mode</div>', unsafe_allow_html=True)
    mode_label = st.selectbox(
        "Mode", list(MODES.keys()), label_visibility="collapsed"
    )
    st.session_state.mode = MODES[mode_label]

    # Web search toggle
    if SERPER_API_KEY:
        st.markdown('<div class="sidebar-label">Features</div>', unsafe_allow_html=True)
        st.session_state.web_search_on = st.toggle(
            "🌐 Web Search", value=st.session_state.web_search_on
        )

    # New session
    st.markdown('<div class="sidebar-label">Session</div>', unsafe_allow_html=True)
    if st.button("✨ New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    # Session history
    st.markdown('<div class="sidebar-label">Recent Chats</div>', unsafe_allow_html=True)
    sessions = load_sessions()
    for s in sessions[:8]:
        if s["id"] != st.session_state.session_id:
            if st.button(f"💬 {s['preview']}", key=s["id"], use_container_width=True):
                st.session_state.session_id = s["id"]
                st.session_state.messages = load_session_messages(s["id"])
                st.rerun()

    # Info
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:11px; color:#555577; text-align:center; line-height:1.6">
        Built by Srimani26<br>
        Powered by Gemini + Groq<br>
        {TODAY}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN CHAT AREA
# ─────────────────────────────────────────────

# Welcome screen
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-logo">A</div>
        <div class="welcome-title">ARIA is ready, Sri.</div>
        <div class="welcome-sub">
            Your personal AI — built for complex engineering, automation,
            Zoho ERP, coding, and everything in between.
        </div>
        <div class="quick-grid">
            <div class="quick-card">
                <div class="quick-card-icon">🤖</div>
                <div class="quick-card-title">AI Engineering</div>
                <div class="quick-card-desc">LLMs, RAG, agents, MCP</div>
            </div>
            <div class="quick-card">
                <div class="quick-card-icon">🏗️</div>
                <div class="quick-card-title">Zoho ERP</div>
                <div class="quick-card-desc">Deluge, CRM, workflows</div>
            </div>
            <div class="quick-card">
                <div class="quick-card-icon">⚙️</div>
                <div class="quick-card-title">Automation</div>
                <div class="quick-card-desc">n8n, Make, Python bots</div>
            </div>
            <div class="quick-card">
                <div class="quick-card-icon">🐍</div>
                <div class="quick-card-title">Python Expert</div>
                <div class="quick-card-desc">FastAPI, async, production code</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-msg">
            <div class="user-bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(msg["content"])

# ─────────────────────────────────────────────
#  CHAT INPUT
# ─────────────────────────────────────────────
if prompt := st.chat_input("Ask ARIA anything..."):

    # Build system prompt
    mode_key = st.session_state.mode
    system_prompt = BASE_SYSTEM + MODE_PROMPTS.get(mode_key, "")

    # Web search injection
    search_context = ""
    if st.session_state.web_search_on and needs_web_search(prompt):
        with st.spinner("🌐 Searching web..."):
            search_results = web_search(prompt)
            if search_results:
                search_context = f"\n\n## Live Web Search Results\n{search_results}\n\nUse the above search results to give an accurate, up-to-date answer.\n"
                system_prompt += search_context
                st.markdown('<div class="search-badge">🌐 Web search used</div>', unsafe_allow_html=True)

    # Show user message
    st.markdown(f"""
    <div class="user-msg">
        <div class="user-bubble">{prompt}</div>
    </div>
    """, unsafe_allow_html=True)

    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(st.session_state.session_id, "user", prompt)

    # Build messages for API (keep last 20 for context)
    api_messages = st.session_state.messages[-20:]

    # Stream response
    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full_response = ""

        for chunk in stream_response(api_messages, system_prompt, st.session_state.model_choice):
            full_response += chunk
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_message(st.session_state.session_id, "assistant", full_response)

import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid
from supabase import create_client

st.set_page_config(
    page_title="ARIA — Sri's AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SECRETS ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
SUPABASE_URL   = st.secrets["SUPABASE_URL"]
SUPABASE_KEY   = st.secrets["SUPABASE_KEY"]
SERPER_API_KEY = st.secrets.get("SERPER_API_KEY", "")
TODAY = datetime.now().strftime("%B %d, %Y")

# ── MODELS & MODES ────────────────────────────────────────────────────────────
MODELS = {
    "Gemini 2.5 Pro  ·  Best quality": "gemini-pro",
    "Groq Llama 3.3  ·  Fastest":      "groq",
    "Gemini 2.5 Flash  ·  Light tasks": "gemini-flash",
}
MODES = {
    "🤖  AI Engineering":   "ai_engineer",
    "🏗️  Zoho / ERP":        "zoho",
    "⚙️  Automation":        "automation",
    "🐍  Python Expert":     "python",
    "🌐  Web Builder":       "web",
    "💡  General":           "general",
}

# ── SYSTEM PROMPTS ────────────────────────────────────────────────────────────
BASE = f"""You are ARIA — Advanced Reasoning & Intelligence Assistant.
You are Sri's (Srimani26) exclusive personal AI. Sri is an AI Engineer & Automation Engineer at Standard Roofs, Erode, Tamil Nadu.

## Sri's full context
- Building Roofing ERP SaaS on Zoho One for Indian roofing companies
- ERP pricing tiers: Starter / Growth / Business (bundled with Zoho One licenses)
- Zoho CRM with custom Deluge function: calculateRoofAreas (multi-section, slope/extension logic)
- Sri AI Memory MCP server — FastAPI + MCP (already live on Render)
- Google Ads AI Advisor project
- Frontend background: HTML, CSS, JS, React
- Python stack: FastAPI, async, Pydantic, OOP
- Tools: n8n, Make.com, LangChain, Supabase, ChromaDB
- Portfolio: srimani26.github.io | GitHub: Srimani26

## How you respond
- Think step by step for complex problems — show reasoning
- Always give complete, production-ready, commented code — never partial
- Diagnose root cause on errors, don't just patch symptoms
- Be direct and confident — no corporate fluff, no excessive disclaimers
- For business: always consider Indian market context
- Today: {TODAY}

## Your personality
You are Sri's senior engineer + trusted advisor. Honest, precise, encouraging.
Sri is 3.5 years into his career building real products — support that ambition."""

MODE_EXTRAS = {
    "ai_engineer": "\nMODE: AI Engineering — focus on LLMs, RAG, agents, MCP, embeddings, LangChain, vector DBs. Deep technical answers with working code.",
    "zoho":        "\nMODE: Zoho/ERP — focus on Zoho One, Deluge scripting, CRM customization, roofing ERP product, Indian SMB market.",
    "automation":  "\nMODE: Automation — focus on n8n, Make.com, Python bots, API integrations, webhook flows, task automation.",
    "python":      "\nMODE: Python Expert — focus on FastAPI, async/await, Pydantic, OOP patterns, clean architecture, performance.",
    "web":         "\nMODE: Web Builder — always give complete HTML/CSS/JS or React code, responsive, dark/light themes.",
    "general":     "\nMODE: General — be a well-rounded assistant, think carefully, give practical advice.",
}

# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_sb():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_msg(sid, role, content):
    try:
        get_sb().table("conversations").insert({
            "session_id": sid, "role": role, "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except: pass

def load_sessions():
    try:
        r = get_sb().table("conversations").select("session_id,content,created_at")\
            .eq("role","user").order("created_at",desc=True).limit(60).execute()
        seen = {}
        for row in r.data:
            s = row["session_id"]
            if s not in seen:
                p = row["content"][:42]+"…" if len(row["content"])>42 else row["content"]
                seen[s] = {"id":s,"preview":p,"date":row["created_at"][:10]}
        return list(seen.values())[:12]
    except: return []

def load_history(sid):
    try:
        r = get_sb().table("conversations").select("role,content")\
            .eq("session_id",sid).order("created_at").execute()
        return [{"role":x["role"],"content":x["content"]} for x in r.data]
    except: return []

# ── WEB SEARCH ────────────────────────────────────────────────────────────────
def search(q):
    if not SERPER_API_KEY: return ""
    try:
        r = requests.post("https://google.serper.dev/search",
            headers={"X-API-KEY":SERPER_API_KEY,"Content-Type":"application/json"},
            json={"q":q,"num":4}, timeout=8)
        items = r.json().get("organic",[])[:4]
        return "\n".join(f"- {i.get('title','')}: {i.get('snippet','')}" for i in items)
    except: return ""

def wants_search(msg):
    kw = ["latest","current","today","now","recent","new","2025","2026",
          "news","update","price","trending","just released","what is happening"]
    return any(k in msg.lower() for k in kw)

# ── GEMINI STREAM ─────────────────────────────────────────────────────────────
def gemini_stream(messages, system, model="gemini-2.5-pro-preview-06-05"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse"
    contents = [{"role":"user" if m["role"]=="user" else "model",
                 "parts":[{"text":m["content"]}]} for m in messages]
    cfg = {"temperature":0.7,"maxOutputTokens":8192}
    if "pro" in model:
        cfg["thinkingConfig"] = {"thinkingBudget":5000}
    payload = {"system_instruction":{"parts":[{"text":system}]},
               "contents":contents,"generationConfig":cfg}
    try:
        r = requests.post(url, json=payload, stream=True, timeout=90)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: "):
                    try:
                        d = json.loads(s[6:])
                        for p in d.get("candidates",[{}])[0].get("content",{}).get("parts",[]):
                            t = p.get("text","")
                            if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ Gemini error: {e}"

# ── GROQ STREAM ───────────────────────────────────────────────────────────────
def groq_stream(messages, system):
    headers = {"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
    msgs = [{"role":"system","content":system}] + \
           [{"role":m["role"],"content":m["content"]} for m in messages]
    payload = {"model":"llama-3.3-70b-versatile","messages":msgs,
               "max_tokens":8192,"temperature":0.7,"stream":True}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers=headers, json=payload, stream=True, timeout=60)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: ") and s != "data: [DONE]":
                    try:
                        t = json.loads(s[6:])["choices"][0].get("delta",{}).get("content","")
                        if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ Groq error: {e}"

# ── ROUTER ────────────────────────────────────────────────────────────────────
def respond(messages, system, model):
    if model == "gemini-pro":
        gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05")
    elif model == "gemini-flash":
        gen = gemini_stream(messages, system, "gemini-2.5-flash")
    else:
        gen = groq_stream(messages, system)

    full = ""
    failed = False
    for chunk in gen:
        if "⚠️" in chunk: failed = True
        full += chunk
        yield chunk

    if failed and model == "gemini-pro":
        yield "\n\n🔄 Switching to Groq backup...\n\n"
        for chunk in groq_stream(messages, system):
            yield chunk

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

/* ── EVERYTHING DARK ── */
html, body, [data-testid="stApp"], .stApp, .main, section.main,
[data-testid="stMain"], [data-testid="block-container"],
[data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"],
.appview-container, .main .block-container {
    background-color: #0c0c12 !important;
    color: #e2e2f0 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stHeader"] {
    display: none !important;
    visibility: hidden !important;
}

/* ── SIDEBAR BACKGROUND ── */
[data-testid="stSidebar"] { background-color: #0e0e18 !important; }
[data-testid="stSidebar"] > div:first-child {
    background-color: #0e0e18 !important;
    border-right: 1px solid #1c1c2e !important;
}
[data-testid="stSidebar"] * { color: #e2e2f0 !important; font-family: 'Inter', sans-serif !important; }

/* ── SELECTBOX — DARK ── */
div[data-baseweb="select"] > div:first-child {
    background-color: #18182a !important;
    border: 1px solid #2c2c44 !important;
    border-radius: 10px !important;
    color: #e2e2f0 !important;
    min-height: 40px !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div { color: #e2e2f0 !important; }
svg[data-testid="stSvgIcon"] { fill: #8888aa !important; }

/* ── DROPDOWN POPUP ── */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[role="listbox"],
div[data-baseweb="menu"] {
    background-color: #18182a !important;
    border: 1px solid #2c2c44 !important;
    border-radius: 12px !important;
}
li[role="option"] {
    background-color: #18182a !important;
    color: #e2e2f0 !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: #23233a !important;
    color: #a29bfe !important;
}

/* ── TOGGLE ── */
[data-testid="stToggle"] span { font-size: 13px !important; color: #9090b0 !important; }
[role="checkbox"][aria-checked="true"] { background-color: #6c5ce7 !important; }

/* ── SIDEBAR BUTTONS ── */
[data-testid="stSidebar"] button {
    background-color: #18182a !important;
    border: 1px solid #2c2c44 !important;
    border-radius: 10px !important;
    color: #9090b0 !important;
    font-size: 12.5px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
    text-align: left !important;
    padding: 8px 14px !important;
}
[data-testid="stSidebar"] button:hover {
    border-color: #6c5ce7 !important;
    color: #a29bfe !important;
    background-color: #1e1e32 !important;
}

/* ── MAIN CONTAINER WIDTH ── */
.block-container {
    max-width: 840px !important;
    padding: 0 2rem 8rem 2rem !important;
    margin: 0 auto !important;
}

/* ── CHAT MESSAGE WRAPPERS ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 6px 0 !important;
    gap: 12px !important;
}

/* ── USER MESSAGE — right aligned ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
    align-items: flex-end !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: linear-gradient(135deg, #1e1b4b, #1a1535) !important;
    border: 1px solid #312e81 !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 12px 16px !important;
    color: #c7d2fe !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
    max-width: 78% !important;
    margin-left: auto !important;
}

/* ── ASSISTANT MESSAGE ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: #13131f !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 4px 18px 18px 18px !important;
    padding: 14px 18px !important;
    color: #e2e2f0 !important;
    font-size: 14px !important;
    line-height: 1.78 !important;
}

/* ── CODE BLOCKS ── */
[data-testid="stChatMessage"] code {
    background: #1a1a2e !important;
    border: 1px solid #2c2c44 !important;
    border-radius: 5px !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 12.5px !important;
    color: #cdd6f4 !important;
    padding: 2px 7px !important;
}
[data-testid="stChatMessage"] pre {
    background: #11111e !important;
    border: 1px solid #2c2c44 !important;
    border-radius: 12px !important;
    padding: 18px !important;
    overflow-x: auto !important;
    margin: 8px 0 !important;
}
[data-testid="stChatMessage"] pre code {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    font-size: 12.5px !important;
    color: #cdd6f4 !important;
}

/* ── AVATARS ── */
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #6c5ce7, #ec4899) !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}
[data-testid="chatAvatarIcon-user"] {
    background: #1e1a3e !important;
    border: 1px solid #312e81 !important;
    border-radius: 10px !important;
    color: #a29bfe !important;
}

/* ── CHAT INPUT — THE KEY FIX ── */
/* Outer bottom bar */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background-color: #0c0c12 !important;
    border-top: none !important;
}
/* The input container */
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
[data-testid="stChatInput"] {
    background-color: #18182a !important;
    border: 1.5px solid #2c2c44 !important;
    border-radius: 14px !important;
    color: #e2e2f0 !important;
}
/* The textarea inside */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputContainer"] textarea {
    background-color: #18182a !important;
    color: #e2e2f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    caret-color: #a29bfe !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #55556a !important;
}
/* Focus glow */
[data-testid="stChatInputContainer"]:focus-within,
[data-testid="stChatInput"]:focus-within {
    border-color: #6c5ce7 !important;
    box-shadow: 0 0 0 3px rgba(108,92,231,0.15) !important;
}
/* Send button */
[data-testid="stChatInputContainer"] button,
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6c5ce7, #a855f7) !important;
    border-radius: 9px !important;
    border: none !important;
    color: white !important;
}
[data-testid="stChatInputContainer"] button:hover,
[data-testid="stChatInput"] button:hover {
    opacity: 0.88 !important;
}

/* ── BOTTOM GRADIENT FADE ── */
[data-testid="stBottom"]::before {
    content: '';
    position: absolute;
    top: -48px; left: 0; right: 0; height: 48px;
    background: linear-gradient(to top, #0c0c12, transparent);
    pointer-events: none;
    z-index: 1;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2c2c44; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a58; }

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: #6c5ce7 !important; }

/* ── MARKDOWN HEADINGS IN CHAT ── */
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: #a29bfe !important;
    font-weight: 600 !important;
    margin: 14px 0 8px !important;
}
[data-testid="stChatMessage"] ul,
[data-testid="stChatMessage"] ol {
    padding-left: 20px !important;
}
[data-testid="stChatMessage"] li { margin: 4px 0 !important; }
[data-testid="stChatMessage"] strong { color: #f0f0ff !important; }
[data-testid="stChatMessage"] a { color: #a29bfe !important; }
[data-testid="stChatMessage"] table {
    border-collapse: collapse !important;
    width: 100% !important;
    margin: 10px 0 !important;
}
[data-testid="stChatMessage"] th {
    background: #1e1e30 !important;
    color: #a29bfe !important;
    padding: 8px 12px !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stChatMessage"] td {
    padding: 8px 12px !important;
    border-bottom: 1px solid #1e1e30 !important;
    font-size: 13px !important;
}

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "sid"      not in st.session_state: st.session_state.sid      = str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state.messages = []
if "model"    not in st.session_state: st.session_state.model    = "gemini-pro"
if "mode"     not in st.session_state: st.session_state.mode     = "general"
if "wsearch"  not in st.session_state: st.session_state.wsearch  = bool(SERPER_API_KEY)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:4px 0 20px">
      <div style="width:38px;height:38px;border-radius:10px;
           background:linear-gradient(135deg,#6c5ce7,#ec4899);
           display:flex;align-items:center;justify-content:center;
           font-size:17px;font-weight:700;color:#fff;flex-shrink:0">A</div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#ddddf0;letter-spacing:-0.3px">ARIA v2</div>
        <div style="font-size:11px;color:#55556a;margin-top:1px">Sri's Personal AI</div>
      </div>
    </div>
    <div style="display:inline-flex;align-items:center;gap:6px;
         background:#0a1f14;border:1px solid #065f46;color:#34d399;
         padding:4px 12px;border-radius:20px;font-size:11px;
         font-weight:500;margin-bottom:20px">
      <span style="width:6px;height:6px;border-radius:50%;
            background:#34d399;display:inline-block;
            animation:pulse 2s infinite"></span>
      Online &amp; Ready
    </div>
    <style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}</style>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.08em;color:#44445a;text-transform:uppercase;margin:0 0 6px">AI Model</p>', unsafe_allow_html=True)
    ml = st.selectbox("model", list(MODELS.keys()), label_visibility="collapsed")
    st.session_state.model = MODELS[ml]

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.08em;color:#44445a;text-transform:uppercase;margin:14px 0 6px">Work Mode</p>', unsafe_allow_html=True)
    mo = st.selectbox("mode", list(MODES.keys()), label_visibility="collapsed")
    st.session_state.mode = MODES[mo]

    if SERPER_API_KEY:
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.08em;color:#44445a;text-transform:uppercase;margin:14px 0 6px">Features</p>', unsafe_allow_html=True)
        st.session_state.wsearch = st.toggle("🌐 Web Search", value=st.session_state.wsearch)

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.08em;color:#44445a;text-transform:uppercase;margin:14px 0 6px">Session</p>', unsafe_allow_html=True)
    if st.button("✦  New conversation", use_container_width=True):
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    sessions = load_sessions()
    if sessions:
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.08em;color:#44445a;text-transform:uppercase;margin:14px 0 6px">Recent</p>', unsafe_allow_html=True)
        for s in sessions[:8]:
            if s["id"] != st.session_state.sid:
                if st.button(f"↩  {s['preview']}", key=s["id"], use_container_width=True):
                    st.session_state.sid = s["id"]
                    st.session_state.messages = load_history(s["id"])
                    st.rerun()

    st.markdown(f"""
    <div style="position:absolute;bottom:20px;left:0;right:0;
         text-align:center;font-size:11px;color:#33334a;line-height:1.7">
      Built by Srimani26<br>Gemini · Groq · Supabase<br>{TODAY}
    </div>""", unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;
         justify-content:center;min-height:62vh;text-align:center;padding:40px 20px">

      <div style="width:68px;height:68px;border-radius:18px;margin:0 auto 22px;
           background:linear-gradient(135deg,#6c5ce7,#ec4899);
           display:flex;align-items:center;justify-content:center;
           font-size:28px;font-weight:700;color:#fff;
           box-shadow:0 0 48px rgba(108,92,231,.35)">A</div>

      <h1 style="font-size:26px;font-weight:700;
           background:linear-gradient(135deg,#a29bfe,#f472b6);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
           margin:0 0 10px;letter-spacing:-0.5px">ARIA is ready, Sri.</h1>

      <p style="color:#55556a;font-size:14px;max-width:400px;
           line-height:1.7;margin:0 0 32px">
        Your personal AI — complex engineering, Zoho ERP,<br>automation, coding, and everything in between.
      </p>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;
           max-width:460px;width:100%">
        {"".join(f'''<div style="background:#13131e;border:1px solid #1e1e2e;
             border-radius:12px;padding:14px 16px;text-align:left">
          <div style="font-size:19px;margin-bottom:6px">{icon}</div>
          <div style="font-size:12px;font-weight:600;color:#ddddf0">{title}</div>
          <div style="font-size:11px;color:#44445a;margin-top:3px">{desc}</div>
        </div>''' for icon,title,desc in [
            ("🤖","AI Engineering","LLMs, RAG, agents, MCP"),
            ("🏗️","Zoho ERP","Deluge, CRM, workflows"),
            ("⚙️","Automation","n8n, Make, Python bots"),
            ("🐍","Python Expert","FastAPI, async, production"),
        ])}
      </div>
    </div>
    """, unsafe_allow_html=True)

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"]=="assistant" else "👤"):
        st.markdown(msg["content"])

# ── INPUT ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask ARIA anything…"):

    sys = BASE + MODE_EXTRAS.get(st.session_state.mode, "")

    # Web search injection
    used_search = False
    if st.session_state.wsearch and wants_search(prompt):
        with st.spinner("🌐 Searching…"):
            results = search(prompt)
        if results:
            sys += f"\n\n## Live web search results\n{results}\nUse these for an accurate, up-to-date answer."
            used_search = True

    if used_search:
        st.markdown('<span style="display:inline-flex;align-items:center;gap:5px;background:#1a1500;border:1px solid #713f12;color:#fbbf24;padding:3px 11px;border-radius:20px;font-size:11px;margin-bottom:6px">🌐 Web search used</span>', unsafe_allow_html=True)

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    st.session_state.messages.append({"role":"user","content":prompt})
    save_msg(st.session_state.sid, "user", prompt)

    api_msgs = st.session_state.messages[-20:]

    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full = ""
        for chunk in respond(api_msgs, sys, st.session_state.model):
            full += chunk
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

    st.session_state.messages.append({"role":"assistant","content":full})
    save_msg(st.session_state.sid, "assistant", full)
